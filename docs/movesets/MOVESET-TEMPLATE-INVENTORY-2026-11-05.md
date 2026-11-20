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
| `cam-moveset-string-lib` | WWE 2K19 Create-A-Moveset string library (5,581 names) | WWE 2K19 | `customization/wwe2k-caw/moveset-library-2k19.txt` (+ GRE pacs) | _(library only — attach per CAW character later)_ | data present; no superstar roster names |
| `cam-powerhouse-brawler` | 2K powerhouse / big-man grappler archetype | WWE 2K19/20/22 | GRE `teardown/wwe2k*`; Steam apps 817130 / 1015500 / 1255630 | _(none yet)_ | reserved for WH powerhouse CAWs |
| `cam-highflyer` | 2K high-flyer / cruiser archetype | WWE 2K19/20/22 | GRE + `customization/templates/meshes/highflyer.glb` body hint | _(none yet)_ | reserved |
| `cam-technician` | 2K technical wrestler archetype | WWE 2K19/20/22 | GRE + `customization/templates/meshes/technician.glb` | _(none yet)_ | reserved |
| `doa-speed-striker` | DOA speed striker family already mirrored in WH movesets | DOA | `game/assets/movesets/doa-*.json` | map per WH character when identity-gated | pointers only |
| `fe-importer-demo-ban` | _(not a playable template)_ | FightingEngine Tag Battle demos | YT Lko4SWLXVEU | **FORBIDDEN** on roster | Hwoarang / Jin / Yugo / Siegfried never attach |

## Pantera detail

- WH character: `pantera`
- Template: `t7-grappler-jaguar-mask`
- Requirement: **100% exact King T7** — no swapped / mixed / T3-as-T7 clips.
- Remaining gaps: `docs/movesets/PANTERA-KING-T7-AUDIT-2026-11-05.md`
- 2026-11-05 MoneyManBusch pass: **A1/C1/RC4 closed**; **55 r17-core8 slots still named-open** (no notation↔clipmap proof without GRE). Template attachment unchanged (`t7-grappler-jaguar-mask` → `pantera`).

## How to add a template

1. Prove the bank / clipmap / moveset rows in GRE or WH.
2. Choose a generic hinting id (no franchise roster name).
3. Add a row here + in `game/data/moveset-templates/index.json`.
4. Attach only to WH character ids.
5. Never commit raw Steam dumps into public WH paths.

## 2026-11-05 update (t383u)

- `t3-ogre-bank` status → **attached-existing** (Chatur already bound to `game/assets/anim/t3/ogre/` via `FIGHTER_BANK.chatur`).

## 2026-11-08 update — moveset template library + creation system (lane 2e9d1e8d)

Builder: `tools/moveset-library/build-templates.mjs` (idempotent; `--check` for CI).
Index: `game/data/moveset-templates/index.json` — **141 templates** (10 hand-written 2026-11-05 rows kept verbatim + 131 generated from measured data).

| Group | Templates | Moves (measured) | Status |
|---|---|---|---|
| T3 per-character banks | 20 | 4,648 | template — full bank each |
| DOA per-character banks | 6 | 146 | template |
| VF per-character banks | 3 | 48 | template |
| VF5 per-character banks | 4 | 96 | template |
| Wrestling (No Mercy) pool | 1 | 4,409 | pool — no per-wrestler grouping yet |
| WMXIX pool | 1 | 169 | pool — per-clip identity pending |
| T7 frame data | 44 | 6,909 | frame-data-only — no anim_ref, not a playable bank |
| T8 frame tables | 41 | 6,411 | frame-data-only — no anim_ref, not a playable bank |
| Pending ingest (UR, Redux, SCII, Def Jam, SF EX, T6, TTT2, 2K19, 2K20/2K22, Devil Within, Brutal Fist) | 11 | UNMEASURED | pending-ingest — no per-character row invented |

Library totals (verified 2026-11-08): **9,516 moves** in `game/data/moveset-library/banks/`; T7 44 files / 6,909 rows; T8 41 chars / 6,411 notation-keyed rows.

Editor engine: `game/js/moveset-editor.js` — WWE Create-A-Moveset category spine
(Bases / Ready / Ground / Turnbuckle / Rope Opponent / Aerial / Running / Double Team / Special),
slot = `position|situation|input` (positions = library schema enum; inputs = clean subset of the
120 canonical T7 inputs measured across the 6,909 T7 rows), per-slot swap with position+input
eligibility, SF6-style slot-conflict rule, source-law enforcement at edit time, `toManifest()`
projection into the existing assembler. Wired into Create Fighter (`game/js/custom-fighter.js`):
a saved fighter with `moveset_custom` fights on it (`moveset: custom:<template>`), otherwise the
named jin fallback stands. Tests: `test/moveset-editor.test.mjs` — 8/8 green 2026-11-08.

**Honest limits (measured, not hidden):**
- T3 base kits assemble to overlay moves ONLY: 0/4,648 T3 rows carry a decoded input, so the
  assembler's base-kit loop adds nothing from a T3 base. A T3-based custom moveset is playable
  only for its explicitly-assigned slots until the #615 fidelity decode lands inputs.
  DOA/VF/VF5 bases assemble FULLY (146/146, 48/48, 96/96 inputs decoded) — proven in-test
  (vf5-el-blaze base assembles 20+ moves, source law green).
- Claimed T3 banks (King, Jin, Eddy, Xiaoyu, Yoshimitsu, etc.) are refused as custom bases
  except by their claimant / an approved exception — the editor enforces the same law the
  assembler does; those templates are viewable, not freely copyable.
- The in-game editor SCREEN is not built: the creation-suite UI is NON-COMPLIANT pending a
  teardown-sourced rebuild (ui_sources gate), so this lane ships the engine + data + tests.
  The screen, movesets.js integration for custom manifests, and a live fight proof are owed next.
- Brutal Fist: identification still in progress (separate agent); this index carries only a
  `brutal-fist-pending` placeholder row, no roster, no counts.
- DOA / Virtua Fighter moveset-editor status: NOT verified in this pass (web search failed on
  a local disk-quota error) — do not claim "no editor" for either until checked.
- Moveset-editor survey (verified 2026-11-08, sources in
  `~/workspace/western-heart-audit/MOVESET-TEMPLATE-LIBRARY.md`): WWE Create-A-Moveset YES
  (the model); MK11 Kustom Variations + MK Armageddon Kreate-a-Fighter YES; Tekken NO editor
  (move lists + practice mode only); Soulcalibur VI whole-style pick, NOT a per-move editor;
  SF6 World Tour slot loadout, NOT a full editor.
