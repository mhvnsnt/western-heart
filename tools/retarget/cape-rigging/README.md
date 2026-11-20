# tools/retarget/cape-rigging — Cape Jones rigging, wired for Western Heart

BlenRig fit/setup/warp, joint detection and weight-cage logic from
Cape Jones, adapted for Western Heart. Pure Python, stdlib only —
it imports and runs with no Blender, no third-party package, so it
runs in CI. Blender-only steps are documented, not faked.

## Location

`tools/retarget/` is WH's existing retarget home (its README,
`tekken-bonemap.json`, `tekken_skeleton_base.json`, `tests/`).
`tools/auto_rig/` is the GameRig creation backend, `tools/rig-guard/`
is only a MODEL_URLS guard, and `tools/rig-repair/` is repair — none
of those is a fit/retarget library. This subdir keeps retarget wiring
in one place and modifies no existing file.

## Files

| File | What |
|---|---|
| `cape_rig.py` | Fit guides (BlenRig fit/warp), cross-section joint detection, procedural weight cage, WH-space conversion, Blender step list. CLI: `fit`, `cage`, `detect`, `blender-steps`. |
| `cape_rig_map.json` | Guide → WH-Canonical-22 map, skeleton differences (incl. the honest 71-joint MB-Lab gap), dropped bones, and the Blender 5.2.3 peg-seating gate. |
| `tests/test_cape_rig.py` | Synthetic test rig (T-pose capsule cloud + joint dict), stdlib unittest. |
| `PROOF-20261102.md` | Proof run for this PR. |

## Source → adaptation (not a blind copy)

- **Fit:** Cape Jones `blenrig_fit.py` scales the BlenRig biped by
  0.544 (1.70 m → 0.9248 m toon), fits guides, rest-bakes, and turns
  reproportion off. WH fits in target space at `rest_scale=1.0`
  (0.544 is opt-in); the guide table itself is preserved.
- **Warp:** Cape Jones `blenrig_warp.py` warps every non-guide bone
  by its nearest guide in edit mode. Here `warp_bones()` records the
  nearest guide + distance in data, so the Blender warp step is
  checkable without Blender.
- **Joint detection:** Cape Jones `joint_detect.py` slices a dense
  mesh (cell 0.006 m, numpy) and reads knees/ankles from radius
  minima. Here the same slice-and-cluster method is reimplemented
  in stdlib, its z-bands scale by detected height / 0.9248 (so it
  works on WH-height characters, not just the 0.9248 m toon), and
  the hard-coded waist (0.56 m) becomes the hip–chest midpoint.
  The test cloud is sparse, so the slice cell is 0.035 × scale —
  dense real meshes should use a smaller cell.
- **Weight cage:** Cape Jones `weight_cage.py` fits BlenRig's shipped
  MDEF cage mesh (1,057 verts) to the character bbox at mesh level,
  then writes 1/d² zone weights (locked bones rigid, max 4
  influences, normalised). Here the cage is procedural (rings
  around each bone segment) and the same weight rule is applied;
  `verify_weights()` proves every vert sums to 1.
- **Blender 5.2.3 peg rig:** the fixed/refined builds are 2D toon
  peg rigs (17 pegs, 11 drawings, FK 6/6), not a 3D skeleton. No
  `.blend` is copied. Their seating rules (cape Torso-parented,
  collar below torso, head base on neck, arm front/back identity,
  crossed snap Z, 120° flex) are carried in `cape_rig_map.json`
  as a pose gate only.

## WH skeleton differences

See `cape_rig_map.json` `skeleton_differences`. Headline: WH is
realistic-proportioned and Y-up / faces +Z (Cape Jones detection
is Z-up / faces −Y); WH-Canonical-22 has 22 core bones vs the Cape
Jones 94-bone show rig; CJ spine (5 segments) and fingers (5+4
segments per side) collapse onto WH's 2 spine bones and 3-segment
finger chains. The brief's 71-joint MB-Lab skeleton has no
checked-in name list in `tools/retarget/` or `tools/mb-lab/` at
the base head, so this module is skeleton-agnostic and reports
unmapped joints instead of inventing 71 names.

## Usage

```bash
python3 tools/retarget/cape-rigging/cape_rig.py fit \
    --joints joints.json --out guides.json
python3 tools/retarget/cape-rigging/cape_rig.py detect \
    --verts verts.json --out joints.json
python3 tools/retarget/cape-rigging/cape_rig.py cage \
    --skeleton skeleton.json --out weights.json
python3 tools/retarget/cape-rigging/cape_rig.py blender-steps
python3 -m unittest discover -s tools/retarget/cape-rigging/tests -v
```

## Still owed (not claimed as wired)

- BlenRig addon + MDEF cage bind inside Blender 5.2.3.
- MB-Lab on Blender 5.2.3 verification (WH pins 4.0.2 for MB-Lab).
- EEVEE QA renders of a real fitted WH character.
- A checked-in 71-joint MB-Lab target skeleton list.

## Rules respected

No file deletions, no force-push, no deploy, no secrets, no
commercial game files/models/textures/animations/audio/ROMs, no
`.blend` binaries, no character names in any UI (this is a tool,
not UI). Source games are named only where the existing WH
retarget docs already name them.
