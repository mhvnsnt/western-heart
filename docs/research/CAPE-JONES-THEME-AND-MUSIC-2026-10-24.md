# Cape Jones theme + no-copyright music pull + tap-for-audio removal

Owner directive 2026-10-24 19:41 CDT (verbatim intent): Ghost Surf Rock
is Cape Jones's theme song — if he ever gets an arena it is the main
track there, with interchanging tracks rotating around it; remember the
vibe from the album/description; pull other Loyalty Freak + no-copyright
music fitting the Western Heart vibe/canon for the game soundtrack and
background music so the game actually has audio; remove the tap-for-audio
thing and put audio on/off in settings (Tekken doesn't have it, MDickey
Wrestling Empire doesn't have it); use Wrestling Empire to understand
mobile setup; everything needs to be more mobile and user friendly.

## 1. Cape Jones theme song

**Ghost Surf Rock — Loyalty Freak Music — 04:07 — CC0 1.0 Universal.**

- Album: WITCHY, BATTY, SPOOKY, HALLOWEEN IN SEPTEMBER !!
- FMA page: https://freemusicarchive.org/music/Loyalty_Freak_Music/WITCHY_BATTY_SPOOKY_HALLOWEEN_IN_SEPTEMBER_/Ghost_Surf_Rock
- FMA genres: Ambient / Halloween / Holiday / Instrumental.
- Plays/downloads on FMA at check: 26.8K plays, 4.4K downloads.
- Correction history (do NOT repeat the old error): the track was
  originally flagged as "A ghost Waltz" in Ep 1 planning; the owner
  corrected it on 2026-10-24 — the ghost track / theme is Ghost Surf
  Rock, not A ghost Waltz. A ghost Waltz is kept only as an
  interchanging track (same album, same vibe, also CC0).

### Cape Jones vibe — remember this for all future music picks for him

Surf rock + spooky + witchy + batty + Halloween. Spooky, surf, fun,
ghostly, Halloween-ish. The album title itself is the vibe statement:
witchy, batty, spooky, Halloween — but playful, not grim. When picking
music for Cape Jones (arena tracks, character moments, show cues),
match this: surf-guitar energy, spooky atmosphere, fun — never
generic dark/epic, never grim horror.

### Theme wiring

- `game/data/music-library.json`: `cape-jones-ghost-surf-rock` is FIRST
  among the 8 `cape-jones-arena` stage-tagged tracks, so the current
  first-match `pickTrack()` plays it as the main track the moment a
  `cape-jones-arena` stage id exists. Rotation pools treat all 8 as
  the pool, Ghost Surf Rock first.
- The Cape Jones arena does NOT exist yet (owner: "if we ever make him
  an arena"). The wiring is forward-looking and costs nothing until
  then: stage tag + docs + test. Mood tags (`spooky` `surf`
  `halloween` `ghost` `fun`) make the tracks reachable by mood picks
  now.
- No new track carries a `modes` tag, so no existing menu/mode/stage
  pick changes. Verified by `test/cape-theme-music.test.mjs` (56 checks).

## 2. License verification — every track checked per-track on FMA

Do NOT assume the Loyalty Freak catalog is uniformly CC0. Each track
below was verified individually on its FMA page on 2026-10-24 — all 8
are CC0 1.0 Universal. If a future track is not CC0 on its own page,
do not add it without recording its actual license + attribution.

| Track | Duration | Album | License | FMA page |
|---|---|---|---|---|
| Ghost Surf Rock | 04:07 | WITCHY, BATTY, SPOOKY, HALLOWEEN IN SEPTEMBER !! | CC0 1.0 | https://freemusicarchive.org/music/Loyalty_Freak_Music/WITCHY_BATTY_SPOOKY_HALLOWEEN_IN_SEPTEMBER_/Ghost_Surf_Rock |
| A ghost Waltz | 01:36 | same | CC0 1.0 | https://freemusicarchive.org/music/Loyalty_Freak_Music/WITCHY_BATTY_SPOOKY_HALLOWEEN_IN_SEPTEMBER_/A_ghost_Waltz/ |
| Hello Regan ! | 07:07 | same | CC0 1.0 | http://freemusicarchive.org/music/Loyalty_Freak_Music/WITCHY_BATTY_SPOOKY_HALLOWEEN_IN_SEPTEMBER_/Hello_Regan_ |
| A really dark alley | 04:16 | same | CC0 1.0 | https://freemusicarchive.org/music/Loyalty_Freak_Music/WITCHY_BATTY_SPOOKY_HALLOWEEN_IN_SEPTEMBER_/A_really_dark_alley |
| The graveyard | 03:40 | same | CC0 1.0 | https://freemusicarchive.org/index.php/music/Loyalty_Freak_Music/WITCHY_BATTY_SPOOKY_HALLOWEEN_IN_SEPTEMBER_/The_graveyard/ |
| The Old Witch Place | 01:36 | same | CC0 1.0 | https://freemusicarchive.org/music/Loyalty_Freak_Music/WITCHY_BATTY_SPOOKY_HALLOWEEN_IN_SEPTEMBER_/The_Old_Witch_Place/ |
| The Witch Are Going Magical | 02:09 | same | CC0 1.0 | https://freemusicarchive.org/music/Loyalty_Freak_Music/WITCHY_BATTY_SPOOKY_HALLOWEEN_IN_SEPTEMBER_/The_Witch_Are_Going_Magical/ |
| Sweat Time ! | 02:07 | ROLLER DISCO DANCE DANCE (Disco / Rock / Dance / Surf) | CC0 1.0 | https://freemusicarchive.org/music/Loyalty_Freak_Music/ROLLER_DISCO_DANCE_DANCE/Loyalty_Freak_Music_-_ROLLER_DISCO_DANCE_DANCE_-_07_Sweat_Time_/ |

## 3. Download manifest — MP3s still to land (browser task)

The library entries are wired, but the MP3 binaries are NOT in the
repo yet (this lane cannot download binary audio — no live-browser
download, no web fetch via shell). Until they land, the engine falls
back to the procedural loop for these tracks — the game never goes
silent or breaks. Download each track from its FMA page above and
commit to `game/assets/music/` with EXACTLY these filenames (the
library already references them; no code change needed once they land):

- `cape-jones-ghost-surf-rock.mp3`
- `cape-jones-ghost-waltz.mp3`
- `cape-jones-hello-regan.mp3`
- `cape-jones-dark-alley.mp3`
- `cape-jones-graveyard.mp3`
- `cape-jones-old-witch-place.mp3`
- `cape-jones-witch-magical.mp3`
- `cape-jones-sweat-time.mp3`

Why no `remote` URL on these tracks: FMA page URLs are HTML pages,
not audio files — the engine would waste a fetch trying to decode
one. The page URL lives in each track's `source` field for provenance.
If a direct MP3 URL is ever verified for a track, it can be added as
`remote` later with no other change.

## 4. Tap-for-audio removal — what changed and why it is safe

Removed (user: "it's kind of dumb"):
- `TAP TO ENABLE SOUND` overlay div from `game/index.html`.
- Its show-on-load timer from `game/js/main.js` (600 ms after load).
- Its CSS from `game/styles.css` (`.tap-hint` rules + its duplicate
  `@keyframes pulse`; the select-timer's own pulse definition remains
  and still covers `.select-timer.low` / `.throw-prompt`).

Kept (browser autoplay policy still requires a user gesture):
- The silent first-interaction unlock: `pointerdown` once listener +
  `unlockAudio()` calls in menu taps and `startFight()`. No overlay,
  no dedicated step — the first real tap (any menu item, any button)
  unlocks audio invisibly. This is what Tekken and Wrestling Empire
  effectively do: you press a button, sound works.

Added (user: audio on/off in settings):
- OPTIONS now shows a `SOUND` toggle (ON = sound plays) instead of
  the confusing `MUTE ALL` toggle (ON = muted). Same persisted
  `muted` key in `wh_settings_v1`, same `applySettings()`, default ON
  (`muted: false`). Implemented as `toggleRowInv()` in
  `game/js/menus.js` — the row displays inverted relative to the
  stored key, so existing saved settings keep working and the label
  reads the way the user asked: sound on/off.

## 5. MDickey Wrestling Empire — mobile reference (verified points)

Studied from MDickie's own controls page and instruction manual
(v1.7.8 / v1.7.2 / v1.2.6), not by playing the game (this lane has no
live-browser play). Verified points applied to Western Heart:

- Mobile controls are virtual joystick (left side) + virtual buttons
  (A Attack, G Grapple, R Run, P Pick-Up/Drop, T Taunt/Pin, EYE focus,
  HEALTH METER switch character, CLOCK pause/camera). WH already
  mirrors this shape (joystick + LP1/RP2/LK3/RK4 buttons) — no change
  needed here, and this PR does not touch fight controls.
- Menus: "Any device with touch-screen or a mouse can instantly
  access any option, pressing either side to change its value."
  Applied: WH OPTIONS rows are tap-to-change (sliders, segments,
  toggles) with no separate confirm step — the SOUND toggle follows
  this exactly (tap the row, it flips, it saves).
- Touch disambiguation matters: v1.7.7 fixed "touching virtual buttons
  after swiping the middle of the screen no longer confuses the
  camera." WH's existing tap helper (12px scroll-drag guard, 600ms
  dedup, PR #1018) is the same class of fix — kept, not changed here.
- Lists: "Long lists scroll to the correct place at any resolution."
  WH menu rail scroll fix (PR #1018) is the same class — kept.
- No tap-for-audio gate exists anywhere in the Wrestling Empire
  manual or controls pages. Audio just works; sound settings live in
  options. This PR matches that exactly.
- Performance note: Wrestling Empire is praised for fast performance
  on mobile at a 208 MB app size. WH's asset-pipeline work (gltfpack
  −54% to −65% on real files, studio-workflow lane) is the parallel
  effort — not in this PR.

## 6. Mobile + user-friendly — what this PR fixes, what remains

Fixed here (user-impact order):
1. Tap-for-audio gate gone — the single biggest mobile friction the
   user named. Game starts, first tap unlocks audio invisibly.
2. SOUND on/off in OPTIONS, plainly labeled, default ON, persisted.
3. Soundtrack expanded 14 → 22 tracks (before Nosferatu 25 from
   PR #1030) — the game actually has audio beyond the procedural loop
   once MP3s land.

Not in this PR (follow-ups, not hidden):
- Live playtest on the user's phone (menu → OPTIONS → SOUND toggle →
  fight audio) — owed after merge + deploy, like every fix.
- MP3 downloads + commit (browser task, §3).
- Cape Jones arena itself (does not exist yet; theme wiring is ready).
- Full mobile friction audit beyond audio (tap targets already under
  the 44px law; a dedicated audit pass is a separate lane).

## 7. Honest gaps (not claimed done)

- The 8 MP3s are not in the repo yet (§3) — library entries + code
  are done, audio files are a browser download away.
- Wrestling Empire was studied from docs/manuals, not played live.
- PR #1030 (Nosferatu 25 tracks + rotation pools) is a separate open
  PR; this PR's stage-tagged tracks are designed to work with both
  the current first-match engine and #1030's pools, but the two PRs
  touch the same library file and the merge order needs care (this
  PR appends tracks at the end of the array; #1030 adds its own
  block — a 3-way merge should reconcile, or rebase if it conflicts).
