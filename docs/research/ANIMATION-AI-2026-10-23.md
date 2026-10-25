# AI Animation Track — research + integration report

**Date:** 2026-10-23
**Track:** 6 (Animation AI), advanced-systems integration
**Owner instruction (verbatim):** "Pull all of this stuff in and wire it up and put it to work the best way possible"
**License note:** per owner override 2026-10-23 the license firewall is OFF — everything below was pulled/evaluated regardless of license; copyleft/proprietary components are documented transparently in §7. Nothing in this track puts license-encumbered code in `game/`.

**Status marks:** [WIRED] = implemented and tested on this VM · [RESEARCHED] = evaluated, not implemented · [NEEDS GPU] = cannot run on this VM (no GPU)

---

## 0. Executive summary

| Item | Verdict |
|---|---|
| Video -> keypoints -> BVH -> game bank pipeline (`tools/mocap/`) | [WIRED] CPU-tested end to end (synthetic data); stage 1 smoke-tested on real extractor |
| Cascadeur | [RESEARCHED] proprietary, cannot be vendored. **Free tier is NOT pipeline-usable** (`.casc`-only export, non-commercial). Workflow documented for Indie ($96/yr, min viable) / Pro ($396/yr, retargeting). Crew tool only, never in repo. |
| Open physics-animation alternatives | [RESEARCHED] Blender rigid-body + JiggleArmature (MIT) + Animatica Choreographer (GPL, free, AI motion generation) recommended as the no-license-cost stack |
| MimicMotion / UniAnimate | [RESEARCHED] [NEEDS GPU]. **Correction: neither outputs skeletons or BVH** — both are pose-guided VIDEO generators (image + pose sequence -> video). Their DWPose preprocessing IS our stage-1 GPU backend; the generators synthesize clean reference footage. Exact GPU setup documented. |
| Output wiring (BVH -> `game/assets/anim/` bank) | [WIRED] `bvh_to_wh_anim.py` emits `wh-anim/1` clips + `wh-anim-skel/1` + new `wh-anim-sets/1` (FIGHT/SHOW tags); `gate_check.py` enforces the show-animation lock offline |
| 3D lifting upgrade (MotionBERT/WHAM) | [RESEARCHED] [NEEDS GPU] — the quality path over the heuristic v1 converter |

---

## 1. Cascadeur — evaluation and workflow (proprietary, NOT vendored)

**What it is:** Nekki's physics-based keyframe animation tool (cascadeur.com).
AutoPosing (ML-assisted posing), AI inbetweening, **AutoPhysics** (gravity /
inertia / momentum enforced across interpolation), ragdoll, secondary motion,
animation unbaking (baked mocap -> editable keyframes), copy/paste retargeting
between different humanoid rigs, video-mocap toolset, Python 3.8 scripting API
(`csc` module). Platforms: Windows 10+, Ubuntu 20.04+, macOS 13.3+ (ARM only).
Current: 2025.2 (2026.1 adds a diffusion-based Root Motion style-transfer tool).

**Pricing (verified 2026-10-23):**
- Free ($0): full toolset, non-commercial, saves **only `.casc`** (proprietary).
- Indie ($96/yr or $12/mo, rent-to-own perpetual after 12 mo): adds FBX/DAE/USD export, commercial use (<$100k revenue).
- Pro ($396/yr or $49/mo): adds copy/paste **retargeting**, environment interaction, scene linking.
- Retargeting hard requirements (per Cascadeur docs): BOTH rigs must have an AutoPosing rig generated, rigged in vertically-symmetrical T- or A-pose, not in an animated pose.

**Free-tier verdict for the pipeline: NO.** The free edition cannot export to any
game-usable format — data cannot leave the app. Minimum viable tier is **Indie**
(FBX export). Retargeting needs **Pro**.

**Crew workflow (tool only — Cascadeur never enters the repo or the game):**

```
T7 skeleton FBX / our mocap BVH / teardown FBX
  │ 1. Import FBX/DAE into Cascadeur (Indie+)
  │ 2. Generate AutoPosing rig on source AND target (T-/A-pose)
  │ 3. Import mocap -> Animation Unbaking -> editable keyframes
  │    (or hand-key with AutoPosing + inbetweening)
  │ 4. AutoPhysics pass: physical plausibility, secondary motion,
  │    collision-penetration cleanup, fulcrum/ground contacts
  │ 5. Edit -> Retargeting copy / Retargeting paste (PRO) onto WH fighter rig
  │ 6. Export FBX (Indie+) — csc Python API can batch steps 1,4,6
  ▼
Blender (crew workstation): FBX -> WH rig -> bake
  ▼
tools/mocap/bvh_to_wh_anim.py --bone-map <names>.json   [WIRED]
  ▼
game/assets/anim/gen/<fighter>/{clip,skeleton,sets}.json -> gate_check.py
```

Cascadeur is GUI-driven; it cannot run unattended on this VM. A crew
workstation runs it; the repo only ever sees exported FBX/BVH.

## 2. Open alternatives to Cascadeur (evaluated)

| Tool | Replaces | License | Notes |
|---|---|---|---|
| Blender Rigid Body World + bake to keyframes | AutoPhysics (full body) | GPL (Blender itself) | Built in. Rigid-body sim on proxy bones -> bake. The crew already runs Blender 4.0.2. |
| JiggleArmature (cheece/JiggleArmature) | secondary motion | MIT | Position-based-dynamics jiggle bones, per-armature sim, bake button. Direct fit for hair/tails/jiggle sets. |
| Wiggle 2 (shteeve3d/blender-wiggle-2) | spring-bone secondary motion | open source | Spring-mass bone model, stiffness/damping per bone. |
| Quick Bone Phys (2026-09, Blender 5.0+) | bone physics w/ collisions | unknown (new) | Bone-to-bone + mesh collisions, bake. Watch; too new to depend on. |
| Animatica Choreographer | AI motion GENERATION | GPL, free | Generates motion takes directly on the rig in Blender; pairs with Marionette ($59) for pose editing. The closest open equivalent to "AI makes the animation". |
| DeepMimic (Berkeley) | physics-based mocap tracking | BSD | Bullet-based; research code, needs integration work. |
| MotionBridge (2026-10-19) | video -> BVH, zero install | MIT | Browser + MediaPipe -> automatic bone mapping -> BVH/GLB export. Fresh; good for quick takes. |

**Recommended no-cost stack:** Blender rigid-body passes + JiggleArmature for
secondary motion + Animatica Choreographer for AI-generated takes, with
`bvh_to_wh_anim.py --bone-map` as the Blender->game bridge. All live in
`tools/` (never `game/`); GPL components noted in §7, not blocking per the
owner's override.

## 3. MimicMotion / UniAnimate — corrected evaluation

**Important correction to the brief:** neither model does video -> skeleton.
Both are **pose-guided video generators**: reference image + driving pose
sequence -> output VIDEO. There is no skeleton/BVH output head. What they DO
give the pipeline:

1. **DWPose preprocessing (the reusable part).** Both repos extract the driving
   pose with the same DWPose ONNX pair (`yolox_l.onnx` + `dw-ll_ucoco_384.onnx`,
   via `run_align_pose.py` in UniAnimate). That is a production-grade
   whole-body keypoint extractor and becomes our **stage-1 GPU backend**,
   writing the same `wh-keypoints/1` schema as the CPU MediaPipe stage.
2. **Reference-footage synthesis.** When real footage is unusable (bad angle,
   occlusion, no performer available), drive the generator with a fighter
   render + driving pose to synthesize clean front-view footage, then run it
   through stages 1-4 like any footage. Also useful for previz.
3. Generated video is NOT ground-truth 3D — it still goes through pose
   estimation. It never bypasses stages 1-4.

**Verified specs:**

| Model | Org | Input -> Output | VRAM | License |
|---|---|---|---|---|
| MimicMotion | Tencent (ICML 2025) | image + DWPose sequence -> video (up to 72f, 576x1024) | 8 GB min (16f UNet); 16 GB for 72f model (~20 min on 4090 for 35 s demo; VAE can run on CPU) | Custom (GitHub NOASSERTION — not OSI) |
| UniAnimate | Alibaba (HUST) | image + aligned pose seq -> video (32f 768x512; long-video mode) | ~12 GB @ 768x512x32f; ~21 GB @ 1216x768x32f | RESEARCH/NON-COMMERCIAL ONLY (repo disclaimer) |
| UniAnimate-DiT | Alibaba (Wan2.1 14B) | same, DiT-based | 23 GB @ 480p; 36 GB @ 720p | same as UniAnimate |

**Exact GPU-machine setup** (also in `tools/mocap/README.md`):

```bash
# --- MimicMotion ---
git clone https://github.com/Tencent/MimicMotion && cd MimicMotion
conda env create -f environment.yaml && conda activate mimicmotion
mkdir -p models/DWPose
wget https://huggingface.co/yzd-v/DWPose/resolve/main/yolox_l.onnx -O models/DWPose/yolox_l.onnx
wget https://huggingface.co/yzd-v/DWPose/resolve/main/dw-ll_ucoco_384.onnx -O models/DWPose/dw-ll_ucoco_384.onnx
wget -P models/ https://huggingface.co/tencent/MimicMotion/resolve/main/MimicMotion_1-1.pth
python inference.py --inference_config configs/test.yaml   # SVD-XT-1.1 auto-downloads

# --- UniAnimate ---
git clone https://github.com/ali-vilab/UniAnimate && cd UniAnimate
conda create -n UniAnimate python=3.9 && conda activate UniAnimate
conda install pytorch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 pytorch-cuda=11.8 -c pytorch -c nvidia
pip install -r requirements.txt && pip install modelscope
python -c "from modelscope.hub.snapshot_download import snapshot_download; snapshot_download('iic/unianimate', cache_dir='checkpoints/')"
pip install onnxruntime-gpu==1.13.1
python run_align_pose.py --ref_name <fighter_render.png> --source_video_paths <driving.mp4> --saved_pose_dir data/saved_pose/<name>
python inference.py --cfg configs/UniAnimate_infer.yaml
```

**Quality upgrade path [NEEDS GPU]:** 3D lifting — **MotionBERT** (MIT) /
**WHAM** / **HybrIK** estimate SMPL parameters from video, export BVH, feed
into stage 3 (`bvh_to_wh_anim.py --bone-map`). This replaces the heuristic v1
converter's swing-only rotations with true 3D pose including twist.

## 4. The wired pipeline — `tools/mocap/` [WIRED]

Four scripts, CPU-only, tested 2026-10-23 (see §6):

1. **`video_to_keypoints.py`** — video -> `wh-keypoints/1` JSON (MediaPipe
   BlazePose, 33 landmarks; undetected frames kept as `detected:false`).
2. **`keypoints_to_bvh.py`** — keypoints -> BVH (22 WH-canonical bones, faces
   +Z / left = +X, ZXY euler). Heuristic v1: metric normalization, missing-
   frame interpolation, smoothing, pelvis/torso frames + shortest-arc limb
   swings (no twist — documented).
3. **`bvh_to_wh_anim.py`** — BVH -> `game/assets/anim/gen/<fighter>/`:
   `<clip>.json` (`wh-anim/1`), `skeleton.json` (`wh-anim-skel/1`, once per
   fighter), `sets.json` (`wh-anim-sets/1`, merged). `--bone-map` adapts
   foreign BVHs (Mixamo etc.); `--flip-180` fixes -Z-facing sources.
4. **`gate_check.py`** — offline twin of `game/js/anim-gate.js` + `bankFacing()`;
   fails CI on lock violations, malformed clips, non-unit quats, or -Z facing.

Test: `python3 tools/mocap/tests/test_pipeline.py` (stdlib + numpy only).

## 5. Output-side wiring — how generated BVH becomes game animation

The game reads `wh-anim/1` clips via `jsonToClip()` (`game/js/t3anims.js`):
`bones` (22 names), `rot_xyzw` (per-bone per-frame quaternions `[x,y,z,w]`),
`root_t` (per-frame meters; kept for `lateralDx`, in-fight positioning is
game-driven — same as T3 banks), `fps`, `stream_frames`, `hand_keyed:false`
provenance. Clips then flow through the existing **`retargetT3Clips()`** onto
any fighter rig — generated banks reuse the T3 banks' bone names, facing
declaration (`faces +Z, character left = +X`), and `skeleton.json`
(`wh-anim-skel/1`: joints with `name`/`parent`/`rest`, `root_rest_y`,
`foot_tip`) so **no game-code changes are needed to play them**.

**New: `sets.json` (`wh-anim-sets/1`)** — per-fighter clip registry written by
stage 3, enforcing the SHOW-ANIMATION LOCK (owner law 2026-10-23):

```json
{
  "format": "wh-anim-sets/1", "fighter": "law", "bank": "gen/mocap/law",
  "clips": {
    "mocap_jab_01":   { "file": "mocap_jab_01.json",   "set": "fight",
                         "contexts": ["FIGHT"], "slot": "light", ... },
    "mocap_taunt_01": { "file": "mocap_taunt_01.json", "set": "show",
                         "contexts": ["INTRO_OUTRO","CUTSCENE","SHOW"],
                         "showSlot": "taunt", ... }
  }
}
```

Loader integration (for the gameplay track; documented here, not implemented
in this PR): the bank loader reads `sets.json`, builds each clip with the
existing `jsonToClip()`, and calls the existing `markShowClip(clip, showSlot)`
from `game/js/anim-gate.js` for every `set: "show"` entry. The runtime gate
already rejects show clips in FIGHT; `gate_check.py` enforces the same rule
offline (a `show` clip listing FIGHT fails CI). **A show move enters a
fighter's moveset only with the owner's explicit approval** — tagging it
`show` never promotes it.

Verified 2026-10-23 against the real `game/js/anim-gate.js` in node: a
`markShowClip`'d clip is rejected in FIGHT (`show clip in FIGHT`) and a fight
clip passes (`moveset clip`). Note: new show slots (e.g. `taunt`) ALSO need to
be added to `game/data/crossover.json` → `show_to_fight.clips` before they
play in INTRO_OUTRO/CUTSCENE/SHOW — that allowlist is owner-governed
(`show_to_fight` may never contain FIGHT; promoting a show clip to FIGHT
requires an owner-approved moveset PR).

Generated banks live under `game/assets/anim/gen/<fighter>/`, parallel to
`game/assets/anim/t3/` — teardown data and AI motion never mix in one dir,
and every clip carries `hand_keyed:false` + source-video sha256 so AI motion
is always distinguishable from teardown banks.

## 6. Test report (this VM, no GPU)

- `tools/mocap/tests/test_pipeline.py` — **ALL PASSED** (synthetic 30-frame
  jab + 12-frame taunt, abstract stick figure, no real person):
  keypoints -> BVH (30 frames, 22 canonical bones, 1 dropped frame
  interpolated) -> `wh-anim/1` (22 bones x 30 quat frames, unit quats,
  `root_t` 30x3, `hand_keyed:false`) -> `wh-anim-skel/1` -> `wh-anim-sets/1`
  (fight + show tags) -> `gate_check.py` PASS, including the facing check
  (knees forward +Z, mean +0.002) and a negative test proving the gate
  catches a show clip tagged for FIGHT, plus `--flip-180` L/R-swap correctness.
- Stage 1 (MediaPipe) on this VM: **smoke-tested** — extractor ran on a
  synthetic video (no person): 30 frames processed, 0 detections, graceful
  warning, valid `wh-keypoints/1` schema written; stage 2 correctly refuses
  zero-detection input (`ValueError`). Real-footage extraction runs on the
  GPU machine with DWPose.
- Runtime gate cross-check: ran the real `game/js/anim-gate.js` in node —
  `markShowClip`'d clip rejected in FIGHT, fight clip allowed; confirmed new
  show slots also require `game/data/crossover.json` allowlisting (§5).

## 7. Licenses (transparency — firewall OFF per owner override 2026-10-23)

| Component | License | Where it lives |
|---|---|---|
| `tools/mocap/*.py` (this track's code) | repo terms (new crew code) | `tools/mocap/` |
| mediapipe, opencv-python-headless | Apache 2.0 | pip (tool dep) |
| numpy | BSD | pip (tool dep) |
| JiggleArmature | MIT | `tools/` (if adopted) |
| Animatica Choreographer | GPL (free) | `tools/` (if adopted) — copyleft noted, not blocking |
| Wiggle 2 | open source | `tools/` (if adopted) |
| MotionBERT | MIT | GPU machine (if adopted) |
| MimicMotion | custom Tencent (GitHub NOASSERTION) | GPU machine, not vendored |
| UniAnimate / UniAnimate-DiT | RESEARCH/NON-COMMERCIAL ONLY | GPU machine, not vendored |
| Cascadeur | proprietary | crew workstation only; never in repo |
| Generated clips | provenance-tagged (`hand_keyed:false`, source sha256) | `game/assets/anim/gen/` |

Nothing license-encumbered was placed in `game/`. The `game/assets/anim/gen/`
dir currently contains no clips (no real footage processed yet) — it is
created by stage 3 on first use.

## 8. What's next (for the crew / other tracks)

1. GPU machine: install DWPose + MotionBERT/WHAM per §3; process first real
   reference footage (martial-arts/wrestling) through stages 1-4.
2. Gameplay track: wire `sets.json` -> `markShowClip()` in the bank loader
   (§5); add `gate_check.py` to CI for `game/assets/anim/gen/**`.
3. Animation track: run stage-3 output through the Cascadeur AutoPhysics pass
   (Indie+) or Blender rigid-body cleanup before banking fight clips.
4. Foot-contact pass (foot-slide killer) as a stage-2.5 — CEB SAM-style
   contact detection or Cascadeur fulcrum groups.
5. Twist estimation (stage 2 v2) or skip straight to the SMPL lifting path.
