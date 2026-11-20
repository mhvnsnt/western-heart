// tools/models/realign_mesh_to_skeleton.mjs — measure (and fix) a skinned mesh that sits away from its own skeleton.
//
// Why (2026-11-11, Brutal Fist pull-in): bf-jager and bf-tarzanian-devil carry the same Mixamo skeleton template as
// the other Brutal Fist fighters, but their mesh vertices sit ~0.95 m above it (bounds y 0..1.90 where every other
// Brutal Fist mesh is centred, y -0.94..0.94). At bind that only misplaces the head bone (the select card framed the
// legs); once posed, every vertex swings around a joint a metre away, which stretches the mesh apart.
//
// Measure: for a bone B, centroid(vertices whose strongest weight is B) - B's bind position (inverse of B's inverse
// bind matrix, in the mesh's bind space). A correctly bound body gives a few centimetres for Hips and Spine; a shifted
// mesh gives its shift. --apply moves every POSITION by minus the Hips offset (inverse bind matrices, skeleton and
// weights untouched), so mesh and skeleton agree again. The skeleton is the reference: it is the one the game drives.
//
// usage: node tools/models/realign_mesh_to_skeleton.mjs IN.glb [--apply OUT.glb] [--axis y | --center-y]
//   (needs @gltf-transform/core + extensions and meshoptimizer resolvable from this file, like tools/anim/scale_glb.mjs)
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { MeshoptDecoder, MeshoptEncoder } from 'meshoptimizer';

const args = process.argv.slice(2);
const inp = args[0];
const out = args.includes('--apply') ? args[args.indexOf('--apply') + 1] : null;
const axis = args.includes('--axis') ? args[args.indexOf('--axis') + 1] : null; // restrict the shift to one axis
// --center-y: shift by the mesh's own vertical bounds centre instead (the exact undo of a 'feet to y=0' move on a mesh
// whose skeleton template is centred, as for bf-jager / bf-tarzanian-devil)
const centerY = args.includes('--center-y');
if (!inp) { console.error('usage: realign_mesh_to_skeleton.mjs IN.glb [--apply OUT.glb] [--axis y]'); process.exit(2); }
await MeshoptDecoder.ready; await MeshoptEncoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS)
  .registerDependencies({ 'meshopt.decoder': MeshoptDecoder, 'meshopt.encoder': MeshoptEncoder });
const doc = await io.read(inp);
const root = doc.getRoot();

function inv4(m) { // column-major 4x4 inverse (rigid + scale; general)
  const a = m, o = new Array(16);
  const b00 = a[0] * a[5] - a[1] * a[4], b01 = a[0] * a[6] - a[2] * a[4], b02 = a[0] * a[7] - a[3] * a[4];
  const b03 = a[1] * a[6] - a[2] * a[5], b04 = a[1] * a[7] - a[3] * a[5], b05 = a[2] * a[7] - a[3] * a[6];
  const b06 = a[8] * a[13] - a[9] * a[12], b07 = a[8] * a[14] - a[10] * a[12], b08 = a[8] * a[15] - a[11] * a[12];
  const b09 = a[9] * a[14] - a[10] * a[13], b10 = a[9] * a[15] - a[11] * a[13], b11 = a[10] * a[15] - a[11] * a[14];
  const det = b00 * b11 - b01 * b10 + b02 * b09 + b03 * b08 - b04 * b07 + b05 * b06;
  const d = 1 / det;
  o[0] = (a[5] * b11 - a[6] * b10 + a[7] * b09) * d; o[1] = (a[2] * b10 - a[1] * b11 - a[3] * b09) * d;
  o[2] = (a[13] * b05 - a[14] * b04 + a[15] * b03) * d; o[3] = (a[10] * b04 - a[9] * b05 - a[11] * b03) * d;
  o[4] = (a[6] * b08 - a[4] * b11 - a[7] * b07) * d; o[5] = (a[0] * b11 - a[2] * b08 + a[3] * b07) * d;
  o[6] = (a[14] * b02 - a[12] * b05 - a[15] * b01) * d; o[7] = (a[8] * b05 - a[10] * b02 + a[11] * b01) * d;
  o[8] = (a[4] * b10 - a[5] * b08 + a[7] * b06) * d; o[9] = (a[1] * b08 - a[0] * b10 - a[3] * b06) * d;
  o[10] = (a[12] * b04 - a[13] * b02 + a[15] * b00) * d; o[11] = (a[9] * b02 - a[8] * b04 - a[11] * b00) * d;
  o[12] = (a[5] * b07 - a[4] * b09 - a[6] * b06) * d; o[13] = (a[0] * b09 - a[1] * b07 + a[2] * b06) * d;
  o[14] = (a[13] * b01 - a[12] * b03 - a[14] * b00) * d; o[15] = (a[8] * b03 - a[9] * b01 + a[10] * b00) * d;
  return o;
}

const report = [];
let shift = null;
for (const node of root.listNodes()) {
  const mesh = node.getMesh(), skin = node.getSkin();
  if (!mesh || !skin) continue;
  const joints = skin.listJoints(), ibmAcc = skin.getInverseBindMatrices();
  const ibm = ibmAcc.getArray();
  const bindPos = joints.map((_, k) => { const m = inv4(Array.from(ibm.slice(k * 16, k * 16 + 16))); return [m[12], m[13], m[14]]; });
  const idx = (re) => joints.findIndex((j) => re.test(j.getName()));
  const want = { Hips: idx(/Hips$/), Spine: idx(/Spine$/), Head: idx(/Head$/) };
  const acc = {}; for (const k of Object.keys(want)) acc[k] = [0, 0, 0, 0];
  let lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
  for (const prim of mesh.listPrimitives()) {
    const P = prim.getAttribute('POSITION'), J = prim.getAttribute('JOINTS_0'), W = prim.getAttribute('WEIGHTS_0');
    if (!P || !J || !W) continue;
    const p = [0, 0, 0], jj = [0, 0, 0, 0], ww = [0, 0, 0, 0];
    for (let i = 0; i < P.getCount(); i++) {
      P.getElement(i, p); J.getElement(i, jj); W.getElement(i, ww);
      for (let c = 0; c < 3; c++) { lo[c] = Math.min(lo[c], p[c]); hi[c] = Math.max(hi[c], p[c]); }
      let best = 0; for (let k = 1; k < 4; k++) if (ww[k] > ww[best]) best = k;
      for (const [name, ji] of Object.entries(want)) if (jj[best] === ji) { const a = acc[name]; a[0] += p[0]; a[1] += p[1]; a[2] += p[2]; a[3]++; }
    }
  }
  const offs = {};
  for (const [name, ji] of Object.entries(want)) {
    const a = acc[name]; if (ji < 0 || !a[3]) continue;
    offs[name] = [0, 1, 2].map((c) => +(a[c] / a[3] - bindPos[ji][c]).toFixed(3));
  }
  report.push({ node: node.getName(), joints: joints.length, bounds: { lo: lo.map((v) => +v.toFixed(3)), hi: hi.map((v) => +v.toFixed(3)) },
    hipsBind: want.Hips >= 0 ? bindPos[want.Hips].map((v) => +v.toFixed(3)) : null, centroidMinusBind: offs });
  if (!shift && offs.Hips) shift = offs.Hips;
}
console.log(JSON.stringify({ file: inp, meshes: report, hipsShift: shift }, null, 1));
if (out) {
  if (!shift) { console.error('no skinned mesh with a Hips bone: nothing to apply'); process.exit(1); }
  const b = report[0] && report[0].bounds;
  const s = centerY ? [0, (b.lo[1] + b.hi[1]) / 2, 0]
    : axis ? [axis === 'x' ? shift[0] : 0, axis === 'y' ? shift[1] : 0, axis === 'z' ? shift[2] : 0] : shift;
  const done = new Set();
  for (const node of root.listNodes()) {
    const mesh = node.getMesh(); if (!mesh || !node.getSkin()) continue;
    for (const prim of mesh.listPrimitives()) {
      for (const acc of [prim.getAttribute('POSITION'), ...prim.listTargets().map((t) => null)]) {
        if (!acc || done.has(acc)) continue; done.add(acc);
        const arr = acc.getArray().slice();
        for (let i = 0; i < arr.length; i += 3) { arr[i] -= s[0]; arr[i + 1] -= s[1]; arr[i + 2] -= s[2]; }
        acc.setArray(arr);
      }
    }
  }
  await io.write(out, doc);
  console.log('wrote', out, 'shifted by', s.map((v) => -v));
}
