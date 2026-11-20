# Closet viewer + registry v2 (closet lane, 2026-10-24)

User directive (2026-10-24 21:02 CDT): the closet is a room the user
drives himself on his phone — toggle every slot/item on/off individually,
swap every slot, move the camera (orbit/pan), zoom in on separate parts
to judge swaps up close, change lighting (studio / living-room / night
at minimum), save named versioned recipes that never overwrite earlier
ones. Presets are shortcuts; toggles are the truth.

## What this PR builds (on main 3bda9d0f, #1065)

- `packages/creation-suite/ui2/viewer.js` — BUILT ON, not replaced.
  The Creation Suite v2 live stage (Three.js, editor-side twin of
  `game/js/customization-consumer.js`) gains the closet controls:
  - `toggleSlot(slot, on?)` — every slot on/off individually.
  - `setClosetSlot(slot, meshes)` / `registerClosetSlot(slot, meshes)`
    — swap every slot live (hide the slot's whole mesh universe, show
    only the new item's meshes).
  - `focusPart(slot)` — camera frames THAT part alone (Box3 of the
    slot's current meshes); `showFullBody()` — one tap back, restoring
    the view saved before the first focus.
  - `setLighting(preset)` + exported `LIGHTING_PRESETS` — studio
    (neutral, for judging color), living_room (warm show-room light),
    night (dark, for spooky surf vibe checks). Lighting is a closet
    control, never baked into a render.
  - `swapFaceTexture(url)` — creation-gaps lane's material chain:
    face/head mesh -> MBLab_skin material -> skin/body material ->
    first mapped material -> first material. It takes the resolved PNG
    URL; the preset-number -> PNG table lives in the creation-suite
    lane's `src/face-texture-map.js`, which is on OPEN PR #1057, not
    on main, so the viewer does NOT import it (see Deviations).
  - `saveClosetRecipe(name)` / `loadClosetRecipe(name, version?)` —
    named versioned recipes via the pure module below.
  - Camera: one finger still orbits exactly as before; two-finger drag
    pans, pinch/wheel zooms. Turntable behaviour unchanged.
  - Verified against main's viewer.js by diff: the only removed lines
    are the intentional replacements (anonymous lights -> named
    `this.lights` rig with identical values/positions; single-pointer
    handlers -> pointer-map handlers preserving the orbit math;
    `_tick` look target 0/targetY/0 -> targetX/targetY/targetZ;
    wheel zoom floor 2.4 -> 0.4 so a part zoom can actually get close).
    `suite2.js` uses only preserved methods (applyRecord, applyMorphs,
    setFighter, liveEdit, rebuildPhysics) — no suite changes needed.
- `packages/creation-suite/ui2/closet-recipes.js` (new, pure, no DOM,
  no Three.js) — `createRecipe` / `saveRecipe` / `loadRecipe` /
  `listRecipes` / `validateRecipe`. `saveRecipe` appends version
  MAX+1 for a name and never mutates an earlier version. Executed
  tests: `~/workspace/gapfill-20261024/closet/work/test-closet-recipes.mjs`
  passes (v1 survives a v2 save untouched; latest + exact-version load).
- `packages/creation-suite/ui2/closet-panel.js` (new) — phone-first
  bottom-sheet panel driving a Viewer: region groups, per-slot toggle
  checkbox + item select + Focus button, Full body button, three
  lighting buttons, preset shortcut buttons, recipe name + Save +
  recipe list with Load. Opens on studio lighting. Body slots flagged
  `always_on` render with a disabled toggle.
- `packages/creation-suite/closet-registry.json` (new, format_version 2)
  — ONE engine-agnostic recipe format shared by the show closet and
  Western Heart's creation suite. Contents:
  - `viewer_controls`: camera/lighting/toggles/swap/save/face_texture.
  - `tekken7`: the full T7 slot spine from `src/t7layout.js` +
    `src/slotmap.js` (18 codes, region tabs Head / Upper Body /
    Lower Body / Body / Effects, flow fighter -> attire -> region ->
    slot -> item -> color -> pattern -> equip, color layers
    base/sub/trim, 144-swatch palette) — STRUCTURE ONLY (see the
    PR #871 correction below). WH extensions listed separately
    (eyes, upper_inner/outer, hands, feet, waist, ink).
  - `wwe2k`: layer pools (60 attire / 40 head-body, 40+ templates,
    body morphing, layer kinds) — STRUCTURE ONLY, accessories list
    EMPTY (see Owed).
  - `characters.alisa`: all 13 slots with mesh universes + items +
    presets carried from the show closet registry, each slot mapped to
    its T7 spine id. `characters.cape_jones`: body + cape slots;
    suit colorways kept as a non-mesh field (colorway only until
    separate garment meshes exist — it is not faked as a mesh slot).
  - `recipes`: versioning rule + a two-version same-name example
    (v1 default, v2 no_belt_no_tie) proving v2 does not overwrite v1.
  - `fit_gate`: the ship rule + shipped/owed/unfit lists.
- `game/ui_sources.json`: NOT touched. The ui-sources gate's UI_GLOBS
  (`tools/ui-sources/check.py`) match `game/index.html`, `game/*.css`,
  `game/js/*menu*/*-screen*/*-ui*/ui-*`, `game/ui/**`,
  `packages/creation-suite/src/*ui*`, `packages/creation-suite/*.html`
  — none of this PR's files (`ui2/*.js`, `closet-registry.json`)
  match, and no `<section>` markup changes. If the gate disagrees at
  CI time, the fix is a `screen-closet` manifest entry citing
  `teardown/tekken7-steam-ui/T7-UI-LAYOUT.md`, not a code change.

## PR #871 correction (applied, not repeated)

PR #871 did NOT land a T7 items catalog JSON in the public repo. It
landed Def Jam + WMXIX catalogs, `tools/extract/t7/t7_customize.py`
(the T7 extractor), `t7layout.js`, `slotmap.js`, `rigswap.js`, and the
creation-suite viewer. The 23,548 figure IS stated in `t7layout.js`
itself ("Derived by tools/extract/t7/t7_customize.py from the owner's
Steam copy (customize_item_data.bin, 23,548 item records)"). Raw tables
live ONLY in the private repo (game-reverse-engineering
tekken7/customization/); the public repo keeps structure only. No raw
T7 item rows are shipped in this PR.

## New finding: T7 code 16 is UNMAPPED (not guessed)

The 18 per-slot counts in `t7layout.js` sum to 23,446, not 23,548.
`t7layout.js` lists codes 1-15, 17, 18, 19 and skips code 16. The
remaining 102 records are recorded in the registry as UNMAPPED with
that arithmetic shown — the file does not say what code 16 is, so no
slot name was invented for it.

## Alisa re-render (closet-viewer proof)

The old proof (`ep1-farm/closet/alisa_default.png`, 640x360, one SUN,
black void, camera 3.2m back) was verified by viewing it: the figure
is tiny, dark, and T-posed at a distance — not a proof. The re-render
script (`~/workspace/gapfill-20261024/closet/render_alisa_close.py`,
Blender 4.2.0 from `~/workspace/tools/blender/`) frames from the
model's own bbox, uses a neutral studio world + key/fill suns, and
renders portrait 800x1067: default / skirt / no_belt_no_tie full-body
plus head, waist (belt+tie), and boots part-zooms on default.
Renders land in `~/workspace/gapfill-20261024/closet/renders/` and are
NOT committed to the repo (no game-model renders in the public repo).

First re-render run FAILED and was discarded, for two honest reasons
worth recording: (1) the script matched meshes by substring
(`"_Boot_L" in "Boot_L.dmx"` is false, `"_Alisa"` is not in
`"Alisa.dmx"`), so the body, belt, boots and most slots rendered
hidden — only Eyes/Hair/Shirts showed; (2) every PNG landed 0 bytes
despite Blender reporting "Saved" (the evening write-block flap).
The fix: EXACT base-name matching (name minus `.dmx`) plus a
3-attempt retry that reports final byte size and treats 0 bytes as
NOT a render. The GLB also carries one stray `Icosphere` mesh, which
is never in any preset and stays hidden. Second run: the write flap
zeroed the first four frames again (3 attempts each), then lifted at
~02:47 — waist (1,057,148 bytes) and boots (919,544 bytes) landed
clean. A targeted rerun of only the four missing frames then landed
them all: default full 926,587, skirt full 926,865, no_belt_no_tie
full 921,860, head zoom 1,130,007. All six were VIEWED by the lane
agent: full-body is bright, neutral, and fills the frame head-to-toe
with all default items visible; head zoom is tight on hair + flower
accessory + face; waist zoom centers belt + tie; boots zoom fills the
frame with the boots. This is the close-camera proof the old
640x360 render was not. Owner eye-check is still the final step —
the renders are not committed to the repo.

## Still owed (NOT claimed done)

1. WWE 2K accessory pull: `teardown/wwe2k/` has no accessory catalog
   on main (verified: `teardown/` lists `wwe-2k`, `wwe2k19/20/22`
   dirs, no `wwe2k/` accessory catalog). The WWE 2K22 CAW structure
   file lives on OPEN PR #1069, not on main, so it is not cited as a
   main source. Unblock path: owned-install teardown -> refit each
   piece to the target rig (Blender weight/Data Transfer) -> render
   clean full-body AND part-zoomed -> mark fit/unfit in
   `fit_gate`. Until then `wwe2k.accessories_shipped` stays empty and
   NO WWE piece is a closet option. GPU batch per the blanket GPU
   order when the teardown exists; no GPU job is claimed from a script.
2. Alisa re-render owner eye-check (renders above, once verified
   non-zero and viewed).
3. Live playtest on the deployed build after merge + deploy (steps in
   the PR body): open the closet viewer; toggle slots individually;
   swap slots live; orbit/pan; tap Focus and confirm the camera
   frames THAT part alone, then Full body; cycle studio / living-room
   / night; save a named recipe, change toggles, save again, confirm
   v1 intact; confirm every shipped piece renders clean full-body AND
   part-zoomed. Tests are NOT a playtest.
4. Deploy queue: the popup PR #1078 (priority #1) jumps the queue and
   #1060's merge is HELD until the popup deploy verifies live — this
   PR takes its normal queue position behind the popup deploy. This
   PR is NOT merged by its author; the deploy lane merges when green
   via git_merge.py.

## Environment notes (verified in this session)

- Sandbox file writes from processes that perform network I/O fail
  EPERM intermittently (git fetch, git show of unmaterialized blobs,
  redirected API output all failed; API output piped to stdout worked).
  All PR files were therefore written with muse.write and verified by
  size + content re-read, never trusted from a write call alone.
  Early `node --check` runs on 0-byte `cp` copies passed vacuously and
  were discarded; the real checks are `vm.SourceTextModule` parses
  (all three JS files parse, nonzero bytes) + executed recipe tests.
- Blender is NOT on PATH but exists at
  `~/workspace/tools/blender/blender-4.2.0-linux-x64/blender`
  (also 4.0.2, 4.5.3) — this corrects any "no Blender on this VM"
  report for this session.
- No live browser in this lane: no site visit is claimed anywhere.
- Buttons are LP1/RP2/LK3/RK4 in user-facing text; no famous names
  are shipped in-game; Tekken/WWE names appear in technical files
  only, never in canon/in-game writing.
