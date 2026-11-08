/* ============================================================
   WESTERN HEART — Moveset Editor engine (2026-11-08, lane:
   moveset template library + creation system)

   The editor's DATA engine — no DOM, no rendering, node-testable.
   The in-game screen is NOT built here: the creation-suite UI is
   NON-COMPLIANT pending a teardown-sourced rebuild (RULES_NO_GUESSING
   + ui_sources gate), so this module is the engine the rebuilt
   screen will drive. It is wired into Create Fighter through
   game/js/custom-fighter.js (a saved fighter may carry
   `moveset_custom`, produced by this module).

   LAYOUT (verified sources, not invented):
   - WWE Create-A-Moveset categories are the layout spine:
     BASES, READY MOVES, GROUND, TURNBUCKLE, ROPE OPPONENT,
     AERIAL, RUNNING, DOUBLE TEAM, SPECIAL — SmackDown! vs. Raw /
     Here Comes the Pain / WWE 2K19 Create-A-Moveset flow
     (choose a category on the left, preview, add to the list).
     WWE 2K19 also contributes PRESET MOVE SETS (a whole existing
     fighter's moveset as the starting template) and fighting
     styles (Powerhouse / Cruiser / Technician / Striker / Giant).
   - Mortal Kombat 11 contributes Kustom Variations (3 ability
     slots, presets incl. tournament-legal variations) and MK
     Armageddon contributes Kreate-a-Fighter (assign already-named
     attacks to buttons; build a style from moves of all
     characters). Tekken contributes NO editor (move lists +
     practice mode only — verified) and supplies the CONTENT:
     Tekken 7 inputs + button mapping, Tekken notation.
   - Slot-conflict rule is SF6 World Tour's: no two moves on the
     same input (here: same input + position + situation).

   SLOT MODEL — every move lives in one slot:
     slot key = "position|situation|input"
     position:  game/data/moveset-library/schema.json position enum
     situation: editor categories (punish, counter-hit, wall ...),
                plain fighting situations, not claimed game data
     input:     Tekken notation. SLOT_INPUTS below is the clean
                subset of the 120 canonical inputs measured across
                the 6,909 rows in game/data/t7-frame-data/*.json
                (3,219 distinct notation_original, 2026-11-08);
                malformed artifacts (parentheses) were dropped.
                Reproduce: node -e reading t7-frame-data and
                collecting notation_original.

   ELIGIBILITY (honest, from the library schema): a move may fill
   a slot only when its position matches the slot position (or the
   move has no decoded position) AND its input matches the slot
   input, is listed in its input_slots, or is null (T3 rows carry
   input null — the #615 fidelity engine owns that decode — so a
   T3 move fills any input slot in its position, flagged as a
   warning, never presented as a decoded input).

   SOURCE LAW: the same law as game/js/moveset-library.js
   (claimed-map.json) is enforced here at assign time — a custom
   moveset may not pull from a CLAIMED Tekken bank unless the
   fighter holds an approved exception. The assembler would refuse
   it at build time; the editor refuses it at edit time, with the
   reason, instead of letting the player build something
   unplayable.

   Usage (node):
     import { createCustomMoveset, assignMove, toManifest }
       from './game/js/moveset-editor.js';
   ============================================================ */

import { checkSourceLaw } from './moveset-library.js';

export const LS_KEY = 'wh_moveset_editor_v1';

/* Positions: schema.json position enum, verbatim. apron/mounted are
   wrestling-only positions (No Mercy / WMXIX pools). */
export const POSITIONS = [
  'standing', 'crouching', 'grounded', 'back-turned',
  'sidestep-left', 'sidestep-right', 'jumping', 'running',
  'airborne', 'corner', 'apron', 'mounted',
];

/* Situations: editor categories. Plain fighting situations — not
   claimed to be any one game's data. */
export const SITUATIONS = [
  'neutral', 'punish', 'whiff-punish', 'counter-hit', 'wall-splat',
  'low-health', 'throw-attempt', 'opponent-grounded',
  'opponent-back-turned', 'round-start',
];

/* Tekken inputs, clean subset of the 120 canonical inputs measured
   in game/data/t7-frame-data (see header). */
export const SLOT_INPUTS = [
  '1', '2', '3', '4',
  '1+2', '1+3', '1+4', '2+3', '2+4', '3+4', '1+2+3+4',
  'f+1', 'f+2', 'f+3', 'f+4',
  'df+1', 'df+2', 'df+3', 'df+4',
  'd+1', 'd+2', 'd+3', 'd+4',
  'd/b+1', 'd/b+2', 'd/b+3', 'd/b+4',
  'b+1', 'b+2', 'b+3', 'b+4',
  'u+1', 'u+2', 'u+3', 'u+4',
  'u/f+1', 'u/f+2', 'u/f+3', 'u/f+4',
  'u/b+1', 'u/b+2', 'u/b+3', 'u/b+4',
  'qcf+1', 'qcf+2', 'qcf+3', 'qcf+4',
  'qcb+1', 'qcb+2', 'qcb+3', 'qcb+4',
  'hcb+1', 'hcb+2', 'hcb+3', 'hcb+4',
  '1,2', '2,1', '3,2', '1,2,1', '1+2,1',
];

/* WWE Create-A-Moveset categories (verified layout) mapped onto WH
   positions/situations. A category is a FILTER over slots, not a
   separate system — every slot still lives in the same library. */
export const WWE_CATEGORIES = [
  { id: 'bases', label: 'Bases', positions: ['standing'], situations: ['neutral', 'round-start'] },
  { id: 'ready', label: 'Ready Moves', positions: ['standing', 'crouching'], situations: ['neutral', 'punish', 'whiff-punish', 'counter-hit'] },
  { id: 'ground', label: 'Ground', positions: ['grounded'], situations: ['neutral', 'opponent-grounded'] },
  { id: 'turnbuckle', label: 'Turnbuckle', positions: ['corner'], situations: ['neutral', 'wall-splat'] },
  { id: 'rope-opponent', label: 'Rope Opponent', positions: ['corner', 'running'], situations: ['opponent-grounded', 'opponent-back-turned'] },
  { id: 'aerial', label: 'Aerial', positions: ['jumping', 'airborne'], situations: ['neutral'] },
  { id: 'running', label: 'Running', positions: ['running'], situations: ['neutral', 'whiff-punish'] },
  { id: 'double-team', label: 'Double Team', positions: ['standing', 'corner'], situations: ['opponent-grounded'] },
  { id: 'special', label: 'Special', positions: ['standing', 'crouching', 'back-turned', 'sidestep-left', 'sidestep-right'], situations: ['low-health', 'counter-hit', 'throw-attempt'] },
];

export function slotKey(position, situation, input) {
  if (!POSITIONS.includes(position)) throw new Error(`unknown position: ${position}`);
  if (!SITUATIONS.includes(situation)) throw new Error(`unknown situation: ${situation}`);
  if (!SLOT_INPUTS.includes(input)) throw new Error(`unknown input: ${input}`);
  return `${position}|${situation}|${input}`;
}

export function parseSlotKey(key) {
  const [position, situation, input] = String(key).split('|');
  if (!position || !situation || !input) throw new Error(`bad slot key: ${key}`);
  return { position, situation, input };
}

export function slotsForCategory(categoryId) {
  const cat = WWE_CATEGORIES.find((c) => c.id === categoryId);
  if (!cat) throw new Error(`unknown WWE category: ${categoryId}`);
  const out = [];
  for (const p of cat.positions) for (const s of cat.situations) for (const i of SLOT_INPUTS) out.push(`${p}|${s}|${i}`);
  return out;
}

/* ---- templates ---- */

/* A template can be the base of a custom moveset only when it has
   playable moves behind it: bank templates and pools, yes;
   frame-data-only (no anim_ref, no bank) and pending-ingest, no. */
export function canBeBaseTemplate(template) {
  return template && (template.status === 'template' || template.status === 'pool');
}

const T3_TO_DISPLAY = {
  king: 'King', paul: 'Paul Phoenix', law: 'Marshall Law', lei: 'Lei Wulong',
  yoshimitsu: 'Yoshimitsu', nina: 'Nina Williams', hwoarang: 'Hwoarang',
  xiaoyu: 'Ling Xiaoyu', eddy: 'Eddy Gordo', jin: 'Jin Kazama', julia: 'Julia Chang',
  kuma: 'Kuma', bryan: 'Bryan Fury', heihachi: 'Heihachi Mishima', ogre: 'True Ogre',
  gunjack: 'Jack', anna: 'Anna Williams', bosconovitch: 'Bosconovitch',
  gon: 'Gon', forestlaw: 'Forest Law',
};

/* A claimed T3 bank may be a template base only for the WH fighter
   who claimed it (claim.by, e.g. Pantera claims King) or for a
   fighter holding an approved exception. Anything else is refused
   here, with the reason — the assembler would refuse it anyway. */
export function canUseTemplate(template, fighterId, claimed) {
  if (!template) return { allowed: false, reason: 'no such template' };
  if (!canBeBaseTemplate(template)) {
    return { allowed: false, reason: `template ${template.id} is ${template.status} — it has no playable moves behind it yet` };
  }
  if (template.source_bank === 't3' && template.library_prefix && claimed) {
    const charSlug = template.library_prefix.split(':')[1];
    const display = T3_TO_DISPLAY[charSlug] || charSlug;
    const claim = claimed.claimed && claimed.claimed[display];
    if (claim) {
      const claimant = String(claim.by).toLowerCase();
      const exceptions = new Set((claimed.approved_exceptions || []).map((e) => String(e.fighter).toLowerCase()));
      const who = String(fighterId || '').toLowerCase();
      if (who !== claimant && !exceptions.has(who)) {
        return { allowed: false, reason: `template ${template.id} pulls from CLAIMED fighter ${display} (claimed by ${claim.by}) — refused by moveset source law` };
      }
    }
  }
  return { allowed: true, reason: '' };
}

/* ---- custom movesets ---- */

export function createCustomMoveset({ templateId, fighterId, name, templates, claimed }) {
  const template = (templates || []).find((t) => t.id === templateId);
  if (!template) throw new Error(`unknown template: ${templateId}`);
  const use = canUseTemplate(template, fighterId, claimed);
  if (!use.allowed) throw new Error(use.reason);
  return {
    schema: 'wh.custom-moveset.v1',
    fighterId: fighterId || 'custom',
    name: name || `Custom (${templateId})`,
    baseTemplate: templateId,
    /* base kit for the assembler: {bank, character} from the
       template's library_prefix (e.g. t3:hwoarang). Pool templates
       have no character — base is null and the moveset is overlays
       only. */
    base: template.library_prefix
      ? { bank: template.source_bank, character: template.library_prefix.split(':')[1] }
      : null,
    slots: {}, // slotKey -> library_id
    created: new Date().toISOString().slice(0, 10),
  };
}

/* A move may fill a slot only when position matches (or the move
   has no decoded position) AND input matches, is in input_slots,
   or is null (T3 rows: input not decoded — position-only fit). */
export function isEligible(move, slot) {
  if (!move || !slot) return false;
  const { position, input } = typeof slot === 'string' ? parseSlotKey(slot) : slot;
  if (move.position && move.position !== position) return false;
  if (move.input) {
    if (move.input === input) return true;
    if (Array.isArray(move.input_slots) && move.input_slots.includes(input)) return true;
    return false;
  }
  return true; // input null: position-only fit (flagged as a warning on assign)
}

export function listEligibleMoves(moves, slot) {
  return (moves || []).filter((m) => isEligible(m, slot));
}

export function assignMove(moveset, key, libraryId, libraryById) {
  parseSlotKey(key);
  const entry = libraryById ? libraryById.get(libraryId) : null;
  if (!entry) throw new Error(`unknown library move: ${libraryId}`);
  if (!isEligible(entry, key)) {
    throw new Error(`move ${libraryId} cannot fill slot ${key} (position ${entry.position || 'any'} / input ${entry.input || 'undecoded'})`);
  }
  const next = { ...moveset, slots: { ...moveset.slots, [key]: libraryId } };
  return next;
}

export function removeMove(moveset, key) {
  const slots = { ...moveset.slots };
  delete slots[key];
  return { ...moveset, slots };
}

export function getMove(moveset, key) {
  return (moveset.slots || {})[key] || null;
}

/* Project a custom moveset to the manifest shape the assembler
   (game/js/moveset-library.js assembleFighter) already accepts:
   base kit + overlay moves {library_id, slot}. */
export function toManifest(moveset) {
  return {
    fighter: moveset.fighterId,
    display: moveset.name,
    base: moveset.base || {},
    moves: Object.entries(moveset.slots || {}).map(([slot, library_id]) => ({ library_id, slot })),
    strings: [],
    specials: [],
  };
}

/* Validate a custom moveset against a loaded library + claimed map.
   Returns {ok, errors[], warnings[]} — never throws for bad data,
   so the UI can show every problem at once. */
export function validateMoveset(moveset, { libraryById, claimed } = {}) {
  const errors = [];
  const warnings = [];
  if (!moveset || moveset.schema !== 'wh.custom-moveset.v1') errors.push('not a wh.custom-moveset.v1 moveset');
  const slots = (moveset && moveset.slots) || {};
  for (const [key, libraryId] of Object.entries(slots)) {
    try { parseSlotKey(key); } catch { errors.push(`bad slot key: ${key}`); continue; }
    const entry = libraryById ? libraryById.get(libraryId) : null;
    if (!entry) { errors.push(`slot ${key}: unknown library move ${libraryId}`); continue; }
    if (!isEligible(entry, key)) errors.push(`slot ${key}: move ${libraryId} is not eligible for this slot`);
    if (!entry.input) warnings.push(`slot ${key}: move ${libraryId} has no decoded input — position-only fit (T3 input decode pending)`);
    if (!entry.anim_ref) warnings.push(`slot ${key}: move ${libraryId} has no anim_ref — no live preview until its bank lands`);
  }
  if (claimed && moveset) {
    const law = checkSourceLaw(toManifest(moveset), claimed);
    if (!law.passed) errors.push(...law.issues);
  }
  return { ok: errors.length === 0, errors, warnings };
}

/* ---- persistence (localStorage, same pattern as custom-fighter.js) ---- */

export function serializeMoveset(moveset) {
  return JSON.stringify(moveset);
}

export function deserializeMoveset(raw) {
  const m = typeof raw === 'string' ? JSON.parse(raw) : raw;
  if (!m || m.schema !== 'wh.custom-moveset.v1') throw new Error('not a wh.custom-moveset.v1 moveset');
  return m;
}

export function saveMoveset(moveset) {
  if (typeof localStorage === 'undefined') throw new Error('localStorage is not available here');
  localStorage.setItem(LS_KEY, serializeMoveset(moveset));
  return moveset;
}

export function loadSavedMoveset() {
  if (typeof localStorage === 'undefined') return null;
  try {
    const raw = localStorage.getItem(LS_KEY);
    return raw ? deserializeMoveset(raw) : null;
  } catch { return null; }
}
