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

## 10. Eastern Mind naming proposals (owner decision needed)

Owner law: finishers are NOT called "fatalities" and nobody dies. The system
needs its own Eastern Mind / Western Heart name — canon-grounded (Nine Souls,
the Trial, Tong-Nou cosmology), short enough for a HUD callout, and
non-lethal by etymology. Four proposals:

1. **KESSHOU (結章) — "the Closing Chapter"** *(recommended)*
   Each fight is a trial chapter in the Nine Souls journey; the finisher
   closes the chapter. The opponent's fighting spirit is *sealed*, not
   destroyed — non-lethal by construction. Short, ownable, works shouted
   by an announcer and printed on a select-screen card.

2. **NINE-SOUL CLIMAX (九魂極, Kyūkon-kyoku) — "Soul Climax"**
   Fires from the Nine-Soul Meter, so the name teaches the resource.
   A *climax* is a peak, not a killing — the meter's ultimate expression.
   Pairs with a UI state callout: meter full → "SOUL CLIMAX READY".
   Recommendation: use this as the *meter-state* name even if Kesshou
   wins as the system name (§11's ready window).

3. **REIHOU (霊放) — "Spirit Release"**
   The non-lethal framing made literal: the fighter releases their spirit
   in one burst; the X-ray beat shows spirit channels flaring with light
   through intact anatomy; the victim is *released* — purified of fighting
   rage — and collapses. Deepest fit with the Buddhist/Hindu purification
   cosmology in the art direction.

4. **TRIAL'S SEAL (試練の封, Shiren no Fū) — "Seal"**
   Canon-grounded in the Trial itself: the finisher seals the bout's
   verdict. The victim's defeat is recorded, not their death. Most
   formal/ceremonial of the four; fits win-pose flow (the seal precedes
   the victor's taunt).

**Proposed pairing (pending owner pick):** system = **KESSHOU**; the
gated window announces **"SOUL CLIMAX READY"**; the KO resolves as a
*seal*/*release*. All four stay clear of MK's "fatality" and of any
death language.

## 11. Tekken-style input scheme (owner directive)

Owner constraint: finishers are **executed Tekken-style — complex inputs
like Tekken super moves (Rage Arts), NOT one-button kills**. MKX fires on
BL+FK+BK and MK11 on R2+L2 — single presses. WH does not copy that.

### 11a. Proposed input

- **Ready window:** Nine-Soul meter full + victim < 25% HP (the existing
  `gatesOpen` conditions). The HUD announces the window
  ("SOUL CLIMAX READY" / fighter-specific flash) — but **the victim is
  not frozen and the timer does not stop**. The flow never breaks, Tekken
  law; unlike MK's "FINISH HIM" daze state, the opponent can still act.
- **Input:** **f, F + LP+RP** — a quick forward dash motion, then both
  punch buttons together. Tekken's Rage Art is 1+2; the added dash makes
  it a deliberate complex input that can't be mashed out by accident.
- **Mobile (MOBILE INPUT LAW):** forward = swipe-forward or double-tap
  forward on the left side; LP+RP = two-finger tap on the right side.
  All targets stay thumb-sized; the input is a gesture + tap, never a
  pixel-precise sequence.
- **Per-fighter customs:** the suite can author a custom input per
  finisher via `getCustomFinisher()` — extend the def format with an
  `input` field (e.g. `input: ['f','F','1+2']`). The synthesized default
  stays f, F + LP+RP for every fighter.

### 11b. Divergence note (implementation status: PROPOSED, not built)

`game/js/finisher.js` as merged (PR #872) **fires the finisher
automatically** when the gates open (§3: "No separate input mode").
That matches Def Jam's beat-bank teardown but **not** this owner
directive. The input scheme above is therefore a proposed additional
layer, not a description of current behavior:

- Add an input listener armed only inside the ready window; outside the
  window, `f, F + LP+RP` falls through to the normal Rage Art / no-op.
- Keep `gatesOpen` as the *arming* condition; the input becomes the
  *trigger*. `tryFinisher` stays the executor.
- Whiff/miss: the input consumes the window (meter drains, window
  closes) — mirroring MK11's whiffed-Fatal-Blow cooldown at Tekken pace.

No code in this PR; the scheme is specified here for the input lane to
build against.

## 12. Non-lethal framing: what happens instead of death

The finisher ends the round with a KO — never a death, never gore. The
in-world framing, consistent with the art direction (psychedelic
Buddhist/Hindu cosmology, Nine Souls, the Trial):

1. **The burst.** The attacker releases their fighting spirit in a single
   Nine-Soul burst — the Kesshou / Soul Climax.
2. **The reveal.** The X-ray beat (§5, `game/js/xray.js`) shows the
   victim's anatomy layers **intact and illuminated**: spirit channels
   (meridian-like light paths) flare through MUSCLE → BONE → ORGAN as
   the blow lands. The spectacle is *illumination*, not destruction —
   MK shows what breaks; WH shows what *surges*.
3. **The seal/release.** The victim's fighting spirit is released and
   sealed — they collapse purified of rage. The KO resolves out of the
   beat; the victor's win taunt plays; **next round they rise again** —
   the Trial continues. (This is also why broken-bone continuity jokes
   from MK reviews can't apply here: nothing was broken.)
4. **No blood, no tearing, no dismemberment.** The `softbody.js` law
   ("no cutting/tearing/destruction") and the anim-gate's render-only
   contract hold for every finisher beat.

## 13. MKX/MK11 technique applied (from MKX-MK11-FINISHERS-2026-10-23.md)

| MK mechanic | WH take |
|---|---|
| MKX: full 3-bar meter, spent on fire | → Nine-Soul meter full gate, meter spent (`finisher.js` gates) |
| MKX: armored startup | → keep: finisher beat carries armor (Tekken-paced, not hyper) |
| MKX: multi-beat camera zoom per hit, "several seconds" | → compress to a **single ~1.9 s beat** (`xray.js` DURATION) — NRS's own lesson via Lebaron: *"we want [these attacks] to be really quick and instant"* |
| MKX: BL+FK+BK one-press super | → rejected; replaced by §11's motion + button input |
| MK11: ≤30% HP gate (wider bar telegraph) | → victim < 25% HP gate (`victimHpGate`); HUD telegraphs the window |
| MK11: one landed Fatal Blow per match; whiff → cooldown | → once per round (round ends at KO); whiffed input drains the window (§11b) |
| MK11: Krushing Blow — conditional X-ray visual, no mode switch | → **the `xray.js` pattern**: hook on R./US.2+3 KO blows, quick beat, fight resumes |
| MK1: X-ray effects back inside the big cinematic | → the X-ray beat lives *inside* the KO blow, not as a separate cinematic |
| MK: "FINISH HIM" daze-state mode switch, 10–20 s cinematics | → rejected; flow never breaks (Tekken law) |
| MK: fatalities — death as the payoff | → rejected; seal/release framing (§12) |

## 14. Integration map (as-built APIs)

- `game/js/finisher.js`: `gatesOpen(game, def)` (arming),
  `tryFinisher(game, def)` (executor), `ensureFinisherMoves(fighterId,
  msApi)` (synthesized per-fighter blow), `getCustomFinisher()`
  (suite-authored override), `FINISHER_NOTATION = 'F.FIN'`.
- `game/js/xray.js`: `XraySystem.onHitKO(attacker, defender, hb)`
  (fires the beat), `xray.update(dt)` (per-frame), `xray.cancel()`
  (round reset); `XRAY.DURATION = 1.9`, `SKIN_OPACITY = 0.25`,
  reveal order MUSCLE → BONE → ORGAN, `CAM_DIST = 1.6`.
- **Docs drift flagged:** §5 of this file specifies an `xrayFlash(opts)`
  contract, but the merged `xray.js` (PR #874) exports the
  class-based `XraySystem` API instead. The finisher lane should target
  the as-built API (or the xray lane should reconcile the doc) — do not
  build new callers against `xrayFlash` until that's resolved.
