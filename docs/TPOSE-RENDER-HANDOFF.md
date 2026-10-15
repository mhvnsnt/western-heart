# T-Pose Render Handoff

Status: handoff/specification only. No renders have been produced by this change.

## Goal

Render the actual Western Heart GLB assets as consistent, neutral, full-body T-pose PNGs and a labeled contact sheet. Preserve existing assets and branches; render outputs should be generated artifacts, not replacements for source models.

## Source branch / model inventory

This handoff is based on the current head of PR #170, `roster-integrate-phase1`. PR #170's description and `RENAME-MAP.md` identify these 23 T7-style model assets:

| GLB path | WH name / source character |
|---|---|
| `game/assets/models/kinpo.glb` | Kinpo / Asuka Kazama |
| `game/assets/models/kinpo_alt1.glb` | Kinpo alternate / Asuka Kazama |
| `game/assets/models/skull.glb` | Skull / Bryan Fury |
| `game/assets/models/king-tyrant.glb` | King Tyrant / Eddy Gordo |
| `game/assets/models/king-tyrant_alt1.glb` | King Tyrant alternate / Eddy Gordo |
| `game/assets/models/thor.glb` | Thor / Ganryu |
| `game/assets/models/sam-ur-a1.glb` | SAM-UR-A1 / Gun Jack |
| `game/assets/models/waterfall.glb` | Waterfall / Josie Rizal |
| `game/assets/models/nightwolf.glb` | Nightwolf / Julia Chang |
| `game/assets/models/pantera_alt1.glb` | Pantera alternate / King |
| `game/assets/models/purple-rain.glb` | Purple Rain / Lee Chaolan |
| `game/assets/models/n3g4tiv0.glb` | N3GΔTIV0 / Negan |
| `game/assets/models/awa-pop.glb` | Awa Pop / Nina Williams |
| `game/assets/models/zui_alt1.glb` | Zui alternate / Steve Fox |
| `game/assets/models/zui_alt2.glb` | Zui alternate 2 / Steve Fox |
| `game/assets/models/saku-ra.glb` | Saku Ra / Ling Xiaoyu |
| `game/assets/models/saku-ra_alt1.glb` | Saku Ra alternate / Ling Xiaoyu |
| `game/assets/models/phantom.glb` | Phantom / Yoshimitsu |
| `game/assets/models/lei.glb` | Unmapped source: Lei Wulong |
| `game/assets/models/lili.glb` | Unmapped source: Lili |
| `game/assets/models/mokujin.glb` | Unmapped source: Mokujin |
| `game/assets/models/zafina.glb` | Unmapped source: Zafina |
| `game/assets/models/baek.glb` | Unmapped source: Baek |

PR #170 also mentions five mapped/alternate source files that were blocked and are not part of the 23 converted models yet: Heihachi→Diablo (RAR), Dr. Bosconovitch→Doc Frank (XPS), and Xiaoyu T8→Saku Ra alternate 2 (RAR), plus phase-2 game archives. Do not treat these as renderable GLBs until they exist in the checkout.

## Render all available variants

Do not rely only on the table above. At run time, discover all `.glb` files under `game/assets/models/` and the relevant roster attire folders, then include each unique available model in a manifest. This catches pre-existing bases and new variants without guessing filenames. Avoid rendering unrelated environment/stage models if present; provide an explicit include/exclude manifest for review.

At minimum, include the available model variants for:
- Bryan Fury, Ganryu, Gun Jack, Josie Rizal, Lee Chaolan, Negan, Nina Williams, Yoshimitsu
- Kinpo, King Tyrant, Nightwolf, Pantera, Purple Rain, SAM-UR-A1, Saku Ra, Zui
- Lei, Lili, Mokujin, Zafina, Baek
- Other existing character variants found by inventory discovery

## Output contract

- One PNG per model, neutral full-body T-pose, front view, orthographic camera, plain light background, soft even lighting.
- Preserve original textures/materials; no creative redesigns or destructive edits.
- Normalize scene scale for framing only. PR #170 documents a model scale fix from 0.01 to 1.0; inspect each imported scene's bounds and do not blindly rescale geometry if the GLB is already corrected.
- Use safe framing based on world-space bounds, including hands, feet, hair, tails, and accessories.
- Save renders in a new, non-overwriting output directory, e.g. `artifacts/tpose-renders/<run-id>/`.
- Produce a manifest CSV/JSON with source path, output path, detected bounds, render status, and any pose/rig warnings.
- Produce a labeled contact sheet from the rendered PNGs.
- If a model is not rigged or does not have a usable T-pose, render its current pose and mark it clearly as a pose exception; do not fabricate a rig or silently omit it.
- Fail visibly per model and continue with the rest. Never replace source GLBs with render intermediates.

## Blender / CI guidance

Do not commit the Blender executable or a machine-specific Blender installation into Git. Install a pinned Blender release in a CI runner or documented local setup, verify the version, and cache/download it as a build dependency. Keep scripts and configuration in version control; keep generated images as workflow artifacts or in a separate output branch/location. Use the official Blender download and command-line background rendering workflow.

## Safe integration

This is a documentation-only handoff branch based on PR #170's head. It does not modify or overwrite any model, render, workflow, or existing script. Merge it as a separate small PR after review; it can be rebased/retargeted if the main integration branch changes.
