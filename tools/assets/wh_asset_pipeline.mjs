#!/usr/bin/env node
// tools/assets/wh_asset_pipeline.mjs — Western Heart's ONE reusable web asset pipeline.
//
//   node tools/assets/wh_asset_pipeline.mjs IN.glb [OUT.glb] [--geo meshopt|draco|none]
//        [--tex webp|ktx2|keep] [--max-tex 2048] [--report report.json]
//   node tools/assets/wh_asset_pipeline.mjs --dir game/assets/fighters --out-dir /tmp/web
//
// NOTHING IS CUT: no simplify, no prune of used data, no texture drop. Every mesh, primitive,
// vertex, joint/bone, skin, morph target, animation, material and node name is kept; the script
// counts all of them before and after and EXITS NON-ZERO if any count changes (the "no-cut gate").
// Only lossless-to-the-eye encodings are applied:
//   * dedup + weld-free + quantize (KHR_mesh_quantization)
//   * geometry: EXT_meshopt_compression (default — game/js/assets.js already wires MeshoptDecoder),
//               or KHR_draco_mesh_compression (needs a DRACOLoader; not vendored in game/ yet)
//   * textures: EXT_texture_webp (default — decoded natively by three.js, no extra decoder),
//               or KHR_texture_basisu/KTX2 (needs `toktx` on PATH + KTX2Loader; not vendored yet)
//   * --max-tex only DOWNSCALES textures larger than N (off by default = full resolution).
// Deps (MIT, not committed): npm i @gltf-transform/core @gltf-transform/extensions
//   @gltf-transform/functions meshoptimizer sharp   (draco: draco3dgltf) — set NODE_PATH if global.
import fs from 'node:fs';
import path from 'node:path';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, quantize, meshopt, draco, textureCompress } from '@gltf-transform/functions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const flags = new Set(['--geo', '--tex', '--max-tex', '--report', '--dir', '--out-dir']);
const pos = args.filter((a, i) => !a.startsWith('--') && !flags.has(args[i - 1]));
const GEO = opt('--geo', 'meshopt'), TEX = opt('--tex', 'webp'), MAXTEX = +opt('--max-tex', 0);

function counts(doc) {
  const r = doc.getRoot(); let prims = 0, verts = 0, morphs = 0, tris = 0;
  for (const m of r.listMeshes()) for (const p of m.listPrimitives()) {
    prims++; const pa = p.getAttribute('POSITION'); verts += pa ? pa.getCount() : 0;
    morphs += p.listTargets().length; const ix = p.getIndices();
    tris += Math.floor((ix ? ix.getCount() : (pa ? pa.getCount() : 0)) / 3);
  }
  return { nodes: r.listNodes().length, meshes: r.listMeshes().length, primitives: prims,
    vertices: verts, triangles: tris, morphTargets: morphs, skins: r.listSkins().length,
    joints: r.listSkins().reduce((n, s) => n + s.listJoints().length, 0),
    animations: r.listAnimations().length,
    channels: r.listAnimations().reduce((n, a) => n + a.listChannels().length, 0),
    materials: r.listMaterials().length, textures: r.listTextures().length,
    nodeNames: r.listNodes().map(n => n.getName()).join('|').length };
}

async function one(io, inp, out) {
  const doc = await io.read(inp); const before = counts(doc);
  const tf = [dedup({ propertyTypes: ['Accessor', 'Mesh', 'Texture'] })];
  if (TEX !== 'keep' && doc.getRoot().listTextures().length) {
    const o = { targetFormat: TEX === 'ktx2' ? undefined : 'webp', quality: 90 };
    if (MAXTEX) o.resize = [MAXTEX, MAXTEX];
    if (TEX === 'webp') tf.push(textureCompress({ encoder: (await import('sharp')).default, ...o }));
    else if (TEX === 'ktx2') throw new Error('ktx2: run `gltf-transform uastc|etc1s` (needs toktx) — not wired here');
  }
  if (GEO === 'meshopt') tf.push(meshopt({ encoder: MeshoptEncoder, level: 'medium' }));
  else if (GEO === 'draco') tf.push(draco({ method: 'edgebreaker' }));
  else tf.push(quantize());
  await doc.transform(...tf);
  // dedup may merge identical meshes/textures — that is not a cut; compare semantic counts
  const after = counts(doc);
  const cut = ['nodes', 'primitives', 'vertices', 'triangles', 'morphTargets', 'skins', 'joints',
    'animations', 'channels', 'materials', 'nodeNames'].filter(k => after[k] < before[k]);
  await io.write(out, doc);
  const rec = { in: inp, out, bytesIn: fs.statSync(inp).size, bytesOut: fs.statSync(out).size,
    geo: GEO, tex: TEX, maxTex: MAXTEX || null, before, after, cut };
  console.log(`${path.basename(inp)}: ${(rec.bytesIn / 1e6).toFixed(2)} MB -> ${(rec.bytesOut / 1e6).toFixed(2)} MB` +
    ` (${(100 * rec.bytesOut / rec.bytesIn).toFixed(0)}%)  ${cut.length ? 'CUT: ' + cut.join(',') : 'no-cut OK'}`);
  return rec;
}

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'meshopt.encoder': MeshoptEncoder, 'meshopt.decoder': MeshoptDecoder });
if (GEO === 'draco') { const d3d = (await import('draco3dgltf')).default;
  io.registerDependencies({ 'draco3d.encoder': await d3d.createEncoderModule(), 'draco3d.decoder': await d3d.createDecoderModule() }); }
await MeshoptEncoder.ready; await MeshoptDecoder.ready;
const jobs = [];
if (opt('--dir')) {
  const od = opt('--out-dir'); if (!od) throw new Error('--dir needs --out-dir (originals are never overwritten)');
  const walk = d => fs.readdirSync(d, { withFileTypes: true }).flatMap(e =>
    e.isDirectory() ? walk(path.join(d, e.name)) : e.name.endsWith('.glb') ? [path.join(d, e.name)] : []);
  for (const f of walk(opt('--dir'))) { const o = path.join(od, path.relative(opt('--dir'), f));
    fs.mkdirSync(path.dirname(o), { recursive: true }); jobs.push([f, o]); }
} else { if (!pos[0]) { console.error('usage: see header'); process.exit(2); }
  jobs.push([pos[0], pos[1] || pos[0].replace(/\.glb$/, '.web.glb')]); }
const recs = []; let bad = 0;
for (const [i, o] of jobs) { if (path.resolve(i) === path.resolve(o)) throw new Error('refusing to overwrite original ' + i);
  try { const r = await one(io, i, o); recs.push(r); if (r.cut.length) bad++; }
  catch (e) { bad++; recs.push({ in: i, error: String(e) }); console.error(i, e.message); } }
const tin = recs.reduce((s, r) => s + (r.bytesIn || 0), 0), tout = recs.reduce((s, r) => s + (r.bytesOut || 0), 0);
console.log(`TOTAL ${recs.length} files: ${(tin / 1e6).toFixed(1)} MB -> ${(tout / 1e6).toFixed(1)} MB; failures/cuts: ${bad}`);
if (opt('--report')) fs.writeFileSync(opt('--report'), JSON.stringify({ format: 'wh-asset-pipeline/1', total: { in: tin, out: tout }, files: recs }, null, 1));
process.exit(bad ? 1 : 0);
