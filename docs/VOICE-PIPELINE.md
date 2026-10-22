# WESTERN HEART — Voice Pipeline

Owner directive (2026-10-22): *"Dorowani is the FIRST voice-acted character —
voice like Squirtle (creature sounds + his Japanese word bursts). Voice
moments: win poses/taunts, intro sequences, cutscenes."*

Pilot character: **DOROWANI** (Gon's replacement — kappa-yokai crocodile
demon of the Eastern Mind swamp). The pipeline is built around him first,
then the roster expands onto it.

## 1. Voice direction (canon — user's words)

- **Squirtle-style creature vocalizations + Japanese word bursts.**
- He does **NOT** speak in sentences — Pokémon/Digimon-style, Pikachu energy
  with Japanese vocabulary.
- His first lines: **"Konnichiwa arigato Ichiban Bankai."**
- Trickster energy: hungry, mischievous, barks random Japanese words like a
  creature name-cry ("Dorowani!").

This direction lives in the per-fighter manifest (`game/data/voices/<id>.json`,
`direction` field) so every future voice session reads the same brief.

## 2. Architecture

```
game/js/voice.js                  VoiceEngine — loading, playback, subtitles
game/js/audio.js                  AudioEngine — owns the Web Audio graph;
                                  exposes a dedicated voice bus (voiceGain)
game/data/voices/<fighter>.json   per-fighter voice manifest (clips, text,
                                  direction, placeholder status)
game/assets/voices/<fighter>/     real recordings land here
docs/VOICE-PIPELINE.md            this contract
```

- The game already has a procedural `AudioEngine` (Web Audio, no files).
  Voice is the first **file-based** audio: `VoiceEngine` fetches +
  `decodeAudioData`s each clip and plays it through `audio.voiceBus`
  (a dedicated gain under the master, so voice never fights music/SFX).
- `VoiceEngine` is lazy: manifests load on first use per fighter, clips
  decode on first play, then stay cached. Missing files are **not** errors —
  see §5.

## 3. Trigger points

| Trigger      | When it fires                                   | Status      |
|--------------|-------------------------------------------------|-------------|
| `select`     | Fighter confirmed on the select screen          | wired (API) |
| `intro`      | Intro-interaction beat references a voice clip  | **WIRED**   |
| `win`        | Winner enters the victory / win-pose state      | **WIRED**   |
| `taunt`      | Victory taunt beat (win pose, second+ clip)     | **WIRED**   |
| `hit` / `ko` | Effort / knockout cries                        | API-ready   |
| `cutscene`   | Cutscene timeline cue (see docs/CUTSCENE-SPEC)  | spec'd      |

Wiring lives in `game/js/game.js`: `_endRound()` fires `voice.play(winner,
'win')` fire-and-forget (never blocks the 3 s win beat); `startMatch()` runs
`playIntroInteraction()` before round 1, and each beat's `voice` field fires
`voice.playLine()`. Win sequences / victory taunts themselves are untouched —
only voice triggers were added (owner: "keep those as-is").

## 4. VoiceEngine API (`game/js/voice.js`)

```js
import { voice } from './voice.js';

voice.unlock();                       // call from a user gesture; builds subtitle layer
await voice.loadManifest('dorowani'); // fetch + cache game/data/voices/dorowani.json
voice.play('dorowani', 'win');        // random 'win' clip: subtitle + audio (fire-and-forget)
voice.play('dorowani', 'intro', 2);   // 3rd intro variant (0-based)
await voice.playLine('dorowani', 'intro-01', 'Konnichiwa!');
// explicit clip id + subtitle override; resolves when the line is done
voice.setEnabled(false);              // mute voice (options menu hook)
```

- `play()` never throws: no manifest → silent no-op + `console.info`; no
  audio file → **subtitle-only** + `console.info('[WH voice] placeholder')`.
- Subtitles render in a bottom-center `#wh-voice-sub` layer, auto-hide after
  ~2.2 s, and never stack (one line at a time, latest wins).
- Overlap policy: a new `play()` ducks nothing — voice clips are short
  (< 3 s); concurrent lines queue per fighter.

## 5. Asset spec (for the user / voice sessions)

Recordings go in `game/assets/voices/<fighter-id>/`:

| Rule | Value |
|------|-------|
| Format | **OGG Vorbis** preferred (web-native, small); MP3 accepted as fallback |
| Sample rate | 44 100 Hz |
| Channels | Mono (voice is center-panned by the engine) |
| Loudness | Normalized, peaks ≈ −3 dBFS; leave 80 ms of room tone head/tail |
| Length | One clip ≤ 3 s (barks/bursts); win lines ≤ 5 s |
| Size | ≤ 500 KB per clip |
| Naming | `<trigger>-<NN>.<ext>` — e.g. `dorowani/win-01.ogg`, `dorowani/intro-02.ogg` |

Manifest clip entry:

```json
{
  "id": "win-01",
  "trigger": "win",
  "file": "assets/voices/dorowani/win-01.ogg",
  "text": "Bankai!",
  "note": "Triumphant roar-burst, chest puffed. Squirtle-energy, NOT a sentence.",
  "status": "placeholder"
}
```

- `file` is relative to `game/` (the page root). Set `status` to
  `"final"` when the real recording lands; the engine doesn't care, but the
  crew's audits do.
- **Delivering audio to the owner (standing rule 2026-10-22):** ALL audio
  files sent to the owner go as **direct download links** via remote-storage
  upload — NEVER as in-chat attachments (the in-chat audio player is broken
  on the owner's Android app: shows 0:00, won't play). State the link expiry
  with the link. The voice-clone pipeline's `deliver` stage does this
  automatically.
- **Placeholder policy (owner rule):** if no recording exists yet, the
  pipeline ships with `status: "placeholder"` manifests and plays
  **subtitle-only**. We do NOT synthesize fake "voice" and present it as
  final. A clearly-labeled dev-only synth blip exists behind
  `voice.debugBleeps = true` for timing tests — it is never on in builds
  the user sees.

## 6. Adding a fighter (roster expansion)

1. Create `game/data/voices/<fighter-id>.json` (copy Dorowani's; keep the
   `direction` field honest to the character).
2. Produce the recordings — **production path is the voice cloning
   pipeline** (`tools/character-voice/voice-clone/`, contract:
   `docs/VOICE-CLONING-PIPELINE.md`): write a voice spec, generate remotely
   (no local weights, ever), review via direct download links, then
   `--deposit` writes the clips to `game/assets/voices/<fighter-id>/` and
   flips `status` to `"final"`. Owner-recorded lines are cleaned first with
   `tools/character-voice/phone_cleanup_chain.py`.
3. Done — `voice.play(id, trigger)` works everywhere the triggers fire.
   Optional: add `voice` clip refs to that fighter's intro-interaction beats
   (see docs/INTRO-INTERACTION-SYSTEM.md).

## 7. Proof / verification

- `node --check game/js/voice.js` — syntax.
- In-engine: win a round as/against a voiced fighter → subtitle shows the
  line; console shows `[WH voice]` trigger + clip id; with a real file in
  `game/assets/voices/`, the clip plays through the voice bus.
- Dorowani pilot manifest: `game/data/voices/dorowani.json` (9 clips,
  all `placeholder` — **blocker: needs voice recordings from the user**).
