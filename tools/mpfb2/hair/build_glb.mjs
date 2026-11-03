// build_glb.mjs — fit/<asset>/<template>.json (fit_proxies.py) -> GLB per template + one shared texture per asset.
// Usage: node build_glb.mjs <outRoot> [assetId ...]
// Each GLB: one mesh "<asset>" in HEAD-BONE-LOCAL space (parent it to the head bone, identity transform),
// morph targets named exactly like the template's face/head sliders, material tintable (greyscale texture x
// baseColorFactor). Compressed with gltfpack -cc; -tr keeps the texture as a shared sibling file (texture.png).
import { Document, NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import { execFileSync } from 'child_process';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const [, , outRoot, ...only] = process.argv;
const assets = JSON.parse(fs.readFileSync(path.join(HERE, 'assets.json'), 'utf8'));
const DEFAULT_COLOR = { hair: [0.16, 0.11, 0.08], eyebrows: [0.12, 0.09, 0.07], eyelashes: [0.05, 0.04, 0.04], beard: [0.14, 0.10, 0.07] };
const TEX_SIZE = { hair: 512, eyebrows: 256, eyelashes: 256, beard: 256 };

function mhmatTexture(a) {
  const d = path.join(HERE, 'mh', a.src); const nm = path.basename(a.src);
  const mat = fs.readFileSync(path.join(d, nm + '.mhmat'), 'utf8');
  const m = /^diffuseTexture\s+(\S+)/m.exec(mat);
  return path.join(d, m[1]);
}

/* greyscale + alpha, luminance normalised so baseColorFactor carries the colour (tint) */
async function makeTexture(a, out) {
  const size = TEX_SIZE[a.kind];
  if (a.kind === 'beard') {
    // procedural strand mask (original, CC0): short vertical-ish strands, density by variant
    const N = size, buf = Buffer.alloc(N * N * 4);
    let seed = 1234567; const rnd = () => ((seed = (seed * 1103515245 + 12345) >>> 0) / 4294967296);
    const density = a.src === 'beard-stubble' ? 0.28 : 0.62;
    for (let i = 0; i < N * N; i++) { buf[i * 4] = buf[i * 4 + 1] = buf[i * 4 + 2] = 255; buf[i * 4 + 3] = 0; }
    const strands = Math.floor(N * N * density * (a.src === 'beard-stubble' ? 0.08 : 0.12));
    for (let s = 0; s < strands; s++) {
      let x = rnd() * N, y = rnd() * N; const len = (a.src === 'beard-stubble' ? 2 : 4) + rnd() * 5;
      const dx = (rnd() - 0.5) * 0.6, lum = 170 + rnd() * 85;
      for (let k = 0; k < len; k++) {
        const xi = ((Math.floor(x) % N) + N) % N, yi = ((Math.floor(y) % N) + N) % N, o = (yi * N + xi) * 4;
        buf[o] = buf[o + 1] = buf[o + 2] = lum; buf[o + 3] = 255; x += dx; y += 1;
      }
    }
    await sharp(buf, { raw: { width: N, height: N, channels: 4 } }).png({ compressionLevel: 9 }).toFile(out);
    return;
  }
  const src = mhmatTexture(a);
  const img = sharp(src).ensureAlpha().resize(size, size, { fit: 'fill' });
  const { data, info } = await img.raw().toBuffer({ resolveWithObject: true });
  let mean = 0, cnt = 0;
  for (let i = 0; i < info.width * info.height; i++) { if (data[i * 4 + 3] > 128) { mean += 0.299 * data[i * 4] + 0.587 * data[i * 4 + 1] + 0.114 * data[i * 4 + 2]; cnt++; } }
  mean = cnt ? mean / cnt : 128;
  const k = 200 / Math.max(mean, 1);
  for (let i = 0; i < info.width * info.height; i++) {
    const l = Math.min(255, (0.299 * data[i * 4] + 0.587 * data[i * 4 + 1] + 0.114 * data[i * 4 + 2]) * k);
    data[i * 4] = data[i * 4 + 1] = data[i * 4 + 2] = l;
  }
  await sharp(data, { raw: { width: info.width, height: info.height, channels: 4 } }).png({ compressionLevel: 9, palette: true, colours: 64 }).toFile(out);
}

function computeNormals(pos, idx) {
  const n = new Float32Array(pos.length);
  for (let f = 0; f < idx.length; f += 3) {
    const [a, b, c] = [idx[f] * 3, idx[f + 1] * 3, idx[f + 2] * 3];
    const ux = pos[b] - pos[a], uy = pos[b + 1] - pos[a + 1], uz = pos[b + 2] - pos[a + 2];
    const vx = pos[c] - pos[a], vy = pos[c + 1] - pos[a + 1], vz = pos[c + 2] - pos[a + 2];
    const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
    for (const o of [a, b, c]) { n[o] += nx; n[o + 1] += ny; n[o + 2] += nz; }
  }
  for (let i = 0; i < n.length; i += 3) { const l = Math.hypot(n[i], n[i + 1], n[i + 2]) || 1; n[i] /= l; n[i + 1] /= l; n[i + 2] /= l; if (!(l > 0)) n[i + 1] = 1; }
  return n;
}

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const gltfpack = path.join(HERE, 'node_modules', '.bin', 'gltfpack');
const sizes = {};
for (const a of assets) {
  if (only.length && !only.includes(a.id)) continue;
  const fitDir = path.join(HERE, 'fit', a.id);
  if (!fs.existsSync(fitDir)) { console.warn('no fit for', a.id); continue; }
  const outDir = path.join(outRoot, a.id); fs.mkdirSync(outDir, { recursive: true });
  const texPath = path.join(outDir, 'texture.png');
  await makeTexture(a, texPath);
  sizes[a.id] = { texture: fs.statSync(texPath).size, glb: {} };
  for (const f of fs.readdirSync(fitDir)) {
    const tpl = f.replace(/\.json$/, '');
    const J = JSON.parse(fs.readFileSync(path.join(fitDir, f), 'utf8'));
    const doc = new Document(); const buffer = doc.createBuffer();
    const pos = new Float32Array(J.pos), uv = new Float32Array(J.uv);
    for (let i = 1; i < uv.length; i += 2) uv[i] = 1 - uv[i]; // obj v-up -> glTF v-down
    const idx = new Uint32Array(J.idx);
    const prim = doc.createPrimitive()
      .setAttribute('POSITION', doc.createAccessor().setType('VEC3').setArray(pos).setBuffer(buffer))
      .setAttribute('NORMAL', doc.createAccessor().setType('VEC3').setArray(computeNormals(pos, idx)).setBuffer(buffer))
      .setAttribute('TEXCOORD_0', doc.createAccessor().setType('VEC2').setArray(uv).setBuffer(buffer))
      .setIndices(doc.createAccessor().setType('SCALAR').setArray(idx).setBuffer(buffer));
    const names = Object.keys(J.targets);
    for (const nm of names) {
      prim.addTarget(doc.createPrimitiveTarget(nm).setAttribute('POSITION',
        doc.createAccessor().setType('VEC3').setArray(new Float32Array(J.targets[nm])).setBuffer(buffer)));
    }
    const tex = doc.createTexture('texture').setURI('texture.png').setMimeType('image/png').setImage(fs.readFileSync(texPath));
    const c = DEFAULT_COLOR[a.kind];
    const mat = doc.createMaterial(a.id).setBaseColorFactor([c[0], c[1], c[2], 1]).setBaseColorTexture(tex)
      .setDoubleSided(true).setAlphaMode('MASK').setAlphaCutoff(a.kind === 'beard' ? 0.5 : 0.35)
      .setRoughnessFactor(0.75).setMetallicFactor(0);
    prim.setMaterial(mat);
    const mesh = doc.createMesh(a.id).addPrimitive(prim).setWeights(names.map(() => 0)).setExtras({ targetNames: names });
    const node = doc.createNode(a.id).setMesh(mesh)
      .setExtras({ wh_part: a.id, wh_kind: a.kind, wh_template: tpl, wh_space: 'head-bone-local', license: 'CC0-1.0' });
    doc.createScene('scene').addChild(node);
    const tmp = path.join(outDir, `_tmp_${tpl}.gltf`);
    await io.write(tmp, doc);
    const out = path.join(outDir, `${tpl}.glb`);
    execFileSync(gltfpack, ['-i', tmp, '-o', out, '-cc', '-tr', '-kn', '-km', '-ke'], { stdio: 'pipe' });
    for (const g of fs.readdirSync(outDir)) if (g.startsWith('_tmp_')) fs.unlinkSync(path.join(outDir, g));
    sizes[a.id].glb[tpl] = fs.statSync(out).size;
  }
  const tot = Object.values(sizes[a.id].glb).reduce((s, v) => s + v, 0);
  console.log(a.id, 'texture', sizes[a.id].texture, 'glb total', tot, 'max', Math.max(...Object.values(sizes[a.id].glb)));
}
fs.writeFileSync(path.join(outRoot, 'sizes.json'), JSON.stringify(sizes, null, 1));
