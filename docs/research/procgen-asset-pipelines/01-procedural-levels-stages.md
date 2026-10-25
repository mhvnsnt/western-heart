# 01 — Procedural Levels / Stages (2026 research)

**Date:** 2026-10-16 · **Branch lane:** procgen + asset pipelines → `mhvnsnt/western-heart`
**Scope:** open PCG for fighting-game stages / brawler arenas that outputs Godot- or Three.js-usable scenes.

## What we found

### GDQuest `godot-procedural-generation` (gdquest-demos/godot-procedural-generation)
- The canonical open PCG reference for Godot 4: RandomWalker (Spelunky-style chunk walker),
  BasicDungeonGenerator (rect + organic rooms + corridors), WorldMap (shader-driven biomes/rivers),
  ModularWeapons (stackable modifiers — Binding of Isaac style), infinite/white-noise/blue-noise worlds.
- License: **dual — MIT (code) + CC-BY 4.0 (art assets)**. Verified from repo LICENSE via GitHub API.
- Status: 1,930 stars, pushed 2026-06-26. Active enough as a reference; algorithms are stable.
- **Pull decision: PULL (algorithms).** Not vendored whole — the WH arena generator
  (`tools/procgen/arena-gen/wh_arena_gen.py`) ports the walker/BSP ideas into a stage-focused
  tool that emits both Godot `.tscn` and Three.js JSON. This is wired, tested, and in this PR.

### polyblast-arena (mohamed3042) — DROPPED
- Was the best fighting-arena-specific find: Godot 4.7 arena FPS with a **procedural Blender
  headless asset pipeline** (`tools/asset_gen/`: shared `style.py` + `gen_*.py` per asset family,
  GLB export with triangle-budget QA). Exactly the pattern our stage pipeline should copy.
- **Repo 404s on GitHub (gone/private).** Cannot pull. Documented here so the pattern survives:
  headless Blender scripts → palette/material primitives → GLB → budget QA → Godot import.
  Our `tools/` already has Blender headless experience (TOOLS.md: `xvfb-run -a`); a
  `gen_stage_*.py` family can be built on this pattern later without the upstream.

### fragline (ipsamurai) — pattern reference
- Godot 4.7 web arena shooter, **levels as ASCII art** in `src/data/maps.gd`; builds collision,
  decoration, item spawns, and bot nav-graph from text; every map mirrored for fairness.
- Relevant to us: fighting stages must be **symmetric/fair** — ASCII-art stage layouts are a
  cheap, version-controllable authoring format. Our arena generator supports a text-layout
  input mode for this reason. (No pull — pattern documented.)

### Fighting-game-specific PCG: the honest gap
- No maintained open project does **fighting-game stage generation** specifically (ring/arena
  with spawn symmetry, wall-splat zones, breakable props, crowd). Dungeon/roguelike PCG
  dominates the open space. The fighting-stage layer (symmetry constraints, interactables,
  camera bounds) is WH-specific code we write on top of generic PCG — which is what
  `wh_arena_gen.py` does.

## Wire-up
- `tools/procgen/arena-gen/wh_arena_gen.py` — seeded arena generator: platform layout,
  symmetric spawn points, wall/interactable zones, crowd instancing markers; emits
  Godot 4 `.tscn` and Three.js scene JSON. Tested (see tools README).
- Docs: this file. Index: `docs/research/procgen-asset-pipelines/README.md`.
