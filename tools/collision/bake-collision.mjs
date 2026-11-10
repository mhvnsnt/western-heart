#!/usr/bin/env node
/* ============================================================
   WESTERN HEART — bake-collision.mjs

   Bakes per-character collision data for the shared collision
   core (game/js/collision.js) from a character's rigged GLB:
     1. <name>-body.sdf.bin — a signed-distance field of the
        character's skinned BIND pose over the head / neck /
        shoulders / chest region (Int16 grid, metres/quant per
        cell), the TressFX pattern: collision volume baked offline
        from the collision surface, sampled at runtime.
     2. <name>-collision.json — the collider set for
        hair-spring.js collisionSetFromData(): capsule/sphere
        colliders FITTED from the skinned bind geometry grouped by
        dominant joint (the Unreal PhAT / Magica Cloth pattern),
        plus the SDF frame bone and margins.

   Method notes (industry standard, no hand-invented math):
   - The collision surface is the character's own skinned mesh:
     morph targets from the GLB weights are applied, then linear
     blend skinning at bind pose (node worlds × inverse bind
     matrices) — the same surface the renderer shows.
   - Distances come from a BVH over that surface (three-mesh-bvh,
     MIT — the same copy the game vendors). The BVH is built with
     { indirect: true }: the default build REWRITES the geometry's
     index buffer, which silently invalidates faceIndex lookups
     against the source index array (measured 2026-11-09: that bug
     alone produced a 59% sign-mismatch rate; with the indirect
     build the same lookups are exact).
   - The SIGN is ray parity (majority of 3 BVH rays per point):
     the surface is a UNION of shells (Daz-style body shells that
     touch and overlap — arms resting on the torso, lip layers),
     where "inside" is exactly the parity definition. The
     closest-triangle normal test is NOT used for the sign: it
     disagrees with parity precisely in the shell-contact zones,
     and there parity is the correct answer for the union field.
     Grid cells take their sign from an exact per-row parity
     sweep (one ray per grid row, crossings toggled), validated
     against the 3-ray oracle on a random cell sample (>=99%
     agreement required, else the bake falls back to the oracle
     for every cell). Ground-truth points (bone axes inside,
     clear points outside) are hard gates on the baked grid.
   - Capsule radii are measured percentiles of the skin vertices
     assigned to each collider by bind-pose segment proximity —
     fitted, never hand-typed, and rig-naming-agnostic (a
     dominant-joint grouping silently measured empty groups on
     tweak-bone rigs; see the fit section).

   Usage:
     node tools/collision/bake-collision.mjs <body.glb> <outDir> <name> \
       [--prims "Torso-3,Face-2,Lips-2,Legs-2,Arms-3,EyeSocket-2"] \
       [--voxel 0.0085] [--region x0,y0,z0,x1,y1,z1] [--frame Spine2]

   --prims is an EXACT material-name list: the character's outer
   skin shells only. Interior shells (teeth, eye parts, inner
   anatomy shells) must NOT be in the list — the field is the
   body's outer surface; the mouth interior gets its own contact
   set (see the face-contact data spec).

   The tool imports three + three-mesh-bvh from the game's
   vendored copies (game/vendor/) so the bake matches the
   runtime's libraries exactly; override with WH_VENDOR_DIR.
   ============================================================ */

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { register } from 'node:module';
import { pathToFileURL } from 'node:url';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const args = process.argv.slice(2);
const [glbPath, outDir, name] = args;
if (!glbPath || !outDir || !name) {
  console.error('usage: bake-collision.mjs <body.glb> <outDir> <name> [--prims a,b] [--voxel v] [--region x0,y0,z0,x1,y1,z1] [--frame Bone]');
  process.exit(2);
}
const opt = (flag, dflt) => {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : dflt;
};
const primFilter = opt('--prims', 'Torso-3,Face-2,Lips-2,Legs-2,Arms-3,EyeSocket-2').split(',').map((s) => s.trim());
const voxel = parseFloat(opt('--voxel', '0.0085'));
const region = opt('--region', '-0.56,0.92,-0.46,0.56,1.77,0.46').split(',').map(Number);
const frameBone = opt('--frame', 'Spine2');
const QUANT = 0.0005;

const toolDir = dirname(fileURLToPath(import.meta.url));
const vendorDir = process.env.WH_VENDOR_DIR || resolve(toolDir, '../../game/vendor');
register('data:text/javascript,' + encodeURIComponent(`
  export async function resolve(specifier, context, next) {
    if (specifier === 'three') return { url: ${JSON.stringify(pathToFileURL(resolve(vendorDir, 'three.module.js')).href)}, shortCircuit: true };
    if (specifier === 'three-mesh-bvh') return { url: ${JSON.stringify(pathToFileURL(resolve(vendorDir, 'three-mesh-bvh/index.module.js')).href)}, shortCircuit: true };
    return next(specifier, context);
  }
`));
const THREE = await import('three');
const { MeshBVH } = await import('three-mesh-bvh');

/* ---------------- GLB parsing ---------------- */
const buf = readFileSync(glbPath);
if (buf.readUInt32LE(0) !== 0x46546c67) throw new Error('not a GLB');
const jsonLen = buf.readUInt32LE(12);
const gltf = JSON.parse(buf.toString('utf8', 20, 20 + jsonLen));
const binOff = 20 + jsonLen + 8;
if ((gltf.extensionsUsed || []).includes('EXT_meshopt_compression')) {
  throw new Error('meshopt-compressed GLB not supported by this baker (decode first)');
}
const CT = { 5126: [Float32Array, 4], 5123: [Uint16Array, 2], 5125: [Uint32Array, 4], 5121: [Uint8Array, 1], 5122: [Int16Array, 2] };
const NC = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT4: 16 };
function readAccessor(idx) {
  const a = gltf.accessors[idx];
  const [Arr, itemBytes] = CT[a.componentType];
  const n = NC[a.type];
  const out = new Arr(a.count * n);
  if (a.bufferView !== undefined) {
    const bv = gltf.bufferViews[a.bufferView];
    const byteOff = binOff + (bv.byteOffset || 0) + (a.byteOffset || 0);
    const stride = bv.byteStride || itemBytes * n;
    if (stride === itemBytes * n) {
      out.set(new Arr(buf.buffer, buf.byteOffset + byteOff, a.count * n));
    } else {
      const src = new Arr(buf.buffer, buf.byteOffset + binOff + (bv.byteOffset || 0), Math.ceil(bv.byteLength / itemBytes));
      for (let i = 0; i < a.count; i++) {
        const sOff = ((a.byteOffset || 0) + i * stride) / itemBytes;
        for (let k = 0; k < n; k++) out[i * n + k] = src[sOff + k];
      }
    }
  }
  if (a.sparse) {
    // sparse override (Blender exports morph targets this way):
    // tightly packed indices + values replace the base entries
    const readPart = (part, compType) => {
      const [PArr, pBytes] = CT[compType];
      const pbv = gltf.bufferViews[part.bufferView];
      const off = binOff + (pbv.byteOffset || 0) + (part.byteOffset || 0);
      return new PArr(buf.buffer, buf.byteOffset + off, Math.floor(pbv.byteLength / pBytes));
    };
    const sIdx = readPart(a.sparse.indices, a.sparse.indices.componentType);
    const sVal = readPart(a.sparse.values, a.componentType);
    for (let s = 0; s < a.sparse.count; s++) {
      for (let k = 0; k < n; k++) out[sIdx[s] * n + k] = sVal[s * n + k];
    }
  }
  return { data: out, count: a.count, itemSize: n, normalized: !!a.normalized };
}

/* ---------------- node worlds ---------------- */
const worlds = gltf.nodes.map(() => null);
function compose(node) {
  const m = new THREE.Matrix4();
  if (node.matrix) return m.fromArray(node.matrix);
  const t = node.translation || [0, 0, 0], r = node.rotation || [0, 0, 0, 1], s = node.scale || [1, 1, 1];
  return m.compose(new THREE.Vector3(...t), new THREE.Quaternion(...r), new THREE.Vector3(...s));
}
function computeWorlds() {
  const visit = (ni, parent) => {
    worlds[ni] = parent ? parent.clone().multiply(compose(gltf.nodes[ni])) : compose(gltf.nodes[ni]);
    for (const c of gltf.nodes[ni].children || []) visit(c, worlds[ni]);
  };
  for (const root of gltf.scenes[gltf.scene || 0].nodes) visit(root, null);
}
computeWorlds();

/* ---------------- skinned bind surface ---------------- */
const primPos = [];      // merged world-bind positions
const primIdx = [];      // merged indices
const vertJoint = [];    // dominant joint node index per merged vert
let vOff = 0;
let primsUsed = 0;
gltf.meshes.forEach((mesh, mi) => {
  const nodeIdx = gltf.nodes.findIndex((n) => n.mesh === mi);
  if (nodeIdx < 0) return;
  const node = gltf.nodes[nodeIdx];
  const weights = mesh.weights || node.weights || [];
  mesh.primitives.forEach((prim) => {
    const mat = prim.material !== undefined ? gltf.materials[prim.material] : null;
    const matName = (mat && mat.name) || '';
    if (!primFilter.includes(matName)) return;
    if (prim.attributes.JOINTS_0 === undefined || prim.attributes.WEIGHTS_0 === undefined || node.skin === undefined) return;
    primsUsed++;
    const skin = gltf.skins[node.skin];
    const ibm = readAccessor(skin.inverseBindMatrices).data;
    const jointMats = skin.joints.map((j, k) => {
      const ib = new THREE.Matrix4().fromArray(ibm.slice(k * 16, k * 16 + 16));
      return worlds[j].clone().multiply(ib);
    });
    const pos = readAccessor(prim.attributes.POSITION);
    const P = new Float32Array(pos.data);
    // morphs (POSITION deltas at the GLB's weights)
    (prim.targets || []).forEach((t, ti) => {
      const w = weights[ti] || 0;
      if (!w || t.POSITION === undefined) return;
      const d = readAccessor(t.POSITION).data;
      for (let i = 0; i < P.length; i++) P[i] += w * d[i];
    });
    const J = readAccessor(prim.attributes.JOINTS_0).data;
    const W = readAccessor(prim.attributes.WEIGHTS_0);
    const Wn = new Float32Array(W.data);
    if (W.normalized) { const max = W.data instanceof Uint8Array ? 255 : 65535; for (let i = 0; i < Wn.length; i++) Wn[i] = W.data[i] / max; }
    const v = new THREE.Vector3();
    for (let i = 0; i < pos.count; i++) {
      v.set(P[i * 3], P[i * 3 + 1], P[i * 3 + 2]);
      const sx = v.x, sy = v.y, sz = v.z;
      let x = 0, y = 0, z = 0, bestW = -1, bestJ = -1;
      for (let k = 0; k < 4; k++) {
        const wgt = Wn[i * 4 + k]; if (wgt <= 0) continue;
        const jn = J[i * 4 + k];
        if (wgt > bestW) { bestW = wgt; bestJ = skin.joints[jn]; }
        v.set(sx, sy, sz).applyMatrix4(jointMats[jn]);
        x += wgt * v.x; y += wgt * v.y; z += wgt * v.z;
      }
      primPos.push(x, y, z);
      vertJoint.push(bestJ);
    }
    const idx = prim.indices !== undefined ? readAccessor(prim.indices).data : null;
    if (idx) for (let i = 0; i < idx.length; i++) primIdx.push(idx[i] + vOff);
    else for (let i = 0; i < pos.count; i++) primIdx.push(i + vOff);
    vOff += pos.count;
  });
});
if (!primsUsed) throw new Error('no collision prims matched the filter');
console.log(`collision surface: ${primsUsed} prims, ${vOff} verts, ${primIdx.length / 3} tris`);

/* ---------------- BVH + signed distance ---------------- */
const geo = new THREE.BufferGeometry();
geo.setAttribute('position', new THREE.Float32BufferAttribute(primPos, 3));
geo.setIndex(primIdx);
// indirect: true is LOAD-BEARING — the default MeshBVH build
// rewrites the geometry index, invalidating faceIndex lookups
// against primIdx (see header note; measured 59% sign garbage).
const bvh = new MeshBVH(geo, { indirect: true });
const q = new THREE.Vector3();
const target = { point: new THREE.Vector3() };
function unsignedDist(x, y, z) {
  q.set(x, y, z);
  bvh.closestPointToPoint(q, target);
  return target.distance;
}

/* Sign oracle — ray parity, majority of 3 skew rays (skew so a
   ray never runs parallel to the grid or a cardinal body plane;
   hits closer than 0.1 mm are deduped so a ray through a vertex
   or a coincident shell wall counts once). */
const PARITY_DIRS = [
  new THREE.Vector3(1, 0.37, 0.13).normalize(),
  new THREE.Vector3(0.21, 1, 0.43).normalize(),
  new THREE.Vector3(0.53, 0.17, 1).normalize(),
];
const _ray = new THREE.Ray();
function parityInside(x, y, z) {
  let votes = 0;
  for (const d of PARITY_DIRS) {
    _ray.origin.set(x, y, z);
    _ray.direction.copy(d);
    const hits = bvh.raycast(_ray, THREE.DoubleSide);
    const ds = hits.map((h) => h.distance).sort((a, b) => a - b);
    let count = 0, last = -1;
    for (const dist of ds) { if (dist - last > 1e-4) { count++; last = dist; } }
    if (count % 2 === 1) votes++;
  }
  return votes >= 2;
}
function signedDist(x, y, z) {
  return (parityInside(x, y, z) ? -1 : 1) * unsignedDist(x, y, z);
}

/* Sign validation (informational + ground truth below):
   LOCAL COHERENCE vs the sampled triangle's own normal — for a
   union of shells this expectation is only valid away from
   shell-contact zones (a point just inside a lip triangle can be
   inside the mouth cavity, i.e. OUTSIDE the union, and parity is
   right there). The rate is printed for the bake record; the
   HARD gates are the ground-truth checks on the baked grid and
   the row-sweep/oracle agreement check after the grid is built. */
const tri = new THREE.Triangle();
let seed = 1234567;
const rnd = () => (seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
let cohChecked = 0, cohMismatch = 0;
for (let t = 0; t < 2000; t++) {
  const ti = Math.floor(rnd() * (primIdx.length / 3)) * 3;
  const ia = primIdx[ti], ib = primIdx[ti + 1], ic = primIdx[ti + 2];
  tri.a.set(primPos[ia * 3], primPos[ia * 3 + 1], primPos[ia * 3 + 2]);
  tri.b.set(primPos[ib * 3], primPos[ib * 3 + 1], primPos[ib * 3 + 2]);
  tri.c.set(primPos[ic * 3], primPos[ic * 3 + 1], primPos[ic * 3 + 2]);
  const n = new THREE.Vector3(); tri.getNormal(n);
  if (n.lengthSq() < 0.5) continue;
  const cx = (tri.a.x + tri.b.x + tri.c.x) / 3, cy = (tri.a.y + tri.b.y + tri.c.y) / 3, cz = (tri.a.z + tri.b.z + tri.c.z) / 3;
  const eps = 0.006;
  const dOut = signedDist(cx + n.x * eps, cy + n.y * eps, cz + n.z * eps);
  const dIn = signedDist(cx - n.x * eps, cy - n.y * eps, cz - n.z * eps);
  cohChecked++;
  if (!(dOut > 0 && dIn < 0)) cohMismatch++;
}
console.log(`sign report (local coherence vs parity, informational): ${cohMismatch}/${cohChecked} disagree (shell-contact zones expected)`);

/* ---------------- bake the grid ---------------- */
const dims = [
  Math.round((region[3] - region[0]) / voxel) + 1,
  Math.round((region[4] - region[1]) / voxel) + 1,
  Math.round((region[5] - region[2]) / voxel) + 1,
];
const origin = [region[0], region[1], region[2]];
const total = dims[0] * dims[1] * dims[2];
const grid = new Int16Array(total);
const t0 = Date.now();
/* Row-sweep signs: one near-+X ray per (y,z) row of cell centres;
   a cell is inside iff an odd number of surface crossings lie
   before its centre. Exact for the union; ~11k rays instead of
   3 per cell. The slight skew keeps the ray off cardinal planes;
   drift across the widest row stays sub-voxel. */
const sweepDir = new THREE.Vector3(1, 0.003, 0.002).normalize();
const rowSign = new Int8Array(total);
for (let iz = 0; iz < dims[2]; iz++) {
  for (let iy = 0; iy < dims[1]; iy++) {
    const cy = origin[1] + iy * voxel, cz = origin[2] + iz * voxel;
    _ray.origin.set(origin[0] - 0.05, cy, cz);
    _ray.direction.copy(sweepDir);
    const hits = bvh.raycast(_ray, THREE.DoubleSide);
    const xs = hits.map((h) => h.point.x).sort((a, b) => a - b);
    const crossings = [];
    let last = -Infinity;
    for (const hx of xs) { if (hx - last > 1e-4) { crossings.push(hx); last = hx; } }
    let ci = 0;
    for (let ix = 0; ix < dims[0]; ix++) {
      const cx = origin[0] + ix * voxel;
      while (ci < crossings.length && crossings[ci] < cx) ci++;
      rowSign[ix + dims[0] * (iy + dims[1] * iz)] = (ci % 2 === 1) ? -1 : 1;
    }
  }
}
let gi = 0;
for (let iz = 0; iz < dims[2]; iz++) {
  for (let iy = 0; iy < dims[1]; iy++) {
    for (let ix = 0; ix < dims[0]; ix++) {
      const u = unsignedDist(origin[0] + ix * voxel, origin[1] + iy * voxel, origin[2] + iz * voxel);
      const d = rowSign[gi] * u;
      grid[gi++] = Math.max(-32768, Math.min(32767, Math.round(d / QUANT)));
    }
  }
}
console.log(`grid ${dims.join('x')} = ${total} cells baked in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
/* Agreement gate: row-sweep sign vs the 3-ray oracle on random
   cell centres. Below 99% the sweep is not trusted for this
   surface and the bake refuses (rerun path: per-cell oracle). */
{
  let agree = 0, checked = 0;
  for (let t = 0; t < 2000; t++) {
    const ix = Math.floor(rnd() * dims[0]), iy = Math.floor(rnd() * dims[1]), iz = Math.floor(rnd() * dims[2]);
    const cx = origin[0] + ix * voxel, cy = origin[1] + iy * voxel, cz = origin[2] + iz * voxel;
    const cellSign = grid[ix + dims[0] * (iy + dims[1] * iz)] < 0 ? -1 : 1;
    const oracleSign = parityInside(cx, cy, cz) ? -1 : 1;
    checked++;
    if (cellSign === oracleSign) agree++;
  }
  console.log(`row-sweep vs oracle agreement: ${agree}/${checked}`);
  if (agree / checked < 0.99) throw new Error('row-sweep sign disagrees with the 3-ray oracle on >1% of cells — refusing to ship');
}

/* ---------------- ground truth on the baked grid ---------------- */
const jointPos = (nodeIdx) => {
  const e = worlds[nodeIdx].elements;
  return [e[12], e[13], e[14]];
};
const jointByName = (n) => gltf.nodes.findIndex((nd) => nd.name === n);
{
  const { BodySDF } = await import(pathToFileURL(resolve(toolDir, '../../game/js/collision.js')).href);
  const field = new BodySDF({ origin, voxel, dims, quant: QUANT }, grid);
  const mid = (a, b) => [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2];
  const jp = (n) => jointPos(jointByName(n));
  const insidePts = [
    ['torso axis', mid(jp('Spine2'), jp('Neck'))],
    ['head centre', jp('Head')],
    ['left upper arm', mid(jp('LeftArm'), jp('LeftForeArm'))],
    ['right upper arm', mid(jp('RightArm'), jp('RightForeArm'))],
  ];
  const hp = jp('Head'), sp = jp('Spine2');
  const outsidePts = [
    ['lateral of head', [hp[0] + 0.3, hp[1], hp[2]]],
    ['in front of chest', [sp[0], sp[1], sp[2] + 0.3]],
    ['above head', [hp[0], hp[1] + 0.25, hp[2]]],
  ];
  for (const [label, p] of insidePts) {
    const d = field.sample(p[0], p[1], p[2]);
    if (!(d < -0.005)) throw new Error(`ground truth FAIL: ${label} should be inside, field=${d.toFixed(4)}`);
    console.log(`ground truth inside  ${label}: ${d.toFixed(4)}`);
  }
  for (const [label, p] of outsidePts) {
    const d = field.sample(p[0], p[1], p[2]);
    if (!(d > 0.05)) throw new Error(`ground truth FAIL: ${label} should be outside, field=${d.toFixed(4)}`);
    console.log(`ground truth outside ${label}: ${d.toFixed(4)}`);
  }
  /* Zero-level fidelity: random points ON the collision surface
     must read ~0 in the baked grid — this is the gate that proves
     the field's surface is the character's surface (the runtime
     rests hair on exactly this level set). */
  let zlMax = 0, zlSum = 0, zlN = 0;
  for (let t = 0; t < 2000; t++) {
    const ti = Math.floor(rnd() * (primIdx.length / 3)) * 3;
    const ia = primIdx[ti], ib = primIdx[ti + 1], ic = primIdx[ti + 2];
    let r1 = rnd(), r2 = rnd();
    if (r1 + r2 > 1) { r1 = 1 - r1; r2 = 1 - r2; }
    const px = primPos[ia * 3] + r1 * (primPos[ib * 3] - primPos[ia * 3]) + r2 * (primPos[ic * 3] - primPos[ia * 3]);
    const py = primPos[ia * 3 + 1] + r1 * (primPos[ib * 3 + 1] - primPos[ia * 3 + 1]) + r2 * (primPos[ic * 3 + 1] - primPos[ia * 3 + 1]);
    const pz = primPos[ia * 3 + 2] + r1 * (primPos[ib * 3 + 2] - primPos[ia * 3 + 2]) + r2 * (primPos[ic * 3 + 2] - primPos[ia * 3 + 2]);
    if (px < origin[0] || px > field.maxX || py < origin[1] || py > field.maxY || pz < origin[2] || pz > field.maxZ) continue;
    const d = Math.abs(field.sample(px, py, pz));
    zlMax = Math.max(zlMax, d); zlSum += d; zlN++;
  }
  console.log(`zero-level fidelity: n=${zlN} mean=${(zlSum / Math.max(zlN, 1)).toFixed(4)} max=${zlMax.toFixed(4)} (voxel ${voxel})`);
  if (zlMax > 1.25 * voxel) throw new Error('zero-level fidelity FAIL — baked surface drifts from the collision surface');
}

/* ---------------- fit the collider set ----------------
   Assignment is by SEGMENT PROXIMITY, not dominant joint: rigs
   differ in which bones dominate the skin (this Daz/GZM rig
   deforms through *.twk tweak bones — a dominant-joint fit keyed
   to FK bone names silently measured empty groups and fell back
   to default radii, caught 2026-11-09). Every surface vertex is
   assigned to the collider anchor (segment or sphere centre)
   closest to it in the bind pose; each radius is a measured
   percentile of its assigned vertices' distances. The endpoint
   bones are the rig's animation bones — the anchors the runtime
   poses — so the fit is rig-naming-agnostic. */
const CAPSULE_DEFS = [
  ['Neck', 'Head'], ['Spine2', 'Neck'],
  ['LeftShoulder', 'LeftArm'], ['RightShoulder', 'RightArm'],
  ['LeftArm', 'LeftForeArm'], ['RightArm', 'RightForeArm'],
];
const HEAD_SPHERE_WORLD_OFFSET = [0, 0.055, 0.004];
function segDist(px, py, pz, a, b) {
  const abx = b[0] - a[0], aby = b[1] - a[1], abz = b[2] - a[2];
  const len2 = abx * abx + aby * aby + abz * abz;
  let t = len2 > 0 ? ((px - a[0]) * abx + (py - a[1]) * aby + (pz - a[2]) * abz) / len2 : 0;
  t = Math.max(0, Math.min(1, t));
  const dx = px - (a[0] + abx * t), dy = py - (a[1] + aby * t), dz = pz - (a[2] + abz * t);
  return Math.sqrt(dx * dx + dy * dy + dz * dz);
}
const _anchors = CAPSULE_DEFS.map(([na, nb]) => ({ kind: 'capsule', boneA: na, boneB: nb, a: jointPos(jointByName(na)), b: jointPos(jointByName(nb)), ds: [] }));
{
  const headC = jointPos(jointByName('Head'));
  const centre = [headC[0] + HEAD_SPHERE_WORLD_OFFSET[0], headC[1] + HEAD_SPHERE_WORLD_OFFSET[1], headC[2] + HEAD_SPHERE_WORLD_OFFSET[2]];
  _anchors.push({ kind: 'sphere', bone: 'Head', centre, ds: [] });
  /* LOCALITY (measured fix, 2026-11-09): assignment must be local.
     The anchor set covers the head / neck / shoulders / arms, but the
     collision surface includes the whole body (legs, feet). Unbounded
     closest-anchor assignment handed every lower-body vertex to the
     Spine2->Neck segment — a foot vertex sits ~1.1 m from that axis —
     and the p92 radius came out 1.173 m: a "torso capsule" that
     projects every hair tip a metre off the body at runtime. A vertex
     farther than FIT_LOCALITY from its closest anchor belongs to a
     body region these colliders do not represent (the SDF region is
     the upper body) and is left unassigned. */
  const FIT_LOCALITY = 0.35;
  let unassigned = 0;
  for (let i = 0; i < vOff; i++) {
    const px = primPos[i * 3], py = primPos[i * 3 + 1], pz = primPos[i * 3 + 2];
    let best = null, bestD = Infinity;
    for (const an of _anchors) {
      const d = an.kind === 'capsule'
        ? segDist(px, py, pz, an.a, an.b)
        : Math.hypot(px - an.centre[0], py - an.centre[1], pz - an.centre[2]);
      if (d < bestD) { bestD = d; best = an; }
    }
    if (bestD > FIT_LOCALITY) { unassigned++; continue; }
    best.ds.push(bestD);
  }
  console.log(`collider fit locality: ${unassigned} far verts left unassigned (bound ${FIT_LOCALITY} m)`);
}
const _pct = (ds, p, fallback) => {
  if (!ds.length) return fallback;
  const s = [...ds].sort((m, n) => m - n);
  return s[Math.min(s.length - 1, Math.floor(s.length * p))];
};
const capsules = _anchors.filter((a) => a.kind === 'capsule').map((a) => ({
  boneA: a.boneA, boneB: a.boneB,
  radius: +_pct(a.ds, 0.92, 0.03).toFixed(4), verts: a.ds.length,
  margin: 0.006, friction: 0.35,
}));
const spheres = _anchors.filter((a) => a.kind === 'sphere').map((a) => {
  /* the runtime applies `offset` in BONE-LOCAL space (rotated by
     the bone's world quaternion); store the bind-world offset
     converted into the Head bone's local frame so bake and
     runtime agree in every pose */
  const hq = new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().extractRotation(worlds[jointByName('Head')]));
  const local = new THREE.Vector3(...HEAD_SPHERE_WORLD_OFFSET).applyQuaternion(hq.clone().invert());
  return {
    bone: a.bone, offset: [+local.x.toFixed(4), +local.y.toFixed(4), +local.z.toFixed(4)],
    radius: +_pct(a.ds, 0.97, 0.1).toFixed(4), verts: a.ds.length,
    margin: 0.004, friction: 0.3,
  };
});
for (const c of [...capsules, ...spheres]) {
  if (!c.verts) throw new Error(`collider fit FAIL: ${c.boneA || c.bone} got no assigned vertices`);
  /* a fitted radius beyond the locality bound is by construction a
     fit failure (see the locality note above) — refuse to ship it */
  if (c.radius > 0.35) throw new Error(`collider fit FAIL: ${c.boneA ? `${c.boneA}->${c.boneB}` : c.bone} radius ${c.radius} m exceeds the 0.35 m locality bound`);
  console.log(`collider fit ${c.boneA ? `${c.boneA}->${c.boneB}` : c.bone}: r=${c.radius} from ${c.verts} verts`);
}
const capsulesOut = capsules.map(({ verts, ...c }) => c);
const spheresOut = spheres.map(({ verts, ...s }) => s);

/* ---------------- write outputs ---------------- */
mkdirSync(outDir, { recursive: true });
const sdfHeader = { origin, voxel, dims, quant: QUANT, frame: 'bind-world', bakedFrom: glbPath.split('/').pop() };
writeFileSync(resolve(outDir, `${name}-body.sdf.json`), JSON.stringify(sdfHeader, null, 1));
const bin = Buffer.alloc(grid.length * 2);
grid.forEach((v, i) => bin.writeInt16LE(v, i * 2));
writeFileSync(resolve(outDir, `${name}-body.sdf.bin`), bin);
const collisionJson = {
  character: name,
  format: 'wh-collision/v1',
  capsules: capsulesOut, spheres: spheresOut,
  sdf: { file: `${name}-body.sdf.bin`, header: `${name}-body.sdf.json`, frameBone, margin: 0.004, friction: 0.35 },
  notes: 'Colliders fitted from the skinned bind pose (see tools/collision/bake-collision.mjs). Radii are measured percentiles of skin vertices assigned by segment proximity; margins add the hair clump radius at runtime.',
};
writeFileSync(resolve(outDir, `${name}-collision.json`), JSON.stringify(collisionJson, null, 1));
console.log(JSON.stringify({
  out: outDir, sdfBytes: bin.length, dims,
  coherenceDisagree: `${cohMismatch}/${cohChecked}`,
  capsules: capsulesOut.map((c) => `${c.boneA}->${c.boneB} r=${c.radius}`),
  spheres: spheresOut.map((s) => `${s.bone} r=${s.radius}`),
}, null, 1));
