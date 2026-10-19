# UI Asset Inventory — Tekken Menu/UI Files in Our Teardowns (Lane I)

Date: 2026-10-18. Inventoried on `origin/main` via `git ls-tree -r`.

## Verdict up front

**We have ZERO real Tekken menu/UI assets** (no select-screen frames, fonts,
backgrounds, button art, or menu sounds) in any teardown directory. The
rebuilt select screen is therefore a clean-room rebuild matching Tekken 8's
layout/behavior per the owner's spec, using our own assets. This is stated
honestly in the PR — no "real Tekken UI files" claims.

## teardown/tekken7 (165 files)

- `king/` — 72 files: King P1 model textures (D/N/S maps), FBX + jpg ref.
- `models/king-variants/` — King model variants (rigmodels, archive-org,
  deviantart, open3dlab, sfmlab, tekken6-psp).
- `arenas/` — 1 rar (mishima-dojo map).
- `tekkenmods-docs/` — TekkenMods documentation site mirror (modding guides,
  UE4 setup screenshots). No game UI art.
- `tools/umodel_linux` — extraction tool.
- Menu/UI assets: **none**.

## teardown/tekken8 (2 files)

- `models/PHANTOM-t8-yoshimitsu-s1.7z`, `models/asuka-kazama-t8_SFM.rar` —
  model archives only.
- Menu/UI assets: **none**.

## teardown/tekken-tag-tournament-2

- Directory exists; no usable UI dump. (Layout lineage for our UI came from
  public footage/research, not from files here.)

## Other teardowns

- Urban Reign `teardown/urban-reign/vgs/decoded/*.png` menus are still
  scrambled (stride/swizzle unsolved) — usable as layout references only, never
  as pixel bases (per `game/ui-wh/README.md`).

## Real assets actually wired into the rebuilt select screen

| Asset | Source | Status |
|---|---|---|
| Fighter GLBs (pantera, steve-fox, jin, demonio, cyborg-x, …) | `game/assets/models/`, `roster/pantera/attires/`, `docs/tpose-refs/` | Ours / owner-pulled — real files, wired |
| Per-fighter card art `card_<fighter>.png` (23) | `docs/qa/roster-cards/` | Our QA renders — real files, wired |
| Oswald variable font | `game/ui-wh/fonts/` | Bundled OFL font — real file, wired |
| Menu wallpaper art | `game/ui-wh/art/wallpaper_wh*.png` (derived from owner's title-bg) | Ours — real files, wired |
| Select-screen frames / buttons / hints chrome | — | **REBUILT** to T8 layout (no real files exist) |
| T8 stat block, hints bar, "?" random, two-cursor flow | — | **REBUILT** from research (§1 of SELECT-DESIGN.md) |
| Select idle animations | GLB embedded clips where present; neutral breathing loop otherwise | Real clips where present; approximation labeled honestly |

## Bottom line

Everything the player sees on the new select screen is either our own real
file or an honest rebuild. The layout lineage (T8 bisected 3D zone + hints bar,
T6 "?" random, TTT2 two-cursor flow, classic punch/kick attire rule) is
documented with citations in SELECT-DESIGN.md §1.
