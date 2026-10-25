# Def Jam: Fight for NY — EAGL Format Spec (Phase R, J4)

**Date:** 2026-10-20 (Phase R) · amended 2026-10-21 (Phase V)
**Lane:** creation-suite gap-fill J4 (Def Jam converter)
**Status:** Outer format **closed with evidence** (Phase R). The
vertex-stream FRAMING was **closed in Phase V** — see §7 (the §6
route was executed: Ghidra on `SLUS_210.04` + cross-part
differentials + the compiled `_C` twin as ground truth). Three
sub-layers are documented open in §7, with evidence, and are NOT
guessed: the vertex draw order / position semantics (§7.9 — the
one blocker; sample renders failed own-eyes validation as
meshes, so the converter ships the proven pool as POINTS), the
Normals stream's payload encoding (§7.5), and UV/STQ data
(absent from the A/B `.o` files, §7.7).
This spec supersedes the guesses in `EAGL-FORMAT-ANALYSIS.md` (kept
for history); where the two disagree, this spec is right and says why.

## 0. The headline correction

The CAW part files are **not** raw EAGL objects and the `.o` files are
**not** "unreadable by readelf". Every sampled game file is wrapped in
**EA RefPack (QFS) compression**. Decompressed, a `.o` is a completely
standard MIPS ELF32 relocatable object that `readelf` parses cleanly,
and a `.ssh` is a standard EA `SHPS` shape (texture) file. The earlier
analysis sampled the *compressed* bytes, which is why section headers
looked proprietary (the "e_type=0xE100 / e_machine=0xC730" values were
compressed-stream bytes misread as an ELF header).

## 1. Layer 0 — RefPack wrapper (PROVEN)

| Offset | Size | Field |
|---|---|---|
| 0 | 1 | `0x10` (bit 7 = 4-byte size fields, bit 0 = compressed-size field present; both flags clear in all FFNY samples) |
| 1 | 1 | `0xFB` |
| 2 | 3 | Decompressed size, **big-endian** |
| 5 | … | RefPack control stream (2/3/4-byte pointer ops + literal ops, stop code `0xFC–0xFF`) |

Algorithm: published QFS/RefPack spec, as implemented in DBPFSharp
`QfsCompression.Decompress` (MIT) — decoder landed as
`customization/tools/eagl_refpack.py`, tests in
`customization/tools/test_eagl_refpack.py`.

Evidence (decoder output, first-hand, 2026-10-20):

| File (mhvnsnt/wrestling-game) | Compressed | Decompressed | Header-declared | Head bytes |
|---|---|---|---|---|
| `V2CP_110_0001_A.o` | 20,346 | 38,144 | 38,144 (`00 95 00`) | `7f 45 4c 46` (ELF) |
| `V2CP_110_0001_B.o` | 20,138 | 38,144 | 38,144 | ELF |
| `V2CP_111_0001_A.o` | 21,252 | 39,696 | 39,696 (`00 9b 10`) | ELF |
| `V2CP_110_0001_C.o` | 68,752 | 105,856 | 105,856 (`01 9d 80`) | ELF |
| `V2CP_111_0001_A01_01.ssh` | 63,862 | 67,024 | 67,024 (`01 05 d0`) | `SHPS` |
| `V2CP_110_9999_A01_01.ssh` | 518 | 66,016 | 66,016 (`01 01 e0`) | `SHPS` |

**Variant rule:** `_C` `.o` files carry an **8-byte zero prefix** before
the `10 FB` record (record at offset 8). `eagl_refpack.find_refpack_offset`
locates the record; never assume offset 0.

## 2. Layer 1a — `.o` = ELF32 relocatable (PROVEN)

Decompressed `V2CP_110_0001_A.o`, via `readelf`:

- `e_type=0x0001` (REL), `e_machine=0x0008` (MIPS), little-endian, entry 0.
- Sections: `.data` (33,904 B @ file 64), `.shstrtab`, `.strtab` (2,256 B),
  `.symtab` (99 symbols × 16 B), `.rel.data` (5 × `R_MIPS_32`, all into `.data`).
- Symbols: ~95 × `__Bone:::root.<name>` (size 4, at 16-byte intervals
  `0x0000–0x05D0`), `__Skeleton:::root` @ `0x05E0`,
  `__Morph:::morph.modelname` @ `0x2F34`, weak
  `__EAGL_TOOLLIB_VERSION:::EAGL_TOOLLIB_VERSION-4` @ 0.
- The bone set is the full shared CAW skeleton (root, tophip, waist, hip,
  chest, neck, head, L/R arm/hand/finger chains, L/R leg/foot chains,
  face bones: JAW, L/R_Brow, L/R_Eye, BotLip, placellip/placerlip, Squint,
  Sneer, Blink; hair bones: HairTop/Front/Back, PonyTail1/2, Pendant1/2).
  Symbol tables are **identical** between `110_0001_A.o` (head) and
  `111_0001_A.o` (upper_body) — every part carries the whole skeleton.

### `.data` layout (from symbol offsets + cross-part diffing)

| `.data` range | Contents | Evidence |
|---|---|---|
| `0x0000–0x05EF` | Bone palette records, 16 B each: first u32 = own index (0,1,2,…), rest zero in samples | direct dump |
| `0x05F0–0x2F0F` | Bone transform data (float matrices / SRT records; contains 1.0 scales and translations, e.g. ±10.56) | float dump; near-identical across parts (61–85 differing bytes per 2 KB between variants) |
| `0x2F10–0x2F6F` | Geometry/morph header: strings `Morph`, `Coordinates`, `Normals`; 5 relocated pointers to those strings and sub-structs; candidate counts `0x1B`, `0x138` (312), `0x34` (52) | `readelf -rW` + struct dump |
| `0x2F70–0x8470` (end) | **Vertex stream data, 21,760 B** | A/B and cross-part diffs: this is the first region that fully differs per part |

Vertex-stream facts so far: byte-periodicity peaks at lag 12 (and
multiples 24/36/48); data reads as int16 LE with values roughly
±2,200 and a recurring `-8192` (`0xE000`) marker value. Positions are
therefore quantized int16, not float32. Exact field split
(position/normal/UV/skin, stride, scale, strip vs list topology) is
**not yet proven** — see §6. No converter code may guess it.

## 3. Layer 1b — `.ssh` = SHPS texture (PROVEN)

Decompressed `.ssh` begins `SHPS`, then a LE u32 total size equal to the
decompressed length (`0x000101E0` = 66,016 for the 9999 sample), entry
count 1, entry name `G359`, and the string
`EAGL240 metal bin attachment for runtime texture management` — a
standard EA Shape file with one image entry, parseable with the EA
Shape format as implemented by EA Graphics Manager (open source).
The `_A01_01`, `_A01_02`, … `.ssh` siblings of a part are its texture
variants (same header/name, different pixel data, identical
decompressed size 67,024 for the 111_0001 pair sampled). The 518-byte
`9999` file is **not** metadata-only as previously believed — it is a
mostly-empty 66,016-byte texture, highly compressible.

So a complete CAW part = one `.o` (skeleton + geometry + morph) plus
its sibling `.ssh` texture variants. The PARTS-INDEX count of 22,360
counts `.o` files only.

## 4. What was wrong in the prior analysis

- "SHPS magic at 0x00 of `.o`" — that was the RefPack stream's early
  literal bytes; `.o` files contain no SHPS.
- "e_type=0xE100, e_machine=0xC730, sections unreadable" — compressed
  bytes misread as a header. Real values: type 1, machine 8 (MIPS).
- "`.ssh` mesh containers ~47–55 KB" — `.ssh` are textures (SHPS);
  geometry lives in the `.o` `.data`.
- "Index-like region `XX 8b 40 0f`" — RefPack control-stream artifact,
  not an index buffer.

## 5. Converter design (Phase V, gated on §6)

`customization/tools/convert_defjam_o.py` (Phase-1 pattern, cf.
`convert_caw_parts.py`):
RefPack-decompress (landed) → parse ELF `.data`/`.symtab` with the
offsets in §2 → decode vertex streams per §6 → build GLB (positions,
normals, UVs, skeleton from the shared bone table, morph target) →
decode the sibling `.ssh` via the EA Shape layout → bind as the GLB
material image. Output catalog:
`customization/parts-converted/defjam/CATALOG.json` in registry-entry
shape (the shape `packages/creation-suite/src/catalogs.js` merges:
`{parts: [...]}` deduped by `file`), alongside the no-mercy/wmxix
catalogs in `customization/parts-converted/CATALOG.json`'s family.

## 6. The one open layer, and how it closes

**CLOSED in Phase V — see §7.** (This section is kept as written in
Phase R; it records the plan that was executed.)

Open: vertex-stream field layout inside `.data[0x2F70…]`, and the exact
semantics of the header counts at `0x2F50–0x2F6F`. Sanctioned routes, in
order (no hand-guessed parsers):

1. **Ghidra on the game executable** (`SLUS_210.04`, from the ISO in
   TEARDOWN.md provenance): find the EAGL object loader that consumes
   `__Morph:::`/stream descriptors; its reads define stride, field
   types, scale and topology exactly. Ghidra 12.1.4 + MCP are already
   installed in this workspace.
2. **Cross-part differential analysis** on decompressed `.data`
   (same-skeleton parts differing in one region) to confirm the
   loader's layout against real bytes.
3. Only then Phase V: ~20 sample parts across all four slots
   (head 110 / upper_body 111 / lower_body 112 / accessories 113),
   Blender renders, own-eyes verdict before any batch work.

Phase B (all 22,360) additionally waits for the coordinator's
Blender-slot release (one Blender-heavy lane at a time).


## 7. Phase V closure — the vertex-stream layout (PROVEN)

### 7.1 How it was closed (three independent evidence lines)

1. **Ghidra on the executable.** `SLUS_210.04` (fetched byte-exact
   from the TEARDOWN.md ISO via the surgical Range method: ISO root
   dir at LBA 261, `SLUS_210.04;1` at LBA 1941376, 3,139,200 bytes;
   stripped MIPS ELF, single LOAD segment, vaddr = fileoff +
   0xFF000) was analyzed with Ghidra 12.1.4, language
   `r5900:LE:32:default`. The exe embeds the full EAGL runtime:
   - `_BuildMorph` error string at vaddr 0x3CBC68, xref at 0x19FB1C;
     the function at **0x19F970** is the CMorph stream/name lookup;
     it calls **0x19FBD8**, which calls the CMorph helpers at
     **0x114BC0 / 0x114C38**; CMorph load at **0x1149B4**.
   - `CVertexInformation::Init` at **0x11EB88**; its member strings
     `mpVertex` / `m_pColour` / `m_pSTQ` at 0x3AFA68 / 0x3AFA90 /
     0x3AFAB8 (xrefs 0x11EB9C / 0x11EBB4 / 0x11EC08).
   - `CModel` loads `"%s/%s.o"` — the A/B `.o` files are the runtime
     source format.
   The CPU-side loader only walks objects and passes stream pointers
   through; per-vertex consumption happens in VU1 microcode on the
   PS2. The loader therefore confirms the *object* structure below,
   while the *record* layout is proven by lines 2 and 3.
2. **Cross-part differential analysis** on 18 decompressed `.o` files
   (slots 110/111/112/113, variants A/B/D/E/F): every framing rule in
   §7.2 was checked byte-exactly on every strip block of every file —
   the converter asserts header zeros, strip indices, and end
   markers as it walks, and the Coordinates stream ends *exactly* on
   the Normals object in all samples.
3. **The compiled `_C` twin as ground truth.** `V2CP_110_0001_C.o` is
   the compiled GeoPrim form of the same part as
   `V2CP_110_0001_A/B.o`. Its strip-descriptor table (in `.data` at
   0x17CA0, stride 0x10: `[flags|count][byteSize][dataAddr][index]`,
   index running 1..27) carries per-strip vertex counts that match
   the A/B block headers **exactly, all 27 strips, in order**
   ([52, 48, 50, 51, 43, 43, 10, 36, 37, 44, 38, 42, 50, 54, 53, 42,
   48, 52, 50, 45, 42, 32, 34, 40, 48, 49, 27], sum 1,160). Its
   symbols prove the topology: `PT_TRIANGLESTRIP` (GeoPrimState),
   and its variable names are the same "Coordinates" / "Normals" /
   "Colours". The `_C` file's own packed stream encoding is a
   separate, still-open layout (not needed: A/B are the source form).

### 7.2 The Morph / stream-object layout (`.data`-relative, part 110_0001)

| Offset | Content |
|---|---|
| 0x2F10 | string "Morph" (root name) |
| 0x2F16 | string "Coordinates"; 0x2F22 string "Normals" |
| 0x2F2C | Morph root: name ptr → "Morph", 0, 1, ptr, ptr, 0, stream count = 2 at +0x18 |
| 0x2F34 | symbol `__Morph:::morph.modelname` |

Each **stream object is a 32-byte header**:

| +0x00 | name pointer (R_MIPS_32) → "Coordinates" / "Normals" |
| +0x04 | 1 |
| +0x08 | 0 |
| +0x0C | u32 strip count (27 for slots 110/113 samples; 28–32 others) |
| +0x10 | i16 count field + i16 stream marker |
| +0x14 | first strip block |

Count field / marker per stream: Coordinates (312, −8192 = 0xE000),
Normals (624, −16384 = 0xC000) for part 110_0001; the Normals count
field is always exactly 2× the Coordinates one in samples. The count
field's full semantics are not proven (it is NOT the unique-vertex
count: 110_0001 has 505 unique vertices vs count 312) — the
converter does not rely on it.

### 7.3 Strip block framing (both streams)

```
[6 x i16 header: vertexCount, 0, 0, 0, stripIndex, 0]
[vertexCount x record]
  Coordinates record = 3 x i16 (x, y, z)
  Normals record     = 6 x i16 (payload, see §7.5)
[if vertexCount x record is odd-length in i16 (Coordinates with an
  odd vertexCount): ONE pad i16 immediately after the data]
[non-final blocks only: i16 trailer (undecoded), i16 stream marker]
```
The final block has no trailer/marker: its data ends exactly on the
next stream object (or end of `.data`). Marker values: −8192
(Coordinates), −16384 (Normals) — the "recurring sentinels" of the
Phase R notes are these block markers, and the Phase R "header
counts" (0x1B / 312 / 52) are the stream header's strip count /
count field / first block's vertex count.

### 7.4 Coordinates semantics — values proven, geometry OPEN

The Coordinates stream provably contains 3×i16 records in the
framing of §7.3, with part-shaped statistics (x symmetric about 0,
110_0001_A: x ∈ [−1156, 1156]; z the long axis, spans 4,069–5,089
across slots; y the smallest). **But the records are NOT final
draw-order positions**: Phase V sample validation (own-eyes,
2026-10-21) rendered a strip build of V2CP_110_0001_A as scrambled
spikes, and the raw pool renders as a loose scatter, not a surface
shell. The geometric interpretation of the pool — draw order and
any per-block transform — is OPEN; see §7.9 for the evidence, the
falsified readings, and the live leads. Converter choices,
documented in `convert_defjam_o.py`: `POS_SCALE = 1/1024`, axis map
(x, y, z) → (x, z, −y) into glTF's right-handed Y-up frame. The
converter emits the pool as a glTF POINTS primitive — exactly the
data the file proves, nothing invented.

### 7.5 Normals payload — framed, encoding OPEN (not guessed)

The Normals stream is framed exactly like Coordinates (6×i16
records; all block headers/markers verified on all samples), but its
payload is NOT plain vectors: byte entropy 7.29 bits/byte (vs 5.70
for Coordinates), zero correlation with the Coordinates data
(r ≈ −0.0004), and i16, byte-swapped i16, f32 LE/BE, half-swapped
f32 and nibble-swapped readings all fail smoothness tests. It is a
VU1-consumed packed encoding. The converter does not emit the
payload as normals and computes none (the POINTS output carries no
normals); the catalog records the stream as undecoded.

### 7.6 Textures — SHPS layout CLOSED

Decompressed `.ssh` = SHPS, 1 entry ("G359"/"0000", data offset
0x70; "Buy ERTS" block between directory and data). Image header at
the data offset (per the Q3R ssh2tga format documentation,
Yagotzirck/Q3R_tools, from XeNTaX SHPS research): u32 = type (low
byte; 2 = paletted 8bpp) | next-header offset << 8; u16 width, u16
height (256×256 in samples). Pixels follow at +16, PS2 GS-swizzled
(unswizzle = the standard published PS2 8bpp permutation, as in
ReverseBox); the palette header sits at header+nextHdrOffset (first
byte 0x21, size field 0x410 = 16 + 1024), followed by 256 RGBA
entries stored **linear** (FFNY palettes are not CSM-swizzled —
verified by eye). PS2 alpha 0x80 = opaque (decoded as min(255, a·2)).
Trailer after the palette contains the "EAGL240 metal bin
attachment" string. Byte accounting on
`V2CP_111_0001_A01_01.ssh` is exact: 128 + 65,536 + 16 + 1,024 +
336 = 67,024. Decoded textures viewed and confirmed (denim garment
with seams/pockets for 111_0001; patterned garment for 113_0001).
Decoder: `customization/tools/eagl_shps.py`.

### 7.7 UVs — absent from the A/B files (proven inventory)

The Morph objects carry exactly two streams (Coordinates, Normals).
STQ data exists only in the compiled `_C` GeoPrim form
(`CVertexInformation::m_pSTQ`), whose packed layout is open. The
converter therefore emits the decoded texture PNG next to the GLB
and records `uv_status=absent_in_o_file` in the catalog; it does NOT
bind a texture into the GLB — a bind without UVs would fabricate
data.

### 7.8 `_C` variant handling

`_C` files (some carry an 8-byte prefix before the RefPack record,
~112 symbols, no Morph stream objects — GeoPrimState/PT_* symbols
instead) are detected by the converter and reported
`status=compiled_variant`; they are never fed to the Morph parser.
The compiled family in the extracted set includes letters C, C1, C2,
C3 and some A/F-letter files — the symbol check, not the letter,
decides. Two `_C_F` files (code 532) carry only a PosePaletteBank
symbol and classify as `pose_palette_only`.

### 7.9 Topology & position semantics — OPEN (the one blocker)

**Status: the vertex draw order / geometric interpretation is not
closed. Everything else in §7 is proven.** Evidence gathered in
Phase V sample validation (2026-10-21):

- A triangle-strip build of V2CP_110_0001_A rendered in Blender
  (EEVEE, own-eyes) as scrambled spikes — not a head part.
  (`teardown/def-jam-fight-for-ny/sample-renders/
  V2CP_110_0001_A_STRIP_FAILED.png`.)
- The raw Coordinates pool rendered as POINTS forms a loose
  scatter with a denser core, not a surface shell
  (`V2CP_110_0001_A_points.png`, `V2CP_111_0001_A_points.png`).
- Stored-order consecutive-vertex distance across files: mean
  ≈ 620–690 units vs a greedy nearest-neighbour path of ≈ 230 —
  the stored order is not the surface order under any reading
  tried.

Falsified readings (do not re-try): triangle strips in stored
order; independent triangle lists; component planes ([x…][y…][z…]);
even/odd, mod-4 and mod-8 deinterleaves; split-half rails;
two-sub-strips; Morton/Z-order storage; delta (cumulative-sum)
encoding; parametric ring/grid structure (z-histograms show no
rings); cross-letter permutation (A/B/D/E/F pools are distinct
point sets, not permutations of one another).

Live leads for the follow-up lane:
1. **Bone-local assembly.** `.data` 0x0000–0x05E0 holds 94 bone
   index records (sequential ids) mapped by `__Bone` symbols; a
   skeleton header at 0x5E0 (count 94) is followed at 0x5F0 by a
   per-bone float region (94 × ~112 bytes to the Morph strings at
   0x2F10) containing matrix-like data (rotations, translations
   ~±10–21). Block index fields (with gaps, e.g. 0..26,28) may key
   into per-part bone groups; the exact matrix packing and the
   block→bone map are undecoded. Naive single-matrix transforms of
   block 0 did not produce a clean shell under a scale-sensitive
   metric — retest with a scale-invariant one.
2. **The VU-packed companion stream** (§7.5): the 6×i16 records
   aligned 1:1 with Coordinates blocks may carry the ordering /
   weighting data the VU1 uses; decoding it likely requires the
   EAGL VU1 microcode or the loader's unpack path in SLUS_210.04
   (CMorph load 0x1149B4, helpers 0x114BC0/0x114C38).
3. **The `_C` compiled twin** contains the same part in draw-ready
   GeoPrim form; its packed vertex encoding (not plain i16/f32
   triples — searched) is a third route to the draw order.

Converter behaviour while this is open: GLB output is the
Coordinates pool as a POINTS primitive with
`topology_status=unproven_vertex_order` in the catalog. Textures
(§7.6) are fully decoded and unaffected. A strip-triangulation
research mode remains in the converter behind
`topology="strip"`, clearly marked unvalidated.

#### 7.9.1 W5c addendum (2026-10-21) — new evidence, blocker stands

The vertex-order attack was re-run with the complete dataset, the
`_C` compiled twin, and cross-letter differentials. The blocker
**stands** — no candidate order passed, and none is shipped — but
the evidence base is now much harder. All measurements below are
reproduced by `teardown/def-jam-fight-for-ny/tools/
w5c_vertex_analysis.py` run against the wrestling-game `.o` files
(parser: the proven J4 converter code, unmodified).

**Proven since §7.9:**

1. **Block trailers are decoded.** The "undecoded" i16 trailer
   after each non-final strip block is the **byte size of the NEXT
   block's record data**: Coordinates trailer[k] = 2 · 3 ·
   count[k+1], exactly, for all 26 trailers of V2CP_110_0001_A;
   Normals trailer[k] = 2 × Coordinates trailer[k] (= 2 · 6 ·
   count[k+1]). The blocks form a size-linked chain (consistent
   with per-block DMA/VU packet chunks), so the trailer carries no
   ordering information — that sub-mystery is closed.
2. **The pool is a clean surface sample; only the order is alien.**
   The 505 unique points of V2CP_110_0001_A have nearest-neighbour
   distances median 87 / p75 131 / max 321 (part spans ~4,069) —
   proper surface density, not a volume fill. 1,143 of 1,160
   records have an exact mirror partner (−x, y, z): the set is a
   real, x-symmetric part. Whatever scrambles the mesh is in the
   sequence/assembly, not in the point set.
3. **The pool is provably NOT one rigid frame.** The `_C` twin's
   `__BBOX` (assembled space) is x ∈ [−8.722, 8.722],
   y ∈ [0, 19.334], z ∈ [−4, 5] (spans 17.44 / 19.33 / 9.0). The A
   pool spans are (2312, 969, 4069). Under **every** axis
   permutation the three span ratios differ (best pairing:
   0.00929 / 0.00754 / 0.00475) — no permutation + uniform scale
   maps the pool onto the assembled box. The assembled geometry is
   therefore produced from the pool by per-vertex or per-block
   transforms (or the pool mixes frames), never by a single rigid
   transform of the stored triples. This kills the entire family
   of "right order, wrong axis/scale" readings at once.
4. **The letters are morph variants of ONE mesh with ONE order.**
   For V2CP_110_0001, the per-strip first-occurrence (topology)
   maps of B and F are **identical to A's in all 27 strips**
   (D: 17/27, E: 23/27 — differing only where their geometry
   merges/splits points). Same strip counts, same vertex counts,
   different geometry. The vertex order is a property of the
   format/toolchain, shared across variants — and any future
   candidate order can be validated against all variants at once.
   Per-letter stored-order strip scores (mean consecutive distance)
   differ widely under the identical topology (110_0001:
   A 685, B 424, D 762, E 1344, F 1699; 111_0001: A 642, B 345),
   which is itself inconsistent with "stored order = surface
   order" for any of them.
5. **The `_C` packed stream anatomy.** Strip blocks in `_C` are
   sequences of 8-byte units (i16 a, i16 b, i16 c, i16 w), where
   **w = 7 · (sequential index), with −1 (0xFFFF) substituted at
   irregular positions** (strip 0: 0, 7, 14, −1, 21, 28, …, 98,
   −1, −1, 105, …). The (a, b, c) triples are NOT positions
   (consecutive distance ≈ 31,570, full-scale noise), and no A/B
   i16 sequence (flat, or any single component) occurs anywhere
   in the `_C` `.data`. The stream is a VU-packetized compiled
   form whose semantics live in the EAGL VU1 microcode / the
   loader's unpack path — it does not yield its vertex order to
   offline inspection alone.
6. **Bone records partially decoded.** Each 112-byte bone record
   at `.data+0x5F0` (94 records) opens with scale (1,1,1), a u32
   (0xFFFFFFFF on record 0, else 0 in samples), and a unit
   quaternion at floats [4:8] (record 0: identity (0,0,0,1);
   record 1: (0,0,0.707,0.707)). The remaining 20 floats carry
   matrix-like data including a ±10.56 translation pair
   (bind / inverse-bind pattern). The exact matrix packing and
   the block→bone map are still undecoded.

**Falsified in W5c (with scores; do not re-try):** record-level
deinterleaves p = 3, 5, 6, 7 (mean consecutive distance 823–870 vs
identity 696); component-level even/odd deinterleave within
2-record groups (818 / 822); all six axis permutations (identical
score to identity by symmetry of the metric, and independently
killed by item 3 above); the `_C` (a,b,c) units as positions, in
all units and in every 3rd-unit subsequence (31,238–36,882); the
A/B Normals stream read as positions in any component triple
((0,2,4), (1,3,5), (0,1,2), (3,4,5) — 1,870–2,618); f32 readings
of the Normals payload at phase 0 and phase 2 (no unit-length
triples, components degenerate). These join the §7.9 falsified
list.

**Why the Ghidra lead could not be executed in W5c:** the route
needs `SLUS_210.04`, which exists only inside the FFNY ISO. The
archive.org item node serving it (`dn721808.ca.archive.org`,
item `slus-210.04.-def-jam-fight-for-ny`) returned HTTP 500 /
connection failure for the entire W5c session — the same outage
the W5a lane recorded from ~14:10 CDT 2026-10-21. No mirror with
the raw ISO was reachable. The executable was therefore never on
disk and no Ghidra claim is made either way.

**Exactly what cracks it next (in order):**
1. Fetch `SLUS_210.04` by the proven surgical Range method
   (ISO root dir LBA 261; `SLUS_210.04;1` at LBA 1941376,
   3,139,200 bytes) as soon as the item node recovers.
2. Ghidra (r5900:LE:32:default) decompile of the CMorph build
   path — CMorph load 0x1149B4, helpers 0x114BC0 / 0x114C38,
   `CVertexInformation::Init` 0x11EB88, and the `_BuildMorph`
   chain 0x19F970 → 0x19FBD8 — tracing how the Coordinates /
   Normals streams are DMA'd to VU1 and what role the 6×i16
   companion records and the bone matrices play in assembly.
   The EAGL VU1 microcode blobs in the exe (`__EAGLMicroCode`
   symbols are named in the `_C` objects) are the ground truth
   for the draw order if it lives VU-side.
3. With the runtime semantics known, re-run the validation the
   J4 way: build V2CP_110_0001_A + samples from at least three
   other slots, Blender-render, own-eyes verdict, using the
   cross-letter topology identity (item 4) and the `_C` BBOX
   (item 3) as hard quantitative gates before any render is
   believed.

Until then the POINTS discipline stands: the converter output and
the catalog's `topology_status=unproven_vertex_order` are
unchanged by this addendum.

#### 7.9.2 W5c Ghidra follow-up (2026-10-21, later session) — the loader chain is plumbing; consumption is VU-side

The archive.org item node recovered during the W5c session and
`SLUS_210.04` was fetched by the surgical Range method
(LBA 1941376 × 2048, 3,139,200 bytes, sha256
`4e65bf2947b3838ce372967cac448bfc8034709a6d70a87fd11d13c5f09b23b2`;
ELF32 MIPS EXEC, entry 0x100008, vaddr = fileoff + 0xFF000 as
recorded in §7.1). It was analyzed with Ghidra 12.1.4
(`r5900:LE:32:default`). The box was memory-starved (7.9 GB total,
~1.7 GB available), which killed two full-analysis JVM launches;
the completed runs used a capped heap (1.2 GB) with `-noanalysis`
plus targeted disassemble/create/decompile scripts — the six
§7.1 addresses first, then their callees. The Ghidra project and
decompiler output are retained in the W5c lane scratch
(`_w5c-work/ghidra/DefJam`, `_w5c-work/ghidra_out.txt`,
`_w5c-work/ghidra_out2.txt`); the executable itself is a game
file and is not committed — re-fetch + sha256 verify per above.

**Proven by decompilation (two levels):**

- `FUN_0019f970` (the `_BuildMorph` caller) is a **name lookup**:
  it formats a morph name (sprintf-like `0x347680`, format at
  0x3CB848), resolves it in a table (`0x16CD18`), raises the
  `_BuildMorph` error (string 0x3CBC68) on miss, and hands off to
  `FUN_0019fbd8`, which loads the object (`FUN_00114bc0` →
  `FUN_001149b4`) and registers it (`0x117628`, itself a thin
  store + `0x114BE8` + list call `0x213650`).
- `FUN_001149b4` (CMorph load) is the generic EAGL object loader:
  find-by-name (`0x101EF8`, type id 0x11), a fast-path lookup
  (`0x16D100`), then one of two constructor paths
  (`0x229DF8` / `0x229E68` — both zero a header struct, store
  name/type, then call `0x229008`, `0x228A08`, `0x229EE8`), and
  finally a **symbol resolution** step: `FUN_0022a1e8` walks the
  loaded object's symbol list comparing names (strcmp-like
  `0x346EDC`) — i.e. the runtime links the relocatable `.o` and
  resolves its named sub-objects (the mechanism behind the
  `__Morph:::` / stream-name pointers the J4 parser follows).
- `FUN_0011eb88` (`CVertexInformation::Init`) only **allocates**:
  three named buffers via the allocator `0x11A288` using the
  member-name strings `mpVertex` (0x3AFA68), `m_pColour`
  (0x3AFA90), `m_pSTQ` (0x3AFAB8); the colour struct is
  initialized to type 4 with four zeroed words. No stream data
  is read, transformed, or reordered here.

**Verdict:** the entire CPU-side chain named in §7.1 is object,
symbol, and allocation plumbing — **no CPU code in this chain
reads vertex records**, which independently confirms the §7.1
conclusion that per-vertex consumption (and therefore the draw
order) lives in the VU1 path: the GeoPrim packet build
(`0x229008` / `0x228A08` / `0x229EE8`, not yet decompiled) and
the EAGL VU1 microcode the `_C` objects name
(`LitGouraud0__EAGLMicroCode`, `IrradTexture_Skin0__EAGLMicroCode`).

**Updated "what cracks it next":** (1) decompile the packet-build
trio `0x229008` / `0x228A08` / `0x229EE8` in the retained Ghidra
project — if CPU code assembles the VU packets from the Morph
streams, the vertex order is written there; (2) if the packets
are passed through untouched, extract the EAGL VU1 microcode
blobs from the executable and read the vertex fetch/transform
loop (VU disassembly — Ghidra's r5900 family covers the EE core;
a VU-capable disassembler pass is the open tooling need);
(3) validation gates unchanged (§7.9.1 item 3–4 + §7.9.2's BBOX /
topology gates). The POINTS discipline still stands.

#### 7.9.3 W5d follow-up (2026-10-21) — the packet-build trio is the ELF linker; the microcode is not in the exe

The trio named at the end of §7.9.2 was decompiled in the retained
Ghidra project (same targeted `-noanalysis`, 1.2 GB heap discipline;
full decompilation + disassembly retained in the W5d lane scratch as
`ghidra_out3.txt`). The §7.9.2 guess that these are "GeoPrim packet
build" functions is **wrong**, and the correction matters:

- `0x229008` is the **relocatable ELF loader**. It allocates a
  0x830-byte object record, reads the ELF header fields the J4 parser
  also reads (section count at header +0x30, shstrndx at +0x32),
  walks the 0x28-byte section headers, dispatches on section type
  (2/3/8/9/10/11 plus the MIPS processor-specific range
  0x70000005–0x7FFFF421), and builds the standard gABI symbol hash
  table (the `& 0xF0000000` / `>> 24` xor-fold loop). Its only callees
  in this role are the allocator (via the pointer at 0x38146C) and the
  error printer `0x227E10`.
- `0x228A08` is the **runtime relocator / symbol resolver**. It walks
  type-9 (SHT_REL) sections and applies the relocation-type switch
  (case 2 = add the resolved value, case 4 = R_MIPS_26 jump-target
  patch with region check, cases 5/6 = HI16/LO16 halfword adds). An
  undefined symbol is resolved first against the already-loaded
  object list (`0x229BC8` name compare), then through a per-object
  resolver callback (object record +0x82C), then a global registry
  (0x4A2CA8 / 0x4A2CE8); the resolved address minus the section base
  is written back into the symbol entry (+0x10), tagged at byte +0xD
  with the resolution source (2 = loaded object, 3 = callback,
  4 = registry, 5 = dynamically loaded) and flagged +0xE = 1.
- `0x229EE8` is an 8-byte **stub**: `jr ra` / `li v0,1` (return 1).

**Verdict (transform vs pass-through): neither — there is no packet
build on this path at all.** The trio contains no VIF opcode, no
GIFtag construction, no DMA setup, and no read of any vertex record,
in either the decompilation or the raw disassembly. Together with
§7.9.2 this closes the CPU side completely: the entire CMorph load
path (name lookup → ELF load → relocate → symbol-resolve → allocate)
never touches vertex data. The streams are handed to the render path
as loaded ELF sections; consumption — and therefore the draw order —
is render-time, VU1-side. The "packet-build trio" lead is exhausted
and should not be re-run.

**Microcode extraction — attempted, stall point located precisely.**
The `_C` objects do not contain the microcode: in every sampled
`_C` (110/111/113) `LitGouraud0__EAGLMicroCode` and
`IrradTexture_Skin0__EAGLMicroCode` are **undefined external symbols**
(symbol value 0, size 0), resolved at load time by `0x228A08` through
the chain above. Nor is the code in the executable under those names:
a full byte scan of `SLUS_210.04` finds only two `__EAGLMicroCode`
names — `Particle0__EAGLMicroCode` and `HeatParticle0__EAGLMicroCode`
(file offsets 0x2DC3F8 / 0x2DC418, in the render-method name table
beside the "Particle model pcode" / "Particle render method pcode"
strings). No `LitGouraud` / `Skin0` / `Gouraud`-suffixed microcode
name or string exists anywhere in the exe. The skinning/lighting
microcode therefore reaches the resolver from a **separate runtime
object or the global registry** (0x4A2CA8 / 0x4A2CE8, populated at
device init), i.e. from another file on the disc — most plausibly an
EAGL runtime/microcode object inside the game's VIV/BIG archives —
and not from the two artifacts this lane holds (exe + CAW `.o` set).

One corroborating datum from the `_C` symbol tables: the
`__EAGL::GeoPrimState` symbols declare
`SetPrimitiveType=EAGL::PT_TRIANGLESTRIP`, independently confirming
the strip framing the J4 parser already uses. It does not order the
vertices inside the strips.

**Next crack (in order):** (1) census the extracted 2,624 `.o` set
(and, if absent there, the disc's VIV/BIG contents) for the object
that *defines* `LitGouraud0__EAGLMicroCode` (symbol value ≠ 0) — that
object's `.data` is the VU1 microcode blob; (2) disassemble it with a
VU-capable pass (Ghidra emotionengine-reloaded VPU language, already
present in the local Ghidra extensions) and read the vertex loop's
buffer walk + GIF emit order; (3) test the bone-local assembly lead
(94-bone palette, 112-byte bind/inverse-bind records) against that
loop; (4) validation gates unchanged (cross-letter topology identity,
`_C` BBOX spans 17.44/19.33/9.0, Blender renders of
V2CP_110_0001_A + 111/112/113, own-eyes). Until a render proves
otherwise the POINTS discipline still stands:
`topology_status=unproven_vertex_order` is unchanged, and no
converter or catalog change is made by this addendum.

#### 7.9.4 W5e follow-up (2026-10-21) — full held-data census: the defining object is NOT held

Step (1) of §7.9.3's next-crack list is now done, at full held-data
scope. Method: the in-repo J4 parser only
(`customization/tools/convert_defjam_o.py:parse_elf` +
`eagl_refpack.py`), applied to every held Def Jam object. A symbol
counts as DEFINED iff its ELF symbol value ≠ 0 or its size ≠ 0 (the
§7.9.3 samples are value 0 / size 0 = undefined externs). Non-ELF
held files were byte-scanned for the target names
(`LitGouraud0__EAGLMicroCode`, `IrradTexture_Skin0__EAGLMicroCode`,
and the `__EAGLMicroCode` marker generally).

**Coverage (exact, per class):**

| Class | Scope | Objects parsed | `__EAGLMicroCode` refs | DEFINED |
|---|---|---|---|---|
| (a) | wrestling-game `models/caw-parts` `.o` | 2,624 `.o` (1,857 ELF-parsed; 767 fail RefPack decompression — see below) + 5,324 sibling files byte-scanned | 1,331 | **0** |
| (b1) | wrestling-game `models/fighters` `.o` (2026-10-14 V2IP extraction) | 156 `.o` (155 parsed, 1 RefPack failure) + 78 files scanned | 292 | **0** |
| (b2) | wrestling-game `models/venues` `.o` | 499 `.o` (all parsed) + 359 files scanned | 385 | **0** |
| (b3) | wrestling-game `motion/` (incl. `MAIN_ALL.DAT`, `ANIMTAGS.DAT`) + `data/` + `tools/` | 770 files byte-scanned | 0 | **0** |
| (c) | on-disk lanes: `_w5c-work` (13 sample `.o` + 2× `SLUS_210.04`) and `defjam-work` surgical tree (156 `.o`) | 324 `.o` parsed (the two roots' V2IP sets are duplicate copies) + 446 files scanned | 590 | **0** |

Repo-set total (a+b): **3,279 `.o`**, 2,008 microcode references,
**zero definitions**. Every reference in every family is an
undefined extern (value 0, size 0). Families referenced, all
undefined: `LitGouraud0`, `IrradTexture_Skin0`,
`DJIrradTextureEnvmap_Skin10`, `DJFXSparkle_Skin0`, `IrradTexture0`
(models); `ClipTextureDim0`, `ClipGouraud0`, `TextureDim_Skin0`,
`ClipTexture0`, `DJClipTextureEyeEnvmap10/20/30/40/50`,
`DJIrradTextureEnvmap_SkinVenue10/20/30`, `ScrollTexture0`,
`PlanarShadow_Skin0` (venues). `SLUS_210.04` re-confirmed by raw
scan: only `Particle0` / `HeatParticle0` names (§7.9.3); the two
target names do not occur in the exe at all.

Two coverage caveats, stated exactly:

- **768 `.o` are unparseable** (767 CAW + 1 fighters): no valid
  RefPack record (the §7.10 `no_valid_refpack_record` population),
  no ELF magic, and no plaintext occurrence of either target name
  or the `__EAGLMicroCode` marker anywhere in their bytes. They are
  corrupt extractions, symbol-censused only to that depth; their
  disc originals sit in the already-extracted V2CP/V2IP archives,
  so closing this gap needs a re-extraction pass, not a new archive.
- `motion/base00/base00.ord` (2,197,856 bytes) carries ELF magic but
  its section table lies beyond EOF for the J4 parser; its raw byte
  scan is negative for all three needles, as is every other motion
  file (`.orl/.ord/.mnl`, `MAIN_ALL.DAT`, `ANIMTAGS.DAT`).

**Verdict: the object that defines
`LitGouraud0__EAGLMicroCode` / `IrradTexture_Skin0__EAGLMicroCode`
is not in any held data.** It remains on the disc, in archives never
extracted. It is therefore a named target for the IA pickup (the
archive.org item `slus-210.04.-def-jam-fight-for-ny` node was down
through W5b, checkpoint `gap-closure-w5-defjam` §W5b): on recovery,
extract the archives below and re-run this exact census (J4 parser,
value ≠ 0 test) over every new entry, plus re-extractions of the 768
corrupt files and the five entry-0 slots.

**Uncensused archives — the IA-gated set (W5b manifest, 912
entries, named pickup priority 1 — model/object carriers):**
`/ASSETS/BLINGFX.VIV` (2), `/ASSETS/DECALFX.VIV` (1),
`/ASSETS/FEPOSES.VIV` (18), `/ASSETS/V2GA.VIV` (21),
`/ASSETS/V2BG_CIN.VIV` (27), `/ASSETS/TROPHIES.VIV` (41),
`/ASSETS/PROPS.VIV` (41), `/ASSETS/SHOPS.VIV` (52),
`/ASSETS/V2IP_CIN.VIV` (56), `/ASSETS/V2CM.VIV` (128),
`/ASSETS/V2WP.VIV` (212), `/ASSETS/V2TA.VIV` (313).

**Uncensused archives — the rest of the never-extracted disc set
(W5a `REMAINDER.json`: 78 never-touched archives in total, 66 beyond
the W5b manifest above):** `/ASSETS/AI/AI.VIV` (779),
`/ASSETS/IRRAD/IRRAD.VIV` (463), `/ASSETS/NIS.VIV` (32),
`/ASSETS/ICROWD.VIV` (14), `/ASSETS/CINCROWD.VIV` (3),
`/ASSETS/TEXANIM.VIV` (2), `/ASSETS/SUBTITLE.VIV` (40),
`/ASSETS/CINEMA/` GF1A, GF1B1–B4, GF1C, GF1D, GF2A–2E, GF3A, GF3C
(6–19 entries each) and SC00–SC06, SC07A, SC07B, SC08–SC21 (4–47
entries each); `/FONTS/FONTS.VIV` (10), `/IOP/BOOT.VIV` (7);
audio families `/AUDIO/MUSIC0/1/3/4.VIV`, `/AUDIO/SFX0/1/2.VIV`,
`/AUDIO/SPEECH3.VIV` (table-censused, never extracted — listed for
completeness; no held evidence makes them object carriers).
Never even table-censused (W5a census errors, contents wholly
unknown): `/ASSETS/MISC.VIV` and `/SCREENS/SCREENS.VIV` (BIG4
containers), `/ASSETS/CINEMA/GF3B.VIV`, `/AUDIO/MUSIC2.VIV`,
`/AUDIO/SFX3.VIV`, `/AUDIO/SPEECH1.VIV`, `/AUDIO/SPEECH2.VIV`,
`/FONTS/BEFONTS.VIV`, `/MOVIES/MOVIES.VIV`. The three motion
archives (`/MOTION/WRES_ALL.VIV`, `/MOTION/BASE00.VIV`,
`/MOTION/BLAZIN.VIV`) are a distinct case: their contents are held
and file-censused (class b3 above, negative), but their BIGF tables
were never walked, so an unlisted entry cannot be ruled out.
Finally, the **entry-0 slot of each already-extracted archive**
(`V2CP_1/2/3.VIV`, `V2IP.VIV`, `V2BG.VIV`) was never read (W5b
entry-0 targets, LBAs in the W5b manifest) — five unread entries,
names known only by elimination.

No vertex-order rule is stated by this addendum: the microcode was
not found, so there is nothing to disassemble and no order to read.
No guessed orders. The POINTS discipline stands unchanged:
`topology_status=unproven_vertex_order`; no converter or catalog
change is made by this addendum.

### 7.10 Phase B census — the extracted set (2026-10-21)

The wrestling-game teardown tree holds **2,624 `.o` + 5,319 `.ssh`**
extracted from the disc. The PARTS-INDEX's 22,360 entries cover
only codes 110/111/112/113 (the four CAW slots); the extracted set
spans the game's wider part taxonomy (codes 110–532). The
remaining **19,736 indexed parts were never extracted** — their
bytes are still inside the disc image; extracting them is a
separate teardown job (ISO-scale), not part of this converter's
scope. Converter census over the 2,624 extracted `.o`:

- converted (Morph pool + textures extracted): **1,201**
  (777 with ≥1 decoded texture PNG; 2,178 PNGs total — parts carry
  multiple `_A01_0N.ssh` variants, all decoded)
- compiled_variant (`_C` family): **654**
- no_valid_refpack_record: **767** — a family concentrated in
  codes 311/312 whose files carry no RefPack record at all (heads
  like `07 01…`, `90 11…`); root cause unresolved (other container
  or corrupt teardown extractions) — a teardown-QA question, not
  guessed here. Converter validation accepts only RefPack records
  that decompress byte-exactly to their declared size.
- pose_palette_only: **2**
- errors: **0**

Phase B format findings folded into the converter: strip-index
fields are source ids, not positions (gaps allowed; walk requires
strictly increasing ids); SHPS palettes vary (u24 palette-block
size — 152-entry palettes exist, V2CP_142_0003); partial-page
textures (height not a multiple of 16, e.g. 64×62 V2CP_361_0013)
store the padded-page swizzle sequence with padded rows' bytes
removed (proven by eye).
