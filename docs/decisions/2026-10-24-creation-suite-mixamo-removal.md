# Creation Suite: Mixamo removal, real templates, clean UI, universal rigs

Date: 2026-10-24. Owner complaints: 2026-10-24 19:42 CDT (screenshots),
19:44 CDT (sub-menus, MPFB/GNM, morphing/swapping), 19:45 CDT (fake blank
base, fighter-select taps dead), 19:54 CDT (universal compatibility).

## Owner instruction (verbatim intent)

- "fully take him out of the game" (Mixamo Soldier as default AND as the
  fake "blank CAW base").
- "hook up the WWE 2K templates or the no mercy templates or the
  Wrestlemania 19 templates or any of the Tekken creation suite stuff"
  — real data, not labels.
- Menus "in sub menus and categories like how WWE and Tekken creation
  suites do it", preview always visible, no overlap, phone-friendly.
- "when I try and select and edit any of the other fighters it literally
  won't tap them" — fighter select must open that fighter's editor.
- "modify and morph the body and the template and swap the templates and
  swap the faces and swap the bodies and the parts and stuff just like
  how WWE does it".
- "make sure all of this stuff works on all the bodies, faces, all the
  characters, all the rigs... every model and every rig and all their
  bones all their parts everything".

## What was wrong (verified in code, not guessed)

1. `customization/creation-suite-ui/js/suite.js`: `BLANK_GLB` and
   `blankFighter().baseGlb` were `customization/create-fighter/assets/
   Soldier.glb`, and `loadBaseModel()` special-cased it. NEW FIGHTER
   literally loaded the Mixamo Soldier. `game/js/assets.js` MODEL_URLS
   `custom:` pointed at the same file, so in-game custom fighters did too.
2. `customization/templates/body-templates.json` (9 MB-Lab bodies) and
   `face-presets.json` (12 presets) existed but were NEVER loaded by the
   suite boot (only parts-catalog, jiggle-schema, roster-attires,
   fighter-parts). The templates README claimed "no code changes to add a
   template... suite's template-select screen picks it up" — false: no
   template-select screen existed and the JSON was never fetched.
3. BODY tab rendered all six sections flat in one scroll (the screenshot's
   "ugly flat menu"). BODY_TYPE buttons only set a label (never passed to
   the viewer). PROPS sliders only called `viewer.setProportions`, a
   near-uniform scale stub — muscle/shoulder/chest/waist/hips/arms/legs
   visibly did nothing. `viewer.setSkinTone` was an empty stub.
4. Fighter-select modal appended the attire grid BELOW the fighter grid
   inside a 50vh scroll box, with click-only handlers — tapping a fighter
   looked like nothing happened (below the fold + scroll-drag cancelling
   the click, the same class as the PR #1018 menu bug).
5. Top bar: single-row flex, ~490px of actions + 200px title block on a
   390px phone — necessarily overlapping. Modal: centered, no max-height
   on the container — covered the preview. Footer: two hints + button
   wider than the phone — overlapping.
6. OUTFIT per-part toggles only worked for the SmutBase 6 (fighter-parts
   inventory); every other model got a dead-end note.
7. `packages/creation-suite/src/body.js` `boneByName` only knew T7 names
   (+ mixamorig: + case-insensitive). Bone sliders and morph regions
   silently did nothing on Cape / MB-Lab / Rigify / Tripo rigs.
8. Equip paths wrote `attire().equipped[slot]` directly — no WWE layering
   conflicts, no T7 zone conflicts.

## Method actually used

- Blank base: Technician mesh (`customization/templates/meshes/
  technician.glb`, body-templates.json "Balanced all-rounder. The blank
  canvas most fighters start from.", No Mercy Medium 1). Suite default +
  `MODEL_URLS.custom` + saved-state migration (Soldier.glb -> technician
  on boot) + `Soldier.glb` file DELETED from the repo. Old create-fighter
  tool has no Soldier reference (verified), so deletion breaks nothing.
- Templates: boot loads body-templates.json + face-presets.json. BODY tab
  is now a drill-down (Templates / Body Type / Skin Tone / Proportions /
  Morphs -> Frame/Mass/Face Shape / Face). Template tap swaps mesh +
  proportions + skin + head. Body-type tap applies proportions via
  `packages/creation-suite/src/template-map.js` (dedicated template, or
  legacy `game/js/custom-fighter.js` h/w + family muscle, or whole family
  proportions for F types — basis shown in the toast, never disguised).
  PROPS route through the DNA engine as deltas (prop-1, clamped to
  dna.js ranges; height/weight stay in setProportions so nothing applies
  twice); morphs add on top (mergeDNA). Skin tone tints skin/body-named
  materials (viewer setSkinTone implemented).
- Fighter select: drill-down (fighters -> attires + BACK + scroll-to-top)
  with the PR #1018 tap() helper (touchend+click, 12px drag guard, 600ms
  dedup) on roster cards, attire cards, rail, topbar, body controls,
  outfit rows, swap rows, part-grid cards, pager, modal actions.
- Layout: top-bar actions scroll horizontally (rail geometry unchanged);
  footer src-note hides on phones (content lives in the TOOLS tab);
  modal is a bottom sheet (<=55dvh) on phones and a right-docked panel on
  desktop; scrim lightened on phones. Preview stays visible in all cases.
- Swapping: OUTFIT toggles work on EVERY loaded model via its own mesh
  names (meshStates, saved per attire like partStates). Face presets
  (wwe + gnm layers) record into the attire for the bake pipeline; live
  face shaping is MORPHS -> FACE SHAPE. Equip applies WWE layering
  conflicts (layering.js SLOT_CONFLICTS, fullbody->full_body normalized)
  + T7 zone conflicts (slot 10 vs 9/11, per MENU_SRC T7_CONFLICTS text).
- Universal rigs: new `packages/creation-suite/src/rig-adapter.js`
  (canonical bones + alias tables for T7/Alisa, Cape, Mixamo, Rigify,
  MB-Lab/MPFB; underscore discipline so Cape spine_1 != T7 Spine1;
  missing bones reported, never guessed). Viewer sockets + body.js
  boneByName resolve through it. TOOLS rail tab shows the tool-to-menu
  map (MPFB/MB-Lab, Build-A-Bod, GameRig/NaughTyRig, Fluid Painter, GNM,
  Tripo, gltfpack) with real paths + honest statuses, plus the current
  model's rig coverage.
- Tests: `test/creation-suite-rig-adapter.test.mjs`, 16 checks, Node,
  no deps. Real fixtures: 160 Alisa bone names + 54 Cape bones from the
  Alisa->Cape bonemap; convention examples for Mixamo/Rigify/MPFB.

## Deviations

None from the owner's instructions. Honest scope boundaries (not
deviations — the owner asked for real wiring, not fake wiring):

- Face preset TEXTURES do not swap live in the preview: the No Mercy face
  files (`Face_<hex>.png`, 146 files) have no verified preset-number ->
  filename mapping in any repo file, and the parts catalog does not carry
  face textures as assignable parts. Presets record for the bake; live
  face change is the FACE SHAPE morphs. Inventing a filename mapping
  would be a guess.
- MPFB finger bones are unconfirmed (template GLB joint lists were not
  readable from this VM — 9MB files exceed the contents-API cap). The
  resolver reports them missing for MB-Lab-style rigs; core bones resolve.
  Follow-up: read joint names off a template GLB and extend the table.
- `tools/mb-lab/run_mblab_job.py` (cited by the templates README) does
  NOT exist in the repo (dir holds only .gitignore). Templates + morphs
  work in-suite; re-baking needs MPFB2 per the templates README.
- gltfpack pipeline script is workspace-side (studio-workflow PR payload,
  not yet landed) — the TOOLS tab says so instead of claiming it shipped.
- GNM bakes need gated HuggingFace weights (google/gnm-3) + optional
  TensorFlow — pipeline-side by nature, not in-browser.

## Proof

- `node test/creation-suite-rig-adapter.test.mjs`: 16/16 checks pass
  (T7 Alisa 31/31 bones, Cape 31/31, Mixamo 31/31, Rigify 31/31, MPFB core
  + fingers honestly missing, Object3D tree, adaptScale clamps, template
  mapping incl. family fallbacks, props->DNA deltas + clamps, mergeDNA).
- `node --check` / `--input-type=module --check` pass on suite.js,
  viewer3d.js, body.js, rig-adapter.js, template-map.js.
- Grep: zero functional `Soldier` references remain in the edited files
  (only migration/removal comments).
- NOT yet proven (requires live browser — subagent cannot operate it):
  open the suite on Netlify phone portrait and confirm the default is not
  the Mixamo soldier, template swap changes the character, body-type tap
  visibly morphs, fighter-select taps open that fighter, preview stays
  visible with menus open, top bar + hints clean. These are delegated to
  the parent as browser tasks. Do NOT claim them verified until played.

## Files

- `customization/creation-suite-ui/js/suite.js` (templates, drill-downs,
  tap, morph routing, layering, mesh states, record extensions, boot)
- `customization/creation-suite-ui/js/viewer3d.js` (rig adapter sockets,
  setSkinTone, listBaseMeshes, rigProfile)
- `customization/creation-suite-ui/js/index.html` (TOOLS rail button)
- `customization/creation-suite-ui/css/suite.css` (topbar scroll, footer,
  modal sheet)
- `packages/creation-suite/src/rig-adapter.js` (new), `template-map.js`
  (new), `body.js` (boneByName adapter fallback)
- `game/js/assets.js` (custom -> technician), `game/js/custom-fighter.js`
  (comment)
- `test/creation-suite-rig-adapter.test.mjs` (new, 16 checks)
- DELETED: `customization/create-fighter/assets/Soldier.glb`
