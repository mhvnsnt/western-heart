#!/usr/bin/env python3
"""
kaggle_batch_retarget.py — BATCH animation retargeting skeleton (NOT a finished retargeter).

SCOPE, HONESTLY STATED
----------------------
This file is a STRUCTURE + TODO skeleton, as tasked. It LOADS and
VALIDATES the real clip formats in the repo and computes the bone-map
that retargeting needs — but it does NOT yet write retargeted GLB
animations, because the target rigs do not exist yet: UniRig predicts a
fresh skeleton per character (bone NAMES and COUNT are model outputs,
not known in advance), so a name-to-name map cannot be finalized until
the first Kaggle UniRig run returns real joint names.

Run it on Kaggle AFTER kaggle_unirig_notebook.py, in the same working
dir, once rigged GLBs exist:
    python kaggle_batch_retarget.py --clips-dir /kaggle/input/t3-banks \
        --rigs-dir /kaggle/working/unirig_out --report retarget_report.json
    python kaggle_batch_retarget.py --test-local   # no GPU, uses repo banks

SOURCE FORMATS (verified 2026-10-24 against wh-repo/game/assets/anim/t3/)
-------------------------------------------------------------------------
Per-fighter bank folder, e.g. game/assets/anim/t3/anna/:
  * t3_<move>.json  — format "wh-anim/1". Keys that matter here:
      bones:      list of bone names, e.g. ['Root','Hips','Spine','Chest',
                  'Neck','Head','LeftShoulder','LeftArm','LeftForeArm',
                  'LeftHand','RightShoulder','RightArm','RightForeArm',
                  'RightHand','LeftUpLeg','LeftLeg','LeftFoot','LeftToeBase',
                  'RightUpLeg','RightLeg','RightFoot','RightToeBase']
      rot_xyzw:   dict bone -> list of [x,y,z,w] quaternions, one per frame
      root_t:     list of [x,y,z] root translations, one per frame
      stream_frames: int, fps: 30.0, hand_keyed: False
      bank:       teardown .bin path, e.g. divmot17_anna.bin
      source:     "REAL decoded Tekken 3 motion (owner's disc teardown)"
      NOTE: t3anims.js IGNORES root_t (game drives root.position) and
      derives playback length from rot arrays + fps. The King bank is
      special: its stream_frames counts the 60fps source stream (2x its
      stored rot frames) — see stream_frames_note in the clip JSON.
  * skeleton.json — format "wh-anim-skel/1". Rest pose: joints[] with
      {name, parent, rest: [x,y,z]} in glTF space, meters, faces +Z,
      character left = +X. All joint rest rotations are identity.
      Example (anna): 18 joints; (gunjack): 18 joints. Clip bones (22)
      are a SUPERSET of skeleton joints (18): Spine/Neck/ToeBase appear
      in clips but not in every skeleton.json — a retargeter MUST handle
      clip bones with no skeleton counterpart (fold into parent) and
      skeleton joints with no clip data (hold rest pose). Do not assume
      1:1.
  * rows.pack.json / reactions.pack.json — format "wh-anim-pack/1":
      the full move-row bank (rows) and reaction bank, same bone lists,
      fps 30.0, hand_keyed False. These are the BATCH source: one pack
      covers a whole fighter, not one move.
  * hit_frames.json — format "wh-hitframes/1", fps 60, rows keyed by
      move_row with [active_first, active_last, stream_frames,
      attack_word, throw, button]. Retargeting must PRESERVE hit frames
      (they are gameplay data, not decoration) — a retargeted clip that
      drops hit_frames.json is incomplete.
  * Bank folders present (22): anna, armorking, bosconovitch, bryan,
      eddy, forestlaw_on_law, gon, gunjack, heihachi, heihachi_on_jin,
      hwoarang, jin, julia, king_on_pantera_leoman, kuma, law, lei,
      nina, ogre, paul, xiaoyu, yoshimitsu. ~30 t3_*.json clips each
      (king_on_pantera_leoman 32, heihachi_on_jin 26, forestlaw 29).

  * T7 clips: NO equivalent T7 anim bank was found under
    wh-repo/game/assets/anim/ (only t3/ exists there). The task's
    "T3/T7 clips" therefore means: T3 banks now (this file), T7 later
    ONLY when a T7 bank with the same wh-anim/1-style schema lands.
    Do NOT invent a T7 format or assume T7 clips match T3 bone names.

TARGET RIGS (what UniRig returns — TODO, depends on Kaggle output)
------------------------------------------------------------------
  * UniRig skeleton FBX / rigged GLB: bone names come from the model's
    Skeleton Tree Tokenization, e.g. J_Bip_* names in the VRM-style
    merge path (merge.py maps hips/spine/chest/neck/head/upper-leg/
    lower-leg/foot/upper-arm/lower-arm/hand when is_vrm). Humanoid
    UniRig outputs are EXPECTED to be humanoid-ish but the exact names
    per character are unknown until run 1. => map_target_bones() below
    implements the KNOWN, verifiable part (T3->canonical humanoid names
    + the Alisa->Cape bonemap when the target IS Cape Jones) and raises
    a loud TODO for unmapped UniRig names instead of guessing.
  * Cape Jones target: bonemap_alisa_to_capejones.json (160 Alisa source
    entries -> 54 Cape targets, 111 non-null). Chain: T3 clip bone ->
    (canonical humanoid name) -> Alisa name -> Cape target via bonemap.
    The bonemap's own rules apply: shared_drive (ValveBiped.Bip01_Spine4
    drives spine_4 AND chest; Neck drives neck_1 AND neck_2), fold
    (helpers/twists fold into parent; toe chains fold into toe),
    drop (facial/hair/misc -> null; face verts fall back to
    head/jaw/neck by nearest-bone + renormalize), fit (JOINT-FIT
    REQUIRED: Alisa joint coordinates must NOT be used raw — Cape rest
    joint positions are kept, Alisa hierarchy + weight patterns only).
    Blaster_L/R have no Alisa counterpart and stay at rest.

RETARGET MATH (what the finished version must do — TODOs marked)
------------------------------------------------------------------
  1. Load source rest pose (skeleton.json) and target rest pose (from
     the rigged GLB's bind pose / skeleton FBX). Compute per-bone rest
     rotation delta: q_delta = q_target_rest^-1 * q_source_rest.
     (Both rests are identity in T3 skeleton.json, but UniRig rests are
     NOT guaranteed identity — never assume.)
  2. Per frame, per mapped bone: q_out = q_delta * q_clip * q_delta^-1
     (or the equivalent for the target's rotation convention — VERIFY
     against a rendered stance frame before batching, per the project's
     verify-by-playing rule).
  3. Root motion: T3 root_t is IGNORED by the game (t3anims.js note),
     so the retargeter must emit root translation in the SAME convention
     the game expects (currently: game drives root.position) — TODO:
     confirm with the game code before emitting root_t, do not guess.
  4. Hands: hand_keyed=False in ALL checked banks, so finger bones get
     rest pose unless a hand pose is supplied separately. Do NOT invent
     finger animation.
  5. Resample: keep 30fps; do NOT resample to 60fps except for the King
     bank's documented 60fps-stream convention (and then only by the
     rule in stream_frames_note).
  6. Output: one wh-anim/1 JSON per retargeted clip (same schema, new
     "source" + "target_rig" fields, bones = target bone list), PLUS a
     copied hit_frames.json with a note that frame indices are
     unchanged (frame counts must match, else FAIL the job).

GPU NOTE (user directive 2026-10-24: use the GPU for everything)
------------------------------------------------------------------
  Retargeting itself is quaternion math over (frames x bones) arrays —
  small enough for numpy on CPU, and this skeleton runs it on CPU.
  The GPU belongs in the STAGES AROUND it: UniRig rigging (previous
  script), Blender render verification of retargeted poses, and any
  batch render pass. Do NOT claim this file "uses the GPU" for the
  quaternion math; the honest GPU step is the verify render in
  kaggle_unirig_notebook.py's render_turntable(), reused here via
  --verify-render on a sample of retargeted clips (TODO: wire it once
  GLB animation export exists).

WHAT THIS FILE DOES TODAY (implemented + locally tested)
---------------------------------------------------------
  * load_clip(), load_skeleton(), load_pack() with schema validation
  * build_bone_map() for T3 -> canonical -> Cape (via bonemap JSON)
  * audit_bank() — per-fighter coverage report (clips, bones, frames,
    hand_keyed, missing skeleton joints, hit_frames presence)
  * --test-local — runs the audit against the repo banks WITHOUT GPU
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

# Canonical humanoid names used as the pivot between T3 bones and any
# target rig. These are NAME mappings only — no rotations are computed
# here (see TODOs in retarget_clip).
T3_TO_CANONICAL = {
    "Root": "Root", "Hips": "Hips", "Spine": "Spine", "Chest": "Chest",
    "Neck": "Neck", "Head": "Head",
    "LeftShoulder": "LeftShoulder", "LeftArm": "LeftArm",
    "LeftForeArm": "LeftForeArm", "LeftHand": "LeftHand",
    "RightShoulder": "RightShoulder", "RightArm": "RightArm",
    "RightForeArm": "RightForeArm", "RightHand": "RightHand",
    "LeftUpLeg": "LeftUpLeg", "LeftLeg": "LeftLeg",
    "LeftFoot": "LeftFoot", "LeftToeBase": "LeftToeBase",
    "RightUpLeg": "RightUpLeg", "RightLeg": "RightLeg",
    "RightFoot": "RightFoot", "RightToeBase": "RightToeBase",
}
# UniRig VRM-style names seen in merge.py's humanoid mapping, for the
# future target-name normalization step (TODO: confirm against run-1 GLBs).
UNIRIG_VRM_NAMES = {
    "J_Bip_C_Hips", "J_Bip_C_Spine", "J_Bip_C_Chest", "J_Bip_C_Neck",
    "J_Bip_C_Head", "J_Bip_L_UpperLeg", "J_Bip_L_LowerLeg", "J_Bip_L_Foot",
    "J_Bip_R_UpperLeg", "J_Bip_R_LowerLeg", "J_Bip_R_Foot",
    "J_Bip_L_UpperArm", "J_Bip_L_LowerArm", "J_Bip_L_Hand",
    "J_Bip_R_UpperArm", "J_Bip_R_LowerArm", "J_Bip_R_Hand",
}


def _need(d: dict, key: str, where: str):
    if key not in d:
        raise ValueError(f"{where}: missing key {key!r}")
    return d[key]


def load_clip(path: Path) -> dict:
    """Load + validate one wh-anim/1 clip. Returns a summary dict.

    Full rot arrays are NOT copied into the report (they are large);
    the returned dict carries counts + a frame-count consistency check.
    """
    d = json.loads(path.read_text())
    if d.get("format") != "wh-anim/1":
        raise ValueError(f"{path}: format={d.get('format')!r}, want 'wh-anim/1'")
    bones = _need(d, "bones", str(path))
    rot = _need(d, "rot_xyzw", str(path))
    root_t = _need(d, "root_t", str(path))
    n = len(root_t)
    bad = [b for b in bones if len(rot.get(b, [])) != n]
    return {"file": path.name, "format": d["format"],
            "bank": d.get("bank"), "slot": d.get("slot"),
            "move_row": d.get("move_row"),
            "bones": bones, "frames": n, "fps": d.get("fps"),
            "hand_keyed": d.get("hand_keyed"),
            "frame_mismatch_bones": bad,
            "source": d.get("source")}


def load_skeleton(path: Path) -> dict:
    d = json.loads(path.read_text())
    if d.get("format") != "wh-anim-skel/1":
        raise ValueError(f"{path}: format={d.get('format')!r}, want 'wh-anim-skel/1'")
    joints = _need(d, "joints", str(path))
    return {"root": d.get("root"), "root_rest_y": d.get("root_rest_y"),
            "joints": {j["name"]: j for j in joints},
            "joint_names": [j["name"] for j in joints]}


def load_bonemap(path: Path) -> dict:
    """Load bonemap_alisa_to_capejones.json; returns map + rules."""
    d = json.loads(path.read_text())
    m = _need(d, "map", str(path))
    return {"map": m, "rules": d.get("rules", {}),
            "source": d.get("source"), "target": d.get("target")}


def build_bone_map(clip_bones, skeleton_joint_names, bonemap=None,
                   target_is_cape: bool = False) -> dict:
    """Map clip bones -> target bones. Loud about gaps, never guessing.

    Returns {"mapped": {clip_bone: target_bone_or_None},
             "unmapped_clip_bones": [...],       # clip bones w/o target
             "skeleton_joints_without_clip": [...]}.
    With target_is_cape + bonemap: canonical T3 name -> Alisa name is
    the IDENTITY for the shared core names (LeftArm, Hips, ... — the
    bonemap keys include exactly these T3-style names), then bonemap
    gives the Cape target (or a LIST for shared_drive bones, or None
    for drop bones). Without a bonemap, target = canonical name.
    TODO (needs UniRig run-1 output): normalize UniRig's actual joint
    names into this map — do NOT ship a hardcoded UniRig name map until
    real GLBs have been inspected.
    """
    mapped, notes = {}, {}
    for b in clip_bones:
        canon = T3_TO_CANONICAL.get(b)
        if canon is None:
            mapped[b] = None
            notes[b] = "no canonical name"
            continue
        if target_is_cape and bonemap is not None:
            if canon == "Root":
                # Verified 2026-10-24: 'Root' is NOT a bonemap key.
                # Correct, not a gap: Root is the rig root, not a
                # deform bone. Hips -> pelvis carries the hips; root
                # motion is handled separately (see TODO-3).
                mapped[b] = None
                notes[b] = ("rig root, not a deform bone; no bonemap key "
                            "by design")
            elif canon == "Chest":
                # Verified 2026-10-24: 'Chest' is NOT a bonemap key, but
                # the bonemap's shared_drive rule says Spine4 drives
                # BOTH spine_4 AND chest. T3 has no Spine4 bone, so the
                # T3 Chest segment is the only source for Cape 'chest'.
                mapped[b] = "chest"
                notes[b] = "via shared_drive rule (Spine4 -> spine_4 + chest)"
            else:
                mapped[b] = bonemap["map"].get(canon)  # str | list | None
        else:
            mapped[b] = canon
    return {"mapped": mapped, "notes": notes,
            "unmapped_clip_bones": [b for b, t in mapped.items()
                                    if t is None and b != "Root"],
            "root_note": "Root excluded from unmapped: rig root, not deform",
            "skeleton_joints_without_clip": [j for j in skeleton_joint_names
                                             if j not in clip_bones]}


def audit_bank(bank_dir: Path, bonemap=None) -> dict:
    """Audit one fighter bank folder. Never raises on a single bad file."""
    clips, errors = [], []
    for p in sorted(bank_dir.glob("t3_*.json")):
        try:
            clips.append(load_clip(p))
        except Exception as e:
            errors.append({"file": p.name, "error": str(e)})
    skel = None
    skel_path = bank_dir / "skeleton.json"
    if skel_path.exists():
        try:
            skel = load_skeleton(skel_path)
        except Exception as e:
            errors.append({"file": "skeleton.json", "error": str(e)})
    packs = {}
    for pack_name in ("rows.pack.json", "reactions.pack.json"):
        pp = bank_dir / pack_name
        if pp.exists():
            try:
                d = json.loads(pp.read_text())
                packs[pack_name] = {"format": d.get("format"),
                                    "bones": d.get("bones"),
                                    "fps": d.get("fps"),
                                    "bytes": pp.stat().st_size}
            except Exception as e:
                errors.append({"file": pack_name, "error": str(e)})
    hit = bank_dir / "hit_frames.json"
    hit_info = None
    if hit.exists():
        d = json.loads(hit.read_text())
        hit_info = {"format": d.get("format"), "fps": d.get("fps"),
                    "rows": len(d.get("rows", {}))}
    bone_map = None
    if clips and skel:
        bone_map = build_bone_map(clips[0]["bones"], skel["joint_names"],
                                  bonemap, target_is_cape=bool(bonemap))
    return {"bank": bank_dir.name, "clips": len(clips),
            "clip_frames_total": sum(c["frames"] for c in clips),
            "frame_mismatch_clips": [c["file"] for c in clips
                                     if c["frame_mismatch_bones"]],
            "skeleton_joints": skel["joint_names"] if skel else None,
            "packs": packs, "hit_frames": hit_info,
            "bone_map_sample": bone_map, "errors": errors}


def retarget_clip(clip_path: Path, skeleton_path: Path, bonemap_path=None,
                  out_path: Path | None = None) -> dict:
    """TODO — full retarget. Currently: validates inputs + reports the map.

    NOT YET IMPLEMENTED (blocked on real UniRig target joint names):
      TODO-1: read target rest pose from the rigged GLB/FBX bind pose
              (glTF skins + inverseBindMatrices, or FBX skeleton) and
              compute per-bone rest deltas vs skeleton.json rests.
      TODO-2: apply q_out = q_delta * q_clip * q_delta^-1 per frame/bone
              (numpy quaternion arrays; verify rotation convention on a
              rendered stance frame BEFORE batching — project rule:
              verify by playing, not by inspecting JSON).
      TODO-3: decide root_t handling from game code (t3anims.js ignores
              root_t today) and emit it in the game's convention, or
              document why it is dropped.
      TODO-4: write wh-anim/1 output JSON (same schema, bones = target
              list, source/target_rig updated) + copy hit_frames.json
              with unchanged frame indices; FAIL if frame counts differ.
      TODO-5: batch driver over rows.pack.json / reactions.pack.json
              (not just t3_*.json singles) + a --verify-render sample
              reusing kaggle_unirig_notebook.render_turntable().
    Calling this today returns the validated map and raises nothing —
    but writes NO animation file. That is deliberate: a half-baked
    retarget that silently drops bones is worse than an explicit TODO.
    """
    clip = load_clip(clip_path)
    skel = load_skeleton(skeleton_path)
    bm = load_bonemap(bonemap_path) if bonemap_path else None
    bone_map = build_bone_map(clip["bones"], skel["joint_names"], bm,
                              target_is_cape=bool(bm))
    return {"clip": clip["file"], "frames": clip["frames"],
            "bone_map": bone_map,
            "status": "TODO: retarget math not yet implemented (see TODO-1..5); "
                      "no output file written",
            "out_path": str(out_path) if out_path else None}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="T3/T7 batch retarget skeleton")
    p.add_argument("--clips-dir", default=None,
                   help="dir of bank folders (game/assets/anim/t3 layout)")
    p.add_argument("--rigs-dir", default=None,
                   help="UniRig output dir (for future TODO wiring)")
    p.add_argument("--bonemap", default=None,
                   help="bonemap_alisa_to_capejones.json path")
    p.add_argument("--report", default="retarget_report.json")
    p.add_argument("--test-local", action="store_true",
                   help="audit the repo T3 banks and exit (no GPU)")
    args = p.parse_args(argv)

    if args.test_local:
        base = Path.home() / "workspace" / "wh-repo" / "game" / "assets" / "anim" / "t3"
        if not base.exists():
            print(f"repo banks not found at {base}", file=sys.stderr)
            return 2
        bm = None
        bm_path = Path.home() / "workspace" / "ep1-farm" / "bonemap_alisa_to_capejones.json"
        if bm_path.exists():
            bm = load_bonemap(bm_path)
        banks = [audit_bank(d, bm) for d in sorted(base.iterdir())
                 if d.is_dir()]
        print(json.dumps({"banks": banks,
                          "total_clips": sum(b["clips"] for b in banks)},
                         indent=2))
        return 0

    if not args.clips_dir:
        p.error("--clips-dir is required (or use --test-local)")
    base = Path(args.clips_dir)
    bm = load_bonemap(Path(args.bonemap)) if args.bonemap else None
    banks = [audit_bank(d, bm) for d in sorted(base.iterdir())
             if d.is_dir()]
    report = {"banks": banks,
              "total_clips": sum(b["clips"] for b in banks),
              "rigs_dir": args.rigs_dir,
              "note": "audit only — retarget_clip() is TODO (see module docstring)"}
    Path(args.report).write_text(json.dumps(report, indent=2))
    print(f"wrote {args.report} ({report['total_clips']} clips audited)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
