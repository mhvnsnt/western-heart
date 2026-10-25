# Creation Suite gaps follow-up — PR #1057 (2026-10-24)

Follow-up to `docs/decisions/2026-10-24-creation-suite-mixamo-removal.md`.
Branch: `feature/creation-suite-mixamo-removal-20261024` (head `a6747a03` at
push time; re-checked before every push). This doc records what each
remaining gap now is: wired, or its exact blocker + active unblock path.
Nothing here is claimed as live-played — the live playtest steps are
listed at the end and are still owed via a browser delegation.

## (a) Face preset textures LIVE SWAP — WIRED

- Map: `packages/creation-suite/src/face-texture-map.js` — preset number
  to PNG file, generated from the live repo listing of
  `customization/parts/no-mercy/faces/` and verified EXACT (146/146,
  no diffs): 98 male (`Face_Male_01`..`Face_Male_98`, no gaps),
  20 female (`Face_Female_01`..`Face_Female_20`, no gaps), 28 extras
  with no preset number (unnumbered `Face_1Exx` + named duplicates).
  A `wwe`-layer preset resolves by `{ gender, no_mercy_face }`;
  `gnm`-layer presets resolve to `null` (expression bake only).
- Wiring: `customization/creation-suite-ui/js/suite.js` FACE panel tap
  handler calls the new `SuiteViewer.swapFaceTexture()` in
  `customization/creation-suite-ui/js/viewer3d.js`. Target chain, first
  hit wins: materials named face/head, then skin/body, then the first
  material with a map, then the first material. All 9 template GLBs
  carry an `MBLab_skin…` material, so the skin bucket hits on every
  template mesh. When no material matches, the toast says the preset
  was recorded for bake and that no live swap happened — never a
  silent no-op presented as a swap.
- UI rule: the suite shows the preset's neutral name (Classic Hero,
  Rugged, …). Filenames in the map are repo asset paths used to load
  the texture, never displayed as character names.
- Test: `test/creation-suite-face-textures.test.mjs` — 17/17 pass
  locally (counts, numbering, uniqueness, all 8 `wwe` presets resolve,
  all 4 `gnm` presets null, bad input null).

## (b) MPFB fingers — CLOSED on real files

- Read, not re-derived: the 71 skin joints of
  `customization/templates/meshes/technician.glb` (9,087,004 bytes,
  same 71-joint skeleton on all 9 templates, verified per template):
  MB-Lab names — `lowerarm_L` (not `forearm_L`), `calf_L` (not
  `shin_L`), `toes_L` (plural), `thumb01_L`/`index01_L`/`middle01_L`/
  `ring01_L`/`pinky01_L` (+00/02/03 segments).
- Measured before/after with the real resolver: before, the old alias
  table missed 16/32 canonical bones on this rig (10 fingers +
  2 forearms + 2 shins + 2 toes — the old table kept underscores, so
  `thumb01l` never matched `thumb01_l`, and `index1_l` never matched
  `index01_l`). After appending the MB-Lab aliases to
  `packages/creation-suite/src/rig-adapter.js` (append-only, no
  existing resolution changed): 32/32, missing `[]`, fingers map to
  the `01` segments, forearm to `lowerarm_L`, shin to `calf_L`, toe
  to `toes_L`.
- Test: `test/creation-suite-rig-adapter.test.mjs` gains the real
  71-joint check — 17/17 pass locally (16 original + 1 new). The old
  convention-guess MPFB fixture check is kept unchanged.
- Note: the GPU queue's MPFB finger-gap job output was not found in
  the workspace, so this lane did the read directly from the template
  GLBs instead of citing an unseen output.

## (c) MB-Lab script / MPFB2 re-bake — PATH DOCUMENTED, RUN OWED

- Correction to the #1057 decision doc: `tools/mb-lab/run_mblab_job.py`
  EXISTS on main (8,562 bytes, headless Blender 4.0.2 job). The
  "absent" claim is stale; do not repeat it.
- Adopted, not rebuilt: `game/js/creation-tool-map.js` (Lane 8,
  PR #1066) already maps body → MB-Lab / Build-A-Bod / MPFB using the
  existing `tools/mb-lab` + `tools/mpfb2` dirs.
- Migration path (from `tools/mpfb2/README.md`): MB-Lab bases (AGPL
  database) → MPFB2 data path — `customization/body-morphs/apply_mpfb_morphs.py`
  on Blender 4.0.2, baking `MPFB_<id>` shape keys from the MPFB target
  tree. Live MPFB2 plugin path needs Blender ≥ 4.2.
- Verified on this VM: Blender 4.0.2, 4.2.0 and 4.5.3 binaries all
  exist under `~/workspace/tools/blender/` and `--version` runs.
  This corrects Lane 8's "no Blender binary on this VM" report.
- Run owed (blocker, exact): MPFB2/MB-Lab vendor trees are
  fetch-on-demand and are not on this VM, and this sandbox blocks
  file writes by any process that performs network I/O (curl, Python
  and Node-after-network all fail with EPERM on write), so the fetch
  cannot complete from this agent. Active path: the GPU job package
  in `~/workspace/gapfill-20261024/creation-gaps/gpu/` runs
  `tools/mpfb2/fetch-mpfb2.sh` (no `--with-blender` needed — 4.2.0 is
  present), then the 4.0.2 data-path bake on `technician.glb`, then
  `tools/gltfpack/run_gltfpack_job.py`. Baked shape keys remain
  ground truth; the bake output must keep 71 joints and gain the
  `MPFB_<id>` keys, or the job fails.

## (d) gltfpack + PR #1038 — ONE WORKING PATH

- Canonical: `tools/gltfpack/` on main (`fetch-gltfpack.sh` +
  `run_gltfpack_job.py`, `-cc -tc` game defaults). The suite TOOLS
  tab gltfpack entry now points there.
- PR #1038 (`feature/studio-payload-20261024`) vendors the same
  gltfpack binary at `tools/wh-asset-pipeline/tools/gltfpack` for its
  studio pipeline script, which resolves gltfpack next to itself.
  That is the pipeline's pinned copy of the same tool, not a second
  suite pipeline. No duplicate suite path was created by this lane.
  If #1038's lane wants full de-duplication it can repoint its
  script at the canonical dir; that edit belongs to #1038's lane,
  not this one (no cross-lane edits).
- Template-pipeline export order: suite EXPORT writes fighter JSON →
  Blender bake → `tools/gltfpack/run_gltfpack_job.py` → game-ready GLB.

## (e) GNM bakes — EXACT GATE DOCUMENTED, BAKE OWED

- Gate, exactly: (1) accept the `google/gnm-3` license on HuggingFace
  (human/coordinator step — no agent can accept it); (2) place the
  released model weights under `tools/gnm/vendor/GNM/assets/` via
  `tools/gnm/fetch-gnm.sh` (clones `github.com/google/GNM`, Apache-2.0,
  at pin `main`, then pulls released assets; the script warns and
  stops if assets are absent); (3) run
  `python3 tools/gnm/run_gnm_job.py --spec tools/gnm/specs/face-determined.json --out <head.glb>`
  (or the suite job queue). TensorFlow is OPTIONAL — the numpy
  backend bakes heads; TensorFlow is needed only for semantic
  identity sampling. Full TF/JAX/torch dev deps are NOT needed.
- Bake owed for the same two reasons as (c): weights not on this VM
  + the network-write sandbox restriction. The suite TOOLS tab GNM
  entry already states this gate honestly; no suite change was
  needed for (e).

## CI — root causes found, one fix pushed, one owner action owed

- `game-unit-tests` FAILED with `ERR_MODULE_NOT_FOUND` for
  `packages/creation-suite/src/rig-adapter.js`: the job's sparse
  checkout lists `test/` but not `packages/creation-suite/`, so
  #1057's test could never import its module in CI (it passes
  locally, 16/16 before this lane, 17/17 after). Fix pushed here:
  `packages/creation-suite` added to the `game-unit-tests`
  sparse-checkout list in `.github/workflows/game-checks.yml`
  (the `menu-touch-e2e` job already includes that path).
- `guard` (no-deletion-guard) FAILED because #1057 deletes
  `customization/create-fighter/assets/Soldier.glb` without the
  `approved-deletion` label. The deletion is owner-directed (verbatim
  quote in the #1057 PR body: "fully take him out of the game"), but
  the label represents owner approval, so this lane does NOT add it
  itself. OWNER/COORDINATOR ACTION: add label `approved-deletion` to
  PR #1057, then re-check CI. Until then the PR must stay open and
  unmerged — never merge before green.
- `material-gate` / `menu-touch-e2e` were still running at last
  check; re-check after the push + label.

## Conflict watch — ZERO same-file overlaps with #1057

Checked file lists 2026-10-24: #1052 (13 files, all
`docs/research/steam-pulls-wrestling.md` + `game/assets/pulls/**`),
#1038 (14 files, `tools/wh-asset-pipeline/**` + docs + audio engine),
#1042 (`game/index.html`, `game/js/audio.js`, `game/js/main.js`,
`game/ui_sources.json`), #1046 (audio/jukebox files +
`game/index.html`/`audio.js`/`main.js`/`lazy.js`/`load-progress.js`/
`menus.js`/`voice.js`). None touches a #1057 file
(`customization/creation-suite-ui/**`,
`packages/creation-suite/src/{rig-adapter,template-map,body}.js`,
`game/js/{assets,custom-fighter}.js`,
`test/creation-suite-rig-adapter.test.mjs`). #1042 vs #1046 share
`game/index.html`/`audio.js`/`main.js` with each other — that is
their mutual conflict, not #1057's. No 3-way merge was needed here.

## Live playtest — OWED (browser delegation, not claimed)

Phone portrait, like the owner plays, on the deployed #1057 build
after merge + deploy:
1. Open the creation suite. Confirm NO Mixamo soldier anywhere
   (default fighter, fallbacks, template list).
2. FACE: tap each No Mercy preset — the preview texture must visibly
   change (live swap). Tap a GNM preset — it records for bake (no
   live texture change is correct there).
3. BODY: pick a template (e.g. Technician → Powerhouse) — the body
   must visibly morph; pick a body type — proportions must change.
4. FIGHTER SELECT: tap several fighters — each tap must open THAT
   fighter's editor (not the blank base, not nothing).
5. Preview must stay visible while menus open (nested sub-menus,
   no menu covering the preview).
6. End-to-end: build a full custom character from the blank base
   (template + face + body + parts), save it, and re-open it intact.
