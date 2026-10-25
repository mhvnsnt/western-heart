#!/usr/bin/env node
// Attack-animation audit (lane D, 2026-10-24). For every roster fighter with its own moveset, resolve
// every playable input slot exactly as a fight does (movesets.js resolveMove -> fighter.js getRealMove)
// and ask fighter.js which clip that move plays on the fighter's bound T3 bank (bankIdFor). Counts:
//   own      the move's own decoded T3 row (t3_row in the bound bank)
//   anim     its anim_t3 row (moveset-merge: same-notation, or 'nearest' = approximate)
//   notation a bank row this fighter's moveset binds to the same input (runtime, same rule as the merge)
//   match    the bank row matching the move's limb + height (+ nearest hit frame), closest real clip
//   generic  the bank's light/medium/heavy/grab clip
//   none     no clip: no bank bound (procedural _animAttack)
// Flags (decoded hit_frames.json throw flag, tools/anim/t3_hit_frames.py): s2t = a STRIKE plays a THROW row,
// t2s = a THROW (isGrab / throw level) plays a strike clip. Examples of both are listed per fighter.
// --legacy reproduces the pre-2026-10-24 selection (_moveRowAction || T3_ATTACK_MAP) for the before table.
// Usage: node tools/anim/attack_anim_audit.mjs [--legacy] [--json out.json] [--only id,id]
import { ROOT } from './node_game_env.mjs';
import { writeFileSync } from 'node:fs';
import { join } from 'node:path';

const args = process.argv.slice(2);
const LEGACY = args.includes('--legacy');
const jsonOut = args.includes('--json') ? args[args.indexOf('--json') + 1] : null;
const only = args.includes('--only') ? new Set(args[args.indexOf('--only') + 1].split(',')) : null;

const THREE = await import('three');
const M = await import(join(ROOT, 'game/js/movesets.js'));
const T = await import(join(ROOT, 'game/js/t3anims.js'));
const F = await import(join(ROOT, 'game/js/fighter.js'));
const { FULL_ROSTER } = await import(join(ROOT, 'game/js/roster-full.js'));
console.warn = () => {}; // loader chatter (missing optional files) is not audit output

await M.loadFighterMovesets();
const ids = FULL_ROSTER.map(c => c.id).filter(id => !only || only.has(id));
await M.ensureMovesets(ids);

function fakeAction(clip) {
  return { getClip: () => clip, timeScale: 1, time: 0, isRunning: () => false };
}
function fakeFighter(id, bank, clips) {
  const f = Object.create(F.Fighter.prototype);
  f.char = { id }; f._movesetId = id; f.isPlayer = true;
  f._t3 = bank && clips ? { bank, clips, model: null, modelKey: 'audit' } : null;
  const acts = {};
  f.t3actions = new Proxy(acts, {
    get: (o, n) => (typeof n === 'string' && clips && clips[n] ? (o[n] || (o[n] = fakeAction(clips[n]))) : o[n]),
    has: (o, n) => !!(clips && clips[n]),
  });
  return f;
}

// Pre-2026-10-24 code path, verbatim logic: fighter.js _moveRowAction (row) || attackClipFor (T3_ATTACK_MAP).
const T3_ATTACK_MAP = { punch: 'light', kick: 'medium', grab: 'grab', surge: 'heavy', heavy: 'heavy',
  '1': 'light', '2': 'light', '3': 'medium', '4': 'medium', '1+3': 'grab', '2+4': 'grab' };
function legacyPlan(f, move, name, clips) {
  if (f._t3 && move) {
    let row = move.t3row, ok = false, kind = 'own';
    if (row != null) {
      const srcBank = move.t3source ? T.SOURCE_TO_BANK[move.t3source] : f._t3.bank;
      ok = srcBank === f._t3.bank || (srcBank === 'king' && f._t3.bank === 'armorking');
    }
    if (!ok && move.animRow != null && (T.SOURCE_TO_BANK[move.animBank] || move.animBank) === f._t3.bank) { row = move.animRow; ok = true; kind = 'anim'; }
    if (ok && clips['row:' + row]) return { name: 'row:' + row, kind };
  }
  let n = T3_ATTACK_MAP[name];
  if (!n && typeof name === 'string') n = T3_ATTACK_MAP[name.split(',').pop().split('+').pop()] || 'heavy';
  return clips && clips[n] ? { name: n, kind: 'generic' } : { name: null, kind: 'none' };
}

// Why a move did not get its own row (from the move record + bank, independent of the code under test).
function whyNoRow(move, bank, clips) {
  if (!bank) return 'bank unresolved';
  if (!move) return 'slot resolves to no move';
  const has = r => !!(clips && clips['row:' + r]);
  const out = [];
  const last = r => (Array.isArray(r) ? r[r.length - 1] : r);
  if (move.t3row != null) {
    const sb = move.t3source ? (T.SOURCE_TO_BANK[move.t3source] ?? `?${move.t3source}`) : bank;
    if (sb !== bank && !(sb === 'king' && bank === 'armorking')) out.push(`t3_row of source '${move.t3source}' (bank ${sb}) != bound ${bank}`);
    else if (!has(last(move.t3row))) out.push(`t3_row ${last(move.t3row)} missing from ${bank} rows.pack`);
  }
  if (move.animRow != null) {
    const ab = T.SOURCE_TO_BANK[move.animBank] || move.animBank;
    if (ab !== bank) out.push(`anim_t3 bank '${move.animBank}' != bound ${bank}`);
    else if (!has(last(move.animRow))) out.push(`anim_t3 row ${last(move.animRow)} missing from ${bank} rows.pack`);
  }
  if (move.t3row == null && move.animRow == null) out.push('no t3_row / anim_t3');
  return out.join('; ');
}

const table = [], missing = {}, reasons = {}, flags = {};
for (const id of ids) {
  const ms = M.getFighterMoveset(id);
  if (!ms || !ms.moves) continue;
  // Playable inputs: the moveset's slots table (notation -> key); files without one fire their keys.
  const notations = Object.keys(ms.slots || ms.moves);
  const bank = F.bankIdFor(id, id);
  const clips = bank ? await T.loadT3Clips(THREE, bank) : null;
  const f = fakeFighter(id, bank, clips);
  const row = { id, bank: bank || '-', slots: 0, own: 0, anim: 0, animNearest: 0, notation: 0, match: 0, generic: 0, none: 0, distinct: 0, s2t: 0, t2s: 0 };
  const seen = new Set();
  for (const notation of notations) {
    const move = F.getRealMove(id, notation);
    row.slots++;
    let plan;
    if (LEGACY || typeof f._attackClipPlan !== 'function') plan = legacyPlan(f, move, notation, clips);
    else plan = f._attackClipPlan(move, notation) || { name: null, kind: 'none' };
    let k = plan.kind;
    const at = move && move.moveKey && ms.moves[move.moveKey] && ms.moves[move.moveKey].anim_t3;
    if (k === 'anim' && at && /nearest/.test(String(at.match || ''))) row.animNearest++;
    if (!(k in row)) k = 'generic';
    row[k]++;
    if (plan.name) seen.add(plan.name);
    if (plan.name && move) {
      const clipThrow = T.clipIsThrow(clips[plan.name]);
      const h = clips[plan.name].userData.hit;
      const clipStrike = !clipThrow && !!(h && h[0] > 0); // decoded attack row that is not a throw
      // Throw as the game treats it (isGrab / throw level / 1+3, 2+4), same test as _attackClipPlan.
      const rawMv = move.moveKey && ms.moves[move.moveKey];
      const moveThrow = !!move.isGrab || /^(1\+3|2\+4)$/.test(notation) || F.Fighter.attackLevel(move, rawMv) === 't';
      const tag = !moveThrow && clipThrow ? 's2t' : moveThrow && clipStrike ? 't2s' : null;
      if (tag) {
        row[tag]++;
        const ex = (flags[id] = flags[id] || { s2t: [], t2s: [] })[tag];
        if (ex.length < 6 || notation === '1' || notation === '2') ex.push(`${notation} '${move.moveName || move.moveKey}' -> ${plan.name} (${k})`);
      }
    }
    if (k === 'generic' || k === 'none') {
      const why = whyNoRow(move, bank, clips);
      const rk = `${bank || '-'} | ${why.replace(/(?<![a-z])\d+/g, 'N')}`;
      reasons[rk] = (reasons[rk] || 0) + 1;
    }
    if (bank && move) {
      const last = r => (Array.isArray(r) ? r[r.length - 1] : r);
      for (const [r, b] of [[last(move.t3row), move.t3source ? T.SOURCE_TO_BANK[move.t3source] : bank], [last(move.animRow), T.SOURCE_TO_BANK[move.animBank] || move.animBank]]) {
        if (r != null && b === bank && !(clips && clips['row:' + r])) {
          const bucket = (missing[b] = missing[b] || {});
          (bucket[r] = bucket[r] || new Set()).add(id);
        }
      }
    }
  }
  row.distinct = seen.size;
  table.push(row);
}

const cols = ['id', 'bank', 'slots', 'own', 'anim', 'animNearest', 'notation', 'match', 'generic', 'none', 'distinct', 's2t', 't2s'];
console.log(`# attack clip selection (${LEGACY ? 'legacy, pre-2026-10-24' : 'current fighter.js'})`);
console.log(cols.join('\t'));
for (const r of table) console.log(cols.map(c => r[c]).join('\t'));
const tot = Object.fromEntries(cols.slice(2).map(c => [c, table.reduce((s, r) => s + r[c], 0)]));
console.log(['TOTAL', '', ...cols.slice(2).map(c => tot[c])].join('\t'));
console.log('\n# strike<->throw clip mismatches (examples)');
for (const [id, f] of Object.entries(flags)) {
  if (f.s2t.length) console.log(`${id} STRIKE->THROW: ${f.s2t.slice(0, 6).join(' | ')}`);
  if (f.t2s.length) console.log(`${id} THROW->STRIKE: ${f.t2s.slice(0, 4).join(' | ')}`);
}
console.log('\n# why no own row (bank | reason: slots)');
for (const [k, v] of Object.entries(reasons).sort((a, b) => b[1] - a[1]).slice(0, 40)) console.log(`${v}\t${k}`);
console.log('\n# referenced rows missing from rows.pack.json (bank: count [rows])');
const missOut = {};
for (const [b, rows] of Object.entries(missing)) {
  const rs = Object.keys(rows).map(Number).sort((a, c) => a - c);
  missOut[b] = Object.fromEntries(rs.map(r => [r, [...rows[r]].sort()]));
  console.log(`${b}: ${rs.length} [${rs.join(',')}]`);
}
if (jsonOut) writeFileSync(jsonOut, JSON.stringify({ legacy: LEGACY, table, total: tot, reasons, missing: missOut, flags }, null, 1));
