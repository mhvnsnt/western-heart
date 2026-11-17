// build_glb.mjs — CLOTHING + ACCESSORIES phase: fit/<item>/<template>.json (shell_fit.py, Blender) -> one GLB per
// item per template. Adapted from tools/mpfb2/hair/build_glb.mjs (hair phase).
// Usage: WH_TEMPLATE_DIR=<dir with the 9 template GLBs> node build_glb.mjs <outRoot> [itemId ...]
// Each GLB: one skinned mesh "<item>" in the template's MODEL BIND space (metres), JOINTS_0/WEIGHTS_0 from the
// template's own skin weights (Blender vertex groups), morph targets named exactly like the template's body sliders,
// an untextured tintable PBR material (baseColorFactor = the item's default colour; the suite recolours it).
// mesh.extras.wh_hide = the template body vertices the garment covers, per body primitive (skin / generic / nails), as
// run-length [start, count, start, count, ...] lists — the runtime drops body triangles whose 3 vertices are all
// hidden (game/js/fitted-parts.js), so the body can't poke through under the cloth.
// Compressed with gltfpack -cc (meshopt); budget <= 300 KB per GLB.
import { Document, NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'meshoptimizer';
import fs from 'fs';
import path from 'path';
import { execFileSync } from 'child_process';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const [, , outRoot, ...only] = process.argv;
const items = JSON.parse(fs.readFileSync(path.join(HERE, 'items.json'), 'utf8'));
const FIT = process.env.WH_FIT_DIR || path.join(HERE, 'fit');
const TPL_DIR = process.env.WH_TEMPLATE_DIR || path.join(HERE, '..', '..', '..', 'customization', 'templates', 'meshes');
const BUDGET = 300 * 1024;

function computeNormals(pos, idx) {
  const n = new Float32Array(pos.length);
  for (let f = 0; f < idx.length; f += 3) {
    const [a, b, c] = [idx[f] * 3, idx[f + 1] * 3, idx[f + 2] * 3];
    const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2];
    const vx = pos[c] - pos[a], vy = pos[c + 1] - pos[a + 1], vz = pos[c + 2] - pos[a + 2];
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
    for (const o of [a, b, c]) { n[o] += nx; n[o + 1] += ny; n[o + 2] += nz; }
  }
  for (let i = 0; i < n.length; i += 3) { const l = Math.hypot(n[i], n[i + 1], n[i + 2]); if (l > 0) { n[i] /= l; n[i + 1] /= l; n[i + 2] /= l; } else n[i + 1] = 1; }
  return n;
}
/* sorted vertex index list -> run-length [start, count, ...] */
export function toRuns(list) {
  const s = [...new Set(list)].sort((a, b) => a - b); const out = [];
  for (let i = 0; i < s.length;) { let j = i; while (j + 1 < s.length && s[j + 1] === s[j] + 1) j++; out.push(s[i], j - i + 1); i = j + 1; }
  return out;
}
/* gltfpack keeps only targetNames in mesh extras: rewrite the packed GLB's JSON chunk (binary chunk untouched) so
   mesh.extras + the mesh node's extras carry the wh_* fields, and restore the mesh node's name. */
function patchExtras(file, extras) {
  const b = fs.readFileSync(file); const jl = b.readUInt32LE(12);
  const j = JSON.parse(b.subarray(20, 20 + jl).toString('utf8').replace(/[\s\0]+$/, ''));
  for (const m of j.meshes) m.extras = { ...(m.extras || {}), ...extras };
  for (const n of j.nodes) if (n.mesh !== undefined) { n.name = extras.wh_part; n.extras = { ...(n.extras || {}), ...extras }; }
  let js = Buffer.from(JSON.stringify(j), 'utf8'); const pad = (4 - (js.length % 4)) % 4; js = Buffer.concat([js, Buffer.alloc(pad, 0x20)]);
  const rest = b.subarray(20 + jl);
  const head = Buffer.alloc(20); head.writeUInt32LE(0x46546c67, 0); head.writeUInt32LE(2, 4);
  head.writeUInt32LE(20 + js.length + rest.length, 8); head.writeUInt32LE(js.length, 12); head.writeUInt32LE(0x4e4f534a, 16);
  fs.writeFileSync(file, Buffer.concat([head, js, rest]));
}
const mat4 = { invert(out, m) {
  const a = [0, 1, 2, 3].map((r) => [0, 1, 2, 3].map((c) => m[c * 4 + r]).concat([0, 1, 2, 3].map((k) => (k === r ? 1 : 0))));
  for (let c = 0; c < 4; c++) {
    let p = c; for (let r = c + 1; r < 4; r++) if (Math.abs(a[r][c]) > Math.abs(a[p][c])) p = r;
    [a[c], a[p]] = [a[p], a[c]]; const d = a[c][c]; for (let k = 0; k < 8; k++) a[c][k] /= d;
    for (let r = 0; r < 4; r++) if (r !== c) { const f = a[r][c]; for (let k = 0; k < 8; k++) a[r][k] -= f * a[c][k]; }
  }
  for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) out[c * 4 + r] = a[r][4 + c];
  return out;
} };

await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder });
const _tj = {};
async function templateJoints(tpl) {
  if (_tj[tpl]) return _tj[tpl];
  const d = await io.read(path.join(TPL_DIR, tpl + '.glb'));
  const sk = d.getRoot().listSkins()[0]; const acc = sk.getInverseBindMatrices();
  const js = sk.listJoints();
  return (_tj[tpl] = { names: js.map((j) => j.getName()), world: js.map((j) => j.getWorldMatrix()), ibm: js.map((j, i) => acc.getElement(i, [])) });
}
const gltfpack = path.join(HERE, 'node_modules', '.bin', 'gltfpack');
const sizes = {}; let over = 0;
for (const it of items) {
  if (only.length && !only.includes(it.id)) continue;
  const fitDir = path.join(FIT, it.id);
  if (!fs.existsSync(fitDir)) { console.warn('no fit for', it.id); continue; }
  const outDir = path.join(outRoot, it.id); fs.mkdirSync(outDir, { recursive: true });
  sizes[it.id] = {};
  for (const f of fs.readdirSync(fitDir).filter((f) => f.endsWith('.json')).sort()) {
    const tpl = f.replace(/\.json$/, '');
    const J = JSON.parse(fs.readFileSync(path.join(fitDir, f), 'utf8'));
    const T = await templateJoints(tpl);
    if (J.joint_names && J.joint_names.some((n, i) => n !== T.names[i])) throw new Error(`${it.id}/${tpl}: joint order differs from template skin`);
    const doc = new Document(); const buffer = doc.createBuffer();
    const pos = new Float32Array(J.pos), idx = new Uint32Array(J.idx);
    const prim = doc.createPrimitive()
      .setAttribute('POSITION', doc.createAccessor().setType('VEC3').setArray(pos).setBuffer(buffer))
      .setAttribute('NORMAL', doc.createAccessor().setType('VEC3').setArray(computeNormals(pos, idx)).setBuffer(buffer))
      .setIndices(doc.createAccessor().setType('SCALAR').setArray(idx).setBuffer(buffer));
    const used = [...new Set(J.joints.filter((j, i) => J.weights[i] > 0))].sort((x, y) => x - y);
    const local = new Uint8Array(J.joints.map((j, i) => (J.weights[i] > 0 ? used.indexOf(j) : 0)));
    prim.setAttribute('JOINTS_0', doc.createAccessor().setType('VEC4').setArray(local).setBuffer(buffer));
    prim.setAttribute('WEIGHTS_0', doc.createAccessor().setType('VEC4').setArray(new Float32Array(J.weights)).setBuffer(buffer));
    const names = Object.keys(J.targets);
    for (const nm of names) {
      prim.addTarget(doc.createPrimitiveTarget(nm).setAttribute('POSITION',
        doc.createAccessor().setType('VEC3').setArray(new Float32Array(J.targets[nm])).setBuffer(buffer)));
    }
    const c = it.color;
    const mat = doc.createMaterial(it.id).setBaseColorFactor([c[0], c[1], c[2], 1]).setRoughnessFactor(it.rough ?? 0.6).setMetallicFactor(0);
    prim.setMaterial(mat);
    const mesh = doc.createMesh(it.id).addPrimitive(prim).setWeights(names.map(() => 0)).setExtras({ targetNames: names });
    const hide = {}; for (const [k, v] of Object.entries(J.hide || {})) if (v.length) hide[k] = toRuns(v);
    const node = doc.createNode(it.id).setMesh(mesh).setExtras({
      wh_part: it.id, wh_kind: 'clothing', wh_family: it.acc ? 'accessories' : 'clothing', wh_template: tpl,
      wh_space: 'model-bind', wh_skinned: true, wh_layer_offset_m: it.offset, wh_hide: hide, wh_hide_encoding: 'runs',
      license: 'CC0-1.0', generator: 'Western Heart shell_fit.py (Blender 4.3.2) — original geometry generated on the template body' });
    const scene = doc.createScene('scene');
    const jnodes = used.map((ti) => { const n = doc.createNode('wh_j_' + T.names[ti]).setMatrix(T.world[ti]); scene.addChild(n); return n; });
    const ibm = new Float32Array(used.length * 16); used.forEach((ti, k) => ibm.set(mat4.invert([], T.world[ti]), k * 16));
    const tplIbm = new Float32Array(used.length * 16); used.forEach((ti, k) => tplIbm.set(T.ibm[ti], k * 16));
    const skin = doc.createSkin('wh_skin').setInverseBindMatrices(doc.createAccessor().setType('MAT4').setArray(ibm).setBuffer(buffer));
    jnodes.forEach((n) => skin.addJoint(n));
    node.setSkin(skin);
    node.setExtras({ ...node.getExtras(), wh_joint_index: used, wh_joint_ibm: Array.from(tplIbm) });
    scene.addChild(node);
    // gltfpack re-parents skinned meshes onto fresh nodes (node name + extras lost); mesh extras survive -ke, so the
    // runtime reads everything from mesh.extras (node extras kept too for unpacked use).
    mesh.setExtras({ targetNames: names, ...node.getExtras() });
    const tmp = path.join(outDir, `_tmp_${tpl}.gltf`);
    await io.write(tmp, doc);
    const out = path.join(outDir, `${tpl}.glb`);
    execFileSync(gltfpack, ['-i', tmp, '-o', out, '-cc', '-kn', '-km', '-ke', '-vp', '14'], { stdio: 'pipe' });
    for (const g of fs.readdirSync(outDir)) if (g.startsWith('_tmp_')) fs.unlinkSync(path.join(outDir, g));
    patchExtras(out, { targetNames: names, ...node.getExtras() });
    const sz = fs.statSync(out).size; sizes[it.id][tpl] = sz; if (sz > BUDGET) { over++; console.warn('OVER BUDGET', it.id, tpl, sz); }
  }
  const v = Object.values(sizes[it.id]);
  console.log(it.id, 'glbs', v.length, 'total', v.reduce((s, x) => s + x, 0), 'max', Math.max(...v));
}
fs.writeFileSync(path.join(outRoot, 'sizes.json'), JSON.stringify(sizes, null, 1));
if (over) { console.error(over, 'GLBs over the 300 KB budget'); process.exit(2); }
