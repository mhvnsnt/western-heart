// Lag in hits and inputs (owner 2026-11-11: "it's mostly in hits and inputs it's getting slow"). Regression checks for
// the fixes measured with tools/perf/sim_spike_probe.mjs and tools/perf/break_compile_probe.mjs:
//   A. move clips are bound ahead of their first press (Fighter.prewarmAttackClips + movesets.pressableNotations):
//      common neutral presses first, a capped list, the fighter's state untouched;
//   B. the BVH hit-verify instrument (hitdetect.js) is opt-in: a normal fight never bakes a skinned body on a hit;
//   C. a stage break builds nothing at the hit: its lights exist from stage build (the scene's light count never
//      changes, so no shader recompiles), its materials are built with the stage, burst particles are pooled.
// Run: node test/lag-hits-inputs.test.mjs  (plain node, no DOM, no network)
import assert from 'assert';
import { readFileSync, existsSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
let fails = 0;
const check = async (name, fn) => { try { await fn(); console.log('ok', name); } catch (e) { fails++; console.log('FAIL', name, '-', e.message); } };

// ---------- A. move-clip prewarm ----------
const M = await import(join(ROOT, 'game/js/movesets.js'));
const pantera = join(ROOT, 'game/assets/movesets/pantera.json');
if (existsSync(pantera)) {
  M.registerMoveset('pantera', JSON.parse(readFileSync(pantera, 'utf8')));
  await check('pressableNotations: neutral presses first, shortest first; stance-prefixed rows after them', () => {
    const ns = M.pressableNotations('pantera');
    assert.ok(ns.length > 200, 'pantera has hundreds of notations: ' + ns.length);
    assert.deepEqual(ns.slice(0, 4), ['1', '2', '3', '4']);
    const stance = (n) => /^[A-Za-z_][A-Za-z0-9_]*[. ]/.test(n) && !/^[udfbn](\/[fb])?[+,]/.test(n);
    const firstStance = ns.findIndex(stance);
    assert.ok(firstStance > 0, 'stance rows exist');
    assert.ok(ns.slice(firstStance).every(stance), 'every stance-prefixed row comes after every neutral one');
    for (let i = 1; i < firstStance; i++) assert.ok(ns[i].length >= ns[i - 1].length, `neutral rows shortest first: ${ns[i - 1]} then ${ns[i]}`);
    for (const n of ['d/f+1', 'f+2', 'b+1', '1,2']) assert.ok(ns.indexOf(n) >= 0 && ns.indexOf(n) < 120, n + ' is in the warmed head');
  });
} else console.log('NOTE pantera moveset absent from this checkout: ordering check skipped');

const F = await import(join(ROOT, 'game/js/fighter.js'));
await check('prewarmAttackClips: waits for the bind, warms in budgeted slices, caps the list, restores the attack state', () => {
  assert.ok(F.PREWARM_NOTATIONS >= 60 && F.PREWARM_NOTATIONS <= 200, 'cap ' + F.PREWARM_NOTATIONS);
  M.registerMoveset('warmtest', { moves: Object.fromEntries(Array.from({ length: 300 }, (_, i) => [`${['1', '2', '3', '4'][i % 4]}${',1'.repeat(Math.floor(i / 4))}`, { damage: 5, startup: 0.2, active: 0.05, recovery: 0.3 }])) });
  const f = Object.create(F.Fighter.prototype);
  Object.assign(f, { _movesetId: 'warmtest', _t3: null, mixer: null, _atkPlan: { id: 7, name: 'keep' }, _attackId: 7, state: 'idle' });
  assert.equal(f.prewarmAttackClips(5), false, 'not bound yet: try again later');
  f._t3 = { model: {} }; f.mixer = {};
  const seen = [];
  f._attackClip = function (move, n) { seen.push(n); this._atkPlan = { id: this._attackId, name: 'warm:' + n }; return null; };
  let done = false, calls = 0;
  while (!done && calls < 10000) { done = f.prewarmAttackClips(0); calls++; }   // budget 0: one notation per call
  assert.equal(done, true);
  assert.equal(seen.length, Math.min(F.PREWARM_NOTATIONS, M.pressableNotations('warmtest').length), 'warms the capped list exactly once each');
  assert.equal(new Set(seen).size, seen.length);
  assert.deepEqual(f._atkPlan, { id: 7, name: 'keep' }, 'attack plan restored');
  assert.equal(f._attackId, 7, 'attack id restored');
  assert.equal(f.state, 'idle');
  assert.equal(f.prewarmLeft, 0);
  assert.equal(f.prewarmAttackClips(5), true, 'done stays done');
});
const gameSrc = readFileSync(join(ROOT, 'game/js/game.js'), 'utf8');
await check('game loop warms after each drawn frame outside the fight, only in idle time during it, never while paused', async () => {
  assert.ok(/this\.arena\.render\(\);\s*\n\s*this\._prewarmTick\(\);/.test(gameSrc), '_loop calls _prewarmTick after render');
  const G = await import(join(ROOT, 'game/js/game.js')).catch(() => null);
  if (!G) { console.log('   (game.js not importable here: source checks only)'); return; }
  const slices = []; let idle = null;
  globalThis.requestIdleCallback = (cb) => { idle = cb; return 1; };
  const fighter = () => ({ _warmDone: false, prewarmAttackClips(b) { slices.push(b); return slices.length >= 3; } });
  const g = Object.assign(Object.create(G.Game.prototype), { running: true, paused: false, roundState: 'intro', p1: fighter(), p2: null });
  g._prewarmTick();
  assert.deepEqual(slices, [6], 'intro: a 6 ms slice right after the frame');
  g.roundState = 'fight';
  g._prewarmTick();
  assert.deepEqual(slices, [6], 'fight: nothing on the frame itself');
  assert.ok(idle, 'fight: an idle callback is queued');
  idle({ timeRemaining: () => 3 });
  assert.deepEqual(slices, [6], 'too little idle time: nothing');
  g._prewarmTick(); idle({ timeRemaining: () => 30 });
  assert.deepEqual(slices, [6, 2, 2], 'idle time: 2 ms slices until done');
  assert.equal(g.p1._warmDone, true);
  g.paused = true; slices.length = 0; g.p1._warmDone = false; g.roundState = 'intro';
  g._prewarmTick();
  assert.deepEqual(slices, [], 'paused: nothing');
  delete globalThis.requestIdleCallback;
});

// ---------- B. BVH hit verify is opt-in ----------
const H = await import(join(ROOT, 'game/js/hitdetect.js'));
await check('hit verify is off by default and does no work on a hit', async () => {
  assert.equal(H.HIT_VERIFY_DEFAULT, 'off');
  const h = new H.WHHitDetect();
  assert.equal(h.mode, 'off');
  h.ready = true;
  let built = 0;
  h.buildFighterBVH = async () => { built++; return null; };
  h.testLimbVsBody = async () => { built++; return { hit: false }; };
  assert.equal(await h.verify({}, {}, true, null, {}), true, 'sphere result kept');
  assert.equal(built, 0, 'no BVH bake on a hit');
  assert.equal(h.stats.sphereHits, 0);
});
await check('integration.js calls verify only when the instrument is switched on', () => {
  const src = readFileSync(join(ROOT, 'game/js/integration.js'), 'utf8');
  assert.ok(/if \(S\.hitdetect && S\.hitdetect\.mode !== 'off'\)/.test(src));
});

// ---------- C. stage breaks build nothing at the hit ----------
globalThis.document = globalThis.document || { createElement: () => ({ width: 0, height: 0,
  getContext: () => new Proxy({}, { get: (t, k) => (/^create(Linear|Radial)Gradient$/.test(k) ? () => ({ addColorStop() {} }) : () => {}), set: () => true }) }) };
const THREE = await import(join(ROOT, 'game/vendor/three.module.js'));
const { StageBreaks } = await import(join(ROOT, 'game/js/stagebreaks.js'));
await check('floor break: lights and materials exist from stage build; the break only switches them on', () => {
  const scene = new THREE.Scene();
  let compiled = 0;
  const stageDef = { id: 'teststage', dims: { wallDistance: 8, depth: 8 }, breakables: [{ type: 'floor', x: 0, z: 0, r: 2.5, depth: 6 }] };
  const game = { roundState: 'fight', arena: { scene, _stage: { def: { id: 'teststage' } }, shake() {}, compileFor() { compiled++; } },
    ui: { updateHP() {} }, rage: { onHitKO() {} }, p1: null, p2: null, _hitStop: 0 };
  const sb = new StageBreaks(game);
  sb.bindStage(stageDef, { setArenaLimit() {}, setGroundY() {} });
  sb._ensureBuilt();
  assert.ok(sb._built && compiled === 1, 'built and compiled once with the stage');
  const lights = () => { const l = []; scene.traverse((o) => { if (o.isLight) l.push(o); }); return l; };
  const mats = () => { const s = new Set(); scene.traverse((o) => { for (const m of [].concat(o.material || [])) s.add(m.uuid); }); return s; };
  const l0 = lights();
  assert.equal(l0.length, 3, 'the three ember lights exist from stage build');
  assert.ok(l0.every((l) => l.intensity === 0 && l.visible), 'dark but present (the light count never changes)');
  const def = sb.defs.find((d) => d.type === 'floor');
  assert.ok(def._disc && def._disc.visible === false, 'lower-level disc built, hidden');
  assert.ok(sb._pool.length >= 54, 'burst particles pooled: ' + sb._pool.length);
  const m0 = mats();
  const victim = { root: { position: new THREE.Vector3(0.5, 0, 0.3) }, hp: 100, maxHp: 100, dead: false, _knockout() {} };
  const attacker = { root: { position: new THREE.Vector3(-0.6, 0, 0) } };
  sb.checkHit(attacker, victim, { knock: 7, launch: true, knockdown: true }, 'hit');
  assert.ok(sb.broken.size === 1, 'the floor broke');
  const l1 = lights();
  assert.equal(l1.length, 3, 'no light added at the break');
  assert.ok(l1.every((l) => l.intensity === 14), 'embers on');
  assert.ok(def._disc.visible, 'disc shown');
  const m1 = mats();
  const added = [...m1].filter((u) => !m0.has(u));
  assert.equal(added.length, 0, 'no material created at the break: ' + added.length);
  assert.equal(sb.groundY, -6);
});

console.log(JSON.stringify({ fails }));
if (fails) { console.log('FAIL lag-hits-inputs'); process.exit(1); }
console.log('PASS lag-hits-inputs');
