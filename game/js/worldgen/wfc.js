// wfc.js — Wave Function Collapse layout generation for Western Heart.
//
// Generates 2D tile layouts (arena surroundings, Heart-and-Mind-Within zone
// structure) from human-authored rule sets. Rule sets live in
// game/js/worldgen/rulesets/*.json and use a compact, hand-editable schema;
// this module converts them to the vendored WFC library's format.
//
// Vendored engine: game/js/worldgen/vendor/wfc.bundle.mjs
// (wavefunctioncollapse 2.1.0, MIT — port of mxgmn/WaveFunctionCollapse, MIT).
//
// Arena law: this generates NEW layouts (surroundings / HMW zones). It never
// touches existing arenas' canon look.
//
// No DOM. Safe to import in node and in the browser.
import { WFC } from './vendor/wfc.bundle.mjs';
import { mulberry32 } from './seeded-rng.js';

// Symmetry -> number of oriented variants (must match the vendored lib).
function cardinality(symmetry) {
  switch (symmetry) {
    case 'L': case 'T': return 4;
    case 'I': case '\\': return 2;
    case 'F': return 8;
    default: return 1; // 'X' and anything else
  }
}

// ---- bitmap rasterization -----------------------------------------------
// The vendored lib needs a tilesize x tilesize RGBA bitmap per tile. Rule sets
// only carry a base color + pattern name; we rasterize here so rule sets stay
// human-editable. The lib rotates/reflects the base bitmap for oriented
// variants itself.

function shade([r, g, b], f) {
  return [Math.max(0, Math.min(255, Math.round(r * f))),
          Math.max(0, Math.min(255, Math.round(g * f))),
          Math.max(0, Math.min(255, Math.round(b * f)))];
}

function rasterizeTile(color, pattern, tilesize) {
  const px = new Array(tilesize * tilesize * 4);
  const dark = shade(color, 0.72);
  const light = shade(color, 1.18);
  const put = (x, y, c) => {
    const i = (y * tilesize + x) * 4;
    px[i] = c[0]; px[i + 1] = c[1]; px[i + 2] = c[2]; px[i + 3] = 255;
  };
  for (let y = 0; y < tilesize; y++) {
    for (let x = 0; x < tilesize; x++) {
      let c = color;
      const bx = Math.floor((x / tilesize) * 4);
      const by = Math.floor((y / tilesize) * 4);
      switch (pattern) {
        case 'checker':
          c = ((bx + by) % 2 === 0) ? color : dark;
          break;
        case 'border':
          c = (bx === 0 || by === 0 || bx === 3 || by === 3) ? dark : color;
          break;
        case 'cross':
          c = (bx === 1 || bx === 2 || by === 1 || by === 2) ? light : color;
          break;
        case 'dots':
          c = (bx % 2 === 0 && by % 2 === 0) ? light : color;
          break;
        case 'circle': {
          const dx = x / tilesize - 0.5, dy = y / tilesize - 0.5;
          c = (dx * dx + dy * dy < 0.14) ? light : dark;
          break;
        }
        case 'diag':
          c = ((x + y) % 4 < 2) ? color : dark;
          break;
        case 'solid':
        default:
          c = color;
      }
      put(x, y, c);
    }
  }
  // The lib reads bitmap[(tilesize*y + x) * 4 + channel]: flat RGBA.
  return px;
}

// ---- rule set conversion ------------------------------------------------
//
// Rule sets declare per-tile edge SOCKETS (4 chars: top,right,bottom,left).
// The converter expands each tile into explicit oriented variants (one
// X-symmetry tile per orientation) and emits every edge-compatible pair.
//
// WHY X-EXPANSION (not the lib's native L/T symmetries):
// The vendored lib's neighbor expansion applies D4 symmetries. For L/T
// tiles its reflection entries do not correspond to geometric reflections,
// which corrupts the propagator (measured 2026-10-23: 32% of generated
// adjacencies geometrically invalid). Expanding to explicit X variants
// sidesteps this entirely.
//
// The lib DOES apply a closure to X tiles: for each emitted (A left-of B)
// it also allows the reverse (B left-of A) and the vertical (A below B).
// This is original WFC behavior (verified against mxgmn's C# source).
// Consequences, all artistically acceptable for our use:
//   - A path/wall arm may end against ground (natural path-ends, wall-ends).
//   - Horizontal connector sockets ALWAYS match (the emitted pairs are exact).
// Strict 100% socket-matching is intentionally not required; what matters is
// that layouts are coherent, which the demos prove (see tools/worldgen/demo).
//
//   edges: "fpfp"  -> top/bottom open ground (f), right/left path (p)
//   socket ids are arbitrary single chars; compatibility is exact match.

// Rotate edges k*90deg counter-clockwise (matches lib's bitmap rotate()).
function orientedEdges(base, k) {
  return [0, 1, 2, 3].map((i) => base[(i + k) % 4]);
}

function orientedName(name, k) {
  return k === 0 ? name : `${name} ${k}`;
}

// Rotate a flat RGBA bitmap (tilesize x tilesize) 90deg CCW, k times.
// Used so each X variant carries its correctly-oriented bitmap (the lib does
// not transform X bitmaps itself, so graphics() stays truthful).
function rotateBitmap(px, tilesize, k) {
  let cur = px;
  for (let r = 0; r < ((k % 4) + 4) % 4; r++) {
    const nxt = new Array(cur.length);
    for (let y = 0; y < tilesize; y++) {
      for (let x = 0; x < tilesize; x++) {
        // lib: rotated(x, y) = original(tilesize-1-y, x).
        const si = (y * tilesize + x) * 4;
        const di = (y * tilesize + (tilesize - 1 - x)) * 4;
        nxt[di] = cur[si]; nxt[di + 1] = cur[si + 1];
        nxt[di + 2] = cur[si + 2]; nxt[di + 3] = cur[si + 3];
      }
    }
    cur = nxt;
  }
  return cur;
}

// Expand to explicit oriented X variants. Returns list of:
// { name (unique), baseName, orientation k, edges[4], weight, bitmap }
function expandTiles(ruleset) {
  const tilesize = ruleset.tilesize || 8;
  const out = [];
  for (const t of ruleset.tiles) {
    const c = cardinality(t.symmetry || 'X');
    const base = (t.edges || 'ffff').split('');
    const bitmap = rasterizeTile(t.color || [128, 128, 128], t.pattern || 'solid', tilesize);
    const weight = (t.weight == null ? 1 : t.weight) / c; // preserve total mass
    for (let k = 0; k < c; k++) {
      out.push({
        name: c === 1 ? t.name : `${t.name}__o${k}`,
        baseName: t.name,
        orientation: k,
        edges: orientedEdges(base, k),
        weight,
        bitmap: rotateBitmap(bitmap, tilesize, k),
      });
    }
  }
  return out;
}

function expandNeighbors(expanded) {
  const out = [];
  const seen = new Set();
  for (const a of expanded) {
    for (const b of expanded) {
      if (a.edges[1] === b.edges[3]) { // a.right touches b.left
        const key = a.name + '|' + b.name;
        if (!seen.has(key)) {
          seen.add(key);
          out.push({ left: a.name, right: b.name });
        }
      }
    }
  }
  return out;
}

function toLibFormat(ruleset) {
  const tilesize = ruleset.tilesize || 8;
  const expanded = expandTiles(ruleset);
  return {
    tilesize,
    unique: false,
    // All X: the lib's per-tile symmetry expansion is a no-op; the only
    // closure applied is the documented reverse+vertical (see above).
    tiles: expanded.map((t) => ({
      name: t.name,
      symmetry: 'X',
      weight: t.weight,
      bitmap: t.bitmap,
    })),
    neighbors: expandNeighbors(expanded),
    subsets: ruleset.subsets || undefined,
    _expanded: expanded, // carried for the name table; stripped before use
  };
}

// Build the observed-index -> { baseName, orientation } table.
function buildNameTable(expanded) {
  return expanded.map((t) => ({ base: t.baseName, k: t.orientation }));
}

// ---- public API ----------------------------------------------------------

/**
 * Generate a tile layout from a rule set.
 *
 * @param {object} ruleset  parsed ruleset JSON (see rulesets/*.json)
 * @param {object} opts     { width, height, seed, subset, maxAttempts }
 * @returns {object} { names, oriented, width, height, seed, attempts,
 *                     success, tileset }
 *   names:    height rows of base tile names (what game code consumes)
 *   oriented: height rows of oriented tile ids ("name k") for debugging.
 *             Orientation k = k * 90deg CCW rotation of the base tile.
 *             (For 3D prop placement: rotate the base prop mesh by k*90 CCW.)
 */
export function generateLayout(ruleset, opts = {}) {
  const width = opts.width || 40;
  const height = opts.height || 28;
  const seed = opts.seed == null ? Date.now() : opts.seed;
  const maxAttempts = opts.maxAttempts || 12;

  const libData = toLibFormat(ruleset);
  const expanded = libData._expanded;
  delete libData._expanded;
  const nameTable = buildNameTable(expanded);
  const baseNames = ruleset.tiles.map((t) => t.name);

  let attempts = 0;
  let success = false;
  let observed = null;

  while (attempts < maxAttempts && !success) {
    attempts++;
    const model = new WFC.SimpleTiledModel(libData, opts.subset || null, width, height, false);
    // Fresh seeded stream per attempt so retries explore different collapses.
    success = model.generate(mulberry32(seed + attempts * 7919));
    if (success) observed = model.observed;
  }

  const names = [];
  const oriented = [];
  for (let y = 0; y < height; y++) {
    const rowN = new Array(width).fill(null);
    const rowO = new Array(width).fill(null);
    if (observed) {
      for (let x = 0; x < width; x++) {
        const idx = observed[x + y * width];
        const entry = nameTable[idx] || { base: '?', k: 0 };
        rowO[x] = orientedName(entry.base, entry.k);
        rowN[x] = entry.base;
      }
    }
    names.push(rowN);
    oriented.push(rowO);
  }

  return {
    names, oriented, width, height, seed, attempts, success,
    tileset: baseNames,
    ruleset: ruleset.name || 'unnamed',
  };
}

/**
 * Count tile usage in a generated layout (quick sanity / art-direction check).
 */
export function tileHistogram(layout) {
  const h = {};
  for (const row of layout.names) {
    for (const n of row) {
      if (n == null) continue;
      h[n] = (h[n] || 0) + 1;
    }
  }
  return h;
}

// Test/debug access to the rule-set conversion (used by test/worldgen.test.mjs).
export const _debug = { expandTiles, expandNeighbors, toLibFormat, cardinality, orientedEdges };
