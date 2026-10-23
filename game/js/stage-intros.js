/* ============================================================
   WESTERN HEART — Stage Intro Camera Sweeps
   Teardown source: Tekken 7 / TTT2 stage intros — on stage load the
   camera performs a short cinematic sweep of the arena (rise, orbit,
   push-in) before settling behind the fighters. Faithful port:
     • per-stage keyframed paths (pos + lookAt + fov), eased in-out;
     • ~INTRO_LEN_S, skippable on any input, then control hands over;
     • paths themed to the land's element (fire stages sweep low past
       the flames; dreaming stages drift and ripple).
   WH canon mapping: the sweep is the land INTRODUCING itself — each of
   the Five Lands shows its nature before the Trial begins. Proposed
   presentation name: "LAND REVEAL" (minor flag).
   ============================================================ */

export const INTRO_LEN_S = 4.2;

/* Keyframe: { t (0..1), pos:[x,y,z], look:[x,y,z], fov }.
   Default sweep: high wide -> low orbit -> settle behind p1. */
function _defaultPath(stage) {
  const w = (stage.dims && stage.dims.width) || 16.8;
  return [
    { t: 0.00, pos: [0, 9.5, w * 0.85], look: [0, 1.5, 0], fov: 55 },
    { t: 0.35, pos: [-w * 0.45, 4.2, w * 0.45], look: [0, 1.2, 0], fov: 50 },
    { t: 0.70, pos: [w * 0.30, 2.2, w * 0.32], look: [0, 1.4, 0], fov: 46 },
    { t: 1.00, pos: [0, 2.6, 9.2], look: [0, 1.4, 0], fov: 45 },
  ];
}

/* Per-land authored paths (element-themed). Falls back to default. */
const LAND_PATHS = {
  'plains-of-chi-u': [ // FIRE — low sweep past the burning tower
    { t: 0.00, pos: [-7, 2.0, 12], look: [2, 3.5, -4], fov: 58 },
    { t: 0.40, pos: [5, 1.4, 9], look: [0, 2.0, -2], fov: 52 },
    { t: 0.75, pos: [-3, 2.4, 10], look: [0, 1.4, 0], fov: 47 },
    { t: 1.00, pos: [0, 2.6, 9.2], look: [0, 1.4, 0], fov: 45 },
  ],
  'palace-of-dreaming': [ // WATER — slow drift, walls ripple
    { t: 0.00, pos: [6, 5.5, 10], look: [-2, 1.0, 0], fov: 60 },
    { t: 0.50, pos: [-6, 4.0, 11], look: [2, 1.2, 0], fov: 55 },
    { t: 1.00, pos: [0, 2.6, 9.2], look: [0, 1.4, 0], fov: 45 },
  ],
  'helix-palace': [ // METAL — spiral descent matching the palace
    { t: 0.00, pos: [9, 10, 6], look: [0, 2, 0], fov: 58 },
    { t: 0.35, pos: [-8, 7, 8], look: [0, 1.6, 0], fov: 52 },
    { t: 0.70, pos: [6, 3.4, 9], look: [0, 1.4, 0], fov: 47 },
    { t: 1.00, pos: [0, 2.6, 9.2], look: [0, 1.4, 0], fov: 45 },
  ],
  'tree-of-life': [ // WOOD — rise through the branches
    { t: 0.00, pos: [0, 1.2, 13], look: [0, 6, -6], fov: 60 },
    { t: 0.45, pos: [-5, 4.5, 10], look: [0, 2.5, -2], fov: 52 },
    { t: 1.00, pos: [0, 2.6, 9.2], look: [0, 1.4, 0], fov: 45 },
  ],
  'shrine': [ // EARTH — still, reverent push-in
    { t: 0.00, pos: [0, 3.4, 14], look: [0, 1.6, 0], fov: 50 },
    { t: 0.60, pos: [0, 2.9, 11], look: [0, 1.5, 0], fov: 47 },
    { t: 1.00, pos: [0, 2.6, 9.2], look: [0, 1.4, 0], fov: 45 },
  ],
};

export function introPathFor(stage) {
  return LAND_PATHS[stage.id] || _defaultPath(stage);
}

/* Sample the path at t (0..1) with smoothstep easing between keys. Pure. */
export function sampleIntroPath(path, t) {
  t = Math.max(0, Math.min(1, t));
  let a = path[0], b = path[path.length - 1];
  for (let i = 0; i < path.length - 1; i++) {
    if (t >= path[i].t && t <= path[i + 1].t) { a = path[i]; b = path[i + 1]; break; }
  }
  const span = Math.max(1e-6, b.t - a.t);
  let u = (t - a.t) / span;
  u = u * u * (3 - 2 * u); // smoothstep
  const lerp = (x, y) => x + (y - x) * u;
  return {
    pos: [lerp(a.pos[0], b.pos[0]), lerp(a.pos[1], b.pos[1]), lerp(a.pos[2], b.pos[2])],
    look: [lerp(a.look[0], b.look[0]), lerp(a.look[1], b.look[1]), lerp(a.look[2], b.look[2])],
    fov: lerp(a.fov, b.fov),
  };
}

/* Player: advances the sweep, applies to a THREE camera. Skippable. */
export class StageIntro {
  constructor(stage, camera) {
    this.path = introPathFor(stage);
    this.camera = camera;
    this.t = 0;
    this.len = INTRO_LEN_S;
    this.done = false;
    this.skipped = false;
  }
  skip() { this.skipped = true; this.done = true; }
  update(dt) {
    if (this.done) return true;
    this.t += dt / this.len;
    const s = sampleIntroPath(this.path, Math.min(1, this.t));
    const cam = this.camera;
    if (cam && cam.position) {
      cam.position.set(s.pos[0], s.pos[1], s.pos[2]);
      cam.lookAt(s.look[0], s.look[1], s.look[2]);
      if ('fov' in cam) { cam.fov = s.fov; cam.updateProjectionMatrix(); }
    }
    if (this.t >= 1) this.done = true;
    return this.done;
  }
}
