# TEKKEN 5 CTYPE-5 / VIF 0x82 DECODE — the last DATA1 format gap, closed

Gap-closure W7d, 2026-10-21. Closes the ctype-5 named gap registered by
W7b (`tekken5:ctype5:unknown_slot:vif-0x82-models`, survey S4): the 16
NUDP models inside the 9 ctype-5 containers of TK5DATA1.BIN, whose VIF
packets carry globalFlags `0x82` and desynced ModelMagic's VIFerator on
every submesh (0 of 97 converted in the survey). **Verdict: format
decoded, structure proven on every packet, all 16 models converted to
GLB — and the decoded geometry is environment/effect class, not
customization items.** No parts[] entries land from this lane; the 8
unique geometries are registered in CATALOG.json under
`decoded_ctype5_models[]` and the named gap is flipped to
`decoded_not_customization_items`.

## 1. Reproduction of the containers (checksum-proven)

Method = the survey's (S1/S2), by HTTP Range against GitHub release
`tekken5-disc-v1` (mhvnsnt/game-reverse-engineering) — no full-disc
download: each of the 9 files was range-fetched from
TK5DATA1.BIN.part_01/part_02 at its E5-table offset, then verified
against the E5 word-sum checksum (table `0x27B5B0`, checksums
`0x27E838`). All 9 files are stored XOR-encrypted; all 9 verify
**DECRYPT-MATCH** after the FileTableGetPS2 LCG decryption (keystream
seed = file index, key = key·5+3, 512 u32 repeated per 2048-byte block):

| DATA1 file | bytes | container contents (sub1 = NUDP set) |
|---|---|---|
| 0022 | 141,200 | 4 models: 5,248 / 10,368 / 18,272 / 19,264 B |
| 0687, 0698 | 43,336 ea | 1 model each: 7,472 B (byte-identical) |
| 0753, 0764 | 23,008 ea | 1 model each: 1,520 B (byte-identical) |
| 1061, 1072, 1083, 1094 | 62,048 ea | 2 models each: 13,520 B + 8,336 B (byte-identical across all four files) |

Container + inner-archive structure exactly as the survey recorded:
`[u32 count=5]` + (offset,size) table; each sub carries an 80-byte inner
header of (size, cumulative-end) pairs. Every NUDP magic and every model
size matches the survey census. **16 models, 8 unique geometries.**

## 2. The VIF 0x82 packet layout (solved)

Solved by byte-budget from the smallest model (file 0753's 1,520-byte
model, first blob 1,184 B for 45 verts — far too small for the 0x91
section set), then proven on every blob (§3). One packet:

```
u16 size, u16 globalFlags = 0x0082
STCYCL 0x01000105
UNPACK S-32 num=1            -> vertCount (u32 data word)
STMASK 0x20000000, mask = 0x00000080
UNPACK V3-32 addr=1 num=N    -> positions (12N bytes)
UNPACK V4-8  addr=3 num=N    -> vertex colors RGBA (4N bytes)
UNPACK V2-32 addr=4 num=N    -> UVs (8N bytes)
STCYCL 0x01000500
STMASK 0x20000000, mask = 0xFFFFFF7F
tristrip marker words (top byte 0x70) until 0-padding / 16B alignment
terminators (final blob of a chain may omit them):
  STCYCL 0x01000101, STMASK, mask 0, FLUSHA 0x14000000
```

Differences vs the working 0x91/0x93 forms, and why ModelMagic desynced:
the 0x82 packet has **no normals section** (addr 2), **no weights**
(addr 0xCC) and **no bone-index section** (addr 0xCD) — a V4-8 section
at addr 3 (colors) is always present instead. VIFerator reads sections
in a fixed 0x91/0x93 order and walks straight into the color bytes
looking for normals. The two STMASK masks are the byte-reversed
complements of the 0x91 form's (`0x80000000`→`0x00000080`,
`0x7FFFFFFF`→`0xFFFFFF7F`). Everything else is shared: STCYCL CL=5 VU
stride, so tristrip markers decode with VIFerator's own logic
(divisor 5) unchanged.

The addr-3 V4-8 section is **vertex color**, not bone indices: values
are color-like triples (e.g. (255,38,0), (255,211,230), (89,110,128))
with the 4th byte inside the PS2 alpha range 0..128 (constant 128 in
file 0753's model; ~101–105 in file 0022's prism models); submesh bone
palettes are all-0xFF and there is no skinning data anywhere in these
packets. Normals therefore do not exist in the source and are computed
from faces at GLB time (stated in every catalog entry's tool chain).

## 3. Structure proof (all 16 models, strict decoder)

`tools/vif082.py` asserts every constant, count and boundary above; a
single deviation raises. Over the full set:

- **238 / 238 VIF blobs decode with zero deviations** and every blob is
  consumed to **exactly** its size field.
- Every UNPACK section's element count equals its packet's own
  vertCount (self-consistency, 238×3 sections).
- Totals: **5,124 vertices, 2,468 triangles**; every face index in
  range; every position finite.
- Header cross-check: each group's `meshBounds` is a bounding sphere
  (center, radius) — e.g. file 0022 model 2: center (0, 0, 1250),
  radius 1253.99 = the exact corner distance of the decoded prism.
- End-to-end reproduction: `tools/fetch_decode_ctype5.py` re-fetches
  from the release, re-verifies checksums, re-decodes and rebuilds the
  GLBs; geometry and counts identical to the first build.

## 4. What the models are (from decoded data only)

Characterization is from the decoded geometry, the vertex colors, the
referenced TIM2 picture, and own-eyes renders (`proof/ctype5-*.png`) —
never from header metadata or other games' files. (The 'head portrait'
label that circulated for the 1061 pair was a retracted T6/W7a
misattribution; the decoded 1061 models are a flat panel and a
prism-beam unit.)

Three geometry classes, all at scene scale (thousands of source units):

1. **Triangular-prism beam units** — one 12-vertex unit (3 quads):
   equilateral-triangle cross-section 150 × 173.2, extruded 2500 long,
   saturated vertex colors (orange-red 255,38,0 in 0022-m2; browns in
   0022-m3; reds in 0687 and the 1061 family's m1), mapped to a shared
   64×64 white alpha-gradient TIM2 (RGB all-white, alpha gradient —
   the tint and translucency live in the vertex colors). Models repeat
   the unit in 17–42 byte-identical mesh groups; runtime placement
   transforms are not stored in the NUDP, so GLBs carry the groups as
   stored (coincident at the unit origin).
2. **Flat square panels** — 2000 × 2000, 118–186 thick, grey/blue-grey
   vertex colors, same gradient texture (0022-m0, 0022-m1, 1061-m0).
3. **Cylindrical wall segment** — file 0753/0764's model: an open
   cylinder of diameter ≈1996 and height ≈3972 (45 verts in ring
   strips + one 3-vert blob), two-tone vertex colors (dark brown
   (64,58,51) / pink-white (255,211,230)), textured with a 128×128 dark
   metallic panel TIM2 (vertical seams, rivet detail — viewed in
   `proof/ctype5-f0753-m0.png` render and the raw TIM2 export).

**None of the 16 is a wearable/customization item, and none is a skull,
mask, or head-covering shape** — the skull-mask named gap's DATA1
verdict (not found) now covers these models too, leaving TK5DATA0.BIN
as the only unexamined archive.

## 5. Deliverables

- GLBs (8 unique models): GitHub release **tekken5-ctype5-glbs-v1** on
  this repo; per-asset sha256/size recorded in CATALOG.json
  `decoded_ctype5_models[]` and reproducible via
  `tools/fetch_decode_ctype5.py`. Conventions match the W7e costume
  GLBs: raw source coordinates, UV V flipped, TIM2 picture 0 embedded
  as baseColorTexture, vertex colors carried as COLOR_0 (PS2 alpha
  0..128 → 0..1), computed smooth normals, material double-sided +
  alpha-blended (gradient-texture translucency).
- Tools: `tools/vif082.py` (strict decoder), `tools/ctype5_glb.py`
  (GLB writer), `tools/fetch_decode_ctype5.py` (end-to-end driver).
- Catalog: `decoded_ctype5_models[]` (8 entries), census additions,
  ctype-5 named gap flipped to `decoded_not_customization_items`,
  skull-mask gap addendum. `catalog.test.mjs` stays **3/3** — parts[]
  and the registry contract are untouched because these are not parts.
- Proof: `proof/ctype5-contact-sheet.png` + per-class renders in
  `proof/`, all viewed by this lane before landing.

*W7d lane, 2026-10-21. Extraction/disc evidence: W7b survey (S1–S4);
community Tekken5_Tools constants (© its author, NO LICENSE — used for
evaluation/extraction only, not vendored), same precedent as W7b/W7e.*
