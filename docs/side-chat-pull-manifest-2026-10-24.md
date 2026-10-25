# Side-chat work pulled into main — manifest (2026-10-24)

Rule enforced: only WORK PRODUCTS move (files, scripts, research, methods). No private
user info, no credentials, no token values are copied anywhere in this manifest or in code.

## 1. Kaggle API token → automation (WIRED AS PATTERN, token NOT in files)
- Side chat "Cape Jones 3D work" was generating a Kaggle API token (Settings > API Tokens).
- Correct handling: automation code reads the token from the Kaggle CLI config location
  (`~/.kaggle/kaggle.json`, mode 600) or env, never from chat text, never committed.
- Parent browser action still owed: place the generated token via the browser/Secure Vault
  flow into the automation host's kaggle.json, then verify with `kaggle competitions list`
  (or any read-only call) — token value is never printed, logged, or pasted.
- Once placed, main can drive Kaggle notebooks/datasets via API instead of browser-only.
- Status: PATTERN WIRED, TOKEN PLACEMENT PENDING (parent browser delegation).

## 2. Cape / Alisa rig work → UniRig pipeline (PULLED, paths recorded)
- Bone map: `~/workspace/ep1-farm/bonemap_alisa_to_capejones.json` (160/160 Alisa joints
  accounted: 111 mapped, 49 dropped facial/hair/misc) — input to UniRig/rig-fit stage.
- IK stance bake: `tools/show/bake_stance_ik.py` (direction-based two-bone IK for arms) +
  clip `ep1_cape_stance` (131,240 bytes) — method reference for arm retargeting.
- Hand-placement guard: `~/workspace/ep1-farm/ep1_cape_stance_hand.glb` (wrist error 0.0000
  both sides at bake time; hands read open + head bows — NOT accepted as final, eye-check owed).
- Weld/smoothing passes + topology audit: Cape body 1,638,010 verts, 1,045,182 non-manifold
  edges (33%) — weight smoothing alone CANNOT fix; next step is remesh to clean manifold
  ~50–100k topology with Alisa weight transfer, crotch in same pass. This is the UniRig
  pipeline's first GPU job (Kaggle job 01).
- Alisa rest pose verified symmetric; defect is in T3 stance bake, not Alisa rest pose.
- Alisa default pose (user kept, "JoJo-like" character pose) is a SHOW pose reference, NOT
  a game fighter stance — do not wire it as a fight stance.

## 3. Floor detection → game grounding (CODE WRITTEN, game PR owed)
- Requirement (side chat, user): floating character — "detect the floor like a grid sensor
  or anything else ... so you can get her feet on the [floor]".
- Wired as: `floor-detect.js` in this directory — 5-ray median grid sensor, Three.js
  Raycaster, no new dependency. Integration point: `game/js/fighter.js`, once per tick,
  AFTER root-motion, BEFORE arena clamp + pushout. On no hit, holds last good height.
- Status: MODULE WRITTEN, NOT YET MERGED — needs game PR + live playtest (Alisa/Cape feet
  on floor on Jungle Outpost + flat arena, no jitter).

## 4. 3D fighter games research → extraction targets (PULLED AS TARGET LIST)
- Source: side chat "Troubleshoot messages" (user question) + main-chat relay.
- Games to mine for Tekken-style inputs: DOA (Bass Armstrong already used — more DOA
  fighters unmined), VF5 (Dural = Zen base; full VF5 roster unmined), KOF 3D titles,
  plus whatever else is already in teardown files. Rule: moveset/animation/stance pulls
  only, renamed to WH canon, Tekken names stay in technical files only.
- Tripo asset: Theory Attire 4 — https://studio.tripo3d.ai/3d-model/30a01989-2954-4de8-a764-324f2a7a53be
  — intake needs owner confirmation of which fighter Theory maps to before archiving
  (side-chat agent flagged this; do NOT archive unmapped).
- Status: TARGET LIST PULLED; extraction itself belongs to the extraction lane (batch).

## 5. Pantera voice → already in main (NO ACTION)
- `~/workspace/king-mods/`: classic sampler, T2 grunts sampler (owner-preferred), T8 death
  scream, manifest with King attribution. Owner ear-checked 2026-10-24. Sound lock picks
  growls; Pantera does not "talk". No re-pull.

## 6. Nosferatu M4 synth score → game soundtrack lane (HANDOFF, not duplicated here)
- Correct score = 1980s VHS synth (Internet Archive Nosferatu1922VHS). 18 pieces cut,
  cue sheet in cape-jones repo PR #252. Game soundtrack + rotating stage BGM wiring is
  owned by the separate music lane (Tekken-style BGM system). This manifest does not
  duplicate audio files.

## 7. Kaggle GPU notebook → compute backend for ALL GPU jobs (WIRED)
- Notebook: https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
- Verified by parent browser task: 2x Tesla T4, 15GB each, driver 580.178.04, CUDA 13.0,
  ~30 hrs/week quota, ~29h59m remaining at check. Session left running (quota counts
  while open — close when idle).
- Job scripts in `kaggle-jobs/`: 01 UniRig, 02 Real-ESRGAN. Each job downloads ONLY
  outputs back to the repo pipeline. GPU verification per job = nvidia-smi + job output
  metrics recorded in the job's run log, not claimed from setup alone.
- SUPERSEDING FIND (2026-10-24 ~00:21–00:25, parallel lane): `~/workspace/unirig/`
  already holds the fuller GPU lane — USE THESE INSTEAD of re-writing:
  - `kaggle_unirig_notebook.py` — full Kaggle UniRig driver (paste whole file into
    one notebook cell, or `python kaggle_unirig_notebook.py --jobs cape-jones`).
    Drives REAL upstream UniRig (VAST-AI/UniRig, SIGGRAPH'25) via its documented
    `launch/inference/generate_skeleton.sh`, `generate_skin.sh`, `merge.sh`, plus
    remesh/clean, Alisa→Cape weight transfer + smoothing (only with reference rig),
    verify/render. Pipeline per job: clean → skeleton inference (GPU) → skin
    inference (GPU) → merge → weight transfer → verify/render; jobs parallel across
    GPUs via `--gpus 2`.
  - `kaggle_batch_retarget.py` — batch retarget SKELETON (honestly labeled NOT
    finished): loads/validates real T3 clip formats (`wh-anim/1`, bone lists,
    rot_xyzw quaternions) and computes the bone map, but does NOT yet write
    retargeted GLBs — target rig joint names are UniRig outputs, unknown until the
    first Kaggle run returns real joint names. Run AFTER the UniRig job, same dir.
  - `checkpoint/` and `tests/` are EMPTY placeholder dirs — checkpoint download
    still happens at Kaggle runtime (HF, per script; "No token is used" unless the
    repo is gated). No secrets found in either script (token mentions are only the
    words "tokenization" and "No token is used").
  - This manifest's `kaggle-jobs/01-unirig-setup.py` is therefore a POINTER-level
    starter; the unirig/ scripts are authoritative. Do not maintain two versions —
    point the PR payload at `~/workspace/unirig/` scripts.
