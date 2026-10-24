# Virtua Fighter 5 — Mechanics Federation Doc

**For the Western Heart chimera build.** Owner directive 2026-10-13.
Tekken's input style stays the base. VF contributes MECHANICS on top.

## The VF Design Philosophy

Virtua Fighter is the most technically precise 3D fighter ever made. Its core
design principle: **every situation has a correct defensive answer, and the
attacker must earn every hit.** Where Tekken rewards aggression and knowledge
of long strings, VF rewards frame-tight defense, spacing, and reading the
opponent. This is what we're federating.

## 1. Defensive Mechanics

### 1.1 Guard System
- **Hold back to guard** (same as Tekken — maps directly)
- **High guard** blocks high + mid attacks
- **Crouch guard** blocks low + mid attacks
- **Guard is NOT absolute:** throws beat guard (same as Tekken)

**Federation:** No change needed. Tekken's guard system is compatible.

### 1.2 Evade (Sidestep)
- VF pioneered 3D sidestepping: **tap up or down** to sidestep
- **Successful evade** (dodging an attack) grants frame advantage
- **Evade throw escape:** inputting a throw escape during evade covers both options
- **Offensive move (OM):** sidestep into attack — sidestep cancelled into a strike

**Federation:** Tekken already has sidestep (up/down). Adopt VF's **successful evade
advantage** — if you sidestep through an attack's active frames, gain +frames.
Add **OM-style attacks**: specific moves that can only be done from sidestep.

### 1.3 Throw Escapes
- VF throws are broken by inputting the **correct throw direction + P+G** during throw startup
- **Multiple throw escapes:** can input up to 2-3 escape directions in sequence
- **Throw escape hierarchy:** some throws are unbreakable (catch throws)
- **Evade throw escape guard (ETEG):** the high-level defensive option select

**Federation:** Tekken has 1+2 / 1+3 / 2+4 throw breaks. Adopt VF's **multi-escape
input** — allow buffering 2 throw break inputs during throw startup animation.
This deepens the throw mindgame without changing Tekken's input scheme.

### 1.4 Sabaki (Parry/Deflect)
- **Sabaki moves:** attacks that simultaneously deflect incoming strikes of a
  specific level (high/mid/low) and counter-attack
- Example: Aoi's `b,b+P+K` sabakis high/mid punches
- **Inashi:** catch-and-redirect moves (Aoi's specialty) — catches a strike and
  throws the opponent using their own momentum

**Federation:** New move property: `sabaki_levels: [high, mid]` — a move with
this property auto-deflects incoming strikes of those levels during its active
frames, then continues its own attack. Maps to Tekken's existing "power crush"
concept but directional and level-specific. Add as a new Extra Move Property
in the TKMovesets-style data model.

### 1.5 Reversals
- Aoi can **reverse** (catch and counter) most strikes with correct timing
- High/mid/low reversals as separate moves
- Some characters have limited reversals (e.g., vs punches only)

**Federation:** New move category: `reversal` — a defensive move that, on
successful catch of a strike, plays a canned counter animation. Add reversal
slots to the moveset system (like WWE reversal slots, but strike-specific).

## 2. Weight Classes

VF divides the roster into weight classes that affect combo physics:

| Class | Characters | Effect |
|-------|-----------|--------|
| Feather | Eileen, El Blaze, Aoi, Pai | Launch higher, juggle longer, take more throw damage |
| Light | Sarah, Lion, Lei-Fei | Standard juggle |
| Middle | Akira, Jacky, Kage, Brad, Goh, Vanessa | Standard |
| Heavy | Wolf, Jeffry | Launch lower, juggle shorter, take less throw damage |
| Super Heavy | Taka-Arashi | Resists launchers, minimal juggle |

**Federation:** Add `weight_class` to every fighter's character data. The juggle
system reads weight class to scale launch height and combo gravity. This is a
pure data addition — no input changes. Tekken's juggle system gets VF's
physicality.

## 3. Ring-Out System

- VF stages have **no invisible walls** (most stages). Fight near the edge and
  you can be knocked out of the ring = lose the round.
- **Ring-out happens when:** both feet cross the ring boundary while in hit-stun
  or from a throw near the edge
- **Half-fenced stages:** walls on some sides (VF5 added these), wall combos
  possible on walled sides, ring-out on open sides
- **Stage size matters:** smaller stages = more ring-out pressure

**Federation:** Add `ring_out_enabled` to stage data. For arena-mode stages
(from WMXIX), enable ring-outs on stages without full walls. New round-loss
condition: `both_feet_out_of_bounds && in_hitstun`. This gives the wrestling
arena mode a real VF-flavored danger zone.

## 4. Stance System (Open/Closed)

- Fighters have **open stance** (opposite feet forward) or **closed stance**
  (same feet forward) relative to each other
- Stance changes after certain moves (stance-switching attacks)
- **Affects:** throw break directions, some move tracking, combo routing
- High-level VF is heavily stance-dependent

**Federation:** Add `stance: open|closed` to the fight state. Certain moves
have `stance_change: true`. Throw break input directions are relative to
stance. This is advanced — implement as a Phase 2 federation after the core
defense mechanics land.

## 5. Counter Hit System

| Type | Trigger | Effect |
|------|---------|--------|
| Normal hit | Opponent not attacking | Base damage |
| Minor counter | Opponent attacking (different move) | +25% damage, slight advantage |
| Major counter | Interrupting opponent's attack startup | +50% damage, crumple/launch |

**Federation:** Tekken already has counter hits. Adopt VF's **two-tier** system
(minor/major) instead of Tekken's single counter-hit flag. Add `counter_tier`
to hit resolution.

## 6. Frame Data Philosophy

VF's core loop at high level:
1. **Attack** → if blocked, you're at disadvantage (negative frames)
2. **Defender's turn** → they attack with a fast move
3. **Attacker must defend** → guard, evade, or use a sabaki
4. Back to step 1 — this is called **"the exchange"**

Key numbers (VF5):
- Fastest attacks: 10-12 frames (jabs)
- Most launchers: 16-20 frames, very punishable on block (-15 or worse)
- Throw: 10 frames, beats guard
- **Fuzzy guard:** crouch-dash into standing guard to block both mid and throw (advanced technique)

**Federation:** This is a tuning philosophy, not a system. When building
fighter movelists, ensure every launcher is properly punishable and every
string has a real defensive answer. The moveset data model already supports
this via frame advantage fields.

## 7. Okizeme (Wakeup Game)

VF has the deepest wakeup game in 3D fighters:
- **Tech roll:** roll on landing to avoid ground pressure (left/right/neutral)
- **Rising attacks:** kick or punch while getting up (mid or low)
- **Downed attacks:** stomp/pounce on a downed opponent (some guaranteed)
- **Ground throw:** catch a downed opponent (character-specific)

**Federation:** Add `tech_roll` options to the knockdown state. Add rising
attack slots to the moveset system. Downed attack moves get a new slot
category. This significantly deepens Tekken's oki game.

## 8. Wall System

- **Half-fenced stages:** walls on 2 sides, open on 2 sides
- **Wall stagger:** hitting a walled opponent causes a stagger (combo extender)
- **Wall throw:** some throws can be done against the wall for extra damage
- **No infinite wall combos:** wall pushback limits combo length

**Federation:** For walled stages, add `wall_stagger` reaction. Wall combo
scaling already exists in Tekken's system — adopt VF's pushback limiter to
prevent infinites.

## Federation Summary

| VF System | Western Heart Layer | Input Change? |
|-----------|-------------------|---------------|
| Guard (hold back) | Already in Tekken | No |
| Evade advantage | Add +frames on successful sidestep-through | No |
| OM attacks | New move flag: `from_sidstep_only` | No |
| Multi throw escape | Buffer 2 break inputs | No |
| Sabaki | New move property: `sabaki_levels` | No |
| Inashi/Reversal | New move category: `reversal` | No |
| Weight classes | New character data: `weight_class` | No |
| Ring-outs | New stage flag + round-loss condition | No |
| Open/closed stance | New fight state (Phase 2) | No |
| Two-tier counter hits | Replace single CH flag | No |
| Tech roll / rising attacks | New moveset slots | No |
| Wall stagger | New reaction type | No |

**The rule holds:** Tekken's inputs are the language. Every VF mechanic above
plugs into the existing input scheme with zero changes to how the player
controls their fighter.
