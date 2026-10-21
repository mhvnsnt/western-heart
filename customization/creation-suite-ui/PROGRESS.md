# Creation Suite Pass — Worker C, Recovery Run #4

Branch: feat/cs-ui-wiring-20261020 · Worktree: ~/workspace/_wh-work/cs-ui
Law: commit + push after EVERY item. No local-only work.
Run #4 note: the cs-ui worktree vanished from disk mid-run (external cleanup);
recreated from the pushed branch @1534a7746 via western-heart-main worktree add
+ sparse checkout customization/packages/game/roster. No work lost (push-early).

## Checklist
- [x] Setup: fetched + fast-forward merged origin/main (f8b3b5d67); sparse checkout customization/packages/game/roster
- [x] 1. ROSTER MODE: build_roster_attires.py + data/roster-attires.json GENERATED (run3, coordinator-rescued); suite.js roster-mode UI WIRED (run4): FIGHTER SELECT modal lists real roster fighters -> attire picker; selecting loads that attire's real GLB (viewer.loadBase, parts/markers cleared on swap); topbar attire tabs switch attires in roster mode; blank-fighter mode intact (mode/rosterRef/records on F, legacy wh_creation_suite_v1 top-level shape unchanged)
- [x] 2. REAL SLIDERS (run4): BODY tab gains packages morphs.js catalog — BODY_MORPHS split Frame (height/shoulders/limbs/neck/hands/feet) + Mass (bulk/muscle/fat/belly/chest/waist/hips) and FACE_SHAPE_MORPHS as Face group; thin MORPH2DNA adapter maps morph ids onto dna.js SLIDERS, body.js applySliders drives live preview on the loaded roster model (+ morphs.js applyMorphProxies); values stored in F.morphs and stashed into the per-attire record. Skin tone + No Mercy body-type presets unchanged. importmap maps wh-creation-suite/ -> ../../packages/creation-suite/src/ (bare 'three' already mapped).
- [ ] 3. UNIFIED PARTS CATALOG: build_suite_catalog.py merges PARTS-REGISTRY (1148 entries verified) + parts-converted/CATALOG.json + hair GLBs + eye-library; T7-slot browse, source labels, tap-to-assign only
- [ ] 4. PER-ATTIRE SAVE: records keyed fighter+attire in wh_creation_suite_v1 (legacy blank key intact); fetch in-repo customization.json on select; Save to Attire = persist + download + copyable panel
- [ ] 5. PROOF HARNESS: Playwright shots (Baek -> Master White, 2 morphs + hair part) in proof-pass/, own-eyes viewed
- [ ] 6. PR to main; merge only if checks PASS + CLEAN, zero deletions, node --check all touched JS

## Verified facts / blockers
- customization/parts-converted/CATALOG.json is ABSENT on origin/main f8b3b5d67 and in Worker A worktree (checked 2026-10-20). Builder handles it as an optional source (count 0) and notes it; will re-run if it lands.
- PARTS-REGISTRY.json actually holds 1148 parts (wmxix 1050 geometryPending, no-mercy 35, rest texture/mesh libraries). The old UI catalog had only the 34 curated entries (all present in registry).
- Disk: /home at 96% at start. No new staging folders; work only in this worktree.
