# Eastern Mind: The Lost Souls of Tong-Nou — Teardown (100%)

**Game:** Eastern Mind: The Lost Souls of Tong-Nou (OutSide Directors Company / Osamu Sato, 1994 Mac, 1995 Windows)
**Source:** `eastern-mind-v1` release (`emtlsotn.zip`, 575,140,238 bytes, byte-verified)
**Engine:** Macromedia Director 4 (MV93 RIFX)
**Extracted:** 2026-10-15 by wh-easternmind-100 lane

## What was extracted

| Asset type | Count | Details |
|---|---|---|
| Bitmaps (PNG, 8-bit, game palette) | 5,321 | All Director BITD cast members, RLE-decoded, palette-applied |
| Sounds (WAV, 8-bit/22kHz mono) | 229 | All Mac 'snd ' resources from DXRs |
| CD audio (WAV, 16-bit/44.1kHz stereo) | 3 | Red Book tracks 2-4: Tong-Nou Theme (4:29), Transmigration Ending Theme (5:16), Tong-Nou Esoteric Mix (8:01) |
| Videos (MP4 H.264) | 22 | All QuickTime .MOVs converted (game animations + transcript promo) |
| Ending theme (WAV) | 1 | ENDING.AIF → WAV |
| Text (raw) | 31 | STXT cast members (cast lists, UI strings) |
| Palettes | 48 unique | 256×RGB, game global + per-character (CHARA/PORT) |

## Format notes

- DXR = Director 4 protected movie (RIFX/MV93). Cast data is NOT encrypted — only Lingo bytecode is protected.
- Bitmap pixel data uses Director's own RLE (NOT PackBits): byte ≥ 0x80 → run of `((b^0xFF)+2)`; else literal `b+1` bytes. (0x80 = run of 129, NOT PackBits NOP.)
- Bitmap dimensions/bpp/palette come from the CASt member info records, matched to BITD chunks by decoded pixel count (w×h).
- Palette: game-global 256-color CLUT (shared across all area DXRs); CHARA.DIR/PORT.DIR have per-bitmap palettes.
- Sounds are Mac 'snd ' format-2 resources: 8-bit unsigned PCM, 22254.54 Hz mono.
- CD tracks 2-4 extracted from CloneCD .img (2352-byte sectors, audio at LBAs 216490/236694/260387).

## WH stage mapping (owner-assigned stage names from stages.md)

| DXR prefix | EM land | WH stage |
|---|---|---|
| F_ | Shi-chieng (Fire/Time) | stage-1-plains-of-chi-u |
| G_ | Yui-wang (Metal/Desire) | stage-2-helix-palace |
| W_ | Man-chien (Water/Dreaming) | stage-3-palace-of-dreaming |
| L_ | Ming-ken (Wood/Life) | stage-4-tree-of-life |
| D_MARKET, D_MERCHA | (liminal) | stage-5-phantom-marketplace |
| E_ | Tong-nou (Earth/Source) | stage-6-octagonal-shrine-par-fang |
| D_* (rest) | prologue/ending | prologue-ending |
| R_* | nine incarnations | incarnation-system |
| TRANSCRI | Sato works/promo | transcript-promo |

## Tools

`extract_dxr.py` — pure-Python Director 4 RIFX parser (mmap/KEY*/CASt/BITD/snd/STXT/CLUT).
Reference implementations: ScummVM `engines/director` (BITDDecoder, BitmapCastMember), ProjectorRays (RIFX structures).

## Gaps

- ~7% of BITD chunks unmatched to dimension info (non-8-bit or unusual records) — pixel data preserved in analysis logs, recoverable.
- Lingo scripts (115 per DXR avg) NOT decompiled — gameplay logic available via ProjectorRays if needed.
- THUM thumbnails not extracted (redundant with full bitmaps).
