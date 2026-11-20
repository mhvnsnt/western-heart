# Dead or Alive 6 — Combat Mechanics Federation Doc

**Source:** Team Ninja / Koei Tecmo, released March 1, 2019 (PC/PS4/Xbox One)
**Status:** Mechanics documented from competitive community sources (freestepdodge.com,
gaming press). Full game pull blocked: ~50GB+ install, local disk at 93%.
**Why DOA6 matters to Western Heart:** Tekken's input style stays the base. DOA6 contributes
its counter/hold layer ON TOP — the triangle system, holds, stun game, and break gauge
are the mechanics we're federating into the chimera.

---

## 1. The Triangle System

The core of DOA. A rock-paper-scissors relationship between three action types:

- **Strikes beat Throws** — attack the thrower before the throw connects
- **Throws beat Holds** — a thrower grabs the holder out of their hold attempt
- **Holds beat Strikes** — a hold reverses an incoming strike

One button for each attack type (punch, kick, hold/throw context). The triangle is the
decision engine of every exchange — every guess is one side of the triangle.

**Federation note:** This is a *layer*, not a replacement. Tekken's move inputs stay.
The triangle maps onto the resolver as a new reaction table: when a hold input is
matched against an incoming strike within the hold window, the strike's move is
cancelled and the hold's counter animation + damage plays instead. The throw-beats-hold
and strike-beats-throw edges are throw-tech/whiff rules in the same table.

---

## 2. The Hold System

Holds are DOA's counters — the deepest defensive mechanic in the game.

### 2.1 Hold levels (4-way holds in DOA6)
Every strike has a **hit level**, and holds are matched to levels:
- **High holds** — counter high strikes
- **Mid-punch holds** — counter mid punches (split from kicks)
- **Mid-kick holds** — counter mid kicks
- **Low holds** — counter low strikes

DOA6 uses the **4-Way Hold** system: each direction counters a specific move level.
Input is hold button + direction. Guessing the wrong level = whiffed hold = punished.

### 2.2 Hold types
- **Defensive holds (DH)** — the standard counter. Reverses the opponent's strike,
  deals damage, sometimes launches or grants frame advantage.
- **Advanced holds / expert holds** — character-specific holds with tighter timing
  or extra properties (some deal heavy damage, some reposition).
- **Parries** — some characters have parries that grant frame advantage instead of
  damage, feeding the stun game instead of ending it.
- **Offensive holds** — holds used proactively in neutral, not just as reversals.

### 2.3 Hold damage and properties
Holds deal damage scaled by the held move's strength. Some holds launch. The hold
game is a *read* game: you must know the opponent's strings, string-enders, and
go-to moves to hold correctly. Panic-holding is a known beginner trap (community
calls it "counter-happy" play).

**Federation note:** Hold levels map onto Tekken's hit-level system (high/mid/low)
which already exists in the move data. The 4-way split (mid-punch vs mid-kick) is
a new tag on incoming strikes. The hold resolver: `hold_input(level) + active
strike(level) within window → counter`. Wrong level → hold whiffs with recovery
frames. This slots into the existing moveset slots as a new "counter" category.

---

## 3. The Stun System

DOA's combo engine. Strikes don't just do damage — they inflict **stun**, and the
stun state is where the real game happens.

### 3.1 Stun types
- **Critical stun** — the standard stun. Opponent is dazed, player has frame
  advantage. Can be extended with follow-up strikes, converted into a launch,
  a knockdown, or used to restrike before the opponent recovers.
- **Critical burst** — a stun state that guarantees a follow-up (the burst
  "pops" the opponent for a free hit).
- **Fatal stun** — inflicted by Fatal Rush (see §5). Opponent cannot hold out of
  it with a normal hold — it's unprotected.

### 3.2 Slow escape
Most stuns can be **slow-escaped**: the stunned player spins the stick rapidly to
recover faster. This is the defender's counterplay inside the stun game — the
attacker must know which stuns are escapable and time their follow-ups accordingly.
Three stun types cannot be slow-escaped (community knowledge; character-specific).

### 3.3 Stun → launch → juggle
- **Launch attacks** send the opponent airborne for juggle follow-ups, air-throws,
  wall hits. Some launch on normal hit; all launch on counter/hi-counter hit;
  all launch during stun (the opponent can't do anything while launched).
- **Knockdown attacks** put the opponent on the ground, often with knockback that
  carries into walls.

**Federation note:** The stun system is a *state machine overlay*. Tekken moves
already have counter-hit properties; DOA's contribution is the *stun depth* —
critical stun as a distinct state with slow-escape counterplay, and the
stun→launch→juggle pipeline as an explicit combo grammar. This can be layered
onto the existing move properties as new reaction types.

---

## 4. The Break Gauge (DOA6's meter system)

New to DOA6, replacing DOA5's Power Blow system. A meter under the HP bar that
fills as you deal damage (and shifts with hold-game success).

### 4.1 Break Blow
- Costs the full gauge. A cinematic power strike.
- Beats high and mid attacks, **can even break throws** — the "invincible attack."
- Loses to lows and to Break Holds.
- Can be woven into juggles and used with the environment.
- Unlike DOA5's Power Blow, does NOT require low health — it's meter-gated.

### 4.2 Break Hold
- Costs gauge. A universal defensive option: **hold anything from any stun state**.
- The defender teleports behind the attacker and deals damage.
- The panic-button answer to pressure — but it costs meter, so it's a resource
  decision, not a free escape.

**Federation note:** The break gauge is a *resource layer* independent of the
triangle. In Western Heart terms: a per-round meter that buys either an
armored offensive option (Break Blow) or a universal defensive escape
(Break Hold). Clean to implement as a gauge + two special move entries.

---

## 5. Fatal Rush

DOA6's auto-combo for accessibility (Special button pressed repeatedly):
- A 4-hit string (S, S, S, S) any character can do.
- First hit inflicts **Fatal Stun** (unholdable).
- If the break gauge is full, the last hit can convert into a Break Blow.
- Deliberately unsafe on block, no invincibility — it's a teaching tool, not a
  competitive crutch.

**Federation note:** Fatal Rush is a *presentation-layer* feature — a canned string
any character can access. In Western Heart it maps to a universal beginner string
per fighter, useful for onboarding.

---

## 6. Throws

- **Normal throws** — beat holds (triangle edge), lose to strikes.
- **Offensive holds** — some characters have throws that function as holds.
- **Ground throws, air throws** — situational, tied to launch/juggle states.
- **Throw breaks** — the defender can break neutral throws with a reaction input.

---

## 7. Movement (DOA6 additions)

- **Sidestep Attack (SSA)** — new in DOA6: attack out of sidestep, giving the
  3D movement a direct offensive payoff.
- Standard 8-way movement with DOA's fast sidestep.

---

## 8. Stage Mechanics

- **Danger Zones** — walls and hazards that add damage (exploding walls, etc.).
- **Multi-tier stages** — knock the opponent off a ledge to change floors.
- Wall splat combos are a core damage source; "the 20 damage rule" governs
  rising-kick punishes at the wall (community lab work).

---

## 9. Roster (DOA6, 24 story characters + DLC)

Kasumi, Ayane, Hayate, Ryu Hayabusa, Tina Armstrong, Bass Armstrong, Jann Lee,
Leifang, Gen Fu, Zack, Leon, Bayman, Christie, Helena Douglas, Kokoro,
La Mariposa (Lisa Hamilton), Eliot, Mila, Rig, Diego, NiCO, Tamaki, Raidou,
Honoka, Marie Rose, Phase 4, Nyotengu, Kula Diamond (guest), Mai Shiranui (guest).

---

## 10. File Formats (for future extraction)

- **Models:** `.g1m` (Koei Tecmo proprietary model format)
- **Textures:** `.g1t` (Koei Tecmo proprietary texture format)
- **Engine:** Team Ninja's in-house engine (DOA5 lineage)
- **Steam App ID:** 838380
- The DOA5/DOA6 modding community has g1m/g1t converters (community tools exist;
  pull these in per the PULL-IN DIRECTIVE when extraction begins)

---

## 11. Federation Summary — what DOA6 gives Western Heart

| DOA6 system | Western Heart layer |
|---|---|
| Triangle (strike > throw > hold > strike) | Reaction table overlay on the resolver |
| 4-way holds (high/mid-P/mid-K/low) | New counter category in moveset slots; level tags on strikes |
| Critical stun + slow escape | Stun state machine; defender counterplay input |
| Stun → launch → juggle grammar | Combo reaction pipeline on move properties |
| Break gauge | Per-round resource meter |
| Break Blow (armored, beats throws) | Gauge-spend offensive special |
| Break Hold (universal escape) | Gauge-spend defensive special |
| Fatal Rush (S,S,S,S) | Universal beginner string per fighter |
| Sidestep Attack | Movement-to-offense bridge |

Tekken inputs stay the base. DOA6's systems layer on top as the counter/hold/stun
game — the defensive depth that makes the neutral game a triangle instead of a
slugfest.
