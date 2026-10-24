# URBAN REIGN — Teardown for Western Heart

**Role in Chimera Build (owner 2026-10-12):** GAME #6 — street-brawl systems. *"It's kind of a hybrid of the wrestling, the WrestleMania XIX and No Mercy modes. And the Tekken modes."*
**Developer:** Namco (ex-Tekken / Soulcalibur team)
**Platform:** PlayStation 2 (2005)
**Last updated:** 2026-10-13 (full teardown sweep)

---

## What's Extracted and Documented

### ISO — Downloaded, Verified, Safe on GitHub Release (DONE 2026-10-13)
- `Urban Reign (USA).iso` — 4.14 GB, Internet Archive `urban-reign-usa_202608`, verified.
- **Safe storage:** GitHub Release `urban-reign-iso-v1` (https://github.com/mhvnsnt/western-heart/releases/tag/urban-reign-iso-v1) — split into 8×500MB parts (GitHub 2GB/file limit). Reassemble: `cat urban-reign-500m.part_* > "Urban Reign (USA).iso"`.
- **Teardown (PR #23 merged):** AFS structure mapped, **7 stage PPKs identified** (back alleys, bars, rooftops, Chinatown, junkyards + 2 more). See commit `b1cc587`.
- NOTE: 4.14GB exceeds the browser file-grant upload size limit — TeraBox upload of this ISO needs a non-browser path (owner manual).

### Research (done, no ISO needed)
- Documented in `docs/URBAN-REIGN-TEARDOWN.md`:
- **60+ playable fighters**, each with own style (boxing, wrestling, karate, brawling, capoeira, kung fu); ~30 special moves + ~50 double-team attacks per character
- **Tekken guests:** Paul Phoenix and Marshall Law (Tekken 5-era models) — direct chimera-relevant assets
- **100-mission Story Mode** (Brad Hawk, brawler-for-hire, Green Harbor)
- **AI partner system:** double-team combos — launch enemy into the air, partner catches and slams
- **30+ weapons:** bats, pipes, bottles, shovels, 2x4s
- **Destructible environments:** back alleys, bars, rooftops, Chinatown, junkyards — furniture breaks, shelves shed boxes, cars/pinball machines shatter
- **Special arts meter:** builds on damage/dodges/hits → uncounterable super moves
- **Modes:** Story, Free, Challenge (wave survival), plus 4-player free-for-all brawling

---

## What's Blocked and Why

- **Stage geometry decode** — 7 stage PPKs extracted to `ppks/stages/` (2026-10-13) but inner Namco geometry/texture chunks not yet decoded (multi-day binary RE; format notes in `PPK-FORMAT.md`).
- **Character model decode** — all 72 `char*.ppk` extracted to `ppks/chars/` (2026-10-13); PPK inner structure documented, model chunk decode open.
- **Design question open (owner decision needed):** Option A — third **BRAWL MODE** vs Option B — merged into Wrestling Mode. Added to CHIMERA-BUILD.md 2026-10-12.

---

## Extraction Log — 2026-10-13 (no-ISO surgical extraction)

Local ISO was deleted after GitHub verification; disk at 90% blocked a
4GB re-download. Instead: parsed ISO9660 from the release parts
(`urban-reign-iso-v1`), located DVD000.AFS (LBA 1496016), parsed its AFS
header + name table, and pulled **79 files via HTTP Range requests —
77.4MB total, zero ISO download.** Method is reusable for any of the
2,431 DVD000 entries (offsets in `afs-map/dvd000_afs_map.json`).

### Extracted

| Set | Location | Contents |
|-----|----------|----------|
| 7 stage PPKs | `ppks/stages/` | stage003, 004, 020, 028, 029, 030, 031 (34MB) |
| 72 fighter PPKs | `ppks/chars/` | char001–char072 (44MB) — full 60+ roster + alternates |
| Motion pools | `motion/` | `general_normal.gyu` (1.5MB), `general_30frame.gyu` (1.8MB), `general_weapon.gyu` (587KB), `gyuindex.bin` (`pmot001.` move index), `gyuindex_ppk.bin`, `gyu_debug.gyu` |
| AFS map | `afs-map/dvd000_afs_map.json` | all 2,431 DVD000 entries with byte offsets + sizes |
| Tools | `tools/ppk_probe.py` | PPK header/signature probe |

### Format findings (full notes in `PPK-FORMAT.md`)

- PPK: magic `ppk\0`, LE32 total size @4, `0x200` data offset @8.
  Stage PPKs carry a sub-chunk offset table (146 entries in stage028).
  Char PPKs are float-heavy (identity quats); no ASCII fighter names.
- Motion: `gyuindex.bin` maps per-character `pmotNNN` slots into the
  three shared `general.gyu` animation pools.

### Still reachable (surgical, no ISO download)

`mission*.ppk` (~100, ~10MB each — fetch selectively), `data/light/stage/bg*.lit`,
`data/kageTest/vgs/mc_stage*.vgs` test stages, `tec/demo/` cutscene data.

---

## Chimera Build Value

- **The missing link between Tekken Mode and Wrestling Mode** — a Namco brawler built by the Tekken team, with wrestling moves, weapons, and 4-player mayhem
- **Double-team combat:** AI partner launch-and-catch slams → template for chimera tag/team mechanics
- **Weapon + destructible-environment systems:** 30+ weapons and breaking environments are chimera stage-design targets
- **Tekken guests (Paul/Law):** Tekken 5-era models of characters already in the chimera roster → alt-model/reference material
- **Special arts meter:** proven super-move economy to mirror against chimera design

---

## Next Steps

1. Extract the 7 stage PPKs → geometry (PS2 stage format RE)
2. Extract Paul/Law models + motion data; catalog weapon/prop models
3. Owner decision: Option A (BRAWL MODE) vs Option B (merged into Wrestling Mode)
