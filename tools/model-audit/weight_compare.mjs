// tools/model-audit/weight_compare.mjs — before/after of a re-weighted fight model, judged by eye.
// Renders the fighter (game/poselab.html: the game's own loader, bank and retarget) with its CURRENT model and with a
// candidate GLB loaded under the same model key, through the same clips, textured and as a stretch heat map
// (blue rigid -> yellow 2x -> red 3x+), plus each pose's torn-vertex count (score >= 2 with a 1 cm floor).
//   node tools/model-audit/weight_compare.mjs OUTDIR fighterId candidate.glb [clip@t,...]
// (serve the repo root on $WH_URL first, default http://127.0.0.1:8822; candidate path relative to the repo root)
import { createRequire } from 'node:module';
import fs from 'node:fs';
const req = createRequire(import.meta.url);
let pw;
try { pw = req('playwright'); } catch { pw = req(process.env.PLAYWRIGHT_MODULE || '/opt/node-tools/node_modules/playwright'); }
const BASE = process.env.WH_URL || 'http://127.0.0.1:8822';
const [, , out, id, cand, list] = process.argv;
if (!out || !id || !cand) { console.error('usage: node tools/model-audit/weight_compare.mjs OUTDIR fighterId candidate.glb [clip@t,...]'); process.exit(2); }
fs.mkdirSync(out, { recursive: true });
const POSES = (list || 'stance@0.5,light@0.45,medium@0.45,heavy@0.45,block@0.5,hit@0.4').split(',').map((s) => s.split('@'));
const YAW = +(process.env.YAW || 0);
const PART = process.env.PART || 'full'; // 'full' body, 'upper' (hips to head, both hands) or 'face'
const b = await pw.chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const rows = [];
for (const which of ['before', 'after']) {
  const p = await b.newPage({ viewport: { width: 1200, height: 900 } });
  await p.goto(BASE + '/game/poselab.html');
  await p.waitForFunction(() => window.__poselab, null, { timeout: 90000 });
  for (const [clip, t] of POSES) {
    for (const heat of [false, true]) {
      const r = await p.evaluate(async ([id, clip, t, heat, which, cand, yaw, process_part]) => {
        try {
          const A = await import('./js/assets.js');
          const { FULL_ROSTER } = await import('./js/roster-full.js');
          const { resolveFighterAttire } = await import('./js/attires.js');
          const key = resolveFighterAttire(FULL_ROSTER.find((c) => c.id === id)).model;
          if (which === 'after' && !window.__candSet) { A.MODEL_URLS[key] = '../' + cand; window.__candSet = true; }
          await window.__poselab.showFighter({ id, clip, t: +t });
          const s = window.__poselab.stretchMap({ heat });
          window.__poselab.closeup({ yaw, part: process_part });
          return { key, torn: s.reduce((n, m) => n + m.badVerts, 0) };
        } catch (e) { return { err: String(e.message || e).slice(0, 160) }; }
      }, [id, clip, t, heat, which, cand, YAW, PART]);
      if (r.err) { console.log(which, clip, r.err); continue; }
      await p.screenshot({ path: `${out}/${id}_${clip}_${which}_${heat ? 'heat' : 'tex'}.png` });
      if (heat) rows.push({ which, clip, t: +t, torn: r.torn });
    }
  }
  await p.close();
}
await b.close();
fs.writeFileSync(`${out}/${id}_compare.json`, JSON.stringify(rows, null, 1));
for (const [clip] of POSES) {
  const bf = rows.find((r) => r.which === 'before' && r.clip === clip), af = rows.find((r) => r.which === 'after' && r.clip === clip);
  console.log(clip.padEnd(8), 'torn verts before', bf ? bf.torn : '-', 'after', af ? af.torn : '-');
}
