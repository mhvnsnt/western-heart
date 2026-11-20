/* ============================================================
   WESTERN HEART — viscous fluid FX (Track 3: fluid dynamics)
   DualSPHysics-inspired, game-appropriate implementation.

   WHAT THIS IS: a lightweight SPH-lite particle fluid for viscous
   splash effects (blood / mud / ink) at finisher impact moments.
   It is NOT a port of DualSPHysics — DualSPHysics is a native
   C++/CUDA engineering solver (millions of particles, needs a real
   GPU) and cannot run on a phone browser. What we take from it is
   the formulation vocabulary, simplified to a game budget:

     - WCSPH-style pressure stand-in: short-range pairwise repulsion
       (positional de-overlap, unconditionally stable at our dt).
     - Monaghan artificial viscosity on approaching pairs, with a
       per-particle VISCOSITY dial (DualSPHysics's non-Newtonian
       branch `src_mphase/DSPH_v5.0_NNewtonian` is the variable-
       viscosity precedent) — blood/mud/ink presets below.
     - Cohesion band (surface-tension stand-in) so spray blobs back
       together instead of scattering like dry sparks.
     - Dynamic-Boundary-Condition spirit: ground plane + arena walls
       + fighter capsule colliders; slow impacts STICK (coat the
       surface, drip, stamp a decal), fast impacts bounce + splat.
     - Droplet breakup: a droplet faster than its viscosity-scaled
       threshold splits along its velocity vector, conserving volume.

   BUDGET (mobile-first, measured — see docs/research/
   FLUID-DYNAMICS-2026-10-23.md): <=480 live particles, brute-force
   neighbor loop (480^2 = 115k pairs, early-out on squared distance),
   fixed dt=1/120, max 2 substeps/frame, 1 draw call (THREE.Points).

   LIFECYCLE: this layer is INERT except during finisher/X-ray beats.
   fluidBurst() is fired from the finisher's killing-blow beat
   (game/js/finisher.js _fluidBurst, same fire-and-forget pattern as
   _xrayFlash). The FluidWorld runs its own rAF only while particles
   are alive, then parks itself — zero cost in neutral.

   CONTENT: stylized impact splash only. No dismemberment, no gore
   systems — per PR #872 the impact viz is X-ray reveal + deformation;
   this module adds the viscous splash at that same beat. The fluid
   color/preset is parameterized; content tuning is the owner's call.

   EFFEKSEER BOUNDARY (other track): Effekseer = general particles
   (sparks, smoke, energy, flashes). This module = viscous fluids
   ONLY (cohesion, breakup, adhesion, drips, stains). No overlap;
   both can fire from the same finisher beat via separate hooks.

   TESTING: the sim core has no THREE/DOM imports — THREE is injected
   into FluidRenderer, canvas into SplatLayer (see ./decals.js) — so
   node --test game/tests/fluid-decals.test.mjs covers the physics.
   ============================================================ */

/* ---------------- tuning ---------------- */
export const FLUID = Object.freeze({
  MAX_PARTICLES: 480,
  SUB_DT: 1 / 120,
  MAX_SUBSTEPS: 2,
  SMOOTH_R: 0.06,          // smoothing length h (m); pair radius = 2h
  GRAVITY: -9.8,
  FLOOR_Y: 0,              // arena ground plane
  // breakup: speed threshold scales with viscosity (thicker = harder)
  BREAKUP_BASE_V: 7.5,     // m/s at visc = 1
  BREAKUP_MAX_DEPTH: 2,
  MIN_RADIUS: 0.006,
});

/* Viscous presets. visc = the variable-viscosity dial (DualSPHysics
   non-Newtonian branch analogue): scales artificial-viscosity damping,
   Stokes drag, adhesion probability, and breakup resistance. */
export const PRESETS = Object.freeze({
  blood: Object.freeze({ visc: 1.0,  stickV: 1.15, stickP: 0.78, rest: 0.22, drag: 0.55, cohes: 2.6, soak: 1.6, color: [0.42, 0.045, 0.06],  css: '#8f1d26' }),
  mud:   Object.freeze({ visc: 2.2,  stickV: 1.9,  stickP: 0.94, rest: 0.08, drag: 1.4,  cohes: 4.2, soak: 0.9, color: [0.23, 0.15, 0.09],  css: '#4a3423' }),
  ink:   Object.freeze({ visc: 0.45, stickV: 0.7,  stickP: 0.5,  rest: 0.42, drag: 0.25, cohes: 1.4, soak: 2.4, color: [0.05, 0.05, 0.10],  css: '#14141f' }),
});

/* Deterministic PRNG (mulberry32) so bursts are reproducible. */
export function rng32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/* ---------------- pure sim core (no THREE, no DOM) ---------------- */

let _nextId = 1;

export class FluidSim {
  constructor(opts = {}) {
    this.maxP = opts.maxParticles || FLUID.MAX_PARTICLES;
    this.h = FLUID.SMOOTH_R;
    this.pairR2 = (2 * this.h) * (2 * this.h);
    this.particles = [];
    this._acc = 0;
    this.onEvent = null;      // ({type:'stamp', x, z, r, preset}) — decals
    this._rand = rng32(opts.seed || 1234);
    this.steps = 0;           // diagnostics
  }

  get activeCount() { return this.particles.length; }

  /* Spawn one droplet. Returns the particle or null when over budget
     (recycles the oldest stuck particle first, else the oldest). */
  spawn(x, y, z, vx, vy, vz, r, preset, life = 3.2) {
    const P = PRESETS[preset] || PRESETS.blood;
    if (this.particles.length >= this.maxP) {
      let idx = this.particles.findIndex((p) => p.stuck);
      if (idx < 0) idx = 0;
      this.particles.splice(idx, 1);
    }
    const p = {
      id: _nextId++, x, y, z, vx, vy, vz, r,
      visc: P.visc, preset, life, maxLife: life,
      stuck: false, coat: null, // coat: {cx,cy,cz,cr} sphere when coating a fighter
      stampT: 0, depth: 0, seed: this._rand(),
    };
    this.particles.push(p);
    return p;
  }

  /* Cone burst of droplets at origin along dir. */
  burst(ox, oy, oz, dx, dy, dz, opts = {}) {
    const { count = 90, speed = 5.5, spread = 0.55, preset = 'blood',
            rMin = 0.012, rMax = 0.030, life = 3.2, seed = null } = opts;
    const rand = seed != null ? rng32(seed) : this._rand;
    const dl = Math.hypot(dx, dy, dz) || 1;
    const ux = dx / dl, uy = dy / dl, uz = dz / dl;
    for (let i = 0; i < count; i++) {
      // spawn inside a small volume, not a mathematical point: a real
      // impact sprays from a contact patch, and co-located particles
      // degenerate the neighbor loop into a 480^2 worst case.
      const jr = 0.05 * Math.cbrt(rand());
      const jt = rand() * Math.PI * 2, jp = Math.acos(2 * rand() - 1);
      const jx0 = jr * Math.sin(jp) * Math.cos(jt);
      const jy0 = jr * Math.cos(jp) * 0.6; // flatter disc, spray goes outward
      const jz0 = jr * Math.sin(jp) * Math.sin(jt);
      // random perpendicular for cone spread
      const a = rand() * Math.PI * 2, s = rand() * spread;
      const px = -uz, pz = ux; // one perpendicular (dir never straight up here)
      const pl = Math.hypot(px, pz) || 1;
      const jx = (px / pl) * Math.cos(a) * s, jz = (pz / pl) * Math.cos(a) * s;
      const jy = Math.sin(a) * s * 0.7 + rand() * 0.25; // slight upward bias
      const sp = speed * (0.45 + rand() * 0.9);
      const vl = Math.hypot(ux + jx, uy + jy, uz + jz) || 1;
      this.spawn(
        ox + jx0, oy + jy0, oz + jz0,
        ((ux + jx) / vl) * sp, ((uy + jy) / vl) * sp, ((uz + jz) / vl) * sp,
        rMin + rand() * (rMax - rMin), preset,
        life * (0.7 + rand() * 0.6));
    }
    return this;
  }

  /* One fixed substep. colliders: [{cx,cy,cz,cr}] fighter spheres. */
  substep(colliders = []) {
    const dt = FLUID.SUB_DT, h2 = this.pairR2;
    const ps = this.particles, n = ps.length;
    // pairwise: repulsion (positional), cohesion, artificial viscosity
    for (let i = 0; i < n; i++) {
      const a = ps[i];
      if (a.stuck && !a.coat) continue; // soaked into ground: skip pair work
      for (let j = i + 1; j < n; j++) {
        const b = ps[j];
        if (b.stuck && !b.coat) continue;
        const dx = a.x - b.x, dy = a.y - b.y, dz = a.z - b.z;
        const d2 = dx * dx + dy * dy + dz * dz;
        if (d2 >= h2 || d2 < 1e-12) continue;
        const d = Math.sqrt(d2), nx = dx / d, ny = dy / d, nz = dz / d;
        const rr = a.r + b.r;
        if (d < rr) {
          // positional de-overlap — unconditionally stable
          const push = (rr - d) * 0.5 * 0.6;
          a.x += nx * push; a.y += ny * push; a.z += nz * push;
          b.x -= nx * push; b.y -= ny * push; b.z -= nz * push;
        } else if (d < 2 * this.h) {
          // cohesion band: pull together (surface-tension stand-in)
          const mu = (a.visc + b.visc) * 0.5;
          const coh = 2.0 * mu * (1 - d / (2 * this.h)) * dt;
          a.vx -= nx * coh; a.vy -= ny * coh; a.vz -= nz * coh;
          b.vx += nx * coh; b.vy += ny * coh; b.vz += nz * coh;
        }
        // Monaghan-style artificial viscosity on approaching pairs
        const rvx = a.vx - b.vx, rvy = a.vy - b.vy, rvz = a.vz - b.vz;
        const vn = rvx * nx + rvy * ny + rvz * nz;
        if (vn < 0) {
          const mu = (a.visc + b.visc) * 0.5;
          const damp = Math.min(0.5, 0.14 * mu * (1 - d / (2 * this.h)));
          const imp = -vn * damp;
          a.vx += nx * imp * 0.5; a.vy += ny * imp * 0.5; a.vz += nz * imp * 0.5;
          b.vx -= nx * imp * 0.5; b.vy -= ny * imp * 0.5; b.vz -= nz * imp * 0.5;
        }
      }
    }
    // integrate + boundaries
    const dead = [];
    for (let i = 0; i < n; i++) {
      const p = ps[i], P = PRESETS[p.preset] || PRESETS.blood;
      if (p.stuck && !p.coat) {
        // soaked into the ground: shrink, then despawn (stain stays as decal)
        p.life -= dt * P.soak;
        p.r *= (1 - dt * 1.5);
        if (p.life <= 0 || p.r < 0.004) dead.push(i);
        continue;
      }
      // gravity + Stokes-ish drag scaled by viscosity
      p.vy += FLUID.GRAVITY * dt;
      const dr = Math.max(0, 1 - P.drag * p.visc * dt);
      p.vx *= dr; p.vy *= dr; p.vz *= dr;
      p.x += p.vx * dt; p.y += p.vy * dt; p.z += p.vz * dt;
      p.life -= dt * 0.25;

      if (p.coat) this._coatSlide(p, dt, P);
      else {
        this._collideGround(p, P);
        this._collideSpheres(p, colliders, P, dt);
      }
      this._maybeBreak(p, P);

      if (p.life <= 0 || p.y < -2) dead.push(i);
    }
    for (let k = dead.length - 1; k >= 0; k--) ps.splice(dead[k], 1);
    this.steps++;
  }

  /* Frame update: fixed-step accumulator, max 2 substeps (never spiral). */
  update(dt, colliders = []) {
    if (!this.particles.length) return;
    this._acc = Math.min(this._acc + Math.min(dt, 0.1), FLUID.SUB_DT * FLUID.MAX_SUBSTEPS);
    let n = 0;
    while (this._acc >= FLUID.SUB_DT && n < FLUID.MAX_SUBSTEPS) {
      this.substep(colliders);
      this._acc -= FLUID.SUB_DT;
      n++;
      if (!this.particles.length) { this._acc = 0; break; }
    }
    if (n === FLUID.MAX_SUBSTEPS) this._acc = 0; // drop backlog on hitches
  }

  _emitStamp(x, z, r, preset) {
    if (this.onEvent) {
      try { this.onEvent({ type: 'stamp', x, z, r, preset }); } catch (e) { /* never break sim */ }
    }
  }

  /* Ground plane: DBC-inspired stick-or-bounce. Slow => sticks (coats),
     stamps a splat, soaks in. Fast => bounces + smaller splat. */
  _collideGround(p, P) {
    if (p.y >= p.r) return;
    const vn = -p.vy; // impact normal speed
    const stickV = P.stickV * (0.55 + 0.45 * p.visc);
    p.y = p.r;
    if (vn < stickV && this._rand() < P.stickP) {
      p.stuck = true; p.vx = p.vy = p.vz = 0;
      p.life = Math.min(p.life, 1.4);
      this._emitStamp(p.x, p.z, p.r * (2.2 + vn * 0.8), p.preset);
    } else {
      p.vy = vn * P.rest;
      p.vx *= 0.6; p.vz *= 0.6;
      this._emitStamp(p.x, p.z, p.r * (1.2 + vn * 0.35), p.preset);
    }
  }

  /* Fighter sphere colliders: coat (stick to surface, then slide/drip
     under gravity — "roll down surfaces") or deflect. */
  _collideSpheres(p, colliders, P, dt) {
    for (const c of colliders) {
      const dx = p.x - c.cx, dy = p.y - c.cy, dz = p.z - c.cz;
      const d2 = dx * dx + dy * dy + dz * dz, rr = c.cr + p.r;
      if (d2 >= rr * rr || d2 < 1e-12) continue;
      const d = Math.sqrt(d2), nx = dx / d, ny = dy / d, nz = dz / d;
      const vn = -(p.vx * nx + p.vy * ny + p.vz * nz); // approach speed
      const stickV = P.stickV * 0.8 * (0.55 + 0.45 * p.visc);
      if (vn < stickV && this._rand() < P.stickP * 0.9) {
        p.coat = c;
        p.x = c.cx + nx * c.cr; p.y = c.cy + ny * c.cr; p.z = c.cz + nz * c.cr;
        p.vx = p.vy = p.vz = 0;
        p.stampT = 0;
      } else {
        // deflect along the surface
        p.x = c.cx + nx * rr; p.y = c.cy + ny * rr; p.z = c.cz + nz * rr;
        const dot = p.vx * nx + p.vy * ny + p.vz * nz;
        if (dot < 0) { p.vx -= 1.6 * dot * nx; p.vy -= 1.6 * dot * ny; p.vz -= 1.6 * dot * nz; }
        p.vx *= 0.7; p.vy *= 0.7; p.vz *= 0.7;
      }
      return;
    }
  }

  /* A coated droplet slides along the sphere under tangential gravity,
     stamping a drip trail — the "rolls down surfaces" behavior. */
  _coatSlide(p, dt, P) {
    const c = p.coat;
    let dx = p.x - c.cx, dy = p.y - c.cy, dz = p.z - c.cz;
    const d = Math.hypot(dx, dy, dz) || 1;
    const nx = dx / d, ny = dy / d, nz = dz / d;
    // tangential gravity
    const gx = 0, gy = FLUID.GRAVITY, gz = 0;
    const dot = gx * nx + gy * ny + gz * nz;
    const tx = gx - dot * nx, ty = gy - dot * ny, tz = gz - dot * nz;
    const slide = 0.35 / (0.4 + p.visc); // thicker fluid slides slower
    // (tx,ty,tz) already carries |g| — scale by the slide factor only
    p.vx += tx * dt * slide; p.vy += ty * dt * slide; p.vz += tz * dt * slide;
    const dr = Math.max(0, 1 - 3.0 * p.visc * dt);
    p.vx *= dr; p.vy *= dr; p.vz *= dr;
    p.x += p.vx * dt; p.y += p.vy * dt; p.z += p.vz * dt;
    // re-project to the surface
    dx = p.x - c.cx; dy = p.y - c.cy; dz = p.z - c.cz;
    const d2 = Math.hypot(dx, dy, dz) || 1;
    p.x = c.cx + (dx / d2) * c.cr; p.y = c.cy + (dy / d2) * c.cr; p.z = c.cz + (dz / d2) * c.cr;
    p.life -= dt * P.soak * 0.8;
    p.stampT += dt;
    if (p.stampT > 0.3) { // drip trail stamp (project to ground below)
      p.stampT = 0;
      this._emitStamp(p.x, p.z, p.r * 1.4, p.preset);
    }
    if (p.life <= 0) { p.coat = null; p.stuck = true; p.life = 0.3; }
  }

  /* Droplet breakup along the velocity vector, conserving volume.
     Children inherit 0.8x the parent velocity so breakup is single-level:
     the spray fragments once on impact instead of cascading every frame
     (the cascade was a 3x particle-count spike in the first 2 substeps). */
  _maybeBreak(p, P) {
    if (p.depth >= FLUID.BREAKUP_MAX_DEPTH || p.r <= FLUID.MIN_RADIUS) return;
    const sp = Math.hypot(p.vx, p.vy, p.vz);
    const thresh = FLUID.BREAKUP_BASE_V * (0.55 + 0.45 * p.visc);
    if (sp < thresh) return;
    const k = sp > thresh * 1.7 ? 3 : 2;
    const nr = p.r / Math.cbrt(k);
    const rand = this._rand;
    for (let i = 0; i < k - 1; i++) {
      // children spray off the parent's velocity vector with a small cone
      const s = 0.12 + rand() * 0.1;
      const a = rand() * Math.PI * 2;
      this.spawn(
        p.x, p.y, p.z,
        p.vx * 0.8 + Math.cos(a) * sp * s,
        p.vy * 0.8 + (rand() - 0.3) * sp * s,
        p.vz * 0.8 + Math.sin(a) * sp * s,
        nr, p.preset, p.life * 0.8);
      this.particles[this.particles.length - 1].depth = p.depth + 1;
    }
    p.r = nr; p.depth++;
    p.vx *= 0.8; p.vy *= 0.8; p.vz *= 0.8;
    p.life *= 0.8;
  }

  /* Sum of droplet volumes — test hook for breakup conservation. */
  totalVolume() {
    let v = 0;
    for (const p of this.particles) v += p.r * p.r * p.r;
    return v * (4 / 3) * Math.PI;
  }
}

/* ---------------- three.js render layer (THREE injected) ---------------- */

const _VS = `
attribute float aSize;
attribute vec3 aColor;
attribute float aAlpha;
varying vec3 vColor;
varying float vAlpha;
void main() {
  vColor = aColor; vAlpha = aAlpha;
  vec4 mv = modelViewMatrix * vec4(position, 1.0);
  float px = aSize * (320.0 / max(0.1, -mv.z));
  gl_PointSize = min(px, 220.0); /* mobile point-size clamp */
  gl_Position = projectionMatrix * mv;
}`;
const _FS = `
varying vec3 vColor;
varying float vAlpha;
void main() {
  vec2 uv = gl_PointCoord - 0.5;
  float d = length(uv) * 2.0;
  if (d > 1.0) discard;
  float body = smoothstep(1.0, 0.55, d);
  float rim = smoothstep(0.45, 1.0, d);
  vec3 col = vColor * (1.0 - 0.45 * rim); /* viscous rim darkening */
  gl_FragColor = vec4(col, vAlpha * body);
}`;

export class FluidRenderer {
  constructor(THREE, scene, opts = {}) {
    this.THREE = THREE;
    this.maxP = opts.maxParticles || FLUID.MAX_PARTICLES;
    const g = new THREE.BufferGeometry();
    this._pos = new Float32Array(this.maxP * 3);
    this._size = new Float32Array(this.maxP);
    this._col = new Float32Array(this.maxP * 3);
    this._alpha = new Float32Array(this.maxP);
    g.setAttribute('position', new THREE.BufferAttribute(this._pos, 3).setUsage(THREE.DynamicDrawUsage));
    g.setAttribute('aSize', new THREE.BufferAttribute(this._size, 1).setUsage(THREE.DynamicDrawUsage));
    g.setAttribute('aColor', new THREE.BufferAttribute(this._col, 3).setUsage(THREE.DynamicDrawUsage));
    g.setAttribute('aAlpha', new THREE.BufferAttribute(this._alpha, 1).setUsage(THREE.DynamicDrawUsage));
    g.setDrawRange(0, 0);
    this._mat = new THREE.ShaderMaterial({
      vertexShader: _VS, fragmentShader: _FS,
      transparent: true, depthWrite: false, depthTest: true,
    });
    this.points = new THREE.Points(g, this._mat);
    this.points.frustumCulled = false;
    this.points.renderOrder = 5;
    this.points.visible = false;
    scene.add(this.points);
    this._scene = scene;
  }

  /* Copy live particles into the GPU buffers. One draw call. */
  sync(sim) {
    const ps = sim.particles, n = Math.min(ps.length, this.maxP);
    for (let i = 0; i < n; i++) {
      const p = ps[i], P = PRESETS[p.preset] || PRESETS.blood;
      this._pos[i * 3] = p.x; this._pos[i * 3 + 1] = p.y; this._pos[i * 3 + 2] = p.z;
      this._size[i] = p.r * 2;
      const fade = Math.min(1, p.life / (p.maxLife * 0.35));
      this._col[i * 3] = P.color[0]; this._col[i * 3 + 1] = P.color[1]; this._col[i * 3 + 2] = P.color[2];
      this._alpha[i] = 0.92 * Math.min(1, fade + 0.25);
    }
    const g = this.points.geometry;
    g.setDrawRange(0, n);
    g.attributes.position.needsUpdate = true;
    g.attributes.aSize.needsUpdate = true;
    g.attributes.aColor.needsUpdate = true;
    g.attributes.aAlpha.needsUpdate = true;
    this.points.visible = n > 0;
  }

  dispose() {
    try {
      this._scene.remove(this.points);
      this.points.geometry.dispose();
      this._mat.dispose();
    } catch (e) { /* never break teardown */ }
  }
}

/* ---------------- world: sim + renderer + decals, self-ticking ---------------- */

export class FluidWorld {
  constructor(THREE, scene, SplatLayer, opts = {}) {
    this.sim = new FluidSim({ seed: opts.seed });
    this.renderer = new FluidRenderer(THREE, scene, opts);
    const rect = opts.rect || { minX: -6, maxX: 6, minZ: -6, maxZ: 6 };
    this.splats = new SplatLayer({ size: opts.splatSize || 1024, rect });
    this.splats.attach(THREE, scene, opts.splatY == null ? 0.02 : opts.splatY);
    this.sim.onEvent = (ev) => {
      if (ev.type === 'stamp') {
        const P = PRESETS[ev.preset] || PRESETS.blood;
        this.splats.stamp(ev.x, ev.z, Math.min(0.35, ev.r), P.css, 0.85);
      }
    };
    this.colliders = [];
    this._raf = 0;
    this._last = 0;
    this._boundTick = () => this._tick();
  }

  setColliders(colliders) { this.colliders = colliders || []; }

  burstAt(x, y, z, dx, dy, dz, opts) {
    this.sim.burst(x, y, z, dx, dy, dz, opts);
    this._kick();
  }

  clearSplats() { this.splats.clear(); }

  _kick() {
    if (this._raf) return;
    this._last = performance.now();
    const loop = () => {
      this._raf = requestAnimationFrame(loop);
      this._tick();
    };
    this._raf = requestAnimationFrame(loop);
  }

  _tick() {
    const now = performance.now();
    const dt = Math.min(0.1, (now - this._last) / 1000);
    this._last = now;
    this.sim.update(dt, this.colliders);
    this.renderer.sync(this.sim);
    this.splats.uploadThrottled(now);
    if (!this.sim.particles.length) {
      cancelAnimationFrame(this._raf);
      this._raf = 0;
      this.renderer.sync(this.sim); // hides the points
    }
  }

  dispose() {
    try { if (this._raf) cancelAnimationFrame(this._raf); } catch (e) {}
    this._raf = 0;
    this.renderer.dispose();
    this.splats.dispose();
  }
}

/* ---------------- finisher hook ---------------- */

/* Best-effort world position of a fighter object. */
function _fighterPos(f) {
  try {
    const m = (f && (f.mesh || f.object3d || f.node)) || null;
    const p = (m && m.position) || (f && f.position) || (f && f.pos);
    if (p && typeof p.x === 'number') return { x: p.x, y: p.y || 0, z: p.z || 0 };
  } catch (e) { /* fall through */ }
  return { x: 0, y: 0, z: 0 };
}

/* One shared FluidWorld per game instance (never two sims). */
async function _getWorld(game) {
  if (game._fxFluidWorld) return game._fxFluidWorld;
  const scene = game.scene || game.threeScene || game.world;
  if (!scene) return null;
  let THREE = game.THREE || (typeof globalThis !== 'undefined' && globalThis.THREE) || null;
  if (!THREE) {
    try { THREE = await import('three'); }
    catch (e) { return null; }
  }
  const { SplatLayer } = await import('./decals.js');
  const rect = (game.arena && game.arena.bounds) || { minX: -6, maxX: 6, minZ: -6, maxZ: 6 };
  const world = new FluidWorld(THREE, scene, SplatLayer, { rect });
  game._fxFluidWorld = world;
  return world;
}

/* Fire-and-forget entry called from the finisher's killing-blow beat.
   Mirrors _xrayFlash: a missed splash never breaks the fight. */
export function fluidBurst(spec) {
  try {
    const { game, attacker, victim, power = 0.7, fluid = null } = spec || {};
    if (!game) return;
    _getWorld(game).then((world) => {
      try {
        if (!world) return;
        const vp = _fighterPos(victim);
        const ap = _fighterPos(attacker);
        let dx = vp.x - ap.x, dz = vp.z - ap.z;
        const dl = Math.hypot(dx, dz);
        if (dl < 1e-3) { dx = 0; dz = -1; } else { dx /= dl; dz /= dl; }
        // fighter collider: torso-sized sphere at the victim
        world.setColliders([{ cx: vp.x, cy: (vp.y || 0) + 0.95, cz: vp.z, cr: 0.42 }]);
        const preset = (fluid && fluid.preset) || 'blood';
        const intensity = Math.min(1.4, Math.max(0.4,
          (fluid && fluid.intensity) || power || 0.7));
        const count = Math.round(70 + 90 * intensity);
        world.burstAt(
          vp.x, (vp.y || 0) + 1.05, vp.z,   // impact point: upper torso
          dx * 0.7, 0.35, dz * 0.7,          // mostly outward + up
          { count, speed: 4.2 + 2.4 * intensity, spread: 0.6, preset,
            rMin: 0.012, rMax: 0.030 + 0.012 * intensity,
            seed: (Date.now() ^ (Math.random() * 1e9)) >>> 0 });
      } catch (e) { /* a bad splash never breaks the fight */ }
    }).catch(() => { /* no world — finisher continues */ });
  } catch (e) { /* sync failure — never break the finisher */ }
}
