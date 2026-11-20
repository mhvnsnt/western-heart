# Workflow: Rokoko Studio + Rokoko Vision mocap (FREE tier)

Rokoko gives us **original motion** — the owner (or anyone) acts out a
punch, a taunt, a victory pose on camera, and minutes later it's a
skeletal clip on a WH fighter. No mocap suit needed.

**Cost:** $0 forever on the Starter plan (record + export FBX/BVH, cleanup
filters). Rokoko Vision (browser AI video→motion): free single-camera
recordings (15s each), 30s/month cloud processing.
**Account:** free Rokoko account (email signup). The owner blanket-approved
Google/GitHub sign-ins; Rokoko is its own account — sign up once in the
browser, then it's hands-off.

## A. Rokoko Vision — video to motion (fastest)

1. https://www.rokoko.com → Vision → record with webcam/phone (single
   camera, free) or upload an existing fight clip (≤15s per recording).
2. Cloud processing: ~30-40s per 10s of footage.
3. Trim in the browser, export **FBX** (or BVH).
4. Retarget:
   ```bash
   xvfb-run -a env -u PYTHONPATH <blender> -b --python tools/anim-retarget/retarget_blender.py -- \
     --source anims/vision_take1.fbx \
     --target game/assets/models/demonio-body.glb \
     --out    game/assets/models/demonio-body@VisionTake1.glb \
     --bonemap tools/anim-retarget/bone_maps/mixamo_to_wh.json \
     --clip-name VisionTake1 --in-place
   ```
   Rokoko exports a Mixamo-compatible skeleton, so the same bone map works.

## B. Rokoko Studio — record, clean, export

1. Install Rokoko Studio (free), record with webcam (Vision AI) or import video.
2. Clean: foot-lock filter (kills foot slide), drift editor, smoothing.
3. Export FBX/BVH → retarget as above.

## C. Blender plugin (free) — manual retarget passes

1. Install the Rokoko Blender plugin (free download from rokoko.com).
2. N-panel → Retargeting shelf → set Source/Target armatures → Build Bone
   List → Retarget Animation (Use Pose: Rest + Auto Scale).
3. Use for clips where the headless script needs hand-tuning (finger
   detail, prop bones, non-T-pose sources).

## Capture tips (from Rokoko's docs)

- Plain background, fitted clothing, stable camera at chest height.
- Act **bigger** than the game needs — retargeting + 30fps sampling soften it.
- Keep takes short (one move per take); trim ruthlessly.
- Foot slide is the #1 artifact: always run the foot-lock filter.

## Limits (honest)

- Single-camera AI mocap struggles with occlusions, fast spins, and fingers.
  Use it for body mechanics; hand-key fingers and faces.
- 30s/month free cloud processing on Starter — plan takes, or upgrade to
  Basic ($10/mo billed annually) for 600s/month when a lane needs volume.

## Source

- https://www.rokoko.com/products/studio (Starter: $0 free forever)
- Vision: browser-based, free single-camera.
