// Lane H: screenshot the select screen's P1 preview pane for EVERY selectable fighter.
// Page setup copied from tools/proof-harness/touch_play.mjs (iPhone landscape, touch, software GL).
//   node shoot_select.mjs URL OUTDIR [ids,comma,separated]
//   env ATTIRES='{"negativo":"n3g4tiv0"}' presets the saved attire map (wh_attires_v1) like a returning player.
// Writes OUTDIR/<id>.png (the P1 pane) and OUTDIR/diag.json (per-fighter render diagnostics).
const { chromium } = await import('/opt/node22/lib/node_modules/playwright/index.mjs');
import fs from 'fs';
const [,, URL, out, only = ''] = process.argv;
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome',
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const W = +(process.env.VW || 844), H = +(process.env.VH || 390);
const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: +(process.env.DPR || 1), isMobile: true, hasTouch: true,
  userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' });
if (process.env.ATTIRES) await ctx.addInitScript((a) => { try { if (!sessionStorage.getItem('lh')) { localStorage.setItem('wh_attires_v1', a); sessionStorage.setItem('lh', '1'); } } catch (_) {} }, process.env.ATTIRES);
const page = await ctx.newPage();
const logs = [];
page.on('console', m => { const t = m.text(); if (m.type() === 'error' || /select preview|retarget|stance|material gate/i.test(t)) logs.push(`[${m.type()}] ${t}`); });
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
await page.goto(URL, { waitUntil: 'load', timeout: 120000 });
await page.waitForFunction(() => window.__modes && window.__selectScreen, null, { timeout: 120000 });
await sleep(1500);
await page.evaluate(() => window.__modes.startMode('versus'));
await page.waitForFunction(() => document.getElementById('screen-select').classList.contains('active'), null, { timeout: 60000 });
await sleep(2500); // tripo-fighters.json rebuild
const ids = only ? only.split(',') : await page.evaluate(() => [...document.querySelectorAll('#char-grid .char-card')].map(c => c.dataset.id).filter(i => i && i !== '__random'));
console.log('fighters:', ids.length);
const diag = [];
for (const id of ids) {
  const t0 = Date.now();
  logs.length = 0;
  await page.evaluate((i) => window.__selectScreen.selectById(i), id);
  await sleep(300);
  await page.waitForFunction(() => !window.__selectScreen._panes.p1._loading, null, { timeout: 120000 }).catch(() => {});
  await sleep(1200); // stance settles; a few frames render
  const d = await page.evaluate(async () => {
    const THREE = await import('three');
    const pane = window.__selectScreen._panes.p1;
    const r = { model: !!pane.model, stance: pane.stanceSource || null, label: document.querySelector('#pane-p1 .pane-style')?.textContent || '',
      fallbackShown: !(document.querySelector('#pane-p1 .pane-fallback') || { hidden: true }).hidden, meshes: [] };
    if (!pane.model) return r;
    const cam = pane.camera; cam.updateMatrixWorld();
    const fr = new THREE.Frustum().setFromProjectionMatrix(new THREE.Matrix4().multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse));
    pane.model.updateMatrixWorld(true);
    const all = new THREE.Box3();
    pane.model.traverse((o) => {
      if (!o.isMesh) return;
      const mats = [].concat(o.material);
      const m = { name: o.name, skinned: !!o.isSkinnedMesh, visible: o.visible, verts: o.geometry.attributes.position.count,
        mats: mats.map(x => ({ n: x.name, transparent: x.transparent, opacity: +x.opacity.toFixed(2), depthWrite: x.depthWrite, side: x.side, map: !!x.map, mapReady: !!(x.map && x.map.image && (x.map.image.width || x.map.image.videoWidth)) })) };
      let sph = null;
      if (o.isSkinnedMesh) sph = o.boundingSphere ? o.boundingSphere.clone() : null;
      else { if (!o.geometry.boundingSphere) o.geometry.computeBoundingSphere(); sph = o.geometry.boundingSphere.clone(); }
      if (sph) { sph.applyMatrix4(o.matrixWorld); m.cullSphere = [...sph.center.toArray(), sph.radius].map(v => +v.toFixed(2)); m.inFrustum = fr.intersectsSphere(sph); }
      const b = new THREE.Box3(), v = new THREE.Vector3(), n = o.geometry.attributes.position.count, step = Math.max(1, Math.floor(n / 4000));
      for (let i = 0; i < n; i += step) { o.isSkinnedMesh ? o.getVertexPosition(i, v) : v.fromBufferAttribute(o.geometry.attributes.position, i); v.applyMatrix4(o.matrixWorld); b.expandByPoint(v); }
      m.liveBox = [...b.min.toArray(), ...b.max.toArray()].map(x => +x.toFixed(2));
      m.liveInFrustum = fr.intersectsBox(b);
      all.union(b);
      r.meshes.push(m);
    });
    r.box = [...all.min.toArray(), ...all.max.toArray()].map(x => +x.toFixed(2));
    r.cam = { pos: cam.position.toArray().map(x => +x.toFixed(2)), near: cam.near, far: cam.far, aspect: +cam.aspect.toFixed(2) };
    r.cullMiss = r.meshes.filter(m => m.inFrustum === false && m.liveInFrustum).map(m => m.name);
    return r;
  });
  const el = await page.$('#pane-p1');
  try { await (el || page).screenshot({ path: `${out}/${id}.png`, timeout: 90000 }); } catch (e) { logs.push(`[shot] ${e.message.split('\n')[0]}`); }
  diag.push({ id, ms: Date.now() - t0, ...d, logs: [...logs] });
  console.log(id, d.model ? 'model' : 'NO MODEL', d.stance, `"${d.label}"`, 'meshes', (d.meshes || []).length, 'cullMiss', JSON.stringify(d.cullMiss || []), logs.length ? logs[0].slice(0, 160) : '');
}
fs.writeFileSync(`${out}/diag.json`, JSON.stringify(diag, null, 1));
await browser.close();
