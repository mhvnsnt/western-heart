# TK Fighting Game — Combat System Analysis
## For Western Heart adaptation

**Source:** `assets/free-pull-1/tk-fighting-game/` ("SHADOW STRIKERS")
**Analyzed:** 2026-10-13
**Files studied:** `js/fighter.js`, `js/game.js`, `js/characters.js`, `js/ai.js`

---

## 1. Architecture Overview

Complete 3D fighting game in browser (Three.js/WebGL, 60fps mobile-first).
Runs a **fixed-timestep combat simulation** (120Hz) decoupled from rendering (60fps).
This makes combat deterministic — critical for frame-data accuracy.

```
Game (match arbiter)
├── Fighter (p1, p2) — state machine, hitboxes, damage, meter
├── AIController — CPU opponent behavior
├── Arena — scene, camera, particles
└── UI callbacks — HUD updates (health, meter, timer, combos)
```

**Key insight for Western Heart:** This is the reference implementation.
The Godot port should mirror this architecture: fixed-timestep combat core + decoupled render.

---

## 2. Frame Data System

Moves defined as data, not code:

```js
punch:   { startup: 0.08, active: 0.09, recovery: 0.18, damage: 6,  knock: 2.2, meterGain: 8,  cost: 0 }
kick:    { startup: 0.14, active: 0.11, recovery: 0.30, damage: 11, knock: 4.2, meterGain: 11, cost: 0 }
special: { startup: 0.24, active: 0.20, recovery: 0.42, damage: 24, knock: 7.8, meterGain: 0,  cost: 100 }
```

Three phases per move:
- **Startup** — windup, no hitbox. Can be interrupted.
- **Active** — hitbox live. One hit per swing.
- **Recovery** — vulnerable cooldown. Cannot act.

**Western Heart:** Template for moveset data format. Tekken frame data
(startup/active/recovery in frames at 60fps) maps directly — convert frames to seconds.

---

## 3. Hitboxes & Hurtboxes

**Hitboxes:** World-space spheres on weapon bones.
- Punch/special → RightHand, radius 0.5 (1.0 for special)
- Kick → RightFoot, radius 0.5
- Active only during `active` phase.

**Hurtboxes:** World-space spheres on body bones.
- Spine1 → torso (r=0.58), Head (r=0.34)
- Disabled during dodge i-frames or death.

**Collision:** Sphere-sphere test per frame. One hit per swing max.

**Western Heart:** Sphere approach works for prototyping. Production needs
per-limb hurtboxes (arms, legs) + throw grab boxes. Tekken models have more
bones — map hurtboxes to: Head, Spine, UpperArm L/R, Thigh L/R.

---

## 4. Health, Meter & Damage

- **Health:** 100 HP. No regen.
- **Meter:** 0–100. Gain on attack (+8/+11), on damage taken (+6), on block (+4).
- **Damage:** `damage / defender.stats.defense`
- **Block:** 12% chip damage, small stun. Must face attacker. Builds meter.
- **KO:** HP ≤ 0 → knockout with launch physics.

### Western Heart: Nine-Soul Meter

| tk concept | Western Heart |
|---|---|
| Super meter (0–100) | Nine-Soul Meter (0–100) |
| Special (cost 100) | Soul Surge (cost 100) |
| Meter gain on hit/block/damage | Same (soul energy) |

**Design note:** Nine-Soul Meter could show 9 segments (one per soul, ~11pts each).
Soul Surge at full (9/9). UI change only — systems stay the same.

---

## 5. State Machine

States: `idle`, `walk`, `jump`, `attack`, `block`, `hitstun`, `knockdown`, `dodge`, `ko`, `victory`

- `canAct()` — true only in idle/walk/jump, not stunned, not dead.
- Attack phases tick by `stateT` vs startup/active/recovery durations.
- Dodge: 0.34s invulnerability, quick retreat.
- Knockdown: launched if knock ≥ 6, else hitstun.

**Western Heart:** Add `throw`, `throwTech`, `soulSurge` states.
Grappling (King's chain throws) needs a `grapple` state with positional lock.

---

## 6. Combo System

- `combo` counter increments per landed hit.
- `_comboTimer` (1.2s) resets between hits — combo drops if gap too long.
- UI shows combo at ≥ 2 hits.

**Western Heart:** Same. Add per-character combo scaling (damage reduction per hit
in long combos) for balance.

---

## 7. AI Controller

Utility-based: reads distance, player state, own meter.
- **Reactive defense:** Block/dodge incoming attacks (reaction chance scales with difficulty).
- **Spacing:** Approach if far (>3.2), attack if in range (1.4–3.2), create space if too close.
- **Special:** Uses meter dump when full and in range.
- **Difficulty:** 0–1 scales reaction time and aggression.

**Western Heart:** Good baseline. Per-character AI personalities (Pantera aggressive
grappler, Saku Ra evasive) can tune the weights.

---

## 8. Match Flow

- Best of 3 rounds, 60s timer.
- Round intro (1.6s lock) → "FIGHT!" → combat → KO/timeout → 3s → next round.
- Timeout: higher HP wins. Double KO possible.
- Hit-stop: brief freeze on impact (0.04–0.12s) for weight.
- Camera shake on heavy hits. Impact particles at contact point.

---

## 9. Animation System

Two-layer approach:
- **Base layer:** Real mocap clips (Idle/Walk/Run) through AnimationMixer, crossfaded.
- **Combat layer:** Procedural CCD inverse kinematics on real bones.
  - Punch: IK drives RightArm→RightForeArm→RightHand toward target point.
  - Kick: IK drives RightUpLeg→RightLeg→RightFoot.
  - Block: both forearms raised via IK.
  - Weight-blended against mocap base pose.

**Western Heart:** This IK-driven combat layer is the key technique. It means we don't
need a unique punch animation per character — the IK adapts to each skeleton.
Combined with the Quaternius/CMU mocap base layer, every fighter gets a full moveset.

---

## 10. Adaptation Checklist for Western Heart

- [ ] Port fixed-timestep combat core to Godot 4 (GDScript or GDExtension)
- [ ] Replace super meter with Nine-Soul Meter (9-segment UI)
- [ ] Replace special with Soul Surge (per-character visual + effect)
- [ ] Add throw/grapple states for King's chain throws
- [ ] Expand hurtboxes to per-limb on Tekken skeletons
- [ ] Define Pantera's full moveset in frame-data format
- [ ] Retarget mocap base layer to Tekken 7 King skeleton
- [ ] Implement IK combat layer in Godot (or bake IK to animations)
- [ ] Character select → replace ROSTER with Western Heart fighters
- [ ] Stage select → Eastern Mind arenas

---

*Analysis by wireup subagent, 2026-10-13. Source code in `assets/free-pull-1/tk-fighting-game/`.*
