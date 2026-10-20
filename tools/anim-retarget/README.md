# tools/anim-retarget — skeletal animation pipeline for Western Heart

Production-grade animation sourcing + retargeting. The game no longer needs
to fall back to JSON movesets with T3 retarget anims only — this wires in
real skeletal animation from free/production sources.

## Why this exists

Bottleneck #2 in the 2026-10-19 roster audit: **no skeletal animation
pipeline** — movesets are JSON data, the game falls back to T3 retarget
anims. This toolset closes it:

1. **Source** — free, production-grade animation sources:
   - **Mixamo** (Adobe, free with Adobe ID): 2,000+ mocap clips + auto-rigger.
     See `workflow-mixamo.md`.
   - **Rokoko Studio / Rokoko Vision** (free Starter tier forever):
     AI video-to-motion mocap from any video or webcam, FBX/BVH export.
     See `workflow-rokoko.md`.
   - **Tripo one-click rig + animation** (2026): Tripo models can ship
     rigged + animated already.
2. **Retarget** — map source bones onto the WH 52-bone Mixamo-style skeleton
   (`tools/auto_rig/backends/skeleton_template.json`):
   - `retarget_blender.py` — headless Blender: source FBX/BVH + target rigged
     GLB -> retargeted animated GLB (offline, bakes into the asset).
   - `runtime/wh-retarget.js` — three.js runtime retarget via
     `SkeletonUtils.retargetClip()` (loads Mixamo anim GLBs at runtime).
3. **Bone maps** — `bone_maps/mixamo_to_wh.json` (identity for true Mixamo
   skeletons; prefix-stripping for `mixamo:`-prefixed FBX exports).

## Quick start

```bash
# 1. Retarget a Mixamo FBX animation onto a WH-rigged GLB (offline bake)
xvfb-run -a env -u PYTHONPATH ~/workspace/tools/blender/blender-4.0.2-linux-x64/blender \
  -b --python tools/anim-retarget/retarget_blender.py -- \
  --source anims/mixamo_punch.fbx \
  --target game/assets/models/demonio-body.glb \
  --out    game/assets/models/demonio-body@Punch.glb \
  --bonemap tools/anim-retarget/bone_maps/mixamo_to_wh.json

# 2. Validate the result passes the playable gate
python3 tools/auto_rig/validate.py --in game/assets/models/demonio-body@Punch.glb

# 3. Wire it into the game (runtime path) — see runtime/wh-retarget.js
```

## Conventions

- WH skeletons are **Y-up, face -Z, Mixamo bone names** (see
  `tools/auto_rig/backends/skeleton_template.json`). Mixamo exports already
  match; only `mixamo:` name prefixes need stripping (handled by the bone map).
- Animations ship as **separate GLBs** named `model@Clip.glb`
  (e.g. `demonio-body@Punch.glb`), NOT baked into the base model — the game's
  `AssetManager.clips` loads them on demand per fighter.
- Root motion: the game's `AssetManager.loadModels` pins `Hips.position` to
  bind pose (in-place). Export clips **in place** or let the game pin them.

## Pulled / wired (open source, free)

| Tool | Source | License | What it does |
|------|--------|---------|--------------|
| Blender 5.x Retarget extension | blender.org (bundled extension) | **GPL** (built into Blender) | GUI retarget with Mixamo/Unreal presets — use for manual cleanup passes |
| three.js `SkeletonUtils.retargetClip` | threejs (three/addons, already vendored in `game/vendor`) | **MIT** | runtime bone-map retarget in `runtime/wh-retarget.js` |
| Rokoko Blender plugin | rokoko.com (free download) | **free** | live-stream / import Rokoko mocap into Blender, retarget shelf |
| Rokoko Studio Starter | rokoko.com | **free forever** | record + export mocap FBX/BVH, cleanup filters |
| Rokoko Vision | rokoko.com (browser) | **free** (single-camera) | AI video -> motion, 30s/month processing free |
| Mixamo | mixamo.com (Adobe) | **free** (Adobe ID) | auto-rig + 2,000+ animation library, FBX export |

## Documented, not pulled

- **Auto-Rig Pro** (paid, ~$40) — the Blender gold standard for rigging +
  retargeting. Documented per CONTINUOUS RESEARCH law; NOT cracked, NOT
  pulled. Buy from blendermarket if the owner wants it.
- **Cascadeur** (free tier) — AI-assisted keyframe animation; good for
  hand-authoring signature moves the mocap libraries lack.

## File layout

```
tools/anim-retarget/
  README.md                  this file
  retarget_blender.py        headless Blender: FBX/BVH -> WH-skeleton animated GLB
  bone_maps/
    mixamo_to_wh.json        Mixamo bone name -> WH bone name (+ prefix strip)
    rokoko_to_wh.json        Rokoko Studio skeleton -> WH (planned)
  runtime/
    wh-retarget.js           three.js runtime retarget module (game integration)
    README.md                runtime integration guide
  workflow-mixamo.md         Mixamo auto-rig + animation library workflow
  workflow-rokoko.md         Rokoko Studio/Vision free-tier mocap workflow
  tests/
    test_bonemap.py          bone-map coverage test (all 52 WH bones mapped)
```
