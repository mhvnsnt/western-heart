# BUILD-LOG — Western Heart (resume point for Muse / any agent)

Lane ownership is claimed on #866. MoneyManBusch owns: Pantera and the core-8 chat-owned animation wiring, the Tekken 7 bank extraction (`tools/anim/t7_*`), and the PR queue. Muse owns #1096 and its stack, the moves audit, and `tools/auto_rig`.

## 2026-10-30 — King's real T7 stance on Pantera (Claude, owner-approved mannequin run)

- **Shipped first real T7 clip in the game.** Pantera idles in King's actual Tekken 7 stance (kinrotsm clip 132 `nakg_kg2kam`, 0xC8), not the T3 slot-3 stance.
- **Bake path:** `tools/anim/t7_c8_stance_bake.py` runs Koenji's mannequin plus Kiloutre's `applyRotationFromAnimdata` (the 18:00 control path), then converts to `wh-anim/1`. FK self-check: 0.000000 m.
- **Data:** `game/assets/anim/t7/king/`. **Wiring:** `game/js/t3anims.js` `T7_STANCES` / `applyT7Stance()`, Pantera only.
- **Reusable for any 0xC8 clip.** 0x64 (all attacks) still needs the joint frame; see `docs/anim/T7-0x64-FRAME-RESEARCH-2026-10-30.md`.

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

## 2026-10-29 17:50 CDT: move → real T7 clip map (Pantera/King)
- #1226 (decoder) merged.
- `tools/anim/t7_clipmap.py` joins the motbin JSON with `<code>rotsm.arc`: `anim_id & 0xC000 == 0x4000` gives `rotsm.arc` MOTA block 0, index `anim_id & 0x3FFF`.
- King: 467 of 552 attacks (85%) resolve to real decodable clips, with 0 errors. The other 71 attacks use the 0x8000 common bank and 14 use the inline bank. Those are gaps, filled with T3/VF5.
- Kinematic check: the 1,2 jab clip 315 has its arm peak at frame 8 (active frame 10). The 1+2 arm peak is at frame 10 (active 12). Right kick 318 is leg-dominant with its peak at frame 11 (active 13).
- GRE has no 0x8000 character bank (only Mob/Demo motion). Confirmed gap.
- Proof: `docs/proof/t7-clipmap-king-pantera.json`.
- Next: bake (quaternions + spike filter) to `wh-anim/1` on the WH rig and wire it for Pantera. After that: first-play gaps (stages, flow, HUD, results, rematch, sound) per owner t358u.
- Muse: moves lane and tools/auto_rig untouched.

## 2026-10-29 18:00 CDT: 0xC8 vs 0x64 pose finding (MoneyManBusch)

- **Control:** King `kinrotsm.arc` 0xC8 clips (raw floats), applied with the community `applyRotationFromAnimdata` onto Koenji's TekkenMannequin in headless Blender, give a correct upright pose. So the importer and mannequin path is fine.
- **Problem:** 0x64 clips (all attacks), decoded with `tools/anim/t7_anim64.py`, come out crumpled. That includes frame 1, the base pose, where no bitstream is involved.
- **Already ruled out:** descriptor layout (the first 23 bones are identical in both formats; 0x64 only appends bones), endianness (matches TKMovesets `Byteswap64Animation`), Euler order, inverse rotation, axis signs and permutations, rotvec. The best fit is still ~54° mean error.
- **Clues:** the hinge sign is flipped (slot 11: 0xC8 −1.56 vs 0x64 +1.61); slot 6 is a length-400 vector in both formats but in a different direction. The likely cause is a per-bone reference frame that 0x64 is stored relative to.
- **UE AnimSequences:** GRE pakchunk1 has none for King or any fighter move (only story/cloth/mob), so that route can't supply attacks.
- **Next:** find the community-documented 0x64 joint frame (TKMovesets / BlenderTekkenDirect / modding notes) and apply it. No guessed rotations ship.
