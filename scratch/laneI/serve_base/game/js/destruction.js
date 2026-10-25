/* ============================================================
   WESTERN HEART — Procedural arena destruction (Voronoi fracture)

   Pulled from: voro++ (Chris H. Rycroft, LBL — BSD 3-clause, see
   game/vendor/voropp/). voro++ computes each Voronoi cell INDIVIDUALLY
   by carving a bounding box with a sequence of plane cuts — one
   perpendicular-bisector plane per neighboring particle. This module
   is an original dependency-free JavaScript implementation of that
   same cell-by-plane-cuts algorithm, specialized to 2D surface
   fracture (walls / floors), plus shard ballistics.

   Pure math: no THREE, no DOM. Runs in node --test unchanged.

   Where it wires in (Foundation Law: Tekken is the base):
   game/js/stagebreaks.js — T7/TTT2 wall, floor and balcony breaks.
   Breakable surfaces register here; hits accumulate damage; when a
   surface's hp hits zero it FRACTURES into Voronoi shards instead of
   vanishing. The caller owns rendering (it maps the surface-local
   frames below into world space).

   Surface-local frames (canonical):
     wall  — plane is XY (x = along wall, y = up), extruded ±depth/2
             along Z (the wall normal). Gravity local: (0,-G,0).
             Shards rest at local y >= 0 (arena floor).
     floor — plane is XY too; the caller mounts it with rotation.x =
             -PI/2 so local (x,y) -> world (x,-z) and local +Z -> world
             +Y. Gravity local: (0,0,-G). Shards rest at
             local z >= -fallDepth (the level below the break).
   ============================================================ */

export const DESTRUCTION_VERSION = '1.0.0';
export const GRAVITY = 18; // world units/s^2 — matches stagebreaks debris

/* ---------- seeded RNG (deterministic fractures for tests) ---------- */

export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/* ---------- polygon helpers ---------- */

export function polygonArea(poly) {
  let a = 0;
  for (let i = 0; i < poly.length; i++) {
    const [x1, y1] = poly[i], [x2, y2] = poly[(i + 1) % poly.length];
    a += x1 * y2 - x2 * y1;
  }
  return Math.abs(a) / 2;
}

export function polygonCentroid(poly) {
  let cx = 0, cy = 0, a = 0;
  for (let i = 0; i < poly.length; i++) {
    const [x1, y1] = poly[i], [x2, y2] = poly[(i + 1) % poly.length];
    const f = x1 * y2 - x2 * y1;
    a += f; cx += (x1 + x2) * f; cy += (y1 + y2) * f;
  }
  a /= 2;
  if (Math.abs(a) < 1e-9) { // degenerate: fall back to vertex average
    let sx = 0, sy = 0;
    for (const [x, y] of poly) { sx += x; sy += y; }
    return { x: sx / poly.length, y: sy / poly.length };
  }
  return { x: cx / (6 * a), y: cy / (6 * a) };
}

/**
 * Clip a convex polygon by the half-plane dot(n, p) <= c.
 * Sutherland–Hodgman — the 2D analogue of voro++'s plane() cut.
 */
export function clipHalfPlane(poly, nx, ny, c) {
  const out = [];
  const n = poly.length;
  if (!n) return out;
  for (let i = 0; i < n; i++) {
    const p = poly[i], q = poly[(i + 1) % n];
    const dp = nx * p[0] + ny * p[1] - c;
    const dq = nx * q[0] + ny * q[1] - c;
    if (dp <= 1e-9) out.push(p);
    if ((dp < -1e-9 && dq > 1e-9) || (dp > 1e-9 && dq < -1e-9)) {
      const t = dp / (dp - dq);
      out.push([p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t]);
    }
  }
  return out;
}

/* ---------- Voronoi: voro++ cell-by-plane-cuts, in 2D ---------- */

/**
 * Compute the Voronoi cell of EVERY seed individually: start from the
 * bounds rectangle, cut by the perpendicular bisector against each
 * other seed. (voro++ does exactly this in 3D with plane cuts.)
 * bounds: {x0, y0, x1, y1}; seeds: [{x, y}, ...]
 * Returns [{seed, poly: [[x,y],...]}, ...] — poly may be [] if a seed
 * is fully dominated (duplicate seeds).
 */
export function voronoiCells(bounds, seeds) {
  const { x0, y0, x1, y1 } = bounds;
  return seeds.map((s, i) => {
    let poly = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]];
    for (let j = 0; j < seeds.length; j++) {
      if (j === i) continue;
      const o = seeds[j];
      // bisector of s and o: dot(o - s, p) <= (|o|^2 - |s|^2) / 2
      const nx = o.x - s.x, ny = o.y - s.y;
      if (Math.abs(nx) < 1e-12 && Math.abs(ny) < 1e-12) continue; // duplicate seed
      const c = (o.x * o.x + o.y * o.y - s.x * s.x - s.y * s.y) / 2;
      poly = clipHalfPlane(poly, nx, ny, c);
      if (!poly.length) break;
    }
    return { seed: s, poly };
  });
}

/** Lloyd relaxation: re-seed at cell centroids — organic shard shapes. */
export function lloydRelax(bounds, seeds, iters = 2) {
  let cur = seeds.map((s) => ({ x: s.x, y: s.y }));
  for (let k = 0; k < iters; k++) {
    const cells = voronoiCells(bounds, cur);
    cur = cells.map((cell) => {
      if (!cell.poly.length) return { x: cell.seed.x, y: cell.seed.y };
      const c = polygonCentroid(cell.poly);
      return { x: c.x, y: c.y };
    });
  }
  return cur;
}

function _placeSeeds(bounds, count, impact, rng) {
  const { x0, y0, x1, y1 } = bounds;
  const seeds = [];
  const minD = Math.min(x1 - x0, y1 - y0) / Math.sqrt(count) * 0.35;
  let guard = 0;
  while (seeds.length < count && guard++ < count * 60) {
    let x, y;
    if (impact && rng() < 0.45) {
      // concentrate near the impact point: denser shards at the hit
      const a = rng() * Math.PI * 2;
      const r = Math.pow(rng(), 0.6) * Math.min(x1 - x0, y1 - y0) * 0.45;
      x = impact.x + Math.cos(a) * r;
      y = impact.y + Math.sin(a) * r;
    } else {
      x = x0 + rng() * (x1 - x0);
      y = y0 + rng() * (y1 - y0);
    }
    if (x < x0 || x > x1 || y < y0 || y > y1) continue;
    if (seeds.some((s) => Math.hypot(s.x - x, s.y - y) < minD)) continue;
    seeds.push({ x, y });
  }
  while (seeds.length < count) { // fallback: fill anywhere valid
    seeds.push({ x: x0 + rng() * (x1 - x0), y: y0 + rng() * (y1 - y0) });
  }
  return seeds;
}

/**
 * Fracture a w×h rectangle into Voronoi shards.
 * impact: {x, y} local point of the hit (denser shards + radial velocities).
 * Returns [{poly, centroid, area, dist}] with dist = distance of the
 * shard centroid from impact (0 when no impact given).
 */
export function fractureRect({ w, h, cells = 24, impact = null, seed = 1, relaxIters = 2, rng = null }) {
  const rand = rng || mulberry32(seed);
  const bounds = { x0: -w / 2, y0: -h / 2, x1: w / 2, y1: h / 2 };
  let seeds = _placeSeeds(bounds, cells, impact, rand);
  if (relaxIters > 0) seeds = lloydRelax(bounds, seeds, relaxIters);
  const vor = voronoiCells(bounds, seeds).filter((c) => c.poly.length >= 3);
  const total = w * h;
  return vor.map((c) => {
    const centroid = polygonCentroid(c.poly);
    const area = polygonArea(c.poly);
    return {
      poly: c.poly,
      centroid,
      area,
      areaFrac: area / total,
      dist: impact ? Math.hypot(centroid.x - impact.x, centroid.y - impact.y) : 0,
    };
  });
}

/* ---------- DestructionSystem: surfaces, damage, shard ballistics ---------- */

const _WALL_DEFAULTS = { hp: 100, cells: 26, depth: 0.28, gravity: [0, -GRAVITY, 0], restAxis: 'y', restAt: 0 };
const _FLOOR_DEFAULTS = { hp: 100, cells: 22, depth: 0.25, gravity: [0, 0, -GRAVITY], restAxis: 'z', restAt: null /* -fallDepth */ };

export class DestructionSystem {
  /**
   * opts.rng: () => [0,1) — inject for deterministic tests. Each
   * fracture draws a fresh seed from it.
   */
  constructor(opts = {}) {
    this._rng = opts.rng || Math.random;
    this.surfaces = new Map(); // id -> surface record
    this.live = [];            // live shards across all fractures
    this.lastFracture = null;  // {surfaceId, shards} of the most recent break
    this.fractureCount = 0;
  }

  /**
   * Register a breakable surface.
   * {id, kind: 'wall'|'floor', w, h, depth, hp, cells, seed,
   *  fallDepth} — fallDepth only for floors (how far shards drop).
   */
  registerSurface(def) {
    const d = def.kind === 'floor' ? _FLOOR_DEFAULTS : _WALL_DEFAULTS;
    const rec = {
      id: def.id,
      kind: def.kind,
      w: def.w, h: def.h,
      depth: def.depth ?? d.depth,
      hp: def.hp ?? d.hp,
      maxHp: def.hp ?? d.hp,
      cells: def.cells ?? d.cells,
      seed: def.seed ?? Math.floor(this._rng() * 1e9),
      fallDepth: def.fallDepth ?? 6,
      gravity: def.gravity || d.gravity,
      restAxis: def.restAxis || d.restAxis,
      restAt: def.restAt ?? (def.kind === 'floor' ? -(def.fallDepth ?? 6) : d.restAt),
      damage: 0,
      fractured: false,
    };
    this.surfaces.set(def.id, rec);
    return rec;
  }

  /** progress 0..1 — arena code can drive a crack overlay from this. */
  progress(id) {
    const s = this.surfaces.get(id);
    if (!s) return 0;
    return s.fractured ? 1 : Math.min(1, s.damage / s.maxHp);
  }

  /**
   * Apply damage at a surface-local point. Returns
   * {fractured, progress, shards?} — shards only on the fracturing hit.
   */
  damage(id, amount, point = null) {
    const s = this.surfaces.get(id);
    if (!s || s.fractured) return { fractured: false, progress: this.progress(id) };
    s.damage += amount;
    if (s.damage < s.maxHp) return { fractured: false, progress: this.progress(id) };
    s.fractured = true;
    const shards = this._fracture(s, point);
    this.lastFracture = { surfaceId: id, shards };
    this.fractureCount++;
    return { fractured: true, progress: 1, shards };
  }

  _fracture(s, point) {
    const seed = Math.floor(this._rng() * 1e9) + s.seed;
    const frags = fractureRect({
      w: s.w, h: s.h, cells: s.cells,
      impact: point, seed, relaxIters: 2,
    });
    const maxDist = Math.max(0.001, Math.hypot(s.w, s.h) / 2);
    const g = s.gravity;
    const shards = frags.map((f, i) => {
      // radial burst away from impact, faster near the hit; plus pop
      const dx = f.centroid.x - (point ? point.x : 0);
      const dy = f.centroid.y - (point ? point.y : 0);
      const dl = Math.max(0.15, Math.hypot(dx, dy));
      const speed = 2.2 + 5.5 * (1 - Math.min(1, f.dist / maxDist));
      const shard = {
        id: `${s.id}#${i}`,
        surfaceId: s.id,
        kind: s.kind,
        poly: f.poly,                 // surface-local 2D polygon
        depth: s.depth,
        area: f.area,
        dist: f.dist,                 // centroid distance from impact (heat)
        mass: Math.max(0.05, f.areaFrac),
        pos: { x: f.centroid.x, y: f.centroid.y, z: 0 },
        vel: {
          x: (dx / dl) * speed + (this._rng() - 0.5) * 1.6,
          y: (dy / dl) * speed + 1.5 + this._rng() * 2.5,
          z: (this._rng() - 0.3) * 4.5,   // pop out of the surface plane
        },
        rot: { x: (this._rng() - 0.5) * 0.6, y: (this._rng() - 0.5) * 0.6, z: this._rng() * Math.PI * 2 },
        spin: { x: (this._rng() - 0.5) * 9, y: (this._rng() - 0.5) * 9, z: (this._rng() - 0.5) * 9 },
        life: 2.2 + this._rng() * 1.2,
        maxLife: 3.4,
        gravity: { x: g[0], y: g[1], z: g[2] },
        restAxis: s.restAxis,
        restAt: s.restAt,
        settled: false,
      };
      this.live.push(shard);
      return shard;
    });
    return shards;
  }

  /**
   * Integrate live shards. Returns the live array (same objects the
   * renderer holds) — settled/dead shards are flagged, not removed;
   * the caller drops meshes when shard.life <= 0.
   */
  step(dt) {
    const dtc = Math.min(dt, 1 / 20);
    for (const sh of this.live) {
      if (sh.life <= 0) continue;
      sh.life -= dtc;
      if (!sh.settled) {
        sh.vel.x += sh.gravity.x * dtc;
        sh.vel.y += sh.gravity.y * dtc;
        sh.vel.z += sh.gravity.z * dtc;
        sh.pos.x += sh.vel.x * dtc;
        sh.pos.y += sh.vel.y * dtc;
        sh.pos.z += sh.vel.z * dtc;
        sh.rot.x += sh.spin.x * dtc;
        sh.rot.y += sh.spin.y * dtc;
        sh.rot.z += sh.spin.z * dtc;
        const p = sh.pos[sh.restAxis];
        const falling = sh.vel[sh.restAxis] < 0;
        if (falling && p <= sh.restAt) {
          sh.pos[sh.restAxis] = sh.restAt;
          sh.vel.x = sh.vel.y = sh.vel.z = 0;
          sh.spin.x = sh.spin.y = sh.spin.z = 0;
          sh.settled = true;
        }
      }
    }
    // prune the fully dead from the live list (renderer already dropped them)
    this.live = this.live.filter((sh) => sh.life > 0);
    return this.live;
  }

  reset() {
    this.surfaces.clear();
    this.live = [];
    this.lastFracture = null;
    this.fractureCount = 0;
  }
}
