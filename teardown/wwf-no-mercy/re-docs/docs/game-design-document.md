# GAME DESIGN DOCUMENT — WWF No Mercy (AKI Engine Recreation)

---

# 1. Project Overview

## 1.1 Purpose

This document is a technical Game Design Document (GDD) for WWF No Mercy (Nintendo 64, AKI Corporation / THQ, 2000). Its purpose is to provide a developer with sufficient specification to recreate the game's systems in a different programming language or on a different platform, with fidelity to the original gameplay mechanics.

## 1.2 Original Platform

|Property|Value|
|---|---|
|Platform|Nintendo 64|
|Developer|AKI Corporation|
|Publisher|THQ|
|Release|November 2000 (North America)|
|Target framerate|~30 fps|
|Engine|AKI Engine (also used in WCW/nWo Revenge, WWF WrestleMania 2000)|

## 1.3 Scope of Recreation

This GDD targets faithful recreation of:

- The complete damage and stamina simulation
- Move eligibility and slot system
- Reversal probability logic
- Character/CAW data model
- Match types, modes, and menu flow
- Spirit and Special state mechanics

It does **not** specify:

- Licensed assets (music, character likenesses, arena art, Titantron videos)
- Proprietary N64-specific rendering or audio code
- Original 3D models, animations, or sound effects

Any reimplementation must supply its own art, audio, and animation content.

## 1.4 Design Philosophy

The AKI Engine is a **deterministic state machine over four resource pools** (Current Health, Max Health, per-limb Joint Stamina, Spirit), driven by floor-rounded integer math and a handful of floating-point constants. Recreations should preserve the rounding behavior exactly; subtle changes to floor/ceiling operations will shift how many hits are needed to pin, how often moves are reversed, and how quickly matches pace out. The engine's "feel" emerges from the interaction of these small mathematical rules, not from any individual number.

---

# 2. Core Engine Architecture

## 2.1 System Overview

A match tick proceeds in roughly this order each frame:

1. Read controller input for each player.
2. Resolve each wrestler's current state (standing, grappling, airborne, etc.).
3. If an action is triggered, look up the applicable move slot using the eligibility rules.
4. If the action is a grapple/strike, run the reversal probability check on the defender.
5. If the move lands, compute Main Health Damage and Joint Stamina Damage.
6. Apply damage to Current Health, Max Health, and Joint Stamina pools.
7. Update Spirit for both wrestlers based on the outcome.
8. Write to the 30-second damage log and per-wrestler state map.
9. Advance Special timers, dizzy timers, count-out timers.
10. Render.

## 2.2 Resource Pools Per Wrestler

Each wrestler maintains:

- **Current Health** (0–255 integer, starts at 255)
- **Max Health** (64–255 integer, starts at 255)
- **Joint Stamina** — five floating-point pools: Head, Body, Arms, Legs, Flying. Each starts at 50.0, floors at 0.0, never regenerates.
- **Spirit** (0–100 integer, starts at 50)
- **Special state** (boolean + 20-second countdown timer)
- **Most-damaged limb pointer** (tracked for the limb-holding animation)

## 2.3 Per-Move Static Data

Each move in the database carries:

- Base Health Damage (integer)
- Attack Parameter (one of: Head, Body, Arms, Legs, Flying)
- Defence Parameter (one of: Head, Body, Arms, Legs, Flying)
- Five Joint Stamina Damage values (one per limb, may be fractional for repeating moves)
- Flag byte at offset 0x1C (the `0x08` value marks "technical" moves — small packages, missed dives, rail whips)
- KO / Bleed / Submit / Pin flags
- Eligibility group (see Section 5)
- Animation category

Repeating moves (submissions, 10-count punches, etc.) have **two complete entries**: one for the initial application and one for each subsequent wrench/rep/pulse.

---

# 3. Damage System

## 3.1 Health Mechanics

### 3.1.1 Current Health

Starts at 255 per wrestler. Depletes when damage is taken. Regenerates slowly while idle, but can never exceed the current Max Health value. Hits zero → KO-eligible.

### 3.1.2 Max Health

Starts at 255, floors at 64, never regenerates. On every damage event:

```
MaxHealthDamage = floor(MainHealthDamage / 4)
MaxHealth = max(64, MaxHealth - MaxHealthDamage)
```

If Max Health drops below Current Health after a hit, Current Health is forced down to match.

### 3.1.3 Example

A Pendulum Backbreaker deals 20 Current Health damage. Max Health takes `floor(20/4) = 5`. After one move, Current Health is 235 and Max Health is 250. Standing idle restores Current Health to 250 but no higher.

## 3.2 Joint Stamina Mechanics

Five pools of 50.0 each. Floating-point; reductions can be fractional (e.g., 48.7). Never regenerates. Reductions applied per move from the move's stamina-damage vector.

**Limb-holding threshold:** When any non-Flying limb drops below 15.0, the wrestler plays a holding animation for that limb. Only one limb is held at a time (the most-damaged one, tracked at player-map offset 0x7C). The threshold value (15.0) is stored as a doubleword float at address `80157A80` in the original ROM.

**Leg stamina movement penalty:** As Leg Joint Stamina falls, movement speed degrades. A wrestler with Leg Stamina 0.0 and a "Fast" speed setting runs at the same speed as one with Leg Stamina 50.0 and a "Slow" speed setting.

**Attack parameter penalty:** As the attacker's stamina in the limb they're using falls, their damage output with that limb drops proportionally (see Factor 1 below).

## 3.3 Main Health Damage Formula

Let:

- `D` = Base Health Damage (from move data)
- `S` = Attacker's Joint Stamina in the limb used by this move
- `A` = Attacker's Offense Parameter for the limb used
- `B` = Defender's Defense Parameter for the limb being hit
- `Spirit_A`, `Spirit_D` = Spirit values for attacker and defender
- `Special_A` = whether attacker is in Special mode

### 3.3.1 Factor 1 — Limb-Stamina-Adjusted Base Damage

```
Factor1 = floor((S + 50) * D * 0.01)
```

If attacker is in Special, `S` is treated as 50.0 (Special ignores limb damage).

The `50` additive constant is at address `80156EE0` in the original ROM; the `0.01` multiplier is at `80156EE8`. Both are doubleword floats.

**Example:** Dragon Screw (D=15) by a wrestler with Arms Stamina 25.0 → `floor((25+50) * 15 * 0.01) = floor(11.25) = 11`.

### 3.3.2 Factor 2 — Parameter Bonus

```
Factor2 = floor(max(0, A - B) * D * 0.1)
```

Can never go negative. If `A <= B`, Factor2 is zero. Parameters run 1–5; max advantage is +4.

**Example:** Mongolian Chop (D=5), attacker Arms Offense 5, defender Head Defense 1 → `floor(4 * 5 * 0.1) = floor(2.0) = 2`.

### 3.3.3 Factor 3 — Spirit Bonus

```
Factor3 = floor((Spirit_A - Spirit_D) * 0.05)
```

Capped at +5 (max when Spirit_A=100, Spirit_D=0). Never negative; if defender has higher Spirit, Factor3 is zero.

**Example:** Spirit difference of 26 → `floor(26 * 0.05) = floor(1.3) = 1`.

### 3.3.4 Factor 4 — Special Bonus

Sum the three prior factors:

```
T = Factor1 + Factor2 + Factor3
```

If attacker is in Special mode:

```
MainHealthDamage = floor(T * 1.2)
```

Otherwise:

```
MainHealthDamage = T
```

The 1.2 multiplier is at address `80156EF0`.

## 3.4 Applying Main Health Damage

### 3.4.1 Technical Moves (flag byte 0x1C == 0x08)

Current Health is **not** reduced. These are small packages, schoolboy rollups, la magistrals, missed dives, guardrail whips, etc. However:

- The notional damage IS logged to the 30-second damage log.
- Max Health IS reduced by `floor(MainHealthDamage / 4)`.
- If Max Health now drops below Current Health, Current Health is forced down to match.

### 3.4.2 Normal Moves

```
CurrentHealth = max(0, CurrentHealth - MainHealthDamage)
MaxHealth     = max(64, MaxHealth - floor(MainHealthDamage / 4))
```

Log the damage to the 30-second damage log (slot indexed by offset 0x2F4, a 0–30 counter). Start a 1-second timer at offset 0x3C.

## 3.5 Joint Stamina Damage

### 3.5.1 Normal Moves

For each limb `i`, subtract the move's listed stamina damage directly:

```
JointStamina[i] = max(0.0, JointStamina[i] - MoveStaminaDamage[i])
```

### 3.5.2 Repeating Moves (Submissions, etc.)

The per-wrench damage is modified by the **Submission Skill Matrix** (also called "Joint Technique Skill" — affects ALL repeating moves, not just submissions):

|Attacker ↓ / Defender →|Novice|Normal|Expert|
|---|---|---|---|
|**Novice**|0|−0.3|−0.5|
|**Normal**|+0.3|0|−0.3|
|**Expert**|+1.0|+0.5|0|

The bonus `B` applies to each affected limb on every wrench:

```
JointStaminaDamage[i] = MoveStaminaDamage[i] + B   // only for limbs with nonzero base damage
```

Each matrix value is stored as a 32-bit float in the original ROM (addresses `801535C4` through `801535E4`).

## 3.6 Worked Example — Figure Four Leglock

Setup: Mutoh (P1) vs. Saito (P2). Mutoh in Special (Spirit 100), Saito Spirit 36. Mutoh Submission Skill: Expert; Saito: Novice. Mutoh Leg Offense 2, Saito Leg Defense 2. Mutoh Leg Stamina 35.0.

Move data:

- Figure 4 (initial): D=5, Attack=Leg, Defense=Leg, Legs=3, Flying=3
- Figure 4 (per wrench): D=2, Attack=Leg, Defense=Leg, Legs=2, Flying=2

**Initial application:**

- Factor 1: `floor((35+50) * 5 * 0.01) = floor(4.25) = 4`
- Factor 2: `floor(max(0, 2-2) * 5 * 0.1) = 0`
- Factor 3: `floor((100-36) * 0.05) = floor(3.2) = 3`
- T = 4+0+3 = 7
- Special: `floor(7 * 1.2) = floor(8.4) = 8`
- Main Health Damage = 8; Max Health Damage = 2
- Joint Stamina: 3 Legs, 3 Flying (no submission bonus on initial phase)

**Each wrench:**

- Factor 1: `floor((35+50) * 2 * 0.01) = floor(1.7) = 1`
- Factor 2: 0
- Factor 3: 3 (unchanged)
- T = 1+0+3 = 4
- Special: `floor(4 * 1.2) = floor(4.8) = 4`
- Main Health Damage = 4; Max Health Damage = 1
- Submission bonus B = +1.0 (Expert vs. Novice)
- Final Stamina: 2+1 = 3 Legs, 2+1 = 3 Flying per wrench

Additionally, each Figure 4 wrench reduces Saito's Spirit by 2%, so Mutoh's Spirit Bonus may continue to grow as the hold extends.

---

# 4. Wrestler Parameters

## 4.1 Overview

Each wrestler has 10 parameters on a 1–5 scale:

- **Offense:** Head, Body, Arms, Legs, Flying
- **Defense:** Head, Body, Arms, Legs, Flying

Total cap is **30 points**. Created wrestlers start with all values at 1 (10 points) and may distribute up to 20 more points. Designers may intentionally leave points unspent to emphasize weaknesses.

## 4.2 Offense Semantics

Offense applies to the body part **the attacker uses**, NOT what they hit:

- Big Boot → uses Legs → Leg Offense
- Clothesline → uses Arms → Arm Offense
- Headbutt → uses Head → Head Offense
- Springboard Splash → uses Flying → Flying Offense

## 4.3 Defense Semantics

Defense applies to the body part **being hit** on the defender:

- Clothesline lands on Head → defender's Head Defense applies
- Leg Drop lands on Head → defender's Head Defense applies
- Splash lands on Body → defender's Body Defense applies

## 4.4 What Parameters Do

|Effect|Affected?|Notes|
|---|---|---|
|Pin difficulty|Yes|Higher Offense = fewer hits to pin; higher Defense = more hits|
|Effective move damage|Yes (via F2)|Offense − Defense difference drives Factor 2|
|Submission speed|Partial|Offense helps slightly; Submission Skill dominates|
|Damage animations|No|Limb-holding triggers at same stamina threshold regardless|
|Block/counter chance|No|Driven by Spirit/weight/health, not parameters|
|Listed move rating|No|Only effective damage changes|

## 4.5 Archetypes

|Archetype|Pattern|
|---|---|
|Powerhouse|High Body/Arms Offense, high Body Defense|
|Technician|High Arms/Legs Offense, balanced Defense|
|High-Flyer|High Flying Offense, low Body Defense|
|Brawler|High Head/Arms Offense, moderate Defense|

## 4.6 Example — The Rock

Offense: Head 2, Body 3, Arms 4, Legs 2, Flying 2 (total 13) Defense: Head 2, Body 3, Arms 2, Legs 2, Flying 2 (total 11) Grand total: 24 (6 points unspent) — a strong upper-body striker with solid durability.

---

# 5. Move Slot System

## 5.1 Concept

The engine defines a fixed grid of **assignable slots**. Each slot represents "when the player is in state X, the opponent is in state Y, and input Z happens, play the assigned move."

Moves in the database reference an **eligibility group**, not individual slots. Multiple slots may pull from the same group, so a single move definition can populate many contextual actions.

## 5.2 Slot Definition Schema

Each slot has:

|Field|Meaning|
|---|---|
|`position`|Broad system area (Grappling, Standing, Running, etc.)|
|`category`|Functional grouping within a position|
|`group`|Eligibility group the slot pulls moves from|
|`slot_id`|Unique identifier|
|`player_state`|Required attacker state|
|`opponent_state`|Required defender state (may be a list)|
|`range`|`close`, `mid`, `any`, or `n/a`|
|`requires_special`|Boolean — finisher slots require Special meter|
|`input`|Controller input combo|

## 5.3 State Vocabulary

### 5.3.1 Neutral Player States

`standing`, `running`, `ducking`, `getting-up`, `airborne`, `at-turnbuckle`, `on-turnbuckle`, `on-apron`, `running-on-apron`, `outside-ring`, `entering`

### 5.3.2 Paired Grapple States (attacker / defender)

- `front-weak-grapple-attacking` / `front-weak-grapple-defending`
- `front-strong-grapple-attacking` / `front-strong-grapple-defending`
- `back-weak-grapple-attacking` / `back-weak-grapple-defending`
- `back-strong-grapple-attacking` / `back-strong-grapple-defending`
- `turnbuckle-front-weak-grapple-attacking` / `-defending`
- `turnbuckle-front-strong-grapple-attacking` / `-defending`
- `turnbuckle-back-weak-grapple-attacking` / `-defending`
- `turnbuckle-back-strong-grapple-attacking` / `-defending`
- `apron-weak-grapple-from-inside-attacking` / `-defending`
- `apron-strong-grapple-from-inside-attacking` / `-defending`
- `apron-weak-grapple-from-apron-attacking` / `-defending`
- `apron-strong-grapple-from-apron-attacking` / `-defending`
- `double-team-grapple-front-attacking` / `-defending`
- `double-team-grapple-back-attacking` / `-defending`
- `double-team-grapple-sandwich-attacking` / `-defending`

### 5.3.3 Defender-Only States

`standing-facing-player`, `standing-facing-away`, `down-facing-up`, `down-facing-down`, `sitting-up`, `kneeling-all-fours`, `tree-of-woe`, `at-turnbuckle-facing-out`, `at-turnbuckle-facing-in`, `on-turnbuckle-facing-player`, `on-turnbuckle-facing-away`, `on-apron`, `outside-ring`, `down-outside-ring`, `down-in-ring`, `running-toward-from-weak-whip`, `running-toward-from-strong-whip`, `running-toward-opponent`, `throwing-punch`, `throwing-kick`, `held-on-shoulders`, `defeated`, `n/a`

## 5.4 Slot Positions

### 5.4.1 Grappling

Contains Front Weak/Strong Grapple (8 slots each, mapped to A/B with directional modifiers), Back Weak/Strong Grapple (4 slots each), Front and Back Finishers (1 each, Special required), and Back Grapple Reversals (R button).

Grapple inputs:

- `[A]`, `[Left/Right] + [A]`, `[D-Pad Up] + [A]`, `[D-Pad Down] + [A]`
- `[B]`, `[Left/Right] + [B]`, `[D-Pad Up] + [B]`, `[D-Pad Down] + [B]`
- Finisher: `[Control Stick]` from a strong grapple state with Special

### 5.4.2 Standing

Weak Arm Strike, Weak Leg Strike, Strong Strike, Recovering Strike (ducking strike from getting-up), Counter Punch (R against `throwing-punch`), Counter Kick (R+A/B against `throwing-kick`), Walking Style.

### 5.4.3 Running

Running Strike (weak and strong variants), Running Grapple (front and back), Running Ground Strike (facing-up, facing-down, sitting-up, kneeling variants), Evasion (`[Run] + [R]`).

### 5.4.4 Ground

Upper-Body Submission, Upper-Body Finisher (Special), Lower-Body Submission, Lower-Body Finisher (Special), Ground Striking — each with variants for defender states `down-facing-up`, `down-facing-down`, `sitting-up`, `kneeling-all-fours`.

### 5.4.5 Turnbuckle

Turnbuckle Strikes, Running Turnbuckle Strikes, Corner Counter (when player at turnbuckle facing incoming Irish-whipped opponent — requires rapid tapping of R, A, B), Tree of Woe strikes, Front/Back Turnbuckle Grapples (weak/strong/finisher), Flying Move Counter, Flying Attack from Top (variants for standing opponent, laying opponent, outside-ring opponent, and Special versions), Flying Attack from Second Rope, Turnbuckle Taunts (corner and top-rope).

### 5.4.6 Ringside

Grapple to Apron (weak, strong, special, counter), Springboard Attack to Inside, Flying Attack to Outside, Running Diving Attack, Running Diving Taunt, Rebound Flying Attack.

### 5.4.7 Apron

Apron Kick (to-inside and to-outside variants), Grapple from Apron (weak/strong/finisher/counter), Flying Attack from Apron (standing, running), Flying Attack to Ring (standing opponent, laying opponent, Special), Apron Taunt.

### 5.4.8 Irish Whip

Irish Whip Strike, Weak Irish Whip Grapple (tap A vs. hold A), Strong Irish Whip Grapple (tap A vs. hold A), Irish Whip Finisher (Control Stick, Special required).

### 5.4.9 Taunt

Taunts with Control Stick directions (Up/Left/Right), Special Taunt (with Special meter), Ducking Taunt, Celebration Taunt (automatic on opponent defeat), Entryway Taunt (automatic during entrance).

### 5.4.10 Double Team

Double-Team Grapple (front, back, sandwich), Running Double-Team Grapple, Double-Team Flying Attack (from top turnbuckle, from top turnbuckle to outside, from apron over top rope).

## 5.5 Resolving a Move

Pseudocode for resolving a player input:

```
on_input(player, input):
    candidate_slots = all slots where:
        slot.player_state   matches player.current_state AND
        slot.opponent_state matches opponent.current_state AND
        slot.range          matches distance(player, opponent) AND
        slot.input          matches input AND
        (slot.requires_special == false OR player.in_special == true)

    slot = pick_highest_priority(candidate_slots)
    if slot:
        move = player.moveset[slot.group]
        execute(move)
```

---

# 6. Reversal System

## 6.1 Trigger

When a wrestler is grabbed into a weak or strong lock-up, the defender may press **A, B, L, or R — exactly once** — to trigger a reversal roll. Multiple taps do not increase the chance. The input must occur before the attacker selects their grapple move.

A reversal flag is written to the defender's player map at offset `0x71`.

## 6.2 Base Spirit-Band Probability Table

|Defender Spirit|Probability (0–1000 scale)|% Chance|
|---|---|---|
|100|500|50.0%|
|81–99|333|33.3%|
|61–80|250|25.0%|
|31–60|125|12.5%|
|11–30|62|6.2%|
|0–10|31|3.1%|

Standing grapples read the table at ROM address `80153610–80153626`; ground grapples at `801535F8`. Values are 16-bit integers.

## 6.3 Weight Factor Adjustment

Every wrestler has a Weight Factor parameter (0–7). Compute:

```
W = floor(defender.weight_factor / 3) - floor(attacker.weight_factor / 3)
if W > 0:
    P = P * 2
```

**Example:** Dragon Kid (WF=1) grabs Magnum TOKYO (WF=4). `floor(4/3) - floor(1/3) = 1 - 0 = 1`. P doubles. Most wrestlers have Weight Factor 5 (→ 1 after floor), so most pairings see no adjustment.

Weight Factor also governs:

- AI dash frequency (higher for lightweights)
- AI grapple follow-up speed (faster for lightweights)

## 6.4 Strong Grapple Health Scaling

For strong grapples only, scale by defender's health:

- If defender is **not** in Special, use Current Health; if defender **is** in Special, use Max Health.
- If health ≥ 192 (~75%): `P = P * 4`
- Else if health ≥ 128 (~50%): `P = P * 2`

This is why strong grapples are reversed constantly early in a match.

## 6.5 Special Mode Rules

|Attacker|Defender|Result|
|---|---|---|
|Special|Not Special|Reversal disabled (no roll)|
|Special|Special|Normal reversal logic applies|
|Not Special|Any|Normal reversal logic applies|

This exists because many Special-mode grapple animations have no reversal counterpart, so the engine simply blocks the reversal path entirely.

## 6.6 Final Probability Algorithm

```
P = spirit_band_probability(defender.spirit)

W = floor(defender.weight_factor / 3) - floor(attacker.weight_factor / 3)
if W > 0:
    P = P * 2

if is_strong_grapple:
    health = defender.max_health if defender.in_special else defender.current_health
    if health >= 192:
        P = P * 4
    elif health >= 128:
        P = P * 2

if attacker.in_special and not defender.in_special:
    return false  // reversals disabled

P = min(P, 1000)  // cap at 100% on 0-1000 scale

roll = RNG()  // 0-999, pre-rolled
reversal_happened = (roll < P)

// consume and refresh the RNG value
```

## 6.7 Notes

- Parameters (1–5 offense/defense) do **not** affect reversal chance.
- Some moves cannot be reversed at all.
- Weak Front Grapple A-button moves cannot be reversed, but have a design tradeoff: they boost the defender's Spirit by 3 (attacker only gets +2).

---

# 7. Spirit System

## 7.1 Overview

Spirit is a 0–100 integer value, starting at 50. It drives:

- Damage Factor 3 bonus
- Reversal probability
- Dizzy duration
- Eligibility for Special mode (filling to 100 triggers Special)

## 7.2 Visual Representation — 25 Discrete Levels

The on-screen Attitude Meter uses 25 distinct bands (7 below green neutral, the neutral green, 17 above neutral, plus SPECIAL at the top). Color and width both change per level.

### Downward (from neutral toward Danger)

|Level|Color|Hex|Top %|Bottom %|
|---|---|---|---|---|
|−1|Medium Green|`#68e803`|50.0%|46.1%|
|−2|Bright Green|`#30fb02`|43.7%|38.7%|
|−3|Green-Cyan|`#04eb62`|38.4%|31.9%|
|−4|Teal|`#00cd95`|31.6%|26.4%|
|−5|Cyan|`#03acbc`|26.0%|19.5%|
|−6|Blue-Teal|`#017fd9`|20.3%|13.9%|
|−7|Blue|`#0338f3`|14.1%|8.9%|
|−8|Deep Blue|`#0029f0`|14.1%|7.6%|

### Upward (from neutral toward Special)

|Level|Color|Hex|Top %|Bottom %|
|---|---|---|---|---|
|1|Green (neutral)|`#67E504`|50.0%|44.8%|
|2|Yellow-Green 1|`#74DE01`|53.8%|46.1%|
|3|Yellow-Green 2|`#7FD801`|55.0%|48.6%|
|4|Yellow-Green 3|`#8ED101`|57.5%|49.8%|
|5|Yellow 1|`#99C600`|58.7%|53.5%|
|6|Yellow 2|`#A2C101`|62.5%|54.7%|
|7|Dark Yellow|`#AABA00`|63.7%|57.2%|
|8|Gold|`#B4AF00`|64.9%|58.4%|
|9|Dark Gold|`#BCA500`|67.4%|63.6%|
|10|Orange-Gold|`#C3A000`|71.5%|66.2%|
|11|Orange|`#CE9200`|73.0%|66.6%|
|12|Deep Orange|`#D48601`|75.6%|67.8%|
|13|Burnt Orange|`#DC7900`|76.8%|71.7%|
|14|Red-Orange 1|`#E16C01`|78.1%|73.1%|
|15|Red-Orange 2|`#E95C00`|82.2%|75.8%|
|16|Vermillion|`#F14800`|84.8%|75.8%|
|17|Red|`#F72E00`|86.2%|79.6%|
|18|Deep Red|`#F91F00`|86.1%|79.6%|
|—|**SPECIAL**|N/A|100%|100%|

Each level has a subtle pulsing animation (~4 widths cycled per level), which is why top and bottom percentages differ.

## 7.3 Spirit Changes

**Passive:**

- Standing outside the ring while opponent is inside: −8% per 4 seconds. Outside-the-ring taunts do not raise Spirit in this state.

**Event-based:**

- Successful attack: attacker Spirit rises (typically +1 to +3), defender drops.
- Weak Front Grapple A-button moves: defender gets +3, attacker gets +2 (unusual inversion, can't be reversed).
- Taunt: boosts own Spirit, and shortens opponent's Special timer by 2 seconds if they're in Special.
- Figure 4 and other drawn-out holds: each wrench drops defender Spirit by 2%.
- Low-HP comeback: while Current Health < 49, every action (strike, grapple, taunt, block) grants a bonus +3 Spirit.

## 7.4 Spirit Decay Observation

In test scenarios with P1 outside the ring and P2 inside, P1's Spirit drops through 7 downward color bands at roughly 9 seconds per band, bottoming out at Deep Blue around 64 seconds of continuous exposure before transitioning to the "Danger" state.

---

# 8. Special Mode

## 8.1 Activation

Special is triggered when Spirit reaches 100 (top of the meter) and a taunt is performed. Indicator: the Attitude Meter displays "SPECIAL" at full width.

## 8.2 Duration

Special lasts **20 seconds** from activation, but the timer is shortened by:

- −2 seconds per strike received
- −2 seconds per grapple move received
- −2 seconds per missed diving move
- −2 seconds per opponent taunt

## 8.3 Effects While in Special

- Factor 1 (Limb-Stamina-Adjusted Base Damage) treats attacker's stamina as 50.0 (no limb-damage penalty to own offense).
- Factor 4 applies a 1.2× multiplier to total damage.
- Grants access to finisher moves (any slot with `requires_special = TRUE`).
- If defender is NOT in Special, grapple reversals against the attacker are entirely disabled.
- For strong-grapple reversal health scaling, the defender's Max Health is used in place of Current Health.

## 8.4 Restrictions

If the attacker is in Special but the defender is too, reversal logic runs normally (50% chance at full Spirit).

---

# 9. Match Pacing & Dynamic Behaviors

## 9.1 Limb Work

Damaging an opponent's arm makes their lariats and arm-driven moves weaker via Factor 1 — this is the core of the engine's strategic depth. Kicking the legs slows movement and weakens kicks. Head damage primarily reduces head-strike output and threatens KOs on head-targeting finishers.

## 9.2 Pin Mechanics

To initiate a pin, press L while standing over a downed opponent (facing up or face down).

Kickout difficulty is driven by:

- Accumulated Current Health and Max Health damage
- Spirit differential
- **Count-weighted button tapping:** Tap effectiveness scales with how far the count has progressed. A single tap after the "2.5" mark is worth approximately 6 taps before the "1" mark — this is what creates dramatic near-falls.
- **Previous kickouts cause fatigue:** Each successful kickout by a wrestler makes subsequent kickouts harder.

Accepted kickout inputs: A, B, L, R (tapping).

## 9.3 Submission Mechanics

Submission hold strength:

```
SubmissionStrength = Attacker.offense_parameter_of_limb_used + SubmissionSkillLevel
```

Defender's Defense Parameter has almost no effect. Submission Skill dominates; a high Offense parameter cannot overcome a Submission Skill deficit.

**Attacker hold trick:** If the attacker holds the analog stick during a submission, the defender cannot tap out at all (the submission is effectively sustained indefinitely, pending stamina).

**Defender hold trick:** The defender can hold the analog stick to voluntarily stay prone, stay in a pin, or remain in a submission.

## 9.4 Dizzy State

Triggered by being Irish-whipped into the guardrail outside the ring. Duration scales inversely with Current Health and Spirit — lower values → longer dizzy.

**Exception:** If the referee count is counting down to a count-out and fewer than 6 seconds remain on the count, dizzy is suppressed. This prevents cheap count-out victories.

While dizzy:

- Dodge (L), Block (R), and Counter-Grapple (A) all retain a minimum 10% success rate at peak dizziness.
- The success rate climbs to 66.7% immediately before wake-up.

## 9.5 Wake-Up Taunt

If the attacker taunts a prone opponent, there is a 30% chance the opponent stands up dizzy (ふらふら state).

## 9.6 Test of Strength

Triggered when both wrestlers initiate a grapple on the same frame AND:

- Both wrestlers have Current Health > 150 (of 255)
- Both wrestlers have a "Test of Strength Move" in their moveset

Winner: the player with the most button presses (A, B, L, R all count).

## 9.7 Catch Counter

If an attacker throws a kick and the defender presses R at the correct frame, the defender catches the kick. Then:

- The defender can press A or B to execute one of their two catch-counter moves.
- The original attacker can also press A or B during this window. If attacker and defender press the **same** button, an enzuigiri kick fires instead (countering the counter).

## 9.8 Slamming a Super Heavyweight

Attempting a scoop slam or backdrop on a Super Heavyweight may fail. On failure:

- Attacker takes 1 point of Back (Body) damage.
- Attacker gains +2 Spirit — which raises the odds of the next attempt succeeding.

Repeated attempts compound Spirit, eventually making the slam land.

## 9.9 Irish Whip Counters

After being Irish-whipped, the defender has a single timing window:

- Tap A at the right time: attempts a counter-attack (reversal move).
- Tap B, L, or R at the right time: grabs the ropes (stops the whip).

## 9.10 Taunt-Into-Move Damage Boosts

Certain character-specific taunt → move chains grant massive damage boosts. Known examples:

|Chain|Base → Boosted Damage|
|---|---|
|`taunt-081` → `clothesline-from-hell`|12 → 30|
|`taunt-184` → `running-knee-drop`|6 → 30|
|`val-venis-taunt` → `body-splash`|25 → 35|
|`taunt-105` → `jumping-hip-attack`|15 → 30|
|`taunt-089` → `clothesline-l-01`|15 → 40|
|`taunt-127` → `clothesline-l-02`|11 → 20|
|`rikishi-01` → `bonzai-drop`|25 → 30|
|`scotty-worm-taunt` → `scotty-worm-chop`|4 → 40|
|`taunt-127` → `clothesline-r-03`|12 → 30|
|`ducking-taunt-010` → `elbow-attack-02`|12 → 25|
|`taunt-016` → `tbone-suplex-02`|12 → 25|
|`taunt-098` → `roundhouse-middle-kick-03`|12 → 20|
|`taunt-105` → `thump`|15 → 30|
|`peoples-elbow` (ground) → `peoples-elbow` (running)|6 → 40|

## 9.11 Movement Speed

Three settings: Slow, Normal, Fast. Affects only **forward, backward, and running** movement. Lateral movement and grapple animations run at the same speed regardless of Movement Speed.

## 9.12 Interference

Interfering wrestlers can only be removed from the ring by reducing **their** Max Health below 249.

## 9.13 30-Second Damage Log

Each player has a rolling 30-slot log, indexed by a 0–30 counter at offset `0x2F4`, with the starting pointer at offset `0x2F8`. Every damaging move logs its notional damage (even technical `0x08` moves that deal no Current Health damage). Used by the AI and pacing systems to track recent match activity.

---

# 10. Character Data Model

## 10.1 Character Slot Structure

Each **character slot** contains **four attire slots**. The four attire slots share:

- Moves
- Fighting Style
- Parameters
- Ally/Enemy

They can differ in:

- Profile/Music (partially — name, alias, music, Titantron)
- Appearance

Multiple distinct characters may occupy the four attire slots of one character slot, but they will share all gameplay configuration.

## 10.2 The Six Configuration Pages

### 10.2.1 Profile / Music

|Field|Range / Options|
|---|---|
|Name|Free text|
|Short Name|Free text (used when Name is too long)|
|Alias|Free text (displayed on in-match Attitude Meter; falls back to Short Name)|
|Picture|64×64 PNG with transparent background|
|Height|5'0" to 7'11"|
|Weight|100 lbs to 599 lbs|
|Music|Select from entrance music library|
|Titantron|Select from entrance video library (may be empty)|

Altering Weight does not change physical appearance — that is set via the Appearance page.

### 10.2.2 Appearance

- **Body Type** — 14 male options (Skinny 1–2, Medium 1–2, Thick 1–2, Fat 1–2, Austin, HBK, Rikishi, Rock, Hairy 1–2), 9 female options (Chyna, Fit 1–4, Grannie, Jackie, Petit 1–2). Combined with 1 of 8 skin tones.
- **Skin Tones** (approx): `#f7c2a1`, `#edaa89`, `#c48061`, `#d89671`, `#8a5240`, `#734040`, `#543430`, `#541910`.
- **Head** — 7 male shapes (Male 1–7), 3 female shapes.
- **Face** — 98 male options (Male 1–98), 20 female options.
- **Hair** — Bald, Shaved, Short 1–3*, Middle 1–4*, Long 1–3*, Afro, Braided, Clean Cut, Curly Hair, Dreads, Mohawk 1–2, Ponytail 1–2*, Shocked. (* = compatible with Front Hair.)
- **Front Hair** — None or Front Hair 1–63.
- **Facial Hair** — None or 1–31.
- **Masks/Etc** — Bat, Bat Mask, Beast, Hockey, Kabuki Paint, Kanji, Kane 1–2, Leather Mask, Mankind, Phantom, Serpent, Undertaker, Aki Man, plus Accessories (Bandana, Boss Man, Buh Buh, Christian, D-Von, Edge, Eye Glasses, Eye Patch, Gold Chain, Gold Medals, Matt, Rikishi, Rock, Too Cool, T & A, Undertaker, X-Pac).
- **Hats/Caps** — None, Austin Cap, Bandanna 1–2, Grandmaster, Scotty Hat, Triple H.
- **Ring Attire** — Category table (Short, Long, Wrestling, Pants, Full Body) covering dozens of preset options per category (see Appendix A).
- **Upper Body** — Category table (No Sleeve, Sleeve S, Sleeve L, Others) covering dozens of presets.
- **Tattoo** — None or 1 of 26 options (Angle, Boss Man, Chaz, Christian, Dude, Edge, Godfather, Rios, Road Dogg, Scar 1–2, Tazz, Test, Thrasher, Tribal 1–2, Undertaker, X-Pac, Original 1–8).
- **Gloves** — None or 1 of 7 (A.P.A., Boxing, Dirtbike, Grappling, Kane, Taping, Undertaker (old)).
- **Wrist Band** — None or 1 of 7 (HBK, HBK-DX, Kane, Taped, Wrist Band 1–3).
- **Elbow Pads (L and R, independent)** — None or 1 of 7 (Angle, Elbow Brace, Hardyz 1–2, Pad, People's Elbow, Supporter).
- **Knee Pads (L and R, independent)** — None or 1 of 14 (Angle, HBK, HBK-DX, Mr. Ass 1–2, Knee Brace 1–3, Knee Pad 1–3, Supporter 1–2, Tye Dyed, X-Pac).
- **Feet** — None or 1 of the foot-attire table (Boots 01–21, Padded 1–9, Pull-Ons 01–19, Athletic 1–5, Kung Fu, Supporter, Tabi, Taped).
- **Entrance Attire** — Optional, from Accessories / Hats-Caps / Costumes tables.
- **Weapons/Props** — Optional entrance prop: Bat, Sledge Hammer, Night Stick, Barbed Wire 2×4, 2×4, Kendo Stick, Microphone, Head, Water Bottle, Roses, Cane, Bazooka, Goblet, Scales.

### 10.2.3 Moves

Assign moves to every move slot. Each slot must be populated with a compatible move (one whose eligibility group matches the slot's group).

A wrestler also has **10 Favorite Moves** — the moves the CPU preferentially chooses when controlling this wrestler.

### 10.2.4 Fighting Style

|Setting|Options|
|---|---|
|Stance|Wrestling, Martial Arts, Shoot, Normal, Women|
|Ring Entry|Normal, Jump, Over the Top, Leap Frog, Flip Over, Woman|
|Counter / Reversals|Heavy, Light-Heavy, Martial Arts|
|Speed|Slow, Normal, Fast|
|Submission Skills|Expert, Normal, Novice|
|Irish Whip Evasion|Yes, No|
|Recovery Rate|Slow, Normal, Fast|
|Bleeding|Rarely, Normal, Often, None|
|Reaction to Blood|Panic, Normal, Aggression, None|
|Endurance|Weak, Normal, Strong|
|Turnbuckle Climbing|Climbing, Jump|
|Jumping Distance|Shortest, Short, Normal, Long, Longest|
|Specific Weapon|Random or specific weapon type|

Note on terminology: "Endurance" controls how long a wrestler struggles to get up after a TKO-class move — functionally closer to "Recovery From KO."

### 10.2.5 Parameter

The 10 offense/defense values (1–5 each, 30-point cap). See Section 4.

### 10.2.6 Ally / Enemy

|Field|Purpose|
|---|---|
|Rival 1 (50%)|Primary interference rival|
|Rival 2 (30%)|Secondary interference rival|
|Rival 3 (20%)|Tertiary interference rival|
|Accompanied By|Valet or manager who accompanies this wrestler|

When interference is enabled in Rules, the interfering character is rolled from this table.

## 10.3 CAW Limits

The engine supports up to **18 fully created wrestlers** stored as "jobbers." Cloned wrestlers count against this total. Data can be moved between Game Pak (cartridge) and Controller Pak via the Data menu.

---

# 11. Match Types

Match types are selected at the start of a match and determine win conditions, participant count, and available features.

## 11.1 Single Match

One versus one. Win by pin, submission, TKO, count-out, or DQ (depending on Rules settings).

## 11.2 Tag Match

Two vs. two. One wrestler per team is active in the ring; partners can be tagged in (Up C) or can climb in to make a save. Tag Team Championship can be contested only in this match type.

## 11.3 Triple Threat Match

Three-way free-for-all. Match ends when any one wrestler is pinned/KO'd; the wrestler who landed the deciding blow wins.

## 11.4 Handicap Match

Two vs. one. The lone wrestler can win by eliminating only one opponent.

## 11.5 Cage Match

Two wrestlers inside a cage. Winner is the first to climb out. Pins/submissions may be disabled by Rules.

## 11.6 Ladder Match

A belt hangs 15 feet above the ring. Winner is the first to set up the ladder, climb it, and grab the belt. Tap A rapidly at the top of the ladder to grab the belt. Variants:

- Single
- Tag
- Triple Threat
- Handicap

## 11.7 Royal Rumble

Up to 40 wrestlers; entry order random or player-selected. Elimination by throwing over the top rope (default), plus pin and submission. **TKO is not a valid elimination in Royal Rumble.** "Team Battle" variant pits up to 4 teams with multiple wrestlers each.

## 11.8 Iron Man Match

Most pins in the time limit wins. Variants: Single, Tag, Triple Threat, Handicap.

## 11.9 Guest Referee

Player controls the referee. Variants: Single, Triple Threat, Handicap.

## 11.10 Survival Mode (Single Play Only)

Royal Rumble with unlimited respawning opponents. Starts with 4 wrestlers (1P vs. 3 CPU). TKO not allowed. Each elimination grants in-game currency for the SmackDown! Mall.

## 11.11 Championship Mode (Single Play Only)

Scripted career paths per championship belt:

- WWF (World Heavyweight)
- WWF Tag Team
- Intercontinental
- European
- Hardcore
- Light Heavyweight
- WWF Women's

Completing a championship path can unlock hidden Superstars, Managers, and Valets.

## 11.12 King of the Ring

Tournament bracket with 3–16 wrestlers. Bracket Setup allows:

- Changing Superstars between Human/CPU control
- Rearranging bracket order by swapping pairs
- Choosing to Watch or Skip CPU-only matches

Match types available in KOTR: Single, Tag, Cage, Royal Rumble, Ladder (Single), Ladder (Tag Team).

## 11.13 Pay-Per-View

Custom match card builder. Player names the PPV, sets date and place, then adds matches one at a time (each with full match type, rules, belt, and Superstar selection).

---

# 12. Rules Configuration

Selected before each match:

|Rule|Options|
|---|---|
|Time Limit|5, 10, 15, 30, 60 minutes, or No Limit|
|Count Out|10 Counts, 20 Counts (default), Anywhere/Hardcore, No Count|
|Pin|Yes / No|
|Submission|Yes / No|
|TKO|Yes / No|
|Rope Break|Yes / No|
|DQ|Yes / No|
|Bloodshed|Yes / No / First Blood|
|Interference|Yes / No|

**Interference timing:** When enabled, a CPU wrestler runs in at a randomly-chosen time of 30, 45, or 60 seconds. The interferer is chosen randomly, weighted by the in-match competitors' Ally/Enemy settings.

**First Blood:** First wrestler to bleed loses automatically.

---

# 13. Arenas

The engine supports 10 arena presets:

1. RAW is WAR
2. No Mercy
3. SmackDown!
4. King of the Ring
5. SummerSlam
6. Survivor Series
7. Royal Rumble
8. WrestleMania
9. Backlash
10. Armageddon

Additional arenas may be hidden and unlockable through Championship progression.

---

# 14. Belts / Championships

Championship data model:

|Belt|Notes|
|---|---|
|WWF (World Heavy)|Top title; contested in most match types|
|WWF Tag Team|Contested ONLY in Tag Team matches|
|Intercontinental|Mid-card title|
|European|Lower-card title|
|Hardcore|No-rules title match; weapons legalized|
|Light Heavyweight|Weight-restricted|
|WWF Women's|Women's division only|

Each belt tracks a current champion. Winning a belt in Championship mode unlocks the belt as a selectable option in other modes.

---

# 15. Main Menu Structure

Three horizontally-navigated main screens (D-Pad Left/Right or L/R to switch):

## 15.1 Multi-Play

- Exhibition (Single, Tag, Triple Threat, Handicap, Cage)
- Royal Rumble (Random, Team Select, Team Battle)
- Pay-Per-View (Single, Tag, Triple Threat, Handicap, Cage, Royal Rumble, Ladder, Guest Referee, Iron Man)
- King of the Ring (Single, Tag, Cage, Royal Rumble, Ladder Single, Ladder Tag)
- Guest Referee (Single, Triple Threat, Handicap)
- Ladder Match (Single, Tag, Triple Threat, Handicap)
- Iron Man Match (Single, Tag, Triple Threat, Handicap)

## 15.2 Single Play

- Championship (7 belt paths)
- Survival

## 15.3 Commissioner

- SmackDown! Mall
    - Superstar Options: Edit, Create, Clone, Change Stable, Stables Name
    - Shop (Costume / Moves / Etc, purchased with in-game money)
    - Data (Controller Pak transfer: Check, Clone, Move, Erase)
- Options
- Records

## 15.4 Options

|Setting|Options|
|---|---|
|Difficulty|Beginner, Easy, Normal, Hard, Expert|
|Attitude Meter|On / Off|
|Replay|On / Off|
|Camera|On / Off|
|Sound|Stereo / Mono|
|Music|On / Off|
|BGM Volume|Minimum / Normal / Maximum|
|Controller|Remappable button layout per connected controller|

## 15.5 Records

View Win/Loss statistics per wrestler. Sort by Use, Wins, or Losses.

---

# 16. Match Setup Flow

The standard flow for any match:

1. **Match Type** — Single, Tag, Triple Threat, etc.
2. **Player Assignment** — assign each slot to a controller (1P–4P) or CPU, or select WATCH (all CPU).
3. **Arena** — choose from 10 (plus unlockable).
4. **Rules** — set all toggles listed in Section 12.
5. **Belt** — default is Non-Title; select a unlocked championship if desired.
6. **Superstar Select** — each player picks their wrestler. L/R cycles between stables. Up C randomizes. Left/Right C cycles attire. A confirms.
7. **Match-Up Screen** — TV-style preview. A confirms; B returns to previous screen.

## 16.1 Pause Menu

Accessible any time during a match with Start:

- Continue Match
- Rematch
- Quit Match
- Attitude Meter toggle
- Camera toggle
- Replay toggle

---

# 17. Controls

All inputs below use N64 controller notation. Any recreation should map these to the target platform's controller.

## 17.1 Base Mapping

|Input|Function|
|---|---|
|Control Pad|Move wrestler (4 directions)|
|Control Stick|Taunt (directional); Finisher activation (during Special)|
|A|Grapple — Tap for Weak, Hold for Strong|
|B|Strike — Tap for Weak, Hold for Strong; Weapon attack|
|▲C|Climb through/over ropes; Grab weapon from crowd; Pick up ladder; Drag opponent; Tag partner|
|▼C|Run; Climb turnbuckle; Hop over downed opponent; Slide into ring|
|◀C|Flip opponent on mat|
|▶C|Focus on different opponent|
|L|Reverse/Avoid grapple; Flip standing opponent; Pin opponent; Hold opponent from behind|
|R|Block/Counter striking attacks; Release grapple; Pick up opponent from mat|
|Start|Bypass entrance; Pause|
|Z|Toggle CPU / Manual control|

## 17.2 Derived Actions

Many actions are combinations documented throughout Sections 5 and 9 (e.g., `[Run] + [B]` for running strike, `[D-Pad] + [A]` from apron for flying attack, etc.). The move slot system is the canonical source for every input combination.

---

# 18. Save Data

## 18.1 Storage Locations

- **Game Pak (cartridge)** — primary save location. All data stored here by default. Loaded automatically on power-on.
- **Controller Pak (memory card)** — optional. Used to transfer created Superstars between Game Paks.

## 18.2 What Is Saved

- Created wrestlers (up to 18 jobbers)
- Edited Superstars
- Championship history
- Unlocked hidden content
- Win/Loss records per wrestler
- Game Options settings
- Stable names and rosters

## 18.3 Data Menu Actions

- **Check** — View all created info for any created wrestler (read-only).
- **Clone** — Copy a created wrestler to an empty slot.
- **Move** — Transfer a created wrestler between Game Pak and Controller Pak. Must be on Game Pak before use in a match.
- **Erase** — Delete data from Game Pak or Controller Pak.

---

# 19. Key Memory Addresses (Original ROM)

For recreators who want to faithfully preserve tunable constants, these floating-point values in the original N64 ROM define key behaviors:

|Address|Value|Purpose|
|---|---|---|
|`80156EE0`|50.0 (float)|Factor 1 additive constant|
|`80156EE8`|0.01 (float)|Factor 1 multiplier|
|`80156EF0`|1.2 (float)|Factor 4 Special bonus multiplier|
|`80157A80`|15.0 (float)|Limb-holding threshold|
|`80153610–80153626`|16-bit ints|Standing grapple reversal probability table|
|`801535F8`|16-bit ints|Ground grapple reversal probability table|
|`801535C4`|0.0 (float)|Submission: Expert vs Expert bonus|
|`801535C8`|0.5 (float)|Submission: Expert vs Normal bonus|
|`801535CC`|1.0 (float)|Submission: Expert vs Novice bonus|
|`801535D0`|−0.3 (float)|Submission: Normal vs Expert penalty|
|`801535D4`|0.0 (float)|Submission: Normal vs Normal bonus|
|`801535D8`|0.3 (float)|Submission: Normal vs Novice bonus|
|`801535DC`|−0.5 (float)|Submission: Novice vs Expert penalty|
|`801535E0`|−0.3 (float)|Submission: Novice vs Normal penalty|
|`801535E4`|0.0 (float)|Submission: Novice vs Novice bonus|

## 19.1 Key Player Map Offsets

Per-wrestler state lives in a Player Map structure. Notable offsets:

|Offset|Purpose|
|---|---|
|`0x71`|Reversal flag|
|`0x7C`|Most-damaged limb pointer|
|`0x2F4`|30-second damage log index (counts 0–30)|
|`0x2F8`|Pointer to start of 30-second damage log|
|`0x3A`|(On opponent map) Logged Main Health Damage|
|`0x3C`|(On opponent map) 1-second damage timer|

Any recreation should preserve the semantic purpose of these fields while using native data structures.

---

# 20. Recreation Checklist

## 20.1 Correctness-Critical Math

Preserve exact floor-rounding behavior. Don't substitute `round()` or `ceil()` for `floor()`. The entire damage system depends on these rounding decisions.

Preserve Factor 2's clamp-to-zero (`max(0, A - B)`) — Parameter disadvantage never reduces damage below what Factors 1+3+4 produce.

Preserve Joint Stamina as floating-point, not integer.

Preserve the 0x08 technical-move flag: log damage, reduce Max Health, do NOT reduce Current Health.

Preserve Max Health floor at 64, Max Health ceiling for Current Health regen, and the 25% (floor-divided) Max Health loss ratio.

## 20.2 Correctness-Critical Logic

Reversal input must be a single press, not counted taps.

Reversal input must register before the attacker selects their grapple move (not after).

Strong Grapple health-scaling multiplier cannot compound with the ×2 health case (use elif, not if).

Special-vs-not-Special reversal disable must be absolute — no RNG roll should even run.

Count-weighted kickout taps must use a nonlinear scale, not fixed value per tap.

## 20.3 Feel-Critical Details

25 Spirit bands must be visually distinct; internal Spirit value is a 0–100 integer, but band transitions drive the Attitude Meter color/width changes.

Limb-holding animation must track the single most-damaged non-Flying limb, not every limb below 15.0.

Leg Stamina must continuously scale movement speed, not just trigger a hold animation.

Dizzy minimum dodge/block/counter chance of 10% (rising to 66.7% near wake-up) must be preserved — these preserve player agency.

The 20-second Special timer and its −2-second penalties must be exact.

Outside-the-ring Spirit drain of 8%/4s while opponent is inside must be exact.

Low-HP (<49) comeback bonus of +3 Spirit per action must apply to every spirit-generating action.

---

# 21. Glossary

|Term|Meaning|
|---|---|
|AKI Engine / VPG Engine|The underlying engine shared by AKI's N64 wrestling games|
|Attitude Meter|On-screen representation of Spirit|
|CAW|Created-A-Wrestler; a user-made custom character|
|Current Health|Short-term health pool; regenerates up to Max Health|
|Factor 1–4|The four stages of the Main Health Damage formula|
|Joint Stamina|Per-limb damage accumulation, floating-point, never regenerates|
|Joint Technique Skill|More accurate translation of "Submission Skill"; affects ALL repeating moves|
|Limb-holding|Visual cue when a limb drops below 15.0 stamina; one limb held at a time|
|Main Health Damage|Output of the four-factor damage formula, before Current/Max application|
|Max Health|Long-term health pool; floors at 64, never regenerates|
|Parameter|Any of the 10 Offense/Defense stats (1–5 scale)|
|Reversal|Defender flip of an incoming grapple, triggered by a single input after being grabbed|
|Special / Special Mode|Full-Spirit activated state granting damage boost and finisher access (20-sec timer)|
|Spirit|0–100 morale/momentum value affecting damage, reversals, and dizzy|
|Submission Skill|Wrestler attribute (Novice/Normal/Expert) controlling repeating-move damage scaling|
|Superstar|In-game term for a playable wrestler|
|Technical Move|A move with flag byte 0x1C=0x08; deals notional damage, no Current Health damage|
|Titantron|Entrance video shown during wrestler entry|
|Weight Factor|0–7 value affecting reversal chance and AI behavior|

---

# Appendix A — Ring Attire Reference Tables

## A.1 Ring Attire (Primary)

|Short|Long|Wrestling|Pants|Full Body|
|---|---|---|---|---|
|Basket Shorts|Al Snow|Angle 1|Black Pants|Chyna 1|
|Boxing 1|A.P.A.|Angle 2|Cut Jeans|Chyna 2|
|Boxing 2|Benoit|Henry|Gi 1|Commish|
|Crash 1|Boss Man|Funaki|Gi 2|Gi|
|Crash 2|Cactus|Tazz|Gi 3|Kat|
|Cut Jeans 1|Christian|Wrestling|Grandmaster 1|Outfit 1|
|Cut Jeans 2|Dude||Grandmaster 2|Outfit 2|
|Cut Jeans 3|Dudleys 1||Hardyz Pants|Outfit 4|
|Cut Jeans 4|Dudleys 2||Jeans 1|Puppy|
|Half Tights|D'lo||Jeans 2|Suits 1|
|Hardcore|Eddie 1||Jeans 3|Suits 2|
|Ivory Pants|Eddie 2||Jeans 4|Suits 3|
|Malenko|Edge||Leather Pants 1|Suits 4|
|Mawashi|HBK||Leather Pants 2|Suits 5|
|Mr. Ass|HBK-DX||Lita Pants 1|Suits 7|
|Line Tights 1|Kane 1||Lita Pants 2|Swim Suit 1|
|Line Tights 2|Kane 2||Martial Arts 1|Swim Suit 2|
|Rikishi 1|King||Martial Arts 2|Swim Suit 3|
|Rock 1|Long Tights||Rock Pants|Swim Suit 4|
|Rock 2|Mankind||Scotty 1|Swim Suit 5|
|Saturn|Rios||Scotty 2|Trish 1|
|Semi Short|Road Dogg 1||Test Pants|Trish 2|
|Shamrock|Road Dogg 2||Triple H Pants|Viscera|
|Short Tights|Taka||Zebra Pants|AKI Gi|
|Skirt|Triple H-DX||Original Pants|AKI Man|
|Terri Pants|Undertaker 1||||
|Triple H|Undertaker 2||||
|Valboski 1|X-Pac 1||||
|Valboski 2|X-Pac 2||||
|Val Referee|Y2J 1||||
|Original 1|Y2J 2||||
|Original 2|Original 1–4||||

## A.2 Feet

|Boots 1|Leg Guards|Boots 2|Others|
|---|---|---|---|
|Boots 01–21|Padded 1–9|Pull-Ons 01–19|Athletic 1–5, Kung Fu, Supporter, Tabi, Taped|

## A.3 Entrance Attire

|Accessories|Hats / Caps|Costumes|
|---|---|---|
|Boss Man|Cap|Austin|
|Buh Buh|Godfather|Biker Flannel|
|D-Von|Jim Ross|Biker Jacket|
|Gold Medals||Biker Vest|
|Shades 1–2||DX|
|Too Cool||Edge|
|||Grandmaster|
|||HBK|
|||Jerichoholic|
|||Rikishi|
|||Robe|
|||Showster|
|||Taker Robe|
|||Tazz Towel|
|||Test|
|||Too Cool 1–3|
|||Trenchcoat|
|||Val Towel|
|||Y2J|

## A.4 Weapons / Props

Bat, Sledge Hammer, Night Stick, Barbed Wire 2×4, 2×4, Kendo Stick, Microphone, Head, Water Bottle, Roses, Cane, Bazooka, Goblet, Scales.

Also available for in-match Specific Weapon setting: Metal Chair, Table, Cheese, Foam Finger, Foam Bull, Stop Sign, Steve's Can, The Rock Says, Ring Bell, Fire Extinguisher.

---

_End of Game Design Document._
