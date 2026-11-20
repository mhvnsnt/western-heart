// Transfer T1/T3: frame-data row schema + mannequin->WH role map.
// Pure modules only; no DOM, no THREE, no game boot.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import * as F from '../game/js/frame-data-schema.js';
import * as R from '../game/js/mannequin-role-map.js';

let n = 0; const t = (name, f) => { f(); n++; };

// --- startup parsing (documented forms) ---
t('startup plain', () => assert.equal(F.parseStartup('i16'), 16));
t('startup range', () => assert.deepEqual(F.parseStartup('i30~31'), { min: 30, max: 31 }));
t('startup multi-hit', () => assert.deepEqual(F.parseStartup('i10, i23'), [10, 23]));
t('startup first frame of range', () => assert.equal(F.firstStartup(F.parseStartup('i30~31')), 30));
t('startup garbage stays null', () => assert.equal(F.parseStartup('--'), null));
t('startup numeric passthrough', () => assert.equal(F.parseStartup(13), 13));

// --- advantage parsing: states are never coerced to frames ---
t('advantage plus/minus', () => { assert.equal(F.parseAdvantage('+1'), 1); assert.equal(F.parseAdvantage('-9'), -9); });
t('advantage suffix stripped', () => { assert.equal(F.parseAdvantage('+46a'), 46); assert.equal(F.parseAdvantage('+1c'), 1); });
t('advantage KND/STUN stay null', () => { assert.equal(F.parseAdvantage('KND'), null); assert.equal(F.parseAdvantage('STUN'), null); });

// --- damage / levels / tags ---
t('damage plain list', () => assert.deepEqual(F.parseDamage('9,20'), [9, 20]));
t('damage annotated stays null', () => assert.equal(F.parseDamage('20 cs6'), null));
t('hit levels', () => assert.deepEqual(F.parseHitLevels('h,m'), ['h', 'm']));
t('tags windows', () => {
  const tags = F.parseTags('hb pc7~16 js21~29');
  assert.equal(tags.homing, true);
  assert.deepEqual(tags.powerCrush, { start: 7, end: 16 });
  assert.deepEqual(tags.jumpStatus, { start: 21, end: 29 });
  assert.equal(F.isPowerCrushActive(tags, 10), true);
  assert.equal(F.isPowerCrushActive(tags, 20), false);
  assert.equal(F.isJumpStatus(tags, 25), true);
});

// --- guard rules ---
t('guard: high whiffs croucher, low needs crouch guard', () => {
  assert.equal(F.guardOutcome('h', 'crouching'), 'whiff');
  assert.equal(F.guardOutcome('m', 'crouching'), 'blocked');
  assert.equal(F.guardOutcome('l', 'crouching'), 'blocked');
  assert.equal(F.guardOutcome('l', 'standing'), 'hit');
});

// --- row validation / normalization ---
t('row validates and normalizes', () => {
  const row = { command: 'd/f+2', hit_level: 'm', damage: '15', startup: 'i16', on_block: '-9', on_hit: 'KND', tags: 'pc7~16', recovery: 'r34' };
  assert.deepEqual(F.validateFrameRow(row), []);
  const norm = F.normalizeFrameRow(row);
  assert.equal(norm.startupF, 16); assert.equal(norm.onBlock, -9); assert.equal(norm.onHit, null);
  assert.equal(norm.recoveryF, 34); assert.equal(norm.recovery, 34 / 60); assert.deepEqual(norm.flags, []);
});
t('row with bad startup is flagged, not coerced', () => {
  const norm = F.normalizeFrameRow({ command: 'x', startup: '--' });
  assert.equal(norm.startupF, null); assert.ok(norm.flags.includes('startup_unparseable'));
});
t('punish math: -9 on block is punished by i9, not i10', () => {
  assert.equal(F.canPunish(-9, 9), true); assert.equal(F.canPunish(-9, 10), false);
  assert.equal(F.canPunish(1, 10), false);
});

// --- shipped example data is readable by the schema ---
t('example data file validates', () => {
  const url = new URL('../game/data/frame-data-schema-examples.json', import.meta.url);
  const data = JSON.parse(readFileSync(fileURLToPath(url), 'utf8'));
  assert.equal(data.schema, 'wh-frame-row/1'); assert.equal(data.fps, 60);
  assert.ok(data.rows.length >= 4);
  for (const row of data.rows) {
    assert.deepEqual(F.validateFrameRow(row), [], JSON.stringify(row));
    const norm = F.normalizeFrameRow(row);
    assert.ok(norm.startupF > 0, row.command);
  }
  const homing = F.normalizeFrameRow(data.rows.find((r) => r.command === 'SS+3'));
  assert.equal(homing.tags.homing, true); assert.equal(homing.tags.screw, true);
  assert.deepEqual(homing.damage, [18, 20]);
});

// --- mannequin -> WH roles ---
t('mannequin list is 19 bones', () => assert.equal(R.MANNEQUIN_BONES.length, 19));
t('mannequin pose maps 16 roles, root separate, upper arms unmapped-not-dropped', () => {
  const pose = Object.fromEntries(R.MANNEQUIN_BONES.map((b) => [b, [0, 0, 0]]));
  const { roles, root, unmapped } = R.mannequinPoseToRoles(pose);
  assert.equal(Object.keys(roles).length, R.MAPPED_ROLE_COUNT);
  assert.equal(roles.hips, pose.Hip); assert.equal(roles.spine, pose.Spine1);
  assert.equal(roles.elbowL, pose.L_ForeArm); assert.equal(roles.wristR, pose.R_Hand);
  assert.equal(roles.ankleL, pose.L_Foot); assert.equal(root, pose.BASE);
  assert.deepEqual(Object.keys(unmapped).sort(), ['L_Arm', 'R_Arm']);
});
t('unknown bone is reported, not dropped silently', () => {
  const { unmapped } = R.mannequinPoseToRoles({ NopeBone: [1, 2, 3] });
  assert.equal(unmapped.NopeBone.reason, 'unknown-bone');
});

// --- 23-bone clip shape ---
t('clip23 validates shape and spike-filters rotations, not root', () => {
  const frame = () => Array.from({ length: 23 }, () => [0, 0, 0]);
  const f0 = frame(), f1 = frame(); f1[2][0] = 2.0; f1[0][0] = 500; // spike on bone 2, root mm move
  const clip = { frames: [f0, f1] };
  assert.deepEqual(R.validateClip23(clip), []);
  assert.deepEqual(R.validateClip23({ frames: [Array.from({ length: 19 }, () => [0, 0, 0])] }).length > 0, true);
  const { clip: filtered, spikesFiltered } = R.spikeFilterClip23(clip);
  assert.equal(spikesFiltered, 1);
  assert.equal(filtered.frames[1][2][0], 0); // held at previous frame
  assert.equal(filtered.frames[1][0][0], 500); // root untouched
  assert.deepEqual(R.clip23RootMetres(filtered.frames[1])[0][0], 0.5);
});

console.log(`frame-data-schema.test: ${n} passed`);
