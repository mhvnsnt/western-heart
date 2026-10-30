# Urban Reign Phase 2 — Native Motion Conversion Report (2026-10-21)

Companion to PR #442 (stacked on #434). Decoder + proof + full batch
landed; movelist name mapping and textures remain open (named below).

## 1. The .gyu format — CRACKED IN FULL

Tool: `teardown/urban-reign/tools/ur_gyu.py` (sampler-faithful; tables
read from SLUS_212.09, MD5 `0fa29bd55638f9ebe49feb494d4decd5`).

Bank layout (proven from bytes, all banks):
`[u32 n_motions][u32 n_bones][u32 0][n_bones × u32 flags][n_motions ×
u32 cumulative end offsets]` then motions; each motion =
`[n_bones × u32 track offsets][tracks]`; track header = s16 type,
s16 frames-per-key, s16 n_keys.

Track types (all four sampler families decoded):
- **8** — u16 keys at +36; `out = base + key·step` (float pairs @+12..+32).
- **12** — set-1 arithmetic/range-coded s12 delta triples (tables:
  total @0x662aa8, prob @0x65eaa8, cum @0x660aa8, guess @0x662ab0);
  s16 cumulative sum per 8-key block; same float-pair combine.
- **13** — set-2 range-coded s16 values built from symbol pairs
  (tables @0x663ec0/0x663ac0/0x663cc0/0x663ec8); cumsum; scale
  `1/(2^14 − 1)` (float @ELF 0x6646e4 = 16384.0).
- **14** — type-13 values with type-12 float-pair combine. Root track
  of the general banks (decodes to root positions, y ≈ 1.139 m).

Validation: **56,844 tracks decode with 0 failures** — all 4 general
banks (17,658 tracks), all 31 pmot packs, all 10 tmot packs, main/
select packs included in the sweep. Motion bone 0 = root position
track; bones 1..20 = Euler rotation tracks (pose evaluator
FUN_002918xx: flag 1 → FUN_00101628 Euler→matrix; flag 0 → position
× 0.1 × char scale).

Per-character banks: `pmotNNN.ppk` = fncc header (0x80) + .gyu bank;
pmot001 = char001's own 56 motions / 21 bones. 31 of 72 characters
have a pmot bank; 10 tmot banks exist (assignment unproven).

## 2. Proof gate — char001 (pmot001 motion 0, 71 frames)

- Poses baked with numpy skinning (GLB verified exact under matrix
  composition: max dev 6e-08; **Blender's glTF importer mangles these
  GLBs — use matrix composition / three.js semantics, not Blender
  bones**). Composition: GLB-hierarchy locals, `L = Lbind · R_euler`
  (delta), root delta on node 12.
- Renders viewed at frames 0/24/47/70: coherent authored fighting
  motion (stance, lean-in, guard arm), NOT noise. Residual defect:
  one rigid accessory/leg piece swings wide at f47–70; mean relative
  edge distortion 0.04–0.06 (LBS-normal range). The open item is the
  true game node graph (phase 1 left it open too) — mapping used is
  motion bone b → GLB node index b ("H-index"), documented in every
  artifact.
- All 37 bind matrices are pure rotation+translation (orthonormal,
  det +1) — local TRS animation is lossless for this rig.
- Embedded-GLB verification: sampling the embedded animation of
  char001 at f24 reproduces the baked pose with **max dev 1.8e-07**.

## 3. What landed in game/

- `game/assets/models/street-reign/charNNN.glb` (31 pmot characters) —
  their full native banks embedded (`ur_m000...`) + `Idle` alias
  (engine auto-plays embedded Idle per assets.js).
- `game/assets/movesets/ur-charNNN.json` ×31 — native moveset
  records (animation native; move *names* still engine-base — §4).
- `game/assets/movesets/ur-native-index.json` — per-fighter status
  for all 72 (native vs proxy + reason).
- `game/assets/anim/ur-general-{normal,30frame,weapon}/` — all three
  general banks (342 + 373 + 114 motions) converted to wh-anim-style
  packed banks (skeleton.json / clips.json / rows.pack.json, PR #425
  conventions), skeleton referenced to char001's node layout. Shared
  pool data — not per-fighter assignments.
- Tools in `teardown/urban-reign/tools/`: ur_gyu.py (decoder),
  ur_embed.py (GLB embedder), ur_batch_embed.py (batch driver),
  ur_bank_convert.py (general-bank packer), ur_skin_bake.py
  (numpy skinning/proof).

## 4. Honest status per fighter

- **31 pmot characters**: native animation decoded, proven on
  char001, and EMBEDDED in their game GLBs in this PR (per-fighter
  `ur-charNNN.json` records + `ur-native-index.json`).
- **41 characters without pmot banks**: proxy (unchanged from #434).
  Their native motions live in the shared general pools; assigning
  pool motions to fighters needs the movelist correlation below.
- **Move names / native movelists**: NOT yet mapped. motdat .info
  name lists are held (Gnrl 294 names, P1 35; prefixes cbco_/moco_/
  haco_/hahr_/mohr_/itco_ = style archetypes), and gyuindex pairs
  pmotNNN.gyu ↔ pmotIDNNN.bin — the correlation of pmotID tables to
  bank motion indices is the named next step. No names were guessed.
- **Proxy flag**: `street-reign.json` (shared, #434) is untouched.
  Per-fighter `ur-charNNN.json` records carry the split status
  (animation vs moves) explicitly; nothing is labeled native that
  isn't.

## 5. Batch — DONE (embedding); general banks converted

All 31 pmot characters embedded with `ur_batch_embed.py`
(31 native / 41 proxy recorded in `ur-native-index.json`), and all
three general banks converted with `ur_bank_convert.py` into
`game/assets/anim/ur-general-{normal,30frame,weapon}/`.
(weapon.ppk's fncc body is not a plain .gyu at +0x80 — its bank is
general_weapon.gyu, converted from `teardown/urban-reign/motion/`.)

## 6. Job 2 — textures: NOT cracked (state advanced)

Findings this session (char001.ppk, 776,960 B):
- The region after the vertex stream is ONE interleaved VIF/GIF
  stream (vmanifest's `0x2` chunk spans 0xe800..EOF): texture
  uploads ride inside it as GIF packets (BITBLTBUF/TEX0 + image
  data), they are not a standalone trailing blob.
- Entropy map of the tail: structured low-entropy DMA regions to
  ~0xA4000, then a ~90 KB high-entropy (6.5) nibble-structured region
  ≈ candidate GIF image payload (PSMT4/8-shaped sizes: 512×352@4bpp
  = 90,112 B fits).
- Next step (named): a VIF/GIF stream walker that replays upload
  packets into a virtual GS memory, then deswizzle from the TEX0
  parameters the stream itself declares. Phase-1 state (#306) stands
  until then; GLBs remain untextured. No texture data was faked.

## 7. Job 3 — polish: NOT started

char064 s16 group (63 verts) and the 11 unproven accessory pieces
remain open (jobs 1–2 did not fully land; per task ordering, polish
was conditional). The accessory-swing defect seen in the proof
renders is logged in §2 for the same lane.
