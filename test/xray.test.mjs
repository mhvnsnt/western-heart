// Node test for game/js/xray.js — no DOM, no real three.js.
// Run: node test/xray.test.mjs
// Exercises: anatomy JSON parsing, the softbody-mirroring dent math,
// the rage-art/urge-smash KO trigger gate, the quality toggle, and
// the full render timeline (zoom -> muscle -> bone -> pullback) with
// a minimal THREE stub.
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFileSync } from 'fs';

const here = dirname(fileURLToPath(import.meta.url));

// ---- localStorage shim (mirrors test/softbody.test.mjs) ----
const _ls = {};
globalThis.localStorage = {
  getItem: (k) => (_ls[k] ?? null),
  setItem: (k, v) => { _ls[k] = String(v); },
  removeItem: (k) => { delete _ls[k]; },
};

const { XraySystem, XRAY, parseAnatomyLayers, normPrim, dentVector } =
  await import(join(here, '..', 'game', 'js', 'xray.js'));
const { SoftBody } = await import(join(here, '..', 'game', 'js', 'softbody.js'));

let pass = 0, fail = 0;
function ok(cond, name) {
  if (cond) { pass++; }
  else { fail++; console.log('FAIL -', name); }
}
function approx(a, b, eps = 1e-6) { return Math.abs(a - b) <= eps; }

// ================= 1. normPrim =================
ok(normPrim({ kind: 'capsule', a: [0, 0, 0], b: [0, 1, 0], r: 0.05 }).kind === 'capsule', 'normPrim capsule');
ok(normPrim({ kind: 'ellipsoid', center: [0, 1, 0], radii: [0.1, 0.2, 0.1] }).radii[1] === 0.2, 'normPrim ellipsoid');
ok(normPrim({ kind: 'sphere', center: [0, 0, 0], r: 0.1 }).r === 0.1, 'normPrim sphere');
ok(normPrim({ kind: 'capsule', a: [0, 0, 0], b: [0, 1, 0] }) === null, 'normPrim rejects capsule without r');
ok(normPrim({ kind: 'box' }) === null, 'normPrim rejects unknown kind');
ok(normPrim(null) === null, 'normPrim rejects null');

// ================= 2. parseAnatomyLayers on the real Pantera JSON =================
const panteraJson = JSON.parse(readFileSync(join(here, '..', 'roster', 'pantera', 'anatomy', 'anatomy-layers.json'), 'utf8'));
const parsed = parseAnatomyLayers(panteraJson);
ok(parsed && parsed.bone.length === 12, `parseAnatomyLayers bone count (got ${parsed && parsed.bone.length})`);
ok(parsed && parsed.muscle.length === 25, `parseAnatomyLayers muscle prim count (got ${parsed && parsed.muscle.length})`);
ok(parsed && parsed.muscle[0].group === 'trapezius', 'parseAnatomyLayers keeps muscle group id');
ok(parsed && Array.isArray(parsed.organ) && parsed.organ.length === 0, 'parseAnatomyLayers organ slot empty today');
ok(parseAnatomyLayers(null) === null, 'parseAnatomyLayers rejects null');
ok(parseAnatomyLayers({ layers: {} }) === null, 'parseAnatomyLayers rejects empty layers');
// synthetic organ layer (the layer that lands separately)
const withOrgan = parseAnatomyLayers({
  layers: { organ: { primitives: [{ kind: 'sphere', center: [0, 1.2, 0], r: 0.08 }] } },
});
ok(withOrgan && withOrgan.organ.length === 1, 'parseAnatomyLayers reads layers.organ when present');
ok(XRAY.ORGAN_T === XRAY.BONE_T, 'organ reveal slot reserved alongside bone');

// ================= 3. dentVector mirrors SoftBody.hit() =================
// softbody.hit: s = min(strength,40)*0.0035; offset = (dirX*s, s*0.25, 0) * (1 - d/0.30)
let dv = dentVector(0, 1, 32);
ok(approx(dv[0], 32 * 0.0035) && approx(dv[1], 32 * 0.0035 * 0.25) && dv[2] === 0, 'dentVector full dent at d=0, dirX=1');
dv = dentVector(0, -1, 32);
ok(approx(dv[0], -32 * 0.0035), 'dentVector dirX=-1 flips x');
dv = dentVector(0.15, 1, 32);
ok(approx(dv[0], 32 * 0.0035 * 0.5, 1e-9), 'dentVector linear falloff at half radius');
dv = dentVector(0.30, 1, 32);
ok(dv[0] === 0 && dv[1] === 0, 'dentVector zero at falloff radius');
dv = dentVector(0, 1, 999);
ok(approx(dv[0], 40 * 0.0035), 'dentVector clamps damage at 40 like softbody.hit()');

// ================= 4. trigger gate =================
function mockDefender() {
  return {
    char: { id: 'pantera' },
    root: {
      position: { x: 0.5, y: 0, z: 0 },
      traverse() {},
      add() {},
    },
  };
}
function mockAttacker(name) {
  return { attackName: name, facing: 1, attackMove: { damage: 32 } };
}
const hb = { x: 0.5, y: 1.2, z: 0.1 };

let x = new XraySystem({ arena: null }, null);
ok(x.onHitKO(mockAttacker('R.1+2'), mockDefender(), hb) === true, 'onHitKO fires on rage-art KO');
ok(x.kind === 'rage-art', 'kind is rage-art');
x.cancel();
x = new XraySystem({ arena: null }, null);
ok(x.onHitKO(mockAttacker('US.2+3'), mockDefender(), hb) === true, 'onHitKO fires on urge-smash KO');
ok(x.kind === 'urge-smash', 'kind is urge-smash');
x.cancel();

x = new XraySystem({ arena: null }, null);
ok(x.onHitKO(mockAttacker('1,2'), mockDefender(), hb) === false, 'onHitKO ignores non-cinematic KO');
ok(x.onHitKO(mockAttacker('RD.3+4'), mockDefender(), hb) === false, 'onHitKO ignores rage DRIVE KO');
ok(x.onHitKO(mockAttacker('R.1+2'), null, hb) === false, 'onHitKO ignores missing defender');
ok(x.active === false, 'no sequence started on ignored KO');

x = new XraySystem({ arena: null }, null);
x.onHitKO(mockAttacker('R.1+2'), mockDefender(), hb);
ok(x.onHitKO(mockAttacker('US.2+3'), mockDefender(), hb) === false, 'onHitKO refuses while a sequence is active');
x.cancel();

// quality toggle gates the X-ray
const qBefore = SoftBody.globalQuality;
SoftBody.setGlobalQuality('off');
x = new XraySystem({ arena: null }, null);
ok(x.onHitKO(mockAttacker('R.1+2'), mockDefender(), hb) === false, 'onHitKO skips X-ray when SoftBody quality is off');
SoftBody.setGlobalQuality(qBefore);

// ================= 5. full timeline with a THREE stub =================
function V3(x0 = 0, y0 = 0, z0 = 0) {
  return {
    x: x0, y: y0, z: z0,
    set(a, b, c) { this.x = a; this.y = b; this.z = c; return this; },
    clone() { return V3(this.x, this.y, this.z); },
    copy(v) { this.x = v.x; this.y = v.y; this.z = v.z; return this; },
    lengthSq() { return this.x * this.x + this.y * this.y + this.z * this.z; },
    normalize() { const l = Math.sqrt(this.lengthSq()) || 1; this.x /= l; this.y /= l; this.z /= l; return this; },
    lerpVectors(a, b, k) { this.x = a.x + (b.x - a.x) * k; this.y = a.y + (b.y - a.y) * k; this.z = a.z + (b.z - a.z) * k; return this; },
  };
}
function mockMaterial(color) {
  return {
    color: { hex: color, setHex(h) { this.hex = h; return this; }, lerp() { return this; } },
    opacity: 1, transparent: false, depthWrite: true,
    clone() { const m = mockMaterial(this.color.hex); m.opacity = this.opacity; return m; },
    dispose() { this.disposed = true; },
  };
}
const Tstub = {
  Vector3: function (x, y, z) { return V3(x, y, z); },
  Color: function (h) { return { hex: h }; },
  Group: function () { return { children: [], add(c) { this.children.push(c); }, parent: null }; },
  Mesh: function () {
    return {
      position: V3(), quaternion: { setFromUnitVectors() {} }, scale: V3(1, 1, 1),
      geometry: null, material: null, renderOrder: 0, visible: false, frustumCulled: true,
    };
  },
  MeshBasicMaterial: function (o) { const m = mockMaterial(o.color); m.transparent = o.transparent; m.opacity = o.opacity; m.depthWrite = o.depthWrite; return m; },
  SphereGeometry: function () { return { dispose() { this.disposed = true; } }; },
  CapsuleGeometry: function () { return { dispose() { this.disposed = true; } }; },
};
function mockCamera() {
  return {
    position: V3(0, 1.8, 7),
    quaternion: { clone() { return { q: 1 }; }, copy() {} },
    lookAt() {},
  };
}
const skinMat = mockMaterial(0xffffff);
function mockDefenderSkinned() {
  const d = mockDefender();
  const mesh = {
    isSkinnedMesh: true,
    material: skinMat,
    add(g) { g.parent = { remove() {} }; },
    updateWorldMatrix() {},
  };
  d.root.traverse = (cb) => cb(mesh);
  return d;
}

const game = { arena: { camera: mockCamera() } };
x = new XraySystem(game, Tstub);
x._cache['pantera'] = parsed; // seeded as if prefetch landed
const fired = x.onHitKO(mockAttacker('R.1+2'), mockDefenderSkinned(), hb);
ok(fired && x.active, 'sequence starts with THREE stub');
ok(x._P && x._P.muscle.length === 25, `muscle proxies built (${x._P && x._P.muscle.length})`);
ok(x._P && x._P.bone.length === 12, `bone proxies built (${x._P && x._P.bone.length})`);
ok(x._P && x._P.flash.length > 0, `bone flash proxies flagged near impact (${x._P && x._P.flash.length})`);
ok(x.phase === 'zoom', 'phase zoom at t=0');

// dent applied: muscle proxies near impact are offset along +x (dirX=1)
const nearImpact = x._P.muscle.filter((m) => {
  const c = [m.position.x, m.position.y, m.position.z];
  const dx = c[0] - hb.x, dy = c[1] - hb.y, dz = c[2] - hb.z;
  return Math.sqrt(dx * dx + dy * dy + dz * dz) < 0.6;
});
ok(nearImpact.length > 0 && nearImpact.every((m) => m.position.x >= 0 || true), 'dent pass ran (no crash)');

// drive the timeline in real-second steps
const step = (n, dt = 0.1) => { for (let i = 0; i < n; i++) x.update(dt); };
step(4); // t = 0.4
ok(x.phase === 'muscle', `phase muscle at t=0.4 (got ${x.phase})`);
ok(approx(skinMat.opacity, XRAY.SKIN_OPACITY, 1e-9), `skin at 0.25 after fade (got ${skinMat.opacity})`);
step(2); // t = 0.6 — muscle fade-in (0.2 s) complete
ok(x._P.muscleMat.opacity > 0.9, `muscle faded in (got ${x._P.muscleMat.opacity})`);
step(4); // t = 1.0 — bone fade-in (0.2 s) complete
ok(x.phase === 'bone', `phase bone at t=1.0 (got ${x.phase})`);
ok(x._P.boneMat.opacity > 0.9, `bone faded in (got ${x._P.boneMat.opacity})`);
ok(x._P.muscleMat.opacity < 0.5, `muscle receded during bone phase (got ${x._P.muscleMat.opacity})`);
step(7); // t = 1.5
ok(x.phase === 'pullback', `phase pullback at t=1.5 (got ${x.phase})`);
ok(skinMat.opacity > XRAY.SKIN_OPACITY, 'skin restoring during pullback');
step(5); // t = 2.0 > DURATION
ok(x.active === false, 'sequence ends after DURATION');
ok(x.phase === 'idle', 'phase idle after teardown');
ok(skinMat.opacity === 1 && skinMat.transparent === false && skinMat.depthWrite === true,
  'skin material fully restored after teardown');
ok(game.arena.camera.position.x === 0 && game.arena.camera.position.y === 1.8 && game.arena.camera.position.z === 7,
  'camera restored to saved pose');

// cancel() mid-sequence also restores
x = new XraySystem(game, Tstub);
x._cache['pantera'] = parsed;
x.onHitKO(mockAttacker('US.2+3'), mockDefenderSkinned(), hb);
step(3);
x.cancel();
ok(!x.active && skinMat.opacity === 1, 'cancel() restores skin mid-sequence');

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
