# Vendored: Surface Heat Diffuse Skinning

- **Upstream:** https://github.com/meshonline/Surface-Heat-Diffuse-Skinning
- **Commit:** 578fed63590d2034fcc6b0981f3c87265777d184 (2024-08-31)
- **License:** MIT (see `LICENSE` in this folder; Copyright (c) 2018 Mingfen Wang)
- **What it is:** a Blender add-on implementing surface heat diffusion
  skinning (the free/open sibling of the same author's voxel heat
  diffuse method). Instead of Blender's built-in bone-heat solve, it
  diffuses heat over the mesh SURFACE from each bone segment, which
  handles the close-but-geodesically-far cases (armpits, crotch,
  fingers) where built-in heat weights bleed across body parts.
- **Contents vendored:** `addon/surface_heat_diffuse_skinning/__init__.py`
  (operator `wm.surface_heat_diffuse`), `src/` (the C++ helper:
  `main.cpp`, `raytri`, `tribox`, `Vector.hpp`), upstream `README.md`,
  `LICENSE`.
- **Helper binary:** the add-on shells out to a per-platform helper at
  `addon/surface_heat_diffuse_skinning/bin/<platform>/`. The binary is
  NOT committed; build it once per machine:

      cd src && g++ -O2 -o ../addon/surface_heat_diffuse_skinning/bin/Linux/shd main.cpp raytri.cpp tribox.cpp

  (verified building clean with g++ 13.3 on this VM, 2026-10-29;
  `backends/surface_heat.py` also builds it on demand when missing.)
- **Wiring:** `tools/auto_rig/backends/surface_heat.py` runs it inside
  Blender; if the helper cannot be built or the operator fails, the
  caller falls back to `backends/blender_heat.py` (Blender built-in
  bone heat — same algorithm family, weaker on close-surface cases).
