/* ============================================================
   WESTERN HEART — Procedural SFX parameters (MetaSounds-style)
   Pattern source: Unreal MetaSounds (node-based procedural audio).
   This module does NOT duplicate game/js/audio.js (the engine) —
   it computes PARAMETER SETS for procedural sound nodes (oscillator
   / noise / filter / envelope) that audio.js / hitfx.js render
   through Web Audio. Pure functions: Node-testable with no
   AudioContext. renderGraph(audioCtx, params) is the thin browser
   seam that builds the actual nodes when a context is supplied.
   Kinds: hit (punch/kick impact), block, whoosh (swing), soul
   (Soul Urge / aura shimmer). Intensity 0..1 scales gain, filter
   cutoff, and decay — louder hits are brighter and longer, not
   just louder.
   ============================================================ */

export function buildSFXParams(kind, intensity = 0.5) {
  const i = Math.max(0, Math.min(1, intensity));
  const base = {
    hit: { oscType: 'triangle', freq: 120 + i * 80, noiseMix: 0.6, filterFreq: 800 + i * 2400, attack: 0.001, decay: 0.12 + i * 0.15, gain: 0.3 + i * 0.7 },
    block: { oscType: 'square', freq: 200, noiseMix: 0.3, filterFreq: 1200 + i * 1000, attack: 0.001, decay: 0.08 + i * 0.08, gain: 0.2 + i * 0.4 },
    whoosh: { oscType: 'sine', freq: 400 + i * 600, noiseMix: 0.9, filterFreq: 500 + i * 3000, attack: 0.02, decay: 0.15 + i * 0.2, gain: 0.15 + i * 0.45 },
    soul: { oscType: 'sine', freq: 880 + i * 440, noiseMix: 0.1, filterFreq: 2000 + i * 4000, attack: 0.05, decay: 0.5 + i * 0.5, gain: 0.2 + i * 0.5 },
  }[kind];
  if (!base) throw new Error('proc-audio: unknown SFX kind ' + kind);
  return { kind, intensity: i, ...base };
}

// Browser seam: build Web Audio nodes from params. Returns the
// nodes (caller connects / starts them); in Node without a context
// this simply is not called — params alone are the testable unit.
export function renderGraph(audioCtx, params) {
  if (!audioCtx || typeof audioCtx.createOscillator !== 'function') {
    throw new Error('proc-audio: AudioContext is required (browser only)');
  }
  const osc = audioCtx.createOscillator();
  osc.type = params.oscType;
  osc.frequency.value = params.freq;
  const gain = audioCtx.createGain();
  gain.gain.setValueAtTime(0, audioCtx.currentTime);
  gain.gain.linearRampToValueAtTime(params.gain, audioCtx.currentTime + params.attack);
  gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + params.attack + params.decay);
  const filter = audioCtx.createBiquadFilter();
  filter.type = 'lowpass';
  filter.frequency.value = params.filterFreq;
  osc.connect(filter); filter.connect(gain);
  return { osc, filter, gain, destination: gain };
}
