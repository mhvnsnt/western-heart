# Zen spirit body rigged (2026-10-22, Claude session)

Zen's Attire 1 spirit body (owner Tripo 8c46e379) was wired as an unrigged static: the game creates no skinned
mesh for it, so Zen was invisible in fights ("createInstance(zen): ZERO skinned meshes").

- Rigged with `tools/auto_rig/rig_tripo_static.py --facing +X` (GameRig + Blender bone heat + smooth_weights +
  meshopt). Output `roster/zen/attires/attire1/model-rigged.glb`, 73 joints; the Tripo original stays untouched.
- `validate.py`: PASS (valid glTF, skinned, canonical bones, 1.8 m).
- `anim_check` on the CMU boxing stress clip flags Hips->RightPelvis bone variance and 40 vertex spikes
  (`rig_report.json`), the same stress-clip flags the shipped Zui A1 carries. The renders of that clip
  (`zen_stress_clip_front_back_side.png`, front/back/side at 3 times, viewed) show no tearing: kicks, guard and turns
  deform cleanly; the shoulder flames follow the body.
- In-game (`zen_ingame_rest_and_stance.png`, viewed): the game's rest pose faces forward (+Z), clean profile; the T3
  stance retargets with max bone-direction error 0.4 deg.
- Wired: `'zen'` and `'zen-attire1'` -> `model-rigged.glb`; model-facing.json `zen` / `zen-attire1` +Z.
