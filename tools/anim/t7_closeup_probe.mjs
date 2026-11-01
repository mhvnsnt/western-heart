// Close-up pose probe: open ?quick=P1,P2,STAGE, stop the AI, take over the camera and photograph each fighter's idle
// stance from the front and the side (large, so arms / hands / face are judgeable), and log arm + head geometry.
// node closeup_probe.mjs <base-url> <outdir> <p1> <p2> [stage]     env BLOCK_T7=<dir> aborts assets/anim/t7/<dir>/
// env LOG_MODELS=1 prints MODEL <status> <url> for every .glb fetched (verify a live build's model source)
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright');
import fs from 'fs';
const [,, base, out, p1, p2, stage = 'shrine'] = process.argv;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 900, height: 900 } });
if (process.env.BLOCK_T7) await page.route('**/anim/t7/' + process.env.BLOCK_T7 + '/**', r => r.abort());
const logs = [];
// NO_REMOTE=1: block the B2 Worker so models load from the local tree (asset-config tries the remote first)
if (process.env.NO_REMOTE) await page.route(/workers\.dev/, r => r.abort());
page.on('console', m => logs.push(`[${m.type()}] ${m.text()}`));
// LOG_MODELS=1: record every .glb request and its status (which host actually served each fighter on a live build)
if (process.env.LOG_MODELS) page.on('response', r => { if (/\.glb(\?|$)/.test(r.url())) { const l = `MODEL ${r.status()} ${r.url()}`; logs.push(l); console.log(l); } });
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
await page.goto(`${base}?quick=${p1},${p2},${stage}`, { waitUntil: 'load', timeout: 120000 });
const t0 = Date.now();
let ready = false;
while (Date.now() - t0 < 150000) {
  ready = await page.evaluate(() => { const g = window.__game; return !!(g && g.p1 && g.p2 && g.p1.t3actions && Object.keys(g.p1.t3actions).length); }).catch(() => false);
  if (ready) break;
  await page.waitForTimeout(1000);
}
logs.push('READY ' + ready);
await page.evaluate(() => { const g = window.__game; g.ai = { update() {}, reset() {} }; });
await page.waitForTimeout(2500);
const cdp = await page.context().newCDPSession(page);
const shot = async (file) => {
  try {
    const r = await Promise.race([cdp.send('Page.captureScreenshot', { format: 'png' }), new Promise((_, rej) => setTimeout(() => rej(new Error('shot timeout')), 90000))]);
    fs.writeFileSync(file, Buffer.from(r.data, 'base64'));
  } catch (e) { logs.push('SHOT ' + file + ' ' + e.message); }
};
for (const who of ['p1', 'p2']) {
  for (const view of ['front', 'side']) {
    const info = await page.evaluate(([who, view]) => {
      const g = window.__game, f = g[who];
      const V = f.root.position.constructor;
      const wp = (b) => { if (!b) return null; const p = new V(); b.getWorldPosition(p); return p; };
      const r = wp(f.root);
      const dir = f.facing || 1;
      const cam = g.arena.camera;
      g.arena.setFreeCamera(true);
      if (view === 'front') cam.position.set(r.x + dir * 2.3, 1.35, r.z + 0.25);
      else cam.position.set(r.x + dir * 0.2, 1.35, r.z + 2.4);
      cam.lookAt(r.x, 1.05, r.z);
      cam.updateMatrixWorld();
      try { g.arena.render(); } catch (e) {}
      const B = f.bones || {};
      const P = {};
      for (const n of ['Hips', 'Spine', 'Chest', 'Neck', 'Head', 'LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand', 'RightShoulder', 'RightArm', 'RightForeArm', 'RightHand']) {
        const p = wp(B[n]); if (p) P[n] = [+(p.x - r.x).toFixed(3), +p.y.toFixed(3), +(p.z - r.z).toFixed(3)];
      }
      // head forward: the Head bone's local +Z / -Z axis in world (model faces +Z at rest after loader normalize)
      let headFwd = null;
      if (B.Head) { const q = new (f.root.quaternion.constructor)(); B.Head.getWorldQuaternion(q); const z = new V(0, 0, 1).applyQuaternion(q); headFwd = [+z.x.toFixed(2), +z.y.toFixed(2), +z.z.toFixed(2)]; }
      const st = f.t3actions && f.t3actions.stance;
      return { id: f.char.id, state: f.state, facing: dir, stance: st ? st.getClip().name : null, w: st ? +st.getEffectiveWeight().toFixed(2) : null, P, headFwd };
    }, [who, view]);
    logs.push('POSE ' + who + ' ' + view + ' ' + JSON.stringify(info));
    console.log('POSE ' + who + ' ' + view + ' ' + JSON.stringify(info));
    await page.waitForTimeout(400);
    await shot(`${out}/${who}_${view}.png`);
  }
}
fs.writeFileSync(`${out}/console.log`, logs.join('\n'));
console.log(logs.filter(l => /READY|pageerror|fight load failed/.test(l)).join('\n'));
await browser.close();
