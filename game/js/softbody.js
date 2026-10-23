/* ============================================================
   WESTERN HEART — SoftBody (Jolt XPBD volumetric soft-body lane)

   Purdue Dissectible Anatomy program: position-based dynamics (PBD/XPBD)
   soft bodies for muscle deformation under skin. Research report:
   ~/workspace/dissectible-anatomy/research-report-pbd-impls.md

   Engine: JoltPhysics.js (npm jolt-physics 1.1.1) by Jorrit Rouwe,
   vendored at game/vendor/jolt/jolt-physics.wasm-compat.js (wasm-compat
   build: WASM base64-embedded, no separate .wasm hosting needed).
   Jolt is MIT licensed — see game/vendor/jolt/LICENSE and VENDOR.md.

   What this is: a COARSE volumetric soft body (lattice of XPBD particles
   with edge + volume constraints) embedded in ONE anatomy region per
   fighter (v1: torso/belly). Each frame, after the animation pose (and
   after jiggle), the sim's particle displacements are skinned onto the
   render mesh's vertices in that region. Gives:
     - muscle deformation under skin on hit (dent + wobble, then recover)
     - volume-grounded secondary jiggle, excited by body acceleration
       (the spring-bone jiggle in jiggle.js stays — this is the volume
       layer underneath it, not a replacement)

   What this is NOT: no cutting/tearing/destruction (show-animation lock —
   the owner has not asked for gore), no rigid-body coupling, no collision.
   The soft body lives in the character's LOCAL space (mesh bind-pose
   space) pinned to the skeleton core; it never touches the fight physics.

   INTEGRATION CONTRACT (mirrors game/js/jiggle.js):
     1. After loading a fighter's SkinnedMesh:
          const sb = SoftBody.fromMesh(skinnedMesh, SoftBody.anatomyFor(char));
        Returns an instance immediately (safe to call update/hit/dispose
        before Jolt finishes loading — they no-op until ready).
     2. Every frame, AFTER the animation pose AND after jiggle.update:
          sb.update(dt);
     3. On hit landing (fighter.receiveHit):
          sb.hit(worldPoint, dirX, move.damage);   // dirX is -1 or 1
     4. On fighter swap / dispose: sb.dispose() restores the mesh.

   Quality: SoftBody.globalQuality / SoftBody.setGlobalQuality(q) with
   q in 'off' | 'low' | 'high'. Persisted in localStorage `wh_softbody_v1`.
   Default is 'low' (conservative): 3x4x3 lattice, ~30 particles. 'high'
   rebuilds at 4x5x4. 'off' disables sim + restores the mesh.

   Mobile: the solver cost is trivial (tens of particles, no collisions,
   one shared Jolt world stepped once per frame for all fighters). The
   per-frame JS cost is one pass over the region's vertices (a few
   thousand) plus throttled normal recomputation.

   This module has NO top-level imports (no three.js, no Jolt) so it is
   unit-testable in node and adds zero boot cost: Jolt is dynamically
   imported on first fromMesh and every Jolt touch is guarded — physics
   must NEVER crash the fight.
   ============================================================ */

// ---- tiny vector helpers (plain objects; no three.js dependency) ----
const _v3 = (x = 0, y = 0, z = 0) => ({ x, y, z });

// ---- quality ---------------------------------------------------------
const QUALITIES = ['off', 'low', 'high'];
const QUALITY_STORE = 'wh_softbody_v1';
let _globalQuality = 'low'; // conservative default
try {
  const saved = (typeof localStorage !== 'undefined') && localStorage.getItem(QUALITY_STORE);
  if (QUALITIES.indexOf(saved) >= 0) _globalQuality = saved;
} catch (e) { /* private mode / node: keep default */ }

// ---- Jolt world singleton (one physics world for all fighters) --------
const JOLT_URL = '../vendor/jolt/jolt-physics.wasm-compat.js';
let _world = null;          // { Jolt, jolt, physicsSystem, bodyInterface }
let _worldPromise = null;
let _lastStepMs = -1e9;

function ensureWorld() {
  if (_world) return Promise.resolve(_world);
  if (!_worldPromise) {
    _worldPromise = (async () => {
      const initJolt = (await import(JOLT_URL)).default;
      const Jolt = await initJolt();
      // Minimal world: single object layer, NO collision pairs enabled.
      // Soft bodies never collide with anything — they are pinned volumes
      // in character-local space. Zero collision cost.
      const settings = new Jolt.JoltSettings();
      settings.mMaxBodies = 64;
      settings.mMaxBodyPairs = 64;
      settings.mMaxContactConstraints = 32;
      const objectFilter = new Jolt.ObjectLayerPairFilterTable(1);
      const bpInterface = new Jolt.BroadPhaseLayerInterfaceTable(1, 1);
      bpInterface.MapObjectToBroadPhaseLayer(0, new Jolt.BroadPhaseLayer(0));
      settings.mObjectLayerPairFilter = objectFilter;
      settings.mBroadPhaseLayerInterface = bpInterface;
      settings.mObjectVsBroadPhaseLayerFilter =
        new Jolt.ObjectVsBroadPhaseLayerFilterTable(bpInterface, 1, objectFilter, 1);
      const jolt = new Jolt.JoltInterface(settings);
      Jolt.destroy(settings);
      _world = {
        Jolt,
        jolt,
        physicsSystem: jolt.GetPhysicsSystem(),
        bodyInterface: jolt.GetPhysicsSystem().GetBodyInterface(),
      };
      return _world;
    })().catch((e) => {
      // Jolt failed to load — stay inert, never break the game.
      _worldPromise = null;
      _world = null;
      return null;
    });
  }
  return _worldPromise;
}

function _nowMs() {
  try {
    if (typeof performance !== 'undefined' && performance.now) return performance.now();
  } catch (e) {}
  return Date.now();
}

// Step the shared world at most once per animation frame, no matter how
// many fighters call update().
function _stepWorldShared(world, h) {
  const now = _nowMs();
  if (now - _lastStepMs < 5) return;
  _lastStepMs = now;
  world.jolt.Step(h, 1);
}

// ---- anatomy region presets (v1: belly/torso only) ---------------------
// Radii are anatomical meters scaled by character height; the region is an
// ellipsoid centered on the Spine1 bone. The lattice is built over a box
// slightly larger than the ellipsoid so the particle shell covers every
// region vertex. Pinning: the deep core (around the spine) plus the top
// and bottom caps are fixed (invMass 0); the surface shell is dynamic.
const REGION_PRESETS = {
  belly: {
    boneNames: ['Spine1', 'spine1', 'Spine', 'spine', 'Hips', 'hips'],
    radius: [0.17, 0.21, 0.15], // x,y,z meters at 1.7 m character height
    centerLift: 0.02,           // +y from the spine bone
    shellGrow: 1.22,            // lattice box = radius * shellGrow
    // NOTE: the lattice keeps the FULL box (no ellipsoid masking). Every
    // cell must be complete or the volume constraints vanish and the
    // solve goes unstable (verified in tuning: masked -> energy growth).
    pinCore: 0.42,              // enorm <= pinCore -> pinned
    pinCaps: 0.85,              // |ny| >= pinCaps -> pinned
    res: { low: [3, 4, 3], high: [4, 5, 4] },
    edgeCompliance: 2e-5,
    volumeCompliance: 1e-5,
    iterations: { low: 6, high: 10 },
    linearDamping: 0.3,
    excitation: 0.12,           // velocity coupling to body acceleration
    deformGain: 1.0,
    maxDeform: 0.06,            // per-vertex displacement clamp (m)
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
  return { regions };
}

// Geometries already driving a live SoftBody (one body per geometry).
const _claimedGeometries = (typeof WeakSet !== 'undefined') ? new WeakSet() : null;
const _live = (typeof Set !== 'undefined') ? new Set() : { add() {}, delete() {}, forEach() {} };

export class SoftBody {
  constructor() {
    this._mesh = null;
    this._region = null;      // built region data (sync, no Jolt needed)
    this._quality = _globalQuality;
    this._world = null;
    this._Jolt = null;
    this._shared = null;
    this._body = null;
    this._bodyId = null;
    this._motion = null;
    this._ready = false;
    this._disposed = false;
    this._frame = 0;
    this._watchdog = 0;
    this._prevPos = null;     // for acceleration excitation
    this._prevVel = null;
    this._tmpP = null;        // Float32Array particle scratch
  }

  /* ---------------- construction ---------------- */

  static fromMesh(skinnedMesh, anatomySpec, opts) {
    const sb = new SoftBody();
    try {
      sb._buildRegion(skinnedMesh, _normalizeSpec(anatomySpec));
    } catch (e) {
      return sb; // inert on any build failure
    }
    _live.add(sb);
    const autoLoad = !opts || opts.autoLoad !== false;
    if (autoLoad && sb._region) {
      ensureWorld().then((w) => {
        if (w && !sb._disposed) sb._buildBody(w);
      });
    }
    return sb;
  }

  // Map character data -> anatomy spec. Returns null when the character
  // opts out (char.softbody === false) — the fighter then skips creation.
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
    _live.forEach((sb) => { try { sb.setQuality(q); } catch (e) {} });
    return true;
  }

  // Synchronous region analysis: find the belly ellipsoid, collect the
  // render-mesh vertices inside it, build the particle lattice and the
  // vertex->particle skinning map. No Jolt needed.
  _buildRegion(skinnedMesh, spec) {
    if (!skinnedMesh || !skinnedMesh.isSkinnedMesh) return;
    const geometry = skinnedMesh.geometry;
    if (!geometry || !geometry.attributes || !geometry.attributes.position) return;
    if (_claimedGeometries && _claimedGeometries.has(geometry)) return; // already driven
    const posAttr = geometry.attributes.position;
    const arr = posAttr.array;
    const count = posAttr.count;
    if (!count) return;

    // Whole-mesh bounds (manual; no three.js needed).
    let minX = 1e9, minY = 1e9, minZ = 1e9, maxX = -1e9, maxY = -1e9, maxZ = -1e9;
    for (let i = 0; i < count; i++) {
      const x = arr[i * 3], y = arr[i * 3 + 1], z = arr[i * 3 + 2];
      if (x < minX) minX = x; if (y < minY) minY = y; if (z < minZ) minZ = z;
      if (x > maxX) maxX = x; if (y > maxY) maxY = y; if (z > maxZ) maxZ = z;
    }
    const height = Math.max(maxY - minY, 0.5);
    const unit = Math.min(Math.max(height, 1.2), 2.2) / 1.7; // character scale

    // v1: single belly region.
    const preset = spec.regions[0];
    if (!preset) return;

    // Spine bone -> mesh-local center. Prefer the mesh's own skeleton
    // (bones are often siblings of the mesh, not children, in real rigs).
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

    // Collect render vertices inside the ellipsoid.
    const regionVerts = [];
    for (let i = 0; i < count; i++) {
      const nx = (arr[i * 3] - center.x) / radius.x;
      const ny = (arr[i * 3 + 1] - center.y) / radius.y;
      const nz = (arr[i * 3 + 2] - center.z) / radius.z;
      if (nx * nx + ny * ny + nz * nz <= 1) regionVerts.push(i);
    }
    if (!regionVerts.length) return; // nothing to drive

    this._mesh = skinnedMesh;
    this._buildLattice(preset, center, radius, regionVerts, arr);

    // Claim the geometry + keep a base copy for restore/displacement.
    if (_claimedGeometries) _claimedGeometries.add(geometry);
    this._base = new Float32Array(arr); // full-geometry base positions
    this._geometry = geometry;
    this._posAttr = posAttr;

    // Don't let frustum culling pop when we displace vertices.
    try {
      if (!geometry.boundingSphere && geometry.computeBoundingSphere) geometry.computeBoundingSphere();
      if (geometry.boundingSphere) geometry.boundingSphere.radius += 0.15;
    } catch (e) {}
  }

  // Build the particle lattice + vertex->particle map for the current quality.
  // radius is already character-scale adjusted by the caller.
  _buildLattice(preset, center, radius, regionVerts, arr) {
    const res = preset.res[this._quality === 'high' ? 'high' : 'low'];
    const [nx, ny, nz] = res;
    const g = preset.shellGrow;
    const box = _v3(radius.x * g, radius.y * g, radius.z * g);
    const step = _v3(
      (2 * box.x) / Math.max(nx - 1, 1),
      (2 * box.y) / Math.max(ny - 1, 1),
      (2 * box.z) / Math.max(nz - 1, 1));

    const pIndex = new Map(); // "x,y,z" -> particle index
    const pPos = [];          // [x,y,z] per particle
    const pPin = [];
    const key = (x, y, z) => x + ',' + y + ',' + z;
    for (let z = 0; z < nz; z++) for (let y = 0; y < ny; y++) for (let x = 0; x < nx; x++) {
      const px = center.x - box.x + x * step.x;
      const py = center.y - box.y + y * step.y;
      const pz = center.z - box.z + z * step.z;
      const ex = (px - center.x) / radius.x;
      const ey = (py - center.y) / radius.y;
      const ez = (pz - center.z) / radius.z;
      const enorm = Math.sqrt(ex * ex + ey * ey + ez * ez);
      // Full box: every lattice node is kept so all cells stay complete
      // (volume constraints need all 8 corners; masked lattices go unstable).
      const pin = (enorm <= preset.pinCore) || (Math.abs(ey) >= preset.pinCaps);
      pIndex.set(key(x, y, z), pPos.length);
      pPos.push([px, py, pz]);
      pPin.push(pin ? 1 : 0);
    }
    if (!pPos.length) return;
    const nP = pPos.length;

    // Nearest-4 particle map per region vertex (inverse-distance weights).
    const nV = regionVerts.length;
    const mapIdx = new Int32Array(nV * 4);
    const mapW = new Float32Array(nV * 4);
    for (let vi = 0; vi < nV; vi++) {
      const gi = regionVerts[vi];
      const vx = arr[gi * 3], vy = arr[gi * 3 + 1], vz = arr[gi * 3 + 2];
      // best 4 (simple insertion; nP is tiny)
      const best = [[1e9, -1], [1e9, -1], [1e9, -1], [1e9, -1]];
      for (let p = 0; p < nP; p++) {
        const dx = vx - pPos[p][0], dy = vy - pPos[p][1], dz = vz - pPos[p][2];
        const d2 = dx * dx + dy * dy + dz * dz;
        if (d2 < best[3][0]) {
          best[3] = [d2, p];
          best.sort((a, b) => a[0] - b[0]);
        }
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

    // Dynamic (unpinned) particle list + rest pose.
    const rest = new Float32Array(nP * 3);
    const dynList = [];
    for (let p = 0; p < nP; p++) {
      rest[p * 3] = pPos[p][0]; rest[p * 3 + 1] = pPos[p][1]; rest[p * 3 + 2] = pPos[p][2];
      if (!pPin[p]) dynList.push(p);
    }

    this._region = {
      preset, center: [center.x, center.y, center.z],
      radius: [radius.x, radius.y, radius.z],
      res: [nx, ny, nz], box: [box.x, box.y, box.z], step: [step.x, step.y, step.z],
      gridKey: key, pIndex, nP, rest, pinned: pPin,
      regionVerts: Int32Array.from(regionVerts), mapIdx, mapW, dynList,
    };
    this._tmpP = new Float32Array(nP * 3);
  }

  // Build the Jolt soft body once the world is ready. Guarded everywhere.
  _buildBody(world) {
    const Jolt = world.Jolt;
    const R = this._region;
    if (!R) return;
    this._destroyBody(); // in case of rebuild (quality change)
    try {
      const shared = new Jolt.SoftBodySharedSettings();
      const v = new Jolt.SoftBodySharedSettingsVertex();
      const f3 = new Jolt.Float3(0, 0, 0);
      for (let p = 0; p < R.nP; p++) {
        f3.x = R.rest[p * 3]; f3.y = R.rest[p * 3 + 1]; f3.z = R.rest[p * 3 + 2];
        v.mPosition = f3;
        v.mInvMass = R.pinned[p] ? 0 : 1;
        shared.mVertices.push_back(v);
      }
      Jolt.destroy(v); Jolt.destroy(f3);

      // Edge constraints between lattice neighbors.
      const edge = new Jolt.SoftBodySharedSettingsEdge(0, 0, R.preset.edgeCompliance);
      const [nx, ny, nz] = R.res;
      const at = (x, y, z) => R.pIndex.get(R.gridKey(x, y, z));
      for (let z = 0; z < nz; z++) for (let y = 0; y < ny; y++) for (let x = 0; x < nx; x++) {
        const a = at(x, y, z);
        if (a === undefined) continue;
        edge.set_mVertex(0, a);
        const nb = [[x + 1, y, z], [x, y + 1, z], [x, y, z + 1]];
        for (const [qx, qy, qz] of nb) {
          const b = (qx < nx && qy < ny && qz < nz) ? at(qx, qy, qz) : undefined;
          if (b === undefined) continue;
          edge.set_mVertex(1, b);
          shared.mEdgeConstraints.push_back(edge);
        }
      }
      Jolt.destroy(edge);
      shared.CalculateEdgeLengths();

      // Volume constraints: 6 tets per lattice cell (keeps the muscle plump).
      const T = [
        [[0,0,0],[0,1,1],[0,0,1],[1,1,1]], [[0,0,0],[0,1,0],[0,1,1],[1,1,1]],
        [[0,0,0],[0,0,1],[1,0,1],[1,1,1]], [[0,0,0],[1,0,1],[1,0,0],[1,1,1]],
        [[0,0,0],[1,1,0],[0,1,0],[1,1,1]], [[0,0,0],[1,0,0],[1,1,0],[1,1,1]],
      ];
      const sVol = new Jolt.SoftBodySharedSettingsVolume(0, 0, 0, 0, R.preset.volumeCompliance);
      // The lattice is a complete box, so every cell has all 8 corners.
      const cidx = (x, y, z) => R.pIndex.get(R.gridKey(x, y, z));
      for (let z = 0; z < nz - 1; z++) for (let y = 0; y < ny - 1; y++) for (let x = 0; x < nx - 1; x++) {
        const c = (dx, dy, dz) => cidx(x + dx, y + dy, z + dz);
        for (let t = 0; t < 6; t++) {
          for (let i = 0; i < 4; i++) {
            const o = T[t][i];
            sVol.set_mVertex(i, c(o[0], o[1], o[2]));
          }
          shared.mVolumeConstraints.push_back(sVol);
        }
      }
      Jolt.destroy(sVol);
      shared.CalculateVolumeConstraintVolumes();
      shared.Optimize();

      const pos0 = new Jolt.RVec3(0, 0, 0);
      const cs = new Jolt.SoftBodyCreationSettings(
        shared, pos0, Jolt.Quat.prototype.sIdentity(), 0);
      Jolt.destroy(pos0);
      cs.mPressure = 0;                    // volume constraints hold the shape
      cs.mGravityFactor = 0;              // local-space sim: no world gravity
      cs.mLinearDamping = R.preset.linearDamping;
      cs.mNumIterations = R.preset.iterations[this._quality === 'high' ? 'high' : 'low'];
      cs.mAllowSleeping = false;          // jiggle must never freeze
      cs.mMaxLinearVelocity = 30;
      // mUpdatePosition MUST stay false: the sim runs in character-local
      // space; letting Jolt recenter the body would shift our frame.
      cs.mUpdatePosition = false;

      const body = world.bodyInterface.CreateSoftBody(cs);
      Jolt.destroy(cs);
      world.bodyInterface.AddBody(body.GetID(), Jolt.EActivation_Activate);

      this._world = world;
      this._Jolt = Jolt;
      this._shared = shared;
      this._body = body;
      this._bodyId = body.GetID();
      this._motion = Jolt.castObject(body.GetMotionProperties(), Jolt.SoftBodyMotionProperties);
      this._ready = true;
      this._watchdog = 0;
    } catch (e) {
      this._destroyBody();
      this._ready = false;
    }
  }

  _destroyBody() {
    try {
      if (this._world && this._bodyId) {
        this._world.bodyInterface.RemoveBody(this._bodyId);
        this._world.bodyInterface.DestroyBody(this._bodyId);
      }
    } catch (e) {}
    try { if (this._Jolt && this._shared) this._Jolt.destroy(this._shared); } catch (e) {}
    this._shared = null; this._body = null; this._bodyId = null;
    this._motion = null; this._ready = false;
  }

  /* ---------------- per-frame ---------------- */

  setQuality(q) {
    if (QUALITIES.indexOf(q) < 0 || q === this._quality) return;
    this._quality = q;
    if (q === 'off') {
      this._restoreMesh();
      return;
    }
    // Rebuild the lattice + body at the new resolution when possible.
    try {
      if (this._mesh && this._region) {
        const preset = this._region.preset;
        // radius/center already carry the character-scale factor.
        this._buildLattice(preset,
          _v3(this._region.center[0], this._region.center[1], this._region.center[2]),
          _v3(this._region.radius[0], this._region.radius[1], this._region.radius[2]),
          this._region.regionVerts, this._base);
        if (this._world) this._buildBody(this._world);
      }
    } catch (e) {}
  }

  update(dt) {
    if (this._disposed || this._quality === 'off') return;
    if (!this._ready || !this._motion || !this._region) return;
    try {
      this._step(dt);
    } catch (e) {
      this._failSafe();
    }
  }

  _step(dt) {
    const Jolt = this._Jolt;
    const R = this._region;
    const h = Math.min(Math.max(dt || 0, 0), 1 / 30);
    const verts = this._motion.GetVertices();
    const P = this._tmpP;
    const nP = R.nP;

    // -- excitation: body acceleration -> velocity kick on dynamic particles
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
    const k = R.preset.excitation * h;

    for (let p = 0; p < nP; p++) {
      const vref = verts.at(p);
      const pos = vref.mPosition;
      P[p * 3] = pos.GetX(); P[p * 3 + 1] = pos.GetY(); P[p * 3 + 2] = pos.GetZ();
      if (!R.pinned[p] && k !== 0 && (ax || ay || az)) {
        const vel = vref.mVelocity;
        const nv = new Jolt.Vec3(
          vel.GetX() - ax * k, vel.GetY() - ay * k, vel.GetZ() - az * k);
        vref.mVelocity = nv;
        Jolt.destroy(nv);
      }
    }

    // -- step the shared world (once per frame across all fighters)
    if (h > 0) _stepWorldShared(this._world, h);

    // -- re-read positions (solver ran above)
    for (let p = 0; p < nP; p++) {
      const pos = verts.at(p).mPosition;
      P[p * 3] = pos.GetX(); P[p * 3 + 1] = pos.GetY(); P[p * 3 + 2] = pos.GetZ();
    }

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

    // -- skin the displacement onto the render mesh
    const arr = this._posAttr.array;
    const base = this._base;
    const rv = R.regionVerts, mi = R.mapIdx, mw = R.mapW;
    const gain = R.preset.deformGain;
    const maxD = R.preset.maxDeform;
    let maxDisp = 0;
    const nV = rv.length;
    for (let vi = 0; vi < nV; vi++) {
      let dx = 0, dy = 0, dz = 0;
      const o = vi * 4;
      for (let kk = 0; kk < 4; kk++) {
        const p = mi[o + kk], w = mw[o + kk];
        dx += w * (P[p * 3] - R.rest[p * 3]);
        dy += w * (P[p * 3 + 1] - R.rest[p * 3 + 1]);
        dz += w * (P[p * 3 + 2] - R.rest[p * 3 + 2]);
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
      // Recompute normals, throttled on low.
      const every = this._quality === 'high' ? 1 : 3;
      if (maxDisp > 5e-4 && this._frame % every === 0) {
        try { this._geometry.computeVertexNormals(); } catch (e) {}
      }
    }
  }

  _resetToRest() {
    const Jolt = this._Jolt;
    if (!Jolt || !this._motion || !this._region) return;
    const verts = this._motion.GetVertices();
    const R = this._region;
    for (let p = 0; p < R.nP; p++) {
      const vref = verts.at(p);
      const np = new Jolt.Vec3(R.rest[p * 3], R.rest[p * 3 + 1], R.rest[p * 3 + 2]);
      vref.mPosition = np; Jolt.destroy(np);
      const nv = new Jolt.Vec3(0, 0, 0);
      vref.mVelocity = nv; Jolt.destroy(nv);
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
    // Physics must never crash the fight: drop to 'off' and restore.
    try { this._destroyBody(); } catch (e) {}
    try { this._restoreMesh(); } catch (e) {}
    this._quality = 'off';
  }

  /* ---------------- hit injection ---------------- */

  // Dent the muscle volume at a world-space impact point.
  // dirX: -1|1 knock direction along x. strength: move.damage-ish (0..40).
  hit(worldPoint, dirX, strength) {
    if (this._disposed || this._quality === 'off') return;
    if (!this._ready || !this._motion || !this._region) return;
    try {
      const Jolt = this._Jolt;
      const Ctor = this._mesh.position.constructor;
      const lp = new Ctor(worldPoint.x, worldPoint.y, worldPoint.z);
      if (this._mesh.worldToLocal) this._mesh.worldToLocal(lp);
      const s = Math.min(Math.max(strength || 0, 0), 40) * 0.0035;
      if (s <= 0) return;
      const dx = dirX >= 0 ? 1 : -1;
      const rad = 0.30;
      const verts = this._motion.GetVertices();
      for (const p of this._region.dynList) {
        const vref = verts.at(p);
        const pos = vref.mPosition;
        const px = pos.GetX() - lp.x, py = pos.GetY() - lp.y, pz = pos.GetZ() - lp.z;
        const d = Math.sqrt(px * px + py * py + pz * pz);
        if (d < rad) {
          const fall = 1 - d / rad;
          const np = new Jolt.Vec3(
            pos.GetX() + dx * s * fall,
            pos.GetY() + s * 0.25 * fall,
            pos.GetZ());
          vref.mPosition = np; Jolt.destroy(np);
          const vel = vref.mVelocity;
          const nv = new Jolt.Vec3(
            vel.GetX() + dx * s * 8 * fall, vel.GetY(), vel.GetZ());
          vref.mVelocity = nv; Jolt.destroy(nv);
        }
      }
    } catch (e) { /* never crash the fight */ }
  }

  /* ---------------- teardown ---------------- */

  dispose() {
    this._disposed = true;
    try { _live.delete(this); } catch (e) {}
    try { this._destroyBody(); } catch (e) {}
    try { this._restoreMesh(); } catch (e) {}
    try {
      if (_claimedGeometries && this._geometry) _claimedGeometries.delete(this._geometry);
    } catch (e) {}
    this._mesh = null; this._region = null; this._world = null;
  }

  get ready() { return this._ready; }
  get quality() { return this._quality; }
  get particleCount() { return this._region ? this._region.nP : 0; }
  get regionVertexCount() { return this._region ? this._region.regionVerts.length : 0; }

  // Test hook (used by test/softbody.test.mjs).
  _testHandle() {
    return {
      worldPromise: ensureWorld(),
      isReady: () => this._ready,
      // Forces a step even inside the 5 ms coalescing window
      // (tests need back-to-back steps).
      stepOnce: (h) => { if (this._world) { _lastStepMs = -1e9; _stepWorldShared(this._world, h || 1 / 60); } },
      particlePositions: () => {
        if (!this._motion || !this._region) return null;
        const verts = this._motion.GetVertices();
        const out = new Float32Array(this._region.nP * 3);
        for (let p = 0; p < this._region.nP; p++) {
          const pos = verts.at(p).mPosition;
          out[p * 3] = pos.GetX(); out[p * 3 + 1] = pos.GetY(); out[p * 3 + 2] = pos.GetZ();
        }
        return out;
      },
      restPositions: () => (this._region ? this._region.rest.slice() : null),
      pinned: () => (this._region ? this._region.pinned.slice() : null),
    };
  }
}

// Version stamps (see game/vendor/jolt/VENDOR.md for upgrade notes).
SoftBody.VERSION = '1.0.0';
SoftBody.JOLT_VERSION = '1.1.1';
