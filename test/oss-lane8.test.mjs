// Lane 8 OSS integration tests — Node, no browser, no network.
// Run: node test/oss-lane8.test.mjs  (from the repo root)
// Exit non-zero on any failure; prints a check count on success.
import assert from 'node:assert';
import { RollbackSession } from '../game/netplay/rollback.js';
import { shouldActivateRagdoll, ragdollTriggerForState, shouldDeactivateRagdoll, RAGDOLL_TRIGGERS } from '../game/js/ragdoll.js';
import { sequence, selector, condition, action, sectionOf, dodgeForSection, pickAttacker, buildFighterBT, chooseStrategy, chooseExecution, AIPool } from '../game/js/ai-behavior.js';
import { mapByRole, retargetPose, cleanFootSlide, secondaryFollow, solveHandTarget, proceduralIdle } from '../game/js/retarget.js';
import { RIG_TYPES, resolveRig, proportionScale, mapRigBones } from '../game/js/rig-compat.js';
import { ParticleSystem, SOUL_COLORS } from '../game/js/gpu-particles.js';
import { buildSFXParams } from '../game/js/proc-audio.js';
import { CREATION_TOOL_MAP, toolForStep, creationSteps, pipelineForModel } from '../game/js/creation-tool-map.js';
import { capeChainParams, stepCapeChain } from '../game/js/cape-cloth.js';
import { traderPrompt, banterPrompt, buildChatRequest, parseChatResponse } from '../game/js/llm-npc.js';

let checks = 0;
const ok = (cond, msg) => { assert.ok(cond, msg); checks++; };

// ---------- GGPO rollback (E1) ----------
{
  // Deterministic sim: position += input each frame.
  const mkSim = () => ({ pos: 0, save() { return this.pos; }, load(s) { this.pos = s; }, step(inputs) { this.pos += inputs[0] + inputs[1]; } });
  // No-misprediction path: all inputs confirmed on time.
  const sim = mkSim();
  const s = new RollbackSession({ numPlayers: 2, inputDelay: 0, sim });
  for (let f = 0; f < 5; f++) { s.addInput(0, f, 1); s.addInput(1, f, 2); s.advance(); }
  ok(sim.pos === 15, 'rollback: on-time inputs sum to 15, got ' + sim.pos);
  ok(s.stats.rollbacks === 0, 'rollback: no rollback when predictions are right');
  // Misprediction path: frame 2 remote input predicted 0, actually 2.
  const sim2 = mkSim();
  const s2 = new RollbackSession({ numPlayers: 2, inputDelay: 0, sim: sim2 });
  for (let f = 0; f < 3; f++) { s2.addInput(0, f, 1); if (f !== 2) s2.addInput(1, f, 0); s2.advance(); }
  // Late correction for frame 2, then advance two more frames.
  ok(s2.addInput(1, 2, 2) === 'late-mispredicted', 'rollback: late mispredicted input detected');
  s2.addInput(0, 3, 1); s2.addInput(1, 3, 0); s2.advance();
  s2.addInput(0, 4, 1); s2.addInput(1, 4, 0); s2.advance();
  // Ground truth: P0 = 1 x5 = 5, P1 = 0+0+2+0+0 = 2, total 7.
  ok(sim2.pos === 7, 'rollback: after rollback+resim pos must equal ground truth 7, got ' + sim2.pos);
  ok(s2.stats.rollbacks >= 1, 'rollback: at least one rollback recorded');
  // Property test (PR #1036 gate pattern): 200 random runs, rollback
  // result must always equal a ground-truth sim fed the true inputs.
  let seed = 42;
  const rnd = () => (seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
  for (let run = 0; run < 200; run++) {
    const truth = mkSim(); const simR = mkSim();
    const sess = new RollbackSession({ numPlayers: 2, inputDelay: 0, maxRollback: 32, sim: simR });
    const N = 12, trueInputs = [];
    for (let f = 0; f < N; f++) {
      const a = Math.floor(rnd() * 3) - 1, b = Math.floor(rnd() * 3) - 1;
      trueInputs.push([a, b]);
      // Confirm player 0 on time; delay player 1's input by 3 frames sometimes.
      sess.addInput(0, f, a);
      if (f % 3 !== 0) sess.addInput(1, f, b);
      sess.advance();
    }
    for (let f = 0; f < N; f++) if (f % 3 === 0) sess.addInput(1, f, trueInputs[f][1]);
    sess.addInput(0, N, 0); sess.addInput(1, N, 0); sess.advance();
    for (const [a, b] of trueInputs) truth.step([a, b]);
    truth.step([0, 0]);
    assert.strictEqual(simR.pos, truth.pos, `rollback property run ${run}: ${simR.pos} != truth ${truth.pos}`);
    checks++;
  }
}

// ---------- Ragdoll triggers (E26/E27/E29 law) ----------
{
  ok(RAGDOLL_TRIGGERS.length === 3, 'ragdoll: exactly 3 triggers');
  for (const t of ['ko', 'launch', 'wall-splat']) ok(shouldActivateRagdoll(t), 'ragdoll: ' + t + ' activates');
  for (const e of ['idle', 'walk', 'attack', 'block', 'hit', 'throw-start', 'intro', 'win-pose', '', null, undefined, 'KO']) {
    ok(!shouldActivateRagdoll(e), 'ragdoll: ' + String(e) + ' must NOT activate');
  }
  ok(ragdollTriggerForState({ ko: true }) === 'ko', 'ragdoll: ko state maps');
  ok(ragdollTriggerForState({ launched: true }) === 'launch', 'ragdoll: launch state maps');
  ok(ragdollTriggerForState({ wallSplat: true }) === 'wall-splat', 'ragdoll: wall splat state maps');
  ok(ragdollTriggerForState({ attacking: true }) === null, 'ragdoll: attack state maps to null');
  ok(ragdollTriggerForState('bogus') === null, 'ragdoll: unknown string maps to null');
  ok(shouldDeactivateRagdoll('round-reset') && shouldDeactivateRagdoll('round-start'), 'ragdoll: deactivation events');
  ok(!shouldDeactivateRagdoll('ko'), 'ragdoll: ko is not a deactivation');
}

// ---------- Behavior tree AI (U10/U9/U8) ----------
{
  ok(sectionOf(1, 0) === 'front' && sectionOf(-1, 0) === 'back', 'ai: front/back sections');
  ok(sectionOf(0, 1) === 'right' && sectionOf(0, -1) === 'left', 'ai: left/right sections');
  ok(dodgeForSection('front') === 'roll-disengage' && dodgeForSection('back') === 'roll-close' && dodgeForSection('left') === 'sidestep', 'ai: dodge by section');
  const atk = pickAttacker([{ id: 'a', distance: 5 }, { id: 'b', distance: 2 }, { id: 'c', distance: 9 }]);
  ok(atk.id === 'b', 'ai: closest attacker only');
  ok(pickAttacker([]) === null, 'ai: no attackers -> null');
  const runBT = (ctx) => { const acts = []; buildFighterBT()({ ...ctx, act: (a) => acts.push(a) }); return acts; };
  ok(runBT({ stunned: true })[0] === 'recover', 'ai BT: stunned -> recover');
  ok(runBT({ foeAttacking: true, inRange: true, foeSection: 'front' })[0] === 'counter-roll-disengage', 'ai BT: front attack -> counter roll-disengage');
  ok(runBT({ inRange: true })[0] === 'attack', 'ai BT: in range -> attack');
  ok(runBT({})[0] === 'approach', 'ai BT: default -> approach');
  ok(sequence([condition(() => true), action(() => {})])({}) === 'success', 'ai: sequence success');
  ok(selector([condition(() => false), condition(() => true)])({}) === 'success', 'ai: selector falls through');
  ok(chooseStrategy({ hp: 0.2, meter: 1, distance: 'close', style: 'balanced' }) === 'rage-finisher', 'ai: low HP + full meter -> rage-finisher');
  ok(chooseStrategy({ hp: 0.8, meter: 0, distance: 'far', style: 'aggressive' }) === 'close-distance', 'ai: aggressive far -> close');
  const ex = chooseExecution({ difficulty: 'rookie', foeRecoveryFrames: 20 });
  ok(ex.delayFrames === 15 && ex.punishable === true, 'ai: rookie delay 15f, punishable');
  ok(chooseExecution({ difficulty: 'boss' }).delayFrames === 8, 'ai: boss delay 8f, never 0');
  const pool = new AIPool();
  pool.register('aggro', 'aggressive'); pool.register('turtle', 'defensive');
  pool.record('aggro', true); pool.record('aggro', true); pool.record('aggro', false); pool.record('turtle', false);
  ok(pool.winRate('aggro') === 2 / 3, 'ai pool: win rate');
  ok(pool.best() === 'aggro', 'ai pool: best style');
  ok(pool.names().length === 2, 'ai pool: two styles, a pool not one AI');
}

// ---------- Retargeting (U1-U6) ----------
{
  // U4 correspondence-free: no bone map, role-name matching only.
  const map = mapByRole(['Hips', 'Spine', 'Shoulder_L', 'Elbow_L', 'Wrist_L', 'Knee_R']);
  ok(map.hips === 'Hips' && map.shoulderL === 'Shoulder_L' && map.kneeR === 'Knee_R', 'retarget U4: role matching without a bone map');
  const hand = mapByRole(['a', 'b'], { hips: 'myHips' });
  ok(hand.hips === 'myHips', 'retarget: hand map wins over matching');
  // U2 non-humanoid extra roles map too.
  const beast = mapByRole(['Tail', 'Ear_L', 'Shoulder3_L']);
  ok(beast.tail === 'Tail' && beast.earL === 'Ear_L' && beast.shoulder3L === 'Shoulder3_L', 'retarget U2: beast/extra-arm roles');
  // Proportion adaptation: short-armed target scales positions down.
  const out = retargetPose({ wristL: [0, 1, 0], hips: [0, 0, 0] }, { wristL: 'w', hips: 'h' }, { wristL: 0.5 });
  ok(out.wristL[1] === 0.5 && out.hips[1] === 0, 'retarget: proportion scale applied');
  // U5 foot slide: sliding planted foot freezes; airborne foot untouched.
  const frames = [
    { ankleL: [0, 0.01, 0], ankleR: [1, 0.5, 0] },
    { ankleL: [0.3, 0.01, 0], ankleR: [1, 0.5, 0] },
    { ankleL: [0.6, 0.01, 0], ankleR: [1, -0.2, 0] },
  ];
  const clean = cleanFootSlide(frames);
  ok(clean[1].ankleL[0] === 0 && clean[2].ankleL[0] === 0, 'retarget U5: planted foot slide removed');
  ok(clean[2].ankleR[1] === 0, 'retarget U5: floor penetration clamped');
  // U5 secondary follow moves toward driver, damped.
  const f = secondaryFollow([0, 0, 0], [1, 0, 0], 0.5);
  ok(f[0] === 0.5, 'retarget U5: secondary follow damped');
  // U6 Cape guard: 0.34m target with 0.243m reach clamps, balance kept.
  const guard = solveHandTarget([0, 0, 0], [0.34, 0, 0], { maxReach: 0.243, hipsX: 0 });
  ok(!guard.reachable && Math.abs(guard.target[0] - 0.243) < 1e-9 && guard.balanced, 'retarget U6: Cape reach clamped, balance kept');
  const ok2 = solveHandTarget([0, 0, 0], [0.1, 0, 0], { maxReach: 0.243 });
  ok(ok2.reachable && ok2.target[0] === 0.1, 'retarget U6: in-reach target unclamped');
  // U3 idle: deterministic per seed, varies per seed.
  const a = proceduralIdle(7, 1.5), b = proceduralIdle(7, 1.5), c = proceduralIdle(8, 1.5);
  ok(a.breath === b.breath && a.breath !== c.breath, 'retarget U3: idle deterministic per seed, varies per seed');
}

// ---------- Rig compatibility (>=5 rig types) ----------
{
  ok(Object.keys(RIG_TYPES).length === 5, 'rig-compat: 5 rig types registered');
  const rigs = {
    // t7-160 + cape-94 lists use the REAL naming styles (Alisa
    // bonemap source names; CapeJones_Rig deform names) — the
    // full-file-derived patterns, not the guessed styles.
    't7-160': ['Hips', 'Spine', 'lPectoral', 'Neck', 'Head', 'LeftShoulder', 'LeftForeArm', 'LeftHand', 'RightShoulder', 'RightForeArm', 'RightHand', 'LeftUpLeg', 'LeftLeg', 'LeftFoot', 'RightUpLeg', 'RightLeg', 'RightFoot'],
    't3': ['hips', 'spine', 'chest', 'neck', 'head', 'shoulderl', 'elbowl', 'wristl', 'shoulderr', 'elbowr', 'wristr', 'hipl', 'kneel', 'anklel', 'hipr', 'kneer', 'ankler'],
    'cape-94': ['pelvis', 'spine_1', 'chest', 'neck_1', 'head', 'clavicle_L', 'forearm_L', 'hand_L', 'clavicle_R', 'forearm_R', 'hand_R', 'thigh_L', 'shin_L', 'foot_L', 'thigh_R', 'shin_R', 'foot_R'],
    'tripo': ['root', 'spine', 'chest', 'neck', 'head', 'left_shoulder', 'left_elbow', 'left_wrist', 'right_shoulder', 'right_elbow', 'right_wrist', 'left_hip', 'left_knee', 'left_ankle', 'right_hip', 'right_knee', 'right_ankle'],
    'custom': ['Hips', 'Spine', 'Chest', 'Neck', 'Head', 'ShoulderL', 'ElbowL', 'WristL', 'ShoulderR', 'ElbowR', 'WristR', 'HipL', 'KneeL', 'AnkleL', 'HipR', 'KneeR', 'AnkleR'],
  };
  const coreRoles = ['hips', 'spine', 'chest', 'neck', 'head', 'shoulderL', 'elbowL', 'wristL', 'shoulderR', 'elbowR', 'wristR', 'hipL', 'kneeL', 'ankleL', 'hipR', 'kneeR', 'ankleR'];
  for (const [type, bones] of Object.entries(rigs)) {
    const mapped = mapRigBones(type, bones);
    for (const role of coreRoles) ok(mapped[role], `rig-compat: ${type} maps ${role}`);
    if (type !== 'custom') ok(resolveRig(bones) === type, `rig-compat: ${type} identified, got ${resolveRig(bones)}`);
  }
  ok(resolveRig(['weird_bone_1', 'weird_bone_2']) === 'custom', 'rig-compat: unknown rig -> custom (still supported)');
  const scales = proportionScale({ wristL: 0.6, elbowL: 0.5 }, { wristL: 0.3, elbowL: 0.5 });
  ok(scales.wristL === 0.5 && scales.elbowL === 1 && Number.isFinite(scales.hips), 'rig-compat: proportion scales finite, missing -> 1');
}

// ---------- GPU particles (E30) ----------
{
  const ps = new ParticleSystem(64);
  ok(ps.burst('hit-spark', [0, 1, 0]) === 16, 'particles: hit-spark burst count');
  ok(ps.liveCount() === 16, 'particles: live count after burst');
  ps.update(2.0);
  ok(ps.liveCount() === 0, 'particles: all dead after life expiry');
  ps.burst('soul-aura', [0, 0, 0], { soul: 0, count: 5 });
  ok(ps.colors[0] === SOUL_COLORS[0][0], 'particles: soul aura color by soul index');
  ok(ParticleSystem.auraPulse(0, 0) === 1, 'particles: aura pulse at t=0 is 1');
  ok(ParticleSystem.auraPulse(Math.PI / 6, 0) > 1, 'particles: aura pulse oscillates');
  let threw = false;
  try { ps.buildPoints(null); } catch { threw = true; }
  ok(threw, 'particles: buildPoints without THREE fails clearly (browser only)');
}

// ---------- Procedural audio (E25 pattern) ----------
{
  const hit = buildSFXParams('hit', 0.9), soft = buildSFXParams('hit', 0.1);
  ok(hit.gain > soft.gain && hit.filterFreq > soft.filterFreq && hit.decay > soft.decay, 'proc-audio: intensity scales gain+brightness+decay');
  for (const k of ['hit', 'block', 'whoosh', 'soul']) ok(buildSFXParams(k, 0.5).kind === k, 'proc-audio: kind ' + k);
  let threw = false;
  try { buildSFXParams('nope'); } catch { threw = true; }
  ok(threw, 'proc-audio: unknown kind throws');
}

// ---------- Creation tool map ----------
{
  ok(creationSteps().length === 5, 'tool-map: 5 pipeline steps');
  for (const step of ['body', 'rigging', 'skin', 'import', 'export']) {
    const t = toolForStep(step);
    ok(t.tools.length > 0 && t.toolDirs.length > 0 && t.output, 'tool-map: ' + step + ' has tools + dirs + output');
  }
  ok(toolForStep('body').toolDirs.includes('tools/mb-lab'), 'tool-map: body -> tools/mb-lab (existing dir, no duplicate)');
  ok(toolForStep('body').toolDirs.includes('tools/mpfb2'), 'tool-map: body -> tools/mpfb2 (existing dir, no duplicate)');
  ok(toolForStep('export').toolDirs.includes('tools/gltfpack'), 'tool-map: export -> tools/gltfpack (existing dir, no duplicate)');
  ok(toolForStep('import').toolDirs.includes('tools/tripo-intake'), 'tool-map: import -> tools/tripo-intake (existing dir)');
  const pipe = pipelineForModel('cape-94');
  ok(pipe.length === 5 && pipe.every((p) => p.rigType === 'cape-94'), 'tool-map: pipeline carries rig type through all steps');
  let threw = false;
  try { toolForStep('bogus'); } catch { threw = true; }
  ok(threw, 'tool-map: unknown step throws');
}

// ---------- Cape cloth (E28) ----------
{
  const params = capeChainParams(5);
  ok(params.length === 5 && params[0].stiffness > params[4].stiffness, 'cape-cloth: stiffness falls root->hem');
  ok(params[0].dragForce < params[4].dragForce, 'cape-cloth: drag rises toward hem');
  const pts = [[0, 2, 0], [0, 1.5, 0], [0, 1, 0]];
  const prev = pts.map((p) => [...p]);
  // Segment length, no collider in the way.
  const next = stepCapeChain(pts, prev, [0.5, 0.5]);
  ok(next[0][0] === 0 && next[0][1] === 2, 'cape-cloth: neck anchor fixed');
  const seg = Math.hypot(next[1][0] - next[0][0], next[1][1] - next[0][1], next[1][2] - next[0][2]);
  ok(Math.abs(seg - 0.5) < 0.05, 'cape-cloth: segment length held, got ' + seg);
  // Torso collision: a point inside the sphere is pushed to its surface.
  // (Point starts off-center at distance 0.3 < radius 0.4, rest length
  // matches its anchor distance so constraints leave it alone.)
  const rest = Math.hypot(0.3, 0.8);
  const collided = stepCapeChain([[0, 2, 0], [0.3, 1.2, 0], [0.3, 0.5, 0]], [[0, 2, 0], [0.3, 1.2, 0], [0.3, 0.5, 0]], [rest, 0.7], { torsoSphere: [0, 1.2, 0, 0.4], gravity: 0 });
  const d = Math.hypot(collided[1][0] - 0, collided[1][1] - 1.2, collided[1][2] - 0);
  ok(Math.abs(d - 0.4) < 0.05, 'cape-cloth: torso collision pushes point to sphere surface, dist ' + d);
}

// ---------- Local LLM NPC (U7) ----------
{
  const tp = traderPrompt({ souls: 3, stage: 'the crossroads', inventory: ['ember'] });
  ok(tp.includes('Trader') && tp.includes('3 souls'), 'llm-npc: trader prompt carries game state');
  const bp = banterPrompt({ speaker: 'Cape Jones', foe: 'Pantera', event: 'round-start', hp: 0.5 });
  ok(bp.includes('Cape Jones') && bp.includes('Pantera'), 'llm-npc: banter prompt carries matchup');
  const req = buildChatRequest(['sys', 'user']);
  ok(req.messages.length === 2 && !('api_key' in req) && !('key' in req), 'llm-npc: request carries no keys');
  ok(parseChatResponse({ choices: [{ message: { content: '  Deal. ' } }] }) === 'Deal.', 'llm-npc: response parsed');
  ok(parseChatResponse({}) === null, 'llm-npc: empty response -> null (caller falls back to canned banter)');
}

console.log(`OSS LANE 8 TESTS: PASS (${checks} checks)`);
