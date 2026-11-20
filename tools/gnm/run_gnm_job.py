#!/usr/bin/env python3
"""GNM head-bake job — parametric GNM head -> rigged GLB.

Part of the suite job queue (tools/suite-jobs/ convention: run_job(spec, log)).
Pure stdlib + numpy. The vendored GNM numpy backend does the parametric
evaluation; this module adds model loading, semantic param resolution, and a
minimal GLB writer (joints + skin included).

Job spec (JSON):
  {
    "type": "gnm",
    "out": "/abs/path/head.glb",
    "version": "3",                       # GNM major version
    "variant": "head",
    "model_file": "/optional/gnm_head.npz",  # skips download
    "identity": {"gender": "female", "ethnicity": "white", "seed": 7},
    "identity_vector": [...],             # raw PCA vector (overrides identity)
    "expression": {"blend": {"smile": 0.8, "jaw_open": 0.3}},
    "expression_vector": [...],           # raw vector (overrides expression)
    "joint_rotations": {"jaw": [0.2, 0, 0]},  # axis-angle radians, per joint
    "translation": [0, 0, 0]
  }

Model weights: google/gnm-3 is a GATED HuggingFace repo — accept the license
at huggingface.co/google/gnm-3, then `huggingface-cli login` (or set
GNM_CACHE_DIR to a dir containing v3_0/gnm_head.npz). First successful run
caches the weights; later runs are offline.

Semantic identity sampling (IdentitySampler) needs TensorFlow; if TF is not
installed the runner falls back to seeded-random PCA vectors (documented in
the job log). Expression blending maps names to GNM expression indices and
needs no TF.
"""
import json
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "vendor", "GNM")
sys.path.insert(0, VENDOR)


# ---------------------------------------------------------------- model load
def load_model(spec, log):
    from gnm.shape import gnm_data_loader
    from gnm.shape.data.versions import gnm_specs
    from gnm.shape.gnm_numpy import GNM

    version = gnm_specs.GNMMajorVersion(str(spec.get("version", "3")))
    variant = gnm_specs.GNMVariant(str(spec.get("variant", "head")))

    if spec.get("model_file"):
        log(f"loading GNM model from {spec['model_file']}")
        data = gnm_data_loader.load_model_from_custom_file(spec["model_file"])
        return GNM._from_model_data(data)

    from gnm.shape.oss_data_loaders import oss_data_loaders
    cache = oss_data_loaders.get_default_gnm_cache_dir()
    vdir = gnm_data_loader._get_version_dir_name(version)
    fname = gnm_data_loader._get_model_filename(version, variant)
    cached = os.path.join(str(cache), vdir, fname)
    if os.path.exists(cached):
        log(f"loading cached GNM model {cached}")
        data = gnm_data_loader.load_model_from_custom_file(cached)
        return GNM._from_model_data(data)

    log("downloading GNM model (gated HF repo — see module docstring)")
    try:
        data = gnm_data_loader.load_model_from_remote(version, variant)
    except Exception as e:
        raise RuntimeError(
            "GNM weight download failed. google/gnm-3 is a gated HuggingFace "
            "repo: accept the license at huggingface.co/google/gnm-3 and run "
            "`huggingface-cli login`, or pass model_file with a local "
            f"gnm_head.npz. Underlying error: {e}"
        )
    return GNM._from_model_data(data)


# ------------------------------------------------------- param resolution
_GENDER = {"female": 1, "male": 0}
_ETHNICITY = {"middle eastern": 0, "asian": 1, "white": 2, "black": 3}


def resolve_identity(model, spec, log):
    if spec.get("identity_vector") is not None:
        v = np.asarray(spec["identity_vector"], dtype=np.float32)
        assert v.shape == (model.identity_dim,), f"identity dim {v.shape}"
        return v
    ident = spec.get("identity", {}) or {}
    gender = str(ident.get("gender", "female")).lower()
    eth = str(ident.get("ethnicity", "white")).lower()
    seed = int(ident.get("seed", 0))
    try:
        from gnm.shape import semantic_sampler
        from gnm.shape.semantic_sampler import Gender, Ethnicity
        smp = semantic_sampler.IdentitySampler()
        g = Gender.FEMALE if _GENDER.get(gender, 1) else Gender.MALE
        e = [Ethnicity.MIDDLE_EASTERN, Ethnicity.ASIAN,
             Ethnicity.WHITE, Ethnicity.BLACK][_ETHNICITY.get(eth, 2)]
        rng = np.random.default_rng(seed)
        v = smp.sample_identity(g, e, num_samples=1, rng=rng, verbose=False)
        log(f"identity via IdentitySampler ({gender}/{eth} seed={seed})")
        return np.asarray(v[0], dtype=np.float32)
    except ImportError:
        log("TensorFlow not installed — seeded-random identity PCA vector")
        rng = np.random.default_rng(seed * 7919 + _GENDER.get(gender, 1))
        return rng.standard_normal(model.identity_dim).astype(np.float32) * 0.6


def resolve_expression(model, spec, log):
    if spec.get("expression_vector") is not None:
        v = np.asarray(spec["expression_vector"], dtype=np.float32)
        assert v.shape == (model.expression_dim,), f"expression dim {v.shape}"
        return v
    names = [str(n).lower() for n in model.expression_names]
    v = np.zeros(model.expression_dim, dtype=np.float32)
    blend = (spec.get("expression") or {}).get("blend", {})
    if not blend and isinstance(spec.get("expression"), dict):
        p = spec["expression"].get("preset")
        if p:
            blend = {p: float(spec["expression"].get("weight", 1.0))}
    for name, w in blend.items():
        key = str(name).lower()
        hits = [i for i, n in enumerate(names) if key in n]
        if not hits:
            log(f"WARNING: expression '{name}' not in GNM names — skipped")
            continue
        v[hits[0]] += float(w)
        log(f"expression '{name}' -> dim {hits[0]} ({names[hits[0]]}) w={w}")
    # Prefer the TF semantic sampler when the spec used semantic class names
    # and TF is available — raw index mapping above already covers the rest.
    return v


# ---------------------------------------------------------------- GLB writer
def compute_normals(verts, tris):
    n = np.zeros_like(verts)
    v0, v1, v2 = verts[tris[:, 0]], verts[tris[:, 1]], verts[tris[:, 2]]
    fn = np.cross(v1 - v0, v2 - v0)
    np.add.at(n, tris[:, 0], fn)
    np.add.at(n, tris[:, 1], fn)
    np.add.at(n, tris[:, 2], fn)
    l = np.linalg.norm(n, axis=1, keepdims=True)
    n /= np.maximum(l, 1e-12)
    return n.astype(np.float32)


def write_glb(path, verts, tris, uvs, joint_names, joint_pos, joint_parents,
              skin_w):
    """Minimal GLB: one skinned mesh, joint hierarchy, inverse bind matrices."""
    V, J = verts.shape[0], len(joint_names)
    pos = np.asarray(verts, dtype=np.float32)
    nrm = compute_normals(pos, tris)
    uv = np.asarray(uvs, dtype=np.float32)
    idx = np.asarray(tris, dtype=np.uint32).reshape(-1)

    # per-vertex top-4 skin influences
    w = np.asarray(skin_w, dtype=np.float32)          # (J, V)
    order = np.argsort(-w, axis=0)[:4, :]             # (4, V)
    j4 = order.T.astype(np.uint16)                     # (V, 4)
    w4 = np.take_along_axis(w, order, axis=0).T        # (V, 4)
    w4 /= np.maximum(w4.sum(axis=1, keepdims=True), 1e-12)

    # inverse bind matrices (bind pose = template joint translations)
    ibm = np.zeros((J, 16), dtype=np.float32)
    for j in range(J):
        m = np.eye(4, dtype=np.float32)
        m[:3, 3] = -joint_pos[j]
        ibm[j] = m.reshape(-1)

    # pack buffer
    chunks = [pos.tobytes(), nrm.tobytes(), uv.tobytes(), idx.tobytes(),
              j4.tobytes(), w4.tobytes(), ibm.tobytes()]
    blob = b"".join(chunks)
    offs, views, accs = [], [], []

    def add_view(data, target=None):
        o = sum(len(c) for c in chunks[:len(offs)])
        views.append({"buffer": 0, "byteOffset": o,
                      "byteLength": len(data)} | ({"target": target} if target else {}))
        offs.append(data)
        return len(views) - 1

    def add_acc(view, ctype, ctype_n, count, mn=None, mx=None):
        a = {"bufferView": view, "componentType": ctype, "count": count,
             "type": ctype_n}
        if mn is not None:
            a["min"], a["max"] = mn, mx
        accs.append(a)
        return len(accs) - 1

    v_pos = add_view(chunks[0], 34962)
    v_nrm = add_view(chunks[1], 34962)
    v_uv = add_view(chunks[2], 34962)
    v_idx = add_view(chunks[3], 34963)
    v_j = add_view(chunks[4], 34962)
    v_w = add_view(chunks[5], 34962)
    v_ibm = add_view(chunks[6])
    a_pos = add_acc(v_pos, 5126, "VEC3", V,
                    pos.min(0).tolist(), pos.max(0).tolist())
    a_nrm = add_acc(v_nrm, 5126, "VEC3", V)
    a_uv = add_acc(v_uv, 5126, "VEC2", V)
    a_idx = add_acc(v_idx, 5125, "SCALAR", idx.shape[0])
    a_j = add_acc(v_j, 5123, "VEC4", V)
    a_w = add_acc(v_w, 5126, "VEC4", V)
    a_ibm = add_acc(v_ibm, 5126, "MAT4", J)

    # joint hierarchy: parent==self -> root
    children = [[] for _ in range(J)]
    roots = []
    for j, p in enumerate(joint_parents):
        p = int(p)
        if p == j or p < 0 or p >= J:
            roots.append(j)
        else:
            children[p].append(j)
    nodes = []
    for j in range(J):
        nodes.append({
            "name": str(joint_names[j]),
            "translation": [float(x) for x in joint_pos[j]],
            "children": children[j],
        })
    mesh_node = len(nodes)
    nodes.append({"name": "gnm_head", "mesh": 0, "skin": 0})
    scene_roots = [mesh_node] + roots

    doc = {
        "asset": {"version": "2.0",
                  "generator": "western-heart gnm job (google/GNM, Apache-2.0)"},
        "scene": 0,
        "scenes": [{"nodes": scene_roots}],
        "nodes": nodes,
        "meshes": [{"name": "gnm_head", "primitives": [{
            "attributes": {"POSITION": a_pos, "NORMAL": a_nrm,
                           "TEXCOORD_0": a_uv,
                           "JOINTS_0": a_j, "WEIGHTS_0": a_w},
            "indices": a_idx, "material": 0}]}],
        "skins": [{"name": "gnm_skin", "skeleton": roots[0] if roots else 0,
                   "joints": list(range(J)),
                   "inverseBindMatrices": a_ibm}],
        "materials": [{"name": "gnm_skin_mat",
                       "pbrMetallicRoughness": {"baseColorFactor": [0.72, 0.55, 0.47, 1.0],
                                                "roughnessFactor": 0.65}}],
        "accessors": accs,
        "bufferViews": views,
        "buffers": [{"byteLength": len(blob)}],
    }
    js = json.dumps(doc, separators=(",", ":")).encode()
    js += b" " * ((4 - len(js) % 4) % 4)
    blob_padded = blob + b"\x00" * ((4 - len(blob) % 4) % 4)
    total = 12 + 8 + len(js) + 8 + len(blob_padded)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A))
        f.write(js)
        f.write(struct.pack("<II", len(blob_padded), 0x004E4942))
        f.write(blob_padded)
    return {"verts": V, "tris": tris.shape[0], "joints": J}


# ---------------------------------------------------------------- entry point
def run_job(spec, log):
    log("GNM head-bake job starting")
    model = load_model(spec, log)
    log(f"model: V={model.num_vertices} J={model.num_joints} "
        f"I={model.identity_dim} E={model.expression_dim}")

    ident = resolve_identity(model, spec, log)
    expr = resolve_expression(model, spec, log)

    jr = np.zeros((model.num_joints, 3), dtype=np.float32)
    for name, aa in (spec.get("joint_rotations") or {}).items():
        jnames = [str(n) for n in model.joint_names]
        if name in jnames:
            jr[jnames.index(name)] = np.asarray(aa, dtype=np.float32)
            log(f"joint {name} axis-angle {aa}")
    tr = np.asarray(spec.get("translation", [0, 0, 0]), dtype=np.float32)

    log("evaluating GNM mesh function")
    verts = np.asarray(model(identity=ident, expression=expr,
                             rotations=jr, translation=tr), dtype=np.float32)
    tris = np.asarray(model.triangles, dtype=np.int64)
    # per-vertex uvs from triangle uvs (first occurrence wins)
    tuv = np.asarray(model.triangle_uvs, dtype=np.float32).reshape(-1, 2)
    uv = np.zeros((model.num_vertices, 2), dtype=np.float32)
    uv[tris.reshape(-1)] = tuv

    out = spec["out"]
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    log(f"writing GLB {out}")
    info = write_glb(
        out, verts, tris, uv,
        [str(n) for n in model.joint_names],
        np.asarray(model.template_joint_positions, dtype=np.float32),
        np.asarray(model.joint_parent_indices, dtype=np.int64),
        np.asarray(model.skinning_weights, dtype=np.float32),
    )
    log(f"done: {info}")
    return {"glb": out, **info}


if __name__ == "__main__":
    def _log(m):
        print(f"[gnm] {m}", flush=True)
    spec = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else json.load(sys.stdin)
    print(json.dumps(run_job(spec, _log)))
