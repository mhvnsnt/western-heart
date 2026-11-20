# RENDER ORIENTATION — the locked method (owner 2026-10-17)

Our fighter orientation is LOCKED. This doc is the single source of truth for how
every character render is framed, in every repo. Follow it exactly — no guessing,
no "close enough".

## The convention

- **Front camera sits on -X.** The character faces -X (RigModels Tekken 7 FBX rips
  are authored facing -X; "facing negative 90 Z … facing towards him" = front).
- **Orthographic camera**, 2048×2048 PNG, pure white (255,255,255) background.
- **Framing:** `ortho_scale = 1.12 × max(span)` — ~5% / ~109px margin, hands/feet/
  hair fully inside the frame.
- **Side view:** camera on -Y shows the character's left side.
- **T-pose:** via the skeleton (pose bones reset; arm chains posed when needed).
  Models with no skeleton render in authored pose after a facing test render.

## The scripts (in `docs/tpose-refs/_tools/`)

- **`tpose_render_cycles.py`** — the approved renderer (Cycles CPU path; this VM's
  Blender segfaults on bare `-b`, so always run under `xvfb-run -a` with
  `env -u PYTHONPATH`). Usage:
  `blender -b --python tpose_render_cycles.py -- <model.fbx|glb> <outbase> [res]`
  Writes `<outbase>_front.png`, `<outbase>_side.png`, `<outbase>_report.json`.
- **`tpose_render_cycles_faceY.py`** — VARIANT for models authored facing **-Y**
  (not -X). Applies **Rz(-90°) post-import rotation** so the front faces -X where
  the front camera sits. How to tell you need it: render once with the base
  script; if `side.png` (camera on -Y) shows the model front-on, the model faces
  -Y — use the faceY variant. Rz(-90) maps -Y → -X; the side camera then sees the
  model's left side, matching the base spec.

## Own-eyes facing verification (mandatory, every render)

1. Open `_front.png` with your own eyes. The character's FACE/FRONT must look at
   the camera — mask, eyes, chest logo readable, not the back of the head.
2. If it faces away or sideways, you used the wrong variant — switch and re-render.
3. Never ship a render you have not looked at. A worker's "facing verified" is a
   claim; your eyes are the verification.

## Texture rule — deliver nothing flat (owner 2026-10-17)

- Every render must show FULL colors. Flat one-color / washed-out gray renders are
  rejected, no exceptions.
- Root cause found 2026-10-17: GLBs with no embedded image textures (e.g. SFM/VTF
  sources where textures never made it into the GLB) render flat gray in Cycles.
  Study note: Grok's pipeline got colors right by using Workbench FLAT+TEXTURE,
  which displays image textures directly through UVs; our Cycles path needs the
  textures actually present on the materials.
- Fix: embed the model's real textures into the GLB as `baseColorTexture`
  (example: cyborg-x's 23 PNGs from the pull-rest textures mapped by material
  name, script kept with the fix). If a model renders flat, find its textures,
  embed them, re-render — never deliver the flat version.

## Environment

- Blender 4.0.2 at `~/workspace/tools/blender/blender-4.0.2-linux-x64/blender`.
- Always: `xvfb-run -a env -u PYTHONPATH … -b` (bare `-b` segfaults: hard libEGL
  requirement; Mesa + Xvfb installed).
- Low CPU priority for batch work (`nice -n 15`), background, never blocking
  other lanes.

## History

- 2026-10-17: convention locked by owner; documented here and landed in all game
  repos. FaceY variant documented from the No Mercy facing test (GLBs face -Y).
  Texture rule added after the cyborg-x washed-out-gray fix.
