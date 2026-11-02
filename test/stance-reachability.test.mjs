// Stance / state-prefixed moves that could never fire (owner 2026-11-01: "you said many of the moves need a state or
// stance prefix to fire then set that up set all that up with all the moves"). tools/input-verify/
// stance_reachability_audit.mjs found 2,237 of 5,577 prefixed inputs with no way in; the universal fixes here take it
// to 1,952 (docs/movesets/STANCE-REACHABILITY-AUDIT-2026-11-01.md). Node, through the game's own TekkenBuffer.
// Run: node --test test/stance-reachability.test.mjs
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
const keysOf = (d) => Object.keys(d.slots || d.moves || {});

test("side / back throws keyed SIDE_L / SIDE_R / BACK fire at the foe's side / back (same as FLANK_*)", () => {
  assert.deepEqual([...M.FLANK_KEYS.L], ['FLANK_L.', 'SIDE_L.']);
  let checked = 0;
  for (const f of fs.readdirSync(MS).filter((n) => n.endsWith('.json'))) {
    const fid = f.replace(/\.json$/, '');
    let d; try { d = load(fid); } catch { continue; }
    for (const [flank, pre] of [['L', 'SIDE_L.'], ['R', 'SIDE_R.'], ['B', 'BACK.']]) {
      for (const chord of ['1+3', '2+4']) {
        if (!keysOf(d).includes(pre + chord)) continue;
        const r = new M.TekkenBuffer(fid).pressChord(chord, { foeFlank: flank });
        // where the moveset also has the FLANK_ spelling of a side / back throw (canonNotation of the T7 rows), that one
        // wins (unchanged); otherwise the SIDE_ / BACK row itself must fire now
        const flankForm = M.resolveMoveKey(fid, `FLANK_${flank}.1+3`) || M.resolveMoveKey(fid, `FLANK_${flank}.2+4`);
        assert.ok(r && (flankForm ? r.startsWith(`FLANK_${flank}.`) : r.startsWith(pre)), `${fid}: ${chord} at flank ${flank} -> ${r}`);
        checked++;
      }
    }
  }
  assert.ok(checked >= 20, `${checked} side / back throws checked`);
  // and some fighters reach a side / back throw ONLY through the new spelling
  let onlyNew = 0;
  for (const f of fs.readdirSync(MS).filter((n) => n.endsWith('.json'))) {
    const fid = f.replace(/\.json$/, ''); let d; try { d = load(fid); } catch { continue; }
    for (const [flank, pre] of [['L', 'SIDE_L.'], ['R', 'SIDE_R.'], ['B', 'BACK.']]) {
      if (!keysOf(d).some((k) => k === pre + '1+3' || k === pre + '2+4')) continue;
      if (M.resolveMoveKey(fid, `FLANK_${flank}.1+3`) || M.resolveMoveKey(fid, `FLANK_${flank}.2+4`)) continue;
      onlyNew++;
    }
  }
  assert.ok(onlyNew >= 1, `${onlyNew} side / back throw situations reachable only through SIDE_ / BACK`);
});

test('heat moves (H.) fire while Soul Urge is on, and only then', () => {
  let checked = 0;
  for (const f of fs.readdirSync(MS).filter((n) => n.endsWith('.json'))) {
    const fid = f.replace(/\.json$/, '');
    let d; try { d = load(fid); } catch { continue; }
    const k = keysOf(d).find((x) => /^H\.[1-4](\+[1-4])*$/.test(x) && x !== 'H.2+3');
    if (!k) continue;
    const input = k.slice(2);
    const on = input.includes('+') ? new M.TekkenBuffer(fid).pressChord(input, { urgeOn: true }) : new M.TekkenBuffer(fid).pressButton(input, { urgeOn: true });
    assert.equal(on, k, `${fid}: ${input} with Soul Urge on -> ${on}`);
    const off = input.includes('+') ? new M.TekkenBuffer(fid).pressChord(input, {}) : new M.TekkenBuffer(fid).pressButton(input, {});
    assert.notEqual(off, k, `${fid}: ${input} without Soul Urge must not be the heat move`);
    checked++;
  }
  assert.ok(checked >= 5, `${checked} heat moves checked`);
});

test('a tackle throw opens the TACKLE. follow-ups', () => {
  const f = fs.readFileSync(join(ROOT, 'game/js/fighter.js'), 'utf8');
  assert.match(f, /if \(!keys\.length && cur && \/tackle\/i\.test\(cur\.name \|\| ''\)\) \{ const tk = throwStageKeys\(this\._movesetId, 'TACKLE'\)/);
  // at least one fighter has both a tackle throw and TACKLE. rows, so the path is live
  let live = 0;
  for (const n of fs.readdirSync(MS).filter((x) => x.endsWith('.json'))) {
    let d; try { d = JSON.parse(fs.readFileSync(join(MS, n), 'utf8')); } catch { continue; }
    const mv = d.moves || {};
    const tackle = Object.values(mv).some((m) => m && /tackle/i.test(m.name || '') && (m.isGrab || m.move_class === 'throw'));
    if (tackle && Object.keys(mv).some((k) => k.startsWith('TACKLE.'))) live++;
  }
  assert.ok(live >= 5, `${live} fighters with a tackle throw and TACKLE. follow-ups`);
});

test('a move whose frame data says "(BT)" leaves the fighter back-turned, so BT. moves can fire after it', async () => {
  const F = await import(join(ROOT, 'game/js/fighter.js'));
  let checked = 0;
  for (const fid of ['t3-lei', 'skull', 'retsu', 'demonio', 'pantera', 'nightwolf']) {
    const d = load(fid);
    const mv = d.moves || {};
    const sa = d.stance_after || {};
    const keys = Object.keys(mv).filter((k) => !k.startsWith('BT.') && !sa[k] && /\(BT\)/.test(JSON.stringify([mv[k].on_block, mv[k].on_hit, mv[k].on_ch, mv[k].t7_on_block, mv[k].t7_on_hit, mv[k].t7_on_ch, (mv[k].t7 || {}).on_block, (mv[k].t7 || {}).on_hit, (mv[k].t7 || {}).on_ch])));
    if (!keys.length) continue;
    const m = F.getRealMove(fid, keys[0]);
    assert.ok(m, `${fid}: ${keys[0]} resolves`);
    assert.equal(m.stanceAfter, 'BT', `${fid}: ${keys[0]} ends back-turned`);
    checked++;
  }
  assert.ok(checked >= 4, `${checked} fighters checked`);
});
