# Workflow log

## 2026-10-14: Western Heart inventory (Grok Bot executor)
- `gh repo list mhvnsnt --limit 300`, filtered for related repos. Cloned 6 repos at `--depth 50` with `GIT_LFS_SKIP_SMUDGE=1` into /workspace/western-heart-inventory.
- Python walker (`inv.py`): file category counts and sizes, LFS pointer and empty-file scan, and GLB JSON-chunk parse for meshes, skins, joints and animations.
- Read `game/js/*` (grep for loaders and fetch), the READMEs, CHIMERA-BUILD.md, and MoneyManBusch's audit (via `gh api`).
- `gh release list` to see what's stored in Releases.
- Served `game/` with `python3 -m http.server` and took a headless screenshot with Chrome (`--headless=new --use-gl=swiftshader`).
- Wrote INVENTORY.md and inventory.json. Ran gitleaks on the changed files. Docs-only PR: merged origin/main, no rebase or force-push, no deletions.

## 2026-10-14: Lab M1, skeleton + T3 importer + rig check (Grok Bot executor)
- The repo was confirmed PRIVATE (`gh repo view`). The owner approved the Lab track using his own source games.
- Godot 4.3-stable was installed headless at /workspace/tools/godot. Web export templates were streamed out of the .tpz with python `stream-unzip`, because the disk had only about 2 GB free.
- Read the `kmd_parse.py` hierarchy and the `pose_assemble.py` stance OBJ, then fit a rigid Kabsch transform per part (numpy). The stance → world-aligned canonical bind and the `.glb` writer are hand-rolled (numpy).
- Clips use 2-bone analytic IK in `tools/clips.py`.
- Rig check: a numpy glTF evaluator with CPU skinning, checking edge stretch, bone drift and feet-to-floor. It runs as a unittest.
- Previews were rendered with matplotlib and viewed before committing.
- M2: wrote MoveTable (GDScript) and a headless SceneTree test; ran `godot --headless --import` then the test (PASS 7×4).
- M3 (playable slice):
  - Godot GDScript (fighter/ai/hud/main/attire).
  - Owner GLBs pulled with the Google Drive connector. Decoded and LOD'd with `@gltf-transform/cli` (dequantize, weld, simplify, resize).
  - Auto-rig: landmark joints, inverse-distance weights with lateral gating, Laplacian smoothing (scipy) and continuous sparsification to 4 influences. Rig check iterated from FAIL (×77 stretch) to PASS.
  - Bannon mask: per-rig presets fitted in the head-bone rest frame, plus a follow/clip/pop check over 337 frames.
  - Capture: Godot Movie Maker under xvfb with Mesa llvmpipe → ffmpeg H.264, ffprobe and a contact sheet (viewed). HTML5 export uses the `web_nothreads` template; a puppeteer-core real-time screenshot is the web proof.

## 2026-10-14: Shared Creation Suite v0 (Grok Bot executor)
- Survey: `gh search code --owner mhvnsnt` for creation suite / moveset editor / customizer / morphTargetInfluences; read Bannon DNA_SCHEMA, CREATION_SUITE, moveset_schema.json, customizer manifests via `gh api`. Chose Bannon DNA + moveset schema as base.
- Read western-heart PRs (#110–#116) first; Lab #116 owns `lab/` and `attire.gd`, so this PR only adds `packages/creation-suite/` and `docs/creation-suite/`.
- Sparse shallow clone (`--depth 1 --filter=blob:limit=2m`, sparse-checkout) because disk was ~4.5 GB free.
- Wrote the package (ES modules, three r186). `node --test` 4/4 pass.
- Proof: pulled `pantera_leoman.glb` + `bannon_mask.glb` from branch `grok/lab-playable-slice` via `gh api` (not committed), served with python http.server, rendered with playwright-core + headless Chrome (swiftshader). Fixed three bugs found by the render (morph dictionary names, region size units, front/back regions missing the surface). Labels added with PIL → `docs/creation-suite/creation_suite_proof.jpg`.
- gitleaks on the diff; merged origin/main; no deletions.

## 2026-10-17: LANE 3 — Moveset wiring: all 45 fighters on real Tekken inputs (1/2/3/4)

**Audit finding:** the playable build only had TWO movesets wired (`king`, `jin` in
roster-full.js) and the combat system only knew 3 generic actions (punch/kick/grab).
The 7 real T3 teardown movesets (king/jin/yoshimitsu/heihachi/bryan/gunjack/xiaoyu,
teardown/tekken3/movesets/) existed but 5 of them were unreachable from gameplay,
and 29 fighters were mapped to wrong archetypes (e.g. Phantom/Yoshimitsu -> 'jin').

**What was built (branch `feat/moveset-wiring-all-agents`):**
- `game/assets/movesets/{45 ids}.json` — per-fighter Tekken movelists extracted from the
  real T3 motion-bank JSONs via `_lane3/extract_movelists.py` (kept in the lane workdir).
  Each fighter: basics 1/2/3/4, throws 1+3/2+4 (real T3 throw rows, attack_class=1),
  directional attacks (f+1, d/f+2...), strings (1,2 / 2,1 up to 3 hits, from real
  branch chains), specials (motion inputs incl. King's real chain throws
  f,n,b,d/b,d,f+1+2). Every move carries t3_source/t3_row/t3_command provenance.
  Fighters whose Tekken base has no T3 bank use the closest archetype proxy,
  flagged `"proxy": true` with an honest note (T7/TTT2 per-character banks = gapfill lane).
  Capoeira fighters (King Tyrant, Star) moved jin -> xiaoyu proxy (most capoeira-like
  of the 7 T3 sources); roster-full.js `moveset` fields corrected for all 36.
- `game/js/movesets.js` (new) — loader (`loadFighterMovesets`, 45 JSONs into
  window.WH_MOVESETS), `parseSpecialInput`, and `TekkenBuffer`: per-fighter input
  history resolving strings (800ms), motion specials (600ms direction history),
  directionals, and 1+2/3+4 chord specials.
- `game/js/input.js` — Digit1/2/3/4 keys, 1+3/2+4 throw chords + 1+2/3+4 special
  chords (140ms, same pattern as legacy P+K grab), KeyS/ArrowDown + joystick-down
  for d/df/db motions. Legacy J/K/U/L untouched.
- `game/js/fighter.js` — `tryAttack` accepts Tekken notation via TekkenBuffer;
  `getRealMove` reads per-fighter moveset first (legacy aggregate + MOVES fallback,
  plus a no-data fallback so attacks never soft-lock); `_weaponBone`/T3 clip map/
  procedural fallback driven by move limb + notation; AI unchanged (punch->1 etc.).
- `game/js/game.js` — dispatches 1/2/3/4/1+3/2+4/1+2/3+4; feeds facing-relative
  direction (f/b/u/d + diagonals) into each fighter's TekkenBuffer.
- `game/js/main.js` — boots `loadFighterMovesets()` alongside `loadRealMovesets()`.
- Test: `_lane3/test_movesets.mjs` — **1980/1980 checks PASS**: all 45 movesets
  schema-valid, every move executable (startup/active/recovery/damage > 0),
  every T3 row reference verified against the real banks, resolver simulated per
  fighter (raw buttons, string continuation, throws, directionals, motion specials).

**Gaps (honest):** T7/TTT2 per-character movesets are NOT extracted (format docs only
in teardown/tekken7/tekkenmods-docs) — 38 fighters ride T3 archetype proxies until
gapfill lane extracts them. Throw damage: T3 banks store 0, follows WH grappler
convention (flagged per move). Touch UI still has punch/kick buttons (map to 1/4);
dedicated 1/2/3/4 touch buttons are UI lane's call.
