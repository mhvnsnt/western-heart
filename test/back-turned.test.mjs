// BACK-TURNED (BT) system (2026-11-06, owner report: "there's no back turned
// moment in the game... it keeps making them do that while facing the opponent —
// they'll turn backwards and do the move instead").
//
// Diagnosis (docs/movesets/BT-SYSTEM-FIX-2026-11-06.md): the moveset data and the
// input resolver were already Tekken-shaped — BT rows are keyed BT.*, moves end
// back-turned per their own frame data ('(BT)' notes / ',B' string variants /
// explicit stance_after), and the buffer only prefixes BT. when the context says
// back-turned (the roster-wide facing matrix below leaked ZERO BT rows before
// this fix too). What was missing was the STATE itself:
//   1. BT lived in the timed stance slot (0.8 s) and entering it overwrote any
//      character stance, so composed rows (BT_RFF.1, NSS.BT.d+1) could never fire.
//   2. Fighter.update() snapped the body to face the opponent every frame with
//      no BT exception, so a back-turned fighter still LOOKED facing while its
//      presses resolved BT rows — the BT move "fired from the front".
// Fix: BT is a facing state of its own (Fighter._bt) — no timer, coexists with a
// stance, the body faces away while it holds, and it ends the Tekken way:
// stepping toward the opponent re-faces; crouch / sidestep / jump turn around;
// an attack or a hit resolves it through the normal move flow. The buffer tries
// the composed BT spellings the data keys (BT_RFF. / NSS.BT.) before plain BT.,
// and _prepare slots the shared buttons a BT row's own source command declares
// ('BT 1 (or 2)' -> BT.2 fires the BT.1 row, as demonio's merged slots already
// wired by hand) instead of letting the press fall through to the facing row.
// Run: node --test test/back-turned.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const M = await import(join(ROOT, 'game/js/movesets.js'));
const MS = join(ROOT, 'game/assets/movesets');
const load = (fid) => { const d = JSON.parse(fs.readFileSync(join(MS, fid + '.json'), 'utf8')); M.registerMoveset(fid, d); return d; };
const keyOf = (fid, notation) => { const r = M.resolveMove(fid, notation); return r ? r.key : null; };
const BT_KEY = /(^|\.)BT(?=[.+_])/;
const BTNS = ['1', '2', '3', '4'];
const CHORDS = ['1+2', '1+3', '2+4', '3+4'];

test('facing presses NEVER fire a back-turned row (roster-wide)', () => {
  let probed = 0;
  for (const f of fs.readdirSync(MS).filter((n) => n.endsWith('.json'))) {
    const fid = f.replace(/\.json$/, '');
    let d; try { d = load(fid); } catch { continue; }
    if (!d.moves) continue;
    probed++;
    for (const b of BTNS) {
      const n = new M.TekkenBuffer(fid).pressButton(b, {});
      assert.ok(!BT_KEY.test(keyOf(fid, n) || ''), `${fid}: facing ${b} fired BT row ${keyOf(fid, n)}`);
    }
    for (const c of CHORDS) {
      const n = new M.TekkenBuffer(fid).pressChord(c, {});
      assert.ok(!BT_KEY.test(keyOf(fid, n) || ''), `${fid}: facing ${c} fired BT row ${keyOf(fid, n)}`);
    }
  }
  assert.ok(probed > 100, `probed ${probed} movesets`);
});

test('the named five: facing press = facing move, BT press = the BT move', () => {
  load('pond');
  assert.equal(keyOf('pond', new M.TekkenBuffer('pond').pressButton('1', {})), '1~t8.raven'); // her own slots put the T8 Raven row on 1
  assert.equal(keyOf('pond', new M.TekkenBuffer('pond').pressButton('1', { backturned: true })), 'BT.1');
  assert.equal(keyOf('pond', new M.TekkenBuffer('pond').pressButton('2', { backturned: true })), 'BT.2');
  load('pantera');
  assert.equal(keyOf('pantera', new M.TekkenBuffer('pantera').pressButton('1', { backturned: true })), 'BT.1');
  load('demonio'); // demonio's own slots declare the sharing: BT.2 -> BT.1, BT.4 -> BT.3
  assert.equal(keyOf('demonio', new M.TekkenBuffer('demonio').pressButton('2', { backturned: true })), 'BT.1');
  assert.equal(keyOf('demonio', new M.TekkenBuffer('demonio').pressButton('4', { backturned: true })), 'BT.3');
  load('ryusan');
  assert.equal(keyOf('ryusan', new M.TekkenBuffer('ryusan').pressButton('1', { backturned: true })), 'BT 1');
  assert.equal(keyOf('ryusan', new M.TekkenBuffer('ryusan').pressButton('1', {})), '1');
  load('tobi');
  assert.equal(keyOf('tobi', new M.TekkenBuffer('tobi').pressButton('3', { backturned: true })), 'BT.3');
  assert.equal(keyOf('tobi', new M.TekkenBuffer('tobi').pressButton('4', { backturned: true })), 'BT.4');
});

test('BT shared buttons declared by a row\'s own command ("BT 1 (or 2)") fire the BT row, not the facing row', () => {
  for (const fid of ['demonio-human', 'demonio-winged', 'demonio-bloodline-ember', 'gyou-spirit-body',
                     't3-anna', 't3-eddy', 't3-julia', 't3-nina', 't3-paul']) {
    load(fid);
    assert.equal(keyOf(fid, new M.TekkenBuffer(fid).pressButton('2', { backturned: true })), 'BT.1', `${fid}: BT 2`);
    assert.equal(keyOf(fid, new M.TekkenBuffer(fid).pressButton('4', { backturned: true })), 'BT.3', `${fid}: BT 4`);
  }
  load('t3-anna'); // 'BT d+1 (or d+2)' is declared the same way
  const b = new M.TekkenBuffer('t3-anna'); b.noteDirection('d');
  assert.equal(keyOf('t3-anna', b.pressButton('2', { backturned: true })), 'BT.d+1');
  for (const fid of ['sakura', 'sha', 'star']) { // Xiaoyu BT throw: 'BT 1+3 (or 2+4)'
    load(fid);
    assert.equal(keyOf(fid, new M.TekkenBuffer(fid).pressChord('2+4', { backturned: true })), 'BT.1+3', `${fid}: BT 2+4`);
  }
});

test('composed BT rows the data keys (BT_RFF. / NSS.BT.) fire while back-turned in that stance', () => {
  load('tobi');
  assert.equal(keyOf('tobi', new M.TekkenBuffer('tobi').pressButton('1', { backturned: true, stance: 'RFF' })), 'BT_RFF.1');
  assert.equal(keyOf('tobi', new M.TekkenBuffer('tobi').pressButton('2', { backturned: true, stance: 'RFF' })), 'BT_RFF.1'); // '(During BT RFF) 1 or 2': the 2 press fires the shared row
  assert.equal(keyOf('tobi', new M.TekkenBuffer('tobi').pressButton('4', { backturned: true, stance: 'RFF' })), 'BT_RFF.4');
  assert.equal(keyOf('tobi', new M.TekkenBuffer('tobi').pressButton('1', { stance: 'RFF' })), 'RFF.1'); // facing: the stance row, unchanged
  load('koreshi');
  const kb = new M.TekkenBuffer('koreshi'); kb.noteDirection('d');
  assert.equal(keyOf('koreshi', kb.pressButton('1', { backturned: true, stance: 'NSS' })), 'NSS.BT.d+1');
  const kf = new M.TekkenBuffer('koreshi'); kf.noteDirection('d');
  assert.equal(keyOf('koreshi', kf.pressButton('1', { stance: 'NSS' })), 'NSS.d+1'); // facing NSS row, unchanged
});

test('BT dominates a character stance at the buffer (Pond in MIST, back-turned)', () => {
  load('pond');
  assert.equal(keyOf('pond', new M.TekkenBuffer('pond').pressButton('1', { backturned: true, stance: 'MIST' })), 'BT.1');
});

/* ---- Fighter state: BT is a facing state, not a timed stance ---- */
const F = await import(join(ROOT, 'game/js/fighter.js')).catch(() => null);
function makeFighter() {
  const f = Object.create(F.Fighter.prototype);
  f.char = { id: 'pond' }; f._movesetId = 'pond';
  f.root = { position: { x: 0, y: 0, z: 0 } };
  f.state = 'idle'; f.stateT = 0; f.stun = 0; f.invuln = 0; f.lockT = 0;
  f.hp = 100; f.maxHp = 100; f.dead = false; f.onGround = true;
  f.stance = null; f.stanceT = 0; f._risingT = 0; f._bt = false; f._stanceSpins = 0;
  f.vx = 0; f.vy = 0; f.vz = 0; f.facing = 1; f.brawler = false; f._cinematic = null; f._opp = null;
  f.stats = { jump: 8, regenPerSec: 0 };
  f.tekken = { running: () => false, cdActive: () => false };
  f._tickState = () => {}; f._drainPressBuffer = () => {}; f._physics = () => {}; f._animate = () => {};
  return f;
}
const OPP = { root: { position: { x: 2, y: 0, z: 0 } }, state: 'idle' };
const yawTo = Math.atan2(2, 0);

test('fighter body faces AWAY while back-turned, and BT has no timer', (t) => {
  if (!F) { t.skip('fighter.js not in this checkout'); return; }
  const f = makeFighter();
  f.update(0.016, OPP);
  assert.ok(Math.abs(f._faceYaw - yawTo) < 1e-9, 'facing: yaw toward the opponent');
  f._bt = true;
  f.update(0.016, OPP);
  assert.ok(Math.abs(Math.abs(f._faceYaw - yawTo) - Math.PI) < 1e-9, 'back-turned: yaw away from the opponent');
  for (let i = 0; i < 200; i++) f.update(0.016, OPP); // 3.2 s idle — far past the old 0.8 s stance timer
  assert.equal(f._bt, true, 'BT persists in neutral (no timer)');
  assert.ok(Math.abs(Math.abs(f._faceYaw - yawTo) - Math.PI) < 1e-9, 'still turned away');
});

test('turn-around rules: step toward re-faces; walk away keeps BT; crouch / sidestep / jump clear it', (t) => {
  if (!F) { t.skip('fighter.js not in this checkout'); return; }
  const f = makeFighter();
  f._bt = true; f.vx = -1.5; f.state = 'walk';
  f.update(0.016, OPP);
  assert.equal(f._bt, true, 'walking away stays back-turned');
  f.vx = 1.5;
  f.update(0.016, OPP);
  assert.equal(f._bt, false, 'stepping toward the opponent turns around');
  f._bt = true; f.tryCrouch(true);
  assert.equal(f._bt, false, 'crouch turns around');
  assert.equal(f.state, 'crouch');
  const j = makeFighter(); j._bt = true; j.tryJump();
  assert.equal(j._bt, false, 'jump turns around');
  const s = makeFighter(); s._bt = true;
  assert.equal(s.trySidestep(1), true);
  assert.equal(s._bt, false, 'sidestep re-faces');
});

test('input context: backturned comes from the facing state and coexists with a stance', (t) => {
  if (!F) { t.skip('fighter.js not in this checkout'); return; }
  const f = makeFighter();
  assert.equal(f._inputCtx().backturned, false);
  f._bt = true; f.stance = 'RFF';
  const ctx = f._inputCtx();
  assert.equal(ctx.backturned, true);
  assert.equal(ctx.stance, 'RFF', 'the character stance survives entering BT');
});

/* ---- BT GUARD: Tekken-strict + the multi-arm exception (owner rulings
   2026-11-06: Tekken-strict for everyone; multi-arm fighters keep BT guard
   under the hybrid handicap — bleed chip + SoulCalibur guard-break strain.
   Design + strain provenance: game/js/bt-guard.js.) ---- */
const BG = await import(join(ROOT, 'game/js/bt-guard.js')).catch(() => null);
function makeHitFighter(id) {
  const f = makeFighter();
  f.char = { id }; f._movesetId = id;
  f.hp = 180; f.maxHp = 180; f.meter = 0; f.maxMeter = 100; f.soulMeterMult = 1;
  f.stats = { speed: 2.8, jump: 8, power: 1, defense: 1, chipMult: 1 };
  f._stickDir = 'b';            // holding back: standing guard posture
  f.isPlayer = true;
  f._btGuardCfg = BG ? BG.btGuardFor(id, f.char) : null;
  f._btStrain = 0; f._btGuardBroken = false;
  f._addRecoverable = F.Fighter.prototype._addRecoverable;
  f._pickReaction = F.Fighter.prototype._pickReaction;
  f._knockout = () => { f.dead = true; };
  return f;
}
function makeAttacker() {
  const a = Object.create(F.Fighter.prototype);
  a.root = { position: { x: 2, y: 0, z: 0 } };
  a.stats = { power: 1, chipMult: 1 };
  a._clock = 0; a._vtriggerT = 0; a._maxT = 0; a._vbreakT = 0; a.kindle = null;
  return a;
}
const MID = { damage: 16, knock: 2, hitWord: 0x217 };        // mid: standing-guard bit only
const LOW = { damage: 12, knock: 2, hitWord: 0x10F };        // low: crouch-guard bit only
const THROW = { damage: 20, knock: 2, isGrab: true, hitWord: 0x800 };
const KD_MOVE = { damage: 10, knock: 8, hitWord: 0x217 };    // knock >= 6: knockdown class

test('BT guard (a): back-turned + holding guard -> the hit lands UNGUARDED (Tekken-strict)', (t) => {
  if (!F) { t.skip('fighter.js not in this checkout'); return; }
  const f = makeHitFighter('pond'); const atk = makeAttacker();
  f.state = 'block'; f._bt = true;
  const hpBefore = f.hp;
  const r = f.receiveHit({ ...MID }, atk);
  assert.equal(r, 'hit', 'no block while back-turned: full hit resolution');
  assert.equal(hpBefore - f.hp, MID.damage, 'full damage, not chip');
  assert.equal(f.state, 'hitstun');
  assert.equal(f._bt, false, 'the landed hit resolves BT, as #1611 left it');
});

test('BT guard (b): facing + holding guard -> blocks exactly as before', (t) => {
  if (!F) { t.skip('fighter.js not in this checkout'); return; }
  const f = makeHitFighter('pond'); const atk = makeAttacker();
  f.state = 'block'; f._bt = false;
  const hpBefore = f.hp;
  const r = f.receiveHit({ ...MID }, atk);
  assert.equal(r, 'block');
  assert.ok(Math.abs((hpBefore - f.hp) - MID.damage * 0.12) < 1e-9, 'front-guard chip stays 0.12');
  assert.equal(f.meter, 4, 'front guard still earns +4 meter');
  assert.equal(f.vx, -MID.knock * 0.5, 'front-guard pushback unchanged');
});

test('BT guard (c): turn around via a #1611 exit path -> guard blocks again', (t) => {
  if (!F) { t.skip('fighter.js not in this checkout'); return; }
  const f = makeHitFighter('pond'); const atk = makeAttacker();
  f._bt = true; f.tryCrouch(true);                 // crouch = a #1611 turn-around
  assert.equal(f._bt, false);
  f.state = 'block'; f._stickDir = 'b';
  assert.equal(f.receiveHit({ ...MID }, atk), 'block', 'guard restored the moment BT cleared');
});

test('BT guard (d): a BT defender takes the #1611 back-hit knockdown', (t) => {
  if (!F) { t.skip('fighter.js not in this checkout'); return; }
  const f = makeHitFighter('pond'); const atk = makeAttacker();
  f._bt = true; f.state = 'idle';
  const r = f.receiveHit({ ...KD_MOVE }, atk);
  assert.equal(r, 'hit');
  assert.equal(f.state, 'knockdown');
  assert.equal(f._kdHeadTowards, true, 'hit in the back: falls head towards the attacker');
  assert.equal(f._kdFaceDown, true, 'hit in the back: falls face down (FDFA)');
});

test('BT guard (e): the multi-arm exception — Chatur BLOCKS back-turned, Pond eats the hit', (t) => {
  if (!F || !BG) { t.skip('bt-guard.js not in this checkout'); return; }
  const atk = makeAttacker();
  const c = makeHitFighter('chatur');
  assert.ok(c._btGuardCfg, 'chatur resolves a bt_guard config from her model data');
  c.state = 'block'; c._bt = true;
  assert.equal(c.receiveHit({ ...MID }, atk), 'block', 'the back pair guards');
  assert.equal(c._bt, true, 'a BT block never clears BT (clears_bt: false)');
  const p = makeHitFighter('pond');
  assert.equal(p._btGuardCfg, null, 'pond has no exception');
  p.state = 'block'; p._bt = true;
  assert.equal(p.receiveHit({ ...MID }, atk), 'hit', 'same setup, normal fighter: Tekken-strict');
});

test('BT guard (f): BT block bleeds 0.30 chip, earns NO meter, pushes back at half rate', (t) => {
  if (!F || !BG) { t.skip('bt-guard.js not in this checkout'); return; }
  const atk = makeAttacker();
  const front = makeHitFighter('pond'); front.state = 'block';
  const frontHp = front.hp;
  assert.equal(front.receiveHit({ ...MID }, atk), 'block');
  const frontChip = frontHp - front.hp, frontPush = Math.abs(front.vx);
  const c = makeHitFighter('chatur'); c.state = 'block'; c._bt = true;
  const hpBefore = c.hp;
  assert.equal(c.receiveHit({ ...MID }, atk), 'block');
  const btChip = hpBefore - c.hp;
  assert.ok(Math.abs(btChip - MID.damage * 0.30) < 1e-9, 'BT chip = the 0.30 bleed rate');
  assert.ok(Math.abs(btChip / frontChip - 0.30 / 0.12) < 1e-9, 'BT chip scales off the same formula as front guard');
  assert.equal(c.meter, 0, 'meter_on_block is 0 (front guard earned +4)');
  assert.ok(Math.abs(Math.abs(c.vx) - frontPush * 0.5) < 1e-9, 'pushback at pushback_mult 0.5');
  assert.ok(Math.abs((c._recoverable || 0) - btChip) < 1e-9, 'bled chip feeds the recoverable pool, as front guard');
  assert.ok(Math.abs(c._btStrain - 0.75 * MID.damage) < 1e-9, 'one block of strain: 0.75 x damage');
});

test('BT guard (g): strain accumulates, warnings fire at 60/80, at max the guard BREAKS', (t) => {
  if (!F || !BG) { t.skip('bt-guard.js not in this checkout'); return; }
  const atk = makeAttacker();
  const c = makeHitFighter('chatur'); c.state = 'block'; c._bt = true;
  // 16-dmg mid -> 12 strain per block: 5 blocks = 60 (warn 1), 7 = 84 (warn 2), 9 = capped 100 (break)
  for (let i = 0; i < 5; i++) assert.equal(c.receiveHit({ ...MID }, atk), 'block');
  assert.equal(c.btGuardState().warn, 1, 'yellow warning at 60% strain (SC)');
  for (let i = 0; i < 2; i++) assert.equal(c.receiveHit({ ...MID }, atk), 'block');
  assert.equal(c.btGuardState().warn, 2, 'red warning at 80% strain (SC)');
  assert.equal(c.receiveHit({ ...MID }, atk), 'block');
  assert.equal(c.receiveHit({ ...MID }, atk), 'block', 'the block that reaches strain max still blocks');
  const st = c.btGuardState();
  assert.equal(st.strain, 100); assert.equal(st.broken, true, 'the back pair is spent');
  const hpBefore = c.hp;
  assert.equal(c.receiveHit({ ...MID }, atk), 'hit', 'next high/mid lands unguarded while still back-turned');
  assert.equal(hpBefore - c.hp, MID.damage, 'post-break hit is full damage, not chip');
});

test('BT guard (h): strain resets when _bt ends; a fresh BT stint guards again', (t) => {
  if (!F || !BG) { t.skip('bt-guard.js not in this checkout'); return; }
  const atk = makeAttacker();
  const c = makeHitFighter('chatur'); c.state = 'block'; c._bt = true;
  for (let i = 0; i < 9; i++) c.receiveHit({ ...MID }, atk);   // break the pair
  assert.equal(c.btGuardState().broken, true);
  c.tryCrouch(true);                                            // a real BT exit (#1611 path)
  assert.equal(c._bt, false);
  c.update(0.016, OPP);                                         // the strain watchdog tick
  assert.deepEqual([c.btGuardState().strain, c.btGuardState().broken], [0, false], 'strain spent with the stint');
  c.state = 'block'; c._stickDir = 'b'; c._bt = true;           // fresh BT stint
  assert.equal(c.receiveHit({ ...MID }, atk), 'block', 'the back pair guards again');
});

test('BT guard (i): lows and throws beat the BT guard clean, even at zero strain', (t) => {
  if (!F || !BG) { t.skip('bt-guard.js not in this checkout'); return; }
  const atk = makeAttacker();
  const c = makeHitFighter('chatur'); c.state = 'block'; c._bt = true;
  const hpLow = c.hp;
  assert.equal(c.receiveHit({ ...LOW }, atk), 'hit', 'lows are not covered (high/mid only)');
  assert.equal(hpLow - c.hp, LOW.damage, 'the low lands at 100%, no chip');
  const c2 = makeHitFighter('chatur'); c2.state = 'block'; c2._bt = true;
  const hpThrow = c2.hp;
  const r = c2.receiveHit({ ...THROW }, atk);
  assert.notEqual(r, 'block', 'throws are never BT-guarded');
  assert.equal(hpThrow - c2.hp, THROW.damage, 'the throw lands at 100%');
});

/* The multi-arm table is DERIVED from the fighters' in-game models, not a
   name list: re-run the same arm-chain detector
   (tools/anatomy/bt_guard_arm_scan.py) over the GLB bytes and require the
   checked-in table to match — every entry qualifies, and the two
   owner-named fighters whose data does not carry the extra pair stay out. */
function armChainRoots(glbPath) {
  const buf = fs.readFileSync(glbPath);
  const clen = buf.readUInt32LE(12);
  const js = JSON.parse(buf.subarray(20, 20 + clen).toString('utf8'));
  const nodes = js.nodes || [];
  const joints = new Set();
  for (const s of js.skins || []) for (const j of s.joints || []) joints.add(j);
  const parent = {};
  nodes.forEach((n, i) => { for (const c of n.children || []) parent[c] = i; });
  const armWord = (nm) => ['arm', 'shoulder', 'elbow', 'wrist', 'hand', 'clavicle'].some((k) => nm.includes(k));
  const roots = [];
  for (const j of [...joints].sort((a, b) => a - b)) {
    const nm = (nodes[j].name || '').toLowerCase();
    const isStart = nm.includes('shoulder') || nm.includes('upper_arm') || nm.includes('upperarm') ||
      nm === 'leftarm' || nm === 'rightarm' || (nm.endsWith('arm') && !nm.includes('fore'));
    const p = parent[j];
    if (!isStart || (p != null && armWord((nodes[p].name || '').toLowerCase()))) continue;
    let hands = 0; const stack = [j];
    while (stack.length) {
      const x = stack.pop();
      if ((nodes[x].name || '').toLowerCase().includes('hand')) hands++;
      for (const c of nodes[x].children || []) stack.push(c);
    }
    if (hands) roots.push(nodes[j].name);
  }
  return roots;
}

test('BT guard data: the multi-arm table matches the models on disk (derived, not named)', (t) => {
  if (!BG) { t.skip('bt-guard.js not in this checkout'); return; }
  for (const [id, entry] of Object.entries(BG.BT_GUARD_MULTI_ARM)) {
    const p = join(ROOT, entry.model);
    if (!fs.existsSync(p)) { t.skip(entry.model + ' not in this checkout'); return; }
    const roots = armChainRoots(p);
    assert.ok(roots.length > 2, id + ': in-game model carries more than one arm pair');
    assert.deepEqual([...roots].sort(), [...entry.chains].sort(), id + ': checked-in chains match the GLB');
  }
  // The documented negatives: the exception activates when their model
  // data carries the extra pair — until then the flag stays OFF.
  const negatives = {
    'dxmmii (attire1)': 'roster/dxmmii/attires/attire1/model-rigged.glb',
    'dxmmii (patchwork)': 'roster/dxmmii/attires/patchwork-dj/dxmmii-patchwork-rigged.glb',
    'zen (attire1)': 'roster/zen/attires/attire1/model-rigged.glb',
    'zen (tentacle)': 'roster/zen/tentacle/model-rigged.glb',
    'zen (spirit)': 'roster/zen/spirit/model-rigged.glb',
  };
  for (const [label, rel] of Object.entries(negatives)) {
    const p = join(ROOT, rel);
    if (!fs.existsSync(p)) continue;
    assert.ok(armChainRoots(p).length <= 2, label + ': no extra arm pair in current data');
  }
  assert.equal(BG.btGuardFor('dxmmii-patchwork', { id: 'dxmmii-patchwork' }), null);
  assert.equal(BG.btGuardFor('zen', { id: 'zen' }), null);
  assert.ok(BG.btGuardFor('chatur', { id: 'chatur' }), 'chatur qualifies on her model data');
});
