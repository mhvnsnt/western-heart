/* ============================================================
   WESTERN HEART — WHLabels (troika SDF 3D text)
   Vendored: game/vendor/troika-three-text/* (MIT, protectwise/troika).
   Loaded lazily by game/js/integration.js; falls back gracefully.

   Uses: fighter nameplates above heads, floating damage numbers,
   arena signage, cutscene title cards. SDF text stays crisp at any
   distance and patches standard materials (lighting/fog keep working).
   ============================================================ */

import * as THREE from 'three';

let Troika = null;
async function loadTroika() {
  if (Troika) return Troika;
  Troika = await import('troika-three-text');
  return Troika;
}

export class WHLabels {
  constructor() {
    this.ready = false;
    this.scene = null;
    this._floaters = []; // {text, born, life}
  }

  async init(scene) {
    await loadTroika();
    this.scene = scene;
    this.ready = true;
    return this;
  }

  /** Crisp 3D text mesh. Returns the troika Text (a THREE.Mesh). */
  make(text, {
    fontSize = 0.22, color = 0xffffff, outlineColor = 0x000000,
    outlineWidth = 0.06, anchorX = 'center', anchorY = 'middle',
    font = null, maxWidth = 0,
  } = {}) {
    const T = Troika;
    const t = new T.Text();
    t.text = text;
    t.fontSize = fontSize;
    t.color = color;
    t.outlineWidth = outlineWidth;
    t.outlineColor = outlineColor;
    t.anchorX = anchorX;
    t.anchorY = anchorY;
    if (font) t.font = font;
    if (maxWidth) t.maxWidth = maxWidth;
    t.sync();
    return t;
  }

  /** Fighter nameplate that follows a fighter root (billboarded). */
  nameplate(fighterRoot, name, { height = 2.15, fontSize = 0.2, color = 0xffe9b0 } = {}) {
    if (!this.ready) return null;
    const label = this.make(name, { fontSize, color });
    label.position.set(0, height, 0);
    // Billboard: face the camera every frame (updated in update()).
    label.userData.billboard = true;
    fighterRoot.add(label);
    (this._plates ||= []).push({ label, root: fighterRoot });
    return label;
  }

  /** Floating damage number: rises, fades, auto-removes. */
  damageNumber(x, y, z, amount, { color = 0xffdf6b, fontSize = 0.3, life = 0.9 } = {}) {
    if (!this.ready || !this.scene) return null;
    const label = this.make(String(amount), { fontSize, color });
    label.position.set(x, y, z);
    label.userData.billboard = true;
    this.scene.add(label);
    this._floaters.push({ label, born: performance.now() / 1000, life, vy: 1.1 });
    return label;
  }

  /** Cutscene / round banner: big centered text that fades. */
  banner(text, { fontSize = 0.8, color = 0xffd76a, life = 2.2, y = 2.6 } = {}) {
    if (!this.ready || !this.scene) return null;
    const label = this.make(text, { fontSize, color, outlineWidth: 0.09 });
    label.position.set(0, y, 0);
    label.userData.billboard = true;
    this.scene.add(label);
    this._floaters.push({ label, born: performance.now() / 1000, life, vy: 0 });
    return label;
  }

  update(dt, camera) {
    if (!this.ready) return;
    const now = performance.now() / 1000;
    // Billboard everything flagged.
    const face = (o) => { if (camera) o.quaternion.copy(camera.quaternion); };
    if (this._plates) for (const p of this._plates) face(p.label);
    for (let i = this._floaters.length - 1; i >= 0; i--) {
      const f = this._floaters[i];
      const age = now - f.born;
      if (camera) f.label.quaternion.copy(camera.quaternion);
      f.label.position.y += f.vy * dt;
      const k = Math.max(0, 1 - age / f.life);
      f.label.material.opacity = k;
      f.label.material.transparent = true;
      if (age >= f.life) {
        this.scene.remove(f.label);
        f.label.dispose();
        this._floaters.splice(i, 1);
      }
    }
  }
}
