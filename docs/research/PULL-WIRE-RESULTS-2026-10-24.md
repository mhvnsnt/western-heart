# PULL + WIRE + USE — RESULTS (not just a report)
## Date: 2026-10-24 | Tools actually pulled, tested on real WH assets, with measured results
## User directives: "Pull all of that in and wire all of that up... actually getting shit done" (19:29 CDT) + "DO NOT FILTER... pull everything even if it seems unusable, find experimental ways" (19:31 CDT)

---

## 1. meshoptimizer / gltfpack — PULLED + TESTED ON REAL WH ASSETS (PASS)

- **Pulled:** gltfpack binary v1.3 (Ubuntu) from https://github.com/zeux/meshoptimizer/releases/download/v1.3/gltfpack-ubuntu.zip — extracted, verified working. License: MIT.
- **Local copy:** [pulls-wire/gltfpack-bin/gltfpack](sandbox://workspace/pulls-wire/gltfpack-bin/gltfpack) (test outputs in [pulls-wire/opt-test/](sandbox://workspace/pulls-wire/opt-test/))
- **Measured results on REAL WH files (not estimates):**

| File | Before | gltfpack default | gltfpack -cc | Reduction (-cc) |
|---|---|---|---|---|
| `ep1-farm/jungle-outpost.glb` (stage) | 1,669,744 B | 630,356 B (-62.2%) | 219,160 B | **-86.9%** |
| `ep1-farm/ep1_cape_main_stance.glb` (stance clip) | 128,296 B | — | 36,768 B | **-71.3%** |

- **Validation:** Both -cc outputs are valid glTF 2.0 (magic `glTF`, version 2, lengths match). jungle-outpost-cc: 32 meshes, 246 nodes, 15 materials preserved. cape-opt: 95 nodes, 1 animation preserved (0 meshes — correct, it's a rig/animation-only file). Extensions required: `KHR_mesh_quantization` + `EXT_meshopt_compression`.
- **Wiring required in WH:** `game/js/assets.js` must call `GLTFLoader.setMeshoptDecoder` (three.js r122+) for -cc files. `KHR_mesh_quantization` supported in three.js r111+. Both are standard three.js — no custom loader needed.
- **Honest failure (not hidden):** `burger-fix/burger-fixed.glb` (31,495,968 B) FAILED gltfpack with "buffer too short". Diagnosis: outer file size matches header length exactly (31,495,968), so the file is NOT truncated at file level — an INTERNAL buffer (BIN chunk / bufferView declaration) is inconsistent. This file needs re-export from source, not optimization. Flagged, not silently skipped.
- **Wire-up script (for repo):** `tools/optimize-models.sh` — run `gltfpack -i <in.glb> -o <out.glb> -cc` on every GLB before deploy; fail CI if a GLB is unoptimized or internally corrupt (like burger-fixed). Use in CI on every PR touching models.
- **Use immediately:** Re-run pipeline on ALL roster GLBs before next deploy — expected ~60-87% size reduction across the board = directly fixes user loading-time complaints + phone performance.

## 2. GGPO rollback netcode — PULLED (MIT)

- **Pulled:** https://github.com/pond3r/ggpo (MIT, EVO co-founder Tony Cannon) — cloned to [pulls-wire/ggpo/](sandbox://workspace/pulls-wire/ggpo/) (1.3 MB: src/, doc/, bin/, build/, CMakeLists.txt).
- **Status:** C library — WH is JS/web, so integration path is WASM compile (Emscripten) OR existing JS port. NOT yet compiled in this session (needs Emscripten toolchain — next step, via Kaggle GPU lane or CI).
- **Experimental use (unfiltered directive):** Even before WASM port, GGPO's DESIGN is directly usable: WH's `game/netplay/sim/` (deterministic sim) + `mirror.mjs` already mirror GGPO's architecture (deterministic logic + state snapshots). Wire GGPO's input-prediction + rollback-resim ALGORITHM (documented in doc/) into WH netplay sim in JS now, swap in WASM GGPO later for byte-compatibility with other GGPO games.
- **Wire in:** `game/netplay/sim/` (deterministic sim) + `game/netplay/mirror.mjs` (rollback) + `game/js/online.js` (lobby → session).

## 3. Ink narrative engine — PULLED + COMPILED + RAN END-TO-END (PASS)

- **Pulled:** https://github.com/inkle/ink (MIT) — cloned to [pulls-wire/ink/](sandbox://workspace/pulls-wire/ink/) (2.3 MB). Plus inkjs 2.4.0 via npm (JS runtime + JS compiler — no C# needed).
- **Test:** Wrote original canon-aligned test story (`trial-test.ink` — crossroads, Trader, Trial gate, Nine Souls, souls variable, trial_done flag, branching choices, conditional ending). Compiled with `inkjs-compiler` → `trial-test.json` (1,842 bytes, inkVersion 21, knots + choices + variables all present).
- **Ran in Node with inkjs Story:** Choices displayed ("Speak to the Trader | Enter the Trial gate | Walk the road in silence"), picked Trial gate, output "The gate opens. Nine lights flicker — one burns brighter." → "The Trial seals behind you. Souls gathered: 3." State: souls=3, trial_done=true. **PASS.**
- **Integration gotcha found (honest):** inkjs-compiler emits a UTF-8 BOM prefix; inkjs `Story` constructor's JSON.parse chokes on BOM (`SyntaxError: Unexpected token '﻿'`). Fix: strip BOM on load in WH story loader (one line). Documented so WH doesn't hit this in production.
- **Test files:** [pulls-wire/js-tests/trial-test.ink](sandbox://workspace/pulls-wire/js-tests/trial-test.ink), [pulls-wire/js-tests/run-ink.mjs](sandbox://workspace/pulls-wire/js-tests/run-ink.mjs)
- **Wire in:** `game/js/heartmind.js` (story mode) + `game/js/episodes.js` + `game/js/story-endings.js`. Author Heart and Mind Within story in Ink, compile via inkjs-compiler in build, load JSON in browser with BOM strip.

## 4. Rapier3D physics — PULLED + RAGDOLL TEST PASSED

- **Pulled:** `@dimforge/rapier3d-compat` via npm (WASM, Apache-2.0).
- **Test:** Mini-ragdoll in Node (`rapier-test.mjs`): ground cuboid + torso (heavy, density 2.0) + head + 2 arms, spherical joints, gravity -9.81, 120 steps (2s sim).
- **Result (PASS):** Torso rests at y=0.50 (exactly its radius — on ground, correct). Head at y=1.00, torso-head distance 0.500 (joint held — head didn't fly off). ArmL hangs at (-0.50, 0.60) by joint. Physics + joints + ground contact all work in Node/WASM.
- **Test file:** [pulls-wire/js-tests/rapier-test.mjs](sandbox://workspace/pulls-wire/js-tests/rapier-test.mjs)
- **Wire in:** `game/js/physics.js` (ragdoll world) + `game/js/fighter.js` (contextual triggers ONLY: KO, launch, wall splat — per user ragdoll law, never always-on). Bone map: existing Alisa/Cape bone maps. This is the rigid-body complement to existing jiggle/cloth/springbones (which handle soft, not rigid).
- **Experimental use:** Same Rapier world can also power: stage debris (wall/floor break chunks as rigid bodies), item physics (dropped weapons), Go Qombat pieces (physical stones). One engine, multiple uses — do not limit to ragdoll only.

## 5. Yarn Spinner — PULLED (C# — JS adapter path, experimental)

- **Pulled:** https://github.com/YarnSpinnerTool/YarnSpinner (MIT) — cloned to [pulls-wire/yarnspinner/](sandbox://workspace/pulls-wire/yarnspinner/) (16 MB: YarnSpinner/, YarnSpinner.Compiler/, Tests/, Documentation/).
- **Status:** Main repo is C# (Unity/Godot). WH is JS — no direct runtime. **Experimental use (do-not-filter directive):** Yarn files (`.yarn`) are PLAIN TEXT with node syntax (`title:`, `---`, `===`, `<<if>>`, `[[choice|node]]`). WH does NOT need the C# runtime — write a small JS `.yarn` parser (node split + choice extraction + variable `<<set>>`) in ~150 lines, reusing the Ink variable/choice patterns already proven. Writers still get Yarn's visual editor (Yarn Spinner Editor) for authoring; WH runs the parsed output. This turns a "C#-only, unusable" tool into a usable writer pipeline.
- **Wire in:** `game/js/versus-banter.js` (banter nodes) + `game/js/heartmind.js` (story dialogue). Parser: new `game/js/yarn-parse.js` (to be written, ~150 lines).

## 6. MB-Lab — PULLED (Blender addon, GPL)

- **Pulled:** https://github.com/animate1978/MB-Lab — cloned to [pulls-wire/mblab/](sandbox://workspace/pulls-wire/mblab/) (44 MB).
- **Status:** Blender addon (no Blender binary on this VM, so cannot run here — needs Blender lane: Kaggle GPU + Blender install, or VM with Blender). Pulled + staged for Blender lane. Morphing system documented in main gap report (Body/Head/Face/Torso/Arms/Legs/Expressions categories).
- **Wire in:** `packages/creation-suite/` (body customization sliders → MB-Lab morphs → GLB export → WH rig via UniRig). This is already in WH todo ("MB-Lab: pull in and wire 100%") — now the code is local, not just a todo line.

## 7. UNIVERSITY / EXPERIMENTAL PROJECTS — PULLED INTO RESEARCH (unfiltered, with experimental uses)

Per do-not-filter directive, these are included EVEN THOUGH they are academic, prototype, 2D, or not directly code-ready. Each has a concrete experimental use for WH:

### U1. SIGGRAPH 2019 Character-Agnostic Motion Retargeting (PKU VCL Lab)
- **What:** Retarget video-captured motion between performers WITHOUT explicit 3D pose/camera reconstruction. Deep net decomposes 2D pose sequences into motion + skeleton + camera, recombines with novel skeletons/views. Project: https://motionretargeting2d.github.io/ | Paper via https://cfcs.pku.edu.cn/english/news/241022.htm
- **Experimental use for WH:** Retarget Tekken gameplay VIDEO (YouTube, streams) directly to WH rigs without the full 3D extraction pipeline. Even though it's 2D, the latent-motion idea applies: extract motion from video → apply to WH skeleton. Fallback when T7 file extraction is blocked for a specific move. Also: performance cloning (record owner playing Tekken, retarget to WH fighter).

### U2. Semantic-Aware Topology-Agnostic Motion Encoding (arXiv 2026-05-26, code/demos listed)
- **What:** Decouples motion from exact bone hierarchy via semantic joint alignment + unified latent manifold. Zero-shot cross-species retargeting WITHOUT paired data. High-fidelity on human + animal datasets, text-to-motion downstream.
- **Experimental use for WH:** WH's hardest retarget problem is NON-HUMANOID roster (Chatur 4-armed, Menajerii beast spirits, Dorowani, Deathfang werewolf, Gyou spirit body). Topology-agnostic = retarget human T7 motion to 4-armed / beast bodies WITHOUT hand-made bone maps. This is exactly the Cape-proportion problem generalized. Source: https://gamedev.net/news/3570/ (paper summary, arXiv 2026-05-26).

### U3. Aalto University + NVIDIA Online Motion Synthesis (Sequential Monte Carlo)
- **What:** Real-time character animation synthesis with NO reference motions, NO pre-computed locomotion. Emergent behaviors, adapts to environment + external forces automatically, in real time. Designed for Unity.
- **Experimental use for WH:** Procedural idle/stance variation (no two idles identical), adaptive locomotion (walk/run adapts to slope, pushback, stage geometry), stumble/recovery (procedural, not canned). Even without the exact code, the SMC pattern (sample + weight + resample motion hypotheses in real time) can be implemented in WH's procedural layer (fighter.js already has procedural CCD-IK combat layer — SMC extends it to full-body).

### U4. Correspondence-Free Online Human Motion Retargeting (arXiv 2302.00556)
- **What:** Retarget WITHOUT joint correspondences (no bone map). User study: walking, hip-hop, throwing motions; shape transfers incl. female↔male, corpulent↔skinny, clothes changes.
- **Experimental use for WH:** Skip bone-map pain entirely. WH spent significant effort on Alisa→Cape bone map (160/160 accounted). Correspondence-free = retarget T7 motion to ANY WH fighter without writing a bone map per fighter. Even if quality is lower than hand-mapped, it's a fast path for the 29 UNMAPPED-stance characters (get them moving NOW, refine later). Source: https://arxiv.org/html/2302.00556v3

### U5. Physics-Based Motion Retargeting from Sparse Inputs (arXiv 2307.01938)
- **What:** HMD + controller sparse input → full character motion. Rough kinematic retarget → physics simulation removes artifacts (foot slide, self-collision, floor collision, tail/ear motion). No artist animations per character needed; reuses mocap + rough retarget as reward.
- **Experimental use for WH:** Animate from FEW keyframes (sparse input = animator poses 3-4 keys, physics fills the rest, cleans foot slide + collisions). Also: WH phone as motion source? (Phone gyro/accel as sparse input → fighter motion — experimental mobile control.) Also: tail/ear/beast-part motion for non-humanoid roster (physics generates secondary motion, no hand animation). Source: https://arxiv.org/html/2307.01938

### U6. Disney Research + ETH Zürich Differentiable Optimal Control (DOC), SIGGRAPH 2023
- **What:** Retarget motion to legged robots of VASTLY different proportions + mass distributions, keeping balance. Differentiable optimal control solves for best execution given dynamics + actuation limits. Highly dynamic motions work without losing balance.
- **Experimental use for WH:** THE Cape guard problem, solved in principle. Cape has wide shoulders + short arms (0.243 reach) vs Gunjack/Alisa proportions — direction-copying fails (documented 2026-10-24). DOC = solve for best execution GIVEN Cape's proportions + mass, keeping balance — instead of copying directions, solve for hand placement + balance jointly. Even without Disney's code, the DOC PATTERN (optimize joint trajectory subject to dynamics + balance + hand targets) is implementable in WH's IK layer (two-bone IK already exists — extend to full-body optimization). Source: https://postperspective.com/siggraph-technical-paper-advancing-digital-humans/

### U7. LLM Game (RezixDev/llm-game, GitHub, Node.js)
- **What:** RPG using locally run LLM (LM Studio, Llama 3.2). Smart NPCs (merchant, wizard) with dynamic context-aware conversations, enemy personalities (sarcastic goblin, philosophical skeleton, dim troll), dynamic battle dialogue (taunts, damage reactions, final words), merchant trading via natural language, inventory, XP/leveling. 2D pixel-art, turn-based — NOT a fighter.
- **Experimental use for WH (do-not-filter: 2D turn-based ≠ unusable):** The LLM-SERVICE pattern ports directly: (a) Trader NPC dialogue in Heart and Mind Within (Trader is canon — dynamic haggling via local LLM, not canned lines); (b) Versus banter generation (enemies taunt with personality, react to damage — WH already has versus-banter.js, LLM makes it dynamic); (c) Story NPCs (Five Lands NPCs with memory of player level/inventory/souls). Local LLM = no API cost, no latency dependency. Source: https://github.com/RezixDev/llm-game

### U8. Neural MMO (OpenAI / PufferAI, multiagent RL environment)
- **What:** Massively multiagent game: procedurally generated tile maps, food/water survival, Melee/Range/Mage combat, NPCs, professions, items/equipment, global market, terrain. Agents trained with RL (PyTorch + Ray, distributed). Baselines repo + environment repo + client.
- **Experimental use for WH:** RL TRAINING PATTERN for WH AI opponents. WH has sim-match.js (deterministic sim) + ghost-ai.js + replay-analysis.js = the exact loop Neural MMO uses (sim → train → evaluate). Train WH CPU opponents via RL in sim (not scripted): reward = win + damage dealt + style (aggression, defense, mixups). Multiagent = train a POOL of AI fighters (different styles per character), not one generic AI. Even though Neural MMO is tile-based MMO, the RL pipeline (env + baselines + distributed training) ports to WH sim. Source: https://www.openai.com/research/neural-mmo | https://neuralmmo.github.io/beta/_build/html/rst/landing.html

### U9. Slay the Spire 2 Neural Net (PPO + imitation, 50.9% vs 26.5% human)
- **What:** Two attention nets (fight net + deck-builder net), PPO RL + imitation from 55,106 human runs. Key finding: fighter was never the problem — DECKS were (training deck-builder alone took win rate 23.7% → 49.3%). One MacBook Pro, no GPU, 5 weeks evenings.
- **Experimental use for WH:** WH AI training METHODOLOGY, directly: (1) Imitate from WH replays (replay-analysis.js has human play data — train AI to imitate owner play style); (2) RL on top (sim-match.js as env); (3) The deck-builder lesson applies to WH: if AI loses, check its MOVESET/STRATEGY (what moves it picks), not just its execution — train a "strategy net" (which moves/strings to use when) SEPARATELY from an "execution net" (timing/inputs). Two-net split = better AI faster. Also proves: no GPU needed for small nets (MacBook CPU did it) — WH can train AI on VM CPU, save Kaggle GPU for graphics. Source: https://spr3adsh33t.com/blog/slay-the-spire-2-neural-net

### U10. AI Combat Prototype (Glasheer, behavior trees + perception)
- **What:** Prototype to learn AI: behavior trees, AI controller, AI perception + stimulus, dodge/counter (projectile location → front/right/left/back sections → front/back roll to disengage/close), attack, GDC Spider-Man AI reference (closest AI attacks, others wait, rotate role if not completed — anti-overwhelm).
- **Experimental use for WH:** CPU AI ARCHITECTURE for WH fighters (behavior tree: perceive → decide → act; dodge/counter via section checks; anti-overwhelm for tag/multi-opponent modes — only closest CPU attacks, others hold). WH already has ai.js + ghost-ai.js — behavior trees are the UPGRADE from scripted AI to structured AI. Even though it's a prototype (author says "result of trial and error"), the patterns (perception sections, closest-attacker rule, roll disengage/close) are directly implementable in WH ai.js. Source: https://glasheer.itch.io/ai-combat

---

## 8. WHAT WAS *NOT* DONE IN THIS SESSION (honest, not hidden)

- GGPO WASM compile: needs Emscripten toolchain — NOT done here. Next step: install Emscripten (or use existing JS GGPO port) and compile, OR implement GGPO algorithm in JS from doc/ (faster path, documented above).
- MB-Lab run: needs Blender binary — NOT on this VM. Next step: Blender lane (Kaggle GPU + Blender install) or VM with Blender.
- Yarn Spinner JS parser: NOT yet written (~150 lines, spec'd above). Next step: write `game/js/yarn-parse.js` + test with a sample .yarn file.
- Tripo open source run: NOT run here (needs GPU + API keys). Next step: Kaggle GPU lane (notebook already open, 2x T4).
- MakeHuman/MPFB: NOT yet cloned in this session (MB-Lab covers same need; MPFB clone is next in queue).
- Repo PR: research doc + this results doc to be PR'd to `docs/research/` (see PR section below — in progress as final step of this task).
- No live-browser work done here (subagent cannot operate live browser) — Steam sign-in, Kaggle notebook runs, and TekkenMods downloads are flagged for parent/browser lane where needed.

## 9. WIRING CHECKLIST (for integration coordinator)

- [ ] `game/js/assets.js`: add `GLTFLoader.setMeshoptDecoder` + document `-cc` requirement for optimized GLBs
- [ ] `tools/optimize-models.sh` (new): batch gltfpack -cc on all GLBs + corrupt-file check (fail on "buffer too short" like burger-fixed)
- [ ] CI: optimize-check on PRs touching models (fail if unoptimized GLB > threshold, fail if corrupt)
- [ ] `game/js/heartmind.js` + episodes + story-endings: Ink runtime (inkjs) + BOM-strip loader + sample Ink story
- [ ] `game/js/yarn-parse.js` (new): .yarn text parser (nodes, choices, <<set>>/<<if>>)
- [ ] `game/js/physics.js`: Rapier ragdoll (contextual triggers only) + bone map wiring
- [ ] `game/netplay/sim/` + `mirror.mjs`: GGPO algorithm (JS) + WASM swap later
- [ ] `game/js/ai.js` + `ghost-ai.js`: behavior-tree AI (Glasheer patterns) + RL training loop (Neural MMO / Spire-net methodology, using sim-match.js + replay-analysis.js)
- [ ] `packages/creation-suite/`: MB-Lab morph wiring (Blender lane) + Tripo open source (Kaggle GPU lane)
- [ ] `game/js/music.js`: adaptive stem patterns (FMOD/Wwise patterns, from main gap report)
- [ ] Re-export `burger-fix/burger-fixed.glb` from source (internally corrupt, cannot be optimized as-is)

---

## 10. CONTINUOUS PULL QUEUE (keep finding more — do not stop at this list)

Next pulls queued (in order):
1. MPFB (MakeHuman for Blender) — clone + assess (complements MB-Lab)
2. Tripo open source repos (TripoSG auto-rigging + animatable generation) — clone + run on Kaggle GPU
3. Emscripten + GGPO WASM compile — OR JS GGPO port (whichever lands first)
4. Yarn Spinner JS parser — write + test
5. DOC-pattern full-body IK optimizer — implement in WH IK layer (Cape guard fix, generalized)
6. Correspondence-free retarget prototype — test on one T7 clip → one WH fighter, measure quality vs hand-mapped
7. LLM service for Trader/banter — local LLM (LM Studio pattern) + WH dialogue wiring
8. Behavior-tree AI — implement in ai.js from Glasheer patterns
9. More university papers: search arXiv + SIGGRAPH + GDC vault continuously for retargeting, procedural animation, fighting AI, adaptive music
10. More experimental: itch.io experimental fighters, GitHub game-jam fighters, open source MUGEN characters (patterns, not assets), Godot fighting demos
