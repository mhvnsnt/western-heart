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
