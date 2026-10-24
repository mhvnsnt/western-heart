# tools/open-source/

Vendored open-source tooling. RESEARCH → PULL → WIRE-UP: every tool here is researched,
pulled, and tested — see `docs/research/OPEN-SOURCE-PULL-INS-2026-10-19.md` for the full
pull-in log, licenses, and what was NOT pulled (and why).

| Dir | Tool | Use here | License |
|-----|------|----------|---------|
| `tkmovesets/` | TKMovesets (Kiloutre) | Tekken T5–T8 moveset extraction format reference | GPL-3.0 |
| `gamerig/` | GameRig (Arminando) | Game-engine-friendly auto-rigging for Blender | see LICENSE |
| `blender-addons/wiggle-2/` | Wiggle 2 (shteeve3d) | Spring-physics jiggle bones — TESTED on Blender 4.0.2 | see LICENSE |
| `blender-addons/wiggle-bones/` | Wiggle Bones (Hans-xwh) | Wiggle 2 refactor for Blender 5.0+ (upgrade path) | GPL-3.0 |
| `blender-addons/keemap-retargeting/` | Keemap (nkeeline) | Mocap/rig retargeting — TESTED on Blender 4.0.2 | GPL-3.0 |

## How the lanes use these

- **Jiggle lanes:** load `blender-addons/wiggle-2/wiggle_2.py` into Blender, apply to the real
  jiggle bones (DEF-breast.L/R, Butt_L/R chains), bake to keyframes. No hand-tooled
  sine-wave jiggle — physics, not guesswork.
- **Animation/mocap lanes:** retarget CMU/Mixamo clips through `keemap-retargeting/`
  (Source/SourceFiles). Match hip placement first (the stretch fix).
- **Move-decode lanes:** read `tkmovesets/TKMovesets2/LocalStorage/MovesetStructs.h` for the
  TKM2 binary format; use TKMovesets extraction as the data source for 100+ moves/fighter.
- **Rig lanes:** `gamerig/` for game-ready auto-rigs.

Blender 4.0.2 at `~/workspace/tools/blender/blender-4.0.2-linux-x64/blender`.
