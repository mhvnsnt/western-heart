# BUILD-LOG — Western Heart (resume point for Muse / any agent)

Lane ownership is claimed on #866. MoneyManBusch owns: Pantera and the core-8 chat-owned animation wiring, the Tekken 7 bank extraction (`tools/anim/t7_*`), and the PR queue. Muse owns #1096 and its stack, the moves audit, and `tools/auto_rig`.

## 2026-10-29 — T7 0x64 animation decoder (MoneyManBusch)

- **What landed:** `tools/anim/t7_anim64.py` is a pure-Python decoder for Tekken 7 compressed (0x64) animations inside MOTA blocks, big- or little-endian.
  - It's a port of the TKMovesets2 `Utils/Animations_T_x64.cpp` `ParseAnimation0x64` routine (Kiloutre, GPL-3.0), which is a decompilation of the T7 runtime routine.
  - The Blender Tekken importer only reads 0xC8, and no other public 0x64 decoder exists.
- **Fix over upstream:** the keyframe table holds `(len+14)>>4` entries. Upstream reads one past the table on the last frame when `(len-1)%16==0`; the decoder clamps it.
- **Proof** (`docs/proof/t7-anim64-king-rotsm.json`): King `kinrotsm.arc` (GRE `teardown/tekken7-steam/tkdata/mothead/mask/`):
  - 6 MOTA blocks
  - 1031 0x64 clips plus 123 0xC8 clips
  - 150,531 frames
  - 0 decode errors
  - Every clip is a full-body, 23-bone clip. Bones 0–1 are float root translations (mm, height ~1100); the rest are short Euler rotations.
- **Caveat:** 0.43% of frame steps exceed 0.5 rad. All of them are on the Y axis of end bones (hands and feet) at ±π/2, which is gimbal, not corruption. The bake stage must convert to quaternions and spike-filter.
- **How to run:** `python3 tools/anim/t7_anim64.py <file-with-MOTA> [report.json]`. It exits non-zero on any decode error. Raw game files stay in GRE.

## Bank coverage (motbin move+0x10 anim id)

| Bank | Source | Status |
|---|---|---|
| 0x0000 | `mot.bin` MotaList slot 0 | decodable with this tool |
| 0x4000 | `<code>rotsm.arc` | decodable with this tool; 22–37% of moves for the measured characters |
| 0x8000 | main character anims; not in tkdata (pakchunk / live memory only) | gap. Plan: best community-extracted alternative, then T3/VF5 fill, documented here |

## Next steps

1. T7 23-bone to WH rig bone map, then bake to `wh-anim/1` (quaternion + spike filter).
2. Wire the baked clips into `_attackClipPlan` ahead of donor/match, for core-8 chat-owned fighters only.
3. Pipeline script that regenerates and validates (decode, then bake, then skin-deformation check).
