// tools/model-audit/stretch_audit.mjs — deformation stretch audit of every fight model on the clips the fight plays.
//
// Owner 2026-11-07: "Arms at shoulders, forearms, and hands are all crushed and twisted some have extreme weight
// painting issues all over and some have twisted necks or stretched faces evaluate and fix it all".
// Industry practice: a stretch / compression map (every triangle edge, posed length vs bind length) on the shipping
// animations finds weight-paint errors (skin bound to the wrong bone, a joint with no blend) and shows WHERE they are.
// This drives game/poselab.html: showFighter (the model the fight loads, the game's own retarget and bank) then
// stretchMap (CPU skinning identical to the GPU's). Per fighter it records each clip's percentiles and the bones that own
// the worst vertices, then renders the worst clip as a heat map (blue = rigid, yellow = 2x, red = 3x+) front and 3/4,
// next to the textured pose, for judging BY EYE.
//
// usage (serve the repo root on $WH_URL first, default http://127.0.0.1:8822):
//   node tools/model-audit/stretch_audit.mjs OUTDIR id[,id...]      -> OUTDIR/stretch.json, OUTDIR/<id>_heat.png
import { createRequire } from 'node:module';
import fs from 'node:fs';

const req = createRequire(import.meta.url);
let pw;
try { pw = req('playwright'); } catch { pw = req(process.env.PLAYWRIGHT_MODULE || '/opt/node-tools/node_modules/playwright'); }
const BASE = process.env.WH_URL || 'http://127.0.0.1:8822';
const [, , out, list] = process.argv;
if (!out || !list) { console.error('usage: node tools/model-audit/stretch_audit.mjs OUTDIR id[,id...]'); process.exit(2); }
fs.mkdirSync(out, { recursive: true });
const CLIPS = [['stance', 0.3], ['walk_fwd', 0.5], ['light', 0.45], ['medium', 0.45], ['heavy', 0.45], ['block', 0.5], ['hit', 0.4]];
const jf = `${out}/stretch.json`;
const all = fs.existsSync(jf) ? JSON.parse(fs.readFileSync(jf, 'utf8')) : {};
const b = await pw.chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
for (const id of list.split(',')) {
  const p = await b.newPage({ viewport: { width: 1200, height: 900 } });
  await p.goto(BASE + '/game/poselab.html');
  await p.waitForFunction(() => window.__poselab, null, { timeout: 90000 });
  const rec = { clips: {}, worst: null };
  for (const [clip, t] of CLIPS) {
    const r = await p.evaluate(async ([id, clip, t]) => {
      try { const f = await window.__poselab.showFighter({ id, clip, t }); return { model: f.model, meshes: window.__poselab.stretchMap() }; }
      catch (e) { return { err: String(e.message || e).slice(0, 160) }; }
    }, [id, clip, t]);
    rec.model = rec.model || r.model;
    if (r.err) { rec.clips[clip] = { err: r.err }; continue; }
    // the fighter's score for this clip: the worst mesh by bad-vertex fraction (ties -> p99.9)
    const ms = r.meshes.filter((m) => m.edges > 0);
    const w = ms.slice().sort((a, b) => (b.badFrac - a.badFrac) || (b.p999 - a.p999))[0] || null;
    rec.clips[clip] = { t, worstMesh: w, meshes: ms };
    if (w && (!rec.worst || w.badFrac > rec.worst.badFrac)) rec.worst = { clip, t, ...w };
  }
  // heat map of the worst clip, front and 3/4, beside the textured pose
  if (rec.worst) {
    for (const [tag, yaw, heat] of [['tex0', 0, false], ['heat0', 0, true], ['heat35', 35, true], ['heatm35', -35, true]]) {
      const ok = await p.evaluate(async ([id, clip, t, yaw, heat]) => {
        try {
          await window.__poselab.showFighter({ id, clip, t });
          if (heat) window.__poselab.stretchMap({ heat: true });
          window.__poselab.closeup({ yaw });
          return true;
        } catch (e) { return false; }
      }, [id, rec.worst.clip, rec.worst.t, yaw, heat]);
      if (ok) await p.screenshot({ path: `${out}/${id}_${tag}.png`, clip: { x: 0, y: 0, width: 1200, height: 900 } });
    }
  }
  all[id] = rec;
  fs.writeFileSync(jf, JSON.stringify(all, null, 1));
  const w = rec.worst;
  console.log(id.padEnd(18), w ? `${w.clip.padEnd(8)} bad ${(w.badFrac * 100).toFixed(2)}% p99.9 ${w.p999} max ${w.max} [${w.badBones.join(' ')}] ${w.mesh}` : 'no data',
    Object.entries(rec.clips).filter(([, v]) => v.err).map(([k, v]) => `${k}: ${v.err}`).join(' | '));
  await p.close();
}
await b.close();
