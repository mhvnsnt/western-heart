# Where real Tekken 7 rigs and motion are (and are not): checked 2026-11-09

Owner (verbatim): "do the skin wait and get the rig and stuff the skeleton in the model and the skin and the weights and
all perfect and then put it on the f****** more upgraded Tekken 7 are taking five f****** bases". Standing law
(2026-10-23): T7 is first-class, T3 is fallback only.

## The plan this serves

1. Give each fighter's Tripo model its base character's own T7 skeleton.
2. Transfer that character's professional (Namco) skin weights onto it with Robust Skin Weights Transfer (Abdrashitov et
   al., SIGGRAPH Asia 2023, the industry method).
3. Animate it with the character's own T7 motion on that skeleton.

## Inventory

| Source | What it really holds |
|---|---|
| `teardown/tekken7/king/`, `king-variants/rigmodels/` | King only: Pantera's exact-King T7 build. |
| Release `tekken7-full-v1` (3.3 GB, 7 parts, 1,266 files, listed by streaming) | Fan and model-site downloads: King variants plus `models/<char>/` zips for Julia, Negan, Eddy, Steve Fox, Asuka, Xiaoyu, Lili, Josie (12-34 MB), small (~1 MB) fan models for Ganryu, Yoshimitsu, Bryan, Lee, Lei, Nina, Baek, Mokujin, Gun Jack, Zafina (T6 XNALara) and Bosconovitch (TTT2 XPS). |
| The eight large FBX rips, imported in Blender 4.0.2 | **Static meshes: no armature, zero vertex groups.** Model-site exports drop the rig. One zip also carries an `Animate3D.exe` (never run; the extracted files were deleted). |
| Release `tekken7-full-v1`, any motion | **None:** no `.arc`, `.anm`, `motbin` or pak files. |
| Release `tekken5-ctype5-glbs-v1` | Stage and effect geometry (beams, rings), not characters. |
| `game/assets/anim/t7/<base>/` | The 17 bases' T7 stances and move packs. Baked from `GRE teardown/tekken7-steam/tkdata/mothead/mask/<code>rotsm.arc` (`tools/anim/t7_c8_stance_bake.py`): a T7 Steam teardown on another lane's machine, not in the repo or Releases. |

## What unblocks it

The T7 game files from the owner's install, uploaded as a Release (as the earlier archives were):

- the character paks, for the skeletal meshes with Namco's weights;
- the `tkdata` motion folder, for each base's own walk / block / hit / KO through `tools/anim/t7_generic_bank_bake.py`.

The owner's steps are in `tools/depot-pull/T7-USER-STEPS.md`. Alternatively, share the T7 folder with a session through
Remote Control in the Claude desktop app.

## Why the rig-only route is not enough (Thor, 2026-11-09)

Re-rigging Thor with `tools/auto_rig/refit_rig.py` changed his weights and joints. The owner judged the in-fight change
at about 5%, and against his base model he is still squashed.

He plays the Tekken 3 Bryan stance. The retarget leaves his torso 12.6 deg and his arms 11-12 deg off that source, and
it stacks three correction layers on the old data: head 77 deg, spine -12.9 deg and arm rolls of 48-76 deg. Switching
them off (`globalThis.__WH_RETARGET_LAYERS` in poselab) exposes the raw T3 head twisted about 77 deg.

Proof: `docs/proof/2026-11-09/refit-thor/`.
