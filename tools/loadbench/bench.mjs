// Load-speed bench: simulates the browser fetch sequence for each menu transition.
// Usage: node bench.mjs <base-url> [--label X]
// Measures wall time with N-way parallelism (browser-like: 6 conns/host).
import { readFileSync } from 'fs';
import vm from 'vm';

const BASE = process.argv[2] || 'http://127.0.0.1:8901';
const GAME = '/home/hatch/workspace/fix3/loadspeed';
const PAR = 6;

async function get(path) {
  const t0 = performance.now();
  const r = await fetch(BASE + '/' + path);
  if (!r.ok) throw new Error(`HTTP ${r.status} ${path}`);
  const buf = Buffer.from(await r.arrayBuffer());
  return { path, bytes: buf.length, ms: performance.now() - t0 };
}
// Fetch a list with at most PAR in flight (like a browser's per-host pool).
async function pool(paths) {
  const out = []; let i = 0, inflight = 0, t0 = performance.now();
  let maxInflight = 0;
  await new Promise((resolve, reject) => {
    const next = () => {
      while (inflight < PAR && i < paths.length) {
        const p = paths[i++]; inflight++; maxInflight = Math.max(maxInflight, inflight);
        get(p).then(r => { out.push(r); inflight--; next(); }, reject);
      }
      if (i >= paths.length && inflight === 0) resolve();
    };
    next();
  });
  const bytes = out.reduce((a, r) => a + r.bytes, 0);
  return { files: out.length, bytes, ms: performance.now() - t0, maxInflight };
}
// V8 parse cost of a JS file (parse only, no execution) — real parser timing.
function parseCost(paths) {
  const t0 = performance.now();
  for (const p of paths) {
    const src = readFileSync(`${GAME}/${p}`, 'utf8');
    new vm.SourceTextModule(src, { identifier: p }); // parses, does not evaluate
  }
  return performance.now() - t0;
}
const bootJs = JSON.parse(readFileSync(new URL('./bootjs.json', import.meta.url), 'utf8'));
const fmtMB = b => (b / 1048576).toFixed(2) + ' MB';
const rep = (name, r, extra = '') => console.log(`${name}: ${r.files} files, ${fmtMB(r.bytes)}, wall ${r.ms.toFixed(0)} ms${extra}`);

const results = {};
// T1: boot -> main menu interactive. Blocking: HTML+CSS+JS fetch+parse.
// (async JSON fetches ride along on bandwidth; measured separately as T1b.)
{
  const blocking = ['game/index.html', 'game/styles.css', 'game/select.css', 'game/menus.css', ...bootJs];
  const r = await pool(blocking);
  const parseMs = parseCost(bootJs);
  rep('T1 boot->menu (blocking JS/CSS/HTML)', r, ` | V8 parse ${parseMs.toFixed(0)} ms`);
  results.t1 = { ...r, parseMs };
  const asyncJson = ['game/assets/models/model-facing.json','game/data/tripo-fighters.json','game/assets/ui/title-bg.png'];
  const r2 = await pool(asyncJson);
  rep('T1b boot async fetches (facing, tripo, title-bg; moves JSON now fight-time)', r2);
  results.t1b = r2;
}
// T2: menu -> select interactive. Screen shows instantly (DOM); the base warm
// moved to the idle lane (non-blocking) — measured as bytes, not blocking wall.
{
  const r = await pool(['game/assets/models/pantera.glb','game/assets/models/steve-fox.glb','game/assets/models/demonio.glb']);
  rep('T2 menu->select: select paints instantly; idle warm (3 base GLBs, non-blocking)', r);
  results.t2 = { ...r, blocking_ms: 0 };
}
// T3: select -> stage select. Stage grid builds; 23 lazy thumbs.
{
  const thumbs = JSON.parse(readFileSync(new URL('./thumbs.json', import.meta.url), 'utf8'));
  const r = await pool(thumbs);
  rep('T3 select->stage (stage thumbs)', r);
  results.t3 = r;
}
// T4: highlight -> 3D preview. 1 fighter GLB (tripo-size) + its T3 bank.
{
  const r = await pool(['roster/charger/attires/attire1/model.glb']);
  rep('T4 highlight preview GLB (charger ~18MB tripo)', r);
  results.t4 = r;
  const bankFiles = JSON.parse(readFileSync(new URL('./bank.json', import.meta.url), 'utf8'));
  const r2 = await pool(bankFiles);
  rep('T4b T3 anim bank (king)', r2);
  results.t4b = r2;
}
console.log(JSON.stringify(results, null, 1));
