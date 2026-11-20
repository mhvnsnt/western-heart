# Open-source wave-2 — completion verification + wiring dispositions — 2026-10-24

## Verification result: COMPLETE (clones)

The wave-2 install log (workspace wave2-install.log) ends with the line
"Wave-2 pulls done." and one size line per clone. All seven directories
were re-checked on disk in this wiring session (timestamps 2026-10-25
01:05–01:10, .git present in each). No wave-2 item is incomplete. The
script that finished the wave is the workspace wave2-install.sh (skips
already-pulled dirs, aborts under 5 GB free).

| Clone | Log size | On-disk check |
|---|---|---|
| assimp | 383M | Present, LICENSE + full source tree |
| fbx2gltf (FBX2glTF) | 1.8M | Present, LICENSE + src |
| webgpu-cloth-jspdown (jspdown/cloth) | 512K | Present, LICENSE.txt + src |
| webgpu-cloth-nakjun (Cloth-Simulation-WebGPU) | 96M | Present, src + package.json, NO license file (see below) |
| filediver | 388M | Present, LICENSE + wwise/bnk.go + wwise/wem.go |
| godot-shinobi-arena (SHINOBI ARENA 2D) | 13M | Present, project.godot + scripts, NO license file (see below) |
| godot-topdown-template | 9.2M | Present, LICENSE + full template |

## Per-item license (read from the pulled files, not guessed)
- assimp: BSD-3-Clause (assimp team, 2006–2026).
- fbx2gltf: BSD-3-Clause (Facebook, Inc.) — CORRECTION: the wave-1
  INDEX.md called this "Apache-2.0 (upstream)". The LICENSE file in
  the clone itself says "BSD License" with the three BSD conditions
  including the neither-name clause. BSD-3-Clause is the honest label.
- webgpu-cloth-jspdown: MIT (Harold Ozouf, 2023).
- webgpu-cloth-nakjun: NO LICENSE STATED — no LICENSE file, no license
  field in package.json (private: true), no license statement in the
  README. Disposition is reference-only until a license is stated.
  It is NOT labeled MIT, Apache, or anything else.
- filediver: BSD-3-Clause (Copyright 2026 Filediver contributors).
- godot-shinobi-arena: NO LICENSE STATED — no LICENSE file, no license
  statement found in the README. Disposition is reference-only until a
  license is stated.
- godot-topdown-template: MIT (Stefano Mercadante 2025; bundled
  Dialogue Manager / TileBitTools parts carry their own MIT notices in
  the same file).

## Dispositions (what each wave-2 item becomes in this repo)
- filediver: WIRED AS A PIPELINE NOTE, not vendored. The Go source
  (wwise/bnk.go for .bnk containers, wwise/wem.go for .wem entries)
  closes the .bnk-container gap the audio script documents: extract
  embedded .wem from a .bnk with a filediver build (needs a Go
  toolchain), then decode each .wem with tools/audio/wem-decode.sh
  (vgmstream-cli). The 388M clone is NOT copied into git.
- fbx2gltf: WIRED AS A PIPELINE NOTE, not vendored. FBX → GLB with
  skeletal animation + morphs, CLI batch. Build the source clone (it
  needs the FBX SDK to build; no prebuilt binary is relied on).
  Blender FBX→GLB remains the fallback, and every GLB it produces goes
  through tools/glb-tools/validate.mjs first.
- WebGPU cloth (jspdown MIT + nakjun unstated): REFERENCE ONLY for a
  future custom WebGPU cloth pass (XPBD / graph-colored parallel
  solve tier). The shipped cape-cloth wiring stays game/lib/vfx.js
  (three-simplecloth, MIT). No nakjun code is shipped or derived from
  until its license is stated.
- Godot (shinobi + topdown): REFERENCE ONLY. Godot is not the WH stack;
  importing either template would replace, not extend, the WH engine.
  The concepts already ported into game/lib/hitbox.js (frame-gated
  boxes, activation rescan) are the durable takeaway; the templates
  themselves stay out of the repo.
- assimp: PIPELINE NOTE, not vendored (383M). Use assimp export for
  formats Blender / FBX2glTF do not cover; verify a working assimp
  binary (apt or built) before pipeline use. Outputs go through
  tools/glb-tools/validate.mjs like every other GLB.

## What was NOT vendored, and why
No wave-2 clone was copied into git. Combined wave-2 size is roughly
900M (assimp 383M + filediver 388M dominate); vendoring upstream
source wholesale would bloat the repo, fork upstream, and misstate
provenance. Wiring here means: verified clone + honest license +
pipeline note + the wave-1 tool it feeds. That is the complete wave-2
outcome for this lane.

## Remaining gaps (honest, not hidden)
- nakjun + shinobi licenses unstated → reference-only, no derived code.
- FBX2glTF build (needs FBX SDK) and filediver build (needs Go) are
  build steps for the pipeline owner, not done in this lane.
- assimp binary availability unverified on the pipeline box.
- Kaggle T4 runs for tools/gpu/ are still a parent step
  (see tools/gpu/KAGGLE_RUNBOOK.md).
- Blender addon headless-enable tests are still owed
  (see customization/OPEN-SOURCE-CREATION-RUNBOOK.md).
- Live-build play verification for VFX/cloth is owed to the parent
  browser delegation. Deploy sequence: popup PR #1076 FIRST, then the
  wave-1/wave-2 PRs.
