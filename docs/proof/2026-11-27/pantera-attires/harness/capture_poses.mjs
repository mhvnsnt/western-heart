// capture the game's own posed skeleton (poselab showFighter) as per-bone local TRS, for weight evaluation
const { chromium } = await import('/home/box/dpipe/pw/node_modules/playwright-core/index.mjs');
import fs from 'fs';
const [,, fighter, model, out] = process.argv;
const clips = ['stance','intro','light','medium','heavy','grab','block','hit','launch','ko','win','walkFwd','walkBack','dash','crouch','crouchHold','backdash','runA','jumpUp','jumpFwd','jumpBack','sidestepA','sidestepB'];
const ts = [0.1,0.3,0.5,0.7,0.9];
const browser = await chromium.launch({ executablePath: '/opt/google/chrome/chrome', args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
await page.goto('http://127.0.0.1:8799/game/poselab.html', { waitUntil: 'load' });
await page.waitForFunction(() => window.__poselab, null, { timeout: 60000 });
const frames = [];
for (const clip of clips) for (const t of ts) {
  try {
    const r = await page.evaluate(async (a) => {
      const res = await window.__poselab.showFighter(a);
      const tgt = window.__poselab.cur().tgt; tgt.updateMatrixWorld(true);
      let sk = null; tgt.traverse(o => { if (!sk && o.isSkinnedMesh) sk = o.skeleton; });
      const bones = {}; for (const b of sk.bones) bones[b.name] = { q: b.quaternion.toArray(), p: b.position.toArray(), s: b.scale.toArray() };
      return { bank: res.bank || null, bones };
    }, { id: fighter, clip, t, model });
    frames.push({ clip, t, ...r });
  } catch (e) { console.error('skip', clip, t, String(e).slice(0, 120)); }
}
fs.writeFileSync(out, JSON.stringify({ fighter, model, frames }));
console.log('frames', frames.length);
await browser.close();
