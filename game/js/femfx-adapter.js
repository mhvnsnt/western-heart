/* ============================================================
   WESTERN HEART — FemfxBody (AMD FEMFX finite-element tissue backend)

   Optional physics backend alongside the Jolt SoftBody
   (game/js/softbody.js). FEMFX is AMD's MIT-licensed finite-element
   library: the anatomy region becomes a real TETRAHEDRAL mesh with
   per-tet tissue material params (Young's modulus, Poisson ratio,
   fracture threshold) instead of an XPBD particle lattice.

   What changes vs Jolt: the SOLVER. Everything else is identical —
   same region lattice, same vertex skinning, same integration
   contract, so switching backends never changes the visual mapping:

     1. After loading a fighter's SkinnedMesh:
          const sb = FemfxBody.fromMesh(skinnedMesh, FemfxBody.anatomyFor(char));
        (or pick the backend: (WH_PHYSICS_BACKEND === 'femfx' ? FemfxBody : SoftBody))
     2. Every frame, AFTER the animation pose AND after jiggle.update:
          sb.update(dt);
     3. On hit landing (fighter.receiveHit):
          sb.hit(worldPoint, dirX, move.damage);
     4. On fighter swap / dispose: sb.dispose() restores the mesh.

   Backend selection: window.WH_PHYSICS_BACKEND = 'jolt' | 'femfx'
   (default 'jolt'). The WASM module lives at
   game/vendor/femfx/femfx.wasm.js — built by tools/femfx/build_wasm.sh
   (Emscripten). It is NOT in the repo by default.

   SAFETY: this module never throws and never breaks the fight. If the
   WASM module is missing or fails to init, fromMesh() silently falls
   back to the Jolt SoftBody for that fighter. update/hit/dispose are
   no-ops until the backend is ready — same contract as softbody.js.

   Fracture: FEMFX reports fractured tet faces via
   femfx_poll_fractures(). The adapter exposes pollFractures() but wires
   it to NOTHING visible — the show-animation lock means bone breaking
   needs explicit owner approval before any visual is built on it.

   Like softbody.js, this module has NO top-level imports (no three.js,
   no WASM) so it is unit-testable in node and adds zero boot cost.
   ============================================================ */

// ---- tiny vector helpers (plain objects; no three.js dependency) ----
const _v3 = (x = 0, y = 0, z = 0) => ({ x, y, z });

// ---- quality (mirrors softbody.js) -----------------------------------
const QUALITIES = ['off', 'low', 'high'];
const QUALITY_STORE = 'wh_femfx_v1';
let _globalQuality = 'low';
try {
  const saved = (typeof localStorage !== 'undefined') && localStorage.getItem(QUALITY_STORE);
  if (QUALITIES.indexOf(saved) >= 0) _globalQuality = saved;
} catch (e) { /* private mode / node: keep default */ }

// ---- WASM module (built by tools/femfx/build_wasm.sh) -----------------
const FEMFX_URL = '../vendor/femfx/femfx.wasm.js';
let _wasmPromise = null;
let _wasmFailed = false;

function ensureWasm() {
  if (_wasmFailed) return Promise.resolve(null);
  if (!_wasmPromise) {
    _wasmPromise = (async () => {
      const createModule = (await import(FEMFX_URL)).default;
      const M = await createModule();
      // wrap the C API
      const api = {
        create: M.cwrap('femfx_create', 'number', ['number', 'number']),
        addTetmesh: M.cwrap('femfx_add_tetmesh',
          'number', ['number', 'number', 'number', 'number', 'number', 'number', 'number']),
        step: M.cwrap('femfx_step', null, ['number']),
        getPositions: M.cwrap('femfx_get_positions', 'number', ['number']),
        applyImpulse: M.cwrap('femfx_apply_impulse', null,
          ['number','number','number','number','number','number','number','number']),
        pollFractures: M.cwrap('femfx_poll_fractures', 'number', []),
        destroy: M.cwrap('femfx_destroy', null, []),
        _M: M,
      };
      return api;
    })().catch((e) => {
      _wasmPromise = null;
      _wasmFailed = true;   // don't retry every frame; fall back stays
      return null;
    });
  }
  return _wasmPromise;
}

// ---- region preset (same belly region as the Jolt backend) -------------
const REGION = {
  boneNames: ['Spine1', 'spine1', 'Spine', 'spine', 'Hips', 'hips'],
  radius: [0.17, 0.21, 0.15],
  centerLift: 0.02,
  shellGrow: 1.22,
  pinCore: 0.42,
  pinCaps: 0.85,
  res: { low: [3, 4, 3], high: [4, 5, 4] },
  maxDeform: 0.06,
  tissue: 1,          // 0=fat, 1=muscle, 2=bone (femfx_bind.cpp presets)
  restDensity: 1050,  // kg/m^3, ~human tissue
};

const _live = (typeof Set !== 'undefined') ? new Set() : { add() {}, delete() {}, forEach() {} };

// 5-tet decomposition of a unit cube cell, corners indexed x+2y+4z.
// 4 corner tets (vol 1/6) + 1 central tet (vol 1/3); all positive orientation.
// (Verified: volumes sum to exactly 1.0.)
const CUBE_TETS = [
  [0, 1, 2, 4], [3, 1, 7, 2], [5, 1, 4, 7], [6, 2, 7, 4], [1, 2, 4, 7],
];

export class FemfxBody {
  constructor() {
    this._mesh = null;
    this._region = null;
    this._quality = _globalQuality;
    this._wasm = null;
    this._ready = false;
    this._disposed = false;
    this._fallback = null;   // Jolt SoftBody when WASM is unavailable
    this._acc = 0;
    this._lastFractures = 0;
  }

  /* ---------------- construction ---------------- */

  static fromMesh(skinnedMesh, anatomySpec, opts) {
    const fb = new FemfxBody();
    try {
      fb._buildRegion(skinnedMesh, anatomySpec);
    } catch (e) {
      return fb; // inert on any build failure
    }
    _live.add(fb);
    const autoLoad = !opts || opts.autoLoad !== false;
    if (autoLoad && fb._region) {
      ensureWasm().then((w) => {
        if (fb._disposed) return;
        if (w) fb._buildTetMesh(w);
        else fb._buildFallback();   // WASM missing -> Jolt SoftBody
      });
    }
    return fb;
  }

  static anatomyFor(char) {
    if (!char || char.softbody === false) return null;
    return { regions: char.softbodyRegions || ['belly'] };
  }

  static get globalQuality() { return _globalQuality; }

  static setGlobalQuality(q) {
    if (QUALITIES.indexOf(q) < 0) return false;
    _globalQuality = q;
    try {
      if (typeof localStorage !== 'undefined') localStorage.setItem(QUALITY_STORE, q);
    } catch (e) {}
    _live.forEach((fb) => { try { fb.setQuality(q); } catch (e) {} });
    return true;
  }

  // Backend probe for menus / diagnostics.
  static backendStatus() {
    if (_wasmFailed) return 'fallback-jolt';
    if (_wasmPromise) return 'loading';
    return 'not-started';
  }

  /* ---------------- region lattice (sync, no WASM) ---------------- */

  _buildRegion(skinnedMesh, anatomySpec) {
    if (!skinnedMesh || !skinnedMesh.isSkinnedMesh) return;
    const geometry = skinnedMesh.geometry;
    if (!geometry || !geometry.attributes || !geometry.attributes.position) return;
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

    let center = _v3((minX + maxX) / 2, (minY + maxY) / 2, (minZ + maxZ) / 2);
    try {
      const bones = [];
      if (skinnedMesh.skeleton && skinnedMesh.skeleton.bones) {
        for (const b of skinnedMesh.skeleton.bones) bones.push(b);
      } else {
        skinnedMesh.traverse((o) => { if (o.isBone) bones.push(o); });
      }
      let spine = null;
      for (const nm of REGION.boneNames) {
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
        center = _v3(tmp.x, tmp.y + REGION.centerLift * unit, tmp.z);
      }
    } catch (e) { /* keep bbox center */ }

    const radius = _v3(REGION.radius[0] * unit, REGION.radius[1] * unit, REGION.radius[2] * unit);
    const regionVerts = [];
    for (let i = 0; i < count; i++) {
      const nx = (arr[i * 3] - center.x) / radius.x;
      const ny = (arr[i * 3 + 1] - center.y) / radius.y;
      const nz = (arr[i * 3 + 2] - center.z) / radius.z;
      if (nx * nx + ny * ny + nz * nz <= 1) regionVerts.push(i);
    }
    if (!regionVerts.length) return;

    // Lattice over the grown box.
    const res = REGION.res[this._quality === 'high' ? 'high' : 'low'];
    const [nx, ny, nz] = res;
    const hx = radius.x * REGION.shellGrow, hy = radius.y * REGION.shellGrow, hz = radius.z * REGION.shellGrow;
    const latCount = (nx + 1) * (ny + 1) * (nz + 1);
    const latPos = new Float32Array(latCount * 3);
    const pinned = new Uint8Array(latCount);
    const latIndex = (i, j, k) => i + (nx + 1) * (j + (ny + 1) * k);
    for (let k = 0; k <= nz; k++) {
      for (let j = 0; j <= ny; j++) {
        for (let i = 0; i <= nx; i++) {
          const id = latIndex(i, j, k);
          const px = center.x - hx + (2 * hx * i) / nx;
          const py = center.y - hy + (2 * hy * j) / ny;
          const pz = center.z - hz + (2 * hz * k) / nz;
          latPos[id * 3] = px; latPos[id * 3 + 1] = py; latPos[id * 3 + 2] = pz;
          // pinning: deep core + top/bottom caps (mirrors Jolt backend)
          const ex = (px - center.x) / radius.x, ey = (py - center.y) / radius.y, ez = (pz - center.z) / radius.z;
          const enorm = Math.sqrt(ex * ex + ey * ey + ez * ez);
          const capY = Math.abs(j / ny - 0.5) * 2;
          if (enorm <= REGION.pinCore || capY >= REGION.pinCaps) pinned[id] = 1;
        }
      }
    }

    // Tets: 5 per cell.
    const tets = [];
    for (let k = 0; k < nz; k++) {
      for (let j = 0; j < ny; j++) {
        for (let i = 0; i < nx; i++) {
          const c = [
            latIndex(i, j, k), latIndex(i + 1, j, k),
            latIndex(i, j + 1, k), latIndex(i + 1, j + 1, k),
            latIndex(i, j, k + 1), latIndex(i + 1, j, k + 1),
            latIndex(i, j + 1, k + 1), latIndex(i + 1, j + 1, k + 1),
          ];
          for (const t of CUBE_TETS) tets.push(c[t[0]], c[t[1]], c[t[2]], c[t[3]]);
        }
      }
    }

    // Vertex -> lattice trilinear skinning map.
    const skin = new Float32Array(regionVerts.length * 8);
    const skinIdx = new Int32Array(regionVerts.length * 8);
    for (let vi = 0; vi < regionVerts.length; vi++) {
      const p = regionVerts[vi];
      const fx = ((arr[p * 3] - (center.x - hx)) / (2 * hx)) * nx;
      const fy = ((arr[p * 3 + 1] - (center.y - hy)) / (2 * hy)) * ny;
      const fz = ((arr[p * 3 + 2] - (center.z - hz)) / (2 * hz)) * nz;
      const i0 = Math.max(0, Math.min(nx - 1, Math.floor(fx)));
      const j0 = Math.max(0, Math.min(ny - 1, Math.floor(fy)));
      const k0 = Math.max(0, Math.min(nz - 1, Math.floor(fz)));
      const tx = Math.max(0, Math.min(1, fx - i0));
      const ty = Math.max(0, Math.min(1, fy - j0));
      const tz = Math.max(0, Math.min(1, fz - k0));
      const corners = [
        [i0, j0, k0, (1 - tx) * (1 - ty) * (1 - tz)],
        [i0 + 1, j0, k0, tx * (1 - ty) * (1 - tz)],
        [i0, j0 + 1, k0, (1 - tx) * ty * (1 - tz)],
        [i0 + 1, j0 + 1, k0, tx * ty * (1 - tz)],
        [i0, j0, k0 + 1, (1 - tx) * (1 - ty) * tz],
        [i0 + 1, j0, k0 + 1, tx * (1 - ty) * tz],
        [i0, j0 + 1, k0 + 1, (1 - tx) * ty * tz],
        [i0 + 1, j0 + 1, k0 + 1, tx * ty * tz],
      ];
      for (let c = 0; c < 8; c++) {
        skinIdx[vi * 8 + c] = latIndex(corners[c][0], corners[c][1], corners[c][2]);
        skin[vi * 8 + c] = corners[c][3];
      }
    }

    // Base position copy for restore + displacement.
    const base = new Float32Array(arr.length);
    base.set(arr);

    this._mesh = skinnedMesh;
    this._region = {
      verts: regionVerts, latPos, latRest: latPos.slice(), pinned,
      tets: new Uint32Array(tets), skin, skinIdx, base,
      cur: new Float32Array(latPos),  // readback scratch
      center, radius,
    };
  }

  _buildTetMesh(w) {
    const r = this._region;
    const M = w._M;
    const nV = r.latPos.length / 3, nT = r.tets.length / 4;
    const vPtr = M._malloc(nV * 3 * 4);
    const tPtr = M._malloc(nT * 4 * 4);
    const pPtr = M._malloc(nV);
    M.HEAPF32.set(r.latPos, vPtr >> 2);
    M.HEAPU32.set(r.tets, tPtr >> 2);
    M.HEAPU8.set(r.pinned, pPtr);
    const ok = w.create(nV * 2, nT);
    if (ok) {
      const id = w.addTetmesh(vPtr, nV, tPtr, nT, REGION.tissue, REGION.restDensity, pPtr);
      this._ready = id !== 0xffffffff && id !== 4294967295;
    }
    M._free(vPtr); M._free(tPtr); M._free(pPtr);
    if (this._ready) this._wasm = w;
    else this._buildFallback();
  }

  _buildFallback() {
    // WASM missing/failed -> drive this fighter with the Jolt backend.
    // Dynamic import keeps the hard dependency out of this module.
    import('./softbody.js').then((mod) => {
      if (this._disposed || this._ready) return;
      try {
        this._fallback = mod.SoftBody.fromMesh(this._mesh, { regions: ['belly'] });
        this._fallback.setQuality(this._quality);
      } catch (e) { this._fallback = null; }
    }).catch(() => { this._fallback = null; });
  }

  /* ---------------- runtime ---------------- */

  setQuality(q) {
    if (QUALITIES.indexOf(q) < 0) return false;
    this._quality = q;
    if (this._fallback && this._fallback.setQuality) {
      try { this._fallback.setQuality(q); } catch (e) {}
    }
    // NOTE: changing lattice res post-build requires rebuild; v1 keeps the
    // build-time res and applies quality only to fresh instances (same as
    // the Jolt backend's documented behavior for live instances).
    return true;
  }

  update(dt) {
    if (this._disposed || this._quality === 'off') return;
    if (this._fallback) { try { this._fallback.update(dt); } catch (e) {} return; }
    if (!this._ready || !this._region) return;
    const r = this._region, w = this._wasm;
    // fixed-step accumulator (FEMFX implicit solve likes small steps)
    this._acc = Math.min(this._acc + dt, 0.1);
    const h = 1 / 60;
    while (this._acc >= h) { w.step(h); this._acc -= h; }

    const M = w._M;
    const nV = r.latPos.length / 3;
    const pPtr = M._malloc(nV * 3 * 4);
    const got = w.getPositions(pPtr);
    if (got === nV) {
      r.cur.set(M.HEAPF32.subarray(pPtr >> 2, (pPtr >> 2) + nV * 3));
      this._applySkinning();
      this._lastFractures = w.pollFractures();
    }
    M._free(pPtr);
  }

  _applySkinning() {
    const r = this._region;
    const posAttr = this._mesh.geometry.attributes.position;
    const arr = posAttr.array;
    const maxD = REGION.maxDeform;
    for (let vi = 0; vi < r.verts.length; vi++) {
      const p = r.verts[vi];
      let dx = 0, dy = 0, dz = 0;
      for (let c = 0; c < 8; c++) {
        const li = r.skinIdx[vi * 8 + c], wt = r.skin[vi * 8 + c];
        dx += wt * (r.cur[li * 3] - r.latRest[li * 3]);
        dy += wt * (r.cur[li * 3 + 1] - r.latRest[li * 3 + 1]);
        dz += wt * (r.cur[li * 3 + 2] - r.latRest[li * 3 + 2]);
      }
      const len = Math.sqrt(dx * dx + dy * dy + dz * dz);
      if (len > maxD) { const s = maxD / len; dx *= s; dy *= s; dz *= s; }
      arr[p * 3] = r.base[p * 3] + dx;
      arr[p * 3 + 1] = r.base[p * 3 + 1] + dy;
      arr[p * 3 + 2] = r.base[p * 3 + 2] + dz;
    }
    posAttr.needsUpdate = true;
  }

  hit(worldPoint, dirX, damage) {
    if (this._disposed) return;
    if (this._fallback) { try { this._fallback.hit(worldPoint, dirX, damage); } catch (e) {} return; }
    if (!this._ready || !this._region) return;
    try {
      const w = this._wasm, r = this._region;
      // world -> mesh-local (mesh may be transformed)
      let lx = worldPoint.x, ly = worldPoint.y, lz = worldPoint.z;
      if (this._mesh.worldToLocal && this._mesh.position) {
        const Ctor = this._mesh.position.constructor;
        const tmp = new Ctor(lx, ly, lz);
        this._mesh.worldToLocal(tmp);
        lx = tmp.x; ly = tmp.y; lz = tmp.z;
      }
      const mag = 0.02 * (damage || 10);   // tuned impulse scale
      const rad = (r.radius.x + r.radius.y + r.radius.z) / 3;
      w.applyImpulse(lx, ly, lz, dirX, 0.15, 0, mag, rad);
    } catch (e) { /* never break the fight */ }
  }

  // Fracture faces reported by FEMFX since the last update (0 when the
  // Jolt fallback or no WASM). Wired to nothing visible — see header.
  pollFractures() {
    return this._lastFractures | 0;
  }

  dispose() {
    this._disposed = true;
    _live.delete(this);
    if (this._fallback) { try { this._fallback.dispose(); } catch (e) {} this._fallback = null; }
    if (this._region && this._mesh && this._mesh.geometry) {
      try {
        const posAttr = this._mesh.geometry.attributes.position;
        posAttr.array.set(this._region.base);
        posAttr.needsUpdate = true;
      } catch (e) {}
    }
    if (this._wasm) { try { this._wasm.destroy(); } catch (e) {} this._wasm = null; }
    this._ready = false;
    this._region = null;
    this._mesh = null;
  }
}
