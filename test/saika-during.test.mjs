// Deathfang 'saika' sweep row (docs/proof/moveset-sweep-20261028/r17-core8-failing.json):
// its input 'during Ya Otome, qcf,qcf,qcf,qcf+1+2' was 'unparsed' because the no-paren
// 'during X' canon rule's lookahead accepted only direction/button starts, not motion
// starts (qcf/qcb/hcf/hcb/dp). With the motion-start lookahead it canonicalises to the
// YA_OTOME. stance prefix — the same pattern the sweep's setup() already plays (its
// default case sets f.stance = pre) and _prepare already slots on its prefixed input,
// so the row is pressed from the Ya Otome stance on the next sweep instead of failing
// to parse. Recorded residual, not hidden: _prepare's byName maps the full KOF move name
// ('DEATHFANG_KIN_1211_SHIKI_YA_OTOME'), not 'YA_OTOME', so pressing Ya Otome itself does
// not set the YA_OTOME stance in real play — the sweep sets the stance directly, and the
// real-play entry mapping is a follow-up. No fighter data touched — shared canon only.
import test from 'node:test';
import assert from 'node:assert/strict';
import { canonNotation } from '../game/js/movesets.js';

test('during-X rows with motion-start follow-ups canonicalise to the stance prefix', () => {
  assert.equal(canonNotation('during Ya Otome, qcf,qcf,qcf,qcf+1+2'), 'YA_OTOME.qcf,qcf,qcf,qcf+1+2');
  assert.equal(canonNotation('during Ya Otome, qcf+1'), 'YA_OTOME.qcf+1');
  assert.equal(canonNotation('during Ya Otome, qcb+3'), 'YA_OTOME.qcb+3');
});

test('guards: neighbouring during/context rules unchanged', () => {
  assert.equal(canonNotation('during Bad Stomach, 1+2'), 'BAD_STOMACH.1+2');
  assert.equal(canonNotation('during Elbow Drop 1+4'), 'ELBOW_DROP.1+4');
  assert.equal(canonNotation('(During Hisenkyaku) qcf+1+2'), 'HISENKYAKU.qcf+1+2');
  assert.equal(canonNotation('(During Rage) 1,1,f,3,2'), 'R.1,1,f,3,2');
  assert.equal(canonNotation('during Ya Otome, f+1'), 'YA_OTOME.f+1');
  assert.equal(canonNotation('(During Jump) qcf+1'), 'AIR.qcf+1');
  assert.equal(canonNotation('f,n,d,d/f+1'), 'f,n,d,d/f+1');
});
