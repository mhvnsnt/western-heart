# WESTERN HEART — UFC Grappling Design
## Clinch, takedowns, and ground fighting, per-character, in Tekken's language

*Design reference. Mechanics first, universe flavor second. Every mechanic traces to Tekken research or UFC systems — nothing invented.*

**Federation rule (CHIMERA-ARCHITECTURE.md):** *"Tekken's inputs are the language. Every federated mechanic must speak that language."*

---

## 1. Grappling Depth Tiers

Tekken does not give every character the same grappling game. Research confirms the differentiation is real and structural:

- **King (T8)** has **48 throws total**, including branching chain throws (multi-throws) with multiple escape points per link. Each game adds to his grapple set — T3 added ground grapples, T5 added air throws and Jaguar Step chains, T6 added wall throws. He is the grappling ceiling.
- **Nina** has "the most extensive grapple set after King" (community consensus, Tekken 7 era). Assassin-style chain throws, arm-break sequences.
- **Armor King** is classified as a **brawler**, not a pure grappler — rougher striking, less chain-throw depth than King despite the shared wrestling aesthetic.

Western Heart follows the same principle: grappling depth is a **character property**, not a system-wide toggle. Four tiers:

### Tier 1 — Wrestler
Full chain throws with branching paths. Ground grapples. Clinch mastery — every clinch option available, fastest transitions, most damaging holds. One fighter lives here.

### Tier 2 — Grapple Specialist
Deep throw game (multiple command throws, some chains but shorter than Tier 1). Full clinch access. Differentiated by *style* — each fighter's grappling expresses their discipline, not King's wrestling.

### Tier 3 — Brawler
Basic throws plus a brawler's clinch: dirty boxing emphasis, fewer position options, no chains. The clinch is a phone booth, not a chessboard.

### Tier 4 — Basic
Standard Tekken throws (1+3 / 2+4 and side/back variants). No chains. Clinch entry available but limited options inside — they can start it, they can't run it.

---

## 2. UFC Layer Mapped to Tekken Inputs

Everything below uses Tekken notation only: **1** (left punch), **2** (right punch), **3** (left kick), **4** (right kick), plus **f/b/u/d** directions. No new buttons. No mode switch.

### 2.1 Clinch Entry

The clinch is entered as a **throw variant**, not a new system. From neutral:

| Input | Result |
|---|---|
| `f+1+2` | Clinch entry (high) — opponent breaks with `1+2` on reaction, same timing as a throw break |
| `d/f+1+2` | Clinch entry (mid) — catches crouching opponents |
| Whiffed throw at close range (Tier 1–2 only) | Cancel into clinch instead of recovering — the wrestler's option |

Breaking clinch entry uses the existing throw-break system. Nothing new to learn.

### 2.2 Inside the Clinch

The clinch is a **two-person stance**. Both fighters are locked at close range. Movement is disabled; all inputs are clinch actions.

| Input | Action |
|---|---|
| `1` / `2` | Dirty boxing — short punches, elbows. Fast, low damage, builds frame advantage |
| `3` / `4` | Knees and position battles. Slower, higher damage, advances clinch position on hit |
| `u` / `d` | Pummel for underhooks / overhooks. Wins the inside position — unlocks stronger `3`/`4` |
| `f` | Drive opponent toward the wall. Wall reached = wall-splat throw available |
| `b` | Break the clinch — costs frames, punishable if read (like a slow backdash) |
| `1+2` (on opponent's `3`/`4`) | Block the knee, reverse position |

**Position track (hidden):** Underhook advantage → Double underhooks → Body lock. Each level unlocks a throw. Losing the pummel battle drops you a level. This is the UFC clinch game (single collar → double underhooks → body lock) expressed as Tekken inputs.

**Tier gating:** Tier 4 fighters cannot pummel (`u`/`d` does nothing for them). They get `1`/`2`/`3`/`4`/`b` only — they can brawl in the clinch but can't win the position battle.

### 2.3 Takedowns

From the clinch (requires underhook advantage or better, Tier 1–3):

| Input | Result |
|---|---|
| `d+1+3` | Single-leg attempt. Opponent sprawls with `d+1` (timing-based, like a throw break) |
| `d+2+4` | Double-leg attempt. Opponent sprawls with `d+2` |
| `d/b+1+2` (Tier 1–2) | Trip/throw — Judo-style, uses opponent's forward pressure |

Failed takedown = both fighters return to neutral, attacker at frame disadvantage. Successful takedown = ground phase.

**Tier 4** cannot attempt takedowns. They can only break the clinch.

### 2.4 Ground Phase

New layer, Tekken language. The grounded fighter is on their back; the standing fighter has top position. (No separate "guard/half-guard" visual states in v1 — position is tracked internally and expressed through available options.)

**Top fighter:**

| Input | Action |
|---|---|
| `1` / `2` | Ground strikes. Fast, chip damage, keeps opponent down |
| `3` / `4` | Heavy ground strikes. Slower, real damage, riskier (opponent can time a reversal) |
| `u` | Advance position — side control → mount. Each advance unlocks a submission attempt |
| `d` | Disengage — stand up, return to neutral at advantage |
| `1+2` (at mount, Tier 1–2) | Submission attempt — opponent escapes with `1+2` mash (like a chain-throw escape) |

**Bottom fighter:**

| Input | Action |
|---|---|
| `1` / `2` | Block / cover. Reduces ground-strike damage |
| `3` / `4` | Bridge and shrimp — escape attempt. Timing-based; succeeds if top fighter is mid-strike |
| `3+4` | Technical standup — costs significant frames, punishable, but returns to neutral |
| `u` (Tier 1–2) | Sweep reversal — flips to top position if timed during opponent's heavy strike |

**Design note:** The ground phase is deliberately simpler than UFC's full positional system. Tekken has no ground-fighting precedent — this is new territory, so v1 keeps it readable: top hits, bottom escapes, position advances unlock submissions. Depth comes from the *timing* (strike vs. escape reads), not from a complex position tree.

### 2.5 What This Is Not

- **Not a separate "grappling mode."** The clinch is a stance. The ground is a phase. Inputs never change meaning globally — they're contextual, the way `d+1` means different things standing vs. crouching vs. grounded in Tekken already.
- **Not UFC controls.** Nobody learns a new control scheme. A Tekken player understands every input on first exposure because the *language* is unchanged.
- **Not mandatory.** Strikers can play entire matches without entering the clinch. The system rewards grapplers without forcing anyone into it.

---

## 3. Per-Character Assignment

### Tier 1 — Wrestler

| Fighter | Source | Reasoning |
|---|---|---|
| **Pantera** | King | The only true wrestler on the roster. King's 48-throw game, chain throws, and Jaguar Step mixups map directly. Pantera's canon philosophy — *"The hold is honest. Everything else is negotiation."* — is the design brief. Full clinch, all takedowns, ground submissions, chain throws with branching paths. |

### Tier 2 — Grapple Specialist

| Fighter | Source | Reasoning |
|---|---|---|
| **Yukihyō** | Armor King | Tekken classifies Armor King as a brawler/wrestler hybrid — rougher striking than King, less chain depth, but a real grappling game. Yukihyō gets the hybrid treatment: strong throws, short chains (2–3 links, not King's 5+), full clinch. |
| **Awa Pop** | Nina | Nina has the most extensive grapple set after King. Awa Pop inherits the assassin's grappling: arm-break chains, Aikido redirections expressed as clinch reversals. Her sweetness is the misdirection — the holds are real. |
| **Torch** | Anna | Nina's sister, same assassin discipline. Mirrors Awa Pop's depth with a darker edge — her chains end in damage, not control. |
| **Thor** | Ganryu | Sumo *is* clinch fighting. The mawashi grip, the belt battles, the push-out — Thor's entire discipline is the `u`/`d` pummel game and the `f` wall-drive. Limited chain throws (sumo doesn't chain), but the deepest clinch position game on the roster after Pantera. His takedowns are trips and throws, not shots. |

### Tier 3 — Brawler

| Fighter | Source | Reasoning |
|---|---|---|
| **Bruno** | Miguel | Street brawler. Miguel's style is raw power punches — in the clinch, that translates to dirty boxing. Bruno gets `1`/`2`/`3`/`4` in the clinch and basic takedown defense, but no pummel game and no chains. His clinch is a bar fight, not a wrestling match. |

### Tier 4 — Basic

Everyone else. Standard Tekken throws (`1+3`, `2+4`, side/back variants). Clinch entry available (`f+1+2`) but no pummel, no takedowns, no ground submissions. They can start a clinch exchange and throw basic strikes inside it, but a Tier 1–2 fighter will systematically dismantle them there — which is the point. The tier gap *is* the matchup.

**Notable Tier 4 cases:**
- **Demonio** (Jin) — Mishima karate is a striking art. His throws are fundamental, not featured. Correct at Tier 4.
- **Skull** (Bryan) — Brutal kickboxing. Bryan has throws in Tekken but they're not his identity. Tier 4.
- **Dio** (Akuma) — The Satsui no Hado doesn't grapple. It kills. Tier 4.
- **King Tyrant / Star** (Eddy/Christie) — Capoeira has ground flow, but it's acrobatic, not grappling. Their ground game is movement, not holds. Tier 4 for grappling; their mobility is their defense against it.
- **SAM-UR-A1 / Cyborg X** — Built fighters. Their grappling is mechanical: basic holds, no chains. The machine doesn't improvise. Tier 4.

---

## 4. Universe Integration (Eastern Mind / Western Heart)

Mechanics first — but the universe gives them weight. All connections below use **existing canon only** (CANON.md). Nothing invented.

### 4.1 The Clinch Is the Fragments Pressing Together

The nine souls are fragments of one being (CANON.md §4). In the clinch, two vessels are chest-to-chest, souls pressed against each other through flesh. This is the closest any two fighters get to remembering they were once whole. The design implication: **clinch exchanges build Soul Meter faster than any other action.** The game rewards what the fiction demands — the fragments seeking each other.

### 4.2 Pantera Remembers Nothing but the Clinch

CANON.md: *"A soul that remembers nothing but the clinch — the grip, the hold, the throw."* Pantera's Tier 1 status isn't a balance decision. It's canon. TOU (闘 — battle itself) expresses through the hold because the hold is the purest form of battle: no distance, no deception, just force answering force. When Pantera enters the clinch, the tail stops circling (CANON.md signature detail: *"the tail tells you when the hold is coming"*) — a visual tell wired to the mechanic.

### 4.3 The Ground Is the Earth

The Octagonal Shrine Par-fang is the Source. Element: **Earth** (CANON.md §1). Demonio's element is Earth — *"the still point at the center."* The ground phase takes place on the Earth element's terms: stillness, weight, the end of movement. A fighter who is grounded has been brought to the Source — the place where the trial's questions are asked without words. Mechanically: **ground-phase damage scales with the attacker's Earth force** (per the Ladder system, §5: claiming Earth solidifies defense — here, it deepens the hold).

### 4.4 Reincarnation Preserves the Holds

CANON.md §1: *"Death adapts you. The soul that loses and returns is not the soul that fell."* The Reincarnation gives fighters new faces — but muscle memory isn't in the face. A fighter who learned the clinch in a past life keeps it. Design implication: **grappling proficiency is soul-bound, not vessel-bound.** In systems terms, a player's clinch/ground skill persists across Reincarnation Rounds even as their striker toolkit shifts with the new face. The hold is the part of you death can't take.

### 4.5 Soul Surge Borrows Holds

The Nine-Soul Meter lets a fighter channel one of the other eight souls for ten seconds, borrowing its signature techniques (CANON.md §4). During Soul Surge, a Tier 4 fighter can borrow Pantera's Tier 1 clinch game — for ten seconds, the striker wrestles. The fiction: *the fighter remembers being whole.* The mechanic: temporary tier elevation, telegraphed by the surge visual. This is the system's comeback mechanic and its most dramatic moment — the fragments remembering each other through the hold.

### 4.6 Waterfall Feels Every Hold

CANON.md: Waterfall *"feels the nine souls — every fragment's pain, every death, every reincarnation passes through her."* She is the trial's witness. In the clinch — where souls press closest — she feels the most. Design implication (presentation, not mechanics): during Waterfall's matches, clinch and ground phases trigger a subtle visual/audio shift — the game acknowledging that she feels what the player is doing. She weeps. The hold continues. This is flavor, not balance — but it's the kind of flavor that makes a system *belong* to its universe.

### 4.7 What This Doesn't Do

- No new souls, vessels, or lands are introduced by this system.
- No existing canon is contradicted or reinterpreted.
- The Trader, the Phantom Marketplace, and Sun Rā's realm are untouched — the grappling system doesn't need them.
- ZEN and GYOU remain unvesseled. Their absence from the tier list is canon, not oversight.

---

## 5. Implementation Notes

- **v1 scope:** Clinch entry, clinch striking/position, takedowns, basic ground phase (strikes + escapes + technical standup). Submissions and sweep reversals are v2.
- **Balance anchor:** Pantera is the grappling ceiling. If anyone out-grapples Pantera, the tier system is broken.
- **Netcode consideration:** Clinch and ground are timing-heavy (breaks, reversals, escapes). These need the same rollback priority as throw breaks in Tekken netcode.
- **Tutorial:** The clinch must be teachable in under 60 seconds: "It's a throw that doesn't end. Punch with 1/2, knee with 3/4, push with directions, break with B."

---

*Design doc 2026-10-14. Grounded in Tekken throw research (King 48 throws, Nina 2nd deepest, Armor King brawler classification) and UFC clinch/ground systems. Universe connections use CANON.md only.*
*The owner's game. Built from understanding, not imitation.*
