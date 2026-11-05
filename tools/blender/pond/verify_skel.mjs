// verify_skel.mjs — skeleton/IBM identity checks for the grafted Pond.
//   node verify_skel.mjs SHIPPED_PLAIN GRAFT_PLAIN GRAFT_ENCODED SHIPPED_ENCODED
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'meshoptimizer';
await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.decoder': MeshoptDecoder });
const [SP, GP, GE, SE] = process.argv.slice(2);
const docs = Object.fromEntries(await Promise.all([['sp', SP], ['gp', GP], ['ge', GE], ['se', SE]].map(async ([k, f]) => [k, await io.read(f)])));
const out = {}; let ok = true;
const jointNodes = (d) => { const s = d.getRoot().listSkins()[0]; return s.listJoints(); };
const trsBytes = (n) => Buffer.from(new Float32Array([...n.getTranslation(), ...n.getRotation(), ...n.getScale()]).buffer);
const nodeKey = (d) => jointNodes(d).map((n) => [n.getName(), n.getParentNode()?.getName(), trsBytes(n).toString('hex')]);
const ref = JSON.stringify(nodeKey(docs.sp));
for (const k of ['gp', 'ge', 'se']) { out[`joints_name_parent_trs_bytes_equal_${k}`] = JSON.stringify(nodeKey(docs[k])) === ref; ok &&= out[`joints_name_parent_trs_bytes_equal_${k}`]; }
// every skin in every file lists the same joint nodes in the same order
for (const k of ['gp', 'ge', 'se']) {
  const names = JSON.stringify(jointNodes(docs.sp).map((n) => n.getName()));
  out[`all_skins_same_joint_order_${k}`] = docs[k].getRoot().listSkins().every((s) => JSON.stringify(s.listJoints().map((n) => n.getName())) === names);
  out[`skins_${k}`] = docs[k].getRoot().listSkins().length;
  ok &&= out[`all_skins_same_joint_order_${k}`];
}
const ibm = (s) => s.getInverseBindMatrices().getArray();
const spI = ibm(docs.sp.getRoot().listSkins()[0]);
out.ibm_bytes_equal_plain = Buffer.compare(Buffer.from(spI.buffer, spI.byteOffset, spI.byteLength), Buffer.from(ibm(docs.gp.getRoot().listSkins()[0]).buffer)) === 0
  && docs.gp.getRoot().listSkins().length === 1;
ok &&= out.ibm_bytes_equal_plain;
// encoded skins: IBM_k = IBM_orig @ Q (Q = per-mesh dequantization: scale+translate) -> check Q constant across joints
const mul = (a, b) => { const r = new Array(16).fill(0); for (let c = 0; c < 4; c++) for (let rr = 0; rr < 4; rr++) for (let k = 0; k < 4; k++) r[c * 4 + rr] += a[k * 4 + rr] * b[c * 4 + k]; return r; };
const inv = (m) => { // general 4x4 inverse (column-major)
  const a = m, b = new Array(16);
  b[0] = a[5]*a[10]*a[15]-a[5]*a[11]*a[14]-a[9]*a[6]*a[15]+a[9]*a[7]*a[14]+a[13]*a[6]*a[11]-a[13]*a[7]*a[10];
  b[4] = -a[4]*a[10]*a[15]+a[4]*a[11]*a[14]+a[8]*a[6]*a[15]-a[8]*a[7]*a[14]-a[12]*a[6]*a[11]+a[12]*a[7]*a[10];
  b[8] = a[4]*a[9]*a[15]-a[4]*a[11]*a[13]-a[8]*a[5]*a[15]+a[8]*a[7]*a[13]+a[12]*a[5]*a[11]-a[12]*a[7]*a[9];
  b[12] = -a[4]*a[9]*a[14]+a[4]*a[10]*a[13]+a[8]*a[5]*a[14]-a[8]*a[6]*a[13]-a[12]*a[5]*a[10]+a[12]*a[6]*a[9];
  b[1] = -a[1]*a[10]*a[15]+a[1]*a[11]*a[14]+a[9]*a[2]*a[15]-a[9]*a[3]*a[14]-a[13]*a[2]*a[11]+a[13]*a[3]*a[10];
  b[5] = a[0]*a[10]*a[15]-a[0]*a[11]*a[14]-a[8]*a[2]*a[15]+a[8]*a[3]*a[14]+a[12]*a[2]*a[11]-a[12]*a[3]*a[10];
  b[9] = -a[0]*a[9]*a[15]+a[0]*a[11]*a[13]+a[8]*a[1]*a[15]-a[8]*a[3]*a[13]-a[12]*a[1]*a[11]+a[12]*a[3]*a[9];
  b[13] = a[0]*a[9]*a[14]-a[0]*a[10]*a[13]-a[8]*a[1]*a[14]+a[8]*a[2]*a[13]+a[12]*a[1]*a[10]-a[12]*a[2]*a[9];
  b[2] = a[1]*a[6]*a[15]-a[1]*a[7]*a[14]-a[5]*a[2]*a[15]+a[5]*a[3]*a[14]+a[13]*a[2]*a[7]-a[13]*a[3]*a[6];
  b[6] = -a[0]*a[6]*a[15]+a[0]*a[7]*a[14]+a[4]*a[2]*a[15]-a[4]*a[3]*a[14]-a[12]*a[2]*a[7]+a[12]*a[3]*a[6];
  b[10] = a[0]*a[5]*a[15]-a[0]*a[7]*a[13]-a[4]*a[1]*a[15]+a[4]*a[3]*a[13]+a[12]*a[1]*a[7]-a[12]*a[3]*a[5];
  b[14] = -a[0]*a[5]*a[14]+a[0]*a[6]*a[13]+a[4]*a[1]*a[14]-a[4]*a[2]*a[13]-a[12]*a[1]*a[6]+a[12]*a[2]*a[5];
  b[3] = -a[1]*a[6]*a[11]+a[1]*a[7]*a[10]+a[5]*a[2]*a[11]-a[5]*a[3]*a[10]-a[9]*a[2]*a[7]+a[9]*a[3]*a[6];
  b[7] = a[0]*a[6]*a[11]-a[0]*a[7]*a[10]-a[4]*a[2]*a[11]+a[4]*a[3]*a[10]+a[8]*a[2]*a[7]-a[8]*a[3]*a[6];
  b[11] = -a[0]*a[5]*a[11]+a[0]*a[7]*a[9]+a[4]*a[1]*a[11]-a[4]*a[3]*a[9]-a[8]*a[1]*a[7]+a[8]*a[3]*a[5];
  b[15] = a[0]*a[5]*a[10]-a[0]*a[6]*a[9]-a[4]*a[1]*a[10]+a[4]*a[2]*a[9]+a[8]*a[1]*a[6]-a[8]*a[2]*a[5];
  const det = a[0]*b[0]+a[1]*b[4]+a[2]*b[8]+a[3]*b[12]; return b.map((x) => x / det);
};
for (const k of ['ge', 'se']) {
  let worst = 0, notScaleTranslate = 0;
  for (const s of docs[k].getRoot().listSkins()) {
    const I = ibm(s); let Q0 = null;
    for (let j = 0; j < 52; j++) {
      const o = Array.from(spI.slice(j * 16, j * 16 + 16)), n = Array.from(I.slice(j * 16, j * 16 + 16));
      const Q = mul(inv(o), n); // n = o @ Q
      if (!Q0) { Q0 = Q; if ([1, 2, 3, 4, 6, 7, 8, 9, 11].some((i) => Math.abs(Q[i]) > 1e-5)) notScaleTranslate++; }
      worst = Math.max(worst, ...Q.map((v, i) => Math.abs(v - Q0[i]) / Math.max(1, Math.abs(Q0[i]))));
    }
  }
  out[`encoded_ibm_eq_orig_times_constQ_${k}`] = { maxRelDev: worst, skinsNotScaleTranslate: notScaleTranslate };
  ok &&= worst < 1e-4 && notScaleTranslate === 0;
}
out.PASS = ok;
console.log(JSON.stringify(out, null, 1));
