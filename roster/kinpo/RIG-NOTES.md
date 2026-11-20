# KINPO — Rig Notes (owner specs, recorded 2026-10-20)

Standing rig-stage requirements for Kinpo, in the owner's own direction. These
are implemented at rig/animation time — NOT in the pull/wire lanes. Riggers:
read this before rigging any Kinpo attire.

## Jiggle — soft jiggle physics (jiggle bones / soft-body secondary motion)

- **Attire 1** (Tripo 2cb681d2-ae49-4999-9936-44f2d6814a79): butt + thighs +
  hips get soft jiggle physics. Owner verbatim: "needs a jiggly butt" /
  "Jiggly thighs too" / "And hips."
- **Attire 2 "Goth Sport"** (Tripo 4f3eb502-a37b-43a7-999b-020ad81624f5):
  ENHANCED jiggle set — butt + thighs + hips, stronger amplitude than
  Attire 1. Owner: this attire has "a even fatter and jigglier butt and hips
  and thighs."

## M-rated anatomy — Attire 2 "Goth Sport" only (owner 2026-10-20)

- The attire wears the same mini skirt as Attire 1, with **no panties** under
  the skirt.
- The model carries anatomical detail: a gap between the buttcheeks with an
  anus, and a vaginal texture.
- **RIG REQUIREMENT:** rig the vagina and anus for the M-rated tests — the
  anatomy gets rigged (bones/blendshapes as the rig pass determines), not
  left as texture only.
- Context: this is the game's standing M-rated content direction (see the
  law header in `docs/MODEL-INVENTORY.md` — rated M, nudity is never a gate,
  nothing watered down).

## Mesh verification — Attire 1 (repair lane, 2026-10-21)

Owner reported tearing, holes, and triangle tears all over Attire 1's front
render (2026-10-21 ~09:39 CDT). Full diagnosis was run on the shipped GLB
itself (byte-identical to the release pull, sha256
ec67f8f0ddd57e97a915cc85408df08956dcc8bfddfe982698261f03fb6a155f):

- **The geometry is clean.** 1,000,652 verts / 1,933,814 tris; one shell;
  watertight in position space (after an exact-position weld the census is
  3 boundary edges + 6 non-manifold edges out of 2,934,143 — two
  sub-millimetre sliver overlaps, invisible at any render size, deliberately
  left untouched); 0 degenerate triangles; 0 winding inconsistencies;
  0 NaN/outlier vertices; stored normals unit length and aligned with the
  surface (median dot 1.0). The base-color texture is an RGB JPEG — there
  is no alpha channel, so alpha-cut holes are impossible.
- **The tears were in the old proof render, not the model.** That render
  was produced in the pull lane's local workdir on the same night that
  workdir's checkout suffered a write-block incident that zeroed GLB files
  (documented in the lane's own PR #436 report; the commit itself was built
  from API blobs and the shipped file verified). Re-rendered from the
  verified file (1024px, four views, plus native crops of the flagged
  zones): clean everywhere.
  Proof: `docs/tpose-refs/kinpo/a1_front.png` +
  `docs/tpose-refs/kinpo/a1_closeup_*.png` (1024px render, native crops of
  the flagged zones; 2048px re-render attempts were killed six times by VM
  oversubscription, an OOM pile-up and a full VM reboot on 2026-10-21 — a
  2048 pass stays a follow-up for when the box calms; the model file itself
  needs no change).
- **Do NOT position-weld this GLB.** Its 66,844 index-space boundary edges
  are UV-island splits: every one of the 33,038 duplicate-position vertex
  groups carries different UVs (0% attribute-identical), so merging
  positions would tear the texture mapping — it would create the exact
  defect class the owner reported. If manifold topology is wanted at rig
  time, weld inside Blender, where loop data protects the UVs — never on
  the shipped file.
- **Tooling note:** the file uses EXT_meshopt_compression. Blender 4.0.2's
  glTF importer cannot open it directly ("Extension
  EXT_meshopt_compression is not available on this addon version") —
  decompress first (`@gltf-transform/cli copy`). The game loads it as-is
  via the three.js meshopt decoder.
