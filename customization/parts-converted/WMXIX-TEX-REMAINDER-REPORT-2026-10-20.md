# WMXIX texture remainder — conversion report (Job 2, 2026-10-20)

Tool: `customization/tools/decode_wmxix_tex_remainder.py`
Builds on: `teardown/wmxix/decode_tpl.py` (validated TPL decoder) and the
`customization/tools/convert_caw_parts.py` pattern from PR #398.

## Scope

PR #398 decoded 1,044 of 1,470 WMXIX `.tex` textures. This job took the
exact remainder recorded in `customization/parts-converted/CATALOG.json`:

| status at start | count |
|---|---|
| blocked_no_tpl | 426 |
| not_converted | 12 |
| palette_only | 8 |
| **total target** | **446** |

## Result (counts from tool output and the updated CATALOG.json)

| outcome | count |
|---|---|
| decoded to PNG | **433** |
| still blocked, proven reason | **13** |
| failed | **0** |

- 426 / 426 `blocked_no_tpl` `.tex` files decoded. `blocked_no_tpl` no
  longer exists in CATALOG.json (426 -> 0).
- 7 / 12 `not_converted` files decoded (2 TPL, 2 TGA, 1 TM2, 2 PSD).
- WMXIX converted textures in CATALOG.json: **1,044 -> 1,477**.
- All 1,477 PNGs verified on disk: exist, non-zero, PIL-openable.
- Unified runtime catalog (`customization/build_suite_catalog.py`,
  the PR #404 path): total unchanged at 4,523 parts; WMXIX
  `texture_part` entries with an asset **1,044 -> 1,477**;
  parts-converted `geometry_pending` 1,646 -> 1,213.
- Runtime's own enumeration (`packages/creation-suite/src/catalogs.js`
  `mergeCatalogs` + `entriesForSource`): 1,477 WMXIX entries carry a
  texture asset.
- Tests, run by filename: `node --test
  packages/creation-suite/test/catalogs.test.js` 5/5 pass;
  `node --test packages/creation-suite/test/dna.test.js` 4/4 pass.

## Why the 426 blocked — evidence per class

`.tex` is a little-endian container: u32 entry count, then 32-byte
directory records {name[16], type "tpl", u32 size, u32 offset, pad},
payloads at the recorded offsets. Every entry of every blocked file
(426 files, surveyed exhaustively, zero directory parse failures)
carries a TPL whose magic is `01 20 AF 30` instead of the standard
`00 20 AF 30` — a variant header byte the PR #398 byte-scan could not
match. The original `blocked_no_tpl` reason ("name-table-only
container", e.g. TEX/64gara) was wrong: 64gara files contain full C8
textures. All blocked entries are format 9 (C8, 256-entry palette;
palette formats IA8 192+ files, RGB5A3, RGB565 all occur). Everything
after the magic byte is standard TPL layout, so the validated decoder
handles them once the variant magic is accepted. Per the PR #398 rule,
the container's first directory entry was decoded (one PNG per .tex).

Many of these are MAKE_UP / face-option overlays whose pixel data is a
single palette index (e.g. TEX/Face td0_001.tex uses 2 indices, 16,380
of 16,384 pixels one transparent IA8 entry) — faithfully decoded
near-blank "none" options, not failures. A 16-image contact sheet of
new decodes was viewed: cat graphic, paw prints, beard, kanji,
sunglasses, tattoo lettering, flame logos, jeans, lace — real textures.

## The 12 not_converted — per-file verdicts

Decoded (7), all in `textures/Woman/Face/tq0_417/`:

- `tq0_417_TPL/c3_c_00.tpl`, `c3_c_00l.tpl` — standalone standard TPLs;
  the first pass only scanned `*.tex`.
- `c3_c_00.tga` (64x32), `c3_c_00l.tga` (32x16) — truecolor TGA via PIL.
- `c3_c_00.tm2` — PS2 TIM2, 64x32 indexed-8, RGBA32 CLUT in CSM1 order.
  Verified against the sibling TGA of the same texture: mean RGB
  (146, 91, 72) vs (147, 91, 73), mean saturation 74.0 vs 74.2.
  Output kept as `c3_c_00.tm2.png` so it never clobbers the TGA's PNG.
- `c3_c_00..._wo.psd` (256x128) — PSD RLE composite; PIL rejects this
  file, so a PackBits composite reader decoded it (ch 3 = uniform 255
  alpha; a 5th spot channel ignored). `c3_c_00..._wo1.psd` (128x64)
  decoded via PIL.

Still blocked (5), reasons now recorded in each entry's `detail`:

- `script.txt` — 3D MAX build path list. Not image data.
- 3x `hair/woman/Hair/mk0_*/c0.ymm` — YOBJ mesh data (magic "YOBJ"),
  the unsolved YOBJ mesh family, not textures.
- `tq0_417.tpg` — texture-page index: 91% zero bytes, embedded strings
  list sibling paths (c3_c_00l.tga, c3_c_00.tm2). No pixel data.

## The 8 palette_only — verdict

`colors/COL/{000,001}_{0..3}.ycg` stay `palette_only`, reason refined
in `detail`: YCG color/gradient data records — no image header, no
dimensions, sizes 228-2,356 B in a repeating 4-file pattern. Palette
data consumed with a mesh, not a standalone texture.

## Known limitation (flagged, pre-existing)

`convert_caw_parts.py build_catalog()` regenerates leftover entries
(.tpl/.tga/.tm2/.psd/.ymm/.txt/.tpg) with a hardcoded `not_converted`
status, so a full rebuild with that tool would revert those 7 entries'
catalog status (their PNGs and convert-log records persist). The 426
.tex entries survive a rebuild via the log. Extending that tool's
leftover handling was out of this job's scope.

## Proof

- Contact sheets viewed by the converting agent (16 batch samples +
  10 forensic samples) — real texture content, listed above.
- `customization/parts-converted/convert-log.jsonl`: 448 appended
  records tagged `decode_wmxix_tex_remainder.py` (433 converted —
  script.txt and tq0_417.tpg were re-logged once when their detail
  text was written in the sample pass and again in the full pass).
- CATALOG.json and parts-catalog.json diffs are status/asset-line
  only; no entries added or removed (3,372 and 4,523 totals unchanged).
