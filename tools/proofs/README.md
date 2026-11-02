# Western Heart — free-stack proof tools (PROOFS ONLY)

This directory wires the **outside free stack** from the tools audit
(`docs/handoffs/TOOLS-AUDIT-20261102.md`, PR #1506) into Western Heart
**for proof output only** — stills and clips shown for review. It does
not touch fight code, game logic, or shipped game assets, and it adds
no commercial asset, model, texture, animation, audio, or ROM to the
public repo.

Source of truth: the audit's outside-stack section lists FFmpeg, Krita,
glTF-Transform, OpenToonz / Tahoma2D, Synfig, RIFE, and DaVinci Resolve
(free), sourced from the cape-jones `FREE-STACKS-INDUSTRY-STANDARDS.md`
2D-animation / free stack. Paid tools are explicitly out: Toon Boom
Harmony, Adobe Animate, and the Spine editor are **not installed**,
have **no licence in this repo**, and are **not claimed, faked, or
emulated** anywhere in this PR. OpenToonz / Tahoma2D is the free
fallback for 2D animation.

## What this PR wires (each piece labelled runnable or docs-only)

| Piece | File(s) | Status |
|---|---|---|
| (a) FFmpeg delivery | `ffmpeg-deliver.sh` | **Runnable** — tested on this VM (ffmpeg 8.1.2). Image sequence, single image, or video in; H.264 proof MP4 + thumbnail + `delivery.json` manifest out. Silent by default. |
| (b) Krita clean-up | `krita-cleanup.md` + `krita-cleanup-check.py` | **Docs-only GUI step + runnable checker.** Krita is not installed on this CPU-only VM, so the GUI clean-up cannot run here and is not faked; the checker verifies the exported PNG and records the operator's attestation. |
| (c) glTF-Transform validate | `gltf-validate.mjs` | **Runnable (tier 1 always; tier 2 when codec deps resolve).** Wired into the existing flow, not a duplicate: run it *after* `tools/anim/gltf_codec.mjs encode` and before a proof GLB is shared. It does not encode. glTF-Transform + meshopt are already used by `gltf_codec.mjs` (pinned `@gltf-transform/*@4.1.1`, `meshoptimizer@0.22.0`) and by `tools/gltfpack/`; this script reuses those same deps for its deep tier and adds the missing *validate* step (container/JSON checks + deep parse). No new codec code. |

## How the pieces fit together (proof flow)

```
WH render (frames / still / GLB)
  -> [optional, human] Krita clean-up ......... krita-cleanup.md + check.py
  -> [GLB only] gltf_codec.mjs encode ........ existing, unchanged
  -> [GLB only] gltf-validate.mjs ............ must exit 0 before sharing
  -> [clips] ffmpeg-deliver.sh ............... proof MP4 + thumb + manifest
```

## Still owed (not claimed as done)

- **OpenToonz / Tahoma2D 2D-animation step** — owed: free fallback named
  by the audit, but no OpenToonz/Tahoma2D install or project wiring exists
  in this PR; needs an installed copy and a real proof project to test.
- **Synfig step** — owed: same reason; listed in the audit's free stack,
  not installed here, no tested wiring.
- **RIFE frame interpolation** — owed: needs a GPU. This VM is CPU-only
  (4 vCPUs, no NVIDIA device), and the audit notes GPU renders need a
  GPU machine; a CPU-only RIFE run is not claimed.
- **DaVinci Resolve (free) edit** — owed: GUI editor, not installed on
  this VM, no headless edit path tested here.
- **Headless/automated Krita clean-up** — owed: Krita not installed
  here; the GUI step is documented and checker-verified only.
- **Full Khronos glTF validator report** — partially owed: tier 1 +
  gltf-transform deep parse are runnable; a standalone Khronos
  validator binary/report is not bundled, so if the team wants that
  exact report format it is a follow-up, not something this PR fakes.

## Rules this PR keeps

- PR-only, 0 file deletions, no force-push, merge only on green gates,
  NO DEPLOY.
- No API keys or secrets in any file.
- No raw commercial game files, models, textures, animations, audio,
  or ROMs.
- Player-facing names law: no other games' character names appear in
  any UI or proof output here; proof subjects are referred to
  generically. (This directory contains no character names at all.)
- Proof outputs (`*.mp4`, `*-clean.png`, manifests) are delivery /
  review files, not game assets; do not check generated proof media
  into the repo unless a proof brief explicitly asks for it.
