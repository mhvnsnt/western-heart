/* ============================================================
   WESTERN HEART — Strand-level hair simulation (browser / Node)

   WHY THIS EXISTS (owner collision order 2026-11-09, Phase B2):
   the first Phase B proof was VACUOUS — measured in
   docs/proof/2026-11-09/megami-collision-strands/README.md §v1:
   the spring-bone driver (hair-spring.js) moves 19 guide BONES,
   but the visible hair is 174,406 vertices on 3,208 independent
   strand CARDS that no solver touched, and the bone chains were
   held to their animated pose by a 0.55 stiffness spring, so the
   tips never came within ~68 mm of the body. Collision was
   "proven" on trajectories that could not make contact.

   THIS MODULE fixes the structure, following the industry
   guide-strand model exactly as shipped in AMD TressFX
   (Hodes/Engel, "Hair in Tomb Raider", GDC): a modest number of
   GUIDE strands are simulated; every rendered vertex FOLLOWS a
   guide by a baked relative-frame binding. Here:

   - GUIDES come from the hair part itself: tools/collision/
     bake-strands.mjs extracts card centrelines from the actual
     GLB, picks ~200 guide centrelines by whole-path proximity,
     and binds all 174k card verts to guides with per-vertex
     relative frames (A = G^T C, offset in the vert's own card
     frame). The bake's bind round-trip gate reproduces every
     source vertex to 0.000 mm through THIS deform formula.
   - SIMULATION is Verlet + position-based dynamics (Jakobsen;
     Müller et al. 2007 "Position Based Dynamics"; XPBD,
     Macklin et al. 2016): gravity integrates freely, DISTANCE
     constraints preserve segment LENGTH ONLY — direction is
     never constrained, so strands DRAPE. There is deliberately
     NO stiffness-to-animated-pose term (that term is what made
     the v1 proof vacuous). A weak bend constraint (PBD bending,
     Müller et al. 2007 §3.5) at low stiffness keeps cards from
     folding into kinks; it resists curvature, not direction.
   - COLLISION is the shared core (game/js/collision.js):
     collideSphere / collideCapsule on posed analytic colliders
     + BodySDF.project for the torso volume, with
     applyContactFriction so strands REST and DRAG. The posed
     collision set has the same shape as hair-spring's
     collisionSetFromData() output, posed to plain arrays:
       { spheres: [{c:[x,y,z], r, friction}],
         capsules: [{a:[x,y,z], b:[x,y,z], r, friction}],
         sdf: { body: BodySDF, fromWorld: Float32Array(16)
                column-major, margin, friction } | null }
     r already includes the strand margin.
   - Roots are pinned to caller-supplied ANCHORS: per frame the
     caller passes the head-follow transform as a 4x4
     (column-major) mapping SIM space -> current anchor space is
     NOT used; instead the anchor is expressed directly: root
     world positions are computed as anchorM * bindRoot (bind
     roots are in part space; the caller folds the part's bind
     root matrix, the sunk-skin compensation, and the animated
     head motion into anchorM). Root FRAMES come from anchorM's
     rotation applied to the baked bind root frames, then RMFs
     are parallel-transported along each live polyline — the
     rotation-minimising frame propagation of the bake.

   Frames: everything simulates in ONE frame ("sim frame" = the
   stage/world frame the colliders are posed in). Bind data is
   in part space; setAnchor() takes bindToSim (the part root
   matrix at bind, incl. any presentation shift) once, and
   setHeadPose() takes the head's CURRENT matrix each frame;
   root targets = headPose * headBindInv * bindToSim * bindRoot.
   A static head therefore keeps roots exactly at bind.

   Three-free like collision.js: plain typed arrays, unit-tested
   in Node (hair-strands.test.mjs). The stage adapter converts
   three.js matrices to column-major Float32Arrays.
   ============================================================ */

import { collideSphere, collideCapsule, applyContactFriction, SelfCollider } from './collision.js';

/* ---------- tiny mat helpers (column-major 4x4 / 3x3) ---------- */
function m4MulV(m, x, y, z) {
  return [
    m[0] * x + m[4] * y + m[8] * z + m[12],
    m[1] * x + m[5] * y + m[9] * z + m[13],
    m[2] * x + m[6] * y + m[10] * z + m[14],
  ];
}
function m4RotV(m, x, y, z) {
  return [
    m[0] * x + m[4] * y + m[8] * z,
    m[1] * x + m[5] * y + m[9] * z,
    m[2] * x + m[6] * y + m[10] * z,
  ];
}
function m4Mul(a, b) { // a*b, column-major
  const o = new Float64Array(16);
  for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) {
    o[c * 4 + r] = a[r] * b[c * 4] + a[4 + r] * b[c * 4 + 1] + a[8 + r] * b[c * 4 + 2] + a[12 + r] * b[c * 4 + 3];
  }
  return o;
}
function m4Invert(m) { // affine inverse (rotation orthonormal-ish)
  const o = new Float64Array(16);
  // transpose of the 3x3 (assumes orthonormal rotation part)
  o[0] = m[0]; o[1] = m[4]; o[2] = m[8];
  o[4] = m[1]; o[5] = m[5]; o[6] = m[9];
  o[8] = m[2]; o[9] = m[6]; o[10] = m[10];
  const tx = m[12], ty = m[13], tz = m[14];
  o[12] = -(o[0] * tx + o[4] * ty + o[8] * tz);
  o[13] = -(o[1] * tx + o[5] * ty + o[9] * tz);
  o[14] = -(o[2] * tx + o[6] * ty + o[10] * tz);
  o[15] = 1;
  return o;
}
const IDENTITY16 = () => { const m = new Float64Array(16); m[0] = m[5] = m[10] = m[15] = 1; return m; };

export class StrandHairSystem {
  /* header: parsed megami-strands.json; bin: ArrayBuffer of the
     .bin (blocks: guideIdx u16 | s f32 | off 3xf32 | relA 9xf32).
     opts: { gravity [0,-9.8,0], damping 0..1 (velocity kept per
     substep ~0.98 typ), substeps (default 3), iterations (PBD
     constraint iterations per substep, default 6), bendStiffness
     0..1 (default 0.15), selfCollide: metres or 0 (default 0),
     collision: bool (default true) } */
  constructor(header, bin, opts = {}) {
    this.header = header;
    this.guides = header.guides;
    this.G = this.guides.length;
    const NV = header.counts.verts;
    this.NV = NV;
    const u16 = new Uint16Array(bin, 0, NV);
    const f32s = new Float32Array(bin, NV * 2, NV);
    const f32o = new Float32Array(bin, NV * 2 + NV * 4, NV * 3);
    const f32a = new Float32Array(bin, NV * 2 + NV * 4 + NV * 12, NV * 9);
    this.bGuide = u16; this.bS = f32s; this.bOff = f32o; this.bA = f32a;

    // particle layout: guides concatenated
    this.gStart = new Int32Array(this.G);
    this.gCount = new Int32Array(this.G);
    let P = 0;
    this.bindPts = [];   // per guide: Float64Array points (part space)
    this.restLen = [];   // per guide: Float64Array segment lengths
    this.rootFrameBind = []; // per guide {T,N,B} arrays (part space)
    for (let g = 0; g < this.G; g++) {
      const pts = this.guides[g].points;
      this.gStart[g] = P; this.gCount[g] = pts.length;
      const bp = new Float64Array(pts.length * 3);
      pts.forEach((p, i) => { bp[i * 3] = p[0]; bp[i * 3 + 1] = p[1]; bp[i * 3 + 2] = p[2]; });
      this.bindPts.push(bp);
      const rl = new Float64Array(pts.length - 1);
      for (let i = 0; i < rl.length; i++) {
        rl[i] = Math.hypot(bp[(i + 1) * 3] - bp[i * 3], bp[(i + 1) * 3 + 1] - bp[i * 3 + 1], bp[(i + 1) * 3 + 2] - bp[i * 3 + 2]);
      }
      this.restLen.push(rl);
      const rf = this.guides[g].rootFrame;
      this.rootFrameBind.push({ T: rf.T, N: rf.N, B: rf.B });
      P += pts.length;
    }
    this.P = P;
    this.pos = new Float64Array(P * 3);
    this.prev = new Float64Array(P * 3);
    this.invMass = new Float64Array(P).fill(1);
    for (let g = 0; g < this.G; g++) this.invMass[this.gStart[g]] = 0; // roots pinned
    // FRINGE RULE: guides with <=3 particles are bang wisps / cap
    // fringe — at 15-30 mm segment scale they have no meaningful
    // drape, and a single free particle inside a collider volume
    // gets teleported to the collider surface, stretching every
    // bound card (measured on the real bake: 155 mm snap on a
    // 2-particle guide). Pin them fully to the head anchor: they
    // move rigidly with the head, exactly like production fringe.
    this.fringeGuides = 0;
    for (let g = 0; g < this.G; g++) {
      if (this.gCount[g] <= 3) {
        this.fringeGuides++;
        for (let k = 0; k < this.gCount[g]; k++) this.invMass[this.gStart[g] + k] = 0;
      }
    }
    // SCALP-ATTACH RULE: when the bake ships header.bindSdf (bind
    // signed distance of every particle against the body SDF), a
    // particle authored within scalpAttachDist of the body surface
    // is ATTACHED along the scalp — cap/weave anchoring (the
    // HAIR-FIT STANDARD's attachment model; TressFX follow-strand
    // attach points). Endpoint-only guides cannot represent
    // up-swept strands that lie ON the head: unattached, they
    // swing off the scalp and drag their bound cards through the
    // body (measured: guide 65's verts 86 mm inside after settle
    // with every particle outside the SDF). Attached particles
    // are pinned to the head anchor like roots.
    this.attachDist = opts.scalpAttachDist ?? 0.012;
    this.attachedParticles = 0;
    this.pinned = new Uint8Array(P);
    for (let i = 0; i < P; i++) if (this.invMass[i] === 0) this.pinned[i] = 1;
    if (Array.isArray(header.bindSdf) && header.bindSdf.length === P) {
      for (let i = 0; i < P; i++) {
        if (this.invMass[i] !== 0 && header.bindSdf[i] < this.attachDist) {
          this.invMass[i] = 0; this.pinned[i] = 1; this.attachedParticles++;
        }
      }
    }

    this.gravity = opts.gravity || [0, -9.8, 0];
    this.damping = opts.damping ?? 0.985;
    this.substeps = opts.substeps ?? 3;
    this.iterations = opts.iterations ?? 6;
    this.bendStiffness = opts.bendStiffness ?? 0.15;
    this.collisionEnabled = opts.collision !== false;
    this.collision = null; // posed set, set via setCollision()
    this.selfCollideDist = opts.selfCollide || 0;
    this.selfCollider = this.selfCollideDist > 0 ? new SelfCollider(this.selfCollideDist) : null;
    this.selfSkip = null;
    if (this.selfCollider) {
      this.selfSkip = new Set();
      for (let g = 0; g < this.G; g++) {
        const st = this.gStart[g], cn = this.gCount[g];
        for (let k = 0; k < cn - 1; k++) this.selfSkip.add((st + k) + '_' + (st + k + 1));
        for (let k = 0; k < cn - 2; k++) this.selfSkip.add((st + k) + '_' + (st + k + 2));
      }
    }

    // frame buffers (per particle T and N; B = T x N on the fly)
    this.frT = new Float64Array(P * 3);
    this.frN = new Float64Array(P * 3);
    // anchor transforms
    this.bindToSim = IDENTITY16();
    this.headBind = IDENTITY16();     // head matrix at bind (sim frame)
    this.headPose = IDENTITY16();     // head matrix now (sim frame)
    this._rootM = IDENTITY16();       // headPose * inv(headBind) * bindToSim
    this.time = 0;
    this.initialized = false;
  }

  /* bindToSim: part-space -> sim frame at bind (part root
     matrixWorld incl. presentation shifts). headBindM: the head
     anchor's matrix at bind IN SIM FRAME. Call once. */
  setAnchor(bindToSim, headBindM) {
    this.bindToSim = Float64Array.from(bindToSim);
    this.headBind = Float64Array.from(headBindM);
    this.headPose = Float64Array.from(headBindM);
    this._updateRootM();
    this.resetToBind();
  }
  setHeadPose(headPoseM) {
    this.headPose = Float64Array.from(headPoseM);
    this._updateRootM();
  }
  _updateRootM() {
    this._rootM = m4Mul(m4Mul(this.headPose, m4Invert(this.headBind)), this.bindToSim);
  }

  /* Place all particles at their bind positions mapped to sim
     frame (pos = prev, zero velocity). */
  resetToBind() {
    const m = this.bindToSim;
    for (let g = 0; g < this.G; g++) {
      const bp = this.bindPts[g], st = this.gStart[g], cn = this.gCount[g];
      for (let k = 0; k < cn; k++) {
        const r = m4MulV(m, bp[k * 3], bp[k * 3 + 1], bp[k * 3 + 2]);
        const gi = (st + k) * 3;
        this.pos[gi] = r[0]; this.pos[gi + 1] = r[1]; this.pos[gi + 2] = r[2];
        this.prev[gi] = r[0]; this.prev[gi + 1] = r[1]; this.prev[gi + 2] = r[2];
      }
    }
    this.initialized = true;
  }

  setCollision(posedSet) { this.collision = posedSet; }

  _pinRoots() {
    const m = this._rootM;
    for (let g = 0; g < this.G; g++) {
      const bp = this.bindPts[g], st = this.gStart[g], cn = this.gCount[g];
      // every PINNED particle (roots, fringe guides, scalp-attached)
      // is placed by the head-follow root matrix: pos = rootM*bind.
      for (let k = 0; k < cn; k++) {
        if (!this.pinned[st + k]) continue;
        const r = m4MulV(m, bp[k * 3], bp[k * 3 + 1], bp[k * 3 + 2]);
        const gi = (st + k) * 3;
        this.pos[gi] = r[0]; this.pos[gi + 1] = r[1]; this.pos[gi + 2] = r[2];
        this.prev[gi] = r[0]; this.prev[gi + 1] = r[1]; this.prev[gi + 2] = r[2];
      }
    }
  }

  /* Advance the simulation by dt seconds (frame dt; split into
     substeps internally). Deterministic for fixed dt. */
  step(dt) {
    if (!this.initialized) this.resetToBind();
    const sub = Math.max(1, this.substeps | 0);
    const h = dt / sub;
    const [gx, gy, gz] = this.gravity;
    const damp = Math.pow(this.damping, 1 / sub);
    const pos = this.pos, prev = this.prev, invM = this.invMass;
    const p3 = [0, 0, 0], pr3 = [0, 0, 0], n3 = [0, 0, 0];
    for (let s = 0; s < sub; s++) {
      this._pinRoots();
      // verlet integrate (roots have invMass 0 but are pinned anyway)
      for (let i = 0; i < this.P; i++) {
        if (invM[i] === 0) continue;
        const i3 = i * 3;
        const vx = (pos[i3] - prev[i3]) * damp, vy = (pos[i3 + 1] - prev[i3 + 1]) * damp, vz = (pos[i3 + 2] - prev[i3 + 2]) * damp;
        prev[i3] = pos[i3]; prev[i3 + 1] = pos[i3 + 1]; prev[i3 + 2] = pos[i3 + 2];
        pos[i3] += vx + gx * h * h; pos[i3 + 1] += vy + gy * h * h; pos[i3 + 2] += vz + gz * h * h;
      }
      // constraint iterations: distance (length only) + bend + collision
      for (let it = 0; it < this.iterations; it++) {
        this._pinRoots();
        this._solveDistance();
        if (this.bendStiffness > 0) this._solveBend();
        if (this.collisionEnabled && this.collision) this._collideAll(p3, pr3, n3);
        if (this.selfCollider && it === this.iterations - 1) {
          const posF = Float32Array.from(pos);
          this.selfCollider.collide(posF, Float32Array.from(invM), this.selfSkip, 1);
          pos.set(posF);
        }
      }
      this._pinRoots();
    }
    this.time += dt;
  }

  _solveDistance() {
    const pos = this.pos, invM = this.invMass;
    for (let g = 0; g < this.G; g++) {
      const st = this.gStart[g], cn = this.gCount[g], rl = this.restLen[g];
      for (let k = 0; k < cn - 1; k++) {
        const i = st + k, j = i + 1, i3 = i * 3, j3 = j * 3;
        const wi = invM[i], wj = invM[j], w = wi + wj;
        if (w === 0) continue;
        let dx = pos[j3] - pos[i3], dy = pos[j3 + 1] - pos[i3 + 1], dz = pos[j3 + 2] - pos[i3 + 2];
        const d = Math.hypot(dx, dy, dz);
        if (d < 1e-12) continue;
        const diff = (d - rl[k]) / d / w;
        dx *= diff; dy *= diff; dz *= diff;
        pos[i3] += dx * wi; pos[i3 + 1] += dy * wi; pos[i3 + 2] += dz * wi;
        pos[j3] -= dx * wj; pos[j3 + 1] -= dy * wj; pos[j3 + 2] -= dz * wj;
      }
    }
  }

  _solveBend() {
    // PBD bending constraint (Müller et al. 2007 §3.5 form):
    // rest = straight continuation; pull particle k+2 toward the
    // point at rest distance from k projected — implemented as a
    // weak distance constraint between k and k+2 with rest length
    // rl[k]+rl[k+1] scaled by bendStiffness application factor.
    const pos = this.pos, invM = this.invMass, stf = this.bendStiffness;
    for (let g = 0; g < this.G; g++) {
      const st = this.gStart[g], cn = this.gCount[g], rl = this.restLen[g];
      for (let k = 0; k < cn - 2; k++) {
        const i = st + k, j = i + 2, i3 = i * 3, j3 = j * 3;
        const wi = invM[i], wj = invM[j], w = wi + wj;
        if (w === 0) continue;
        const rest = rl[k] + rl[k + 1];
        let dx = pos[j3] - pos[i3], dy = pos[j3 + 1] - pos[i3 + 1], dz = pos[j3 + 2] - pos[i3 + 2];
        const d = Math.hypot(dx, dy, dz);
        if (d < 1e-12 || d >= rest) continue; // only resist folding, never straighten past rest
        const diff = (d - rest) / d / w * stf;
        dx *= diff; dy *= diff; dz *= diff;
        pos[i3] += dx * wi; pos[i3 + 1] += dy * wi; pos[i3 + 2] += dz * wi;
        pos[j3] -= dx * wj; pos[j3 + 1] -= dy * wj; pos[j3 + 2] -= dz * wj;
      }
    }
  }

  /* Collision resolution per particle: DEEPEST-PROJECTION-WINS.
     Every collider is evaluated against the particle's ORIGINAL
     position; only the single deepest penetration is projected,
     with friction applied once using that collider's normal.
     Sequential projection against OVERLAPPING colliders ping-pongs
     a trapped particle between facing surfaces and the distance
     constraints convert the ping-pong into a slingshot (measured:
     13 m/s with the fitted r=0.2434 Spine2->Neck capsule overlapping
     Neck->Head at a guide root particle). Deepest-wins is the
     production cloth/hair practice for coincident colliders and is
     order-independent. The SDF competes by its penetration depth
     (margin - sample). */
  _collideAll(p3, pr3, n3) {
    const set = this.collision;
    const pos = this.pos, prev = this.prev;
    const spheres = set.spheres || [], capsules = set.capsules || [];
    const cand = [0, 0, 0], cn = [0, 0, 0], tn = [0, 0, 0];
    for (let i = 0; i < this.P; i++) {
      if (this.invMass[i] === 0) continue;
      const i3 = i * 3;
      const ox = pos[i3], oy = pos[i3 + 1], oz = pos[i3 + 2];
      let bestDepth = 0, bestFriction = 0.35, hasBest = false;
      p3[0] = ox; p3[1] = oy; p3[2] = oz;
      for (const sp of spheres) {
        p3[0] = ox; p3[1] = oy; p3[2] = oz;
        const d = collideSphere(p3, sp.c, sp.r, tn);
        if (d > bestDepth) {
          bestDepth = d; bestFriction = sp.friction ?? 0.35; hasBest = true;
          cand[0] = p3[0]; cand[1] = p3[1]; cand[2] = p3[2];
          cn[0] = tn[0]; cn[1] = tn[1]; cn[2] = tn[2];
        }
      }
      for (const cp of capsules) {
        p3[0] = ox; p3[1] = oy; p3[2] = oz;
        const d = collideCapsule(p3, cp.a, cp.b, cp.r, tn);
        if (d > bestDepth) {
          bestDepth = d; bestFriction = cp.friction ?? 0.35; hasBest = true;
          cand[0] = p3[0]; cand[1] = p3[1]; cand[2] = p3[2];
          cn[0] = tn[0]; cn[1] = tn[1]; cn[2] = tn[2];
        }
      }
      if (set.sdf) {
        const m = set.sdf.fromWorld;
        const lx = m[0] * ox + m[4] * oy + m[8] * oz + m[12];
        const ly = m[1] * ox + m[5] * oy + m[9] * oz + m[13];
        const lz = m[2] * ox + m[6] * oy + m[10] * oz + m[14];
        const margin = set.sdf.margin || 0;
        const sd = set.sdf.body.sample(lx, ly, lz);
        const pen = margin - sd;
        if (pen > bestDepth) {
          p3[0] = lx; p3[1] = ly; p3[2] = lz;
          const resolved = set.sdf.body.project(p3, margin);
          if (resolved > 0) {
            const w = set.sdf.toWorld;
            cand[0] = w[0] * p3[0] + w[4] * p3[1] + w[8] * p3[2] + w[12];
            cand[1] = w[1] * p3[0] + w[5] * p3[1] + w[9] * p3[2] + w[13];
            cand[2] = w[2] * p3[0] + w[6] * p3[1] + w[10] * p3[2] + w[14];
            const g = [0, 0, 0];
            set.sdf.body.gradient(lx, ly, lz, g);
            const gw = [
              w[0] * g[0] + w[4] * g[1] + w[8] * g[2],
              w[1] * g[0] + w[5] * g[1] + w[9] * g[2],
              w[2] * g[0] + w[6] * g[1] + w[10] * g[2],
            ];
            const gl = Math.hypot(gw[0], gw[1], gw[2]);
            if (gl > 1e-9) { cn[0] = gw[0] / gl; cn[1] = gw[1] / gl; cn[2] = gw[2] / gl; }
            else { cn[0] = cand[0] - ox; cn[1] = cand[1] - oy; cn[2] = cand[2] - oz; const cl = Math.hypot(cn[0], cn[1], cn[2]) || 1; cn[0] /= cl; cn[1] /= cl; cn[2] /= cl; }
            bestDepth = pen; bestFriction = set.sdf.friction ?? 0.35; hasBest = true;
          }
        }
      }
      if (hasBest) {
        p3[0] = cand[0]; p3[1] = cand[1]; p3[2] = cand[2];
        pr3[0] = prev[i3]; pr3[1] = prev[i3 + 1]; pr3[2] = prev[i3 + 2];
        n3[0] = cn[0]; n3[1] = cn[1]; n3[2] = cn[2];
        applyContactFriction(p3, pr3, n3, bestFriction);
        pos[i3] = p3[0]; pos[i3 + 1] = p3[1]; pos[i3 + 2] = p3[2];
        prev[i3] = pr3[0]; prev[i3 + 1] = pr3[1]; prev[i3 + 2] = pr3[2];
      }
    }
  }

  /* Frames per particle. POINT frames, matching the bake exactly:
     T at particle k uses the CENTRED difference (segments k-1,k)
     — the bake's rmfFrames; then N is parallel-transported along
     those tangents (Rodrigues form, same as the bake). Root frame:
     the baked bind root frame carried by the root matrix — at
     bind this reproduces the bake's frames to float precision
     (gated in the unit tests against the real bake + GLB). */
  _computeFrames() {
    const pos = this.pos;
    const m = this._rootM;
    for (let g = 0; g < this.G; g++) {
      const st = this.gStart[g], cn = this.gCount[g];
      const rf = this.rootFrameBind[g];
      let Tx = 0, Ty = 0, Tz = 0, Nx = 0, Ny = 0, Nz = 0;
      let pTx = 0, pTy = 0, pTz = 0; // previous tangent (transport)
      for (let k = 0; k < cn; k++) {
        const gi = st + k, g3 = gi * 3;
        // centred-difference tangent at this particle
        const ia = (st + Math.max(0, k - 1)) * 3, ib = (st + Math.min(cn - 1, k + 1)) * 3;
        let ux = pos[ib] - pos[ia], uy = pos[ib + 1] - pos[ia + 1], uz = pos[ib + 2] - pos[ia + 2];
        const ul = Math.hypot(ux, uy, uz);
        if (ul > 1e-12) { ux /= ul; uy /= ul; uz /= ul; } else { ux = pTx; uy = pTy; uz = pTz; }
        if (k === 0) {
          // seed N from the baked root frame rotated by rootM
          const nB = m4RotV(m, rf.N[0], rf.N[1], rf.N[2]);
          Nx = nB[0]; Ny = nB[1]; Nz = nB[2];
          const d = Nx * ux + Ny * uy + Nz * uz;
          Nx -= d * ux; Ny -= d * uy; Nz -= d * uz;
          const nl = Math.hypot(Nx, Ny, Nz);
          if (nl > 1e-9) { Nx /= nl; Ny /= nl; Nz /= nl; } else { Nx = 1; Ny = 0; Nz = 0; }
        } else {
          // parallel transport N by the rotation prevT -> T (bake form)
          let ax = pTy * uz - pTz * uy, ay = pTz * ux - pTx * uz, az = pTx * uy - pTy * ux;
          const s = Math.hypot(ax, ay, az), co = pTx * ux + pTy * uy + pTz * uz;
          if (s >= 1e-9) {
            ax /= s; ay /= s; az /= s;
            const ang = Math.atan2(s, co), sn = Math.sin(ang), cs = Math.cos(ang);
            const kd = ax * Nx + ay * Ny + az * Nz;
            const kx = ay * Nz - az * Ny, ky = az * Nx - ax * Nz, kz = ax * Ny - ay * Nx;
            Nx += kx * sn + ax * kd * (1 - cs);
            Ny += ky * sn + ay * kd * (1 - cs);
            Nz += kz * sn + az * kd * (1 - cs);
          }
          const d = Nx * ux + Ny * uy + Nz * uz;
          Nx -= d * ux; Ny -= d * uy; Nz -= d * uz;
          const nl = Math.hypot(Nx, Ny, Nz) || 1e-12;
          Nx /= nl; Ny /= nl; Nz /= nl;
        }
        Tx = ux; Ty = uy; Tz = uz;
        pTx = Tx; pTy = Ty; pTz = Tz;
        this.frT[g3] = Tx; this.frT[g3 + 1] = Ty; this.frT[g3 + 2] = Tz;
        this.frN[g3] = Nx; this.frN[g3 + 1] = Ny; this.frN[g3 + 2] = Nz;
      }
    }
  }

  /* Write deformed strand vertex positions (SIM frame) into
     out (Float32Array, NV*3, bake vert order). The stage converts
     sim -> geometry space with the inverse part-root matrix.
     Formula identical to the bake's deformVert:
       pos = P_g(s) + Frame_g(s) * (relA * off). */
  deform(out) {
    this._computeFrames();
    const pos = this.pos, frT = this.frT, frN = this.frN;
    const { bGuide, bS, bOff, bA } = this;
    for (let v = 0; v < this.NV; v++) {
      const g = bGuide[v];
      const st = this.gStart[g], cn = this.gCount[g];
      const s = Math.min(bS[v], cn - 1);
      const i = Math.min(Math.floor(s), Math.max(0, cn - 2));
      const f = Math.min(1, Math.max(0, s - i));
      const gi = st + i, gj = gi + 1, g3 = gi * 3, h3 = gj * 3;
      const Px = pos[g3] + (pos[h3] - pos[g3]) * f;
      const Py = pos[g3 + 1] + (pos[h3 + 1] - pos[g3 + 1]) * f;
      const Pz = pos[g3 + 2] + (pos[h3 + 2] - pos[g3 + 2]) * f;
      // frame lerp (T,N), B = T x N after orthonormalization
      let Tx = frT[g3] + (frT[h3] - frT[g3]) * f, Ty = frT[g3 + 1] + (frT[h3 + 1] - frT[g3 + 1]) * f, Tz = frT[g3 + 2] + (frT[h3 + 2] - frT[g3 + 2]) * f;
      let tl = Math.hypot(Tx, Ty, Tz) || 1e-12; Tx /= tl; Ty /= tl; Tz /= tl;
      let Nx = frN[g3] + (frN[h3] - frN[g3]) * f, Ny = frN[g3 + 1] + (frN[h3 + 1] - frN[g3 + 1]) * f, Nz = frN[g3 + 2] + (frN[h3 + 2] - frN[g3 + 2]) * f;
      const dn = Nx * Tx + Ny * Ty + Nz * Tz;
      Nx -= dn * Tx; Ny -= dn * Ty; Nz -= dn * Tz;
      const nl = Math.hypot(Nx, Ny, Nz) || 1e-12; Nx /= nl; Ny /= nl; Nz /= nl;
      const Bx = Ty * Nz - Tz * Ny, By = Tz * Nx - Tx * Nz, Bz = Tx * Ny - Ty * Nx;
      const o3 = v * 3, a9 = v * 9;
      const ox = bOff[o3], oy = bOff[o3 + 1], oz = bOff[o3 + 2];
      const gx = bA[a9] * ox + bA[a9 + 1] * oy + bA[a9 + 2] * oz;
      const gy = bA[a9 + 3] * ox + bA[a9 + 4] * oy + bA[a9 + 5] * oz;
      const gz = bA[a9 + 6] * ox + bA[a9 + 7] * oy + bA[a9 + 8] * oz;
      out[o3] = Px + Tx * gx + Nx * gy + Bx * gz;
      out[o3 + 1] = Py + Ty * gx + Ny * gy + By * gz;
      out[o3 + 2] = Pz + Tz * gx + Nz * gy + Bz * gz;
    }
  }

  /* Particle positions (Float64Array, P*3, sim frame) — the
     guide-level truth used by tests and stage diagnostics. */
  particlePositions() { return this.pos; }
  particleCount() { return this.P; }
  guideStart(g) { return this.gStart[g]; }
  guideCount(g) { return this.gCount[g]; }
  guideRestLengths(g) { return this.restLen[g]; }
}
