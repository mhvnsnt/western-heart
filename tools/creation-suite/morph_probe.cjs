/* morph_probe.cjs — phone-size Playwright probe of the creation suite's REAL body + face morphing.

   NODE_PATH=<dir with playwright> node tools/creation-suite/morph_probe.cjs <W> <H> <outdir> [template-id]

   Serves the repo on 127.0.0.1:8766, opens customization/creation-suite-ui at W x H (touch, mobile), starts a new
   fighter from the template, walks APPEARANCE -> Body Morphing -> region -> sliders and Face Deformation -> part ->
   sliders by tapping the real buttons, moves real <input type=range> sliders, and checks numerically:
     - mesh.morphTargetInfluences carry the slider value on the '<id>+' / '<id>-' target,
     - the CPU-evaluated vertex (three.js Mesh/SkinnedMesh.getVertexPosition: morphs + skinning) actually moves,
     - the saved record (customizationRecord().body.morph_targets) and localStorage carry the values,
     - nothing in the panel overlaps or leaves the screen; no page errors.
   WebGL draw calls are stubbed (software GL stalls on the build box): layout + JS state + vertex maths are real,
   the screenshot shows the UI only. Proxy: honours HTTPS_PROXY (login passed to Chromium), loopback bypassed. */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const http = require('http');

const [W, H, OUT, TPL] = [+process.argv[2] || 390, +process.argv[3] || 844, process.argv[4] || '/tmp/morph-probe', process.argv[5] || 'powerhouse'];
const ROOT = path.resolve(__dirname, '..', '..');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json',
  '.css': 'text/css', '.glb': 'model/gltf-binary', '.png': 'image/png', '.jpg': 'image/jpeg', '.ttf': 'font/ttf', '.woff2': 'font/woff2' };

function serve() {
  return new Promise(res => {
    const srv = http.createServer((q, r) => {
      const p = path.join(ROOT, decodeURIComponent(new URL(q.url, 'http://x').pathname));
      if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { r.writeHead(404); return r.end(); }
      r.writeHead(200, { 'content-type': TYPES[path.extname(p)] || 'application/octet-stream' });
      fs.createReadStream(p).pipe(r);
    }).listen(8766, '127.0.0.1', () => res(srv));
  });
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const srv = await serve();
  const px = process.env.HTTPS_PROXY; const pu = px && new URL(px);
  const b = await chromium.launch({ ...(pu ? { proxy: { server: pu.protocol + '//' + pu.host, username: decodeURIComponent(pu.username), password: decodeURIComponent(pu.password), bypass: '127.0.0.1,localhost' } } : {}),
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await b.newContext({ viewport: { width: W, height: H }, hasTouch: true, isMobile: true, deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  if (!process.env.DRAW) await p.addInitScript(() => { for (const C of [WebGL2RenderingContext, WebGLRenderingContext]) for (const m of ['drawElements', 'drawArrays', 'drawElementsInstanced', 'drawArraysInstanced', 'drawRangeElements']) if (C.prototype[m]) C.prototype[m] = function () {}; });
  await p.route(/^https?:\/\/(?!127\.0\.0\.1)/, r => r.abort()); // offline: everything the suite needs is in the repo
  const errs = []; p.on('pageerror', e => errs.push(e.message.slice(0, 240)));
  const out = { viewport: [W, H], template: TPL, steps: [] };
  const step = (name, data) => { out.steps.push({ name, ...data }); };

  await p.goto('http://127.0.0.1:8766/customization/creation-suite-ui/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => window.__suite && window.__suite.viewer && window.__suite.viewer.ready, null, { timeout: 90000 });
  // CREATE from the chosen template through the real TEMPLATE SELECT window
  await p.evaluate(() => document.querySelector('#tpl-change') ? document.querySelector('#tpl-change').click() : null);
  await p.waitForSelector(`[data-t="${TPL}"]`, { timeout: 10000 });
  await p.tap(`[data-t="${TPL}"]`);
  await p.waitForFunction(t => window.__suite.viewer.ready && /\/templates\/meshes\//.test(window.__suite.viewer.currentUrl) && window.__suite.viewer.currentUrl.includes(t) && window.__suite.wiredMorphs().size > 0, TPL, { timeout: 90000 });
  step('template-loaded', await p.evaluate(() => ({ url: window.__suite.viewer.currentUrl, wired: window.__suite.wiredMorphs().size, catalog: window.__suite.MORPH_SLIDERS.length })));

  const layout = async (tag) => {
    await p.waitForTimeout(700); // T7 slide-in of the panel finishes before measuring
    const r = await p.evaluate(() => {
      const els = [...document.querySelectorAll('#right-rail button, #right-rail .ctl label, #right-rail input[type=range], #right-rail .sect, #topbar button, #topbar #breadcrumb')]
        .filter(e => { const s = getComputedStyle(e), r = e.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0; });
      const panel = document.querySelector('#panel-body').getBoundingClientRect();
      const vis = els.filter(e => { const r = e.getBoundingClientRect(); return !e.closest('#panel-body') || (r.bottom > panel.top && r.top < panel.bottom); });
      const nm = e => (e.id ? '#' + e.id : e.tagName.toLowerCase() + '.' + (e.className || '').toString().split(' ')[0]) + ' "' + (e.textContent || e.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' ').slice(0, 24) + '"';
      const ov = [];
      for (let i = 0; i < vis.length; i++) for (let j = i + 1; j < vis.length; j++) {
        if (vis[i].contains(vis[j]) || vis[j].contains(vis[i])) continue;
        const a = vis[i].getBoundingClientRect(), c = vis[j].getBoundingClientRect();
        const ix = Math.min(a.right, c.right) - Math.max(a.left, c.left), iy = Math.min(a.bottom, c.bottom) - Math.max(a.top, c.top);
        if (ix > 1 && iy > 1) ov.push(`${nm(vis[i])} x ${nm(vis[j])}`);
      }
      const off = vis.filter(e => { const r = e.getBoundingClientRect(); return r.left < -0.5 || r.right > innerWidth + 0.5 || (r.bottom > innerHeight + 0.5 && !e.closest('#panel-body')); }).map(nm);
      const small = vis.filter(e => e.tagName === 'BUTTON' && e.getBoundingClientRect().height < 32).map(nm);
      return { crumb: (document.querySelector('#breadcrumb') || {}).textContent, sub: document.querySelector('#panel-sub').textContent, overlaps: ov, offscreen: off, smallTargets: small };
    });
    await p.screenshot({ path: path.join(OUT, `${tag}.png`) });
    step('layout:' + tag, r);
    return r;
  };

  // vertex probe: biggest-moving vertex of a target, measured through three.js getVertexPosition (morph + skin)
  const vertexMove = (targetName) => p.evaluate((tn) => {
    const v = window.__suite.viewer; let best = null;
    v.model.traverse(o => {
      if (!o.morphTargetDictionary || o.morphTargetDictionary[tn] === undefined) return;
      const idx = o.morphTargetDictionary[tn], attr = o.geometry.morphAttributes.position[idx];
      let k = -1, m = 0; for (let i = 0; i < attr.count; i++) { const x = attr.getX(i), y = attr.getY(i), z = attr.getZ(i); const L = x * x + y * y + z * z; if (L > m) { m = L; k = i; } }
      if (k >= 0 && (!best || m > best.m)) best = { o, k, m };
    });
    if (!best) return null;
    const V = best.o.position.constructor; const a = new V(), w = new V();
    v.model.updateMatrixWorld(true);
    best.o.getVertexPosition(best.k, a); w.copy(a).applyMatrix4(best.o.matrixWorld);
    return { mesh: best.o.name, vertex: best.k, world: [w.x, w.y, w.z].map(x => +x.toFixed(5)) };
  }, targetName);
  const influences = (id) => p.evaluate((id) => {
    const r = []; window.__suite.viewer.model.traverse(o => { if (o.morphTargetDictionary && o.morphTargetDictionary[id + '+'] !== undefined) r.push([o.morphTargetInfluences[o.morphTargetDictionary[id + '+']], o.morphTargetInfluences[o.morphTargetDictionary[id + '-']]]); });
    return r;
  }, id);
  const setRange = async (id, val) => {
    await p.$eval(`input[data-mt="${id}"]`, (el, v) => { el.value = String(v); el.dispatchEvent(new Event('input', { bubbles: true })); }, val);
  };

  await p.tap('.rail-btn[data-tab="body"]').catch(() => {});
  await p.waitForSelector('#bw-body-morph', { timeout: 10000 });
  await layout('01-appearance');

  const checks = [];
  const exercise = async (winBtn, groupKey, id, val) => {
    if (winBtn) await p.tap(winBtn);
    await p.waitForSelector(`#mg-${groupKey}`);
    await p.tap(`#mg-${groupKey}`); await p.waitForSelector(`input[data-mt="${id}"]`);
    const tn = id + (val > 0 ? '+' : '-');
    const before = await vertexMove(tn);
    await setRange(id, Math.round(val * 100));
    const inf = await influences(id);
    const after = await vertexMove(tn);
    const moved = before && after ? Math.hypot(...after.world.map((x, i) => x - before.world[i])) : 0;
    const shown = await p.$eval(`#mt-${id} .val`, e => e.textContent);
    const c = { id, value: val, shown, influences: inf, vertex: before && before.vertex, moved_m: +moved.toFixed(5) };
    checks.push(c);
    return c;
  };
  await exercise('#bw-body-morph', 'chest', 'b_chest', 1);
  await layout('02-body-chest');
  await exercise('#btn-back', 'waist', 'b_belly', 0.8); // back to region list, then Waist & Abdomen
  await p.tap('#btn-back'); await p.waitForSelector('#mg-overall');
  await p.tap('#btn-back'); await p.waitForSelector('#bw-face-morph');
  await exercise('#bw-face-morph', 'jaw', 'f_jaw_w', 1);
  await layout('03-face-jaw');
  await exercise('#btn-back', 'nose', 'f_nose_w', -1);
  await p.tap('#btn-back'); await p.waitForSelector('#mg-ears');
  await exercise(null, 'ears', 'f_ear_angle', 0.6);
  await layout('04-face-ears');
  step('slider-checks', { checks });

  const rec = await p.evaluate(() => ({ record: window.__suite.customizationRecord().body, stored: JSON.parse(localStorage.getItem('wh_creation_suite_v1')).body.morph_targets }));
  step('saved', rec);
  // template switch resets to the template shape
  out.errors = errs;
  const okChecks = checks.every(c => c.moved_m > 0.0003 && c.influences.length && c.influences.every(([pl, mi]) => (c.value > 0 ? Math.abs(pl - c.value) < 0.011 && mi === 0 : Math.abs(mi + c.value) < 0.011 && pl === 0)));
  const okLayout = out.steps.filter(s => s.name.startsWith('layout:')).every(s => !s.overlaps.length && !s.offscreen.length);
  const okSave = Object.keys(rec.record.morph_targets || {}).length >= 4 && JSON.stringify(rec.record.morph_targets) === JSON.stringify(Object.fromEntries(Object.entries(rec.stored).map(([k, v]) => [k, Math.round(v * 100) / 100])));
  out.pass = { sliders: okChecks, layout: okLayout, save: okSave, noPageErrors: !errs.length };
  fs.writeFileSync(path.join(OUT, 'probe.json'), JSON.stringify(out, null, 1));
  console.log(JSON.stringify(out.pass), 'checks', JSON.stringify(checks.map(c => [c.id, c.shown, c.moved_m])), 'errors', errs.length);
  await b.close(); srv.close();
})().catch(e => { console.error('PROBE FAILED', e); process.exit(1); });
