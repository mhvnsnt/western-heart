/* Headless test for tekken-wiring-brick.js — Coordinator lane 3/4.
 * Run: node tekken-wiring-brick-test.cjs  (exit 0 = ALL PASS)
 * Asserts counts against the manifest, that every clip refuses
 * playability with the right reasons, that unknown/KoC2 ids refuse,
 * and that the sampled ground-truth rows (R127, T7 DVD, DW nage_y)
 * carry the exact flags the audit records. No match is played here;
 * the test proves the refusal, not a playback.
 */
'use strict';
var b = require('./tekken-wiring-brick.js');
var pass = 0;
function check(name, cond) {
  if (!cond) { console.log('FAIL: ' + name); process.exitCode = 1; return; }
  pass++;
  console.log('PASS ' + pass + ': ' + name);
}

var v = b.validateTekkenBrick();
check('brick validates clean (383 clips)', v.ok === true);
check('counts 230 T3 / 96 T7 / 54 DW / 3 MADE',
  v.bySource.tekken3 === 230 && v.bySource.tekken7 === 96 &&
  v.bySource.tekken5_dw === 54 && v.bySource.western_heart_made === 3);
check('verdicts 361 blocked / 14 truncated / 5 not-a-move / 3 adaptation',
  v.verdicts.BLOCKED_NO_RECEIVER === 361 && v.verdicts.BLOCKED_TRUNCATED === 14 &&
  v.verdicts.NOT_A_MOVE === 5 && v.verdicts.ADAPTATION === 3);

var r127 = b.lookupTekkenClip('T3_KING_R127');
check('R127 exists, T3 throw clip, truncated before contact',
  !!r127 && r127.source === 'tekken3' && r127.isThrowClip === true &&
  r127.truncatedBeforeContact === true && r127.verdict === 'BLOCKED_TRUNCATED');
check('R127 refuses with G2+G3+G4+G5 reasons',
  (function () {
    var r = b.isPlayableTekkenClip('T3_KING_R127');
    return r.playable === false && r.reasons.indexOf('G2 no receiver') !== -1 &&
      r.reasons.indexOf('G5 truncated before contact') !== -1;
  })());

var t7 = b.lookupTekkenClip('T7_KING_mokg_tkr_DVD');
check('T7 spike-exception clip exists, T7, pair lead names King .tkmvst receiver 554',
  !!t7 && t7.source === 'tekken7' && t7.spikeException === true &&
  typeof t7.pairLead === 'string' && t7.pairLead.indexOf('554') !== -1);

var dw = b.lookupTekkenClip('T5DW_PANTERA_ikdv_36_nage_y');
check('DW clip exists, DW, spike exception, blocked-no-receiver',
  !!dw && dw.source === 'tekken5_dw' && dw.spikeException === true &&
  dw.verdict === 'BLOCKED_NO_RECEIVER');

var made = b.lookupTekkenClip('MADE_PANTERA_battle_itself');
check('MADE clip flagged adaptation, not decoded motion',
  !!made && made.madeAdaptation === true && made.verdict === 'ADAPTATION' &&
  b.isPlayableTekkenClip('MADE_PANTERA_battle_itself').reasons.join(' ').indexOf('not decoded motion') !== -1);

var beam = b.lookupTekkenClip('T5DW_PANTERA_ikdv_beam');
check('non-wrestling beam clip is NOT_A_MOVE',
  !!beam && beam.nonWrestling === true && beam.verdict === 'NOT_A_MOVE');

check('every one of the 383 refuses playable',
  b.TEKKEN_CLIPS.every(function (c) { return b.isPlayableTekkenClip(c.id).playable === false; }));
check('unknown Tekken id returns null / refuses',
  b.lookupTekkenClip('T3_KING_R999') === null &&
  b.isPlayableTekkenClip('T3_KING_R999').playable === false);
check('VPW2/KoC2 ids are not Tekken clips (null)',
  b.lookupTekkenClip('VPW2_2FED') === null && b.lookupTekkenClip('KOC2_00001') === null);
check('KoC2 motion lookup always MISSING, 0 clips',
  (function () {
    var r = b.lookupKoC2Motion('anything');
    return r.status === 'MISSING' && r.clips === 0;
  })());
check('KoC2 state records the 0x1189B8 correction and next functions',
  b.KOC2_STATE.decodedClips === 0 && b.KOC2_STATE.mvsFiles === 16660 &&
  b.KOC2_STATE.xrefCorrection.indexOf('0x3a8be0') !== -1 &&
  b.KOC2_STATE.nextFunctions.indexOf('0x30cf80') !== -1);

console.log(pass === 14 ? 'ALL PASS: 14 tests, exit 0' : 'FAILURES PRESENT: ' + pass + '/14 passed');
