# Creation-suite local-assets landing — 2026-11-01

Owner order (2026-11-01, verbatim): "Get any of this stuff that's not any of this stuff that's not in the repo get it to the repo so Claude can get a hold of it and use it like the WWE files or whatever else it needs"

Every creation-suite folder on the machine (~/workspace: csuite-lane/, csuite-ui/, creation-suite-flagship/, creation-suite-wiring/, creationsuite-work/, _csui-layout-work/, _csui-work/, _csui-v2-work/, _stance-batch-20261031/, _zui-stances-work/, wwe2k-teardown/, teardowns/, tekken-customization-extraction/, _mini-retemplate-work/, defjam-work/) was inventoried file-by-file and compared by git blob hash against western-heart main and checked against game-reverse-engineering (GRE). Result, in three buckets:

## (a) Already in western-heart — nothing landed, do not duplicate

- The nine WWE-style base bodies: `customization/templates/meshes/{athletic-w,highflyer,luchador,powerhouse-w,powerhouse,showman,striker-w,super-heavyweight,technician}.glb` (8,684,824–9,087,008 B each) + `customization/templates/body-templates.json`. No local copies exist anymore; they only live on main.
- The create-fighter prototype with the WWE-style template flow: `customization/create-fighter/` (28 files, incl. `assets/Soldier.glb`, `js/creation-flow.js`).
- The game-menu creation suite: `customization/creation-suite-ui/` and `packages/creation-suite/` (src + ui + ui2 + proofs + surveys all match local copies by hash).
- WWE 2K CAW docs: local `wwe2k-teardown/` files are byte-identical to `customization/wwe2k-caw/{CAW-STRUCTURE-2026-10-19,COMBINED-CREATION-SUITE,MOVESET-LIBRARY-2026-10-19,TRANSFER-PLAN-2026-10-19}.md` and `moveset-library-2k19.txt`.
- Stance banks: local `_stance-batch-20261031/` (INDEX.json, STANCE-STATUS.json, 12 banks, 3 clip-maps) is byte-identical to `game/assets/anim/t7/` on main.
- Hair CC0 set, Soldier.glb, slot catalogs (tekken6/ttt2), facemorphs, layering, morphdata, PARTS-REGISTRY (repo copy is newer/larger), csuite demo videos, flagship pipeline demo video — all already on main.
- The 2026-11-01 stance-reachability audit tool + report (`tools/input-verify/stance_reachability_audit.mjs`, `docs/movesets/STANCE-REACHABILITY-AUDIT-2026-11-01.md`) are Claude's own landing from `claude/amazing-keller-p8644u` — not duplicated here.

## (b) Already in game-reverse-engineering (GRE) — not duplicated into western-heart

- `teardown/wwe2k19/` — 1,677 files: extracted Yuke .yobj character meshes, 597 textures, 6 YOBJ models, CAW part tables (YOBJ-to-glTF conversion still pending). Raw game files stay in GRE per standing rule.
- Tekken 7 customization extraction incl. 200 customization-mesh GLBs and the `SW_UI_CharacterCustomize` UI textures under `teardown/tekken7-steam/`.

## (c) Newly landed by this lane (local-only, in neither repo)

PR #1473 (merge f0303da2):
- `teardown/FIGHT_CLUB_TEARDOWN.md`
- `teardown/SA_TURF_WAR_TEARDOWN.md`
- `teardown/SLEEPING_DOGS_TEARDOWN.md`
- `teardown/WARRIORS_TEARDOWN.md`
- `teardown/YAKUZA_TEARDOWN.md`
- `teardown/TEKKEN-CUSTOMIZATION-EXTRACTION-REPORT.md`
- `docs/creation-suite/GNM-HEAD.md`
- `docs/creation-suite/PARAMETRIC-BODY.md`
- `docs/creation-suite/T8-LAYOUT-RESEARCH-2026-10-22.md`

PR #1474 (merge 8f522301):
- `tools/build_zui_stances.py`
- `tools/guard_zui.py`
- `customization/tools/cj_face_presets.py`
- `customization/tools/gen_registry.py` (imports the local ghpush push helper, deliberately not landed — credential-adjacent operational script)
- `customization/tools/cj_parametric_face.py`
- `customization/body-morphs/mpfb_target.json`
- `customization/tools/customize_render.py`
- `customization/tools/mask_test.py`
- `customization/tools/passA.py`
- `customization/tools/passB.py`
- `customization/tools/catalog-append.js`
- `customization/tools/maskonly.py`
- `docs/creation-suite-ui-v2-survey/tekken-frontend-inventory.json`
- `docs/creation-suite-ui-v2-survey/wwe-defjam-frontend-inventory.json`
- `customization/create-fighter/reference/ref-catalog.js`
- `customization/create-fighter/reference/ref-preview3d.js`
- `customization/create-fighter/reference/ref-create-fighter.css`

## Deliberately skipped (local snapshots the repo has already superseded)

Older local versions whose repo counterparts are newer/larger — landing them would add stale duplicates: csuite-lane app.js/catalog.js/preview3d.js/morphs.js/index.html and PARTS-REGISTRY snapshots; csuite-ui build/ suite files and work/CHARACTER-CREATION.md, SYSTEMS-WIRING.md, TEKKEN7-SLOT-CATALOG.json, EYE-LIBRARY-MANIFEST.json; csuite-lane body-morphs-MANIFEST.json; _csui-work/_csui-v2-work package snapshots (slotmap/suite.js/index.js/morphs/profile.js + registry/tekken7 catalogs); _stance-batch fighter.js/t3anims.js snapshots; creationsuite-work dl_* download copies of repo files. Ephemeral render intermediates also skipped: csuite-lane/video_frames/ (240 frames of a demo video already on main) and csuite-ui/demo/ frame/sheet PNGs (frames of the demo video already on main). Operational push helpers skipped: ghpush.py, ig.py, startw.py, ship*.py, vid_dbg.py/vid_test.py, probe/measure/view34/record-demo scratch scripts — no unique creation-suite content.
