# WWE 2K Parts — Pull Plan

Owner CONFIRMED 2026-10-18 ~09:26 CDT: pull WWE 2K19 or 2K18 for the
creation-suite research — target the customization/creation-suite data
specifically. Standing CAW exception: the WWE 2K creation system goes into
WESTERN HEART.

## Status (2026-10-18)

- WWE 2K14: PARTS-CATALOG.md said "downloading (extraction pending)" — **no game
  files found on disk** (only `game-reverse-engineering/wrestling-games/WWE2K14-DLC-CATALOG.md`).
- WWE 2K19: was "via TeraBox pipeline" — **not verified on TeraBox** (listing
  needs a browser lane; subagents cannot operate the live browser).
- **No `pac/edit/` files anywhere on disk.** The extraction lane is blocked on
  the game files landing.

## Exact targets (from PARTS-CATALOG.md)

| Category | Location | Contents |
|----------|----------|----------|
| Body templates | `pac/edit/bbtemplate.pac` | Male/female base bodies, morph targets |
| Default parts | `pac/edit/default.pac` | Starter heads, bodies, attire |
| Edit parts | `pac/edit/edit.pac` | Full customization part library |
| Sample parts | `pac/edit/sample.pac` | Preset samples |
| Head parts | `pac/edit/ch/` | Masks, face accessories, normals |
| Body parts | `pac/edit/body/` | Torso, limb meshes |
| CAW metadata | `pac/profile/profile_dat.pac` | Hometown, CAW IDs, slot data |

Reference models: slots 256 (Male default CAW) / 257 (Female default CAW) —
used in cutscenes, the base bodies to build on.

## Extraction toolchain

1. Get game files (2K19 preferred; 2K14 as fallback): ~51GB. Pull straight to
   TeraBox per the PULL-STRAIGHT-TO-STORE law — do NOT stage 51GB on local
   disk (disk at 84%).
2. Extract `pac/edit/` with 2K modding tools (real tooling, no hand-guesses):
   the `.pac` format is Yuke's archive — use the community pac extractor used
   for 2K14/2K19 modding.
3. Wire parts into `customization/parts/wwe2k/` with MANIFEST entries in the
   canonical format (see `CUSTOMIZATION-LIBRARY-LAYOUT.md`).
4. Slots 256/257 bodies → `customization/parts/templates/` as FULL CHARACTER
   TEMPLATES.

## Blockers

- Disk: 84% — the 51GB game files must go straight to a store, not local disk.
- TeraBox verification needs a browser lane (parent/main chat delegation).
- 2K14 download status unknown — check whether it completed anywhere before
  starting a fresh pull.

---

## Detailed pull batches (cust-wwe2k-inventory lane, 2026-10-18)

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
