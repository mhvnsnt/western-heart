// t214u: the select-screen visual audit (tools/select-audit: headless capture
// at 390x844 + skinned-mesh probe) must show no T-pose/bind pose, no
// duplicate pose and no deformation outliers. Gate reads the committed
// tools/select-audit/AUDIT-STATUS.json (re-run run_all.sh + analyze.py to
// refresh). A failing fighter passes only while listed in
// AUDIT-BLOCKERS.json with the flag kinds it still has; a fixed fighter left
// listed fails too, so the list can only shrink.
import fs from 'node:fs';
const S = JSON.parse(fs.readFileSync(new URL('../tools/select-audit/AUDIT-STATUS.json', import.meta.url)));
const B = JSON.parse(fs.readFileSync(new URL('../tools/select-audit/AUDIT-BLOCKERS.json', import.meta.url))).blocked;
const kind = (f) => f.split(/[ :(]/)[0];
const fails = [];
for (const r of S) {
  const kinds = [...new Set((r._flags || []).map(kind))];
  const allowed = new Set(B[r.id] || []);
  for (const k of kinds) if (!allowed.has(k)) fails.push(`${r.id}: ${k} (not in AUDIT-BLOCKERS)`);
  for (const k of allowed) if (!kinds.includes(k)) fails.push(`${r.id}: ${k} fixed — remove it from AUDIT-BLOCKERS.json`);
}
for (const id of Object.keys(B)) if (!S.find(r => r.id === id)) fails.push(`${id}: blocker for a fighter not in the audit`);
if (fails.length) { console.error('FAIL select-audit:\n  ' + fails.join('\n  ')); process.exit(1); }
console.log(`ok select-audit: ${S.length} fighters, ${Object.keys(B).length} listed blockers`);
