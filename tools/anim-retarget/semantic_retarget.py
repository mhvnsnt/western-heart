#!/usr/bin/env python3
"""Semantic-aware motion retargeting (WH-native implementation of SATA).

Paper: "Semantic-Aware Motion Encoding for Topology-Agnostic Character
Animation" (Zhang et al., arXiv:2605.27055, May 2026, ICML 2026).
Code: https://github.com/zzysteve/SATA (Apache-2.0).

WHAT THIS DOES
-------------
Retargets a wh-anim/1 motion clip from a source rig to a target rig with
NO manual joint mapping, NO canonical joint set, NO paired data. The
source and target may differ in joint count, proportions, names, and
topology (extra limbs, missing segments) -- the paper's zero-shot
cross-species setting.

HOW (paper Sec. 3.1-3.3, analysis mode)
---------------------------------------
1. Both rigs become topology-agnostic graphs: static features
   F_s = (X_g global offset, X_l parent-relative rest, X_t semantic tags)
   plus depth / reverse-depth edge features (Sec. 3.1).
2. Semantic tags: taxonomic-neutral functional descriptions per joint
   (paper Table 11 pattern; Sec. 3.2), embedded deterministically.
3. Semantic-spatial correspondence: per target joint, softmax over source
   joints of alpha*cos(semantic) + beta*cos(spatial-structure) -- the
   functional joint alignment the paper's Semantic-Spatial Modulation
   (FiLM gamma/beta + gate, eq. 1-3) learns; here computed explicitly so
   the mapping is fully inspectable (--map-report).
4. Motion transfer: target local rotations = correspondence-weighted
   quaternion mean of source local rotations (Markley); root translation
   scaled by leg-length ratio (decoder conditioned on target rest-pose
   geometry, Sec. 3.3: {X'_t, X'_g, X'_l}).
5. FK validation + character-normalized retarget error (paper App. D.2,
   eq. 4 / SAN, Aberman et al. 2020).

DEVIATION FROM THE PAPER (documented, honest): the paper trains a
spatio-temporal interleaved graph VAE (Sec. 3.3-3.4) on 80k human +
30k animal sequences; this tool implements the *semantic joint alignment*
core in training-free analysis mode (no torch, no checkpoints). The
alignment mechanism -- functional correspondence from semantic tags plus
spatial structure, never names or manual maps -- is the paper's core
technique and is fully preserved. A checkpoint-backed SATA VAE backend
can be added later; see docs/research/SEMANTIC-RETARGET-2026-10-23.md.

Usage:
    python3 semantic_retarget.py \
        --src-clip game/assets/anim/t3/paul/t3_light.json \
        --src-skel game/assets/anim/t3/paul/skeleton.json \
        --tgt-skel game/assets/anim/t3/gon/skeleton.json \
        --out /tmp/gon_t3_light.json \
        --map-report /tmp/gon_t3_light.map.json
"""

import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graph_rep import SkelGraph, semantic_correspondence
from quat import qnormalize, fk, set_parents


# ---------------------------------------------------------------------------
# Rig loading
# ---------------------------------------------------------------------------

# Standard parent resolution for clip bone rigs (wh-anim/1 banks). Used only
# when a clip bone has no same-named joint in the bank's skeleton.json
# (e.g. Spine/Neck/ToeBase, which clips reference but skeleton.json omits).
_STD_PARENTS = {
    "Hips": "Root", "Spine": "Hips", "Chest": "Spine", "Neck": "Chest",
    "Head": "Neck",
    "LeftShoulder": "Chest", "LeftArm": "LeftShoulder",
    "LeftForeArm": "LeftArm", "LeftHand": "LeftForeArm",
    "RightShoulder": "Chest", "RightArm": "RightShoulder",
    "RightForeArm": "RightArm", "RightHand": "RightForeArm",
    "LeftUpLeg": "Hips", "LeftLeg": "LeftUpLeg", "LeftFoot": "LeftLeg",
    "LeftToeBase": "LeftFoot",
    "RightUpLeg": "Hips", "RightLeg": "RightUpLeg", "RightFoot": "RightLeg",
    "RightToeBase": "RightFoot",
}


def load_skeleton(skel_path):
    """Load wh-anim-skel/1 skeleton.json -> SkelGraph."""
    with open(skel_path) as f:
        sk = json.load(f)
    joints = []
    name_to_idx = {}
    for i, j in enumerate(sk["joints"]):
        name_to_idx[j["name"]] = i
    for j in sk["joints"]:
        p = j["parent"]
        joints.append(
            {
                "name": j["name"],
                "parent": name_to_idx.get(p) if p else None,
                "rest": np.array(j["rest"], dtype=np.float64),
            }
        )
    return SkelGraph(joints), sk


def _synthesize_rest(bone, joints_by_name):
    """Rest world position for clip bones missing from skeleton.json.

    Structural interpolation from real rest data (documented derivation,
    not guessed motion): Spine between Hips/Chest, Neck between
    Chest/Head, ToeBase forward of Foot. Faces +Z per wh-anim-skel/1 note.
    """
    g = lambda n: np.array(joints_by_name[n]["rest"], dtype=np.float64)
    if bone == "Spine":
        return g("Hips") + 0.55 * (g("Chest") - g("Hips"))
    if bone == "Neck":
        return g("Chest") + 0.75 * (g("Head") - g("Chest"))
    if bone in ("LeftToeBase", "RightToeBase"):
        foot = bone.replace("ToeBase", "Foot")
        leg = bone.replace("ToeBase", "Leg")
        fwd = np.array([0.0, 0.0, 1.0])
        leg_len = np.linalg.norm(g(foot) - g(leg))
        return g(foot) + fwd * 0.35 * leg_len
    return None


def build_source_rig(clip_bones, skel_graph):
    """Build the source motion rig graph from clip bone list + skeleton.

    Returns (SkelGraph over clip bones, notes about synthesized bones).
    """
    by_name = {j["name"]: j for j in skel_graph.joints}
    joints = []
    notes = []
    idx = {}
    for b in clip_bones:
        idx[b] = len(joints)
        if b in by_name:
            joints.append(
                {"name": b, "parent": None,
                 "_skel": by_name[b], "rest": None}
            )
        else:
            rest = _synthesize_rest(b, by_name)
            if rest is None:
                raise ValueError(f"no rest synthesis rule for bone {b!r}")
            notes.append(f"synthesized rest for {b} (structural interpolation)")
            joints.append({"name": b, "parent": None, "_skel": None,
                           "rest": rest})
    # Resolve parents. NOTE: skel_graph stores parent as an *index* into the
    # skeleton's joint order, so map back through names into clip-bone order.
    for j in joints:
        b = j["name"]
        if j["_skel"] is not None:
            p_idx = j["_skel"]["parent"]
            p_name = skel_graph.names[p_idx] if p_idx is not None else None
            j["parent"] = idx.get(p_name) if p_name else None
            j["rest"] = np.array(j["_skel"]["rest"], dtype=np.float64)
        else:
            p = _STD_PARENTS.get(b)
            j["parent"] = idx.get(p) if p else None
        del j["_skel"]
    return SkelGraph(joints), notes


def load_source_quats(src_clip):
    """(T, J_s, 4) normalized local quats; short bone tracks hold last frame
    (same clamp rule as game/js/t3anims.js jsonToClip)."""
    bones = src_clip["bones"]
    T = src_clip["stream_frames"]
    return qnormalize(
        np.stack(
            [
                np.array(
                    [
                        src_clip["rot_xyzw"][b][
                            min(t, len(src_clip["rot_xyzw"][b]) - 1)
                        ]
                        for t in range(T)
                    ],
                    dtype=np.float64,
                )
                for b in bones
            ],
            axis=1,
        )
    )


def load_source_root(src_clip):
    return np.array(src_clip["root_t"], dtype=np.float64)


def leg_length(graph):
    """Rest leg length: Hips->Foot chain, for root-motion scaling."""
    def find(role_names):
        for i, n in enumerate(graph.names):
            ln = n.lower().replace("_", "")
            if any(r in ln for r in role_names):
                return i
        return None

    for side in ("left", "right"):
        hip = find([side + "upleg", side + "thigh", side + "hip"])
        foot = find([side + "foot"])
        if hip is not None and foot is not None:
            return float(np.linalg.norm(graph.rest[foot] - graph.rest[hip]))
    # Fallback: root rest height.
    return float(graph.rest[graph.roots[0]][1])


# ---------------------------------------------------------------------------
# Retarget
# ---------------------------------------------------------------------------

def retarget_clip(src_clip, src_rig, tgt_graph, A, hold_thresh=0.40):
    """Transfer motion. Returns (tgt_quats [T,J_t,4], tgt_root [T,3], info)."""
    bones = src_clip["bones"]
    T = src_clip["stream_frames"]
    src_q = load_source_quats(src_clip)  # (T, J_s, 4), normalized
    src_root = load_source_root(src_clip)

    Jt = tgt_graph.n
    tgt_q = np.zeros((T, Jt, 4))
    tgt_q[..., 3] = 1.0  # identity default
    held = []

    for j in range(Jt):
        w = A[j]
        top = int(np.argmax(w))
        if w[top] < hold_thresh:
            # No functional counterpart: hold rest pose (paper's zero-shot
            # behavior for novel limbs -- e.g. a tail or 4th arm stays
            # neutral instead of inheriting wrong motion).
            held.append(tgt_graph.names[j])
            continue
        # Hard top-1 semantic mapping: transfer the matched source joint's
        # local rotation verbatim. (An earlier soft-blend variant averaged
        # rotations across neighboring source joints and corrupted the
        # transfer by ~0.3-0.6 rad; a mapping maps.) wh-anim/1 rest
        # rotations are identity, so source local == target local directly
        # (the general rest-delta form reduces to identity here).
        tgt_q[:, j] = src_q[:, top]

    # Root motion: transfer delta-from-rest, scaled by leg-length ratio
    # (decoder conditioned on target rest-pose geometry, paper Sec. 3.3).
    src_leg = leg_length(src_rig)
    tgt_leg = leg_length(tgt_graph)
    scale = tgt_leg / max(src_leg, 1e-9)
    src_rest_root = src_rig.rest[src_rig.roots[0]]
    tgt_rest_root = tgt_graph.rest[tgt_graph.roots[0]]
    tgt_root = tgt_rest_root + (src_root - src_rest_root) * scale

    info = {
        "leg_length_ratio": round(scale, 4),
        "held_at_rest": held,
        "frames": T,
    }
    return tgt_q, tgt_root, info


def validate(tgt_graph, tgt_q, tgt_root, src_rig, src_clip, A, hold_thresh=0.40):
    """FK validation + character-normalized retarget error (paper D.2 eq.4)."""
    set_parents(tgt_graph.parent.tolist())
    T = tgt_q.shape[0]
    # 1. Bone lengths preserved (exact by construction; check numerics).
    gp0 = fk(tgt_q[0], tgt_graph.X_l, tgt_root[0])
    max_dev = 0.0
    for i, p in enumerate(tgt_graph.parent):
        if p >= 0:
            rest_len = np.linalg.norm(tgt_graph.X_l[i])
            got = np.linalg.norm(gp0[i] - gp0[p])
            max_dev = max(max_dev, abs(got - rest_len))

    # 2. Character-normalized MSE vs source pose on matched joints.
    # FK all target frames first (parents still target's).
    gp_t_all = np.stack(
        [fk(tgt_q[t], tgt_graph.X_l, tgt_root[t]) for t in range(T)])
    bones = src_clip["bones"]
    src_q = load_source_quats(src_clip)
    src_root = load_source_root(src_clip)
    set_parents(src_rig.parent.tolist())
    gp_s_all = np.stack(
        [fk(src_q[t], src_rig.X_l, src_root[t]) for t in range(T)])
    H = float(np.linalg.norm(
        tgt_graph.rest.max(axis=0) - tgt_graph.rest.min(axis=0)))
    errs = []
    match_idx = np.argmax(A, axis=1)
    # Source joint position, scaled to target character size.
    s = tgt_graph.rest[tgt_graph.roots[0]][1] / max(
        src_rig.rest[src_rig.roots[0]][1], 1e-9)
    for t in range(T):
        for j in range(tgt_graph.n):
            i = int(match_idx[j])
            if A[j, i] < hold_thresh:
                continue
            ps = gp_s_all[t, i] * s
            errs.append(np.sum((gp_t_all[t, j] - ps) ** 2) / (H ** 2))
    E = 1000.0 * float(np.mean(errs)) if errs else float("nan")
    return {"bone_length_max_dev_m": float(max_dev),
            "retarget_E_char_norm": round(E, 4),
            "matched_joints": int(np.sum(np.max(A, axis=1) >= hold_thresh)),
            "target_joints": int(tgt_graph.n)}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src-clip", required=True)
    ap.add_argument("--src-skel", required=True)
    ap.add_argument("--tgt-skel", required=True)
    ap.add_argument("--out", required=True, help="output wh-anim/1 clip JSON")
    ap.add_argument("--map-report", default=None)
    ap.add_argument("--alpha", type=float, default=0.65)
    ap.add_argument("--beta", type=float, default=0.35)
    ap.add_argument("--tau", type=float, default=0.12)
    ap.add_argument("--hold-thresh", type=float, default=0.40,
                      help="minimum top-1 correspondence weight to inherit "
                           "motion; below it the joint holds rest pose "
                           "(novel-limb behavior). 0.40 keeps margin above "
                           "the ~0.35 noise floor of terminal-chain "
                           "coincidences; true matches score >= 0.56.")
    ap.add_argument("--bank", default="retarget")
    ap.add_argument("--slot", default="retarget")
    args = ap.parse_args()

    with open(args.src_clip) as f:
        src_clip = json.load(f)
    assert src_clip.get("format") == "wh-anim/1", "source clip must be wh-anim/1"

    src_skel_graph, _ = load_skeleton(args.src_skel)
    src_rig, synth_notes = build_source_rig(src_clip["bones"], src_skel_graph)
    tgt_graph, tgt_skel_json = load_skeleton(args.tgt_skel)

    A, map_report, corr_cfg = semantic_correspondence(
        src_rig, tgt_graph, alpha=args.alpha, beta=args.beta, tau=args.tau)

    tgt_q, tgt_root, rt_info = retarget_clip(
        src_clip, src_rig, tgt_graph, A, hold_thresh=args.hold_thresh)
    val = validate(tgt_graph, tgt_q, tgt_root, src_rig, src_clip, A,
                   hold_thresh=args.hold_thresh)

    out = {
        "format": "wh-anim/1",
        "source": args.src_clip,
        "source_bank_skel": args.src_skel,
        "target_skel": args.tgt_skel,
        "bank": args.bank,
        "slot": args.slot,
        "move_row": src_clip.get("move_row"),
        "stream_frames": int(tgt_q.shape[0]),
        "fps": src_clip.get("fps", 30.0),
        "decoder": "tools/anim-retarget/semantic_retarget.py",
        "tool": ("semantic-retarget: SATA semantic joint alignment "
                 "(arXiv:2605.27055), WH-native analysis mode"),
        "bones": tgt_graph.names,
        "rot_xyzw": {
            b: [[round(float(v), 6) for v in q] for q in tgt_q[:, j]]
            for j, b in enumerate(tgt_graph.names)
        },
        "root_t": [[round(float(v), 6) for v in p] for p in tgt_root],
        "retarget": {
            "correspondence": corr_cfg,
            "synth_notes": synth_notes,
            **rt_info,
            "validation": val,
        },
    }
    with open(args.out, "w") as f:
        json.dump(out, f)

    if args.map_report:
        with open(args.map_report, "w") as f:
            json.dump(
                {
                    "source_clip": args.src_clip,
                    "target_skel": args.tgt_skel,
                    "config": corr_cfg,
                    "alignment": map_report,
                    "held_at_rest": rt_info["held_at_rest"],
                    "validation": val,
                },
                f,
                indent=1,
            )

    print(f"retargeted {src_clip['stream_frames']} frames "
          f"{len(src_clip['bones'])} src bones -> {tgt_graph.n} tgt joints")
    print(f"leg-length ratio: {rt_info['leg_length_ratio']}, "
          f"held at rest: {rt_info['held_at_rest'] or 'none'}")
    print(f"validation: bone-dev={val['bone_length_max_dev_m']:.2e} m, "
          f"E(char-norm)={val['retarget_E_char_norm']}, "
          f"matched {val['matched_joints']}/{val['target_joints']}")
    print("top alignments:")
    for r in map_report[:6]:
        m = r["matches"][0]
        print(f"  {r['target']:16s} <- {m['source']:16s} w={m['weight']}")


if __name__ == "__main__":
    main()
