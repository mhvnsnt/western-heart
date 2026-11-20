/* ============================================================
   WESTERN HEART — WHHitFX (three-nebula GPU particle hit effects)
   Vendored: game/vendor/three-nebula/three-nebula.mjs (MIT).
   Loaded lazily by game/js/integration.js.

   Owner bug 2026-10-22: "HIT EFFECTS — current ones look prototype —
   pull Tekken's hit effects and replace." This module replaces the
   hand-rolled 8-sprite `_spawnImpact` with JSON-driven nebula emitters:
   impact bursts, heavy hits, KO explosion, block sparks, whiff dust,
   surge aura.

   API notes (three-nebula 13.x, flat exports — verified from the
   vendored README): Emitter#setRate(Rate)/setInitializers/setBehaviours,
   initializers Position/Mass/Radius/Life/RadialVelocity/BodySprite,
   behaviours Alpha/Scale/Color/Gravity, System#addRenderer(SpriteRenderer)
   /addEmitter/update, System.fromJSON for designer presets.

   Designers author effects in the Nebula designer, export JSON, drop into
   game/assets/fx/*.json and register via registerJSON() — no code per
   effect. The built-in presets below are code-shaped equivalents tuned
   for a Tekken-like feel: tight core flash + directional sparks.
   ============================================================ */

import * as THREE from 'three';

let Nebula = null;
async function loadNebula() {
  if (Nebula) return Nebula;
  Nebula = await import('three-nebula');
  return Nebula;
}

export class WHHitFX {
  constructor() {
    this.ready = false;
    this.system = null;
    this.scene = null;
    this.enabled = true;
    this._jsonPresets = {};
  }

  async init(scene, threeRenderer) {
    const N = await loadNebula();
    this.N = N;
    this.scene = scene;
    this.system = new N.System();
    // SpriteRenderer draws nebula sprite particles into our scene.
    this.system.addRenderer(new N.SpriteRenderer(scene, THREE));
    this.ready = true;
    return this;
  }

  /** Register a three-nebula System JSON preset (from the Nebula designer). */
  async registerJSON(name, json) {
    const N = this.N || await loadNebula();
    this._jsonPresets[name] = N.System.fromJSON(json);
  }

  _burst({ color = 0xffcf4d, count = 26, speed = 220, size = [4, 9],
           life = 0.45, gravity = -320, up = [0, 1, 0], spread = 180 } = {}) {
    const N = this.N;
    const e = new N.Emitter();
    e.setRate(new N.Rate(new N.Span(count, count), new N.Span(0.02, 0.04)));
    e.setInitializers([
      new N.Position(new N.PointZone(0, 0, 0)),
      new N.Mass(1),
      new N.Radius(size[0], size[1]),
      new N.Life(life * 0.7, life * 1.3),
      new N.RadialVelocity(new N.Span(speed * 0.5, speed), new N.Vector3D(...up), spread),
      new N.BodySprite(THREE, null, { color, transparent: true, opacity: 0.95, depthWrite: false }),
    ]);
    e.setBehaviours([
      new N.Gravity(gravity),
      new N.Alpha(1, 0),
      new N.Scale(1.4, 0.15),
      new N.Color('#' + color.toString(16).padStart(6, '0'), '#331100'),
    ]);
    return e;
  }

  _ring({ color = 0xffffff, size = 1.2, life = 0.3 } = {}) {
    const N = this.N;
    const e = new N.Emitter();
    e.setRate(new N.Rate(new N.Span(1, 1), new N.Span(0.02, 0.03)));
    e.setInitializers([
      new N.Position(new N.PointZone(0, 0, 0)),
      new N.Life(life, life),
      new N.Body(new THREE.Mesh(
        new THREE.RingGeometry(size * 0.55, size, 40),
        new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.85,
          side: THREE.DoubleSide, depthWrite: false }))),
    ]);
    e.setBehaviours([
      new N.Scale(0.3, 2.0),
      new N.Alpha(0.9, 0),
    ]);
    return e;
  }

  /** Spawn a hit effect. kind: impact|heavy|ko|block|dust|surge.
      Signature-compatible with game.js _spawnImpact(x,y,z,color,scale). */
  spawn(x, y, z, color = 0xffcf4d, scale = 1, kind = null) {
    if (!this.ready || !this.enabled) return false;
    const k = kind || (scale >= 1.3 ? 'ko' : scale >= 0.9 ? 'heavy' : 'impact');
    const sys = this.system; // one shared system, one SpriteRenderer
    const fire = (emitter, ttl = 1400) => {
      emitter.setPosition({ x, y, z });
      sys.addEmitter(emitter);
      emitter.emit();
      setTimeout(() => emitter.stopEmit && emitter.stopEmit(), 90);
      setTimeout(() => { sys.removeEmitter(emitter); }, ttl);
    };
    if (k === 'ko') {
      fire(this._burst({ color, count: 60, speed: 420, size: [5, 11], life: 0.8 }));
      fire(this._burst({ color: 0xffffff, count: 24, speed: 260, size: [7, 14], life: 0.35 }));
      fire(this._ring({ color, size: 1.6 * scale, life: 0.45 }));
    } else if (k === 'heavy') {
      fire(this._burst({ color, count: 40, speed: 320, size: [4, 10], life: 0.55 }));
      fire(this._ring({ color, size: 1.0 * scale, life: 0.3 }));
    } else if (k === 'block') {
      fire(this._burst({ color: 0x9fd8ff, count: 22, speed: 190, size: [3, 7], life: 0.35, gravity: -120 }));
    } else if (k === 'dust') {
      fire(this._burst({ color: 0xbba88a, count: 16, speed: 110, size: [8, 16], life: 0.7, gravity: 40, up: [0, 1, 0] }));
    } else if (k === 'surge') {
      fire(this._burst({ color, count: 46, speed: 170, size: [5, 10], life: 0.9, gravity: 130, up: [0, 1, 0] }));
      fire(this._ring({ color, size: 1.3 * scale, life: 0.5 }));
    } else { // impact
      fire(this._burst({ color, count: 26, speed: 230, size: [4, 9], life: 0.45 }));
    }
    return true;
  }

  update(dt) {
    if (!this.ready) return;
    this.system.update(dt);
    for (const k in this._jsonPresets) this._jsonPresets[k].update(dt);
  }
}
