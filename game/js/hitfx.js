/* ============================================================
   WESTERN HEART — HitFX (Tekken-style hit effects)
   Replaces the prototype _spawnImpact spheres (game.js) with the
   real Tekken hit-feedback stack, per the teardown docs:
     • teardown/tekken3/docs/TEKKEN3-RIG-LESSONS.md — hitstop /
       hit-freeze is part of the move data; effects are simple
       proxy shapes, never the visible mesh.
     • teardown/tekken7 Tekken 8 moveset docs — a landed hit plays
       a Hit Condition: damage + reaction + presentation.
   Tekken's on-hit presentation (T3–T8, consistent across the
   series):
     1. HIT SPARK — jagged star-burst sprite at the impact point.
        Gold-white on normal hits, red-orange and larger on
        counter hits, pale blue and smaller on block.
     2. DEBRIS SPARKS — small additive particles flying outward.
     3. SHOCKWAVE RING — expanding ring on heavy hits / KOs.
     4. SCREEN FLASH — brief fullscreen flash on counter / KO.
     5. HITSTOP — the whole sim freezes for N frames (game.js
        _hitStop); HitFX.update receives dt=0 during the freeze so
        the spark holds, then bursts — exactly like Tekken.
     6. CAMERA SHAKE — arena.shake, tiered by hit weight.
   All textures are canvas-generated (no asset files). All motion
   is dt-driven (game time), never requestAnimationFrame wall-time.
   ============================================================ */
import * as THREE from 'three';

/* ---- canvas texture builders ---- */
function _canvas(size) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  return [c, c.getContext('2d')];
}

/* Tekken's iconic spark: a jagged multi-point star with a hot core.
   Drawn white; tinted per hit type via material.color. */
function makeSparkTexture() {
  const [c, ctx] = _canvas(128);
  const cx = 64, cy = 64;
  // hot core
  let g = ctx.createRadialGradient(cx, cy, 0, cx, cy, 26);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.55, 'rgba(255,255,255,0.85)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 128, 128);
  // jagged rays — deterministic pseudo-random so every spark matches
  let seed = 7;
  const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  ctx.globalCompositeOperation = 'lighter';
  const spikes = 12;
  for (let i = 0; i < spikes; i++) {
    const a = (i / spikes) * Math.PI * 2 + rnd() * 0.3;
    const len = 30 + rnd() * 32;
    const w = 2.5 + rnd() * 4;
    const grad = ctx.createLinearGradient(cx, cy, cx + Math.cos(a) * len, cy + Math.sin(a) * len);
    grad.addColorStop(0, 'rgba(255,255,255,0.95)');
    grad.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.strokeStyle = grad;
    ctx.lineWidth = w;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(cx + Math.cos(a) * 8, cy + Math.sin(a) * 8);
    ctx.lineTo(cx + Math.cos(a) * len, cy + Math.sin(a) * len);
    ctx.stroke();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/* soft dot for debris particles */
function makeDotTexture() {
  const [c, ctx] = _canvas(64);
  const g = ctx.createRadialGradient(32, 32, 0, 32, 32, 30);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(0.4, 'rgba(255,255,255,0.7)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 64, 64);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/* shockwave ring for heavy hits */
function makeRingTexture() {
  const [c, ctx] = _canvas(128);
  ctx.strokeStyle = 'rgba(255,255,255,0.9)';
  ctx.lineWidth = 7;
  ctx.beginPath(); ctx.arc(64, 64, 52, 0, Math.PI * 2); ctx.stroke();
  ctx.strokeStyle = 'rgba(255,255,255,0.35)';
  ctx.lineWidth = 16;
  ctx.beginPath(); ctx.arc(64, 64, 52, 0, Math.PI * 2); ctx.stroke();
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/* ---- per-type presentation (Tekken color language) ---- */
const STYLE = {
  hit:     { color: 0xffd76a, spark: 1.00, debris: 10, ring: false, flash: 0.00, life: 0.26 },
  heavy:   { color: 0xffbe3c, spark: 1.35, debris: 14, ring: true,  flash: 0.10, life: 0.32 },
  counter: { color: 0xff4a1e, spark: 1.60, debris: 18, ring: true,  flash: 0.22, life: 0.36 },
  block:   { color: 0x9fd8ff, spark: 0.65, debris: 6,  ring: false, flash: 0.00, life: 0.20 },
  grab:    { color: 0xfff2c8, spark: 1.20, debris: 12, ring: false, flash: 0.06, life: 0.30 },
  ko:      { color: 0xffe9a8, spark: 2.10, debris: 24, ring: true,  flash: 0.32, life: 0.45 },
  surge:   { color: 0xffffff, spark: 1.80, debris: 20, ring: true,  flash: 0.28, life: 0.40 },
};

// Exported for the proof harness (renders the real textures to PNG).
export { makeSparkTexture, makeDotTexture, makeRingTexture, STYLE };

export class HitFX {
  constructor(scene) {
    this.scene = scene;
    this._items = [];
    this._tex = {
      spark: makeSparkTexture(),
      dot: makeDotTexture(),
      ring: makeRingTexture(),
    };
    this._flashT = 0;
    this._flashMax = 0;
    this._flashEl = null;
  }

  /* Fullscreen impact flash (counter / KO / surge). The div + style are
     created lazily so no index.html / CSS edits are needed. */
  _flash(strength) {
    if (strength <= 0) return;
    if (!this._flashEl) {
      const el = document.createElement('div');
      el.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:60;opacity:0;' +
        'background:radial-gradient(circle at 50% 50%, rgba(255,255,255,0.95) 0%,' +
        'rgba(255,244,214,0.45) 45%, rgba(255,244,214,0) 75%);';
      document.body.appendChild(el);
      this._flashEl = el;
    }
    this._flashT = 0.14;
    this._flashMax = strength;
    this._flashEl.style.opacity = String(strength);
  }

  /* Spawn the full Tekken on-hit stack at a world-space impact point.
     type: hit | heavy | counter | block | grab | ko | surge
     opts: { scale, color (override), dirX (knock direction, biases debris) } */
  spawn(type, x, y, z, opts = {}) {
    const st = STYLE[type] || STYLE.hit;
    const scale = opts.scale || 1;
    const color = opts.color != null ? opts.color : st.color;
    const dirX = opts.dirX || 0;

    // 1 — the spark: pops to full size in ~2 frames, then dies over `life`
    const sm = new THREE.SpriteMaterial({
      map: this._tex.spark, color, transparent: true,
      blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false,
    });
    const spark = new THREE.Sprite(sm);
    const sparkSize = 1.15 * st.spark * scale;
    spark.position.set(x, y, z);
    spark.scale.setScalar(0.2);
    spark.renderOrder = 999;
    this.scene.add(spark);
    this._items.push({ obj: spark, kind: 'spark', t: 0, life: st.life, size: sparkSize });

    // 2 — debris sparks, biased away from the attacker
    const n = st.debris;
    for (let i = 0; i < n; i++) {
      const dm = new THREE.SpriteMaterial({
        map: this._tex.dot, color, transparent: true,
        blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false,
      });
      const d = new THREE.Sprite(dm);
      d.position.set(x, y, z);
      const a = Math.random() * Math.PI * 2;
      const sp = 2.5 + Math.random() * 4.5;
      d.scale.setScalar(0.10 + Math.random() * 0.14);
      d.renderOrder = 998;
      this.scene.add(d);
      this._items.push({
        obj: d, kind: 'debris', t: 0, life: 0.35 + Math.random() * 0.2,
        vx: Math.cos(a) * sp + dirX * 3.0,
        vy: 1.5 + Math.random() * 3.5,
        vz: Math.sin(a) * sp * 0.7,
      });
    }

    // 3 — shockwave ring on heavy hits
    if (st.ring) {
      const rm = new THREE.SpriteMaterial({
        map: this._tex.ring, color, transparent: true,
        blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false,
      });
      const ring = new THREE.Sprite(rm);
      ring.position.set(x, y, z);
      ring.scale.setScalar(0.4);
      ring.renderOrder = 997;
      this.scene.add(ring);
      this._items.push({ obj: ring, kind: 'ring', t: 0, life: 0.32, size: 2.6 * scale });
    }

    // 4 — screen flash
    this._flash(st.flash * scale);
  }

  /* Advance all live effects by dt (game time). Called with dt=0 during
     hitstop so the whole stack freezes like Tekken, then bursts. */
  update(dt) {
    if (this._flashT > 0 && this._flashEl) {
      this._flashT -= dt;
      const f = Math.max(0, this._flashT / 0.14);
      this._flashEl.style.opacity = String(this._flashMax * f);
      if (this._flashT <= 0) this._flashEl.style.opacity = '0';
    }
    if (dt <= 0 || this._items.length === 0) return;
    const dead = [];
    for (const it of this._items) {
      it.t += dt;
      const k = it.t / it.life;
      if (k >= 1) { dead.push(it); continue; }
      if (it.kind === 'spark') {
        // Tekken pop: full size almost instantly, shrink+fade after
        const pop = Math.min(1, it.t / 0.035);
        const fade = 1 - Math.max(0, (k - 0.25) / 0.75);
        it.obj.scale.setScalar(Math.max(0.001, it.size * pop * (0.6 + 0.4 * fade)));
        it.obj.material.opacity = fade;
        it.obj.material.rotation += dt * 9;
      } else if (it.kind === 'debris') {
        it.vy -= 12 * dt;
        it.obj.position.x += it.vx * dt;
        it.obj.position.y += it.vy * dt;
        it.obj.position.z += it.vz * dt;
        if (it.obj.position.y < 0.03) { it.obj.position.y = 0.03; it.vy *= -0.35; }
        it.obj.material.opacity = 1 - k;
      } else if (it.kind === 'ring') {
        const e = 1 - Math.pow(1 - k, 2);
        it.obj.scale.setScalar(0.4 + (it.size - 0.4) * e);
        it.obj.material.opacity = 0.85 * (1 - k);
      }
    }
    for (const it of dead) {
      this.scene.remove(it.obj);
      it.obj.material.dispose();
      const i = this._items.indexOf(it);
      if (i >= 0) this._items.splice(i, 1);
    }
  }
}
