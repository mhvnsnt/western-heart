# WWE 2K Pull Plan — CAW Parts (2K14 / 2K19)

**Lane:** cust-wwe2k-inventory — 2026-10-18
**Owner confirmation:** WWE 2K19/2K18 pull CONFIRMED 2026-10-18 ~09:26 CDT.
Target: `pac/edit/` creation-suite data — slot 256 Male default CAW, `bbtemplate.pac`,
`edit.pac`, `default.pac` (per `customization/wwe2k-caw/PARTS-CATALOG.md`).

## 1. Status as of 2026-10-18

| Item | Status |
|------|--------|
| WWE 2K14 full game (ISO/disc) | **NOT on disk.** `PARTS-CATALOG.md` said "downloading (extraction pending)" — a full disk search on 2026-10-18 found NO ISO, NO partial download, NO staging dir. Only 2K14 artifacts anywhere: the 2K14 DLC zip already on GitHub (see below) and a DLC catalog doc. If a 2K14 download was started by another lane, its location is unknown — check with the parent lane before assuming it exists. |
| WWE 2K19 full game (CSF 50.96GB) | **Not verified on TeraBox.** TeraBox has no read API from this environment (browser-lane only), and subagents cannot run browser tasks. The parent/browser lane must confirm `/WesternHeart/teardowns/wwe2k/` contents. |
| WWE 2K18 (45.11GB) | Same as 2K19 — needs TeraBox folder listing. |
| Already secured (no re-pull) | `wwe2k19-entrance-pack.tar.gz` (175,112,192 B) + `wwe2k19-moves-pack.tar.gz` (123,317,410 B) — GitHub release `wwe2k19-animation-packs-v1` on `mhvnsnt/wrestling-game`. `WWE.2K14.DLCS.zip` (44,660,178 B, 12 PS3 DLC unlock PKGs + RAPs) — release `wwe2k14-dlcs-v1` on `mhvnsnt/wrestling-game`. |

## 2. Pull plan (do NOT start on the VM — disk is 84%)

**Destination:** TeraBox folder `/WesternHeart/teardowns/wwe2k/` (create if missing).
Upload in ≤25 MB parts; verify name + byte size in the folder listing before clearing
staging. Never route through the VM (each game is 33–84 GB; extraction needs 2–3×).

**Batch A — already on GitHub, pull straight to TeraBox (no VM disk used):**

| File | Size (bytes) | Source URL |
|------|-------------|------------|
| `wwe2k19-entrance-pack.tar.gz` | 175,112,192 | https://github.com/mhvnsnt/wrestling-game/releases/download/wwe2k19-animation-packs-v1/wwe2k19-entrance-pack.tar.gz |
| `wwe2k19-moves-pack.tar.gz` | 123,317,410 | https://github.com/mhvnsnt/wrestling-game/releases/download/wwe2k19-animation-packs-v1/wwe2k19-moves-pack.tar.gz |
| `WWE.2K14.DLCS.zip` | 44,660,178 | https://github.com/mhvnsnt/wrestling-game/releases/download/wwe2k14-dlcs-v1/WWE.2K14.DLCS.zip |

**Batch B — full games, Archive.org → TeraBox (priority order, browser lane):**

| Pri | Game | Size | Archive.org identifier | File on Archive.org |
|-----|------|------|------------------------|---------------------|
| 1 | WWE 2K19 (Clean Steam Files) | 50.96 GB | `WWE_2K19_CSF` | `WWE 2K19 [Build 3467910].7z` |
| 2 | WWE 2K18 | 45.11 GB | `wwe-2k18` | `WWE 2K18/WWE 2K18.7z` |
| 3 | WWE 2K15 (Clean Steam Files) | 33.13 GB | `WWE_2K15_CSF` | `WWE_2K15_CSF.7z` |
| 4 | WWE 2K23 | 84.48 GB | `wwe-2k23` | `WWE 2K23/WWE 2K23.7z` |

Download URLs:
- 2K19 CSF: `https://archive.org/download/WWE_2K19_CSF/WWE%202K19%20%5BBuild%203467910%5D.7z`
- 2K18: `https://archive.org/download/wwe-2k18/WWE%202K18/WWE%202K18.7z`
- 2K15 CSF: `https://archive.org/download/WWE_2K15_CSF/WWE_2K15_CSF.7z`
- 2K23: `https://archive.org/download/wwe-2k23/WWE%202K23/WWE%202K23.7z`

(Identifiers + URLs verified live on Archive.org 2026-10-14; source:
`game-reverse-engineering/wrestling-games/WWE2K15-23-ACQUISITION.md`.)

**2K14 full game:** true PS3/360 2K14 was NOT found on Archive.org as of 2026-10-14
(the two `wwe-2-k-14*` items there are mislabeled SvR2011 PSP / a PSP mod — do NOT pull).
2K14 remains "still hunting" — the confirmed path is 2K18/2K19 for now.

## 3. Extraction toolchain (runs AFTER the 7z lands on TeraBox, NOT on this VM)

Requirements: a machine with 200 GB+ free (not this VM — 84% full).

1. `7z x` the game archive.
2. Yukes PAC unpack — all `.pac` are Yukes PAC containers (same family as WMXIX; the
   `wrestling-game` lane's existing PAC tooling applies). 2K community modding tools for
   per-version quirks — real tooling, no guessing.
3. Targets: `pac/edit/bbtemplate.pac`, `pac/edit/default.pac`, `pac/edit/edit.pac`,
   `pac/edit/sample.pac`, `pac/edit/ch/`, `pac/edit/body/`,
   `pac/profile/profile_dat.pac` (per PARTS-CATALOG.md: slots 256/257 = default
   Male/Female CAW reference models).
4. Decode meshes + textures → wire into `customization/parts/wwe2k/<slot>/` in the
   canonical layout (`CUSTOMIZATION-LIBRARY-LAYOUT.md`), one `MANIFEST.json` per part
   folder, then update `parts/PARTS-INDEX.json` and the count table in PARTS-CATALOG.md.

**Estimated result:** the full 2K19/2K18 CAW part library (100+ hairstyles, layered
attire per body region, masks, face paint, tattoos) — feeding
`customization/parts/hair/`, `parts/attire/`, `parts/accessories/`, `parts/decals/`,
`parts/tattoos/`.
