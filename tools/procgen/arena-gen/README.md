# WH procedural arena generator (`tools/procgen/arena-gen/`)

Seeded fighting-stage generator — arenas, not dungeons. Emits **Godot 4 `.tscn`**
and **Three.js scene JSON** from one seed.

```bash
./wh_arena_gen.py --seed 1234 --theme street --out stage_street_1234
# -> stage_street_1234.tscn + stage_street_1234.three.json
```

## What it generates
- Core floor + side platforms (counts/sizes seeded)
- Back + side walls (wall-splat zones)
- Breakable props (crates/barrels/lanterns, RigidBody3D in tscn)
- 40 crowd markers → `MultiMeshInstance3D` (Godot) / instanced list (three.js,
  pairs with `EXT_mesh_gpu_instancing` at delivery)
- Symmetric spawn points, camera bounds, kill-Y

## Fairness rule (tested)
**Generate one side, mirror it.** Never roll each side independently — P1/P2 must
get identical stages. The test asserts platform/prop mirroring and spawn symmetry.

## PCG lineage
Walker/symmetry/noise concepts ported from GDQuest `godot-procedural-generation`
(MIT code) and the fragline ASCII-arena pattern (mirrored maps for fairness).
Fighting-stage constraints (symmetry, wall zones, camera bounds) are WH-original.

## Test evidence (2026-10-16)
- Mirrored platforms/props, symmetric spawns, valid tscn + three.json.
- Deterministic: same seed → byte-identical arena.
- The fairness test caught and fixed a real bug (independent per-side RNG).
