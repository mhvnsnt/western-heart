# tools/character-voice/lipsync — voice line → mouth-cue pipeline

**Owner law: Chatterbox stays the character-voice default. This pipeline
complements it — it turns finished voice lines into animation data.**

## What it does

`lipsync.mjs` takes a voice-line WAV (e.g. Dorowani's Squirtle-style Japanese
word bursts) and produces `*.cues.json` — Rhubarb-style mouth cues
(`[{start, end, value}]`, values X/A/B/C/D/E/F/G/H per Preston Blair
visemes). The game plays them back with `game/js/lipsync-player.js`
(`WHLipSyncPlayer`), which drives the fighter's jaw bone in sync with the
audio. No hand-keyed lip flap.

## Engine

**lip-sync-engine 1.0.3** (biolimbo/lip-sync-engine) — **MIT** —
WASM port of Rhubarb Lip Sync (Daniel Wolf) + PocketSphinx speech
recognition, built for browsers. Credits: original Rhubarb Lip Sync,
PocketSphinx, Preston Blair phoneme set. The engine + WASM + 37MB
acoustic model load from the package's own unpkg CDN on first run
(pipeline machine only — never shipped to players).

## Quick start

```bash
# 1. serve the repo (the page + wav must be fetchable)
python3 -m http.server 8765   # from the repo root

# 2. generate cues for a voice line
node tools/character-voice/lipsync/lipsync.mjs \
  path/to/dorowani_win1.wav \
  game/assets/voice/dorowani/win1.cues.json \
  --text "Konnichiwa arigato Ichiban Bankai"
```

The `--text` dialog hint significantly improves phoneme accuracy.

## Wiring

- **Pipeline:** this tool (Blender-free, CPU-only, runs on the VM).
- **Runtime:** `game/js/lipsync-player.js` — `WHLipSyncPlayer.play(fighterRoot, cuesUrl, {audio})`.
  Exposed as `window.WHIntegration.systems.lipsync` when the integration
  module loads; the voice lane calls it when a voice moment triggers
  (win poses, taunts, intros, cutscenes).
- **Voice cleanup first:** run `../phone_cleanup_chain.py` on phone-recorded
  lines before cue generation (de-reverb/denoise → polish → loudnorm).

## Why not vendored

The 37MB acoustic model + WASM would bloat the repo and the game.
The pipeline downloads it on demand; the game only ever sees the tiny
cues JSON (KBs). This is the same pattern as the other heavy models
(Chatterbox, RVC) — server/pipeline side, thin client.
