const { chromium } = await import('/home/box/dpipe/pw/node_modules/playwright-core/index.mjs');
import fs from 'fs';
const browser = await chromium.launch({ executablePath: '/opt/google/chrome/chrome', args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 1200, height: 960 } });
await page.goto('http://127.0.0.1:8799/game/poselab.html', { waitUntil: 'load' });
await page.waitForFunction(() => window.__poselab, null, { timeout: 60000 });
const out=[];
const sel = await page.evaluate(async()=>{ const m=await import('./js/attires.js'); const r=await import('./js/roster-full.js'); const b=r.FULL_ROSTER.find(x=>x.id==='pantera'); const res=[];
  for (const a of m.selectableAttires(b)) { m.setAttire(b,a.model); res.push({set:a.model,label:m.attireLabel?m.attireLabel(b,a.model):null,resolved:m.resolveFighterAttire(b).model}); } return res; });
for (const s of sel) {
  // showFighter with NO model override = the fight's own resolution from the saved selection
  await page.evaluate(async(id)=>{ const m=await import('./js/attires.js'); const r=await import('./js/roster-full.js'); m.setAttire(r.FULL_ROSTER.find(x=>x.id==='pantera'), id); }, s.set);
  const r=await page.evaluate(()=>window.__poselab.showFighter({id:'pantera',clip:'light',t:0.45}));
  s.showFighterModel=r.model; s.bank=r.bank; out.push(s);
}
console.log(JSON.stringify(out,null,1));
fs.writeFileSync('/workspace/pantera-attires-work/after/attire_select.json', JSON.stringify(out,null,1));
await browser.close();
