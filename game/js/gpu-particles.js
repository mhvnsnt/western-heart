/* ============================================================
   WESTERN HEART — GPU particle / aura VFX (E30)
   Honest split: particle STATE lives in typed arrays here (GPU-
   ready layout: position + color + size buffers a THREE.Points
   object can consume directly), the per-frame update is CPU-side
   in this module, and rendering is GPU point sprites via
   buildPoints(THREE) in the browser. A full GPU compute-shader
   update is a later step, not claimed here.
   Presets: hit sparks, Soul aura (color by Nine-Soul index,
   pulsing scale — the aura VFX for Soul Urge / KESSHOU moments),
   wall/floor-break debris. No THREE import at module top level:
   buildPoints() takes THREE as an argument so Node tests run
   without a renderer.
   ============================================================ */

export const SOUL_COLORS = Object.freeze([
  [1.0, 0.85, 0.3], [1.0, 0.4, 0.2], [0.3, 0.7, 1.0], [0.6, 0.2, 1.0],
  [0.2, 1.0, 0.5], [1.0, 0.9, 0.9], [0.9, 0.9, 0.2], [0.4, 0.4, 0.4],
  [1.0, 0.5, 0.8],
]);

export class ParticleSystem {
  constructor(max = 1024) {
    this.max = max;
    this.positions = new Float32Array(max * 3);
    this.colors = new Float32Array(max * 3);
    this.sizes = new Float32Array(max);
    this.velocities = new Float32Array(max * 3);
    this.life = new Float32Array(max);
    this.maxLife = new Float32Array(max);
    this.count = 0; // live count; dead slots are compacted on update
    this._next = 0;
  }

  spawn({ pos = [0, 0, 0], vel = [0, 0, 0], color = [1, 1, 1], size = 1, life = 1 } = {}) {
    const i = this._next;
    this._next = (this._next + 1) % this.max;
    this.positions.set(pos, i * 3);
    this.velocities.set(vel, i * 3);
    this.colors.set(color, i * 3);
    this.sizes[i] = size;
    this.life[i] = life;
    this.maxLife[i] = life;
    if (this.count < this.max) this.count++;
    return i;
  }

  // Spawn a burst preset. kind: 'hit-spark' | 'soul-aura' | 'debris'.
  burst(kind, origin, opts = {}) {
    const n = opts.count ?? (kind === 'soul-aura' ? 40 : kind === 'debris' ? 30 : 16);
    const color = kind === 'soul-aura' ? SOUL_COLORS[(opts.soul ?? 0) % SOUL_COLORS.length] : kind === 'debris' ? [0.6, 0.55, 0.5] : [1.0, 0.85, 0.3];
    for (let k = 0; k < n; k++) {
      const a = (k / n) * Math.PI * 2;
      const speed = kind === 'debris' ? 1 + (k % 3) : 2;
      this.spawn({
        pos: origin,
        vel: [Math.cos(a) * speed, 1 + (k % 4) * 0.5, Math.sin(a) * speed],
        color, size: opts.size ?? 1, life: opts.life ?? (0.4 + (k % 5) * 0.1),
      });
    }
    return n;
  }

  update(dt, { gravity = -9.81 } = {}) {
    for (let i = 0; i < this.max; i++) {
      if (this.life[i] <= 0) continue;
      this.life[i] -= dt;
      if (this.life[i] <= 0) continue;
      this.velocities[i * 3 + 1] += gravity * dt * 0.15;
      for (let c = 0; c < 3; c++) this.positions[i * 3 + c] += this.velocities[i * 3 + c] * dt;
    }
    return this.liveCount();
  }

  liveCount() {
    let n = 0;
    for (let i = 0; i < this.max; i++) if (this.life[i] > 0) n++;
    return n;
  }

  // Soul-aura pulse: aura scale oscillates with time (used by the
  // caller to scale the aura mesh / point size). Deterministic.
  static auraPulse(t, soul = 0) {
    return 1 + 0.25 * Math.sin(t * 3 + soul * 0.7);
  }

  // Browser only: build a THREE.Points object over these buffers.
  // Throws a clear error in Node (no THREE) instead of failing oddly.
  buildPoints(THREE) {
    if (!THREE || !THREE.BufferGeometry) throw new Error('gpu-particles: THREE with BufferGeometry is required (browser only)');
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(this.positions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(this.colors, 3));
    const mat = new THREE.PointsMaterial({ size: 0.1, vertexColors: true, sizeAttenuation: true, transparent: true });
    return new THREE.Points(geo, mat);
  }
}
