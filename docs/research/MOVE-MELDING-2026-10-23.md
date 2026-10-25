# MOVE MELDING — Wrestling Empire's procedural move combination, WH-native design

Date: 2026-10-23. Lane: Destruction + MDickey Systems integration lead.
Owner instruction (verbatim): "Pulling everything from the list and wire it all up and where it'll work and where it's appropriate"

> **License firewall note:** MDickey's code is proprietary. This document studies the
> PUBLIC design (interviews, dev blog) and specifies a WH-native implementation.
> No MDickey code was read, copied, or ported. All code in `game/js/ai/move-melding.js`
> is original.

---

## 1. What Wrestling Empire actually does (sources)

**The Wrestling Estate interview** (https://estate.w1wrestling.com/mdickie-builds-wrestling-video-game-empire/):

> "In most games, you'll have to grapple your opponent at the exact same time as your
> partner to execute a double-team move. Now? **You can literally combine moves in real
> time**, leading to a web of infinite possibilities. Have you ever seen a
> **hurricanrana-to-a-piledriver** before? How about a **back body drop-to-a-vertical
> suplex**? Both of these maneuvers are now possible thanks to the new physics system,
> and it doesn't end with double-team moves. You can now **throw your opponent into the
> air only for them to land on someone else and execute a counter** that may or may not
> include an Ace Crusher or Rear Naked Choke."

> "My favorite thing about these games is thinking about **all the ways one human body
> can interact with another human body**," Dickie said. "And what's great about video
> games is I don't have to be realistic about it, so I can do all these ungodly things
> you wouldn't necessarily see in a real wrestling match. **I put a lot of effort into
> this animation system where anything can happen at any moment.** You wouldn't believe
> all the hours I've put into thinking how one can counter a hurricanrana. It's like
> solving a puzzle. **With every new move added to the game, there is a new counter
> and a new hybrid to be added as well.**"

**Old School Gamer Magazine interview** (https://www.oldschoolgamermagazine.com/old-school-gamer-magazine-exclusive-mat-dickie-talks-wrestling-empire/):

> "There is a new **'move melding' system where any move can blend into any other at
> any moment**, along with **new lying grapples that increase your chances of doing so
> deliberately**."

**MDickie's dev blog — how the sausage is made** (http://mdickie.com/code_wm2008_moves.htm,
public Blitz3D-era notes, design facts only):

- Moves are procedural/keyframed animation sequences; a move is "done" when its
  animation timer hits the exact end frame — `pAnimTim(cyc)` must name the EXACT
  moment the animation ends or the transition looks jumpy.
- Moves do NOT get smooth blending for free: Dickie covers the cracks himself with a
  `SharpTransition()` call — both the anim-change and the transition name the SAME
  animation id (e.g. 150 = lying on back, 152 = lying on front), so both bodies agree
  on the shared end pose. The call also takes the exit ANGLE (0 = unchanged, 180 =
  tossed onto back) and whether to commit the location change.
- Every finished move registers in a data table ("Moves" section of `Values.bb`);
  the move list count increments — **moves are data, and the roster of melds grows
  by adding rows**.
- Double-team precedent (2007 blog): "Whenever two wrestlers attempt to grab someone
  at the same time, a dual animation is now triggered instead of a regular one...
  4 alternatives to cover each combination of positions" — melds keyed off
  **position combinations**, a pattern we reuse.

### The design, distilled (no code — just the ideas)

1. **Moves are interruptible at phase boundaries.** A move isn't atomic; it has
   internal structure (our phases: entry → contact → payload → release).
2. **Any move can blend into any other at any moment** — constrained in practice by
   body mechanics: the end pose of move A must be a legal start pose of move B
   (Dickie's "puzzle": how does a body get from a hurricanrana into a piledriver?).
3. **Counters are first-class melds.** A counter isn't a separate system — it's a
   meld edge where the *victim* becomes the attacker of the hybrid.
4. **Every new move adds a new counter + a new hybrid.** The possibility space grows
   combinatorially, which is why the move table is data, not code.
5. **Transitions are covered, not blended.** MDickey doesn't crossfade; he snaps both
   bodies to an agreed shared pose (`SharpTransition`) and commits root motion.
6. **Deliberate melding is a skill input.** Lying grapples exist specifically to
   *raise the chance of melding on purpose* — i.e., meld windows are also a control
   surface, not just AI spice.

---

## 2. WH-native design: the Meld Graph

### 2.1 Foundation Law compliance

Tekken throws are the base: fixed, frame-data-driven, input-matched (King's chain
throws, etc.). **Melding is the extension layer on top** — it never replaces a
Tekken throw, it offers *exits* from one throw into another at defined windows.
A WH grapple move = Tekken throw data + WH meld metadata (phases, grips, windows).

### 2.2 Data structures

```js
GrappleMove = {
  id: 'hurricanrana', name: 'Hurricanrana',
  archetype: 'lucha',                 // for AI flavor + creation-suite filters
  roles: { attacker: 'standing', victim: 'standing' },  // entry requirements
  phases: ['entry','contact','payload','release'],
  // grip vocabulary per phase, per participant — THE compatibility contract:
  grips: {
    entry:   { attacker: ['leg-hook'],      victim: ['none'] },
    contact: { attacker: ['leg-hook','head'], victim: ['shoulders'] },
    payload: { attacker: ['leg-hook'],      victim: ['inverted'] },
    release: { attacker: ['none'],          victim: ['prone'] },
  },
  meldWindows: [                       // exits out of THIS move
    { at: 'payload', into: ['piledriver','powerbomb'], kind: 'chain' },
    { at: 'contact', into: ['ace-crusher'], kind: 'counter', counterBy: 'victim' },
  ],
  duration: 1.4,        // seconds, Tekken frame data stays authoritative in-game
  damage: 22,
  endState: { attacker: 'standing', victim: 'prone' },
}

MeldEdge = {
  from: 'hurricanrana', fromPhase: 'payload',
  to: 'piledriver', kind: 'chain' | 'counter' | 'assist',
  gripMap: { attacker: 'leg-hook->waistlock', victim: 'inverted->inverted' },
  blendCost: 0.35,      // 0..1 — pose distance + timing strictness
  hybrid: 'hurricane-driver',  // generated or authored id (see 2.4)
}

Hybrid = {
  id: 'hurricane-driver', name: 'Hurricane Driver',
  from: 'hurricanrana', to: 'piledriver',
  phases: [...from.phases up to fromPhase, ...to.phases after entry],
  duration, damage: from.dmg*0.4 + to.dmg,   // the setup is "paid for"
  roles, endState, counterOf: null | edgeId,
}
```

**Grip vocabulary** (closed set, data — extend freely):
`none, wrist, headlock, waistlock, leg-hook, shoulders, inverted, carry-shoulder,
front-facelock, back-control, ground-mount, ground-side, ground-back, prone, seated`

### 2.3 Blending logic — `findMelds` / `meld`

At a phase boundary the engine evaluates, in order:

1. **Window check** — does the active move declare an exit at this phase?
2. **Grip continuity** — asymmetric gate. The *victim's* body must be continuous
   (hard gate: they can't teleport — every victim grip held at the end of the
   from-phase must be satisfiable by the to-move's entry victim grips). The
   *attacker* is allowed to re-grip mid-flow — that re-grip IS the skill of the
   transition — and novel grips add soft blend cost. This is Dickie's puzzle,
   formalized: no legal body path → no meld.
3. **State check** — both fighters' states match the to-move's `roles` entry
   requirements (standing/grounded/etc.), range within clinch tolerance.
4. **Rank by blendCost** — lower cost = smoother body path. The AI weighs cost
   against personality (`meldBias`: technicians chain more, brawlers less) and
   meter context; the *player* gets deliberate melds via the lying-grapple input
   (mirrors MDickey: a control surface for doing it on purpose, not just AI spice).
5. **Cover the transition** — WH's `SharpTransition` equivalent: both fighters are
   posed to the hybrid's shared entry pose over a short fixed window (4–8 frames)
   with root motion committed, exactly like Dickie's agreed-pose snap. No
   crossfade — fighting games can't afford the ambiguity.

**Counters:** a counter edge flips the roles — the victim of the active move becomes
the attacker of the hybrid. Evaluated when `ReversalBrain` fires during an open
window (`lockMove` set): `findCounters(moveId, phase)` returns victim-authored
hybrids. This makes "every new move adds a new counter" literally true in the data:
adding a move = adding its row + its counter edges.

### 2.4 Hybrids are data, and they compose

`meld(from, to)` generates the hybrid descriptor on demand; named hybrids
(`hurricane-driver`) are cached in the graph and can themselves be melded *from* —
chains of 3+ moves fall out naturally (hurricanrana → piledriver → rear-naked-choke).
This is the MDickey "web of infinite possibilities", bounded by grip continuity so
it never produces impossible bodies.

### 2.5 Integration with `game/js/ai/grapple-chains.js`

The Yuka state machine stays **advisory** (it returns intents; `AIController` owns
execution). Changes are surgical:

- New intent `GRAPPLE_INTENTS.CHAIN_MELD = 'chain-meld'`.
- `GrappleChain.attachMeldEngine(engine)` — optional; no engine = today's behavior,
  bit for bit.
- In `THROW` state: the snap may carry `throwMove` (move id) and `throwProgress`
  (0..1). The chain maps progress → phase (`entry <0.25 < contact <0.5 < payload
  <0.75 < release`). At each phase *entry*, it calls
  `engine.findMelds(throwMove, phase, ctx)`; if a candidate passes the AI's
  `meldBias` roll, it sets `intent = 'chain-meld'` and `chain.meld = { from, to,
  hybrid, kind }` for the controller to execute.
- The victim's counter path hooks into `reversal-logic.js`'s `lockMove` snapshot:
  when a reversal fires inside an open counter window, the controller asks the
  engine for `findCounters` and plays the role-reversed hybrid. (Hook documented;
  reversal-logic itself untouched in this pass.)
- KESSHOU tie-in: grappler archetypes' chain-throw KESSHOU (King-style: chain every
  grapple together, full chain = KESSHOU) are authored as meld graphs. The Nine-Soul
  meter-full + victim <25% HP gate is checked by the controller before it honors a
  `chain-meld` intent that would complete a KESSHOU chain. The meld system is the
  mechanism; KESSHOU is the prize.

### 2.6 What's prototype vs. what's future

**This pass (prototype, in-repo):** data structures, grip vocabulary, meld graph,
`findMelds`/`findCounters`/`meld`, chain integration (advisory intent), deterministic
node tests. **Future:** two-fighter transition posing in the anim system (the
`SharpTransition` equivalent over real rigs), player-facing deliberate-meld inputs
(lying grapples), creation-suite UI for authoring meld edges, assist melds
(double-team: two attackers, one victim — the 2007 precedent).

---

## 3. Sources

- https://estate.w1wrestling.com/mdickie-builds-wrestling-video-game-empire/ (Wrestling Estate interview — move melding, hurricanrana-to-piledriver, "with every new move... a new counter and a new hybrid")
- https://www.oldschoolgamermagazine.com/old-school-gamer-magazine-exclusive-mat-dickie-talks-wrestling-empire/ (OSG interview — "any move can blend into any other at any moment", lying grapples)
- http://mdickie.com/code_wm2008_moves.htm (dev blog — SharpTransition, exact end-frame timing, Moves table as data)
- http://www.mdickie.com/prev_wm2008ce_beta.htm (dev blog — double-team moves keyed off position combinations)
- WH: `game/js/ai/grapple-chains.js` (Yuka grapple state machine), `game/js/ai/reversal-logic.js` (counter hook), `game/js/ai/move-melding.js` (this design, implemented)
