import { readFileSync, existsSync } from 'fs';
import { resolve, dirname } from 'path';
const GAME = '/home/hatch/workspace/fix3/loadspeed/game';
const seen = new Set();
function visit(f) {
  if (seen.has(f)) return; seen.add(f);
  let src; try { src = readFileSync(f, 'utf8'); } catch { return; }
  const dir = dirname(f);
  for (const m of src.matchAll(/(?:from|import)\s*['"]([^'"]+)['"]/g)) {
    let p = m[1];
    if (p === 'three') p = GAME + '/vendor/three.module.js';
    else if (p.startsWith('three/addons/')) p = GAME + '/vendor/addons/' + p.slice('three/addons/'.length);
    else if (!p.startsWith('.')) continue;
    else p = resolve(dir, p);
    if (!p.endsWith('.js')) p += '.js';
    if (existsSync(p) && p.startsWith(GAME)) visit(p);
  }
}
visit(GAME + '/js/main.js');
const files = [...seen].map(f => f.slice(GAME.length + 1)).sort();
let total = 0;
for (const f of files) { const s = readFileSync(GAME + '/' + f).length; total += s; console.log(String(s).padStart(9), f); }
console.log('TOTAL JS bytes:', total, 'files:', files.length);
