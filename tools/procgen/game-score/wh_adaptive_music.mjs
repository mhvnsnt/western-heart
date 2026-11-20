// wh_adaptive_music.mjs — pure, deterministic composition core for the WH adaptive score.
// No Web Audio dependency: runs in node (tests) and feeds any scheduler/adapter
// (Tone.js browser adapter in wh_tone_adapter.mjs). Music RNG is ISOLATED from gameplay
// RNG by construction: every function takes an explicit seed.
export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export const SCALES = {
  minorPentatonic: [0, 3, 5, 7, 10],
  dorian: [0, 2, 3, 5, 7, 9, 10],
  phrygian: [0, 1, 5, 7, 8],
};

// State -> { bpm, progression (scale-degree roots), layers active, density }
export const STATES = {
  menu:    { bpm: 84,  prog: [0, 5, 3, 6], layers: ['pad', 'arp'],            density: 0.35 },
  explore: { bpm: 96,  prog: [0, 3, 5, 4], layers: ['pad', 'arp', 'bass'],    density: 0.5 },
  combat:  { bpm: 140, prog: [0, 0, 5, 6], layers: ['pad', 'bass', 'drums', 'lead', 'arp'], density: 0.9 },
  victory: { bpm: 112, prog: [0, 4, 5, 3], layers: ['pad', 'lead', 'arp'],    density: 0.65 },
};

const midi = (root, degree) => root + degree;

// Markov chain over scale degrees for "composing in probabilities" (Spore-style).
export function markovMelody(rand, scale, bars, density) {
  const notes = [];
  let degree = Math.floor(rand() * scale.length);
  const transitions = [-2, -1, -1, 0, 1, 1, 2, 3]; // stepwise bias, occasional leap
  for (let b = 0; b < bars; b++) {
    for (let s = 0; s < 8; s++) {
      if (rand() < density) {
        notes.push({ beat: b * 4 + s * 0.5, degree, dur: 0.5, vel: 0.6 + rand() * 0.4 });
      }
      degree = (degree + transitions[Math.floor(rand() * transitions.length)] + scale.length * 2) % scale.length;
    }
  }
  return notes;
}

const DRUM_PATTERNS = {
  kick:  [1, 0, 0, 0, 1, 0, 0, 0.6, 1, 0, 0, 0, 1, 0, 0.6, 0],
  snare: [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0.5],
  hat:   [0.5, 0.3, 0.5, 0.3, 0.5, 0.3, 0.5, 0.3, 0.5, 0.3, 0.5, 0.3, 0.5, 0.3, 0.5, 0.4],
};

// Compose `bars` bars for a state. Returns { bpm, events: [{beat, midi, dur, vel, layer}] }.
export function composeBars(state, seed, bars = 4, rootMidi = 45 /* A2 */) {
  const cfg = STATES[state];
  if (!cfg) throw new Error(`unknown state: ${state}`);
  const rand = mulberry32(seed);
  const scale = state === 'combat' ? SCALES.phrygian : SCALES.minorPentatonic;
  const events = [];
  const active = new Set(cfg.layers);

  for (let b = 0; b < bars; b++) {
    const chordRoot = midi(rootMidi, scale[cfg.prog[b % cfg.prog.length] % scale.length]);
    const beat0 = b * 4;
    if (active.has('pad')) {
      for (const iv of [0, 2, 4]) {
        events.push({ beat: beat0, midi: midi(chordRoot + 12, scale[iv % scale.length]), dur: 4, vel: 0.35, layer: 'pad' });
      }
    }
    if (active.has('bass')) {
      for (let s = 0; s < 8; s++) {
        if (s % 2 === 0 || rand() < cfg.density * 0.5) {
          events.push({ beat: beat0 + s * 0.5, midi: chordRoot - 12 + (s % 4 === 2 ? 7 : 0), dur: 0.4, vel: 0.7, layer: 'bass' });
        }
      }
    }
    if (active.has('arp')) {
      for (let s = 0; s < 16; s++) {
        if (rand() < cfg.density) {
          events.push({ beat: beat0 + s * 0.25, midi: midi(chordRoot + 12, scale[(s + b) % scale.length]), dur: 0.22, vel: 0.4, layer: 'arp' });
        }
      }
    }
    if (active.has('drums')) {
      for (let s = 0; s < 16; s++) {
        const p = s / 16 * 16 | 0;
        if (DRUM_PATTERNS.kick[p] && rand() < DRUM_PATTERNS.kick[p]) events.push({ beat: beat0 + s * 0.25, midi: 36, dur: 0.2, vel: 0.9, layer: 'kick' });
        if (DRUM_PATTERNS.snare[p] && rand() < DRUM_PATTERNS.snare[p]) events.push({ beat: beat0 + s * 0.25, midi: 40, dur: 0.2, vel: 0.8, layer: 'snare' });
        if (rand() < DRUM_PATTERNS.hat[p] * cfg.density) events.push({ beat: beat0 + s * 0.25, midi: 42, dur: 0.1, vel: 0.4, layer: 'hat' });
      }
    }
    if (active.has('lead')) {
      for (const n of markovMelody(rand, scale, 1, cfg.density)) {
        events.push({ beat: beat0 + n.beat, midi: midi(chordRoot + 24, scale[n.degree]), dur: n.dur, vel: n.vel, layer: 'lead' });
      }
    }
  }
  events.sort((a, b) => a.beat - b.beat);
  return { bpm: cfg.bpm, events };
}

// Intensity 0..1 crossfade helper: returns per-layer gains for smooth transitions.
export function layerGains(fromState, toState, t) {
  const gains = {};
  for (const layer of new Set([...STATES[fromState].layers, ...STATES[toState].layers])) {
    const a = STATES[fromState].layers.includes(layer) ? 1 : 0;
    const b = STATES[toState].layers.includes(layer) ? 1 : 0;
    gains[layer] = a + (b - a) * t;
  }
  return gains;
}
