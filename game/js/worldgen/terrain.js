// terrain.js — FastNoise-based terrain for Western Heart.
//
// Layered heightmaps, biome masks and cave masks for arena surroundings and
// Heart-and-Mind-Within open zones. Runtime noise source is the vendored
// FastNoiseLite JS port (MIT, same algorithm family and author as FastNoise2).
// FastNoise2 itself is C++/SIMD with no JS/WASM build shipped — see
// docs/research/WORLD-GENERATION-2026-10-23.md for the [RESEARCHED] WASM path.
//
// Arena law: generates NEW terrain. Never touches existing arenas' canon look.
//
// No DOM. Safe to import in node and in the browser.
import FastNoiseLite from './vendor/fastnoise-lite.js';
import { normalizeSeed } from './seeded-rng.js';

export { FastNoiseLite };

// One configured noise layer.
export function makeNoise(cfg = {}, seed = 1337) {
  const n = new FastNoiseLite(normalizeSeed(seed ^ (cfg.salt || 0)));
  n.SetNoiseType(cfg.noiseType || FastNoiseLite.NoiseType.OpenSimplex2);
  n.SetFrequency(cfg.frequency == null ? 0.02 : cfg.frequency);
  const fractal = cfg.fractal || FastNoiseLite.FractalType.FBm;
  n.SetFractalType(fractal);
  n.SetFractalOctaves(cfg.octaves == null ? 4 : cfg.octaves);
  n.SetFractalLacunarity(cfg.lacunarity == null ? 2.0 : cfg.lacunarity);
  n.SetFractalGain(cfg.gain == null ? 0.5 : cfg.gain);
  if (cfg.cellularDistanceFn) n.SetCellularDistanceFunction(cfg.cellularDistanceFn);
  if (cfg.cellularReturnType) n.SetCellularReturnType(cfg.cellularReturnType);
  if (cfg.cellularJitter != null) n.SetCellularJitter(cfg.cellularJitter);
  return n;
}

// Built-in layer presets. Frequencies assume world units ~= meters and a
// ~60m zone; scale frequency inversely with zone size.
export const LAYER_PRESETS = {
  // Gentle rolling base for temple courtyards: mostly flat, slight undulation.
  courtyardBase: {
    noiseType: 'OpenSimplex2', fractal: 'FBm', octaves: 3,
    frequency: 0.03, gain: 0.5, amplitude: 1.2, salt: 101,
  },
  // Ridged hills for HMW open zones.
  hmwHills: {
    noiseType: 'OpenSimplex2S', fractal: 'Ridged', octaves: 5,
    frequency: 0.012, gain: 0.55, amplitude: 9.0, salt: 202,
  },
  // Fine detail added on top of any base.
  detail: {
    noiseType: 'Perlin', fractal: 'FBm', octaves: 2,
    frequency: 0.15, gain: 0.5, amplitude: 0.35, salt: 303,
  },
  // Cellular mask for cave mouths / rock clusters (thresholded, not height).
  caves: {
    noiseType: 'Cellular', fractal: 'None', octaves: 1,
    frequency: 0.05, amplitude: 1.0, salt: 404,
    cellularReturnType: 'Distance2Div',
  },
};

function resolvePreset(p) {
  const out = { ...p };
  out.noiseType = FastNoiseLite.NoiseType[p.noiseType] ?? FastNoiseLite.NoiseType.OpenSimplex2;
  out.fractal = FastNoiseLite.FractalType[p.fractal] ?? FastNoiseLite.FractalType.FBm;
  if (p.cellularReturnType) {
    out.cellularReturnType = FastNoiseLite.CellularReturnType[p.cellularReturnType];
  }
  return out;
}

/**
 * Sample a layered heightmap.
 *
 * @param {object} opts {
 *   width, height (samples), seed,
 *   layers: [presetName | layerCfg]  (heights sum: amplitude * noise),
 *   flatten: { cx, cy, radius, to }  optional arena-floor flattening —
 *            keeps the fight area level while surroundings roll.
 *   offsetX, offsetY: sample-space offset (for chunked/infinite zones)
 * }
 * @returns {object} { data: Float32Array (row-major), width, height,
 *                     min, max, mean, seed }
 */
export function sampleHeightmap(opts = {}) {
  const width = opts.width || 96;
  const height = opts.height || 96;
  const seed = opts.seed == null ? 1337 : opts.seed;
  const layers = (opts.layers || ['courtyardBase', 'detail']).map((l) =>
    makeNoise(resolvePreset(typeof l === 'string' ? LAYER_PRESETS[l] : l), seed));
  const amps = (opts.layers || ['courtyardBase', 'detail']).map((l) => {
    const p = typeof l === 'string' ? LAYER_PRESETS[l] : l;
    return p.amplitude == null ? 1 : p.amplitude;
  });

  const data = new Float32Array(width * height);
  const ox = opts.offsetX || 0;
  const oy = opts.offsetY || 0;
  let min = Infinity, max = -Infinity, sum = 0;

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      let h = 0;
      for (let li = 0; li < layers.length; li++) {
        h += layers[li].GetNoise(x + ox, y + oy) * amps[li];
      }
      // Optional arena-floor flattening: blend to a fixed height near center.
      const fl = opts.flatten;
      if (fl) {
        const dx = x - (fl.cx == null ? width / 2 : fl.cx);
        const dy = y - (fl.cy == null ? height / 2 : fl.cy);
        const d = Math.sqrt(dx * dx + dy * dy) / fl.radius;
        if (d < 1) {
          const t = d * d * (3 - 2 * d); // smoothstep
          h = fl.to * (1 - t) + h * t;
        }
      }
      data[y * width + x] = h;
      if (h < min) min = h;
      if (h > max) max = h;
      sum += h;
    }
  }
  return { data, width, height, min, max, mean: sum / data.length, seed };
}

/**
 * Async variant: yields to the event loop every `rowsPerYield` rows so the
 * mobile UI stays responsive during large generations. Resolves to the same
 * shape as sampleHeightmap.
 */
export async function sampleHeightmapAsync(opts = {}, rowsPerYield = 16, onProgress) {
  const width = opts.width || 96;
  const height = opts.height || 96;
  const seed = opts.seed == null ? 1337 : opts.seed;
  const layerCfgs = opts.layers || ['courtyardBase', 'detail'];
  const layers = layerCfgs.map((l) =>
    makeNoise(resolvePreset(typeof l === 'string' ? LAYER_PRESETS[l] : l), seed));
  const amps = layerCfgs.map((l) => {
    const p = typeof l === 'string' ? LAYER_PRESETS[l] : l;
    return p.amplitude == null ? 1 : p.amplitude;
  });

  const data = new Float32Array(width * height);
  const ox = opts.offsetX || 0;
  const oy = opts.offsetY || 0;
  let min = Infinity, max = -Infinity, sum = 0;
  const fl = opts.flatten;

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      let h = 0;
      for (let li = 0; li < layers.length; li++) {
        h += layers[li].GetNoise(x + ox, y + oy) * amps[li];
      }
      if (fl) {
        const dx = x - (fl.cx == null ? width / 2 : fl.cx);
        const dy = y - (fl.cy == null ? height / 2 : fl.cy);
        const d = Math.sqrt(dx * dx + dy * dy) / fl.radius;
        if (d < 1) {
          const t = d * d * (3 - 2 * d);
          h = fl.to * (1 - t) + h * t;
        }
      }
      data[y * width + x] = h;
      if (h < min) min = h;
      if (h > max) max = h;
      sum += h;
    }
    if ((y + 1) % rowsPerYield === 0) {
      if (onProgress) onProgress((y + 1) / height);
      await new Promise((r) => setTimeout(r, 0));
    }
  }
  if (onProgress) onProgress(1);
  return { data, width, height, min, max, mean: sum / data.length, seed };
}

/**
 * Classify each sample into a biome id. Thresholds are in height units.
 * Returns Uint8Array: 0=water, 1=sand/floor, 2=grass, 3=rock, 4=snow/peak.
 */
export function classifyBiomes(hm, opts = {}) {
  const water = opts.water == null ? -0.6 : opts.water;
  const sand = opts.sand == null ? -0.15 : opts.sand;
  const rock = opts.rock == null ? 3.2 : opts.rock;
  const snow = opts.snow == null ? 6.0 : opts.snow;
  const out = new Uint8Array(hm.data.length);
  for (let i = 0; i < hm.data.length; i++) {
    const h = hm.data[i];
    out[i] = h < water ? 0 : h < sand ? 1 : h < rock ? 2 : h < snow ? 3 : 4;
  }
  return out;
}

/**
 * Cave/void mask from cellular noise: 1 where the mask is "open".
 * Used for cave mouths in cliff walls / tunnel entrances in HMW zones.
 */
export function sampleCaveMask({ width = 96, height = 96, seed = 1337, threshold = 0.28, frequency = 0.05 } = {}) {
  const n = makeNoise(resolvePreset({ ...LAYER_PRESETS.caves, frequency }), seed);
  const out = new Uint8Array(width * height);
  let open = 0;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const v = Math.abs(n.GetNoise(x, y));
      const o = v < threshold ? 1 : 0;
      out[y * width + x] = o;
      open += o;
    }
  }
  return { mask: out, width, height, openFraction: open / out.length, seed, threshold };
}
