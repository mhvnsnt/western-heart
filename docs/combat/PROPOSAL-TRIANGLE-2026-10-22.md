# PROPOSAL — DOA Triangle System, Tekken-ified (NOT YET APPROVED)

**Status:** ON HOLD per user 2026-10-22 ("Tekken doesn't do that for a reason").
**This is a design proposal only. Nothing below is implemented.**
**Teardown source:** `teardown/dead-or-alive-6/DOA6-MECHANICS.md` (§1–2, §6).

---

## 1. What DOA's triangle actually is

A rock-paper-scissors decision engine over three action types:

- **Strikes beat Throws** — hit the thrower before the throw connects.
- **Throws beat Holds** — grab the holder out of their hold attempt.
- **Holds beat Strikes** — a hold reverses an incoming strike.

DOA6 implements it with a dedicated **hold button + direction** (4-way holds:
high / mid-punch / mid-kick / low). Every strike carries a hit level; the hold
must match the level. Wrong level = whiffed hold = punished. Holds deal damage
scaled to the held move, some launch. The triangle is the decision engine of
every exchange — every guess is one side of it.

## 2. Why the user is right to hesitate

Three reasons Tekken skips the universal hold, and all three apply to WH:

1. **Character identity.** A universal hold button gives every fighter the same
   defensive RPS. Tekken's depth comes from *character-specific* defensive
   answers — you learn Asuka's parry, King's chain-throw breaks, Bryan's
   orbital. A universal hold flattens the roster into one guessing game.
2. **Neutral integrity.** Tekken's neutral is frame-tight spacing and punishment.
   A universal "guess right, reverse anything" button injects RPS guessing into
   situations Tekken resolves with frames and reads. It cheapens the exchange.
3. **The beginner trap is real.** DOA's own community calls it "counter-happy"
   play: new players mash holds instead of learning defense. A system whose
   failure mode is *less* learning is a bad fit for a game about mastery.

## 3. The Tekken-ified proposal: the triangle as movelist property, not a button

**Do not add a hold button.** Instead, enforce the triangle's three edges in the
resolver, using tools that already exist or are already planned:

### Edge 1 — Strikes beat throws (already ~true; make it explicit)
Today a 10f jab vs a 12f throw is already a strike win on frames. Proposal:
make it a *rule* — a throw in startup loses **cleanly** to any strike (no
trade, no throw armor). This is a 3-line resolver change and it sharpens the
grappler/striker matchup the Tekken way: the striker's answer to King's
pressure is frame knowledge, not a guess button.

### Edge 2 — Throws beat holds (new rule, tiny)
WH's planned defensive tools (see below) must not catch throws. A throw that
connects against a reversal/sabaki/parry in startup *or* active frames wins
outright — the hold attempt is cancelled into the throw. This is the DOA rule
verbatim, and it keeps grapplers honest against defensive characters.

### Edge 3 — Holds beat strikes (character-specific, never universal)
This is the whole proposal: **holds exist only as character-owned moves.**
The VF5 federation doc (`teardown/virtua-fighter-5/docs/VF5-MECHANICS.md`
§1.4–1.5) already plans exactly the machinery:

- `sabaki_levels: [high, mid]` — a move property: the attack auto-deflects
  incoming strikes of those levels during its active frames, then continues.
- `reversal` — a move category: a defensive move that catches a strike of a
  named level and plays a canned counter.

Those ARE Tekken-ified holds. Aoi-style fighters get reversals; brawlers get
sabaki pressure tools; most of the roster gets neither. The triangle then
**emerges from matchup knowledge** — vs a reversal character, your
strike/throw mixup gains a third axis (bait the reversal, then throw it:
Edge 2). That is DOA's mindgame, but *earned through movelist study* instead
of granted by a button. It makes the game deeper, not simpler.

### Explicitly NOT imported
- The universal hold button and 4-way hold inputs.
- Hold-everything design (DOA6's Break Hold universal escape — see §4).
- The mid-punch/mid-kick hold split as a universal input (it can live as data
  tags on reversals if a character needs it).

## 4. What about Break Blow / Break Hold / Fatal Rush?

Out of scope for this proposal. The break gauge is a separate resource layer
(and WH's meter economy — Nine Souls + Soul Surge — already covers comeback
design). Fatal Rush is an onboarding presentation feature, not a combat
system. If the triangle lands, these can be proposed separately.

## 5. How it would feel

Neutral stays Tekken — frames, spacing, punishment. The triangle surfaces
only in specific matchups: against a reversal/sabaki character, offense
becomes a three-way read (strike the reversal's recovery / throw the reversal
attempt / bait and launch). Defense against that character means knowing
*which* levels their tools cover. No new buttons, no new HUD, no minigame —
just a richer answer to "what do I do on offense."

## 6. Open questions for the user

1. Which fighters get reversal/sabaki tools? (Proposal: grappler-adjacent and
   technician archetypes only — scarcity is what makes the triangle a
   matchup feature instead of wallpaper.)
2. Should the movelist UI label a move's sabaki/reversal coverage, or is that
   lab knowledge? (Proposal: label it — WH is a learning game.)
3. Edge 1 (strikes cleanly beat throw startup) — take it even if the rest
   stays on hold? It's the smallest, safest piece.

## 7. Implementation sketch (only if approved)

- Move schema: `sabaki_levels[]`, `reversal: { beats: [levels] }` (already
  specified in the VF5 federation doc).
- Resolver (`fighter.js receiveHit` + `game.js _resolveCombat`):
  - throw startup vs strike → strike wins cleanly;
  - throw connect vs defender in reversal/sabaki startup/active → throw wins;
  - reversal/sabaki active vs strike of covered level → counter plays.
- Wrong-read punishment falls out of existing recovery frames.
- Estimated: ~120 lines + tests. No input changes. No HUD changes.
