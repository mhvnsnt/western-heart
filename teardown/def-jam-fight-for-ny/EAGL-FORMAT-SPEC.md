# Def Jam: Fight for NY — EAGL Format Spec (Phase R, J4)

**Date:** 2026-10-20 · **Lane:** creation-suite gap-fill J4 (Def Jam converter)
**Status:** Outer format **closed with evidence**. Geometry vertex-stream
layout is the one remaining open layer; the route to close it is named in
§6. This spec supersedes the guesses in `EAGL-FORMAT-ANALYSIS.md` (kept
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
