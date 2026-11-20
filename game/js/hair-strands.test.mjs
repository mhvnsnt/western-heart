// hair-strands.test.mjs — verifies the strand-level hair solver.
// Run: node --test game/js/hair-strands.test.mjs
// The REAL bake (customization data for Megami's straight hair) is
// loaded when present; synthetic mini-bakes keep the physics tests
// independent of it.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';

const { StrandHairSystem } = await import('./hair-strands.js');
const { BodySDF } = await import('./collision.js');

const IDENT = () => { const m = new Float64Array(16); m[0] = m[5] = m[10] = m[15] = 1; return m; };

/* ---- synthetic bake: one guide strand, points root->tip ---- */
function synthBake(points, opts = {}) {
  // frames: tangent along the strand; N = any perpendicular
  const T = [0, -1, 0], N = [1, 0, 0], B = [0, 0, -1];
  const header = {
    kind: 'wh-strand-guides', version: 1,
    prims: [{ verts: opts.verts ?? 0 }],
    counts: { cards: 1, guides: 1, particles: points.length, verts: opts.verts ?? 0 },
    guides: [{ points, rootFrame: { T, N, B } }],
  };
  const NV = header.counts.verts;
  const bin = new ArrayBuffer(NV * 54);
  if (NV > 0) {
    const u16 = new Uint16Array(bin, 0, NV);
    const fs = new Float32Array(bin, NV * 2, NV);
    const fo = new Float32Array(bin, NV * 2 + NV * 4, NV * 3);
    const fa = new Float32Array(bin, NV * 2 + NV * 4 + NV * 12, NV * 9);
    for (let v = 0; v < NV; v++) {
      u16[v] = 0; fs[v] = opts.sOf ? opts.sOf(v) : v % (points.length - 1);
      fo[v * 3] = 0; fo[v * 3 + 1] = 0.01; fo[v * 3 + 2] = 0; // 10mm in +N (card T,N,B order: T=0,N=0.01,B=0)
      const A = [1, 0, 0, 0, 1, 0, 0, 0, 1];
      for (let k = 0; k < 9; k++) fa[v * 9 + k] = A[k];
    }
  }
  return { header, bin };
}
function mkSys(points, opts = {}) {
  const { header, bin } = synthBake(points, opts);
  const sys = new StrandHairSystem(header, bin, opts.sys || {});
  sys.setAnchor(IDENT(), IDENT());
  return sys;
}
const segLen = (pos, i, j) => Math.hypot(pos[j * 3] - pos[i * 3], pos[j * 3 + 1] - pos[i * 3 + 1], pos[j * 3 + 2] - pos[i * 3 + 2]);
const distToSeg = (p, a, b) => {
  const ab = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
  const l2 = ab[0] ** 2 + ab[1] ** 2 + ab[2] ** 2;
  let t = l2 > 0 ? ((p[0] - a[0]) * ab[0] + (p[1] - a[1]) * ab[1] + (p[2] - a[2]) * ab[2]) / l2 : 0;
  t = Math.min(1, Math.max(0, t));
  const q = [a[0] + ab[0] * t, a[1] + ab[1] * t, a[2] + ab[2] * t];
  return Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2]);
};

/* A horizontal strand held at its root above a shoulder-height
   capsule. Gravity must drape it onto the capsule; collision ON
   rests ON the surface, collision OFF falls THROUGH. Capsule:
   axis along X at y=1.05, radius 0.11+0.006 margin (shoulder-like,
   cf. baked Shoulder->Arm r=0.1145 at y~1.35). */
/* The geometry, from the measured diag runs (do not guess here):
   a strand rooted at z=-0.20 hangs at z~-0.14..-0.20 — it keeps its
   own z channel under gravity (hang = mostly y motion + small z
   pull-in). So the capsule is placed IN that channel: axis along X
   at (y=1.05, z=-0.155), radius 0.116. The hanging strand's lower
   particles (k>=7) fall into the capsule's front-top volume
   (measured OFF clearance at the tip: 0.137 without the capsule
   moved; with the axis at z=-0.155 the penetration is real), and
   with collision ON they must rest ON the surface instead. */
const CAP = { a: [-0.4, 1.05, -0.155], b: [0.4, 1.05, -0.155], r: 0.116, friction: 0.35 };
function fallSetup(collisionOn) {
  const pts = [];
  for (let k = 0; k <= 10; k++) pts.push([0, 1.45 - 0.001 * k, -0.20 + 0.03 * k]); // root z=-0.20, extends +z horizontal
  const sys = mkSys(pts, { sys: { substeps: 3, iterations: 8, bendStiffness: 0.1 } });
  if (collisionOn) sys.setCollision({ spheres: [], capsules: [CAP], sdf: null });
  return sys;
}

test('strand FALLS under gravity and DRAPES (direction not pinned)', () => {
  const sys = fallSetup(false);
  const pos = sys.particlePositions();
  const tipY0 = pos[10 * 3 + 1];
  for (let f = 0; f < 180; f++) sys.step(1 / 60);
  // vertical hang from a horizontal start (measured diag): tip drops
  // ~0.28m, z pulls in from +0.10 to ~-0.14 — the strand hangs in its
  // own z channel, progressively lower per particle.
  assert.ok(tipY0 - pos[10 * 3 + 1] > 0.2, `tip fell ${(tipY0 - pos[10 * 3 + 1]).toFixed(3)}m`);
  assert.ok(pos[10 * 3 + 2] < -0.10, `tip swung toward the root channel, z=${pos[10 * 3 + 2].toFixed(3)}`);
  // drape is progressive along the strand, not a rigid body swing:
  // each particle hangs lower than the one before it
  for (let k = 1; k <= 10; k++) assert.ok(pos[k * 3 + 1] < pos[(k - 1) * 3 + 1], `particle ${k} hangs below ${k - 1}`);
  // the hanging strand passes the capsule centre height at its z
  assert.ok(pos[10 * 3 + 1] < CAP.a[1] + CAP.r, 'tip below capsule top surface height');
});

test('collision ON: strand comes to REST on the capsule (sustained contact, no penetration)', () => {
  const sys = fallSetup(true);
  const pos = sys.particlePositions();
  for (let f = 0; f < 180; f++) sys.step(1 / 60);
  // every particle at or outside the capsule surface (tol 2mm)
  let minD = Infinity;
  for (let k = 1; k <= 10; k++) {
    const p = [pos[k * 3], pos[k * 3 + 1], pos[k * 3 + 2]];
    const d = distToSeg(p, CAP.a, CAP.b);
    minD = Math.min(minD, d);
    assert.ok(d >= CAP.r - 0.002, `particle ${k} penetration: d=${d.toFixed(4)} < r=${CAP.r}`);
  }
  // sustained contact: at least one particle rests within 3mm of surface
  assert.ok(minD <= CAP.r + 0.003, `resting contact expected, minD=${minD.toFixed(4)}`);
  // rest: velocities ~0 over the last stretch
  const yBefore = pos[10 * 3 + 1];
  for (let f = 0; f < 30; f++) sys.step(1 / 60);
  assert.ok(Math.abs(pos[10 * 3 + 1] - yBefore) < 0.002, `rest state: tip moved ${Math.abs(pos[10 * 3 + 1] - yBefore).toFixed(4)}m in 0.5s`);
});

test('collision OFF is the discriminating control: strand passes THROUGH the capsule volume', () => {
  const on = fallSetup(true), off = fallSetup(false);
  for (let f = 0; f < 180; f++) { on.step(1 / 60); off.step(1 / 60); }
  const po = on.particlePositions(), pf = off.particlePositions();
  // OFF: at least one particle ends INSIDE the capsule (penetration) —
  // the hanging strand's path crosses the capsule's front volume.
  let maxPenOff = 0, minDOn = Infinity;
  for (let k = 1; k <= 10; k++) {
    const pOff = [pf[k * 3], pf[k * 3 + 1], pf[k * 3 + 2]];
    maxPenOff = Math.max(maxPenOff, CAP.r - distToSeg(pOff, CAP.a, CAP.b));
    const pOn = [po[k * 3], po[k * 3 + 1], po[k * 3 + 2]];
    minDOn = Math.min(minDOn, distToSeg(pOn, CAP.a, CAP.b));
  }
  assert.ok(maxPenOff > 0.005, `OFF must penetrate the capsule (>5mm), got maxPen=${(maxPenOff * 1000).toFixed(1)}mm`);
  assert.ok(minDOn >= CAP.r - 0.002, `ON keeps every particle out, minD=${minDOn.toFixed(4)}`);
});

test('segment lengths preserved under gravity + collision (length-only constraints)', () => {
  const sys = fallSetup(true);
  const rest = sys.guideRestLengths(0);
  for (let f = 0; f < 180; f++) sys.step(1 / 60);
  const pos = sys.particlePositions();
  for (let k = 0; k < 10; k++) {
    const L = segLen(pos, k, k + 1);
    assert.ok(Math.abs(L - rest[k]) / rest[k] < 0.02, `seg ${k}: ${L.toFixed(4)} vs rest ${rest[k].toFixed(4)}`);
  }
});

test('root pinning follows the head anchor exactly', () => {
  const sys = fallSetup(true);
  const m = IDENT(); m[12] = 0.05; m[13] = -0.02; m[14] = 0.03; // head moved
  sys.setHeadPose(m);
  sys.step(1 / 60);
  const pos = sys.particlePositions();
  assert.ok(Math.abs(pos[0] - 0.05) < 1e-9 && Math.abs(pos[1] - 1.43) < 1e-9 && Math.abs(pos[2] - (-0.17)) < 1e-9,
    `root at ${pos[0]},${pos[1]},${pos[2]}`);
});

test('deform writes bound verts offset from the live polyline (round-trip at bind)', () => {
  const pts = [];
  for (let k = 0; k <= 6; k++) pts.push([0.01 * k, 1.5 - 0.03 * k, -0.02 * k]);
  const sys = mkSys(pts, { verts: 12 });
  const out = new Float32Array(12 * 3);
  sys.deform(out);
  // vert v: s = v % 6, offset 10mm along the frame normal.
  // At bind the frame's N was authored [1,0,0] and relA = identity,
  // so out ≈ pointAt(s) + [0.01, 0, 0] (RMF transport may rotate N
  // slightly along a straight-ish strand; tolerance 3mm).
  for (let v = 0; v < 12; v++) {
    const s = v % 6;
    const px = pts[s][0] + (pts[s + 1][0] - pts[s][0]) * 0; // s integer -> point s
    const err = Math.hypot(out[v * 3] - (pts[s][0] + 0.01), out[v * 3 + 1] - pts[s][1], out[v * 3 + 2] - pts[s][2]);
    assert.ok(err < 0.003, `vert ${v} err ${err.toFixed(4)}`);
  }
});

/* ---------- real bake integration (when staged locally) ---------- */
const CANDIDATES = [
  new URL('../../../baked/megami-v5/megami-strands.json', import.meta.url),
  new URL('../../customization/collision/megami/megami-strands.json', import.meta.url),
];
const bakeURL = CANDIDATES.find(u => existsSync(u));

test('real bake: deform at bind reproduces the strand data particles; perf smoke at real counts', { skip: !bakeURL && 'strand bake not staged' }, () => {
  const header = JSON.parse(readFileSync(bakeURL, 'utf8'));
  const binBuf = readFileSync(new URL(bakeURL.href.replace(/\.json$/, '.bin')));
  const bin = binBuf.buffer.slice(binBuf.byteOffset, binBuf.byteOffset + binBuf.byteLength);
  const sys = new StrandHairSystem(header, bin, { substeps: 3, iterations: 4 });
  sys.setAnchor(IDENT(), IDENT());
  sys.resetToBind();
  assert.equal(sys.particleCount(), header.counts.particles);
  const out = new Float32Array(header.counts.verts * 3);
  sys.deform(out);
  // deform writes finite positions for every vert
  let bad = 0;
  for (let i = 0; i < out.length; i++) if (!Number.isFinite(out[i])) bad++;
  assert.equal(bad, 0);
  // perf smoke: one full step at real guide counts
  const t0 = performance.now();
  sys.step(1 / 60);
  const ms = performance.now() - t0;
  console.log(`real-bake step: ${ms.toFixed(1)} ms (${sys.particleCount()} particles, ${header.counts.guides} guides, ${header.counts.verts} verts)`);
  assert.ok(ms < 100, `step too slow: ${ms.toFixed(1)}ms`);
});

/* The runtime deform at bind must land on the SOURCE hair — this is
   the gate that catches frame-convention drift between the bake
   and the runtime (segment tangents vs the bake's centred point
   frames cost 41mm at the tips before it was fixed). Needs the
   source GLB; skipped where it is not staged. */
const GLB_CANDIDATES = [
  new URL('/home/hatch/workspace/_hair-fit-20261109/glb/megami-hair-angel-straight.glb', 'file:///'),
];
test('real bake: runtime deform at bind matches the source GLB verts', { skip: !(bakeURL && GLB_CANDIDATES.some(u => existsSync(u))) && 'bake or GLB not staged' }, (t) => {
  const bakeHeader0 = JSON.parse(readFileSync(bakeURL, 'utf8'));
  if (bakeHeader0.wear) {
    // WEAR-SEATED bake: bake space is the body-joint frame (verts
    // skinned by the part skeleton driven by the body skeleton),
    // NOT the raw GLB geometry — the raw-GLB comparison is invalid
    // by construction. The bake's own round-trip gate (<=2mm,
    // enforced in bake-strands.mjs, measured 0.000mm on this bake)
    // plus the finiteness test above carry the guarantee here.
    t.skip('wear-seated bake: raw-GLB comparison not applicable (bake space = body-joint frame)');
    return;
  }
  const header = JSON.parse(readFileSync(bakeURL, 'utf8'));
  const binBuf = readFileSync(new URL(bakeURL.href.replace(/\.json$/, '.bin')));
  const bin = binBuf.buffer.slice(binBuf.byteOffset, binBuf.byteOffset + binBuf.byteLength);
  const glbUrl = GLB_CANDIDATES.find(u => existsSync(u));
  const glb = readFileSync(glbUrl);
  const clen = glb.readUInt32LE(12);
  const js = JSON.parse(glb.subarray(20, 20 + clen).toString('utf8'));
  const binOff = 20 + clen + 8;
  const accData = (idx) => {
    const a = js.accessors[idx]; const bv = js.bufferViews[a.bufferView];
    const off = binOff + (bv.byteOffset || 0) + (a.byteOffset || 0);
    const ncomp = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4 }[a.type];
    const T = a.componentType === 5126 ? Float32Array : Uint16Array;
    return new T(glb.buffer, glb.byteOffset + off, a.count * ncomp);
  };
  const NV = header.counts.verts;
  const srcPos = new Float32Array(NV * 3);
  let bse = 0;
  for (const prim of header.prims) {
    const p = js.meshes[prim.mesh].primitives[prim.prim];
    srcPos.set(accData(p.attributes.POSITION), bse * 3); bse += prim.verts;
  }
  const sys = new StrandHairSystem(header, bin, {});
  sys.setAnchor(IDENT(), IDENT());
  sys.resetToBind();
  const out = new Float32Array(NV * 3);
  sys.deform(out);
  const errs = new Float64Array(NV);
  for (let v = 0; v < NV; v++) errs[v] = Math.hypot(out[v * 3] - srcPos[v * 3], out[v * 3 + 1] - srcPos[v * 3 + 1], out[v * 3 + 2] - srcPos[v * 3 + 2]);
  errs.sort();
  const pc = (q) => errs[Math.floor(q * NV)] * 1000;
  console.log(`runtime deform vs GLB: p50 ${pc(0.5).toFixed(2)}mm p95 ${pc(0.95).toFixed(2)}mm p99 ${pc(0.99).toFixed(2)}mm max ${pc(0.99999).toFixed(2)}mm`);
  assert.ok(pc(0.95) < 1, `p95 deform error ${pc(0.95).toFixed(2)}mm`);
  assert.ok(pc(1 - 1e-9) < 3, `max deform error ${pc(0.99999).toFixed(2)}mm`);
});

/* ---------- regression tests for the 2026-11-09 collision fixes ---------- */

/* Deepest-projection-wins: a particle authored INSIDE two
   overlapping capsules (the real bake's trap: guide roots sit
   inside both Neck->Head and the r=0.2434 Spine2->Neck capsule)
   must settle OUTSIDE both, calmly — sequential projection
   ping-ponged it to a measured 13 m/s slingshot. */
test('overlapping capsules: trapped particle settles calmly (deepest-projection regression)', () => {
  const pts = [];
  for (let k = 0; k <= 8; k++) pts.push([0, 1.50 - 0.03 * k, 0]);
  const sys = mkSys(pts, { sys: { substeps: 3, iterations: 6, bendStiffness: 0.15 } });
  const A = { a: [0, 1.30, 0], b: [0, 1.50, 0], r: 0.10, friction: 0.35 };   // vertical, around the strand
  const B = { a: [0, 1.10, 0], b: [0, 1.42, 0], r: 0.25, friction: 0.35 };   // fat torso-like, overlaps A
  sys.setCollision({ spheres: [], capsules: [A, B], sdf: null });
  const pos = sys.particlePositions();
  for (let f = 0; f < 200; f++) sys.step(1 / 60);
  // frame-delta speed: step once more, measure actual movement
  const before = Float32Array.from(pos);
  sys.step(1 / 60);
  let maxV = 0;
  for (let i = 0; i < sys.particleCount(); i++) maxV = Math.max(maxV, Math.hypot(pos[i * 3] - before[i * 3], pos[i * 3 + 1] - before[i * 3 + 1], pos[i * 3 + 2] - before[i * 3 + 2]) * 60);
  assert.ok(maxV < 0.5, `settled speed ${maxV.toFixed(2)} m/s — ping-pong regression`);
  // free particles end outside BOTH capsules (tol 3mm)
  for (let k = 1; k <= 8; k++) {
    const p = [pos[k * 3], pos[k * 3 + 1], pos[k * 3 + 2]];
    assert.ok(distToSeg(p, A.a, A.b) >= A.r - 0.003, `particle ${k} inside capsule A`);
    assert.ok(distToSeg(p, B.a, B.b) >= B.r - 0.003, `particle ${k} inside capsule B`);
  }
});

/* Fringe rule: a <=3-particle guide is pinned wholesale — it must
   follow the head anchor rigidly and never fall. */
test('fringe guides (<=3 particles) are pinned to the head anchor', () => {
  const { header, bin } = synthBake([[0, 1.5, 0], [0.01, 1.47, 0], [0.02, 1.44, 0]], { verts: 0 });
  const sys = new StrandHairSystem(header, bin, {});
  sys.setAnchor(IDENT(), IDENT());
  assert.equal(sys.fringeGuides, 1);
  for (let f = 0; f < 120; f++) sys.step(1 / 60);
  const pos = sys.particlePositions();
  assert.ok(Math.abs(pos[2 * 3 + 1] - 1.44) < 1e-9, `fringe tip moved: y=${pos[2 * 3 + 1]}`);
});

/* Scalp-attach rule: with header.bindSdf present, particles
   authored within scalpAttachDist of the surface are pinned;
   particles beyond it fall freely. */
test('scalp-attach: bindSdf below threshold pins the particle', () => {
  const pts = [];
  for (let k = 0; k <= 6; k++) pts.push([0, 1.5 - 0.03 * k, 0]);
  const { header, bin } = synthBake(pts, { verts: 0 });
  header.bindSdf = [0.05, 0.005, 0.005, 0.05, 0.05, 0.05, 0.05]; // k1,k2 attached
  const sys = new StrandHairSystem(header, bin, {});
  sys.setAnchor(IDENT(), IDENT());
  assert.equal(sys.attachedParticles, 2);
  for (let f = 0; f < 60; f++) sys.step(1 / 60);
  const pos = sys.particlePositions();
  assert.ok(Math.abs(pos[1 * 3 + 1] - 1.47) < 1e-9 && Math.abs(pos[2 * 3 + 1] - 1.44) < 1e-9, 'attached particles held at bind');
  // the free tail (authored hanging straight down) stays extended
  // under the attached segment: tip at its bind depth, chain
  // unshortened — the attach held the top, gravity kept the tail
  assert.ok(Math.abs(pos[6 * 3 + 1] - 1.32) < 0.002, `free tip held its hang: y=${pos[6 * 3 + 1].toFixed(3)}`);
  assert.ok(pos[6 * 3 + 1] > 1.44 - 4 * 0.03 - 0.01, `tip within chain reach of the attach point: y=${pos[6 * 3 + 1].toFixed(3)}`);
});
