// tools/model-audit/rig_qa_sheet.mjs — close-up deformation QA of every fighter, for judging BY EYE.
//
// Owner 2026-11-07: "Arms at shoulders, forearms, and hands are all crushed and twisted some have extreme weight
// painting issues all over and some have twisted necks or stretched faces evaluate and fix it all".
// Industry practice (pose QA sheets): pose the character through the same clips the game plays and inspect the
// deformation close up. For each fighter this drives game/poselab.html (the game's own loader + retarget, the clips its
// fight binds) through stance / light / medium / heavy / block / hit at a few times, and renders the upper body
// full-canvas from the front and a 3/4 angle, plus a face close-up. One PNG per (fighter, clip, time, view) and a
// contact sheet per fighter (OUT/<id>_sheet.png) to be judged by eye.
//
// usage (serve the repo root on $WH_URL first, default http://127.0.0.1:8822):
//   node tools/model-audit/rig_qa_sheet.mjs OUTDIR id[,id...]
import { createRequire } from 'node:module';
import fs from 'node:fs';

const req = createRequire(import.meta.url);
let pw;
try { pw = req('playwright'); } catch { pw = req(process.env.PLAYWRIGHT_MODULE || '/opt/node-tools/node_modules/playwright'); }
const BASE = process.env.WH_URL || 'http://127.0.0.1:8822';
const [, , out, list] = process.argv;
if (!out || !list) { console.error('usage: node tools/model-audit/rig_qa_sheet.mjs OUTDIR id[,id...]'); process.exit(2); }
fs.mkdirSync(out, { recursive: true });
const SHOTS = [
  ['stance', 0.3, 0], ['stance', 0.3, 35], ['light', 0.45, 0], ['light', 0.45, 35], ['medium', 0.45, 0],
  ['heavy', 0.45, 0], ['heavy', 0.45, -35], ['block', 0.5, 0], ['hit', 0.4, 0],
];
const b = await pw.chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const results = {};
for (const id of list.split(',')) {
  const p = await b.newPage({ viewport: { width: 1200, height: 900 } });
  await p.goto(BASE + '/game/poselab.html');
  await p.waitForFunction(() => window.__poselab, null, { timeout: 90000 });
  results[id] = [];
  for (const [clip, t, yaw] of SHOTS) {
    const r = await p.evaluate(async ([id, clip, t, yaw]) => {
      try { await window.__poselab.showFighter({ id, clip, t }); return window.__poselab.closeup({ yaw }); }
      catch (e) { return { err: String(e.message || e).slice(0, 120) }; }
    }, [id, clip, t, yaw]);
    const name = `${id}_${clip}_${Math.round(t * 100)}_${yaw}`;
    if (!r.err) await p.screenshot({ path: `${out}/${name}.png` });
    results[id].push({ name, ...r });
  }
  // face close-up on the stance
  const f = await p.evaluate(async (id) => {
    try { await window.__poselab.showFighter({ id, clip: 'stance', t: 0.3 }); return window.__poselab.closeup({ yaw: 0, part: 'face' }); }
    catch (e) { return { err: String(e.message || e).slice(0, 120) }; }
  }, id);
  if (!f.err) await p.screenshot({ path: `${out}/${id}_face.png` });
  results[id].push({ name: `${id}_face`, ...f });
  console.log(id, results[id].filter((x) => x.err).map((x) => `${x.name}: ${x.err}`).join(' | ') || 'ok');
  await p.close();
  // contact sheet: every shot of this fighter in one image (5 x 2, labelled), the page to judge by eye
  const shots = results[id].filter((x) => !x.err && fs.existsSync(`${out}/${x.name}.png`));
  if (shots.length) {
    const cells = shots.map((x) => `<figure><img src="data:image/png;base64,${fs.readFileSync(`${out}/${x.name}.png`).toString('base64')}">`
      + `<figcaption>${x.name}</figcaption></figure>`).join('');
    const sp = await b.newPage({ viewport: { width: 1500, height: 600 } });
    await sp.setContent(`<style>body{margin:0;background:#111;display:grid;grid-template-columns:repeat(5,300px)}`
      + `figure{margin:0;position:relative}img{width:300px;height:225px;display:block}`
      + `figcaption{position:absolute;top:2px;left:4px;color:#ff0;font:11px sans-serif}</style>${cells}`);
    await sp.screenshot({ path: `${out}/${id}_sheet.png`, fullPage: true });
    await sp.close();
  }
}
fs.writeFileSync(`${out}/results.json`, JSON.stringify(results, null, 1));
await b.close();
