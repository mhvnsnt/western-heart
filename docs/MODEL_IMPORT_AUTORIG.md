# Model import + auto-rig (spec and prototype)

Goal: drop a GLB in, get a Western Heart fighter: rigged to the canonical skeleton, segmented like Tekken, P1 animations mapped, rig gates passed, registered on the select screen. Tool: `tools/import_model.py`. Bigger product spec (Create a Fighter, Drive, agents): `docs/CREATE_A_FIGHTER_SPEC.md`.

## What the prototype does today (honest status)
| Step | Status |
|---|---|
| 1. Fetch (local path, or Drive link/id via `gdown` if public) | DONE. Private Drive: agent uses the DownloadFile tool, then passes the local path |
| 2. Versioned copy `roster/<id>/imports/<attire>_vN.glb`, SHA-256 checked, never overwrites | DONE |
| 3. Auto-rig | PARTIAL. Already-skinned models are **mapped** by bone name onto `lab/skeleton/canonical_skeleton.json` (Mixamo, `mixamorig:`, `Bip01`, `DEF-` prefixes, Spine1/Spine2 aliases). **Unskinned meshes are refused** with the fix: Tripo/Mixamo auto-rig of the T-pose model. No in-house skin-weight solver yet |
| 4. Segment | DONE. Dominant skin weight per vertex -> head, torso, arm/hand L/R, leg/foot L/R vertex counts (Tekken-style parts) |
| 5. Retarget P1 | MAP ONLY. Writes source->canonical bone map and lists the P1 clips in `lab/game/assets/pantera_leoman.glb`. Live playback of P1 clips on the imported rig is NOT validated yet (needs rest-pose correction because the canonical skeleton uses identity rests) |
| 6. Rig gates | DONE: rigged, required bones, height 1.3-2.4 m, arms >= 40 deg from spine (T/A-pose), symmetric hands, segments cover body, retarget map complete |
| 7. Register | DONE: `game/ui-wh/imports.json` entry (glb, sha, portraits). Add the id to `ART` in `game/ui-wh/roster.js` to show it on select |
| 8. Card render (`--render`) | DONE: `lab/game/tools/render_card.gd` |

## Proof (one real import)
```
python3 tools/import_model.py game/assets/models/demonio.glb --character zui --attire base --render
```
Output (2026-10-14): all 7 gates PASS, height 1.71 m, arm 89.8 deg from spine (T-pose), segments head 3837 / torso 2806 / hands 1146+1146 / arms 148+148 / legs 969+943 / feet 0 (shoes are weighted to the shins: known). Report: `docs/qa/import/import_report_zui_base_v1.json`. Frame: `docs/qa/import/import_render_full.png`. Source SHA-256 9b5ff2a1086b837c0bf652ac245d74767fbc23516ed211039cfbe7a727941349 (untouched).

## Next work (in order)
1. Rest-pose correction + Godot gate that plays every P1 clip on the import and checks no bone flips (frames to docs/qa/import/).
2. Feet segment fix (re-assign shoe vertices below ankle height to foot).
3. Write a segmented GLB (one mesh per segment) for hit-zones and part swaps.
4. Read `imports.json` in roster.js so registration needs no hand edit.

## Physics sandbox hookup (coordination only; that repo belongs to the physics agent)
The physics playground's jiggle lab (`lab-jiggle.js` in physics-playground-pwa) auto-detects secondary chains **by bone name regex**. So the import must output secondary bones named so they match, and keep them OUT of the canonical-22 (they are extra children):
| Chain | Name the bones | Matches their regex | Parent |
|---|---|---|---|
| Chest | `breast_L_01`, `breast_L_02`, `breast_R_01`... | `/breast|bust|boob/i` | Chest |
| Butt | `butt_L_01`, `butt_R_01` | `/butt|glute|cheek/i` | Hips |
| Thighs | `thigh_L_jiggle`, `thigh_R_jiggle` | `/thigh/i` | LeftUpLeg/RightUpLeg |
| Hair | `hair_01`..`hair_06`, `ponytail_01`.. | `/hair|ponytail|pigtail|bun/i` | Head |
| Tail | `tail_01`..`tail_06` (Pantera already) | `/tail/i` | Hips |
| Skirt | `skirt_F_01`, `skirt_B_01`, `skirt_L_01`, `skirt_R_01` | `/skirt/i` | Hips |
| Belly | `belly_01` | (creation-suite `applyDNA` belly slider generates its own) | Spine |
Rules: numbered root-to-tip, `_L`/`_R` for character left/right (left = +X), never reuse canonical names, keep chain depth <= their `depth`. Export GLB with these bones skinned; the import gate will list found chains in the report under `secondary`. Don't edit the physics repo: post the naming on the agent-ops board and let its owner wire it.
