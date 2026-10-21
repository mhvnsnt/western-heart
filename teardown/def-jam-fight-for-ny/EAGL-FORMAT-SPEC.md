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
