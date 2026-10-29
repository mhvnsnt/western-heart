/* ============================================================
   WESTERN HEART — Hair + Cloth Physics (browser/Three.js)
   Teardown source: DOA/SF cloth-sim approaches. The teardowns document
   the DESIGN (soft-body secondary motion on hair/costumes) but no
   implementation-level cloth code survived extraction — so this module
   implements the industry-standard approach those games use, adapted for
   the browser.

   Solver (2026-10-23 upgrade): the verlet core below is now a thin
   compatibility facade over game/js/fx/cloth.js — a real XPBD solver
   (ported from jspdown/cloth, MIT) with compliance-based fabric
   stiffness, stretch + bend constraints from mesh topology, and
   graph-colored Gauss-Seidel solving. Public API unchanged:
   VerletSystem / ClothSheet / HairChain / autoAttachCloth keep their
   signatures, so fighter-depth.js and the whole roster pick up the
   upgrade with zero call-site changes.
   Performance (browser-first):
     • Fixed-substep XPBD, typed arrays, particle BUDGETS.
     • Distance LOD: sim sleeps beyond CLOTH_LOD_DIST, resumes on approach.
     • Colliders are analytic spheres/capsules (no mesh collision).
   Pipeline wiring: character pipeline tags meshes via glTF extras ->
   THREE userData.whCloth = { kind:'cloth'|'hair', ...params }. Tag in
   Blender with a custom property `wh_cloth` on the object; the intake
   pipeline copies extras -> userData. autoAttachCloth(scene) finds them.
   ============================================================ */

import {
  XPBDSolver, buildSheet, buildChain, writePositions, CLOTH_LOD_DIST,
} from './fx/cloth.js';
export { CLOTH_LOD_DIST };

export const CLOTH_SUBSTEPS = 2;
export const CLOTH_MAX_PARTICLES = 900; // per-system budget

/* ---------- XPBD core (facade over game/js/fx/cloth.js) ----------
   Same public surface as the old verlet core (addParticle,
   addConstraint, step, pos/prev/invMass/count/constraints, gravity,
   damping, wind) so existing call sites keep working; the physics
   underneath is now XPBD with graph-colored constraint solving. */
export class VerletSystem {
  constructor(maxParticles) {
    const n = Math.min(maxParticles, CLOTH_MAX_PARTICLES);
    this.n = n;
    this._solver = new XPBDSolver(n, { substeps: CLOTH_SUBSTEPS, damping: 0.985 });
    this.prev = new Float32Array(n * 3); // compat: pos at previous step
    this.constraints = []; // [ia, ib, rest] — introspection only
    this.gravity = -9.8;
    this.damping = 0.985;
    this.wind = { x: 0, y: 0, z: 0, t: 0 };
  }
  get pos() { return this._solver.pos; }
  get invMass() { return this._solver.invMass; }
  get count() { return this._solver.count; }
  addParticle(x, y, z, invMass = 1) {
    const i = this._solver.addParticle(x, y, z, invMass);
    this.prev.set([x, y, z], i * 3);
    return i;
  }
  addConstraint(a, b, rest = -1) {
    const s = this._solver;
    if (rest < 0) {
      const dx = s.pos[b*3]-s.pos[a*3], dy = s.pos[b*3+1]-s.pos[a*3+1], dz = s.pos[b*3+2]-s.pos[a*3+2];
      rest = Math.sqrt(dx*dx + dy*dy + dz*dz);
    }
    this.constraints.push([a, b, rest]);
    // rigid (compliance 0), matching the old solver's inextensible links
    return s.addConstraint(a, b, 0, rest);
  }
  step(dt, colliders = []) {
    const s = this._solver;
    this.prev.set(s.pos.subarray(0, s.count * 3));
    s.gravity = this.gravity;
    s.damping = this.damping;
    s.wind.x = this.wind.x; s.wind.y = this.wind.y; s.wind.z = this.wind.z;
    s.step(dt, colliders);
    this.wind.t = s.wind.t;
  }
}

/* ---------- cloth sheet (capes, skirts, sashes) ---------- */
/* Builds a pinned-top grid cloth on the XPBD engine: rigid stretch
   constraints on mesh edges + compliance bend constraints on
   adjacent-triangle hinges (proper fabric drape — cotton default).
   writeTo(geometry) copies sim positions into a THREE.BufferGeometry's
   position attribute each frame. */
export class ClothSheet {
  constructor(cols, rows, width, height, pinTop = true) {
    this.cols = cols; this.rows = rows;
    const built = buildSheet(cols, rows, width, height, {
      pinTop, fabric: 'cotton', substeps: CLOTH_SUBSTEPS,
    });
    this.sys = built.solver;
    this.idx = built.idx;
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
    writePositions(this.sys, positionAttr, ox, oy, oz);
  }
}

/* ---------- hair chains (ponytails, long hair, tassels) ---------- */
/* XPBD chain on the hair fabric preset: rigid stretch links + soft
   skip-one bend constraints so strands curve instead of kinking.
   Root is pinned to a moving anchor (the head bone) via pinTo — the
   caller sets it from the bone's world position each frame and the
   chain follows with physical lag. */
export class HairChain {
  constructor(segments, segLen, thickness = 1) {
    this.segLen = segLen;
    const built = buildChain(segments, segLen, { fabric: 'hair', substeps: CLOTH_SUBSTEPS });
    this.sys = built.solver;
    this.idx = built.idx;
    this.thickness = thickness;
    this.root = { x: 0, y: 0, z: 0 };
    this._rootPlaced = false;
  }
  setRoot(x, y, z) {
    const s = this.sys;
    if (!this._rootPlaced) {
      // First placement: rigid-translate the whole strand to the anchor
      // instead of stretching the root link across the scene — no whip
      // injected on attach; the strand starts hanging from the bone.
      const i0 = this.idx[0] * 3;
      const dx = x - s.pos[i0], dy = y - s.pos[i0+1], dz = z - s.pos[i0+2];
      for (const i of this.idx) { s.pos[i*3] += dx; s.pos[i*3+1] += dy; s.pos[i*3+2] += dz; }
      this._rootPlaced = true;
    }
    this.root = { x, y, z };
    s.pinTo(this.idx[0], x, y, z);
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
