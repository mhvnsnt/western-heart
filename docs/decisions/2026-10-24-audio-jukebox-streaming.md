# Audio split + jukebox + loading/performance — decision log 2026-10-24

Status: implemented + tested locally (45 checks, see below). Shipped as the
PR that references this doc. Playable verification is a parent/user
playtest step — this doc never claims playable from tests alone.

## Owner directives (verbatim, as received)

Original completeness-audit task: "WIRE AUDIO SPLIT + JUKEBOX +
LOADING/PERFORMANCE INTO WESTERN HEART. You are a worker for a
completeness audit. Do real work, not just a report: implement, test,
ship via PR." Items: (1) Pantera voice split into Opus OR cue ranges
from the manifest, never invented offsets; (2) T7-style Jukebox with
soundtrack pools per mode/stage, including the Nosferatu synth score
as one selectable pool, without duplicating the music lane's work;
(3) announcer coverage; (4) asset streaming / background loading
without breaking the Netlify roster proxy; (5) model/texture
optimization pipeline wiring, if not already shipped — check main
first, do not duplicate a merged PR.

Finish directive 2026-10-24 19:39 CDT: "Don't leave any PRs unpushed or
unmerged don't leave any work unfinished or leave it queued start
working on everything use the GPU to get it finished and make sure
everything is merged and pushed and playable and testable without
clobbering anything on any side."

New directives 2026-10-24 19:41 CDT: (1) "Ghost Surf Rock" by Loyalty
Freak Music = Cape Jones theme song; if Cape Jones gets an arena,
Ghost Surf Rock is the MAIN track there, with interchanging tracks
rotating around it; vibe surf rock + spooky + witchy + batty +
Halloween (collection "WITCHY BATTY SPOOKY HALLOWEEN IN SEPTEMBER !!");
(2) remove the "tap to turn audio on" unlock, put audio on/off in
SETTINGS instead; (3) everything more mobile and user friendly,
phone-first, no dumb friction.

## What was verified first (files, not claims)

- `game/js/audio.js` on main is fully procedural (no file banks, no
  voice bus). `game/js/music.js` is one-BGM-per-stage with crossfade
  and intensity scaling. `game/js/voice.js` already has `announce()`
  and `game/data/voices/announcer.json` already covers all 11 calls —
  but `voice.announce` had ZERO call sites in `game.js`/`main.js`/
  `modes.js`/`menus.js` (grep, 2026-10-24), so announcer calls never
  played. `audio.voiceBus()` did not exist (voice.js already falls
  back to `ctx.destination` when it is absent).
- Pantera sampler: `pantera-sounds-from-king-t2-grunts-sampler.mp3`
  ffprobe 64.210045 s. Set B manifest durations sum to 48.609624 s;
  plus 26 × 0.6 s `silence.wav` gaps = 64.209624 s — 0.000421 s short
  of ffprobe, i.e. MP3 padding. Cue starts are therefore computed,
  not invented: start[n] = sum of earlier durations + 0.6 s per
  earlier gap. Raw Set B WAV durations match the manifest to ~5e-06 s.
- No Cape Jones arena exists: `game/js/stages.js` stage ids on main
  are shrine, tong-nou, tree-of-life, plains-of-chi-u,
  octagonal-shrine, helix-palace, palace-of-dreaming,
  phantom-marketplace, sunra, t7-mishima-dojo. The Cape Jones pool
  is therefore keyed to the future stage id `cape-jones-arena` and
  flagged pending-stage, and is selectable in Settings now so it is
  testable before the arena lands.
- Ghost Surf Rock: Free Music Archive page (Loyalty Freak Music,
  album WITCHY, BATTY, SPOOKY, HALLOWEEN IN SEPTEMBER !!, released
  Oct 01, 2018, 04:07, CC0 1.0) and Bandcamp page agree on title,
  artist, album and license. No direct MP3 URL was published on the
  fetched page text, and none is guessed here — the file download is
  a parent browser task (below).
- No asset-pipeline workflow existed on main (workflows on main:
  canon-names, clobber-guard, coverage-guard, deletion-guard,
  game-checks, instruction-gate, merge-tree-guard,
  no-deletion-guard, pr-safety-guard, ui-sources). No repo-wiring
  worker had shipped the gltfpack step, so it is wired here.

## Coordination with open PRs (by file, no duplication)

- PR #1028 (MERGED during this work, merge commit 6ee90f40): ships the split
  clips as OGG in `game/assets/voices/pantera/` (pantera-t2-01..26 +
  pantera-classic-01..26) with a rewritten `game/data/voices/
  pantera.json`. This PR therefore does NOT ship a second copy of
  those clips and does NOT touch `pantera.json`. What it adds is the
  missing half: the sampler cue table (`game/data/audio-events.json`,
  computed as above), the cue-slicing playback support
  (`voice.js` `clip.cue`), and the WHAudio event engine that consumes
  the cues. A local Opus re-encode of Set B (libopus 48k, from the
  raw norm WAVs) totals 274,958 bytes and matches manifest durations
  within Opus frame padding; it is kept as the fallback encode and
  is NOT committed, to avoid duplicating #1028.
- PR #1030 (MERGED during this work, merge commit 8579c6df): owns
  `game/js/music.js`, `game/data/music-library.json`, `game/js/main.js`
  (music lines), `game/js/game.js` (music lines) and the 25
  nos-t* track entries. This PR does NOT edit `music-library.json`
  or `game.js` at all. Jukebox pools live in the new
  `game/data/jukebox-pools.json`; `game/js/jukebox.js` reads library
  tracks at runtime and wraps `pickRotationTrack`/`pickTrack`, so
  either lane can land first (pre-#1030 the nosferatu pool delegates
  instead of failing; post-#1030 it resolves to nos-t01..nos-t25).
  The only `main.js` touch is the tap-banner removal, in a region
  #1030 does not change except its `music.unlock()` line inside
  `unlockAudio()` — this PR deliberately does NOT add that line, so
  the two branches merge as identical-deletion + one-side-addition.
- Blockers formerly on #1028 / #1030 (diagnosed during this work,
  resolved by their merges, not by faking approval): before merging,
  #1028's latest instruction-gate run failed while its current body
  passed the gate script locally (stale event payload is the script's
  own documented failure mode), and its `guard` job failed on
  "Fail if PR deletes files (unless labelled approved-deletion)"
  for its 9 deletions; #1030's instruction-gate failed
  deterministically on 4 deviation lines carrying no approval ref.
  Both PRs have since merged (commits above), so those blockers are
  moot — but their pending follow-ups (track bytes, Kaggle cut)
  remain open below and are NOT claimed done by this PR.

## Per-item status

1. Pantera voice split — DONE (cue table + engine + playback).
   `game/data/audio-events.json` (new) carries the 26 Set B cues and
   a `pantera_grunt_cued` random event; `game/js/wh-audio.js` (new,
   from the audio-middleware research engine) posts cues with
   no-repeat random + pitch jitter 0.94–1.06, bus gains, master
   compressor (threshold −12, ratio 8), state snapshots and the
   RTPC intensity formula
   0.35·comboHeat + 0.35·healthDeficit + 0.30·roundTimerPressure
   (last 15 s). `voice.js` slices `clip.cue`. Split files themselves
   are #1028's OGG set (above), not duplicated here.
2. Jukebox — DONE (pools + Settings UI + runtime wiring).
   `game/data/jukebox-pools.json` + `game/js/jukebox.js`, installed
   from `menus.js` at boot. Settings → JUKEBOX offers STAGE ROTATION
   (default, delegates to music.js), CAPE JONES and NOSFERATU.
   Cape Jones cycle = [Ghost Surf Rock, ...battle pool] repeating,
   so the theme leads each cycle and the battle tracks interchange
   around it. Nosferatu pool references nos-t01..nos-t25 only.
   Ghost Surf Rock entry: file `assets/music/ghost-surf-rock.mp3`
   (pending-file), license CC0-1.0, 247 s, vibe tags surf rock /
   spooky / witchy / batty / halloween, stage `cape-jones-arena`
   (pending-stage). Until the file lands, music.js falls back to its
   procedural loop for that track — never silence, never a crash.
3. Announcer — DONE (wiring) + NEEDS RECORDING (audio bytes).
   `audio.js` gains a voice bus (`voiceBus()`). `menus.js`
   `hookAnnouncer` wraps `_startRound`/`_endRound`/`_afterRound`
   (the codebase's existing hook pattern; `game.js` untouched):
   round-N or final-round at match point, fight on the 1100 ms
   FIGHT! beat, double-ko / time-up (timer at 0) / perfect (winner
   at full HP) / ko, you-win on a P1 match win. All calls are
   fire-and-forget and guarded — voice can never break a round.
   NEEDS RECORDING — exact lines, all currently subtitle-only
   placeholders in `game/data/voices/announcer.json`, no audio
   invented: "Round 1", "Round 2", "Round 3", "Final Round",
   "Fight!", "K.O.", "Double K.O.", "Perfect!", "Time Up", "Draw",
   "You Win". Proprietary announcer voice replaces these via the
   voice-clone pipeline; no copyrighted game audio ships.
4. Asset streaming / progressive LOD — DONE (pattern + hooks).
   `lazy.js` adds `preloadNextFight` (rematch pair via the existing
   fail-silent `assets.prefetch` lane, which dedups with the real
   fight load so a FIGHT press joins — never re-fetches — a warming
   model) and `preloadLowFirst` (caller-supplied low-LOD URL warmed
   first; no `-lod1` variant ships yet, so none is assumed).
   `menus.js` calls it on the VS screen and again at fight outro
   (leaveFight), so REMATCH rarely waits. `load-progress.js` adds
   `window.__whPreloadNote` status. Only MODEL_URLS ids are ever
   fetched, so the Netlify proxy (`game/_redirects` +
   `game/netlify.toml`, /roster/*, /customization/*, /packages/*,
   /game/* → gh-pages, 200) is untouched and its paths unchanged.
   Stage variants are not prefetched as models because stages stream
   through `arena.setStage`, not MODEL_URLS — that is a measured
   fact, not a gap in the pattern.
5. Optimization pipeline CI — DONE (script + budget check, advisory
   v1). `tools/asset-pipeline/wh-asset-pipeline.sh` (gltfpack batch,
   proven −54%/−59% on real WH assets; binary not committed),
   `tools/asset-pipeline/check-budgets.py` (warns over 25 MB, exits 2
   over GitHub's 100 MB push limit),
   `tools/asset-pipeline/README.md`, and
   `.github/workflows/asset-pipeline.yml`. The CI step is
   `continue-on-error` in v1 because the roster baseline has not
   been fully measured; promotion to a blocking gate is a follow-up
   once that baseline is known. It never fails for a missing
   gltfpack binary (optimization stays a local step).

## Tap-for-audio removal + mobile (2026-10-24 19:41 CDT) — DONE

- `game/index.html`: the `TAP TO ENABLE SOUND` banner div is removed.
- `game/js/main.js`: `unlockAudio()` no longer touches the banner,
  and the first-pointerdown listener + 600 ms show timer are deleted.
  All other `unlockAudio()` call sites stay: the first real tap (a
  menu, mode or fight tap) supplies the browser's required user
  gesture. Honest limit: browsers block sound before ANY gesture —
  that is platform policy, not a WH screen — so sound starts on the
  first tap the player already makes, never on a tap invented for
  audio. There is no way to make sound play before any tap in a
  mobile browser, and none is claimed here.
- Settings (`menus.js`, existing `wh_settings_v1` system, existing
  full-row toggle/segment components — phone-first targets as
  built): new SOUND toggle (`soundOn`, default true; honoured
  alongside the existing MUTE ALL key so older saves keep working)
  and the JUKEBOX segment row (STAGE ROTATION / CAPE JONES /
  NOSFERATU). Audio on/off now lives in Settings, as directed.

## Tests run (local, this PR's checkout shape)

- `node test/audio-jukebox.test.mjs`: ALL 45 CHECKS PASSED
  (cue table incl. 0.6 s gaps and ffprobe total; WHAudio cue slicing
  + missing-bank/unknown-event no-ops; jukebox cape cycle, nosferatu
  order, default delegation, pre-#1030 delegation; announcer 11
  triggers all placeholder; all surgical-edit text checks; Netlify
  proxy lines intact; lazy preload mapping incl. unknown-id skip).
- Syntax: `node --check` passed for all 8 JS files (audio, voice,
  lazy, load-progress, menus, main, jukebox, wh-audio).
- `python3 -m py_compile` passed for `check-budgets.py`; JSON parses
  for both new data files; workflow YAML parses.
- Budget script behaviour: 101 MB file → exit 2 with FAIL line;
  30 MB file → warning only, exit 0.
- GPU note: batch audio work here was 26 short clips (275 KB Opus
  total) — ffmpeg on the VM finished in under a minute, so no Kaggle
  GPU run was needed for this lane. The Kaggle GPU cut that IS still
  needed belongs to #1030's 25 Nosferatu tracks (below), not this PR.

## Specific next steps (actively worked, not queued vaguely)

1. Parent browser task — download Ghost Surf Rock (CC0, free) from
   the Free Music Archive page in `jukebox-pools.json`
   (`sourceUrl`) and place it at
   `game/assets/music/ghost-surf-rock.mp3`. Until then the Cape
   Jones pool orders correctly but that track falls back to the
   procedural loop. A live-browser fetch was attempted for the track
   link and failed with a local worker error (not a source failure);
   it was not retried, per the browser-failure rule.
2. (Resolved by merge — kept for the record.) #1028's former
   `guard`/gate blockers above; do NOT self-label to bypass a guard.
3. Parent browser task — #1030 merged, but its Kaggle GPU cut run
   (25 Nosferatu track bytes + Tekken audio bytes) is still pending
   from its own deviations. This PR's nosferatu pool resolves to
   those track ids as soon as the bytes land; until then the pool
   entries fall back like any other missing file track.
4. Voice lane — record the 11 proprietary announcer lines listed
   above (NEEDS RECORDING). No placeholder audio is presented as
   final anywhere in this PR.
5. Playtest (parent/user, phone portrait like the owner plays):
   open Settings → confirm SOUND toggle + JUKEBOX row render and
   persist; start a fight → confirm no tap-for-audio banner and
   sound starts on the first menu tap; play rounds → confirm
   announcer subtitles fire on round/fight/KO calls; pick JUKEBOX →
   CAPE JONES → confirm the pool order (Ghost Surf Rock slot falls
   back to the procedural loop until step 1 lands); rematch →
   confirm the second load does not stall at the old 6% point.
   Live Netlify behaviour was NOT verified by this worker (subagents
   cannot operate a live browser) and must be part of that playtest.

## CI fix (test only, after the first CI run)

The first CI run failed `game-unit-tests` only: this PR's test read
`game/index.html` and `game/_redirects`, which the game-unit-tests
sparse checkout (`.github/workflows/game-checks.yml`) does not include
(it checks out `test/`, `game/js`, `game/data` and a few asset dirs).
Reproduced locally in a sparse-shaped checkout (ENOENT on
`game/index.html`), then fixed in the test only: those two checks now
assert when the files are present and log a skip when they are absent.
The banner removal is additionally proven by the `main.js` text check,
which IS in the sparse scope. No game code changed in this fix.
