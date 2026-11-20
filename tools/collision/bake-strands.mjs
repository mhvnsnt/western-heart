/* ============================================================
   bake-strands.mjs — offline guide-strand bake for strand hair.

   WHY: the visible hair in a DAZ-style part is thousands of
   independent triangle-strip CARDS (here: 3,208 cards, 174k
   verts). Simulating every card is wasteful; simulating only
   the part's 19 two-level bones never touches the visible
   strands at all (Phase B finisher-8 verdict). The industry
   pattern (AMD TressFX, Tomb Raider 2013) is GUIDE strands:
   simulate a few hundred representative strands as verlet/PBD
   chains, and deform every render vert from its bound guide.

   This bake, from the part GLB alone:
     1. splits each strand prim into cards (connected components
        over the index buffer),
     2. extracts each card's centreline (PCA-axis row binning,
        root end = the end nearest the head joint),
     3. selects GUIDE cards greedily by root coverage (root
        proximity + initial-tangent alignment + length ratio),
     4. binds EVERY strand vert to a guide: parameter s along
        the guide (arc-length fraction mapped) + offset in the
        guide's bind rotation-minimising frame (RMF) coords.

   Output (next to the character's collision bake):
     <name>-strands.json — header: source, prims, guide bind
        polylines + root frames, counts, layout of the .bin.
     <name>-strands.bin  — per-vert bindings:
        u16 guideIdx | f32 s | f32 offN | f32 offB | f32 offT
        (18 bytes/vert, arrays concatenated in that order).

   All positions are in the part GLB's geometry space (mesh
   nodes must be identity — asserted; that space is what the
   runtime deforms back into).

   usage: node bake-strands.mjs <part.glb> <outPrefix>
          [--guide-radius 0.025] [--max-guides 700]
   ============================================================ */
import { readFileSync, writeFileSync } from 'node:fs';

const [glbPath, outPrefix, bodyPath] = process.argv.slice(2);
if (!glbPath || !outPrefix) { console.error('usage: bake-strands.mjs <part.glb> <outPrefix> [body.glb] [--sdf-prefix <bodySdfPrefix>]'); process.exit(2); }
/* optional body SDF (from bake-collision.mjs output): when given,
   every guide particle's bind signed distance is sampled and
   shipped as header.bindSdf — the runtime pins particles glued to
   the scalp at bind (attach model: weave/cap anchoring). */
let SDF_PREFIX = null;
{ const si = process.argv.indexOf('--sdf-prefix'); if (si >= 0) SDF_PREFIX = process.argv[si + 1]; }
let bodySDF = null;
if (SDF_PREFIX) {
  const { BodySDF } = await import(new URL('../../game/js/collision.js', import.meta.url).href);
  const sh = JSON.parse(readFileSync(SDF_PREFIX + '.json', 'utf8'));
  const sb = readFileSync(SDF_PREFIX + '.bin');
  bodySDF = new BodySDF(BodySDF.headerFromJSON(sh), new Int16Array(sb.buffer, sb.byteOffset, sb.byteLength / 2));
  console.log(`bindSdf: sampling against ${SDF_PREFIX}.json`);
}
const args = {};
for (let i = 5; i < process.argv.length; i += 2) args[process.argv[i].replace(/^--/, '')] = parseFloat(process.argv[i + 1]);
const GUIDE_R = args['guide-radius'] ?? 0.06;
const PATH_OK = args['path-ok'] ?? 0.020;   // accept a guide if mean centreline distance < this (m)
const MAX_GUIDES = args['max-guides'] ?? 700;
const SEG_LEN = 0.030;               // target sim segment length (m)
const MIN_GUIDE_LEN_FRAC = 0.8;      // a guide must be >= 0.8x its card

/* ---------------- GLB read ---------------- */
const buf = readFileSync(glbPath);
const jsonLen = buf.readUInt32LE(12);
const g = JSON.parse(buf.toString('utf8', 20, 20 + jsonLen));
const binOff = 20 + jsonLen + 8;
function readAcc(idx) {
  const a = g.accessors[idx];
  const bv = g.bufferViews[a.bufferView];
  const off = binOff + (bv.byteOffset || 0) + (a.byteOffset || 0);
  const comp = { 5121: ['getUint8', 1], 5123: ['getUint16', 2], 5125: ['getUint32', 4], 5126: ['getFloat32', 4] }[a.componentType];
  const n = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT4: 16 }[a.type];
  const out = new Float32Array(a.count * n);
  // honour interleaved bufferViews (byteStride): JOINTS_0/WEIGHTS_0
  // in Blender exports are packed per-vertex with other attributes.
  const stride = bv.byteStride && bv.byteStride !== n * comp[1] ? bv.byteStride : null;
  if (stride) {
    const dv = new DataView(buf.buffer, buf.byteOffset + off, bv.byteLength - (a.byteOffset || 0));
    for (let vI = 0; vI < a.count; vI++) for (let cI = 0; cI < n; cI++) out[vI * n + cI] = dv[comp[0]](vI * stride + cI * comp[1], true);
  } else {
    const dv = new DataView(buf.buffer, buf.byteOffset + off, a.count * n * comp[1]);
    for (let i = 0; i < a.count * n; i++) out[i] = dv[comp[0]](i * comp[1], true);
  }
  return out;
}

/* node world transforms (bind) — plain TRS composition */
function nodeWorld(i, cache) {
  if (cache[i]) return cache[i];
  const n = g.nodes[i];
  const t = n.translation || [0, 0, 0], r = n.rotation || [0, 0, 0, 1], s = n.scale || [1, 1, 1];
  const [x, y, z, w] = r;
  const m = new Float64Array(16); // column-major
  const x2 = x + x, y2 = y + y, z2 = z + z, xx = x * x2, xy = x * y2, xz = x * z2, yy = y * y2, yz = y * z2, zz = z * z2, wx = w * x2, wy = w * y2, wz = w * z2;
  m[0] = (1 - (yy + zz)) * s[0]; m[1] = (xy + wz) * s[0]; m[2] = (xz - wy) * s[0]; m[3] = 0;
  m[4] = (xy - wz) * s[1]; m[5] = (1 - (xx + zz)) * s[1]; m[6] = (yz + wx) * s[1]; m[7] = 0;
  m[8] = (xz + wy) * s[2]; m[9] = (yz - wx) * s[2]; m[10] = (1 - (xx + yy)) * s[2]; m[11] = 0;
  m[12] = t[0]; m[13] = t[1]; m[14] = t[2]; m[15] = 1;
  // find parent
  let parent = -1;
  g.nodes.forEach((pn, pi) => { if (pn.children && pn.children.includes(i)) parent = pi; });
  if (parent >= 0) {
    const pm = nodeWorld(parent, cache);
    const out = new Float64Array(16);
    for (let c = 0; c < 4; c++) for (let r2 = 0; r2 < 4; r2++) {
      out[c * 4 + r2] = pm[r2] * m[c * 4] + pm[4 + r2] * m[c * 4 + 1] + pm[8 + r2] * m[c * 4 + 2] + pm[12 + r2] * m[c * 4 + 3];
    }
    cache[i] = out; return out;
  }
  cache[i] = m; return m;
}
const worldCache = {};
// head joint world position (scalp reference for card roots)
const skin = g.skins[0];
const headJointNode = skin.joints.map(j => g.nodes[j].name).indexOf('head');
const headNodeIdx = skin.joints[headJointNode];
const headW = nodeWorld(headNodeIdx, worldCache);
const HEAD = [headW[12], headW[13], headW[14]];
console.log('head joint bind world:', HEAD.map(v => v.toFixed(3)).join(','));

/* ---------------- wear-transform seating (body given) ----------------
   Strand geometry is authored around the PART's skeleton. As worn,
   the part's skeleton is DRIVEN by the body skeleton (the stage's
   drivePartHead pattern, generalised to every joint): each part
   joint's world becomes Mw_j = B_j ∘ Wp_j^-1 applied through the
   part's own skinning — verts land where the worn part renders at
   bind, in BODY-JOINT frame (the frame the collision bake, the SDF
   and the runtime anchors live in). Joint matching is by NAME,
   with the part's lowercase DAZ names mapped to the body's
   capitalised ones for the head anchor chain (head->Head etc.);
   unmatched joints keep their part world (identity delta).
   The map is applied to raw positions BEFORE card extraction, so
   guides, bindings and HEAD all live in the seated frame. The
   runtime then treats bake space == sim space directly. */
function mulM(a, b) { const o = new Float64Array(16); for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) o[c * 4 + r] = a[r] * b[c * 4] + a[4 + r] * b[c * 4 + 1] + a[8 + r] * b[c * 4 + 2] + a[12 + r] * b[c * 4 + 3]; return o; }
function invAffine(m) { const o = new Float64Array(16);
  o[0]=m[0];o[1]=m[4];o[2]=m[8]; o[4]=m[1];o[5]=m[5];o[6]=m[9]; o[8]=m[2];o[9]=m[6];o[10]=m[10];
  o[12]=-(o[0]*m[12]+o[4]*m[13]+o[8]*m[14]); o[13]=-(o[1]*m[12]+o[5]*m[13]+o[9]*m[14]); o[14]=-(o[2]*m[12]+o[6]*m[13]+o[10]*m[14]); o[15]=1; return o; }
let wearInfo = null;
if (bodyPath) {
  const bbuf = readFileSync(bodyPath);
  const blen = bbuf.readUInt32LE(12);
  const bg = JSON.parse(bbuf.toString('utf8', 20, 20 + blen));
  const bBinOff = 20 + blen + 8;
  const readAccB = (idx) => {
    const a = bg.accessors[idx]; const bv = bg.bufferViews[a.bufferView];
    const off = bBinOff + (bv.byteOffset || 0) + (a.byteOffset || 0);
    const comp = { 5121: ['getUint8', 1], 5123: ['getUint16', 2], 5125: ['getUint32', 4], 5126: ['getFloat32', 4] }[a.componentType];
    const n = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT4: 16 }[a.type];
    const out = new Float32Array(a.count * n);
    const stride = bv.byteStride && bv.byteStride !== n * comp[1] ? bv.byteStride : null;
    if (stride) {
      const dv = new DataView(bbuf.buffer, bbuf.byteOffset + off, bv.byteLength - (a.byteOffset || 0));
      for (let vI = 0; vI < a.count; vI++) for (let cI = 0; cI < n; cI++) out[vI * n + cI] = dv[comp[0]](vI * stride + cI * comp[1], true);
    } else {
      const dv = new DataView(bbuf.buffer, bbuf.byteOffset + off, a.count * n * comp[1]);
      for (let i = 0; i < a.count * n; i++) out[i] = dv[comp[0]](i * comp[1], true);
    }
    return out;
  };
  // body joint worlds from IBMs (meshes are sunk vs joints — node
  // worlds of a Blender export do NOT give the joint frame)
  const bskin = bg.skins[0];
  const bIBM = readAccB(bskin.inverseBindMatrices);
  const bodyJointByName = new Map();
  bskin.joints.forEach((jn, ji) => {
    bodyJointByName.set(bg.nodes[jn].name, invAffine(bIBM.slice(ji * 16, ji * 16 + 16)));
  });
  // part joint worlds from node composition (validated == inv(IBM))
  const partIBM = readAcc(skin.inverseBindMatrices);
  const NAME_FIX = { head: 'Head', neck: 'Neck', hip: 'Hips' };
  const skinMats = skin.joints.map((jn, ji) => {
    const Wp = nodeWorld(jn, worldCache);
    const name = g.nodes[jn].name;
    const bname = bodyJointByName.has(name) ? name : (NAME_FIX[name] && bodyJointByName.has(NAME_FIX[name]) ? NAME_FIX[name] : null);
    const Mw = bname ? mulM(bodyJointByName.get(bname), invAffine(Wp)) : null;
    const ibm = partIBM.slice(ji * 16, ji * 16 + 16);
    // skinned position = Mw * Wp * IBM * p  (Mw null -> plain bind skinning)
    return { m: Mw ? mulM(Mw, mulM(Wp, ibm)) : mulM(Wp, ibm), matched: !!bname, name };
  });
  const matched = skinMats.filter(x => x.matched).map(x => x.name);
  console.log(`wear transform: ${matched.length}/${skinMats.length} part joints matched to body: ${matched.join(',')}`);
  // apply to every strand prim's positions (JOINTS_0/WEIGHTS_0 read here)
  // NOTE: prims[] is built below this block in file order — the map is
  // applied lazily via seatPos() inside the prim loop instead.
  var seatPos = (pr) => {
    const pos = pr.pos, jts = readAcc(pr.jtsIdx), wts = readAcc(pr.wtsIdx);
    const out = new Float32Array(pos.length);
    for (let v = 0; v < pos.length / 3; v++) {
      let x = 0, y = 0, z = 0;
      for (let k = 0; k < 4; k++) {
        const wgt = wts[v * 4 + k]; if (!wgt) continue;
        const m = skinMats[jts[v * 4 + k]].m;
        const px = pos[v * 3], py = pos[v * 3 + 1], pz = pos[v * 3 + 2];
        x += wgt * (m[0] * px + m[4] * py + m[8] * pz + m[12]);
        y += wgt * (m[1] * px + m[5] * py + m[9] * pz + m[13]);
        z += wgt * (m[2] * px + m[6] * py + m[10] * pz + m[14]);
      }
      out[v * 3] = x; out[v * 3 + 1] = y; out[v * 3 + 2] = z;
    }
    return out;
  };
  // HEAD re-based: body Head joint world (the scalp reference now)
  const bHeadW = bodyJointByName.get('Head');
  HEAD[0] = bHeadW[12]; HEAD[1] = bHeadW[13]; HEAD[2] = bHeadW[14];
  wearInfo = { body: bodyPath.split('/').pop(), matchedJoints: matched };
  console.log('seated frame: head reference now body Head at', HEAD.map(v => v.toFixed(3)).join(','));
}

/* strand prims: every primitive of the skinned mesh EXCEPT cap/headband mats */
const SKIP_MAT = /cap|headband/i;
const prims = [];
g.meshes.forEach((mesh, mi) => {
  mesh.primitives.forEach((pr, pi) => {
    const mat = (g.materials[pr.material] && g.materials[pr.material].name) || '';
    // the mesh node must be identity for geometry space == part space
    const nodeIdx = g.nodes.findIndex(n => n.mesh === mi);
    const nw = nodeWorld(nodeIdx, worldCache);
    const ident = Math.abs(nw[0] - 1) + Math.abs(nw[5] - 1) + Math.abs(nw[10] - 1) + Math.abs(nw[12]) + Math.abs(nw[13]) + Math.abs(nw[14]);
    if (ident > 1e-4) throw new Error(`mesh node ${nodeIdx} not identity (sum ${ident}) — geometry space transform required`);
    if (SKIP_MAT.test(mat)) { console.log(`skip prim mesh${mi}.${pi} ${mat} (rigid)`); return; }
    if (pr.attributes.JOINTS_0 === undefined) return;
    const entry = { mesh: mi, prim: pi, mat, pos: readAcc(pr.attributes.POSITION), idx: readAcc(pr.indices), jtsIdx: pr.attributes.JOINTS_0, wtsIdx: pr.attributes.WEIGHTS_0 };
    if (typeof seatPos === 'function') entry.pos = seatPos(entry); // wear-transform seating
    prims.push(entry);
    console.log(`strand prim mesh${mi}.${pi} ${mat}: ${pr.attributes.POSITION ? '' : ''}${prims[prims.length - 1].pos.length / 3} verts`);
  });
});

/* ---------------- small vec helpers ---------------- */
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const len = (a) => Math.hypot(a[0], a[1], a[2]) || 1e-12;
const norm = (a) => { const l = len(a); return [a[0] / l, a[1] / l, a[2] / l]; };
const scale = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];

function pcaAxis(pts) {
  const c = [0, 0, 0];
  for (const p of pts) { c[0] += p[0]; c[1] += p[1]; c[2] += p[2]; }
  c[0] /= pts.length; c[1] /= pts.length; c[2] /= pts.length;
  let xx = 0, xy = 0, xz = 0, yy = 0, yz = 0, zz = 0;
  for (const p of pts) {
    const d = sub(p, c);
    xx += d[0] * d[0]; xy += d[0] * d[1]; xz += d[0] * d[2]; yy += d[1] * d[1]; yz += d[1] * d[2]; zz += d[2] * d[2];
  }
  let v = [1, 0.3, 0.2];
  for (let i = 0; i < 40; i++) {
    const w = [xx * v[0] + xy * v[1] + xz * v[2], xy * v[0] + yy * v[1] + yz * v[2], xz * v[0] + yz * v[1] + zz * v[2]];
    const wl = len(w);
    if (!(wl > 1e-300)) { v = [0, 1, 0]; break; } // degenerate covariance (coincident verts): arbitrary axis
    v = [w[0] / wl, w[1] / wl, w[2] / wl];
  }
  return { axis: v, centroid: c };
}

function arcTable(pts) {
  const cum = [0];
  for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + len(sub(pts[i], pts[i - 1])));
  return { cum, total: cum[cum.length - 1] };
}
function pointAtArc(pts, cum, s) {
  const total = cum[cum.length - 1];
  s = Math.min(Math.max(s, 0), total);
  let i = 0;
  while (i < cum.length - 2 && cum[i + 1] < s) i++;
  const f = (s - cum[i]) / Math.max(cum[i + 1] - cum[i], 1e-12);
  const p = add(pts[i], scale(sub(pts[i + 1], pts[i]), f));
  return { p, seg: i, frac: f, sFloat: i + f };
}
function nearestOnPolyline(pts, cum, p) {
  let best = { d2: Infinity, s: 0, point: pts[0] };
  for (let i = 0; i < pts.length - 1; i++) {
    const a = pts[i], ab = sub(pts[i + 1], a);
    const t = Math.min(1, Math.max(0, dot(sub(p, a), ab) / Math.max(dot(ab, ab), 1e-12)));
    const q = add(a, scale(ab, t));
    const d2 = dot(sub(p, q), sub(p, q));
    if (d2 < best.d2) best = { d2, s: cum[i] + t * (cum[i + 1] - cum[i]), point: q };
  }
  return best;
}

/* rotation-minimising frames along a polyline (points) */
function rmfFrames(pts) {
  const n = pts.length;
  const T = [], N = [], B = [];
  for (let i = 0; i < n; i++) {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)];
    T.push(norm(sub(b, a)));
  }
  // initial normal: deterministic perpendicular of T0
  const t0 = T[0];
  const ax = Math.abs(t0[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0];
  let nv = norm(sub(ax, scale(t0, dot(ax, t0))));
  N.push(nv); B.push(cross(t0, nv));
  for (let i = 1; i < n; i++) {
    // parallel transport: rotate previous N by the rotation T[i-1]->T[i]
    const a = T[i - 1], b = T[i];
    const c = cross(a, b), s = len(c), co = dot(a, b);
    if (s < 1e-9) nv = N[i - 1].slice();
    else {
      const k = norm(c), ang = Math.atan2(s, co), K = [[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]];
      const v = N[i - 1];
      const kv = cross(k, v);
      nv = norm([
        v[0] + kv[0] * Math.sin(ang) + (k[0] * dot(k, v)) * (1 - Math.cos(ang)),
        v[1] + kv[1] * Math.sin(ang) + (k[1] * dot(k, v)) * (1 - Math.cos(ang)),
        v[2] + kv[2] * Math.sin(ang) + (k[2] * dot(k, v)) * (1 - Math.cos(ang)),
      ]);
      void K;
    }
    // re-orthogonalise against T[i]
    nv = norm(sub(nv, scale(T[i], dot(nv, T[i]))));
    N.push(nv); B.push(cross(T[i], nv));
  }
  return { T, N, B };
}
function frameAt(frames, pts, sFloat) {
  const n = pts.length;
  const i = Math.min(Math.floor(sFloat), Math.max(0, n - 2));
  const f = Math.min(1, Math.max(0, sFloat - i));
  const mix = (A) => norm(add(A[i], scale(sub(A[Math.min(i + 1, n - 1)], A[i]), f)));
  let T = mix(frames.T), N = mix(frames.N);
  N = norm(sub(N, scale(T, dot(N, T))));
  const B = cross(T, N);
  const P = add(pts[i], scale(sub(pts[Math.min(i + 1, n - 1)], pts[i]), f));
  return { P, T, N, B };
}
/* One interpolated frame+point at parameter s along a polyline —
   THE interpolation used by storage, by the gate, and (mirrored)
   by the runtime deform. Position and frame share one lerp so
   they stay consistent at segment joins. */
function lerpFrameAt(pts, frames, s) {
  const n = pts.length;
  const i = Math.min(Math.floor(s), Math.max(0, n - 2));
  const f = Math.min(1, Math.max(0, s - i));
  const j = Math.min(i + 1, n - 1);
  const mixv = (A) => {
    const x = A[i][0] + (A[j][0] - A[i][0]) * f;
    const y = A[i][1] + (A[j][1] - A[i][1]) * f;
    const z = A[i][2] + (A[j][2] - A[i][2]) * f;
    const l = Math.hypot(x, y, z) || 1e-12;
    return [x / l, y / l, z / l];
  };
  const T = mixv(frames.T);
  let N = mixv(frames.N);
  N = norm(sub(N, scale(T, dot(N, T))));
  const B = cross(T, N);
  const P = [
    pts[i][0] + (pts[j][0] - pts[i][0]) * f,
    pts[i][1] + (pts[j][1] - pts[i][1]) * f,
    pts[i][2] + (pts[j][2] - pts[i][2]) * f,
  ];
  return { P, T, N, B };
}
/* THE deform (runtime formula, gated below at bind):
   pos = P(s) + Frame(s) * (A * oStored)
   where Frame(s) columns are (T,N,B) at s, A is the vert's stored
   3x3 (row-major), oStored its stored offset. At bind, storage set
   A = G^T C and oStored = C^T (p - P_g) with G/C the guide/card
   lerped frames at the matched fraction, so Frame*(A*oStored)
   = G * G^T * C * C^T * d = d exactly. */
function deformVert(pts, frames, s, A, o) {
  const { P, T, N, B } = lerpFrameAt(pts, frames, s);
  const gx = A[0] * o[0] + A[1] * o[1] + A[2] * o[2];
  const gy = A[3] * o[0] + A[4] * o[1] + A[5] * o[2];
  const gz = A[6] * o[0] + A[7] * o[1] + A[8] * o[2];
  return [
    P[0] + T[0] * gx + N[0] * gy + B[0] * gz,
    P[1] + T[1] * gx + N[1] * gy + B[1] * gz,
    P[2] + T[2] * gx + N[2] * gy + B[2] * gz,
  ];
}

/* A_v = G^T * C (both frames as basis matrices with columns
   (T,N,B)): A[i][j] = G_i . C_j. Pairs with oStored = C^T d as in
   deformVert's identity. */
function relMat(G, C) {
  const Gb = [G.T, G.N, G.B], Cb = [C.T, C.N, C.B];
  const A = new Float64Array(9);
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) A[i * 3 + j] = dot(Gb[i], Cb[j]);
  return A;
}

/* ---------------- cards ---------------- */
const cards = [];   // {prim, verts:[indices], pts, line, cum, total, root, tan0}
let vertCursor = 0;
const primVertBase = [];
for (const pr of prims) {
  primVertBase.push(vertCursor);
  const nv = pr.pos.length / 3;
  const parent = new Int32Array(nv);
  for (let i = 0; i < nv; i++) parent[i] = i;
  const find = (x) => { while (parent[x] !== x) { parent[x] = parent[parent[x]]; x = parent[x]; } return x; };
  const idx = pr.idx;
  for (let t = 0; t < idx.length; t += 3) {
    const ra = find(idx[t]), rb = find(idx[t + 1]), rc = find(idx[t + 2]);
    if (ra !== rb) parent[ra] = rb;
    if (rb !== rc) parent[rb] = rc;
  }
  const compMap = new Map();
  for (let v = 0; v < nv; v++) {
    const r = find(v);
    if (!compMap.has(r)) compMap.set(r, []);
    compMap.get(r).push(v);
  }
  for (const verts of compMap.values()) {
    if (verts.length < 2) continue; // degenerate speck: no strand to extract (its verts bind via the fallback below)
    const pts = verts.map(v => [pr.pos[v * 3], pr.pos[v * 3 + 1], pr.pos[v * 3 + 2]]);
    cards.push({ prim: prims.indexOf(pr), verts, pts });
  }
  vertCursor += nv;
}
console.log(`cards: ${cards.length} across ${prims.length} prims, strand verts ${vertCursor}`);

/* centrelines */
for (const card of cards) {
  const { axis, centroid } = pcaAxis(card.pts);
  const proj = card.pts.map(p => dot(sub(p, centroid), axis));
  const order = card.pts.map((_, i) => i).sort((a, b) => proj[a] - proj[b]);
  // root end = end whose verts sit closest to the head joint
  const endA = order.slice(0, Math.max(1, Math.floor(order.length * 0.12)));
  const endB = order.slice(-Math.max(1, Math.floor(order.length * 0.12)));
  const dA = endA.reduce((s, i) => s + len(sub(card.pts[i], HEAD)), 0) / endA.length;
  const dB = endB.reduce((s, i) => s + len(sub(card.pts[i], HEAD)), 0) / endB.length;
  const flip = dB < dA;
  const sorted = flip ? [...order].reverse() : order;
  // rough length from sorted-projection span + centroid path
  const span = Math.abs(proj[order[order.length - 1]] - proj[order[0]]);
  const K = Math.max(1, Math.min(16, Math.round(span / SEG_LEN), card.pts.length - 1));
  const line = [];
  for (let bIdx = 0; bIdx <= K; bIdx++) {
    const lo = Math.floor(sorted.length * bIdx / (K + 1));
    const hi = Math.max(lo + 1, Math.floor(sorted.length * (bIdx + 1) / (K + 1)));
    const c = [0, 0, 0];
    const cnt = Math.min(hi, sorted.length) - lo;
    if (cnt <= 0) { line.push(line.length ? line[line.length - 1].slice() : card.pts[sorted[0]].slice()); continue; }
    for (let j = lo; j < Math.min(hi, sorted.length); j++) { const p = card.pts[sorted[j]]; c[0] += p[0]; c[1] += p[1]; c[2] += p[2]; }
    line.push([c[0] / cnt, c[1] / cnt, c[2] / cnt]);
  }
  const { cum, total } = arcTable(line);
  card.line = line; card.cum = cum; card.total = total;
  card.root = line[0];
  card.tan0 = K >= 1 && line.length > 1 ? norm(sub(line[1], line[0])) : [0, -1, 0];
  card.K = K;
}

/* every card gets its own RMF path (binding is relative-frame) */
for (const card of cards) card.frames = rmfFrames(card.line);

/* ---------------- guide selection ---------------- */
/* A vert must bind to the guide that follows its OWN card's path —
   nearest by PATH DISTANCE over the whole centreline, not by root.
   Root-only coverage makes distant cards (flyaways, side sheets
   whose roots sit >GUIDE_R from every selected root) bind across
   the head with dm-scale offsets. Path distance = mean distance
   from the card's centreline points to the guide's centreline. */
function pathDist(card, gv) {
  let s = 0;
  for (const p of card.line) s += Math.sqrt(nearestOnPolyline(gv.line, gv.cum, p).d2);
  return s / card.line.length;
}
const byLen = [...cards].sort((a, b) => b.total - a.total);
const guides = [];  // card refs
for (const card of byLen) {
  let best = null, bestPD = Infinity;
  for (const gv of guides) {
    if (len(sub(card.root, gv.root)) > GUIDE_R) continue;      // cheap reject
    if (dot(card.tan0, gv.tan0) < 0.7) continue;
    const ratio = card.total / gv.total;
    if (ratio < 0.4 || ratio > 1.25) continue;
    if (gv.total < card.total * MIN_GUIDE_LEN_FRAC) continue;
    const pd = pathDist(card, gv);
    if (pd < bestPD) { bestPD = pd; best = gv; }
  }
  if (best && bestPD < PATH_OK) { card.guide = best; }
  else if (guides.length < MAX_GUIDES) { card.guide = card; guides.push(card); }
  else { // budget exhausted: nearest by path distance, honestly
    let bd = Infinity;
    for (const gv of guides) { const pd = pathDist(card, gv); if (pd < bd) { bd = pd; best = gv; } }
    card.guide = best;
  }
}
// cards that found no length-OK match were made guides above only when
// best existed but failed length — re-check: such cards need their own
// guide, else tip squash. Second pass: promote them if budget allows.
for (const card of cards) {
  if (card.guide !== card && card.guide && card.guide.total < card.total * MIN_GUIDE_LEN_FRAC && guides.length < MAX_GUIDES) {
    card.guide = card; guides.push(card);
  }
}
const guideIndex = new Map(guides.map((gv, i) => [gv, i]));
console.log(`guides selected: ${guides.length}`);

/* guide bind frames */
for (const gv of guides) gv.frames = rmfFrames(gv.line);

/* ---------------- bindings (relative-frame, per-vert A) ----------------
   Per vert: guideIdx, s (guide param at the vert's own arc
   fraction), oStored = C^T (p - P_g(s)) — coords in the vert's own
   card frame of the offset from the GUIDE centre point — and
   A = G^T C (9 floats). deformVert(bind) reproduces p exactly;
   the gate below runs deformVert itself on every vert. */
const N = vertCursor;
const bGuide = new Uint16Array(N);
const bS = new Float32Array(N);
const bOff = new Float32Array(N * 3);
const bA = new Float32Array(N * 9);
let maxOff = 0, offSum = 0;
const offHist = [];
const boundMark = new Uint8Array(N);
/* fallback for verts in degenerate (<2-vert) components skipped
   during card extraction: bind each to the nearest guide point
   with zero offset (they ride the guide surface exactly). */
{
  let fb = 0;
  const inCards = new Uint8Array(N);
  for (const card of cards) for (const v of card.verts) inCards[primVertBase[card.prim] + v] = 1;
  for (let gi2 = 0; gi2 < N; gi2++) {
    if (inCards[gi2]) continue;
    // position from the prim arrays
    let primIdx = 0; while (primIdx + 1 < primVertBase.length && primVertBase[primIdx + 1] <= gi2) primIdx++;
    if (primVertBase[primIdx] > gi2) primIdx--;
    const pr = prims[primIdx]; const v = gi2 - primVertBase[primIdx];
    const p = [pr.pos[v * 3], pr.pos[v * 3 + 1], pr.pos[v * 3 + 2]];
    let bestG = 0, bestS = 0, bestD = Infinity;
    guides.forEach((gv, g3) => {
      for (let k = 0; k < gv.line.length; k++) {
        const d = len(sub(p, gv.line[k]));
        if (d < bestD) { bestD = d; bestG = g3; bestS = k; }
      }
    });
    bGuide[gi2] = bestG; bS[gi2] = bestS;
    bOff[gi2 * 3] = 0; bOff[gi2 * 3 + 1] = 0; bOff[gi2 * 3 + 2] = 0;
    const I9 = [1, 0, 0, 0, 1, 0, 0, 0, 1];
    for (let k = 0; k < 9; k++) bA[gi2 * 9 + k] = I9[k];
    boundMark[gi2] = 1; fb++;
  }
  if (fb) console.log(`fallback-bound degenerate verts: ${fb}`);
}
for (const card of cards) {
  const gv = card.guide, gi = guideIndex.get(gv);
  for (let vi = 0; vi < card.verts.length; vi++) {
    const v = card.verts[vi];
    const p = card.pts[vi];
    const near = nearestOnPolyline(card.line, card.cum, p);
    const frac = card.total > 1e-9 ? near.s / card.total : 0;
    const atG = pointAtArc(gv.line, gv.cum, frac * gv.total);
    const s = atG.sFloat;
    const frG = lerpFrameAt(gv.line, gv.frames, s);
    const atC = pointAtArc(card.line, card.cum, frac * card.total);
    const frC = lerpFrameAt(card.line, card.frames, atC.sFloat);
    const d = sub(p, frG.P);
    const A = relMat(frG, frC);
    const gIdx = primVertBase[card.prim] + v;
    bGuide[gIdx] = gi;
    bS[gIdx] = s;
    // oStored in card-frame coords, component order (T,N,B)
    bOff[gIdx * 3] = dot(d, frC.T);
    bOff[gIdx * 3 + 1] = dot(d, frC.N);
    bOff[gIdx * 3 + 2] = dot(d, frC.B);
    for (let k = 0; k < 9; k++) bA[gIdx * 9 + k] = A[k];
    const ol = len(d);
    offSum += ol; if (ol > maxOff) maxOff = ol; offHist.push(ol);
  }
}
offHist.sort((a, b) => a - b);
const pct = (q) => (offHist[Math.min(offHist.length - 1, Math.floor(q * offHist.length))] * 1000).toFixed(1);
console.log(`bindings: ${N} verts, |offset from guide centre| mean ${(offSum / N * 1000).toFixed(1)}mm p50 ${pct(0.5)}mm p95 ${pct(0.95)}mm p99 ${pct(0.99)}mm max ${(maxOff * 1000).toFixed(1)}mm`);

/* BIND ROUND-TRIP GATE: the runtime deform at bind must return
   every source vert (float32 storage tolerance only). */
{
  let worst = 0, worstV = -1;
  const errHist = [];
  for (const card of cards) {
    const gv = card.guide;
    for (let vi = 0; vi < card.verts.length; vi++) {
      const gIdx = primVertBase[card.prim] + card.verts[vi];
      const A = new Float64Array(9);
      for (let k = 0; k < 9; k++) A[k] = bA[gIdx * 9 + k];
      const rec = deformVert(gv.line, gv.frames, bS[gIdx], A,
        [bOff[gIdx * 3], bOff[gIdx * 3 + 1], bOff[gIdx * 3 + 2]]);
      const err = len(sub(rec, card.pts[vi]));
      errHist.push(err);
      if (err > worst) { worst = err; worstV = gIdx; }
    }
  }
  errHist.sort((a, b) => a - b);
  const ep = (q) => (errHist[Math.floor(q * errHist.length)] * 1000).toFixed(3);
  console.log(`bind round-trip (runtime deform at bind): worst ${(worst * 1000).toFixed(3)}mm (vert ${worstV}), p50 ${ep(0.5)}mm p95 ${ep(0.95)}mm p99 ${ep(0.99)}mm`);
  if (worst > 0.002) { console.error('ROUND-TRIP GATE FAILED (>2mm)'); process.exit(1); }
}

/* ---------------- write out ---------------- */
const particles = guides.reduce((s, gv) => s + gv.line.length, 0);
const header = {
  kind: 'wh-strand-guides', version: 1,
  source: glbPath.split('/').pop(),
  bakedFrom: glbPath,
  frame: wearInfo
    ? 'BODY-JOINT frame, wear-seated: strand verts skinned by the part skeleton driven by the BODY skeleton at bind (per-joint world delta); runtime treats bake space as sim space, anchors follow the body Head bone'
    : 'part GLB geometry space (bind); runtime maps bind->world with the part root matrix at bind, anchors follow the body head bone',
  wear: wearInfo,
  prims: prims.map(p => ({ mesh: p.mesh, prim: p.prim, material: p.mat, verts: p.pos.length / 3 })),
  counts: { cards: cards.length, guides: guides.length, particles, verts: N },
  bindSdf: bodySDF ? (() => { const arr = []; for (const gv of guides) for (const p of gv.line) arr.push(+bodySDF.sample(p[0], p[1], p[2]).toFixed(4)); return arr; })() : null,
  params: { guideRadius: GUIDE_R, pathOk: PATH_OK, maxGuides: MAX_GUIDES, segLenTarget: SEG_LEN },
  guides: guides.map((gv) => ({
    points: gv.line.map(p => p.map(v => +v.toFixed(5))),
    rootFrame: { T: gv.frames.T[0].map(v => +v.toFixed(5)), N: gv.frames.N[0].map(v => +v.toFixed(5)), B: gv.frames.B[0].map(v => +v.toFixed(5)) },
  })),
  binLayout: {
    file: outPrefix.split('/').pop() + '.bin',
    order: ['guideIdx:u16 block', 's:f32 block', 'off:3xf32 block (card-frame coords, order T,N,B)', 'relA:9xf32 block (row-major G^T C)'],
    vertOrder: 'prims in header order, GLB vertex order within each prim',
    bytesPerVert: 54,
    deform: 'pos = P_g(s) + Frame_g(s) * (relA * off), Frame columns (T,N,B) interpolated along the CURRENT guide polyline (RMF propagated from the posed root frame). Bind round-trip gated <=2mm at bake time (float32).',
  },
};
// binding arrays ship as concatenated blocks, not interleaved:
const binFull = Buffer.concat([
  Buffer.from(bGuide.buffer, bGuide.byteOffset, N * 2),
  Buffer.from(bS.buffer, bS.byteOffset, N * 4),
  Buffer.from(bOff.buffer, bOff.byteOffset, N * 12),
  Buffer.from(bA.buffer, bA.byteOffset, N * 36),
]);
writeFileSync(outPrefix + '.json', JSON.stringify(header));
writeFileSync(outPrefix + '.bin', binFull);
console.log(`wrote ${outPrefix}.json + .bin (${(binFull.length / 1e6).toFixed(2)} MB), particles=${particles}`);
