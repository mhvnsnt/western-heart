// Deathfang saika follow-up (docs/proof/moveset-sweep-20261028/r17-core8-failing.json +
// PR #1240 residual): the saika row 'during Ya Otome, qcf,qcf,qcf,qcf+1+2' canonicalises to
// the YA_OTOME. stance prefix, and the sweep sets that stance directly — but in real play
// the stance is set only from stance_after of the move just performed (fighter.js: after a
// move ends, stance = stance_after[key]), and _prepare's byName mapped the FULL KOF title
// ('DEATHFANG_KIN_1211_SHIKI_YA_OTOME'), never 'YA_OTOME' — so pressing Ya Otome itself
// never entered the YA_OTOME stance and saika was unreachable outside the sweep. The
// suffix fallback in _prepare closes that entry mapping: every move whose stateCode ends
// with '_' + the during-row's prefix enters the state. Existing stance_after entries are
// kept, and a prefix with no suffix match (WALLSTUN, a sweep setup, not a stance) gains
// nothing. The MAX Ya Otome ('YA_OTOME_MAX') is deliberately NOT matched — its name does
// not end with the state name, and no data says it enters the same state.
// This test registers a minimal moveset through the REAL registerMoveset path (which runs
// _prepare), so it fails on the unedited code and passes on the fixed code.
import test from 'node:test';
import assert from 'node:assert/strict';
import { registerMoveset, getFighterMoveset } from '../game/js/movesets.js';

function deathfangMini() {
  return { moves: {
    yaotome_a: { name: 'DEATHFANG — Kin 1211 Shiki: Ya Otome', input: 'qcf,hcb+1' },
    20: { name: 'KIN 1211 SHIKI: YA OTOME', input: 'qcf,hcb+1+2' },
    yaotome_c: { name: 'DEATHFANG — Kin 1211 Shiki: Ya Otome (MAX)', input: 'qcf,hcb+2' },
    saika: { name: 'DEATHFANG — Ura 316 Shiki: Saika', input: 'during Ya Otome, qcf,qcf,qcf,qcf+1+2' },
    badstomach: { name: 'Bad Stomach', input: '1+2' },
    badstomach_follow: { name: 'Bad Stomach Follow', input: 'during Bad Stomach, 1+2' },
  } };
}

test('Ya Otome performances enter the YA_OTOME stance', () => {
  const data = deathfangMini();
  registerMoveset('__yaotest__', data);
  const ms = getFighterMoveset('__yaotest__');
  assert.equal(ms.stance_after.yaotome_a, 'YA_OTOME');
  assert.equal(ms.stance_after['20'], 'YA_OTOME');
  assert.equal(ms.stance_after.badstomach, 'BAD_STOMACH');
});

test('guards: MAX variant not matched, existing entries kept, WALLSTUN gains nothing', () => {
  const data = deathfangMini();
  data.moves.yaotome_a = { name: 'DEATHFANG — Kin 1211 Shiki: Ya Otome', input: 'qcf,hcb+1' };
  data.stance_after = { yaotome_a: 'OTHER' };
  data.moves.wallstun_row = { name: 'Wall Stun Row', input: 'During enemy wall stun... f, hcf+1' };
  registerMoveset('__yaotest2__', data);
  const ms = getFighterMoveset('__yaotest2__');
  assert.equal(ms.stance_after.yaotome_a, 'OTHER');
  assert.equal(ms.stance_after['20'], 'YA_OTOME');
  assert.equal(ms.stance_after.yaotome_c, undefined);
  assert.equal(ms.stance_after.wallstun_row, undefined);
});
