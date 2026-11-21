/* ============================================================
   WESTERN HEART — Moveset Editor engine (2026-11-20, skeleton rebuild)

   The editor's DATA engine — no DOM, no rendering, node-testable.
   Rebuilt from the 2026-11-08 engine per EDITOR-SPEC §3
   (~/workspace/_wh-moveset-creator-20261120/lane-c-design/EDITOR-SPEC.md),
   on Lane A (TAXONOMY.md) + Lane B (FRONTEND.md) ground truth.

   WHAT CHANGED IN THE REBUILD (old file kept no ground truth here):
   - POSITIONS are the engine's own resolver prefix list (A §3a/§3b,
     movesets.js _pressV2 order), NOT the old corner/apron/mounted
     words. The old
     words 'corner', 'apron', 'mounted', 'jumping', 'sidestep-left/right'
     are NOT data prefixes (A §3d, A §8.13) and are REMOVED — a slot
     whose notation carries one is refused by validateNotation().
   - The slot key is a PLAIN RESOLVER NOTATION ("1", "WS.1", "BT.2",
     "FC.d/f+1") — the same keys the loadout and the file's `slots` dict
     use (A §1g). The old "position|situation|input" key format is
     RETIRED; legacy '|' keys are migrated on read (migrateDocSlots),
     never written. SITUATIONS + WWE_CATEGORIES (filters over the old
     words) are removed with it.
   - The save is a NAMED-DOCUMENT STORE (EDITOR-SPEC §3b/§3c): one
     wh.custom-moveset.v1 document per custom moveset under
     wh_moveset_editor_v1, {version:1, movesets:{name:doc}, applied:{}}.
     A named moveset becomes playable ONLY by compiling into the LIVE
     loadout wh_moveset_loadout_v1 via setLoadoutSlot() + __base
     (compileToLoadout) — the loadout is the only thing a fight reads
     (B §6.1). moveset_custom on the fighter save is an
     applied-document POINTER ({schema, name, baseTemplate, fighterId}),
     not a full document.
   - toManifest() -> assembleFighter() is RETIRED (B §6.2: the fight
     wiring was never done; EDITOR-SPEC §3a). toManifest() is kept
     exported, marked RETIRED below, and is never called by the editor.
   - Positions with data but NO resolver path (GROUNDED., FDFL., FDFR.,
     FUFL., CH., TACKLE., REV. — A §8.1, EDITOR-SPEC §6a) are never offered as
     assignable positions; validateNotation() refuses them (engine work
     owed, not this skeleton). Lane C 2026-11-20: FUFT./FUFA./FDFT./FDFA.
     left this list — they fire from the knockdown-exit stance window
     (fighter.js:4503-4517) via the generic stance line, so they are
     assignable now (RESOLVER_POSITIONS entries below).
   - Demonio forms are FOUR SEPARATE FIGHTERS (A §6): demonio,
     demonio-human, demonio-winged, demonio-bloodline-ember. No form
     field, no in-editor form switch (transform wiring untraced).
     demonio-winged (Devil) is CANON and a first-class editable fighter.

   KEPT API SHAPE (where the spec keeps it): createCustomMoveset /
   assignMove / removeMove / getMove / toManifest / validateMoveset /
   saveMoveset / loadSavedMoveset / serializeMoveset /
   deserializeMoveset / isEligible / listEligibleMoves. Signatures
   changed where the old signature carried the retired model (template
   objects, '|' slot keys, library ids) — see each function's note.

   SOURCE LAW: enforced at ASSIGN time by the UI (which holds the move
   + the claimed map) via moveset-library.js checkSourceLaw on the
   move's anim_ref. This engine's validateMoveset runs the same check
   when a library + claimed map are supplied.
   ============================================================ */

import { checkSourceLaw } from './moveset-library.js';

export const LS_KEY = 'wh_moveset_editor_v1';
export const STORE_VERSION = 1;
export const SCHEMA = 'wh.custom-moveset.v1';

/* ---- resolver positions (A §3a/§3b; EDITOR-SPEC §2d) ----
   In the resolver's own prefix order. `prefix` is the exact key prefix;
   SOUL/STANCE have per-fighter vocabularies instead of one prefix. RD is
   synthesized at runtime with no data keys — the chip shows, but no slot
   is ever offered under it. */
export const RESOLVER_POSITIONS = [
  { id: 'WR', prefix: 'WR.', label: 'Running' },
  { id: 'CD', prefix: 'CD.', label: 'Crouch dash' },
  { id: 'SOUL', prefix: null, label: 'Soul state', soul: true },
  { id: 'BT', prefix: 'BT.', label: 'Back-turned' },
  { id: 'STANCE', prefix: null, label: 'Stance', stance: true },
  // Ground orientations (Lane C 2026-11-20): the four canonical Tekken grounded stances
  // (wavu "Wake-up"; TKMovesets req 148/149). They fire from the knockdown-exit stance
  // window (fighter.js:4503-4517, 0.6 s, via the generic stance line in _pressV2) — a slot
  // under one of these fires ONLY inside that window, never as a standing position.
  { id: 'FUFT', prefix: 'FUFT.', label: 'Face-up, feet-toward' },
  { id: 'FUFA', prefix: 'FUFA.', label: 'Face-up, feet-away' },
  { id: 'FDFT', prefix: 'FDFT.', label: 'Face-down, feet-toward' },
  { id: 'FDFA', prefix: 'FDFA.', label: 'Face-down, feet-away' },
  { id: 'R', prefix: 'R.', label: 'Rage' },
  { id: 'H', prefix: 'H.', label: 'Heat / Soul Urge' },
  { id: 'RD', prefix: 'RD.', label: 'Rage Drive', synthesized: true },
  { id: 'SSL', prefix: 'SSL.', label: 'Sidestep left' },
  { id: 'SSR', prefix: 'SSR.', label: 'Sidestep right' },
  { id: 'SS', prefix: 'SS.', label: 'Sidestep' },
  { id: 'FC', prefix: 'FC.', label: 'Crouching' },
  { id: 'OTG', prefix: 'OTG.', label: 'Downed foe' },
  { id: 'WALL', prefix: 'WALL.', label: 'Back to wall' },
  { id: 'WS', prefix: 'WS.', label: 'While rising' },
  { id: 'AIR', prefix: 'AIR.', label: 'Airborne' },
  { id: 'STAND', prefix: '', label: 'Standing' },
];

/* Soul-state prefixes the resolver tries before BT. (B §5a:
   full-movelist.js installAddedMoves — SPIRIT / KESSHOU / SOUL9 /
   REIHOU / SEAL.) */
export const SOUL_STATES = ['SPIRIT', 'KESSHOU', 'SOUL9', 'REIHOU', 'SEAL'];

/* Prefixes with data but NO resolver path — never assignable (A §8.1,
   EDITOR-SPEC §6a). Engine work owed, not this skeleton.
   Lane C 2026-11-20: FUFT/FUFA/FDFT/FDFA left this list — they fire
   from the knockdown-exit stance window (fighter.js:4503-4517) via the
   generic stance line, so they are assignable now. The seven left here
   still have no live path: GROUNDED (needs the fighter.js ctx field +
   canAct decision), FDFL/FDFR/FUFL (need a lateral fall bit — no Tekken
   source implements a feet-left/right grounded stance), CH (a hit
   property, not a position — owner/engine design decision owed),
   TACKLE (fires today only as a throw chain, not a press), REV (no
   stance_after ever sets REV — reversal-route design decision owed). */
export const NO_RESOLVER_PATH = [
  'GROUNDED', 'FDFL', 'FDFR', 'FUFL',
  'CH', 'TACKLE', 'REV',
];

/* Words from the old engine's vocabulary that are NOT data prefixes
   (A §3d). A notation carrying one is refused, not silently mapped. */
export const RETIRED_POSITION_WORDS = [
  'corner', 'apron', 'mounted', 'jumping', 'sidestep-left', 'sidestep-right',
];

/* Demonio's four form FILES as four separate fighters (A §6). No form
   field exists anywhere in the data; the editor edits one file at a
   time and never offers an in-editor form switch. */
export const DEMONIO_FORMS = [
  'demonio', 'demonio-human', 'demonio-winged', 'demonio-bloodline-ember',
];

/* Tekken inputs, clean subset of the 120 canonical inputs measured in
   game/data/t7-frame-data (see old header, 2026-11-08). Kept VERBATIM —
   the build lane reads the exact list from the old engine (EDITOR-SPEC
   §2f); the editor offers only these notations for ADD NOTATION. */
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

/* ---- notation helpers ---- */

/* First dot-prefix of a notation ('' when bare, e.g. '1', 'f+1', '1,2').
   Throw-chain stage tags (AB1., DHH., ARM_BREAKER.) and flank prefixes
   (BACK., SIDE_L., SIDE_R.) are NOT positions: they ride on the bare /
   flank rules (A §3a step 2, A §4) and bucket under Standing for the
   position filter — the notation itself stays visible, with its stage
   tag preserved on the row. */
export function prefixOf(notation) {
  const n = String(notation || '');
  const dot = n.indexOf('.');
  if (dot <= 0) return '';
  const pre = n.slice(0, dot);
  if (/^[A-Za-z][A-Za-z0-9_]*$/.test(pre)) return pre;
  return '';
}

/* Which resolver position a notation belongs to. stanceCodes = the
   fighter's own stance codes (from its stance_after values, A §1h).
   Returns { id, stance: <code>|null, quarantine: bool }.
   - id 'QUARANTINE' = prefix with no resolver path (A §8.1): the
     notation exists in the data but cannot be assigned a position.
   - Unknown non-stance prefixes (chain tags, flank prefixes) fall to
     STAND — they are reached by string/flank rules, not by a position. */
export function positionOfNotation(notation, stanceCodes = []) {
  const pre = prefixOf(notation);
  if (!pre) return { id: 'STAND', stance: null, quarantine: false };
  if (NO_RESOLVER_PATH.includes(pre)) return { id: 'QUARANTINE', stance: null, quarantine: true };
  if (SOUL_STATES.includes(pre)) return { id: 'SOUL', stance: null, quarantine: false };
  const hit = RESOLVER_POSITIONS.find((p) => p.prefix === pre + '.');
  if (hit) return { id: hit.id, stance: null, quarantine: false };
  if (stanceCodes.includes(pre)) return { id: 'STANCE', stance: pre, quarantine: false };
  return { id: 'STAND', stance: null, quarantine: false };
}

/* A notation is assignable only when the resolver can try it: plain
   resolver notation, no legacy '|' key, no no-path prefix, no retired
   engine word, no corrupt HTML-escaped key (A §8.8: "BT.3,&#58;1+2"). */
export function validateNotation(notation) {
  const n = String(notation || '');
  if (!n) throw new Error('empty notation');
  if (n.includes('|')) throw new Error(`legacy slot key: ${n} — migrate it (migrateDocSlots) before assigning`);
  if (n.includes('&#')) throw new Error(`corrupt key (HTML-escaped): ${n} — quarantined, never offered as a slot`);
  const pre = prefixOf(n);
  if (pre && NO_RESOLVER_PATH.includes(pre)) {
    throw new Error(`position ${pre}. has data but no resolver path — engine work owed (A §8.1), not assignable`);
  }
  if (pre && RETIRED_POSITION_WORDS.includes(pre.toLowerCase())) {
    throw new Error(`position word ${pre} is not a data prefix (A §3d) — use the resolver list`);
  }
  return n;
}

/* The slot key IS the notation now (EDITOR-SPEC §3b). Kept name for API
   compat; validates instead of building a '|' key. */
export function slotKey(notation) {
  return validateNotation(notation);
}

/* Parse a slot key. Plain notations return {position, situation: null,
   input}. Legacy '|' keys are parsed for MIGRATION ONLY (legacy: true)
   — the caller must re-key them, never write them back. */
export function parseSlotKey(key) {
  const k = String(key || '');
  if (k.includes('|')) {
    const [position, situation, input] = k.split('|');
    if (!position || !situation || !input) throw new Error(`bad slot key: ${key}`);
    return { position, situation, input, legacy: true };
  }
  const pos = positionOfNotation(k);
  return { position: pos.id, situation: null, input: validateNotation(k), legacy: false };
}

/* Which layer a move key points at (A §1f key-suffix conventions).
   Returns { layer: 'T8'|'T7'|'T3'|'DONOR'|'MAIN'|'BASE', base } where
   base is the key with its variant suffix stripped (for alternates). */
export function layerOfKey(key) {
  const k = String(key || '');
  const base = k.split(/__|~|_t\d$|_r\d|_c\d/)[0];
  if (/~t8\./.test(k) || /_t8$/.test(k)) return { layer: 'T8', base };
  if (/~t7\./.test(k)) return { layer: 'T7', base };
  if (/~t3\./.test(k)) return { layer: 'T3', base };
  if (/~donor\./.test(k)) return { layer: 'DONOR', base };
  if (/__main$/.test(k)) return { layer: 'MAIN', base };
  return { layer: 'BASE', base };
}

/* The runtime grab test — the ONE throw definition the editor uses
   (fighter.js:449-453, A §5, EDITOR-SPEC §2e.3): the file's own throw
   counts disagree (Pantera move_class 'throw' 146 vs throw:true 124),
   so only isGrab || move_class==='throw' decides what plays. */
export function isGrabMove(move) {
  return !!(move && (move.isGrab || move.move_class === 'throw'));
}

/* ---- custom movesets (named documents, EDITOR-SPEC §3b) ---- */

/* One document per custom moveset. slots: plain resolver notation ->
   move key (bare key for the fighter's own moves, "<otherId>::<key>"
   for cross-fighter borrows). Only slots that differ from the base kit
   are stored (a sparse map, like the loadout itself).
   Signature change vs the old engine: the base kit is a FIGHTER ID
   (another fighter's whole moveset, the loadout's __base), not a
   library template object — the template world retired with the
   assembler path. baseTemplate defaults to 'demonio' for the custom
   fighter (B §3a, suite parity). */
export function createCustomMoveset({ name, fighterId, baseTemplate, base } = {}) {
  if (!name || !String(name).trim()) throw new Error('a custom moveset needs a name');
  return {
    schema: SCHEMA,
    name: String(name).trim(),
    fighterId: fighterId || 'custom',
    baseTemplate: baseTemplate || (fighterId === 'custom' || !fighterId ? 'demonio' : fighterId),
    /* base kit for the fight path: {bank, character} from the index
       entry (anim bank per bankIdFor, tekken_base). Null when the
       document has no base — allowed by the format, but the editor
       warns that a fighter with no base and no file has no moves to
       fall back on. */
    base: base || null,
    slots: {}, // notation -> moveKey | "otherId::key"
    created: new Date().toISOString(),
  };
}

/* A move may fill a notation when its input matches, is listed in its
   input_slots, or is null (T3 rows carry input null — position-only
   fit, flagged as a warning, never presented as a decoded input).
   moveKey is the move's dict key: its position prefix must match the
   notation's position, unless the move has no decoded position. */
export function isEligible(move, notation, moveKey) {
  if (!move || !notation) return false;
  try { validateNotation(notation); } catch { return false; }
  if (moveKey) {
    const mp = positionOfNotation(moveKey);
    const np = positionOfNotation(notation);
    if (!mp.quarantine && !np.quarantine && mp.id !== 'STAND' && np.id !== 'STAND' && mp.id !== np.id) return false;
    if (mp.quarantine || np.quarantine) return false;
  }
  if (move.input) {
    if (move.input === notation) return true;
    if (Array.isArray(move.input_slots) && move.input_slots.includes(notation)) return true;
    return false;
  }
  return true; // input null: position-only fit (flagged as a warning on assign)
}

export function listEligibleMoves(moves, notation) {
  return (moves || []).filter((m) => isEligible(m, notation, m.input));
}

export function assignMove(moveset, notation, moveKey, opts = {}) {
  validateNotation(notation);
  const key = String(moveKey || '');
  if (!key || key.includes('|') || key.includes('&#')) throw new Error(`bad move key: ${moveKey}`);
  if (opts.move && !isEligible(opts.move, notation, key)) {
    throw new Error(`move ${key} cannot fill slot ${notation} (input ${opts.move.input || 'undecoded'})`);
  }
  const next = { ...moveset, slots: { ...moveset.slots, [notation]: key } };
  return next;
}

export function removeMove(moveset, notation) {
  const slots = { ...moveset.slots };
  delete slots[notation];
  return { ...moveset, slots };
}

export function getMove(moveset, notation) {
  return (moveset.slots || {})[notation] || null;
}

/* RETIRED (EDITOR-SPEC §3a): toManifest() -> assembleFighter() was the
   projection into the assembler, whose call from the fight path was
   never built. The editor never calls this; the playable path is
   compileToLoadout() into wh_moveset_loadout_v1. Kept exported so
   nothing that imported it breaks, and so validateMoveset can still
   project for the source-law check when it has library data. */
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

/* Validate a custom moveset. Returns {ok, errors[], warnings[]} — never
   throws for bad data, so the UI can show every problem at once.
   libraryById (Map of library_id -> entry, when the index exists) checks
   each slot's move exists + is eligible; claimed runs checkSourceLaw on
   the slots' anim_refs (the t3: pull behind each assigned move). */
export function validateMoveset(moveset, { libraryById, claimed } = {}) {
  const errors = [];
  const warnings = [];
  if (!moveset || moveset.schema !== SCHEMA) errors.push('not a wh.custom-moveset.v1 moveset');
  const slots = (moveset && moveset.slots) || {};
  for (const [notation, moveKey] of Object.entries(slots)) {
    try { validateNotation(notation); } catch (e) { errors.push(`slot ${notation}: ${e.message}`); continue; }
    if (typeof moveKey !== 'string' || !moveKey || moveKey.includes('|')) {
      errors.push(`slot ${notation}: bad move key ${moveKey}`);
      continue;
    }
    const entry = libraryById ? libraryById.get(moveKey) : null;
    if (libraryById && !entry) { errors.push(`slot ${notation}: unknown library move ${moveKey}`); continue; }
    if (entry) {
      if (!isEligible(entry, notation, moveKey)) errors.push(`slot ${notation}: move ${moveKey} is not eligible for this slot`);
      if (!entry.input) warnings.push(`slot ${notation}: move ${moveKey} has no decoded input — position-only fit (T3 input decode pending)`);
      if (!entry.anim_ref) warnings.push(`slot ${notation}: move ${moveKey} has no anim_ref — no live preview until its bank lands`);
    }
  }
  if (claimed && moveset) {
    const manifest = {
      fighter: moveset.fighterId,
      moves: Object.entries(slots).map(([slot, library_id]) => ({ library_id, slot })),
    };
    const law = checkSourceLaw(manifest, claimed);
    if (!law.passed) errors.push(...law.issues);
  }
  return { ok: errors.length === 0, errors, warnings };
}

/* Compile a named document into the LIVE loadout (EDITOR-SPEC §3a).
   setLoadoutSlot is injected (movesets.js) so this engine stays
   node-testable without the fight loader. clearNotations = the
   fighter's current loadout notations (from getLoadout) — they are
   deleted first so APPLY replaces the kit instead of merging stale
   entries over it. Returns {cleared, applied, base}. */
export function compileToLoadout(moveset, { setLoadoutSlot, clearNotations = [] } = {}) {
  if (typeof setLoadoutSlot !== 'function') throw new Error('compileToLoadout needs setLoadoutSlot (movesets.js)');
  const fid = moveset.fighterId;
  let cleared = 0;
  for (const n of clearNotations) {
    if (n === '__base') continue;
    if (setLoadoutSlot(fid, n, null)) cleared += 1;
  }
  let applied = 0;
  for (const [notation, moveKey] of Object.entries(moveset.slots || {})) {
    validateNotation(notation);
    if (setLoadoutSlot(fid, notation, moveKey)) applied += 1;
  }
  if (moveset.baseTemplate) setLoadoutSlot(fid, '__base', moveset.baseTemplate);
  return { cleared, applied, base: moveset.baseTemplate || null };
}

/* ---- persistence: the named-document store (EDITOR-SPEC §3c) ----
   wh_moveset_editor_v1 = {version:1, movesets:{name:doc}, applied:{fid:name}}.
   The single-slot shape of the old engine is migrated on read (below),
   never silently dropped. In node (no localStorage) an in-memory store
   stands in so the module stays testable. */

let _memStore = null;

function _storeBackend() {
  if (typeof localStorage !== 'undefined') {
    return {
      get: () => localStorage.getItem(LS_KEY),
      set: (raw) => localStorage.setItem(LS_KEY, raw),
    };
  }
  return {
    get: () => _memStore,
    set: (raw) => { _memStore = raw; },
  };
}

/* Re-key a legacy document's slots: "position|situation|input" ->
   plain resolver notation (the input part). Collisions keep the plain
   key (first wins). Returns {doc, migrated:[oldKeys]}. */
export function migrateDocSlots(doc) {
  const slots = {};
  const migrated = [];
  for (const [key, value] of Object.entries((doc && doc.slots) || {})) {
    if (key.includes('|')) {
      const parsed = parseSlotKey(key);
      migrated.push(key);
      if (!(parsed.input in slots)) slots[parsed.input] = value;
    } else if (!(key in slots)) {
      slots[key] = value;
    }
  }
  return { doc: { ...doc, slots }, migrated };
}

function _emptyStore() {
  return { version: STORE_VERSION, movesets: {}, applied: {} };
}

/* Read the store, migrating the old single-document shape when found:
   a top-level wh.custom-moveset.v1 document becomes movesets[name].
   Bad JSON returns an empty store (the UI surfaces the loss; the
   editor never crashes on a corrupt save). */
export function readStore() {
  let raw = null;
  try { raw = _storeBackend().get(); } catch { return _emptyStore(); }
  if (!raw) return _emptyStore();
  let parsed = null;
  try { parsed = JSON.parse(raw); } catch { return _emptyStore(); }
  if (parsed && parsed.schema === SCHEMA) {
    const { doc } = migrateDocSlots(parsed);
    const store = _emptyStore();
    store.movesets[doc.name || 'Custom'] = doc;
    return store;
  }
  if (parsed && parsed.movesets && typeof parsed.movesets === 'object') {
    const store = { version: 1, movesets: {}, applied: parsed.applied || {} };
    for (const [name, doc] of Object.entries(parsed.movesets)) {
      if (!doc || doc.schema !== SCHEMA) continue;
      const { doc: fixed } = migrateDocSlots(doc);
      store.movesets[name] = fixed;
    }
    return store;
  }
  return _emptyStore();
}

export function writeStore(store) {
  const raw = JSON.stringify(store);
  _storeBackend().set(raw);
  return store;
}

export function listNamedMovesets() {
  const store = readStore();
  return Object.values(store.movesets)
    .map((d) => ({ name: d.name, fighterId: d.fighterId, baseTemplate: d.baseTemplate, created: d.created, slots: Object.keys(d.slots || {}).length }))
    .sort((a, b) => String(b.created || '').localeCompare(String(a.created || '')));
}

export function loadNamedMoveset(name) {
  const store = readStore();
  const doc = store.movesets[String(name)];
  return doc ? JSON.parse(JSON.stringify(doc)) : null;
}

/* Save a named document. Saving with an existing name OVERWRITES that
   document (the save sheet says so; rename/duplicate are owner
   decisions owed, EDITOR-SPEC §6d.6, and are not offered). */
export function saveNamedMoveset(doc) {
  if (!doc || doc.schema !== SCHEMA) throw new Error('not a wh.custom-moveset.v1 moveset');
  if (!doc.name) throw new Error('a custom moveset needs a name');
  const { doc: fixed } = migrateDocSlots(doc);
  const store = readStore();
  store.movesets[fixed.name] = fixed;
  writeStore(store);
  return fixed;
}

export function deleteNamedMoveset(name) {
  const store = readStore();
  const had = Boolean(store.movesets[String(name)]);
  delete store.movesets[String(name)];
  for (const [fid, applied] of Object.entries(store.applied)) {
    if (applied === name) delete store.applied[fid];
  }
  writeStore(store);
  return had;
}

export function getAppliedName(fighterId) {
  return readStore().applied[fighterId] || null;
}

export function setAppliedName(fighterId, name) {
  const store = readStore();
  if (name) store.applied[fighterId] = name;
  else delete store.applied[fighterId];
  writeStore(store);
  return store.applied[fighterId] || null;
}

/* ---- persistence shims (old single-slot API, kept for compat) ----
   saveMoveset writes into the named store under the document's name;
   loadSavedMoveset returns the most recently created named document,
   or null. New code uses the named functions above. */

export function serializeMoveset(moveset) {
  return JSON.stringify(moveset);
}

export function deserializeMoveset(raw) {
  const m = typeof raw === 'string' ? JSON.parse(raw) : raw;
  if (!m || m.schema !== SCHEMA) throw new Error('not a wh.custom-moveset.v1 moveset');
  return migrateDocSlots(m).doc;
}

export function saveMoveset(moveset) {
  return saveNamedMoveset(moveset);
}

export function loadSavedMoveset() {
  const list = listNamedMovesets();
  if (!list.length) return null;
  return loadNamedMoveset(list[0].name);
}
