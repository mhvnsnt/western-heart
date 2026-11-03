// Creation suite TATTOOS + SCARS phase (2026-11-02): body-region decal layers.
// Numeric probe, Node only (no browser, no WebGL):
//  - every authored default placement (customization/templates/decal-placements.json,
//    authored in Blender by tools/creation-suite/decals/author_placements_blender.py)
//    re-resolves with the GAME's own resolver (game/js/decal-layers.js) on the real
//    template GLB to within 1 mm of Blender's anchor, ON skin weighted to that
//    region's bones, on all 9 template bodies;
//  - the anchor sits in the right part of the body (height band, side, front/back);
//  - the projected decal patch is non-empty, its UVs stay in 0..1 and every patch
//    vertex lies on a skin triangle near the anchor;
//  - layer stacks save/restore per attire (JSON round trip, order, cap, mirror);
//  - the scar set + tattoo wiring in the parts catalog are real files.
// Run: node --test test/decal-layers.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  BODY_REGIONS, REGION_BY_KEY, MAX_LAYERS, resolveAnchor, projectDecal, regionFrame, layerSize,
  createLayer, normalizeLayers, addLayer, removeLayer, moveLayer, mirrorLayer, defaultPlacement,
  buildDecalMesh,
} from '../game/js/decal-layers.js';
import { createLayer as wearLayer, applyHit, WEAR_FLOORS } from '../game/js/wear-off.js';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
// CI's unit-test job may be a sparse checkout: read files from git when not on disk.
const bytes = (rel) => existsSync(join(ROOT, rel)) ? readFileSync(join(ROOT, rel))
  : execFileSync('git', ['show', `HEAD:${rel}`], { cwd: ROOT, maxBuffer: 1 << 28 });
const src = (rel) => bytes(rel).toString('utf8');
let readSkinMesh = null;
try { ({ readSkinMesh } = await import('../tools/creation-suite/decals/glb-skin.mjs')); } catch (e) { /* sparse CI without tools/ */ }

const TABLE = JSON.parse(src('customization/templates/decal-placements.json'));
const TEMPLATES = ['super-heavyweight', 'powerhouse', 'showman', 'technician', 'highflyer', 'luchador',
  'powerhouse-w', 'athletic-w', 'striker-w'];

test('placement table covers 9 templates x 12 regions', () => {
  assert.deepEqual(Object.keys(TABLE.templates).sort(), [...TEMPLATES].sort());
  for (const t of TEMPLATES) {
    for (const R of BODY_REGIONS) {
      const r = TABLE.templates[t].regions[R.key];
      assert.ok(r, `${t}/${R.key} authored`);
      assert.ok(R.bones.includes(r.bone), `${t}/${R.key} Blender hit bone ${r.bone} is a region bone`);
      assert.ok(r.size_m > 0.03 && r.size_m < 0.5, `${t}/${R.key} size ${r.size_m}`);
    }
  }
});

const meshes = new Map();
async function mesh(t) {
  if (!meshes.has(t)) meshes.set(t, await readSkinMesh(bytes(`customization/templates/meshes/${t}.glb`)));
  return meshes.get(t);
}

test('placements land in the right region on every template (game resolver vs Blender)', { skip: !readSkinMesh && 'tools/ not in this checkout' }, async () => {
  for (const t of TEMPLATES) {
    const m = await mesh(t);
    const B = m.bones;
    for (const R of BODY_REGIONS) {
      const r = TABLE.templates[t].regions[R.key];
      const a = resolveAnchor(m, R.key, r.u, r.v, { fallback: false });
      assert.ok(a, `${t}/${R.key} resolves on the region's own skin`);
      assert.ok(R.bones.includes(a.bone), `${t}/${R.key} lands on ${a.bone}`);
      const d = Math.hypot(...a.point.map((x, i) => x - r.anchor[i]));
      assert.ok(d < 0.001, `${t}/${R.key} JS anchor within 1 mm of Blender (${(d * 1000).toFixed(3)} mm)`);
      const [x, y, z] = a.point;
      // body-part sanity, from the template's own skeleton
      const side = R.key.endsWith('_L') ? 1 : R.key.endsWith('_R') ? -1 : 0;
      if (side) assert.ok(x * side > 0.02, `${t}/${R.key} on the ${side > 0 ? 'left (+X)' : 'right (-X)'} side (x=${x.toFixed(3)})`);
      else assert.ok(Math.abs(x) < 0.08, `${t}/${R.key} near the midline (x=${x.toFixed(3)})`);
      const band = {
        chest: [B.spine02[1], B.neck[1]], back: [B.spine01[1], B.neck[1]], neck: [B.neck[1] - 0.04, B.head[1] + 0.02],
        face: [B.head[1] - 0.02, B.head[1] + 0.22],
        upper_arm_L: [B.lowerarm_L[1] - 0.03, B.upperarm_L[1] + 0.03], upper_arm_R: [B.lowerarm_R[1] - 0.03, B.upperarm_R[1] + 0.03],
        forearm_L: [B.hand_L[1] - 0.03, B.lowerarm_L[1] + 0.03], forearm_R: [B.hand_R[1] - 0.03, B.lowerarm_R[1] + 0.03],
        thigh_L: [B.calf_L[1], B.thigh_L[1]], thigh_R: [B.calf_R[1], B.thigh_R[1]],
        calf_L: [B.foot_L[1], B.calf_L[1]], calf_R: [B.foot_R[1], B.calf_R[1]],
      }[R.key];
      assert.ok(y >= band[0] && y <= band[1], `${t}/${R.key} height ${y.toFixed(3)} in [${band[0].toFixed(3)}, ${band[1].toFixed(3)}]`);
      const f = regionFrame(m, R.key);
      const out = [x - (f.start[0] + (f.end[0] - f.start[0]) * r.v), 0, z - (f.start[2] + (f.end[2] - f.start[2]) * r.v)];
      if (R.key === 'back') assert.ok(out[2] < 0, `${t}/back is behind the spine (dz=${out[2].toFixed(3)})`);
      else if (!R.key.startsWith('neck')) assert.ok(out[2] > 0, `${t}/${R.key} is on the front (dz=${out[2].toFixed(3)})`);
    }
  }
});

test('decal patch: non-empty, UVs in 0..1, on the skin near the anchor', { skip: !readSkinMesh && 'tools/ not in this checkout' }, async () => {
  for (const t of ['super-heavyweight', 'technician', 'athletic-w']) {
    const m = await mesh(t);
    for (const R of BODY_REGIONS) {
      const r = TABLE.templates[t].regions[R.key];
      const a = resolveAnchor(m, R.key, r.u, r.v, { fallback: false });
      const sz = layerSize({ scaleX: 1, scaleY: 1 }, R.key, 1, r.size_m);
      const p = projectDecal(m, a, sz);
      const n = p.positions.length / 3;
      assert.ok(n >= 9, `${t}/${R.key} patch has triangles (${n / 3})`);
      for (let i = 0; i < n; i++) {
        const u = p.uvs[i * 2], v = p.uvs[i * 2 + 1];
        assert.ok(u > -1e-6 && u < 1 + 1e-6 && v > -1e-6 && v < 1 + 1e-6, `${t}/${R.key} uv in range`);
        const P = [p.positions[i * 3], p.positions[i * 3 + 1], p.positions[i * 3 + 2]];
        const d = Math.hypot(P[0] - a.point[0], P[1] - a.point[1], P[2] - a.point[2]);
        assert.ok(d <= Math.hypot(sz.width, sz.height, Math.max(sz.width, sz.height) * 0.6) / 2 + 0.002, `${t}/${R.key} vertex inside the decal box`);
        // barycentric source rebuilds the same point on the skin (+ the 0.6 mm lift)
        const s = p.src[i], I = m.indices;
        const Q = [0, 1, 2].map((c) => s.b[0] * m.positions[I[s.tri * 3] * 3 + c] + s.b[1] * m.positions[I[s.tri * 3 + 1] * 3 + c] + s.b[2] * m.positions[I[s.tri * 3 + 2] * 3 + c]);
        assert.ok(Math.hypot(P[0] - Q[0], P[1] - Q[1], P[2] - Q[2]) < 0.0015, `${t}/${R.key} patch vertex lies on its skin triangle`);
      }
    }
  }
});

test('layer stack saves and restores per attire (JSON round trip)', () => {
  const attires = [{ equipped: {}, decals: [] }, { equipped: {}, decals: [] }];
  const a = createLayer({ part_id: 'nm-tattoo-2b18', kind: 'tattoo', region: 'upper_arm_R', u: 0.1, v: 0.4, scaleX: 1.5, rotation: 30, opacity: 0.8, color: '#22AA44' });
  const b = createLayer({ part_id: 'wh-scar-cheek-slash', kind: 'scar', region: 'face', u: 0.1, v: 0.12 });
  addLayer(attires[0].decals, a); addLayer(attires[0].decals, b);
  addLayer(attires[1].decals, mirrorLayer(a));
  const saved = JSON.stringify({ attires });
  const back = JSON.parse(saved).attires.map((x) => normalizeLayers(x.decals));
  assert.deepEqual(back[0], [a, b], 'attire 1 restores exactly, in draw order');
  assert.equal(back[1].length, 1);
  assert.equal(back[1][0].region, 'upper_arm_L', 'mirror moves R -> L');
  assert.equal(back[1][0].rotation, -30);
  assert.equal(a.color, '#22aa44');
  assert.ok(moveLayer(back[0], b.id, -1)); assert.equal(back[0][0].id, b.id, 'layer order moves');
  assert.ok(removeLayer(back[0], a.id)); assert.equal(back[0].length, 1);
  const junk = normalizeLayers([null, { part_id: 'x', region: 'nowhere', u: 7.25, v: 9, opacity: -1, scaleX: 99 }, { nope: 1 }]);
  assert.equal(junk.length, 1);
  assert.deepEqual([junk[0].region, junk[0].u, junk[0].v, junk[0].opacity, junk[0].scaleX], ['chest', 0.25, 1, 0, 4]);
  const many = []; for (let i = 0; i < MAX_LAYERS + 5; i++) addLayer(many, createLayer({ part_id: 'p' + i }));
  assert.equal(many.length, MAX_LAYERS, `capped at ${MAX_LAYERS} layers (WWE 2K22: 40 body/head layers)`);
  assert.throws(() => createLayer({ region: 'chest' }), /part_id/);
});

test('defaultPlacement reads the authored table, falls back per region', () => {
  const d = defaultPlacement(TABLE, 'athletic-w', 'chest');
  assert.equal(d.v, TABLE.templates['athletic-w'].regions.chest.v);
  assert.equal(d.size, TABLE.templates['athletic-w'].regions.chest.size_m);
  const f = defaultPlacement(null, 'x', 'back');
  assert.equal(f.u, 0.5); assert.equal(f.size, REGION_BY_KEY.back.size);
});

test('wear-off hook: region zones map onto wear-off.js layers', () => {
  for (const R of BODY_REGIONS) assert.ok(['face', 'upper', 'lower'].includes(R.zone));
  const scar = wearLayer({ id: 's', kind: 'scar', zone: REGION_BY_KEY.face.zone });
  for (let i = 0; i < 100; i++) applyHit(scar, { zone: 'face' });
  assert.equal(scar.opacity, WEAR_FLOORS.scar, 'a scar decal barely fades');
});

test('buildDecalMesh with a stubbed THREE (no WebGL): skinned patch shares skeleton + morphs', { skip: !readSkinMesh && 'tools/ not in this checkout' }, async () => {
  const m = await mesh('technician');
  class Attr { constructor(a, n) { this.array = a; this.itemSize = n; this.count = a.length / n; }
    getX(i) { return this.array[i * this.itemSize]; } getY(i) { return this.array[i * this.itemSize + 1]; } getZ(i) { return this.array[i * this.itemSize + 2]; } }
  const THREE = {
    BufferGeometry: class { constructor() { this.attributes = {}; this.morphAttributes = {}; } setAttribute(k, v) { this.attributes[k] = v; } computeVertexNormals() { this.normals = true; } },
    Float32BufferAttribute: class extends Attr { constructor(a, n) { super(Float32Array.from(a), n); } },
    Uint16BufferAttribute: class extends Attr { constructor(a, n) { super(Uint16Array.from(a), n); } },
    Color: class { constructor(c) { this.c = c; } },
    MeshStandardMaterial: class { constructor(o) { Object.assign(this, o); } },
    SkinnedMesh: class { constructor(g, mat) { this.geometry = g; this.material = mat; this.userData = {};
      const v = () => ({ copy() {} }); this.position = v(); this.quaternion = v(); this.scale = v(); }
      bind(s, b) { this.skeleton = s; this.bindMatrix = b; } },
    SRGBColorSpace: 'srgb',
  };
  const nv = m.positions.length / 3;
  const morph = new Attr(new Float32Array(nv * 3).fill(0.01), 3);
  const children = [];
  const body = { geometry: { morphAttributes: { position: [morph] }, morphTargetsRelative: true }, skeleton: { id: 'skel' }, bindMatrix: 'bm',
    morphTargetInfluences: [0.5], morphTargetDictionary: { m: 0 }, parent: { add: (o) => children.push(o) }, position: {}, quaternion: {}, scale: {} };
  const layer = createLayer({ part_id: 'wh-scar-chest-slash', kind: 'scar', region: 'chest', ...TABLE.templates.technician.regions.chest });
  const dm = buildDecalMesh(THREE, body, layer, { image: { width: 512, height: 512 } }, { meshData: m, size: TABLE.templates.technician.regions.chest.size_m });
  assert.ok(dm, 'decal mesh built');
  assert.equal(children[0], dm, 'added beside the body');
  assert.equal(dm.skeleton.id, 'skel', 'shares the body skeleton');
  assert.equal(dm.morphTargetInfluences, body.morphTargetInfluences, 'body sliders drive the decal');
  const mp = dm.geometry.morphAttributes.position[0];
  assert.ok(Math.abs(mp.getX(0) - 0.01) < 1e-6, 'morph deltas interpolated onto the patch');
  assert.equal(dm.geometry.attributes.skinIndex.count, dm.geometry.attributes.position.count);
  assert.equal(dm.material.opacity, 1); assert.equal(dm.material.transparent, true);
});

test('catalog: 99 tattoos carry a body-region decal placement; scars are real CC0 files', () => {
  const C = JSON.parse(src('customization/creation-suite-ui/data/parts-catalog.json'));
  assert.equal(C.total, C.parts.length);
  assert.equal(Object.values(C.counts).reduce((a, b) => a + b, 0), C.total);
  const tats = C.parts.filter((p) => p.source === 'teardown/wwf-no-mercy/textures/rom/tattoo');
  assert.equal(tats.length, 99);
  for (const p of tats) {
    assert.equal(p.placement.kind, 'body_region_decal');
    assert.ok(REGION_BY_KEY[p.placement.region]);
    assert.equal(p.decal_kind, 'tattoo');
  }
  const scars = C.parts.filter((p) => p.suite_slot === 'scar' && !p.reference_only);
  assert.ok(scars.length >= 8 && scars.length <= 12, `${scars.length} scars`);
  const TRACKED = new Set(execFileSync('git', ['ls-files'], { cwd: ROOT, maxBuffer: 1 << 28 }).toString().split('\n'));
  for (const p of scars) {
    assert.equal(p.geometry_pending, false);
    assert.equal(p.license, 'CC0-1.0');
    assert.ok(REGION_BY_KEY[p.placement.region], `${p.id} region`);
    assert.ok(TRACKED.has(p.asset) || existsSync(join(ROOT, p.asset)), `${p.id} PNG in repo`);
    const png = bytes(p.asset);
    assert.equal(png.readUInt32BE(0), 0x89504e47, `${p.id} is a PNG`);
    assert.equal(png[25], 6, `${p.id} is RGBA`);
    assert.doesNotMatch(p.name, /kaz|heihachi|mishima|tekken|wwe|austin|rock/i, 'generic name (names law)');
  }
  const ref = C.parts.filter((p) => p.reference_only);
  assert.equal(ref.length, 1);
  assert.equal(ref[0].asset, null, 'reference row claims no texture');
  assert.equal(ref[0].geometry_pending, true);
  assert.doesNotMatch(ref[0].name, /kaz/i);
});
