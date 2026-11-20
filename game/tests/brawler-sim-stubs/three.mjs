/* Headless three.js stub for the brawler sim test.
 * Minimal scene-graph math: positions, hierarchy, opacity. No rendering. */
class V3 {
  constructor(x = 0, y = 0, z = 0) { this.x = x; this.y = y; this.z = z; }
  set(x, y, z) { this.x = x; this.y = y; this.z = z; return this; }
  copy(v) { this.x = v.x; this.y = v.y; this.z = v.z; return this; }
  addScaledVector(v, s) { this.x += v.x * s; this.y += v.y * s; this.z += v.z * s; return this; }
}
function makeScale() {
  const s = { x: 1, y: 1, z: 1 };
  s.set = (x, y, z) => { s.x = x; s.y = y; s.z = (z === undefined ? s.z : z); };
  s.setScalar = (v) => { s.x = s.y = s.z = v; };
  s.multiplyScalar = (v) => { s.x *= v; s.y *= v; s.z *= v; };
  return s;
}
class Node {
  constructor() {
    this.position = new V3();
    this.rotation = { x: 0, y: 0, z: 0 };
    this.scale = makeScale();
    this.children = [];
    this.visible = true;
    this.material = null;
    this.userData = {};
  }
  add(...o) { this.children.push(...o); return this; }
  remove(...o) {
    for (const x of o) { const i = this.children.indexOf(x); if (i >= 0) this.children.splice(i, 1); }
    return this;
  }
  lookAt() {}
}
export class Group extends Node {}
export class Mesh extends Node { constructor(g, m) { super(); this.geometry = g; this.material = m; } }
export class Sprite extends Node { constructor(m) { super(); this.material = m; } }
export class PointLight extends Node { constructor() { super(); } }
export class PerspectiveCamera extends Node {}
export class Vector3 extends V3 {}
class Disposable { dispose() {} }
export class SphereGeometry extends Disposable {}
export class IcosahedronGeometry extends Disposable {}
export class MeshBasicMaterial extends Disposable {
  constructor(o) { super(); Object.assign(this, o || {}); this.opacity = 1; }
  clone() { return new MeshBasicMaterial(this); }
}
export class SpriteMaterial extends MeshBasicMaterial {}
export class CanvasTexture extends Disposable { constructor() { super(); } }
