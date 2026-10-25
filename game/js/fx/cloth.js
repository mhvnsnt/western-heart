/* ============================================================
   WESTERN HEART — WHCloth (XPBD cloth engine, CPU backend)

   Algorithm + design ported from jspdown/cloth
   (MIT License, Copyright (c) 2023 Harold Ozouf,
   https://github.com/jspdown/cloth):
     • XPBD (Macklin, Müller, Chentanez 2016) distance constraints
       with compliance (controllable fabric stiffness)
     • "Small steps" sub-stepping (Macklin et al. 2019) for stability
     • Graph-colored parallel Gauss-Seidel constraint solving
     • Stretch constraints from mesh edges, bend constraints from
       adjacent-triangle pairs, particle mass from triangle areas

   Reference implementations consulted (see
   docs/research/CLOTH-EVALUATION-2026-10-23.md):
     • openxrlab/XRTailor (Apache 2.0) — real-time parameter guidance
     • vitalight/Velvet (MIT) — attach / long-range-attachment ideas

   Backend note: this module ships the CPU backend. The game renders
   with Three.js WebGL (Effekseer shares the WebGL context) and the
   target phones cannot be assumed WebGPU-capable, so cloth positions
   must live on the CPU to feed BufferGeometry attributes every frame
   anyway. Constraint color groups are preserved in the solve order, so
   a future WebGPU backend can dispatch one compute pass per color
   group using jspdown/cloth's WGSL shaders verbatim
   (src/physic/shaders/*.compute.wgsl); only the buffer plumbing would
   be new. Cape/hair/costume particle counts (hundreds to low
   thousands) run at 60fps on the CPU backend — see quality table.

   Conventions (matches game/js/fx/particles.js):
     • No top-level imports (no three.js, no DOM): safe to import in
       node for unit tests. All rendering work happens through the
       writePositions() adapter, which only needs a position attribute
       with setXYZ() (or a raw Float32Array).
     • Quality levels with device auto-detect + localStorage override
       ('wh-cloth-quality'), particle budgets, distance LOD sleep.

   Wiring: costume capes / skirts / sashes / hair attach through
   game/js/cloth-hair.js (autoAttachCloth), which builds on this
   engine. Mesh-based costume pieces use buildFromMesh() so intake
   costume geometry simulates directly instead of generated grids.

   ALL CHARACTERS ARE ADULTS (owner law) — cloth attaches to adult
   fighter costume meshes only.
   ============================================================ */

/* ---------- quality levels (mirrors fx/particles.js) ---------- */
export const CLOTH_QUALITY = {
  low:    { substeps: 4,  maxParticles: 600,  label: 'low' },
  medium: { substeps: 8,  maxParticles: 1500, label: 'medium' },
  high:   { substeps: 12, maxParticles: 3000, label: 'high' },
};
export const CLOTH_LOD_DIST = 14; // beyond this, systems sleep

/** Quality pick: stored override, else device heuristics (phone-safe). */
export function detectClothQuality(env) {
  const e = env || {};
  try {
    const stored = e.localStorage && e.localStorage.getItem('wh-cloth-quality');
    if (stored && CLOTH_QUALITY[stored]) return stored;
    const ua = (e.navigator && e.navigator.userAgent) || '';
    const cores = (e.navigator && e.navigator.hardwareConcurrency) || 4;
    const mobile = /Android|iPhone|iPad|iPod|Mobile/i.test(ua);
    if (mobile || cores <= 4) return 'low';
    return 'medium';
  } catch (err) { return 'medium'; }
}

/* ---------- fabric presets ----------
   stretchCompliance / bendCompliance follow jspdown/cloth's units:
   0 = rigid, larger = softer (XPBD alpha). bend is the adjacent-
   triangle hinge constraint; hair chains use bend to keep strands
   from kinking. damping is an explicit velocity damp per substep. */
export const FABRICS = {
  silk:    { stretchCompliance: 0.0,  bendCompliance: 0.60, damping: 0.995, density: 0.10 },
  cotton:  { stretchCompliance: 0.0,  bendCompliance: 0.30, damping: 0.99,  density: 0.15 },
  denim:   { stretchCompliance: 0.0,  bendCompliance: 0.12, damping: 0.985, density: 0.30 },
  leather: { stretchCompliance: 0.0,  bendCompliance: 0.04, damping: 0.98,  density: 0.60 },
  cape:    { stretchCompliance: 0.0,  bendCompliance: 0.18, damping: 0.99,  density: 0.20 },
  hair:    { stretchCompliance: 0.0,  bendCompliance: 0.02, damping: 0.985, density: 0.05 },
};

/* ============================================================
   XPBDSolver — the engine.
   State: positions / velocities / estimated positions /
   inverse masses, all typed arrays, zero per-frame allocation.
   Constraints are reordered by greedy graph color at finalize()
   so each color group is particle-disjoint (parallel-safe on GPU,
   deterministic cache-friendly order on CPU).
   ============================================================ */
const MAX_COLORS = 64;

export class XPBDSolver {
  constructor(maxParticles, opts = {}) {
    const n = Math.max(1, Math.floor(maxParticles));
    this.maxParticles = n;
    this.pos = new Float32Array(n * 3);      // current positions
    this.vel = new Float32Array(n * 3);      // velocities
    this.est = new Float32Array(n * 3);      // estimated positions (substep scratch)
    this.invMass = new Float32Array(n);      // 0 = pinned
    this.count = 0;
    // constraints (structure-of-arrays, reordered by color at finalize)
    this.cA = []; this.cB = [];             // particle index pairs (temp lists)
    this.cRest = []; this.cAlpha = [];
    this.ca = null; this.cb = null;          // Int32Array, color-ordered
    this.crest = null; this.calpha = null;   // Float32Array, color-ordered
    this.colorStarts = null; this.colorCounts = null;
    this.colorCount = 0;
    this.constraintCount = 0;
    this.gravity = opts.gravity !== undefined ? opts.gravity : -9.8;
    this.damping = opts.damping !== undefined ? opts.damping : 0.99;
    this.substeps = opts.substeps || 8;
    this.wind = { x: 0, y: 0, z: 0, t: 0 };
    this._finalized = false;
    this._push = new Float32Array(n * 3); // per-substep contact push vectors
  }

  addParticle(x, y, z, invMass = 1) {
    if (this.count >= this.maxParticles) throw new Error('cloth: particle budget exceeded');
    const i = this.count++;
    this.pos[i*3] = x; this.pos[i*3+1] = y; this.pos[i*3+2] = z;
    this.invMass[i] = invMass;
    this._finalized = false;
    return i;
  }

  /** rest < 0 → measured from current positions. alpha = XPBD compliance. */
  addConstraint(a, b, alpha = 0, rest = -1) {
    if (rest < 0) {
      const dx = this.pos[b*3]-this.pos[a*3];
      const dy = this.pos[b*3+1]-this.pos[a*3+1];
      const dz = this.pos[b*3+2]-this.pos[a*3+2];
      rest = Math.sqrt(dx*dx + dy*dy + dz*dz);
    }
    this.cA.push(a); this.cB.push(b); this.cRest.push(rest); this.cAlpha.push(alpha);
    this._finalized = false;
    return this.cA.length - 1;
  }

  /** Pin a particle to a moving anchor (e.g. hair root on head bone). */
  pinTo(i, x, y, z) {
    const ix = i*3;
    this.pos[ix] = x; this.pos[ix+1] = y; this.pos[ix+2] = z;
    this.vel[ix] = 0; this.vel[ix+1] = 0; this.vel[ix+2] = 0;
  }

  /** Greedy graph coloring; reorders constraints so each color group
      shares no particle (jspdown/cloth constraints.ts color()). */
  finalize() {
    const m = this.cA.length;
    const A = new Int32Array(m), B = new Int32Array(m);
    const R = new Float32Array(m), Al = new Float32Array(m);
    for (let i = 0; i < m; i++) { A[i] = this.cA[i]; B[i] = this.cB[i]; R[i] = this.cRest[i]; Al[i] = this.cAlpha[i]; }
    const markedC = new Uint8Array(m);
    const markedP = new Uint8Array(this.count);
    const order = new Int32Array(m);
    const starts = [], counts = [];
    let remaining = m, colorCount = 0, oi = 0;
    while (remaining > 0) {
      if (colorCount >= MAX_COLORS) throw new Error('cloth: max colors reached');
      markedP.fill(0);
      const start = oi;
      for (let i = 0; i < m; i++) {
        if (markedC[i]) continue;
        const a = A[i], b = B[i];
        if (markedP[a] || markedP[b]) continue;
        order[oi++] = i;
        markedC[i] = 1; markedP[a] = 1; markedP[b] = 1;
        remaining--;
      }
      starts.push(start); counts.push(oi - start);
      colorCount++;
    }
    this.ca = new Int32Array(m); this.cb = new Int32Array(m);
    this.crest = new Float32Array(m); this.calpha = new Float32Array(m);
    for (let k = 0; k < m; k++) {
      const src = order[k];
      this.ca[k] = A[src]; this.cb[k] = B[src];
      this.crest[k] = R[src]; this.calpha[k] = Al[src];
    }
    this.colorStarts = starts; this.colorCounts = counts;
    this.colorCount = colorCount;
    this.constraintCount = m;
    this._finalized = true;
    return this;
  }

  _ensureFinalized() { if (!this._finalized) this.finalize(); }

  /** One frame: substeps of (integrate → solve colors → collide →
      commit). colliders: [{x,y,z,r}] spheres and
      [{x1,y1,z1,x2,y2,z2,r}] capsules. */
  step(dt, colliders = []) {
    this._ensureFinalized();
    const h = dt / this.substeps;
    for (let s = 0; s < this.substeps; s++) this._substep(h, colliders);
  }

  _substep(h, colliders) {
    const { pos, vel, est, invMass, count } = this;
    // wind gusts vary over time so cloth never looks frozen
    this.wind.t += h;
    const gust = 0.6 + 0.4 * Math.sin(this.wind.t * 2.1);
    const gust2 = 0.6 + 0.4 * Math.cos(this.wind.t * 1.7);
    const wx = this.wind.x * gust, wz = this.wind.z * gust2, wy = this.wind.y * gust;
    const g = this.gravity * h, damp = this.damping;
    for (let i = 0; i < count; i++) {
      if (invMass[i] === 0) { // pinned: estimated = current
        est[i*3] = pos[i*3]; est[i*3+1] = pos[i*3+1]; est[i*3+2] = pos[i*3+2];
        continue;
      }
      const ix = i*3;
      vel[ix]   = vel[ix]*damp + wx*h;
      vel[ix+1] = vel[ix+1]*damp + (g + wy*h);
      vel[ix+2] = vel[ix+2]*damp + wz*h;
      est[ix] = pos[ix] + vel[ix]*h;
      est[ix+1] = pos[ix+1] + vel[ix+1]*h;
      est[ix+2] = pos[ix+2] + vel[ix+2]*h;
    }
    this._solveColors(h);
    // Commit velocity from the solved (pre-contact) estimate, then
    // project out of colliders. Contact is fully inelastic for cloth:
    // _contactVelocity() removes the surface-normal velocity component
    // so resting contact neither gains energy (deep-spawn launch) nor
    // accumulates fall speed while pinned to a surface.
    const inv_h = 1 / h;
    for (let i = 0; i < count; i++) {
      if (invMass[i] === 0) continue;
      const ix = i*3;
      vel[ix]   = (est[ix]   - pos[ix])   * inv_h;
      vel[ix+1] = (est[ix+1] - pos[ix+1]) * inv_h;
      vel[ix+2] = (est[ix+2] - pos[ix+2]) * inv_h;
    }
    this._collide(colliders);
    this._contactVelocity();
    for (let i = 0; i < count; i++) {
      if (invMass[i] === 0) continue;
      const ix = i*3;
      pos[ix] = est[ix]; pos[ix+1] = est[ix+1]; pos[ix+2] = est[ix+2];
    }
  }

  /** XPBD distance-constraint projection per color group.
      Matches jspdown/cloth apply_constraint.compute.wgsl:
      alphaTilde = alpha/h²; dλ = -(d-rest)/(w1+w2+alphaTilde). */
  _solveColors(h) {
    const { est, invMass, ca, cb, crest, calpha } = this;
    const h2 = h * h;
    for (let c = 0; c < this.colorCount; c++) {
      const start = this.colorStarts[c], end = start + this.colorCounts[c];
      for (let k = start; k < end; k++) {
        const a = ca[k], b = cb[k];
        const w1 = invMass[a], w2 = invMass[b], wsum = w1 + w2;
        if (wsum <= 0) continue;
        const ax = a*3, bx = b*3;
        const dx = est[ax]-est[bx], dy = est[ax+1]-est[bx+1], dz = est[ax+2]-est[bx+2];
        const d = Math.sqrt(dx*dx + dy*dy + dz*dz);
        if (d < 1e-7) continue;
        const alphaTilde = calpha[k] / h2;
        const dl = -(d - crest[k]) / (wsum + alphaTilde);
        const s = dl / d;
        const cx = dx*s, cy = dy*s, cz = dz*s;
        est[ax] += cx*w1; est[ax+1] += cy*w1; est[ax+2] += cz*w1;
        est[bx] -= cx*w2; est[bx+1] -= cy*w2; est[bx+2] -= cz*w2;
      }
    }
  }

  _collide(colliders) {
    const { est, invMass, count, _push } = this;
    _push.fill(0);
    if (!colliders || colliders.length === 0) return;
    for (let n = 0; n < colliders.length; n++) {
      const c = colliders[n];
      if (c.r === undefined) continue;
      const isCapsule = c.x1 !== undefined;
      for (let i = 0; i < count; i++) {
        if (invMass[i] === 0) continue;
        const ix = i*3;
        const px = est[ix], py = est[ix+1], pz = est[ix+2];
        let cx, cy, cz;
        if (isCapsule) {
          // closest point on segment
          const abx = c.x2-c.x1, aby = c.y2-c.y1, abz = c.z2-c.z1;
          const t = Math.max(0, Math.min(1,
            ((px-c.x1)*abx + (py-c.y1)*aby + (pz-c.z1)*abz) /
            (abx*abx + aby*aby + abz*abz || 1e-9)));
          cx = c.x1 + abx*t; cy = c.y1 + aby*t; cz = c.z1 + abz*t;
        } else { cx = c.x; cy = c.y; cz = c.z; }
        const dx = px-cx, dy = py-cy, dz = pz-cz;
        const d2 = dx*dx + dy*dy + dz*dz, r = c.r;
        if (d2 < r*r && d2 > 1e-12) {
          const d = Math.sqrt(d2), push = (r - d) / d;
          const ox = dx*push, oy = dy*push, oz = dz*push;
          est[ix] = px + ox; est[ix+1] = py + oy; est[ix+2] = pz + oz;
          _push[ix] += ox; _push[ix+1] += oy; _push[ix+2] += oz;
        }
      }
    }
  }

  /** Inelastic contact: strip the surface-normal velocity component for
      every particle the colliders pushed, so cloth rests on bodies
      instead of bouncing or accumulating fall speed. Tangential
      (sliding) velocity is preserved. */
  _contactVelocity() {
    const { vel, invMass, count, _push } = this;
    for (let i = 0; i < count; i++) {
      if (invMass[i] === 0) continue;
      const ix = i*3;
      const px = _push[ix], py = _push[ix+1], pz = _push[ix+2];
      const l2 = px*px + py*py + pz*pz;
      if (l2 < 1e-18) continue;
      const l = Math.sqrt(l2), nx = px/l, ny = py/l, nz = pz/l;
      const vn = vel[ix]*nx + vel[ix+1]*ny + vel[ix+2]*nz;
      vel[ix] -= nx*vn; vel[ix+1] -= ny*vn; vel[ix+2] -= nz*vn;
    }
  }
}

/* ============================================================
   Topology — edges + adjacent-triangle pairs from an index list
   (ports jspdown/cloth triangles.ts extractTopology()).
   ============================================================ */
export function extractTopology(indices) {
  const triCount = Math.floor(indices.length / 3);
  const edges = [];
  const adj = []; // [triA, triB] pairs sharing an edge
  const edgeMap = new Map(); // "a_b" -> triangle id
  for (let t = 0; t < triCount; t++) {
    const v = [indices[t*3], indices[t*3+1], indices[t*3+2]].sort((x, y) => x - y);
    const pairs = [[v[0], v[1]], [v[0], v[2]], [v[1], v[2]]];
    for (const [a, b] of pairs) {
      const key = a + '_' + b;
      if (edgeMap.has(key)) adj.push([edgeMap.get(key), t]);
      else { edgeMap.set(key, t); edges.push([a, b]); }
    }
  }
  return { edges, adjacentTriangles: adj };
}

/* ============================================================
   Builders
   ============================================================ */

/** Grid sheet (capes, skirts, sashes, banners). Returns {solver, idx,
    cols, rows} with idx[r*cols+c] → particle. Pin via pinTest or
    pinTop/pinLeft/pinRight/pinBottom. Bend constraints come from the
    grid's adjacent-triangle topology (proper hinge, not shear hack). */
export function buildSheet(cols, rows, width, height, opts = {}) {
  const fabric = FABRICS[opts.fabric] || FABRICS.cape;
  const q = CLOTH_QUALITY[opts.quality] || CLOTH_QUALITY.medium;
  const solver = new XPBDSolver(cols * rows, {
    damping: opts.damping !== undefined ? opts.damping : fabric.damping,
    substeps: opts.substeps || q.substeps,
    gravity: opts.gravity,
  });
  const idx = [];
  const pinTest = opts.pinTest || ((c, r) =>
    (opts.pinTop !== false && r === 0) ||
    (opts.pinLeft && c === 0) || (opts.pinRight && c === cols - 1) ||
    (opts.pinBottom && r === rows - 1));
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const x = (cols === 1 ? 0 : c / (cols - 1) - 0.5) * width;
      const y = -(rows === 1 ? 0 : r / (rows - 1)) * height;
      idx.push(solver.addParticle(x, y, 0, pinTest(c, r) ? 0 : 1));
    }
  }
  // index the grid as triangles, then derive stretch (edges) + bend
  // (adjacent-triangle hinges) from the real topology
  const indices = [];
  for (let r = 0; r < rows - 1; r++) {
    for (let c = 0; c < cols - 1; c++) {
      const a = r*cols+c, b = a+1, d = a+cols, e = d+1;
      indices.push(a, d, b, b, d, e);
    }
  }
  addTopologyConstraints(solver, idx, indices, fabric);
  solver.finalize();
  return { solver, idx, cols, rows };
}

/** Cloth from an existing mesh (intake costume geometry): positions is
    a flat xyz array, indices the triangle list. Mass per particle comes
    from adjacent triangle areas (jspdown/cloth initParticles). pinTest
    receives (x, y, z, i) in mesh-local space. */
export function buildFromMesh(positions, indices, opts = {}) {
  const fabric = FABRICS[opts.fabric] || FABRICS.cape;
  const q = CLOTH_QUALITY[opts.quality] || CLOTH_QUALITY.medium;
  const vCount = Math.floor(positions.length / 3);
  const budget = Math.min(vCount, opts.maxParticles || q.maxParticles);
  const solver = new XPBDSolver(Math.max(1, budget), {
    damping: opts.damping !== undefined ? opts.damping : fabric.damping,
    substeps: opts.substeps || q.substeps,
    gravity: opts.gravity,
  });
  // NOTE: meshes over budget are rejected (not decimated) — the caller
  // picks a LOD. Silent decimation would simulate the wrong shape.
  if (vCount > budget) {
    throw new Error(`cloth: mesh has ${vCount} verts, budget ${budget} — supply a LOD`);
  }
  const pinTest = opts.pinTest || (() => false);
  const areaSum = new Float64Array(vCount);
  const triCount = Math.floor(indices.length / 3);
  for (let t = 0; t < triCount; t++) {
    const a = indices[t*3], b = indices[t*3+1], c = indices[t*3+2];
    const ax = positions[a*3], ay = positions[a*3+1], az = positions[a*3+2];
    const abx = positions[b*3]-ax, aby = positions[b*3+1]-ay, abz = positions[b*3+2]-az;
    const acx = positions[c*3]-ax, acy = positions[c*3+1]-ay, acz = positions[c*3+2]-az;
    const cx = aby*acz - abz*acy, cy = abz*acx - abx*acz, cz = abx*acy - aby*acx;
    const area = 0.5 * Math.sqrt(cx*cx + cy*cy + cz*cz);
    areaSum[a] += area; areaSum[b] += area; areaSum[c] += area;
  }
  for (let i = 0; i < vCount; i++) {
    const pinned = pinTest(positions[i*3], positions[i*3+1], positions[i*3+2], i);
    // mass = density × third of adjacent area; invMass = 1/mass
    const mass = Math.max(1e-6, fabric.density * areaSum[i] / 3);
    solver.addParticle(positions[i*3], positions[i*3+1], positions[i*3+2],
      pinned ? 0 : 1 / mass);
  }
  const idx = []; for (let i = 0; i < vCount; i++) idx.push(i);
  addTopologyConstraints(solver, idx, indices, fabric);
  solver.finalize();
  return { solver, idx };
}

/** Hair / tassel / chain strap: particles in a line with stretch +
    gentle bend so strands curve instead of kinking. */
export function buildChain(segments, segLen, opts = {}) {
  const fabric = FABRICS[opts.fabric] || FABRICS.hair;
  const q = CLOTH_QUALITY[opts.quality] || CLOTH_QUALITY.medium;
  const solver = new XPBDSolver(segments + 1, {
    damping: opts.damping !== undefined ? opts.damping : fabric.damping,
    substeps: opts.substeps || q.substeps,
    gravity: opts.gravity,
  });
  const idx = [];
  const dir = opts.direction || [0, -1, 0];
  for (let i = 0; i <= segments; i++) {
    idx.push(solver.addParticle(dir[0]*i*segLen, dir[1]*i*segLen, dir[2]*i*segLen,
      i === 0 ? 0 : 1));
  }
  for (let i = 0; i < segments; i++) {
    solver.addConstraint(idx[i], idx[i+1], fabric.stretchCompliance, segLen);
    if (i < segments - 1) {
      // skip-one bend constraint keeps the strand smooth (Velvet-style
      // long-range attachment idea, applied as a soft XPBD constraint)
      solver.addConstraint(idx[i], idx[i+2], Math.max(fabric.bendCompliance, 0.05), segLen * 2);
    }
  }
  solver.finalize();
  return { solver, idx };
}

/** Shared: stretch constraints on every edge + bend constraints on
    every adjacent-triangle hinge (the two non-shared vertices). */
function addTopologyConstraints(solver, idx, indices, fabric) {
  const { edges, adjacentTriangles } = extractTopology(indices);
  for (const [a, b] of edges) {
    solver.addConstraint(idx[a], idx[b], fabric.stretchCompliance);
  }
  for (const [ta, tb] of adjacentTriangles) {
    const va = [indices[ta*3], indices[ta*3+1], indices[ta*3+2]];
    const vb = [indices[tb*3], indices[tb*3+1], indices[tb*3+2]];
    const onlyA = va.find(v => vb.indexOf(v) === -1);
    const onlyB = vb.find(v => va.indexOf(v) === -1);
    if (onlyA === undefined || onlyB === undefined) continue;
    solver.addConstraint(idx[onlyA], idx[onlyB], fabric.bendCompliance);
  }
}

/* ============================================================
   Three.js adapter — no three import; works with anything shaped
   like a BufferAttribute (setXYZ + needsUpdate) or a raw array.
   ============================================================ */
export function writePositions(solver, positionAttr, ox = 0, oy = 0, oz = 0) {
  const { pos, count } = solver;
  if (typeof positionAttr.setXYZ === 'function') {
    for (let i = 0; i < count; i++) positionAttr.setXYZ(i, pos[i*3]+ox, pos[i*3+1]+oy, pos[i*3+2]+oz);
    positionAttr.needsUpdate = true;
  } else {
    for (let i = 0; i < count; i++) {
      positionAttr[i*3] = pos[i*3]+ox; positionAttr[i*3+1] = pos[i*3+1]+oy; positionAttr[i*3+2] = pos[i*3+2]+oz;
    }
  }
}

/** Area-weighted normals into a normal attribute (or raw array).
    indices: the simulated triangle list. */
export function writeNormals(solver, normalAttr, indices) {
  const { pos, count } = solver;
  const nx = new Float32Array(count), ny = new Float32Array(count), nz = new Float32Array(count);
  const triCount = Math.floor(indices.length / 3);
  for (let t = 0; t < triCount; t++) {
    const a = indices[t*3]*3, b = indices[t*3+1]*3, c = indices[t*3+2]*3;
    const abx = pos[b]-pos[a], aby = pos[b+1]-pos[a+1], abz = pos[b+2]-pos[a+2];
    const acx = pos[c]-pos[a], acy = pos[c+1]-pos[a+1], acz = pos[c+2]-pos[a+2];
    const cx = aby*acz - abz*acy, cy = abz*acx - abx*acz, cz = abx*acy - aby*acx;
    nx[indices[t*3]] += cx; ny[indices[t*3]] += cy; nz[indices[t*3]] += cz;
    nx[indices[t*3+1]] += cx; ny[indices[t*3+1]] += cy; nz[indices[t*3+1]] += cz;
    nx[indices[t*3+2]] += cx; ny[indices[t*3+2]] += cy; nz[indices[t*3+2]] += cz;
  }
  if (typeof normalAttr.setXYZ === 'function') {
    for (let i = 0; i < count; i++) {
      const l = Math.sqrt(nx[i]*nx[i] + ny[i]*ny[i] + nz[i]*nz[i]) || 1;
      normalAttr.setXYZ(i, nx[i]/l, ny[i]/l, nz[i]/l);
    }
    normalAttr.needsUpdate = true;
  } else {
    for (let i = 0; i < count; i++) {
      const l = Math.sqrt(nx[i]*nx[i] + ny[i]*ny[i] + nz[i]*nz[i]) || 1;
      normalAttr[i*3] = nx[i]/l; normalAttr[i*3+1] = ny[i]/l; normalAttr[i*3+2] = nz[i]/l;
    }
  }
}

/* ---------- backend probe ----------
   'cpu' always. 'webgpu' reports whether the WebGPU compute upgrade
   path is available in this environment (navigator.gpu). */
export function availableBackends(env) {
  const e = env || (typeof navigator !== 'undefined' ? { navigator } : {});
  const webgpu = !!(e.navigator && e.navigator.gpu);
  return { cpu: true, webgpu, active: 'cpu' };
}
