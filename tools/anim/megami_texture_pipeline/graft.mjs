// Graft full-resolution image payloads + the proxy export's material /
// texture wiring onto a geometry GLB exported with images=NONE.
//   node graft.mjs BASE.glb PROXY.glb MANIFEST.json OUT.glb
// Materials are matched by NAME (donor materials reordered to the base
// file's material order so primitive material indices stay valid).
import fs from 'node:fs';

const [, , basePath, proxyPath, manifestPath, outPath] = process.argv;

function readGLB(p) {
  const b = fs.readFileSync(p);
  const len = b.readUInt32LE(12);
  const json = JSON.parse(b.toString('utf8', 20, 20 + len));
  const binOff = 20 + len;
  const binLen = b.readUInt32LE(binOff);
  return { json, bin: b.subarray(binOff + 8, binOff + 8 + binLen) };
}

const base = readGLB(basePath);
const proxy = readGLB(proxyPath);
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

const bj = base.json, pj = proxy.json;

// --- sanity: same material name multiset
const bNames = bj.materials.map(m => m.name).sort();
const pNames = pj.materials.map(m => m.name).sort();
if (JSON.stringify(bNames) !== JSON.stringify(pNames)) {
  console.error('MATERIAL NAME MISMATCH'); process.exit(1);
}
// --- sanity: manifest covers proxy images 1:1
if (manifest.length !== pj.images.length) { console.error('MANIFEST COUNT MISMATCH'); process.exit(1); }

// --- build new BIN: base bin + payloads (4-byte aligned)
const chunks = [Buffer.from(base.bin)];
let cursor = base.bin.length;
const align = () => { const pad = (4 - (cursor % 4)) % 4; if (pad) { chunks.push(Buffer.alloc(pad)); cursor += pad; } };
const newViews = [];
for (const entry of manifest) {
  align();
  const data = fs.readFileSync(entry.file);
  if (data.length !== entry.bytes) { console.error('PAYLOAD SIZE MISMATCH', entry.name); process.exit(1); }
  newViews.push({ buffer: 0, byteOffset: cursor, byteLength: data.length });
  chunks.push(data); cursor += data.length;
}
const newBin = Buffer.concat(chunks);

// --- compose JSON
const baseViewCount = bj.bufferViews.length;
const out = bj;
out.bufferViews = [...bj.bufferViews, ...newViews];
out.buffers = [{ byteLength: newBin.length }];
out.images = pj.images.map((im, i) => ({ name: im.name, mimeType: im.mimeType, bufferView: baseViewCount + i }));
out.textures = pj.textures;
out.samplers = pj.samplers;
const donorByName = new Map(pj.materials.map(m => [m.name, m]));
out.materials = bj.materials.map(m => donorByName.get(m.name));
const extUsed = new Set([...(bj.extensionsUsed || []), ...(pj.extensionsUsed || [])]);
out.extensionsUsed = [...extUsed];
if (pj.extensionsRequired) out.extensionsRequired = pj.extensionsRequired;

// --- write GLB
const jsonStr = JSON.stringify(out);
const jsonBuf = Buffer.from(jsonStr, 'utf8');
const jsonPad = (4 - (jsonBuf.length % 4)) % 4;
const jsonChunk = Buffer.concat([jsonBuf, Buffer.alloc(jsonPad, 0x20)]);
const binPad = (4 - (newBin.length % 4)) % 4;
const binChunk = binPad ? Buffer.concat([newBin, Buffer.alloc(binPad)]) : newBin;
const header = Buffer.alloc(12);
header.writeUInt32LE(0x46546c67, 0); header.writeUInt32LE(2, 4);
header.writeUInt32LE(12 + 8 + jsonChunk.length + 8 + binChunk.length, 8);
const jh = Buffer.alloc(8); jh.writeUInt32LE(jsonChunk.length, 0); jh.writeUInt32LE(0x4e4f534a, 4);
const bh = Buffer.alloc(8); bh.writeUInt32LE(binChunk.length, 0); bh.writeUInt32LE(0x004e4942, 4);
fs.writeFileSync(outPath, Buffer.concat([header, jh, jsonChunk, bh, binChunk]));
console.log('GRAFTED ->', outPath, 'images:', out.images.length, 'materials:', out.materials.length, 'bin:', newBin.length);
