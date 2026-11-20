# Project Chrono — physics evaluation for Western Heart's grappling lane

**Track 4, advanced-systems integration — 2026-10-23**
**Owner directive (verbatim):** "Pull all of this stuff in and wire it up and put it to work the best way possible"
**Status legend:** [WIRED] = in the game, tested · [RESEARCHED] = evaluated, not in the game · [SPEC ONLY] = documented path, not built

---

## 1. Verdict up front

**AUGMENT, not replace.** Chrono fills exactly one gap in WH's physics stack — articulated joint constraints with torque readout for grappling — and nothing else. cannon-es keeps the visuals-only rigid bodies, Jolt keeps the soft tissue, the PhysicsServo spec keeps the muscle layer. The full Chrono C++ engine is [SPEC ONLY] (documented build path); what is [WIRED] is a deterministic, dependency-free JS joint-constraint module modeled on Chrono's `ChLink` architecture, purpose-built for joint-locks, submission chains, and real-time muscle-strain calculation.

## 2. What Project Chrono is [RESEARCHED]

- **Source:** `github.com/projectchrono/chrono` — multibody dynamics engine out of the University of Wisconsin SBEL lab, used for robotics, vehicle, and granular simulation.
- **License: BSD-3-Clause (permissive).** Verified via the project's Coverity record and distribution pages (October 2026). No copyleft; compatible with a public repo. (Standing note: the user lifted the license firewall entirely on 2026-10-23 — "pull and wire everything regardless of license" — so this is documented for transparency only, not as a gate.)
- **What it offers beyond Rapier/cannon-es/Jolt for OUR needs:**
  - **Joint taxonomy as first-class citizens.** `ChLinkLockRevolute/Spherical/Prismatic/Universal/Cylindrical/Free/PointLine/PointPlane`, `ChLinkBushing` (6-DOF), `ChLinkTrajectory`. Rapier has joints too, but Chrono's links are constraint objects with **force/torque readouts** (`Get_react_force()` / `Get_react_torque()`) — the torque-calculation-node concept this track needed comes straight from Chrono's API design.
  - **ChLinkEngine** — torque / speed / position / keyed-polynomial motors on a joint's free DOF (`ENG_MODE_TORQUE`, `ENG_MODE_SPEED`, `ENG_MODE_ROTATION`). This is the "attacker applies the lock / defender resists" primitive.
  - **ChLinkTSDA / ChLinkRSDA** — translational/rotational spring-damper actuators = the muscle model with runtime-variable stiffness/damping.
  - **DVI solver** (differential variational inequality: `ChSolverPSOR/BB/MINRES`) — handles stiff, over-constrained joint chains without exploding. This is the solver philosophy the JS module borrows (realized as sequential impulses, the standard game-engine form of the same idea).
  - **Chrono::FEA** (finite elements) and **Chrono::Vehicle** exist but are out of scope for this track — noted as future lanes in §7.

## 3. Replace vs augment — the architecture decision [RESEARCHED]

| Domain | Engine | Why it stays | Chrono's role |
|---|---|---|---|
| Arena props, impact debris, KO tumble (visuals-only) | **cannon-es** (MIT, vendored, pure JS) | Zero-dep, zero boot cost; combat never reads it (determinism law). 2026-10-22 decision log: cannon-es chosen over Rapier deliberately. | None — no overlap |
| Muscle deformation under skin (XPBD volumetric soft body) | **Jolt** (`jolt-physics.wasm-compat`, MIT, vendored) | Coarse lattice sim already wired in `game/js/softbody.js` | None — Chrono FEA is heavier than needed |
| Muscle servos (per-limb PD, driveScale blend, runtime-variable stiffness) | **PhysicsServo spec** (Gang Beasts research) | The Euphoria-equivalent muscle layer; my module FEEDS it targets | Consumer of my module's output |
| **Joint-locks, submission chains, multi-step ground transitions, torque nodes** | **ChronoGrapple (this track)** | **The gap**: neither cannon-es (visuals-only) nor Jolt (soft tissue) does articulated joint constraints with torque readout | **Chrono's lane** |

**Why not the full Chrono C++ → WASM build:** Chrono ships no maintained JS/npm package. The official path is a from-source Emscripten build (15–25 min, documented in §6). A multi-MB WASM engine is the wrong tool for a subsystem that needs ~6 bodies and must be **bit-deterministic for netplay rollback** — a small purpose-built solver with fixed substeps and fixed iteration counts is deterministic by construction, speaks the game's units, and plugs directly into the PhysicsServo layer. The WASM path stays [SPEC ONLY] for future lanes (4-armed fighters, vehicles, FEA flesh).

**Correction to the track brief:** the brief said "Rapier3D already in use" — on-disk, the rigid-body layer is **cannon-es** (per `docs/decisions/2026-10-22-integration-unwired.md` item 5, Rapier was evaluated and deliberately not pulled). The EUPHORIA-PHYSICS research doc references Rapier as the vision-stack equivalent. This doc records the on-disk reality.

## 4. What is [WIRED]

**`game/js/chrono-grapple.js`** (~700 lines, zero dependencies, no top-level `three.js` import — node-testable like `softbody.js`):

- **Joint taxonomy** (`ChronoLink`): `FIXED` / `SPHERICAL` / `REVOLUTE` / `PRISMATIC` / `UNIVERSAL`, modeled on `ChLinkLock*`. Linear rows solved as 3×3 block impulses (closed-form symmetric inverse); angular rows as scalar axis-alignment rows. Fixed substeps (2× per 1/60 tick), fixed iteration count (12), Baumgarte 0.1 — deterministic.
- **`ChronoEngine`** (`ChLinkEngine` analog): `TORQUE` / `SPEED` / `POSITION` modes on a revolute joint's free DOF. The attacker's lock drive and the defender's resistance.
- **`ChronoSpring`** (`ChLinkTSDA/RSDA` analog): linear + angular spring-damper with **runtime-variable stiffness/damping** — the muscle model (Euphoria lesson: stiffness is the control signal).
- **Torque nodes**: per-link `reactionForce` / `reactionTorque`, the `Get_react_force()/Get_react_torque()` analogs, accumulated from constraint impulses each substep. Two readout doctrines, both documented in code: arm locks read the **attack link** (the attacker forms the lever); chokes read the **anatomical neck joint's axial compression** mapped through a gameplay squeeze lever (0.18) into torque units.
- **`MuscleStrain`**: real-time muscle-strain force calculation per target joint. `JOINT_TOLERANCE` table (N·m gameplay-tunable caps: neck 55, shoulder 95, elbow 75, wrist 35, hip 130, knee 125, ankle 65 — order-of-magnitude from sports-biomechanics literature, **balance numbers, not medical claims**). Strain accumulates above a 0.55 danger floor, recovers below it; progress ≥ 1 ⇒ tap-out; ratio ≥ 1.5 sustained 0.25 s ⇒ bone-snap. Defender escape torque subtracts from the effective load.
- **`SubmissionChain`**: data-driven multi-step ground transitions (`CHAINS`: armbar, kimura, triangle, rear-naked choke — data, not hardcode, like the rank ladder). Each step: lock joint + type, torque band to HOLD, dwell time, defender escape inputs. Out-of-band torque bleeds dwell; escapes route out; terminal step fires tap.
- **`GrappleRig` + `ChronoGrapple` facade**: defender arm (shoulder/elbow) + head/neck bodies on kinematic torso anchors; `startChain()` / `stepCombat(fixedDt, {defenderInput, escapeTorque})` (authoritative combat tick) / `update(dt)` (cosmetic render-frame solve, no-ops while idle) / `getServoTargets()` → per-limb `{targetAngle, stiffness, damping, driveScale}` for the PhysicsServo PD controllers (null while idle — zero cost).
- **Determinism contract**: no `Math.random`, no wall clock, no allocation-order dependence. Asserted by test (`identical runs ⇒ identical snapshots`).
- **Measured behavior** (all four chains run entry → control → lock → tap with in-band torques, no snaps): armbar taps at ~2.1 s control, kimura ~2.2 s, triangle ~2.4 s, RNC ~2.0 s.

**Tests:** `game/tests/chrono-grapple.test.mjs` — 18 tests, all green: joint taxonomy (fixed weld, spherical free-spin, revolute hinge isolation), engine speed servo, spring contraction, torque-node weight readout (≈ m·g), determinism, strain accumulate/recover/tap/snap/escape, chain advance/bleed/escape/terminal, full-rig chains (all four tap), escape input, servo contract null/live/null.

**Wiring:** `game/js/integration.js` block 8 — lazy `tryInit('grapple', './chrono-grapple.js', …)` + `S.grapple.update(dt)` in the frame loop. The fight state machine calls `stepCombat` on the combat tick (contract documented in the module header; fight-logic lane owns that call).

## 5. What is [RESEARCHED] (not wired)

- Full Chrono evaluation (§2), license verification (BSD-3-Clause), joint/solver taxonomy mapping, the replace-vs-augment architecture table (§3), torque-readout doctrines, joint-tolerance sourcing notes.
- The Euphoria interplay: this module is the **joint-constraint authority** the Euphoria-style behavior layer was missing — stiffness-modulating behaviors (flinch/stumble/brace) drive the PhysicsServo muscles; the grapple module drives joint locks with torque feedback. They compose: a stunned defender's servo stiffness drops, so the attacker's lock torque reads higher, so submissions finish faster. That composition is designed but not yet wired (behavior library is still the documented gap).

## 6. What is [SPEC ONLY] (documented path, not built)

**Full Chrono C++ → WASM vendor path** (official tutorial: `https://api.projectchrono.org/tutorial_install_chrono_emscripten.html`):
1. Install Emscripten (`emsdk`), Eigen ≥ 3.4 (header-only), CMake, Ninja.
2. `git clone -b master [email protected]:projectchrono/chrono.git`, then `git switch --detach <latest release tag>` (10.0.0 at time of writing).
3. `mkdir build && cd build && emcmake ccmake -G Ninja ..` — set `EIGEN3_INCLUDE_DIR`, enable optional modules for WebGL visualization as needed.
4. `ninja` (15–25 min) → per-demo `.wasm` + `.js` glue in `bin/`.
5. To use it for grappling (not just demos), write a C++ embind layer exposing a grapple-specific API (bodies, `ChLinkLock*` joints, `ChLinkEngine`, `Get_react_torque`), then a JS facade mirroring `game/js/chrono-grapple.js`'s interface so the game code doesn't change.

**When to revisit:** 4+-limb fighters (Chatur/Rahkasa's four arms are a natural multi-body chain), stage vehicles, or FEA-grade flesh — i.e., when the subsystem outgrows ~dozens of bodies. Until then the JS module is the right size.

**Also [SPEC ONLY]:** Chrono::FEA soft-tissue (Jolt covers it), Chrono::Vehicle (no vehicle stages scoped), PyChrono tooling-side validation of chain choreography (possible future: validate submission chains in Python before wiring).

## 7. License transparency note

Chrono = BSD-3-Clause (permissive, verified October 2026). No GPL/copyleft components were introduced by this track — the wired module is WH-original code inspired by Chrono's architecture, not a Chrono derivative. Per the user's 2026-10-23 override the license firewall is off regardless; this is recorded for transparency only.

## 8. Open questions for the owner / other tracks

1. **Joint tolerance tuning** — the `JOINT_TOLERANCE` numbers are starting values. The owner tunes feel: taps should feel earned, snaps rare.
2. **Fight-logic wiring** — `stepCombat` needs the combat tick + defender escape inputs (the escape minigame UI). Fight-logic lane owns this.
3. **Behavior-layer composition** — Euphoria-style stiffness behaviors × grapple torque (stunned ⇒ easier submissions) is designed, not wired.
4. **More chains** — kneebar, ankle-lock, omoplata, twister are data additions to `CHAINS`, no code changes.
