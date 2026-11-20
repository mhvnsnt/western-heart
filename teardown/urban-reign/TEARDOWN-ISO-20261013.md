# URBAN REIGN — ISO Teardown (2026-10-13)

**Game:** Urban Reign (Namco, PS2, 2005) — SLUS-21209
**ISO:** `Urban Reign (USA).iso` — 4,140,924,928 bytes, MD5 `7de3002510bdf1397d3fbc5b94158377`
**Source:** Internet Archive `urban-reign-usa_202608`
**Filesystem:** UDF 1.5 / ISO9660
**Status:** Downloaded + verified 2026-10-13. File structure mapped. Stage packages identified.

---

## ISO Layout (ISO9660 root — 15 files, 1 dir)

| File | Size | Purpose |
|------|------|---------|
| `DVD001.AFS` | 1,258,674,176 | CRIWARE AFS archive #2 — movies, audio |
| `DVD000.AFS` | 1,077,082,112 | CRIWARE AFS archive #1 — game data (missions, stages, models) |
| `SLUS_212.09` | 6,366,044 | Main executable (MIPS ELF) |
| `IRX/` | ~500KB | PS2 IOP modules (PADMAN, LIBSD, CRI_ADXI, etc.) |
| `SYSTEM.CNF` | 57 | Boot config |
| `FCACHE.DVD` | 24 | Disc cache |

**All game content lives inside the two AFS archives** (2.34GB combined).
Parsed in-place with `afs_list_iso.py` (no extraction needed).

---

## DVD000.AFS — Game Data (2,431 files)

### Stage packages (THE TARGET)
`afs/safe/ppk/stage*.ppk` — 7 stage packages:

| File | Size | Likely stage |
|------|------|--------------|
| `stage003.ppk` | 5,406,080 | — |
| `stage004.ppk` | 4,492,928 | — |
| `stage020.ppk` | 3,571,328 | — |
| `stage028.ppk` | 3,470,464 | — |
| `stage029.ppk` | 6,991,232 | — |
| `stage030.ppk` | 4,794,624 | — |
| `stage031.ppk` | 5,175,168 | — |

**PPK format** (from `stage028.ppk` header probe):
- Magic: `ppk\0` (4 bytes)
- @4: total size field (~file size)
- @8: `0x200` (512) — data offset
- Namco-proprietary package; inner structure TBD (multi-day RE task)

### Mission packages
`afs/safe/ppk/mission*.ppk` — ~100 files, ~10MB each (the 100-mission Story Mode).
Each mission PPK likely bundles its stage instance + enemy placements + script.

### Stage lighting
`data/light/stage/bg*.lit` — per-stage lighting data (bg01, bg02, bg03, bg11, bg13, bg39, bg40, bg60).

### Test stages
`data/kageTest/vgs/mc_stage*.vgs` — developer test stage files (mc_stage00–06 + random).

### Other notable dirs
- `tec/motion/` — character motion data (normal, weapon, 30frame, demo)
- `tec/demo/` — demo/cutscene data (anim_obj, effect, facial)
- `data/mission/` — mission metadata
- `data/mc/` — memory card data (japan/usa)
- `motion/` — additional motion test data

---

## DVD001.AFS — Movies + Audio (1,173 files)

- `data/movie/*.sfd` — CRI Sofdec videos: opening, ending, 9 demos, 30+ monitoring_camera clips
- `sound/ok_adx/adx/` — ADX audio files

---

## Chimera Build Value

1. **7 stage packages** are the direct source for Western Heart brawl arenas — back alleys, bars, rooftops, Chinatown, junkyards per the design docs.
2. **100 mission PPKs** contain stage instances + AI placements — template for the Brawl Mode mission structure.
3. **Stage lighting** (`.lit`) gives the intended mood per arena.
4. **Motion data** (`tec/motion/`) — the brawling animation set; complements the Tekken 7 model library.
5. **Tekken guests** (Paul/Law) — their models are somewhere in DVD000; worth extracting for comparison with T7 versions.

---

## What's Next (RE tasks)

1. **PPK format RE** — parse the `ppk\0` container, extract stage geometry/textures. Multi-day task.
2. **Stage-to-arena pipeline** — once PPK is cracked, convert the 7 stages to a usable format (OBJ/glTF).
3. **Paul/Law model hunt** — find the guest character data in DVD000.
4. **Mission structure** — parse a mission PPK for the AI placement + objective format.

---

## Files in this directory

- `Urban Reign (USA).iso` — the full game (4.14GB) — DO NOT DELETE (NO-DELETE-BEFORE-SAFE-STORAGE LAW)
- `iso-file-listing.txt` — ISO9660 root listing
- `dvd000-contents.txt` — full DVD000.AFS file list (2,431 files)
- `dvd001-contents.txt` — full DVD001.AFS file list (1,173 files)
- `analyze_iso.py` — ISO9660 walker (pycdlib)
- `afs_list.py`, `afs_list_iso.py` — AFS parsers (in-place, no extraction)
- `TEARDOWN.md` — this file

## Tools pulled in
- **pycdlib 1.22.0** (pip) — ISO9660/UDF reading
- **AFS format** parsed with custom Python (documented CRIWARE format)
