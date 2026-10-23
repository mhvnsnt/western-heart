# Tekken 3 — hand/arm rigging + posing reference

Source: teardown/tekken3/ — USA SLUS_004.02 verified tables and parsers
(tools/local/usa_tables.py, usa_motion.py, pose_assemble.py, kmd_parse.py).

## Rig architecture: rigid parts, NOT bones

Tekken 3 has **no bone skeleton at all**. Fighters are 18 rigid KMD part meshes
(parts 0..17) + 4 costume-attachment rows, posed by 18 matrix slots driven from
the USA motion banks (divmot*.bin).

- Part -> KMD row (EXE 0x8001A05C): [0, 1, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24]
- Part -> matrix slot (EXE 0x8001A074): [0, 1, 11, 12, 13, 14, 15, 16, 17, 3, 4, 5, 6, 7, 8, 9, 10, 2, 18, 19, 20, 21]
- KMD = 27 rows; each row carries verts/faces, a joint offset (jx, jy, jz) and a parent index.
- Per-part local matrix = animation rotation (bit-exact AnimDecodePose port) x KMD joint offset (x, y, -z).
- Channel shift: 49 bytes == [1]*15 + [5]*34 (USA verified, JP-identical).

## Hands: ZERO finger articulation

- **No finger bones exist in Tekken 3.** Hands are single rigid parts.
- Fist vs open hand is **baked into the part geometry** — there is no pose to change.
- Hand posing = whole-hand rotation at the wrist slot only.
- This is why T3-era ports read as "mitten hands": they are.

## Arm posing (stance/idle)

- Arm pose comes from the motion-bank Euler slots; the stance is move-index
  slots 0-2 of each fighter's divmot bank (common bank divmot99_common.bin for shared moves).
- Win poses: same mechanism — pick the win move's slot and sample frames.

## What WH takes from this

- T3 is the negative reference for hands: if a WH fighter's hands look like
  mittens, check that finger chains (a) exist, (b) are weighted, (c) are driven
  by the move animation — T3 had none of the three.
- The wrist-slot rotation model is still how T3-era idle/win hand motion works;
  port any T3 motion with hand movement = wrist rotation only.
