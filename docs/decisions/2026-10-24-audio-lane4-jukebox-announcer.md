# Lane 4 audio — Jukebox eras + announcer events + pending rule (2026-10-24)

## What this PR is

Gap-fill on top of merged PR #1030 (Nosferatu rotation, merged
8579c6df) and alongside open PR #1046 (Jukebox pools + streaming).
It deliberately does NOT duplicate #1030, #1046, #1028 (Pantera
voice rewire, merged), or #1049 (Pantera triggers). What it adds is
the set of Lane 4 items those PRs left open or got wrong.

## Audit (verified 2026-10-24 from main + open PR branches)

- Jukebox: main's `game/js/music.js` already does stage/mode rotation
  pools, final-round swap, and `playSequence` (from #1030). PR #1046
  adds a Settings pool switch (`game/js/jukebox.js` +
  `game/data/jukebox-pools.json`: default / cape-jones / nosferatu
  pools, battle only). What was MISSING: browse by era/collection
  (T7's Jukebox browses by game; WH browses by collection), and a
  play-across-modes era resolver. This PR adds that layer
  (`game/data/jukebox-eras.json` + `game/js/jukebox-eras.js`).
- Announcer: main has the engine (`game/js/voice.js` announce()) and
  an 11-clip manifest (`game/data/voices/announcer.json`), but every
  clip is subtitle-only placeholder (file null, no audio bytes) and
  NO `voice.announce()` call site was found in `game/js/main.js`,
  `game.js`, `modes.js`, `fighter.js`, `select-screen.js`,
  `episodes.js`, `versus-setup.js`, `stage-intros.js`,
  `combat-core.js`, or `wh-boot.js`. Character-select has NO clip
  at all. This PR adds the event table
  (`game/data/announcer-events.json`) + pure resolver
  (`game/js/announcer-events.js`); the call-site wiring belongs to
  the fight/select lanes (this lane does not touch `fighter.js`,
  menus/HTML, or story files). No stage sounds, music, or SFX are
  presented as dialogue anywhere in this table.
- Pending rule gap (real bug, fixed here): rotation pools already
  excluded fileless tracks, but `pickTrack` (first-match) did NOT
  filter availability — a pending-download slot that was the first
  stage/mode match WOULD be returned, saved only by the procedural
  fallback. `game/js/music.js` now filters every pick through
  `_available`, and `_available` now also excludes
  `status === 'pending-download'` explicitly. Pending-file tracks
  (file field set, bytes not yet in repo) stay pickable and fall
  back procedurally on fetch failure — the game never goes silent.
- Pantera voice: VERIFIED, not redone. PR #1046's
  `pantera_grunt_cued` ranges match Set B (Tekken 2 grunts, 26
  clips) durations from `~/workspace/king-mods/
  pantera-sounds-manifest.md` plus the 0.6 s silence gap after each
  clip (cue 1 [0, 0.801088], cue 2 starts 1.401088, total
  64.209624 s vs ffprobe sampler 64.21 s). The brief allowed split
  OR cue; the cue half is shipped, so NO sampler split is done
  here — splitting still needs confirmation and is flagged, not
  silently done. Owner ear-check: T2 grunts sampler PREFERRED, all
  sets usable; clips are jaguar growls/roars/grunts, NOT words.
- Procedural/Wwise patterns: PR #1046's `game/js/wh-audio.js`
  already wires postEvent to fresh AudioBufferSourceNode, random
  containers with no-repeat, and buses into a master compressor.
  What it did NOT pin down: the RTPC Intensity formula, the
  0.94–1.06 playbackRate jitter bounds, and the compressor numbers
  as tested constants. Those live now in the pure module
  `game/js/audio/rtpc.js` (Intensity = 0.35×comboHeat +
  0.35×healthDeficit + 0.30×roundTimerPressure; states
  Menu/Fight/KO/Pause; buses music/sfx/voice/ui/ambience).
- Story hook: `sequences.ep01-fight` (9 Nosferatu tracks) exists in
  the library and `music.playSequence` exists in the engine, but NO
  caller was found in the audited files (`episodes.js` has no
  playSequence/music reference). The hook is documented below for
  the story lane; this lane does not touch story files.

## Canonical Cape Jones unification (read this before merging #1037 / #1040 / #1046)

Three different Ghost Surf Rock identities existed at once:

- PR #1037 (stale, mergeable=false, based on pre-#1030 main):
  id `cape-jones-ghost-surf-rock`, file
  `assets/music/cape-jones-ghost-surf-rock.mp3` — CANONICAL, and
  the 8 filenames in this PR match it exactly.
- PR #1040: id `ghost-surf-rock`, file null, mode
  `cape-jones-theme` — a DUPLICATE entry. If #1040 merges, the
  library would hold two Ghost Surf Rock entries. Recommendation:
  #1040 drops its library entry (keep its research doc) or is
  closed as superseded by this PR's cape 8.
- PR #1046 pools file: mainTrack id `ghost-surf-rock`, file
  `assets/music/ghost-surf-rock.mp3` — NEITHER matches the
  canonical entry, so the pool's lead slot can never resolve to
  the downloaded file; worse, its cape cycle rest is EVERY
  available library track, not the cape era. Fix in the pools
  file (posted as a coordination comment on #1046): set
  mainTrack.id to `cape-jones-ghost-surf-rock` and mainTrack.file
  to `assets/music/cape-jones-ghost-surf-rock.mp3`, and restrict
  the cycle rest to cape-era tracks (this PR's
  `playableEraQueue` already implements the correct rule, and
  `checkPoolsConsistency` fails on the old values and passes on
  the canonical ones — see the new test).

Merge order: #1046 first (Settings pool switch), then this PR
(era browse + library cape 8 + pending rule + announcer table).
This PR touches no #1046 file, so the 3-way merge should be clean. #1037's library content is superseded by this PR (same 8 tracks, rebased onto post-#1030 main, plus `status: pending-file`).

## Ghost Surf Rock rule (LOCKED, user directive 2026-10-24 19:41 CDT)

Ghost Surf Rock by Loyalty Freak Music, 04:07, CC0 1.0, from
WITCHY BATTY SPOOKY HALLOWEEN IN SEPTEMBER !!, is the Cape Jones
theme song and the MAIN track: first among the 8
`cape-jones-arena` stage-tagged tracks, leading every cape-era
rotation cycle, others interchanging around it. Vibe: surf rock +
spooky + witchy + batty + Halloween — spooky, surf, fun, ghostly,
Halloween-ish. NEVER "A ghost Waltz" as theme (corrected
2026-10-24; Waltz is interchanging only). The Cape Jones arena
does not exist yet; the wiring is forward-looking.

## Files changed

- `game/data/music-library.json` — append 8 Cape Jones tracks
  (exact PR #1037 entries + `status: pending-file`); 44 → 52
  tracks; first 44 entries byte-identical (surgical splice, 168
  lines added, 0 deleted).
- `game/js/music.js` — `_available` excludes
  `status: pending-download`; `pickTrack` filters through
  `_available` (29-line diff, 2 hunks).
- `game/data/jukebox-eras.json` — NEW: 4 eras (wh-originals 14,
  nosferatu 25, cape-jones 8 main-first, tekken-data-only 5
  playable:false).
- `game/js/jukebox-eras.js` — NEW: pure era browse/resolve +
  pools-consistency guard.
- `game/data/announcer-events.json` — NEW: 9 events (8 fight +
  character-select as needs-recording, no invented line).
- `game/js/announcer-events.js` — NEW: pure announcer resolver.
- `game/js/audio/rtpc.js` — NEW: pure RTPC/jitter/no-repeat/
  compressor helpers.
- `game/data/audio-download-manifest.json` — NEW: exact manifests
  for Nosferatu 25 cuts, Cape 8 downloads, Tekken 5 data-only
  slots (no invented URLs).
- `test/jukebox-eras-announcer.test.mjs` — NEW: 49 checks, all
  passing locally (see Proof in PR body).
- `test/music-rotation.test.mjs` — count assertion 44 → 52 only
  (library grew; everything else unchanged, still passing).

## Story-lane hook (delegation, not done here)

In the Ep1 story fight, at fight start, call (exact snippet for
the story lane to place at its fight-start call site):

    await music.playSequence('ep01-fight');

The engine plays the 9 sequence tracks in order, then resumes
battle rotation on the last battle stage (`_playSequenceNext`
already implements the resume). Until the Nosferatu cuts land,
sequence tracks are file-fielded but byte-missing, so the engine
falls back to the procedural loop per track — the sequence still
advances; it just does not play score audio yet.

## Pending list (honest, nothing claimed done)

- 25 Nosferatu MP3 cuts → `game/assets/music/` — pending the
  Kaggle GPU cut job (`tools/music/kaggle-cut-tracks.py`, PR
  #1030). A browser Kaggle run is ALREADY tasked to the
  coordinator — do not start a duplicate; check first. Kaggle
  notebook: https://www.kaggle.com/code/marsfmmg/notebook2ff3176461/edit
  (T4 x2). Manifest ranges are in
  `game/data/audio-download-manifest.json` (from library
  `source.range_sec`, contiguous 0–5067 s).
- 8 Cape Jones MP3s → `game/assets/music/` with the exact
  filenames in the manifest — pending a parent browser
  delegation (Free Music Archive pages; each page is HTML, use
  the page's download control, not the page URL as audio).
- 5 Tekken data-only slots — pending-download, no URL claimed,
  engine skips them. No download delegation is made for these
  until the coordinator confirms a source.
- Announcer audio — no bytes exist; all 11 manifest clips are
  subtitle-only placeholders, character-select needs recording.
  No voice is invented or synth-presented as final.
- Live audio play verification on a phone (menu → JUKEBOX era →
  fight audio, announcer subtitles) — owed after merge + deploy;
  Node tests are NOT playtest.

## Parent browser delegations (with the standing sign-in rule)

1. FMA Cape Jones downloads (8 files, exact filenames in the
   manifest). SIGN-IN RULE (user directive 2026-10-24 20:06 CDT,
   never make the user repeat): if ANY download page presents a
   sign-in, use GitHub sign-in (account mhvnsnt) OR Google /
   Gmail sign-in (fmmg.mars@gmail.com, username marsfmmg, saved
   logins, tap-to-sign-in) ONLY. NEVER ask for an email/password,
   NEVER request a secure-entry password card first. FMA
   downloads normally need no sign-in; if a site genuinely offers
   NO GitHub/Google SSO after a thorough check (login page +
   sign-up flow), report that exact finding — do not silently fall
   back to password entry.
2. Kaggle GPU Nosferatu cut run — already tasked; coordinator to
   confirm status before any new run (same sign-in rule: Google
   fmmg.mars@gmail.com tap-to-sign-in for Kaggle).
3. Live audio playtest on the user's phone after merge + deploy
   (coordinator/deployer lane, not this lane).

## Update: Jukebox engine wiring (PR #1056 contract, commit 2 on PR #1058)

- PR #1056 (UI lane, open) stores one soundtrack choice per UI mode
  in localStorage key `wh_jukebox_v1` (`menu` / `arcade` / `treasure`
  / `versus`), value = track title with id as fallback, or null =
  engine default rotation. `game/js/music.js` now reads that SAME
  key directly (no import of `game/js/ui-gaps.js`, so the engine
  works whether #1056 has landed or not, with no import cycle).
- Resolution: exact id first, then exact title; an id match that is
  pending-download returns null (never plays a different track
  sharing the title). Unresolvable or pending choices fall back to
  existing rotation — never silence, never a break.
- Mapping: `playMenu` title/select/online use the `menu` choice,
  `playMenu` versus uses the `versus` choice, credits/results have
  no owning UI mode and stay on rotation; `playBattle` uses
  `opts.uiMode` when the caller knows it, else arcade choice if
  set, else versus choice. `game/js/main.js` passes the real mode
  through at the fight-start call site (`opts.mode` versus /
  arcade / treasure, else undefined). Treasure has no music call
  site yet, so a stored treasure choice is read but unplayed
  (recorded, not faked). The victory jingle is untouched.
- Tests: 12 new checks in
  `test/jukebox-eras-announcer.test.mjs` (title/id resolution,
  pending fallback, unknown fallback, results isolation, explicit
  arcade/versus, no-mode default order, versus screen, treasure
  fallback) — all passing locally alongside the rotation test.
