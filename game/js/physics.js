/* ============================================================
   WESTERN HEART — WHPhysics (cannon-es rigid-body layer)
   Vendored: game/vendor/cannon-es/cannon-es.js (MIT, pmndrs/cannon-es).
   Loaded lazily by game/js/integration.js; the game runs fine without it.

   SCOPE (owner feel target): extra physics — partial ragdoll à la
   Gang Beasts / Human Fall Flat / MK Royal Rumble, NOT fully ragdoll.
   cannon-es is VISUALS ONLY: arena props, impact debris, KO tumble.
   Combat simulation + netplay rollback must never read physics state.
   ============================================================ */

import * as THREE from 'three';

let CANNON = null;

export async function loadCannon() {
  if (CANNON) return CANNON;
  CANNON = await import('cannon-es');
  return CANNON;
}

export class WHPhysics {
  constructor() {
    this.ready = false;
    this.world = null;
    this.bodies = [];   // {body, mesh, life}
    this.props = [];    // arena prop bodies (persistent)
    this.scene = null;
    this._acc = 0;
  }

  async init(scene, opts = {}) {
    const C = await loadCannon();
    this.C = C;
    this.scene = scene;
    this.world = new C.World({ gravity: new C.Vec3(0, opts.gravity ?? -14, 0) });
    this.world.broadphase = new C.SAPBroadphase(this.world);
    this.world.allowSleep = true;
    // Static ground plane at y=0 (arena floor)
    const ground = new C.Body({ type: C.Body.STATIC, shape: new C.Plane() });
    ground.quaternion.setFromEuler(-Math.PI / 2, 0, 0);
    this.world.addBody(ground);
    this.ready = true;
    return this;
  }

  /** Register an arena prop as a knockable physical body. mesh: THREE.Mesh. */
  addProp(mesh, { mass = 2, shape = 'box', radius = 0.3 } = {}) {
    if (!this.ready) return null;
    const C = this.C;
    let cshape;
    if (shape === 'sphere') cshape = new C.Sphere(radius);
    else {
      mesh.geometry.computeBoundingBox();
      const s = new C.Vec3();
      mesh.geometry.boundingBox.getSize(s);
      cshape = new C.Box(new C.Vec3(s.x / 2, s.y / 2, s.z / 2));
    }
    const body = new C.Body({ mass, shape: cshape });
    body.position.copy(mesh.position);
    body.quaternion.copy(mesh.quaternion);
    body.angularDamping = 0.4;
    body.linearDamping = 0.05;
    this.world.addBody(body);
    const rec = { body, mesh, prop: true };
    this.props.push(rec);
    mesh.userData.whPhys = rec;
    return rec;
  }

  /** Load breakable props from a tools/procgen/arena-gen three.json arena.
      arenaJson.props: [{x, z, kind: crate|barrel|lantern, breakable}].
      Creates simple meshes, flags them userData.whProp, registers bodies.
      Returns the created meshes. */
  loadArenaProps(arenaJson, { y = 0.5 } = {}) {
    if (!this.ready || !this.scene) return [];
    const kinds = {
      crate:   { geo: () => new THREE.BoxGeometry(0.7, 0.7, 0.7),      color: 0x8a5a2b, mass: 3 },
      barrel:  { geo: () => new THREE.CylinderGeometry(0.32, 0.32, 0.9, 10), color: 0x5a3a22, mass: 4 },
      lantern: { geo: () => new THREE.SphereGeometry(0.28, 10, 8),      color: 0xff9a3c, mass: 1 },
    };
    const out = [];
    for (const pr of (arenaJson.props || [])) {
      const spec = kinds[pr.kind] || kinds.crate;
      const mesh = new THREE.Mesh(
        spec.geo(),
        new THREE.MeshStandardMaterial({ color: spec.color, roughness: 0.85 }));
      mesh.position.set(pr.x, y, pr.z);
      mesh.castShadow = true;
      mesh.userData.whProp = { mass: spec.mass, shape: pr.kind === 'lantern' ? 'sphere' : 'box', radius: 0.3 };
      this.scene.add(mesh);
      this.addProp(mesh, mesh.userData.whProp);
      out.push(mesh);
    }
    return out;
  }

  /** Shove the nearest prop bodies away from a point (hit knockback). */
  blast(point, { radius = 2.2, power = 6 } = {}) {
    if (!this.ready) return;
    const C = this.C;
    const p = new C.Vec3(point.x, point.y, point.z);
    for (const rec of this.props) {
      const d = rec.body.position.vsub(p);
      const dist = d.length();
      if (dist > radius || dist < 1e-4) continue;
      const f = (1 - dist / radius) * power;
      d.normalize();
      rec.body.wakeUp();
      rec.body.applyImpulse(new C.Vec3(d.x * f, d.y * f * 0.7 + f * 0.35, d.z * f));
      rec.body.angularVelocity.set(
        (Math.random() - 0.5) * f, (Math.random() - 0.5) * f, (Math.random() - 0.5) * f);
    }
  }

  /** Spawn short-lived physical debris chunks at a hit point. */
  debris(point, { count = 6, color = 0xffcf4d, size = 0.07, life = 1.1, power = 5 } = {}) {
    if (!this.ready || !this.scene) return;
    const C = this.C;
    for (let i = 0; i < count; i++) {
      const body = new C.Body({
        mass: 0.4,
        shape: new C.Sphere(size * (0.6 + Math.random() * 0.8)),
      });
      body.position.set(
        point.x + (Math.random() - 0.5) * 0.3,
        point.y + (Math.random() - 0.5) * 0.3,
        point.z + (Math.random() - 0.5) * 0.3);
      const th = Math.random() * Math.PI * 2, up = 0.4 + Math.random() * 0.9;
      body.velocity.set(Math.cos(th) * power * (0.4 + Math.random() * 0.6), up * power * 0.6, Math.sin(th) * power * (0.4 + Math.random() * 0.6));
      body.angularVelocity.set(Math.random() * 12 - 6, Math.random() * 12 - 6, Math.random() * 12 - 6);
      this.world.addBody(body);
      const mesh = new THREE.Mesh(
        new THREE.SphereGeometry(size, 6, 5),
        new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.95 }));
      mesh.position.copy(body.position);
      this.scene.add(mesh);
      this.bodies.push({ body, mesh, life });
    }
  }

  /** KO tumble: give the fighter's root a physical launch (visual only).
      The game's own KO animation stays authoritative; this adds the
      ragdoll-lite tumble on top via a proxy body the caller samples. */
  koTumble(fighterRoot, { power = 7, up = 4 } = {}) {
    if (!this.ready) return null;
    const C = this.C;
    const body = new C.Body({ mass: 80, shape: new C.Sphere(0.55) });
    body.position.copy(fighterRoot.position);
    const dir = fighterRoot.position.x >= 0 ? 1 : -1;
    body.velocity.set(dir * power * (0.7 + Math.random() * 0.6), up, (Math.random() - 0.5) * 2);
    body.angularVelocity.set((Math.random() - 0.5) * 6, 0, dir * (3 + Math.random() * 3));
    body.linearDamping = 0.12;
    this.world.addBody(body);
    const rec = { body, mesh: null, life: 2.2, koProxy: true, root: fighterRoot };
    this.bodies.push(rec);
    return rec;
  }

  step(dt) {
    if (!this.ready) return;
    // Fixed-ish step, clamped (visuals only — never drives combat).
    this._acc = Math.min(this._acc + dt, 0.1);
    const h = 1 / 60;
    while (this._acc >= h) { this.world.step(h); this._acc -= h; }
    const sync = (rec) => {
      if (rec.mesh && rec.body) {
        rec.mesh.position.copy(rec.body.position);
        rec.mesh.quaternion.copy(rec.body.quaternion);
        if (rec.mesh.material && rec.life < 0.5) {
          rec.mesh.material.opacity = Math.max(0, rec.life / 0.5) * 0.95;
        }
      }
    };
    for (const rec of this.props) sync(rec);
    for (let i = this.bodies.length - 1; i >= 0; i--) {
      const rec = this.bodies[i];
      rec.life -= dt;
      // KO proxy: ease the fighter root toward the proxy each frame.
      if (rec.koProxy && rec.root) {
        rec.root.position.lerp(rec.body.position, 0.35);
      }
      sync(rec);
      if (rec.life <= 0) {
        if (rec.mesh) { this.scene.remove(rec.mesh); rec.mesh.geometry.dispose(); rec.mesh.material.dispose(); }
        this.world.removeBody(rec.body);
        this.bodies.splice(i, 1);
      }
    }
  }
}
