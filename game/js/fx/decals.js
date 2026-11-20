/* ============================================================
   WESTERN HEART — render-to-texture blood/splatter decals
   Track 3 (fluid dynamics), companion to ./fluid.js.

   THE PIPELINE: fluid particles that hit a surface don't stay as
   floating meshes. On stick/bounce each particle emits a stamp event;
   SplatLayer bakes those stamps into ONE dynamic canvas texture on a
   single ground plane. Permanent per-round stains, one draw call,
   no mesh-per-splat memory growth (the mobile constraint in the
   track brief).

   Memory: one 1024x1024 RGBA canvas (4 MB) + one GPU texture (4 MB).
   Stamps are draw calls on the 2D canvas, throttled to GPU upload at
   most every 150 ms. Cleared on round reset via clear().

   WHAT'S WIRED: ground splat layer (fluid.js FluidWorld owns one).
   WHAT'S SPEC'D (see docs/research/FLUID-DYNAMICS-2026-10-23.md):
   fighter-body stain decals — pooled decal quads projected onto the
   victim at impact, parented to bones, capped at 12/fighter. Not wired
   this pass: per-fighter texture-space baking needs the attire /
   character texture pipeline to land first.

   No THREE import at module top level (injected into attach()); the
   stamp math is pure and covered by game/tests/fluid-decals.test.mjs.
   ============================================================ */

/* World (x,z) -> texture UV over the arena rect. v=0 is minZ. */
export function worldToUV(x, z, rect) {
  const w = rect.maxX - rect.minX, d = rect.maxZ - rect.minZ;
  return { u: (x - rect.minX) / w, v: (z - rect.minZ) / d };
}

export function uvToWorld(u, v, rect) {
  const w = rect.maxX - rect.minX, d = rect.maxZ - rect.minZ;
  return { x: rect.minX + u * w, z: rect.minZ + v * d };
}

/* Deterministic PRNG so a stamp's blob layout is reproducible. */
export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/* Blob layout for one splat: irregular main blot + satellites.
   radiusUV is the main blot radius in UV units; returns
   [{u, v, r, a}] with r in UV units, a = alpha multiplier. */
export function computeSplat(u, v, radiusUV, seed) {
  const rand = mulberry32(seed);
  const blobs = [{ u, v, r: radiusUV, a: 1 }];
  const nSat = 3 + Math.floor(rand() * 4);
  for (let i = 0; i < nSat; i++) {
    const ang = rand() * Math.PI * 2;
    const dist = radiusUV * (0.9 + rand() * 1.3);
    blobs.push({
      u: u + Math.cos(ang) * dist,
      v: v + Math.sin(ang) * dist,
      r: radiusUV * (0.12 + rand() * 0.3),
      a: 0.5 + rand() * 0.4,
    });
  }
  // dark rim blobs: a couple of offset arcs for the irregular edge
  for (let i = 0; i < 2; i++) {
    const ang = rand() * Math.PI * 2;
    blobs.push({
      u: u + Math.cos(ang) * radiusUV * 0.95,
      v: v + Math.sin(ang) * radiusUV * 0.95,
      r: radiusUV * (0.35 + rand() * 0.25),
      a: 0.35,
    });
  }
  return blobs;
}

export class SplatLayer {
  constructor({ size = 1024, rect = null, canvas = null } = {}) {
    this.size = size;
    this.rect = rect || { minX: -6, maxX: 6, minZ: -6, maxZ: 6 };
    if (canvas) {
      this.canvas = canvas;
    } else if (typeof document !== 'undefined' && document.createElement) {
      this.canvas = document.createElement('canvas');
      this.canvas.width = size; this.canvas.height = size;
    } else {
      throw new Error('SplatLayer: no canvas and no document — inject a canvas (tests do).');
    }
    this.ctx = this.canvas.getContext('2d');
    this.dirty = false;
    this.stampCount = 0;
    this._lastUpload = 0;
    this._mesh = null;
    this._texture = null;
  }

  /* Bake one splat at world (x, z). radiusWorld in meters. */
  stamp(x, z, radiusWorld, cssColor, alpha = 0.85) {
    const { u, v } = worldToUV(x, z, this.rect);
    if (u < -0.08 || u > 1.08 || v < -0.08 || v > 1.08) return false;
    const w = this.rect.maxX - this.rect.minX;
    const radiusUV = Math.max(0.002, radiusWorld / w);
    const seed = ((u * 1e6) | 0) ^ ((v * 1e6) | 0) ^ this.stampCount;
    const blobs = computeSplat(u, v, radiusUV, seed);
    const ctx = this.ctx, S = this.size;
    ctx.save();
    for (const b of blobs) {
      const px = b.u * S, py = b.v * S, pr = Math.max(1, b.r * S);
      const g = ctx.createRadialGradient(px, py, pr * 0.1, px, py, pr);
      g.addColorStop(0, cssColor);
      g.addColorStop(0.75, cssColor);
      g.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.globalAlpha = Math.min(1, alpha * b.a);
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(px, py, pr, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
    ctx.globalAlpha = 1;
    this.dirty = true;
    this.stampCount++;
    return true;
  }

  /* Push the canvas to the GPU, throttled. nowMs from performance.now(). */
  uploadThrottled(nowMs, minIntervalMs = 150) {
    if (!this.dirty) return false;
    if (nowMs - this._lastUpload < minIntervalMs) return false;
    this._lastUpload = nowMs;
    if (this._texture) this._texture.needsUpdate = true;
    this.dirty = false;
    return true;
  }

  forceUpload() {
    if (this._texture) this._texture.needsUpdate = true;
    this.dirty = false;
  }

  clear() {
    this.ctx.clearRect(0, 0, this.size, this.size);
    this.dirty = true;
    this.stampCount = 0;
  }

  /* Build the THREE mesh: one plane over the arena rect. THREE injected. */
  attach(THREE, scene, y = 0.02) {
    if (this._mesh) return this._mesh;
    const w = this.rect.maxX - this.rect.minX, d = this.rect.maxZ - this.rect.minZ;
    this._texture = new THREE.CanvasTexture(this.canvas);
    this._texture.colorSpace = THREE.SRGBColorSpace;
    this._texture.anisotropy = 4;
    const geo = new THREE.PlaneGeometry(w, d);
    const mat = new THREE.MeshBasicMaterial({
      map: this._texture, transparent: true, depthWrite: false,
      polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2,
    });
    this._mesh = new THREE.Mesh(geo, mat);
    this._mesh.rotation.x = -Math.PI / 2;
    // PlaneGeometry UVs: u left->right, v bottom->top; after -90° X rotation
    // the plane's v=1 edge faces -z (minZ). CanvasTexture flipY=true (the
    // default) puts canvas row 0 at v=1, so worldToUV's v=0-at-minZ stamps
    // land on the minZ side of the plane. u is unmirrored (minX -> px 0).
    this._mesh.position.set((this.rect.minX + this.rect.maxX) / 2, y,
      (this.rect.minZ + this.rect.maxZ) / 2);
    this._mesh.renderOrder = 2;
    scene.add(this._mesh);
    return this._mesh;
  }

  dispose() {
    try {
      if (this._mesh) {
        if (this._mesh.parent) this._mesh.parent.remove(this._mesh);
        this._mesh.geometry.dispose();
        this._mesh.material.dispose();
      }
      if (this._texture) this._texture.dispose();
    } catch (e) { /* never break teardown */ }
    this._mesh = null; this._texture = null;
  }
}
