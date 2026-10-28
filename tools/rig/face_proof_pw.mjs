// face_proof_pw.mjs MODEL_REL OUT_PREFIX [poses=jab,uppercut]  (needs playwright-core; PW_PATH dir)
// Waits for face_proof.html to set document.title='DONE', then screenshots.
import { createRequire } from 'module';
const require = createRequire(process.env.PW_PATH || import.meta.url);
const { chromium } = require('playwright-core');
const [model, out, poses = 'jab,uppercut'] = process.argv.slice(2);
const port = process.env.PORT || 8765;
const b = await chromium.launch({ executablePath: process.env.PW_EXE || undefined, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--no-sandbox'] });
const p = await b.newPage({ viewport: { width: +(process.env.VW || 390), height: +(process.env.VH || 844) } });
for (const pose of poses.split(',')) {
  await p.goto(`http://127.0.0.1:${port}/tools/rig/face_proof.html?model=/${model}&pose=${pose}&facez=1`);
  await p.waitForFunction(() => document.title === 'DONE', null, { timeout: 240000 });
  await p.screenshot({ path: `${out}_${pose}.png` });
  console.log('shot', `${out}_${pose}.png`);
}
await b.close();
