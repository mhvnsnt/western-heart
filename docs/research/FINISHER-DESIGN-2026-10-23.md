# FINISHER DESIGN — Tekken-styled fatalities for Western Heart (2026-10-23)

**Status:** design → implemented in this PR (`game/js/finisher.js`).
**Owner instruction (verbatim):** "we're going to do it in like a Tekken style of way but now we're going to have really good anatomy"
**Foundation files:** `game/js/finisher.js` (Def Jam-style gates), `game/js/rage.js` (Tekken Rage Art/Drive synthesis), `game/js/anim-gate.js` (show/fight clip wall), `docs/research/ANATOMY-LAYERS-SPEC-2026-10-23.md` (4 anatomy layers).

---

## 1. How Mortal Kombat fatalities work

- **Separate input mode.** When the announcer says "FINISH HIM/HER", the fight
  stops being a fight: the victim stands dazed, the timer freezes, and the
  player enters a special input sequence (e.g. `← → ↓ ← 4`).
- **Long cinematic payoff.** The finisher is a dedicated authored cinematic —
  often 10–20 seconds — that completely replaces the fight flow.
- **Gore is the point.** Blood, dismemberment, X-ray *breaking bones*
  (MK X's X-Ray moves show ribs cracking, skulls fracturing). The spectacle
  is anatomical *destruction*.

MK's model: **interrupt the flow, change the mode, reward with gore.**

## 2. How Tekken does finishers

Tekken has never had a separate fatality mode. Its two finisher-adjacent
systems both stay *inside* the fight flow:

- **Rage Arts (T7):** quick cinematics (a few seconds) triggered by a normal
  input (`1+2`) while raging. Armor through startup, big damage, knockdown —
  and then **the fight resumes**. The cinematic never leaves the round.
- **Win poses:** character-specific authored animations that play *after* the
  KO, as the victory celebration. They extend the round's end, they don't
  interrupt anything. (This is already a WH law: "Show animations and fight
  moves are separate locked sets… win poses already good — keep those.")

Tekken's model: **the flow never breaks — the finisher is a punctuation mark
on the fight, not a new mode.**

## 3. The Western Heart approach: finishers as victory-flow extension

WH does MK's *desire* (a signature killing moment per fighter) the *Tekken way*:

```
…final exchange → gates open → FINISHER beats → KO → win taunt (always) → next round
```

Concretely:

- **No separate input mode.** The finisher fires automatically from the
  *existing* gates in `finisher.js`: Nine-Soul meter full (resource gate) +
  opponent HP < 25% (victim gate). Same trigger philosophy as the Def Jam
  teardown (`BLAZIN.VIV`): the finisher is an *authored beat bank*, not a
  mode switch.
- **The finisher IS the killing blow.** The beat sequence delivers the final
  damage; the KO resolves out of it. After KO, the flow continues into the
  character's win taunt — unchanged. **Finishers never replace win taunts.**
- **Per-fighter style, synthesized not hand-authored.** Following `rage.js`'s
  proven pattern: the finisher blow is derived from the fighter's *own*
  moveset data — the strongest strike (`_strongestStrike` scan, grabs
  excluded) becomes the finisher blow (`ensureFinisherMoves(fighterId, msApi)`,
  idempotent, mirroring `ensureRageMoves`). Every fighter in the roster gets a
  working, character-true finisher with zero per-fighter authoring. A
  suite-authored finisher (`getCustomFinisher()`) always wins over the
  synthesized one when present.
- **The Tekken X-ray, not the MK X-ray.** On the killing-blow beat, the game
  *reveals* the victim's anatomy layers (BONE/MUSCLE/FAT/SKIN per
  `ANATOMY-LAYERS-SPEC-2026-10-23.md`) as a brief flash, combined with
  soft-body deformation (dent + wobble, per `softbody.js`). **No gore, no
  cutting, no tearing, no blood** — the `softbody.js` header is explicit
  ("no cutting/tearing/destruction — the owner has not asked for gore") and
  this design holds that line. Impact is *visualized*, not inflicted.

## 4. Anim-gate placement: INTRO_OUTRO context

Per the SHOW-ANIMATION LOCK (owner law 2026-10-23): show clips play only in
INTRO_OUTRO / CUTSCENE / SHOW, never in FIGHT. The finisher is part of the
round's *outro*, so:

- `tryFinisher` switches the anim context to `INTRO_OUTRO` for the duration
  of the beats and **restores the previous context when the beats finish**
  (save/restore, so a dropped finisher can never strand the game in the
  wrong context).
- In INTRO_OUTRO the gate's `fight_to_show` allowlist covers the finisher
  beats (authored bank, same contract as throws); any show-pose beat must be
  allowlisted in `crossover.json`'s `show_to_fight` — that file belongs to
  the gate lane and is NOT touched here.

## 5. X-ray interface (contract for the parallel `xray.js` module)

`game/js/xray.js` is being built in parallel. The finisher lane does not
depend on it: the hook is a **fire-and-forget dynamic import with a
try/catch fallback** — if the module isn't there yet, the finisher plays on
without the flash. When it lands, it must export:

```js
// game/js/xray.js — required interface
export function xrayFlash(opts) {
  // opts: {
  //   attacker: Fighter,          // the finisher's owner
  //   victim: Fighter,            // rooted victim
  //   limb: 'armR'|'armL'|'legR'|'legL'|'torso'|'head', // striking limb / target region
  //   power: 0..1,                // scales the reveal + deformation
  //   layers: ['BONE','MUSCLE'],  // which anatomy layers to reveal (subset of the 4)
  //   duration: 0.45,             // seconds of the flash
  // }
  // No gore: reveal is a layer-opacity pulse + soft-body dent, never
  // cutting/tearing/blood. Pure render effect, touches no fight state.
}
```

Call site in `finisher.js`: `_xrayFlash(game, { attacker, victim, limb, power })`
fires once, on the killing-blow beat only. The promise is never awaited by
the beat scheduler — a dropped frame of anatomy never breaks a fight.

## 6. Beat format (unchanged, extended)

The existing def format stands:

```js
{ name, beats: [ { btn, dur, pose, xray?: { limb, power } } ... ],
  meterCost: 1.0, victimHpGate: 0.25 }
```

New optional per-beat field `xray`: marks the beat as the killing blow.
`ensureFinisherMoves` synthesizes a def whose final beat carries
`xray: { limb: <blow limb>, power: <scaled by blow damage> }`.

## 7. Full sequence (derived from the three foundation files)

1. Fight in FIGHT context. `RageSystem`/round setup calls
   `ensureFinisherMoves(fighterId, msApi)` (idempotent — safe every match,
   same injection point as `ensureRageMoves` in `game.js:128-129`).
2. Attacker's Nine-Soul meter hits full while victim < 25% HP →
   `gatesOpen` true → `tryFinisher` fires.
3. Meter spent. Victim rooted (`_finisherLock`, throws contract).
4. Context → INTRO_OUTRO (saved, restored after).
5. Beats play as authored attacks/poses; the `xray` beat fires
   `_xrayFlash` (X-ray layer reveal + soft-body dent on the killing blow).
6. KO resolves. Win taunt plays (existing law — untouched by this PR).
7. Context restores to FIGHT for the next round.

## 8. Constraints (non-negotiable, from standing law)

- **ALL CHARACTERS ARE ADULTS.** Finisher choreography contains no
  content the roster law forbids; no new characters are introduced here.
- **No gore/dismemberment.** Impact = X-ray layer reveal + soft-body
  deformation. `softbody.js` already codifies "no cutting/tearing" — this
  design never asks it to do otherwise.
- **Finishers never replace win taunts.** The taunt still plays after the
  finisher resolves (existing `finisher.js` header law, preserved).
- **SHOW-ANIMATION LOCK respected.** FIGHT context sees zero show clips;
  the finisher's authored content lives in INTRO_OUTRO only.
- **No hand-tooled guessing.** The finisher blow is synthesized from real
  moveset data (`_strongestStrike` pattern); nothing here is authored per
  fighter by hand.

## 9. Test plan

`test/finisher.test.mjs` (new, node-only, no DOM/three.js):
- `gatesOpen`: meter-full + victim<25% opens; anything else closed.
- `ensureFinisherMoves`: strongest-strike blow synthesized, idempotent,
  grabs excluded, falls back cleanly with no moveset.
- `tryFinisher`: beats scheduled, meter spent, victim lock released,
  **X-ray hook never throws when `xray.js` is absent** (the parallel-module
  fallback), context save/restore around the beats.
