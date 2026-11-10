// hair-spring.test.mjs — verifies the spring-bone hair solver against a
// synthetic rig built with the repo's own vendored three.js.
// Run: node --test game/js/hair-spring.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { register } from 'node:module';

const THREE_URL = process.env.WH_THREE
  || new URL('../../customization/create-fighter/vendor/three.module.js', import.meta.url).href;
register('data:text/javascript,' + encodeURIComponent(
  `export async function resolve(spec, ctx, next) {
     if (spec === 'three') return { url: ${JSON.stringify(THREE_URL)}, shortCircuit: true };
     return next(spec, ctx);
   }`));

const THREE = await import('three');
const { attachHairPhysics, discoverHairChains } = await import('./hair-spring.js');

function buildRig() {
  const root = new THREE.Group();
  const neck = new THREE.Bone(); neck.name = 'neck'; neck.position.set(0, 1.40, 0);
  const head = new THREE.Bone(); head.name = 'head'; head.position.set(0, 0.12, 0);
  neck.add(head); root.add(neck);
  const mkChain = (prefix, x) => {
    const bones = [];
    let parent = head;
    for (let i = 0; i < 3; i++) {
      const b = new THREE.Bone(); b.name = `${prefix}${i + 1}`;
      b.position.set(i === 0 ? x : 0, i === 0 ? 0.02 : -0.07, i === 0 ? -0.04 : -0.015);
      parent.add(b); bones.push(b); parent = b;
    }
    return bones;
  };
  const chainA = mkChain('Hair_OPT_A', -0.05);
  const chainB = mkChain('Hair_OPT_B', 0.05);
  const bones = [neck, head, ...chainA, ...chainB];
  // skinned strip weighted down both chains (and the head, like a real cap)
  const geo = new THREE.BufferGeometry();
  const verts = []; const idx = []; const sw = [];
  const all = [head, ...chainA, ...chainB];
  all.forEach((b, i) => {
    verts.push(0, -i * 0.05, 0);
    idx.push(bones.indexOf(b), 0, 0, 0);
    sw.push(1, 0, 0, 0);
  });
  geo.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
  geo.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(idx, 4));
  geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute(sw, 4));
  const mesh = new THREE.SkinnedMesh(geo, new THREE.MeshBasicMaterial());
  mesh.add(neck); // bones live under the mesh like a loaded GLB skin
  mesh.bind(new THREE.Skeleton(bones));
  root.add(mesh);
  root.updateMatrixWorld(true);
  return { root, head, chainA, chainB };
}

test('discovery finds the chains and never the carrier head/neck', () => {
  const { root, head } = buildRig();
  const chains = discoverHairChains(root);
  assert.equal(chains.length, 2);
  assert.ok(chains.every((c) => !c.joints.includes(head)));
});

test('gravity: chains lag the pose and hang below the rigid-follow tip', () => {
  const rig = buildRig();
  const sys = attachHairPhysics(rig.root, {});
  assert.ok(sys, 'system attaches');
  assert.equal(sys.chains.length, 2);
  // rigid reference: same pose, no physics
  const ref = buildRig();
  rig.head.rotation.z = 0.6; ref.head.rotation.z = 0.6;
  rig.root.updateMatrixWorld(true); ref.root.updateMatrixWorld(true);
  for (let i = 0; i < 120; i++) { rig.root.updateMatrixWorld(true); sys.update(1 / 60, {}); }
  rig.root.updateMatrixWorld(true); ref.root.updateMatrixWorld(true);
  const tipA = new THREE.Vector3(); rig.chainA[2].getWorldPosition(tipA);
  const tipR = new THREE.Vector3(); ref.chainA[2].getWorldPosition(tipR);
  assert.ok(tipA.y < tipR.y - 0.01, `physics tip hangs lower (${tipA.y.toFixed(3)} < ${tipR.y.toFixed(3)})`);
  // the solver must never write the carrier bones
  assert.equal(rig.head.quaternion.z, ref.head.quaternion.z);
  assert.equal(rig.head.quaternion.w, ref.head.quaternion.w);
});

test('wind: tips displace downwind versus the gravity-only state', () => {
  const rig = buildRig();
  const sys = attachHairPhysics(rig.root, {});
  rig.head.rotation.z = 0.3; rig.root.updateMatrixWorld(true);
  for (let i = 0; i < 90; i++) { rig.root.updateMatrixWorld(true); sys.update(1 / 60, {}); }
  const before = new THREE.Vector3(); rig.chainA[2].getWorldPosition(before);
  for (let i = 0; i < 60; i++) { rig.root.updateMatrixWorld(true); sys.update(1 / 60, { wind: new THREE.Vector3(7, 0, 0) }); }
  const after = new THREE.Vector3(); rig.chainA[2].getWorldPosition(after);
  assert.ok(after.x > before.x + 0.01, `wind pushed tip +x (${before.x.toFixed(3)} -> ${after.x.toFixed(3)})`);
});

test('authored-rig jiggle chains stay with WHSpringBones (never claimed)', () => {
  const rig = buildRig();
  // rename one chain to the authored Wiggle-2 convention
  rig.chainB.forEach((b, i) => { b.name = `hair_jiggle_0_${i}`; });
  const chains = discoverHairChains(rig.root);
  assert.equal(chains.length, 1, 'only the imported-convention chain is discovered');
  assert.ok(chains[0].joints[0].name.startsWith('Hair_OPT_A'));
});

test('rigid hair (head-weighted only) attaches no system', () => {
  const root = new THREE.Group();
  const neck = new THREE.Bone(); neck.name = 'neck'; neck.position.set(0, 1.4, 0);
  const head = new THREE.Bone(); head.name = 'head'; head.position.set(0, 0.12, 0);
  neck.add(head);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0], 3));
  geo.setAttribute('skinIndex', new THREE.Uint16BufferAttribute([1, 0, 0, 0], 4));
  geo.setAttribute('skinWeight', new THREE.Float32BufferAttribute([1, 0, 0, 0], 4));
  const mesh = new THREE.SkinnedMesh(geo, new THREE.MeshBasicMaterial());
  mesh.add(neck);
  mesh.bind(new THREE.Skeleton([neck, head]));
  root.add(mesh); root.updateMatrixWorld(true);
  assert.equal(attachHairPhysics(root, {}), null);
});
