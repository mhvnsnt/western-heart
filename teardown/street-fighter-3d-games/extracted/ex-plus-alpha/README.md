# extracted/ex-plus-alpha — SF EX Plus Alpha disc extraction (2026-10-20)

Re-extracted after the 2026-10-14 extraction was deleted by disk-space-guardian.
Source: Archive.org `street-fighter-ex-plus-alpha.-7z` (size-verified
263,912,228 bytes = metadata; py7zr header-validated) → `.bin` 528,049,872 bytes
(raw 2352-byte Mode-2 sectors) → jPSXdec v2.0 (Temurin JRE 17) disc index
(612 items) → full file-tree extraction.

## Contents

| Dir | Files | Size | Notes |
|-----|-------|------|-------|
| `PL/` | P00.PAC … P19.PAC (26) | 7.7 MB | Character model packs (44-entry LE offset table + chunks: TMD parts, TIM textures, animation data). Index in `PAC-CHUNK-INDEX.json` |
| `STG/` | S00T.PAC … S13T.PAC (20) | 2.5 MB | Stage texture packs. **20 packs, not 8** (corrects PR-1 doc) |
| `STG2/` | S00D.PAC … S13D.PAC (20) | 1.7 MB | Stage geometry packs (20 packs) |
| `TMD/` | GAMEN.LMD, HAPA.LMD, VEGADAMA.LMD, FDEMO.PAC | 104 KB | Loose stage/effect models |

## What is decoded so far

- `PAC-CHUNK-INDEX.json` — per-PAC 44-entry chunk index (offsets, sizes, magic
  words, TIM/TMD type hints). Generator: `teardown/street-fighter-3d-games/tools/pac_index.py`.
- **Finding (2026-10-20):** the 44-entry table is NOT a clean sequential chunk list —
  46/1144 entries have out-of-range offsets and some tables jump backwards.
  TIM magic (0x10) hits at 134 chunks are NOT standalone TIMs (version field
  reads 0x54, not 0x00) — chunks carry PAC-level sub-headers. Full PAC container
  decode is a dedicated RE pass (logged on `~/workspace/agent-ops/TEARDOWN-IDLE-QUEUE.md`).
- **Finding (2026-10-20):** STG/STG2 hold 20 packs each (S00–S13 hex), not 8.
- P-slot → character mapping still pending select-screen (SEL2/) cross-check
  (name-table order from SLUS_005.48 is recorded in `../character-roster.md`).

## NOT committed (on local disk `~/workspace/_sf-scratch/`)

- The 528 MB `.bin` and 7z sources (re-downloadable; NOT Git-stored).
- Loose `TIM/`, `TEX/`, `SEL2/`, `SND/`, `MUS/` (XA music), `MOV/` (FMV STR) — disk copies
  only; store-to-TeraBox is a separate lane (browser lane).
- jPSXdec install: `~/workspace/_sf-scratch/sf-tools/` (Temurin JRE 17 + jPSXdec v2.0).
