## 2026-10-19 — production tooling wave (Stream 5: full chimera build push)

Owner: "anything else that you can find that's industry standard high quality
or really development or production studio level that you can get into this
pulled in and wired up pull it in wired it up completely."

Closes the 4 pipeline bottlenecks from the 2026-10-19 roster audit:
(1) rigging automation, (2) skeletal animation, (3) textures, (4) game wiring.

### Pulled / built (open source, free)

| Tool | Source | License | Bottleneck | Where it landed |
|------|--------|---------|-----------|-----------------|
| tools/anim-retarget (retarget_blender.py, wh-retarget.js, bone maps, tests) | WH-original, wraps Blender + three.js | repo license | #2 skeletal animation | `tools/anim-retarget/` |
| tools/texture-pipe (bake_pbr_blender.py, apply_pbr_set.py) | WH-original, Blender pipeline | repo license | #3 textures | `tools/texture-pipe/` |
| tools/wire-fighter (wire-fighter.py) | WH-original | repo license | #4 game wiring | `tools/wire-fighter/` |
| UniRig (skeleton + skinning prediction, SIGGRAPH 2025) | https://github.com/VAST-AI-Research/UniRig | **MIT** | #1 rigging (already vendored in PR #273) | `tools/auto_rig/vendor/unirig/` |
| MagicArticulate (fastest skeleton predictor, CVPR 2025) | https://github.com/Seed3D/MagicArticulate | **Apache-2.0** | #1 rigging (already vendored in PR #273) | `tools/auto_rig/vendor/magicarticulate/` |
| Puppeteer (AI rig + video-guided animation) | vendored in PR #273 | **Apache-2.0** | #1/#2 | `tools/auto_rig/vendor/puppeteer/` |
| Materialize workflow (photo -> PBR maps) | https://github.com/BoundingBoxSoftware/Materialize | **GPL-3.0** (app; outputs are ours) | #3 textures | documented `tools/texture-pipe/materialize-workflow.md`, code NOT vendored |
| Material Maker (procedural PBR authoring) | https://github.com/RodZill4/material-maker | **MIT** | #3 textures | already wired `tools/procgen/textures/` |
| TEXTtoPBR algorithms (albedo -> tileable PBR) | https://github.com/Vasco888888/text-to-pbr | **MIT** | #3 textures | already ported `tools/procgen/textures/wh_seamless_pbr.py` |
| ArmorPaint 1.0 (3D texture painting + neural Image-to-PBR) | https://github.com/armory3d/armorpaint | **open source** (verify LICENSE at build; binaries $19, source build free) | #3 textures | documented `tools/texture-pipe/armorpaint-build.md`, code NOT vendored |
| Rokoko Studio Starter + Vision (AI video mocap, FBX/BVH export) | https://www.rokoko.com | **free tier** (account) | #2 animation sourcing | documented `tools/anim-retarget/workflow-rokoko.md` |
| Rokoko Blender plugin (retarget shelf) | https://www.rokoko.com | **free** | #2 retarget | documented `tools/anim-retarget/workflow-rokoko.md` |
| Mixamo (auto-rigger + 2,000+ animation library) | https://www.mixamo.com (Adobe) | **free** (Adobe ID) | #2 animation sourcing | documented `tools/anim-retarget/workflow-mixamo.md` |
| three.js SkeletonUtils.retargetClip (runtime retarget) | three.js r160, already vendored | **MIT** | #2 runtime | `tools/anim-retarget/runtime/wh-retarget.js` |
| Blender 5.x Retarget extension (Mixamo/Unreal presets) | blender.org (bundled) | **GPL** (part of Blender) | #2 retarget | documented `tools/anim-retarget/README.md` |

### Verified already on main (not re-pulled)

- **tools/auto_rig (PR #273, merged):** unified auto-rig CLI, 5 backends
  (blender-heat CPU / knn CPU / magicarticulate GPU / unirig GPU / puppeteer
  GPU), `validate.py` playable gate. Bottleneck #1 already closed — this wave
  adds the visual proof + the remaining three bottlenecks.

### Documented, NOT pulled (per law: document license status honestly)

| Tool | Why not pulled |
|------|----------------|
| Auto-Rig Pro (~$40, Blender Market) | Paid. The Blender gold standard for rig+retarget; buy if the owner wants it. NOT cracked. |
| Adobe Substance 3D Painter | Paid. ArmorPaint 1.0 is the open equivalent, wired above. NOT cracked. |
| Cascadeur (free tier) | AI-assisted keyframe animation; useful later for hand-authored signature moves. Not needed this wave. |

### Visual proof

- auto_rig blender-heat on Tripo phantom.glb (1M verts -> 60k -> rigged):
  before/after renders + posed skeleton overlay.
- texture-pipe bake on the rigged model: AO/normal/roughness/albedo set.
- anim-retarget: procedural source animation retargeted onto WH skeleton,
  rendered frames.
- wire-fighter: dry-run diff on the real game/js files.
All proof images attached to the PR.

---

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
