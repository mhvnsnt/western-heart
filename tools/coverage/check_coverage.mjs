// coverage-guard: fails if a coverage row is removed, its status regresses, a
// 'wired' row lacks existing code+test, or SYSTEMS-COVERAGE.md is stale.
// Usage: node tools/coverage/check_coverage.mjs [base.json]
import fs from 'node:fs';
import { execSync } from 'node:child_process';
const TRACKED = new Set(execSync('git ls-tree -r --name-only HEAD', { maxBuffer: 1 << 30 }).toString().split('\n'));
const exists = p => TRACKED.has(p) || [...TRACKED].some(t => t.startsWith(p + '/')) || fs.existsSync(p);
const RANK = { 'not-wired': 0, partial: 1, wired: 2 };
const cur = JSON.parse(fs.readFileSync('tools/coverage/systems-coverage.json', 'utf8')).rows;
const errs = [];
for (const r of cur) {
  if (!(r.status in RANK)) errs.push(`${r.id}: bad status ${r.status}`);
  if (r.status === 'wired') {
    if (!r.code || !r.test) errs.push(`${r.id}: wired needs code + test`);
    for (const p of [r.code, r.test]) if (p && !exists(p)) errs.push(`${r.id}: missing ${p}`);
  }
}
const base = process.argv[2];
if (base && fs.existsSync(base)) {
  const b = JSON.parse(fs.readFileSync(base, 'utf8')).rows;
  const m = new Map(cur.map(r => [r.id, r]));
  for (const r of b) {
    const c = m.get(r.id);
    if (!c) errs.push(`${r.id}: row removed`);
    else if (RANK[c.status] < RANK[r.status]) errs.push(`${r.id}: regressed ${r.status} -> ${c.status}`);
  }
}
const md = fs.existsSync('docs/tech/SYSTEMS-COVERAGE.md') ? fs.readFileSync('docs/tech/SYSTEMS-COVERAGE.md', 'utf8') : '';
for (const r of cur) if (!md.includes(`\`${r.id}\``)) errs.push(`${r.id}: not in SYSTEMS-COVERAGE.md`);
const n = s => cur.filter(r => r.status === s).length;
console.log(`coverage: ${cur.length} rows — wired ${n('wired')}, partial ${n('partial')}, not-wired ${n('not-wired')}`);
if (errs.length) { console.error(errs.join('\n')); process.exit(1); }
