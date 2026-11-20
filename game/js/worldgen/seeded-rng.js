// seeded-rng.js — deterministic RNG for world generation.
// Worldgen must be reproducible: same seed -> same arena surroundings, same HMW
// zone, on every device. mulberry32 is small, fast, and good enough for layout
// work (NOT for crypto or gameplay-critical randomness).
// No DOM. Safe to import in node and in the browser.

/**
 * Hash an arbitrary string seed to a uint32.
 * FNV-1a 32-bit.
 */
export function hashSeed(str) {
  let h = 0x811c9dc5;
  const s = String(str);
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

/**
 * Normalize a seed (number or string) to uint32.
 */
export function normalizeSeed(seed) {
  if (typeof seed === 'number' && Number.isFinite(seed)) return seed >>> 0;
  return hashSeed(seed);
}

/**
 * mulberry32 PRNG. Returns a function rng() -> [0, 1).
 */
export function mulberry32(seed) {
  let a = normalizeSeed(seed);
  return function rng() {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * Convenience: rng + helpers (int range, pick, shuffle) sharing one stream.
 */
export function makeRng(seed) {
  const rng = mulberry32(seed);
  return {
    rng,
    next() { return rng(); },
    int(min, max) { return min + Math.floor(rng() * (max - min + 1)); },
    pick(arr) { return arr[Math.floor(rng() * arr.length)]; },
    shuffle(arr) {
      const a = arr.slice();
      for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(rng() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
      }
      return a;
    },
  };
}
