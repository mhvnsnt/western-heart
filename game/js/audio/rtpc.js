/* ============================================================
   WESTERN HEART — Wwise-style RTPC / jitter / no-repeat helpers
   (2026-10-24, Lane 4 audio). Pure supplement to the WebAudio
   event engine: the patterns come from the audio-middleware
   research sketch (~/workspace/audio-middleware-research/
   wh-audio-engine.js + audio-events.json), which PR #1046's
   game/js/wh-audio.js already wires as postEvent → fresh
   AudioBufferSourceNode, random containers with no-repeat, and
   buses into a master compressor. What #1046's engine does NOT
   pin down, this module does — as pure, tested functions any
   engine can import, without editing #1046's file:

   • RTPC Intensity = 0.35 × comboHeat + 0.35 × healthDeficit
     + 0.30 × roundTimerPressure (each input clamped to [0,1],
     result clamped to [0,1]).
   • playbackRate jitter 0.94–1.06 (random container variation).
   • Random no-repeat pick (never the same variation twice in a
     row when more than one variation exists).
   • Master compressor settings from the research sketch:
     threshold −12 dB, ratio 8 (no other values claimed).
   • Engine states: Menu / Fight / KO / Pause.
   • Buses: music / sfx / voice / ui / ambience.

   Side-effect free: no AudioContext, no DOM. The engine owns
   nodes; this module owns the numbers.
   ============================================================ */

export const ENGINE_STATES = ['Menu', 'Fight', 'KO', 'Pause'];
export const BUSES = ['music', 'sfx', 'voice', 'ui', 'ambience'];

export function clamp01(v) {
  const n = Number(v);
  if (!Number.isFinite(n)) return 0;
  return Math.min(1, Math.max(0, n));
}

/* RTPC Intensity, research formula. Inputs are 0..1 measures:
   comboHeat (how hot the current combo/pressure is),
   healthDeficit (1 − defender HP fraction, i.e. how close to KO),
   roundTimerPressure (how late in the round it is). */
export function computeIntensity({ comboHeat = 0, healthDeficit = 0, roundTimerPressure = 0 } = {}) {
  return clamp01(
    0.35 * clamp01(comboHeat)
    + 0.35 * clamp01(healthDeficit)
    + 0.30 * clamp01(roundTimerPressure),
  );
}

/* playbackRate jitter for random-container variations: 0.94–1.06.
   rand defaults to Math.random; tests inject a stub. */
export function jitterRate(rand = Math.random) {
  return 0.94 + rand() * 0.12;
}

/* Random variation pick with no-repeat: returns an index in
   [0, n). When n > 1 it never returns lastIdx; when n <= 1 it
   returns 0. lastIdx null/undefined means "no previous pick". */
export function pickNoRepeat(n, lastIdx, rand = Math.random) {
  if (n <= 1) return 0;
  let idx = Math.floor(rand() * n);
  if (idx === lastIdx) idx = (idx + 1) % n;
  return idx;
}

/* Master compressor (DynamicsCompressor) settings, exactly as
   set in the research sketch. Nothing else is claimed here. */
export function masterCompressorSettings() {
  return { threshold: -12, ratio: 8 };
}
