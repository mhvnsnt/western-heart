// Frame-by-frame Tekken input scripts (owner t231u: "random attacks, can't combo").
// Run: node test/input-frame-scripts.test.mjs [--movesets-js path] [--report out.json]
// Each script is a list of 60 Hz frames: {d: stick dir, b: button/chord pressed this frame,
// ctx}. Asserts the exact notation that fires. Also: roster-wide reachability of every slot
// notation (incl. tap-release b,1 / f,n,2 / u/f,n,1 forms) and 0 random outputs.
import { readFileSync, readdirSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join, resolve } from 'path';
const here = dirname(fileURLToPath(import.meta.url)); const root = join(here, '..');
const _ls = {}; globalThis.localStorage = { getItem: k => _ls[k] ?? null, setItem: (k, v) => { _ls[k] = String(v); }, removeItem: k => { delete _ls[k]; } };
const args = process.argv.slice(2);
const msJs = args.includes('--movesets-js') ? resolve(args[args.indexOf('--movesets-js') + 1]) : join(root, 'game/js/movesets.js');
const M = await import(msJs);
const msDir = join(root, 'game/assets/movesets');
try { M.setInputTables(JSON.parse(readFileSync(join(msDir, 't3_input_tables.json'), 'utf8'))); } catch (e) {}
// deterministic clock: one 60 Hz frame = 16.667 ms
let clock = 0; globalThis.performance = { now: () => clock };
const ids = readdirSync(msDir).filter(f => f.endsWith('.json') && !/index|input_tables|^_/.test(f)).map(f => f.replace(/\.json$/, ''));
for (const id of ids) { try { const d = JSON.parse(readFileSync(join(msDir, id + '.json'), 'utf8')); if (d && d.moves) M.registerMoveset(id, d); } catch (e) {} }

function run(fid, frames) {
  const buf = new M.TekkenBuffer(fid); const out = [];
  for (const fr of frames) {
    clock += 1000 / 60;
    buf.noteDirection(fr.d || 'n');
    if (fr.b) { const ctx = fr.ctx || {}; out.push(fr.b.includes('+') ? buf.pressChord(fr.b, ctx) : buf.press(fr.b, ctx)); }
  }
  return out;
}
const F = (d, n = 1, b) => Array.from({ length: n }, (_, i) => ({ d, b: i === n - 1 ? b : undefined }));
const S = (...a) => a.flat();

const has = (fid, n) => !!M.resolveMoveKey(fid, n);
const pick = (n) => ids.find(id => has(id, n));
const cases = [];
const add = (name, fid, frames, want) => { if (fid) cases.push({ name, fid, frames, want }); };
// Known misses (t231u brief)
add('b,1 tap-release (not b+1)', pick('b,1'), S(F('n', 10), F('b', 3), F('n', 2, '1')), 'b,1');
add('b+1 held stays b+1', ids.find(i => has(i, 'b,1') && has(i, 'b+1')), S(F('n', 10), F('b', 4, '1')), 'b+1');
add('f,n,2', pick('f,n,2'), S(F('n', 10), F('f', 3), F('n', 2, '2')), 'f,n,2');
add('u/f,n,1', pick('u/f,n,1'), S(F('n', 10), F('u/f', 3), F('n', 2, '1')), 'u/f,n,1');
add('WS.4 after 10f crouch release', pick('WS.4'), S(F('n', 5), F('d', 12), F('n', 3, '4')), 'WS.4');
add('qcf+2 at 60Hz', pick('qcf+2'), S(F('n', 10), F('d', 2), F('d/f', 2), F('f', 1, '2')), 'qcf+2');
add('f,F+2 dash', pick('f,F+2'), S(F('n', 10), F('f', 2), F('n', 2), F('f', 2, '2')), 'f,F+2');
add('neutral 1 is the jab', pick('1'), S(F('n', 30, '1')), '1');
add('1+3 chord', pick('1+3'), S(F('n', 30, '1+3')), '1+3');
// Strings
for (const s of ['1,2', '1,1,2', '2,1', 'd/f+1,2', 'b+1,2']) {
  const fid = pick(s); if (!fid) continue;
  const toks = s.split(','); let fr = F('n', 10), wantSeq = [];
  toks.forEach((t, i) => { const m = /^(.*)\+(\d)$/.exec(t); const d = m && isNaN(+m[1]) ? m[1] : 'n'; const b = m && isNaN(+m[1]) ? m[2] : t;
    fr = fr.concat(F(d, 3, b).map(x => x.b ? { ...x, ctx: i ? { inMove: true } : {} } : x), F('n', 8)); });
  cases.push({ name: 'string ' + s, fid, frames: fr, want: s, last: true });
}
let fail = 0; const results = [];
for (const c of cases) {
  const out = run(c.fid, c.frames).filter(x => x !== null && x !== undefined);
  const got = out[out.length - 1] ?? null;
  const ok = got === c.want; if (!ok) fail++;
  results.push({ case: c.name, fighter: c.fid, want: c.want, got, ok });
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${c.name.padEnd(30)} ${c.fid.padEnd(14)} want ${c.want} got ${got}`);
}
// Determinism: same script twice = same output (no random picks)
let nondet = 0;
for (const c of cases) if (JSON.stringify(run(c.fid, c.frames)) !== JSON.stringify(run(c.fid, c.frames))) nondet++;
// Reachability: every slot notation that is a single input (button / dir+button / motion / tap-release / stance)
const CTX = { 'FC.': { crouching: true }, 'WS.': { rising: true }, 'SS.': { sidestep: true }, 'BT.': { backturned: true }, 'R.': { rage: true } };
let tot = 0, reach = 0; const miss = {};
for (const fid of ids) {
  const ms = M.getFighterMoveset(fid); if (!ms) continue;
  const slots = Object.assign({}, ms.slots || {}); for (const k of Object.keys(ms.moves)) if (!(k in slots)) slots[k] = k;
  for (const n of Object.keys(slots)) {
    if (/[,~:].*[1-4]/.test(M.splitNotation(n).body.replace(/^[^,~:]*?[1-4](?:\+[1-4])*\*?(?=[,~:])/, 'X'))) {} // strings counted below
    const { prefix, body } = M.splitNotation(n);
    const ps = prefix.split('.').filter(Boolean); if (ps.length > 1) continue;
    const ctx = ps.length ? (CTX[ps[0] + '.'] ? { ...CTX[ps[0] + '.'] } : { stance: ps[0] }) : {};
    const b = body.replace(/\*$/, '');
    let frames = null;
    const dm = /^(d\/f|d\/b|u\/f|u\/b|f|b|u|d|D\/F|D\/B|U\/F|U\/B|F|B|U|D)\+([1-4](?:\+[1-4])*)$/.exec(b);
    if (/^[1-4](?:\+[1-4])*$/.test(b)) frames = S(F('n', 20, b));
    else if (dm) frames = S(F('n', 20), F(dm[1].toLowerCase(), dm[1] === dm[1].toLowerCase() ? 2 : 12, dm[2]));
    else { const mo = M.parseMotion(n); if (mo) {
      frames = F('n', 30);
      mo.dirs.forEach((d, i) => { frames = frames.concat(F(d, 2)); if (mo.dirs[i + 1] === d) frames = frames.concat(F('n', 2)); });
      if (!mo.neutral && /[A-Z]/.test(n.split(',').pop().split('+')[0])) frames = frames.concat(F(mo.dirs[mo.dirs.length - 1], 2));
      frames = frames.concat(F(mo.neutral ? 'n' : mo.dirs[mo.dirs.length - 1], 1, mo.btn));
    } }
    if (!frames) continue; // strings: covered by input-determinism.test.mjs
    tot++;
    frames = frames.map(f => f.b ? { ...f, ctx } : f);
    const got = run(fid, frames).pop();
    const same = got === n || (got && M.resolveMoveKey(fid, got) === M.resolveMoveKey(fid, n));
    if (same) reach++; else (miss[fid] = miss[fid] || []).push(`${n}->${got}`);
  }
}
const pct = (100 * reach / tot).toFixed(2);
console.log(`reachability ${reach}/${tot} = ${pct}%   scripted fails ${fail}/${cases.length}   nondeterministic ${nondet}`);
if (args.includes('--report')) writeFileSync(args[args.indexOf('--report') + 1], JSON.stringify({ reach, tot, pct: +pct, fail, cases: results, nondet, miss }, null, 1));
if (fail || nondet || +pct < 98) { console.log('FAIL input frame scripts'); process.exit(1); }
console.log('PASS input frame scripts');
