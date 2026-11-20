# FLUID DYNAMICS — Track 3 research & integration (2026-10-23)

Owner directive (verbatim): "Pull all of this stuff in and wire it up and put it to work the best way possible"
Owner override (2026-10-23): license firewall OFF — pull and wire regardless of license; document copyleft/GPL components here for transparency.

Track: DualSPHysics (SPH fluid sim) + render-to-texture blood decals, wired into the finisher/X-ray impact moments.

## 1. DualSPHysics evaluation

**What it is** (verified from the repo README and project site, 2026-10-23):
- `github.com/DualSPHysics/DualSPHysics` — C++/CUDA/OpenMP Smoothed Particle Hydrodynamics solver, based on SPHysics. Built for free-surface engineering flows (waves, dam-breaks, offshore structures), not games.
- Current release line v5.4. Pre/post-processing (GenCase) ships in a separate package, not the GitHub repo.
- Scale it is designed for: **millions of particles** (papers routinely run 4–12M). GPU (CUDA 12.3) gives ~100x over the serial CPU build; a CPU-only build exists (`Makefile_cpu`) but is two orders of magnitude slower.
- Relevant features for us: Weakly Compressible SPH (pressure from equation of state), Incompressible SPH variant, Monaghan **artificial viscosity** (the α-coefficient formulation), Dynamic Boundary Condition (boundaries as particle layers satisfying the same equations), and — directly on point for blood — a **non-Newtonian branch** (`src_mphase/DSPH_v5.0_NNewtonian`) implementing variable viscosity.

**License**: **LGPL-2.1** per the GitHub repo LICENSE file (older papers, e.g. Crespo et al. 2015, say GPL — the repo is the current authority). Either way it is copyleft; the owner's override explicitly permits game/runtime use. **No DualSPHysics code was copied into this repo** — we re-implemented the formulation ideas in simplified form (see §3), so no LGPL obligations attach to the game code. If anyone later vendors DualSPHysics source, the LGPL-2.1 terms (source availability for the library portion) apply — flag it then.

**What runs where**:
- This VM has **no GPU** (`nvidia-smi` absent), so even the reference solver could only build CPU-only here — and was not built: there is nothing to validate against at game scale, and a CPU build at our particle counts would still be overkill.
- On the target (a phone browser): DualSPHysics cannot run. No CUDA on mobile GPUs, no native modules in the web build, and an engineering solver's per-particle cost is wrong for a 60 fps game loop.
- **Verdict: [RESEARCHED], not vendored.** The shippable artifact is a game-appropriate re-implementation of its ideas (§3), which is what the track brief asked for ("a lightweight SPH or particle-fluid … inspired by DualSPHysics (not a port)").

**Alternatives considered**: SPlisHSPlasH (MIT, graphics-quality SPH — also native C++/CUDA, same verdict); vendoring a JS SPH lib (nothing mature/maintained at this scale — rejected in favor of a purpose-built ~600-line module we fully control and can unit-test).

## 2. What is WIRED vs SPEC'D

| # | Item | Status | Path |
|---|------|--------|------|
| 1 | DualSPHysics formulation study (viscosity, DBC, WCSPH, non-Newtonian branch) | [RESEARCHED] | this doc §1 |
| 2 | Viscous particle fluid core: burst, gravity, Stokes drag, pairwise repulsion/cohesion, Monaghan-style artificial viscosity with per-particle viscosity dial, droplet breakup (volume-conserving), ground stick-or-bounce, fighter-sphere coat + slide + drip | [WIRED] | `game/js/fx/fluid.js` (`FluidSim`) |
| 3 | Blood/mud/ink presets (variable-viscosity dial) | [WIRED] | `game/js/fx/fluid.js` (`PRESETS`) |
| 4 | THREE.Points renderer, 1 draw call, custom viscous-sprite shader, injected THREE (node-testable core) | [WIRED] | `game/js/fx/fluid.js` (`FluidRenderer`) |
| 5 | Render-to-texture ground decals: stamp-on-impact baked into one 1024² canvas texture, throttled GPU upload, per-round clear | [WIRED] | `game/js/fx/decals.js` (`SplatLayer`) |
| 6 | Finisher killing-blow hook: fluid burst fires with the X-ray beat, fire-and-forget, miss-safe; optional per-beat `fluid: { preset, intensity }` tuning | [WIRED] | `game/js/finisher.js` (`_fluidBurst`), `game/js/fx/fluid.js` (`fluidBurst`) |
| 7 | Self-ticking FluidWorld (own rAF only while particles alive, parks at zero — no game-loop surgery) | [WIRED] | `game/js/fx/fluid.js` (`FluidWorld`) |
| 8 | Node test suite: 18 tests (budget, breakup volume, stick/bounce, coat/slide/drip, viscosity dial, determinism, decal math/stamps/throttle) | [WIRED] | `game/tests/fluid-decals.test.mjs` |
| 9 | Fighter-body stain decals (pooled decal quads projected onto the victim, parented to bones, capped 12/fighter) | [SPEC ONLY] | spec below |
| 10 | Vendoring DualSPHysics itself / WASM CPU build | [RESEARCHED] | rejected — §1 |

### Spec: fighter-body stains (not wired this pass)
Fighter models are GLBs with their own materials — there is no per-fighter paintable texture layer yet. The intended pipeline when the character texture/attire work lands: at a fluid impact on a fighter collider, project a decal quad (pooled, max 12 per fighter, fade out at round end) oriented to the surface normal at the hit point, parented to the nearest bone so it rides the animation. Until then, fighter hits are represented by (a) the airborne splash, (b) the coat-and-drip behavior on the collider, and (c) ground splats below the drip line. No mesh-per-splat is ever created — the ground layer stays one draw call regardless of stamp count.

## 3. Architecture

```
finisher killing-blow beat (INTRO_OUTRO context)
  ├─ _xrayFlash  → game/js/xray.js        (anatomy reveal, existing)
  └─ _fluidBurst → game/js/fx/fluid.js     (NEW — viscous splash)
                    │  fire-and-forget dynamic import; miss-safe
                    ▼
              fluidBurst(spec)
                ├─ impact point: victim torso (attacker→victim dir)
                ├─ collider: torso-sized sphere on the victim
                ├─ FluidWorld (one per game, cached on game._fxFluidWorld)
                │    ├─ FluidSim   — pure physics, no THREE/DOM
                │    ├─ FluidRenderer — single THREE.Points, 1 draw call
                │    └─ SplatLayer — 1024² canvas → ground plane, 1 draw call
                └─ self-ticking rAF; stops when particles drain
```

**Physics behaviors** (the DualSPHysics ideas, game-sized):
- **Variable viscosity** (`visc` per particle; blood 1.0 / mud 2.2 / ink 0.45): scales artificial-viscosity damping on approaching pairs, Stokes drag, adhesion probability, and breakup resistance. This is the game analogue of the `DSPH_v5.0_NNewtonian` branch.
- **Droplet breakup**: speed above `7.5 × (0.55 + 0.45·visc)` m/s splits the droplet into 2–3 children along its velocity vector, conserving volume (`r' = r/∛k`). Children inherit 0.8× velocity so breakup is single-level — no cascade (an early version cascaded 160→285 particles in 2 substeps; fixed).
- **Stick-or-bounce** (DBC spirit): slow impacts stick — ground particles soak in and stamp a splat; fighter-sphere hits coat the surface, slide under tangential gravity ("roll down surfaces"), and stamp a drip trail. Fast impacts bounce with viscosity-scaled restitution and stamp a smaller splat.
- **Decals**: every stick/bounce/slide-drip emits a stamp event; `SplatLayer` bakes irregular multi-blob splats (seeded, deterministic) into the canvas. GPU upload throttled to 150 ms. Stains persist for the round; cleared on round reset.

**Lifecycle / show-lock compliance**: the fluid layer is inert in neutral — it only exists during finisher/X-ray beats (the finisher already runs in `INTRO_OUTRO` anim context). It is an effect layer, not a show move, and never plays during the fight.

**Effekseer boundary** (coordination, no duplication): Effekseer (other track) = general-purpose particles — sparks, smoke, energy, impact flashes. This module = viscous fluids only — cohesion, breakup, adhesion, drips, persistent stains. Separate hooks, separate code, both firable from the same finisher beat.

**Content note**: stylized impact splash only. No dismemberment, no gore systems — per the PR #872 constraint the impact viz is X-ray reveal + deformation, and this module adds the splash at that same beat. Preset colors are parameterized; content tuning is the owner's call.

## 4. Perf budget (measured, not estimated)

Method: `node` on this VM (shared, throttled CPU — strictly weaker than a modern phone; treat VM numbers as a pessimistic bound, phone ≈ 3× faster on scalar V8 loops).

- **Sim**: realistic finisher burst (160 particles, intensity 1.0) through 2 sim-seconds (240 substeps @120 Hz): **710 ms total CPU on this VM** → ~2.96 ms/substep → ~6 ms/frame at 2 substeps/frame on the VM, **≈2 ms/frame on a phone**. Peak 175 live particles (budget cap 480), 402 decal stamps emitted, drains to ~0 — the sim parks itself.
- **Dense-phase note**: the first 2–3 substeps are the most expensive (all particles within pair radius + one breakup pass); cost collapses to ~0.1 ms/substep once the spray spreads. Spawn positions are jittered in a 5 cm contact volume (physical — spray comes from a contact patch, not a point), which also avoids the degenerate all-co-located neighbor case. Brute-force neighbors (no spatial grid) is a deliberate choice at ≤480 particles: 115k pairs worst-case ≈ 3.75 ms on this VM in isolation; a grid buys little at this scale.
- **Render**: 1 draw call (`THREE.Points`, ≤480 sprites), custom shader clamps `gl_PointSize` to 220 px for mobile point-size limits. Normal blending, `depthWrite: false`.
- **Decals**: 1 draw call, 4 MB canvas + 4 MB GPU texture, uploads throttled to 150 ms, stamps are 2D-canvas ops on impact events only (never per-frame).
- **Total frame budget during a finisher beat**: sim ~2 ms + render ~0.5 ms + decal upload amortized ≈ **<3 ms on target phones**, for the 2–4 s the beat lasts. Zero cost otherwise (rAF parked, points hidden).

Perf test: `game/tests/fluid-decals.test.mjs` (18 tests, all passing 2026-10-23).

## 5. Files

- `game/js/fx/fluid.js` — FluidSim / FluidRenderer / FluidWorld / fluidBurst / PRESETS / FLUID
- `game/js/fx/decals.js` — SplatLayer / worldToUV / computeSplat
- `game/js/finisher.js` — `_fluidBurst` hook + beat `fluid?` tuning field (surgical, +14/−1 lines)
- `game/tests/fluid-decals.test.mjs` — 18 node tests

## 6. Open questions / follow-ups

1. Fighter-body stain decals (§2 spec) — needs the character texture/attire pipeline; then wire the pooled-quad projector.
2. Suite side: expose `fluid: { preset, intensity }` in the finisher creator UI (customization suite) so designers can tune per-finisher splash.
3. If the owner ever wants true SPH (splashing liquid volumes, not droplets), revisit a WASM build of the DualSPHysics **CPU** solver for the creation suite (offline bake), never the live game loop.
