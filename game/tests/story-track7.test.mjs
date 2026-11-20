/* story-track7.test.mjs — Track 7 (cutscenes & story mode) guards.
 *
 * WHAT THIS GUARDS: game/js/story/* — the cinematic director
 * (Theatre-pattern sequences + Orchestrator-pattern triggers + ink
 * narrative), the multi-target brawler camera, the Yuka-backed
 * navmesh + grunt pathfinding, and the combat-reactive dialogue FSM.
 * A regression here silently breaks Heart and Mind Within's
 * cutscenes, brawler framing, grunt movement, and banter.
 *
 * Run: node --test game/tests/story-track7.test.mjs (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const storyDir = join(root, 'game', 'js', 'story');

const {
  WHSequence, WHProject, WHTriggerGraph, WHCinematicDirector,
} = await import(join(storyDir, 'cinematic-director.js'));
const { WHBrawlerCamera } = await import(join(storyDir, 'brawler-camera.js'));
const { WHNavMesh, WHSquad } = await import(join(storyDir, 'navmesh.js'));
const { WHDialogueFSM, DEMO_LINES } = await import(join(storyDir, 'dialogue-fsm.js'));

/* ---------------- cinematic director ---------------- */
test('sequence interpolates keyframed props with easing', () => {
  const seq = new WHSequence('t');
  seq.addTrack('pos', [
    { t: 0, value: [0, 0, 0] },
    { t: 2, value: [10, 0, 0], ease: 'linear' },
  ]);
  const target = { pos: [0, 0, 0] };
  seq.play(target);
  seq.update(1.0);
  assert.ok(Math.abs(target.pos[0] - 5) < 0.001, `linear mid = 5, got ${target.pos[0]}`);
  seq.update(1.0);
  assert.ok(Math.abs(target.pos[0] - 10) < 0.001, 'ends at keyframe value');
  assert.equal(seq.playing, false, 'stops at end');
});

test('sequence fires onDone and supports scrub', () => {
  const seq = new WHSequence('t');
  seq.addTrack('x', [{ t: 0, value: 0 }, { t: 4, value: 8 }]);
  const target = { x: 0 };
  let done = false;
  seq.play(target, { onDone: () => { done = true; } });
  seq.seek(target, 2);
  assert.ok(Math.abs(target.x - 4) < 0.01, `scrub to t=2 -> x~4, got ${target.x}`);
  seq.update(2.5);
  assert.equal(done, true, 'onDone fired');
});

test('trigger graph: flag trigger fires once and runs actions', () => {
  const g = new WHTriggerGraph();
  const seen = [];
  g.onDialogue = (prompt) => seen.push(prompt);
  g.addTrigger({
    id: 't1',
    when: { flag: ['waveClear', 2] },
    do: [{ action: 'flag', name: 'bossSpawn', value: true }, { action: 'dialogue', prompt: 'The warden stirs.' }],
  });
  g.update(0.016, {});
  assert.equal(seen.length, 0, 'not fired before flag set');
  g.setFlag('waveClear', 2);
  g.update(0.016, {});
  assert.equal(seen.length, 1, 'dialogue action ran');
  assert.equal(g.getFlag('bossSpawn'), true, 'flag action ran');
  g.update(0.016, {});
  assert.equal(seen.length, 1, 'one-shot: no refire');
});

test('trigger graph: proximity zone trigger', () => {
  const g = new WHTriggerGraph();
  let fired = 0;
  g.addTrigger({ id: 'z', when: { zone: { x: 5, z: 0, r: 2 } }, do: [{ action: 'fn', fn: () => fired++ }] });
  g.update(0.016, { playerPos: { x: 0, y: 0, z: 0 } });
  assert.equal(fired, 0, 'outside zone: silent');
  g.update(0.016, { playerPos: { x: 5.5, y: 0, z: 0 } });
  assert.equal(fired, 1, 'inside zone: fired');
});

test('director plays shots and advances', () => {
  const d = new WHCinematicDirector();
  const cam = { position: { x: 0, y: 0, z: 0, set(x, y, z) { this.x = x; this.y = y; this.z = z; } }, lookAt() {} };
  d.playShots(cam, [
    { pos: [0, 2, 8], look: [0, 1, 0], transition: 1, hold: 0 },
    { pos: [4, 2, 6], look: [0, 1, 0], transition: 1, hold: 0 },
  ]);
  d.update(0.5, {});
  assert.ok(cam.position.x > 0 && cam.position.x < 4, `camera dollying: x=${cam.position.x}`);
  assert.equal(d.active.length, 1, 'sequence active');
});

test('director runs the vendored ink demo story', async () => {
  const d = new WHCinematicDirector();
  const json = readFileSync(join(root, 'game', 'story', 'demo', 'demo-banter.ink.json'), 'utf8');
  const res = await d.loadStory(json);
  assert.equal(res.ok, true, 'inkjs runtime loads the compiled story');
  const first = d.storyContinue();
  assert.ok(first.lines.length >= 2, `story yields lines: ${first.lines.length}`);
  assert.equal(first.choices.length, 3, 'story yields 3 choices');
  const after = d.storyChoose(1);
  assert.ok(after.lines.some((l) => l.includes('Take it back')), 'choice 1 branch text');
  assert.equal(d.storyVar('wave'), 2, 'ink variable incremented');
});

/* ---------------- brawler camera ---------------- */
function fakeCam(aspect = 16 / 9, fov = 50) {
  return {
    aspect, fov,
    position: { x: 0, y: 3, z: 12, },
    updateProjectionMatrix() {},
    lookAt() {},
  };
}

test('brawler camera frames N targets within the frustum fit', () => {
  const cam = new WHBrawlerCamera().attach(fakeCam());
  cam.setTargets([
    { pos: { x: -3, y: 0, z: 0 }, weight: 2 }, // player, weighted
    { pos: { x: 3, y: 0, z: 0 }, weight: 1 },
    { pos: { x: 0, y: 0, z: 2 }, weight: 1 },
  ]);
  const f = cam.frame(16 / 9, 50);
  assert.ok(f.dist >= 5.5, `min distance respected: ${f.dist}`);
  assert.ok(f.center.x < 0, `weighted centroid leans to player: ${f.center.x}`);
  // Widen the threat spread -> camera must pull back.
  cam.setTargets([
    { pos: { x: -8, y: 0, z: 0 }, weight: 1 },
    { pos: { x: 8, y: 0, z: 0 }, weight: 1 },
  ]);
  const f2 = cam.frame(16 / 9, 50);
  assert.ok(f2.dist > f.dist, `wider spread -> farther camera (${f.dist} -> ${f2.dist})`);
});

test('brawler camera portrait behavior: widen FOV, respect wall cap', () => {
  const cam = new WHBrawlerCamera().attach(fakeCam(0.5, 50)); // tall phone
  cam.setTargets([
    { pos: { x: -10, y: 0, z: 0 }, weight: 1 },
    { pos: { x: 10, y: 0, z: 0 }, weight: 1 },
  ]);
  const f = cam.frame(0.5, 50);
  assert.ok(f.dist <= 10.5 + 1e-6, `never past the arena wall cap: ${f.dist}`);
  assert.ok(f.fov > 50, `portrait widens FOV instead of pullback: ${f.fov}`);
});

test('brawler camera wall clamp keeps the dolly out of geometry', () => {
  const cam = new WHBrawlerCamera().attach(fakeCam());
  cam.enable();
  cam.setTargets([{ pos: { x: 0, y: 0, z: 0 }, weight: 1 }]);
  cam.setObstacleTester(() => 4.0); // wall 4m behind the centroid
  for (let i = 0; i < 120; i++) cam.update(1 / 60);
  const px = cam.camera.position.x, py = cam.camera.position.y, pz = cam.camera.position.z;
  const d = Math.hypot(px - cam._center.x, py - (cam._center.y + 0.75), pz - cam._center.z);
  assert.ok(d < 5.5, `clamped dolly distance ${d.toFixed(2)} < unclamped`);
  cam.disable();
  assert.equal(cam.enabled, false);
});

/* ---------------- navmesh ---------------- */
test('navmesh builds from floor rects and paths across regions', async () => {
  const nm = new WHNavMesh();
  await nm.init();
  nm.buildFromRects([
    { x1: -8, z1: -8, x2: 0, z2: 8 },
    { x1: 0, z1: -8, x2: 8, z2: 8 },
  ]);
  assert.ok(nm.regionCount() >= 1, 'regions built');
  const path = nm.findPath({ x: -6, y: 0, z: 0 }, { x: 6, y: 0, z: 0 });
  assert.ok(path && path.length >= 2, 'path found across regions');
  assert.ok(Math.abs(path[0].x - -6) < 0.01 && Math.abs(path[path.length - 1].x - 6) < 0.01, 'path endpoints correct');
});

test('navmesh clampStep keeps steps on the walkable area', async () => {
  const nm = new WHNavMesh();
  await nm.init();
  nm.buildFromRects([{ x1: -5, z1: -5, x2: 5, z2: 5 }]);
  const inside = nm.clampStep(null, { x: 0, y: 0, z: 0 }, { x: 2, y: 0, z: 2 });
  assert.ok(Math.abs(inside.pos.x - 2) < 0.01, 'inside steps pass through');
  const outside = nm.clampStep(nm.regionFor({ x: 0, y: 0, z: 0 }), { x: 4, y: 0, z: 0 }, { x: 40, y: 0, z: 0 });
  assert.ok(Math.abs(outside.pos.x) <= 5.5, `escaped step clamped to the mesh: x=${outside.pos.x}`);
});

test('squad of grunts pursues the focus without stacking', async () => {
  const nm = new WHNavMesh();
  await nm.init();
  nm.buildFromRects([{ x1: -20, z1: -20, x2: 20, z2: 20 }]);
  const squad = new WHSquad(nm, { count: 8 });
  await squad.init();
  squad.spawnRing(0, 0, 0, 10);
  squad.setFocus({ x: 0, y: 0, z: 0 }, 'flank');
  const before = squad.grunts.map((g) => Math.hypot(g.pos.x, g.pos.z));
  for (let i = 0; i < 120; i++) squad.update(1 / 60);
  const after = squad.grunts.map((g) => Math.hypot(g.pos.x, g.pos.z));
  const avgBefore = before.reduce((a, b) => a + b, 0) / before.length;
  const avgAfter = after.reduce((a, b) => a + b, 0) / after.length;
  assert.ok(avgAfter < avgBefore, `grunts closed distance (${avgBefore.toFixed(1)} -> ${avgAfter.toFixed(1)})`);
  // Separation: no two grunts share the same spot.
  let minD = Infinity;
  for (let i = 0; i < squad.grunts.length; i++)
    for (let j = i + 1; j < squad.grunts.length; j++) {
      const a = squad.grunts[i].pos, b = squad.grunts[j].pos;
      minD = Math.min(minD, Math.hypot(a.x - b.x, a.z - b.z));
    }
  assert.ok(minD > 0.15, `separation kept grunts apart (min dist ${minD.toFixed(2)})`);
});

/* ---------------- dialogue FSM ---------------- */
test('dialogue FSM picks combat-state-reactive lines', () => {
  const fsm = new WHDialogueFSM({ globalCooldownMs: 0 }).registerLines(DEMO_LINES);
  const heard = [];
  fsm.onLine = (rec) => heard.push(rec);
  fsm.emit({ type: 'fightStart' });
  assert.equal(heard.length, 1, 'fight start line fired');
  fsm.emit({ type: 'damageTaken', damage: 5, hpPct: 0.9 });
  assert.equal(heard.length, 1, 'small hit: below minDmg, silent');
  fsm.emit({ type: 'damageTaken', damage: 50, hpPct: 0.6 });
  assert.equal(heard.length, 2, 'heavy hit: damage threshold line fired');
  assert.ok(heard[1].line.includes('cracked'), 'picked the minDmg:40 line');
});

test('dialogue FSM hp watcher fires low/critical once per fight', () => {
  const fsm = new WHDialogueFSM({ globalCooldownMs: 0 }).registerLines(DEMO_LINES);
  const heard = [];
  fsm.onLine = (rec) => heard.push(rec);
  let e = fsm.watchHp('p2', 0.8);
  assert.equal(e, null, 'healthy: silent');
  e = fsm.watchHp('p2', 0.4);
  assert.equal(e && e.type, 'hpLow', 'crossed 50%: hpLow event');
  fsm.emit(e);
  fsm.emit(fsm.watchHp('p2', 0.35) || { type: 'none' });
  assert.equal(heard.filter((h) => h.event === 'hpLow').length, 1, 'hpLow fires once');
  e = fsm.watchHp('p2', 0.2);
  assert.equal(e && e.type, 'hpCritical', 'crossed 25%: hpCritical event');
});

test('dialogue FSM inworld envelope is well-formed', () => {
  const fsm = new WHDialogueFSM();
  const env = fsm.toInworldEvent({ type: 'damageTaken', fighterId: 'echo-1', hpPct: 0.62, damage: 22, wave: 3, recentLines: ['a', 'b'] });
  assert.equal(env.characterId, 'echo-1');
  assert.equal(env.eventType, 'damageTaken');
  assert.equal(env.combatState.hpPct, 0.62);
  assert.equal(env.combatState.wave, 3);
});
