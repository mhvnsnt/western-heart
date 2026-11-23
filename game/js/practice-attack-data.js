/* practice-attack-data.js — the practice-mode ATTACK DATA readout, and nothing in a normal fight.

   Owner 2026-11-11: "stop adding stuff into the actual fights and combat that are only for debug and practice type
   shit like how much damage a hit is giving popping up big across the screen ... even if it did happen in practice u
   should do it like Tekken ... straight from the games source files".

   What the reference game's own files say (Tekken 7 Steam exe, TekkenGame-Win64-Shipping.exe strings, read
   2026-11-11; see docs/research/2026-11-11-in-fight-hud.md):
   - The battle HUD movie (SW_UI_HUD) carries life gauges, round counters, timer, names, rank, rage and the
     side gauges, plus net/wins counters. It has NO hit counter, NO damage number and NO hit-type text.
   - Hit data lives in its own movie, SW_UI_AttackData, driven by SwfAttackData::exec and labelled with the
     practice-mode message ids prc_573..prc_581. Per side (AttackData_L_mc / AttackData_R_mc) it has exactly
     these fields, each with a _Glow state for the value that just changed:
       TotalDamage, MaxComboDamage, Damage, HitCombo, ComboDamage   (numbers)
       CleanHit, CounterHit, WallHit, Punish                        (lamps)
   - Frame data is a separate practice movie too (SW_UI_Practice_Frames).
   So: a normal fight shows none of it; practice shows this panel, these fields, on the attacker's side.

   Field meanings used here (never invented data: a lamp the move data cannot support stays dark):
     Damage          this hit's damage (a blocked hit: its chip, usually 0)
     ComboDamage     damage of the current combo (hits counted by Fighter.registerCombo's window)
     HitCombo        hits in the current combo
     MaxComboDamage  best ComboDamage since practice started
     TotalDamage     all damage this side has dealt since practice started
     CounterHit      the hit landed as a counter hit (game.js result === 'counter')
     WallHit         the hit's reaction is a wall splat (combat-systems.js reactionFor)
     Punish          the defender was in the recovery of an attack that had just been blocked
     CleanHit        the move carries a clean-hit property (no move data does yet, so it stays dark) */

export const ATTACK_DATA_FIELDS = ['damage', 'comboDamage', 'hits', 'maxComboDamage', 'totalDamage'];
export const ATTACK_DATA_LAMPS = ['clean', 'counter', 'wall', 'punish'];

export function newAttackDataSide() {
  return { damage: 0, comboDamage: 0, hits: 0, maxComboDamage: 0, totalDamage: 0,
    clean: false, counter: false, wall: false, punish: false, changed: [] };
}

/* Pure update of one side's readout. ev: { kind: 'hit' | 'counter' | 'ko' | 'throw' | 'block', dealt, combo,
   clean, wall, punish }. Returns the same object with `changed` = the fields that glow this time. */
export function recordAttackData(s, ev) {
  const dealt = Math.max(0, Math.round(Number(ev.dealt) || 0));
  const before = { ...s };
  if (ev.kind === 'block') {
    s.damage = dealt;
    s.comboDamage = 0; s.hits = 0;
    s.clean = s.counter = s.wall = s.punish = false;
    s.totalDamage += dealt;
  } else {
    const hits = Math.max(1, ev.combo | 0);
    s.damage = dealt;
    s.comboDamage = hits <= 1 ? dealt : s.comboDamage + dealt;
    s.hits = hits;
    s.maxComboDamage = Math.max(s.maxComboDamage, s.comboDamage);
    s.totalDamage += dealt;
    s.clean = !!ev.clean;
    s.counter = ev.kind === 'counter';
    s.wall = !!ev.wall;
    s.punish = !!ev.punish;
  }
  s.changed = [...ATTACK_DATA_FIELDS, ...ATTACK_DATA_LAMPS].filter((k) => s[k] !== before[k] || (k === 'damage' && ev.kind !== 'block'));
  return s;
}

/* Which attack, and which USE of it: move objects are shared between uses (fighter.attack = the move definition),
   so the use is told apart by the clock time its state began (fighter._clock - fighter.stateT is constant while
   one state lasts). */
export function attackUse(f) {
  if (!f || !f.attack) return null;
  return { attack: f.attack, start: (Number(f._clock) || 0) - (Number(f.stateT) || 0) };
}

/* game.js block branch: remember the attacker's blocked attack use. */
export function markBlocked(attacker) {
  if (attacker) attacker._adBlocked = attackUse(attacker);
}

/* The defender was punished: hit while still recovering from that same blocked attack use. */
export function isPunish(defender) {
  if (!defender || defender.state !== 'attack' || defender._attackPhase !== 'recovery') return false;
  const b = defender._adBlocked, u = attackUse(defender);
  return !!(b && u && b.attack === u.attack && Math.abs(b.start - u.start) < 1e-6);
}

/* game.js entry point. Does nothing outside practice (game.training): a normal fight shows no hit data at all. */
export function practiceAttackData(game, attacker, defender, dealt, ev) {
  if (!game || !game.training || !attacker) return null;
  const side = attacker === game.p2 ? 'p2' : 'p1';
  const st = game._attackDataState || (game._attackDataState = { p1: newAttackDataSide(), p2: newAttackDataSide() });
  const s = recordAttackData(st[side], { ...ev, dealt });
  const ui = game.ui;
  if (ui && typeof ui.attackData === 'function') ui.attackData(side, s);
  return s;
}

/* Clear both readouts (match start). Safe on stub UIs. */
export function resetPracticeAttackData(game) {
  if (!game) return;
  game._attackDataState = null;
  const ui = game.ui;
  if (ui && typeof ui.attackDataClear === 'function') ui.attackDataClear(!!game.training);
}
