# WESTERN HEART — Music Pipeline

Owner directive (2026-10-22, Track 2): *"Pull the MUSIC SYSTEMS/CODE from the
teardown files — how tracks are assigned to stages/menus, how they loop,
transition, layer, how battle music intensifies, all of it. The SONGS
themselves get replaced over time with: the user's own music + open-source /
public-domain / non-copyright music. Build the replacement pipeline now."*

## What the teardowns taught us (systems, not songs)

- **Urban Reign** (`teardown/urban-reign/sound/ok_adx/ADX-INVENTORY.csv`):
  per-stage battle BGM as `bgNN_01.adx` (one track per stage), character
  voices as `v_*` ADX, menu/DC music as `bgm_*`. I.e. **stage-tagged BGM
  assignment** — the exact model `MusicEngine.pickTrack()` implements.
- **Tekken convention** (series-wide, reflected across the tekken3/7/8
  teardowns): one BGM per stage; separate title / character-select / versus
  themes; music plays ACROSS rounds and only changes on screen/stage change;
  final-round intensity lift; announcer ducks the music; results jingle.
- **Eastern Mind** (owner's own game): CDA soundtrack —
  `cda-tong-nou-theme`, `cda-tong-nou-esoteric-mix`,
  `cda-transmigration-ending`, `ending-theme` — these ship IN the game as
  the seed of the owner's-music side of the library.

No copyrighted teardown MUSIC ships in the repo — only the systems above
and the owner's own tracks.

## The engine: `game/js/music.js` (MusicEngine)

| System | How it works |
|---|---|
| **Assignment** | `pickTrack({stage, mode, mood})` — stage tag wins, then mode, then mood, then first battle track. Tekken jukebox rule. |
| **Looping** | Gapless WebAudio buffer loops (`loopStart`/`loopEnd` supported per track). |
| **Transitions** | 1.6 s crossfade on every switch — never a hard cut. |
| **Layering / intensity** | `setIntensity(0..1)` ramps a lowpass filter (700 Hz → 16 kHz) + gain. Tracks may ALSO ship `stems` (layer files) later — the format reserves it. Call sites: round start 0.55, FIGHT 0.7, final round 0.85, KO/time-up 0.3, fighter <25% HP 1.0 (wire the HP hook when the HUD exposes it). |
| **Voice ducking** | `voice.onSpeech` → `music.duck()` dips BGM ~8 dB under announcer/intro/win lines. |
| **Fallback** | Library/track missing → the procedural taiko/shakuhachi loop in `audio.js`. The game is never silent. |
| **File preference** | Each track tries `file` (local `game/assets/music/`) first, then `remote` URL. |

Wiring: `main.js` — `music.unlock()` on first gesture; `playMenu('title'/'select')`
on menu screens; `playBattle(stageId)` at fight start; `playVictory()` on the
results beat; `game.js` drives intensity + announcer calls.

## The library: `game/data/music-library.json`

One JSON file, zero code. Each track:

```json
{
  "id": "battle-volatile",
  "file": "assets/music/battle-volatile.mp3",
  "remote": "https://incompetech.com/.../Volatile%20Reaction.mp3",
  "title": "Volatile Reaction",
  "artist": "Kevin MacLeod",
  "license": "CC-BY-4.0",
  "credit": "Volatile Reaction — Kevin MacLeod (incompetech.com) — CC BY 4.0",
  "moods": ["aggressive"],
  "modes": ["battle"],
  "stages": ["shrine"],
  "loop": true,
  "gain": 1.0
}
```

- `modes`: `title` `select` `versus` `battle` `victory` `results` `credits`
  (future: `gungaku` for the fight-lab mode, side-game modes).
- `moods`: `calm` `tense` `aggressive` `dark` `epic` `driving` `mystical`
  `mechanical` `triumphant` — free-form; the engine matches on them.
- `stages`: stage ids from `game/js/stages.js`.

## How to add a track (no code changes)

1. Drop the file into `game/assets/music/` (OGG preferred, MP3 fine).
2. Add an entry to `game/data/music-library.json` with `moods`/`modes`/`stages` tags.
3. Done — `pickTrack` finds it. Test: `node` harness or just load the game.

## How the user swaps in their own music

- **Same filename**: drop `battle-volatile.mp3` (your version) into
  `game/assets/music/` — the local `file` always wins over `remote`.
- **New file**: point the track's `file` at it, retag moods/stages.
- **Full takeover**: replace the whole `tracks` array — the engine only
  reads tags. Keep the `credit`/`license` fields honest.
- **License rule**: only ship files we have the rights to (owner-original,
  CC0, CC-BY with credit, public domain). The `license` + `credit` fields
  are the audit trail — gitleaks/CI and the merge gate check them.

## Seed content (shipped now)

| # | Track | Source | Used for |
|---|---|---|---|
| 1 | Meditation Impromptu 01 | Kevin MacLeod, CC BY 4.0 | Calm menu alt (mood-tagged) |
| 2 | Exhilarate | Kevin MacLeod, CC BY 4.0 | Character select (+ Plains of Chi-U) |
| 3 | Volatile Reaction | Kevin MacLeod, CC BY 4.0 | Shrine of the Blade |
| 4 | The Cannery | Kevin MacLeod, CC BY 4.0 | Palace of Dreaming |
| 5 | Basic Implosion | Kevin MacLeod, CC BY 4.0 | Helix Palace |
| 6 | Five Armies | Kevin MacLeod, CC BY 4.0 | Tree of Life, Sun Rā |
| 7 | Hitman | Kevin MacLeod, CC BY 4.0 | Phantom Marketplace |
| 8 | Mechanolith | Kevin MacLeod, CC BY 4.0 | Octagonal Shrine |
| 9 | Fanfare for Space | Kevin MacLeod, CC BY 4.0 | Victory jingle |
| 10 | Deliberate Thought | Kevin MacLeod, CC BY 4.0 | spare menu bed |
| 11 | **Tong-Nou Theme (CDA) — FLAGSHIP** | Owner's Eastern Mind OST | **Title screen**, TONG-NOU stage, versus rotation |
| 12 | Tong-Nou Esoteric Mix (CDA) | Owner's Eastern Mind OST | Versus screen |
| 13 | Transmigration Ending (CDA) | Owner's Eastern Mind OST | Credits |
| 14 | Ending Theme | Owner's Eastern Mind OST | Results screen |

Full credit lines live in each track's `credit` field (CC BY 4.0
attribution requirement). The owner's four CDA tracks are `license:
"owner-original"`.

## Future hooks (not built)

- **Track stems**: per-track `stems` array for true layered intensity
  (drums/lead fade with `setIntensity`). Format reserved; engine falls back
  to filter+gain today.
- **Gungaku mode** (fight lab, user-locked 2026-10-22): tag tracks
  `modes: ["gungaku"]` when the mode ships — "war music" deserves its own bed.
- **Crowd reactions**: deferred by owner decision — ships WITH the crowd
  system, not here (see `docs/VOICE-MAPPING.md`).
