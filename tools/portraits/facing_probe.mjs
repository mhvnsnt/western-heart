// tools/portraits/facing_probe.mjs — which way does each fighter's model really face on its select card?
// (owner 2026-11-06: "go through and look and actually look and see which all ones are currently broken ... fix them
// all per character"). The select card and the fight use the same instance (assets.createInstance + the bank stance),
// so a card that shows a fighter's back means the fighter stands the same way in the game. This renders each fighter's
// card exactly as tools/portraits/capture.mjs does, from four camera angles around the head (yaw 0 = the card camera
// on +Z, 90, 180, 270), into one labelled strip per fighter, to be judged by eye.
//
// usage (serve the repo root on $WH_URL first, default http://127.0.0.1:8822):
//   node tools/portraits/facing_probe.mjs OUTDIR id[,id...] [--rest]
// writes OUTDIR/<id>_yaw<deg>.png (--rest: the bind pose, OUTDIR/<id>_rest_yaw<deg>.png) (320x320). Tile them with any image tool (or PIL) to compare.
import fs from 'node:fs';
import { createRequire } from 'node:module';

const req = createRequire(import.meta.url);
let pw;
try { pw = req('playwright'); } catch { pw = req(process.env.PLAYWRIGHT_MODULE || '/opt/node-tools/node_modules/playwright'); }
const BASE = process.env.WH_URL || 'http://127.0.0.1:8822';
const rest = process.argv.includes('--rest');
const [, , out, list] = process.argv.filter((a) => a !== '--rest');
if (!out || !list) { console.error('usage: node tools/portraits/facing_probe.mjs OUTDIR id[,id...]'); process.exit(2); }
fs.mkdirSync(out, { recursive: true });
const b = await pw.chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
for (const id of list.split(',')) {
  for (const yaw of [0, 90, 180, 270]) {
    const p = await b.newPage({ viewport: { width: 320, height: 320 } });
    await p.goto(BASE + '/game/portrait-capture.html');
    await p.waitForFunction(() => window.ready, null, { timeout: 60000 });
    let r;
    try { r = await p.evaluate(([i, y, r]) => window.capture(i, { yaw: y, rest: r }), [id, yaw, rest]); } catch (e) { r = { id, error: String(e.message || e).slice(0, 160) }; }
    if (r.png) fs.writeFileSync(`${out}/${id}${rest ? '_rest' : ''}_yaw${yaw}.png`, Buffer.from(r.png.split(',')[1], 'base64'));
    console.log(JSON.stringify({ id, yaw, model: r.model, error: r.error || null }));
    await p.close();
  }
}
await b.close();
