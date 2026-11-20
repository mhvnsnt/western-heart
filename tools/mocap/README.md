# WH Mocap Pipeline — video in, game animation bank out

AI-animation track (Track 6), 2026-10-23. The game needs motion data: movesets
are being pulled from teardowns but motion is the gap. This pipeline generates
NEW animations from reference footage (martial arts, wrestling, choreography)
with no mocap studio.

## Pipeline map

```
reference video (mp4)
   │  [WIRED · CPU]  video_to_keypoints.py  (MediaPipe BlazePose, 33 landmarks)
   ▼
wh-keypoints/1 JSON          (canonical schema; backend-agnostic)
   │  [WIRED · CPU]  keypoints_to_bvh.py     (heuristic v1: swing-only, no twist)
   ▼
BVH  (22 WH-canonical bones, faces +Z, ZXY euler)
   │  [WIRED · CPU]  bvh_to_wh_anim.py       (BVH -> wh-anim/1 + skeleton + sets)
   ▼
game/assets/anim/gen/<fighter>/
     <clip>.json      wh-anim/1  (what game/js/t3anims.js jsonToClip() reads)
     skeleton.json   wh-anim-skel/1
     sets.json       wh-anim-sets/1  (FIGHT/SHOW tags for the anim-gate)
   │  [WIRED · CPU]  gate_check.py           (offline anim-gate conformance)
   ▼
game loader: jsonToClip -> retargetT3Clips -> markShowClip (per sets.json)
```

Status marks used everywhere: **[WIRED]** = implemented + tested on this VM ·
**[RESEARCHED]** = evaluated, not implemented · **[NEEDS GPU]** = cannot run here.

## Quick start (CPU)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r tools/mocap/requirements.txt   # mediapipe, numpy, opencv (CPU)

# 1. video -> keypoints
python3 tools/mocap/video_to_keypoints.py refs/law_jab.mp4 /tmp/law_jab.kp.json --stride 1

# 2. keypoints -> BVH
python3 tools/mocap/keypoints_to_bvh.py /tmp/law_jab.kp.json /tmp/law_jab.bvh

# 3. BVH -> game bank (fight clip)
python3 tools/mocap/bvh_to_wh_anim.py /tmp/law_jab.bvh \
    --fighter law --clip mocap_jab_01 --out-root game/assets/anim \
    --set fight --slot light --source-video refs/law_jab.mp4

# 3b. a SHOW clip (taunt for intros/cutscenes -- NEVER fights)
python3 tools/mocap/bvh_to_wh_anim.py /tmp/law_taunt.bvh \
    --fighter law --clip mocap_taunt_01 --out-root game/assets/anim \
    --set show --show-slot taunt --source-video refs/law_taunt.mp4

# 4. offline gate conformance (CI)
python3 tools/mocap/gate_check.py game/assets/anim/gen/law

# run the synthetic end-to-end test (no video needed)
python3 tools/mocap/tests/test_pipeline.py
```

## Stage details

### Stage 1 — video_to_keypoints.py [WIRED · CPU]
MediaPipe Pose (33 landmarks) per frame -> `wh-keypoints/1` JSON. Frames with
no detection are kept as `detected:false` and interpolated downstream. Output
coords: x/y normalized 0..1 (y DOWN), z = MediaPipe relative depth. If no
person is detected in ANY frame the script warns and stage 2 refuses to run.

GPU alternative [NEEDS GPU]: **DWPose** (IDEA-Research) — the exact
`yolox_l.onnx` + `dw-ll_ucoco_384.onnx` pair that MimicMotion and UniAnimate
both use for pose guidance. It writes the same `wh-keypoints/1` schema (whole-
body 133 points; the canonical subset is used), so stages 2-4 don't care which
backend produced the keypoints. Setup on the GPU machine:

```bash
conda create -n wh-mocap python=3.10 && conda activate wh-mocap
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install onnxruntime-gpu==1.13.1 opencv-python-headless numpy
mkdir -p models/DWPose
wget https://huggingface.co/yzd-v/DWPose/resolve/main/yolox_l.onnx -O models/DWPose/yolox_l.onnx
wget https://huggingface.co/yzd-v/DWPose/resolve/main/dw-ll_ucoco_384.onnx -O models/DWPose/dw-ll_ucoco_384.onnx
# then run DWPose per frame and dump wh-keypoints/1 (script: stage1_dwpose.py -- TODO)
```

### Stage 2 — keypoints_to_bvh.py [WIRED · CPU]
Heuristic converter, v1. Per-frame joint positions -> metric Y-up space
(torso normalized to 0.50 m) -> bone world orientations from geometry
(pelvis/torso frame + shortest-arc limb swings) -> parent-relative local
quats -> ZXY euler BVH with the 22 WH-canonical bone names. Faces +Z,
character left = +X (same declaration as the T3 banks).

Known limits (documented, not hidden): no twist estimation, rigid torso/head
in v1, no foot-contact enforcement (expect mild foot slide), single performer.
The quality upgrade path is 3D lifting on the GPU machine [NEEDS GPU]:
**MotionBERT** (MIT) / **WHAM** / **HybrIK** -> SMPL parameters -> BVH export,
then feed that BVH into stage 3. Also evaluated: **MotionBridge** (MIT,
2026-10-19, browser+MediaPipe -> BVH/GLB export) as a no-install alternative
for quick takes.

### Stage 3 — bvh_to_wh_anim.py [WIRED · CPU]
Parses any standard BVH (`--bone-map` remaps foreign rigs, e.g. Mixamo names,
to the canonical 22) and writes the bank layout the game reads:

- `<clip>.json` — `wh-anim/1`: `bones` (canonical 22), `rot_xyzw` quats per
  bone per frame, `root_t` meters per frame, fps, provenance (`hand_keyed:
  false`, tool chain, sha256 of source video/BVH).
- `skeleton.json` — `wh-anim-skel/1` rest pose (written once per fighter).
- `sets.json` — `wh-anim-sets/1`, MERGED (never clobbers other clips):
  per-clip `set: fight|show`, `contexts`, `slot`/`showSlot`, provenance.

Because clips use the same 22 bone names and the same facing declaration as
the T3 banks, they flow through the existing `retargetT3Clips()` onto any
fighter rig — no game-code changes needed to play them. The loader side reads
`sets.json` and calls `markShowClip()` for `show` clips (wiring note in
`docs/research/ANIMATION-AI-2026-10-23.md`). Verified against the real
`game/js/anim-gate.js`: show clips are rejected in FIGHT; new show slots must
also be allowlisted in `game/data/crossover.json` → `show_to_fight.clips`
(owner-governed) before playing in INTRO_OUTRO/CUTSCENE/SHOW.

`--flip-180` turns a -Z-facing BVH into the +Z convention (same math the game
uses for turned banks: negate x/z, conjugate quats, swap L/R names).

### Stage 4 — gate_check.py [WIRED · CPU]
Offline twin of `game/js/anim-gate.js` + `bankFacing()`. Fails CI if: a `show`
clip lists FIGHT in contexts (**the show-animation lock**), clip files are
missing/malformed, quats aren't unit, frame counts disagree, or the bank
faces -Z (warns; fix with `--flip-180`). Pure stdlib+numpy — no browser needed.

## MimicMotion / UniAnimate — where they actually fit [RESEARCHED · NEEDS GPU]

Correction to the original brief: **neither model outputs skeletons or BVH.**
Both are pose-guided VIDEO generators (reference image + driving pose sequence
-> video). Their role in our pipeline:

1. **DWPose reuse** — both repos ship the DWPose pose-extraction preprocessing
   (`yolox_l` + `dw-ll_ucoco_384` ONNX). That IS our stage-1 GPU backend.
2. **Reference-footage synthesis** — when real footage is unusable (bad angle,
   occlusion, no performer), drive MimicMotion/UniAnimate with a fighter render
   + a driving pose sequence to synthesize clean front-view reference footage,
   then run it through stages 1-4. Also useful for previz before committing to
   a real shoot.
3. **NOT a motion source** — generated video has no ground-truth 3D; it still
   goes through pose estimation like any footage.

GPU requirements (verified from repos, 2026-10-23):
- MimicMotion (Tencent): 8 GB VRAM min (16-frame UNet); 16 GB for the 72-frame
  model (~20 min on a 4090 for the 35 s demo). License: custom (GitHub
  NOASSERTION — not a standard OSI license).
- UniAnimate (Alibaba): ~12 GB VRAM @ 768x512x32f; ~21 GB @ 1216x768x32f.
  License: RESEARCH/NON-COMMERCIAL ONLY (repo disclaimer).
- UniAnimate-DiT (Wan2.1 14B): 23 GB @ 480p, 36 GB @ 720p.

GPU-machine setup (exact):
```bash
# MimicMotion
git clone https://github.com/Tencent/MimicMotion && cd MimicMotion
conda env create -f environment.yaml && conda activate mimicmotion
mkdir -p models/DWPose
wget https://huggingface.co/yzd-v/DWPose/resolve/main/yolox_l.onnx -O models/DWPose/yolox_l.onnx
wget https://huggingface.co/yzd-v/DWPose/resolve/main/dw-ll_ucoco_384.onnx -O models/DWPose/dw-ll_ucoco_384.onnx
wget -P models/ https://huggingface.co/tencent/MimicMotion/resolve/main/MimicMotion_1-1.pth
# SVD-XT-1.1 downloads automatically on first run
python inference.py --inference_config configs/test.yaml

# UniAnimate
git clone https://github.com/ali-vilab/UniAnimate && cd UniAnimate
conda create -n UniAnimate python=3.9 && conda activate UniAnimate
conda install pytorch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 pytorch-cuda=11.8 -c pytorch -c nvidia
pip install -r requirements.txt
pip install modelscope
# checkpoints: modelscope snapshot_download('iic/unianimate') -> checkpoints/
pip install onnxruntime-gpu==1.13.1   # pose alignment step
python run_align_pose.py --ref_name <fighter_render.png> \
    --source_video_paths <driving.mp4> --saved_pose_dir data/saved_pose/<name>
python inference.py --cfg configs/UniAnimate_infer.yaml
```

## Cascadeur workflow [RESEARCHED] (proprietary — NOT vendored, tool only)

Cascadeur (Nekki, cascadeur.com) is physics-based keyframe animation:
AutoPosing (ML-assisted posing), inbetweening, **AutoPhysics** (gravity /
inertia / momentum enforced on interpolation), ragdoll, secondary motion,
animation unbaking (baked mocap -> editable keys), copy/paste retargeting.

**Free-tier verdict: NOT pipeline-usable.** The free edition saves ONLY the
proprietary `.casc` format and is non-commercial — data cannot leave the app.
Minimum viable tier is **Indie ($96/yr, rent-to-own perpetual after 12 mo)**,
which unlocks FBX/DAE/USD export. **Pro ($396/yr)** adds the copy/paste
retargeting and environment interaction. So the crew uses Cascadeur as a
desktop TOOL (never in the repo, never in the game):

```
T7 skeleton / our mocap BVH / teardown FBX
   │  import FBX/DAE into Cascadeur (Indie+)
   │  generate AutoPosing rig (both rigs, T- or A-pose, for retargeting)
   │  keyframe / import mocap -> Animation Unbaking -> editable keys
   │  AutoPhysics pass: gravity/inertia/momentum cleanup, secondary motion
   │  Edit -> Retargeting copy/paste (PRO) onto the WH fighter rig
   ▼  export FBX (Indie+)
Blender: FBX -> WH rig -> bake -> tools/mocap/bvh_to_wh_anim.py --bone-map
   ▼
game/assets/anim/gen/<fighter>/ + gate_check.py
```

Cascadeur has a Python 3.8 scripting API (`csc` module) for batching the
import/physics/export steps; the app itself is GUI-driven (Windows 10+,
Ubuntu 20.04+, macOS ARM). It cannot run on this VM's pipeline unattended —
a crew workstation runs it, the repo only ever sees the exported FBX/BVH.

### Open alternatives (evaluated; license firewall is OFF per owner 2026-10-23)

| Tool | What it replaces | License | Status |
|---|---|---|---|
| Blender Rigid Body World + bake-to-keyframes | AutoPhysics (full-body) | GPL (Blender) | [RESEARCHED] built-in, no addon needed |
| JiggleArmature (cheece/JiggleArmature) | secondary motion (hair, tails, jiggle sets) | MIT | [RESEARCHED] position-based dynamics, bake button |
| Wiggle 2 (shteeve3d/blender-wiggle-2) | spring-bone secondary motion | open source | [RESEARCHED] spring-mass model |
| Animatica Choreographer | AI motion GENERATION in Blender | GPL (free) | [RESEARCHED] generates motion takes on the rig |
| DeepMimic (Berkeley) | physics-based tracking of mocap | BSD | [RESEARCHED] research code, Bullet-based |
| MotionBridge (2026-10-19) | video -> BVH, no-install | MIT | [RESEARCHED] browser + MediaPipe, BVH/GLB export |

Recommended crew stack (no Cascadeur license): Blender rigid-body/AutoPhysics-
equivalent passes + JiggleArmature for secondary motion + Animatica
Choreographer for AI-generated takes, with our `bvh_to_wh_anim.py` as the
Blender->game bridge (`--bone-map` for whatever the addon exports).

## Licenses (transparency; firewall OFF per owner override 2026-10-23)

- tools/mocap/*.py (this pipeline): new crew code, same terms as the repo.
- mediapipe / opencv-python-headless: Apache 2.0. numpy: BSD.
- Blender addons (JiggleArmature MIT; Wiggle 2 open; Animatica Choreographer
  GPL): live in tools/, never in game/. GPL noted, not blocking.
- MimicMotion: custom Tencent license (GitHub NOASSERTION). UniAnimate:
  RESEARCH/NON-COMMERCIAL ONLY. Both are GPU-machine tools, not vendored.
- Cascadeur: proprietary; not vendored, not downloaded; crew tool only.
- Generated clips carry provenance (`hand_keyed:false`, source video sha256)
  so AI motion is always distinguishable from teardown data in the banks.
