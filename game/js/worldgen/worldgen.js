// worldgen.js — entry point for Western Heart procedural world generation.
//
// TRACK 5 (2026-10-23): WaveFunctionCollapse layouts + FastNoise terrain,
// wired for (a) NEW arena surroundings and (b) Heart-and-Mind-Within open
// zones. Generates nothing over existing arenas — see the arena law in
// docs/research/WORLD-GENERATION-2026-10-23.md.
//
// Usage (browser, as a module):
//   import { generateZone } from './js/worldgen/worldgen.js';
//   const zone = generateZone({ kind: 'temple-courtyard', seed: 1337 });
//   // zone.layout.names[y][x] -> tile id per cell
//   // zone.heightmap.data      -> Float32Array heights
//   // zone.props               -> [{ id, x, y, h, rot }]
//
// Usage (node): same import path from tools/worldgen/generate.mjs.
import { generateLayout } from './wfc.js';
import { sampleHeightmap, classifyBiomes, sampleCaveMask } from './terrain.js';
import { scatterProps, PROP_SETS } from './props.js';

// Rule sets are JSON so artists can edit them without touching code.
import templeCourtyard from './rulesets/temple-courtyard.json' with { type: 'json' };
import hmwForest from './rulesets/hmw-forest.json' with { type: 'json' };

export const RULESETS = {
  'temple-courtyard': templeCourtyard,
  'hmw-forest': hmwForest,
};

// Per-kind generation profiles: which systems run and at what size.
// Sizes are mobile budgets first (see docs/research/WORLD-GENERATION-2026-10-23.md).
export const ZONE_PROFILES = {
  'temple-courtyard': {
    ruleset: 'temple-courtyard',
    layoutW: 40, layoutH: 28,
    terrainW: 80, terrainH: 56,
    terrainLayers: ['courtyardBase', 'detail'],
    flatten: { radius: 14, to: 0 }, // keep the fight floor level
    biomes: true, caves: false,
    props: 'temple-courtyard',
  },
  'hmw-forest': {
    ruleset: 'hmw-forest',
    layoutW: 48, layoutH: 48,
    terrainW: 96, terrainH: 96,
    terrainLayers: ['hmwHills', 'detail'],
    flatten: null,
    biomes: true, caves: true,
    props: 'hmw-forest',
  },
};

/**
 * Generate a complete zone. Deterministic for a fixed { kind, seed }.
 *
 * @param {object} opts { kind, seed, profile overrides... }
 * @returns {object} { kind, seed, layout, heightmap, biomes, caveMask, props, meta }
 */
export function generateZone(opts = {}) {
  const kind = opts.kind || 'temple-courtyard';
  const seed = opts.seed == null ? 1337 : opts.seed;
  const profile = { ...(ZONE_PROFILES[kind] || ZONE_PROFILES['temple-courtyard']), ...opts.profile };
  const t0 = (typeof performance !== 'undefined' ? performance : Date).now();

  const ruleset = RULESETS[profile.ruleset];
  const layout = generateLayout(ruleset, {
    width: profile.layoutW, height: profile.layoutH, seed,
    maxAttempts: opts.maxAttempts || 12,
  });

  const heightmap = sampleHeightmap({
    width: profile.terrainW, height: profile.terrainH, seed: seed ^ 0x9e37,
    layers: profile.terrainLayers,
    flatten: profile.flatten ? {
      radius: profile.flatten.radius, to: profile.flatten.to,
      cx: profile.terrainW / 2, cy: profile.terrainH / 2,
    } : null,
  });

  const biomes = profile.biomes ? classifyBiomes(heightmap) : null;
  const caveMask = profile.caves
    ? sampleCaveMask({ width: profile.terrainW, height: profile.terrainH, seed: seed ^ 0x51f2 })
    : null;

  const props = scatterProps({
    seed: seed ^ 0xabcd,
    // NOTE: layout grid and heightmap grid differ in resolution; props use the
    // layout grid for tile rules. Height lookup is skipped when grids differ
    // (h=0) — callers sampling the real mesh should re-project.
    layout, heightmap: null,
    defs: PROP_SETS[profile.props] || [],
  });

  const t1 = (typeof performance !== 'undefined' ? performance : Date).now();
  return {
    kind, seed, layout, heightmap, biomes, caveMask, props,
    meta: {
      generatedMs: t1 - t0,
      layoutSuccess: layout.success,
      layoutAttempts: layout.attempts,
      terrainMin: heightmap.min, terrainMax: heightmap.max,
    },
  };
}

// Browser global for non-module callers / debugging.
if (typeof window !== 'undefined') {
  window.WH_WorldGen = { generateZone, RULESETS, ZONE_PROFILES };
}
