# King of Colosseum II — Teardown

**Game:** King of Colosseum II (Spike, PS2, 2004, Japan-only, SLPM-65602,
VER 1.03, NTSC). The 3D Fire Pro successor: deep timing-based grappling,
crowd-psychology system, ~200 wrestlers (NJPW, NOAH, AJPW, ZERO-1, WJ).
CAGEMATCH rates it #4 of all wrestling games (9.64/10).
**Lane:** E (KoC2) · **Date:** 2026-11-19 · **Owner priority:** TOP 2.

> **Status: EXTRACTION COMPLETE — 49,214 files, all decoded.** The ISO is
> sourced and hash-verified; all five archives are extracted (Spike
> container format + custom LZSS both reverse-engineered in this lane);
> the master string table, music table, commentary script, AFS audio
> index, threshold tables, grade grids, and 273 camera scripts are
> parsed into `data/`. Models (`.mdl`) and motion (`.MVS`) are extracted
> but their geometry/animation layouts are only partially mapped —
> see §5 and §9. The ISO itself is never committed to any repo.

## 1. Provenance (where every file came from)

| Artifact | Source | Size | Hash | Label |
|---|---|---|---|---|
| `King of Colosseum II (Japan).7z` | archive.org item `ps2-isos-and-translations` — https://archive.org/download/ps2-isos-and-translations/King%20of%20Colosseum%20II%20%28Japan%29.7z | 1,738,818,479 B | md5 `319396fd807341fa4b6586f2f67f1eeb`, sha1 `6706da7f2b0395777f6682576ee65a96781502c1` (both match archive.org metadata), sha256 `54b2ee70df965de71ef33a9445dbe906630c4d5a5d0893b303325745e65ce372` | FETCH-VERIFIED |
| `King of Colosseum II (Japan).iso` | extracted from the 7z (7zip 23.01) | 4,593,778,688 B | sha256 `7daa1f8c950272f24e9888d26338645fdbac1974da8dbf43b30c0042ceed0511` | FETCH-VERIFIED |
| `CDRomance.url` (inside the 7z) | packed with the 7z (2020-07-21) | 112 B | — | Provenance note: the 7z was packed from a CDRomance download |

The ISO / 7z itself is **never committed** to any repo. It lives in the
lane workdir only. Extracted files and data go here; binaries too large
for the text-only push path are listed in `FILES-SHA256.txt` with their
hashes and flagged to the coordinator (see §6).

**Binary store (2026-11-19, lane W2):** the ~2.7 GiB of extracted
binaries (`kc2fire000/`, `kc2fire001/`, `kc2fireafs/`, `kc2firemvs/` +
manifests, 49,208 files) are copied to the Oracle VM at
`/data/koc2/` (host `bannon-oracle-vm`, 132.145.194.139) as the durable
binary home — the lane workdir is no longer the only copy. The whole-game
ISO (`iso/`, 4.3 GiB) is NOT in that copy.

## 2. ISO layout

Disc created 2004-07-28. `SYSTEM.CNF`: `BOOT2 = cdrom0:\SLPM_656.02;1`,
`VER = 1.03`, `VMODE = NTSC`. 12 files, 2 folders:

| Path | Size | What it is |
|---|---|---|
| `SLPM_656.02` | 3,048,408 B | Game executable (ELF, MIPS). Built 30 Jun 2004 (SJ/PS2EE Ver.6.24). Contains the data-structure names `WrestlerData`, `MoveBase`, `MotionBase`, `BasicMotion`, `ExtraMotion`, `ExtraEditMotion`, `PartyData`, `TeamData`, `PartyOrder`, `PilonData`, `MotionCommand`, `lpMatchmaker*`, `lpSurvival*`, and its own TIM2 loader error strings. |
| `MODULES/MODULES.BIN` | 393,216 B | Spike container, 15 files (raw IRX IOP modules; file 0 is a raw ELF). |
| `MODULES/IOPRP300.IMG` | 275,345 B | Standard IOP image (starts with "RESET"). |
| `DATA/KC2FIRE.DIR` | 52 B | Manifest listing `kc2fire.afs`, `kc2fire.mvs`, `kc2fire.000`, `kc2fire.001`. |
| `DATA/KC2FIRE.AFS` | 1,874,507,776 B | Standard AFS archive: **9,003 files** (9,000 `.adx` audio + 3 `.sfd` videos). |
| `DATA/KC2FIRE.MVS` | 48,629,760 B | Spike container: **16,660 files**, all stored raw (motion data). |
| `DATA/KC2FIRE.000` | 244,441,088 B | Spike container: **7,519 files**, 4,167 LZSS-compressed (textures, sound banks, text/data). |
| `DATA/KC2FIRE.001` | 239,804,416 B | Spike container: **16,017 files**, 16,015 LZSS-compressed (models, textures, small data). |
| `DATA/HELLO.FOR`, `DATA/GOOD.BYE` | 1,073,741,824 B each | **Entirely zeros** (verified by full streaming scan; identical sha256 `49bc20df15e412a64472421e13fe86ff1c5165e18b2afccf160d4dc19fe68a14`) — disc-layout padding, nothing to extract. |
| `DATA/LAST.DAY` | 34,603,008 B | **Entirely zeros** (sha256 `c28a8f34a7efbd4cffe424a21e4a6e4d5bfa8b5daccc381f9eb3c1dc5bac689c`) — padding. |

Total archive files: **49,214** (9,003 + 16,660 + 7,519 + 16,017 + 15).

## 3. Archive format: Spike container (KC2FIRE.000/.001/.MVS, MODULES.BIN)

Reverse-engineered in this lane, validated on all four archives
(offset chains perfect; data_start + sum(stored_size) == file size
exactly on all four):

```
Header (8 bytes): u32 0x800 (block size?), u32 file_count
Entry table: file_count x 16-byte LE entries:
    u32 offset            (relative to the data region start)
    u32 stored_size       (bytes as stored; padded)
    u32 decompressed_size (bytes after decompression)
    u32 flags             bit 0 = valid; bit 16 = LZSS-compressed
                          (.000/.001 use 0x00010001;
                           .MVS/MODULES.BIN use 0x00000001 = raw)
Zero padding from the end of the table up to the next 2048-byte
boundary; the data region starts there, files packed contiguously.
```

Files carry no names — extracted as `fileNNNNN.bin`. Extractor:
`tools/kc2_extract.py` (decompresses inline via `koc2_lzss.py`).

## 4. Compression: Spike LZSS (CRACKED in this lane)

`tools/koc2_lzss.py`. Solved from known plaintext: compressed TIM2
files whose decompressed form was already known (neighbouring
uncompressed TIM2s of the same size). Verified: files 15972/15973 of
KC2FIRE.001 decode to exactly their catalogued sizes and reproduce
the known TIM2 header byte-for-byte; all 20,182 compressed files
across `.000`/`.001` decode to exactly their catalogued sizes.

```
Stream = groups; each group = 1 flag byte + 8 items, LSB first:
  bit = 1 -> literal: 1 byte copied to the output.
  bit = 0 -> match: 2 bytes (b1, b2).
Match: offset = (b1 | ((b2 & 0x0F) << 8)) - 1   (absolute position in a
         4096-byte ring buffer; the stored value is offset+1, 1-based)
       length = (b2 >> 4) + 2                    (lengths 2..17)
Ring buffer starts zero-filled, write position starts at 0. Matches
may overlap the write position (runs are encoded that way).
The decoder stops after exactly decompressed_size bytes.
```

Two quirks found while validating:
- A stored offset of 0 means ring position 4095, not -1 (the
  offset must be masked to 12 bits after subtracting 1).
- About 6% of files (1,492) end with a run of `(0,0)` matches — all
  zero token bytes — and the stored blob is cut short a few bytes
  mid-run. The decoder treats input as zero-extended past its end,
  which reconstitutes the truncated matches and lands exactly on the
  catalogued size. All 1,492 recovered this way.

Stored streams are usually zero-padded (to a 2048-byte boundary for
large files); the decoder ignores trailing input past the end of
the stream. Community state (ResHax topic 18443): decompression was
already solved by the community; byte-exact *compression* is solved
for TIM2 textures (Oct 2025) but still open for models (May 2026).
This lane only needs decompression.

## 5. File formats decoded

| Format | What it is | Decoder | Status |
|---|---|---|---|
| TIM2 | PS2 textures (`.001`: 4,641; `.000`: 3,282) | `tools/tim2_decode.py` | Header + layout cracked; color mapping partial (see below) |
| `.mdl` | Models (`.001`: ~6,413) | — | Section structure mapped; vertex/face layout open (community open problem) |
| IECS | Sound banks (`.000`: ~759+) | — | Chunk structure mapped (Vers/Head/Vagi/Smpl) |
| ADX | Audio (AFS: 9,000) | standard CRI ADX | Extracted; IDs mapped by `data/afs-ids.json` |
| SFD | Video (AFS: 3) | standard CRI Sofdec | Extracted (movtop, KC2Opening, KachinukiOP) |
| MVS | Motion data (16,660 files) | — | Extracted; packed format, layout open |
| Text data | Strings, music, commentary, tables, camera scripts | `tools/koc2_strings.py`, `tools/koc2_text.py`, `tools/koc2_tables.py` | **Fully parsed — see `data/`** |
| AFS | Archive (KC2FIRE.AFS) | `tools/kc2_afs.py` | Complete (9,003 named files) |

### TIM2 (KoC2 quirks — found in this lane)

- The picture header does **not** start at offset 16: KoC2's TIM2s
  put it at **0x80** (112-byte zero gap after the file header), with
  `header_size` 0x80, so the CLUT starts at picture_start + 128.
  `tim2_decode.py` scans for a consistent header instead of assuming
  offset 16.
- The `pict_format` byte reads 0x01 on files that are plainly 8-bit
  indexed (128×128, 16,384 image bytes, 256-color 32-bit CLUT), so
  the decoder derives the mode from `image_size / (width*height)`
  + CLUT presence.
- The image data is stored **4-way byte-interleaved**: bytes ≡ k
  (mod 4) form stream k, and the 4 streams are the 4 quadrants of
  the 128×128 image (verified by lag analysis: lag-4 neighbours are
  the most similar; quadrant reassembly drops the smoothness error
  from 51.8 to 22.3). **Update (lane W2, 2026-11-19):** quadrant
  reassembly improves colour smoothness on 5/5 test files of several
  sizes, but looks WRONG on at least one 64×64 file (file10853, where
  linear order looks coherent) — the layout is NOT settled.
  `tim2_decode.py --deinterleave` applies the quadrant reassembly as
  an option; the default stays linear. The full PS2 GS
  page/block/column swizzle scores between linear and quadrant and
  is not the answer either.
- The CLUT is in file order, but the palette is dark and colours
  render speckled — the colour mapping is still open. File 15974
  (the test case) may be a tiled/noisy texture by design; more
  samples are needed before the TIM2 colour path is claimed solved.
  **Update (lane W2):** a 60-file survey shows palettes are NOT
  systematically dark (mean brightness 123/255) — file 15974's dark
  palette is per-texture, and the CLUT is smooth in file order
  (mean adjacent-entry diff 10.5; 4-way deinterleave of the CLUT is
  worse at 27.6). `clut_type` 0x43 (CSM2 flag, bit 0x40) appears on
  ~5% of TIM2s, all 4-bit indexed with 32-colour CLUTs so far; the
  CSM2 unswizzle is not verified (best 5-bit permutation only
  improves palette smoothness 29.2 → 26.3 on the one non-trivial
  sample) — the decoder warns on CSM2 and decodes in file order.
  The game's own ELF contains the strings
  `Tim2CheckFileHeaer: TIM2 is broken (2)` and `Illegal clut and
  texture combination`, confirming the loader checks the
  CLUT/texture combination.

### `.mdl` models (section structure — file 0 of `.001` as example)

A model file is a chain of sections that tiles the file. Each
section starts with `(u32 size, u32 type, u32 a, u32 b)` followed by
3 float vectors at +16 and payload. File 0 (56,576 bytes)
has 18 sections; types seen: 0 (skeleton/bones?), 1 (mesh parts),
2, 4. The payload from ~0x88 on is PS2 VIF/GIF DMA packet data
(`00 10` markers) — the geometry is stored as native display lists,
which is why `.mdl` → OBJ conversion is still the community's open
problem (ResHax, May 2026). Section map documented; vertex/face
extraction is a follow-up RE task, not claimed here.

**Update (lane W2, 2026-11-19 — `tools/koc2_mdl_sections.py`):**
729 of the first 3,000 non-TIM2 `.001` files parse as clean section
chains (the rest are other file types). Section counts are mostly 18
(633), some 17/19/20/21. Every model file has exactly one type-2 and
one type-4 section (type 4 is always last, with `a`=1), ~4 type-0
and ~12 type-1 sections. Field `b` ≈ 2.4× section size (hypothesis:
unpacked VU-memory size after VIF unpack — not verified). The three
+16 vectors are **not** identity quaternions in general: they are
`(0, y, z, 1)` triples, the middle one always `(0,0,0,1)` — section 0
is identity, mesh sections are not (per-part transform or YZ
bounding-box min/max; interpretation open). A trailer of a repeated
u16 (`0x1066`/`0x1067`, 16–96 bytes) follows the last section. The
payload is u16 component data with `0x1000` fixed-point-1.0 markers
and repeated 6-word chunks (shared vertices); no VIFcode words were
found in the sampled payload, so the VIF unpack commands (if any)
live elsewhere in the section.

### IECS sound banks

Chunked container, chunk = `IECS` + 4-byte reversed name + u32 size:
`Vers` (version, 0x10 bytes), `Head` (header, 0x40), `Vagi` (VAG
info table — entries of (u32 offset, `11 2b 00 ff`)), `Smpl`
(sample data, VAG ADPCM). Sizes 288–1,296+ bytes; ~759 files in
`.000` (plus the 288/560-byte sizes, which are also IECS).

### MVS motion files

16,660 small raw files (197–12,503 bytes, mean 2,392). Common heads
`eb 37 00 02`, `6b 37 00 02`, ... Files 0 and 1 share a 128+ byte
prefix (same move, different lengths — truncated variants or shared
intros). Packed binary with embedded floats; layout open.

**Update (lane W2, 2026-11-19 — see `MVS-FORMAT.md`,
`tools/koc2_mvs_survey.py`):** only 8,205 distinct contents (max 36
copies of one motion — shared motions stored per wrestler/move slot).
Two families by bytes 2–3: A `(0x00,0x02)`, 15,672 files; B
`(0x01,0x00)`, 964 files, much larger on average; plus 24 rare files
with `(0x02,0x00)`/`(0x03,0x00)`. Byte 1 is very likely a frame (or
keyframe) count: corr(byte 1, size) = 0.83, size ≈ 596 + 16.1 × byte
1. At ~16 bytes/frame the format is keyframed/sparse or
delta-compressed, not dense per-frame joint data. The bitstream
itself is still not decoded.

### Text data (fully parsed — in `data/`)

| File | What it is | Parser output |
|---|---|---|
| `.000` file 02010 (197,125 B) | **Master string table**: header (25 categories, 4,021 strings, 68,237 string bytes), 25-category index, **32-byte record table, CRACKED (lane W2, 2026-11-19 — see `FILE-02010-FORMAT.md`)**: u32 string offset, u8 category, u16 index-in-category; category 0 (wrestler names) has federation (byte @0x07) and person-id (u16 @0x04, a permutation of 0..427) fields; the real per-wrestler data (movesets, stats) is in file 01999, surveyed in the same doc | `data/koc2-strings.json`, `data/koc2-file02010-records.json`, `data/koc2-file01999-survey.json` |
| `.000` file 01454 (23,184 B) | **Music table**: 483 slots × 48 bytes, 240 non-empty entrance-theme titles | `data/koc2-music.json` |
| `.000` file 02030 (331,155 B) | **Commentary script**: 20 ADX refs + 8,983 lines with situation codes (a/b general, fc/kc/nc/oc per-fed, VS versus, *BGM music cues); ends with `KC2OPENING_SFD`, `KACHINUKIOP_SFD` | `data/koc2-commentary.json` |
| `.000` file 02031 (388,097 B) | **AFS file-ID header** (a C header left in the game data): `#define K06_ADX (0) /* k06.adx */` × 9,003; order verified identical to the AFS index | `data/afs-ids.json` |
| `.000` files 02893–02900 | **Threshold tables** (8 files, 44 blocks): value → score 50–90 in 8-row blocks; block scales 1600/2000/5600/6000/7000/10000/15000/28000/60000 look like venue capacities — likely the Audience Ranking / Match Maker attendance scoring (interpretation, not verified fact) | `data/threshold-tables.json` |
| `.000` files 02401–02402 | **Grade grids** (16 grids of 5×5 letter grades D/C/B/BC/CD/BCD); purpose unidentified | `data/grade-grids.json` |
| `.000` files 02266+ (273 files) | **ACW camera scripts**: plain text, `{ frame, {x,y,z}, {rx,ry,rz} }` keyframes (`MaxFrame`, `_iAugment`, `_iMode`) — camera paths for entrances/cutscenes | `data/acw/*.txt` (284 text files total incl. the header/grids/tables above) |

The 25 string categories (labels from content): 0 wrestler names
(429 entries, **363 distinct wrestlers** after stripping version
suffixes like “02Ver”/“IWGPVer”), 1 wrestle styles (13), 2 body
types (13), 3 size classes (5: SS/S/M/L/LL), 4 costume types (11),
5 boolean (2), 6 body parts (234), 7–14 costume parts by region
(52/52/207/207/406/258/258/137), 15 wrestler names, 2nd list (429),
16 staff/referees (23), 17 entrance attire (185), 18 gowns (2),
19 booleans (31), 20 title names (12), 21 entrance items (133),
22 nicknames/catchphrases (241), 23 music themes (336), 24 entrance
narration (345).

## 6. What was pulled (extracted data inventory)

| Archive | Files | Decompressed | Contents |
|---|---|---|---|
| KC2FIRE.001 | 16,017 | 468.1 MiB | ~6,413 models, 4,641 TIM2 textures, 2,145 × 128-byte template records (2 distinct contents), misc data |
| KC2FIRE.000 | 7,519 | 341.5 MiB | 3,282 TIM2 textures, ~759+ IECS sound banks, master strings, music, commentary, AFS header, threshold/grade tables, 273 ACW camera scripts |
| KC2FIRE.MVS | 16,660 | 38.0 MiB | Motion data (raw) |
| KC2FIRE.AFS | 9,003 | 1.86 GiB | 9,000 ADX audio + 3 SFD videos (all named) |
| MODULES.BIN | 15 | 0.4 MiB | IRX IOP modules (raw) |
| **Total** | **49,214** | **~2.7 GiB** | |

Manifests: `FILES-SHA256.txt` (sha256 of every extracted file) and
per-archive `index.csv` files (offsets/sizes/flags/names) are in the
lane workdir and staged here where text-sized. **Binary files
(models, textures, audio, video, motion) are NOT pushed through the
text-only push path** — they are listed in the manifest with hashes
and flagged to the coordinator for a binary-capable transfer
(git-lfs / release / Oracle VM). What IS pushed here: tools, docs,
parsed text data (JSON), ACW scripts, indexes, manifests.

## 7. What wired into Bannon

- `docs/koc2/` — grappling wiring spec, crowd wiring spec, README
  (both specs' extraction checklists now filled with real values
  from §5: roster 363 wrestlers / 429 entries, 240 themes, 8,983
  commentary lines, threshold tables as the audience-score model).
- `assets/moves/` — `koc2-moveset-slots.json` (271 slots, 34
  categories), `koc2-systems.json` (styles, rules, skills,
  parameters, COM Logic, titles), `koc2-roster.json` (real roster
  from the string table), `koc2-text-data.json` (real text-data
  counts + threshold tables summary).
- No UE C++ in this lane (Lane A owns that; C++ needs are flagged
  in the specs).

## 8. Tools in this dir

| Tool | What it does |
|---|---|
| `tools/kc2_extract.py` | Spike container extractor (decompresses inline) |
| `tools/koc2_lzss.py` | Spike LZSS decompressor (cracked in this lane) |
| `tools/kc2_afs.py` | AFS archive extractor (mmap-based, keeps real names) |
| `tools/tim2_decode.py` | TIM2 → PNG (KoC2 quirks handled: 0x80 header, mode from sizes; lane W2: `--deinterleave` quadrant option, CSM2 warning) |
| `tools/koc2_file02010.py` | File 02010 32-byte record table → JSON (lane W2) |
| `tools/koc2_file01999.py` | File 01999 WrestlerData survey → JSON (lane W2) |
| `tools/romanize_koc2.py` | Romanize the 363 KoC2 roster names (FAQ-backed + machine, lane W2) |
| `tools/koc2_mvs_survey.py` | MVS motion-file structural survey (lane W2) |
| `tools/koc2_mdl_sections.py` | `.mdl` section-chain parser (lane W2) |
| `tools/kc2fire_inspect.py` | Archive inspector: header hexdump, magic scan, string sample |
| `tools/koc2_strings.py` | Master string table (file 02010) → JSON |
| `tools/koc2_text.py` | Music table (01454) + commentary script (02030) → JSON |
| `tools/koc2_tables.py` | AFS header (02031) + threshold tables (02893–02900) + grade grids (02401–02402) → JSON |

## 9. Open items (not claimed)

- **TIM2 colour mapping**: palettes are NOT systematically dark
  (60-file survey, lane W2) and the CLUT is in file order, but the
  image-data layout is still not settled (quadrant deinterleave
  helps smoothness yet looks wrong on one 64×64 file; GS swizzle
  does not fit either) and the CSM2 CLUT unswizzle is unverified.
  Needs the ELF TIM2 loader disassembled or a reference
  implementation.
- **`.mdl` geometry**: section map done (729-file survey, lane W2);
  vertex/face/bone layout open — needs a VIF unpack interpreter
  (community open problem since May 2026).
- **MVS motion layout**: header families + frame-count field
  surveyed (lane W2, see `MVS-FORMAT.md`); the bitstream itself is
  not decoded — needs the ELF `MotionBase` loader (xref 0x1189B8).
- **File 01999 WrestlerData interior**: the 441×2285-byte records
  are surveyed (names, finishers located, lane W2) but the interior
  layout (stats, moveset slots, COM Logic, costume data) is still
  open — the biggest remaining KoC2 RE job. Cross-checks: Jerrold
  Ng FAQ per-wrestler movelists; ELF `MoveBase`/`MotionBase`
  loaders (xrefs 0x118994/0x1189B8).
- **Threshold tables' purpose**: the venue-scale reading is
  interpretation; the game code path that reads them is not traced.
- **Grade grids' purpose**: unidentified.
- **ResHax attachments** (community LZSS script, sample `.mdl`) and
  **modding Discord/Drive** (English menu mod, texture packs) remain
  BROWSER-GATED — see lane `BROWSER-QUEUE.md`. Not needed for what
  is claimed here.

## 10. Sources (evidence labels)

Full log: lane `VERIFY-LOG.md`. Summary:
- FETCH-VERIFIED: archive.org metadata + 7z (md5/sha1/sha256 match);
  ISO sha256; every extracted file sha256 in `FILES-SHA256.txt`.
- SEARCH-VERIFIED: Jerrold Ng FAQ/Movelist v1.0; GameSpot review;
  CAGEMATCH (#4, 9.64); ResHax topic 18443; KoC2 modding FAQ;
  bordersdown review thread.
- BROWSER-GATED: ResHax attachments; modding Discord + Google Drive.
