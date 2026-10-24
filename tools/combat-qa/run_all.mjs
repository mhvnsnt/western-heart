// Combat QA Orchestrator — runs all audits and produces a unified report.
//
// Run: node tools/combat-qa/run_all.mjs [--report out.json]
//
// This is the autonomous combat testing system. It catches:
// - "buttons do random moves" (input audit)
// - "combos don't work" (combo audit)
// - "grapple animations don't play" (anim audit)
// - "hits don't connect" (hit audit)
import { spawnSync } from 'child_process';
import { writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const here = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const reportPath = args.includes('--report') ? args[args.indexOf('--report') + 1] : null;

console.log('=== COMBAT QA — AUTONOMOUS TESTING ===\n');

const audits = [
  { name: 'Input Audit', script: 'input_audit.mjs', desc: 'every input fires the exact move' },
  { name: 'Combo Audit', script: 'combo_audit.mjs', desc: 'strings execute with Tekken timing' },
  { name: 'Animation Audit', script: 'anim_audit.mjs', desc: 'anim_refs resolve, throws have victim anims' },
  { name: 'Hit Audit', script: 'hit_audit.mjs', desc: 'attacks connect at proper range' },
];

const results = {
  timestamp: new Date().toISOString(),
  audits: {}
};

let anyFail = false;

for (const audit of audits) {
  console.log(`\n--- ${audit.name} ---`);
  console.log(`(${audit.desc})\n`);

  const r = spawnSync('node', [join(here, audit.script)], {
    stdio: 'inherit',
    cwd: join(here, '..', '..')
  });

  const passed = r.status === 0;
  results.audits[audit.name] = { passed, exitCode: r.status };
  if (!passed) anyFail = true;

  console.log(`\n${audit.name}: ${passed ? 'PASS' : 'FAIL'}`);
}

console.log('\n\n=== COMBAT QA SUMMARY ===');
for (const [name, r] of Object.entries(results.audits)) {
  console.log(`  ${name}: ${r.passed ? 'PASS' : 'FAIL'}`);
}
console.log(`\nOverall: ${anyFail ? 'ISSUES FOUND — see above' : 'ALL CLEAR'}`);

if (reportPath) {
  writeFileSync(reportPath, JSON.stringify(results, null, 2));
  console.log(`\nSummary written to ${reportPath}`);
}

process.exit(anyFail ? 1 : 0);
