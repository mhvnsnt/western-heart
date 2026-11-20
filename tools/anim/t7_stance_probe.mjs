// Stance probe: open ?quick=P1,P2,STAGE, wait for the fight, screenshot the idle stance and log the clip each
// fighter is playing (proves Pantera idles in the real T7 King stance, 't7_pantera_stance@...').
// node stance_probe.mjs <base-url> <outdir> [p1] [p2] [stage]
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright');
import fs from 'fs';
const [,, base, out, p1 = 'pantera', p2 = 'demonio', stage = 'shrine'] = process.argv;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
const logs = [];
page.on('console', m => logs.push(`[${m.type()}] ${m.text()}`));
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
await page.goto(`${base}?quick=${p1},${p2},${stage}`, { waitUntil: 'load', timeout: 120000 });
const t0 = Date.now();
let ready = false;
while (Date.now() - t0 < 150000) {
  ready = await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p1.t3actions && Object.keys(g.p1.t3actions).length); }).catch(() => false);
  if (ready) break;
  await page.waitForTimeout(1000);
}
logs.push('READY ' + ready + ' after ' + (Date.now() - t0) + ' ms');
await page.waitForTimeout(3500);
const state = () => page.evaluate(() => {
  const g = window.__game; if (!g || !g.p1) return null;
  const f = (x) => {
    const acts = x.t3actions || {};
    const st = acts.stance;
    const h = x.bones && x.bones.Hips, hd = x.bones && x.bones.Head;
    const v = (b) => { if (!b) return null; const p = new (b.position.constructor)(); b.getWorldPosition(p); return [+p.x.toFixed(2), +p.y.toFixed(2), +p.z.toFixed(2)]; };
    return { id: x.char.id, state: x.state, stanceClip: st ? st.getClip().name : null, stanceW: st ? +st.getEffectiveWeight().toFixed(2) : null,
      t7: !!(st && st.getClip().userData && st.getClip().userData.t7), hips: v(h), head: v(hd) };
  };
  return { round: g.roundState, p1: f(g.p1), p2: f(g.p2) };
});
const cdp = await page.context().newCDPSession(page);
for (let i = 0; i < 4; i++) {
  const s = await state().catch(e => ({ err: e.message }));
  logs.push('STATE ' + i + ' ' + JSON.stringify(s));
  console.log('STATE ' + i + ' ' + JSON.stringify(s));
  try {
    const r = await Promise.race([cdp.send('Page.captureScreenshot', { format: 'png' }), new Promise((_, rej) => setTimeout(() => rej(new Error('shot timeout')), 90000))]);
    fs.writeFileSync(`${out}/idle_${i}.png`, Buffer.from(r.data, 'base64'));
  } catch (e) { logs.push('SHOT ' + i + ' ' + e.message); }
  await page.waitForTimeout(400);
}
fs.writeFileSync(`${out}/console.log`, logs.join('\n'));
console.log(logs.filter(l => /READY|STATE|WH-T7|pageerror|\[error\]/.test(l)).slice(0, 30).join('\n'));
await browser.close();
