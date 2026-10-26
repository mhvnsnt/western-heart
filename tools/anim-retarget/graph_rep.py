"""Topology-agnostic skeletal graph representation + semantic correspondence.

Implements paper Section 3.1 (motion as a sequence of graphs) and the
alignment half of Section 3.2 (Semantic-Aware Feature Modulation).

Paper 3.1 recap: a motion frame is an undirected graph G=(V,E,E_f,F_s,F_m)
where the static node features F_s=(X_g, X_l, X_t) are the global offset
w.r.t. root, the rest-pose coordinate relative to the parent, and the
encoded joint semantic features; E_f carries topological depth and reverse
depth of the connected child joint.

Paper 3.2 recap: motion features are modulated by FiLM parameters
(gamma, beta) predicted from the joint condition c=Phi([z_s; z_t]) with a
gated residual (eq. 1-3), so joints are compared in a semantic-spatial
space instead of by hierarchy index or name.

WH-native analysis mode: no trained weights ship with this tool, so the
learned projections (phi_m, phi_s, phi_t, Phi, Psi) are replaced by
deterministic structure:
  * z_s -- sinusoidal encoding of [X_g; X_l] (paper eq. 1, phi_s), made
    scale-invariant (unit directions + normalized depths) so a 0.4m-tall
    creature and a 1.8m fighter live in the same space;
  * z_t -- semantic tag embedding from semantic_tags.py (paper's X_t);
  * correspondence -- per target joint, softmax over source joints of
    alpha*cos(z_t) + beta*cos(z_s). This IS the functional joint
    correspondence the paper's modulation learns; here it is computed
    explicitly, which also makes it fully inspectable (see --map-report).

The result: motion decouples from bone hierarchy. Two rigs with different
joint counts, different proportions, different names -- even extra limbs --
align through shared functional semantics, exactly the paper's claim
("no canonical joint set, no source-target motion pairs, no hand-crafted
joint correspondences", Sec. 3).
"""

import math

import numpy as np

from semantic_tags import describe_joint, make_embedder


# ---------------------------------------------------------------------------
# Graph construction (paper Sec. 3.1)
# ---------------------------------------------------------------------------

class SkelGraph:
    """Topology-agnostic graph of one rig.

    joints: list of dicts {name, parent (index or None), rest (3-vector,
    world position in the rig's rest pose)}.
    """

    def __init__(self, joints):
        self.joints = joints
        self.names = [j["name"] for j in joints]
        self.n = len(joints)
        self.rest = np.array([j["rest"] for j in joints], dtype=np.float64)
        self.parent = np.array(
            [j["parent"] if j["parent"] is not None else -1 for j in joints],
            dtype=int,
        )
        self.children = [[] for _ in range(self.n)]
        self.roots = []
        for i, p in enumerate(self.parent):
            if p < 0:
                self.roots.append(i)
            else:
                self.children[p].append(i)

        # X_l: rest-pose coordinate relative to parent (paper F_s)
        self.X_l = np.zeros((self.n, 3))
        for i, p in enumerate(self.parent):
            if p >= 0:
                self.X_l[i] = self.rest[i] - self.rest[p]

        # X_g: global offset w.r.t. root (paper F_s)
        root_pos = self.rest[self.roots[0]]
        self.X_g = self.rest - root_pos

        # E_f: topological depth and reverse depth (paper Sec. 3.1)
        self.depth = np.zeros(self.n, dtype=int)
        order = list(self.roots)
        for i in order:
            for c in self.children[i]:
                self.depth[c] = self.depth[i] + 1
                order.append(c)
        self.rev_depth = np.zeros(self.n, dtype=int)
        for i in reversed(order):
            if self.children[i]:
                self.rev_depth[i] = 1 + max(self.rev_depth[c] for c in self.children[i])

        self.max_depth = max(int(self.depth.max()), 1)

        # Chain length for structural descriptions: longest root->leaf path
        # passing through this joint's subtree.
        self.chain_len = self.depth + self.rev_depth

    # -- paper eq. 1: sinusoidal spatial encoder phi_s ---------------------
    def sinusoidal_spatial(self, n_freqs=6):
        """phi_s([X_g; X_l]): sinusoidal encoding of spatial coordinates."""
        feats = np.concatenate([self.X_g, self.X_l], axis=1)  # (n, 6)
        # Normalize per-coordinate by max abs so encoding is scale-aware but
        # bounded; direction information dominates downstream anyway.
        scale = np.abs(feats).max() or 1.0
        feats = feats / scale
        cols = [feats]
        for k in range(1, n_freqs + 1):
            cols.append(np.sin(feats * (2.0 ** k) * math.pi))
            cols.append(np.cos(feats * (2.0 ** k) * math.pi))
        return np.concatenate(cols, axis=1)

    def structural_descriptor(self):
        """Scale-invariant, direction-free structural vector per joint.

        Cross-species rest poses differ wildly (a creature's "shoulder" can
        point down while a human's points up), so bone DIRECTIONS are not a
        valid alignment cue -- the paper's network learns around this, but
        in analysis mode we use features that are invariant by
        construction: bone-length proportions, topological depth /
        reverse depth (the paper's E_f edge features), branching, and
        subtree size. Cosine similarity on this is invariant to uniform
        character scale AND to rest-pose orientation -- the property that
        lets a 0.4m creature align with a 1.8m fighter.
        """
        height = float(
            np.linalg.norm(self.rest.max(axis=0) - self.rest.min(axis=0))
        ) or 1.0
        bone_len = np.linalg.norm(self.X_l, axis=1) / height
        root_dist = np.linalg.norm(self.X_g, axis=1) / height
        n_children = np.array([len(c) for c in self.children], dtype=float)
        # descendant (subtree) count via reverse topological walk
        desc_count = np.zeros(self.n)
        order = []
        stack = list(self.roots)
        while stack:
            i = stack.pop()
            order.append(i)
            stack.extend(self.children[i])
        for i in reversed(order):
            desc_count[i] = len(self.children[i]) + sum(
                desc_count[c] for c in self.children[i]
            )
        desc = np.concatenate(
            [
                bone_len.reshape(-1, 1),
                root_dist.reshape(-1, 1),
                (self.depth / self.max_depth).reshape(-1, 1),
                (self.rev_depth / self.max_depth).reshape(-1, 1),
                (n_children / max(n_children.max(), 1)).reshape(-1, 1),
                (desc_count / max(desc_count.max(), 1)).reshape(-1, 1),
                (n_children == 0).astype(float).reshape(-1, 1),
            ],
            axis=1,
        )
        return desc

    def semantic_descriptions(self):
        descs = []
        for i, j in enumerate(self.joints):
            descs.append(
                describe_joint(
                    j["name"],
                    depth=int(self.depth[i]),
                    is_leaf=len(self.children[i]) == 0,
                    n_children=len(self.children[i]),
                    chain_len=int(self.chain_len[i]),
                )
            )
        return descs


# ---------------------------------------------------------------------------
# Semantic-spatial correspondence (paper Sec. 3.2, analysis mode)
# ---------------------------------------------------------------------------

def _cosine(a, b):
    a = a / np.clip(np.linalg.norm(a, axis=1, keepdims=True), 1e-9, None)
    b = b / np.clip(np.linalg.norm(b, axis=1, keepdims=True), 1e-9, None)
    return a @ b.T


def semantic_correspondence(src, tgt, alpha=0.65, beta=0.35, tau=0.12):
    """Compute the target->source soft correspondence matrix.

    S[j, i] = alpha * cos(z_t_tgt[j], z_t_src[i])
            + beta  * cos(z_s_tgt[j], z_s_src[i])
    A = softmax(S / tau) over source joints i (rows sum to 1).

    alpha/beta mirror the paper's finding that semantics carry the
    alignment while spatial structure disambiguates (e.g. left vs right,
    spine level). tau is the softmax temperature; lower = harder mapping.
    Returns (A, report) where report lists per-target-joint top matches.
    """
    all_descs = src.semantic_descriptions() + tgt.semantic_descriptions()
    embedder, backend = make_embedder(all_descs)
    z_t = np.array([embedder.embed(d) for d in all_descs])
    z_t_src, z_t_tgt = z_t[: src.n], z_t[src.n :]

    z_s_src = src.structural_descriptor()
    z_s_tgt = tgt.structural_descriptor()

    sem = _cosine(z_t_tgt, z_t_src)
    spa = _cosine(z_s_tgt, z_s_src)
    S = alpha * sem + beta * spa

    # Softmax with temperature over source joints.
    Sm = S / max(tau, 1e-6)
    Sm = Sm - Sm.max(axis=1, keepdims=True)
    exp = np.exp(Sm)
    A = exp / exp.sum(axis=1, keepdims=True)

    report = []
    for j in range(tgt.n):
        order = np.argsort(-A[j])[:3]
        report.append(
            {
                "target": tgt.names[j],
                "target_desc": tgt.semantic_descriptions()[j],
                "matches": [
                    {
                        "source": src.names[i],
                        "source_desc": src.semantic_descriptions()[i],
                        "weight": round(float(A[j, i]), 4),
                    }
                    for i in order
                ],
                "top_weight": round(float(A[j, order[0]]), 4),
            }
        )
    return A, report, {"embed_backend": backend, "alpha": alpha,
                      "beta": beta, "tau": tau}
