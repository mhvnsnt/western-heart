# WESTERN HEART — Intro Interaction System

Owner directive (2026-10-22): *"Tekken-style pre-fight character
interactions when two fighters are picked — but VARIED, not one fixed
interaction per matchup. Multiple different interactions per character
pairing, different interactions per character. Builds backstory and canon."*

## 1. What it is

When two fighters are selected and the match loads, they exchange a short
scripted interaction **in the arena, in-engine, in real time** — both
fighters live in the 3D scene, idling, while dialogue (+ voice, when
recorded) plays over them. Then ROUND 1 begins. This is Tekken's versus
intro, but with the owner's key twist: **no fixed script per pairing**.

## 2. Architecture

```
game/js/intro-interactions.js   DB + selection + presentation
game/js/game.js                 startMatch() hook (before round 1)
game/js/voice.js                per-beat voice lines (voice.playLine)
docs/INTRO-INTERACTION-SYSTEM.md  this contract
```

### 2.1 The database

`INTRO_INTERACTIONS` — keyed by fighter pair, ids **sorted** and joined with
`|` (`'demonio|diablo'`). Every pair holds an **array of variants** (2+
required — the variety requirement is enforced by test-intro.mjs).

Variant shape:

```js
{ id: 'dem-dia-1',
  tags: ['rivalry'],              // selection hints: rivalry, respect, family...
  source: 'episodes.js: "..."',   // canon provenance for EVERY variant
  beats: [
    { speaker: 'demonio', line: 'I bow to every soul in this trial.' },
    { speaker: 'diablo', line: 'Then bow, little saint.' },
    { speaker: 'demonio', line: 'Not to you.', voice: 'win-01' },
    //                    voice ^ optional voice-manifest clip id
  ] }
```

`GENERIC_INTROS` — per-fighter **solo** beats (one speaker only), used when
the pair has no scripted exchange. Solo so we never put words in an
arbitrary foe's mouth. Dorowani ships 3.

Fallback chain: pair variants → fighter-generic → **versus title card**
(names + ⚔, no invented words). The fallback never invents dialogue.

### 2.2 Selection (`pickIntroInteraction`)

Pure logic, no DOM — unit-tested (`game/js/test-intro.mjs`):

- Key = sorted pair ids. Random variant per play.
- **No immediate repeats**: the last-played variant id per pair is
  remembered; the pool excludes it (when 2+ variants exist).
- **Context-aware**: `ctx.rivalry` weights `rivalry`-tagged variants;
  `ctx.storyState` is reserved for future story flags (episode progress,
  win streaks, rematch detection).
- Returns `{ kind: 'pair'|'generic'|'versus', variant }`.

### 2.3 Presentation (`playIntroInteraction`)

- Builds its own `#wh-intro` overlay (same pattern as menus.js
  `buildOverlays` + `#wh-story`); styles injected by the module so no CSS
  file edit was needed.
- Each beat: speaker name + line shown, `voice.playLine(speaker, clip,
  line)` awaited — real recording plays when it exists, subtitle-only
  placeholder until then (see docs/VOICE-PIPELINE.md §5).
- **Skippable**: tap advances the beat, SKIP ▸▸ ends the interaction.
  Beats race voice completion vs. tap so pacing stays snappy.
- The fighters idle-animate behind the dialogue (game.js pumps their
  `update()` on a timer for the beat's duration — their update loop only
  runs during rounds otherwise). Guarded try/catch: animation can never
  break the intro.
- Resolves `{ kind, variant, skipped }`. Total added match time: ~3–7 s,
  skippable to ~0.

### 2.4 Wiring (game.js)

`startMatch()`: after fighters spawn, before `_startRound()` —

```js
if (!opts.skipIntroInteraction) {
  const { playIntroInteraction } = await import('./intro-interactions.js');
  ...
  await playIntroInteraction(this, playerChar, enemyChar);
}
```

- Dynamic `import()` keeps the module off the menu boot path
  (loadspeed lane: intro-interactions.js is fight-only).
- Modes opt out with `opts.skipIntroInteraction` (survival gauntlet,
  training resets, etc.).
- Failure policy: any exception → `console.warn`, match continues.
  The intro can never block a fight.

## 3. Seed content (shipped)

| Pair | Variants | Canon grounding |
|------|----------|-----------------|
| dorowani｜pantera | 2 | owner voice canon |
| demonio｜dorowani | 2 | owner voice canon + demonio discipline |
| dorowani｜skull | 2 | owner voice canon + skull "targets" |
| demonio｜diablo | 2 | episodes.js rivalry ("never bowed to Diablo") |
| demonio｜pantera | 2 | episodes.js ("only soul he respects") |
| cyborgx｜docfrank | 2 | episodes.js (daughter / peer review) |
| docfrank｜samura1 | 2 | episodes.js ("what do you fight for" / "data") |
| diablo｜mariposa-monarch | 2 | episodes.js (crowbar / locksmith) |
| dorowani generic | 3 | owner voice canon |

## 4. Canon policy (owner rule)

**Never invent backstory that contradicts CANON.md/docs.** Every variant
carries a `source` field citing its provenance. Lines that are
archetype-consistent but not quoted canon are marked
`[NEEDS-OWNER-REVIEW]` in their source string. Current review flags:

- `dem-pan-2` — Pantera's lines ("Then ask." / "Fight like it.") are
  terse-grappler archetype, not quoted canon. Pantera has no established
  dialogue; the owner should approve or replace.
- `doc-cyb-2` — Doc Frank/Cyborg X banter beyond the quoted beats.
- `dia-mar-2` — Mariposa/Diablo second exchange.

**Gaps flagged for the owner (not guessed):** Dorowani has no canon
beyond the 2026-10-22 voice brief (swamp, trickster, Japanese bursts) —
his intro lines stay inside that brief. Full backstory (why he was
summoned, swamp lore, ladder: Dorowani → Numidoro → Gabu → Wanizame)
needs the owner's canon pass before deeper exchanges are written.

## 5. Expanding the database

1. Add variants to an existing pair, or a new sorted `a|b` key.
2. Give every variant a `source` (canon quote or NEEDS-OWNER-REVIEW).
3. Add `voice` clip refs where manifests exist.
4. Run `node game/js/test-intro.mjs` — variety + ref integrity enforced.

## 6. Proof / verification

- `node --check game/js/intro-interactions.js`
- `node game/tests/intro-interactions.test.mjs` — 140 assertions: pair keys sorted,
  2+ variants per pair, beat shape, selection rotation, no-repeat,
  generic/versus fallbacks, rivalry weighting, voice-ref integrity.
- `node game/tests/intro-play.test.mjs` — full presentation flow with
  stubbed DOM: beat order, voice call args, skip, rotation.
- In-engine: start any versus match → intro plays before ROUND 1;
  console shows `[WH voice]` trigger lines; Dorowani's voice refs fire
  his manifest clips (subtitle-only until recordings land).
