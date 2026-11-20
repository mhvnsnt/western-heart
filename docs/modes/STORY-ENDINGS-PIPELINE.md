# Story Endings — per-character cinematics pipeline

## Owner decisions (2026-10-22)

- **Intros and win taunts are OFF LIMITS.** The existing Tekken-style
  intros and win taunts stay exactly as they are — never replaced,
  never re-authored by this system.
- Story endings **layer beside** them: they play AFTER a story or
  arcade run completes, from a WATCH ENDING button on the clear
  screen. New system on top/beside, never over.

## Pipeline

Built on worker 13's cutscene systems:

| Worker 13 system | How endings reuse it |
|---|---|
| `intro-interactions.js` (in-engine pre-fight beats) | same "play in the live arena" contract |
| `transform-cinematic.js` (phase timelines, aura/flash/shockwave fx) | ending shots reuse the fx vocabulary (best-effort) |
| `episodes.js` (per-character story beats, canon-grounded text) | ending text follows the same canon-grounded beat style |

## Files

| File | Role |
|---|---|
| `game/js/story-endings.js` | `STORY_ENDINGS` data (per-character), `getEnding` + fallback, `StoryEndingPlayer` |
| `game/js/modes.js` | `_arcadeClear` / `_storyComplete` gain a WATCH ENDING button; `_playEnding` dynamic-imports the player |

## Data shape

```js
STORY_ENDINGS[charId] = {
  title: 'PANTERA — THE KING EATS LAST',
  shots: [
    { dur: 3.0, cam: 'wide',  text: '…', fx: 'aura' },
    { dur: 3.2, cam: 'close', text: '…', fx: 'none' },
    { dur: 3.8, cam: 'orbit', text: '…', fx: 'shockwave' },
  ],
};
```

- `cam`: `wide` | `close` | `low` | `orbit` — framing of the winning fighter in the live arena.
- `fx`: `aura` | `flash` | `shockwave` | `none` — decorative, fail-safe.
- Shots render as letterboxed title + text cards over the arena; SKIP dismisses.

## Canon law

Ending text uses only CANON.md vocabulary (the Trial, the Nine
Souls, purification, Tong-Nou). No invented backstory. Characters
without a bespoke ending get `FALLBACK_ENDING` — the Trial's
purification arc in generic-but-true terms, never a placeholder.

## Current coverage

Bespoke endings: pantera, demonio, docfrank, phantom, diablo, skull,
and the Nine Souls (rin, byou, tou, sha, kai, retsu, zen, gyou).
Everyone else: canon-safe fallback. Adding a bespoke ending = one
entry in `STORY_ENDINGS` (title + 2–4 shots).
