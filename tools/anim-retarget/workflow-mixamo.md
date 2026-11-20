# Workflow: Mixamo auto-rig + animation library (FREE)

Mixamo (Adobe) is still the fastest free route to a rigged, animated
fighter: browser auto-rigger + 2,000+ mocap clips, FBX export that drops
straight into `tools/anim-retarget/retarget_blender.py`.

**Cost:** $0 — needs a free Adobe ID (sign in once in the browser).
**License of output:** Mixamo's characters/animations are free to use in
projects (Adobe's standard free terms); the rig+clips you download are yours
to ship. Our fighters are WH-original models — we only borrow the *motion*.

## A. Auto-rig a Tripo/static model on Mixamo

1. Prep the mesh (Blender, or `tools/auto_rig/backends/normalize.py`):
   - T-pose or A-pose, facing +Z... Mixamo expects the character **facing +Z**
     in the upload. WH convention is face -Z — the retarget step handles the
     flip, but rigging is cleaner if you rotate the mesh 180° about Y first
     and rotate back after.
   - Apply all transforms, feet on the ground (y=0), single watertight mesh.
2. https://www.mixamo.com → Upload Character → place the chin/wrist/elbow/
   knee/groin markers → Auto-rig. ~1-2 min.
3. Download: **FBX for Unity (.fbx), T-pose, 30fps, WITHOUT skin**
   if you only want the skeleton to transfer weights yourself, or **with
   skin** for the full rigged character.
4. The downloaded skeleton is Mixamo-named → our WH template already matches.
   Run it through `tools/auto_rig/validate.py` (the playable gate).

## B. Pull animation clips

1. Pick a character (any — e.g. the Mixamo "X Bot"), search the animation
   library: `Punch`, `Kick`, `Idle`, `Fight Idle`, `Walking`, `Running`,
   `Knockdown`, `Victory`, etc.
2. Download each as **FBX for Unity (.fbx), 30fps, WITHOUT skin**
   (skin adds nothing for retarget; keeps files small).
3. Retarget onto the WH fighter:
   ```bash
   xvfb-run -a env -u PYTHONPATH <blender> -b --python tools/anim-retarget/retarget_blender.py -- \
     --source anims/Mixamo_Punch.fbx \
     --target game/assets/models/demonio-body.glb \
     --out    game/assets/models/demonio-body@Punch.glb \
     --bonemap tools/anim-retarget/bone_maps/mixamo_to_wh.json \
     --clip-name Punch --in-place
   ```
4. Validate: `python3 tools/auto_rig/validate.py --in game/assets/models/demonio-body@Punch.glb`
5. The game loads `@Clip.glb` files on demand via `AssetManager.clips`
   (or runtime-retarget with `tools/anim-retarget/runtime/wh-retarget.js`
   while iterating).

## Gotchas (from the 2026 guides)

- Mixamo rigs have **no facial bones** and simple hands (no per-finger
  twist) — fine for fighting-game bodies.
- **In-place vs root motion:** download "In Place" versions for attacks;
  the game pins `Hips.position` to bind pose anyway.
- Trim the clip: Mixamo downloads include lead-in/out frames — cut in the
  Blender NLA or pass `--fps` consistently (30).
- Finger motion: only a handful of Mixamo clips animate fingers. For
  grapple/grab clips, hand-key the fingers in Blender after retarget
  (the Rokoko plugin's retarget shelf is handy here too).

## Source

- https://www.mixamo.com (Adobe ID, free)
- Guides: schoolofmotion.com "Why Mixamo Is Still a Great Animation Resource"
  (2026), tripo3d.ai retarget guide (2026).
