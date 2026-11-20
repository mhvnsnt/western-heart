// WH hitbox/hurtbox module — zero-dependency, Three.js-agnostic math.
// Wiring target in repo: game/lib/hitbox.js (drop-in; game code feeds it
// world-space boxes each frame and reads hit events).
// Design rules (ported from the Godot hitbox lesson + Tekken frame data):
//  1. Boxes are only dangerous on their ACTIVE frames (startup/active/
//     recovery gating) — a box that is not active can never hit.
//  2. On activation, already-overlapping hurtboxes are scanned immediately:
//     area-entered style detection alone LOSES hits when a swing turns on
//     while already touching the opponent (the classic lost-melee-hit bug).
//  3. One hit per activation per target (alreadyHit set, cleared on deactivate).
// Buttons: LP1 = Left Punch, RP2 = Right Punch, LK3 = Left Kick, RK4 = Right Kick.

export class Box3 {
  constructor(cx, cy, cz, hx, hy, hz) {
    this.cx = cx; this.cy = cy; this.cz = cz;
    this.hx = hx; this.hy = hy; this.hz = hz;
  }
  overlaps(o) {
    return Math.abs(this.cx - o.cx) <= this.hx + o.hx &&
           Math.abs(this.cy - o.cy) <= this.hy + o.hy &&
           Math.abs(this.cz - o.cz) <= this.hz + o.hz;
  }
}

// A hurtbox: one body volume on a fighter. `team` stops self-hits.
export class Hurtbox {
  constructor(team, box, onHit) {
    this.team = team; this.box = box; this.onHit = onHit || (() => {});
  }
}

// A hitbox: an attack volume with frame data. Frames are counted in
// 60fps game frames, matching Tekken frame data conventions.
export class Hitbox {
  // startup: frames before active; active: dangerous frames; damage: int
  constructor({ team, box, startup = 0, active = 1, damage = 10, move = 'LP1' }) {
    this.team = team; this.box = box;
    this.startup = startup; this.active = active; this.damage = damage; this.move = move;
    this.frame = 0; this.isActive = false; this.alreadyHit = new Set();
  }
  start() { this.frame = 0; this.isActive = false; this.alreadyHit.clear(); }
  // Advance one frame; returns true on the exact frame it becomes active,
  // so the caller can run the already-overlapping rescan (rule 2).
  tick() {
    this.frame++;
    const wasActive = this.isActive;
    this.isActive = this.frame > this.startup && this.frame <= this.startup + this.active;
    if (this.isActive && !wasActive) return 'activated';
    if (!this.isActive && wasActive) { this.alreadyHit.clear(); return 'deactivated'; }
    return 'same';
  }
  // Test against hurtboxes. Call every frame while active AND once on
  // activation (with the same list) to catch already-overlapping targets.
  // Returns array of { target, damage, move } hits landed this call.
  test(hurtboxes) {
    const hits = [];
    if (!this.isActive) return hits;
    for (const hb of hurtboxes) {
      if (hb.team === this.team) continue;           // no self-hits
      if (this.alreadyHit.has(hb)) continue;         // one hit per swing
      if (!this.box.overlaps(hb.box)) continue;
      this.alreadyHit.add(hb);
      hb.onHit(this.damage, this.move);
      hits.push({ target: hb, damage: this.damage, move: this.move });
    }
    return hits;
  }
}

// Optional Three.js wireframe helper. THREE is passed in (never imported)
// so this file stays runnable in Node tests. In game: pass the game's THREE.
export function wireframeForBox(THREE, box, color) {
  const geo = new THREE.BoxGeometry(box.hx * 2, box.hy * 2, box.hz * 2);
  const mat = new THREE.LineBasicMaterial({ color });
  const mesh = new THREE.LineSegments(new THREE.EdgesGeometry(geo), mat);
  mesh.position.set(box.cx, box.cy, box.cz);
  return mesh;
}
