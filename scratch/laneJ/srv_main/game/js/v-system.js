/* ============================================================
   WESTERN HEART — V-System (owner-approved 2026-10-22)
   A WH-original take on Street Fighter V's V-System, Tekken-ified:
   Tekken's 4-limb inputs stay the base; the V-System layers on top
   as a resource game over the Nine-Soul meter (0-100).

   SFV grounding (community-documented mechanics):
     V-Skill   = MP+MK, per-character unique move, builds V-Gauge.
     V-Trigger = HP+HK at full gauge, timed install / power-up state.
     V-Reversal= while blocking, 1 bar, guard-cancel counter.
     V-Shift   = Season 5, HP+MK defensive shift; evade -> slow-mo
                 -> V-Shift Break counter window.

   WH mapping (Tekken-ified):
     V-Skill   = dedicated 'vskill' input (KeyV / V touch button),
                 per-character unique move, +souls on use and on hit.
     V-Trigger = 'vskill' at FULL meter (100 souls): 12s install —
                 +15% damage, chip on all blocked attacks, enhanced
                 (armored, harder-hitting) V-Skill.
     V-Reversal= 'vskill' while in blockstun: 50-soul guard-cancel
                 counter, strike-invulnerable through its active frames.
     V-Shift   = double-tap block in neutral: 0.35s invulnerable
                 backshift; evading an attack triggers 0.3x slow-mo and
                 a 1.2s V-Shift Break window (+50% damage, auto-CH).

   NAMING: all user-facing names are «name TBD» placeholders flagged
   for user approval (owner directive 2026-10-22). Code keys stay
   neutral (vskill/vtrigger/vreversal/vshift).
   ============================================================ */

/* ---- Tuning ------------------------------------------------ */
export const V = {
  SKILL_SOUL_ON_USE: 4,     // souls granted for activating a V-Skill
  TRIGGER_COST: 100,        // full Nine-Soul meter
  TRIGGER_DURATION: 12,     // seconds of install
  TRIGGER_DMG_MULT: 1.15,   // damage multiplier while triggered
  TRIGGER_CHIP_MULT: 0.25,  // blocked attacks deal 25% of damage as chip
  TRIGGER_SKILL_MULT: 1.3,  // V-Skill damage/knock multiplier while triggered
  REVERSAL_COST: 50,        // souls for a V-Reversal
  REVERSAL_STAGGER: 0.3,    // (unused: reversal is a strike, not a stun)
  PARRY_WINDOW: 0.2,        // V-Skill parry active window (12f)
  PARRY_SOUL_GAIN: 12,      // souls on a successful V-Skill parry
  PARRY_STAGGER: 0.25,      // attacker hitstun on parried attack
  SHIFT_TAP_MS: 280,        // block double-tap window for V-Shift
  SHIFT_DURATION: 0.35,     // invulnerable shift length (21f)
  SHIFT_BACK_DIST: 2.2,     // metres travelled during the shift
  SHIFT_EVADE_RANGE: 3.2,   // attacker must be this close to count as evaded
  SLOWMO_SCALE: 0.3,        // timescale during V-Shift slow-mo
  SLOWMO_DURATION: 0.8,     // real seconds of slow-mo
  BREAK_WINDOW: 1.2,        // V-Shift Break counter window (seconds)
  BREAK_DMG_MULT: 1.5,      // damage multiplier inside the break window
};

/* ---- V-Skill catalog -----------------------------------------
   Per-character unique V-Skill. kind: 'strike' | 'parry'.
   Fields mirror the fighter move shape (startup/active/recovery in
   seconds, damage on the WH 100HP scale). Fighters not listed use
   `default`. `name` carries the «name TBD» placeholder flag. */
function _strike(o) {
  return Object.assign({
    kind: 'strike', vskill: true, unblockable: false, isGrab: false,
    cost: 0, limb: 'armR', heavy: false, hitWord: 0x217,
    name: 'V-SKILL «name TBD»',
  }, o);
}

export const VSKILLS = {
  default: _strike({
    id: 'soul-palm', name: 'V-SKILL «name TBD» — Soul Palm',
    startup: 0.22, active: 0.05, recovery: 0.45,
    damage: 10, knock: 3.5, soulGain: 8,
    desc: 'A lunging soul-charged palm. Builds meter; safe-ish poke.',
  }),
  // Pantera (King/grappler): armored shoulder — the grappler's way in.
  pantera: _strike({
    id: 'iron-shoulder', name: 'V-SKILL «name TBD» — Iron Shoulder',
    startup: 0.3, active: 0.06, recovery: 0.55,
    damage: 12, knock: 5.0, soulGain: 8, armor: true, heavy: true,
    desc: 'Armored shoulder tackle. Armor through a poke, start the grab game.',
  }),
  // Dio (Akuma): fast, rude, higher damage — the demon's tax.
  dio: _strike({
    id: 'demon-lash', name: 'V-SKILL «name TBD» — Demon Lash',
    startup: 0.18, active: 0.05, recovery: 0.5,
    damage: 14, knock: 4.2, soulGain: 8,
    desc: 'A vicious backhand. Fast for a V-Skill, punished on whiff.',
  }),
  // Ryusan (Lucky Chloe): the fastest V-Skill — blink-and-miss.
  ryusan: _strike({
    id: 'vitriol-flick', name: 'V-Skill «name TBD» — Vitriol Flick',
    startup: 0.15, active: 0.04, recovery: 0.42,
    damage: 8, knock: 2.8, soulGain: 9,
    desc: 'Acid-fast flick. Builds meter quicker than anyone.',
  }),
  // Phantom (Yoshimitsu/trickster): a parry, not a strike — the
  // swordsman's answer. Catches a strike, staggers the attacker.
  phantom: Object.assign(_strike({
    id: 'moon-catch', name: 'V-SKILL «name TBD» — Moon Catch',
    startup: 0.08, active: V.PARRY_WINDOW, recovery: 0.5,
    damage: 0, knock: 0, soulGain: 4, noHitbox: true,
    desc: 'A 12f parry stance. Catch a strike: stagger them, drink their souls.',
  }), { kind: 'parry' }),
};

/** This fighter's V-Skill (default when unlisted). */
export function vskillFor(fighterId) {
  return VSKILLS[fighterId] || VSKILLS.default;
}

/** V-Trigger-enhanced V-Skill: harder, armored, meaner. */
export function vtriggerEnhance(base) {
  return Object.assign({}, base, {
    id: base.id + '-ex',
    name: base.name.replace('«name TBD»', '«name TBD» EX'),
    damage: Math.round(base.damage * V.TRIGGER_SKILL_MULT),
    knock: base.knock * V.TRIGGER_SKILL_MULT,
    armor: true,
  });
}

/** V-Reversal move template: guard-cancel counter, strike-invulnerable
    through startup+active (the fighter sets invuln to cover it). */
export function vreversalMove() {
  return {
    vskill: true, kind: 'reversal',
    id: 'v-reversal', name: 'V-REVERSAL «name TBD»',
    startup: 0.18, active: 0.08, recovery: 0.5,
    damage: 10, knock: 6.5, soulGain: 6, cost: 0,
    limb: 'armR', heavy: false, unblockable: false, isGrab: false,
    hitWord: 0x217,
    desc: 'Guard-cancel counter. Costs 50 souls. "Get off me."',
  };
}

/* ---- 'vskill' input dispatch (pure) ---------------------------
   One button, three context moves (Tekken-ified from SFV's three
   separate inputs):
     blocking in blockstun + 50 souls -> 'vreversal'
     full meter (100)                 -> 'vtrigger'
     otherwise                        -> 'vskill'                */
export function vskillDispatch({ state, stun, meter }) {
  if (state === 'block' && stun > 0.05 && meter >= V.REVERSAL_COST) return 'vreversal';
  if (meter >= V.TRIGGER_COST) return 'vtrigger';
  return 'vskill';
}

/** Should this block-press edge count as a V-Shift double-tap?
    `lastReleaseMs` = performance.now() of the previous block release
    (null when block was never released). Pure for testability. */
export function vshiftTap(lastReleaseMs, nowMs) {
  return lastReleaseMs != null && (nowMs - lastReleaseMs) <= V.SHIFT_TAP_MS;
}

/** Backshift velocity for the V-Shift (metres/sec, world x). */
export function vshiftVelocity(facing) {
  return -facing * (V.SHIFT_BACK_DIST / V.SHIFT_DURATION);
}
