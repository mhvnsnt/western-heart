# STREET FIGHTER EX2 PLUS — Teardown for Western Heart

**Role in Chimera Build:** 3D Street Fighter reference (owner 2026-10-13) — Arika's 3D
fighter lineage (EX series = the original 3D Street Fighter games, PS1 era). Roster,
move-set structure, and stage design reference for the chimera build's 3D-fighter
lane alongside Tekken/Virtua Fighter teardowns.
**Developer:** Arika / Capcom
**Platform:** PlayStation 1 (PSX)
**Disc ID:** SLUS_011.05 (US release) | **Volume:** STREET_FIGHTER_EX2_PLUS
**Source:** Internet Archive `street-fighter-ex-2-plus.-7z` (197.9 MB 7z)
**Pulled:** 2026-10-14 via watchdog resume (sf3d-pull checkpoint, attempt 3)
**Last updated:** 2026-10-14

---

## Acquisition & Verification

- `Street Fighter EX2 Plus.7z` — 207,533,625 bytes, **byte-exact vs archive.org metadata**.
- Extraction: 7-Zip 24.09 (`7zz`) — 95 entries extracted; 9 sub-item errors, all
  trivial Mednafen emulator artifacts (`sav/*.mcr`, `sf2.jpg`, `stderr.txt`,
  `stdout.txt`). **Zero game-data files affected.**
  (Note: py7zr 1.1.4 fails on this archive with bogus CRC errors — its threaded
  extractor misattributes failures; always use real 7z for these rips.)
- Disc image: `Street Fighter EX2 Plus.bin` — 98,524,629 bytes, raw 2352-byte
  sectors, Mode 2. Valid ISO9660 at sector 16 (PVD), `SYSTEM.CNF` + `PS-X EXE`
  magic present, 403 files/dirs parsed programmatically.
- **Safe storage:** GitHub Release `sf-ex2-plus-v1`
  (https://github.com/mhvnsnt/western-heart/releases/tag/sf-ex2-plus-v1) —
  single 98.5 MB `.bin`. TeraBox upload pending (browser lane).
- Local working copy: `~/workspace/game-reverse-engineering/street-fighter-3d-games/extracted/ex2-plus/`
  (Mednafen bundle + ROM). Full ISO9660 listing: `iso-file-listing.txt`.

---

## Disc Layout (403 entries)

| Dir | Contents | Count |
|---|---|---|
| `/` | `SYSTEM.CNF`, `SLUS_011.05` (743,424-byte US executable), `SILENT3.DA` (31.7 MB) | 3 |
| `/PL/` `/PL2/` | Player data packs | — |
| `/PLNMD/` | Player models — **NMD** (PS1 native model format) | 2 |
| `/PLTEX/` | Player textures | — |
| `/PLSND/` `/PLWSND/` | Player sound / weapon sound | — |
| `/STG2/` | Stage packs `S00D.PAC`–`S07D.PAC` (+ `ENDD.PAC`) — **8 stages** | 9 |
| `/STTEX/` | Stage textures | — |
| `/OVL/` `/OVL2/` `/OVL3/` | Overlays — `PL00_1.OVL`–`PL0D_1.OVL` etc. (per-character code/data) | 87 |
| `/MOG16/` | Core game data: `*.D`/`*.PD` data blobs, `*.TIM` textures, `*.PAL` palettes, `ST_DATA.D` | — |
| `/ADVER/` | Attract-mode packs (`TITLE.PAC`, `ARIKA.PAC`, `CAPDEMO.PAC`, `ADVER.PAC`) | 5 |
| `/ENDP/` | Character ending packs `END00P`–`END1EP` (~20) + `ENDMOJI*.TIM` text art | ~25 |
| `/SEL2/` | Character-select screen assets | — |
| `/STR/` | `M00.XA`–`M04.XA` — 5 XA streams (music/FMV audio) | 5 |
| `/SND3/` | Sound driver/data | — |
| `/TIM/` | Shared textures (31 TIM files) | 31 |
| `/REP/` | Replay data (27 files) | 27 |

**Extensions:** 157× `.PAC` (Arika pack container — priority RE target), 87× `.OVL`,
31× `.TIM` (PS1 texture), 25× `.DP`, 24× `.PD`, 5× `.XA`, 2× `.NMD`.

---

## Format Notes (for the model-extraction lane)

1. **`.PAC`** — Arika's pack container (157 files: stages, endings, attract, player
   data). Header format unknown — needs a PAC unpacker (first RE task).
2. **`.NMD`** (`/PLNMD/`) — PS1 native model format (TMD variant). Standard PS1
   toolchain (psxprev / Noesis / Blender PSX plugins) should read these once
   extracted from PACs.
3. **`.TIM`** — standard PS1 texture (4/8/16/24-bit CLUT). Trivially convertible.
4. **`.OVL`** — per-character overlays; likely code + embedded data.
5. **`.XA`** — CD-XA ADPCM audio; playable via ffplay/vgmstream.
6. **`SLUS_011.05`** — 743 KB MIPS executable; strings/disassembly can reveal
   file-table and format details if PAC/NMD parsing stalls.

---

## What's Next

- [ ] Write PAC unpacker (header RE on `S00D.PAC` / `TITLE.PAC` — smallest first)
- [ ] Extract NMD models from `/PLNMD/` → convert to GLB for roster reference
- [ ] Convert TIM textures → PNG (player + stage sets)
- [ ] Stage geometry: unpack `STG2/S*.PAC`, identify mesh chunks
- [ ] Move-set data: locate per-character data in `/PL/` + OVLs (frame data for chimera)
- [ ] Sibling pull: EX Plus Alpha (re-downloading clean 2026-10-14 — prior partial
      was a truncated+resumed Frankenstein, discarded), then EX3 (669 MB PS2),
      SFIV PC (4.18 GB), SFxT PS3 (12.99 GB), USFIV PS3 (16.61 GB)

## Federation

- Chimera build: `CHIMERA-BUILD.md` — 3D-fighter lane (Tekken foundation,
  Virtua Fighter/DOA/Soulcalibur federated; EX series = Capcom/Arika 3D lineage).
- Sibling checkpoint: `sfv-pull-teardown.json` (SFV blocked on piracy route —
  these EX pulls are the approved alternative).
