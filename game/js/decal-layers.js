/* ============================================================
   WESTERN HEART — body decal LAYERS (tattoos + scars)
   (creation suite TATTOOS + SCARS phase, 2026-11-02)

   STRUCTURE SOURCE (not invented):
   - WWE 2K Create-A-Superstar Tattoos / Logos: "layered, placeable,
     scalable, rotatable — full body canvas"
     (customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md §2.2), decal layers
     with position / scale / rotation / opacity (COMBINED-CREATION-SUITE.md
     §3.5), per-layer colour (Parts Color), "40 body/head layers"
     (menu-data.js MENU_SRC.WWE_ATTIRE), scars movable on the face
     (MENU_SRC.WWE_FACEBODY). Decals apply after attire layering
     (CAW-STRUCTURE-2026-10-19.md §4 step 4).
   - Tekken: the list stays the Tekken category list (Face Paint = slot 8,
     CharacterItemTex, teardown/tekken7/facepaint-reference.json).

   HOW A LAYER LANDS ON A BODY (UV-space projection, per region):
   Each body REGION has its own UV canvas built from the template's
   skeleton: v runs ALONG the region's bone axis (0 = start joint,
   1 = end joint), u runs AROUND it (0 = front of the body, +Z; 0.5 =
   back). A layer stores { region, u, v, scaleX, scaleY, rotation,
   opacity, color, mirror }. resolveAnchor() casts a ray out of the bone
   axis at (u,v) against the skin triangles weighted to that region's
   bones; projectDecal() then clips the skin around the hit into a decal
   patch (the DecalGeometry method: oriented box, Sutherland–Hodgman
   clip) and keeps, for every patch vertex, its source triangle + the
   barycentric weights — so the THREE bridge can carry skin weights AND
   the template's morph targets onto the decal (it deforms with the body
   sliders and the fight animation instead of floating).

   Pure logic (no THREE import at module top level) so Node tests can
   import it — same pattern as game/js/wear-off.js. THREE is passed in
   to buildDecalMesh().
   ============================================================ */

/* ---- body regions (MB-Lab template skeleton bone names) ----
   axis: [startBone, endBone] or [bone, null, extendMetres] (head: no end bone).
   bones: the skin-weight bones whose triangles the region may land on.
   zone: wear-off zone (game/js/wear-off.js) — face | upper | lower. */
export const BODY_REGIONS = Object.freeze([
  { key: 'chest',       label: 'Chest',            axis: ['spine01', 'neck'],          bones: ['spine02', 'spine03', 'breast_L', 'breast_R', 'clavicle_L', 'clavicle_R', 'spine01'], zone: 'upper', size: 0.20 },
  { key: 'back',        label: 'Back',             axis: ['spine01', 'neck'],          bones: ['spine02', 'spine03', 'clavicle_L', 'clavicle_R', 'spine01'], zone: 'upper', size: 0.26 },
  { key: 'neck',        label: 'Neck',             axis: ['neck', 'head'],             bones: ['neck'], zone: 'upper', size: 0.07 },
  { key: 'face',        label: 'Face',             axis: ['head', null, 0.22],         bones: ['head'], zone: 'face', size: 0.06 },
  { key: 'upper_arm_L', label: 'Upper Arm L',      axis: ['upperarm_L', 'lowerarm_L'], bones: ['upperarm_L', 'upperarm_twist_L'], zone: 'upper', size: 0.09 },
  { key: 'upper_arm_R', label: 'Upper Arm R',      axis: ['upperarm_R', 'lowerarm_R'], bones: ['upperarm_R', 'upperarm_twist_R'], zone: 'upper', size: 0.09 },
  { key: 'forearm_L',   label: 'Forearm L',        axis: ['lowerarm_L', 'hand_L'],     bones: ['lowerarm_L', 'lowerarm_twist_L'], zone: 'upper', size: 0.08 },
  { key: 'forearm_R',   label: 'Forearm R',        axis: ['lowerarm_R', 'hand_R'],     bones: ['lowerarm_R', 'lowerarm_twist_R'], zone: 'upper', size: 0.08 },
  { key: 'thigh_L',     label: 'Thigh L',          axis: ['thigh_L', 'calf_L'],        bones: ['thigh_L', 'thigh_twist_L'], zone: 'lower', size: 0.13 },
  { key: 'thigh_R',     label: 'Thigh R',          axis: ['thigh_R', 'calf_R'],        bones: ['thigh_R', 'thigh_twist_R'], zone: 'lower', size: 0.13 },
  { key: 'calf_L',      label: 'Calf L',           axis: ['calf_L', 'foot_L'],         bones: ['calf_L', 'calf_twist_L'], zone: 'lower', size: 0.10 },
  { key: 'calf_R',      label: 'Calf R',           axis: ['calf_R', 'foot_R'],         bones: ['calf_R', 'calf_twist_R'], zone: 'lower', size: 0.10 },
]);
export const REGION_BY_KEY = Object.freeze(Object.fromEntries(BODY_REGIONS.map((r) => [r.key, r])));
/* WWE 2K22 "40 body/head layers" (MENU_SRC.WWE_ATTIRE). */
export const MAX_LAYERS = 40;
export const LAYER_KINDS = Object.freeze(['tattoo', 'scar']);

import { createLayer as createWearLayer, applyHit, setMaterialOpacity } from './wear-off.js';

const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const num = (v, d) => (typeof v === 'number' && Number.isFinite(v) ? v : d);
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const mul = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const len = (a) => Math.hypot(a[0], a[1], a[2]);
const norm = (a) => { const l = len(a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };

/* ---------------- layer model (saved per attire) ---------------- */
let _seq = 0;
export function createLayer(opts = {}) {
  const region = REGION_BY_KEY[opts.region] ? opts.region : 'chest';
  const kind = LAYER_KINDS.includes(opts.kind) ? opts.kind : 'tattoo';
  if (!opts.part_id) throw new Error('decal-layers: layer needs a part_id');
  return normalizeLayer({
    id: opts.id || `L${Date.now().toString(36)}${(_seq++).toString(36)}`,
    part_id: opts.part_id, kind, region,
    u: opts.u, v: opts.v, scaleX: opts.scaleX, scaleY: opts.scaleY,
    rotation: opts.rotation, opacity: opts.opacity, color: opts.color, mirror: opts.mirror, asset: opts.asset,
  });
}
export function normalizeLayer(l) {
  if (!l || typeof l !== 'object' || !l.part_id) return null;
  const region = REGION_BY_KEY[l.region] ? l.region : 'chest';
  return {
    id: String(l.id || ''), part_id: String(l.part_id),
    kind: LAYER_KINDS.includes(l.kind) ? l.kind : 'tattoo', region,
    u: ((num(l.u, 0) % 1) + 1) % 1,
    v: clamp(num(l.v, 0.5), 0, 1),
    scaleX: clamp(num(l.scaleX, 1), 0.1, 4),
    scaleY: clamp(num(l.scaleY, 1), 0.1, 4),
    rotation: clamp(num(l.rotation, 0), -180, 180),
    opacity: clamp(num(l.opacity, 1), 0, 1),
    color: /^#[0-9a-f]{6}$/i.test(l.color || '') ? l.color.toLowerCase() : '#ffffff',
    mirror: !!l.mirror,
    // repo-relative texture path, carried so the fight needs no 5 MB parts catalog to draw the layer
    ...(typeof l.asset === 'string' && /^[\w\-./]+\.png$/i.test(l.asset) && !l.asset.includes('..') && !l.asset.startsWith('/') ? { asset: l.asset } : {}),
  };
}
/** Sanitize a saved layer stack (drops junk, caps at MAX_LAYERS, keeps order = draw order bottom->top). */
export function normalizeLayers(list) {
  return (Array.isArray(list) ? list : []).map(normalizeLayer).filter(Boolean).slice(0, MAX_LAYERS);
}
export function addLayer(list, layer) {
  if (list.length >= MAX_LAYERS) return false;
  list.push(layer); return true;
}
export function removeLayer(list, id) {
  const i = list.findIndex((l) => l.id === id); if (i < 0) return false;
  list.splice(i, 1); return true;
}
/** Move a layer up (+1, drawn later = on top) or down (-1). */
export function moveLayer(list, id, dir) {
  const i = list.findIndex((l) => l.id === id); const j = i + (dir > 0 ? 1 : -1);
  if (i < 0 || j < 0 || j >= list.length) return false;
  [list[i], list[j]] = [list[j], list[i]]; return true;
}
/** WWE "Mirror": copy a layer onto the opposite-side region (L <-> R), mirrored. */
export function mirrorLayer(layer) {
  const flip = { _L: '_R', _R: '_L' };
  const m = /_(L|R)$/.exec(layer.region);
  const region = m ? layer.region.replace(/_(L|R)$/, flip['_' + m[1]]) : layer.region;
  return normalizeLayer({ ...layer, id: layer.id + 'm', region, u: (1 - layer.u) % 1, rotation: -layer.rotation, mirror: !layer.mirror });
}

/** Default placement for (template, region) from the authored table
 *  (customization/templates/decal-placements.json), else a region default. */
export function defaultPlacement(table, templateId, region) {
  const t = table && table.templates && table.templates[templateId];
  const r = t && t.regions && t.regions[region];
  if (r) return { region, u: r.u, v: r.v, scaleX: 1, scaleY: 1, rotation: 0, size: r.size_m };
  const R = REGION_BY_KEY[region] || REGION_BY_KEY.chest;
  return { region: R.key, u: R.key === 'back' ? 0.5 : 0, v: 0.5, scaleX: 1, scaleY: 1, rotation: 0, size: R.size };
}

/* ---------------- geometry: region frame + anchor ---------------- */
/* mesh = { positions: Float32Array(n*3), indices, joints (n*4), weights (n*4),
            jointNames: string[], bones: { name: [x,y,z] } }  (bind pose) */
export function regionFrame(mesh, regionKey) {
  const R = REGION_BY_KEY[regionKey]; if (!R) throw new Error(`decal-layers: unknown region ${regionKey}`);
  const a = mesh.bones[R.axis[0]];
  if (!a) throw new Error(`decal-layers: template has no bone ${R.axis[0]}`);
  let b;
  if (R.axis[1]) b = mesh.bones[R.axis[1]];
  else { const n = mesh.bones.neck || [a[0], a[1] - 0.1, a[2]]; b = add(a, mul(norm(sub(a, n)), R.axis[2])); }
  const axis = norm(sub(b, a));
  // front = +Z with the axis component removed (u = 0 faces the camera at the select screen)
  let front = sub([0, 0, 1], mul(axis, axis[2]));
  if (len(front) < 1e-4) front = [0, 1, 0];
  front = norm(front);
  const side = cross(axis, front);
  return { start: a, end: b, axis, front, side, length: len(sub(b, a)) };
}

function dominantBone(mesh, vi) {
  let best = -1, bw = -1;
  for (let k = 0; k < 4; k++) { const w = mesh.weights[vi * 4 + k]; if (w > bw) { bw = w; best = mesh.joints[vi * 4 + k]; } }
  return mesh.jointNames[best];
}
const _regionTris = new WeakMap();
/** Triangle indices (into mesh.indices/3) whose vertices are majority-weighted to the region's bones. */
export function regionTriangles(mesh, regionKey) {
  let cache = _regionTris.get(mesh); if (!cache) { cache = {}; _regionTris.set(mesh, cache); }
  if (cache[regionKey]) return cache[regionKey];
  const set = new Set(REGION_BY_KEY[regionKey].bones);
  const out = [];
  const I = mesh.indices;
  for (let t = 0; t < I.length / 3; t++) {
    let c = 0;
    for (let k = 0; k < 3; k++) if (set.has(dominantBone(mesh, I[t * 3 + k]))) c++;
    if (c >= 2) out.push(t);
  }
  cache[regionKey] = out;
  return out;
}
function vtx(mesh, i) { const p = mesh.positions; return [p[i * 3], p[i * 3 + 1], p[i * 3 + 2]]; }
function rayTri(o, d, a, b, c) { // Möller–Trumbore, both faces
  const e1 = sub(b, a), e2 = sub(c, a), p = cross(d, e2), det = dot(e1, p);
  if (Math.abs(det) < 1e-12) return null;
  const E = 1e-6, inv = 1 / det, s = sub(o, a), u = dot(s, p) * inv; if (u < -E || u > 1 + E) return null;
  const q = cross(s, e1), v = dot(d, q) * inv; if (v < -E || u + v > 1 + E) return null;
  const t = dot(e2, q) * inv; return t > 1e-6 ? { t, u, v } : null;
}

/**
 * Where (u,v) of a region lands on the skin.
 * Returns { point, normal, dir, up, tri, bone } or null when the ray misses
 * the region's skin (the caller reports it; it never throws into a fight).
 */
export function resolveAnchor(mesh, regionKey, u, v, opts = {}) {
  const f = regionFrame(mesh, regionKey);
  const ang = 2 * Math.PI * u;
  const dir = norm(add(mul(f.front, Math.cos(ang)), mul(f.side, Math.sin(ang))));
  const origin = add(f.start, mul(sub(f.end, f.start), clamp(v, 0, 1)));
  let best = null;
  const tris = opts.anyTriangle ? null : regionTriangles(mesh, regionKey);
  const N = tris ? tris.length : mesh.indices.length / 3;
  for (let k = 0; k < N; k++) {
    const t = tris ? tris[k] : k;
    const I = mesh.indices, a = vtx(mesh, I[t * 3]), b = vtx(mesh, I[t * 3 + 1]), c = vtx(mesh, I[t * 3 + 2]);
    const h = rayTri(origin, dir, a, b, c);
    if (h && (!best || h.t < best.t)) best = { ...h, tri: t, a, b, c };
  }
  if (!best) {
    // the region's own skin was missed (e.g. a slider pushed the point off it):
    // land on whatever skin is there, flagged, rather than dropping the layer
    if (!opts.anyTriangle && opts.fallback !== false) {
      const any = resolveAnchor(mesh, regionKey, u, v, { anyTriangle: true });
      if (any) any.inRegion = false;
      return any;
    }
    return null;
  }
  const point = add(origin, mul(dir, best.t));
  let normal = norm(cross(sub(best.b, best.a), sub(best.c, best.a)));
  // windingSign: +1 when the skin is wound outward (normal agrees with the outward ray)
  const windingSign = dot(normal, dir) < 0 ? -1 : 1;
  if (windingSign < 0) normal = mul(normal, -1);
  const I = mesh.indices;
  const w = [1 - best.u - best.v, best.u, best.v];
  const vi = I[best.tri * 3 + w.indexOf(Math.max(...w))];
  // decal 'up' = the region axis turned to point UP the body (limbs run downward: shoulder->hand, hip->foot),
  // so a design's top edge faces the head on every region
  const up = f.axis[1] < -0.2 ? mul(f.axis, -1) : f.axis;
  return { point, normal, dir, up, tri: best.tri, bone: dominantBone(mesh, vi), distance: best.t, origin, windingSign, inRegion: !opts.anyTriangle };
}

/* ---------------- decal patch (DecalGeometry method) ---------------- */
/**
 * Clip the skin around an anchor into a decal patch.
 * opts: { width, height, depth, rotation (deg), mirror, offset (m) }
 * Returns { positions: number[], uvs: number[], src: [{ tri, b:[b0,b1,b2] }] }
 * — three vertices per triangle (non-indexed), src per vertex.
 */
export function projectDecal(mesh, anchor, opts = {}) {
  const width = num(opts.width, 0.1), height = num(opts.height, 0.1), depth = num(opts.depth, Math.max(width, height) * 0.6);
  const offset = num(opts.offset, 0.0006);
  const z = anchor.dir; // projector looks along -z (into the body)
  let y = sub(anchor.up, mul(z, dot(anchor.up, z)));
  if (len(y) < 1e-6) y = [0, 1, 0];
  y = norm(y);
  let x = cross(y, z);
  const r = (num(opts.rotation, 0) * Math.PI) / 180;
  const xr = add(mul(x, Math.cos(r)), mul(y, Math.sin(r)));
  const yr = add(mul(y, Math.cos(r)), mul(x, -Math.sin(r)));
  x = xr; y = yr;
  const P = anchor.point;
  const toLocal = (p) => { const d = sub(p, P); return [dot(d, x), dot(d, y), dot(d, z)]; };
  const half = [width / 2, height / 2, depth / 2];
  const out = { positions: [], uvs: [], src: [] };
  const I = mesh.indices;
  const lim = Math.hypot(half[0], half[1], half[2]);
  for (let t = 0; t < I.length / 3; t++) {
    const ids = [I[t * 3], I[t * 3 + 1], I[t * 3 + 2]];
    const ws = ids.map((i) => vtx(mesh, i));
    const ls = ws.map(toLocal);
    if (ls.every((l) => Math.hypot(l[0], l[1], l[2]) > lim * 2.5)) continue; // far away
    // facing: keep only triangles that face the projector (outward-wound skin;
    // the far side of a limb or the torso is never painted through)
    const n = norm(cross(sub(ws[1], ws[0]), sub(ws[2], ws[0])));
    if (dot(n, z) * (anchor.windingSign || 1) < 0.05) continue;
    let poly = ls.map((l, k) => ({ p: l, b: [k === 0 ? 1 : 0, k === 1 ? 1 : 0, k === 2 ? 1 : 0] }));
    for (let ax = 0; ax < 3 && poly.length; ax++) {
      poly = clipPoly(poly, ax, half[ax], 1);
      poly = clipPoly(poly, ax, half[ax], -1);
    }
    if (poly.length < 3) continue;
    for (let k = 1; k < poly.length - 1; k++) {
      for (const q of [poly[0], poly[k], poly[k + 1]]) {
        const w = add(P, add(add(mul(x, q.p[0]), mul(y, q.p[1])), mul(z, q.p[2] + offset)));
        out.positions.push(w[0], w[1], w[2]);
        let uu = q.p[0] / width + 0.5; const vv = q.p[1] / height + 0.5;
        if (opts.mirror) uu = 1 - uu;
        out.uvs.push(uu, vv);
        out.src.push({ tri: t, b: q.b.slice() });
      }
    }
  }
  return out;
}
function clipPoly(poly, ax, h, sign) {
  const out = [];
  const inside = (v) => sign * v.p[ax] <= h;
  for (let i = 0; i < poly.length; i++) {
    const a = poly[i], b = poly[(i + 1) % poly.length];
    const ia = inside(a), ib = inside(b);
    if (ia) out.push(a);
    if (ia !== ib) {
      const t = (sign * h - a.p[ax]) / (b.p[ax] - a.p[ax]);
      out.push({ p: [0, 1, 2].map((k) => a.p[k] + (b.p[k] - a.p[k]) * t), b: [0, 1, 2].map((k) => a.b[k] + (b.b[k] - a.b[k]) * t) });
    }
  }
  return out;
}

/** Decal box size in metres for a layer on a region (texture aspect = w/h). */
export function layerSize(layer, region, aspect = 1, sizeOverride) {
  const base = num(sizeOverride, (REGION_BY_KEY[region] || REGION_BY_KEY.chest).size);
  const a = aspect > 0 ? aspect : 1;
  const w = a >= 1 ? base : base * a, h = a >= 1 ? base / a : base;
  return { width: w * layer.scaleX, height: h * layer.scaleY };
}

/* ---------------- THREE bridge ---------------- */
/** Bind-pose mesh data from a three.js SkinnedMesh (same shape as the Node reader). */
export function meshDataFromSkinned(skinned) {
  const g = skinned.geometry;
  const pos = g.attributes.position, si = g.attributes.skinIndex, sw = g.attributes.skinWeight;
  const n = pos.count;
  const positions = new Float32Array(n * 3), joints = new Float32Array(n * 4), weights = new Float32Array(n * 4);
  for (let i = 0; i < n; i++) {
    positions[i * 3] = pos.getX(i); positions[i * 3 + 1] = pos.getY(i); positions[i * 3 + 2] = pos.getZ(i);
    for (let k = 0; k < 4; k++) { joints[i * 4 + k] = si.getComponent(i, k); weights[i * 4 + k] = sw.getComponent(i, k); }
  }
  const index = g.index ? Uint32Array.from(g.index.array) : Uint32Array.from({ length: n }, (_, i) => i);
  const skel = skinned.skeleton;
  const jointNames = skel.bones.map((b) => b.name);
  // bind position of each bone in the mesh's geometry space: inverse(boneInverse) origin, back through bindMatrix
  const bones = {};
  skel.bones.forEach((b, k) => {
    const inv = skel.boneInverses[k].clone().invert();
    const v = { x: inv.elements[12], y: inv.elements[13], z: inv.elements[14] };
    const m = skinned.bindMatrixInverse.elements; // world(bind) -> mesh space
    bones[b.name] = [m[0] * v.x + m[4] * v.y + m[8] * v.z + m[12], m[1] * v.x + m[5] * v.y + m[9] * v.z + m[13], m[2] * v.x + m[6] * v.y + m[10] * v.z + m[14]];
  });
  return { positions, indices: index, joints, weights, jointNames, bones };
}

/**
 * Build a skinned decal mesh for one layer ON a body SkinnedMesh.
 * The patch interpolates the body's skin weights (dominant source vertex)
 * and morph targets (barycentric), shares the body's skeleton, and is
 * added as the body's sibling. Returns the mesh, or null when the anchor
 * misses (caller logs; never throws into a fight).
 */
export function buildDecalMesh(THREE, skinned, layer, texture, opts = {}) {
  const data = opts.meshData || meshDataFromSkinned(skinned);
  const anchor = resolveAnchor(data, layer.region, layer.u, layer.v);
  if (!anchor) return null;
  const img = texture && texture.image;
  const aspect = img && img.width && img.height ? img.width / img.height : 1;
  const size = layerSize(layer, layer.region, aspect, opts.size);
  const patch = projectDecal(data, anchor, { ...size, rotation: layer.rotation, mirror: layer.mirror });
  if (!patch.positions.length) return null;
  const g = new THREE.BufferGeometry();
  const n = patch.src.length;
  g.setAttribute('position', new THREE.Float32BufferAttribute(patch.positions, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(patch.uvs, 2));
  const sg = skinned.geometry, I = data.indices;
  const si = new Uint16Array(n * 4), sw = new Float32Array(n * 4);
  patch.src.forEach((s, k) => {
    const m = s.b.indexOf(Math.max(...s.b));
    const vi = I[s.tri * 3 + m];
    for (let c = 0; c < 4; c++) { si[k * 4 + c] = data.joints[vi * 4 + c]; sw[k * 4 + c] = data.weights[vi * 4 + c]; }
  });
  g.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(si, 4));
  g.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4));
  const morphs = sg.morphAttributes && sg.morphAttributes.position;
  if (morphs && morphs.length) {
    g.morphAttributes.position = morphs.map((ma) => {
      const arr = new Float32Array(n * 3);
      patch.src.forEach((s, k) => {
        for (let c = 0; c < 3; c++) {
          const vi = I[s.tri * 3 + c];
          arr[k * 3] += ma.getX(vi) * s.b[c]; arr[k * 3 + 1] += ma.getY(vi) * s.b[c]; arr[k * 3 + 2] += ma.getZ(vi) * s.b[c];
        }
      });
      return new THREE.Float32BufferAttribute(arr, 3);
    });
    g.morphTargetsRelative = sg.morphTargetsRelative;
  }
  g.computeVertexNormals();
  const mat = new THREE.MeshStandardMaterial({
    map: texture || null, transparent: true, opacity: layer.opacity, color: new THREE.Color(layer.color),
    depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4, roughness: 0.75, metalness: 0,
  });
  if (texture) texture.colorSpace = THREE.SRGBColorSpace;
  const mesh = new THREE.SkinnedMesh(g, mat);
  mesh.name = `wh_decal_${layer.kind}_${layer.id}`;
  mesh.userData.decalLayer = { ...layer };
  mesh.frustumCulled = false;
  mesh.renderOrder = 10 + (opts.order || 0);
  if (skinned.morphTargetInfluences && g.morphAttributes.position) {
    mesh.morphTargetInfluences = skinned.morphTargetInfluences; // shared array: body sliders drive the decal too
    mesh.morphTargetDictionary = skinned.morphTargetDictionary;
  }
  (skinned.parent || skinned).add(mesh);
  mesh.position.copy(skinned.position); mesh.quaternion.copy(skinned.quaternion); mesh.scale.copy(skinned.scale);
  mesh.bind(skinned.skeleton, skinned.bindMatrix);
  return mesh;
}

/** The body SkinnedMesh of a template model (material name has "skin"; else the largest SkinnedMesh). */
export function findBodySkin(root) {
  let best = null, bestN = -1;
  root.traverse((o) => {
    if (!o.isSkinnedMesh) return;
    const mats = Array.isArray(o.material) ? o.material : [o.material];
    const skin = mats.some((m) => m && /skin/i.test(m.name || ''));
    const nv = o.geometry.attributes.position.count + (skin ? 1e9 : 0);
    if (nv > bestN) { bestN = nv; best = o; }
  });
  return best;
}

/* ---------------- in-fight wear-off hook (game/js/wear-off.js) ----------------
   Each built decal registers a wear layer on model.userData.whDecals; a landed hit
   (fighter.js receiveHit) wears the layers in the hit's zone: face paint would vanish,
   tattoos fade to 0.55 of their set opacity, scars to 0.85 (wear-off.js floors). */
export function registerDecalWear(model, mesh, layer) {
  if (!model || !mesh) return null;
  const wear = createWearLayer({ id: layer.id, kind: layer.kind === 'scar' ? 'scar' : 'tattoo', zone: (REGION_BY_KEY[layer.region] || {}).zone || 'any' });
  const entry = { mesh, wear, base: layer.opacity };
  (model.userData.whDecals = model.userData.whDecals || []).push(entry);
  return entry;
}
export function zoneForMove(move) {
  const lv = String((move && (move.level || move.hitLevel || move.height)) || '').toLowerCase();
  return /low/.test(lv) ? 'lower' : /high/.test(lv) ? 'face' : /mid/.test(lv) ? 'upper' : 'any';
}
export function wearBodyDecals(model, move, dmg = 10) {
  const list = model && model.userData && model.userData.whDecals;
  if (!list || !list.length) return 0;
  const zone = zoneForMove(move), strength = clamp(num(dmg, 10) / 20, 0, 2);
  let n = 0;
  for (const e of list) {
    const before = e.wear.opacity;
    applyHit(e.wear, { zone, strength });
    if (e.wear.opacity !== before) { setMaterialOpacity(e.mesh.material, e.base * e.wear.opacity); n++; }
  }
  return n;
}
