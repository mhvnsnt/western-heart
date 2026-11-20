# Leomon Attire — Tail Save

**Owner directive (seq 84241):** the Leomon attire tail uses the SAME bones, placement,
and movement as Attire 1's tail. Same skeleton for all Pantera tails across all attires.

## Files
- `pantera_tail.glb` — tail mesh + 5-bone chain, copied from `roster/pantera/tail-rig/pantera_tail.glb`
  (attire-1 tail). The attire-2 tail was made simple (tapered + golden tuft), NOT a game rip;
  this GLB is the canonical rig both attires share.

## Rig
- 5-bone chain with Wiggle 2 spring physics (see `roster/pantera/tail-rig/`)
- Bone 1 (attachment) rotation locked to 0; amplitude ramps `0.35*(i/4)^1.3` from bone 2 to tip;
  phase lag keeps the traveling wave
- Blender pose bones: rotation_mode MUST be 'XYZ' (quaternion default silently ignores euler keyframes)

## Owner-placed base position (via Model 3D Placement Tool, 2026-10-12)
- **X=-0.0400, Y=0.0450, Z=0.0000, Scale=1.00**
- Formula: `tail_base = (maxx - widthx*0.06 - 0.04, cy, 0.135)` in both rig scripts
  (`roster/pantera/tail-rig/rig_tail_wiggle.py`, `render_tail_wiggle_video.py`)

## Status
Saved 2026-10-14. Mane Y-axis layering fix still belongs to the owner (see `../mane-pieces/PROVENANCE.md`).
