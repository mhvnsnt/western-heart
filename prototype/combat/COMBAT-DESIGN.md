# Western Heart — Combat Design

**Adapted from:** tk fighting game (`assets/free-pull-1/tk-fighting-game/`)
**See also:** `docs/TK-COMBAT-ANALYSIS.md` for full system breakdown.

---

## Core Loop

Two fighters. Best of 3 rounds. 60-second timer. Last one standing wins.

Fixed-timestep simulation (120Hz) for deterministic frame data.
Decoupled rendering (60fps) for smooth visuals.

---

## Nine-Soul Meter

Replaces tk's super meter. 0–100 soul energy.

**Gain:**
- Landing a hit: +8 (light) / +11 (heavy)
- Taking damage: +6
- Blocking: +4

**Visual:** 9 segments, one per soul. Each segment ≈ 11 points.
Full meter = all 9 souls lit.

**Spend:** Soul Surge costs 100 (full meter).

---

## Soul Surge

Replaces tk's special move. Per-character ultimate attack.

- **Cost:** 100 soul energy (full Nine-Soul Meter)
- **Startup:** 0.24s (punishable — high risk)
- **Active:** 0.20s
- **Damage:** 24 (before defense scaling)
- **Visual:** Character-specific aura burst + screen effect.
  - Pantera: purple/red panther aura
  - Demonio: cold blue-white flame
  - Saku Ra: sand swirl
  - Zui: drunken multicolor haze

**Design rule:** Soul Surge should feel like the character's soul manifesting,
not a generic super move.

---

## Frame Data Format

Every move defined as data:

```json
{
  "name": "jab",
  "startup": 0.08,
  "active": 0.09,
  "recovery": 0.18,
  "damage": 6,
  "knockback": 2.2,
  "soulGain": 8,
  "cost": 0,
  "limb": "armR",
  "hitHeight": "mid"
}
```

Times in seconds. Convert from Tekken frames: `seconds = frames / 60`.

**Hit heights:** high / mid / low (for block system).
**Limbs:** armR, armL, legR, legL (for hitbox attachment).

---

## States

`idle`, `walk`, `jump`, `attack`, `block`, `hitstun`, `knockdown`,
`dodge`, `throw`, `throwTech`, `soulSurge`, `ko`, `victory`

**New vs tk:** `throw`, `throwTech`, `soulSurge` added.
`throw` is for King's grappling — positional lock, multi-stage.

---

## Blocking

- Hold back to block (or block button).
- Reduces damage to 12% chip.
- Must be facing attacker.
- High/mid/low: block must match attack height.
  - Standing block: high + mid
  - Crouching block: mid + low

---

## Throws (Pantera / King style)

- Unblockable at close range.
- `throw` state: attacker locks to defender position.
- Multi-stage: initial grab → follow-up choice → finisher.
- `throwTech`: defender can break with matching input (tight timing).
- Chain throws: successful throw → option for second throw (King's signature).

---

## Hitstop & Feel

- **Hitstop:** 0.04s (light) / 0.08s (heavy) / 0.12s (KO) freeze on impact.
- **Camera shake:** 0.18 (light) / 0.35 (heavy) / 0.5 (KO).
- **Impact particles:** Kenney spark sprites at contact point.
- **KO launch:** Defeated fighter launched with physics (vx=5.5, vy=6).

---

## AI Personalities

Base: tk's utility AI (spacing, reactive defense, meter management).

Per-character tuning:
- **Pantera:** Aggressive. Closes distance, goes for throws. High risk.
- **Demonio:** Balanced. Fundamental Tekken-style spacing.
- **Saku Ra:** Evasive. Sidesteps, whiff-punishes.
- **Zui:** Unpredictable. Random sway, sudden bursts.

---

*Combat design v1. Will expand as fighters are implemented.*
