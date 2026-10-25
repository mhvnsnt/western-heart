# T-Pose Render Pipeline

One command: model file + character name → white-void + styled T-pose PNGs per the
Western Heart T-pose spec (`docs/tpose-refs/MUSE_TPOSE_SPEC.md`).

## Usage

```bash
./render.py <model.fbx|.glb|.obj> <character-name> [options]
```

Options:
- `--attire p1` — attire name (default: p1). Output: `<attire>_front.png`, `<attire>_side.png`
- `--facing +x` — model forward axis: `+x`, `-x`, `+y`, `-y` (default: `+x`; rigmodels rips face +X)
- `--outdir DIR` — output root (default: `~/workspace/tpose-renders`)
- `--white-only` — skip the styled version
- `--styled-only` — skip the white version

Output goes to `<outdir>/<character>/`. Filenames are unique — existing files
are never overwritten (`-v2`, `-v3` suffixes).

## What it does

1. Imports FBX / GLB / glTF / OBJ (clears animations, drops stray import primitives)
2. Auto-detects armatures → resets to rest pose → T-poses arm chains if needed
   (Mixamo, Tekken 8, and XNALara bone-name patterns)
3. Frames per the spec: orthographic camera, ortho scale = 1.12 × max span
   (~5% margin, hands/feet/hair fully inside, 1:1 square)
4. Renders **white** (2048×2048, Workbench FLAT+TEXTURE, pure white #FFFFFF)
   and **styled** (2048×2048, Cycles 64spp, soft 3-point studio — accurate, no stylization)
5. Writes `<attire>_report.json` (bounds, bones posed, margin check)

## Environment

Blender 4.0.2 headless needs all three (handled automatically by the launcher):
- `xvfb-run -a` (bare `-b` segfaults — Blender needs an X display for Workbench)
- `LD_LIBRARY_PATH=~/workspace/tools/libegl1/usr/lib/x86_64-linux-gnu` (libEGL.so.1)
- `env -u PYTHONPATH` (system numpy breaks Blender's Python)

## Fidelity

The white version is the deliverable the owner uses for Tripo 3D image-to-3D.
No stylization, no mesh edits — clean accurate renders of the model as-is.
If a model has no skeleton and isn't already T-posed, it is NOT posed by hand;
the report flags it and the operator decides (spec: mark BLOCKED-no-rig).
