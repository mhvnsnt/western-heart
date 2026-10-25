/* brawler-sim.test.mjs — headless bot playthrough of the Heart and Mind
 * Within brawler (worker 20, phase-1 verification).
 *
 * Runs the REAL game/js/brawler.js (byte for byte, imported from a data:
 * URL so it stays ESM; its imports are redirected by brawler-sim-hooks.mjs
 * to headless stubs in brawler-sim-stubs/). A bot plays the full descent:
 * moves camera-relative, attacks with Tekken limbs, blocks when threatened,
 * surges at full meter, collects soul embers — through all 5 stages and
 * all 5 bosses to victory.
 *
 * What this proves: the mode loop is genuinely playable end-to-end
 * (spawn → waves → zone gates → bosses incl. masks-multiply, sphere
 * spawner, shadow second form → stage clear → victory), with no stubs
 * in the loop and no exceptions. Rendering/combat feel is verified
 * live in the browser (parent playtest).
 *
 * Run: node --test game/tests/brawler-sim.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { register } from 'node:module';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const TESTDIR = dirname(fileURLToPath(import.meta.url));
const ROOT = join(TESTDIR, '..', '..');

// Redirect brawler.js's imports to headless stubs before loading it.
register('./brawler-sim-hooks.mjs', import.meta.url);

/* ---- DOM / browser globals ---- */
const statusEl = { style: {}, textContent: '' };
globalThis.document = {
  getElementById: (id) => (id === 'brawler-status' ? statusEl : null),
  createElement: (tag) => {
    if (tag === 'canvas') return { width: 64, height: 64,
      getContext: () => ({ createRadialGradient: () => ({ addColorStop(){} }),
        fillRect(){}, set fillStyle(v){} }) };
    return { style: {} };
  },
};
globalThis.requestAnimationFrame = (fn) => setTimeout(fn, 0);

/* ---- the real module under test, byte for byte ---- */
const brawlerSrc = readFileSync(join(ROOT, 'game/js/brawler.js'), 'utf8');
const BRAWLER_URL = 'data:text/javascript;base64,' + Buffer.from(brawlerSrc).toString('base64');
const { BrawlerGame } = await import(BRAWLER_URL);

// Keep failure output readable: data: URLs make stacks megabytes long.
function shortErr(e) {
  return String((e && e.stack) || e).split('\n').slice(0, 4).join('\n')
    .replace(/data:text\/javascript;base64,[A-Za-z0-9+/=]+/g, '[brawler.js]');
}
process.on('uncaughtException', (e) => {
  console.error('SIM UNCAUGHT:\n' + shortErr(e));
  process.exit(1);
});

/* ---- harness: stub game/input/ui/roster/content ---- */
const hudNotes = [];
const input = {
  brawlerMode: false, axisX: 0, axisY: 0, joyY: 0, enabled: false,
  held: { block: false }, _q: [],
  enable(on){ this.enabled = on; },
  reset(){ this.axisX=0; this.axisY=0; this.joyY=0; this._q.length=0; this.held.block=false; },
  consume(){ const q=this._q.slice(); this._q.length=0; return q; },
};
const ui = {
  setNames(){}, setRounds(){}, setStageName(){}, updateHP(){}, updateMeter(){},
  setTimer(){}, combo(){}, surgeFlash(){}, surgeName(){},
  throwBreakPrompt(){}, throwEscape(){}, matchOver(){},
  hudNote(m){ hudNotes.push(m); },
};
const sceneStub = { add(){}, remove(){} };
const game = {
  arena: { scene: sceneStub, setStage(){}, camOverride: null, shake(){} },
  input, _hitStop: 0, brawler: null,
  resetFightState(){ this.brawler = null; },
};
function mkFighter(id, dmgMul = 1) {
  return { id, name: id.toUpperCase(), model: 'pantera',
    // Loop-test proxy: the stub bot only throws single pokes (no Tekken
    // strings/combos/movement/oki), so it gets overwhelming stats to
    // blitz the descent. What's under test is the MODE LOOP — spawns,
    // waves, zone gates, boss phases, stage flow, victory — which is
    // identical either way. Balance is verified by human playtest.
    dmgMul: id === 'f0' ? 10 : dmgMul,
    maxHp: id === 'f0' ? 20000 : 100,
    colors: { suit: 0x111111, trim: 0xffffff },
    surge: { color: 0xff2222, accent: 0xffffff, name: 'TEST SURGE' },
    ai: { aggression: 0.6, grabBias: 0.15, reaction: 0.55 },
    stats: { speed: 2.8, jump: 7.2, power: 1.1, defense: 1.05 } };
}
const roster = [];
for (let i = 0; i < 8; i++) roster.push(mkFighter('f' + i, 1));
const getChar = (id) => roster.find((c) => c.id === id) || null;
const content = {
  stages: [
    { n:1, key:'threshold', name:'THE THRESHOLD', stage:'test', sub:'', diff:0.45 },
    { n:2, key:'masks', name:'THE GALLERY OF MASKS', stage:'test', sub:'', diff:0.55 },
    { n:3, key:'drowning', name:'THE DROWNING ROOM', stage:'test', sub:'', diff:0.65 },
    { n:4, key:'furnace', name:'THE FURNACE', stage:'test', sub:'', diff:0.75 },
    { n:5, key:'stillpoint', name:'THE STILL POINT', stage:'test', sub:'', diff:0.90 },
  ],
  makeEcho: (c, d) => ({ ...c, id: c.id + '-echo', name: 'ECHO OF ' + c.name,
    ai: { aggression: 0.6, reaction: 0.55 } }),
  buildShadowSelf: (c) => ({ ...c, id: c.id + '-shadow', name: 'SHADOW OF ' + c.name,
    stats: { power: 1.4, speed: 3.0, defense: 1.2 },
    ai: { aggression: 0.9, reaction: 0.85 } }),
};
const events = { stages: [], victory: false, death: false, surge: false, bosses: new Set() };
const hooks = {
  onStageIntro: (i, done) => { events.stages.push(i); done(); },
  onBossIntro: (s, k, l, done) => done(),
  onStageClear: (i, r, done) => done(),
  onVictory: (done) => { events.victory = true; done(); },
  onDeath: () => { events.death = true; },
};

test('bot playthrough: full 5-stage descent to victory', async () => {
  const B = new BrawlerGame({ game, input, ui, getChar, roster, content });
  await B.begin('f0', hooks);

  const dt = 1 / 60;
  let tick = 0, atkCd = 0, limb = 0;
  const limbs = ['1', '2', '3', '4'];
  while (tick < 400000 && !events.victory && !events.death) {
    // ---- bot brain ----
    const p = B.player;
    if (p && !p.dead) {
      let tx = null, tz = null, bd = 1e9;
      const consider = (x, z) => {
        const d = Math.hypot(x - p.root.position.x, z - p.root.position.z);
        if (d < bd) { bd = d; tx = x; tz = z; }
      };
      for (const e of B.enemies) if (!e.fighter.dead) consider(e.fighter.root.position.x, e.fighter.root.position.z);
      if (B.sphere && B.sphere.hp > 0) consider(B.sphere.mesh.position.x, B.sphere.mesh.position.z);
      if (tx === null && B.zoneState === 'advance') {
        const nz = B.zones[B.zoneIdx + 1]; if (nz) { tx = nz.cx; tz = nz.cz; bd = 99; }
      }
      // Threat check: only point-blank melee makes the bot block. (Full
      // projectile defense is a human-playtest skill; the loop test needs
      // the bot to close with kiting gunners instead of blocking forever.)
      let threat = false;
      for (const e of B.enemies) {
        if (e.fighter.dead) continue;
        const d = Math.hypot(e.fighter.root.position.x - p.root.position.x,
                             e.fighter.root.position.z - p.root.position.z);
        if (d < 1.8 && e.fighter.state === 'attack') { threat = true; break; }
      }
      input.held.block = threat;
      let foraging = false;
      if (p.hp < 45) {
        let ex = null, ez = null, ed = 1e9;
        for (const k of B.pickups) {
          const d = Math.hypot(k.mesh.position.x - p.root.position.x,
                               k.mesh.position.z - p.root.position.z);
          if (d < ed) { ed = d; ex = k.mesh.position.x; ez = k.mesh.position.z; }
        }
        if (ex !== null && ed < 14) { tx = ex; tz = ez; bd = ed; foraging = true; }
      }
      if (tx !== null && !input.held.block) {
        const wx = tx - p.root.position.x, wz = tz - p.root.position.z;
        const d = Math.hypot(wx, wz) || 1, nx = wx / d, nz2 = wz / d;
        const sy = Math.sin(B.camYaw), cy = Math.cos(B.camYaw);
        input.axisY = nx * sy + nz2 * cy;
        input.axisX = nx * (-cy) + nz2 * sy;
        atkCd -= dt;
        if (!foraging && bd < 2.8 && bd < 90 && atkCd <= 0 && p.canAct()) {
          input._q.push(limbs[limb++ % 4]); atkCd = 0.55;
        }
      } else { input.axisX = 0; input.axisY = 0; }
      if (p.meter >= p.maxMeter && !p.surgeForm) input._q.push('transform');
      if (p.surgeForm) events.surge = true;
      for (const e of B.enemies) if (e.boss) events.bosses.add(e.kind);
      if (B.sphere) events.bosses.add('sphere');
    }
    try {
      B.frame(dt);
    } catch (e) {
      console.error('SIM ERROR at tick ' + tick + ':\n' + shortErr(e));
      assert.fail('brawler.frame threw at tick ' + tick + ': ' + String((e && e.message) || e).slice(0, 200));
    }
    tick++;
    if (tick % 60000 === 0) {
      console.log(`  ... tick ${tick}: stage ${B.stageIdx + 1} zone ${B.zoneIdx + 1}` +
        ` foes ${B.enemies.filter((e) => !e.fighter.dead).length}` +
        ` hp ${B.player ? Math.round(B.player.hp) : '-'}`);
    }
  }

  console.log(`  finished at tick ${tick}: stages=[${events.stages}]` +
    ` bosses=[${[...events.bosses]}] surge=${events.surge} hudNotes=${hudNotes.length}` +
    ` death=${events.death} php=${B.player ? Math.round(B.player.hp) : '-'}` +
    ` zone=${B.zoneIdx + 1}/${B.zones.length} zoneState=${B.zoneState}` +
    ` foes=${B.enemies.map((e) => e.fighter.char.id + ':' + Math.round(e.fighter.hp)).join(',')}`);
  assert.ok(events.victory, 'the bot should complete the descent (victory)');
  assert.ok(!events.death, 'the bot should survive');
  assert.deepStrictEqual(events.stages, [0, 1, 2, 3, 4], 'all 5 stages started');
  assert.ok(events.surge, 'soul surge form fired at full meter');
  for (const k of ['warden', 'mask', 'ogre', 'shadow', 'shadow2', 'sphere'])
    assert.ok(events.bosses.has(k), `boss kind spawned: ${k}`);
  assert.ok(hudNotes.some((b) => /CLEARED/.test(b)), 'stage-clear HUD note shown');
  assert.ok(hudNotes.some((b) => /SOUL SURGE/.test(b)), 'surge HUD note shown');
});
