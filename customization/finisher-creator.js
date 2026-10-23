/* ============================================================
   WESTERN HEART — Create-a-Finisher (suite side)
   User-approved 2026-10-22: wire it up from the teardowns.

   From the Def Jam: Fight for NY teardown (ANIMATION-FINDINGS.md):
   - Finishers are an AUTHORDED bank of their own (BLAZIN.VIV),
     never scaled-up normals.
   - Two gates: resource (momentum/WH: Nine-Soul Meter full) +
     victim state (danger zone/WH: opponent HP <= 25%).
   - WAZA move database (676 named moves) = the vocabulary.

   This module authors a finisher as data on the suite fighter:
   F.finisher = { name, beats: [{btn|pose, dur}...],
                  meterCost: 1.0, victimHpGate: 0.25 }.
   Runtime: game/js/finisher.js. Never touches win taunts.
   ============================================================ */

export const FINISHER_GATES = {
  meterCost: 1.0,    // Nine-Soul Meter must be FULL (Def Jam: BLAZIN' mode)
  victimHpGate: 0.25, // opponent at/below 25% HP (Def Jam: red "danger" zone)
};

export const FINISHER_BEAT_BUTTONS = ['1', '2', '3', '4', '1+2', '3+4'];

/* A beat is one authored moment: a Tekken button (resolves on the
   fighter's own moveset at runtime) or a named pose, plus its time. */
export function makeBeat(btnOrPose, dur = 0.8) {
  const beat = { dur: Math.max(0.3, Math.min(3, dur)) };
  if (FINISHER_BEAT_BUTTONS.includes(btnOrPose)) beat.btn = btnOrPose;
  else if (typeof btnOrPose === 'string') beat.pose = btnOrPose;
  return beat;
}

export function makeFinisher(name, beats) {
  return {
    name: (name || 'SOUL FINISHER').toUpperCase(),
    beats: (beats || []).map((b) => (b.btn || b.pose)
      ? { btn: b.btn || null, pose: b.pose || null, dur: b.dur || 0.8 }
      : makeBeat('1')),
    meterCost: FINISHER_GATES.meterCost,
    victimHpGate: FINISHER_GATES.victimHpGate,
  };
}

export function setFighterFinisher(F, finisher) {
  if (!finisher || !Array.isArray(finisher.beats) || !finisher.beats.length) {
    delete F.finisher;
    return F;
  }
  F.finisher = finisher;
  return F;
}

/* Starter templates: authored beat skeletons the player re-times and
   re-buttons in the suite (the "create" in create-a-finisher). */
export const FINISHER_TEMPLATES = [
  { id: 'soul-rush', name: 'SOUL RUSH',
    beats: [makeBeat('1', .5), makeBeat('2', .5), makeBeat('1+2', 1.2)] },
  { id: 'nine-blows', name: 'NINE BLOWS',
    beats: [makeBeat('3', .4), makeBeat('4', .4), makeBeat('3', .4), makeBeat('3+4', 1.4)] },
  { id: 'purge', name: 'PURGE',
    beats: [makeBeat('taunt-pose', 1.0), makeBeat('2', .6), makeBeat('1+2', 1.4)] },
];
