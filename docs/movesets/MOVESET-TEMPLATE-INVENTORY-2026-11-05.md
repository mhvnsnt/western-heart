# Moveset template inventory — 2026-11-05

WWE-style copy-moveset templates for Western Heart (owner t374u / t375u).
Machine-readable twin: `game/data/moveset-templates/index.json`.

## Rules

- Template **id** = generic hint (never a franchise roster label).
- WH **character id** stays the owner's name (Pantera, Demonio, …).
- Raw Steam / WWE / Tekken dumps live in private `mhvnsnt/game-reverse-engineering`.
  WH stores mappings + pointers only.
- Do not put Hwoarang / Jin / Yugo / Siegfried / WWE superstar names on the roster.
- Steam library reference: `docs/tech/STEAM-LIBRARY.md` (no credentials).

## Template → WH character map

| Template id | Hint | Source game | Teardown / bank pointer | Attached WH characters | Status |
|---|---|---|---|---|---|
| `t7-grappler-jaguar-mask` | T7 jaguar-masked wrestler-grappler (King-style 0x64) | Tekken 7 | GRE `teardown/tekken7/`; WH `game/assets/anim/t7/` King packs; clipmap `docs/proof/t7-clipmap-king-pantera.json`; moveset `game/assets/movesets/pantera.json` | `pantera` | **primary — exact King T7** |
| `t7-mishima-style-karate` | T7 Mishima-style karate (Jin-family motion; WH name Demonio) | Tekken 7 | WH Demonio / jin bank paths; never roster-name "Jin" | `demonio` | attached (existing WH binding; template id formalized here) |
| `t7-heavy-bob-style` | T7 heavyweight bob-and-weave brawler | Tekken 7 | Burger T7 stance / moves path | `burger` | attached (existing); verify clip identity in later audit |
| `t7-flashy-counter-kickbox` | T7 flashy counter kickboxer (Hwoarang-family motion — **template only**, never roster Hwoarang) | Tekken 7 | GRE / WH bank when claimed | _(none yet)_ | template reserved — **do not** create a Hwoarang roster entry |
| `t3-ogre-bank` | T3 Ogre-family bank already in WH | Tekken 3 | `game/assets/anim/t3/ogre/` | `chatur` (existing bank use) | pointer only; T3 ≠ T7 King rule still holds for Pantera |
| `wwe2k-moveset-string-lib` | WWE 2K19 Create-A-Moveset string library (5,581 names) | WWE 2K19 | `customization/wwe2k-caw/moveset-library-2k19.txt` (+ GRE pacs) | _(library only — attach per CAW character later)_ | data present; no superstar roster names |
| `wwe2k-powerhouse-brawler` | 2K powerhouse / big-man grappler archetype | WWE 2K19/20/22 | GRE `teardown/wwe2k*`; Steam apps 817130 / 1015500 / 1255630 | _(none yet)_ | reserved for WH powerhouse CAWs |
| `wwe2k-highflyer` | 2K high-flyer / cruiser archetype | WWE 2K19/20/22 | GRE + `customization/templates/meshes/highflyer.glb` body hint | _(none yet)_ | reserved |
| `wwe2k-technician` | 2K technical wrestler archetype | WWE 2K19/20/22 | GRE + `customization/templates/meshes/technician.glb` | _(none yet)_ | reserved |
| `doa-speed-striker` | DOA speed striker family already mirrored in WH movesets | DOA | `game/assets/movesets/doa-*.json` | map per WH character when identity-gated | pointers only |
| `fe-importer-demo-ban` | _(not a playable template)_ | FightingEngine Tag Battle demos | YT Lko4SWLXVEU | **FORBIDDEN** on roster | Hwoarang / Jin / Yugo / Siegfried never attach |

## Pantera detail

- WH character: `pantera`
- Template: `t7-grappler-jaguar-mask`
- Requirement: **100% exact King T7** — no swapped / mixed / T3-as-T7 clips.
- Remaining gaps: `docs/movesets/PANTERA-KING-T7-AUDIT-2026-11-05.md`

## How to add a template

1. Prove the bank / clipmap / moveset rows in GRE or WH.
2. Choose a generic hinting id (no franchise roster name).
3. Add a row here + in `game/data/moveset-templates/index.json`.
4. Attach only to WH character ids.
5. Never commit raw Steam dumps into public WH paths.
