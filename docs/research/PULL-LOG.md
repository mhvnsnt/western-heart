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

## 2026-10-16 — KayKit Adventurers weapons (CC0)
- **Pack:** KayKit Adventurers Character Pack free tier (https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0)
- **Kept:** 27 GLB — swords x3, axes x2, dagger, crossbows x2, staff, wand,
  shields x9, quiver/arrow/arrow_bundle, spellbooks x2, smokebomb, mugs x2
- **License:** CC0 1.0 Universal (pack LICENSE.txt copied as LICENSE-CC0.txt)
- **Provenance:** official KayKit GitHub account; upstream .gltf+.bin+.png packed
  to single-file GLB and validated (magic, JSON, meshes, PNG magic)
- **Landed:** `game/assets/accessories/kaykit-adventurers/`
- **Research note:** `docs/research/accessory-packs-kaykit.md`
