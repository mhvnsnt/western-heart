# Soulcalibur VI — Combat Mechanics (Federation Reference)

**Game #8 for the Western Heart chimera build.** Owner-directed 2026-10-13.

**Architecture note (owner):** Tekken's input style stays the base. Soulcalibur contributes
MECHANICS on top — this document is the federation reference for what SCVI brings.

**Sources:** SuperCombo Wiki (wiki.supercombo.gg/w/Soulcalibur_VI/System), community frame data
(Frame Calibur / Dustloop), press coverage. All mechanics below are community-documented;
internal data structures are inferred from player-facing behavior.

---

## 1. Input Model

SCVI is a **3-button fighter** (excluding block): **A** (horizontal), **B** (vertical), **K** (kick),
plus **G** (guard — a dedicated block button, NOT hold-back like Tekken).

- **A (Horizontal):** tracks sidestep. If the opponent steps, horizontals catch them.
- **B (Vertical):** sidesteppable, but longer range and stronger. Forceblock situations exist
  where a vertical at advantage reliably tracks step.
- **K (Kick):** fastest, shortest range, utility.
- **G (Guard):** dedicated button. Movement is free — no back-to-block.

**Notation:** numpad directions (1-9) + button. `66` = double-tap forward (dash), `44` = backdash,
`22`/`88` = sidesteps. Stances entered via attacks or direct input.

**Contrast with Tekken:** Tekken uses 4 limb buttons (1/2/3/4) + hold-back blocking. SCVI's
3-button + dedicated guard is simpler at the input layer but deeper in the defensive layer
(GI, RE, guard stamina). For the chimera: **keep Tekken's 4-button limb inputs**, federate
SCVI's defensive systems (guard stamina, GI, RE) and movement (8-way run).

---

## 2. 8-Way Run (Movement System)

The series' signature movement. Hold or double-tap any of 8 directions → character runs in
that direction. Key properties:

- **Enter instantly**, exit instantly (release directions).
- 8WR attacks: a different move set accessible while running (e.g., running A/B/K).
- Moves performed during 8WR (after 10+ frames in run, except 44/66 moves) become 8WR
  variants — the same input produces a different attack while running.
- **Counterhit state** while running in any direction except forward (same as sidestep).
- Repeated sidesteps/backsteps are faster than 8WR in those directions but have recovery.

**Federation value:** 8-way run gives full planar movement (Tekken is more lane-based with
sidestep as a discrete action). For Western Heart's arena mode (wrestling/Urban Reign
environments), 8WR is the natural movement model. For the Tekken-mode duels, Tekken's
sidestep stays.

**Data model suggestion:**
```
MovementState { mode: STANDING | STEP | RUN_8WAY, direction: 1-9, frames_in_state, counterhit_vulnerable: bool }
Move { ..., requires_8wr_frames: int (0 = any, 10 = must be running 10f), ... }
```

---

## 3. Guard Stamina & Guard Crush

Blocking drains a **guard stamina** meter (separate from health):

- Guarding attacks drains stamina. Health bar glows yellow → red → flashing as stamina depletes.
- **Guard crush:** stamina hits zero → guard breaks, wide open. The punish hit counts as a
  counter hit (combo starters that need CH now work).
- Heavy attacks drain more stamina; small quick attacks can't crush even at low stamina.
- GI and RE also cost small amounts of guard stamina.

**Federation value:** This is a whole defensive-resource layer Tekken lacks. It punishes
turtling and rewards pressure. Portable as-is: `Fighter { guard_stamina: 0-100 }`,
drain per blocked hit by move level, crush at 0.

---

## 4. Guard Impact (GI)

The classic SC parry. Timed button press parries non-break/unblockable attacks.

- **SCVI simplification:** single forward GI (older games had forward + back variants).
- **No meter cost** (unlike SCV). Costs 10% guard stamina instead.
- Reward scales by parried move's level:
  - Light parried → GIer +28 (opponent falls down)
  - Medium parried → GIer +16 (opponent's arms fly up)
  - Heavy parried → GIer +8 (opponent's arms fly sideways)
- **Cancels opponent's actions outright** — the key differentiator vs Reversal Edge.
- Can't block break attacks (blue lightning) or unblockables (red flames).
- **Resist Impact:** enhanced GI (costs ½ soul gauge bar) that WORKS on break attacks
  and unblockables.
- **Auto GIs:** specific moves with built-in GI windows (e.g., Xianghua 6A+B, stance
  transitions). Narrower coverage than manual GI but bigger reward (lethal hit combos).

**Federation value:** GI is the skill-based defensive answer to Tekken's more
read-heavy defense. The move-level-scaled reward (+28/+16/+8) is an elegant,
portable rule.

**Data model suggestion:**
```
Move { ..., gi_window: [start_f, end_f], gi_beats: [light, medium, heavy] | subset (auto GI), ... }
On GI success: attacker_state = GI_STAGGER(level), defender_advantage = {light: 28, medium: 16, heavy: 8}
```

---

## 5. Reversal Edge (RE)

SCVI's signature comeback mechanic. Single-button (R1/RB) universal parry → minigame.

- **6-frame startup** universal parry. Can be HELD to extend the parry window (attack
  eventually comes out automatically).
- Parries high/mid/low (but NOT break attacks or unblockables).
- On successful parry → RE attack. If it lands → **slow-motion minigame**:
  - Each player picks ONE action: A attack, B attack, K attack, Guard, or Step.
  - Rock-paper-scissors triangle: **A beats K, K beats B, B beats A** (roughly;
    exact: 8_2 beats B, loses to A/K; 4 beats K, loses to A/B).
  - Guarding vs B attack → clash restarts (round 2).
  - Stepping the correct way dodges for big damage; wrong way = eat the hit.
- **Charged RE** (held to max): becomes a +8 on block break attack, big chip, big meter.
- **Round 2:** if both pick the same option or G-vs-B, clash continues. Initiator gets
  massive advantage: B attack does 100% guard damage (instant crush), all options
  become lethal hits, initiator wins ties.
- RE builds significant soul gauge (fastest meter builder in the game).

**Federation value:** RE is a momentum-breaker — it lets a losing player force a
mind-game reset. For Western Heart's trial narrative (purification, the self as final
boss), RE's "clash of wills" maps beautifully to soul-vs-soul moments.

**Data model suggestion:**
```
ReversalEdge { startup: 6, holdable: true, parries: [high, mid, low], loses_to: [break, unblockable] }
RE_Clash { initiator, round: 1|2, options: [A, B, K, G, STEP], resolution: RPS_MATRIX }
```

---

## 6. Soul Gauge (Meter)

Two bars. Gained by: attacking (hit/whiff/blocked), getting hit, throws, lethal hits,
just inputs, RE actions, 8WR forward movement. Loser gets 1 free bar when opponent is
at match point.

### 6a. Critical Edge (1 bar)
Metered super. Cinematic on hit. Used for block punishes, whiff punishes, combo enders.
Input: A+B+K+G equivalent. NOT a reversal.

### 6b. Soul Charge (1 bar) — THE mechanic
- Fully invincible burst → knocks opponent back → user enters **enhanced state**:
  - New moves exclusive to Soul Charge
  - Small damage boost
  - Match timer stops
  - **All attacks deal chip damage**
- Defensive answers: GI, RE, or just don't block (chip only applies on guard).

### 6c. Soul Attack (1 bar, Season 2)
Universal 16-frame attack that puts the user INTO Soul Charge.

### 6d. Meter gain rates (per hit)
| Action | Gain |
|--------|------|
| Light hit | 1/60 bar |
| Medium hit | 1/24 bar |
| Heavy hit | 1/15 bar |
| Whiff | 1/120 bar |

**Federation value:** Soul Charge is a install-super with chip damage — a clean,
portable power-up state. Maps to Western Heart's soul-vessel theme directly
(a vessel "charging" their soul = Soul Charge).

---

## 7. Lethal Hit (LH)

New to SCVI. Character-specific moves gain enhanced properties when landed under
specific conditions → slowdown animation → combo opportunity.

- Conditions are per-character and per-move (e.g., Mitsurugi: vertical while rising
  from knockdown; Sophitia: block into downward slash).
- **Impact counter:** the most common — landing an A+B break attack as a counter
  to opponent's GI or RE startup/parry/recovery.
- LH generates significant meter + combo opportunity.
- Training mode lists each character's LH conditions.

**Federation value:** LH rewards matchup knowledge and conditioning. Portable as
conditional move properties: `Move { lethal_hit_condition: <predicate>, ... }`.

---

## 8. Attack Properties

- **5 heights:** high (crouchable), mid (must stand-block), low (must crouch-block),
  special mid (either), special low (either + jumpable).
- **Move levels:** light (0-21 dmg), medium (22-34), heavy (35+). Determines:
  - Clash outcomes (see below)
  - GI reward scaling (+28/+16/+8)
  - Meter gain
  - Guard crush ability (all heavies, some mediums)
- **Clashes:** simultaneous weapon hits compare clash values (light H=1/M=2/H=3,
  verticals +1). Tie → both stagger. Diff 1 → higher wins frame advantage. Diff 2+ →
  higher scores a counter hit. Critical Edge / Soul Attack always win clashes.
- **Counter hits:** during opponent's startup or step vulnerability. Banner + blue arc
  visual. Many moves gain launch/stun only on CH.
- **Throws:** 2 basics + command throws + side/back variants. 17-frame break window.
  Break input = attack button + direction matching throw type. Broken throws still
  deal 5 (non-lethal) damage.

---

## 9. Ring-Out

The arena edge is a kill plane. Knock the opponent out of the ring → round win
regardless of health. (SC's defining spatial mechanic since 1995.)

**Federation value:** Directly portable to Western Heart's arena mode. Ring-out
rules per stage: `Stage { ring_out_enabled: bool, edge_type: WALL | EDGE | INFINITE }`.

---

## 10. What SCVI Federates Into Western Heart

| SCVI System | Western Heart Use | Notes |
|-------------|-------------------|-------|
| 8-way run | Arena-mode movement | Tekken sidestep stays for duel mode |
| Guard stamina / crush | Universal defense resource | New layer Tekken lacks |
| Guard Impact | Skill-based parry | +28/+16/+8 reward rule |
| Reversal Edge | Comeback / soul-clash moments | Maps to trial narrative |
| Soul Charge | Soul-vessel power state | Chip damage + exclusive moves |
| Critical Edge | Metered super | 1-bar cinematic |
| Lethal Hit | Conditional combo starters | Per-character predicates |
| Move levels | Damage/frame taxonomy | Light/medium/heavy |
| Clash system | Simultaneous-hit resolution | Integer comparison |
| Ring-out | Arena-mode kill condition | Per-stage config |
| Weapon ranges | Weapon fighters (SC roster) | Range as move property |
| Stances | Character-specific modes | SC roster imports |

**What stays Tekken:** 4-button limb inputs (1/2/3/4), input notation (f+2, df+1),
hold-back blocking for duel mode, juggle system, wall combos, rage system.

---

## 11. Character Creation (CaS)

SCVI's Create-a-Soul is one of the genre's deepest: race/gender/body morphing,
equipment with stats (in casual modes), full moveset assignment from any
character's style. Relevant to Western Heart's Create Fighter — SCVI's CaS
proves the "any style on any body" model works at retail quality.

---

*Document version: 2026-10-13. Sources: SuperCombo Wiki, Dustloop/Frame Calibur
community data, press coverage. Internal formats not yet reverse-engineered —
game binary not yet acquired (see TEARDOWN.md).*
