# tools/retarget/show-retarget — Cape Jones show retarget, wired for Western Heart

Bonemap, idle retarget, stance-IK bake and QA render/weights flows
from Cape Jones, adapted for Western Heart. Pure Python, stdlib only —
it imports and runs with no Blender, so it runs in CI. Blender-only
steps are documented, not faked.

## Location

Same justification as `../cape-rigging/README.md`: `tools/retarget/`
is WH's existing retarget home. This subdir adds show retarget
alongside the existing game retarget (`retarget_tekken.py`,
`tekken-bonemap.json`) and modifies no existing file.

## Files

| File | What |
|---|---|
| `wh_show_retarget.py` | Rotation-delta retarget, clip retarget (in-place / hip-ratio root), direction-based stance-IK bake, weight QA, stick-figure SVG QA. CLI: `retarget`, `stance`, `qa`, `render-svg`, `blender-steps`. |
| `cape_show_bonemap.json` | CMU → Cape Jones → WH maps, the idle-script map discrepancy, spine-collapse and finger rules, dropped bones, held-at-rest list. |
| `tests/test_show_retarget.py` | Synthetic poses only, stdlib unittest. |
| `PROOF-20261102.md` | Proof run for this PR. |

## Source → adaptation (not a blind copy)

- **Idle retarget:** Cape Jones `retarget_idle_cape.py` retargets a
  CMU idle onto the 94-bone Cape Jones rig, in place, with
  `R_target = (R_src_pose @ R_src_rest⁻¹) @ R_target_rest`. Here
  the same math is used in local form (as in WH
  `retarget_tekken.py`), and the target is WH-Canonical-22, reached
  through the Cape Jones deform bones — not a copy of the CJ rig.
- **Map discrepancy (flagged, not hidden):** the CJ bonemap file
  maps `LeftArm → upperarm_L`, while the CJ idle script maps
  `LeftShoulder → upperarm_L` (shifted by one joint). The bonemap
  file is primary here; the shifted variant is a separate, explicit
  map in `cape_show_bonemap.json`. Mixing them in one clip would
  shift every arm by a joint — do not do it.
- **Stance IK:** Cape Jones `bake_stance_ik.py` exists because
  orientation retarget lands stance arms wrong where bone rolls
  differ. Arms are therefore solved from segment *directions*
  (shortest-arc from rest direction to desired direction) while
  torso/legs/clavicle/hand keep the orientation bake. That exact
  split is preserved here, in data form.
- **QA weights:** Cape Jones `qa_weights.py` flags head verts
  dominated by spine/pelvis/lower bones (FAIL above 5%). Here the
  height axis is WH Y-up (CJ used Z-up) and weight-sum / unweighted
  checks are added, since cage weights must sum to 1.
- **QA render:** Cape Jones `qa_render.py` is an EEVEE front+side
  render. The CI equivalent here is a stick-figure SVG
  (`qa_render_svg`); the EEVEE render of a real character is owed,
  not claimed from the SVG.
- **Not carried over:** `bake_cape_t3.py`'s game-specific orientation
  bake paths, `render_paired.py`'s Blender paired renders, and
  `export_stage.py`'s stage export — WH already has its own game
  retarget and export paths; duplicating them would be copy, not
  wiring. The cape-T3 bake idea (orientation bake for torso/legs)
  is retained as the non-arm path in `bake_stance_ik`.

## WH skeleton differences

See `cape_show_bonemap.json`. Headline: CJ spine (5 segments)
collapses onto WH Spine + Chest with sign-aligned averaging;
CJ fingers in the bonemap are thumb + index only, so other WH
fingers hold rest; CJ cape/collar drop out of the skeleton map
(routed to `tools/cape/`); CMU sources carry no shoulder bone, so
WH shoulders hold rest unless the stance bake drives them. The
brief's 71-joint MB-Lab list has no checked-in name list in
`tools/retarget/` or `tools/mb-lab/` at the base head, so targets
are skeleton-agnostic and unmapped joints are reported, not
invented.

## Usage

```bash
python3 tools/retarget/show-retarget/wh_show_retarget.py retarget \
    --bonemap tools/retarget/show-retarget/cape_show_bonemap.json \
    --map show_to_wh_canonical --pose pose.json --out out.json
python3 tools/retarget/show-retarget/wh_show_retarget.py stance \
    --stance stance.json --out out.json
python3 tools/retarget/show-retarget/wh_show_retarget.py qa \
    --weights weights.json --out report.json
python3 tools/retarget/show-retarget/wh_show_retarget.py render-svg \
    --joints joints.json --out qa.svg
python3 -m unittest discover -s tools/retarget/show-retarget/tests -v
```

## Still owed (not claimed as wired)

- Blender BVH/FBX → GLB import/export on a real show clip.
- EEVEE QA render of a real retargeted WH character.
- A real CMU idle clip retarget (clip bytes are not in this repo).
- A checked-in 71-joint MB-Lab target skeleton list.

## Rules respected

No file deletions, no force-push, no deploy, no secrets, no
commercial game files/models/textures/animations/audio/ROMs, no
`.blend`/BVH/GLB binaries, no character names in any UI (this is
a tool, not UI). Source games are named only where the existing
WH retarget docs already name them.
