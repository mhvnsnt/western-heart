# THE HEART AND MIND INSIDE — Design Doc

**Owner-locked name (2026-10-19):** "The Heart and Mind Inside".
NOT "Western Heart Eastern Mind mode" — that describes the full game.

## What it is

Tekken 5's **Devil Within** skeleton, proprietized: the structure is Tekken's,
the flesh is Western Heart. A third-person action descent — pick ANY fighter,
each with their OWN storyline framed as a personal journey down into their
own heart and mind. The trial turned inward.

## Devil Within structure (researched, to be cloned 1:1 when teardown lands)

From Tekkenpedia / Gamespot (T5 bonus preview):

- **5 stages**, each unlocked by defeating the stage boss.
- Navigate the stage, fight **enemies in groups**, minor key quests / door
  puzzles to progress.
- **Limited button system**: Block, Jump, Punch, Kick — but the character's
  real special moves still work.
- **Devil Gene meter**: full meter → transform into Devil Jin — far more
  powerful, laser attacks, but it **consumes health**. Risk/reward transform.
- Stage themes escalate: industrial → industrial → tomb ruins → alien/mystical
  → alien/mystical at higher complexity.
- Bosses: Modified Gun Jack, Clone Heihachi, True Ogre, Soul Sphere,
  Monstrous Ogre.

## Our proprietized mapping

| Devil Within | The Heart and Mind Inside |
|---|---|
| 5 stages | 5 inner stages: THE THRESHOLD → THE GALLERY OF MASKS → THE DROWNING ROOM → THE FURNACE → THE STILL POINT |
| Industrial/tomb/alien arenas | Canon Eastern Mind lands: Tong-Nou, Phantom Marketplace, Palace of Dreaming, Plains of Chi-U, Octagonal Shrine |
| Jin only | **ANY fighter** — each with their own storyline |
| Jack/G-Corp enemies | **Echoes** — roster fighters as inner demons (dark tint, real movesets) |
| 5 bosses | Stage wardens (themed echoes) → final boss: **your SHADOW SELF** (your model, your moveset, darkened, buffed) |
| Devil Gene meter → Devil Jin | **Soul Surge meter** → channel the nine souls against the dark inside (already in the engine) |
| Health pickups | **Soul embers**: HP restore between waves (+30–35%) |
| Jin's story (find mother) | Per-character descent: entry cutscene → mid-stage beats tied to their CANON.md **"Being purified of"** → shadow confrontation → resolution |

## Story system

`game/js/heartmind.js` — `HEARTMIND_STORIES[fighterId]`:

- **entry**: 2–3 dialogue beats (cutscene before stage 1)
- **beats**: per-stage mid-descent lines keyed by stage (`masks`, `drowning`, `furnace`)
- **bossLines**: pre-shadow-self confrontation
- **resolution**: purification payoff

Deep canon (grounded in CANON.md verbatim where possible):

- **DEMONIO** — purified of *the apology*: the guilt he can't name. "He bows to every opponent. He has never once bowed to Diablo."
- **DOC FRANK** — purified of *the god complex*: "the difference between making a thing and being the thing."
- **MARIPOSA** — purified of *the post*: "raised to be a lock, not a person… cocoons are for changing."
- **THOR** — "He doesn't know he's being purified. That's the point."
- **The nine souls** (rin/byou/tou/sha/kai/jin/retsu/zen/gyou) — compact arcs from their canon natures.

Everyone else: `genericStory(char)` builds a real personal arc from their
roster identity (name/title/style) — the framework lets the rest plug in;
no placeholders, every button works.

## Combat model

**Phase 1 (shipped):** sequential inner battles — each wave is a single-round
fight vs an echo with HP carry-over (`opts.hpCarry`, already honored by
`Game.startMatch`) + soul-ember restores. Stage = 3 echoes + warden; stage 5
= shadow self only. Real, playable, wired end-to-end.

**Phase 2 (when T5 teardown lands):** simultaneous multi-enemy density via the
`HM_TEARDOWN` seam — `enemyAi`, `waveTables`, `doorSystems` consumed 1:1.
The story system and proprietary layer do not change.

## Teardown integration (NO-DEFERRAL — T5 teardown top priority)

The teardown stream is acquiring Tekken 5 now. When Devil Within's exact
mechanics land (enemy AI patterns, wave composition tables, door/platforming
systems), they go into `HM_TEARDOWN` in `game/js/heartmind.js` and the wave /
boss builders consume them 1:1 — clone then proprietize, per the owner spec.

## Records

- `heartmind_<fighterId>` → furthest stage reached
- `heartmind_<fighterId>_clear` → completions
- Surfaced in the Records screen (`#wh-rec-extra`).

## Files

- `game/js/heartmind.js` — stages, echoes, shadow self, story system, controller
- `game/js/menus.js` — `playStoryBeats` dialogue UI, mode buttons, select routing
- `game/menus.css` — story card styles
- `docs/modes/shots/` — visual proof

## Shrine体系 at the Still Point (2026-10-24)

Owner-directed 2026-10-24: the shrine terminal appears in the
Heart and Mind Within at stage 5 (the Still Point,
octagonal-shrine). Before the shadow-self fight, the terminal
reads the descending soul — two beat lines, played for every
fighter through `HeartmindController._runStage()` (the
stillpoint branch), via `SHRINE_OS_SEGMENT` and `shrineOsBeat()`
in `game/js/heartmind.js`. The same terminal is playable on its
own in the side games (see the Shrine体系 prototype in
`game/side-games.html`, engine in `game/js/shrine-os.js`).
Canon: the Shrine体系 section of `CANON.md`.
