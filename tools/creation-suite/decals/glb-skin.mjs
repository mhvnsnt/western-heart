/* ============================================================
   glb-skin.mjs — read a template body GLB's SKIN mesh in Node
   (creation suite TATTOOS + SCARS phase, 2026-11-02)

   The 9 template bodies (customization/templates/meshes/*.glb) are
   gltfpack output: EXT_meshopt_compression + KHR_mesh_quantization.
   Blender 4.3's glTF importer refuses EXT_meshopt_compression, and Node
   has no GLTFLoader without a DOM, so this is a tiny dependency-free
   reader that uses the game's OWN vendored decoder
   (game/vendor/addons/libs/meshopt_decoder.js, MIT) to:
     - decode every meshopt bufferView,
     - dequantize accessors (normalized ints -> floats),
     - return the skin primitive (material name contains "skin") in
       bind-pose model space: mesh-node TRS applied to POSITION, exactly
       what three.js renders for a SkinnedMesh at rest,
     - return each joint's bind-pose position (inverse of its
       inverseBindMatrix), keyed by joint name.
   Also exports decodeGlbToPlain(): the same GLB with meshopt removed, so
   Blender can import it (tools/creation-suite/decals/decode_glb.mjs).

   Used by: test/decal-layers.test.mjs (numeric placement probe) and
   tools/creation-suite/decals/decode_glb.mjs (Blender hand-off).
   ============================================================ */
import { readFileSync } from 'node:fs';
import { MeshoptDecoder } from '../../../game/vendor/addons/libs/meshopt_decoder.js';

const COMP = { 5120: [Int8Array, 1], 5121: [Uint8Array, 1], 5122: [Int16Array, 2], 5123: [Uint16Array, 2], 5125: [Uint32Array, 4], 5126: [Float32Array, 4] };
const NCOMP = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT4: 16 };
const NORM = { 5120: (v) => Math.max(v / 127, -1), 5121: (v) => v / 255, 5122: (v) => Math.max(v / 32767, -1), 5123: (v) => v / 65535 };

export function parseGlb(bytes) {
  const buf = Buffer.isBuffer(bytes) ? bytes : Buffer.from(bytes);
  if (buf.readUInt32LE(0) !== 0x46546c67) throw new Error('not a GLB');
  let off = 12, json = null, bin = null;
  while (off < buf.length) {
    const len = buf.readUInt32LE(off), type = buf.readUInt32LE(off + 4);
    const chunk = buf.subarray(off + 8, off + 8 + len);
    if (type === 0x4e4f534a) json = JSON.parse(chunk.toString('utf8'));
    else if (type === 0x004e4942) bin = chunk;
    off += 8 + len;
  }
  return { json, bin };
}

/* Decode all bufferViews into standalone Uint8Arrays (meshopt or plain). */
export async function decodeViews(json, bin) {
  await MeshoptDecoder.ready;
  return json.bufferViews.map((bv) => {
    const ext = bv.extensions && bv.extensions.EXT_meshopt_compression;
    if (ext) {
      const src = new Uint8Array(bin.buffer, bin.byteOffset + (ext.byteOffset || 0), ext.byteLength);
      const out = new Uint8Array(ext.count * ext.byteStride);
      MeshoptDecoder.decodeGltfBuffer(out, ext.count, ext.byteStride, src, ext.mode, ext.filter || 'NONE');
      return out;
    }
    if (bv.buffer !== 0 || !bin) return null; // fallback (zero-filled) buffer with no meshopt payload
    return new Uint8Array(bin.buffer, bin.byteOffset + (bv.byteOffset || 0), bv.byteLength);
  });
}

export function readAccessor(json, views, index) {
  const acc = json.accessors[index];
  const [Arr, size] = COMP[acc.componentType];
  const n = NCOMP[acc.type];
  const bv = json.bufferViews[acc.bufferView];
  const view = views[acc.bufferView];
  const stride = (bv.extensions?.EXT_meshopt_compression?.byteStride) || bv.byteStride || size * n;
  const out = new Float32Array(acc.count * n);
  const dv = new DataView(view.buffer, view.byteOffset, view.byteLength);
  const getter = { 5120: 'getInt8', 5121: 'getUint8', 5122: 'getInt16', 5123: 'getUint16', 5125: 'getUint32', 5126: 'getFloat32' }[acc.componentType];
  const norm = acc.normalized ? NORM[acc.componentType] : null;
  for (let i = 0; i < acc.count; i++) {
    const base = (acc.byteOffset || 0) + i * stride;
    for (let c = 0; c < n; c++) {
      const v = dv[getter](base + c * size, true);
      out[i * n + c] = norm ? norm(v) : v;
    }
  }
  return { data: out, n, count: acc.count };
}

function trsMatrix(node) {
  const t = node.translation || [0, 0, 0], r = node.rotation || [0, 0, 0, 1], s = node.scale || [1, 1, 1];
  const [x, y, z, w] = r;
  const m = [
    (1 - 2 * (y * y + z * z)) * s[0], 2 * (x * y + z * w) * s[0], 2 * (x * z - y * w) * s[0], 0,
    2 * (x * y - z * w) * s[1], (1 - 2 * (x * x + z * z)) * s[1], 2 * (y * z + x * w) * s[1], 0,
    2 * (x * z + y * w) * s[2], 2 * (y * z - x * w) * s[2], (1 - 2 * (x * x + y * y)) * s[2], 0,
    t[0], t[1], t[2], 1];
  return m; // column-major
}
const apply = (m, x, y, z) => [m[0] * x + m[4] * y + m[8] * z + m[12], m[1] * x + m[5] * y + m[9] * z + m[13], m[2] * x + m[6] * y + m[10] * z + m[14]];
function invertAffineTranslation(m) {
  // position of the joint in bind = inverse(IBM) applied to origin
  const a = m[0], b = m[4], c = m[8], d = m[1], e = m[5], f = m[9], g = m[2], h = m[6], i = m[10];
  const det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
  const inv = [(e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det,
    (f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det,
    (d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det];
  const tx = -m[12], ty = -m[13], tz = -m[14];
  return [inv[0] * tx + inv[1] * ty + inv[2] * tz, inv[3] * tx + inv[4] * ty + inv[5] * tz, inv[6] * tx + inv[7] * ty + inv[8] * tz];
}

/**
 * Read the skin primitive + joint bind positions of a template GLB.
 * Returns { positions: Float32Array(n*3), normals, indices: Uint32Array,
 *   joints: Uint8Array(n*4)->Float32, weights, jointNames: string[],
 *   bones: { name: [x,y,z] }, material }.
 */
export async function readSkinMesh(bytesOrPath) {
  const bytes = typeof bytesOrPath === 'string' ? readFileSync(bytesOrPath) : bytesOrPath;
  const { json, bin } = parseGlb(bytes);
  const views = await decodeViews(json, bin);
  const meshNodeIdx = json.nodes.findIndex((n) => n.mesh !== undefined && n.skin !== undefined);
  const meshNode = json.nodes[meshNodeIdx];
  const mesh = json.meshes[meshNode.mesh];
  const prim = mesh.primitives.find((p) => /skin/i.test((json.materials[p.material] || {}).name || ''));
  if (!prim) throw new Error('no skin primitive');
  const M = trsMatrix(meshNode);
  const pos = readAccessor(json, views, prim.attributes.POSITION);
  const positions = new Float32Array(pos.count * 3);
  for (let i = 0; i < pos.count; i++) {
    const p = apply(M, pos.data[i * 3], pos.data[i * 3 + 1], pos.data[i * 3 + 2]);
    positions[i * 3] = p[0]; positions[i * 3 + 1] = p[1]; positions[i * 3 + 2] = p[2];
  }
  const idx = readAccessor(json, views, prim.indices);
  const indices = Uint32Array.from(idx.data);
  const joints = readAccessor(json, views, prim.attributes.JOINTS_0).data;
  const weights = readAccessor(json, views, prim.attributes.WEIGHTS_0).data;
  const skin = json.skins[meshNode.skin];
  const ibm = readAccessor(json, views, skin.inverseBindMatrices).data;
  const jointNames = skin.joints.map((j) => json.nodes[j].name);
  const bones = {};
  // IBMs here map the QUANTIZED vertex space (gltfpack folds the dequantize
  // transform into them), so a joint's bind position is the mesh-node TRS
  // applied to inverse(IBM)'s origin — the same space as `positions`.
  jointNames.forEach((nm, k) => { const q = invertAffineTranslation(Array.from(ibm.subarray(k * 16, k * 16 + 16))); bones[nm] = apply(M, q[0], q[1], q[2]); });
  return { positions, indices, joints, weights, jointNames, bones, material: json.materials[prim.material].name, vertexCount: pos.count };
}

/**
 * The same GLB with every meshopt bufferView decoded into a plain BIN
 * chunk and the extension dropped (KHR_mesh_quantization stays — Blender
 * reads it). Returns a Buffer.
 */
export async function decodeGlbToPlain(bytes) {
  const { json, bin } = parseGlb(bytes);
  const views = await decodeViews(json, bin);
  const parts = []; let len = 0;
  const j = JSON.parse(JSON.stringify(json));
  j.bufferViews.forEach((bv, k) => {
    const data = views[k] || new Uint8Array(bv.byteLength);
    const pad = (4 - (len % 4)) % 4; if (pad) { parts.push(new Uint8Array(pad)); len += pad; }
    const stride = bv.extensions?.EXT_meshopt_compression?.byteStride;
    j.bufferViews[k] = { buffer: 0, byteOffset: len, byteLength: data.byteLength };
    if (stride && bv.target === 34962) j.bufferViews[k].byteStride = stride;
    else if (bv.byteStride) j.bufferViews[k].byteStride = bv.byteStride;
    if (bv.target) j.bufferViews[k].target = bv.target;
    parts.push(data); len += data.byteLength;
  });
  j.buffers = [{ byteLength: len }];
  j.extensionsUsed = (j.extensionsUsed || []).filter((e) => e !== 'EXT_meshopt_compression');
  j.extensionsRequired = (j.extensionsRequired || []).filter((e) => e !== 'EXT_meshopt_compression');
  if (!j.extensionsRequired.length) delete j.extensionsRequired;
  const binBuf = Buffer.concat(parts.map((p) => Buffer.from(p.buffer, p.byteOffset, p.byteLength)));
  const binPad = Buffer.concat([binBuf, Buffer.alloc((4 - (binBuf.length % 4)) % 4)]);
  let js = Buffer.from(JSON.stringify(j), 'utf8');
  js = Buffer.concat([js, Buffer.alloc((4 - (js.length % 4)) % 4, 0x20)]);
  const header = Buffer.alloc(12); header.writeUInt32LE(0x46546c67, 0); header.writeUInt32LE(2, 4);
  header.writeUInt32LE(12 + 8 + js.length + 8 + binPad.length, 8);
  const jh = Buffer.alloc(8); jh.writeUInt32LE(js.length, 0); jh.writeUInt32LE(0x4e4f534a, 4);
  const bh = Buffer.alloc(8); bh.writeUInt32LE(binPad.length, 0); bh.writeUInt32LE(0x004e4942, 4);
  return Buffer.concat([header, jh, js, bh, binPad]);
}
