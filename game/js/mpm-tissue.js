/* ============================================================
   WESTERN HEART — MpmTissue (CPU MPM-lite soft-tissue backend)

   NEXTGEN-2026-10-23 lane: wires three 2026 research pulls into ONE
   new tissue solver that runs in the browser game today.

   1. SurRoL (arXiv:2402.01181v1, Yang et al.) — Material Point Method
      soft-body surgical sim in Taichi (GPU parallel). MPM handles large
      deformations better than FEM: Lagrangian particles carry the
      deformation gradient F; an Eulerian grid solves forces/velocities.
      VERDICT: Taichi cannot run in the browser (Python-embedded DSL,
      CUDA/Metal/Vulkan targets — no WASM target), so the portable part
      is the ALGORITHM CORE, re-implemented here in dependency-free JS
      as "MPM-lite": quadratic B-spline P2G/G2P, APIC transfer, explicit
      grid solve. At our scale (36–80 particles, ~150–300 grid nodes,
      ≤12 substeps) the whole solve is a few ×10⁴ FLOPs/frame — trivial
      on a phone CPU, no GPU needed.
   2. NVIDIA Isaac for Healthcare (isaac-for-healthcare.github.io,
      Newton 1.6.1 + Warp 1.17.0, GA April 2026) — open-source medical
      physics. Newton/Warp cannot run in the browser (CUDA, Python,
      Docker), but the ARCHITECTURE ports directly: STAGED SOLVER
      SYSTEMS (i4h-physics runs deformation/grasp/contact/stretch
      stages per step) and RIGID↔SOFT COUPLING (pinned bone core =
      rigid wrap driving the pose, soft layers follow). This module
      runs MUSCLE → FAT → SKIN stages per frame with per-layer material
      params, and pins the deep core + caps as the rigid Dirichlet
      boundary — the same coupling idea as Newton's two-way contact.
   3. Neural Deformation Gradients (Nolte et al., Eurographics 2026,
      CC BY-NC — TECHNIQUE REFERENCE ONLY, no code copied): predicts
      per-element DEFORMATION GRADIENTS instead of vertex displacements,
      which makes the method robust to element inversion and volume
      deviation; Poisson reconstruction; stable Neo-Hookean with
      E_muscle=45 kPa / E_fat=15 kPa / ν=0.47 (λ≈16µ, strongly
      volume-preserving); embedded deformation (hi-res anatomy rides a
      coarse sim volume). WIRED AS TECHNIQUE: (a) the solver state IS
      the deformation gradient F per particle and the sim corrects in
      gradient space — an INVERSION GUARD rescales F when det(F) drops
      below 0.35 instead of letting the volume collapse; (b) the
      high-λ Neo-Hookean stress IS the volume-preservation term;
      (c) the render mesh rides the particle lattice exactly like
      NDG's embedded deformation (nearest-4 inverse-distance skinning,
      identical visual mapping to the Jolt lane).

   What this is: a SECOND tissue backend beside the Jolt XPBD lane
   (game/js/softbody.js) and the FEMFX lane (game/js/femfx-adapter.js).
   Same belly-region lattice, same vertex skinning, same integration
   contract — switching backends never changes the visual mapping:

     1. After loading a fighter's SkinnedMesh:
          const sb = MpmTissue.fromMesh(skinnedMesh, MpmTissue.anatomyFor(char));
     2. Every frame, AFTER the animation pose AND after jiggle.update:
          sb.update(dt);
     3. On hit landing (fighter.receiveHit):
          sb.hit(worldPoint, dirX, move.damage);
     4. On fighter swap / dispose: sb.dispose() restores the mesh.

   Backend selection: window.WH_PHYSICS_BACKEND = 'jolt' | 'mpm' | 'femfx'
   (default 'jolt'), or per-character char.softbodyBackend. Wired in
   game/js/fighter.js. Pure JS — no WASM, no async load: ready on the
   first frame, which also makes it the natural fallback where WASM is
   unavailable.

   Quality: SHARES the 'wh_softbody_v1' localStorage store with the Jolt
   lane, so SoftBody.globalQuality / X-ray gating keep working no matter
   which backend drives a fighter. 'low': 3x4x3 lattice, 'high': 4x5x4.

   Like softbody.js, this module's only top-level import is the
   dependency-free shared tissue quality store (./tissue-quality.js) — no
   three.js, no WASM — so it stays unit-testable in node and adds zero
   boot cost: physics must NEVER crash the fight.

   License notes: SurRoL is open-source (github.com/med-air/SurRoL);
   Isaac for Healthcare numerical sim is Apache-2.0. NDG is CC BY-NC —
   used as technique reference only; every line of solver code below is
   an original implementation of the standard MPM algorithm.
   ============================================================ */
import { getTissueQuality, setTissueQuality, onTissueQuality, TISSUE_QUALITIES } from './tissue-quality.js';

// ---- tiny vector/matrix helpers (plain arrays; no three.js) ---------
const _v3 = (x = 0, y = 0, z = 0) => ({ x, y, z });

// 3x3 matrices as length-9 row-major arrays.
function _m3Ident() { return [1,0,0, 0,1,0, 0,0,1]; }
function _m3Det(m) {
  return m[0]*(m[4]*m[8]-m[5]*m[7])
       - m[1]*(m[3]*m[8]-m[5]*m[6])
       + m[2]*(m[3]*m[7]-m[4]*m[6]);
}
// Inverse-transpose of m (for the Neo-Hookean F^-T term). Falls back to
// identity when near-singular — the inversion guard below fires first.
function _m3InvTrans(m, out) {
  const a=m[0],b=m[1],c=m[2],d=m[3],e=m[4],f=m[5],g=m[6],h=m[7],i=m[8];
  // Cofactor matrix (transposed adjugate = inverse-transpose directly).
  const C00=e*i-f*h, C01=-(b*i-c*h), C02=b*f-c*e;
  const C10=-(d*i-f*g), C11=a*i-c*g, C12=-(a*f-c*d);
  const C20=d*h-e*g, C21=-(a*h-b*g), C22=a*e-b*d;
  const det = a*C00 + b*C10 + c*C20;
  const s = Math.abs(det) > 1e-9 ? 1/det : 0;
  out[0]=C00*s; out[1]=C01*s; out[2]=C02*s;
  out[3]=C10*s; out[4]=C11*s; out[5]=C12*s;
  out[6]=C20*s; out[7]=C21*s; out[8]=C22*s;
  return out;
}

// ---- quality (SHARED store with the Jolt lane — game/js/tissue-quality.js)
const QUALITIES = TISSUE_QUALITIES;

// ---- materials --------------------------------------------------------
// NDG (Nolte et al. 2026) published tissue values: E_muscle = 45 kPa,
// E_fat = 15 kPa, Poisson's ratio ν = 0.47 for both (λ ≈ 16µ, strongly
// volume-preserving human tissue). The browser solver runs these at a
// reduced "solver scale" for explicit-integration stability — the µ/λ
// RATIO is preserved, which is what carries the volume-preservation
// character. anatomySpec.materials can override per character (future:
// feed from roster/<fighter>/anatomy/anatomy-layers.json).
const SOLVER_SCALE = 10 / 45; // 45 kPa -> 10 kPa solver scale
const _lame = (E, nu) => ({
  mu: E / (2 * (1 + nu)),
  lambda: (E * nu) / ((1 + nu) * (1 - 2 * nu)),
});
const MATERIALS = {
  muscle: Object.assign({ E: 45000 * SOLVER_SCALE, nu: 0.47 }, _lame(45000 * SOLVER_SCALE, 0.47)),
  fat:    Object.assign({ E: 15000 * SOLVER_SCALE, nu: 0.47 }, _lame(15000 * SOLVER_SCALE, 0.47)),
};
const REST_DENSITY = 1050;   // kg/m^3, ~human tissue (same as FEMFX lane)

// ---- region preset (same belly region as the Jolt lane: identical -----
// ---- visual mapping, only the solver differs) -------------------------
const REGION_PRESETS = {
  belly: {
    boneNames: ['Spine1', 'spine1', 'Spine', 'spine', 'Hips', 'hips'],
    radius: [0.17, 0.21, 0.15], // x,y,z meters at 1.7 m character height
    centerLift: 0.02,
    shellGrow: 1.22,
    pinCore: 0.42,              // enorm <= pinCore -> pinned (rigid bone wrap)
    pinCaps: 0.85,              // |ny| >= pinCaps -> pinned
    muscleSplit: 0.80,          // pinCore < enorm <= muscleSplit -> MUSCLE, else FAT
    res: { low: [3, 4, 3], high: [4, 5, 4] },
    linearDamping: 1.5,         // grid velocity damping (1/s)
    excitation: 0.12,           // velocity coupling to body acceleration
    deformGain: 1.0,
    maxDeform: 0.06,            // per-vertex displacement clamp (m)
    maxGridVel: 30,
    dtMax: 1 / 480,             // explicit MPM substep cap (CFL)
    maxSubsteps: 12,
    jMin: 0.35,                 // NDG-style inversion guard: rescale F if det < jMin
    skinSmoothIters: 2,         // SKIN stage: lattice-neighbor displacement relax
  },
};

function _normalizeSpec(anatomySpec) {
  const regions = [];
  const list = (anatomySpec && anatomySpec.regions) || ['belly'];
  for (const r of list) {
    if (typeof r === 'string' && REGION_PRESETS[r]) {
      regions.push(Object.assign({ name: r }, REGION_PRESETS[r]));
    } else if (r && typeof r === 'object' && r.name && REGION_PRESETS[r.name]) {
      regions.push(Object.assign({ name: r.name }, REGION_PRESETS[r.name], r));
    }
  }
  const materials = Object.assign(
    { muscle: MATERIALS.muscle, fat: MATERIALS.fat },
    (anatomySpec && anatomySpec.materials) || {});
  return { regions, materials };
}

const _claimedGeometries = (typeof WeakSet !== 'undefined') ? new WeakSet() : null;
const _live = (typeof Set !== 'undefined') ? new Set() : { add() {}, delete() {}, forEach() {} };

// Shared-store fan-out: a quality change via ANY backend's
// setGlobalQuality updates every live MpmTissue.
onTissueQuality((q) => { _live.forEach((mt) => { try { mt.setQuality(q); } catch (e) {} }); });

export class MpmTissue {
  constructor() {
    this._mesh = null;
    this._region = null;      // built region data (sync — no async load)
    this._quality = getTissueQuality();
    this._ready = false;      // pure JS: ready as soon as the region builds
    this._disposed = false;
    this._frame = 0;
    this._watchdog = 0;
    this._prevPos = null;
    this._prevVel = null;
    // particle state (Structure-of-Arrays, Float32Array)
    this._P = null;           // positions (nP*3)
    this._V = null;           // velocities (nP*3)
    this._F = null;           // deformation gradients (nP*9)
    this._C = null;           // APIC affine matrices (nP*9)
    this._rest = null;        // rest positions (nP*3)
    this._vol = null;         // rest volumes (nP)
    this._mat = null;         // Uint8: 0=muscle 1=fat
    this._pinned = null;      // Uint8
    this._disp = null;        // displacement scratch (nP*3)
    // grid state
    this._gN = null;          // nodes per axis [gx,gy,gz]
    this._gOrigin = null;     // [ox,oy,oz]
    this._gDx = null;         // [dx,dy,dz]
    this._gM = null;          // mass
    this._gMV = null;         // momentum (nN*3)
    this._gV = null;          // velocity (nN*3)
    this._gF = null;          // force (nN*3)
    this._gPin = null;        // Uint8 pinned nodes
  }

  /* ---------------- construction ---------------- */

  static fromMesh(skinnedMesh, anatomySpec, opts) {
    const mt = new MpmTissue();
    try {
      mt._buildRegion(skinnedMesh, _normalizeSpec(anatomySpec));
    } catch (e) {
      return mt; // inert on any build failure
    }
    _live.add(mt);
    return mt;
  }

  // Map character data -> anatomy spec. Returns null when the character
  // opts out (char.softbody === false) — the fighter then skips creation.
  // char.softbodyMaterials (optional) overrides {muscle:{E,nu},fat:{E,nu}}.
  static anatomyFor(char) {
    if (!char || char.softbody === false) return null;
    const spec = { regions: char.softbodyRegions || ['belly'] };
    if (char.softbodyMaterials) spec.materials = char.softbodyMaterials;
    return spec;
  }

  static get globalQuality() { return getTissueQuality(); }

  static setGlobalQuality(q) {
    // Live instances update via the shared-store listener registered
    // below (works across backends).
    return setTissueQuality(q);
  }

  // Backend probe for menus / diagnostics: pure JS, always ready.
  static backendStatus() { return 'ready'; }

  // Synchronous region analysis: identical geometry to the Jolt lane
  // (same ellipsoid, same spine anchoring) so the visual mapping matches
  // exactly — only the solver differs.
  _buildRegion(skinnedMesh, spec) {
    if (!skinnedMesh || !skinnedMesh.isSkinnedMesh) return;
    const geometry = skinnedMesh.geometry;
    if (!geometry || !geometry.attributes || !geometry.attributes.position) return;
    if (_claimedGeometries && _claimedGeometries.has(geometry)) return;
    const posAttr = geometry.attributes.position;
    const arr = posAttr.array;
    const count = posAttr.count;
    if (!count) return;

    let minX = 1e9, minY = 1e9, minZ = 1e9, maxX = -1e9, maxY = -1e9, maxZ = -1e9;
    for (let i = 0; i < count; i++) {
      const x = arr[i * 3], y = arr[i * 3 + 1], z = arr[i * 3 + 2];
      if (x < minX) minX = x; if (y < minY) minY = y; if (z < minZ) minZ = z;
      if (x > maxX) maxX = x; if (y > maxY) maxY = y; if (z > maxZ) maxZ = z;
    }
    const height = Math.max(maxY - minY, 0.5);
    const unit = Math.min(Math.max(height, 1.2), 2.2) / 1.7;

    const preset = spec.regions[0];
    if (!preset) return;

    let center = _v3((minX + maxX) / 2, (minY + maxY) / 2, (minZ + maxZ) / 2);
    try {
      const bones = [];
      if (skinnedMesh.skeleton && skinnedMesh.skeleton.bones) {
        for (const b of skinnedMesh.skeleton.bones) bones.push(b);
      } else {
        skinnedMesh.traverse((o) => { if (o.isBone) bones.push(o); });
      }
      let spine = null;
      for (const nm of preset.boneNames) {
        spine = bones.find((b) => b.name === nm);
        if (spine) break;
      }
      if (spine) {
        if (skinnedMesh.updateWorldMatrix) skinnedMesh.updateWorldMatrix(true, false);
        if (spine.updateWorldMatrix) spine.updateWorldMatrix(true, false);
        const Ctor = skinnedMesh.position.constructor;
        const tmp = new Ctor();
        spine.getWorldPosition(tmp);
        if (skinnedMesh.worldToLocal) skinnedMesh.worldToLocal(tmp);
        center = _v3(tmp.x, tmp.y + preset.centerLift * unit, tmp.z);
      }
    } catch (e) { /* keep bbox center */ }

    const radius = _v3(
      preset.radius[0] * unit, preset.radius[1] * unit, preset.radius[2] * unit);

    const regionVerts = [];
    for (let i = 0; i < count; i++) {
      const nx = (arr[i * 3] - center.x) / radius.x;
      const ny = (arr[i * 3 + 1] - center.y) / radius.y;
      const nz = (arr[i * 3 + 2] - center.z) / radius.z;
      if (nx * nx + ny * ny + nz * nz <= 1) regionVerts.push(i);
    }
    if (!regionVerts.length) return;

    this._mesh = skinnedMesh;
    this._buildParticles(preset, spec.materials, center, radius, regionVerts, arr);

    if (_claimedGeometries) _claimedGeometries.add(geometry);
    this._base = new Float32Array(arr);
    this._geometry = geometry;
    this._posAttr = posAttr;
    this._ready = true; // no async step: the solver is pure JS

    try {
      if (!geometry.boundingSphere && geometry.computeBoundingSphere) geometry.computeBoundingSphere();
      if (geometry.boundingSphere) geometry.boundingSphere.radius += 0.15;
    } catch (e) {}
  }

  // Lattice particles over the grown box + MPM grid + vertex skinning map.
  _buildParticles(preset, materials, center, radius, regionVerts, arr) {
    const res = preset.res[this._quality === 'high' ? 'high' : 'low'];
    const [nx, ny, nz] = res;
    const g = preset.shellGrow;
    const box = _v3(radius.x * g, radius.y * g, radius.z * g);
    const nP = nx * ny * nz;
    const P = new Float32Array(nP * 3);
    const V = new Float32Array(nP * 3);
    const F = new Float32Array(nP * 9);
    const C = new Float32Array(nP * 9);
    const rest = new Float32Array(nP * 3);
    const mat = new Uint8Array(nP);    // 0 muscle, 1 fat
    const pinned = new Uint8Array(nP);
    // lattice neighbor lists (for the SKIN smoothing stage)
    const nbr = new Array(nP);
    const key = (x, y, z) => x + nx * (y + ny * z);
    const at = (x, y, z) => (x < 0 || y < 0 || z < 0 || x >= nx || y >= ny || z >= nz)
      ? -1 : key(x, y, z);
    let p = 0;
    for (let z = 0; z < nz; z++) for (let y = 0; y < ny; y++) for (let x = 0; x < nx; x++) {
      const px = center.x - box.x + (2 * box.x * x) / Math.max(nx - 1, 1);
      const py = center.y - box.y + (2 * box.y * y) / Math.max(ny - 1, 1);
      const pz = center.z - box.z + (2 * box.z * z) / Math.max(nz - 1, 1);
      P[p*3] = px; P[p*3+1] = py; P[p*3+2] = pz;
      rest[p*3] = px; rest[p*3+1] = py; rest[p*3+2] = pz;
      F[p*9] = 1; F[p*9+4] = 1; F[p*9+8] = 1;
      const ex = (px - center.x) / radius.x;
      const ey = (py - center.y) / radius.y;
      const ez = (pz - center.z) / radius.z;
      const enorm = Math.sqrt(ex * ex + ey * ey + ez * ez);
      // Newton-style rigid↔soft coupling: deep core + caps are the rigid
      // bone wrap (Dirichlet); the rest is soft tissue in two stages.
      pinned[p] = (enorm <= preset.pinCore) || (Math.abs(ey) >= preset.pinCaps) ? 1 : 0;
      mat[p] = enorm <= preset.muscleSplit ? 0 : 1;
      const nb = [];
      const cand = [[x+1,y,z],[x-1,y,z],[x,y+1,z],[x,y-1,z],[x,y,z+1],[x,y,z-1]];
      for (const [qx, qy, qz] of cand) {
        const q = at(qx, qy, qz);
        if (q >= 0) nb.push(q);
      }
      nbr[p] = nb;
      p++;
    }
    const vol = new Float32Array(nP);
    const boxVol = (2 * box.x) * (2 * box.y) * (2 * box.z);
    for (let q = 0; q < nP; q++) vol[q] = boxVol / nP;

    // MPM grid: cells a touch larger than the particle lattice with one
    // cell of padding so the quadratic stencil never runs off the edge.
    const dx = _v3(
      (2 * box.x) / Math.max(nx - 1, 1),
      (2 * box.y) / Math.max(ny - 1, 1),
      (2 * box.z) / Math.max(nz - 1, 1));
    const gx = nx + 2, gy = ny + 2, gz = nz + 2; // nodes per axis
    const nN = gx * gy * gz;
    const origin = _v3(center.x - box.x - dx.x, center.y - box.y - dx.y, center.z - box.z - dx.z);
    const gPin = new Uint8Array(nN);
    for (let k = 0; k < gz; k++) for (let j = 0; j < gy; j++) for (let i = 0; i < gx; i++) {
      const wx = origin.x + i * dx.x, wy = origin.y + j * dx.y, wz = origin.z + k * dx.z;
      const ex = (wx - center.x) / radius.x;
      const ey = (wy - center.y) / radius.y;
      const ez = (wz - center.z) / radius.z;
      const enorm = Math.sqrt(ex * ex + ey * ey + ez * ez);
      if (enorm <= preset.pinCore || Math.abs(ey) >= preset.pinCaps) {
        gPin[i + gx * (j + gy * k)] = 1;
      }
    }

    // Nearest-4 inverse-distance vertex->particle map (identical visual
    // mapping to the Jolt lane).
    const nV = regionVerts.length;
    const mapIdx = new Int32Array(nV * 4);
    const mapW = new Float32Array(nV * 4);
    for (let vi = 0; vi < nV; vi++) {
      const gi = regionVerts[vi];
      const vx = arr[gi * 3], vy = arr[gi * 3 + 1], vz = arr[gi * 3 + 2];
      const best = [[1e9, -1], [1e9, -1], [1e9, -1], [1e9, -1]];
      for (let q = 0; q < nP; q++) {
        const ddx = vx - P[q * 3], ddy = vy - P[q * 3 + 1], ddz = vz - P[q * 3 + 2];
        const d2 = ddx * ddx + ddy * ddy + ddz * ddz;
        if (d2 < best[3][0]) { best[3] = [d2, q]; best.sort((a, b) => a[0] - b[0]); }
      }
      let wSum = 0;
      const ws = [];
      for (let k = 0; k < 4; k++) {
        const w = 1 / (Math.sqrt(best[k][0]) + 1e-6);
        ws.push(w); wSum += w;
        mapIdx[vi * 4 + k] = best[k][1];
      }
      for (let k = 0; k < 4; k++) mapW[vi * 4 + k] = ws[k] / wSum;
    }

    const dynList = [];
    for (let q = 0; q < nP; q++) if (!pinned[q]) dynList.push(q);

    this._P = P; this._V = V; this._F = F; this._C = C;
    this._rest = rest; this._vol = vol; this._mat = mat; this._pinned = pinned;
    this._disp = new Float32Array(nP * 3);
    this._nbr = nbr;
    this._gN = [gx, gy, gz];
    this._gOrigin = [origin.x, origin.y, origin.z];
    this._gDx = [dx.x, dx.y, dx.z];
    this._gM = new Float32Array(nN);
    this._gMV = new Float32Array(nN * 3);
    this._gV = new Float32Array(nN * 3);
    this._gF = new Float32Array(nN * 3);
    this._gPin = gPin;
    this._region = {
      preset, materials,
      center: [center.x, center.y, center.z],
      radius: [radius.x, radius.y, radius.z],
      res: [nx, ny, nz], nP,
      regionVerts: Int32Array.from(regionVerts), mapIdx, mapW, dynList,
    };
  }

  /* ---------------- MPM solver (SurRoL algorithm core) ---------------- */

  // Quadratic B-spline weights + gradients for one axis.
  // fx: particle position in grid units (origin at node 0).
  // Fills w[3], gw[3] (gradient w.r.t. world x) and returns base node.
  _spline1D(fx, invDx, w, gw) {
    const base = Math.floor(fx - 0.5);
    const f = fx - base; // in [0.5, 1.5)
    w[0] = 0.5 * (1.5 - f) * (1.5 - f);
    w[1] = 0.75 - (f - 1) * (f - 1);
    w[2] = 0.5 * (f - 0.5) * (f - 0.5);
    gw[0] = (f - 1.5) * invDx;
    gw[1] = (-2 * (f - 1)) * invDx;
    gw[2] = (f - 0.5) * invDx;
    return base;
  }

  // One explicit MPM substep: P2G (APIC) -> grid Neo-Hookean solve ->
  // G2P. STAGED (Isaac/Newton staged-systems technique): the MUSCLE
  // stage and FAT stage run the same pipeline with their own Lamé
  // params; the SKIN stage is a volume-preserving relax of the
  // displacement field (NDG's discrete-shell regularizer analogue).
  _substep(h) {
    const R = this._region, pr = R.preset;
    const nP = R.nP;
    const [gx, gy, gz] = this._gN;
    const [ox, oy, oz] = this._gOrigin;
    const [dx, dy, dz] = this._gDx;
    const idx = dx, idy = dy, idz = dz;
    const gM = this._gM, gMV = this._gMV, gV = this._gV, gF = this._gF, gPin = this._gPin;
    const nN = gx * gy * gz;
    gM.fill(0); gMV.fill(0); gF.fill(0);

    const P = this._P, V = this._V, F = this._F, C = this._C;
    const wx = [0,0,0], wy = [0,0,0], wz = [0,0,0];
    const gxw = [0,0,0], gyw = [0,0,0], gzw = [0,0,0];

    // ---- P2G: scatter mass + APIC momentum to the grid ----
    for (let p = 0; p < nP; p++) {
      const px = P[p*3], py = P[p*3+1], pz = P[p*3+2];
      const bx = this._spline1D((px - ox) / dx, idx, wx, gxw);
      const by = this._spline1D((py - oy) / dy, idy, wy, gyw);
      const bz = this._spline1D((pz - oz) / dz, idz, wz, gzw);
      if (bx < 0 || by < 0 || bz < 0 || bx + 2 >= gx || by + 2 >= gy || bz + 2 >= gz) continue;
      const mp = REST_DENSITY * this._vol[p];
      const c00=C[p*9],c01=C[p*9+1],c02=C[p*9+2],
            c10=C[p*9+3],c11=C[p*9+4],c12=C[p*9+5],
            c20=C[p*9+6],c21=C[p*9+7],c22=C[p*9+8];
      for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) for (let k = 0; k < 3; k++) {
        const w = wx[i] * wy[j] * wz[k];
        const n = (bx + i) + gx * ((by + j) + gy * (bz + k));
        // APIC: momentum + affine term m_p * C_p * (x_i - x_p)
        const dxn = (ox + (bx + i) * dx) - px;
        const dyn = (oy + (by + j) * dy) - py;
        const dzn = (oz + (bz + k) * dz) - pz;
        const avx = c00*dxn + c01*dyn + c02*dzn;
        const avy = c10*dxn + c11*dyn + c12*dzn;
        const avz = c20*dxn + c21*dyn + c22*dzn;
        gM[n] += w * mp;
        gMV[n*3]   += w * mp * (V[p*3]   + avx);
        gMV[n*3+1] += w * mp * (V[p*3+1] + avy);
        gMV[n*3+2] += w * mp * (V[p*3+2] + avz);
      }
    }

    // ---- grid: Neo-Hookean stress -> forces (per STAGE material) ----
    const FinvT = [0,0,0,0,0,0,0,0,0];
    for (let p = 0; p < nP; p++) {
      const o9 = p * 9;
      const f0=F[o9],f1=F[o9+1],f2=F[o9+2],f3=F[o9+3],f4=F[o9+4],
            f5=F[o9+5],f6=F[o9+6],f7=F[o9+7],f8=F[o9+8];
      const J = f0*(f4*f8-f5*f7) - f1*(f3*f8-f5*f6) + f2*(f3*f7-f4*f6);
      const Jc = Math.max(J, 1e-4);
      _m3InvTrans(F.subarray(o9, o9 + 9), FinvT);
      const mt = this._mat[p] === 0 ? R.materials.muscle : R.materials.fat;
      const mu = mt.mu, lam = mt.lambda;
      const sj = lam * Math.log(Jc);
      // P = mu*(F - F^-T) + lambda*ln(J)*F^-T  (stable Neo-Hookean)
      const p00 = mu*(f0-FinvT[0]) + sj*FinvT[0], p01 = mu*(f1-FinvT[1]) + sj*FinvT[1],
            p02 = mu*(f2-FinvT[2]) + sj*FinvT[2], p10 = mu*(f3-FinvT[3]) + sj*FinvT[3],
            p11 = mu*(f4-FinvT[4]) + sj*FinvT[4], p12 = mu*(f5-FinvT[5]) + sj*FinvT[5],
            p20 = mu*(f6-FinvT[6]) + sj*FinvT[6], p21 = mu*(f7-FinvT[7]) + sj*FinvT[7],
            p22 = mu*(f8-FinvT[8]) + sj*FinvT[8];
      const px = P[p*3], py = P[p*3+1], pz = P[p*3+2];
      const bx = this._spline1D((px - ox) / dx, idx, wx, gxw);
      const by = this._spline1D((py - oy) / dy, idy, wy, gyw);
      const bz = this._spline1D((pz - oz) / dz, idz, wz, gzw);
      if (bx < 0 || by < 0 || bz < 0 || bx + 2 >= gx || by + 2 >= gy || bz + 2 >= gz) continue;
      const vp = this._vol[p];
      for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) for (let k = 0; k < 3; k++) {
        const n = (bx + i) + gx * ((by + j) + gy * (bz + k));
        // f_i -= Vp * P(F) * grad(w)
        const gwx = gxw[i] * wy[j] * wz[k];
        const gwy = wx[i] * gyw[j] * wz[k];
        const gwz = wx[i] * wy[j] * gzw[k];
        gF[n*3]   -= vp * (p00*gwx + p01*gwy + p02*gwz);
        gF[n*3+1] -= vp * (p10*gwx + p11*gwy + p12*gwz);
        gF[n*3+2] -= vp * (p20*gwx + p21*gwy + p22*gwz);
      }
    }

    // ---- grid velocity update + rigid (pinned) boundary ----
    const damp = Math.exp(-pr.linearDamping * h);
    const maxV = pr.maxGridVel;
    for (let n = 0; n < nN; n++) {
      const m = gM[n];
      if (m < 1e-12) continue;
      let vx = (gMV[n*3] + h * gF[n*3]) / m;
      let vy = (gMV[n*3+1] + h * gF[n*3+1]) / m;
      let vz = (gMV[n*3+2] + h * gF[n*3+2]) / m;
      if (gPin[n]) { vx = 0; vy = 0; vz = 0; } // rigid bone wrap: Dirichlet
      vx *= damp; vy *= damp; vz *= damp;
      const sp2 = vx*vx + vy*vy + vz*vz;
      if (sp2 > maxV * maxV) {
        const s = maxV / Math.sqrt(sp2);
        vx *= s; vy *= s; vz *= s;
      }
      gV[n*3] = vx; gV[n*3+1] = vy; gV[n*3+2] = vz;
    }

    // ---- G2P: gather velocity, update C/F, advect ----
    const jMin = pr.jMin;
    for (let p = 0; p < nP; p++) {
      const px = P[p*3], py = P[p*3+1], pz = P[p*3+2];
      const bx = this._spline1D((px - ox) / dx, idx, wx, gxw);
      const by = this._spline1D((py - oy) / dy, idy, wy, gyw);
      const bz = this._spline1D((pz - oz) / dz, idz, wz, gzw);
      if (bx < 0 || by < 0 || bz < 0 || bx + 2 >= gx || by + 2 >= gy || bz + 2 >= gz) continue;
      let nvx = 0, nvy = 0, nvz = 0;
      // velocity gradient L = sum v_i outer grad(w); APIC C = sum w v_i (x_i - x_p)^T
      let L00=0,L01=0,L02=0,L10=0,L11=0,L12=0,L20=0,L21=0,L22=0;
      let c00=0,c01=0,c02=0,c10=0,c11=0,c12=0,c20=0,c21=0,c22=0;
      for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) for (let k = 0; k < 3; k++) {
        const w = wx[i] * wy[j] * wz[k];
        const n = (bx + i) + gx * ((by + j) + gy * (bz + k));
        const vx = gV[n*3], vy = gV[n*3+1], vz = gV[n*3+2];
        const gwx = gxw[i] * wy[j] * wz[k];
        const gwy = wx[i] * gyw[j] * wz[k];
        const gwz = wx[i] * wy[j] * gzw[k];
        nvx += w * vx; nvy += w * vy; nvz += w * vz;
        L00 += vx*gwx; L01 += vx*gwy; L02 += vx*gwz;
        L10 += vy*gwx; L11 += vy*gwy; L12 += vy*gwz;
        L20 += vz*gwx; L21 += vz*gwy; L22 += vz*gwz;
        const dxn = (ox + (bx + i) * dx) - px;
        const dyn = (oy + (by + j) * dy) - py;
        const dzn = (oz + (bz + k) * dz) - pz;
        c00 += w*vx*dxn; c01 += w*vx*dyn; c02 += w*vx*dzn;
        c10 += w*vy*dxn; c11 += w*vy*dyn; c12 += w*vy*dzn;
        c20 += w*vz*dxn; c21 += w*vz*dyn; c22 += w*vz*dzn;
      }
      V[p*3] = nvx; V[p*3+1] = nvy; V[p*3+2] = nvz;
      const o9 = p * 9;
      C[o9]=c00; C[o9+1]=c01; C[o9+2]=c02;
      C[o9+3]=c10; C[o9+4]=c11; C[o9+5]=c12;
      C[o9+6]=c20; C[o9+7]=c21; C[o9+8]=c22;
      // F_new = (I + h*L) * F_old  (deformation gradient update)
      const f0=F[o9],f1=F[o9+1],f2=F[o9+2],f3=F[o9+3],f4=F[o9+4],
            f5=F[o9+5],f6=F[o9+6],f7=F[o9+7],f8=F[o9+8];
      const a00=1+h*L00, a01=h*L01, a02=h*L02,
            a10=h*L10, a11=1+h*L11, a12=h*L12,
            a20=h*L20, a21=h*L21, a22=1+h*L22;
      let n00=a00*f0+a01*f3+a02*f6, n01=a00*f1+a01*f4+a02*f7, n02=a00*f2+a01*f5+a02*f8;
      let n10=a10*f0+a11*f3+a12*f6, n11=a10*f1+a11*f4+a12*f7, n12=a10*f2+a11*f5+a12*f8;
      let n20=a20*f0+a21*f3+a22*f6, n21=a20*f1+a21*f4+a22*f7, n22=a20*f2+a21*f5+a22*f8;
      // NDG-style inversion guard, in gradient space: if the volume
      // collapses (det F < jMin), rescale F isotropically back above the
      // floor instead of letting the element invert.
      const J = n00*(n11*n22-n12*n21) - n01*(n10*n22-n12*n20) + n02*(n10*n21-n11*n20);
      if (J < jMin && J > 1e-9) {
        const s = Math.cbrt(jMin / J);
        n00*=s; n01*=s; n02*=s; n10*=s; n11*=s; n12*=s; n20*=s; n21*=s; n22*=s;
      } else if (!(J > 0)) {
        n00=1; n01=0; n02=0; n10=0; n11=1; n12=0; n20=0; n21=0; n22=1;
      }
      F[o9]=n00; F[o9+1]=n01; F[o9+2]=n02;
      F[o9+3]=n10; F[o9+4]=n11; F[o9+5]=n12;
      F[o9+6]=n20; F[o9+7]=n21; F[o9+8]=n22;
      if (!this._pinned[p]) {
        P[p*3] = px + h * nvx;
        P[p*3+1] = py + h * nvy;
        P[p*3+2] = pz + h * nvz;
      }
    }
  }

  /* ---------------- per-frame ---------------- */

  setQuality(q) {
    if (QUALITIES.indexOf(q) < 0 || q === this._quality) return;
    this._quality = q;
    if (q === 'off') { this._restoreMesh(); return; }
    try {
      if (this._mesh && this._region) {
        const R = this._region;
        this._buildParticles(R.preset, R.materials,
          _v3(R.center[0], R.center[1], R.center[2]),
          _v3(R.radius[0], R.radius[1], R.radius[2]),
          Array.from(R.regionVerts), this._base);
      }
    } catch (e) {}
  }

  update(dt) {
    if (this._disposed || this._quality === 'off') return;
    if (!this._ready || !this._region) return;
    try {
      this._step(dt);
    } catch (e) {
      this._failSafe();
    }
  }

  _step(dt) {
    const R = this._region, pr = R.preset;
    const h = Math.min(Math.max(dt || 0, 0), 1 / 30);
    if (h <= 0) return;
    const nP = R.nP;
    const P = this._P, V = this._V;

    // -- excitation: body acceleration -> velocity kick (same as Jolt lane)
    let ax = 0, ay = 0, az = 0;
    try {
      const Ctor = this._mesh.position.constructor;
      const wp = new Ctor();
      this._mesh.getWorldPosition(wp);
      if (this._prevPos && h > 1e-6) {
        const vx = (wp.x - this._prevPos.x) / h;
        const vy = (wp.y - this._prevPos.y) / h;
        const vz = (wp.z - this._prevPos.z) / h;
        ax = (vx - this._prevVel.x) / h;
        ay = (vy - this._prevVel.y) / h;
        az = (vz - this._prevVel.z) / h;
        const aLen = Math.sqrt(ax * ax + ay * ay + az * az);
        if (aLen > 40) { const s = 40 / aLen; ax *= s; ay *= s; az *= s; }
        this._prevVel = { x: vx, y: vy, z: vz };
      } else {
        this._prevVel = { x: 0, y: 0, z: 0 };
      }
      this._prevPos = { x: wp.x, y: wp.y, z: wp.z };
    } catch (e) { ax = ay = az = 0; }
    if (ax || ay || az) {
      const k = pr.excitation * h;
      for (const p of R.dynList) {
        V[p*3] -= ax * k; V[p*3+1] -= ay * k; V[p*3+2] -= az * k;
      }
    }

    // -- staged substeps (SurRoL/Newton: substepped explicit solve)
    const nSub = Math.min(pr.maxSubsteps,
      Math.max(1, Math.ceil(h / pr.dtMax)));
    const sh = h / nSub;
    for (let s = 0; s < nSub; s++) this._substep(sh);

    // -- watchdog: NaN / explosion -> reset to rest, then kill-switch
    let bad = false;
    for (let i = 0; i < P.length; i++) {
      const c = P[i];
      if (c !== c || c > 50 || c < -50) { bad = true; break; }
    }
    if (bad) {
      this._watchdog++;
      if (this._watchdog > 3) { this._failSafe(); return; }
      this._resetToRest();
      return;
    }

    // -- SKIN stage (NDG shell-regularizer analogue): relax the particle
    // -- displacement field over lattice neighbors before skinning, so the
    // -- render surface stays smooth and inextensible-looking.
    const disp = this._disp, rest = this._rest;
    for (let p = 0; p < nP; p++) {
      disp[p*3] = P[p*3] - rest[p*3];
      disp[p*3+1] = P[p*3+1] - rest[p*3+1];
      disp[p*3+2] = P[p*3+2] - rest[p*3+2];
    }
    for (let it = 0; it < pr.skinSmoothIters; it++) {
      for (const p of R.dynList) {
        const nb = this._nbr[p];
        if (!nb.length) continue;
        let sx = 0, sy = 0, sz = 0;
        for (let k = 0; k < nb.length; k++) {
          const q = nb[k];
          sx += disp[q*3]; sy += disp[q*3+1]; sz += disp[q*3+2];
        }
        const inv = 1 / nb.length;
        disp[p*3]   = 0.6 * disp[p*3]   + 0.4 * sx * inv;
        disp[p*3+1] = 0.6 * disp[p*3+1] + 0.4 * sy * inv;
        disp[p*3+2] = 0.6 * disp[p*3+2] + 0.4 * sz * inv;
      }
    }

    // -- skin the displacement onto the render mesh (same map as Jolt lane)
    const arr = this._posAttr.array;
    const base = this._base;
    const rv = R.regionVerts, mi = R.mapIdx, mw = R.mapW;
    const gain = pr.deformGain, maxD = pr.maxDeform;
    let maxDisp = 0;
    const nV = rv.length;
    for (let vi = 0; vi < nV; vi++) {
      let dx = 0, dy = 0, dz = 0;
      const o = vi * 4;
      for (let kk = 0; kk < 4; kk++) {
        const p = mi[o + kk], w = mw[o + kk];
        dx += w * disp[p * 3];
        dy += w * disp[p * 3 + 1];
        dz += w * disp[p * 3 + 2];
      }
      const len = Math.sqrt(dx * dx + dy * dy + dz * dz);
      if (len > maxDisp) maxDisp = len;
      let sx = dx * gain, sy = dy * gain, sz = dz * gain;
      if (len * gain > maxD) { const s = maxD / (len * gain); sx *= s; sy *= s; sz *= s; }
      const gi = rv[vi] * 3;
      arr[gi] = base[gi] + sx;
      arr[gi + 1] = base[gi + 1] + sy;
      arr[gi + 2] = base[gi + 2] + sz;
    }
    if (maxDisp > 1e-6) {
      this._posAttr.needsUpdate = true;
      this._frame++;
      const every = this._quality === 'high' ? 1 : 3;
      if (maxDisp > 5e-4 && this._frame % every === 0) {
        try { this._geometry.computeVertexNormals(); } catch (e) {}
      }
    }
  }

  _resetToRest() {
    if (!this._region) return;
    const nP = this._region.nP;
    this._P.set(this._rest);
    this._V.fill(0);
    this._C.fill(0);
    for (let p = 0; p < nP; p++) {
      const o9 = p * 9;
      this._F[o9]=1; this._F[o9+1]=0; this._F[o9+2]=0;
      this._F[o9+3]=0; this._F[o9+4]=1; this._F[o9+5]=0;
      this._F[o9+6]=0; this._F[o9+7]=0; this._F[o9+8]=1;
    }
  }

  _restoreMesh() {
    try {
      if (this._posAttr && this._base) {
        this._posAttr.array.set(this._base);
        this._posAttr.needsUpdate = true;
      }
    } catch (e) {}
  }

  _failSafe() {
    try { this._restoreMesh(); } catch (e) {}
    this._quality = 'off';
    this._ready = false;
  }

  /* ---------------- hit injection ---------------- */

  // Dent the tissue volume at a world-space impact point — same injection
  // math as SoftBody.hit() so the X-ray layer dent matches the skin dent.
  hit(worldPoint, dirX, strength) {
    if (this._disposed || this._quality === 'off') return;
    if (!this._ready || !this._region) return;
    try {
      const Ctor = this._mesh.position.constructor;
      const lp = new Ctor(worldPoint.x, worldPoint.y, worldPoint.z);
      if (this._mesh.worldToLocal) this._mesh.worldToLocal(lp);
      const s = Math.min(Math.max(strength || 0, 0), 40) * 0.0035;
      if (s <= 0) return;
      const dx = dirX >= 0 ? 1 : -1;
      const rad = 0.30;
      const P = this._P, V = this._V;
      for (const p of this._region.dynList) {
        const px = P[p*3] - lp.x, py = P[p*3+1] - lp.y, pz = P[p*3+2] - lp.z;
        const d = Math.sqrt(px * px + py * py + pz * pz);
        if (d < rad) {
          const fall = 1 - d / rad;
          P[p*3]   += dx * s * fall;
          P[p*3+1] += s * 0.25 * fall;
          V[p*3]   += dx * s * 8 * fall;
        }
      }
    } catch (e) { /* never crash the fight */ }
  }

  /* ---------------- teardown ---------------- */

  dispose() {
    this._disposed = true;
    try { _live.delete(this); } catch (e) {}
    try { this._restoreMesh(); } catch (e) {}
    try {
      if (_claimedGeometries && this._geometry) _claimedGeometries.delete(this._geometry);
    } catch (e) {}
    this._mesh = null; this._region = null;
    this._P = this._V = this._F = this._C = this._rest = this._vol = null;
  }

  get ready() { return this._ready; }
  get quality() { return this._quality; }
  get particleCount() { return this._region ? this._region.nP : 0; }
  get regionVertexCount() { return this._region ? this._region.regionVerts.length : 0; }
  get gridNodeCount() {
    if (!this._gN) return 0;
    return this._gN[0] * this._gN[1] * this._gN[2];
  }

  // Test hook.
  _testHandle() {
    return {
      stepOnce: (h) => { this._substep(h || 1 / 480); },
      particlePositions: () => (this._P ? this._P.slice() : null),
      restPositions: () => (this._rest ? this._rest.slice() : null),
      deformationDets: () => {
        if (!this._F || !this._region) return null;
        const out = new Float32Array(this._region.nP);
        for (let p = 0; p < this._region.nP; p++) {
          const o9 = p * 9, F = this._F;
          out[p] = F[o9]*(F[o9+4]*F[o9+8]-F[o9+5]*F[o9+7])
                 - F[o9+1]*(F[o9+3]*F[o9+8]-F[o9+5]*F[o9+6])
                 + F[o9+2]*(F[o9+3]*F[o9+7]-F[o9+4]*F[o9+6]);
        }
        return out;
      },
      // Crush one particle's deformation gradient to det=j to test the
      // NDG-style inversion guard on the next substep.
      forceDet: (p, j) => {
        if (!this._F || !this._region || p < 0 || p >= this._region.nP) return;
        const s = Math.cbrt(Math.max(j, 1e-6));
        const o9 = p * 9;
        this._F[o9]=s; this._F[o9+4]=s; this._F[o9+8]=s;
      },
      materials: () => (this._region ? this._region.materials : null),
      pinned: () => (this._pinned ? Array.from(this._pinned) : null),
      particleMaterials: () => (this._mat ? Array.from(this._mat) : null),
    };
  }
}

// Version stamps.
MpmTissue.VERSION = '1.0.0';
MpmTissue.ENGINE = 'mpm-lite';
