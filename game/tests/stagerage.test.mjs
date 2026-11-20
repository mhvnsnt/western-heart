/* stagerage.test.mjs — Stage mechanics + Rage + Soul Urge regression tests.
 *
 * Covers the worker-28 lane (stage breaks, rage arts/drives, slow-mo,
 * Soul Urge/Heat): rage thresholds, rage art/drive synthesis + input
 * resolution, slow-mo triggers, urge burst/engager/smash/dash wiring,
 * wall/floor break triggers, once-per-match semantics, bonus damage.
 *
 * Run: node --test game/tests/stagerage.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const sandbox = mkdtempSync(join(process.env.TMPDIR || '/tmp', 'wh-stagerage-'));

/* Stage the sandbox with python3: this VM's write filter throttles bursty
   node writes, but python chunked writes go through reliably. */
const STAGER = `
import sys, os, time
src, dst = sys.argv[1], sys.argv[2]
def wchunk(d, data):
    if isinstance(data, str):
        data = data.encode()
    with open(d, 'wb') as f:
        for i in range(0, len(data), 2048):
            f.write(data[i:i+2048])
            f.flush()
            time.sleep(0.02)
def wcp(s, d):
    wchunk(d, open(s, 'rb').read())
    time.sleep(0.1)
for fn in ['movesets.js', 'full-movelist.js', 'canon-names.js', 'rage.js', 'audio.js', 'soulurge.js', 'destruction.js']:
    wcp(os.path.join(src, fn), os.path.join(dst, fn))
wchunk(os.path.join(dst, 'three-stub.js'), '''__THREESTUB__''')
wchunk(os.path.join(dst, 'fighter-stub.js'),
    "export const calls = { arenaLimit: [], groundY: [] };\\n" +
    "export function setArenaLimit(v){ calls.arenaLimit.push(v); }\\n" +
    "export function setGroundY(v){ calls.groundY.push(v); }\\n")
sb = open(os.path.join(src, 'stagebreaks.js')).read()
sb = sb.replace("from 'three'", "from './three-stub.js'").replace("from './fighter.js'", "from './fighter-stub.js'")
wchunk(os.path.join(dst, 'stagebreaks.js'), sb)
wchunk(os.path.join(dst, 'package.json'), '{"type":"module"}')
print('staged ok')
`;
const THREE_STUB = `
export class _Rot { constructor(){ this.x=0; this.y=0; this.z=0; }
  set(x,y,z){ this.x=x; this.y=y; this.z=z; return this; } }
export class Group { constructor(){ this.children = []; this.parent = null; this.name='';
    this.position = new Vector3(); this.rotation = new _Rot(); }
  add(...o){ for (const x of o){ x.parent = this; this.children.push(x); } }
  remove(x){ this.children = this.children.filter(c => c !== x); }
  clear(){ this.children = []; } }
export class Mesh { constructor(g=null, m=null){ this.geometry=g; this.material=m||{opacity:1}; this.position=new Vector3(); this.rotation=new _Rot(); this.scale={setScalar(){}}; this.visible=true; this.castShadow=false; this.receiveShadow=false; } }
export class PlaneGeometry { constructor(){} }
export class BoxGeometry { constructor(){} }
export class CircleGeometry { constructor(){} }
export class Vector2 { constructor(x=0,y=0){ this.x=x; this.y=y; } }
export class Shape { constructor(pts=[]){ this.points=pts; } }
export class ExtrudeGeometry { constructor(){} translate(){ return this; } dispose(){} }
export class MeshBasicMaterial { constructor(o={}){ Object.assign(this, o); if (this.opacity===undefined) this.opacity=1; } }
export class MeshStandardMaterial { constructor(o={}){ Object.assign(this, o); if (this.opacity===undefined) this.opacity=1; } }
export class CanvasTexture { constructor(){ this.colorSpace=''; } }
export class Color { constructor(){ } setHex(){} }
export class Vector3 { constructor(x=0,y=0,z=0){ this.x=x; this.y=y; this.z=z; }
  set(x,y,z){ this.x=x; this.y=y; this.z=z; return this; }
  addScaledVector(v, s){ this.x+=v.x*s; this.y+=v.y*s; this.z+=v.z*s; return this; } }
export class PointLight { constructor(){ this.position=new Vector3(); } }
`;
execFileSync('python3',
  ['-c', STAGER.replace('__THREESTUB__', THREE_STUB.replace(/\\/g, '\\\\').replace(/'''/g, "\\'\\'\\'")),
   join(ROOT, 'game/js'), sandbox],
  { stdio: 'pipe' });

// minimal document for canvas textures
globalThis.document = {
  createElement: () => ({
    width: 0, height: 0,
    getContext: () => ({
      fillRect(){}, beginPath(){}, moveTo(){}, lineTo(){}, stroke(){}, arc(){},
      createLinearGradient: () => ({ addColorStop(){} }),
      createRadialGradient: () => ({ addColorStop(){} }),
      set fillStyle(v){}, set strokeStyle(v){}, set lineWidth(v){},
    }),
  }),
};

const imp = (f) => import(pathToFileURL(join(sandbox, f)).href);
const { registerMoveset, getFighterMoveset, TekkenBuffer, playedMoveset } = await imp('movesets.js');
const msApi = { playedMoveset, getFighterMoveset };
const { isRaging, ensureRageMoves, RageSystem, RAGE_ART_DAMAGE } = await imp('rage.js');
const { ensureUrgeMoves, SoulUrge, URGE_BURST_TIME, URGE_ENGAGER_TIME } = await imp('soulurge.js');
const { StageBreaks } = await imp('stagebreaks.js');
const fighterStubMod = await imp('fighter-stub.js');

/* fake moveset: a jab, a 1+2, a heavy, a launcher */
registerMoveset('testrage', {
  moves: {
    '1': { damage: 7, knock: 2.2, limb: 'armL', move_class: 'strike' },
    '1+2': { damage: 10, knock: 2.2, limb: 'armR', move_class: 'strike' },
    'f+2': { damage: 24, knock: 6.5, limb: 'armR', move_class: 'strike' },
    'launcher': { damage: 20, knock: 7, launch: true, limb: 'legR', move_class: 'strike' },
  },
});

test('rage threshold: <=25% hp, unspent, alive', () => {
  assert.equal(isRaging({ hp: 25, maxHp: 100, dead: false, _rageUsed: false }), true);
  assert.equal(isRaging({ hp: 26, maxHp: 100, dead: false, _rageUsed: false }), false);
  assert.equal(isRaging({ hp: 10, maxHp: 100, dead: false, _rageUsed: true }), false);
  assert.equal(isRaging({ hp: 0, maxHp: 100, dead: true, _rageUsed: false }), false);
});

test('ensureRageMoves synthesizes art + drive from real data', () => {
  assert.equal(ensureRageMoves('testrage', msApi), true);
  const ms = getFighterMoveset('testrage');
  const art = ms.moves['R.1+2'];
  assert.ok(art, 'rage art registered');
  assert.equal(art.damage, RAGE_ART_DAMAGE);
  assert.equal(art.armor, true);
  assert.equal(art.knockdown, true);
  const drive = ms.moves['RD.3+4'];
  assert.ok(drive, 'rage drive registered');
  assert.ok(drive.damage > 10, 'drive hits harder than the base 1+2');
  // idempotent
  assert.equal(ensureRageMoves('testrage', msApi), true);
  assert.equal(ms.moves['R.1+2'], art);
});

test('rage inputs resolve: 1+2 -> R.1+2, 3+4 -> RD.3+4 while raging', () => {
  const tb = new TekkenBuffer('testrage');
  assert.equal(tb.pressChord('1+2', { rage: true }), 'R.1+2');
  assert.equal(tb.pressChord('3+4', { rage: true }), 'RD.3+4');
  assert.equal(tb.pressChord('1+2', {}), '1+2', 'normal 1+2 when not raging');
  assert.equal(tb.pressChord('3+4', {}), null, 'no normal 3+4 in this moveset');
});

test('RageSystem: announce at threshold, clear when healed/spent', () => {
  const uiCalls = [];
  const game = {
    p1: { hp: 20, maxHp: 100, dead: false, _rageUsed: false, _rageOn: false, setRageAura(){} },
    p2: { hp: 100, maxHp: 100, dead: false, _rageUsed: false, _rageOn: false, setRageAura(){} },
    ui: { setRage: (id, on) => uiCalls.push([id, on]), banner: () => {} },
    wins: { p1: 0, p2: 0 }, roundsToWin: 2,
    arena: { shake(){} }, _hitStop: 0,
  };
  const rs = new RageSystem(game);
  rs.update();
  assert.equal(game.p1._rageOn, true);
  assert.deepEqual(uiCalls[0], ['p1', true]);
  // spend rage -> clears
  game.p1._rageUsed = true;
  rs.update();
  assert.equal(game.p1._rageOn, false);
  assert.deepEqual(uiCalls[uiCalls.length - 1], ['p1', false]);
  rs.resetRound();
  assert.equal(game.p1._rageUsed, false);
});

test('RageSystem.onHitKO: slow-mo on match-deciding and rage-art KOs only', () => {
  const mk = (wins) => ({
    p1: { attackName: 'f+2' }, p2: { attackName: 'f+2' },
    ui: {}, wins, roundsToWin: 2, arena: { shake(){} }, _hitStop: 0,
  });
  let g = mk({ p1: 1, p2: 0 });
  let rs = new RageSystem(g);
  assert.equal(rs.onHitKO(g.p1, g.p2), true, 'match point KO -> slow-mo');
  assert.ok(rs.slowMoT > 0);
  assert.equal(rs.timeScale < 1, true);

  g = mk({ p1: 0, p2: 0 });
  rs = new RageSystem(g);
  assert.equal(rs.onHitKO(g.p1, g.p2), false, 'round-1 KO -> no slow-mo');

  g = mk({ p1: 0, p2: 0 });
  g.p1.attackName = 'R.1+2';
  rs = new RageSystem(g);
  assert.equal(rs.onHitKO(g.p1, g.p2), true, 'rage-art KO -> slow-mo');
});

test('ensureUrgeMoves: burst + smash + engager flag', () => {
  assert.equal(ensureUrgeMoves('testrage', msApi), true);
  const ms = getFighterMoveset('testrage');
  assert.ok(ms.moves['UB.2+3'], 'urge burst registered');
  assert.equal(ms.moves['UB.2+3'].armor, true);
  assert.ok(ms.moves['US.2+3'], 'urge smash registered');
  assert.equal(ms.moves['launcher'].urgeEngager, true, 'launcher flagged as engager');
});

test('urge inputs: 2+3 -> UB.2+3 fresh, US.2+3 while urging', () => {
  const tb = new TekkenBuffer('testrage');
  assert.equal(tb.pressChord('2+3', { urgeAvailable: true, urgeOn: false }), 'UB.2+3');
  assert.equal(tb.pressChord('2+3', { urgeAvailable: false, urgeOn: true }), 'US.2+3');
});

test('SoulUrge: activate, timer pause on opponent hit, expiry, spendAll', () => {
  const uiCalls = [];
  const f1 = { _urgeUsed: false, _urgeOn: false, _urgePips: 0, _urgeT: 0, setUrgeAura(){} };
  const f2 = { state: 'idle', onGround: true };
  const game = {
    p1: f1, p2: f2,
    ui: { setUrge: (id, on) => uiCalls.push([id, on]), updateUrge(){}, banner(){} },
  };
  const su = new SoulUrge(game);
  assert.equal(su.activate(f1, 'p1', 2, URGE_ENGAGER_TIME), true);
  assert.equal(f1._urgeOn, true);
  assert.equal(f1._urgePips, 2);
  assert.deepEqual(uiCalls[0], ['p1', true]);
  // double activation refused (once per round)
  f1._urgeOn = false;
  assert.equal(su.activate(f1, 'p1', 1, URGE_BURST_TIME), false);
  f1._urgeOn = true;
  // timer ticks...
  su.update(1.0);
  assert.ok(f1._urgeT < URGE_ENGAGER_TIME && f1._urgeT > 13);
  // ...but pauses while the opponent is being hit
  const tBefore = f1._urgeT;
  f2.state = 'hitstun';
  su.update(1.0);
  assert.equal(f1._urgeT, tBefore, 'timer paused during opponent hitstun');
  f2.state = 'idle';
  // smash spends everything
  su.spendAll(f1, 'p1');
  assert.equal(f1._urgeOn, false);
  assert.deepEqual(uiCalls[uiCalls.length - 1], ['p1', false]);
  // natural expiry
  const f4 = { _urgeUsed: false, _urgeOn: false, _urgePips: 0, _urgeT: 0, setUrgeAura(){} };
  game.p1 = f4;
  su.activate(f4, 'p1', 1, URGE_BURST_TIME);
  su.update(URGE_BURST_TIME + 1);
  assert.equal(f4._urgeOn, false, 'urge expires at zero');
});

test('StageBreaks: wall break on heavy slam at the bound', () => {
  fighterStubMod.calls.arenaLimit.length = 0;
  fighterStubMod.calls.groundY.length = 0;
  const banners = [];
  const game = {
    roundState: 'fight',
    arena: { scene: { add(){} }, shake(){} },
    ui: { banner: (t) => banners.push(t), updateHP(){} },
    rage: { onHitKO(){} },
  };
  const sbk = new StageBreaks(game);
  const fx = { setArenaLimit: (v) => fighterStubMod.calls.arenaLimit.push(v), setGroundY: (v) => fighterStubMod.calls.groundY.push(v) };
  const fxArg = { setArenaLimit: () => {}, setGroundY: () => {} };
  sbk.bindStage({ id: 'shrine', dims: { wallDistance: 8.4, depth: 6 }, swatch: ['#000', '#f00'] }, fx);
  const atk = { root: { position: { x: 5, z: 0 } } };
  const def = { root: { position: { x: 8.2, z: 0 } }, hp: 100, dead: false,
    _knockout() { this.dead = true; } };
  sbk.checkHit(atk, def, { knock: 5 }, 'hit');
  assert.equal(sbk.broken.size, 1, 'wall broken');
  assert.deepEqual(fighterStubMod.calls.arenaLimit, [12.9], 'bounds extended past the breach');
  assert.equal(def.hp, 92, 'wall-break bonus damage applied');
  assert.ok(!banners.includes('WALL BREAK'), 'no on-screen break text: Tekken shows breaks via destruction + camera (UI immersion fix 2026-10-24)');
  // once per match: no double-break
  sbk.checkHit(atk, def, { knock: 5 }, 'hit');
  assert.equal(sbk.broken.size, 1);
  assert.equal(fighterStubMod.calls.arenaLimit.length, 1);
});

test('StageBreaks: light hits never break walls', () => {
  const game = {
    roundState: 'fight',
    arena: { scene: { add(){} }, shake(){} },
    ui: { banner(){}, updateHP(){} },
    rage: { onHitKO(){} },
  };
  const sbk = new StageBreaks(game);
  const fx = { setArenaLimit: (v) => fighterStubMod.calls.arenaLimit.push(v), setGroundY: (v) => fighterStubMod.calls.groundY.push(v) };
  const fxArg = { setArenaLimit: () => {}, setGroundY: () => {} };
  sbk.bindStage({ id: 'shrine', dims: { wallDistance: 8.4, depth: 6 }, swatch: ['#000', '#f00'] }, fx);
  const atk = { root: { position: { x: 5, z: 0 } } };
  const def = { root: { position: { x: 8.2, z: 0 } }, hp: 100, dead: false, _knockout(){} };
  sbk.checkHit(atk, def, { knock: 2 }, 'hit');
  assert.equal(sbk.broken.size, 0, 'jab at the wall does not break it');
  assert.equal(def.hp, 100, 'no bonus damage');
});

test('StageBreaks: floor break drops the level on a slam in the zone', () => {
  fighterStubMod.calls.groundY.length = 0;
  const banners = [];
  const game = {
    roundState: 'fight',
    arena: { scene: { add(){} }, shake(){} },
    ui: { banner: (t) => banners.push(t), updateHP(){} },
    rage: { onHitKO(){} },
  };
  const sbk = new StageBreaks(game);
  const fx = { setArenaLimit: (v) => fighterStubMod.calls.arenaLimit.push(v), setGroundY: (v) => fighterStubMod.calls.groundY.push(v) };
  const fxArg = { setArenaLimit: () => {}, setGroundY: () => {} };
  sbk.bindStage({ id: 'shrine', dims: { wallDistance: 8.4, depth: 6 }, swatch: ['#000', '#f00'],
    breakables: [{ type: 'floor', x: 0, z: 0, r: 2.5, depth: 6 }] }, fx);
  const atk = { root: { position: { x: 0, z: 0 } } };
  const def = { root: { position: { x: 0.5, z: 0.3 } }, hp: 100, dead: false,
    _knockout() { this.dead = true; } };
  sbk.checkHit(atk, def, { knock: 7 }, 'hit');
  assert.equal(sbk.groundY, -6, 'fighting level dropped');
  const gyCalls = fighterStubMod.calls.groundY;
  assert.equal(gyCalls[gyCalls.length - 1], -6, 'setGroundY(-6) called last');
  assert.equal(def.hp, 88, 'floor-break slam bonus applied');
  assert.ok(!banners.includes('FLOOR BREAK'), 'no on-screen break text: Tekken shows breaks via destruction + camera (UI immersion fix 2026-10-24)');
  // outside the zone: no break
  const def2 = { root: { position: { x: 6, z: 0 } }, hp: 100, dead: false, _knockout(){} };
  const sbk2 = new StageBreaks(game);
  sbk2.bindStage({ id: 'shrine', dims: { wallDistance: 8.4, depth: 6 }, swatch: ['#000', '#f00'],
    breakables: [{ type: 'floor', x: 0, z: 0, r: 2.5, depth: 6 }] }, fxArg);
  sbk2.checkHit(atk, def2, { knock: 7 }, 'hit');
  assert.equal(sbk2.groundY, 0, 'slam outside the cracked zone does not break');
});

test('SoulUrge.onHit: burst activates (1 pip/10s), engager gives 2 pips + heal, smash spends all', () => {
  const uiCalls = [];
  const mk = () => ({ _urgeUsed: false, _urgeOn: false, _urgePips: 0, _urgeT: 0,
    hp: 80, maxHp: 100, facing: 1, vx: 0, setUrgeAura(){}, });
  const f1 = mk(), f2 = mk();
  const game = { p1: f1, p2: f2,
    ui: { setUrge: (id, on) => uiCalls.push([id, on]), updateUrge(){}, banner(){} } };
  const su = new SoulUrge(game);
  su.onHit(f1, { urgeBurst: true });
  assert.equal(f1._urgeOn, true, 'burst hit activates urge');
  assert.equal(f1._urgePips, 1);
  assert.equal(f1._urgeT, URGE_BURST_TIME);
  assert.equal(f1._urgeUsed, true, 'once per round');
  // engager while already urging: no double-activate
  su.onHit(f1, { urgeEngager: true });
  assert.equal(f1._urgePips, 1, 'no re-trigger while urging');
  su.onBlockedHit(f2, { urgeBurst: true });
  assert.equal(f2._urgeOn, true, 'burst activates on block too (T8)');
  // smash spends everything
  su.onHit(f1, { urgeSmash: true });
  assert.equal(f1._urgeOn, false, 'smash ends urge');
  assert.equal(f1._urgePips, 0);
});

test('SoulUrge.onHit: engager on a fresh fighter heals + dashes in', () => {
  const f1 = { _urgeUsed: false, _urgeOn: false, _urgePips: 0, _urgeT: 0,
    hp: 70, maxHp: 100, facing: -1, vx: 0, setUrgeAura(){}, };
  const f2 = { _urgeUsed: false, _urgeOn: false };
  const game = { p1: f1, p2: f2, ui: { setUrge(){}, updateUrge(){}, banner(){} } };
  const su = new SoulUrge(game);
  su.onHit(f1, { urgeEngager: true });
  assert.equal(f1._urgeOn, true);
  assert.equal(f1._urgePips, 2, 'engager grants 2 pips');
  assert.equal(f1._urgeT, URGE_ENGAGER_TIME);
  assert.equal(f1.hp, 80, 'engager heals 10');
  assert.equal(f1.vx, -4, 'dash-in toward facing');
});

test('SoulUrge.spendPip: urge dash costs exactly one pip', () => {
  const game = { p1: null, p2: null, ui: {} };
  const su = new SoulUrge(game);
  const f = { _urgePips: 2 };
  su.spendPip(f);
  assert.equal(f._urgePips, 1);
  su.spendPip(f); su.spendPip(f);
  assert.equal(f._urgePips, 0, 'floors at zero');
});

test('RageSystem.slowMoScale: 0.12x while the clock runs, 1x after', () => {
  const game = { p1: null, p2: null, ui: {}, wins: { p1: 0, p2: 0 }, roundsToWin: 2 };
  const r = new RageSystem(game);
  r.slowMoT = 1.0;
  const scaled = r.slowMoScale(0.5);
  assert.ok(Math.abs(scaled - 0.06) < 1e-9, '0.12x scale');
  assert.ok(Math.abs(r.slowMoT - 0.5) < 1e-9, 'clock ticks in real seconds');
  r.slowMoT = 0;
  assert.equal(r.slowMoScale(0.5), 0.5, 'no slow-mo, full dt');
});
