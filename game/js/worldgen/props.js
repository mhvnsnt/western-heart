// props.js — seeded prop scattering for generated zones.
//
// Takes a WFC layout and/or heightmap and places props (lanterns, rocks,
// trees, rubble) with exclusion rules, so set dressing follows the generated
// structure instead of floating randomly.
//
// No DOM. Safe to import in node and in the browser.
import { makeRng } from './seeded-rng.js';

/**
 * Scatter props.
 *
 * @param {object} opts {
 *   seed,
 *   layout:  { names } from wfc.generateLayout (optional),
 *   heightmap: { data, width, height } from terrain (optional),
 *   defs: [ { id, tiles: ['floor','grass'], // allowed layout tiles
 *             biomes: [2],                 // allowed biome ids (optional)
 *             minH, maxH,                  // height range (optional)
 *             count | density,              // exact count or per-100-cells
 *             minSpacing,                   // cells of separation
 *             yOffset } ]
 * }
 * @returns {array} [{ id, x, y, h, rot }]  x/y in cell coords, h = terrain height
 */
export function scatterProps(opts = {}) {
  const seed = opts.seed == null ? 4242 : opts.seed;
  const rng = makeRng(seed);
  const defs = opts.defs || [];
  const layout = opts.layout || null;
  const hm = opts.heightmap || null;

  const W = layout ? layout.width : hm ? hm.width : 0;
  const H = layout ? layout.height : hm ? hm.height : 0;
  if (!W || !H) return [];

  // Precompute biome ids if needed.
  let biomes = null;
  if (hm && defs.some((d) => d.biomes)) {
    biomes = new Uint8Array(hm.data.length); // caller can pass classified; default: all grass(2)
    biomes.fill(2);
  }

  const placed = []; // {x, y}
  const out = [];

  for (const def of defs) {
    const want = def.count != null ? def.count
      : Math.round(((def.density == null ? 1 : def.density) / 100) * W * H);
    const spacing2 = Math.pow(def.minSpacing == null ? 2 : def.minSpacing, 2);
    let added = 0;
    let guard = want * 60 + 200; // give up gracefully, never hang

    while (added < want && guard-- > 0) {
      const x = rng.int(0, W - 1);
      const y = rng.int(0, H - 1);

      if (def.tiles && layout) {
        const t = layout.names[y][x];
        if (!def.tiles.includes(t)) continue;
      }
      if (def.biomes && biomes) {
        if (!def.biomes.includes(biomes[y * W + x])) continue;
      }
      let h = 0;
      if (hm) {
        h = hm.data[y * W + x];
        if (def.minH != null && h < def.minH) continue;
        if (def.maxH != null && h > def.maxH) continue;
      }
      let ok = true;
      for (const p of placed) {
        const dx = p.x - x, dy = p.y - y;
        if (dx * dx + dy * dy < spacing2) { ok = false; break; }
      }
      if (!ok) continue;

      placed.push({ x, y });
      out.push({ id: def.id, x, y, h: h + (def.yOffset || 0), rot: rng.next() * Math.PI * 2 });
      added++;
    }
  }
  return out;
}

// Default prop sets per zone kind.
export const PROP_SETS = {
  'temple-courtyard': [
    { id: 'rubble', tiles: ['floor', 'moss'], density: 2.0, minSpacing: 2 },
    { id: 'fallen-petals', tiles: ['floor', 'moss', 'path'], density: 3.0, minSpacing: 1 },
  ],
  'hmw-forest': [
    { id: 'rock', tiles: ['grass', 'clearing'], density: 1.2, minSpacing: 3 },
    { id: 'bush', tiles: ['grass'], density: 2.5, minSpacing: 2 },
    { id: 'firefly-swarm', tiles: ['clearing', 'grass'], count: 6, minSpacing: 6 },
  ],
};
