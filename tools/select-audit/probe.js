// In-page probe: run via page.evaluate(PROBE, side). Measures the select
// pane's live model (window.__whSelectPanes[side].model). No THREE import:
// constructors are borrowed from the model's own objects.
window.__whProbe = function (side) {
  const pane = window.__whSelectPanes && window.__whSelectPanes[side || 'p1'];
  if (!pane || !pane.model) return { error: 'no model' };
  const root = pane.model;
  const V3 = root.position.constructor, M4 = root.matrixWorld.constructor;
  const Q = root.quaternion.constructor;
  root.updateMatrixWorld(true);
  const meshes = []; root.traverse(o => { if (o.isSkinnedMesh) meshes.push(o); });
  const out = { skinned: meshes.length, meshes: [], hasStance: !!pane.hasStance, stance: pane.stanceSource || null };
  if (!meshes.length) { out.error = 'no skinned mesh'; return out; }
  const invRoot = new M4().copy(root.matrixWorld).invert();
  let restMin = new V3(1e9,1e9,1e9), restMax = new V3(-1e9,-1e9,-1e9);
  let poseMin = restMin.clone(), poseMax = restMax.clone();
  let zero = 0, total = 0, far = 0, stretch = 0;
  let maxBoneDev = 0; const v = new V3(), p = new V3(), bp = new V3(), bb = new V3();
  for (const m of meshes) {
    const g = m.geometry, sk = m.skeleton;
    const pos = g.attributes.position, si = g.attributes.skinIndex, sw = g.attributes.skinWeight;
    if (!pos || !si || !sw) continue;
    sk.update();
    const n = pos.count, step = Math.max(1, Math.floor(n / 4000));
    const bindWorld = sk.boneInverses.map(bi => new M4().copy(bi).invert()); // bind-space bone mats
    const toBind = m.bindMatrixInverse;
    const toRoot = new M4().multiplyMatrices(invRoot, m.matrixWorld).multiply(m.bindMatrix);
    const boneNow = sk.bones.map(b => new M4().multiplyMatrices(toBind, new M4().multiplyMatrices(new M4().copy(m.matrixWorld).invert(), b.matrixWorld)));
    // bone local deviation from bind
    for (let i = 0; i < sk.bones.length; i++) {
      const b = sk.bones[i]; const pi = sk.bones.indexOf(b.parent);
      const lb = pi >= 0 ? new M4().copy(bindWorld[pi]).invert().multiply(bindWorld[i]) : bindWorld[i].clone();
      const lc = pi >= 0 ? new M4().copy(boneNow[pi]).invert().multiply(boneNow[i]) : boneNow[i].clone();
      const qa = new Q(), qb = new Q(), t = new V3(), s = new V3();
      lb.decompose(t, qa, s); lc.decompose(t, qb, s);
      const ang = 2 * Math.acos(Math.min(1, Math.abs(qa.dot(qb))));
      if (ang > maxBoneDev) maxBoneDev = ang;
    }
    let mz = 0, mf = 0, ms = 0, mt = 0;
    for (let i = 0; i < n; i += step) {
      mt++; v.fromBufferAttribute(pos, i);
      let ws = sw.getX(i) + sw.getY(i) + sw.getZ(i) + sw.getW(i);
      if (ws < 0.01) mz++;
      let top = si.getX(i), tw = sw.getX(i);
      for (const [a, w] of [[si.getY(i), sw.getY(i)], [si.getZ(i), sw.getZ(i)], [si.getW(i), sw.getW(i)]]) if (w > tw) { tw = w; top = a; }
      p.copy(v).applyMatrix4(toRoot); restMin.min(p); restMax.max(p);
      m.getVertexPosition(i, p); // skinned, mesh space
      const pp = p.clone().applyMatrix4(m.matrixWorld).applyMatrix4(invRoot); poseMin.min(pp); poseMax.max(pp);
      if (bindWorld[top]) {
        bb.setFromMatrixPosition(bindWorld[top]); const dr = v.distanceTo(bb);
        bp.setFromMatrixPosition(boneNow[top]); const pb = p.clone().applyMatrix4(toBind);
        const dp = pb.distanceTo(bp);
        out._h = out._h || 0;
        if (dr > 0 && Math.abs(dp - dr) > 0.25 * dr + 0.02) ms++;
        mf += dr; // accumulate for later
        if (!out._d) out._d = []; if (out._d.length < 20000) out._d.push(dr);
      }
    }
    // Triangle edge stretch: posed edge / rest edge, sampled triangles.
    const idx = g.index; const triN = idx ? idx.count / 3 : n / 3; const tstep = Math.max(1, Math.floor(triN / 6000));
    const a = new V3(), b2 = new V3(), ra = new V3(), rb2 = new V3();
    let eBad = 0, eTot = 0;
    for (let t = 0; t < triN; t += tstep) {
      const ia = idx ? idx.getX(3 * t) : 3 * t, ib = idx ? idx.getX(3 * t + 1) : 3 * t + 1;
      ra.fromBufferAttribute(pos, ia); rb2.fromBufferAttribute(pos, ib);
      const rl = ra.distanceTo(rb2); if (rl < 1e-6) continue;
      m.getVertexPosition(ia, a); m.getVertexPosition(ib, b2);
      const r = a.distanceTo(b2) / rl; eTot++;
      if (r > 2.5 || r < 0.25) eBad++;
    }
    out.edgeBad = (out.edgeBad || 0) + eBad; out.edgeTot = (out.edgeTot || 0) + eTot;
    zero += mz; total += mt; stretch += ms;
    out.meshes.push({ name: m.name, verts: n, bones: sk.bones.length, zero: mz, sampled: mt, stretch: ms });
  }
  const rs = restMax.clone().sub(restMin), ps = poseMax.clone().sub(poseMin);
  const h = Math.max(rs.y, 1e-6);
  // weights pointing at far bones: top-bone distance > 45% of height
  const d = out._d || []; far = d.filter(x => x > 0.45 * h).length; delete out._d; delete out._h;
  out.restSize = rs.toArray().map(x => +x.toFixed(3)); out.poseSize = ps.toArray().map(x => +x.toFixed(3));
  out.bboxRatio = +(ps.length() / Math.max(rs.length(), 1e-6)).toFixed(3);
  out.zeroFrac = +(zero / Math.max(total, 1)).toFixed(4);
  out.farFrac = +(far / Math.max(d.length, 1)).toFixed(4);
  out.stretchFrac = +(stretch / Math.max(total, 1)).toFixed(4);
  out.edgeFrac = +((out.edgeBad || 0) / Math.max(out.edgeTot || 1, 1)).toFixed(4);
  out.maxBoneDevDeg = +(maxBoneDev * 180 / Math.PI).toFixed(1);
  // Arm angles + pose vector in root space
  const bones = []; root.traverse(o => { if (o.isBone) bones.push(o); });
  const find = (res) => { for (const re of res) { const b = bones.find(x => re.test(x.name)); if (b) return b; } return null; };
  const wp = (b) => new V3().setFromMatrixPosition(b.matrixWorld).applyMatrix4(invRoot);
  const child = (b) => b && b.children.find(c => c.isBone);
  const L = [/^(mixamorig:?)?LeftArm$/i, /L_?UpperArm|UpperArm_?L|upperarm_l|L_?UpArm|Bip0?1 L UpperArm|LeftUpArm|BN_Arm_L|Arm_L$|l_arm$/i];
  const R = [/^(mixamorig:?)?RightArm$/i, /R_?UpperArm|UpperArm_?R|upperarm_r|R_?UpArm|Bip0?1 R UpperArm|RightUpArm|BN_Arm_R|Arm_R$|r_arm$/i];
  const armAng = (b) => { const c = child(b); if (!b || !c) return null; const dir = wp(c).sub(wp(b)).normalize(); return +(Math.acos(Math.max(-1, Math.min(1, -dir.y))) * 180 / Math.PI).toFixed(1); };
  const lb = find(L), rb = find(R);
  out.armL = armAng(lb); out.armR = armAng(rb); out.armBones = [lb && lb.name, rb && rb.name];
  // pose vector: direction of every bone->first child, root space, normalized by height
  const vec = [];
  for (const b of bones) { const c = child(b); if (!c) continue; const dd = wp(c).sub(wp(b)); const l = dd.length(); if (l < 1e-5) continue; dd.divideScalar(l); vec.push(b.name, +dd.x.toFixed(2), +dd.y.toFixed(2), +dd.z.toFixed(2)); }
  out.poseVec = vec;
  out.mixerClip = pane.mixer && pane.mixer._actions ? pane.mixer._actions.filter(a => a.isRunning()).map(a => a.getClip().name) : [];
  // t230u extras: model key, textures, framing, feet.
  out.modelId = pane.modelId || null;
  let mats = 0, untex = 0, white = 0;
  root.traverse(o => { if (!o.isMesh || !o.visible) return; for (const mt of [].concat(o.material || [])) {
    mats++; if (!mt.map) { untex++; const c = mt.color; if (c && c.r > 0.92 && c.g > 0.92 && c.b > 0.92) white++; } } });
  out.mats = mats; out.untexturedMats = untex; out.whiteMats = white;
  const cam = pane.camera;
  if (cam) {
    cam.updateMatrixWorld(); const W = poseMin, X = poseMax; let lo = [9, 9], hi = [-9, -9];
    for (const x of [W.x, X.x]) for (const y of [W.y, X.y]) for (const z of [W.z, X.z]) {
      const q = new V3(x, y, z).applyMatrix4(root.matrixWorld).project(cam);
      lo = [Math.min(lo[0], q.x), Math.min(lo[1], q.y)]; hi = [Math.max(hi[0], q.x), Math.max(hi[1], q.y)];
    }
    out.ndc = [lo, hi].map(a => a.map(v => +v.toFixed(3)));
  }
  const footW = new V3(0, poseMin.y, 0).applyMatrix4(root.matrixWorld);
  out.feetY = +footW.y.toFixed(3); out.heightW = +((poseMax.y - poseMin.y) * root.scale.y).toFixed(3);
  return out;
};
