/* ============================================================
   WESTERN HEART — WHBrawlerCamera (Track 7, 2026-10-23)
   Multi-target brawler camera for Heart and Mind Within phase-2
   density: player vs multiple threats. Zoom/pan keeps every active
   target in frame; walls clamp the dolly so the view never clips
   through tight-space geometry.

   Algorithm lineage (docs/research/CUTSCENE-STORY-2026-10-23.md):
   the standard multi-target / "Smash-bros" framing — bounding box of
   all targets -> weighted centroid -> dolly distance from the
   horizontal FOV fit (d = halfExtent / tan(hFov/2)). The fit math is
   the SAME formula as the Tekken CameraRig port in game/js/scene.js
   (PR #851): vertical FOV invariant, horizontal FOV derived from the
   live aspect, portrait widening instead of pullback past the arena
   walls. This controller BUILDS ON that rig (same constants,
   same portrait behavior) for N targets — it does NOT replace or
   edit scene.js. The fight camera is untouched; this is opt-in.

   Node-testable: THREE is never statically imported. The obstacle
   tester is injectable: setObstacleTester((origin, dir, maxDist) =>
   hitDist | null). In-game it is wired to a THREE.Raycaster over the
   arena's collidables.
   ============================================================ */

const DEF = {
  pad: 1.6,          // extra meters around the target box
  minDist: 5.5,      // never closer than this
  maxDist: 10.5,     // arena wall pullback cap (same as PR #851)
  maxFov: 80,        // portrait widen cap (same as PR #851)
  height: 1.75,      // base camera height
  lookY: 1.0,        // base look height
  heightPerY: 0.45,  // rise with tallest target (same as #851)
  lookPerY: 0.25,
  dampPos: 4,        // exponential damp rates (same family as #851)
  dampLook: 4,
  pitchDeg: 8,       // slight downward pitch
  shakeDecay: 2.2,
};

export class WHBrawlerCamera {
  constructor(opts = {}) {
    this.cfg = { ...DEF, ...opts };
    this.camera = null;
    this.enabled = false;
    this._targets = [];      // { pos: {x,y,z}, weight }
    this._trauma = 0;
    this._savedFov = null;
    this._center = { x: 0, y: 0, z: 0 };
    this._dist = this.cfg.minDist;
    this._obstacleTester = null;
    this._framing = null;    // cinematic override { zoomMul, focusIdx }
    this._t = 0;
  }

  attach(camera) {
    this.camera = camera;
    if (this._savedFov == null && camera.fov != null) this._savedFov = camera.fov;
    return this;
  }
  setTargets(targets) { this._targets = targets || []; return this; }
  /* target: { pos:{x,y,z} } or a THREE.Object3D (uses .position) */
  static targetOf(obj, weight = 1) {
    const pos = obj && obj.position ? obj.position : (obj.pos || obj);
    return { pos, weight };
  }
  setObstacleTester(fn) { this._obstacleTester = fn || null; return this; }
  /* Cinematic director can push framing: { zoomMul, focus: {x,y,z} } */
  setFraming(f) { this._framing = f; return this; }
  clearFraming() { this._framing = null; return this; }
  addShake(amount) { this._trauma = Math.min(1, this._trauma + amount); return this; }
  enable() { this.enabled = true; return this; }

  disable() {
    this.enabled = false;
    if (this.camera && this._savedFov != null && this.camera.fov !== this._savedFov) {
      this.camera.fov = this._savedFov;
      if (this.camera.updateProjectionMatrix) this.camera.updateProjectionMatrix();
    }
    return this;
  }

  /* Pure framing math — testable without a renderer. Returns the
     desired { center, dist, fov } for the current targets. */
  frame(aspect, fovBase) {
    const c = this.cfg;
    const ts = this._targets.filter((t) => t && t.pos);
    if (!ts.length) return { center: { ...this._center }, dist: c.minDist, fov: fovBase };
    let wSum = 0, cx = 0, cy = 0, cz = 0;
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const t of ts) {
      const w = t.weight || 1, p = t.pos;
      wSum += w; cx += p.x * w; cy += p.y * w; cz += (p.z || 0) * w;
      if (p.x < minX) minX = p.x; if (p.x > maxX) maxX = p.x;
      if (p.y < minY) minY = p.y; if (p.y > maxY) maxY = p.y;
    }
    cx /= wSum; cy /= wSum; cz /= wSum;
    if (this._framing && this._framing.focus) {
      cx = this._framing.focus.x; cy = this._framing.focus.y; cz = this._framing.focus.z || 0;
    }
    const halfW = Math.max((maxX - minX) / 2, 0.9) + c.pad;
    const halfH = Math.max((maxY - minY) / 2, 0.6) + c.pad * 0.6;
    const vFov = fovBase * Math.PI / 180;
    const hFov = 2 * Math.atan(Math.tan(vFov / 2) * aspect);
    let dist = Math.max(
      halfW / Math.tan(hFov / 2),
      halfH / Math.tan(vFov / 2),
      c.minDist,
    );
    let fov = fovBase;
    const portrait = aspect < 1;
    if (portrait && dist > c.maxDist) {
      // PR #851 portrait behavior: stay inside the arena, widen FOV.
      const needH = 2 * Math.atan(halfW / c.maxDist);
      fov = Math.min(c.maxFov, 2 * Math.atan(Math.tan(needH / 2) / aspect) * 180 / Math.PI);
      dist = c.maxDist;
    }
    if (this._framing && this._framing.zoomMul) dist *= this._framing.zoomMul;
    return { center: { x: cx, y: cy, z: cz }, dist, fov, halfW, halfH };
  }

  update(dt, now) {
    if (!this.enabled || !this.camera) return;
    const c = this.cfg;
    const aspect = this.camera.aspect || 16 / 9;
    const fovBase = this._savedFov != null ? this._savedFov : (this.camera.fov || 50);
    const { center, dist, fov } = this.frame(aspect, fovBase);

    // Damped centroid + distance (same smoothing family as #851's rig).
    const k = 1 - Math.exp(-Math.max(dt, 0) * c.dampPos);
    this._center.x += (center.x - this._center.x) * k;
    this._center.y += (center.y - this._center.y) * k;
    this._center.z += (center.z - this._center.z) * k;
    this._dist += (dist - this._dist) * k;

    const pitch = (c.pitchDeg * Math.PI) / 180;
    const dir = { x: 0, y: Math.sin(pitch), z: Math.cos(pitch) };
    let d = this._dist;
    // Wall clamp: never push the camera through tight-space geometry.
    if (this._obstacleTester) {
      const hit = this._obstacleTester(this._center, dir, d);
      if (hit != null && hit < d) d = Math.max(c.minDist * 0.7, hit - 0.35);
    }
    const px = this._center.x + dir.x * d;
    const py = this._center.y + dir.y * d + c.height - 1.0;
    const pz = this._center.z + dir.z * d;

    const kp = 1 - Math.exp(-Math.max(dt, 0) * c.dampPos);
    this.camera.position.x += (px - this.camera.position.x) * kp;
    this.camera.position.y += (py - this.camera.position.y) * kp;
    this.camera.position.z += (pz - this.camera.position.z) * kp;

    if (Math.abs(fov - this.camera.fov) > 0.05) {
      this.camera.fov = fov;
      if (this.camera.updateProjectionMatrix) this.camera.updateProjectionMatrix();
    }
    if (this.camera.lookAt) {
      const ly = this._center.y * 0.5 + c.lookY * 0.5 + (this._framing && this._framing.lookY != null ? this._framing.lookY : 0);
      this.camera.lookAt(this._center.x, ly, this._center.z);
    }
    // Trauma shake (decaying noise, squared falloff).
    this._t += dt;
    if (this._trauma > 0.001) {
      const s = this._trauma * this._trauma;
      this.camera.position.x += Math.sin(this._t * 61.7) * 0.22 * s;
      this.camera.position.y += Math.cos(this._t * 53.3) * 0.16 * s;
      this._trauma = Math.max(0, this._trauma - dt * c.shakeDecay);
    }
  }
}
