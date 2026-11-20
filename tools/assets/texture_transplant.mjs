#!/usr/bin/env node
// tools/assets/texture_transplant.mjs — restore a model's REAL textures from an
// earlier textured copy of the SAME model (git history, the owner's source
// export, or an intake folder). Geometry, skin, rig and weights of the target
// are untouched; only material texture slots + colour factors are copied, by
// material NAME. Never point --from at another character's model.
//   node tools/assets/texture_transplant.mjs --target cur.glb --from old.glb --out fixed.glb [--mats a,b,c | --all-untextured]
//   node tools/assets/texture_transplant.mjs --target cur.glb --images dir --map mat=file.png[,mat2=file2.png] --out fixed.glb
// Requires @gltf-transform (GLTFX_MODULES, default /workspace/tools/gltfx/node_modules).
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const mods = process.env.GLTFX_MODULES || '/workspace/tools/gltfx/node_modules';
const req = createRequire(path.join(mods, 'x.js'));
const { NodeIO } = req('@gltf-transform/core');
const { ALL_EXTENSIONS } = req('@gltf-transform/extensions');
const a = process.argv.slice(2); const opt = k => { const i = a.indexOf(k); return i < 0 ? null : a[i + 1]; };
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(opt('--target'));
const mats = doc.getRoot().listMaterials();
const hasUV = m => m.listParents().some(p => p.propertyType === 'Primitive' && p.getAttribute('TEXCOORD_0'));
const untextured = m => !m.getBaseColorTexture();
const want = opt('--mats') ? new Set(opt('--mats').split(',')) : null;
const SLOTS = ['BaseColor', 'Normal', 'MetallicRoughness', 'Occlusion', 'Emissive'];
const cache = new Map();
const copyTex = (t) => {
  const key = t.getName() + '|' + t.getURI() + '|' + t.getImage()?.byteLength;
  if (!cache.has(key)) cache.set(key, doc.createTexture(t.getName()).setImage(t.getImage()).setMimeType(t.getMimeType()).setURI(t.getURI()));
  return cache.get(key);
};
let changed = [];
if (opt('--from')) {
  const src = await io.read(opt('--from'));
  const byName = new Map(src.getRoot().listMaterials().map(m => [m.getName(), m]));
  for (const m of mats) {
    if (want ? !want.has(m.getName()) : !(a.includes('--all-untextured') && untextured(m))) continue;
    const s = byName.get(m.getName()); if (!s || !s.getBaseColorTexture()) { console.log('no textured source for', m.getName()); continue; }
    if (!hasUV(m)) { console.log('target has no UVs for', m.getName()); continue; }
    for (const sl of SLOTS) { const t = s['get' + sl + 'Texture'](); if (t) { m['set' + sl + 'Texture'](copyTex(t));
      const si = s['get' + sl + 'TextureInfo'](), ti = m['get' + sl + 'TextureInfo'](); if (si && ti) ti.setTexCoord(si.getTexCoord()); } }
    m.setBaseColorFactor(s.getBaseColorFactor()).setAlphaMode(s.getAlphaMode()).setAlphaCutoff(s.getAlphaCutoff()).setDoubleSided(s.getDoubleSided());
    changed.push(m.getName());
  }
} else if (opt('--map')) {
  const dir = opt('--images') || '.';
  for (const pair of opt('--map').split(',')) {
    const [mn, file] = pair.split('=');
    const targets = mats.filter(m => m.getName() === mn); if (!targets.length) { console.log('no material', mn); continue; }
    const bytes = new Uint8Array(fs.readFileSync(path.join(dir, file)));
    const tex = doc.createTexture(path.basename(file, path.extname(file))).setImage(bytes).setMimeType(file.endsWith('.png') ? 'image/png' : 'image/jpeg');
    for (const m of targets) { if (!hasUV(m)) { console.log('target has no UVs for', mn); continue; } m.setBaseColorTexture(tex).setBaseColorFactor([1, 1, 1, 1]); changed.push(mn); }
  }
}
await io.write(opt('--out'), doc);
console.log('transplanted:', changed.join(', ') || '(none)');
