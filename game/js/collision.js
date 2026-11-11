/* ============================================================
   WESTERN HEART — Collision Core (browser / Three.js runtime)

   WHY THIS EXISTS (owner order 2026-11-09): "collision between
   their own bodies... do it the industry standard where they're
   not phasing — when their hair touches their shoulders it sits
   on their shoulders and gets pushed around... doesn't phase
   through their skin — for all the models, starting with Megami,
   but universally across all of them."

   WHAT THE INDUSTRY STANDARD IS (researched 2026-11-09, see
   docs/handoffs/COLLISION-SYSTEM-2026-11-09.md for sources):
   Real-time character contact in production engines is a stack,
   not one trick:
     1. ANALYTIC COLLIDERS fitted to the skeleton — Unreal's
        Physics Asset (PhAT) capsules/spheres per bone and Unity
        Cloth / Magica Cloth 2's sphere+capsule collider sets are
        the runtime contact surface for hair and cloth.
     2. BAKED SIGNED DISTANCE FIELDS — AMD TressFX ships an SDF
        collision mesh (.tfxmesh) per character; Unreal distance
        fields do the same job. The SDF is the high-fidelity
        contact + measurement layer where capsules are too coarse.
     3. XPBD / PBD projection solvers — Macklin et al. 2016 +
        Small Steps (Macklin et al. 2019): positions are PROJECTED
        out of penetration every substep; contact is inelastic
        with friction, so things REST on surfaces instead of
        bouncing or sinking. Our solver already exists
        (game/js/fx/cloth.js, ported from jspdown/cloth, MIT) and
        the spring-bone hair driver (game/js/hair-spring.js);
        this module is the shared collision layer both consume.
     4. SELF-COLLISION by spatial hashing (Müller et al. PBD
        particle collision; Magica Cloth 2 does PointTriangle +
        EdgeEdge — the particle form here is the real-time
        budget version, labelled as such).
     5. FACIAL CONTACT by CONTACT-DRIVEN COUPLING — film/game
        face pipelines (lip-collision de-intersection passes;
        JALI's separation of jaw vs lip drives) resolve tongue /
        lip / teeth contact by DRIVING the jaw and lips from the
        measured penetration, then deflecting the tongue — never
        by letting solids interpenetrate. solveArticulator-
        Coupling() below is that solver, head-agnostic.

   This module is three-free (plain arrays / typed arrays, like
   fx/cloth.js) so it is unit-testable in Node:
   game/js/collision.test.mjs. Three-side adapters live in the
   consumers (hair-spring.js, cloth-hair.js).

   PER-CHARACTER DATA (baked offline, per model — the core is
   shared, the data is not): tools/collision/bake-collision.mjs
   produces, under customization/collision/<character>/:
     - <character>-collision.json — capsule/sphere set fitted
       from the skinned bind pose (bone names + radii + margins)
     - <character>-body.sdf.bin — Int16-quantized SDF grid of the
       bind-pose body (head/torso contact region), baked with the
       game's vendored three-mesh-bvh (MIT) closest-point queries.
   ============================================================ */

/* ---------- small vector helpers (flat xyz arrays) ---------- */
function segClosest(px, py, pz, ax, ay, az, bx, by, bz, out) {
  const abx = bx - ax, aby = by - ay, abz = bz - az;
  const len2 = abx * abx + aby * aby + abz * abz;
  let t = 0;
  if (len2 > 1e-12) {
    t = ((px - ax) * abx + (py - ay) * aby + (pz - az) * abz) / len2;
    t = t < 0 ? 0 : (t > 1 ? 1 : t);
  }
  out[0] = ax + abx * t; out[1] = ay + aby * t; out[2] = az + abz * t;
  return t;
}

/* ============================================================
   BodySDF — baked signed-distance volume.

   Grid: regular lattice, `origin` = world position of voxel
   (0,0,0)'s CENTRE in the bake frame, `voxel` = spacing (m),
   dims [nx, ny, nz]. Data is Int16 quantized: metres = raw *
   quant. Sign: negative INSIDE the body, positive outside
   (three-mesh-bvh closest-point + closest-face-normal sign,
   validated at bake time; see bake-collision.mjs).
   Sampling is trilinear; the gradient is the trilinear
   gradient's finite-difference form (central differences of
   the sampled field), normalized by the caller as needed.
   Points outside the grid return the distance to the grid box
   plus the clamped sample — the standard "SDF falls off to
   Euclidean outside" approximation, so far points still get a
   sane outward direction from the gradient.
   ============================================================ */
export class BodySDF {
  constructor(meta, data) {
    this.origin = meta.origin;         // [x,y,z]
    this.voxel = meta.voxel;           // metres
    this.dims = meta.dims;             // [nx,ny,nz]
    this.quant = meta.quant || 1;      // metres per Int16 unit (1 for float data)
    this.data = data;                  // Int16Array or Float32Array, x-fastest
    const [nx, ny, nz] = this.dims;
    this.maxX = this.origin[0] + (nx - 1) * this.voxel;
    this.maxY = this.origin[1] + (ny - 1) * this.voxel;
    this.maxZ = this.origin[2] + (nz - 1) * this.voxel;
  }

  _at(ix, iy, iz) {
    const [nx, ny] = this.dims;
    return this.data[ix + nx * (iy + ny * iz)] * this.quant;
  }

  /** Signed distance (metres) at a point in the bake frame. */
  sample(x, y, z) {
    const [nx, ny, nz] = this.dims;
    const v = this.voxel;
    // clamp into the lattice for the field value
    let gx = (x - this.origin[0]) / v, gy = (y - this.origin[1]) / v, gz = (z - this.origin[2]) / v;
    const cx = Math.min(Math.max(gx, 0), nx - 1), cy = Math.min(Math.max(gy, 0), ny - 1), cz = Math.min(Math.max(gz, 0), nz - 1);
    const x0 = Math.floor(cx), y0 = Math.floor(cy), z0 = Math.floor(cz);
    const x1 = Math.min(x0 + 1, nx - 1), y1 = Math.min(y0 + 1, ny - 1), z1 = Math.min(z0 + 1, nz - 1);
    const fx = cx - x0, fy = cy - y0, fz = cz - z0;
    const c000 = this._at(x0, y0, z0), c100 = this._at(x1, y0, z0);
    const c010 = this._at(x0, y1, z0), c110 = this._at(x1, y1, z0);
    const c001 = this._at(x0, y0, z1), c101 = this._at(x1, y0, z1);
    const c011 = this._at(x0, y1, z1), c111 = this._at(x1, y1, z1);
    const x00 = c000 + (c100 - c000) * fx, x10 = c010 + (c110 - c010) * fx;
    const x01 = c001 + (c101 - c001) * fx, x11 = c011 + (c111 - c011) * fx;
    const y0v = x00 + (x10 - x00) * fy, y1v = x01 + (x11 - x01) * fy;
    let d = y0v + (y1v - y0v) * fz;
    // outside the lattice: add the Euclidean distance to the box
    if (gx < 0 || gy < 0 || gz < 0 || gx > nx - 1 || gy > ny - 1 || gz > nz - 1) {
      const dx = Math.max(this.origin[0] - x, 0, x - this.maxX);
      const dy = Math.max(this.origin[1] - y, 0, y - this.maxY);
      const dz = Math.max(this.origin[2] - z, 0, z - this.maxZ);
      d += Math.sqrt(dx * dx + dy * dy + dz * dz);
    }
    return d;
  }

  /** Gradient (unnormalized) at a point; writes into out[3]. */
  gradient(x, y, z, out) {
    const h = this.voxel;
    out[0] = this.sample(x + h, y, z) - this.sample(x - h, y, z);
    out[1] = this.sample(x, y + h, z) - this.sample(x, y - h, z);
    out[2] = this.sample(x, y, z + h) - this.sample(x, y, z - h);
    return out;
  }

  /** Project a point out of the volume: if sample(p) < margin,
      move p along the gradient to the margin iso-surface.
      p is a mutable [x,y,z]. Returns penetration depth resolved
      (0 when no contact). maxIter guards degenerate gradients. */
  project(p, margin = 0, maxIter = 3) {
    let resolved = 0;
    const g = [0, 0, 0];
    for (let i = 0; i < maxIter; i++) {
      const d = this.sample(p[0], p[1], p[2]);
      const pen = margin - d;
      if (pen <= 0) break;
      this.gradient(p[0], p[1], p[2], g);
      const gl = Math.sqrt(g[0] * g[0] + g[1] * g[1] + g[2] * g[2]);
      if (gl < 1e-9) break;
      const s = pen / gl;
      p[0] += g[0] * s; p[1] += g[1] * s; p[2] += g[2] * s;
      resolved += pen;
    }
    return resolved;
  }

  /** Serialize the header (data ships as a separate .bin). */
  static headerFromJSON(json) {
    return {
      origin: json.origin, voxel: json.voxel, dims: json.dims,
      quant: json.quant, format: json.format || 'int16',
    };
  }
}

/* ============================================================
   Analytic colliders — the PhAT-style layer.
   A collider set is fitted ONCE per character (bake) as bone-
   relative data, then posed per frame by the consumer:
     { type:'sphere',  bone, offset:[x,y,z] (bone-local), radius, margin, friction }
     { type:'capsule', boneA, boneB, radius, margin, friction }
   The posed forms used by the solver are plain world-space
   values: sphere {c:[x,y,z], r}, capsule {a:[x,y,z], b:[x,y,z], r}
   with r = radius + margin (margin = the simulated thing's own
   radius, e.g. hair strand/clump thickness).
   ============================================================ */

/** Project point p out of a posed sphere. Returns depth or 0.
    On contact, `normal` (if given) receives the unit normal. */
export function collideSphere(p, c, r, normal) {
  const dx = p[0] - c[0], dy = p[1] - c[1], dz = p[2] - c[2];
  const d2 = dx * dx + dy * dy + dz * dz;
  if (d2 >= r * r) return 0;
  const d = Math.sqrt(d2);
  if (d < 1e-9) { // dead centre: push up arbitrarily
    p[1] = c[1] + r;
    if (normal) { normal[0] = 0; normal[1] = 1; normal[2] = 0; }
    return r;
  }
  const s = r / d;
  p[0] = c[0] + dx * s; p[1] = c[1] + dy * s; p[2] = c[2] + dz * s;
  if (normal) { normal[0] = dx / d; normal[1] = dy / d; normal[2] = dz / d; }
  return r - d;
}

/** Project point p out of a posed capsule (segment a-b, radius r). */
export function collideCapsule(p, a, b, r, normal) {
  const q = [0, 0, 0];
  segClosest(p[0], p[1], p[2], a[0], a[1], a[2], b[0], b[1], b[2], q);
  return collideSphere(p, q, r, normal);
}

/** Friction for a verlet particle: given current pos p, previous
    pos prev, and a contact normal n, remove the into-surface
    velocity and scale the tangential velocity by (1 - mu).
    This is what makes hair REST and DRAG on a shoulder instead
    of skating off it (inelastic contact, Müller PBD friction).
    Mutates prev (velocity is implicit: v = p - prev). */
export function applyContactFriction(p, prev, n, mu) {
  let vx = p[0] - prev[0], vy = p[1] - prev[1], vz = p[2] - prev[2];
  const vn = vx * n[0] + vy * n[1] + vz * n[2];
  // tangential component
  let tx = vx - vn * n[0], ty = vy - vn * n[1], tz = vz - vn * n[2];
  const keep = 1 - Math.min(Math.max(mu, 0), 1);
  tx *= keep; ty *= keep; tz *= keep;
  // normal velocity: contact is inelastic — no bounce, no sink
  const nnx = vn > 0 ? vn * n[0] : 0, nny = vn > 0 ? vn * n[1] : 0, nnz = vn > 0 ? vn * n[2] : 0;
  vx = tx + nnx; vy = ty + nny; vz = tz + nnz;
  prev[0] = p[0] - vx; prev[1] = p[1] - vy; prev[2] = p[2] - vz;
}

/* ============================================================
   SelfCollider — spatial-hash particle self-collision.
   The real-time form of PBD self-collision (Müller et al.
   2007 §4.4; every production cloth since): particles within
   `minDist` of each other are pushed apart symmetrically,
   weighted by inverse mass. Topological neighbours (particles
   joined by a constraint) are excluded via `skipPairs`, the
   standard practice — their distance is the constraint's job.
   Deterministic: particles are visited in index order.
   NOTE (honest scope): this is PARTICLE self-collision. The
   film/Magica high end uses PointTriangle + EdgeEdge contacts;
   particle form is the real-time budget version and is what
   ships in games at 60 fps.
   ============================================================ */
export class SelfCollider {
  constructor(minDist) {
    this.minDist = minDist;
    this.cell = minDist;
    this.map = new Map();
  }

  _key(ix, iy, iz) { return ix + ',' + iy + ',' + iz; }

  /** pos: Float32Array xyz; invMass: Float32Array.
      skipPairs: Set of "i_j" (i<j) or null. Mutates pos.
      Returns the number of pairs resolved. */
  collide(pos, invMass, skipPairs = null, iterations = 1) {
    const n = Math.floor(pos.length / 3);
    const cell = this.cell, md = this.minDist, md2 = md * md;
    let resolved = 0;
    for (let it = 0; it < iterations; it++) {
      this.map.clear();
      for (let i = 0; i < n; i++) {
        const ix = Math.floor(pos[i * 3] / cell), iy = Math.floor(pos[i * 3 + 1] / cell), iz = Math.floor(pos[i * 3 + 2] / cell);
        const k = this._key(ix, iy, iz);
        let arr = this.map.get(k);
        if (!arr) { arr = []; this.map.set(k, arr); }
        arr.push(i);
      }
      for (let i = 0; i < n; i++) {
        // NOTE: a pinned particle (invMass 0) still takes part in
        // pair tests as the LOWER index — its partner must receive
        // the full push. Skipping pinned i here would drop the pair.
        const px = pos[i * 3], py = pos[i * 3 + 1], pz = pos[i * 3 + 2];
        const cx = Math.floor(px / cell), cy = Math.floor(py / cell), cz = Math.floor(pz / cell);
        for (let ox = -1; ox <= 1; ox++) for (let oy = -1; oy <= 1; oy++) for (let oz = -1; oz <= 1; oz++) {
          const arr = this.map.get(this._key(cx + ox, cy + oy, cz + oz));
          if (!arr) continue;
          for (let a = 0; a < arr.length; a++) {
            const j = arr[a];
            if (j <= i) continue;
            if (skipPairs && skipPairs.has(i + '_' + j)) continue;
            const wj = invMass[j];
            const dx = pos[j * 3] - pos[i * 3], dy = pos[j * 3 + 1] - pos[i * 3 + 1], dz = pos[j * 3 + 2] - pos[i * 3 + 2];
            const d2 = dx * dx + dy * dy + dz * dz;
            if (d2 >= md2 || d2 < 1e-12) continue;
            const d = Math.sqrt(d2);
            const wi = invMass[i], wsum = wi + wj;
            if (wsum <= 0) continue;
            const push = (md - d) / d;
            const si = push * (wi / wsum), sj = push * (wj / wsum);
            pos[i * 3] -= dx * si; pos[i * 3 + 1] -= dy * si; pos[i * 3 + 2] -= dz * si;
            pos[j * 3] += dx * sj; pos[j * 3 + 1] += dy * sj; pos[j * 3 + 2] += dz * sj;
            resolved++;
          }
        }
      }
    }
    return resolved;
  }
}

/* ============================================================
   Articulator coupling — tongue / lips / teeth / jaw (Phase C).

   The production pattern (film lip-collision de-intersection
   passes; JALI's independent jaw vs lip drive spaces): the
   mouth's solids (teeth, gums, lips) form a signed-distance
   volume IN HEAD SPACE that DEFORMS with the drives — jaw angle
   drops the lower assembly, lip drives part the lips. Given a
   set of tongue sample points (head space) that an animation
   wants to place:
     1. measure penetration against the volume at current drives
     2. convert the worst regional penetration into drive
        changes (jaw opens, lips part) — the BODY makes room
     3. deflect the tongue points out along the SDF gradient —
        the TONGUE yields where the drives cannot
   iterated to a fixed point. Nothing interpenetrates at the
   end: either the mouth made room, or the tongue moved.

   Head-agnostic by design: the caller supplies
     sample(x,y,z,drives) -> signed distance (neg = inside solid)
     gradient(x,y,z,drives,out)
     classify(x,y,z) -> 'lower' | 'upper' | 'other'
        (which assembly a contact belongs to — from the bake's
        region segmentation; lower = jaw-driven, upper = lip)
   drives = { jaw: radians, lipLower: metres, lipUpper: metres }
   with limits passed in opts. Returns final drives + stats.
   ============================================================ */
export function solveArticulatorCoupling(points, oracle, drives, opts = {}) {
  const margin = opts.margin ?? 0.0015;
  const iterations = opts.iterations ?? 4;
  const jawMax = opts.jawMax ?? 0.55;          // rad (~31°)
  const jawLever = opts.jawLever ?? 0.085;     // m: jaw rotation -> incisor drop per rad
  const lipLowerMax = opts.lipLowerMax ?? 0.02;
  const lipUpperMax = opts.lipUpperMax ?? 0.015;
  const d = { jaw: drives.jaw || 0, lipLower: drives.lipLower || 0, lipUpper: drives.lipUpper || 0 };
  const n = Math.floor(points.length / 3);
  const g = [0, 0, 0];
  const stats = { initialPen: 0, residualPen: 0, contacts: 0 };

  const worstInRegion = (region) => {
    let worst = 0;
    for (let i = 0; i < n; i++) {
      const x = points[i * 3], y = points[i * 3 + 1], z = points[i * 3 + 2];
      if (oracle.classify(x, y, z) !== region) continue;
      const pen = margin - oracle.sample(x, y, z, d);
      if (pen > worst) worst = pen;
    }
    return worst;
  };

  // initial measure
  for (let i = 0; i < n; i++) {
    const pen = margin - oracle.sample(points[i * 3], points[i * 3 + 1], points[i * 3 + 2], d);
    if (pen > stats.initialPen) stats.initialPen = pen;
    if (pen > 0) stats.contacts++;
  }

  for (let it = 0; it < iterations; it++) {
    // 1) drives make room: lower contacts open the jaw first,
    //    then part the lower lip; upper contacts part the upper lip.
    const penLower = worstInRegion('lower');
    if (penLower > 0) {
      const jawRoom = Math.max(0, (jawMax - d.jaw)) * jawLever;
      const useJaw = Math.min(penLower, jawRoom);
      d.jaw += useJaw / jawLever;
      const rest = penLower - useJaw;
      if (rest > 0) d.lipLower = Math.min(lipLowerMax, d.lipLower + rest);
    }
    const penUpper = worstInRegion('upper');
    if (penUpper > 0) d.lipUpper = Math.min(lipUpperMax, d.lipUpper + penUpper);
    // 2) the tongue yields: project every penetrating point out
    for (let i = 0; i < n; i++) {
      const p = [points[i * 3], points[i * 3 + 1], points[i * 3 + 2]];
      for (let k = 0; k < 3; k++) {
        const pen = margin - oracle.sample(p[0], p[1], p[2], d);
        if (pen <= 0) break;
        oracle.gradient(p[0], p[1], p[2], d, g);
        const gl = Math.sqrt(g[0] * g[0] + g[1] * g[1] + g[2] * g[2]);
        if (gl < 1e-9) break;
        const s = pen / gl;
        p[0] += g[0] * s; p[1] += g[1] * s; p[2] += g[2] * s;
      }
      points[i * 3] = p[0]; points[i * 3 + 1] = p[1]; points[i * 3 + 2] = p[2];
    }
  }

  for (let i = 0; i < n; i++) {
    const pen = margin - oracle.sample(points[i * 3], points[i * 3 + 1], points[i * 3 + 2], d);
    if (pen > stats.residualPen) stats.residualPen = pen;
  }
  return { drives: d, stats };
}
