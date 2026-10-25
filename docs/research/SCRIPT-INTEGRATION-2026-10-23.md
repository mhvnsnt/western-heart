# SCRIPT Integration — language-to-motion for the creation suite

**Date:** 2026-10-23
**Lane:** Future Tech prototyping (research-stage)
**Owner directive (verbatim 2026-10-23):** "Pulling everything from the list and wire it all up and where it'll work and where it's appropriate"
**Status:** RESEARCH-DESIGN — no public code as of 2026-10-23 (verified: no GitHub repo found via API search, arXiv page carries no code link; the paper states "Our code will be publicly available for future research"). Nothing is vendored. The prototype in this PR is the **integration contract as code** (`tools/script-adapter/`), so the real weights plug in the day code drops.

**Paper:** SCRIPT: Scalable Diffusion Policy with Multi-stage Training for Language-driven Physics-based Humanoid Control — arXiv:2605.22894 (cs.GR), submitted 2026-05-21, v3 2026-09-04. Authors: Jingyan Zhang, Han Liang, Ruichi Zhang, Bin Li, Juze Zhang, Xin Chen, Jingya Wang, Lan Xu, Jingyi Yu. Paper header lists venue as SIGGRAPH Asia 2026 Conference Papers (Dec 1–4, 2026, Kuala Lumpur).

**What it is in one line:** type "punch like a boxer" → get physically believable humanoid motion, generated as *actions for a physics simulator* — not kinematic keyframes that foot-skate and float.

**Companion track:** `docs/research/ANIMATION-AI-2026-10-23.md` (mocap/video pipeline — real data today). SCRIPT is the *generative* counterpart: describe a move, get animation, no camera or actor needed.

---

## 0. TL;DR — the whole picture

| # | Fact | Detail |
|---|------|--------|
| 1 | Core model | JAST-DiT: Joint Action-State-Text Diffusion Transformer — separate token streams for actions, physical states, text; dense cross-modal interaction via joint attention (not text-as-coarse-condition like prior work) |
| 2 | Stability trick | Nonlinear long-term history conditioning: dense recent states + sparsely sampled distant context during autoregressive rollouts |
| 3 | Training | Stage I: supervised flow-matching imitation pre-training. Stage II: RLHR — Reinforcement Learning with Hybrid Rewards (PPO) optimizing semantic alignment + physical stability, with learnable noise injected into flow sampling |
| 4 | Data | 550K curated *physical* trajectories (~1,200 hours): HumanML3D + MotionMillion kinematic clips → artifact filtering → PHC (Luo et al. 2023) expert tracking in simulation → keep only clean rollouts |
| 5 | Scale | Base 206M / Large 578M / Huge 1.23B params; consistent gains 0.2B→1.2B on MotionMillion; SOTA on HumanML3D (text alignment, motion quality, physical realism) |
| 6 | I/O contract | Text (CLIP embeddings) + state history → H-step future state-action chunk; state s_t ∈ R^358, action a_t ∈ R^69 (PD-controller target joint angles); receding-horizon execution |
| 7 | WH fit | Creation-suite "describe-a-move": offline text→move-animation generation. NOT live combat. NOT on the phone. GPU workstation/cloud only |
| 8 | Code status | NOT released (2026-10-23). Integration contract + prompt builder + retarget interface prototyped now; weights plug in later |
| 9 | License | None stated (unreleased). Assume restrictive/research-only until published. Nothing vendored; WH-original contract code only |

---

## 1. Why SCRIPT matters for WH (and what it is NOT)

The creation suite's endgame (per CORE VISION: new-age MUGEN) is: *anyone can make or bring in any fighter*. The two hard walls today are (a) rigging (UniRig lane, MIT, in progress) and (b) **animation authoring** — making a new move currently needs mocap, video, or hand keyframes.

SCRIPT attacks (b) directly: natural-language → physically plausible motion. "Punch like a boxer" doesn't just produce a plausible-looking arm swing — it produces *joint torques/angles that a simulated humanoid can actually execute without falling over*, because the model was trained on physical state-action demonstrations and RL-fine-tuned for physical stability. That is the difference between a kinematic text-to-motion model (MDM, MotionDiffuse — offline trajectories with foot-skating artifacts the paper explicitly calls out) and SCRIPT.

**What SCRIPT is NOT for us:**
- NOT a live-combat controller. Inference is a diffusion model (hundreds of ms per chunk even distilled) and non-deterministic — combat stays on Tekken frame data, 60fps deterministic. This is an *authoring* tool.
- NOT a replacement for the mocap pipeline (`tools/mocap/`) — that pipeline produces Tekken-faithful data today; SCRIPT produces *new* moves that don't exist in any teardown.
- NOT phone-side. Ever. Offline generation on GPU iron; the game only ever sees baked `wh-anim/1` clips.

---

## 2. The exact I/O contract (this is what the game must speak)

From the paper (§3–§4), the shapes that matter for integration:

**Text conditioning:** instruction `c` encoded with the CLIP text encoder → pooled embedding `c_pool` + penultimate-layer token features `c_txt` (they deliberately use penultimate-layer features so token-level semantics survive).

**Proprioceptive state** `s_t ∈ R^358`: root height + per-joint local position, 6D rotation (Zhou et al. 2019), linear velocity, angular velocity. This is the PHC/Isaac-Gym-class SMPL humanoid state convention.

**Action** `a_t ∈ R^69`: target joint angles for a proportional-derivative (PD) controller. 69 dims = SMPL joint set.

**Inference loop (receding horizon):** at each rollout step, given text embeddings + nonlinearly-sampled state history `H_t` (dense recent buffer `B_t`, sparse distant), the policy jointly denoises an H-step future state-action chunk `[a_{t+1:t+H}; s_{t+1:t+H}]` (action/state tokens attend bidirectionally; text padding mask retained; AdaLN-Zero modulation from flow-time + pooled text; QK-Norm for stability). Execute only the first action, update history, re-plan.

**What this means for the adapter:** the retarget stage consumes *both* streams — the action stream gives PD target angles (control intent), the state stream gives the resulting joint transforms (the actual motion to bake into keyframes). Baking keyframes from the state stream avoids re-simulating; the action stream is the fallback if states are noisy.

**Model variants (paper Table 1):** SCRIPT-Base 8 layers / 512 dim / 206.31M params; SCRIPT-Large 10 / 768 / 577.97M; SCRIPT-Huge 12 / 1024 / 1231.39M. Start integration with Base (cheapest inference); scale to Huge for hero moves.

---

## 3. Where it wires in — the whole list (per the integration standard: everything, everywhere appropriate)

| Slot | Verdict | Why |
|------|---------|-----|
| Creation suite → **Describe-a-move** | ✅ FLAGSHIP | The feature: type a move description → get a physically-plausible animation → becomes a fighter's move. Directly serves new-age MUGEN ("anyone can make any fighter") |
| Creation suite → style transfer for existing moves | ✅ | "Make this jab more like a boxer's" — re-generate a teardown move with a style prompt; output reviewed like any other animation pull |
| Intros / cutscenes / win poses | ✅ | Generated motion is SHOW-set by default → tagged `"set": "SHOW"`; enters FIGHT only with explicit owner approval (SHOW-ANIMATION LOCK) |
| Heart and Mind Within (story mode) ambient motion | ✅ | NPC idle/ambient loops generated from text ("tavern brawler warming up") — cheap content at scale |
| KESSHOU / finisher prototyping | ⚠️ RESEARCH | Generated sequences can *prototype* finisher choreography for owner review, but KESSHOU is a gated canon system — nothing auto-enters it |
| CPU AI personalities | ❌ | Wrong tool — FightingICE methodology lane covers this; SCRIPT is authoring, not runtime |
| Live combat / rollback / netcode | ❌ | Non-deterministic, GPU-heavy, wrong latency class. Never |
| Tripo intake cleanup | ⚠️ MAYBE | Motion-cleanup of noisy captures is plausible later; the mocap pipeline owns this today |
| Phone / in-game runtime | ❌ | Baked clips only. No inference on device, ever |

---

## 4. Integration architecture

### 4.1 The pipeline (all offline)

```
Owner/creator types: "spinning backfist, Muay Thai style, fast"
  │
  ▼ ① PROMPT BUILDER (tools/script-adapter/prompt_builder.py — CPU, in repo)
  │   canon/style guardrails + frame-data constraints + adult-content filter
  │   → canonical SCRIPT prompt + generation job spec
  │
  ▼ ② INFERENCE SERVICE (GPU workstation / cloud — NOT in repo, NOT on VM)
  │   POST /v1/generate {prompt, style, seed, duration_s, fps, constraints}
  │   → SCRIPT weights (Base→Huge) → state-action trajectory (.npz)
  │   → GET /v1/jobs/{id} → artifact download
  │
  ▼ ③ RETARGET (tools/script-adapter/smpl_to_wh.py — CPU, in repo)
  │   SMPL 69-dim joints → WH fighter skeleton via bone-map JSON
  │   (same bone-map convention as tools/mocap/); state stream → 60fps
  │   quaternion keyframes; foot-contact cleanup; root-motion extraction
  │
  ▼ ④ FRAME-DATA ANCHORING (new; spec'd here, built in Phase 2)
  │   contact events in trajectory → startup/active/recovery split;
  │   damage assigned from archetype table — NEVER generated by the model
  │
  ▼ ⑤ BANK + GATES (existing infra)
      → wh-anim/1 clip + wh-anim-skel/1, tagged "set": "FIGHT" or "SHOW"
      → tools/mocap/gate_check.py (show-animation lock enforced offline)
      → game/assets/anim/ bank → played verification (proof-harness fight)
```

### 4.2 The inference-service API (spec — implement when weights drop)

`POST /v1/generate`
```json
{
  "prompt": "a boxer throws a fast jab-cross combination, orthodox stance",
  "style_hints": ["boxing"],
  "seed": 1337,
  "duration_s": 2.5,
  "fps": 60,
  "model": "script-base",
  "constraints": {
    "max_duration_s": 3.0,
    "require_foot_contact": true,
    "upright_bias": 0.8,
    "forbidden": ["ground", "weapons"]
  }
}
```
→ `202 Accepted` → `{"job_id": "...", "status": "queued"}`
`GET /v1/jobs/{id}` → `{"status": "done", "artifacts": {"trajectory_npz": "...", "preview_mp4": "...", "metrics": {"text_align": 0.91, "foot_skate_cm": 1.2, "falls": 0}}}`
`GET /v1/jobs/{id}/trajectory` → `.npz` with `states` (T×358), `actions` (T×69), `fps`, `joint_names`, `prompt`, `seed`, `model`.

The client (`tools/script-adapter/client.py`) implements exactly this contract against a stub server today; swap the base URL when the real service exists.

### 4.3 Prompt builder rules (canon safety)

The prompt builder is where WH's laws become code:
- **Style hints** come from the fighter's moveset source (see §8 table) — e.g. a King-based fighter gets `["lucha-libre wrestling", "chain grappling"]`, never a free-form style that breaks canon.
- **Adult filter:** prompts describing minors, sexual content, or real-person likenesses are rejected. ALL CHARACTERS ARE ADULTS — enforced at the prompt layer, not just the model layer.
- **No famous names:** "punch like Mike Tyson" → rejected/rewritten to "punch like a boxer". Game ships no famous names; the prompt layer follows the same law. (Tekken fighter names may appear in *technical* files/params per the TEKKEN-NAMES law, never in user-facing prompts.)
- **Frame-data constraints:** every generated move declares intended duration and archetype (strike/throw/stance); damage/frames are assigned by WH tables, not the model.

### 4.4 Frame-data anchoring (why generated moves are still Tekken moves)

A SCRIPT trajectory is motion, not a fighting-game move. The anchoring step converts it:
1. Detect contact events (fist/foot velocity minima + proximity) → active frames.
2. Startup = first movement → first contact; recovery = last contact → return to guard.
3. Damage/scaling from the archetype table (jab/chin-check/launcher/throw), block properties from Tekken conventions for that archetype.
4. The result is a normal WH moveset entry — indistinguishable downstream from a teardown move. It then goes through the same verification (played, not pushed).

---

## 5. What we need the day code drops (checklist)

- [ ] Weights: Base / Large / Huge checkpoints + license file (read it before any use)
- [ ] Inference script: exact entry point, env (torch/CUDA versions), CLIP checkpoint version
- [ ] Joint ordering: the 69 action dims ↔ SMPL joint names (needed for `smpl_to_wh.py` bone map)
- [ ] Frame rate of training rollouts (likely 30fps — affects keyframe resampling to WH 60fps)
- [ ] PD gains used in their simulator (only needed if we re-simulate; we bake states, so likely not)
- [ ] Prompt format examples (how they phrase instructions in training — the prompt builder should match)
- [ ] Simulator env spec (for the optional closed-loop validation pass)
- [ ] Data license note: HumanML3D/MotionMillion-derived weights — check redistribution terms for weights

---

## 6. Prototype delivered in this PR (`tools/script-adapter/`)

CPU-runnable, std-lib + numpy only, synthetic-data tests — no GPU, no weights, no faked "AI output":

| File | What it is |
|------|-----------|
| `script_contract.py` | `ScriptRequest` / `ScriptState` (358-dim) / `ScriptAction` (69-dim) / `ScriptTrajectory` dataclasses + shape/range validators. The I/O contract as code |
| `prompt_builder.py` | `build_script_prompt(move_desc, fighter_style, constraints)` → canonical prompt + job spec; `canon_filter()` rejects minors/sexual content/famous names; style-hint table keyed by moveset source |
| `smpl_to_wh.py` | `SMPL_JOINTS_69` layout doc + `load_bone_map()` (same JSON convention as `tools/mocap/`) + `trajectory_to_keyframes()` (state stream → 60fps quaternion keyframes, synthetic-data tested) |
| `client.py` | `ScriptClient` implementing the §4.2 REST contract; `StubScriptServer` for offline tests |
| `README.md` | Setup, the API spec, "when code drops" runbook |
| `tests/test_script_contract.py` | Contract validation, prompt filter cases, keyframe conversion on synthetic trajectories, client↔stub round-trip |

Run: `python3 -m pytest tools/script-adapter/tests/ -q` (or `python3 tools/script-adapter/tests/test_script_contract.py`).

**Honest boundary:** the stub server returns *synthetic* trajectories (seeded sine-based joint motion) — it proves the plumbing (contract → client → retarget → keyframes), not the AI. The AI arrives with the weights.

---

## 7. Risks and limits

1. **No code, unknown timeline.** Paper says "will be publicly available for future research" — could be months. Mitigation: the contract is built from the paper's published shapes, so integration work isn't blocked.
2. **License unknown.** Assume research-only until the release states otherwise. Weights/code stay OUT of `game/` and out of the repo until cleared; inference runs as an external service.
3. **Sim-to-game gap.** SCRIPT outputs PD *control targets* for a simulator; WH needs keyframes. We bake the predicted *state* stream (joint transforms), which is the right source — but state prediction quality at contact moments needs validation against real rollouts in Phase 1.
4. **Prompt-injection of non-canon content.** Mitigated by the prompt builder (§4.3), not by trusting the model.
5. **Non-determinism.** Seed everything; every generated move is reviewed and played before entering any bank — same bar as teardown pulls.
6. **No GPU on this VM.** All inference is cloud/workstation. The contract code and tests are CPU-only by design.
7. **Style drift across the roster.** Per-fighter style hints (§8) keep a King-based grappler from suddenly moving like a capoeira dancer unless the owner asks for it.

---

## 8. Whole-roster style-hint table (moveset source → SCRIPT style hints)

Per the integration standard (use it across the whole roster, not just one fighter) and the REPLACEMENT MAP law (unmapped fighters are flagged, never guessed):

| WH fighter | Moveset source (Tekken) | SCRIPT style hints |
|------------|------------------------|-------------------|
| Pantera | King | lucha-libre wrestling, chain grappling, powerful throws |
| Yukihyo | Armor King | wrestling, dark brawler, chain throws |
| Dio | Akuma | karate-based rushdown, fireball-stance power moves (no projectiles generated — strikes only) |
| Scimitar | Shaheen | military close-quarters, efficient strikes |
| Chordz | Lars | Tekken-force military, dynamic entry strikes |
| Mary Posa | Zafina | contortionist, evasive, unpredictable angles |
| Doc Frank | Bosconovitch | unorthodox gadget-fighter movement, comic timing |
| Phantom | Yoshimitsu | katana-stance sword movement (blades as props), spinning evasion |
| Purple Rain | Lee Chaolan | elegant kickboxing, precise straight punches |
| Saku-ra | Ling Xiaoyu | acrobatic kung fu, evasive dance-like footwork |
| Buffalo Bill | Law | Jeet-Kune-Do-inspired rapid strikes |
| Gyou | Paul Phoenix | power karate, devastating straight punches |
| Birodo | Feng Wei | internal martial arts, iron-palm strikes |
| Jotei | Craig Marduk | vale-tudo brawler, heavy grappling |
| Chatur | True Ogre | monstrous power, four-armed flow (extra limbs need custom rig — flagged) |
| Ryusan | Lucky Chloe | agile dance-fighter, acrobatic kicks |
| Pond | Raven | ninjutsu, teleport-stance movement |
| Megami | Jun Kazama | defensive karate, flowing counters |
| Menagerie | Roger Jr. | beast-mimicry boxing (kangaroo stance) |
| Tobi | Hwoarang | taekwondo kick chains, fast footwork |
| Cape Jones | Alisa | android movement, chainsaw-stance (props), detachable-limb flow |
| *(remaining roster)* | *(unmapped)* | ⚠️ FLAGGED per REPLACEMENT MAP law — no style hints assigned until the owner maps them |

Note: style hints describe *movement quality only*. Frame data, damage, and canon always come from WH systems.

---

## 9. Roadmap

- **Phase 0 (this PR):** contract code + design doc. Done.
- **Phase 1 — code drop:** pull weights on a cloud GPU box; run the 10 canonical prompts (jab, cross, roundhouse, throw, stance, sweep, uppercut, elbow, knee, taunt); validate trajectories against the contract; publish quality notes.
- **Phase 2 — retarget pilot:** `trajectory_to_keyframes` on real SCRIPT output → 1 pilot move for 1 fighter → wh-anim bank → proof-harness played verification.
- **Phase 3 — service hardening:** the §4.2 API as a real service; job queue; preview renders for owner review.
- **Phase 4 — creation-suite wiring:** spec feeds the menus lane (teardown-sourced UI); per-fighter style packs from §8.

---

## 10. License transparency

- **SCRIPT code/weights:** NOT released as of 2026-10-23. No license to evaluate. This doc assumes research-only terms until the release says otherwise. Nothing is vendored or fetched.
- **This PR's code** (`tools/script-adapter/`): WH-original, repo license. It contains no SCRIPT code, weights, or derived artifacts.
- **Related — PHC** (Luo et al. 2023, used in SCRIPT's data curation, not needed for inference): check its license at pull time if the closed-loop validation pass is ever built.
- **Related — CLIP** (Radford et al. 2021, text encoder): MIT. The prompt builder targets CLIP text embeddings; any CLIP implementation works.
- Per the sale-status rule: no commercial track until the owner declares it — but NC-licensed weights would still need clearance before shipping regardless.

---

## Sources

- Paper (arXiv abs): https://arxiv.org/abs/2605.22894
- Paper (full HTML): https://arxiv.org/html/2605.22894
- Paper (PDF): https://arxiv.org/pdf/2605.22894
- GameDev.net coverage: https://gamedev.net/news/3523-script-scalable-diffusion-policy-with-multi-stage-training-for-language-driven/
- Scout entry: `docs/research/CUTTING-EDGE-SCOUT-2026-10-23.md` §9
- Companion track: `docs/research/ANIMATION-AI-2026-10-23.md`
- Contract code: `tools/script-adapter/`
