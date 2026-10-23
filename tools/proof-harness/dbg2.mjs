// Pose lab retarget probe
//
// node tools/proof-harness/dbg2.mjs MODEL
// Prints per-bone world directions after retargeting one clip.
//
// Proof harness from the 2026-10-20/21 Claude session (tools/TOOLS-INDEX.md). Serve the repo
// first:  python3 -m http.server 8765   (from the repo root), then run with node 18+.
// PLAYWRIGHT_MODULE / CHROMIUM_PATH override the defaults below (cloud container layout).
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright/index.mjs');
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'] });
const page = await browser.newPage();
page.on('pageerror', e => console.log('pageerror', e.message));
await page.goto('http://127.0.0.1:8765/game/poselab.html', { waitUntil: 'load' });
await page.waitForFunction(() => window.__poselab);
const r = await page.evaluate(async (model) => {
  const THREE = await import('three');
  const { assets } = await import('./js/assets.js');
  const { loadT3Clips, retargetT3Clips } = await import('./js/t3anims.js');
  await assets.loadModels([model]);
  const inst = assets.createInstance(model, 0xffffff, 0x888888, 0);
  const clips = await loadT3Clips(THREE, 'xiaoyu');
  let hips = null; inst.model.traverse(o => { if (o.isBone && /Hips$/.test(o.name) && !hips) hips = o; });
  const chain = []; for (let o = hips; o; o = o.parent) chain.push({ n: o.name, type: o.type, p: o.position.toArray().map(x => +x.toFixed(3)), q: o.quaternion.toArray().map(x => +x.toFixed(3)), s: o.scale.toArray().map(x => +x.toFixed(3)) });
  inst.model.updateMatrixWorld(true);
  const wp = hips.getWorldPosition(new THREE.Vector3());
  const rt = retargetT3Clips(clips, 'xiaoyu', inst.model, THREE, null);
  const tr = rt.stance.tracks.find(t => t.name.endsWith('.position'));
  return { chain, hipsWorld: wp.toArray(), track: tr && { name: tr.name, v0: Array.from(tr.values.slice(0, 3)) } };
}, process.argv[2] || 'star');
console.log(JSON.stringify(r, null, 1));
await browser.close();
