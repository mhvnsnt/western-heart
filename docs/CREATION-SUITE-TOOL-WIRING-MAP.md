# Creation suite — tool-to-menu wiring map (2026-10-22)

Every tool in `tools/` placed under the suite menu/submenu where it belongs.
Wired = the menu option invokes the tool end to end (in-browser where
possible, otherwise a real queued job with live status via
tools/suite-jobs/). No dead buttons.

Suite surfaces: **create-fighter** (`customization/create-fighter/`, the
Create New Fighter hub) and **creation-suite-ui**
(`customization/creation-suite-ui/`).

## Menus and their tools

### TEMPLATE (template-select screen)
| Tool | How it's wired |
|---|---|
| `tools/mb-lab` | "Re-bake this template" per card → `mb-lab` job with the card's `mb_lab` spec; "Bake new template" → job form |
| `tools/suite-jobs` | queue + status behind every bake |

### BODY
| Tool | How it's wired |
|---|---|
| `tools/mb-lab` | MB-Lab morph slider group (live preview + fighter JSON) + "Generate base body" job |
| `tools/mpfb2` | MPFB2 target slider group (data path, works now) + "MPFB2 live bake" job (needs Blender 4.2+) |
| `tools/procgen/gltf-delivery` | procedural body-part delivery (where applicable) |

### FACE
| Tool | How it's wired |
|---|---|
| `tools/gnm` | "Bake GNM head" job (identity/expression/pose → head GLB) + GNM preset picker (data path, works now) |
| `tools/mb-lab` | MB-Lab face-morph sliders (unified with GNM — one face system) |

### RIGGING (LIMBS tab + jobs)
| Tool | How it's wired |
|---|---|
| `tools/auto_rig` (GameRig backend) | "Auto-rig" job on the current fighter GLB |
| `tools/open-source/gamerig` | vendored GameRig feature set used by the above |
| `tools/jiggle` (`wiggle2_jiggle.py`, `jiggle_physics_bake.py`) | "Bake jiggle" job (Wiggle 2 spring chains on jiggle bones) |
| `tools/rig_repair` | "Repair rig" job (defect taxonomy cases) |
| `tools/limb-system` (DXMMII) | 4-arm limb controls (already in LIMBS tab) |
| `tools/open-source/blender-addons/keemap-retargeting` | mocap retarget jobs |

### SKIN / TEXTURE
| Tool | How it's wired |
|---|---|
| `tools/texture-pipe` (`bake_pbr_blender.py`, `apply_pbr_set.py`) | "Bake PBR set" job |
| `tools/customization/skin-library` | skin browser (already in suite) |

### HAIR
| Tool | How it's wired |
|---|---|
| `tools/mb-lab` | "Generate hair (MB-Lab hair engine)" job |

### ATTIRE / PARTS (ATTIRE tab, WARDROBE tab)
| Tool | How it's wired |
|---|---|
| `tools/partposer` (`partposer.html`) | "Position part in 3D" — linked from the item detail panel |
| `tools/model-3d-placement-tool` | "Place part (viewport)" — linked from the item detail panel |
| `tools/customization/*` (`apply_customization.py`, `build_parts_index.py`, …) | parts index rebuild jobs |
| `tools/creation-suite` | legacy suite UI (reference) |

### IMPORT
| Tool | How it's wired |
|---|---|
| `tools/tripo-pull` | "Pull Tripo model" job (URL → GLB, no sign-in) |
| `tools/tripo-intake` (`intake.py`) | "Intake model" job (facing check, normalize, queue) |
| `tools/triposr` | "TripoSR fast mesh" job (image → 3D) |
| `tools/stable-fast-3d` | "Stable Fast 3D" job (image → 3D, alt backend) |
| `tools/cue4parse` | "Extract UE pak" job (.pak/.uasset → glTF) |
| `tools/import_model.py` | "Import model file" job (fbx/obj → GLB normalize) |
| `tools/model-audit` | "Audit model" job (skinned/unskinned, bind check, facing cues) |
| `tools/render-prep` | "Prep for Blender" job (never feed raw Tripo GLB to Blender) |
| `tools/watermark-removal` | "Remove watermark" job (asset cleanup) |

### EXPORT
| Tool | How it's wired |
|---|---|
| `tools/gltfpack` | "Optimize GLB" job (size report in status) |
| `tools/anim/gltf_codec.mjs` | glTF-Transform + meshoptimizer encode jobs |
| `tools/render-prep` | Blender batch cleanup jobs |
| `tools/tpose-render` | "Render T-pose proof" job (PNG proof per model) |

### CHARACTER (PROFILE tab)
| Tool | How it's wired |
|---|---|
| `tools/character-voice` | voice pick / cleanup chain (Chatterbox default) |
| `tools/dxmmii-poser` | limb-system pose widget |

### JOBS (JOBS tab)
| Tool | How it's wired |
|---|---|
| `tools/suite-jobs` | the queue itself: submit, poll, load results |
| `tools/proof-harness` | "Screenshot proof" jobs (Playwright + Chromium) |
| `tools/setup` | toolchain status (what's installed) |

## Tools with no creation-menu home (documented)

These are build-time fight/asset pipelines, not creation tools. They stay
in `tools/` (labeled, documented) but get no suite menu — putting them
there would be a launcher, not a creation flow.

| Tool | Why no menu home |
|---|---|
| `tools/moveset-*` (decode/expand/merge/restore/coverage) | Fight-data build pipeline. The suite's MOVESET *tab* assigns moves; these tools *build* the move database offline. |
| `tools/anim` (T3 banks, gltf_codec covered above) | Fight animation banks. |
| `tools/anim-retarget` | Clip retargeting for the fight engine. |
| `tools/netcode` | Multiplayer infrastructure. |
| `tools/re` (+ Ghidra) | Reverse-engineering bench. |
| `tools/ur-texcrack`, `tools/stage-arena-pull` | Stage/arena pipeline (arenas have their own lane). |
| `tools/procgen` (arena-gen, game-score) | Procedural arenas/scores. |
| `tools/ai-inference` | Game-side AI. |
| `tools/wire-fighter`, `tools/roster` | Roster build-time wiring. |
| `tools/open-source/tkmovesets` | Moveset format reference (docs). |
| `tools/fetch_*.py`, `tools/gen-movesets-t3.py` | Frame-data pulls (reference data). |

## Named in the directive, not in tools/ (status)

| Tool | Status |
|---|---|
| Build-A-Bod | Referenced in intake notes; **no verifiable open-source upstream found** in this pass (niche creator addon). NOT pulled — documented, not stalled. Body-scaling is covered by MB-Lab morphs + MPFB2 targets meanwhile. |
| NaughTyRig | Same — no verifiable upstream; NOT pulled. Rigify feature-set role covered by GameRig (vendored) + Wiggle 2 spring chains meanwhile. |
| Fluid Painter (NSFW) | Same — no verifiable upstream; NOT pulled. Texture-paint role covered by `tools/texture-pipe` meanwhile. |
| UModel | Classic UE viewer; CUE4Parse covers the extraction job. UModel stays a manual companion (no CLI to wire). |

If upstream URLs for the three pending addons surface, they get the standard
fetch-script + menu treatment (BODY / RIGGING / SKIN rows above).
