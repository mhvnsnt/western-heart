# TTT2 MOTA per-clip decode spec (2026-11-03)

Source file: `data004/data004-decoded.bin` (6,522,032 B, sha256
`18b18d0ff2356219e9fac852eaa48f6b0a839479ea41f6d4b94069b5f86b2b21`), big table
MOTA @ file offset 256, 1,875 entries. All multi-byte fields are BIG-ENDIAN
(X360). Evidence base: Kiloutre/TekkenMovesetExtractor (vendored in
`kiloutre/`: `ByteSwap.py`, `GUI_TekkenAnimationEditor.py`, `motasearch.py`,
`motbinExport.py`) cross-checked against the real bytes; every claim below
was verified on the data, not assumed.

## Shared facts

- Entry start marker: BE u16 `100` (0x64, compressed) or `200` (0xC8, raw).
  Big table: 1,820 × 100, 42 × 200, 12 shared-offset entries (marker 16384 =
  the byte pair at a shared offset, not a clip start), 1 null slot (index 0).
- Per-track "type" table is a skeleton constant: 23-track skeleton =
  `[11,11,5,7,7,7,11,7,7,7,7,6,7,7,7,6,7,7,6,7,7,6,7]` — byte-identical to
  Kiloutre's hard-coded T5 header in `motbinExport.py` (`animHeaders['t5']`).
  A 25-track variant also occurs (entry 8: 25 tracks, K=4).
- Byte-swap: T7-PC tools store these clips little-endian. Kiloutre's
  `SwapMotaBytes`/`SwapAnimBytes` converts BE→LE by reversing each u16/u32/f32
  field in place (it does NOT change layout). Our decoder reads BE natively;
  equivalence is proven by the cross-check below.

## Type 0xC8 (200) — FULLY DECODED, VALIDATED

| offset | field | type | evidence |
|---|---|---|---|
| +0 | clip type = 200 | BE u16 | marker census |
| +2 | track count N | BE u16 | editor `getOffset/getFramesize`; =23 on entry 685 |
| +4 | frame count F | BE u32 | editor `getLength` (type C8 → `int(4)`) |
| +8 | per-track types | N × BE u32 | swapper swaps N 4-byte groups at +8; values equal the 0x64 u16 table widened to u32 |
| +8+4N | frame data | F × N × 3 × BE f32 | editor frame_size = N*12, field = f32 |

Total size = `8 + 4N + 12·N·F`. Entry 685: N=23, F=128 → 35,428 B = exact
distance to the next unique MOTA offset. **Validation (entry 685):**
2,944/2,944 triples match Kiloutre's own `SwapAnimBytes` output re-parsed as
LE (0 mismatches); zero NaNs; rotation tracks sit in ±3.2 rad with smooth
frame-to-frame deltas; type-6 tracks (11,15,18,21) animate on exactly one
component (single-axis joints — elbows/knees class); type-5 track 2 is
all-zero; track 1 is a position triple (~(12, 1024, −6)); the clip is a
near-loop (frame 127 ≈ frame 0), consistent with an idle/stance clip.
Artifacts: `clip0685_tracks.json`, `clip0685_tracks.csv`,
`clip0685_sample_frames.md` (frames 0/64/127).

## Type 0x64 (100) — HEADER + INITIAL POSE DECODED; STREAM OPEN

| offset | field | type | evidence |
|---|---|---|---|
| +0 | clip type = 100 | BE u16 | marker census |
| +2 | track count N | BE u16 | editor `get0x64HeaderSize`, swapper `Swap64Anim` |
| +4 | per-track types | N × BE u16 | swapper reads them into `auStack536[]` |
| +4+2N | frame count F | BE u16 | `ByteSwap.getAnimationLength` (0x64 branch) |
| +6+2N | field A — UNIDENTIFIED | BE u16 | skipped by both editor and swapper; values 1024/1026/1028 on entries 8/1/2/3 (bit pattern `0x04xx`; possibly flags + a count) |
| +8+2N | root float count K | BE u16 | editor `__unknown__`; swapper reverses K f32s |
| +10+2N | root/global floats | K × BE f32 | decoded: small plausible values, e.g. entry 1 (0.0546, 0.00275, 0), entry 8 K=4 |
| +10+2N+4K | initial pose, per track | type 4..7 → 3 × BE i16; type ≥8 → 3 × BE f32 | swapper record sizes (6 B / 12 B); entry 3 pose ends exactly where the keyframe block must start (offset 224) |
| then | keyframe-index block | 4·⌈(F+14)/16⌉ B (editor formula adds +2 — 2-byte discrepancy between Kiloutre's editor and swapper, unresolved) | editor comment: "16 frames between each keyframe" |
| then | compressed keyframe/delta stream | remainder of entry | NOT decoded — see below |

Header decodes for entries 1/2/3/8: `clip_type64_headers.json` (23/23/23/25
tracks; 16/60/5/128 frames; stream remainders 706/1722/274/6136 B). The i16
initial-pose triples are reported RAW; a scale hypothesis (i16 · π/16384,
from the recurring 0x4000 = quarter-turn pattern) is NOT asserted — it is
unproven. The trailing stream shows runs of repeated BE i16 patterns
(e.g. `08 3c` ×4 in entry 3), consistent with quantized per-track keyframe
data, but no field layout is claimed. **No public decoder for this stream
exists**: Kiloutre's editor sets frame_size = 0 for 0x64 (header-only), and
a GitHub code search for `getAnimationLength` returns only Kiloutre's own
repos. Decoding this stream is the next research step (candidates: per-track
keyframe lists keyed by the keyframe-index block; the game's own
decompression in the X360 binary via Ghidra is the ground-truth route).

## Track → bone mapping (honest level: inferred, not proven)

MOTA carries no bone names or hierarchy. Mapping uses Kiloutre's own
track naming from BOTH of his tools — the editor field labels and, more
authoritatively, `BlenderTekkenAnimationImporter/AnimationFrame0x17.py`
(0x17 = 23 tracks; each track = one Euler triple) — + the type/single-axis
evidence above. That importer also confirms the "no public 0x64 decoder"
finding: it implements only `Animation0xC8` + `AnimationFrame0x17`, with no
0x64 code path at all. FK joint positions are therefore NOT produced: no
hierarchy/bind pose in the data, and inventing one would be fabrication.

| track | type | Kiloutre track name (Importer) / editor group | wh-anim/1 bone (engine) |
|---|---|---|---|
| 0 | 11 | Offset / Movement X, Height, Movement Z | Root (motion) |
| 1 | 11 | JumpStrength / Pos X, Pos Y, Pos Z | Root (position) |
| 2 | 5 | Unknown (all-zero in clip 685 ✓ both sources) | — unmapped |
| 3 | 7 | Mesh / Rot X/Y/Z | Root |
| 4 | 7 | UpperBody / Spine 1 | Spine |
| 5 | 7 | LowerBody / Hip | Hips |
| 6 | 11 | SpineFlexure / Spine 2 | Chest |
| 7 | 7 | Neck | Neck |
| 8 | 7 | Head | Head |
| 9 | 7 | RightInnerShoulder | RightShoulder |
| 10 | 7 | RightOuterShoulder | RightArm |
| 11 | 6 | RightElbow (single-axis ✓) | RightForeArm |
| 12 | 7 | RightHand | RightHand |
| 13 | 7 | LeftInnerShoulder | LeftShoulder |
| 14 | 7 | LeftOuterShoulder | LeftArm |
| 15 | 6 | LeftElbow (single-axis ✓) | LeftForeArm |
| 16 | 7 | LeftHand | LeftHand |
| 17 | 7 | RightHip | RightUpLeg |
| 18 | 6 | RightKnee (single-axis ✓) | RightLeg |
| 19 | 7 | RightFoot | RightFoot |
| 20 | 7 | LeftHip | LeftUpLeg |
| 21 | 6 | LeftKnee (single-axis ✓) | LeftLeg |
| 22 | 7 | LeftFoot | LeftFoot |

wh-anim/1 bone list fetched from `game/assets/anim/t3/king_on_pantera_leoman/t3_stance.json`
(22 bones; `LeftToeBase`/`RightToeBase` have no TTT2 track). MPFB 48-bone
rig names were not in any fetched source; mapping stops at wh-anim/1 names.
