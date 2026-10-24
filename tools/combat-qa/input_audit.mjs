// Input Audit — verifies every fighter's every move fires from its exact Tekken input.
// Uses the same API as test/input-determinism.test.mjs: TekkenBuffer + resolveMoveKey.
//
// Run: node tools/combat-qa/input_audit.mjs [--report out.json] [--fighter NAME]
import { readFileSync, readdirSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..', '..');

const _ls = {};
globalThis.localStorage = {
  getItem: k => _ls[k] ?? null,
  setItem: (k, v) => { _ls[k] = String(v); },
  removeItem: k => { delete _ls[k]; }
};
globalThis.WH_INPUT_RESOLVER = 'v2';

const args = process.argv.slice(2);
const reportPath = args.includes('--report') ? args[args.indexOf('--report') + 1] : null;
const fighterFilter = args.includes('--fighter') ? args[args.indexOf('--fighter') + 1] : null;

const M = await import(join(root, 'game', 'js', 'movesets.js'));
const msDir = join(root, 'game', 'assets', 'movesets');
try {
  M.setInputTables(JSON.parse(readFileSync(join(msDir, 't3_input_tables.json'), 'utf8')));
} catch (e) {}

const BTN = /^[1-4](?:\+[1-4])*$/;

function feed(buf, dir, frames = 4) {
  for (let i = 0; i < frames; i++) buf.noteDirection(dir);
}
function fire(buf, btn, ctx) {
  return BTN.test(btn) && btn.includes('+') ? buf.pressChord(btn, ctx) : buf.press(btn, ctx);
}

function plan(n) {
  const { prefix, body } = M.splitNotation(n);
  let ctx = {};
  if (prefix) {
    const ps = prefix.split('.').filter(Boolean);
    if (ps.length !== 1) return null;
    const CTX = {
      'FC': { crouching: true }, 'WS': { rising: true },
      'SS': { sidestep: true }, 'BT': { backturned: true }, 'R': { rage: true }
    };
    ctx = CTX[ps[0]] ? { ...CTX[ps[0]] } : { stance: ps[0] };
  }
  const b = body.replace(/\*$/, '');
  if (/\*$/.test(body)) return { kind: 'button-hold', ctx, run: null };
  if (BTN.test(b)) return { kind: 'button', ctx, run: buf => { feed(buf, 'n'); return fire(buf, b, ctx); } };
  const dm = /^(d\/f|d\/b|u\/f|u\/b|f|b|u|d|D\/F|D\/B|U\/F|U\/B|F|B|U|D)\+([1-4](?:\+[1-4])*)$/.exec(b);
  if (dm) {
    const d = dm[1].toLowerCase();
    const hold = dm[1] !== d;
    return { kind: hold ? 'direction-held' : 'direction', ctx, run: buf => { feed(buf, 'n'); feed(buf, d, hold ? 12 : 2); return fire(buf, dm[2], ctx); } };
  }
  const toks = b.split(/[,~:]/);
  const TOK = /^(?:(d\/f|d\/b|u\/f|u\/b|f|b|u|d|D\/F|D\/B|U\/F|U\/B|F|B|U|D)\+)?([1-4](?:\+[1-4])*)$/;
  if (toks.length >= 2 && toks.every(t => TOK.test(t))) return {
    kind: 'string', ctx, run: buf => {
      let got = null;
      toks.forEach((t, i) => {
        const mt = TOK.exec(t);
        const d = mt[1], btn = mt[2];
        feed(buf, 'n'); if (d) feed(buf, d.toLowerCase(), d === d.toLowerCase() ? 2 : 12);
        got = fire(buf, btn, i === 0 ? ctx : { ...ctx, inMove: true });
      });
      return got;
    }
  };
  const mo = M.parseMotion(n);
  if (mo) return {
    kind: 'motion', ctx, run: buf => {
      feed(buf, 'n', 30);
      mo.dirs.forEach((d, i) => { feed(buf, d, 2); if (mo.dirs[i + 1] === d) feed(buf, 'n', 2); });
      if (mo.neutral) feed(buf, 'n', 2);
      return fire(buf, mo.btn, ctx);
    }
  };
  return null;
}

const results = {
  timestamp: new Date().toISOString(),
  fighters: {},
  summary: { total: 0, pass: 0, fail: 0, skipped: 0, failures: [] }
};

const files = readdirSync(msDir).filter(f => f.endsWith('.json') && !/^(index|t3_input_tables)/.test(f));

for (const f of files) {
  let data;
  try { data = JSON.parse(readFileSync(join(msDir, f), 'utf8')); } catch (e) { continue; }
  if (!data || !data.moves) continue;

  const id = data.fighter || f.replace(/\.json$/, '');
  if (fighterFilter && id !== fighterFilter) continue;

  M.registerMoveset(id, data);
  const slots = Object.assign({}, data.slots || {});
  for (const k of Object.keys(data.moves)) if (!(k in slots)) slots[k] = k;

  const fr = { tested: 0, pass: 0, fail: 0, skipped: 0, failures: [] };

  for (const n of Object.keys(slots)) {
    if (n.includes('~') || !data.moves[slots[n]]) { fr.skipped++; continue; }
    const p = plan(n);
    if (!p || !p.run) { fr.skipped++; continue; }

    const buf = new M.TekkenBuffer(id);
    let got;
    try {
      got = p.run(buf);
    } catch (e) {
      fr.fail++; results.summary.fail++;
      fr.failures.push({ fighter: id, input: n, error: e.message.slice(0, 100), kind: p.kind });
      continue;
    }

    const want = M.resolveMoveKey(id, n);
    const gotKey = got ? M.resolveMoveKey(id, got) : null;
    fr.tested++; results.summary.total++;

    const same = (a, b) => a && b && (a === b || (
      data.moves[a] && data.moves[b] &&
      data.moves[a].name === data.moves[b].name &&
      data.moves[a].startup === data.moves[b].startup
    ));

    if (got === n || same(gotKey, want)) {
      fr.pass++; results.summary.pass++;
    } else {
      fr.fail++; results.summary.fail++;
      const failure = {
        fighter: id, input: n, kind: p.kind,
        expected: want, expectedName: want && data.moves[want] ? data.moves[want].name : null,
        got, gotName: gotKey && data.moves[gotKey] ? data.moves[gotKey].name : null
      };
      fr.failures.push(failure);
      results.summary.failures.push(failure);
    }
  }

  // Neutral button check: 1/2/3/4 must fire ONLY the neutral move (or nothing)
  fr.neutral = {};
  for (const b of ['1', '2', '3', '4']) {
    const buf = new M.TekkenBuffer(id);
    feed(buf, 'n', 10);
    const got = buf.press(b, {});
    const slot = M.resolveMoveKey(id, b);
    const ok = slot ? (got === b || (got && M.resolveMoveKey(id, got) === slot)) : got === null;
    fr.neutral[b] = { fired: got, ok: !!ok };
    if (!ok) {
      fr.fail++; results.summary.fail++;
      results.summary.failures.push({
        fighter: id, input: `neutral ${b}`, kind: 'neutral',
        expected: slot, got
      });
    }
  }

  results.fighters[id] = fr;
  if (fr.fail > 0) {
    console.log(`${id}: ${fr.pass}/${fr.tested} pass, ${fr.fail} FAIL`);
    for (const fail of fr.failures.slice(0, 3)) {
      console.log(`    ${fail.input} -> got ${fail.got} (${fail.gotName || '?'}) expected ${fail.expected} (${fail.expectedName || '?'})`);
    }
  }
}

console.log(`\n=== INPUT AUDIT COMPLETE ===`);
console.log(`Total: ${results.summary.total}, Pass: ${results.summary.pass}, Fail: ${results.summary.fail}, Skipped: ${results.summary.skipped}`);

if (reportPath) {
  writeFileSync(reportPath, JSON.stringify(results, null, 2));
  console.log(`Report: ${reportPath}`);
}

process.exit(results.summary.fail > 0 ? 1 : 0);
