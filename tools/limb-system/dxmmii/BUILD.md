# DXMMII Four-Arm Rig — Build Doc

**Owner order:** Real, 2026-10-16 — production implementation of the limb-system R&D.
**Status:** Rig built, 5-state machine keyed, switch-frame measurements PASS (< 1mm).
**Rig file:** `blend/dxmmii_4arm_rig.blend` (Blender 4.0.2)
**Repro:** `scripts/01_metarig.py → 02_generate.py → 03_build_body.py → 04_states_demo.py`

Reference: `~/workspace/tripo-renders/dxmmii-reference.png` (viewed with own eyes).
Design: `~/workspace/forge3d-pipeline/track1-tripo-recovery/attire-integration/DXMMII-LIMB-SYSTEM-RND.md`
Technique: `RESEARCH.md` (this lane).

---

## What was built

**1. Rigify multi-arm meta-rig (scripts 01–02).** Human meta-rig + 2 extra `limbs.arm`
samples duplicated from the standard arms, socketed at the upper back/shoulder
region (Goro-anatomy layout): roots parented UNCONNECTED to `spine.003` (chest),
translated to socket points at `spine.003.head + (±0.34, -0.26, +0.10)`, pivots
snapped to the 0.05 grid (KatsBits). `bpy.ops.pose.rigify_generate()` produced
`DXMMII_rig` (774 bones) with full FK/IK controls, IK targets, pole targets,
tweak chains, and per-arm `IK_FK` switches for all 4 arms.

**2. Modular mechanical body (script 03).** 39 separate mesh parts (KatsBits
method: one mesh per part, rigidly parented to its DEF bone, no smooth
skinning — DXMMII is a patchwork robot). Patchwork color blocking
(yellow/orange/teal/white), boxy head with X eyes + tongue + boombox + antenna,
hazard band. Extra arms are fully separate objects on their own chains.

**3. Five-state machine per extra arm (script 04, frames 1–300 @24fps).**
Driven DIRECTLY on the repaired DEF bones (pure FK — see design choice 4).

| Frames | State (L / R) |
|---|---|
| 1–48 | ATTACHED / ATTACHED — 4-arm idle, extra arms sweeping |
| 48–72 | ATTACHED / RETRACTING — R folds + parts scale 1→0.001 onto socket |
| 72–96 | ATTACHED / HIDDEN — R invisible at socket; L punches (3-arm mode) |
| 96–132 | ATTACHED / GROWING — socket opens (shape key), R scales back out |
| 132–156 | ATTACHED / ATTACHED — 4-arm flourish |
| 156–168 | DETACH ANTICIPATION (L) — gyro flies to socket |
| **168** | **SWITCH: L DETACHED** — parts reparented to gyro controller, world-preserved |
| 168–228 | GYRO (L floating) / ATTACHED (R) — spring-damper hover + attack sweep baked to gyro |
| 228–240 | REATTACH ANTICIPATION — gyro flies arm back to socket |
| **240** | **SWITCH: L REATTACHED** — parts reparented to DEF bones, world-preserved |
| 240–300 | ATTACHED / ATTACHED — 4-arm victory pose |

**4. Shoulder-socket shape keys.** `socket_open` blend shape on each collar flares
the socket ring during grow (0→1→0, peak mid-grow) — no pop. Stump-cap domes
scale 0.001→1 while an arm is detached — never a hollow hole. Collars stay
visible in 2-arm mode as designed machinery joints.

**5. Gyro animation set (retarget proof).** Procedural spring-damper hover
(k=20, c=5) on the gyro controllers with Lissajous drift + rigid-assembly attack
sweeps (f192–216), baked to keys on the superset skeleton's gyro controllers,
which drive the detached arm chains. The detached arm floats, bobs, lags, and
strikes — then re-docks.

## Switch-frame measurements (TEARDOWN-COMPLETION LAW)

Measured in `measurements.json`. Requirement: detach/reattach switch-frame
delta < 1mm.

| Switch | Part | Delta |
|---|---|---|
| Detach f168 | upper / fore / hand | 0.00012 / 0.00013 / 0.00017 mm |
| Reattach f240 | upper / fore / hand | 0.00039 / 0.00017 / 0.00015 mm |
| Continuity f167→f169 | hand | 0.046 mm (normal inter-frame motion, no pop) |
| Continuity f239→f241 | hand | 0.047 mm (normal inter-frame motion, no pop) |

**PASS.** The detach/reattach is pop-free to sub-micron precision (manual
keep-transform reparenting; Blender's `parent_set(keep_transform=True)` was
found to use the wrong world matrix for bone-parented objects — 304mm pops —
so the switch math is done explicitly and measured).

## Renders

- `renders/dxmmii_state_demo.mp4` — full 300f state-transition demo (eyes-QC'd)
- `renders/dxmmii_turntable.mp4` — 96f 360° turntable of the 4-arm finale pose
- `renders/stills/qc_*.png` — QC stills at every transition frame

## Deliberate rig-design choices (documented, not shortcuts)

0. **Blender 4.0.2 RNA BONE-parenting quirk (root cause of the 2026-10-16
   disassembly defect, fixed).** Setting `parent_type='BONE'` via RNA makes the
   depsgraph AND the renderer parent the object to the bone's TAIL
   (`X = T(posed_tail) @ Rot(pose)`), not the head — proven with minimal
   repros (RNA => tail-based regardless of assignment order;
   `bpy.ops.object.parent_set(type='BONE')` => head-based;
   RNA `parent_type='OBJECT'` => correct). Therefore `matrix_parent_inverse`
   MUST be `(R @ T(tail_local) @ Rot(matrix_local))^-1`, the inverse of the
   TAIL-based rest matrix. The old head-based Pinv shifted every part by one
   bone-vector toward the tail in all renders. Bone roll was investigated and
   ruled out. `true_world_of()` uses the tail-based X — the old head-based
   formula measured sub-micron switch deltas while renders were shifted.

1. **DEF hierarchy repaired; extra-arm DEF chains are pure FK.** Rigify 4.0's
   generation cross-parented the arm DEF chains through `.001` duplicate bones
   (e.g. `DEF-forearm.x.L` parented to `DEF-upper_arm.x.L.001`), which broke FK
   propagation — verified by render: FK controls moved but DEF bones stayed
   frozen. Repaired into clean `upper→fore→hand` chains. All arm-DEF constraints
   (COPY_TRANSFORMS / STRETCH_TO) muted: the DEF skeleton is now the animation
   skeleton, exactly as a game engine drives it. Verified by render: DEF-direct
   keys pose all four arms correctly.
2. **Retract = socket-centric part scaling** (not DEF-bone scaling): parts are
   authored with pivots at the socket, so object-scale collapses each part
   exactly onto the socket point (verified: 0.67mm residual at scale 0.001),
   hidden inside the torso behind the collar. Mathematically equivalent to the
   R&D's bone-scale retract; works the same in a game engine on a plain skeleton.
3. **IK quirk (known issue):** all four arms' `upper_arm_ik` mechanism bones are
   generated static (the `.x.` infix breaks Rigify's MCH naming, so the IK
   solver chain is incomplete on the extras; mains share the pattern). FK is the
   verified animation path. Repair path: re-run generation after renaming extra
   limbs to Rigify-safe names (e.g. `upper_arm2`), or hand-wire the MCH IK
   outputs. Does not affect the state machine, which is FK-driven by design.
4. **Switch math done explicitly.** Blender's `parent_set(keep_transform=True)`
   uses the RNA `matrix_world`, which is wrong for bone-parented objects
   (produced 304mm pops). Detach/reattach reparenting computes the true world
   matrix (`P_bone @ Pinv @ B_basis`) and sets `matrix_basis` directly —
   measured sub-micron switch deltas (see below).

## State transition table (for the game implementation)

Each transition = bone transforms + part scale + one shape key. All states are
plain skeletal animation — no mesh swapping, no visibility hacks.

- ATTACHED → RETRACTING: FK fold (0.4s) + part scale 1→0.001; socket flexes.
- RETRACTING → HIDDEN: hold scale 0.001 at socket (hurtboxes: none for that arm).
- HIDDEN → GROWING: socket_open 0→1; part scale 0.001→1 (0.5s, ease-out); socket closes.
- GROWING → ATTACHED: FK unfold to guard.
- ATTACHED → DETACHED: anticipation (gyro flies to socket, 0.5s); switch frame:
  bake world → reparent chain to gyro controller → stump cap on.
- DETACHED → ATTACHED: gyro flies arm to socket; switch frame: bake world →
  reparent to socket bones → stump cap off; settle.
- Interrupts: transitions are keyframed bone transforms — hit-stun freezes them
  mid-flight safely (bones are bones).

---

## REAL MODEL TRANSFER (2026-10-16) — DXMMII Rig-Completion Worker

**Status:** Transferred to real DXMMII model. 5-state machine rebuilt. Measurements PASS.
**Rig file:** `blend/dxmmii_4arm_rig_REAL.blend` (Blender 4.0.2)
**Repro:** `scripts/01r_fit_metarig.py → 02r_generate.py → 02br_repair.py → 02cr_calibrate_fk.py → 03r_build_real.py → 04r_states_real.py → 05r_qc_real.py`
**Renders:** `renders/real/state_{attached,retracting,hidden,growing,detached}.png` + QC frames
**Measurements:** `measurements_real.json` (pass: true)

### What changed vs proxy

1. **Model:** Real DXMMII from `~/workspace/tripo-recovery/dxmmii.glb` (via `viz/dxmmii_plain.glb`). ONE merged mesh, separated into 621 fragments, rejoined per-bone into 39 DXR_* parts. Model→Rigify rotation Rz(−90°), no mirror (Rigify faces −Y, model faces +X).

2. **Rigify DEF repair (02br):** Rigify's `limbs.arm` generator MISPLACED the DEF arm bones on the fitted metarig (e.g. DEF-upper_arm.L tail at 0.1804 instead of metarig 0.2609) and left wrong rolls (2.0724). Fixed by repositioning DEF head/tail from the fitted metarig AND setting proven rolls (4.7455 upper, 4.9383 forearm/hand — from proxy's working Rigify output). **Critical finding:** for mirrored arm bones (+X vs −X), rolls must be IDENTICAL (not negated) for FK to mirror — empirically verified (R upper with roll 271° raises with Z-, negated roll inverts).

3. **Leg gaps FIXED by construction:** Real geometry covers all 5 DEF leg segments (thigh→thigh.L.001→shin→shin.L.001→foot). Fragments assigned by z-segmentation matching DEF bones. No fake connector parts needed.

4. **Detach playback FIXED via basis-baking:** Parts stay bone-parented entire timeline. Detach window f168–240: per-frame basis `B_f = Pinv⁻¹ @ Xb⁻¹ @ R⁻¹ @ (Pg_f @ Pg_168⁻¹ @ W_168)` keyed as loc/quat/scale. Zero switch delta by construction (B_168 = pre-bake basis exactly). Measurements: detach switch 0.000031mm, bake max recompose 0.000241mm.

5. **FK recalibration (02cr):** With corrected rolls: upper Z− raises, forearm Z− bends (was Z+/X− with wrong rolls). 04r updated accordingly.

### Known limitations
- Face/finger Rigify controls unplaced (DEF skeleton is the deliverable; face bones left at default).
- Main-arm shoulder seams articulate as mechanical joints (by design — KatsBits).
- f240→f241 shows 1.36mm bone-driven settle motion (smooth, not a teleport — documented in measurements).
