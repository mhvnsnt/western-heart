/* Hit-feel tuning params — the review stage's training-mode tuner.
 *
 * The user NEVER builds numbers from zero: these are the current wired values
 * (Tekken teardown numbers come from the retargeting lane; the tuner shows the
 * base and lets the user nudge it). Each param is a MULTIPLIER (delta) applied
 * on top of the wired value: 1.0 = untouched.
 *
 * Game applies them in game.js (hitstop, camera shake) and fighter.js
 * (knockback, launch) off game.feel. The tuner writes game.feel live.
 */
export const FEEL_PARAMS = [
  {
    key: 'hitstop', label: 'Hitstop', unit: 'x', min: 0, max: 2, step: 0.05, def: 1,
    baseNote: 'wired: KO/heavy 0.12s, throw 0.10s, grab 0.06s, block 0.04s, strike 0.05-0.10s',
  },
  {
    key: 'shake', label: 'Camera shake', unit: 'x', min: 0, max: 2, step: 0.05, def: 1,
    baseNote: 'wired: KO 0.50/0.40, throw 0.45/0.28, grab 0.30/0.20, strike 0.18-0.45',
  },
  {
    key: 'knockback', label: 'Knockback', unit: 'x', min: 0, max: 2, step: 0.05, def: 1,
    baseNote: 'wired: per-move move.knock (vx = dir x knock); KO blowback 5.5',
  },
  {
    key: 'launch', label: 'Launch height', unit: 'x', min: 0, max: 2, step: 0.05, def: 1,
    baseNote: 'wired: launcher vy 4.6 (grab 5.2); KO vy 6.0',
  },
];

export function feelPatch({ fighter, values, notes }) {
  const changes = [];
  const tune = {};
  let touched = false;
  for (const p of FEEL_PARAMS) {
    const v = values[p.key] ?? 1;
    tune[p.key] = v;
    if (v !== 1) touched = true;
  }
  if (!touched) return null;
  changes.push({ kind: 'hitfeel_tune', ...tune, note: notes || '' });
  return {
    format: 'wh-tweak-patch',
    version: 1,
    kit_id: null,
    fighter,
    attire: 'default',
    exported_at: new Date().toISOString().replace(/\.\d+Z$/, 'Z'),
    exported_by: 'suite',
    suite_build: '',
    notes: notes || '',
    changes,
  };
}
