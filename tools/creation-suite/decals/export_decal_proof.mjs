#!/usr/bin/env node
/* export_decal_proof.mjs — run the GAME's decal pipeline (game/js/decal-layers.js) on every template body and
   write each layer's projected patch as an OBJ (+ a layers.json) so Blender can render what the fight draws.
   Usage (repo root): node tools/creation-suite/decals/export_decal_proof.mjs OUT_DIR
   The sample attire: one No Mercy tattoo on each of the 11 body regions + 3 face scars + back lashes over the
   back tattoo (layer order). Rendered by render_decal_proof_blender.py. */
import { readFileSync, writeFileSync, mkdirSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { readSkinMesh } from './glb-skin.mjs';
import { createLayer, resolveAnchor, projectDecal, layerSize, defaultPlacement } from '../../../game/js/decal-layers.js';

const out = process.argv[2] || '/tmp/wh-decal-proof';
const TABLE = JSON.parse(readFileSync('customization/templates/decal-placements.json', 'utf8'));
const TAT = 'teardown/wwf-no-mercy/textures/rom/tattoo';
const tats = readdirSync(TAT).filter((f) => f.endsWith('.png')).sort();
const pick = [0, 1, 2, 3, 6, 8, 9, 13, 17, 18, 22];
const regions = ['chest', 'back', 'neck', 'upper_arm_L', 'upper_arm_R', 'forearm_L', 'forearm_R', 'thigh_L', 'thigh_R', 'calf_L', 'calf_R'];
const pngSize = (f) => { const b = readFileSync(f); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };
for (const t of Object.keys(TABLE.templates)) {
  const m = await readSkinMesh(`customization/templates/meshes/${t}.glb`);
  const dir = join(out, t); mkdirSync(dir, { recursive: true });
  const layers = regions.map((r, i) => {
    const d = defaultPlacement(TABLE, t, r);
    return { l: createLayer({ id: `tat${i}`, part_id: tats[pick[i]], kind: 'tattoo', region: r, u: d.u, v: d.v, scaleX: 1.6, scaleY: 1.6 }), asset: `${TAT}/${tats[pick[i]]}` };
  });
  const S = 'customization/decal-library/scars';
  for (const [id, region, u, v, sc] of [['cheek-slash', 'face', 0.1, 0.12, 1], ['brow-cut', 'face', 0.93, 0.42, 1], ['eye-cross', 'face', 0.07, 0.32, 0.9], ['back-lashes', 'back', 0.5, 0.66, 1]]) {
    layers.push({ l: createLayer({ id: 'scar-' + id, part_id: 'wh-scar-' + id, kind: 'scar', region, u, v, scaleX: sc, scaleY: sc }), asset: `${S}/${id}.png` });
  }
  const meta = [];
  for (const [i, { l, asset }] of layers.entries()) {
    const a = resolveAnchor(m, l.region, l.u, l.v);
    if (!a) { meta.push({ id: l.id, miss: true }); continue; }
    const [w, h] = pngSize(asset);
    const size = layerSize(l, l.region, w / h, defaultPlacement(TABLE, t, l.region).size);
    const p = projectDecal(m, a, { ...size, rotation: l.rotation, mirror: l.mirror, offset: 0.0015 + i * 0.0002 });
    let obj = `# ${l.id} ${l.region}\n`;
    const n = p.positions.length / 3;
    for (let k = 0; k < n; k++) obj += `v ${p.positions[k * 3]} ${p.positions[k * 3 + 1]} ${p.positions[k * 3 + 2]}\n`;
    for (let k = 0; k < n; k++) obj += `vt ${p.uvs[k * 2]} ${p.uvs[k * 2 + 1]}\n`;
    for (let k = 0; k < n; k += 3) obj += `f ${k + 1}/${k + 1} ${k + 2}/${k + 2} ${k + 3}/${k + 3}\n`;
    writeFileSync(join(dir, `${String(i).padStart(2, '0')}_${l.id}.obj`), obj);
    meta.push({ id: l.id, region: l.region, kind: l.kind, asset, tris: n / 3, inRegion: a.inRegion, searchedV: a.searchedV ?? null });
  }
  writeFileSync(join(dir, 'layers.json'), JSON.stringify(meta, null, 1));
  console.log(t, meta.map((x) => `${x.id}:${x.miss ? 'MISS' : x.tris}`).join(' '));
}
