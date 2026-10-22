# WESTERN HEART — Cutscene System Spec

Owner directive (2026-10-22): *"real-time rendered cutscenes with
characters animated in-engine (not pre-rendered video)."*

Status: **SPEC ONLY** (Track 3) — not implemented. Dorowani will appear
with his voice when cutscenes land. This doc is the build contract for
the future cutscene lane.

## 1. Non-negotiable principles

1. **Real-time, in-engine.** Cutscenes render live in the Three.js scene
   with the actual fighter rigs and animation banks. No pre-rendered
   video files. Ever.
2. **Skippable.** Every cutscene: tap/SKIP ends it instantly and lands in
   a clean game state (fighters posed, HUD ready).
3. **Data-driven.** A cutscene is a JSON/JS timeline, not code. Writers
   (and the owner) author beats; the engine plays them.
4. **Reuses existing systems.** Voice pipeline (`game/js/voice.js`),
   intro-interaction presentation patterns, T3 animation banks, arena
   scenes. No parallel cinematic stack.

## 2. Timeline model

```js
// game/data/cutscenes/<id>.js  (JS module, like episodes.js)
export const CUTSCENE = {
  id: 'dorowani-meets-swamp',
  beats: [
    { at: 0.0, cam: { pos: [4, 2, 6], look: 'dorowani' },
      anim: { fighter: 'dorowani', clip: 'idle' } },
    { at: 0.5, voice: { fighter: 'dorowani', clip: 'intro-01', text: 'Konnichiwa!' } },
    { at: 2.8, cam: { pos: [-3, 1.5, 5], look: 'pantera' } },
    { at: 3.0, voice: { fighter: 'pantera', clip: 'intro-01', text: '...It talks.' } },
    { at: 5.5, anim: { fighter: 'dorowani', clip: 'win' } },
    { at: 5.5, voice: { fighter: 'dorowani', clip: 'win-01', text: 'Bankai!' } },
  ],
  onSkip: 'fight',   // where SKIP lands: 'fight' | 'menu' | <cutscene id>
};
```

Beat types (v1):

| Beat | What it does |
|------|--------------|
| `cam` | Camera director: position + look-target, eased over the beat gap. Targets: fighter ids, arena marks, fixed points. |
| `anim` | Play a T3 bank clip (or procedural fallback) on a fighter, once or looped. |
| `voice` | `voice.playCue({ fighter, clip, text })` — subtitle + recording (placeholder-safe). |
| `sfx` | One-shot procedural SFX via `audio` (impacts, stingers). |
| `banner` | Full-screen title text (episode-style). |
| `wait` | Explicit pause; mostly unnecessary (beats schedule by `at`). |

## 3. Camera director (to build)

- Keyframed `pos` + `look`, smoothstep-eased between beats.
- Never clips through fighters: keep a min-distance guard vs. fighter
  root positions (cheap sphere test per frame).
- Cutscene camera is a separate rig from the fight camera; on cutscene
  end/skip, the fight camera resumes its normal framing — no pops
  (blend 0.25 s).

## 4. Relationship to shipped systems

- **Voice**: `voice.playCue()` already exists in `game/js/voice.js` as
  the cutscene hook — the timeline calls it; placeholder behavior
  (subtitle-only) is identical to intro/win lines.
- **Intro interactions** are the minimal cutscene: 2–4 dialogue beats,
  static camera, in-arena. The cutscene system generalizes them
  (camera + animation + SFX beats).
- **Episodes** (`game/js/episodes.js` + `playStoryBeats`) own the
  tap-through story-card UI. Cutscenes may embed episode beats as
  `banner`/`voice` beats, or hand off to `playStoryBeats` between
  cinematic segments.

## 5. Dorowani (pilot character)

- His voice manifest (`game/data/voices/dorowani.json`) already defines
  `trigger: "cutscene"`-eligible clips; cutscene authors reference them
  by clip id (`intro-01`, `win-01`, `taunt-02`, ...).
- Voice direction for cutscene sessions is the same brief:
  Squirtle-style creature vocalizations + Japanese word bursts, no
  sentences ("Konnichiwa arigato Ichiban Bankai").

## 6. Performance budget (Tekken discipline)

- Cutscenes must not load anything the fight doesn't already have:
  same fighter GLBs, same anim banks, same arena. Voice clips stream
  per-beat (decode is ~ms for <500 KB files).
- First-frame deadline: cutscene starts on already-loaded assets only.
  No mid-cutscene fetches except voice clips (placeholder-safe).

## 7. Build order (for the future lane)

1. `game/js/cutscene.js` — timeline player (clock, beat dispatch, skip).
2. Camera director (keyframed pos/look + fighter-avoidance guard).
3. `game/data/cutscenes/` — first cutscene: Dorowani's intro
   ("swamp" — owner to approve the script; see canon gaps in
   docs/INTRO-INTERACTION-SYSTEM.md §4).
4. Wire into episodes/modes (pre-boss, endings).
5. Proof: screen-recorded playthrough, in-engine, with voice.

## 8. Explicitly out of scope

- Pre-rendered video (owner: no).
- Lip-sync (creature barks don't need it; revisit if sentence-speaking
  fighters get voiced).
- Branching dialogue trees (v1 is linear timelines; choices come later
  if the owner wants them).
