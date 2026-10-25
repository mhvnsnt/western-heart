/* ============================================================
   WESTERN HEART — WHNavMesh (Track 7, 2026-10-23)
   NavMesh pathfinding for Heart and Mind Within open zones:
   dozens of AI grunts pursuing / flanking / swarming the player
   across multi-level structures (arena floor + platforms).

   Open-source core: Yuka.js (Mugen87/yuka, MIT) — vendored
   unmodified at game/vendor/yuka/yuka.module.js. This module is
   the Western Heart adaptation layer over YUKA.NavMesh,
   YUKA.Corridor, YUKA.Vehicle + steering behaviors.

   LANE SPLIT (coordination, issue #866): another track owns Yuka's
   COMBAT state machines (State / StateMachine / GoalEvaluator).
   THIS track owns NAVMESH/pathfinding only. Both share the same
   vendored yuka.module.js — no duplicate pulls.

   Verified API notes (Yuka 0.7.8, tested in node 2026-10-23):
     • contours: new Y.Polygon().fromContour(Vector3[]) — winding
       must be positive-area CCW in the xz-plane, e.g.
       (x1,z1)->(x1,z2)->(x2,z2)->(x2,z1).
     • navMesh.fromPolygons(polys) merges coplanar+convex regions.
     • findPath(from, to) -> Vector3[] waypoints (corridor-smoothed).
     • clampMovement(region, start, end, out) -> new region; when the
       end point is already on the mesh, `out` is untouched and the
       caller keeps `end` (handled inside clampStep()).
     • getRegionForPoint(point) -> region | null.

   Node-testable: Yuka is engine-independent; no three.js import.
   ============================================================ */

let _Y = null;
async function _yuka() {
  if (_Y) return _Y;
  _Y = await import('../../vendor/yuka/yuka.module.js');
  return _Y;
}
const V3 = (Y, x, y, z) => new Y.Vector3(x, y || 0, z || 0);

/* ---------------- WHNavMesh: one walkable level ---------------- */
export class WHNavMesh {
  constructor() {
    this.Y = null;
    this.navMesh = null;
    this.ready = false;
  }
  async init() {
    this.Y = await _yuka();
    this.navMesh = new this.Y.NavMesh();
    this.ready = true;
    return this;
  }
  _need() { if (!this.ready) throw new Error('WHNavMesh: call init() first'); }

  /* rects: [{ x1, z1, x2, z2, y=0 }] — floor quads, any order. */
  buildFromRects(rects) {
    this._need();
    const Y = this.Y;
    const polys = rects.map((r) => {
      const y = r.y || 0;
      const pts = [
        V3(Y, r.x1, y, r.z1), V3(Y, r.x1, y, r.z2),
        V3(Y, r.x2, y, r.z2), V3(Y, r.x2, y, r.z1),
      ];
      return new Y.Polygon().fromContour(pts);
    });
    this.navMesh.fromPolygons(polys);
    return this;
  }
  /* Raw triangles: positions Float32Array-ish [x,y,z,...], index [i..]. */
  buildFromTriangles(positions, index) {
    this._need();
    const Y = this.Y;
    const polys = [];
    for (let i = 0; i + 2 < index.length; i += 3) {
      const pts = [index[i], index[i + 1], index[i + 2]].map((vi) =>
        V3(Y, positions[vi * 3], positions[vi * 3 + 1], positions[vi * 3 + 2]));
      polys.push(new Y.Polygon().fromContour(pts));
    }
    this.navMesh.fromPolygons(polys);
    return this;
  }
  regionCount() { this._need(); return this.navMesh.regions.length; }

  /* -> [{x,y,z}] waypoints, corridor-smoothed. null when unreachable. */
  findPath(from, to) {
    this._need();
    const Y = this.Y;
    const pts = this.navMesh.findPath(V3(Y, from.x, from.y, from.z), V3(Y, to.x, to.y, to.z));
    if (!pts || !pts.length) return null;
    return pts.map((p) => ({ x: p.x, y: p.y, z: p.z }));
  }
  /* Clamp one simulation step to the mesh (slides along borders).
     region: cached region object (or null). Returns { pos, region }. */
  clampStep(region, from, to) {
    this._need();
    const Y = this.Y;
    const s = V3(Y, from.x, from.y, from.z), e = V3(Y, to.x, to.y, to.z);
    const endRegion = this.navMesh.getRegionForPoint(e);
    if (endRegion) return { pos: { x: to.x, y: to.y, z: to.z }, region: endRegion };
    const out = V3(Y, 0, 0, 0);
    const newRegion = this.navMesh.clampMovement(region, s, e, out);
    return { pos: { x: out.x, y: out.y, z: out.z }, region: newRegion || region };
  }
  regionFor(p) {
    this._need();
    return this.navMesh.getRegionForPoint(V3(this.Y, p.x, p.y, p.z));
  }
  contains(p) { return !!this.regionFor(p); }
}

/* ---------------- WHNavZoneSet: multi-level structures --------- */
/* zones: { levelId: WHNavMesh }. Off-mesh links (stairs, doors,
   ledges) stitch levels: { id, from:{zone,pos}, to:{zone,pos} }.
   Path across zones: path within zone A to link, teleport/climb
   through the link, path within zone B. Link traversal animation
   (climb/vault) is the combat track's lane — here we expose the
   route as segments. */
export class WHNavZoneSet {
  constructor() { this.zones = new Map(); this.links = []; }
  addZone(id, navMesh) { this.zones.set(id, navMesh); return this; }
  addLink(link) { this.links.push({ id: link.id || ('link' + this.links.length), ...link }); return this; }
  /* -> [{ zone, waypoints:[{x,y,z}], via }] segments, or null. */
  route(fromZone, from, toZone, to) {
    const A = this.zones.get(fromZone), B = this.zones.get(toZone);
    if (!A || !B) return null;
    if (fromZone === toZone) {
      const wp = A.findPath(from, to);
      return wp ? [{ zone: fromZone, waypoints: wp, via: null }] : null;
    }
    // Cheapest single link bridging the zones (Euclidean heuristic).
    let best = null, bestCost = Infinity;
    for (const l of this.links) {
      if (l.from.zone !== fromZone || l.to.zone !== toZone) continue;
      const d = Math.hypot(l.from.pos.x - from.x, l.from.pos.z - from.z)
              + Math.hypot(l.to.pos.x - to.x, l.to.pos.z - to.z);
      if (d < bestCost) { bestCost = d; best = l; }
    }
    if (!best) return null;
    const w1 = A.findPath(from, best.from.pos), w2 = B.findPath(best.to.pos, to);
    if (!w1 || !w2) return null;
    return [
      { zone: fromZone, waypoints: w1, via: best.id },
      { zone: toZone, waypoints: w2, via: null },
    ];
  }
}

/* ---------------- WHGrunt: pathfinding combat mook -------------- */
/* A Yuka Vehicle wired to a navmesh: seeks a goal along nav waypoints
   with Separation so dozens of grunts don't stack. The COMBAT brain
   (attack decisions, state machine) belongs to the other Yuka track —
   this class only moves the body: pursue / flank / swarm. */
export class WHGrunt {
  constructor(navMesh, opts = {}) {
    this.nav = navMesh;
    this.opts = { maxSpeed: 3.2, arriveRadius: 0.6, repathEvery: 0.5, ...opts };
    this.vehicle = null;
    this.goal = null;          // {x,y,z}
    this.flankAngle = 0;       // ring slot around the focus
    this.flankRadius = 2.2;
    this._waypoints = [];
    this._wpIndex = 0;
    this._repathT = 0;
    this._region = null;
    this.pos = { x: 0, y: 0, z: 0 };
  }
  async init(Y) {
    const yuka = Y || this.nav.Y;
    this.vehicle = new yuka.Vehicle();
    this.vehicle.maxSpeed = this.opts.maxSpeed;
    this.vehicle.position.set(this.pos.x, this.pos.y, this.pos.z);
    this.vehicle.neighbors = []; // SeparationBehavior reads vehicle.neighbors
    this._seek = new yuka.SeekBehavior(new yuka.Vector3());
    this._sep = new yuka.SeparationBehavior();
    this.vehicle.steering.add(this._seek);
    this.vehicle.steering.add(this._sep);
    return this;
  }
  spawn(x, y, z) {
    this.pos = { x, y, z: z };
    this.pos.y = y;
    if (this.vehicle) this.vehicle.position.set(x, y, z);
    this._region = this.nav.regionFor(this.pos);
    return this;
  }
  /* behavior: 'pursue' (straight at focus) | 'flank' (ring slot) |
     'swarm' (pursue + tighter separation handled by squad) */
  setGoal(focus, behavior = 'pursue') {
    let gx = focus.x, gz = focus.z;
    if (behavior === 'flank') {
      gx = focus.x + Math.cos(this.flankAngle) * this.flankRadius;
      gz = focus.z + Math.sin(this.flankAngle) * this.flankRadius;
    }
    this.goal = { x: gx, y: focus.y || 0, z: gz };
    this._repathT = 0; // repath immediately
    return this;
  }
  update(dt, neighbors = []) {
    if (!this.vehicle || !this.goal) return this.pos;
    this._repathT -= dt;
    if (this._repathT <= 0) {
      this._repathT = this.opts.repathEvery;
      const wp = this.nav.findPath(this.pos, this.goal);
      this._waypoints = wp || [{ ...this.goal }];
      this._wpIndex = 0;
    }
    // Advance to the furthest visible waypoint (simple string-pulling).
    while (this._wpIndex < this._waypoints.length - 1) {
      const n = this._waypoints[this._wpIndex];
      if (Math.hypot(n.x - this.pos.x, n.z - this.pos.z) < this.opts.arriveRadius) this._wpIndex++;
      else break;
    }
    const target = this._waypoints[this._wpIndex] || this.goal;
    this._seek.target.set(target.x, target.y || 0, target.z);
    // Separation from nearby grunts (dozens-deep crowds stay readable).
    const nb = this.vehicle.neighbors;
    nb.length = 0;
    for (const o of neighbors) {
      if (o === this || !o.vehicle) continue;
      const d = Math.hypot(o.pos.x - this.pos.x, o.pos.z - this.pos.z);
      if (d < 2.5) nb.push(o.vehicle);
    }
    this.vehicle.update(dt);
    // Stay on the mesh: clamp the integrated step.
    const p = this.vehicle.position;
    const step = this.nav.clampStep(this._region, this.pos, { x: p.x, y: p.y, z: p.z });
    this._region = step.region;
    this.pos = { x: step.pos.x, y: step.pos.y, z: step.pos.z };
    p.set(this.pos.x, this.pos.y, this.pos.z);
    return this.pos;
  }
}

/* ---------------- WHSquad: dozens of grunts, one update --------- */
export class WHSquad {
  constructor(navMesh, opts = {}) {
    this.nav = navMesh;
    this.opts = { count: 12, ...opts };
    this.grunts = [];
    this.focus = { x: 0, y: 0, z: 0 };
    this.behavior = 'pursue';
  }
  async init(Y) {
    for (let i = 0; i < this.opts.count; i++) {
      const g = new WHGrunt(this.nav, this.opts.grunt);
      await g.init(Y || this.nav.Y);
      g.flankAngle = (i / this.opts.count) * Math.PI * 2;
      this.grunts.push(g);
    }
    return this;
  }
  spawnRing(cx, cy, cz, radius) {
    this.grunts.forEach((g, i) => {
      const a = (i / this.grunts.length) * Math.PI * 2;
      g.spawn(cx + Math.cos(a) * radius, cy, cz + Math.sin(a) * radius);
    });
    return this;
  }
  setFocus(focus, behavior) {
    this.focus = focus;
    if (behavior) this.behavior = behavior;
    for (const g of this.grunts) g.setGoal(focus, this.behavior);
    return this;
  }
  update(dt) {
    for (const g of this.grunts) g.update(dt, this.grunts);
    return this.grunts.map((g) => g.pos);
  }
  get Y() { return this.nav.Y; }
}
