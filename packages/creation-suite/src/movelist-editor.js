// Create-A-Move List editor for the Western Heart creation suite.
//
// Port of WWE Create-A-Moveset into Western Heart, organized in Tekken
// input style. Button names use LP1/RP2/LK3/RK4 everywhere in UI text
// and in code comments:
//
//   LP1 = Left Punch  = Tekken 1
//   RP2 = Right Punch = Tekken 2
//   LK3 = Left Kick   = Tekken 3
//   RK4 = Right Kick  = Tekken 4
//
// Data source: real fighter moveset files at
// `game/assets/movesets/{fighter}.json`. Nothing here is guessed or
// procedurally generated: every entry shown comes from a moveset file,
// or from a library entry the host passes in.
//
// Library adapter: the host may pass library entries built by
// `packages/creation-suite/src/movelist-data.js` (entry shape documented
// on LIBRARY_ENTRY_SHAPE below). This module deliberately does NOT
// import that file: it was not present on main when this editor was
// written, and importing a missing module would break the editor. When
// the host passes no library, the editor builds entries directly from
// the fighter's own moveset file with fromMovesetFile(), so the editor
// works either way. Entries built by movelist-data.js and entries built
// here share the same shape, and entries passed in always win over
// derived ones for the same id.
//
// Flow (owner spec, docs/MOVE-MATCHING-SYSTEM.md):
//   Select character -> Create-A-Move List -> Edit -> Choose character
//   -> See ALL moves (including wrongly mapped ones)
//   -> Swap moves to correct slots -> Save
//
// Context validation (CORE REQUIREMENT, owner directive verbatim):
//   "where you can replace the move with the proper animation that goes
//   there not with just like any bullshit animation but like if you're
//   pressing if it's a crouching position that only the crouching
//   animations can get chosen there and such and such"
//
// That means: a jumping slot takes ONLY jumping animations, a crouching
// slot takes ONLY crouching animations, a standing slot takes ONLY
// standing animations, a grapple slot takes ONLY grapple/throw
// animations, and a directional or diagonal slot takes ONLY animations
// matching that direction. validateAssignment() enforces this, and
// swapMove() BLOCKS a mismatched assignment by default instead of
// silently saving a wrong one. Existing wrong mappings are still
// SHOWN in the full list (status "wrong") so the user can see and fix
// them; the block applies to NEW assignments made through the editor.
//
// Animation properties and honesty about them:
// A candidate's properties come from clip analysis when the library
// entry carries them (entry.properties / entry.anim_properties with
// source "clip": jumping/crouching/standing, direction, limb, type, as
// measured from the actual clip, not from a JSON label). When no clip
// tags exist, properties are derived from the move's own Tekken input
// (source "input"). Input-derived properties can catch a wrong slot
// (for example a crouching input sitting in a standing slot), but they
// cannot catch the PR #988 failure mode — a clip that jumps while its
// JSON label says "jab". So every status also carries a `verification`
// field: "clip" when clip tags decided it, "input" otherwise. An
// input-consistent entry is "correct" with verification "input", which
// means: consistent with its input, still to be verified by playing.
// Never present an input-derived status as clip-verified.
//
// Save: this module never writes a local file. serializeMoveset() and
// exportMovesetJSON() produce the updated moveset object/text, and
// createSavePayload() produces the exact payload a host sends to the
// GitHub API to update `game/assets/movesets/{fighter}.json` through a
// feature-branch PR. The editor's own delivery follows the same rule:
// feature branch + PR, never a push to main.
//
// This is a creation-suite editor, not a game menu. The creation-suite
// UI is grandfathered as legacy-unsourced; this editor is functional
// and cites its data source (the moveset files) in every row it shows.
//
// No DOM framework is required. The pure functions (parsing, context,
// validation, combo editing, serialization) run in Node and in the
// browser. renderEditorHTML() returns an HTML string and mount()
// wires it to a real element when `document` exists.

// ---------------------------------------------------------------------------
// Button names: LP1, RP2, LK3, RK4
// ---------------------------------------------------------------------------

export const BUTTON_NAMES = {
  1: 'LP1',
  2: 'RP2',
  3: 'LK3',
  4: 'RK4',
};

// Tekken button number -> limb used by that button, for LP1/RP2/LK3/RK4.
export const BUTTON_TO_LIMB = {
  1: 'armL', // LP1, Left Punch
  2: 'armR', // RP2, Right Punch
  3: 'legL', // LK3, Left Kick
  4: 'legR', // RK4, Right Kick
};

export const LIMB_TO_BUTTON = {
  armL: 'LP1',
  armR: 'RP2',
  legL: 'LK3',
  legR: 'RK4',
};

// Mapping statuses shown in the list. Exactly these four values.
export const MAPPING_STATUSES = ['correct', 'wrong', 'approximate', 'unmapped'];

// Named stance prefixes seen at the front of Tekken inputs, before the
// first ".". Only prefixes in this table get a stance from the prefix;
// an unknown named prefix yields stance "unknown" (status approximate),
// never a guessed stance.
const NAMED_PREFIX_STANCE = {
  FC: 'crouching', // Full Crouch, e.g. FC.LP1,RP2
  WS: 'rising', // While Standing (while rising), e.g. WS.RP2
  AIR: 'jumping',
  JGR: 'jumping', // Jump, grounded recovery family in the files
  JGS: 'jumping',
  BT: 'back_turned', // Back Turned
  CD: 'crouch_dash', // Crouch Dash
  SS: 'sidestep',
  // Grapple-chain names (PILE_DRIVER, TACKLE, BACKDROP, ...) are not
  // stances. They are handled by kind derivation, not by this table.
};

// Named prefixes that mark a grapple/throw slot, whatever the buttons.
const GRAPPLE_PREFIXES = new Set([
  'PILE_DRIVER', 'PD', 'TACKLE', 'BACKDROP', 'DHH', 'FDFA', 'SLEEPER',
  'R', // King-style rolling / chain-throw families use R. prefixes in files
]);

// ---------------------------------------------------------------------------
// Input parsing and display: Tekken 1/2/3/4 -> LP1/RP2/LK3/RK4
// ---------------------------------------------------------------------------

// Normalize a direction token: "df" -> "d/f", "db" -> "d/b",
// "uf" -> "u/f", "ub" -> "u/b". Everything else passes through.
export function normalizeDirection(direction) {
  if (direction == null) return 'none';
  const d = String(direction).toLowerCase();
  if (d === 'df') return 'd/f';
  if (d === 'db') return 'd/b';
  if (d === 'uf') return 'u/f';
  if (d === 'ub') return 'u/b';
  if (d === '' || d === 'n') return 'none';
  return d;
}

// Convert one Tekken button token to LP1/RP2/LK3/RK4 display form.
// "1" -> "LP1", "1+2" -> "LP1+RP2", "3+4" -> "LK3+RK4".
// Non-button tokens (directions, prefixes, "P", "K") pass through.
export function toDisplayButton(token) {
  return String(token)
    .split('+')
    .map((part) => BUTTON_NAMES[part] || part)
    .join('+');
}

// Convert a full Tekken input string to LP1/RP2/LK3/RK4 display form.
// Examples:
//   "1"          -> "LP1"
//   "f+LP1"      -> "f+LP1" (input "f+1")
//   "d/f+RP2"    -> "d/f+RP2" (input "d/f+2" or "df+2")
//   "LP1,RP2"    -> "LP1,RP2" (input "1,2")
//   "FC.LP1,RP2" -> "FC.LP1,RP2" (input "FC.1,2")
// Prefixes, commas (string separators) and "+" (simultaneous buttons)
// are preserved; only bare direction shorthands are normalized.
export function toDisplayInput(tekkenInput) {
  if (tekkenInput == null) return '';
  return String(tekkenInput)
    .split(',')
    .map((hit) => {
      const hitText = hit.trim();
      // Named prefix: "FC.1" -> "FC.LP1". Keep the prefix verbatim.
      const dot = hitText.indexOf('.');
      if (dot > 0) {
        const prefix = hitText.slice(0, dot);
        const rest = hitText.slice(dot + 1);
        if (/^[A-Z_]+$/.test(prefix)) {
          return `${prefix}.${toDisplayButton(rest)}`;
        }
      }
      // Simultaneous buttons with no direction: "1+2" -> "LP1+RP2".
      if (/^[0-9]+(\+[0-9]+)+$/.test(hitText)) return toDisplayButton(hitText);
      // Direction + button(s): "df+2" -> "d/f+RP2", "f+1" -> "f+LP1".
      // A hit may also be direction-only ("f") or button-only ("1").
      const plus = hitText.indexOf('+');
      if (plus > 0) {
        const direction = hitText.slice(0, plus);
        const buttons = hitText.slice(plus + 1);
        if (/^[a-z/]+$/i.test(direction) && /^[0-9+]+$/.test(buttons)) {
          const normalized = normalizeDirection(direction);
          return normalized === 'none'
            ? toDisplayButton(buttons)
            : `${normalized}+${toDisplayButton(buttons)}`;
        }
      }
      // Bare button, bare direction, or anything else: convert buttons
      // only when the whole token is button digits.
      if (/^[0-9]+$/.test(hitText)) return toDisplayButton(hitText);
      return hitText;
    })
    .join(',');
}

// Split one hit token (one comma-separated piece of an input) into its
// direction and its LP1/RP2/LK3/RK4 buttons.
// "d/f+2" -> { direction: "d/f", buttons: [2], displayButtons: ["RP2"] }
// "1"     -> { direction: "none", buttons: [1], displayButtons: ["LP1"] }
// "FC.1" is handled by the caller (prefix stripped before this runs).
export function parseHitToken(hitToken) {
  const hit = String(hitToken || '').trim();
  // Simultaneous buttons with no direction: "1+3" -> buttons [1, 3].
  // This check must come first, or "1" would be misread as a direction.
  if (/^[0-9]+(\+[0-9]+)+$/.test(hit)) {
    const buttons = hit.split('+').map((part) => Number(part));
    return { direction: 'none', buttons, displayButtons: buttons.map((n) => BUTTON_NAMES[n]) };
  }
  const plus = hit.indexOf('+');
  if (plus > 0) {
    const direction = normalizeDirection(hit.slice(0, plus));
    const buttons = hit
      .slice(plus + 1)
      .split('+')
      .map((part) => Number(part))
      .filter((n) => Number.isInteger(n) && n >= 1 && n <= 4);
    return {
      direction,
      buttons,
      displayButtons: buttons.map((n) => BUTTON_NAMES[n]),
    };
  }
  if (/^[0-9]$/.test(hit)) {
    return { direction: 'none', buttons: [Number(hit)], displayButtons: [BUTTON_NAMES[Number(hit)]] };
  }
  if (/^(d\/f|d\/b|u\/f|u\/b|df|db|uf|ub|f|b|d|u)$/i.test(hit)) {
    return { direction: normalizeDirection(hit), buttons: [], displayButtons: [] };
  }
  return { direction: 'none', buttons: [], displayButtons: [] };
}

// Split a full Tekken input into { prefix, hits }.
// "FC.1,2" -> { prefix: "FC", hits: ["1", "2"] }
// "d/f+2"  -> { prefix: null, hits: ["d/f+2"] }
// "1,2"    -> { prefix: null, hits: ["1", "2"] }
export function splitInput(tekkenInput) {
  const input = String(tekkenInput || '').trim();
  if (!input) return { prefix: null, hits: [] };
  const parts = input.split(',');
  let prefix = null;
  let first = parts[0];
  const dot = first.indexOf('.');
  if (dot > 0 && /^[A-Z_]+$/.test(first.slice(0, dot))) {
    prefix = first.slice(0, dot);
    first = first.slice(dot + 1);
  }
  return { prefix, hits: [first, ...parts.slice(1)] };
}

// ---------------------------------------------------------------------------
// Slot context and candidate properties
// ---------------------------------------------------------------------------

// Derive a slot's context from its Tekken input string. The context is
// what an animation MUST match to belong in this slot:
//   stance:    standing | crouching | jumping | rising | crouch_dash |
//              back_turned | sidestep | unknown | any
//   direction: none | f | b | d | u | d/f | d/b | u/f | u/b
//   kind:      strike | grapple | any
//   buttons:   Tekken button numbers of the slot's first hit
//   limb:      expected limb for a single-button slot, "both" for a
//              multi-button slot, null when it cannot be derived
// `hint` lets a host pin the kind (for example a WWE-style grapple
// category slot) when the input alone does not carry it.
export function deriveSlotContext(tekkenInput, hint = {}) {
  const { prefix, hits } = splitInput(tekkenInput);
  const firstHit = parseHitToken(hits[0] || '');
  let stance = 'standing';
  if (prefix && NAMED_PREFIX_STANCE[prefix]) {
    stance = NAMED_PREFIX_STANCE[prefix];
  } else if (prefix && GRAPPLE_PREFIXES.has(prefix)) {
    stance = 'standing';
  } else if (prefix) {
    // Unknown named prefix: do not guess a stance.
    stance = 'unknown';
  } else if (['u', 'u/f', 'u/b'].includes(firstHit.direction)) {
    stance = 'jumping';
  } else if (['d', 'd/f', 'd/b'].includes(firstHit.direction)) {
    stance = 'crouching';
  }
  let kind = hint.kind || 'strike';
  if (prefix && GRAPPLE_PREFIXES.has(prefix)) kind = 'grapple';
  // LP1+LK3 (1+3) and RP2+RK4 (2+4) are the standard throw inputs.
  const buttonKey = [...firstHit.buttons].sort().join('+');
  if (buttonKey === '1+3' || buttonKey === '2+4') kind = 'grapple';
  if (hint.kind) kind = hint.kind;
  const limb =
    firstHit.buttons.length === 0
      ? null
      : firstHit.buttons.length === 1
        ? BUTTON_TO_LIMB[firstHit.buttons[0]]
        : 'both';
  return {
    input: tekkenInput,
    displayInput: toDisplayInput(tekkenInput),
    stance,
    direction: firstHit.direction,
    kind,
    buttons: firstHit.buttons,
    displayButtons: firstHit.displayButtons,
    limb,
    prefix,
  };
}

// Derive a candidate move's animation properties. Clip tags win when
// present; otherwise properties are derived from the candidate's own
// Tekken input. The returned `source` says which one decided, so the UI
// never presents an input-derived check as clip-verified.
export function deriveCandidateProperties(candidate) {
  const clip = candidate?.properties || candidate?.anim_properties || null;
  // ONLY properties explicitly tagged source "clip" count as clip
  // analysis. Properties this editor itself derived from an input
  // (source "input") must NOT be re-read as clip tags, or every row
  // would falsely claim to be clip-verified. Untagged properties are
  // treated the same conservative way: derive from the input.
  if (clip && clip.source === 'clip' && (clip.stance || clip.direction || clip.type || clip.limb)) {
    return {
      stance: clip.stance || 'unknown',
      direction: normalizeDirection(clip.direction || 'none'),
      type: clip.type || (candidate.move_class === 'throw' ? 'grapple' : 'strike'),
      limb: clip.limb || null,
      source: 'clip',
    };
  }
  const context = deriveSlotContext(candidate?.input || '', {
    kind: candidate?.move_class === 'throw' ? 'grapple' : undefined,
  });
  let type = 'strike';
  if (candidate?.move_class === 'throw' || candidate?.throw === true) type = 'grapple';
  return {
    stance: context.stance,
    direction: context.direction,
    type,
    limb: context.limb,
    source: 'input',
  };
}

// ---------------------------------------------------------------------------
// Context validation — the core requirement
// ---------------------------------------------------------------------------

// Check one candidate against one slot context. Returns:
//   { allowed, status, reasons, verification }
// allowed is false exactly when a KNOWN property mismatches the slot:
// jumping animation in a standing slot, crouching in a jumping slot,
// grapple in a strike slot (or the reverse), wrong direction, wrong
// limb for a single-button LP1/RP2/LK3/RK4 slot. Unknown properties
// never block: they yield status "approximate" with a reason, so the
// user can still assign them and verify by playing.
// status: "correct" | "wrong" | "approximate" | "unmapped"
// An entry with no anim_ref and no bank/row is "unmapped" and is never
// eligible for assignment (there is no animation to play).
export function validateAssignment(slotContext, candidate) {
  const reasons = [];
  const animRef = candidate?.anim_ref || candidate?.animRef || null;
  const bankRow = candidate?.t3_row ?? candidate?.t3Row ?? candidate?.t7_move_id ?? null;
  if (!animRef && bankRow == null) {
    return {
      allowed: false,
      status: 'unmapped',
      reasons: ['No animation reference: nothing to play for this move.'],
      verification: 'input',
    };
  }
  const props = deriveCandidateProperties(candidate);
  let mismatch = false;
  let unknown = false;
  // Stance: jumping slots take ONLY jumping, crouching ONLY crouching,
  // standing ONLY standing, rising ONLY rising, and so on. "any" slots
  // (user-created custom slots with no stance) skip this check.
  if (slotContext.stance !== 'any') {
    if (props.stance === 'unknown') unknown = true;
    else if (props.stance !== slotContext.stance) {
      mismatch = true;
      reasons.push(
        `Stance mismatch: slot is ${slotContext.stance}, animation is ${props.stance}.`,
      );
    }
  }
  // Direction: a directional or diagonal slot takes ONLY animations
  // matching that direction (d/f+RP2 takes d/f, not f and not d).
  if (props.direction === 'unknown') unknown = true;
  else if (props.direction !== slotContext.direction) {
    mismatch = true;
    reasons.push(
      `Direction mismatch: slot is ${slotContext.direction}, animation is ${props.direction}.`,
    );
  }
  // Kind: grapple slots take ONLY grapple/throw animations; strike
  // slots take ONLY non-grapple animations.
  if (slotContext.kind !== 'any') {
    if (props.type === 'grapple' && slotContext.kind !== 'grapple') {
      mismatch = true;
      reasons.push('Kind mismatch: grapple/throw animation in a strike slot.');
    } else if (props.type !== 'grapple' && slotContext.kind === 'grapple') {
      mismatch = true;
      reasons.push('Kind mismatch: strike animation in a grapple slot.');
    }
  }
  // Limb: a single-button LP1/RP2/LK3/RK4 slot takes ONLY the limb for
  // that button (LP1 -> armL, RP2 -> armR, LK3 -> legL, RK4 -> legR).
  // Grapple slots skip the limb check: throws use the whole body.
  // Multi-button slots expect "both".
  if (slotContext.kind !== 'grapple' && slotContext.limb) {
    if (props.limb == null) unknown = true;
    else if (props.limb !== slotContext.limb) {
      mismatch = true;
      reasons.push(
        `Limb mismatch: slot ${slotContext.displayButtons.join('+') || ''} expects ${slotContext.limb}, animation uses ${props.limb}.`,
      );
    }
  }
  if (mismatch) {
    return { allowed: false, status: 'wrong', reasons, verification: props.source };
  }
  if (unknown) {
    return {
      allowed: true,
      status: 'approximate',
      reasons: [
        ...reasons,
        'Some animation properties are unknown: verify by playing before treating this as correct.',
      ],
      verification: props.source,
    };
  }
  return { allowed: true, status: 'correct', reasons, verification: props.source };
}

// Status of a move against its OWN slot: this is how the full list
// surfaces wrongly mapped moves. A standing LP1 whose clip tags say
// jumping comes back "wrong" here even though its file entry looks
// like a jab — exactly the Pantera row-38 failure this editor exists
// to fix.
export function computeMappingStatus(entry, hint = {}) {
  const slotContext = deriveSlotContext(entry?.input || '', {
    kind: entry?.move_class === 'throw' ? 'grapple' : hint.kind,
  });
  return { slotContext, ...validateAssignment(slotContext, entry) };
}

// Library entries that may be assigned to a slot: only context-matching
// ones. Wrong and unmapped entries are still shown in the full list,
// but they are NOT offered as swap targets.
export function eligibleCandidates(slotContext, library) {
  return (library || []).filter(
    (candidate) => validateAssignment(slotContext, candidate).allowed,
  );
}

// ---------------------------------------------------------------------------
// Library entries from real moveset files
// ---------------------------------------------------------------------------

// The library entry shape. movelist-data.js entries and fromMovesetFile
// entries share it; hosts may pass either.
//   {
//     id, name, input, displayInput, anim_ref, t3_bank, t3_row,
//     category, move_class, limb, throw,
//     properties: { stance, direction, type, limb, source }
//   }
// Categories used by fromMovesetFile: grappling, standing, crouching,
// jumping, rising, ground (reserved: entries whose file data marks
// them grounded; never assigned by guessing), tekken_striking, special.
export const LIBRARY_ENTRY_SHAPE = 'id, name, input, displayInput, anim_ref, t3_bank, t3_row, category, move_class, limb, throw, properties';

export function categoryForEntry(entry, context) {
  if (entry?.category) return entry.category;
  if (entry?.move_class === 'throw' || entry?.throw === true) return 'grappling';
  if (context.stance === 'jumping') return 'jumping';
  if (context.stance === 'crouching' || context.stance === 'crouch_dash') return 'crouching';
  if (context.stance === 'rising') return 'rising';
  if (entry?.move_class === 'strike' || entry?.move_class === 'string') return 'tekken_striking';
  if (entry?.move_class === 'special' || entry?.move_class === 'signature') return 'special';
  return 'standing';
}

// Build library entries from one fighter moveset file object
// (game/assets/movesets/{fighter}.json). The file's `moves` map is
// keyed by Tekken input; each value carries name, anim_ref, t3_row,
// move_class and limb. `specials` entries with throw: true become
// grappling entries. No entry is invented: if a file has no move for
// an input, there is no entry for it.
export function fromMovesetFile(moveset) {
  const entries = [];
  const moves = moveset?.moves || {};
  for (const [key, move] of Object.entries(moves)) {
    if (!move || typeof move !== 'object') continue;
    // Entry id is the file's own key, NOT the input string: a moveset
    // file deliberately carries several source variants for one input
    // (for example "1", "1~t8.king" and "1~t7.king" are all LP1, from
    // different sources, with different animation rows). Collapsing
    // them to one entry per input would silently drop swap candidates
    // and hide the very variants the user needs to compare. Each row
    // keeps its own key, its own name and its own anim_ref; the slot
    // context is derived from its input, which the variants share.
    const context = deriveSlotContext(move.input || key, {
      kind: move.move_class === 'throw' ? 'grapple' : undefined,
    });
    entries.push({
      id: String(key),
      name: move.name || String(move.input || key),
      input: move.input || key,
      displayInput: toDisplayInput(move.input || key),
      anim_ref: move.anim_ref || null,
      t3_bank: move.t3_source || moveset?.t3_bank || moveset?.t3_source || null,
      t3_row: move.t3_row ?? null,
      category: categoryForEntry(move, context),
      move_class: move.move_class || null,
      limb: move.limb || null,
      throw: move.move_class === 'throw' || move.throw === true || false,
      properties: deriveCandidateProperties(move),
      sourceMove: move,
    });
  }
  for (const special of moveset?.specials || []) {
    if (!special || typeof special !== 'object' || !special.input) continue;
    const specialAnimRef = special.t3_row != null
      ? `t3:${moveset?.t3_source || 'unknown'}:row:${special.t3_row}`
      : null;
    // Skip only an exact duplicate (same input, same animation row);
    // a special with a different row is a distinct grapple row to show.
    if (entries.some((entry) => entry.input === special.input && entry.anim_ref === specialAnimRef)) continue;
    const context = deriveSlotContext(special.input, {
      kind: special.throw ? 'grapple' : undefined,
    });
    entries.push({
      id: `special:${special.input}:${special.t3_row ?? 'none'}`,
      name: `Special ${toDisplayInput(special.input)}`,
      input: special.input,
      displayInput: toDisplayInput(special.input),
      anim_ref: specialAnimRef,
      t3_bank: moveset?.t3_source || null,
      t3_row: special.t3_row ?? null,
      category: special.throw ? 'grappling' : 'special',
      move_class: special.throw ? 'throw' : 'special',
      limb: null,
      throw: special.throw === true,
      properties: deriveCandidateProperties({
        ...special,
        move_class: special.throw ? 'throw' : 'special',
      }),
      sourceMove: special,
    });
  }
  return entries;
}

// ---------------------------------------------------------------------------
// Editor state, display list, and combo editing
// ---------------------------------------------------------------------------

// Create editor state. `library` (optional) is an array of library
// entries in the shape above; when omitted, entries are built from
// `moveset` itself. Passing movelist-data.js entries here is the
// supported way to use that library builder with this editor.
export function createEditor({ fighter, moveset, library = null } = {}) {
  if (!moveset || typeof moveset !== 'object') {
    throw new Error('createEditor requires a fighter moveset object.');
  }
  const fighterId = fighter || moveset.fighter || 'unknown';
  const built = library && library.length > 0 ? library : fromMovesetFile(moveset);
  const entries = built.map((entry) => ({
    ...entry,
    displayInput: entry.displayInput || toDisplayInput(entry.input),
  }));
  const byId = new Map(entries.map((entry) => [String(entry.id), entry]));
  // Resolve a combo hit token to an entry: an exact entry id first
  // (for moveset-built entries the id is the file key), then any
  // entry whose input matches the token.
  const resolveHit = (token, fullInput) =>
    byId.get(token) ||
    byId.get(fullInput) ||
    entries.find((entry) => entry.input === token) ||
    null;
  // Editable combos: the file's `strings` list, normalized so bare
  // string inputs ("1,2") and object strings both become combos with
  // per-hit entries. Custom combos added later use the same shape.
  const combos = [];
  for (const raw of moveset.strings || []) {
    const input = typeof raw === 'string' ? raw : raw?.input;
    if (!input) continue;
    const { hits } = splitInput(input);
    combos.push({
      input,
      displayInput: toDisplayInput(input),
      hits: hits.map((token) => {
        const resolved = resolveHit(token, input);
        return {
          token,
          displayToken: toDisplayInput(token),
          entryId: resolved ? String(resolved.id) : null,
          anim_ref: resolved?.anim_ref || null,
          t3_row: resolved?.t3_row ?? null,
        };
      }),
      anim_refs: typeof raw === 'object' && raw !== null ? raw.t3_rows || null : null,
      source: typeof raw === 'object' && raw !== null ? raw.merge_source || 'moveset' : 'moveset',
      custom: false,
    });
  }
  return {
    fighter: fighterId,
    display: moveset.display || fighterId,
    moveset, // original object, never mutated; serialize clones it
    entries,
    byId,
    combos,
    edits: [], // audit trail: every swap / combo change, for the save
    dirty: false,
  };
}

// The full move list for display: EVERY move for the fighter,
// including wrongly mapped, approximate and unmapped ones, each with
// its name, LP1/RP2/LK3/RK4 button input, exact animation reference
// (anim_ref or t3 bank/row) and mapping status. This is the list the
// user scans to find and fix bad mappings.
export function listAllMoves(editor) {
  return editor.entries.map((entry) => {
    const checked = computeMappingStatus(entry);
    return {
      id: String(entry.id),
      name: entry.name,
      input: entry.input,
      displayInput: entry.displayInput || toDisplayInput(entry.input),
      anim_ref: entry.anim_ref || null,
      t3_bank: entry.t3_bank || null,
      t3_row: entry.t3_row ?? null,
      animRefDisplay:
        entry.anim_ref ||
        (entry.t3_row != null ? `t3:${entry.t3_bank || 'unknown'}:row:${entry.t3_row}` : 'unmapped'),
      category: entry.category,
      move_class: entry.move_class,
      limb: entry.limb,
      status: checked.status,
      verification: checked.verification,
      reasons: checked.reasons,
      slotContext: checked.slotContext,
    };
  });
}

// Replace one move row with a library candidate. `entryId` is the row
// being replaced (for moveset-built entries, the file key, so a swap
// rewrites exactly that key on save and never a same-input variant).
// The slot context comes from the replaced row's own input and kind,
// never from its current (possibly wrong) animation: a jumping jab
// sitting in a standing LP1 row does not turn that row into a jumping
// slot. Default mode is "block": a context mismatch leaves the state
// untouched and returns { ok: false, ... }. Pass { mode: "flag" } to
// record the assignment anyway with status "wrong" (visible in the
// list, never silently correct). The default exists because the owner
// directive is to BLOCK wrong animations, not to collect them.
export function swapMove(editor, entryId, candidateId, options = {}) {
  const mode = options.mode || 'block';
  const slotEntry = editor.byId.get(String(entryId));
  const candidate = editor.byId.get(String(candidateId));
  if (!slotEntry) {
    return { ok: false, error: `No move row with id ${entryId}.` };
  }
  if (!candidate) {
    return { ok: false, error: `No library move with id ${candidateId}.` };
  }
  const slotInput = slotEntry.input;
  const slotContext = deriveSlotContext(slotInput, {
    kind: slotEntry.move_class === 'throw' ? 'grapple' : undefined,
  });
  const check = validateAssignment(slotContext, candidate);
  if (!check.allowed && mode === 'block') {
    return {
      ok: false,
      error: `Blocked: ${candidate.name} (${candidate.displayInput}) does not fit slot ${slotContext.displayInput}.`,
      status: check.status,
      reasons: check.reasons,
    };
  }
  const previous = { entryId: String(slotEntry.id), anim_ref: slotEntry.anim_ref || null };
  const nextEntry = {
    ...candidate,
    id: String(entryId),
    input: slotInput,
    displayInput: toDisplayInput(slotInput),
  };
  editor.byId.set(String(entryId), nextEntry);
  editor.entries = editor.entries.map((entry) =>
    String(entry.id) === String(entryId) ? nextEntry : entry,
  );
  editor.edits.push({
    type: 'swap',
    slot: String(entryId),
    slotInput,
    displaySlot: toDisplayInput(slotInput),
    from: previous,
    to: { entryId: String(candidate.id), anim_ref: candidate.anim_ref || null },
    status: check.status,
    mode,
    reasons: check.reasons,
  });
  editor.dirty = true;
  return { ok: true, status: check.status, reasons: check.reasons, entry: nextEntry };
}

// Extend a combo by one hit: LP1,RP2 -> LP1,RP2,LP1 -> LP1,RP2,LP1,RP2.
// The new hit must fit the combo's context: same stance as the first
// hit (a standing string does not gain a jumping hit), and if the hit
// carries its own direction it must match the string's direction.
// Returns a new combo object; the original is untouched.
export function extendCombo(combo, candidate) {
  const base = combo.hits || [];
  const firstContext = deriveSlotContext(combo.input);
  const candidateContext = deriveSlotContext(candidate.input);
  const reasons = [];
  if (
    candidateContext.stance !== 'unknown' &&
    firstContext.stance !== 'any' &&
    candidateContext.stance !== firstContext.stance &&
    !(firstContext.stance === 'standing' && candidateContext.stance === 'standing')
  ) {
    return {
      ok: false,
      error: `Cannot extend ${combo.displayInput || combo.input}: ${candidate.displayInput || candidate.input} is ${candidateContext.stance}, combo is ${firstContext.stance}.`,
    };
  }
  if (candidateContext.direction !== 'none' && firstContext.direction !== 'none') {
    // Continuation hits in Tekken strings usually carry no direction;
    // a hit that DOES carry one must agree with the string's direction.
    if (candidateContext.direction !== firstContext.direction) {
      reasons.push(
        `Direction note: ${candidate.displayInput || candidate.input} is ${candidateContext.direction}, combo direction is ${firstContext.direction}.`,
      );
    }
  }
  const hits = [
    ...base,
    {
      token: candidate.input,
      displayToken: toDisplayInput(candidate.input),
      entryId: String(candidate.id),
      anim_ref: candidate.anim_ref || null,
      t3_row: candidate.t3_row ?? null,
    },
  ];
  const input = hits.map((hit) => hit.token).join(',');
  return {
    ok: true,
    combo: {
      ...combo,
      input,
      displayInput: toDisplayInput(input),
      hits,
      custom: true,
    },
    warnings: reasons,
  };
}

// Shorten a combo: remove hits from the end (default) or at an index.
// Removing the only hit is refused: a combo with no hits is not a move.
export function shortenCombo(combo, countOrIndex = 1, options = {}) {
  const hits = [...(combo.hits || [])];
  if (hits.length <= 1) {
    return { ok: false, error: 'Cannot shorten a one-hit combo further.' };
  }
  let next;
  if (options.atIndex != null) {
    if (options.atIndex < 0 || options.atIndex >= hits.length) {
      return { ok: false, error: `Hit index ${options.atIndex} is out of range.` };
    }
    next = hits.filter((_, index) => index !== options.atIndex);
  } else {
    const count = Math.max(1, countOrIndex);
    if (count >= hits.length) {
      return { ok: false, error: 'Cannot remove every hit from a combo.' };
    }
    next = hits.slice(0, hits.length - count);
  }
  const input = next.map((hit) => hit.token).join(',');
  return {
    ok: true,
    combo: { ...combo, input, displayInput: toDisplayInput(input), hits: next, custom: true },
  };
}

// Build a custom combo by chaining any moves together in any order.
// Not limited to Tekken's preset strings: the user creates their own.
// Each hit after the first is validated as a continuation (same stance
// as the first hit; its own direction, when present, must not clash).
// Returns { ok, combo } or { ok: false, error }.
export function buildCustomCombo(candidates) {
  if (!candidates || candidates.length === 0) {
    return { ok: false, error: 'A custom combo needs at least one move.' };
  }
  const firstContext = deriveSlotContext(candidates[0].input);
  for (let index = 1; index < candidates.length; index += 1) {
    const context = deriveSlotContext(candidates[index].input);
    if (context.stance !== 'unknown' && context.stance !== firstContext.stance) {
      return {
        ok: false,
        error: `Hit ${index + 1} (${candidates[index].displayInput || candidates[index].input}) is ${context.stance}, but this combo starts ${firstContext.stance}.`,
      };
    }
  }
  const hits = candidates.map((candidate) => ({
    token: candidate.input,
    displayToken: toDisplayInput(candidate.input),
    entryId: String(candidate.id),
    anim_ref: candidate.anim_ref || null,
    t3_row: candidate.t3_row ?? null,
  }));
  const input = hits.map((hit) => hit.token).join(',');
  return {
    ok: true,
    combo: {
      input,
      displayInput: toDisplayInput(input),
      hits,
      anim_refs: null,
      source: 'movelist_editor',
      custom: true,
    },
  };
}

// Add a validated custom combo to the editor's combo list.
export function addCombo(editor, combo) {
  if (!combo || !combo.input) return { ok: false, error: 'No combo to add.' };
  editor.combos.push(combo);
  editor.edits.push({ type: 'combo_add', input: combo.input, displayInput: combo.displayInput });
  editor.dirty = true;
  return { ok: true, combo };
}

// Replace one combo in the list (used after extendCombo/shortenCombo).
export function replaceCombo(editor, oldInput, combo) {
  const index = editor.combos.findIndex((item) => item.input === oldInput);
  if (index < 0) return { ok: false, error: `No combo with input ${oldInput}.` };
  editor.combos[index] = combo;
  editor.edits.push({ type: 'combo_replace', from: oldInput, to: combo.input });
  editor.dirty = true;
  return { ok: true, combo };
}

// ---------------------------------------------------------------------------
// Save: serialize, export, and build the GitHub API payload
// ---------------------------------------------------------------------------

// Serialize the editor state back to a moveset object. The original
// moveset object is never mutated: this clones it and touches ONLY
// `moves` entries for swapped slots, `strings` entries for changed or
// added combos, and adds a `movelist_editor` audit block. Every other
// top-level key (fighter, display, tekken_base, t3_bank, specials,
// frame_convention, slots, merge_sources, hit_words, and the rest)
// passes through untouched, so a save cannot clobber unrelated data.
// Note: the file's `slots` index is intentionally NOT rewritten here;
// the game's moveset loader rebuilds it from `moves`.
export function serializeMoveset(editor) {
  const out = JSON.parse(JSON.stringify(editor.moveset));
  for (const edit of editor.edits) {
    if (edit.type !== 'swap') continue;
    const candidate = editor.byId.get(String(edit.slot));
    if (!candidate) continue;
    // Special rows live in `specials`, not `moves`: match by the row's
    // original input and t3 row, then point it at the candidate's row.
    if (String(edit.slot).startsWith('special:') && Array.isArray(out.specials)) {
      const special = out.specials.find(
        (item) => item && item.input === edit.slotInput,
      );
      if (special && candidate.t3_row != null) special.t3_row = candidate.t3_row;
      continue;
    }
    if (!out.moves) continue;
    const original = out.moves[edit.slot];
    if (!original || typeof original !== 'object') continue;
    out.moves[edit.slot] = {
      ...original,
      name: candidate.name,
      anim_ref: candidate.anim_ref || original.anim_ref || null,
      t3_row: candidate.t3_row ?? original.t3_row ?? null,
      t3_source: candidate.t3_bank || original.t3_source || null,
      move_class: candidate.move_class || original.move_class || null,
      limb: candidate.limb || original.limb || null,
      input: edit.slotInput || original.input || edit.slot,
    };
  }
  // Custom / changed combos: replace the matching string entry, or
  // append when the input is new. Object strings keep their other
  // fields; bare string entries are replaced by an object entry that
  // records the editor as its source.
  const customCombos = editor.combos.filter((combo) => combo.custom);
  if (customCombos.length > 0 && Array.isArray(out.strings)) {
    for (const combo of customCombos) {
      const entry = {
        input: combo.input,
        hits: combo.hits.map((hit) => hit.token),
        t3_rows: combo.hits
          .map((hit) => hit.t3_row)
          .filter((row) => row != null),
        source: 'movelist_editor',
      };
      const index = out.strings.findIndex(
        (raw) => (typeof raw === 'string' ? raw : raw?.input) === combo.input,
      );
      if (index >= 0) out.strings[index] = entry;
      else out.strings.push(entry);
    }
  }
  out.movelist_editor = {
    edited: true,
    fighter: editor.fighter,
    edits: editor.edits,
    note: 'Edited in the Create-A-Move List editor. Validate by playing before treating any mapping as final.',
  };
  return out;
}

export function exportMovesetJSON(editor) {
  return `${JSON.stringify(serializeMoveset(editor), null, 2)}\n`;
}

// Payload for the host to send to the GitHub API (contents endpoint on
// a feature branch) to persist the fighter's moveset file. The editor
// itself performs no network call and holds no token: the host, which
// owns the GitHub connection, sends this payload. That keeps the save
// path exactly "GitHub API PR, never a local file write".
export function createSavePayload(editor) {
  const path = `game/assets/movesets/${editor.fighter}.json`;
  const content = exportMovesetJSON(editor);
  return {
    path,
    content,
    contentBase64:
      typeof Buffer !== 'undefined'
        ? Buffer.from(content, 'utf8').toString('base64')
        : btoa(unescape(encodeURIComponent(content))),
    message: `Create-A-Move List: edit ${editor.fighter} moveset`,
    branchNote: 'Commit on a feature branch and open a PR; never push to main.',
    edits: editor.edits,
  };
}

// ---------------------------------------------------------------------------
// Rendering (HTML string) and mounting (vanilla DOM, optional)
// ---------------------------------------------------------------------------

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// One row of the move list: move name, LP1/RP2/LK3/RK4 button input,
// exact animation reference, mapping status.
export function renderEntryRow(row) {
  return `<tr data-move-id="${escapeHtml(row.id)}">`
    + `<td>${escapeHtml(row.name)}</td>`
    + `<td>${escapeHtml(row.displayInput)}</td>`
    + `<td>${escapeHtml(row.animRefDisplay)}</td>`
    + `<td data-status="${escapeHtml(row.status)}">${escapeHtml(row.status)}`
    + (row.verification === 'input' ? ' (input, verify by playing)' : ' (clip-verified)')
    + `</td>`
    + `<td>${escapeHtml(row.reasons.join(' ') || '')}</td></tr>`;
}

export function renderEditorHTML(editor) {
  const rows = listAllMoves(editor);
  const counts = {};
  for (const row of rows) counts[row.status] = (counts[row.status] || 0) + 1;
  const comboRows = editor.combos
    .map((combo) => `<li>${escapeHtml(combo.displayInput)} (${combo.hits.length} hits${combo.custom ? ', custom' : ''})</li>`)
    .join('');
  return `<section class="movelist-editor" data-fighter="${escapeHtml(editor.fighter)}">`
    + `<h2>Create-A-Move List: ${escapeHtml(editor.display)}</h2>`
    + `<p>All moves, including wrongly mapped ones. Swap a move only to a slot whose context it matches: jumping slots take only jumping animations, crouching slots only crouching animations, standing slots only standing animations, grapple slots only grapple animations, and directional slots only animations matching that direction.</p>`
    + `<p>Status counts: ${Object.entries(counts).map(([status, count]) => `${escapeHtml(status)}: ${count}`).join(', ')}</p>`
    + `<table><thead><tr><th>Move name</th><th>Button input (LP1/RP2/LK3/RK4)</th><th>Exact animation</th><th>Mapping status</th><th>Notes</th></tr></thead>`
    + `<tbody>${rows.map(renderEntryRow).join('')}</tbody></table>`
    + `<h3>Combos</h3><ul>${comboRows}</ul>`
    + `<p class="movelist-editor-save-note">Save writes ${escapeHtml(`game/assets/movesets/${editor.fighter}.json`)} through the GitHub API on a feature-branch PR. Changes persist: fix it, save it, it stays fixed.</p>`
    + `</section>`;
}

// Mount the editor into a DOM element. Each move row gets a swap
// control populated ONLY with eligible (context-matching) candidates,
// plus extend/shorten controls on combos and a save button that hands
// the GitHub API payload to `onSave`. No-ops when `document` is absent
// (Node / tests), where the pure functions above are the interface.
export function mount(element, editor, options = {}) {
  if (typeof document === 'undefined' || !element) return null;
  const onSave = options.onSave || (() => {});
  const render = () => {
    element.innerHTML = renderEditorHTML(editor);
    const table = element.querySelector('table tbody');
    if (table) {
      for (const rowEl of table.querySelectorAll('tr')) {
        const moveId = rowEl.getAttribute('data-move-id');
        const entry = editor.byId.get(moveId);
        if (!entry) continue;
        const slotContext = deriveSlotContext(entry.input, {
          kind: entry.move_class === 'throw' ? 'grapple' : undefined,
        });
        const eligible = eligibleCandidates(slotContext, editor.entries);
        const cell = document.createElement('td');
        const select = document.createElement('select');
        select.setAttribute('aria-label', `Swap target for ${entry.displayInput}`);
        const placeholder = document.createElement('option');
        placeholder.value = '';
        placeholder.textContent = 'Swap to a matching move...';
        select.appendChild(placeholder);
        for (const candidate of eligible) {
          if (String(candidate.id) === String(moveId)) continue;
          const option = document.createElement('option');
          option.value = String(candidate.id);
          option.textContent = `${candidate.name} (${candidate.displayInput})`;
          select.appendChild(option);
        }
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = 'Swap';
        button.addEventListener('click', () => {
          if (!select.value) return;
          const result = swapMove(editor, moveId, select.value);
          const note = document.createElement('p');
          note.textContent = result.ok
            ? `Swapped ${moveId} to ${select.value} (${result.status}).`
            : (result.error || 'Swap blocked.');
          element.appendChild(note);
          render();
        });
        cell.appendChild(select);
        cell.appendChild(button);
        rowEl.appendChild(cell);
      }
    }
    const save = document.createElement('button');
    save.type = 'button';
    save.textContent = 'Save moveset (GitHub API PR)';
    save.addEventListener('click', () => onSave(createSavePayload(editor)));
    element.appendChild(save);
  };
  render();
  return { render, editor };
}
