# Example: GameRig backend on Baek "Master White" (workflow log)

First production run of the `gamerig` backend (`tools/auto_rig/backends/gamerig_backend.py`), 2026-10-20.

## Input (verified unrigged static)

`roster/baek/attires/master-white/baek-master-white.glb` — Tripo static,
469,640 bytes, 3,962 verts, 35 mesh parts, 35 materials with baseColor
textures. Verified from its glTF JSON before rigging: **0 skins,
0 joints, 0 animations** (a separate `baek-master-white-rigged.glb`
sibling exists and was deliberately NOT used).

## Command

```bash
python3 tools/auto_rig/auto_rig.py \
    --in roster/baek/attires/master-white/baek-master-white.glb \
    --out baek-master-white_gamerig.glb --backend gamerig \
    --donor assets/free-pull-1/cmu-mocap/fighting/135_04.bvh \
    --clip CMU135_04_boxing --clip-start 240 --clip-frames 72 \
    --clip-step 4
```

(Blender 4.0.2 headless under xvfb; GameRig installed from
`tools/open-source/gamerig` as a Rigify feature set.)

## Outputs in this folder

| File | What it is |
|---|---|
| `baek-master-white_gamerig.glb` | Rigged + animated output: 1 skin, **73 joints** (WH canonical names), 1 clip (`CMU135_04_boxing`, 72 frames), textures intact. md5 `c2698b6bd70184b59e6edd904ebc8ae5`, reproduced byte-identically in 3 runs. |
| `metrics.json` | Backend metrics: normalize (scale 78.43, height 1.80 m), fit, 73 DEF bones, DEF-hierarchy check clean, clip map (26 donor bones mapped, rest inherit). |
| `proof_bind_tpose.png` | Workbench render of the rig-only export at bind pose (clean textured T-pose). |
| `proof_clip_stance_f000.png` | Frame 0 of the baked clip: fighting stance — NOT a T-pose. |
| `proof_clip_kick_f035.png` | Frame 35 of the baked clip: high kick from the CMU boxing take. Limbs attached, no tearing. |
| `anim_check_report.json` | Full `anim_check.py` report (see notes below). |

All three proof frames were viewed by the agent who produced them.

## Validation summary (honest)

- glTF-level: valid, skinned, 73 canonical joints, all validate.py
  required bones present (`missing_bones: []`).
- `validate.py`: passes glTF/skin/bones; its `height_ok` reads only
  `meshes[0].primitives[0]` (a 0.24 m accessory part on this 35-part
  model) — true height is 1.80 m per metrics + full-scene bounds.
- `anim_check.py` on the clip: root deviation 0.0 m (in-place),
  edge-stretch p99.9 = 1.59 (pass). Two flags, both analyzed in
  `tools/open-source/gamerig/USAGE.md`: zero-rest-length pelvis
  helper bones (Rigify artifact; translation channels are constant
  (0,0,0)) and relative-median tearing spikes at one fast mocap
  instant (max displacement 0.32 m < 0.35 m absolute threshold).
  For calibration, the repo's production `pantera.glb` fails the
  same checker harder (root wanders 8.21 m, edge p99.9 = 11.27).
