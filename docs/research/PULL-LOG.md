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

---

# Tool Pull Log — open-source RE/extraction tools (tekken-mining lane)

Standing log per CONTINUOUS RESEARCH + PULL-IN LAW. Newest first.

## 2026-10-16 — tekken-mining lane

### Pulled
| Tool | Source | License | What it does | Where used |
|------|--------|---------|--------------|------------|
| pycdlib | pip (`pip install pycdlib`) | **LGPL-2.1-or-later** | Pure-Python ISO9660 reader (no system deps) | Tekken 6 PSP: listed all 62 files in `tekken6-psp.iso`, confirming game data lives in raw sectors (DATA401 archive) outside the ISO9660 tree |

### Evaluated, NOT pulled (documented for future lanes)
| Tool | Repo | License (verify before use) | What it does | Why not pulled |
|------|------|----------------------------|--------------|----------------|
| 360tools | https://github.com/sp00nznet/360tools | check repo | `extract_iso.py` (XDVDFS XGD1/XGD2), `extract_stfs.py`, `xex_info.py` | Overlaps existing `god_surgical.py` + zarmanager path |
| XGDTool | https://github.com/wiredopposite/XGDTool | check repo | CLI: Xbox disc convert to/from `--extract`/`--god`/`--xiso`/`--list` | Fallback if Python GOD path fails |
| GODSend-360 | https://github.com/ghostyshell/GODSend-360 | check repo | Pure-Go ISO→GOD conversion + game manager | Wrong direction (we need GOD→files) |
| ulbox360 | https://github.com/vladkioladki/ulbox360 | check repo | Rust: ISO→GOD, XISO pack/unpack, FATX FUSE | Not needed while zarmanager works |
| SimpleXisoDrive | https://github.com/purelogiccode/SimpleXisoDrive | GPL-3.0 | FUSE/Dokan mount of XISO (XDVDFS) | Mount path unnecessary |

### Already in use (prior lanes, noted for license hygiene)
| Tool | Repo | License | Note |
|------|------|---------|------|
| zarmanager | https://github.com/dfdevx2/zarmanager | **UNKNOWN — no LICENSE file in local checkout** | Pure-Python GOD/STFS/XISO reader; underpins `tekken-tag-tournament-2/tools/god_surgical.py`. Do not redistribute until license confirmed. |
| py7zr | pip | LGPL-2.1 | Used by god_surgical.py for 7z access |

## 2026-10-16 — game-hud UI kit (MIT)
- **Kit:** threejsassets/game-hud (https://github.com/threejsassets/game-hud)
- **Kept:** dist/ (core.css, game-hud.css, layout.css, 12 skins), index.html
  (component markup templates), LICENSE-MIT.txt, upstream README.md, WH-README.md
- **License:** MIT (Aron & Sharon / threejsassets.com)
- **Why:** pure HTML/CSS/JS, zero deps, 60+ components; Fantasy skin is already
  dark+gold (#f2b01e/#e89b12 on #211d18) — matches Creation Suite aesthetic
- **Landed:** `tools/creation-suite/ui-kit/game-hud/`
- **Skipped:** dev-only references/, docs/, scripts/
- **Research note:** `docs/research/ui-kits-game-hud.md`
