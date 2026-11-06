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
