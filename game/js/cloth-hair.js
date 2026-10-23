/* ============================================================
   WESTERN HEART — Hair + Cloth Physics (browser/Three.js)
   Teardown source: DOA/SF cloth-sim approaches. The teardowns document
   the DESIGN (soft-body secondary motion on hair/costumes) but no
   implementation-level cloth code survived extraction — so this module
   implements the industry-standard approach those games use, adapted for
   the browser: verlet-integration particles + distance constraints
   (the same family as DOA's soft engine and SF's cloth), with bone-chain
   verlet for hair strands (DynamicBone-style).
   Performance (browser-first):
     • Fixed-substep verlet (2 substeps), typed arrays, particle BUDGETS.
     • Distance LOD: sim sleeps beyond CLOTH_LOD_DIST, resumes on approach.
     • Colliders are analytic spheres/capsules (no mesh collision).
   Pipeline wiring: character pipeline tags meshes via glTF extras ->
   THREE userData.whCloth = { kind:'cloth'|'hair', ...params }. Tag in
   Blender with a custom property `wh_cloth` on the object; the intake
   pipeline copies extras -> userData. autoAttachCloth(scene) finds them.
   ============================================================ */

export const CLOTH_LOD_DIST = 14;      // beyond this, sim sleeps
export const CLOTH_SUBSTEPS = 2;
export const CLOTH_MAX_PARTICLES = 900; // per-system budget

/* ---------- verlet core (typed arrays, no per-frame allocation) ---------- */
export class VerletSystem {
  constructor(maxParticles) {
    const n = Math.min(maxParticles, CLOTH_MAX_PARTICLES);
    this.n = n;
    this.pos = new Float32Array(n * 3);
    this.prev = new Float32Array(n * 3);
    this.invMass = new Float32Array(n);   // 0 = pinned
    this.count = 0;
    this.constraints = []; // [ia, ib, rest]
    this.gravity = -9.8;
    this.damping = 0.985;
    this.wind = { x: 0, y: 0, z: 0, t: 0 };
  }
  addParticle(x, y, z, invMass = 1) {
    const i = this.count++;
    this.pos.set([x, y, z], i * 3);
    this.prev.set([x, y, z], i * 3);
    this.invMass[i] = invMass;
    return i;
  }
  addConstraint(a, b, rest = -1) {
    if (rest < 0) {
      const dx = this.pos[a*3]-this.pos[b*3], dy = this.pos[a*3+1]-this.pos[b*3+1], dz = this.pos[a*3+2]-this.pos[b*3+2];
      rest = Math.hypot(dx, dy, dz);
    }
    this.constraints.push([a, b, rest]);
  }
  step(dt, colliders = []) {
    const sub = CLOTH_SUBSTEPS, h = dt / sub;
    for (let s = 0; s < sub; s++) {
      this._integrate(h, colliders);
      for (let it = 0; it < 3; it++) this._solve();
    }
  }
  _integrate(h, colliders) {
    const { pos, prev, invMass, count, damping } = this;
    this.wind.t += h;
    const wx = this.wind.x * (0.6 + 0.4 * Math.sin(this.wind.t * 2.1));
    const wz = this.wind.z * (0.6 + 0.4 * Math.cos(this.wind.t * 1.7));
    for (let i = 0; i < count; i++) {
      if (invMass[i] === 0) continue;
      const ix = i * 3;
      const px = pos[ix], py = pos[ix+1], pz = pos[ix+2];
      const vx = (px - prev[ix]) * damping, vy = (py - prev[ix+1]) * damping, vz = (pz - prev[ix+2]) * damping;
      prev[ix] = px; prev[ix+1] = py; prev[ix+2] = pz;
      pos[ix]   = px + vx + wx * h * h * invMass[i];
      pos[ix+1] = py + vy + this.gravity * h * h * invMass[i];
      pos[ix+2] = pz + vz + wz * h * h * invMass[i];
      // analytic sphere colliders
      for (const c of colliders) {
        const dx = pos[ix]-c.x, dy = pos[ix+1]-c.y, dz = pos[ix+2]-c.z;
        const d2 = dx*dx + dy*dy + dz*dz, r = c.r;
        if (d2 < r*r && d2 > 1e-9) {
          const d = Math.sqrt(d2), push = (r - d) / d;
          pos[ix] += dx*push; pos[ix+1] += dy*push; pos[ix+2] += dz*push;
        }
      }
    }
  }
  _solve() {
    const { pos, invMass, constraints } = this;
    for (const [a, b, rest] of constraints) {
      const wa = invMass[a], wb = invMass[b], w = wa + wb;
      if (w === 0) continue;
      const ax = a*3, bx = b*3;
      const dx = pos[bx]-pos[ax], dy = pos[bx+1]-pos[ax+1], dz = pos[bx+2]-pos[ax+2];
      const d = Math.hypot(dx, dy, dz) || 1e-6;
      const diff = (d - rest) / d / w;
      pos[ax] += dx*diff*wa; pos[ax+1] += dy*diff*wa; pos[ax+2] += dz*diff*wa;
      pos[bx] -= dx*diff*wb; pos[bx+1] -= dy*diff*wb; pos[bx+2] -= dz*diff*wb;
    }
  }
}

/* ---------- cloth sheet (capes, skirts, sashes) ---------- */
/* Builds a pinned-top grid cloth. writeTo(geometry) copies sim positions
   into a THREE.BufferGeometry's position attribute each frame. */
export class ClothSheet {
  constructor(cols, rows, width, height, pinTop = true) {
    this.cols = cols; this.rows = rows;
    this.sys = new VerletSystem(cols * rows);
    this.idx = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const x = (c / (cols-1) - 0.5) * width;
        const y = -(r / (rows-1)) * height;
        const pinned = pinTop && r === 0;
        this.idx.push(this.sys.addParticle(x, y, 0, pinned ? 0 : 1));
      }
    }
    const at = (c, r) => this.idx[r * cols + c];
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      if (c < cols-1) this.sys.addConstraint(at(c,r), at(c+1,r));
      if (r < rows-1) this.sys.addConstraint(at(c,r), at(c,r+1));
      if (c < cols-1 && r < rows-1) { // shear keeps it from over-stretching
        this.sys.addConstraint(at(c,r), at(c+1,r+1));
        this.sys.addConstraint(at(c+1,r), at(c,r+1));
      }
    }
    this.sleeping = false;
  }
  /* origin: THREE.Vector3-ish world anchor; returns Float32Array positions */
  step(dt, origin, colliders, cameraDist) {
    this.sleeping = cameraDist > CLOTH_LOD_DIST;
    if (this.sleeping) return;
    this.sys.step(dt, colliders);
  }
  /* Copy sim -> geometry positions with an origin offset. geometry must
     have exactly cols*rows vertices in row-major order. */
  writeTo(positionAttr, ox, oy, oz) {
    const { pos } = this.sys;
    for (let i = 0; i < this.idx.length; i++) {
      const s = this.idx[i] * 3;
      positionAttr.setXYZ(i, pos[s]+ox, pos[s+1]+oy, pos[s+2]+oz);
    }
    positionAttr.needsUpdate = true;
  }
}

/* ---------- hair chains (ponytails, long hair, tassels) ---------- */
/* DynamicBone-style: a verlet chain whose root is pinned to a moving
   anchor (the head bone). Each frame the caller sets the root from the
   bone's world position; the chain follows with spring lag. */
export class HairChain {
  constructor(segments, segLen, thickness = 1) {
    this.segLen = segLen;
    this.sys = new VerletSystem(segments + 1);
    this.idx = [];
    for (let i = 0; i <= segments; i++) this.idx.push(this.sys.addParticle(0, -i*segLen, 0, i === 0 ? 0 : 1));
    for (let i = 0; i < segments; i++) this.sys.addConstraint(this.idx[i], this.idx[i+1], segLen);
    this.thickness = thickness;
    this.root = { x: 0, y: 0, z: 0 };
  }
  setRoot(x, y, z) {
    this.root = { x, y, z };
    const i = this.idx[0] * 3;
    this.sys.pos[i] = x; this.sys.pos[i+1] = y; this.sys.pos[i+2] = z;
    this.sys.prev[i] = x; this.sys.prev[i+1] = y; this.sys.prev[i+2] = z;
  }
  step(dt, colliders = []) { this.sys.step(dt, colliders); }
  /* Strand points for tube/line rendering (world space). */
  points() {
    const out = [], { pos } = this.sys;
    for (const i of this.idx) out.push([pos[i*3], pos[i*3+1], pos[i*3+2]]);
    return out;
  }
}

/* ---------- pipeline auto-attach ---------- */
/* Scan a loaded character scene for userData.whCloth tags and build sims.
   Tag format (glTF extras -> userData):
     { kind:'cloth', cols, rows, width, height }  -> ClothSheet
     { kind:'hair', strands:[{segments, segLen}], rootBone:'head' } */
export function autoAttachCloth(scene) {
  const attached = [];
  scene.traverse(o => {
    const tag = o.userData && o.userData.whCloth;
    if (!tag) return;
    if (tag.kind === 'cloth') {
      attached.push({ object: o, sim: new ClothSheet(tag.cols||8, tag.rows||10, tag.width||0.6, tag.height||0.9), tag });
    } else if (tag.kind === 'hair') {
      const chains = (tag.strands||[{segments:8,segLen:0.06}]).map(s => new HairChain(s.segments, s.segLen));
      attached.push({ object: o, chains, tag, rootBone: tag.rootBone || 'head' });
    }
  });
  return attached;
}
