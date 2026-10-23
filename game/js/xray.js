/* ============================================================
   WESTERN HEART — X-ray (Purdue anatomy × cinematic KO blows)

   Owner directive 2026-10-23: wire the Purdue anatomy project into
   our physics and how our characters work, Mortal-Kombat-X-ray style.

   What this is: when a Rage Art (R.1+2) or Urge Smash (US.2+3) lands
   as the KO blow, the game plays a quick Tekken-styled X-ray beat
   (~1.9 s, integrated into the KO — NOT a separate mode):
     1. camera zooms to the impact point (existing fight camera),
     2. victim's skin goes translucent (opacity 0.25),
     3. anatomy layers reveal in sequence: MUSCLE -> BONE -> ORGAN,
     4. the muscle layer dents at the impact point (same injection
        math as SoftBody.hit(), so it matches the skin dent),
        the bone layer flashes at the impact site,
     5. camera pulls back, skin restores, KO plays out.

   ANIM-GATE NOTE (owner law 2026-10-23): this is a RENDERING effect
   only — material opacity + mesh visibility + camera moves. It never
   creates, selects, or plays an AnimationClip, so the anim-gate's
   FIGHT-context lock (game/js/anim-gate.js) is untouched: no show
   clip can ever enter a fight through this path.

   Data: roster/<fighter>/anatomy/anatomy-layers.json
   (wh.anatomy-layers/1 — see docs/research/ANATOMY-LAYERS-SPEC-2026-10-23.md).
   Layers render as analytic proxy meshes (ellipsoid/capsule/sphere)
   built once from the SDF primitive data — no per-frame meshing,
   no voxel grids. ORGAN is a reserved reveal slot: the parser reads
   layers.organ when it lands; today only BONE/MUSCLE ship.

   Quality: X-ray is gated on SoftBody.globalQuality — 'off' skips
   the sequence entirely (falls back to the plain rage slow-mo KO).
   Proxy mesh resolution follows 'low' | 'high'.

   Hook points (see game.js):
     - Game._resolveCombat KO branch -> xray.onHitKO(attacker, defender, hb)
     - Game._loop (after arena.update, before render) -> xray.update(realDt)
     - Game.resetFightState / _startRound -> xray.cancel()
   Hook CONDITION: attacker.attackName starts with 'R.' (rage art,
   see rage.js) or equals 'US.2+3' (urge smash, see soulurge.js).

   This module has no static three.js import (THREE is injected via
   the constructor, like jiggle.js's pattern) so the trigger/timing/
   dent math is unit-testable in node. No Jolt, no physics — inert
   until a cinematic KO fires, and every render touch is guarded so
   physics/visuals can never crash the fight.
   ============================================================ */
import { SoftBody } from './softbody.js';

/* Timeline (real seconds — the sequence runs on wall clock, not the
   rage slow-mo time scale, so it stays a quick ~1.9 s beat). */
export const XRAY = Object.freeze({
  DURATION: 1.9,
  SKIN_FADE_T: 0.30,   // skin reaches SKIN_OPACITY
  SKIN_OPACITY: 0.25,
  MUSCLE_T: 0.35,      // muscle proxies fade in
  BONE_T: 0.75,        // bone proxies fade in; muscle recedes
  ORGAN_T: 0.75,       // reserved reveal slot for the organ layer
  PULL_T: 1.45,        // camera pulls back, everything restores
  IMPACT_RADIUS: 0.30, // dent falloff radius (m) — mirrors softbody.hit()
  BONE_FLASH_RADIUS: 0.35,
  CAM_DIST: 1.6,       // zoom distance from the impact point
  MUSCLE_COLOR: 0xc22430,
  BONE_COLOR: 0xe9e2d2,
  BONE_FLASH_COLOR: 0xff5a1a,
  ORGAN_COLOR: 0x7a1e2e,
});

/* ---------------- pure data helpers (node-testable) ---------------- */

/* Normalize one SDF primitive from anatomy-layers.json into a flat
   descriptor. Kinds per spec: 'capsule' {a,b,r}, 'ellipsoid'
   {center,radii}, 'sphere' {center,r}. */
export function normPrim(p) {
  if (!p || typeof p.kind !== 'string') return null;
  if (p.kind === 'capsule' && Array.isArray(p.a) && Array.isArray(p.b) && p.r > 0) {
    return { kind: 'capsule', a: p.a.slice(0, 3), b: p.b.slice(0, 3), r: p.r, id: p.id || null };
  }
  if (p.kind === 'ellipsoid' && Array.isArray(p.center) && Array.isArray(p.radii)) {
    return { kind: 'ellipsoid', center: p.center.slice(0, 3), radii: p.radii.slice(0, 3), id: p.id || null };
  }
  if (p.kind === 'sphere' && Array.isArray(p.center) && p.r > 0) {
    return { kind: 'sphere', center: p.center.slice(0, 3), r: p.r, id: p.id || null };
  }
  return null;
}

/* Parse an anatomy-layers.json doc -> { bone, muscle, organ } primitive
   lists. Returns null when the doc has no usable layer data (fighter
   opts out of the X-ray layer reveal; the skin/camera beat still plays). */
export function parseAnatomyLayers(json) {
  if (!json || !json.layers) return null;
  const L = json.layers;
  const bone = [];
  const muscle = [];
  const organ = [];
  const bonePrims = (L.bone && L.bone.primitives) || [];
  for (const p of bonePrims) { const n = normPrim(p); if (n) bone.push(n); }
  const groups = (L.muscle && L.muscle.groups) || [];
  for (const g of groups) {
    for (const p of g.primitives || []) {
      const n = normPrim(p);
      if (n) { n.group = g.id || null; muscle.push(n); }
    }
  }
  // ORGAN layer (lands separately): same primitive union when present.
  const organPrims = (L.organ && L.organ.primitives) || [];
  for (const p of organPrims) { const n = normPrim(p); if (n) organ.push(n); }
  if (!bone.length && !muscle.length && !organ.length) return null;
  return { bone, muscle, organ };
}

/* Dent offset for a layer point at distance d (m) from the impact site.
   Mirrors SoftBody.hit() (softbody.js): same strength curve
   (min(damage,40) * 0.0035), same 0.30 m falloff, same knock-direction
   bias — so the muscle-layer dent matches the dent the soft body puts
   in the skin. dirX: -1 | 1. Returns [dx, dy, dz] in mesh-local meters. */
export function dentVector(d, dirX, damage) {
  const s = Math.min(Math.max(damage || 0, 0), 40) * 0.0035;
  const fall = Math.max(0, 1 - d / XRAY.IMPACT_RADIUS);
  const sx = (dirX >= 0 ? 1 : -1) * s * fall;
  return [sx, s * 0.25 * fall, 0];
}

function _clamp01(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
function _lerp(a, b, k) { return a + (b - a) * k; }
function _dist3(a, b) {
  const dx = a[0] - b[0], dy = a[1] - b[1], dz = a[2] - b[2];
  return Math.sqrt(dx * dx + dy * dy + dz * dz);
}

/* ---------------- X-ray director ---------------- */

export class XraySystem {
  constructor(game, THREE) {
    this.game = game || null;
    this.THREE = THREE || null; // injected (game.js passes its THREE)
    this.active = false;
    this.t = 0;
    this._cache = {};    // fighterId -> parsed layers | null (failed/missing)
    this._fetching = {}; // fighterId -> true while a fetch is in flight
    this._kind = null;   // 'rage-art' | 'urge-smash'
    this._P = null;      // per-run render state (see _start)
  }

  /* Background prefetch of a fighter's anatomy JSON. Fail-silent:
     a missing file just means no layer reveal for that fighter. */
  prefetch(fighterId) {
    if (!fighterId || this._cache[fighterId] !== undefined || this._fetching[fighterId]) return;
    if (typeof fetch === 'undefined') return;
    this._fetching[fighterId] = true;
    // game/ is the page base (game/index.html); roster/ sits at repo root.
    fetch('../roster/' + fighterId + '/anatomy/anatomy-layers.json')
      .then((r) => (r && r.ok ? r.json() : null))
      .then((j) => { this._cache[fighterId] = parseAnatomyLayers(j); })
      .catch(() => { this._cache[fighterId] = null; })
      .finally(() => { delete this._fetching[fighterId]; });
  }

  /* Called from Game._resolveCombat's KO branch (next to rage.onHitKO).
     Returns true when the X-ray sequence started. Only the two
     cinematic KO blows qualify: Rage Art (attackName 'R.…') and
     Urge Smash (attackName 'US.2+3'). */
  onHitKO(attacker, defender, hb) {
    if (this.active) return false;
    if (SoftBody.globalQuality === 'off') return false; // quality toggle gates X-ray
    const name = attacker && attacker.attackName;
    const rageArt = typeof name === 'string' && name.indexOf('R.') === 0;
    const urgeSmash = name === 'US.2+3';
    if (!rageArt && !urgeSmash) return false;
    if (!defender || !defender.root) return false;
    try {
      this._start(defender, hb, attacker, rageArt ? 'rage-art' : 'urge-smash');
      return true;
    } catch (e) {
      this._teardown();
      return false;
    }
  }

  /* Abort a running sequence (round reset / leaving the fight). */
  cancel() {
    if (this.active) this._teardown();
  }

  get kind() { return this._kind; }
  get phase() {
    if (!this.active) return 'idle';
    if (this.t < XRAY.MUSCLE_T) return 'zoom';
    if (this.t < XRAY.BONE_T) return 'muscle';
    if (this.t < XRAY.PULL_T) return 'bone';
    return 'pullback';
  }

  /* ---- sequence ---- */

  _start(defender, hb, attacker, kind) {
    this._kind = kind;
    const T = this.THREE;
    const P = (this._P = {
      defender,
      skinMats: [],      // [{ mat, opacity, transparent, depthWrite }]
      group: null,       // proxy group (attached to victim's skinned mesh)
      muscle: [],        // proxy meshes
      bone: [],
      organ: [],
      flash: [],         // bone proxies near the impact site
      muscleMat: null, boneMat: null, organMat: null,
      camPos: null, camQuat: null,
      camTarget: null, impactW: null,
      dirX: 1, damage: 8,
      built: false,
    });

    // Impact point (world). hb = attacker's active hitbox {x,y,z}.
    const ip = hb && typeof hb.x === 'number'
      ? [hb.x, hb.y, hb.z]
      : [defender.root.position.x, defender.root.position.y + 1.2, defender.root.position.z];
    P.impactW = ip;
    P.dirX = (attacker && attacker.facing < 0) ? -1 : 1;
    const mv = attacker && attacker.attackMove;
    P.damage = (mv && mv.damage) || 32;

    // Victim skinned meshes (same traversal pattern fighter.js uses).
    const meshes = [];
    try {
      defender.root.traverse((o) => { if (o.isSkinnedMesh) meshes.push(o); });
    } catch (e) {}
    P.meshes = meshes;
    const host = meshes[0] || defender.root;

    // Skin translucency: record + override material state.
    for (const m of meshes) {
      const mats = Array.isArray(m.material) ? m.material : [m.material];
      for (const mat of mats) {
        if (!mat) continue;
        P.skinMats.push({
          mat,
          opacity: mat.opacity, transparent: mat.transparent, depthWrite: mat.depthWrite,
        });
        try {
          mat.transparent = true;
          mat.depthWrite = false;
        } catch (e) {}
      }
    }

    // Impact point in the host's local (bind-pose) frame — the frame the
    // anatomy SDF primitives live in.
    P.impactL = ip.slice();
    try {
      if (host.updateWorldMatrix) host.updateWorldMatrix(true, false);
      if (T && host.worldToLocal) {
        const v = new T.Vector3(ip[0], ip[1], ip[2]);
        host.worldToLocal(v);
        P.impactL = [v.x, v.y, v.z];
      }
    } catch (e) {}

    // Camera: save pose, compute the zoom target along the current view axis.
    const cam = this.game && this.game.arena && this.game.arena.camera;
    if (cam && T) {
      P.camPos = cam.position.clone();
      P.camQuat = cam.quaternion.clone();
      const toCam = new T.Vector3(
        cam.position.x - ip[0], cam.position.y - ip[1], cam.position.z - ip[2]);
      if (toCam.lengthSq() < 1e-6) toCam.set(0, 0.2, 1);
      toCam.normalize();
      P.camTarget = new T.Vector3(
        ip[0] + toCam.x * XRAY.CAM_DIST,
        Math.max(0.35, ip[1] + toCam.y * XRAY.CAM_DIST + 0.12),
        ip[2] + toCam.z * XRAY.CAM_DIST);
    }

    // Build layer proxies now if the data is cached; otherwise the
    // update loop builds them the moment the prefetch lands.
    this._tryBuildProxies();

    this.t = 0;
    this.active = true;
  }

  /* Build the analytic proxy meshes from cached SDF primitive data.
     Safe to call repeatedly; builds once. */
  _tryBuildProxies() {
    const P = this._P;
    if (!P || P.built || !this.THREE) return;
    const fid = P.defender && P.defender.char && P.defender.char.id;
    const layers = fid ? this._cache[fid] : null;
    if (layers === undefined) { this.prefetch(fid); return; } // prefetch in flight or just started — retry next frame
    if (!layers) { P.built = true; return; } // no data: skin/camera beat only
    const T = this.THREE;
    const q = SoftBody.globalQuality === 'high' ? 12 : 8;
    try {
      P.muscleMat = new T.MeshBasicMaterial({ color: XRAY.MUSCLE_COLOR, transparent: true, opacity: 0, depthWrite: false });
      P.boneMat = new T.MeshBasicMaterial({ color: XRAY.BONE_COLOR, transparent: true, opacity: 0, depthWrite: false });
      P.organMat = new T.MeshBasicMaterial({ color: XRAY.ORGAN_COLOR, transparent: true, opacity: 0, depthWrite: false });
      const group = new T.Group();
      const mk = (prim, mat, list, isBone) => {
        const mesh = this._proxyMesh(prim, mat, q);
        if (!mesh) return;
        // Dent the layer at the impact point (softbody.hit() injection math).
        const c = this._primCenter(prim);
        const d = _dist3(c, P.impactL);
        if (d < XRAY.IMPACT_RADIUS) {
          const dv = dentVector(d, P.dirX, P.damage);
          mesh.position.x += dv[0]; mesh.position.y += dv[1]; mesh.position.z += dv[2];
        }
        if (isBone && d < XRAY.BONE_FLASH_RADIUS) {
          mesh.material = mat.clone(); // per-mesh material for the flash pulse
          P.flash.push(mesh);
        }
        mesh.renderOrder = 10;
        mesh.visible = true;
        group.add(mesh);
        list.push(mesh);
      };
      for (const prim of layers.muscle) mk(prim, P.muscleMat, P.muscle, false);
      for (const prim of layers.bone) mk(prim, P.boneMat, P.bone, true);
      // ORGAN slot: parsed + revealed when the organ layer lands in the JSON.
      for (const prim of layers.organ) mk(prim, P.organMat, P.organ, false);
      const host = (P.meshes && P.meshes[0]) || P.defender.root;
      host.add(group);
      P.group = group;
      P.built = true;
    } catch (e) {
      P.built = true; // never let proxy building break the sequence
    }
  }

  _primCenter(prim) {
    if (prim.kind === 'capsule') {
      return [(prim.a[0] + prim.b[0]) / 2, (prim.a[1] + prim.b[1]) / 2, (prim.a[2] + prim.b[2]) / 2];
    }
    return prim.center.slice(0, 3);
  }

  /* One analytic proxy mesh for one SDF primitive. Static geometry,
     built once — no per-frame meshing. */
  _proxyMesh(prim, mat, seg) {
    const T = this.THREE;
    let geo = null;
    const mesh = new T.Mesh();
    if (prim.kind === 'capsule') {
      const a = prim.a, b = prim.b;
      const len = _dist3(a, b);
      geo = new T.CapsuleGeometry(prim.r, Math.max(len, 1e-4), 4, seg);
      mesh.position.set((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2);
      const dir = new T.Vector3(b[0] - a[0], b[1] - a[1], b[2] - a[2]);
      if (dir.lengthSq() > 1e-12) {
        dir.normalize();
        mesh.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), dir);
      }
    } else if (prim.kind === 'ellipsoid') {
      geo = new T.SphereGeometry(1, seg, Math.max(6, seg - 2));
      mesh.scale.set(prim.radii[0], prim.radii[1], prim.radii[2]);
      mesh.position.set(prim.center[0], prim.center[1], prim.center[2]);
    } else if (prim.kind === 'sphere') {
      geo = new T.SphereGeometry(prim.r, seg, Math.max(6, seg - 2));
      mesh.position.set(prim.center[0], prim.center[1], prim.center[2]);
    } else {
      return null;
    }
    mesh.geometry = geo;
    mesh.material = mat;
    mesh.frustumCulled = false; // displaced + transparent: never pop
    return mesh;
  }

  /* Per-frame driver. Runs on REAL seconds (game.js passes the
     unscaled frame dt) — the beat stays ~1.9 s even under KO slow-mo. */
  update(dt) {
    if (!this.active || !this._P) return;
    const P = this._P;
    this.t += Math.min(Math.max(dt || 0, 0), 0.1);
    const t = this.t;

    // Late-arriving anatomy data: build proxies mid-sequence.
    if (!P.built) this._tryBuildProxies();

    // --- skin opacity: 1 -> 0.25 (zoom), hold, -> 1 (pullback) ---
    let skinOp;
    if (t < XRAY.SKIN_FADE_T) skinOp = _lerp(1, XRAY.SKIN_OPACITY, _clamp01(t / XRAY.SKIN_FADE_T));
    else if (t < XRAY.PULL_T) skinOp = XRAY.SKIN_OPACITY;
    else skinOp = _lerp(XRAY.SKIN_OPACITY, 1, _clamp01((t - XRAY.PULL_T) / (XRAY.DURATION - XRAY.PULL_T)));
    for (const s of P.skinMats) { try { s.mat.opacity = skinOp; } catch (e) {} }

    // --- layer reveal: MUSCLE -> BONE (-> ORGAN slot) ---
    const fadeIn = (at) => _clamp01((t - at) / 0.2);
    const fadeOut = _clamp01((t - XRAY.PULL_T) / (XRAY.DURATION - XRAY.PULL_T));
    const mOp = t < XRAY.MUSCLE_T ? 0
      : t < XRAY.BONE_T ? fadeIn(XRAY.MUSCLE_T)
      : t < XRAY.PULL_T ? 0.35
      : _lerp(0.35, 0, fadeOut);
    const bOp = t < XRAY.BONE_T ? 0 : _lerp(fadeIn(XRAY.BONE_T), 0, fadeOut);
    const oOp = t < XRAY.ORGAN_T ? 0 : _lerp(fadeIn(XRAY.ORGAN_T), 0, fadeOut);
    try {
      if (P.muscleMat) P.muscleMat.opacity = Math.max(0, Math.min(1, mOp));
      if (P.boneMat) P.boneMat.opacity = Math.max(0, Math.min(1, bOp));
      if (P.organMat) P.organMat.opacity = Math.max(0, Math.min(1, oOp));
      for (const m of P.flash) m.material.opacity = Math.max(0, Math.min(1, bOp));
    } catch (e) {}

    // --- bone flash at the impact site (during the bone phase) ---
    if (t >= XRAY.BONE_T && t < XRAY.PULL_T && P.flash.length && this.THREE) {
      const pulse = 0.5 + 0.5 * Math.sin(t * 18);
      for (const m of P.flash) {
        try {
          m.material.color.setHex(XRAY.BONE_COLOR).lerp(
            new this.THREE.Color(XRAY.BONE_FLASH_COLOR), 0.35 + 0.65 * pulse);
        } catch (e) {}
      }
    }

    // --- camera: zoom to the impact point, hold, pull back ---
    const cam = this.game && this.game.arena && this.game.arena.camera;
    if (cam && P.camPos && P.camTarget && this.THREE) {
      let k; // 0 = saved pose, 1 = zoomed
      if (t < XRAY.SKIN_FADE_T) k = _clamp01(t / XRAY.SKIN_FADE_T);
      else if (t < XRAY.PULL_T) k = 1;
      else k = 1 - _clamp01((t - XRAY.PULL_T) / (XRAY.DURATION - XRAY.PULL_T));
      k = k * k * (3 - 2 * k); // smoothstep
      try {
        cam.position.lerpVectors(P.camPos, P.camTarget, k);
        cam.lookAt(P.impactW[0], P.impactW[1], P.impactW[2]);
      } catch (e) {}
    }

    if (t >= XRAY.DURATION) this._teardown();
  }

  /* Restore everything: skin materials, camera, remove proxies. */
  _teardown() {
    const P = this._P;
    try {
      if (P) {
        for (const s of P.skinMats) {
          try {
            s.mat.opacity = s.opacity;
            s.mat.transparent = s.transparent;
            s.mat.depthWrite = s.depthWrite;
          } catch (e) {}
        }
        if (P.group && P.group.parent) {
          try { P.group.parent.remove(P.group); } catch (e) {}
        }
        // Dispose proxy resources (shared materials disposed once).
        const seen = new Set();
        const kill = (m) => {
          try {
            if (m.geometry && !seen.has(m.geometry)) { seen.add(m.geometry); m.geometry.dispose(); }
            if (m.material && !seen.has(m.material)) { seen.add(m.material); m.material.dispose(); }
          } catch (e) {}
        };
        for (const m of [...P.muscle, ...P.bone, ...P.organ, ...P.flash]) kill(m);
        for (const mt of [P.muscleMat, P.boneMat, P.organMat]) {
          try { if (mt && !seen.has(mt)) { seen.add(mt); mt.dispose(); } } catch (e) {}
        }
        const cam = this.game && this.game.arena && this.game.arena.camera;
        if (cam && P.camPos && P.camQuat) {
          try { cam.position.copy(P.camPos); cam.quaternion.copy(P.camQuat); } catch (e) {}
        }
      }
    } finally {
      this._P = null;
      this._kind = null;
      this.t = 0;
      this.active = false;
    }
  }
}

XraySystem.VERSION = '1.0.0';
