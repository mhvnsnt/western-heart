// Doc Frank Tripo-forefront probe (2026-10-21 lane).
// Verifies with the game's OWN modules: ladder presentation order,
// Tripo defaults, transform targets, MODEL_URLS targets exist on disk,
// and every Doc Frank GLB the ladder can load is RIGGED (skin + joints).
import { ATTIRE_VARIANTS } from '../../../game/js/attires.js';
import { MODEL_URLS } from '../../../game/js/assets.js';
import { FULL_ROSTER } from '../../../game/js/roster-full.js';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const gameDir = path.join(here, '..', '..', '..', 'game');
let fails = 0;
const ok = (cond, msg) => { console.log((cond ? 'PASS ' : 'FAIL ') + msg); if (!cond) fails++; };

const ladder = ATTIRE_VARIANTS['docfrank'].map(v => v.model);
console.log('LADDER (' + ladder.length + '):');
ladder.forEach((k, i) => console.log(`  ${i + 1}. ${k} — ${ATTIRE_VARIANTS['docfrank'][i].label}`));
const TRIPO_FRONT = ['doc-frank-big', 'doc-frank-wowomomo', 'doc-frank-wowomomo-big', 'doc-frank-hood', 'doc-frank-hood-big'];
ok(JSON.stringify(ladder.slice(0, 5)) === JSON.stringify(TRIPO_FRONT), 'first five ladder entries are his Tripo models');
ok(JSON.stringify(ladder.slice(7)) === JSON.stringify(['doc-frank-a1', 'doc-frank', 'doc-frank-machine-shop']),
  'back of ladder = pre-form (reskin lineage), Bosconovitch base, machine-shop reskin');
ok(ladder[0] === 'doc-frank-big', 'player default (ladder[0]) is Tripo doc-frank-big');

const main = FULL_ROSTER.find(c => c.id === 'docfrank');
ok(main && main.model === 'doc-frank-big', 'roster main entry model is doc-frank-big (Tripo)');
ok(main && main.forms && main.forms['doc-frank-a1'] && main.forms['doc-frank-a1'].up.target === 'doc-frank-big',
  'transform target doc-frank-big preserved (pre-form transforms up)');
ok(main && main.forms && main.forms['doc-frank-big'] && main.forms['doc-frank-big'].down.target === 'doc-frank-a1',
  'Tripo form transforms back down to pre-form');

function glbSkin(file) {
  const buf = fs.readFileSync(file);
  const jlen = buf.readUInt32LE(12);
  const js = JSON.parse(buf.subarray(20, 20 + jlen).toString('utf8'));
  return {
    skins: (js.skins || []).length,
    joints: js.skins && js.skins[0] ? js.skins[0].joints.length : 0,
    images: (js.images || []).length,
    anims: (js.animations || []).length,
  };
}

const KEYS = ['doc-frank-big', 'doc-frank-wowomomo', 'doc-frank-wowomomo-big', 'doc-frank-hood', 'doc-frank-hood-big',
  'doc-frank-frankenstein', 'doc-frank-frankenstein-big', 'doc-frank-a1', 'doc-frank', 'doc-frank-machine-shop'];
for (const k of KEYS) {
  const url = MODEL_URLS[k];
  ok(!!url, `MODEL_URLS has '${k}'`);
  if (!url) continue;
  const file = path.join(gameDir, url);
  ok(fs.existsSync(file), `'${k}' -> ${url} exists on disk`);
  if (!fs.existsSync(file)) continue;
  const s = glbSkin(file);
  ok(s.skins >= 1 && s.joints > 0, `'${k}' is RIGGED (skins=${s.skins}, joints=${s.joints}, images=${s.images}, anims=${s.anims})`);
  ok(s.images >= 1, `'${k}' has embedded texture images (${s.images})`);
}
console.log(fails === 0 ? '\nALL PROBE CHECKS PASS' : `\n${fails} PROBE CHECKS FAILED`);
process.exit(fails === 0 ? 0 : 1);
