/* ============================================================
   WESTERN HEART — Full move list per fighter (owner pt217u, 2026-10-23)
   "make sure they can do combos in their full move lists and everything
    that we added to them" — base Tekken moves (T8 > T7 > TTT2/T6, T3 last
   resort, as already merged into game/assets/movesets) PLUS the EMWH canon
   additions: 魂 ACTION (Spirit Action), KESSHOU, Nine-Soul Release 九魂解放,
   Reihou 霊放, Trial's Seal 試練の封 — each in 3..6 variants per fighter,
   scaled by move-list size, transformations and canon power tier.
   Every entry: notation, startup/active/recovery frames, hit level,
   damage, and cancel/combo routes. Added moves are installed into the
   live moveset (additive: never overwrites an existing slot) so the
   command interpreter (movesets.js TekkenBuffer) reaches each one by input.
   Names on screen go through tools/canon — no source-game names.
   ============================================================ */
import { canonName } from './canon-names.js';

export const SOUL_SYSTEMS = [
  { id: 'spirit',  prefix: 'SPIRIT',  en: '魂 ACTION',        ja: '魂アクション', gate: 'environment (wall / object / spot)', level: 'm', dmg: 38, f: [14, 3, 30], props: { wall: true, heavy: true } },
  { id: 'kesshou', prefix: 'KESSHOU', en: 'KESSHOU',          ja: '結晶',         gate: 'round-ending finisher',             level: 'm', dmg: 55, f: [20, 4, 40], props: { heavy: true, knockdown: true } },
  { id: 'soul9',   prefix: 'SOUL9',   en: 'NINE-SOUL RELEASE', ja: '九魂解放',     gate: 'Nine-Soul Meter full (SOUL RELEASE READY)', level: 'm', dmg: 48, f: [12, 4, 34], props: { heavy: true, launch: true } },
  { id: 'reihou',  prefix: 'REIHOU',  en: 'REIHOU',           ja: '霊放',         gate: 'opponent in rage (purifies rage)', level: 'm', dmg: 30, f: [16, 6, 28], props: { heavy: true, crumple: true, purgeRage: true } },
  { id: 'seal',    prefix: 'SEAL',    en: "TRIAL'S SEAL",     ja: '試練の封',     gate: 'final round, opponent low health (seals the verdict)', level: 'm', dmg: 60, f: [22, 4, 44], props: { heavy: true, knockdown: true, unblockable: true } },
];
// Inputs per variant slot — unique per system via its state prefix, so they never steal a base input.
export const VARIANT_BUTTONS = ['1+2', '3+4', '2+3', '1+4', '1+2+3', '2+3+4'];

/** 3..6 variants: base 3, +1 big move list, +1 huge list, +1 transformations / canon power. */
export function variantCount(ms, { transformations = 0, powerTier = 0 } = {}) {
  const n = ms && ms.moves ? Object.keys(ms.moves).length : 0;
  let v = 3;
  if (n >= 300) v++;
  if (n >= 700) v++;
  if (transformations >= 2 || powerTier >= 3 || Number(ms?.power_tier) >= 3) v++;
  return Math.min(6, v);
}

const SRC_LEAK = /\((?:T\d|TTT\d?|t\d)[^)]*\)|\b(?:t3|t7|t8|ttt2|tekken)\b/i;
/** Canon display name for a move. Canon-authored moves keep their name; imported ones go through tools/canon. */
export function displayName(fighterId, key, mv) {
  if (mv.wh_canon || mv.canon_name) return mv.canon_name || mv.name;
  const src = mv.t8_source ? 't8' : mv.t7_source ? 't7' : mv.t3_source ? 't3' : (mv.sf_source ? 'sf' : '');
  if (!src && mv.name && !SRC_LEAK.test(mv.name) && mv.move_class === 'signature') return mv.name;
  return canonName('move', `${fighterId}:${key}`, { source: src || 'base' });
}

const F = (s) => (s == null ? null : Math.round(Number(s) * 60));

/** Routes: what each move cancels / strings / juggles into (Tekken combo grammar). */
export function routeFor(notation, mv, slots) {
  const out = [];
  for (const n of Object.keys(slots)) if (n.startsWith(notation + ',') && n.split(',').length === notation.split(',').length + 1) out.push({ type: 'string', to: n });
  if (mv.launch) out.push({ type: 'juggle', to: 'air' });
  if (mv.screw) out.push({ type: 'screw', to: 'floor_bound' });
  if (mv.bound) out.push({ type: 'bound', to: 'air' });
  if (mv.heavy && !mv.launch) out.push({ type: 'wall', to: 'wall_splat' });
  return out;
}

/** Install the EMWH additions into a moveset (additive; idempotent). Returns added notations. */
export function installAddedMoves(fighterId, ms, opts = {}) {
  if (!ms || !ms.moves) return [];
  ms.slots = ms.slots || {};
  const n = variantCount(ms, opts), added = [];
  for (const sys of SOUL_SYSTEMS) {
    for (let i = 0; i < n; i++) {
      const nota = `${sys.prefix}.${VARIANT_BUTTONS[i]}`;
      const key = `wh_${sys.id}_${i + 1}`;
      if (!ms.moves[key]) {
        const t = 1 + i * 0.08; // later variants: bigger, slower, harder
        ms.moves[key] = {
          name: `${sys.en} ${i + 1}`, canon_name: `${sys.en} ${'Ⅰ Ⅱ Ⅲ Ⅳ Ⅴ Ⅵ'.split(' ')[i]}`, ja: `${sys.ja} ${i + 1}`, wh_canon: true,
          input: nota, startup: Math.round(sys.f[0] * t) / 60, active: sys.f[1] / 60, recovery: Math.round(sys.f[2] * t) / 60,
          damage: Math.round(sys.dmg * t), hit_level: sys.level, limb: i % 2 ? 'legR' : 'armR', move_class: 'soul', soul_system: sys.id,
          gate: sys.gate, knock: 3, soulGain: 0, input_slots: [nota], ...sys.props, combo_from: ['launch', 'juggle', 'wall_splat', 'crumple'],
        };
      }
      if (!ms.slots[nota]) ms.slots[nota] = key;
      if (ms._slots && !ms._slots[nota]) ms._slots[nota] = key;
      added.push(nota);
    }
  }
  return added;
}

/** Complete move list rows (base + added), canon-named, with frames, level, damage, routes. */
export function fullMoveList(fighterId, ms) {
  if (!ms || !ms.slots) return [];
  const rows = [];
  for (const [nota, key] of Object.entries(ms.slots)) {
    const mv = ms.moves[key]; if (!mv) continue;
    rows.push({
      notation: nota, key, name: displayName(fighterId, key, mv), ja: mv.ja || null,
      origin: mv.wh_canon ? 'added' : 'base', system: mv.soul_system || null, gate: mv.gate || null,
      startupF: F(mv.startup), activeF: F(mv.active), recoveryF: F(mv.recovery),
      hitLevel: mv.hit_level || mv.t7_hit_level || (mv.isGrab ? 't' : ''), damage: mv.damage || 0,
      onBlock: mv.on_block ?? null, onHit: mv.on_hit ?? null, moveClass: mv.move_class || 'strike',
      routes: routeFor(nota, mv, ms.slots),
    });
  }
  return rows;
}

/** Combo routes for the headless sim / trials: launcher -> fillers -> ender, plus soul enders. */
export function comboRoutes(ms, max = 4) {
  const slots = ms.slots, mv = (n) => ms.moves[slots[n]];
  const ok = (n) => mv(n) && mv(n).startup != null && !mv(n).isGrab;
  const launchers = Object.keys(slots).filter(n => ok(n) && mv(n).launch && !n.includes('.')).slice(0, 3);
  const fillers = ['1', '2', '1,2', '3', '4', 'd/f+1', '2,1'].filter(ok);
  const enders = Object.keys(slots).filter(n => /^(SOUL9|SPIRIT|REIHOU)\./.test(n)).slice(0, 3);
  const routes = [];
  for (const l of launchers.length ? launchers : fillers.slice(0, 1)) {
    routes.push([l, ...fillers.slice(0, 2), ...(enders[routes.length % (enders.length || 1)] ? [enders[routes.length % enders.length]] : [])]);
    if (routes.length >= max) break;
  }
  const strs = Object.keys(slots).filter(n => /^[1-4],[1-4]$/.test(n) && ok(n)).slice(0, 1);
  for (const s of strs) routes.push([s.split(',')[0], s]);
  return routes;
}

/** Which soul-system prefixes are open for this fighter right now (gates from SOUL_SYSTEMS). */
export function soulStates(f) {
  if (!f) return [];
  const g = f.game || {}, opp = f.opponent || (g.fighters ? g.fighters.find(x => x !== f) : null);
  const oppLow = opp && opp.maxHp ? opp.hp / opp.maxHp : 1;
  const out = [];
  const nearWall = typeof g.nearWall === 'function' ? g.nearWall(f) : !!(f._nearWall || f.nearWall);
  if (nearWall || f._nearObject) out.push('SPIRIT');
  if (Number(f.soul ?? f._soul ?? 0) >= Number(f.soulMax ?? f._soulMax ?? 100) || f._soulReleaseReady) out.push('SOUL9');
  if (opp && (opp._rageActive || (opp.hp > 0 && opp.hp <= opp.maxHp * 0.25 && !opp._rageUsed))) out.push('REIHOU');
  if (oppLow <= 0.2 && (g.finalRound || g.isFinalRound)) out.push('SEAL');
  if (oppLow <= 0.15) out.push('KESSHOU');
  return out;
}
