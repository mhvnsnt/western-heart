# Pantera Tail Rig

## Bone chain
5-bone chain (`tail_01`–`tail_05`) along the tail mesh, parented with automatic weights.
Built in `render_pantera.py` (game-reverse-engineering repo) — the tail is now rigged in rest pose on every render.

## Automatic secondary motion: Wiggle 2 (pulled in, not hand-built)
**Wiggle 2** — open-source (GPL v3) spring-physics addon for Blender bones.
Pulled from https://github.com/n30z3n/blender-wiggle-bones-v3 (v3.2.0, Blender 4.0+).
Local copy: `~/workspace/tools/wiggle-bones/wiggle_2_ultimate.py`

Setup (in Blender, after installing the addon):
```python
scene.wiggle_enable = True
arm_obj.wiggle_enable = True
for pb in tail_bones:
    pb.wiggle_enable = True
    pb.wiggle_tail = True
    pb.wiggle_stiff = 0.35 - i*0.05  # stiffer at base, looser at tip
    pb.wiggle_damp = 4.5
```
Animate only the root/body — spring physics propagates natural lag, bounce,
and follow-through down the chain automatically. No hand-written sine waves.

Full working script: `rig_tail_wiggle.py` (installs addon, builds rig, enables
wiggle, simulates, renders).

## Proof renders
`tail_rig_proof_left.png` / `center.png` / `right.png` — same rig posed at three
lateral positions. The bone chain deforms the mesh cleanly with no pinching.
