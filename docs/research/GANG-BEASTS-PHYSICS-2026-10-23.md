# Gang Beasts physics technique spec for Western Heart partial-ragdoll

- **Date:** 2026-10-23
- **Game:** Gang Beasts (Boneloaf, Unity)
- **Owner instruction:** "Perfect for added physics to our Tekken style game and heart and mind inside mode"
- **Scope:** TECHNIQUE EXTRACTION ONLY — no game files were pulled (no Steam credentials on this VM; not needed here). Every substantive claim cites a public source. Game names appear only in this technical file, never in canon.

## 1. What Gang Beasts actually does (cited findings)

### 1.1 There is no keyframed animation — the character IS the ragdoll, always

Boneloaf had no animator on the team, so instead of authored animations they built the game on physics from day one: "because we don't have an animator, we can't make smooth animations and stuff — so let's try it with physics" (James Brown, MCV/Develop interview). The studio built **its own rigid-body animation system** on top of Unity's default physics (PhysX); all movement, climbing, and throwing is driven by it — no motion capture, everything physics-driven (early press/ dev profile). This is the canonical "active ragdoll" pattern, also called "procedural animation": the skeleton is a set of rigid bodies joined by joints, and *control* means applying joint torques/forces toward targets — the character never leaves physics simulation. The community analysis of the technique puts it plainly: it requires "full local-based torque-driven movement with a custom physical movement component," not kinematic animation (Unreal Engine forums thread on recreating Gang Beasts / Human Fall Flat characters).

**WH takeaway:** GB is the extreme end of the spectrum — 100% physics, 0% authored animation. WH goes the opposite way by design: authored animation is authoritative (Tekken feel), and we borrow GB's *control mechanism* (torque-driven joint servos) as the physics overlay, not its rejection of animation.

### 1.2 The control mechanism: drive targets = joint-torque PD servos

Unity's own documentation for `ConfigurableJoint` describes exactly the building block these games use: a **Target Rotation** ("the orientation that the joint's rotational drive should rotate towards") plus an angular drive defined by **Position Spring** ("the spring torque that rotates the joint towards its target position") and **Position Damper** ("reduction of the spring torque in proportion to the speed of the joint's movement… dampen oscillations"). Spring torque proportional to position error plus damping torque proportional to velocity is literally a **PD (proportional-derivative) controller** implemented as joint torque — the industry-standard "active ragdoll" mechanism. Community active-ragdoll implementations show the same math in code form: per bone, `force = stiffness × displacement − damping × velocity` (Hooke's law on position error and rotation error), applied as force/torque each physics step (Godot community active-ragdoll implementation; identical structure to Unity joint drives).

So: **input → target poses → joint servos → torques → motion.** The "wobble" is what happens when servo stiffness is deliberately low and masses/inertias are high — the targets move instantly but the bodies lag and overshoot. The floppy look is a *tuning choice*, not an accident.

**WH takeaway:** This maps directly onto our Rapier layer. Rapier has no Unity-style "drives," but the equivalent is explicit: each physics step, for each servo-controlled limb, compute PD torque from (target pose from the authored animation − current physics pose) and apply via `apply_impulse`/`apply_torque_impulse`. Stiffness/damping constants are per-joint tuning knobs — the same role as Unity's Position Spring/Position Damper.

### 1.3 Punching/attacking = impulse + momentum, not animations

"When you press the punch button, the game calculates the force and trajectory based on your character's current momentum and balance" (diffsense breakdown). Tapping a grab button throws a punch; holding it grabs. Attack feel comes from impulses applied to the limb chain, scaled by body momentum — which is why the same input lands a KO one moment and a limp slap the next. GB has three target "weak spots" — head, stomach, crotch — and diving attacks (hold attack mid-air / while running) get a damage multiplier but also make the *attacker* take more damage (Steam community mechanics write-up). Weak-spot hits and diving strikes are what trigger instant KOs.

**WH takeaway:** In WH's Tekken frame, attacks are authored moves with hit frames — but the *reaction* layer should borrow GB's rule: the physics impulse delivered to the victim's struck limb scales with attacker limb velocity at contact (momentum transfer), and weak-spot/counter-hit bonuses map to our existing counter-hit system. The attacker-side risk (diving = take more damage) is a ready-made design precedent for WH's risk/reward on committal moves.

### 1.4 Full ragdoll vs. animated control: the knockout (KO) state machine

GB's KO mechanic is documented precisely on the Gang Beasts wiki and corroborated by players:

- Each Beast has **100 HP**; strikes, props, and environmental collisions deplete it.
- KO triggers two ways: **HP hits 0**, or **≥40 damage in a single frame** (instant KO regardless of remaining HP — this is why diving headbutts/dropkicks and heavy props insta-KO).
- While KO'd: the character **cannot act at all** — drive targets are effectively off, full ragdoll. Signified by closed eyes + a unique sound. The Beast **cannot take damage while KO'd** and **always wakes with full 100 HP**.
- **KO duration scales with (a) recent KO count and (b) the strength of the finishing hit**, capped at **6 seconds**. Staying awake gradually decays the KO-time penalty. **Mashing attack/jump buttons wakes the Beast slightly faster.**

This is GB's answer to "when does full ragdoll take over vs. animated control": the joint-servo drives are **scaled by a per-character state envelope** — 1.0 when conscious, ~0.0 when KO'd, ramping back on wake. There is no separate ragdoll asset and no kinematic swap; the same bodies just stop being driven.

**WH takeaway:** Our partial-ragdoll already follows this shape — physics takes over the struck limb/landing, then blends back in 0.25–0.4 s. GB validates the architecture and adds two refinements: (1) the envelope should be **per-limb, not per-character** — the struck arm's drive goes to ~0 while the legs keep driving (balance); (2) a **threshold-triggered full-body cut** for launchers/KOs: if a single hit exceeds a damage threshold (GB's analog: 40/100 = 40% of max HP in one frame), cut all drives for a short, mash-shortenable KO window instead of the standard 0.25–0.4 s blend. Do not copy the 100 HP / 6 s numbers — they're GB's tuning; WH maps the *ratios* (instant-KO at ≥40% max-HP single-frame damage; wake always at full HP; KO time scales with hit strength, capped short).

### 1.5 Balance, falling, and getting up

Community technical analysis of GB-style characters treats balance as an inverted-pendulum problem: compute center of mass (COM), project to the support polygon, feed the balance error into the joint PD controllers as corrective torque targets (game-physics coursework describing the standard active-ragdoll balance technique). In GB specifically, knockdowns happen when impulses push the COM outside what the leg servos can recover; recovery is emergent — the servos re-assert the standing target pose and the body rights itself if the drives are strong enough relative to the disturbance. Held buttons double as posture states (hold kick = lie down, hold headbutt = duck/crawl, hold jump = run/sit), i.e., sustained inputs retarget the servo pose set (GMRU controls guide).

**WH takeaway:** Implement a **balance servo on the root/pelvis rigid body**: each step, compute COM vs. support polygon (feet positions); if outside, add corrective torque/impulse toward the upright target (inverted-pendulum correction) and trigger a authored stumble/recover animation whose pose becomes the new servo target set. Small disturbances → stumble step (animation authoritative, servo assists). Large disturbances → the per-limb drive cut from §1.4. This is how "physics takes over the landing" stops looking like a glitch and starts looking like Tekken's existing crumple/launch animations with physical follow-through.

### 1.6 Grabbing and climbing

In GB, grabbing is a constraint between bodies: hold grab near a target and the hands attach (hold = grab, tap = punch). Climbing works by alternating: hold both grabs, hold lift to pull up, alternate releasing each hand — i.e., two hand constraints toggled in sequence plus an upward drive target on the torso (PSN trophy guide controls write-up). Throwing is pure momentum transfer: grab with both hands, lift, build velocity by walking/spinning, release — the engine carries the held body's kinetic energy into flight (diffsense throwing guide). Notably, throws don't use a scripted animation; release timing + body momentum determine the arc.

**WH takeaway:** GB-style grabbing is the right model for WH's wrestling systems (the user's Fire Pro pull: grapples, lifts, carries): a grab = a **temporary fixed/point constraint** between the attacker's hand rigid body and the victim's torso/head rigid body in Rapier, with break-force thresholds so it releases on hard impacts. Carries/throws then work through real momentum — the throw arc is computed, not keyframed. This slots into the existing plan for the moveset library's grapple category.

## 2. Concrete technique spec for WH's physics layer

Architecture recap (existing directive, unchanged): **Rapier.js** = rigid-body layer; **Jolt** = soft-body layer; **authored animation is authoritative**; physics takes over the struck limb / landing, then blends back in ~0.25–0.4 s; spring bones for jiggle. What follows is exactly where GB's techniques plug in.

### 2.1 The PhysicsServo layer (GB §1.2 → WH Rapier)

Add one system between the animation sampler and the Rapier bodies:

```
each physics step, per servo-driven joint:
  target   = authored animation pose for this joint (quaternion)
  current  = physics body orientation
  err      = target − current  (shortest-arc quaternion error)
  vel      = joint angular velocity
  torque   = Kp × err  −  Kd × vel        ← PD servo (GB's drive, explicit)
  torque  *= driveScale[joint]            ← GB's KO envelope, per-limb
  body.apply_torque_impulse(torque × dt)
```

- **Kp (stiffness)** = Unity "Position Spring" analog; **Kd (damping)** = "Position Damper" analog. Start critically damped (Kd ≈ 2√Kp for the limb's inertia) and detune toward underdamped only where floppiness is wanted (jiggle zones stay in the spring-bone/Jolt layer, not here).
- **driveScale[joint]**: 1.0 nominal. This single per-limb scalar is the entire GB control↔ragdoll blend mechanism — no kinematic swaps, no separate ragdoll rig.
- Authored animation remains the *target generator* (GB inverts this: targets are procedural; WH keeps Tekken-authored targets). This preserves input-to-move fidelity while the *execution* is physical.

### 2.2 Hit reaction: per-limb drive cut + momentum-scaled impulse (GB §1.3, §1.4)

On a confirmed hit (during the victim's hitstun frames):

1. **Impulse**: apply to the struck limb's rigid body an impulse proportional to the attacker's striking-limb velocity at contact (GB's momentum rule, §1.3) × move power × counter-hit/weak-spot multiplier. Direction = attack vector.
2. **Drive cut**: set `driveScale[struck limb chain] → 0.0` (arm = shoulder+elbow; leg = hip+knee), all other limbs stay at 1.0 (legs keep driving → fighter doesn't collapse from a jab — this is the partial-ragdoll requirement).
3. **Blend back**: ramp `driveScale` 0 → 1 over **0.25–0.4 s** (existing directive) with a critically-damped ease (fast attack, no overshoot); the animation target during the ramp is the authored hit-reaction pose, so physics and animation converge on the same pose.
4. **Instant-KO threshold (GB's 40%-rule, adapted)**: if single-frame damage ≥ **40% of the victim's max HP**, cut **all** drives (full ragdoll) for a KO window: base 0.8 s + 0.1 s per 10% over threshold, capped at **2.0 s** (GB caps at 6 s; WH's Tekken pacing needs it shorter). Victim is invulnerable during the window (GB rule), wakes at full drive ramp over 0.3 s. Button mashing shortens the window up to 30% (GB's mash-to-wake, §1.4).

### 2.3 Balance servo + landing takeover (GB §1.5)

- Each step, compute the fighter's COM from Rapier bodies; support polygon from foot bodies.
- If COM projection exits the polygon by < small epsilon: apply corrective torque to the pelvis servo toward the authored idle/stance target (inverted-pendulum assist) and retarget the animation layer to a stumble-step clip. Player keeps control (driveScale stays 1.0).
- If it exits by > threshold (launchers, big counters): trigger §2.2 drive-cut on the lower body + full-body impulse along the launch vector; the "landing" is physics until ground contact, then driveScale ramps back over 0.35 s as the authored get-up/landing pose becomes the target set. This is "physics takes over the landing" implemented as GB's mechanism.
- Hard rule: the balance servo **never fights the authored animation** — it only adds torque toward the current animation target. If animation says "lying down" (grounded state), targets are the grounded pose and no righting torque is applied.

### 2.4 Grabs, carries, throws (GB §1.6 → WH wrestling systems)

- Grab connect = create a Rapier fixed joint between attacker's hand body and victim's torso/head body, with a break impulse threshold tuned so light jostling holds but a third-party heavy hit breaks it.
- While grabbed, the victim's `driveScale` for the grabbed region drops to ~0.15 (GB: a held/KO'd body is dead weight), letting the carrier's momentum genuinely swing them — throws are then **release-timed, not animated**: on release input, remove the constraint and keep velocities; the arc is ballistic. Aim assist = nudge the release velocity toward the nearest ring-out/hazard vector within a small cone (design knob, default 10°).
- Climbing (Heart and Mind Within beat-em-up traversal): GB's alternating-hand constraint pattern ports directly — hand constraints toggled per input, torso drive target = upward climb pose. Reuse the same constraint code path as combat grabs.

### 2.5 Soft-body / jiggle layer (GB's "gelatinous" look → WH Jolt + spring bones)

GB's characters read as soft because low servo stiffness + high inertia lets flesh lag behind bone. WH keeps rigid authoritative animation, so the softness belongs in the **Jolt soft-body layer + spring bones** (existing directive): breasts/belly/hips/thighs jiggle and facial/soft-tissue lag are driven by the *physics-space* limb velocities from §2.1, not the animation targets — so a drive-cut arm produces correct secondary-motion lag automatically. Tuning rule: soft-body spring frequency should sit **below** the servo bandwidth (softer than the PD loop) to avoid fighting it; start at ~1/3 of the slowest joint Kp-derived natural frequency.

### 2.6 Heart and Mind Within notes

The beat-em-up mode is where GB's techniques get the most room: multi-enemy brawls, environmental hazards, and longer unscripted sequences. Spec deltas vs. versus mode:

- Enable the §2.4 grab/constraint system for **props and ledges**, not just fighters (GB's world is fully grabbable).
- Lengthen the §2.2 KO cap to **3.5 s** in HMW (crowd-control fantasy; versus stays at 2.0 s).
- Environmental hits (walls, hazards) feed the §2.2 impulse path with the environment as the "attacker" — GB's arenas are the co-combatant, and HMW stages should be too.
- Keep the SHOW-ANIMATION LOCK: physics takeovers never trigger during intros/cutscenes; drives stay at 1.0 following authored targets.

### 2.7 Tuning starting points (proposed for WH, not GB's numbers)

| Parameter | Proposed start | Basis |
|---|---|---|
| Servo Kp (limbs) | critically damped for limb inertia; expose per-joint | Unity drive model (§1.2); tune until authored kicks track within 2 frames |
| Servo Kd | ≈ 2√Kp (critical), detune −20% for heavy limbs | damping prevents oscillation (Unity manual) |
| driveScale nominal | 1.0; struck chain → 0.0; grabbed region → 0.15 | GB KO envelope, per-limb (§1.4, §1.6) |
| Blend-back ramp | 0.25–0.4 s, critically-damped ease | existing WH directive, matches GB wake ramp feel |
| Instant-KO threshold | ≥40% max-HP in one frame | GB's 40/100 rule as a ratio (§1.4) |
| KO window | 0.8 s + 0.1 s/10% over, cap 2.0 s (versus) / 3.5 s (HMW); mash shortens ≤30% | GB's scaling + cap, shortened for Tekken pacing |
| Grab break impulse | holds through light hits, breaks on heavy/third-party hits | GB grab fragility (§1.6); tune per move |
| Soft-body spring freq | ~1/3 of slowest joint natural freq | keeps Jolt layer subordinate to servo loop (§2.5) |

Physics-engine hygiene (learned from GB's history): Boneloaf rebuilt the game **three times**, once because a Unity physics upgrade "broke all our physics" (MCV interview) — **pin Rapier and Jolt versions** in the repo and re-run the physics regression suite (every fighter, every §2.2/§2.3/§2.4 path) on any physics-dependency bump before merge.

## 3. Open questions for the physics implementation crew

1. Rapier impulse joints vs. manual PD torques: §2.1 specifies manual PD via `apply_torque_impulse` (full control of driveScale envelopes). If Rapier's motorized joints prove cheaper, verify they expose an equivalent per-step stiffness/damping scale — otherwise stay manual.
2. Fixed-timestep rate for the servo loop: GB-era Unity ran physics at 50 Hz default; WH's servo bandwidth needs may push to 60–120 Hz substeps. Profile before locking.
3. The mash-to-wake input path (§2.2.4) needs a KO-state input buffer distinct from the fight input buffer — design who owns it (UI vs. fighter state machine).
4. Netcode: driveScale envelopes and constraint attach/break events must be deterministic in rollback — decide whether physics state is rolled back or re-simulated from inputs.

## 4. Sources

- James Brown (Boneloaf) interview — no animator, physics-first development, rebuilt 3×, Unity physics upgrades breaking work: https://mcvuk.com/business-news/when-we-first-started-we-didnt-really-know-what-we-were-doing-how-gang-beasts-became-an-international-success/
- Early dev profile — custom rigid-body animation system on Unity's default physics, everything physics-driven, no mocap: http://krutowebcam.blogg.se/2023/february/game-gang-beasts.html
- Community technical analysis — GB/HFF style requires "full local-based torque-driven movement with a custom physical movement component," not kinematic animation: https://forums.unrealengine.com/t/gang-beasts-human-fall-flat-ragdoll-characters-in-ue4/155641
- Unity Manual, ConfigurableJoint — Target Rotation + Position Spring / Position Damper drive model (the PD-servo mechanism): https://docs.unity3d.com/510/Documentation/Manual/class-ConfigurableJoint.html
- Godot community active-ragdoll — per-bone Hooke's-law PD (`stiffness × displacement − damping × velocity`) as force/torque: https://forum.godotengine.org/t/inverse-kinnematics-combined-with-active-ragdoll-physics-help/130996
- Gang Beasts Wiki, K.O. mechanic — 100 HP, 40-damage single-frame instant KO, invulnerable while KO'd, wake at full HP, KO time scales with recent KOs + hit strength, 6 s cap, mash to wake: https://gangbeasts.fandom.com/wiki/K.O._mechanic
- Steam community mechanics write-up — weak spots (head/stomach/crotch), diving-attack damage multiplier + attacker vulnerability, KO-time factors: https://steamcommunity.com/app/285900/discussions/0/2796125475564421906/
- Controls reference — punch/grab/lift/kick/headbutt/duck mapping, hold-vs-tap semantics, climbing: https://www.gmru.co.uk/blog/gaming-9/mastering-gang-beasts-controls-the-ultimate-guide-1682
- Punch force from momentum/balance; lift-and-throw as momentum transfer: https://diffsense.com/gang-beasts-office-worker-why-everyone-is-obsessed-with-throwing-coworkers-off-buildings-1hkd
- KO/faint behavior, wake-up timing, button-mash recovery: https://TechRaptor.Net/gaming/previews/gang-beasts-online-preview-party-games-unleashed
- Inverted-pendulum COM balance feeding PD joint controllers (standard active-ragdoll balance technique): https://perso.liris.cnrs.fr/nicolas.pronost/UUCourses/GamePhysics/assignment.html
