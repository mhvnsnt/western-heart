/* ============================================================
   WESTERN HEART — Wrestling-sim CPU logic tables (transfer F1-F12)
   Pure, headless-testable. No DOM, no THREE, no fighter handles.
   Complements (does not replace) game/js/ai/cpu-personality.js:
   that module resolves an archetype + a flat option table; this
   module is the position x damage-phase table the wrestling sim
   needs, with priority chains, personality sliders, family ratings,
   stamina/spirit resources, part endurance, traits and the
   critical-spike event — each as data the game reads, not as
   hard-coded behaviour.

   SOURCE (docs only): the documented shape of a wrestling sim's
   edit record — five sections (profile/skills, appearance,
   parameters, moveset, CPU logic), percentage tables per position
   columned by opponent damage phase, personality sliders, priority
   chains (up to 10), a moveset slotted by position, paired
   offense/defense ratings per move family, stamina (breath) and
   spirit as separate resources, per-part endurance, one
   point-bought passive trait per fighter, and a move-class-based
   critical-spike event that leaves the opponent in a "critical"
   damage state the phase tables can read.
   Nothing here copies a source game's numbers, names or tuning:
   - Phase thresholds below are WH tuning (the source docs name
     the phases, not numeric thresholds).
   - Affinity cost multipliers are WH tuning (the source docs say
     affinity grades stamina cost, not by how much).
   - Critical base rates are caller-supplied WH tuning: this module
     never invents a base rate, it only applies caller-supplied
     trait/state multipliers and clamps to [0,1].
   - Trait costs use the documented 15-35 point range as a
     validation range only; WH traits themselves are re-authored
     (see game/data/wrestling-sim-example.json).
   ============================================================ */

export const DAMAGE_PHASES = Object.freeze(['small', 'medium', 'large', 'critical']);
/** Positions a wrestling moveset is slotted by (transfer F5). */
export const POSITIONS = Object.freeze([
  'standing', 'frontGrappleSmall', 'frontGrappleMedium', 'frontGrappleBig',
  'backGrapple', 'groundHead', 'groundLegs', 'corner', 'diving', 'running',
  'counter', 'finisher',
]);
export const MAX_PRIORITY_CHAINS = 10;
/** Move families with paired offense/defense ratings (transfer F6). */
export const FAMILIES = Object.freeze([
  'punch', 'kick', 'throw', 'joint', 'stretch', 'power', 'flying', 'agility', 'arm', 'body',
]);
/** Personality sliders, 0-100 (transfer F2). */
export const SLIDERS = Object.freeze(['showmanship', 'discretion', 'flexibility', 'ukemi']);
/** Style-affinity grades: A = most on-style, E = least (transfer F3 note in teardown §3). */
export const AFFINITY_GRADES = Object.freeze(['A', 'B', 'C', 'D', 'E']);
/** WH tuning: stamina-cost multiplier per affinity grade (documented shape, WH numbers). */
export const AFFINITY_COST = Object.freeze({ A: 0.8, B: 0.9, C: 1.0, D: 1.15, E: 1.3 });

/**
 * Opponent damage phase from damage taken (0..1) and a critical flag.
 * WH tuning thresholds: <1/3 small, <2/3 medium, else large; a critical
 * state always reads as the fourth column, whatever the damage total.
 */
export function phaseOf(damageTaken01, critical = false) {
  if (critical) return 'critical';
  const d = Math.max(0, Math.min(1, +damageTaken01 || 0));
  return d < 1 / 3 ? 'small' : d < 2 / 3 ? 'medium' : 'large';
}

/** Validate a slider set: every slider present, numeric, 0-100. Returns problems. */
export function validateSliders(sliders) {
  const problems = [];
  if (!sliders || typeof sliders !== 'object') return ['sliders not an object'];
  for (const s of SLIDERS) {
    const v = sliders[s];
    if (typeof v !== 'number' || !Number.isFinite(v) || v < 0 || v > 100) problems.push(`slider ${s} out of 0-100: ${v}`);
  }
  return problems;
}

/** Normalize sliders (missing -> 50, clamped to 0-100). */
export function normalizeSliders(sliders = {}) {
  const out = {};
  for (const s of SLIDERS) {
    const v = sliders[s];
    out[s] = typeof v === 'number' && Number.isFinite(v) ? Math.max(0, Math.min(100, v)) : 50;
  }
  return out;
}

/**
 * Validate a CPU table: { position: { phase: { moveId: weight } } }.
 * Weights must be finite numbers >= 0; unknown positions/phases are problems.
 * A position may omit phases (the resolver falls back to 'small' then any phase).
 */
export function validateCpuTable(table) {
  const problems = [];
  if (!table || typeof table !== 'object') return ['cpu table not an object'];
  for (const [pos, byPhase] of Object.entries(table)) {
    if (!POSITIONS.includes(pos)) { problems.push(`unknown position: ${pos}`); continue; }
    if (!byPhase || typeof byPhase !== 'object') { problems.push(`position ${pos}: not an object`); continue; }
    for (const [phase, row] of Object.entries(byPhase)) {
      if (!DAMAGE_PHASES.includes(phase)) { problems.push(`position ${pos}: unknown phase ${phase}`); continue; }
      if (!row || typeof row !== 'object') { problems.push(`position ${pos}/${phase}: not an object`); continue; }
      for (const [move, w] of Object.entries(row)) {
        if (typeof w !== 'number' || !Number.isFinite(w) || w < 0) problems.push(`position ${pos}/${phase}/${move}: bad weight ${w}`);
      }
    }
  }
  return problems;
}

/** Weighted pick from a { moveId: weight } row. rng injectable. Returns moveId or null. */
export function pickWeighted(row, rng = Math.random) {
  const entries = Object.entries(row || {}).filter(([, w]) => w > 0);
  const total = entries.reduce((t, [, w]) => t + w, 0);
  if (!total) return null;
  let r = rng() * total;
  for (const [move] of entries) { r -= row[move]; if (r < 0) return move; }
  return entries[entries.length - 1][0];
}

/**
 * Resolve one CPU pick: position table -> phase column -> weighted pick,
 * with personality applied as documented behaviour only:
 * - showmanship scales the weight of 'taunt' options (corner showboating).
 * - ukemi does not change the pick; it is returned as a reversal
 *   tendency (0..1) for the caller (reversal system) to use.
 * Returns { move, position, phase, ukemi } or { move: null, ... }.
 */
export function resolveCpuPick(table, position, phase, sliders = {}, rng = Math.random) {
  const byPhase = (table && table[position]) || {};
  const row = byPhase[phase] || byPhase.small || Object.values(byPhase)[0] || {};
  const s = normalizeSliders(sliders);
  const adjusted = { ...row };
  if (adjusted.taunt !== undefined) adjusted.taunt = adjusted.taunt * (0.5 + s.showmanship / 100);
  return { move: pickWeighted(adjusted, rng), position, phase, ukemi: s.ukemi / 100 };
}

/**
 * Validate priority chains (transfer F3): at most 10, each with a trigger
 * move, a follow-up move, and per-phase follow-up percentages 0-100.
 */
export function validatePriorityChains(chains) {
  const problems = [];
  if (!Array.isArray(chains)) return ['priority chains not an array'];
  if (chains.length > MAX_PRIORITY_CHAINS) problems.push(`too many priority chains: ${chains.length} > ${MAX_PRIORITY_CHAINS}`);
  chains.forEach((c, i) => {
    if (!c || typeof c !== 'object') { problems.push(`chain ${i}: not an object`); return; }
    if (!c.trigger) problems.push(`chain ${i}: missing trigger`);
    if (!c.followUp) problems.push(`chain ${i}: missing followUp`);
    for (const phase of DAMAGE_PHASES) {
      const v = c.perPhase && c.perPhase[phase];
      if (v !== undefined && (typeof v !== 'number' || v < 0 || v > 100)) problems.push(`chain ${i}/${phase}: bad percentage ${v}`);
    }
  });
  return problems;
}

/**
 * Priority resolution: when `triggerMove` just landed, roll the chain's
 * percentage for the current phase (default: the chain's phase value,
 * else 0 — a chain with no percentage for this phase never fires).
 * Returns the follow-up move id, or null. rng injectable; rng() < pct/100 fires.
 */
export function resolvePriority(chains, triggerMove, phase, rng = Math.random) {
  for (const c of chains || []) {
    if (c.trigger !== triggerMove) continue;
    const pct = c.perPhase ? (c.perPhase[phase] ?? 0) : 0;
    return rng() * 100 < pct ? c.followUp : null;
  }
  return null;
}

/** Validate a moveset-by-position slot table (transfer F5). */
export function validateMovesetSlots(slots) {
  const problems = [];
  if (!slots || typeof slots !== 'object') return ['moveset slots not an object'];
  for (const [pos, move] of Object.entries(slots)) {
    if (!POSITIONS.includes(pos)) problems.push(`unknown slot position: ${pos}`);
    if (move !== null && typeof move !== 'string') problems.push(`slot ${pos}: move must be a string id or null`);
  }
  return problems;
}

/** Move id slotted at `position`, or null when the slot is empty/unfilled. */
export function moveForSlot(slots, position) {
  return (slots && slots[position]) || null;
}

/** Validate paired offense/defense ratings per family (transfer F6). */
export function validateFamilyRatings(ratings) {
  const problems = [];
  if (!ratings || typeof ratings !== 'object') return ['family ratings not an object'];
  for (const [fam, pair] of Object.entries(ratings)) {
    if (!FAMILIES.includes(fam)) { problems.push(`unknown family: ${fam}`); continue; }
    if (!pair || typeof pair.offense !== 'number' || typeof pair.defense !== 'number') {
      problems.push(`family ${fam}: needs numeric offense and defense`);
    }
  }
  return problems;
}

/** WH tuning: family matchup multiplier from offense vs defense (clamped, never negative). */
export function familyMultiplier(offense, defense) {
  return Math.max(0.5, Math.min(1.5, 1 + ((+offense || 0) - (+defense || 0)) * 0.05));
}

/** Stamina cost of a move: base cost scaled by affinity grade (WH tuning multipliers). */
export function staminaCost(baseCost, affinity = 'C') {
  return (+baseCost || 0) * (AFFINITY_COST[affinity] ?? 1.0);
}

/** Create the two-resource fight state (transfer F7): stamina (breath) + spirit, separate. */
export function createResources({ stamina = 100, spirit = 100 } = {}) {
  return { stamina, spirit, parts: {} };
}

/** Apply stamina/spirit deltas, clamped to [0,100]. Returns the new state (mutates the passed object). */
export function applyResourceDelta(res, { stamina = 0, spirit = 0 } = {}) {
  res.stamina = Math.max(0, Math.min(100, res.stamina + stamina));
  res.spirit = Math.max(0, Math.min(100, res.spirit + spirit));
  return res;
}

/** Set per-part endurance (transfer F7): { part: 0..100 }. Damage a part; exhausted = 0. */
export function damagePart(res, part, amount) {
  const cur = res.parts[part] ?? 100;
  res.parts[part] = Math.max(0, cur - (+amount || 0));
  return res.parts[part];
}
export function partExhausted(res, part) { return (res.parts[part] ?? 100) <= 0; }

/**
 * Validate a WH-authored trait (transfer F8): one point-bought passive per
 * fighter, with a trigger and an effect from the documented shapes.
 * Cost is validated against the documented 15-35 point range.
 */
export const TRAIT_TRIGGERS = Object.freeze(['low-stamina', 'low-spirit', 'first-finisher', 'on-reversal', 'high-stamina', 'opponent-critical']);
export const TRAIT_EFFECTS = Object.freeze(['finisher-boost', 'rise-faster', 'no-sell', 'attack-boost', 'critical-boost', 'submission-resist']);
export function validateTrait(trait) {
  const problems = [];
  if (!trait || typeof trait !== 'object') return ['trait not an object'];
  if (!trait.id) problems.push('trait missing id');
  if (!TRAIT_TRIGGERS.includes(trait.trigger)) problems.push(`unknown trait trigger: ${trait.trigger}`);
  if (!TRAIT_EFFECTS.includes(trait.effect)) problems.push(`unknown trait effect: ${trait.effect}`);
  if (typeof trait.cost !== 'number' || trait.cost < 15 || trait.cost > 35) problems.push(`trait cost out of 15-35: ${trait.cost}`);
  return problems;
}

/**
 * Critical-spike event (transfer F9): baseRate is caller-supplied WH tuning
 * (no base rate is documented in the source docs, so none is invented here).
 * Trait modifiers are generic multipliers carried on the trait record
 * ({ criticalMultiplier }); low-stamina reversal doubles the rate only
 * when the caller passes that documented modifier shape explicitly.
 * Returns { rolled, chance } with chance clamped to [0,1]; when rolled,
 * the caller sets the opponent's damage phase to 'critical' via phaseOf(..., true).
 */
export function criticalChance(baseRate, { traits = [], lowStaminaReversal = false } = {}, rng = Math.random) {
  let chance = +baseRate || 0;
  for (const tr of traits) if (tr && typeof tr.criticalMultiplier === 'number') chance *= tr.criticalMultiplier;
  if (lowStaminaReversal) chance *= 2;
  chance = Math.max(0, Math.min(1, chance));
  return { rolled: rng() < chance, chance };
}

/**
 * Validate the one-record fighter file (transfer F12): the five sections
 * of the edit record, each validated by its own validator above.
 * Appearance is data (parts list), not validated for geometry here.
 */
export function validateFighterRecord(rec) {
  const problems = [];
  if (!rec || typeof rec !== 'object') return ['fighter record not an object'];
  for (const sec of ['profile', 'appearance', 'parameters', 'moveset', 'cpuLogic']) {
    if (!(sec in rec)) problems.push(`missing section: ${sec}`);
  }
  if (rec.parameters) problems.push(...validateFamilyRatings(rec.parameters).map((p) => `parameters: ${p}`));
  if (rec.moveset) problems.push(...validateMovesetSlots(rec.moveset).map((p) => `moveset: ${p}`));
  if (rec.cpuLogic) {
    if (rec.cpuLogic.table) problems.push(...validateCpuTable(rec.cpuLogic.table).map((p) => `cpuLogic.table: ${p}`));
    if (rec.cpuLogic.sliders) problems.push(...validateSliders(rec.cpuLogic.sliders).map((p) => `cpuLogic.sliders: ${p}`));
    if (rec.cpuLogic.priority) problems.push(...validatePriorityChains(rec.cpuLogic.priority).map((p) => `cpuLogic.priority: ${p}`));
    if (rec.cpuLogic.traits) rec.cpuLogic.traits.forEach((tr) => problems.push(...validateTrait(tr).map((p) => `cpuLogic.traits: ${p}`)));
  }
  return problems;
}
