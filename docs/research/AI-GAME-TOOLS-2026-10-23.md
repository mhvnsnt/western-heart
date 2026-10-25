# AI + 3D-Generation Tools Evaluation

**Date:** 2026-10-23
**Scope:** RESEARCH ONLY — no installs, no weights downloaded, nothing on disk (VM disk at 93%). Web research via search + page fetches.
**Prior art this builds on:** `docs/research/3d-generation-pipeline-2026-10-22.md` (Worker 44, 2026-10-22) — the "stacked pipeline" report. This doc does **not** re-litigate that comparison; it answers the five follow-up questions below and points at that report for the full model table.
**Related:** `docs/research/OPEN-SOURCE-WAVE-2026-10-22.md` (worker 22 — UniRig already wired into `tools/auto_rig` backends).

**Evaluator questions (verbatim from assignment):**
1. *behaviac vs Yuka.js — does behaviac REPLACE Yuka.js, AUGMENT it, or serve a different layer? Our game is JS/Three.js web-based; behaviac is C++. How would it integrate?*
2. *DreamGaussian vs TripoSR for character/creature generation from images. Repo research already ranks TripoSR lowest on quality but it's the lightest. Which is better for rapid prototyping? Which for final assets? Where do they fit in the stacked pipeline (Hi3DGen → TRELLIS.2 → UniRig via hosted APIs)?*
3. *Document the TripoSR API workflow via hosted APIs (fal.ai, Replicate) — no local install. Write the actual API call patterns. This becomes the interim generation workflow until the full stacked pipeline is ready.*
4. *Stable-Baselines3: how would we use RL to train combat AI opponents? Architecture? (Godot-Gym pattern → our Three.js game?) Long-term roadmap, don't implement.*
5. *Godot/GDevelop/Panda3D: NOT switching engines. Document 2–3 transferable techniques from each for AI integration or asset pipelines.*

---

## 0. Executive summary — recommendations

| Tool | Verdict | One-line reason |
|---|---|---|
| **behaviac** | ❌ **Do not adopt as a runtime. Different layer, don't integrate.** | C++/C# runtime, Windows-only visual designer, no JS/WASM build, slow maintenance (65 commits total). Our game is JS/Three.js. |
| **Yuka.js** | ✅ **Stays as the runtime AI layer** | JS-native, steering + FSM + goal-driven + navmesh + perception, built for three.js. behaviac answers nothing Yuka doesn't already cover at runtime. |
| Behavior Trees (the *idea* from behaviac) | ⚠️ **AUGMENT via a JS BT library on top of Yuka.js** — if/when we outgrow FSMs | If BTs are wanted, use a JS-native BT runtime (e.g. behavior3js-style) driving Yuka entities. Author in JSON. Never port behaviac's C++. |
| **TripoSR** | ✅ **Rapid prototyping, interim workflow** | Seconds per asset, cheapest hosted 3D endpoint, MIT. Draft-tier quality (repo already ranks it lowest) — silhouettes and proportions only. |
| **DreamGaussian** | ⚠️ **Niche: organic creature/props mid-tier** | ~2 min/asset optimization-based; splatting + mesh extraction + UV texture refinement shines on organic forms. Not a final-asset engine. |
| Final assets | ✅ **Stacked pipeline unchanged: Hi3DGen → TRELLIS.2 → UniRig** | Per the 2026-10-22 report. TripoSR = Stage 1c draft path; DreamGaussian = optional Stage 1b-alt for organic drafts. |
| **Stable-Baselines3** | 📋 **Long-term roadmap only** | Train via a headless-Node ↔ Python bridge (the godot-rl-agents socket pattern), export ONNX → onnxruntime-web. Blocked until the combat sim is deterministic and headless — and until the input-to-move fidelity law is satisfied (RL on broken inputs is wasted). |
| Godot / GDevelop / Panda3D | 📋 **Steal techniques, not engines** | AnimationTree combat state-machine discipline (Godot); attachable Behavior components (GDevelop); PandAI steering + ClassicFSM enter/exit naming (Panda3D) — all map onto our Yuka.js layer. |

---

## 1. behaviac vs Yuka.js

### 1.1 What behaviac is (verified)

- **Tencent/behaviac** — "a framework of the game AI development, and it also can be used as a rapid game prototype design tool. behaviac supports the behavior tree, finite state machine and hierarchical task network (BT, FSM, HTN)." Source: https://github.com/Tencent/behaviac
- **Runtime:** C++ and C#. Supports Windows, Linux, Android, iOS, Unity. "The C++ version is suitable for the client and server side."
- **Designer:** visual editor shipped as a Windows-only installer (`BehaviacSetup*.exe`). "Behaviors can be designed and debugged in the designer, exported and executed by the game." The designer runs **only on Windows**.
- **Health:** 3,050 stars / 815 forks, **not archived** — but only **65 commits in the entire history** (created 2016). Effectively in maintenance mode; the release badge sits at 3.6.39. Treat as a stable-but-stagnant project.
- **License caution:** GitHub reports license as NOASSERTION (no machine-readable SPDX identifier; the repo ships a custom `license.txt`). **Verify the license text before any commercial use** — do not assume MIT/BSD.
- **No JavaScript runtime.** There is no official JS or WebAssembly build of the behaviac runtime.

### 1.2 What Yuka.js is (verified)

- **Mugen87/yuka** — "A JavaScript library for developing Game AI." JS-native, engine-independent, with three.js used in all examples. Source: https://mugen87.github.io/yuka/
- Covers: **steering behaviors** (seek, flee, arrive, wander, pursuit, evade, obstacle avoidance, path following) on a physics-based `Vehicle` model; **finite state machines** (`StateMachine` with `enter`/`execute`/`exit` + global state + previous-state revert); **goal-driven agents** (hierarchical goals/subgoals with priorities); **navigation** (graph search + navmesh pathfinding); **perception** (vision component + short-term memory); **triggers**; `EntityManager` lifecycle; `CellSpacePartitioning` for spatial queries.
- This is the industry-standard AI toolkit lineage (Reynolds steering, Mat Buckland FSM/goal patterns) implemented for the web.

### 1.3 The integration question, answered directly

**Does behaviac REPLACE Yuka.js? No.** To run behaviac in our game we would have to compile its C++ runtime to WebAssembly via Emscripten, write JS bindings for every API surface we touch, and maintain that fork forever — against a stagnant upstream. All for BT/FSM/HTN capability that **Yuka.js already provides natively in JS** (FSM + goal-driven planning today; steering and perception included).

**Does it AUGMENT Yuka.js? Only at the design-authoring layer, and even that is optional.** The one thing behaviac has that Yuka lacks is the *visual designer* for authoring behavior trees. But the designer is Windows-only, and its exported format targets the C++/C# runtime. There is no supported path from "behaviac designer file" → "runs in a browser."

**It serves a different layer.** behaviac is a native-game AI runtime + desktop authoring tool. Yuka.js is a web-game AI runtime. They do not meet in our stack.

### 1.4 Recommendation

1. **Keep Yuka.js as the single runtime AI layer.** It is already being wired in; it is JS-native, three.js-friendly, and covers steering, FSM, goals, navmesh, and perception — everything our combat AI, training-dummy logic (Gungaku), and crowd/ambient AI need.
2. **If behavior trees are wanted later** (e.g. for complex boss AI or the Fire Pro-style AI logic programming the user asked for), add a **JS-native BT library as a layer on top of Yuka.js entities** — BT nodes calling into Yuka steering/state primitives. Author trees as JSON. Do not port behaviac.
3. **Borrow behaviac's *design ideas*, not its code:** blackboard data sharing between BT nodes, decorator nodes (cooldown, repeat-until), and the designer→export→runtime split (author visually, execute from data) are all worth copying into our own tooling when the time comes.

---

## 2. DreamGaussian vs TripoSR

### 2.1 Head-to-head (verified specs)

| | **TripoSR** | **DreamGaussian** |
|---|---|---|
| Method | Feedforward transformer (LRM-based). Single forward pass → triplane → mesh. | **Optimization-based, two-stage:** (1) generative 3D Gaussian Splatting with SDS supervision (~500 steps, ~1 min) → coarse shape; (2) mesh extraction (local density query) + **UV-space texture refinement**. |
| Speed | **<0.5 s on an A100**; seconds on consumer GPU; CPU mode exists | **~2 minutes per asset** on a single GPU |
| Quality | Lowest of our evaluated group — "blurry on detail" (per `3d-generation-pipeline-2026-10-22.md` §2). Draft-tier: good silhouettes, weak faces/details. | Competitive mid-tier: explicit texture-refinement stage gives better surface detail than raw splats; organic/rounded forms come out well |
| Input | Single image | Single image **or text prompt** (or both) |
| Output | OBJ/GLB triangle mesh, basic baked texture | Textured mesh + texture maps |
| VRAM (self-host) | ~6 GB | Single-GPU (needs diffusion guidance models resident — heavier than TripoSR) |
| License | **MIT** (code + weights) | Paper: PKU/NTU/Baidu, arXiv 2309.16653 — check repo license before commercial use |
| Sources | https://arxiv.org/html/2403.02151v1 · https://github.com/VAST-AI-Research/TripoSR | https://arxiv.org/pdf/2309.16653 · https://deepwiki.com/dreamgaussian/dreamgaussian |

### 2.2 Verdicts

- **Rapid prototyping: TripoSR, by a mile.** Sub-second-to-seconds per asset, cheapest hosted 3D endpoint, MIT-clean, runs weightlessly via API. When the user drops a reference image, TripoSR answers "does this silhouette/proportion read as the character?" in seconds. That is exactly what a prototype loop needs.
- **Final assets: neither.** The stacked pipeline stands: **Hi3DGen (geometry detail) → TRELLIS.2 (PBR texturing) → UniRig (auto-rig)** per the 2026-10-22 report. Both TripoSR and DreamGaussian sit *below* that bar on detail and PBR quality.
- **DreamGaussian's niche:** organic creature and prop drafts — puma/bear/Godzilla-type/gorilla/Dorowani-style sculpts where Gaussian splatting's free-form blob topology and the UV texture-refinement pass produce nicer organic surfaces than TripoSR's blurry LRM output. Think of it as an **optional Stage 1b-alt**: when a creature draft from TripoSR is too blobby *in the wrong way*, spend 2 minutes on a DreamGaussian pass before committing H100-seconds to the full stack. Also note it does **text-to-3D**, which TripoSR cannot — useful for "I don't have a reference image yet" ideation.
- **Pipeline placement (mapping onto the 2026-10-22 report's stages):**
  - Stage 1c (fast iteration): **TripoSR** — unchanged, now with the concrete API workflow in §3.
  - Stage 1b-alt (organic draft, NEW): **DreamGaussian** — 2 min/asset, only for creatures/props where it beats TripoSR.
  - Stage 1/1b (final generation): **Hi3DGen → TRELLIS.2** — unchanged.
  - Stage 2 (rigging): **UniRig** — unchanged; all draft meshes that survive QC go through the same rigging stage.
- **Watch, don't build on:** VAST/Tripo's own newer open releases — **TripoSplat** (MIT, June 2026: single-image → 3D Gaussians, .ply/.splat) and **TripoSG/TripoSF**. TripoSplat is the "modern DreamGaussian" from the Tripo team itself; if we ever want splatting in the pipeline, prefer it over DreamGaussian (actively maintained, same team as TripoSR). Source: https://radiancefields.com/platforms/tripo-ai
---

## 3. TripoSR API workflow (interim generation path)

**Status:** this is the crew's interim workflow — usable TODAY, no local install, no weights on disk. It produces **draft-tier** meshes (silhouette/proportion checks, mockups, "does this read as the character?"), not final assets. Final assets still go through the stacked pipeline (§2).

### 3.1 Primary route: fal.ai `fal-ai/triposr`

Verified input schema (fal.ai model docs):

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `image_url` | string | ✅ | — | Public URL, base64 data URI, or fal.storage upload URL |
| `output_format` | `"glb"` \| `"obj"` | — | `"glb"` | Use `glb` — loads straight into three.js / our intake viewers |
| `do_remove_background` | boolean | — | `true` | Leave on unless the reference is pre-masked |
| `foreground_ratio` | float | — | `0.9` | How tightly to crop the foreground; lower = tighter |
| `mc_resolution` | integer | — | `256` | Marching-cubes resolution. **Above 512 not recommended** (VRAM/time blowup for little gain at draft tier) |

**JavaScript (crew's main language):**

```js
import { fal } from "@fal-ai/client";

// 1. Upload the reference image (or pass a public URL / data URI directly)
const file = new File([imageBytes], "reference.png", { type: "image/png" });
const image_url = await fal.storage.upload(file);

// 2. Generate — subscribes to the queue and resolves when done
const result = await fal.subscribe("fal-ai/triposr", {
  input: {
    image_url,
    output_format: "glb",
    do_remove_background: true,
    foreground_ratio: 0.9,
    mc_resolution: 256,
  },
});

// 3. result.model_file.url (or similar file object) → download the .glb
console.log(result);
```

**Python (pipeline scripts):**

```python
import fal_client

result = fal_client.subscribe(
    "fal-ai/triposr",
    arguments={
        "image_url": "https://example.com/reference.png",
        "output_format": "glb",
        "do_remove_background": True,
        "foreground_ratio": 0.9,
        "mc_resolution": 256,
    },
)
print(result["model_file"]["url"])  # download this .glb
```

**REST (curl) — queue API:**

```bash
curl -X POST "https://queue.fal.run/fal-ai/triposr" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://example.com/reference.png","output_format":"glb","do_remove_background":true}'
# → returns status/logs; poll the status URL, then fetch result.model_file.url
```

Notes: fal.ai bills pay-per-compute-second; TripoSR is among the cheapest 3D endpoints on the platform (sub-second GPU time). Queue + webhook mode exists for batch runs — prefer `fal.queue.submit` + webhook over polling when scripting multi-character batches.

### 3.2 Secondary route: Replicate

The 2026-10-22 pipeline report confirms TripoSR is hosted on Replicate (pay per second). The exact model slug/version was **not independently verified** in this research round — resolve it at replicate.com/explore before scripting. The call pattern once resolved:

```python
import replicate
output = replicate.run(
    "<owner>/triposr:<version>",  # resolve exact slug on replicate.com
    input={"image": open("reference.png", "rb")},
)
print(output)  # model file URL (.glb/.obj)
```

```js
import Replicate from "replicate";
const replicate = new Replicate({ auth: process.env.REPLICATE_API_TOKEN });
const output = await replicate.run("<owner>/triposr:<version>", {
  input: { image: "https://example.com/reference.png" },
});
```

Prefer fal.ai as the primary (schema verified above); keep Replicate as the fallback/price-check.

### 3.3 The crew workflow, step by step

1. **Reference prep** — user-supplied image (or generated concept art). Square-ish framing, character centered, clean-ish background. If the character has a complex background, pre-mask or rely on `do_remove_background`.
2. **Draft call** — `fal-ai/triposr` with defaults above, `output_format: "glb"`. Expect the result in seconds.
3. **Download** — fetch `model_file.url` to `intake-stage/<character>/triposr-draft-<date>.glb` (scratch — not the roster archive).
4. **QC gate (human)** — open in the existing three.js intake viewer. Check: silhouette reads as the character? Proportions sane? Limbs all present (TripoSR can merge/omit thin limbs)? **Draft-tier bar only** — do not judge textures or faces.
5. **Decision:**
   - Pass → ingest the reference + draft notes into the character's intake folder; when the full stack is ready, this reference feeds Stage 1 (Hi3DGen/TRELLIS.2).
   - Fail → tweak reference (pose, framing, background) and re-run. Drafts are disposable; a re-run costs seconds.
6. **Roster convention** — anything promoted out of draft follows the existing intake layout: `roster/<character>/attires/attire<N>/source/` (immutable original archived, per the Tripo-intake rules).
7. **Handoff to rigging** — draft meshes that survive QC go through the same downstream stages as full-stack output (UniRig backend in `tools/auto_rig`, human skeleton review per UniRig's README guidance for exotic topologies).

### 3.4 Limits the crew must respect

- Quality ceiling is **draft-tier** (repo ranking: lowest of the group, "blurry on detail"). Never present a TripoSR mesh as a finished model.
- Thin extremities (fingers, tails, ears, weapon tips) are the most common failure — check them first in QC.
- Faces will be blobby. For face-critical characters (Jin Eastern Mind from user photos), TripoSR is a **proportion placeholder only**; the face comes from the full stack or the user's hand-picked model.
- `mc_resolution` above 512 is not recommended — it does not fix the quality ceiling, it just costs more.

---
## 4. Stable-Baselines3 — combat AI roadmap (long-term, research only)

### 4.1 What SB3 is (verified)

- **DLR-RM/stable-baselines3** — "a set of reliable implementations of reinforcement learning algorithms in PyTorch." Source: https://pypi.org/project/stable-baselines3/
- Algorithms: PPO, A2C, DQN, SAC, TD3, HER (+ LSTM variants). sklearn-style API: `model = PPO("MlpPolicy", env); model.learn(total_timesteps=...)`.
- Ecosystem: **Gymnasium** API (the env interface), **rl-baselines3-zoo** (tuned hyperparameters per env — use these instead of hand-tuning), **sb3-contrib** (extra algorithms), **SBX** (Jax re-implementation for speed).
- SB3 does not play games by itself — it needs a **Gymnasium environment** wrapping the game. That bridge is the actual work.

### 4.2 The Godot-Gym pattern (verified — this is the architecture to copy)

**edbeeching/godot-rl-agents** connects the Godot engine to SB3 (and Sample Factory, Ray RLlib, CleanRL). How it works:

- **Client–server over TCP sockets with JSON messages.** Python is the server; the game is the client. Default port `11008` (one port per parallel env instance).
- Each message = 4-byte little-endian length header + UTF-8 JSON payload. Messages carry observations, actions, rewards, and control signals (reset/step).
- Game side: a `Sync` node gathers observations and applies actions each physics tick. Python side: `GodotEnv` exposes the Gymnasium API; framework-specific wrappers adapt it to SB3 etc.
- **Two-level parallelization:** N game processes × M agents per process.
- **Deployment:** trained policies export to **ONNX** and run inside the shipped game — training happens in Python, inference happens in-engine.

Sources: https://deepwiki.com/edbeeching/godot_rl_agents · https://deepwiki.com/edbeeching/godot_rl_agents/2.2-communication-protocol

### 4.3 The WH-RL bridge (proposed architecture — Three.js edition)

Same pattern, our stack:

```
┌─────────────────────────────┐        WebSocket/TCP + JSON        ┌──────────────────────────────┐
│  WH headless combat sim     │◄──────────────────────────────────►│  Python trainer              │
│  (Node.js, NO rendering)    │   obs {positions, hp, meter, ...}  │  Gymnasium env (WHEnv)       │
│  - fixed timestep           │   action {discrete Tekken inputs}  │  SB3 PPO (+ Zoo hyperparams) │
│  - seeded RNG               │   reward {dmg dealt/taken, win}    │  curriculum + self-play      │
│  - N parallel instances     │                                    │  checkpoints → ONNX export   │
└─────────────────────────────┘                                    └──────────────────────────────┘
                                   │
                                   ▼
                    onnxruntime-web in the browser:
                    CPU opponent policies ship WITH the game,
                    run offline, no server needed
```

**Design decisions (recommended):**

- **Observation space — proprioceptive first, pixels never (for now).** Frame-data-style vector: both fighters' positions/velocities, health, meter/heat, frame advantage, distance, round timer, current states. This trains in hours, not weeks. Pixel-based policies are a research luxury we don't need for a fighting game with a perfect-information state vector.
- **Action space — discrete Tekken inputs.** Directions × {1, 2, 3, 4} attack buttons + block, matching the INPUT-TO-MOVE FIDELITY LAW: the policy outputs the same inputs a human presses, and the game resolves them identically. This is what makes the AI feel like it "plays Tekken" rather than cheating with direct move calls.
- **Rewards:** +damage dealt, −damage taken, +round/match win bonus, small shaping for approach and successful punishes, penalty for passivity/timeout. Keep shaping minimal — fighting games are already dense-reward.
- **Curriculum (in order):** (1) vs scripted Gungaku dummy (learn to move + hit); (2) vs Yuka.js heuristic AI (learn neutral); (3) self-play vs past checkpoints (learn adaptation — the Fire Pro "AI logic programming" dream, learned instead of hand-written); (4) per-character policies fine-tuned from a generalist.
- **Algorithm:** PPO first (stable on discrete actions, best-understood). rl-baselines3-zoo hyperparams as the starting point. SBX (Jax) if training throughput becomes the bottleneck.
- **Deployment:** ONNX export → **onnxruntime-web**, quantized small MLP policy. Runs on the user's phone CPU, offline. Difficulty = which checkpoint you load + reaction-delay injection (a superhuman-frame-perfect policy is *boring*; Tekken-feel needs human-like reaction windows).

### 4.4 Prerequisites and sequencing (read before scheduling anything)

1. **The combat sim must be deterministic and headless first.** Fixed timestep, seeded RNG, no rendering dependency in the sim loop. This is the real blocker and the real work — everything else is configuration.
2. **Input-to-move fidelity law comes first.** RL trained on random-feeling input mappings learns garbage. The moveset rebuild (user's feel principle, 2026-10-22) is a prerequisite, not a parallel track.
3. **Start with ONE matchup** (e.g. Pantera vs Pantera mirror) before the roster. A generalist policy is a Phase-3 problem.
4. **No implementation in this round.** Next concrete step when scheduled: spike the headless sim extraction and a `WHEnv` skeleton that can `reset()`/`step()` against the Gungaku dummy — no training yet.

### 4.5 Honest effort note

This is a multi-week project *after* the sim prerequisites land, not a weekend script. The godot-rl-agents pattern de-risks the architecture (it's proven), but the WH-specific work is all in sim determinism and reward/curriculum design. Do not start it until §4.4 items 1–2 are done.

---

## 5. Transferable techniques from Godot / GDevelop / Panda3D (no engine switch)

### 5.1 Godot — 3 techniques

1. **AnimationTree combat discipline.** Godot's `AnimationTree` composes `AnimationNodeStateMachine` + `BlendSpace2D` + `OneShot` nodes. The transferable lesson (from Godot action-combat practice): **separate the locomotion blend tree from the attack montage states, use hard transitions for full-body attacks, and keep a dedicated hit-stun branch** that can interrupt locomotion but never silently cancel committed states. This maps directly onto our animation state-machine work — and it is the same *separation* idea as the user's SHOW-ANIMATION LOCK (show moves vs fight moves are separate locked sets; the anim graph should enforce that structurally, not by convention). Sources: https://docs.godotengine.org/en/3.1/tutorials/animation/animation_tree.html · https://gamineai.com/blog/godot-4-action-combat-vertical-slice-animationtree-input-discipline-small-teams-2026
2. **The godot-rl-agents socket bridge** — covered in §4.2; it *is* the Godot technique we're stealing for SB3.
3. **Importer-preset pipeline discipline.** Godot routes every asset through a typed import preset (settings travel with the asset, re-imports are deterministic). Our equivalent: the Tripo/SmutBase intake convention (`roster/<char>/attires/attire<N>/source/` + immutable originals) should grow the same property — a per-character **intake preset** (rig donor, scale, facing, poly budget) stored next to the source, so re-intakes are one command, not archaeology.

### 5.2 GDevelop — 3 techniques

1. **Behaviors as attachable components (composition over inheritance).** GDevelop's 130+ "behaviors" are plug-and-play logic modules attached to objects (physics, pathfinding, tweening…), and custom behaviors can be authored in the event system and shared as extensions. This is the architectural shape our **creation suite** should copy per the TOOL-TO-MENU WIRING and TOOL UNIFICATION laws: each pipeline tool (body/Bod systems, rigging/GameRig/NaughTyRig, skin/Fluid Painter, import, export) exposed as an attachable, composable module in the suite's menus — one unified creation flow, not disconnected scripts. Sources: https://en.wikipedia.org/wiki/GDevelop · https://wiki.gdevelop.io/gdevelop5/behaviors/events-based-behaviors/
2. **Event sheets (If/Then) as a designer layer over code.** GDevelop logic is conditions + actions readable by non-programmers, with a JavaScript escape hatch underneath. Transferable: a no-code tuning layer over our Yuka.js AI (and later over BT JSON) so the user can do his surgical tuning — reaction windows, aggression, combo tendencies — without touching code. This serves the division of labor directly: user does the feel-tuning, crew owns the systems.
3. **Extensions marketplace pattern.** GDevelop extensions (custom behaviors/functions/objects) are shared community-wide from inside the IDE. Long-term, this is the shape of the **Fire Pro community-creation pull**: shareable AI-logic / moveset / wrestler-definition packs with one-click install. Don't build it now; keep the data formats shareable-shaped so it stays possible.

### 5.3 Panda3D — 3 techniques

1. **PandAI steering + navmesh A\* as validation of our Yuka.js approach.** Panda3D ships `panda3d.ai`: steering behaviors (seek/flee/pursue/wander/flock) plus A\* pathfinding over a generated navigation mesh with static/dynamic obstacles. It is the *same algorithm family* Yuka.js implements. Takeaway: our Yuka.js choice is the mainstream one — when we need a reference implementation detail (e.g. obstacle-avoidance tuning), Panda3D's manual and source are a second opinion written against the same math. Source: https://docs.panda3d.org/1.10/python/programming/pandai/pathfinding/index
2. **ClassicFSM enter/exit naming.** Panda3D's FSM convention (`enterWalk`/`exitWalk` paired with the state name) is worth adopting verbatim in our AI code — it makes state-transition bugs (like the side-switch/facing bugs the user reported) greppable and reviewable. Yuka's `State` already has the same lifecycle (`enter`/`execute`/`exit`); we just standardize the naming.
3. **taskMgr frame-task scheduling.** Panda3D schedules work as named tasks on a task manager — the transferable idea is **AI tick budgeting**: not every agent needs a full AI update every frame. Gungaku dummies, background characters, and Heart-and-Mind-Within NPCs can tick at staggered rates. On a phone CPU, this is a real performance lever; design the AI update loop with tick-LOD from the start.

---

## 6. Sources

- behaviac repo + README: https://github.com/Tencent/behaviac
- Yuka.js: https://mugen87.github.io/yuka/ · deep dives: https://deepwiki.com/Mugen87/yuka/4.1-steering-behaviors · https://deepwiki.com/Mugen87/yuka/4.2-finite-state-machines · https://deepwiki.com/Mugen87/yuka/4.3-goal-driven-ai
- TripoSR paper: https://arxiv.org/html/2403.02151v1 · code: https://github.com/VAST-AI-Research/TripoSR · weights: `stabilityai/TripoSR` (Hugging Face)
- DreamGaussian paper: https://arxiv.org/pdf/2309.16653 · overview: https://deepwiki.com/dreamgaussian/dreamgaussian
- fal.ai TripoSR schema: https://www.toolify.ai/ai-model/triposr (mirror of fal.ai model docs)
- Tripo ecosystem (TripoSplat / TripoSG / v3.x API notes): https://radiancefields.com/platforms/tripo-ai
- Stable-Baselines3: https://pypi.org/project/stable-baselines3/ · repo: https://github.com/DLR-RM/stable-baselines3 · docs: https://stable-baselines3.readthedocs.io/en/master/
- godot-rl-agents: https://deepwiki.com/edbeeching/godot_rl_agents · protocol: https://deepwiki.com/edbeeching/godot_rl_agents/2.2-communication-protocol · training: https://deepwiki.com/edbeeching/godot_rl_agents/5-training-with-rl-frameworks
- Godot AnimationTree: https://docs.godotengine.org/en/3.1/tutorials/animation/animation_tree.html
- GDevelop: https://en.wikipedia.org/wiki/GDevelop · https://gdevelop.io/game-makers · custom behaviors: https://wiki.gdevelop.io/gdevelop5/behaviors/events-based-behaviors/
- Panda3D PandAI pathfinding: https://docs.panda3d.org/1.10/python/programming/pandai/pathfinding/index
- Prior repo research this extends: `docs/research/3d-generation-pipeline-2026-10-22.md`, `docs/research/OPEN-SOURCE-WAVE-2026-10-22.md`
