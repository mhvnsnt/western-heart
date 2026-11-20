# Open-source wave-1 wiring — 2026-10-24

Source lane: workspace opensource/ (WIRING.md). This doc is the wiring
record for the wave-1 modules now in the repo. License firewall is OFF
per user rule: everything helpful was pulled, copyleft documented,
nothing blocked on license — but every license below was read from the
pulled files themselves, not guessed.

Buttons, per standing rule: LP1 = Left Punch = Tekken 1, RP2 = Right
Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

## Files wired (wave-1, per WIRING.md patch order)

| Repo file | Source | License | Deps / install |
|---|---|---|---|
| tools/glb-tools/validate.mjs | glb-tools/validate.mjs | Khronos glTF-Validator Apache-2.0 (library 2.0.0-dev.3.10) | npm install gltf-validator |
| tools/glb-tools/optimize.sh | glb-tools/optimize.sh | gltfpack MIT, @gltf-transform/cli MIT | npm install gltfpack @gltf-transform/cli; validate FIRST, then optimize |
| game/lib/hitbox.js | hitbox/hitbox.js (WH's own module) | WH's own, no third-party code | Zero deps |
| game/lib/ragdoll.js | physics/ragdoll.js (WH's own module) | WH's own, no third-party code | Game passes its CANNON; npm install cannon-es (+ @dimforge/rapier3d-compat as the alternative engine) |
| game/lib/retarget.js | retarget/retarget.js (WH's own wrapper) | WH's own over three.js SkeletonUtils (three is MIT) | three already a game dep; SkeletonUtils ships in three examples |
| game/lib/vfx.js | vfx/wh-vfx.js | three.quarks MIT, three-simplecloth MIT | npm install three.quarks three-simplecloth |
| tools/audio/wem-decode.sh | audio/wem-decode.sh | vgmstream MIT (upstream binary, already in workspace) | Set VGMSTREAM_CLI if the binary moves; decodes LOOSE .wem only, never a .bnk directly |
| tools/gpu/kaggle_gpu_animation.py, tools/gpu/kaggle_blender_cycles_gpu.py, tools/gpu/kaggle_batch_gltf.py, tools/gpu/KAGGLE_RUNBOOK.md | gpu/ scripts + runbook (WH's own) | WH's own (torch BSD, Blender GPL) | Kaggle notebook, GPU accelerator ON; T4 runs are a parent step, NOT claimed here |
| customization/OPEN-SOURCE-CREATION-RUNBOOK.md | characters/RUNBOOK.md, licenses re-verified from checkouts | Rokoko LGPL-3.0; MB-Lab code GPL-3.0; MPFB2 code GPL-3.0 + assets CC0; CharMorph code GPL-3.0 | Blender Preferences → Add-ons → Install; addons NOT vendored into this repo |
| docs/research/OPEN-SOURCE-IKEMEN-NOTES.md | reference/ikemen-notes.md | Ikemen GO MIT (reference only, no engine code imported) | Concepts only |

## Tests re-run in this wiring session (workspace copies, before PR)
- Hitbox: PASS — 1 swing = 1 hit, whiff = 0, startup gating holds,
  team/range rules hold.
- Ragdoll (cannon-es): PASS — animated hold, KO launch, ground settle
  (pelvis y = 0.300), getup.
- Retarget: PASS — synthetic 2-skeleton retarget produced 4 tracks.
- VFX imports: PASS — three-simplecloth SimpleCloth present,
  three.quarks BatchedRenderer present (import check in the vfx dir).
- GLB validator smoke: PASS — smoke-valid.glb, 0 errors, 0 warnings,
  0 infos, with gltf-validator 2.0.0-dev.3.10.
- GPU scripts: compile-clean (py_compile equivalent, no writes); T4
  runs still pending (see KAGGLE_RUNBOOK.md).
- Shell scripts: bash -n clean (optimize.sh, wem-decode.sh).
- All staged JS/MJS files: node --check clean.

## Overlap with PR #1066 (open) — exact-path check
PR #1066 added 33 files, 0 modified, 0 deleted. ZERO wave-1 target
paths collide with #1066 paths. Near-overlaps (same area, different
file — none of these files were touched by this lane):
- game/lib/ragdoll.js (this lane, cannon-es) vs game/js/ragdoll.js
  (#1066, Rapier). Both are contextual-only (KO / launch / wall-splat,
  never always-on). The game picks ONE engine at integration time.
  This lane's file carries a cross-reference comment naming the #1066
  file so the two are not confused.
- game/lib/retarget.js (this lane, three SkeletonUtils wrapper) vs
  game/js/retarget.js (#1066, U1-U6 university patterns). Complementary
  layers, not duplicates.
- game/lib/vfx.js (this lane, three.quarks presets + simplecloth) vs
  game/js/gpu-particles.js and game/js/cape-cloth.js (#1066, typed-array
  particle state + chain cloth solver). Complementary, not duplicates.
- tools/gpu/ (this lane, Kaggle scripts) vs tools/gpu-lane/ (#1066,
  batch jobs). Different directories.
- customization/ runbook (this lane) vs game/js/creation-tool-map.js
  (#1066, menu-to-tool map using existing repo tool dirs only).
  No duplicate tools directories were created by either lane.

## What was NOT edited (deliberately)
- No #1066 files. No fighter.js, no physics.js (combat lane owns the
  ragdoll trigger call sites; ragdollTriggerForState stays the seam).
- No game entry files, no menus/HTML, no moveset JSONs, no package.json
  (no root package.json exists on main; tool deps are documented in
  the table above and installed per tool, not wired into a manifest
  this lane does not own). Game-code imports of game/lib modules are a
  follow-up integration step for the combat/UI lanes, not claimed here.
- No upstream clones vendored into the repo (see the wave-2 doc for
  sizes and the reference-only dispositions).
- No play verification claimed: visual tuning of VFX/cloth and the
  live-build check are owed to the parent browser delegation, per
  project law. Deploy sequence: popup PR #1076 FIRST, then these
  wave-1 PRs.

## What was NOT wired (per WIRING.md, kept)
- Ikemen GO / Godot templates: reference only — different engine stack;
  importing their code would replace, not extend, the WH engine.
- UniRig: another lane owns it; not duplicated here.
- Any paid tool: excluded by lane rule.
