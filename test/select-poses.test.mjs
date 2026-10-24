// t199u/t214u: every select fighter has its own pose (no shared clip, no
// shared CMU window), Pantera (king/stance) and Buffalo Bill (cmu#0) are
// owner-locked, and every pose file exists in its bank.
import fs from 'node:fs';
const d = JSON.parse(fs.readFileSync(new URL('../game/data/select-poses.json', import.meta.url)));
const fails = []; const seen = new Map();
for (const [id, p] of Object.entries(d.poses)) {
  const key = p.bank ? `${p.bank}/${p.clip}` : p.clip;
  if (seen.has(key)) fails.push(`${id} shares pose ${key} with ${seen.get(key)}`);
  seen.set(key, id);
  if (p.bank && !p.file) fails.push(`${id}: bank pose without file`);
}
const lock = (id, k) => { const p = d.poses[id]; const key = p && (p.bank ? `${p.bank}/${p.clip}` : p.clip); if (key !== k) fails.push(`${id} LOCKED pose must be ${k}, got ${key}`); };
lock('pantera', 'king/stance'); lock('buffalo-bill', 'cmu#0');
if (fails.length) { console.error('FAIL select-poses:\n  ' + fails.join('\n  ')); process.exit(1); }
console.log(`ok select-poses: ${seen.size} unique poses, locks held`);
