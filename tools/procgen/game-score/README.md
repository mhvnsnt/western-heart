# WH adaptive game score (`tools/procgen/game-score/`)

Infinite, state-driven procedural music for the Three.js playable build —
**zero audio files shipped**. (Sibling audio branch owns composed/AI BGM: YuE, Stable
Audio, MusicGen. This is the real-time generative layer.)

## Files
- **`wh_adaptive_music.mjs`** — pure composition core, no Web Audio dependency:
  seeded PRNG (isolated music RNG — toggling sound never changes gameplay),
  scales (minor pentatonic / dorian / phrygian), per-state chord progressions,
  Markov-chain melody ("composing in probabilities", Spore-style),
  intensity → layer mapping, `layerGains()` crossfades. Node-testable.
- **`wh_tone_adapter.mjs`** — browser adapter to **Tone.js** (MIT, 14.7k stars):
  look-ahead Transport scheduler, per-layer Gain nodes (click-free crossfades,
  ouigame/veilborn pattern), synth rig (pad/bass/arp/lead/kick/snare/hat).
  The adapter is the only Tone.js touchpoint — swappable without recomposing.
- **`test_music.mjs`** — offline tests. `node test_music.mjs` → ALL GREEN (21 asserts).

## States
`menu` (84 BPM, pad+arp) → `explore` (96, +bass) → `combat` (140, full kit,
phrygian) → `victory` (112). `score.setState('combat')` crossfades layers.

## Browser usage
```html
<script type="importmap">{"imports":{"tone":"https://unpkg.com/tone@15/build/Tone.js"}}</script>
<script type="module">
import { WHScore } from './wh_tone_adapter.mjs';
const score = new WHScore();
await score.start('menu');
game.on('fightStart', () => score.setState('combat'));
</script>
```

## Test evidence (2026-10-16)
`node test_music.mjs`: 21/21 PASS — determinism, MIDI range, combat denser than
menu, crossfade endpoints, Markov bounds, unknown-state throws.
