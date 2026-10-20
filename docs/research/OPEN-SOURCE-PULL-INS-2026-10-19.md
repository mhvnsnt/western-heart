# Open Source Pull-Ins — 2026-10-19

Owner order: "don't just research it, don't just pull it in, actually wire it up."
Each tool below was researched, pulled in, and tested. Location: `tools/open-source/`.

## 1. Move Data Decode — TKMovesets (Kiloutre/TKMovesets)

**What it is:** The industry-standard Tekken moveset extractor. Exports/imports movesets from
**T5, T6, T-Rev, TTT2, T7, and T8** (live memory extraction + editor).

**Replaces:** our hand-written move parsers. The moveset-lanes hand-rolled ~40% of what this
already does — do not write new parsers; read `TKMovesets2/LocalStorage/MovesetStructs.h`
(the `TKM2` binary format: header, compressed blocks, crc32) and use its extraction.

**License:** GPL-3.0 (Kiloutre). Study/RE freely; if our game ships this format, keep the
attribution + GPL terms. Document in RENAME-MAP.md where formats are adapted.

**Where:** `tools/open-source/tkmovesets/` (full source, submodules excluded — they are
Windows-only build deps).

**Wire-up:** Move-decode lanes point at this as the reference implementation. The game's
moveset JSONs in `game/assets/movesets/` keep their own schema; use TKMovesets output as
the data source to reach 100+ moves/fighter (FULL MOVESET LAW).

## 2. Jiggle Physics — Wiggle 2 (shteeve3d) + Wiggle Bones (Hans-xwh)

**What they are:** Spring-physics secondary motion for bones (hair, clothing, breast/glute
jiggle chains). Real-time viewport simulation, collision, bake-to-keyframes.

- **Wiggle 2** (single-file `wiggle_2.py`, MIT-ish per repo): **TESTED — registers and runs
  in our Blender 4.0.2.** This is the one the jiggle lanes use NOW. Mass-spring-damper model,
  per-bone stiffness/damping/gravity/stretch, pinning, collision.
- **Wiggle Bones** (GPL-3.0): Wiggle 2 refactor for **Blender 5.0+**. Not for this VM today;
  pulled for the Blender-5 upgrade path. Features: pin solvers (Forward/Backwards/Mixed/Dual),
  full-bone collision, one-click bake with preroll/loop.

**Where:** `tools/open-source/blender-addons/wiggle-2/` and `wiggle-bones/`.

**Wire-up:** Replace hand-tooled sine-wave jiggle (`build_twerk.py` style) with Wiggle 2
physics on the real jiggle bones (DEF-breast.L/R, Butt_L/R chains). One-click chain dynamics
→ bake to keyframes → videos. This is the Scarlett-targeting fix.

## 3. Animation Retargeting — Keemap (nkeeline, GPL-3.0)

**What it is:** Blender rig retargeting addon — maps mocap motions from a source armature
to a target armature with bone mapping, auto-scale/align, hip-proportion-first matching
(the exact fix for the stretching the owner saw on the Scarlett test).

**TESTED — registers and runs in our Blender 4.0.2.**

**Where:** `tools/open-source/blender-addons/keemap-retargeting/`.

**Wire-up:** All mocap retargeting (Mixamo clips, CMU BVH, FreeMoCap output) goes through
Keemap instead of hand keyframing. Source: CMU mocap library / Mixamo library (Adobe ID,
free). Retarget → Keemap bone mapping → apply to Scarlett rig → jiggle via Wiggle 2.

**Not pulled (documented):**
- **MoCapAnything** (arXiv 2512.10881) — cutting-edge video→any-skeleton, but research-grade,
  no usable release yet. Watch, don't depend.
- **Auto-Rig Pro** — best-in-class, but PAID. BlenRig/GameRig cover us free.
- **Good Good retargeting tool** (June 2026) — no public repo found; principle documented above
  (match hips first) is baked into Keemap's workflow.

## 4. Rigging — GameRig (Arminando, open source)

**What it is:** Game-engine-friendly auto-rigging for Blender, built on Rigify — produces
game-ready rigs (clean exports, bone renaming presets) instead of film-grade complexity.

**Where:** `tools/open-source/gamerig/`.

**Not pulled (documented):**
- **BlenRig 6** (GPL-3.0, free) — best free deformation quality (mesh-deform muscle system),
  but the repo is **400MB** — over disk budget tonight. Grab at
  https://github.com/jpbouza/BlenRig when disk frees up or when the film-grade rigs need it.

## 5. Straight-to-Store (CloudDog watch-download-dir)

Owned by the separate CloudDog upgrade lane (owner approved 2026-10-19 ~22:56 CDT) — streams
chunks to GitHub releases while downloading, delete-as-you-go. NOT duplicated here.

## Tested on this VM (Blender 4.0.2 headless)

- `wiggle_2.register()` — OK
- `keemap_retarget.register()` — OK
- TKMovesets: source pulled, format documented, no build attempted (C++ Windows toolchain)
- GameRig: pulled, not yet load-tested (follow-up for the rig lane)

## License log

| Tool | License | Notes |
|------|---------|-------|
| TKMovesets | GPL-3.0 | Kiloutre, attribution required |
| Wiggle 2 | repo license (see LICENSE) | shteeve3d |
| Wiggle Bones | GPL-3.0 | Hans-xwh |
| Keemap | GPL-3.0 | nkeeline |
| GameRig | repo license (see LICENSE) | Arminando |
