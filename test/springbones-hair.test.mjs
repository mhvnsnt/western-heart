// Production hair / cloth secondary motion (2026-11-01): game/js/springbones.js chains collide with the fighter's own
// body, keep their segment lengths, and hold their style at the root while the tips flow (TressFX-style falloff).
// Run: node --test test/springbones-hair.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
await import(join(ROOT, 'tools/anim/node_game_env.mjs'));
const THREE = await import('three');
const SB = await import(join(ROOT, 'game/js/springbones.js'));

// a 1.75 m fighter: spine to head, shoulders, arms, thighs, and a 4-joint hair chain hanging behind the head
function fighter() {
  const root = new THREE.Group();
  const mk = (name, parent, x, y, z) => {
    const b = new THREE.Bone(); b.name = name;
    const pw = new THREE.Vector3(); if (parent.isBone) parent.getWorldPosition(pw);
    b.position.set(x - pw.x, y - pw.y, z - pw.z); parent.add(b); b.updateMatrixWorld(true); return b;
  };
  const hips = mk('Hips', root, 0, 1.0, 0), sp = mk('Spine', hips, 0, 1.1, 0), sp1 = mk('Spine1', sp, 0, 1.2, 0);
  const sp2 = mk('Spine2', sp1, 0, 1.32, 0), neck = mk('Neck', sp2, 0, 1.5, 0), head = mk('Head', neck, 0, 1.58, 0.01);
  for (const [s, x] of [['Left', 1], ['Right', -1]]) {
    const sh = mk(s + 'Shoulder', sp2, 0.06 * x, 1.45, 0), arm = mk(s + 'Arm', sh, 0.18 * x, 1.44, 0);
    mk(s + 'ForeArm', arm, 0.45 * x, 1.44, 0);
    const up = mk(s + 'UpLeg', hips, 0.1 * x, 0.95, 0); mk(s + 'Leg', up, 0.1 * x, 0.52, 0);
  }
  const h0 = mk('hair_jiggle_0_0', head, 0, 1.68, -0.13), h1 = mk('hair_jiggle_0_1', h0, 0, 1.56, -0.15);
  const h2 = mk('hair_jiggle_0_2', h1, 0, 1.44, -0.16); mk('hair_jiggle_0_3', h2, 0, 1.32, -0.16);
  root.updateMatrixWorld(true);
  return { root, hips, head };
}

test('hair chains get body colliders from the fighter\'s own skeleton', () => {
  const { root } = fighter();
  const cols = SB.bodyColliders(root);
  assert.ok(cols.length >= 9, `${cols.length} colliders`);
  const head = cols.find((c) => c.bone.name === 'Head');
  assert.ok(head && head.radius > 0.09 && head.radius < 0.13, `head sphere sized by height (${head && head.radius.toFixed(3)} m)`);
  const sb = new SB.WHSpringBones();
  assert.equal(sb.autoDiscover(root), 1);
  const ch = sb.chains[0];
  assert.equal(ch.substeps, 3); assert.ok(ch.stiffnessTip < ch.stiffness, 'stiffness falls root -> tip');
  assert.ok(ch.colliders.length >= 7 && ch.colliders.every((c) => !c.leg), 'hair collides with the upper body only');
});

test('strands stay outside the head, neck and chest and keep their lengths through violent motion', () => {
  const { root, hips } = fighter();
  const sb = new SB.WHSpringBones();
  sb.autoDiscover(root);
  const ch = sb.chains[0];
  const lens = ch._tails.map((t) => t.len);
  let worst = Infinity;
  for (let f = 0; f < 240; f++) {
    const t = f / 60;
    hips.position.set(Math.sin(t * 9) * 0.25, 1.0 + Math.abs(Math.sin(t * 5)) * 0.2, Math.cos(t * 7) * 0.3); // dash, hop, sway
    hips.rotation.set(Math.sin(t * 6) * 0.6, Math.sin(t * 4) * 1.2, Math.cos(t * 5) * 0.4);
    root.updateMatrixWorld(true);
    sb.update(1 / 60, t);
    const shapes = ch._colliderShapes();
    ch._tails.forEach((tl, i) => {
      assert.ok(Math.abs(tl.cur.distanceTo(tl.head) - lens[i]) < 1e-6, `segment ${i} length`);
      for (const c of shapes.slice(0, 3)) { // head, neck, chest
        const ab = c.b.clone().sub(c.a), L = ab.lengthSq();
        const u = L > 1e-12 ? Math.min(1, Math.max(0, tl.cur.clone().sub(c.a).dot(ab) / L)) : 0;
        worst = Math.min(worst, tl.cur.distanceTo(c.a.clone().addScaledVector(ab, u)) - c.r);
      }
    });
  }
  assert.ok(worst > -0.005, `deepest penetration ${worst.toFixed(4)} m (allowed 5 mm)`);
});

test('the root holds the style while the tip flows (TressFX-style falloff)', () => {
  const { root, hips } = fighter();
  const sb = new SB.WHSpringBones();
  sb.autoDiscover(root);
  const ch = sb.chains[0];
  const rest = ch._tails.map((t) => t.cur.clone().sub(t.head));
  for (let f = 0; f < 30; f++) {  // a quick sidestep (0.3 m over 10 frames), then stand still
    if (f < 10) hips.position.x += 0.03;
    root.updateMatrixWorld(true);
    sb.update(1 / 60, f / 60);
  }
  const dev = ch._tails.map((t, i) => t.cur.clone().sub(t.head).angleTo(rest[i]));
  assert.ok(dev[0] < dev[dev.length - 1], `root ${dev[0].toFixed(3)} rad has settled more than the tip ${dev[dev.length - 1].toFixed(3)} rad`);
});

test('existing jiggle chains keep the old single-step, collider-free behaviour', () => {
  const b = new THREE.Bone(); b.name = 'DEF-breast.L';
  const c = new SB.SpringChain([b]);
  assert.equal(c.substeps, 1); assert.equal(c.colliders.length, 0); assert.equal(c.stiffnessTip, c.stiffness);
});
