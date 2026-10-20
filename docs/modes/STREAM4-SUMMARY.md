# STREAM 4 — MODES & MENUS (2026-10-19)

Owner directive: "all the arenas all the menus get it all working all the modes everything."
Plus: "The Heart and Mind Inside" (Devil Within-style, owner-locked name),
full story mode (Character Episodes), visual proof at every stage.

## Shipped this PR

### Menus & chrome (`game/js/menus.js`, `game/menus.css`)
- **Pause menu** — HUD pause button (touch, ≥44px) → PAUSED overlay:
  RESUME / OPTIONS / QUIT TO MENU. Wired to `game.pause()`.
- **Options/settings** — master / music / SFX volume sliders, mute-all,
  graphics quality (LOW/MED/HIGH → pixel-ratio + shadow toggle, real effect),
  control-hints toggle. Persisted to `localStorage` (`wh_settings_v1`),
  applied on audio unlock.
- **Loading screen** — branded overlay with progress bar, status text, and
  rotating tips. Shown on fight confirm (all modes), hidden at `startMatch`.
- **VS screen** — fighter portraits + names + titles, VS burst, stage name,
  mode label. Hooked into `Game.startMatch` (covers every mode); breathes
  over the ROUND 1 intro, then fades.
- **Records/rankings** — localStorage records (survival, time attack, qombat,
  episodes) rendered as the shrine-stone leaderboard.
- **Story dialogue UI** — `playStoryBeats()`: portrait + name + tap-to-continue
  cards with kicker titles. Shared by Heart/Mind and Episodes.
- **Menu buttons** — THE HEART AND MIND INSIDE, CHARACTER EPISODES, OPTIONS,
  RECORDS injected into the main menu. Mobile-first, all touch.
- **Mode tag** — current mode shown in-HUD during fights.

### The Heart and Mind Inside (`game/js/heartmind.js`)
Devil Within-style action mode, proprietized. 5 inner stages on canon Eastern
Mind lands; echo waves with HP carry + soul-ember restores; stage wardens;
final boss = your SHADOW SELF. Per-character storylines: entry cutscene,
mid-descent beats tied to each fighter's CANON.md "Being purified of",
shadow confrontation, resolution. Deep canon for demonio, docfrank, mariposa,
thor, and all nine souls; generic frame for the rest. `HM_TEARDOWN` seam
ready for the T5 teardown (clone 1:1 → proprietize).
Design: `docs/modes/HEART-AND-MIND-INSIDE.md`.

### Character Episodes (`game/js/episodes.js`)
Full story mode: every fighter's own storyline from CANON.md (what they want,
who they fight, what they're purified of). Chapters of beats + fights
climbing their own ladder to the shrine — where they all face themselves
(shadow-self final). Deep episodes for demonio/docfrank/mariposa/thor/nine
souls; generic frame for the rest.

### Critical fix (this PR)
`game/js/roster-full.js` had a brace bug in the demonio entry (the `forms:`
block closed the entry early, leaving `stats:`/`ai:` dangling) — the roster
module failed to parse and **the entire game did not boot** on origin/main.
One-line fix; 45 fighters import cleanly.

### Research
`docs/modes/TEKKEN-MODES-RESEARCH.md` §4 updated: Devil Within now WIRED.

## Wiring
`main.js`: `import { initMenus } from './menus.js'` + one `initMenus({...})`
call. `index.html`: one `<link>` for `menus.css`. Everything else is new
files — additive only.

## Visual proof
`docs/modes/shots/` — menu, options, records, VS, story card, loading,
pause, heartmind select, episodes select. Rig: `docs/modes/shoot-screenshots.py`.

## What's stubbed / next
- Phase-2 multi-enemy density for Heart/Mind (waits on T5 teardown via
  `HM_TEARDOWN` — documented, not stubbed).
- Attire picker UI, character-select polish (on lane f0b4561d's PR #328),
  in-game customization menus (coordinate lane 4808ea28) — next PRs.
