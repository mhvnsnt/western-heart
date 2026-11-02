# Tools audit - Western Heart, Cape Jones, Mochiichao, GRE, outside open source - 2026-11-02

Owner order (verbatim, 2026-11-02): "start using Blender a bit more, bring in Blender five and bring in anything else from like any of the 250 like 500 tools and things in open source and industry standard 100% things that I done pulled into like the Cape Jones repos and the Mochi Chow repos and all of those things anything that'll help you" and "get all of that done 100% and wired up and landed into the repo, get all of that finished."

Method: counted from the repos themselves via the GitHub API (top-level entries per directory, not guesses). Home-disk writes were blocked by quota, so this doc was uploaded via the Contents API. No deploy. No API keys/secrets in any file. No raw commercial game files, models, textures, animations, audio, or ROMs in this PR. No bot enrollments, no write-access grants, no account creation in this PR.

## Counted inventory (top-level entries, not recursive totals)

- western-heart/tools/: 116 entries - anim, mb-lab, mpfb2, mocap, retarget, glb-tools, gltfpack, tpose-render, proof-harness, gpu-jobs, kaggle, mcp, ai-inference, deploy, coverage, frame-data, moveset-*, rig-*, teardown-coverage, tripo-*, etc.
- western-heart/customization/tools/: 29 entries - convert_caw_parts, convert_defjam_o, convert_wmxix_ymg, convert_no_mercy_parts, rigpose_bake, apply_customization, face/eye builders, tests.
- western-heart/tools/anim/: 38 files - T3/T7 bake, resolve, probe, codec, reaction, coverage.
- cape-jones/tools/: 24 subdirs - blender-mcp, camera-match, rigging, show-retarget, render-manager, inference, upscale-denoise, lighting, weights, wired, pulled, etc.
- cape-jones/tools/rigging/: 43 files - BlenRig fit/setup/warp, bind, weight cage, joint_detect, verify_deform/warp.
- cape-jones/tools/show/ + show-retarget/: 8 + 5 files - bake_cape_t3, bake_stance_ik, render_paired, retarget_idle_cape, bonemap, QA render/weights.
- cape-jones/blender523-* (4 dirs): 33 files - rig-fixed 10, rig-refined 7, motion-snap-lock-study 10, motion-arm-snap-early 6: .blend files, build_*.py, verify JSON, reports.
- cape-jones/cape-jones-rig/: 411 top-level entries - mostly docs, specs, proof dirs and renders; about 25 Python scripts (joint_locked_rig v3-v7c, compositor, lighting, render_clips, slice_clean, repose tests). Do NOT count 411 as 411 tools.
- cape-jones root: 2 scripts - mocap_retarget.py, proof_render.py.
- mochiichao-fresh-start/tools/: 36 entries - 19 Pokemon data extractors, validate_*, title_*, sprite-atlas, sprite-art, music-production, avatar-pipeline, qa, wfc, fastnoise, ndstool, dsdecmp.
- game-reverse-engineering (GRE, private, 5,225,380 KB): 44 root entries - teardown/ 10, tools/ 14, toolkit/ 11, western-heart/ 9, tekken7/ 8, wrestling-games, wwe-wrestlemania-xix, wwf-no-mercy, tekken3/5/6/7/8, soulcalibur, street-fighter, vf5, models.
- teardown-* small repos: 9-10 repos, each README + TEARDOWN + TRANSFER-MAP + WIRING-PLAN = 4 files each, about 36-40 files total. tekken7, fire-pro, bw2, hgss, yakuza, shadow-of-war, spore, persona5, fallout, skyrim-se.
- teardown-reference-library (private, 99,437 KB): 10 entries - staging of public modding tools / decomp study code, staging only, not Western Heart wiring.
- Lyra (fork) / NightSkyEngine (fork) / SchwarzerblitzEngine (fork): 14 / 13 / 10 root entries. Lyra = Epic UE5 sample game. NightSkyEngine = Unreal fighting-game framework. SchwarzerblitzEngine = SFML/irrlicht 3D fighting engine. None is the Unreal Engine source itself.

Top-level entries summed across audited dirs: about 449. That is NOT 449 distinct tools and NOT 449 wired tools. Distinct executable scripts/tools is on the order of 150-200; the rest are docs, specs, proof renders, and directories. No claim of 250 or 500 tools wired is made here.

## GRE / reverse-engineering - found / wired / owed

- WWE 2K19 teardown transfer from GRE: ALREADY WIRED into western-heart - PRs #1480/#1481/#1483/#1485, 1,677 files (2026-11-01). Do not redo it.
- GRE tools/ (14): defjam, ghidra-processors, iso9660_extract, koei-k300, n64-aki, quickbms-scripts, renderware, segafarc, tekken3, watermark-removal, wwe, xbox, yakuza-par - usable as extraction/reference tooling, PRIVATE repo only for raw outputs. Wired new in this audit: 0. Owed: 14, reason: per-tool wire-in PR + private-repo routing for raw output.
- GRE toolkit/ (11): bootstrap, install, pins, selftest, ci-runner, scripts, patches - toolchain installer, not game content. Owed: 11, reason: needs a Western Heart toolchain-adaptation PR, not a copy.
- GRE teardown/tekken7-steam, tkdata, tekken7/customization, tekken7/models: reference data for Tekken 7 systems. Owed, reason: per-system mapping to WH movesets/rigs, no raw files to public repo.
- teardown-tekken7 repo (4 files): README, TEARDOWN, TRANSFER-MAP, WIRING-PLAN - docs, directly relevant to Western Heart/Pantera. Owed as docs-to-code: 1 repo set.
- teardown-fire-pro (4 files): wrestling-sim construction, relevant to Western Heart wrestling systems. Owed: 1 set, docs-to-code.
- Other teardown-* repos (bw2, hgss, yakuza, shadow-of-war, spore, persona5, fallout, skyrim-se): 8 sets x 4 files = 32 files, all Mochiichao systems docs, NOT Western Heart tools. Not counted as Western Heart owed.
- GRE totals for Western Heart: found about 79 top-level GRE entries, wired new in this audit 0, owed WH-relevant about 27, not-WH-relevant Mochiichao docs 32 files, already-wired WWE 2K19 1,677 files (prior PRs).

## Blender - verified, not assumed

- "Blender five" is Blender 5.2.3 LTS. Verified on this VM 2026-11-02 by running the binary (not in PATH, but present at ~/workspace/tools-industry/blender-5.2.3-linux-x64/blender): "Blender 5.2.3 LTS, build 2026-10-22, hash e13b728c6880, blender-v5.2-release". Blender 4.5.3 LTS also verified the same way (build 2025-09-09, hash 67807e1800cc).
- Cape Jones blender523 work is real: build_blender523_rig_fixed.py (14,758 B), build_blender523_rig_refined.py (19,039 B), cape_jones_toon_blender523_*.blend files, motion snap-lock study with template-test PASS/FAIL JSON.
- Western Heart Blender standard in-repo is Blender 4.0.2 for MB-Lab (tools/mb-lab/README.md: MB-Lab 1.8.x needs Blender 4.0+; pipeline standard 4.0.2). That is older than 5.2.3 - MB-Lab 1.8.1 Blender 5.x compatibility is NOT verified in the repo, so do not claim MB-Lab runs on 5.2.3 until a headless run proves it.
- This VM: 4 CPU, 7.7 GB RAM, no NVIDIA device, no GPU. Blender runs CPU-only here. GPU renders need Kaggle/Colab GPU notebooks (owner GPU-first rule) or a Windows/Unreal machine. Blender is NOT in PATH; use the full tools-industry binary path, with HOME=/tmp to avoid the home quota.
- What Blender can do for Western Heart now: re-bake templates (tools/mb-lab/bake_all_templates.sh + bake_morph_templates.py, already used for the 9 templates in #1495), morph/GLB reports, rigging (tools/auto_rig GameRig backend), retarget (tools/retarget/retarget_tekken.py), T-pose renders, GLB export for the web game.

## Unreal + Aura - plain language

- Western Heart is a web Three.js game. Tekken 7 is Unreal Engine 4, Tekken 8 is Unreal Engine 5. That does NOT make Western Heart an Unreal game, and it does not flip to Unreal overnight.
- Fastest real use: Unreal + Aura as PRODUCTION (make animations/characters in Unreal/Aura on Windows), export GLB/FBX, land them in the web game. A full Unreal mobile build (Android/iOS from Unreal) is a separate future project, not a switch.
- Aura AI: owner-supplied link https://app.tryaura.dev/download, trial code BETAPROMO, Google sign-in fmmg.mars@gmail.com. Aura sign-in/trial/download is handled by a SEPARATE browser task owned by the parent - this audit does NOT duplicate that sign-in, and does not claim Aura is installed, trialled, or wired until that browser task reports it.
- Epic Games GitHub check, as actually returned by the API: /user/orgs = [], /user/repository_invitations = [], EpicGames org access = 403 (fine-grained token lifetime >366 days, per GitHub's message), /repos/EpicGames/UnrealEngine = 404. So the engine source is NOT currently reachable with this token. Owner steps that would unblock it: (1) shorten the fine-grained token lifetime to <366 days, (2) accept the EpicGames org invitation in the mhvnsnt account if one is pending, or (3) confirm a different GitHub username that Epic invited. A repo search for "unreal user:mhvnsnt" returned 0; his list DOES include Lyra, NightSkyEngine, and SchwarzerblitzEngine forks - those are Unreal-related projects, not the engine source.

## Outside industry-standard open source - found / wired / owed

All freely licensed / public-documentation, with a repo or public source per item. No raw commercial files. Wired new in this audit: 0 code tools; this PR wires the audit doc itself only. Owed counts below are wire-in PRs, not claims of use.

- Blender 5.2.3 LTS + 4.5.3 LTS - blender.org / cape-jones blender523 work, WH tools/mb-lab. Owed: 1 wire-in (pin 5.2.3 as WH Blender standard + verify MB-Lab on it, or keep 4.0.2 for MB-Lab and 5.2.3 for rig/render).
- MB-Lab (GPL-3.0 code, AGPL-3.0 data) - github.com/animate1978/MB-Lab, WH tools/mb-lab. Already used for the 9 templates (#1495). Owed: 0 new, except the 5.2.3 verification above.
- MPFB2 / MakeHuman (GPL source, CC0 core assets) - github.com/makehumancommunity/mpfb2, WH tools/mpfb2. Owed: 1 wire-in (clean CC0 base alternative to MB-Lab AGPL bases).
- CharMorph (Vitruvian CC0 base) - github.com/Upliner/CharMorph, WH tools/blender/oss-catalog.json. Owed: 1 wire-in (Vitruvian base -> Rigify -> WH rig).
- glTF-Transform + meshoptimizer - WH tools/anim/gltf_codec.mjs, tools/gltfpack/. Already used for GLB optimize/validate. Owed: 0 new.
- OpenToonz / Tahoma2D 1.6.3, Synfig Studio, Krita, FFmpeg, RIFE, DaVinci Resolve (free) - cape-jones FREE-STACKS-INDUSTRY-STANDARDS.md. 2D/animation/free stack, not WH fight code. Owed: 6, reason: show/animation pipeline, not yet wired to WH.
- Spine JSON format / Rigby2D - cape-jones-rig-spine.json (Spine 3.8 skeleton JSON). Owed: 1 wire-in (read/write Spine JSON for WH rigs, no paid Spine editor needed).
- Godot-style / open fighting frameworks (public docs only): SchwarzerblitzEngine (SFML, in owner's forks), NightSkyEngine (Unreal framework, in owner's forks) - reference only. Owed: 2, reason: reference frameworks, not drop-in WH code.
- Outside totals: found 14 items, wired new 0, owed 11, already-wired 3 (MB-Lab templates, glTF/meshopt, Blender binaries present).

## Wiring plan, prioritized (each as its own PR, no deploy)

1. Pin Blender 5.2.3 + verify MB-Lab on it (or document the 4.0.2/5.2.3 split) - 1 PR.
2. Wire WH tools/mb-lab + mpfb2 + CharMorph Vitruvian bases into the creation suite as documented bases - 3 PRs, one per base family.
3. Wire cape-jones rigging (BlenRig fit/setup/warp, joint_detect, weight cage) + show-retarget (bonemap, QA render/weights) into WH tools/retarget - 2 PRs.
4. Wire GRE tools/ extraction scripts that are open-source (iso9660_extract, quickbms-scripts) as reference tooling, private outputs only - 2 PRs.
5. Wire teardown-tekken7 + teardown-fire-pro transfer maps into WH moveset/wrestling docs-to-code - 2 PRs.
6. Wire outside free stack for WH proofs only (FFmpeg delivery, Krita clean-up, glTF-Transform validate) - 1 PR.
7. Unreal/Aura: production-export pipeline doc + GLB export test from Unreal/Aura on a Windows machine - 1 PR, blocked on the separate Aura browser task + Epic token/invitation fix above.
8. Mobile: Unreal mobile build scaffold as a SEPARATE project - 1 PR, blocked on Epic source access above. Do not claim the web game is now Unreal.

## Gaps - still owed, with reasons

- Recursive file totals inside WH tools/ subdirs: NOT fully counted (GitHub tree API truncates at 61,038 entries for western-heart). Top-level counts above are verified; recursive totals are not claimed.
- MB-Lab on Blender 5.2.3: unverified (see above).
- Toon Boom Harmony: BLOCKED, not installed (cape-jones TOP5 audit: shop fmmg.mars@gmail.com = 0 subscriptions, Windows .exe on owner's browser Downloads, not on this VM). Fallback in use: Cape Jones Toon / OpenToonz.
- Adobe Animate / Spine editor: NOT installed, paid, no licence in repo. Not faked.
- MediaPipe/OpenPose pose check: NOT RUN in cape-jones (pip blocked, /tmp space). Not claimed.
- Aura trial/download: pending the separate browser task; not claimed here.
- Epic UnrealEngine source: 404/403 as above; not claimed as accessible.
- Windows-only / GPU-only tools: any tool in the audited sets that needs Windows or a GPU is owed until a Windows/Unreal machine or Kaggle/Colab GPU run proves it. Counted as owed in the per-item reasons above, not as wired.
