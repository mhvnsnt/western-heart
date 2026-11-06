// Roster-100 L5 (2026-11-06): engine contexts for NO-ENTRY prefixed inputs,
// built only where a fighter's own data declares the entry.
//  - CD (crouch dash): rin / demonio / gyou each carry a move named
//    "Crouch Dash" in their own file; their files now declare it as
//    cd_entry, firing it latches the buffer's CD context for the entry
//    move's duration + grace, and CD. rows resolve inside that window.
//    awapop / pantera / tobi have CD. rows but declare NO entry move in
//    their data — theirs stay NO ENTRY (documented, not wired).
//  - SSL / SSR: the engine's sidestep gains a direction (ssSide, by the
//    _foeFlank convention); directional rows resolve while stepping.
// Run: node --test test/cd-ss-contexts.test.mjs
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

const CD_WIRED = { rin: 'f,n,d,d/f', demonio: 'f,n,d,df', gyou: 'd,d/f' };

test('cd_entry declarations name a real "Crouch Dash" row in the same file', () => {
  for (const [fid, entry] of Object.entries(CD_WIRED)) {
    const d = load(fid);
    assert.equal(d.cd_entry, entry, `${fid} declares cd_entry`);
    assert.ok(d.moves[entry], `${fid} cd_entry row exists`);
    assert.match(String(d.moves[entry].name || ''), /crouch dash/i, `${fid} entry row is the Crouch Dash`);
  }
  for (const fid of ['awapop', 'pantera', 'tobi']) {
    const d = load(fid);
    assert.equal(d.cd_entry, undefined, `${fid} declares no cd_entry (no entry move in its data)`);
    assert.ok(Object.keys(d.moves).some((k) => k.startsWith('CD.')), `${fid} still carries its CD rows (documented NO ENTRY)`);
  }
});

test('firing the declared entry latches cdActive; CD rows resolve only inside the window', () => {
  for (const [fid, entry] of Object.entries(CD_WIRED)) {
    load(fid);
    const b = new M.TekkenBuffer(fid);
    assert.equal(b.cdActive(), false, `${fid}: no CD before the entry fires`);
    b.recordExplicit(entry); // the path fighter.js uses when the entry move starts
    assert.equal(b.cdActive(), true, `${fid}: CD latched by its declared entry`);
    const cdRow = Object.keys(M.getFighterMoveset(fid).moves).find((k) => k.startsWith('CD.') && !k.includes(','));
    assert.ok(cdRow, `${fid} has a simple CD row to probe`);
    const btn = cdRow.slice(3);
    if (/^[0-9]\+[0-9]$/.test(btn)) {
      assert.equal(b.pressChord(btn, { crouchDash: true }), cdRow, `${fid}: ${cdRow} fires in the CD window`);
      assert.notEqual(new M.TekkenBuffer(fid).pressChord(btn, {}), cdRow, `${fid}: ${cdRow} does not fire from neutral`);
    } else if (/^[0-9]$/.test(btn)) {
      assert.equal(b.pressButton(btn, { crouchDash: true }), cdRow, `${fid}: ${cdRow} fires in the CD window`);
      assert.notEqual(new M.TekkenBuffer(fid).pressButton(btn, {}), cdRow, `${fid}: ${cdRow} does not fire from neutral`);
    }
  }
});

test('the cd_entry motion itself latches CD through noteDirection (the human input path)', () => {
  const motions = { rin: ['f', 'n', 'd', 'd/f'], demonio: ['f', 'n', 'd', 'd/f'], gyou: ['d', 'd/f'] };
  for (const [fid, seq] of Object.entries(motions)) {
    load(fid);
    const b = new M.TekkenBuffer(fid);
    for (const d of seq) b.noteDirection(d, 1 / 60);
    assert.equal(b.cdActive(), true, `${fid}: CD latched by its own motion ${seq.join(',')}`);
    const b2 = new M.TekkenBuffer(fid);
    b2.noteDirection('f', 1 / 60); b2.noteDirection('f', 1 / 60);
    assert.equal(b2.cdActive(), false, `${fid}: an unrelated double-tap does not latch CD`);
  }
  // a fighter with CD rows but no declared entry never latches
  load('pantera');
  const bp = new M.TekkenBuffer('pantera');
  for (const d of ['f', 'n', 'd', 'd/f']) bp.noteDirection(d, 1 / 60);
  assert.equal(bp.cdActive(), false, 'pantera: no cd_entry declared, no latch');
});

test('negativo: the side-specific row outranks the generic SS row for the same button', () => {
  load('negativo');
  // negativo carries BOTH a generic SS.2 and directional rows (slots 'SSL.2' / 'SSR.2',
  // moves keyed 'SSL 2' / 'SSR 2'). Mid-sidestep the side is always known from ssDir,
  // so the directional row must win; the generic row stays reachable when no side is known.
  assert.equal(new M.TekkenBuffer('negativo').pressButton('2', { sidestep: true, ssSide: 'SSL' }), 'SSL.2');
  assert.equal(new M.TekkenBuffer('negativo').pressButton('2', { sidestep: true, ssSide: 'SSR' }), 'SSR.2');
  assert.equal(new M.TekkenBuffer('negativo').pressButton('2', { sidestep: true }), 'SS.2');
});

test('SSL / SSR rows resolve under the directional sidestep context only', () => {
  for (const fid of ['purplerain', 'negativo']) {
    const d = load(fid);
    for (const side of ['SSL', 'SSR']) {
      const row = Object.keys(d.moves).find((k) => k.startsWith(side + '.') && !k.slice(4).includes(','));
      if (!row) continue;
      const btn = row.slice(4);
      const b = new M.TekkenBuffer(fid);
      if (/^[0-9]\+[0-9]$/.test(btn)) {
        assert.equal(b.pressChord(btn, { sidestep: true, ssSide: side }), row, `${fid}: ${row} fires stepping ${side}`);
        assert.notEqual(new M.TekkenBuffer(fid).pressChord(btn, { sidestep: true, ssSide: side === 'SSL' ? 'SSR' : 'SSL' }), row, `${fid}: ${row} does not fire stepping the other way`);
        assert.notEqual(new M.TekkenBuffer(fid).pressChord(btn, {}), row, `${fid}: ${row} does not fire from neutral`);
      } else if (/^[0-9]$/.test(btn)) {
        assert.equal(b.pressButton(btn, { sidestep: true, ssSide: side }), row, `${fid}: ${row} fires stepping ${side}`);
        assert.notEqual(new M.TekkenBuffer(fid).pressButton(btn, { sidestep: true, ssSide: side === 'SSL' ? 'SSR' : 'SSL' }), row, `${fid}: ${row} does not fire stepping the other way`);
        assert.notEqual(new M.TekkenBuffer(fid).pressButton(btn, {}), row, `${fid}: ${row} does not fire from neutral`);
      }
    }
  }
});
