# PULL + WIRE, PART 2 — Yarn parser + Ink loader landed, corrections to Part 1 (2026-10-24)

Follow-up to docs/research/PULL-WIRE-RESULTS-2026-10-24.md (merged via PR #1033,
merge commit 62a44a2c, 12/12 CI green). This note lands the two story-engine
wiring items Part 1 left as "next steps," and corrects three Part 1 claims
that later file checks contradicted. Corrections are stated plainly, not buried.

## 1. LANDED IN THIS PR

### 1a. game/js/yarn-parse.js — Yarn Spinner dialogue, no C# port
- Yarn Spinner's main repo is C# (Unity/Godot). Its `.yarn` files are plain
  text (`title:`, `---`, `===`, `[[choice|node]]`, `<<set>>`, `<<if>>`),
  so WH reads them directly with this dependency-free parser + runner.
- Supported: node parsing, choices (consecutive choice lines = one prompt),
  `<<set $var = value>>` / `<<set $var to value>>`, `<<if>>` / `<<else>>` /
  `<<endif>>` (with nesting), `<<jump>>`, `<<stop>>`, `{$var}` interpolation.
  Unknown `<<...>>` commands are ignored, never fatal (forward-compatible).
- Proof (workspace, ~/workspace/pulls-wire/js-tests/ — sample.yarn is a
  Trader-crossroads / Trial-gate / Nine-Souls story, the same beats as the
  Ink trial story, so the two engines are interchangeable for WH dialogue):
  - 5 nodes parsed (Start, TrialGate, WalkAway, CondTest, End).
  - Trial path: souls=3, trial_done=true, line "Souls gathered: 3" present,
    End reached.
  - CondTest (souls=1): RIGHT BRANCH only, WRONG BRANCH never emitted.
  - Direct `next()` / `choose()` API verified separately from `run()`
    (an early version only recorded pending choices inside `run()` — fixed
    before landing: `next()` now records them).
- Wire-in: `game/js/versus-banter.js` (versus banter) and
  `game/js/heartmind.js` (Heart and Mind Within dialogue) import
  `parseYarn` / `YarnRunner` from here. Writers keep authoring visually in
  the Yarn editor; WH consumes the `.yarn` files as-is.
- Division of labour (locked here, not guessed): Ink
  (`game/js/ink-loader.js`) is the pick for heavily branching story with
  variables + knots; Yarn is the pick where writers author visually.

### 1b. game/js/ink-loader.js — Ink loader with the BOM fix
- Dependency-free loader for compiled Ink JSON. The inkjs Story runtime is
  NOT vendored — the caller passes its inkjs Story constructor into
  `createInkStory()`, so the game keeps no CDN dependency and the loader
  stays testable in Node.
- The BOM gotcha, measured 2026-10-24: inkjs-compiler emits a UTF-8 BOM
  prefix; inkjs `new Story(json)` chokes on it. `stripBOM()` runs on every
  load; `parseInkJson()` additionally rejects bad JSON, missing
  `inkVersion`, and empty stories instead of returning a half-loaded story.
- Proof (workspace, trial-test.json from trial-test.ink):
  BOM present in the file, stripped before the Story saw it (stub Story
  throws if a BOM leaks through — it did not); inkVersion 21, root present;
  bad JSON and `{}` both rejected with clear errors.
- Wire-in: `game/js/heartmind.js` + story tooling import `parseInkJson` /
  `createInkStory` / `runInkStory` from here. The inkjs runtime itself
  still needs vendoring by a later lane (it was installed via npm in the
  workspace test only, not committed).

## 2. CORRECTIONS TO PART 1 (read before reusing its checklist)

### 2a. MeshoptDecoder is ALREADY wired — do not re-wire it
Part 1 listed "assets.js MeshoptDecoder" as a wiring step. File check
contradicts it: `game/js/assets.js` already has a shared GLTFLoader with
`setMeshoptDecoder(MeshoptDecoder)` (imported from
`three/addons/libs/meshopt_decoder.js`), used by the fetch+parse load path.
The gltfpack -cc outputs from Part 1 are therefore loadable as-is. No
change made here; the checklist item is closed by pre-existing code.

### 2b. gltfpack / MB-Lab / MPFB already have repo tool dirs — no duplicates
Part 1 proposed a new `tools/optimize-models.sh`. File check: the repo
already has `tools/gltfpack/` (README + fetch-gltfpack.sh +
run_gltfpack_job.py, EXPORT panel -> "Optimize with gltfpack", defaults
`-cc -tc`), `tools/mb-lab/` (fetch + job runner), and `tools/mpfb2/`
(fetch script). Creating another optimizer script would duplicate them.
Batch optimization goes through `tools/gltfpack/`; this PR adds no tool
script. The Part 1 measured results (-62.2% default / -86.9% -cc on
jungle-outpost.glb, -71.3% -cc on the Cape stance file, burger-fixed.glb
internally corrupt and needing re-export) still stand.

### 2c. Castagne: NO GitHub clone — docs reference only
Part 1 correctly listed Castagne as a docs reference
(http://castagneengine.com/docs/, rollback netcode out of the box,
modular character definitions). A guessed clone URL
(`pleonexia/Castagne-Engine`) FAILED (git asked for a username = not a
public path as guessed) and the docs front page text exposes no GitHub
URL. Do NOT use that guessed URL anywhere. Castagne stays what Part 1
said it was: an architecture reference for
`packages/creation-suite/src/movelist-editor.js` (character module pattern)
and `game/netplay/` (rollback-by-default pattern), NOT a port — WH is
web/Three.js, not Godot. If a future lane finds Castagne's real repo URL
from its site or docs, verify it by cloning before citing it.

## 3. STILL OPEN (honest, not hidden)
- GGPO WASM compile (needs Emscripten) OR a JS GGPO port — GGPO C source
  is already local (~/workspace/pulls-wire/ggpo/); the algorithm pattern
  (input prediction + rollback + resim) is the near-term wire-in for
  `game/netplay/sim/` + `mirror.mjs`.
- MB-Lab run (needs a Blender lane; code local in ~/workspace/pulls-wire/mblab/).
- Tripo open source run (needs GPU lane + API keys; Kaggle GPU lane).
- inkjs runtime vendoring into the game (loader landed here; runtime not yet).
- burger-fixed.glb re-export from source (internally corrupt per Part 1).
- Rapier ragdoll wiring into `game/js/physics.js` + `game/js/fighter.js`
  (contextual triggers only: KO, launch, wall splat — never always-on, per
  the ragdoll law). Rapier test passed in workspace; game wiring not done.
- MPFB: repo already has `tools/mpfb2/` fetch script — a local MPFB clone
  would duplicate it, so none was made in this pass.

## 4. CONTINUOUS PULL QUEUE (unfiltered — do not stop)
Per the 2026-10-24 19:31 CDT directive, nothing below was filtered out for
looking academic, unfinished, or weird; each needs an experimental-use
assessment before wiring, same as Part 1's university list (U1–U10):
MPFB full assessment via `tools/mpfb2/`; DOC-pattern full-body IK optimizer
in the WH IK layer (generalize the Cape guard fix); correspondence-free
retarget prototype (one T7 clip -> one WH fighter, measured vs hand-mapped);
LLM service for Trader/banter (local-LLM pattern); behavior-tree AI in
`game/js/ai.js`; continuous arXiv + SIGGRAPH + GDC searching; itch.io
experimental fighters, GitHub game-jam fighters, open source MUGEN
characters (patterns, not assets), Godot fighting demos.
