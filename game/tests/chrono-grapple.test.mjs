/* chrono-grapple.test.mjs — Track 4 (Chrono physics) joint-constraint lane.
 *
 * Covers the deterministic joint solver in game/js/chrono-grapple.js:
 * joint taxonomy (fixed/spherical/revolute), engines, springs, torque
 * nodes, the MuscleStrain model, the SubmissionChain state machine, the
 * GrappleRig servo contract, and the determinism contract (identical
 * inputs ⇒ bit-identical outputs). DOM/THREE paths are not unit-tested.
 *
 * Run: node --test game/tests/chrono-grapple.test.mjs   (from repo root)
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const cg = await import(join(here, '..', 'js', 'chrono-grapple.js'));

const DT = 1 / 60;
const V3LEN = (v) => Math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);

function sysNoGravity() {
  return new cg.ChronoSystem({ substeps: 2, iterations: 12, gravity: [0, 0, 0] });
}

/* ---- joint taxonomy ---- */

test('FIXED link welds two bodies: anchors converge, orientation locks', () => {
  const S = sysNoGravity();
  const A = S.addBody(new cg.ChronoBody({ kinematic: true, pos: [0, 0, 0] }));
  const B = S.addBody(new cg.ChronoBody({ mass: 1, inertia: [1, 1, 1], pos: [1, 0, 0] }));
  B.v = [2, 0, 0];
  S.addLink(new cg.ChronoLink(cg.JOINT.FIXED, A, B, {}));
  for (let i = 0; i < 120; i++) S.step(DT);
  assert.ok(V3LEN(B.p) < 0.02, 'body pulled to anchor, got ' + V3LEN(B.p));
  assert.ok(V3LEN(B.v) < 0.05, 'velocity killed, got ' + V3LEN(B.v));
});

test('SPHERICAL link holds position but leaves rotation free', () => {
  const S = sysNoGravity();
  const A = S.addBody(new cg.ChronoBody({ kinematic: true, pos: [0, 0, 0] }));
  const B = S.addBody(new cg.ChronoBody({ mass: 1, inertia: [1, 1, 1], pos: [0.5, 0, 0] }));
  S.addLink(new cg.ChronoLink(cg.JOINT.SPHERICAL, A, B,
    { anchorA: [0.5, 0, 0], anchorB: [0, 0, 0] }));
  B.w = [0, 0, 3];
  for (let i = 0; i < 60; i++) S.step(DT);
  assert.ok(V3LEN(B.p.map((v, i) => v - [0.5, 0, 0][i])) < 0.02, 'anchor held');
  assert.ok(Math.abs(V3LEN(B.w) - 3) < 0.2, 'spin preserved (no angular rows), got ' + V3LEN(B.w));
});

test('REVOLUTE link: hinge axis free, off-axis rotation killed', () => {
  const S = sysNoGravity();
  const A = S.addBody(new cg.ChronoBody({ kinematic: true, pos: [0, 0, 0] }));
  const B = S.addBody(new cg.ChronoBody({ mass: 1, inertia: [1, 1, 1], pos: [0, 0, 0] }));
  const link = S.addLink(new cg.ChronoLink(cg.JOINT.REVOLUTE, A, B, {}));
  B.w = [3, 2, 0]; // off-axis spin must die; hinge (Z) stays free
  for (let i = 0; i < 60; i++) S.step(DT);
  assert.ok(Math.abs(B.w[0]) < 0.15 && Math.abs(B.w[1]) < 0.15,
    'off-axis killed, got [' + B.w.map(v => v.toFixed(2)) + ']');
  B.w = [0, 0, 3];
  for (let i = 0; i < 60; i++) S.step(DT);
  assert.ok(Math.abs(link.angle - 3.0) < 0.3, 'hinge angle tracked, got ' + link.angle.toFixed(2));
});

/* ---- engines, springs, torque nodes ---- */

test('ChronoEngine SPEED mode reaches target hinge speed', () => {
  const S = sysNoGravity();
  const A = S.addBody(new cg.ChronoBody({ kinematic: true, pos: [0, 0, 0] }));
  const B = S.addBody(new cg.ChronoBody({ mass: 1, inertia: [1, 1, 1], pos: [0, 0, 0] }));
  const link = S.addLink(new cg.ChronoLink(cg.JOINT.REVOLUTE, A, B, {}));
  S.addEngine(new cg.ChronoEngine(link, { mode: cg.ENG_MODE.SPEED, targetSpeed: 2, maxTorque: 50, kp: 40 }));
  for (let i = 0; i < 60; i++) S.step(DT);
  assert.ok(Math.abs(link.hingeRelVel() - 2) < 0.15, 'speed reached, got ' + link.hingeRelVel().toFixed(2));
});

test('ChronoSpring pulls bodies toward rest length', () => {
  const S = sysNoGravity();
  const A = S.addBody(new cg.ChronoBody({ mass: 1, inertia: [1, 1, 1], pos: [-1, 0, 0] }));
  const B = S.addBody(new cg.ChronoBody({ mass: 1, inertia: [1, 1, 1], pos: [1, 0, 0] }));
  S.addSpring(new cg.ChronoSpring(A, B, { restLength: 0.5, stiffness: 60, damping: 4 }));
  const d0 = V3LEN([B.p[0]-A.p[0], B.p[1]-A.p[1], B.p[2]-A.p[2]]);
  for (let i = 0; i < 120; i++) S.step(DT);
  const d1 = V3LEN([B.p[0]-A.p[0], B.p[1]-A.p[1], B.p[2]-A.p[2]]);
  assert.ok(d1 < d0 * 0.7, `spring contracted ${d0.toFixed(2)} -> ${d1.toFixed(2)}`);
});

test('torque node: hanging body reports weight as reaction force', () => {
  const S = new cg.ChronoSystem({ substeps: 2, iterations: 12 }); // gravity on
  const A = S.addBody(new cg.ChronoBody({ kinematic: true, pos: [0, 1, 0] }));
  const B = S.addBody(new cg.ChronoBody({ mass: 2, inertia: [1, 1, 1], pos: [0, 0, 0] }));
  S.addLink(new cg.ChronoLink(cg.JOINT.FIXED, A, B, { anchorA: [0, -1, 0], anchorB: [0, 0, 0] }));
  for (let i = 0; i < 120; i++) S.step(DT);
  const link = S.links[0];
  const F = V3LEN(link.reactionForce);
  assert.ok(Math.abs(F - 2 * 9.81) < 2.5, `reaction ≈ m·g, got ${F.toFixed(2)}`);
});

test('determinism: identical runs produce identical snapshots', () => {
  const run = () => {
    const rig = new cg.GrappleRig();
    rig.startChain('armbar');
    for (let i = 0; i < 30; i++) rig.stepCombat(DT, {});
    return JSON.stringify(rig.system.bodies.map(b => b.snapshot()));
  };
  assert.equal(run(), run());
});

/* ---- MuscleStrain ---- */

test('MuscleStrain: sub-floor torque recovers, over-floor accumulates', () => {
  const m = new cg.MuscleStrain('elbow'); // tauMax 75
  let r = m.update(10, DT);               // ratio 0.13 — safe
  assert.ok(!r.tap && m.progress === 0);
  for (let i = 0; i < 120; i++) r = m.update(60, DT); // ratio 0.8 — danger
  assert.ok(m.progress > 0.2, 'progress accumulated, got ' + m.progress.toFixed(2));
  for (let i = 0; i < 600; i++) r = m.update(10, DT); // back under floor
  assert.ok(m.progress < 0.05, 'recovered, got ' + m.progress.toFixed(2));
});

test('MuscleStrain: sustained progress taps; sustained 1.6x snaps', () => {
  const tap = new cg.MuscleStrain('elbow');
  let r;
  for (let i = 0; i < 300; i++) r = tap.update(60, DT);
  assert.ok(r.tap, 'tap at progress>=1');
  const snap = new cg.MuscleStrain('elbow');
  for (let i = 0; i < 20; i++) r = snap.update(120, DT); // ratio 1.6 ≥ 1.5
  assert.ok(r.snap, 'snap after sustained over-torque');
});

test('MuscleStrain: defender escape torque reduces effective strain', () => {
  const a = new cg.MuscleStrain('elbow');
  const b = new cg.MuscleStrain('elbow');
  for (let i = 0; i < 120; i++) { a.update(60, DT, 0); b.update(60, DT, 30); }
  assert.ok(b.progress < a.progress, `escape helps ${b.progress.toFixed(2)} < ${a.progress.toFixed(2)}`);
});

/* ---- SubmissionChain (pure state machine) ---- */

test('SubmissionChain: in-band torque advances steps, out-of-band bleeds dwell', () => {
  const c = new cg.SubmissionChain('armbar');
  for (let i = 0; i < 30; i++) c.stepCombat(DT, { torqueNm: 0 }); // entry: no band
  assert.equal(c.stepId, 'isolate');
  c.stepCombat(DT, { torqueNm: 0 }); // isolate band [8,45]: 0 is out
  assert.equal(c.dwell, 0);
  for (let i = 0; i < 40; i++) c.stepCombat(DT, { torqueNm: 20 });
  assert.equal(c.stepId, 'lock');
});

test('SubmissionChain: defender escape input ends the chain', () => {
  const c = new cg.SubmissionChain('armbar');
  const r = c.stepCombat(DT, { defenderInput: 'sprawl' });
  assert.equal(r.event, 'escape');
  assert.ok(c.done);
});

test('SubmissionChain: terminal step fires tap', () => {
  const c = new cg.SubmissionChain('armbar');
  c.stepIndex = 3;
  const r = c.stepCombat(DT, {});
  assert.equal(r.event, 'tap');
});

/* ---- GrappleRig: full chains, escapes, servo contract ---- */

test('GrappleRig: armbar runs entry→isolate→lock→tap', () => {
  const rig = new cg.GrappleRig();
  assert.equal(rig.startChain('armbar'), 'entry');
  let ev = null, last;
  for (let i = 0; i < 400 && !ev; i++) { last = rig.stepCombat(DT, {}); ev = last.event; }
  assert.equal(ev, 'tap');
  assert.ok(last.progress > 0.3, 'strain accumulated: ' + last.progress.toFixed(2));
});

test('GrappleRig: all four chains reach tap', () => {
  for (const id of ['armbar', 'kimura', 'triangle', 'rear_naked_choke']) {
    const rig = new cg.GrappleRig();
    rig.startChain(id);
    let ev = null;
    for (let i = 0; i < 600 && !ev; i++) ev = rig.stepCombat(DT, {}).event;
    assert.equal(ev, 'tap', id + ' should tap');
  }
});

test('GrappleRig: escape input during isolate ends the chain', () => {
  const rig = new cg.GrappleRig();
  rig.startChain('armbar');
  for (let i = 0; i < 25; i++) rig.stepCombat(DT, {}); // past entry (0.35s)
  const r = rig.stepCombat(DT, { defenderInput: 'stack' });
  assert.equal(r.event, 'escape');
});

test('GrappleRig servo contract: null idle, targets live, null after reset', () => {
  const rig = new cg.GrappleRig();
  assert.equal(rig.getServoTargets(), null);
  rig.startChain('armbar');
  rig.stepCombat(DT, {});
  const t = rig.getServoTargets();
  assert.ok(t && t.defFore && t.defUpper, 'servo targets present');
  assert.ok(typeof t.defFore.stiffness === 'number' && typeof t.defFore.driveScale === 'number');
  rig.reset();
  assert.equal(rig.getServoTargets(), null);
});

test('ChronoGrapple facade exposes the rig API', () => {
  const g = new cg.ChronoGrapple();
  assert.ok(g.ready);
  g.startChain('kimura');
  const t = g.getServoTargets();
  assert.ok(t && t.defFore);
  g.reset();
  assert.equal(g.getServoTargets(), null);
});
