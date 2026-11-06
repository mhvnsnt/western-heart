// dump a template GLB: skin/eyes/eyelash geometry in raw space, head-joint IBM, node matrices, skin weights, morph deltas
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { MeshoptDecoder } from 'meshoptimizer';
import fs from 'fs';
await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder': MeshoptDecoder});
const [,, src, out] = process.argv;
const doc = await io.read(src);
const r = doc.getRoot();
const skin = r.listSkins()[0];
const joints = skin.listJoints();
const ibm = skin.getInverseBindMatrices();
const jn = joints.map(j=>j.getName());
const hi = jn.indexOf('head'), ni = jn.indexOf('neck');
const getIBM = i => { const a=[]; ibm.getElement(i,a); return a; };
const meshNode = r.listNodes().find(n=>n.getMesh());
const res = { joints: jn, ibm_head: getIBM(hi), ibm_neck: getIBM(ni), head_world: joints[hi].getWorldMatrix(), node_matrix: meshNode.getWorldMatrix(), prims:{} , targetNames: meshNode.getMesh().getExtras().targetNames };
const want = { skin:/skin/i, eyes:/human_eyes/i, eyelash:/eyelash/i };
for (const p of meshNode.getMesh().listPrimitives()) {
  const mat = p.getMaterial()?.getName()||'';
  const key = Object.keys(want).find(k=>want[k].test(mat)); if(!key) continue;
  const pos = p.getAttribute('POSITION'); const n = pos.getCount(); const P = new Float32Array(n*3); const t=[];
  for (let i=0;i<n;i++){ pos.getElement(i,t); P.set(t,i*3); }
  const o = { mat, n, pos: Array.from(P) };
  if (key==='skin') {
    const idx = p.getIndices(); o.idx = Array.from(idx.getArray());
    const J = p.getAttribute('JOINTS_0'), W = p.getAttribute('WEIGHTS_0'); const hw = new Float32Array(n); const a=[],b=[];
    for (let i=0;i<n;i++){ J.getElement(i,a); W.getElement(i,b); let s=0; for(let k=0;k<4;k++) if(a[k]===hi) s+=b[k]; hw[i]=s; }
    o.headw = Array.from(hw);
    o.targets = p.listTargets().map(tg=>{ const ta=tg.getAttribute('POSITION'); const D=new Float32Array(n*3); for(let i=0;i<n;i++){ ta.getElement(i,t); D.set(t,i*3);} return Array.from(D); });
  }
  res.prims[key] = o;
}
fs.writeFileSync(out, JSON.stringify(res));
console.log(src, 'head idx', hi, 'prims', Object.keys(res.prims), 'node', res.node_matrix.map(x=>+x.toFixed(6)).join(','));
console.log('ibm_head', res.ibm_head.map(x=>+x.toFixed(6)).join(','));
console.log('head_world', res.head_world.map(x=>+x.toFixed(4)).join(','));
