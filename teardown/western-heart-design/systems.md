# WESTERN HEART — SYSTEMS
## Where Tekken's Engine Meets Tong-Nou's Philosophy

---

## 1. FIGHTING CORE (from Tekken 3 teardown)

Western Heart plays like Tekken 3. Not "inspired by" — the actual systems, reimplemented from the reverse-engineered executable:

- **3D movement:** Full 8-way run, sidestep (up/down), backdash canceling. The arena is 3D space, not a 2D plane.
- **Four-button layout:** Left Punch / Right Punch / Left Kick / Right Kick (PS1: Square/Triangle/X/Circle). Every move is a combination.
- **Frame data:** Startup / active / recovery frames per move, extracted from Tekken 3's animation data. Jabs at ~10f startup. Launchers at ~15-20f. This is the competitive skeleton.
- **Juggles:** Launchers pop opponents airborne; air combos are the primary damage source. Gravity, air control, and tech-roll behavior from the teardown.
- **Throws:** Breakable with matching button input (1-break vs 2-break). Unbreakable chain throws for grappler souls.
- **Counter hits:** Hitting during opponent's startup = counter-hit state, bonus damage, guaranteed followups on certain moves.
- **Walls:** Walled stages (Helix Palace, Shrine) enable wall-splat combos. Wall-splat state from teardown.
- **Health:** Standard fighting-game health bar. Depleting it wins the round.

**What we write:** The fighting engine code (GDScript/C# in Godot), implementing these systems from the teardown documentation. The *logic* is reverse-engineered. The *code* is our glue.

---

## 2. REINCARNATION ROUNDS (death-as-progression)

**The core innovation.** In Eastern Mind, dying is required — you must die and be reborn to advance. In Western Heart, losing a round triggers reincarnation.

**How it works:**
1. You lose a round. Your soul dies.
2. **The Reincarnation Screen appears:** Three pairs of eyes. Three noses. Three mouths. (Directly from Eastern Mind's reincarnation mechanic.)
3. You build a new face. Each feature choice modifies your fighter:
   - **Eyes (3 options):** Perception. Affects counter-hit window timing and throw-break window.
     - *Watchful Eyes:* +2f counter-hit confirm window.
     - *Hungry Eyes:* +damage on counter-hits, -defense.
     - *Closed Eyes:* +throw-break window, -counter-hit damage.
   - **Nose (3 options):** Instinct. Affects movement and spacing tools.
     - *Sharp Nose:* Faster sidestep.
     - *Broad Nose:* Longer backdash.
     - *Broken Nose:* Slower movement, +damage on all hits (pain as power).
   - **Mouth (3 options):** Voice. Affects meter gain and special properties.
     - *Silent Mouth:* Faster Nine-Soul Meter gain.
     - *Screaming Mouth:* Chip damage on block increased.
     - *Sealed Mouth:* No chip damage taken, slower meter.
4. You return for the next round — same soul, new face, adapted.

**Design intent:** The player who is losing keeps evolving. This is a comeback mechanic with philosophical weight — you don't lose and stay the same. Death *teaches*. By round 5, both fighters are unrecognizable from round 1 — adapted, scarred, specific to this match.

**Competitive note:** All modifications are sidegrades, not upgrades. Every bonus has a cost. The system rewards adaptation, not losing on purpose.

**Asset note:** The face options are recombined Eastern Mind face-part extractions (the reincarnation screen assets). The 3D face modification is achieved through texture swaps on the Tekken head geometry — no new geometry.

---

## 3. THE NINE-SOUL METER

A second resource bar below health. It fills as you fight (faster with Silent Mouth).

**What it does:** At full meter, you can invoke a **Soul Surge** — a 10-second state where your fighter channels one of the *other* eight souls:
- You temporarily gain access to 3 signature moves from another soul's moveset.
- Your skin flashes with that soul's palette (texture swap).
- The choice of which soul to channel is made at the Reincarnation Screen (your "dominant fragment").

**Design intent:** The nine souls are fragments of one being. The meter expresses this — you are never fully separate from the others. In the fiction, channeling another soul is remembering who you were.

**Asset note:** No new animations. The borrowed moves are existing Tekken animations from the donor movesets, already extracted.

---

## 4. FORCE CLAIMING (elemental progression)

Winning a match in a land's stage claims that land's elemental force. Forces persist across the arcade ladder (and across a versus set, if both players agree to "trial rules"):

| Force | Land | Effect |
|-------|------|--------|
| Wood | Tree of Life | +5% range on all attacks |
| Fire | Plains of Chi-u | +chip damage on block |
| Earth | Shrine Par-fang | -5% damage taken |
| Metal | Helix Palace | Health regen between rounds (10%) |
| Water | Palace of Dreaming | Faster sidestep |

**Claiming all five** (winning in all five land stages) forges a visual change: your fighter's skin gains the **Katana of Five Forces** pattern overlay (Eastern Mind katana bitmap, applied as texture detail). This is cosmetic + a small universal buff (+3% damage). It signals: this soul is becoming whole.

**The Trader (Marketplace):** Instead of claiming a force, you may *trade* one claimed force for a different one. Sometimes adaptation means letting go.

---

## 5. STORY MODE: THE TRIAL OF THE NINE

**Structure:** 7 matches. Elemental order: Wood → Fire → Earth → Metal → Water → Marketplace → Shrine.

| Match | Stage | Opponent | Stakes |
|-------|-------|----------|--------|
| 1 | Tree of Life (Wood) | SHA (tutorial rival) | Learn the trial |
| 2 | Plains of Chi-u (Fire) | TOU | Claim Fire |
| 3 | Shrine Par-fang (Earth) | ZEN | Claim Earth |
| 4 | Helix Palace (Metal) | RETSU | Claim Metal |
| 5 | Palace of Dreaming (Water) | KAI | Claim Water |
| 6 | Phantom Marketplace | THE TRADER | Trade a force (optional) |
| 7 | Octagonal Shrine | THE ASSEMBLED SOUL | Become whole |

(BYOU, JIN, and GYOU appear as mid-ladder challengers in versus-style interrupt matches — "a soul challenges you.")

**Narrative beats (told through pre-fight text cards in Sato's voice — deadpan, sincere, absurd):**
- *Match 1:* "You woke up inside a head. This is normal."
- *Match 3:* "The shrine does not judge. The shrine only watches. Fight anyway."
- *Match 5:* "The Palace of Dreaming changes while you blink. So do you."
- *Match 6:* The Trader offers: "I will buy your Fire. I will sell you Water. All transactions are final. Nothing here is real, but the prices are."
- *Match 7 (pre-final):* "You have claimed the five forces. The katana is forged. Now fight the one who forged it."
- *Match 7 (post-final):* "Tong-Nou was not devouring souls. Tong-Nou was purifying them. The trial was healing all along. You are whole. Rest now."

**The Purifier Twist:** The Assembled Soul is a composite of all nine fighters — including the player's. Its moveset cycles through all nine styles. Defeating it doesn't destroy it. The victory animation is absorption — the composite dissolves into the player character. You don't win by killing yourself. You win by *becoming* yourself.

---

## 6. VERSUS MODE

Standard Tekken-style versus. Best of 3/5/7 rounds. Reincarnation Rounds active (can be toggled off for "pure" rules). Force Claiming optional ("trial rules" toggle). Stage select from all seven.

---

## 7. WHAT MAKES THIS DIFFERENT FROM EVERY FIGHTING GAME

1. **Losing adapts you.** No other fighter makes defeat a character-building mechanic.
2. **The roster is one being.** Nine fragments, not nine strangers. The fiction and the mechanics agree.
3. **The final boss is you.** Not a bigger evil. Yourself, assembled.
4. **The twist is kindness.** The scary head was healing you. No other fighting game ends with "rest now."

---

*Fighting systems: reimplemented from Tekken 3 teardown (in progress). Reincarnation/meters/forces: original game logic (glue code) operating on extracted assets. All visual/audio assets: recombined extractions only.*
