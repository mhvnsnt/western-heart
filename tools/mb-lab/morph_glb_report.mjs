#!/usr/bin/env node
/* morph_glb_report.mjs — read a template GLB (plain or gltfpack -cc meshopt +
   KHR_mesh_quantization) and report, per morph target, the largest vertex
   displacement IN METERS after dequantization (node scale applied) and how
   many vertices it moves. Used to prove the packed templates still carry
   every slider's targets at usable precision.

   node tools/mb-lab/morph_glb_report.mjs <file.glb> [--json out.json]
   Needs the meshoptimizer decoder only for -cc files: it is looked up at
   game/vendor/addons/libs/meshopt_decoder.js (vendored, MIT). */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '..', '..');

export async function readGlb(file) {
  const buf = fs.readFileSync(file);
  const jsonLen = buf.readUInt32LE(12);
  const json = JSON.parse(buf.subarray(20, 20 + jsonLen).toString('utf8'));
  const binStart = 20 + jsonLen + 8;
  const bin = buf.subarray(binStart);
  const views = [];
  let dec = null;
  for (const [i, bv] of json.bufferViews.entries()) {
    const ext = bv.extensions && bv.extensions.EXT_meshopt_compression;
    if (!ext) { views[i] = bin.subarray(bv.byteOffset || 0, (bv.byteOffset || 0) + bv.byteLength); continue; }
    if (!dec) {
      const mod = await import(pathToFileURL(path.join(REPO, 'game/vendor/addons/libs/meshopt_decoder.js')).href);
      dec = mod.MeshoptDecoder; await dec.ready;
    }
    const src = bin.subarray(ext.byteOffset || 0, (ext.byteOffset || 0) + ext.byteLength);
    const out = new Uint8Array(ext.count * ext.byteStride);
    dec.decodeGltfBuffer(out, ext.count, ext.byteStride, src, ext.mode, ext.filter);
    views[i] = Buffer.from(out.buffer);
  }
  return { json, views };
}

const COMP = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4 };
const CT = { 5120: [Int8Array, 1], 5121: [Uint8Array, 1], 5122: [Int16Array, 2], 5123: [Uint16Array, 2], 5125: [Uint32Array, 4], 5126: [Float32Array, 4] };

export function readAccessor({ json, views }, idx) {
  const a = json.accessors[idx];
  const n = COMP[a.type];
  const out = new Float64Array(a.count * n);
  if (a.bufferView !== undefined) {
    const bv = json.bufferViews[a.bufferView];
    const [T, size] = CT[a.componentType];
    const stride = bv.byteStride || size * n;
    const v = views[a.bufferView];
    const dv = new DataView(v.buffer, v.byteOffset, v.byteLength);
    const get = { 5120: 'getInt8', 5121: 'getUint8', 5122: 'getInt16', 5123: 'getUint16', 5125: 'getUint32', 5126: 'getFloat32' }[a.componentType];
    for (let i = 0; i < a.count; i++) for (let c = 0; c < n; c++) {
      let x = dv[get]((a.byteOffset || 0) + i * stride + c * size, true);
      if (a.normalized) x = a.componentType === 5120 ? Math.max(x / 127, -1) : a.componentType === 5122 ? Math.max(x / 32767, -1) : a.componentType === 5121 ? x / 255 : a.componentType === 5123 ? x / 65535 : x;
      out[i * n + c] = x;
    }
    void T;
  }
  if (a.sparse) {
    const s = a.sparse;
    const iv = views[s.indices.bufferView]; const vv = views[s.values.bufferView];
    const idt = new DataView(iv.buffer, iv.byteOffset + (s.indices.byteOffset || 0));
    const vdt = new DataView(vv.buffer, vv.byteOffset + (s.values.byteOffset || 0));
    const isz = CT[s.indices.componentType][1];
    for (let k = 0; k < s.count; k++) {
      const vi = isz === 4 ? idt.getUint32(k * 4, true) : isz === 2 ? idt.getUint16(k * 2, true) : idt.getUint8(k);
      for (let c = 0; c < n; c++) out[vi * n + c] = vdt.getFloat32((k * n + c) * 4, true);
    }
  }
  return out;
}

/* scale of the node that instances mesh 0 (gltfpack puts the dequantization there) */
function meshNodeScale(json, meshIndex) {
  const node = json.nodes.find(n => n.mesh === meshIndex);
  const s = (node && node.scale) || [1, 1, 1];
  return s;
}

export async function report(file) {
  const g = await readGlb(file);
  const { json } = g;
  const out = { file: path.basename(file), bytes: fs.statSync(file).size, meshes: [] };
  for (const [mi, m] of json.meshes.entries()) {
    const names = (m.extras && m.extras.targetNames) || [];
    const s = meshNodeScale(json, mi);
    const targets = {};
    for (const p of m.primitives) {
      (p.targets || []).forEach((t, ti) => {
        if (t.POSITION === undefined) return;
        const d = readAccessor(g, t.POSITION);
        let max = 0, nz = 0;
        for (let i = 0; i < d.length; i += 3) {
          const x = d[i] * s[0], y = d[i + 1] * s[1], z = d[i + 2] * s[2];
          const L = Math.hypot(x, y, z);
          if (L > 1e-5) nz++;
          if (L > max) max = L;
        }
        const k = names[ti] || String(ti);
        const cur = targets[k] || { max_m: 0, nonzero: 0 };
        cur.max_m = Math.max(cur.max_m, +max.toFixed(5)); cur.nonzero += nz;
        targets[k] = cur;
      });
    }
    out.meshes.push({ name: m.name, primitives: m.primitives.length, targetNames: names.length, targets });
  }
  return out;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const file = process.argv[2];
  const r = await report(file);
  const j = process.argv.indexOf('--json');
  if (j > 0) fs.writeFileSync(process.argv[j + 1], JSON.stringify(r, null, 1));
  for (const m of r.meshes) {
    const vals = Object.entries(m.targets);
    const empty = vals.filter(([, v]) => v.nonzero === 0).map(([k]) => k);
    console.log(`${r.file} ${r.bytes} B  mesh ${m.name}: ${m.targetNames} targets, empty: ${empty.length ? empty.join(',') : 'none'}`);
  }
}
