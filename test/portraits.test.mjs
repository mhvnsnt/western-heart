// t133u: select portraits must exist, come from the fighter's ATTIRE-1 model
// (attires.js ladder, owner's own models first) and be posed in the fighter's
// own moveset-bank stance (not bind/T-pose). Data: game/assets/portraits/
// portraits-manifest.json, written by tools/portraits/capture.mjs.
// A fighter whose bank stance is rejected by the select fit gates may only
// pass while listed in tools/portraits/POSE-BLOCKERS.json (visible debt; the
// list must shrink, a fixed fighter left on it fails too).
import fs from 'node:fs';
import { FULL_ROSTER } from '../game/js/roster-full.js';
import { attiresFor } from '../game/js/attires.js';
const DIR = new URL('../game/assets/portraits/', import.meta.url);
const man = JSON.parse(fs.readFileSync(new URL('portraits-manifest.json', DIR))).fighters;
const blockers = JSON.parse(fs.readFileSync(new URL('../tools/portraits/POSE-BLOCKERS.json', import.meta.url))).blocked;
const src = fs.readFileSync(new URL('../game/js/select-screen.js', import.meta.url), 'utf8');
const hidden = new Set([...src.match(/SELECT_HIDDEN = new Set\(\[([^\]]*)\]/)[1].matchAll(/'([^']+)'/g)].map(m => m[1]));
const fails = []; let n = 0;
for (const c of FULL_ROSTER) {
  if (hidden.has(c.id)) continue;
  n++;
  const want = attiresFor(c)[0].model, m = man[c.id];
  if (!fs.existsSync(new URL(`${c.id}.png`, DIR))) fails.push(`${c.id}: portrait png missing`);
  if (!m) { fails.push(`${c.id}: not in portraits-manifest (run tools/portraits/capture.mjs)`); continue; }
  if (m.error) fails.push(`${c.id}: capture error ${m.error}`);
  if (m.model !== want) fails.push(`${c.id}: portrait rendered from '${m.model}', attire-1 model is '${want}' (wrong model)`);
  if (!m.stance && !blockers[c.id]) fails.push(`${c.id}: portrait is bind/T-posed (bank '${m.bank}' stance not applied) and not listed in POSE-BLOCKERS.json`);
  if (m.stance && blockers[c.id]) fails.push(`${c.id}: stance now works - remove it from POSE-BLOCKERS.json`);
}
for (const id of Object.keys(blockers)) if (!FULL_ROSTER.some(c => c.id === id) || hidden.has(id)) fails.push(`POSE-BLOCKERS lists '${id}', not a select fighter`);
console.log(`portraits: ${n} select fighters, ${Object.keys(blockers).length} pose blockers`);
if (fails.length) { console.error('FAIL\n  ' + fails.join('\n  ')); process.exit(1); }
console.log('PASS');
