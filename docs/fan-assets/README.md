# Western Heart — fan-assets (reuse-licensed public collection)

Public, reuse-safe material that feeds Western Heart's move-set editor, creation
suite (later), and modeling/motion reference.

**Mission:** `docs/handoffs/MUSE_FAN_ASSETS_HANDOFF.md` (assigned to Muse/Ashes, owner via Grok Bot, 2026-10-14).

## What's here

| File | What |
|---|---|
| `CATALOG.md` / `catalog.json` | Every accepted fan-made model, stage, animation (license, author, poly count, format, SHA-256, box-storage release, WH move-slot mapping) |
| `CREDITS.md` | Paste-ready credit lines for every CC-BY / CC-BY-SA item (CC0 gets courtesy lines too) |
| `REJECTED.md` | URLs skipped with the reason (rip dumps, unclear licenses, non-downloadable) |
| `contact-sheet*.png` + `SUMS` | Visual proof sheets: thumbnails of accepted items with name + license |
| `references/` | Links-only modeling + motion reference (TikTok / YouTube / Facebook creator motion approved) |

## Storage rule

- **Binaries:** private `mhvnsnt/box-storage` release assets only. Record SHA-256 in the catalog.
- **Git:** manifests, catalogs, contact sheets, credits — no large meshes/anims in western-heart git.

## Allowed sources

- Sketchfab: **downloadable** items licensed **CC0 / CC-BY / CC-BY-SA** only
- Mixamo (Adobe) free animations (credit Mixamo; follow their current terms)
- OpenGameArt, Poly Haven, itch.io free packs with explicit reuse licenses
- Open motion-capture datasets with clear licenses

## Hard excludes

- Rips or extractions of official Tekken or other commercial game files, even if tagged CC
- Anything whose description, tags, or mesh topology make it obvious it is a game dump
- "Free download" model sites that redistribute ripped game assets without a creator license
- When in doubt: skip, log to `REJECTED.md`

## Out of scope (other agents' claims)

- Teardown wiring / importers / extraction scripts under `teardown/`
- Creation suite under `docs/creation-suite/` and `customization/`
- Physics sandbox / jiggle / Lab physics files
- Model perfection, weight-paint repair, animation retarget work

This tree is **additive docs + catalogs + private binary storage + contact sheets only.**
