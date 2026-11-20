# Roster model audit (2026-10-23)

Owner laws: t183u (no wrong body anywhere), t187u (Tekken + Western Heart is the base).
Gate: `node test/no-wrong-body.test.mjs` (game-checks CI).

## Fixed
| Item | Before | After |
|---|---|---|
| Wrong bodies (PR #900) | Riders fell back to Steve Fox / Pantera | Own model or MODEL PENDING card |
| Phantom ladder | `steve-fox` offered as "JIN · BLADE SOUL" | Removed (gate blocks shared bodies in any ladder rung) |
| Zui ladder | `steve-fox` offered as "BASE · STEVE FOX" | Removed (own A1/A2 + T7 reskin alts kept) |
| `getFighter()` unknown id | Returned Pantera | Returns a model-pending soul (`modelPendingFighter`) |
| `ui-wh-bridge.js` unknown id | Pantera | Model-pending; fight is not started |
| `menus.js` story portrait | `pantera.png` when no charId | Portrait hidden |
| Demonio moveset | `moveset-library` only read `game/data/movesets/` (no demonio file) | Falls back to `game/assets/movesets/demonio.json` (658 moves) |
| `ui_sources.json` | menus.js unlisted | Listed under `screen-menu` |

## Re-rigs onto Tekken skeletons (private only)
Re-rigged GLBs use Tekken skeletons, so they live only in private
`mhvnsnt/game-reverse-engineering` at `rigs/<id>/attire1/model-t7.glb` and load
only when `globalThis.__WH_PRIVATE_ASSETS` is set (`PRIVATE_T7_RIGS` in `game/js/assets.js`).

| Fighter | Source | State |
|---|---|---|
| burger | `rma/tk/burger-dec.glb` -> Bob T7 (232 bones), proxy weights -> full mesh (1,297,527 verts, 1,911,939 tris, nothing cut) | Bind pose OK; **in-fight pose collapses** (T7->T3 remap/bind-frame issue). Backup: private branch `backup/roster-rig-burger`. Not wired live. |
| diablo, samura1, waterfall, charger, koreshi, thor, rave/kiko, cyborgx/cape-jones, ryusan, tobi, slice, dorowani | — | Queued (blocked on disk: Blender needs >= 10 GB free) |
| cainelias | — | Needs first rig, queued |
