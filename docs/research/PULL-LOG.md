# Accessory/UI Pull Log

Running log of every third-party asset pulled into `game/assets/accessories/`
(or UI kits) by the accessory pull-in lane. Newest first.

## 2026-10-16 — Kenney.nl weapon packs (CC0)
- **Packs:** Blaster Kit, Survival Kit, Mini Arena (https://kenney.nl/assets)
- **Kept:** 34 GLB — 18 blasters + 2 grenades (kenney-blaster-kit), 10 hand tools
  axe/hammer/hoe/pickaxe/shovel +upgraded (kenney-survival-kit), sword + spear +
  trophy + banner (kenney-mini-arena)
- **License:** CC0 1.0 Universal (LICENSE-CC0.txt per pack; upstream `License.txt`
  ships in every Kenney zip)
- **Provenance:** content-hashed kenney.nl zip URLs located via makepad MIRROR.toml
  manifest; SHA-256 verified on download; GLB magic + JSON chunk validated
- **Landed:** `game/assets/accessories/kenney-{blaster-kit,survival-kit,mini-arena}/`
- **Skipped:** Pirate/Castle/Retro-Fantasy kits (no equippable accessories —
  Pirate Kit has NO hats, ships/cannons only)
- **Research note:** `docs/research/accessory-packs-kenney.md`
