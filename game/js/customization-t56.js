/* ============================================================
   WESTERN HEART — Creation Suite: T5/T6 customization data model
   (Lane 6, story + canon, 2026-10-24 — system data + canon
   framing only. The UI lane owns the menus; this module owns the
   slot taxonomy, the conflict rules, and the validation that the
   suite and the in-fight consumer share.)

   WHAT WAS PULLED (structure only, no meshes, no Tekken names
   in-game):
   • T5 base (2004): four buyable item categories — head, face,
     upper body, lower body — plus per-character colour zones and
     full costumes, bought with fight money ("G") earned in play
     (GameSpy T5 preview; FunTrivia T5 quiz: "four types of items:
     head, face, upper body, lower body"). Each category held
     ~five items per character in T5; the categories are the
     structure, the counts are T5's, not WH's.
   • T6 expansion: the same four categories widen into per-part
     slots — hairstyle, hair accessory, glasses, facial hair,
     face paint / make-up, upper accessory, lower accessory,
     extra — as shown by T6 item lists (e.g. Julia Chang T6 items:
     cowgirl hat/gloves/top, face paints, suspenders, holsters,
     tribal tops) and by the later-Tekken slot table below.
   • T6 PSP, from the FULL FILES (not a community approximation):
     teardown/tekken6-customization-research.md (2026-10-16) —
     decrypted T6 PSP EBOOT item-name tables (10,495 records) and
     NTXL string tables. Confirmed T6 categories include the hair
     split (Hair - Back, Hair - Front (Right)) and Face - Other,
     and item names include Ki / Aura / Effect / Comic Effect /
     SP Rage variants. So Aura and Effects are era 't6' here
     (T6 PSP items), NOT later-Tekken-only. "SP Rage" is an
     effect-item name in that table — it is NOT the Rage combat
     system, and the two must never be conflated.
   • Later-Tekken slot table (T7, TekkenMods TKDataPatcher docs):
     HEAD, HAIR, FULL_HEAD, HAIR_ACC, GLA, FACE, FACE_HAIR,
     MAKE_UP, UPPER, FULL_BODY, LOWER, UPPER_ACC, LOWER_ACC,
     EXTRA, plus Effects and Aura. Used here as a COMPLETENESS
     cross-check for the taxonomy, not as an era claim: every
     slot below is era 't5' or 't6' on the evidence above.

   CONSUMER WIRING: game/js/customization-consumer.js already
   resolves suite profiles by slot key against merged catalogs
   and notes "Tekken 5/6 catalogs are picked up automatically
   when the gap-closure lane lands them". This module IS that
   landing: profile `parts` keys MUST be slot ids from T56_SLOTS.
   Catalog entries (meshes) arrive from the parts lane keyed by
   the same ids; this module carries no meshes.

   CANON FRAMING (split honestly):
   • CANON-ANCHORED: the face slots (eyes, nose, mouth, face,
     facial-hair, face-paint). Canon: the Reincarnation gives a
     soul "three pairs of eyes, three noses, three mouths" and
     "the face is not cosmetic. Sharper eyes, faster hands. A
     heavier nose, heavier hits" (CANON.md L48-50, L1342). The
     Reincarnation is "the only character creator the Western
     Heart has ever needed" (CANON.md L1342). Face slots ARE
     that creator, in suite form.
   • SYSTEM: every other slot (head, hair, body, accessories,
     colours, effects, aura). These are trial attire and suite
     mechanics. They are NOT given a canon location, being, or
     backstory here — a jacket is a jacket, not a lore object.
     (The Trader's marketplace trades elemental forces, CANON.md
     L477-481 — it is NOT cited as a clothing shop, because
     canon never says that.)

   Dependency-free (browser + Node).
   ============================================================ */

/* Slot: { id, label, era, group, conflicts[], canon }
   era: 't5' (T5's four categories) | 't6' (T6 expansion, incl.
     T6 PSP full-file evidence).
   group: 'face' | 'head' | 'body' | 'colour' | 'layer'.
   conflicts: slot ids that cannot be worn at the same time
     (full-piece slots replace their component slots).
   canon: 'CANON-ANCHORED' | 'SYSTEM' (see header). */
export const T56_SLOTS = [
  // --- T5 base: the four categories ---
  { id: 'head', label: 'Head', era: 't5', group: 'head', conflicts: ['full-head'], canon: 'SYSTEM' },
  { id: 'face', label: 'Face', era: 't5', group: 'face', conflicts: [], canon: 'CANON-ANCHORED' },
  { id: 'upper-body', label: 'Upper Body', era: 't5', group: 'body', conflicts: ['full-body'], canon: 'SYSTEM' },
  { id: 'lower-body', label: 'Lower Body', era: 't5', group: 'body', conflicts: ['full-body'], canon: 'SYSTEM' },
  // --- T5 colours + full costumes ---
  { id: 'colours', label: 'Colours', era: 't5', group: 'colour', conflicts: [], canon: 'SYSTEM' },
  { id: 'costume', label: 'Full Costume', era: 't5', group: 'body', conflicts: ['head', 'face', 'upper-body', 'lower-body', 'hairstyle', 'glasses', 'upper-accessory', 'lower-accessory'], canon: 'SYSTEM' },
  // --- T6 expansion: head/face detail ---
  { id: 'hairstyle', label: 'Hairstyle', era: 't6', group: 'head', conflicts: ['full-head', 'hair-back', 'hair-front'], canon: 'SYSTEM' },
  // T6 PSP split form (decrypted EBOOT / NTXL categories): front
  // and back coexist with each other, not with the combined slot.
  { id: 'hair-back', label: 'Hair - Back', era: 't6', group: 'head', conflicts: ['full-head', 'hairstyle'], canon: 'SYSTEM' },
  { id: 'hair-front', label: 'Hair - Front', era: 't6', group: 'head', conflicts: ['full-head', 'hairstyle'], canon: 'SYSTEM' },
  { id: 'full-head', label: 'Full Head', era: 't6', group: 'head', conflicts: ['head', 'hairstyle', 'hair-accessory'], canon: 'SYSTEM' },
  { id: 'hair-accessory', label: 'Hair Accessory', era: 't6', group: 'head', conflicts: ['full-head'], canon: 'SYSTEM' },
  { id: 'glasses', label: 'Glasses', era: 't6', group: 'face', conflicts: [], canon: 'SYSTEM' },
  { id: 'facial-hair', label: 'Facial Hair', era: 't6', group: 'face', conflicts: [], canon: 'CANON-ANCHORED' },
  { id: 'face-other', label: 'Face - Other', era: 't6', group: 'face', conflicts: [], canon: 'SYSTEM' },
  { id: 'face-paint', label: 'Face Paint / Make-up', era: 't6', group: 'face', conflicts: [], canon: 'CANON-ANCHORED' },
  // --- T6 expansion: body accessories ---
  { id: 'full-body', label: 'Full Body', era: 't6', group: 'body', conflicts: ['upper-body', 'lower-body', 'upper-accessory', 'lower-accessory'], canon: 'SYSTEM' },
  { id: 'upper-accessory', label: 'Upper Accessory', era: 't6', group: 'body', conflicts: ['full-body'], canon: 'SYSTEM' },
  { id: 'lower-accessory', label: 'Lower Accessory', era: 't6', group: 'body', conflicts: ['full-body'], canon: 'SYSTEM' },
  { id: 'extra', label: 'Extra', era: 't6', group: 'body', conflicts: [], canon: 'SYSTEM' },
  // --- Reincarnation face assembly (canon sub-slots) ---
  // CANON.md L48-50, L1342: eyes, nose, mouth are chosen in
  // pieces at the Reincarnation. These are sub-slots of `face`:
  // they refine it, they do not conflict with it.
  { id: 'eyes', label: 'Eyes', era: 't6', group: 'face', conflicts: [], canon: 'CANON-ANCHORED' },
  { id: 'nose', label: 'Nose', era: 't6', group: 'face', conflicts: [], canon: 'CANON-ANCHORED' },
  { id: 'mouth', label: 'Mouth', era: 't6', group: 'face', conflicts: [], canon: 'CANON-ANCHORED' },
  // --- T6 PSP effect layer (full-file evidence, see header) ---
  // Item names in the decrypted T6 PSP tables: Ki, Aura, Effect,
  // Comic Effect, SP Rage variants. Layer slots, no conflicts.
  { id: 'effects', label: 'Effects', era: 't6', group: 'layer', conflicts: [], canon: 'SYSTEM' },
  { id: 'aura', label: 'Aura', era: 't6', group: 'layer', conflicts: [], canon: 'SYSTEM' },
];

export function slotById(id) {
  return T56_SLOTS.find((s) => s.id === id) || null;
}

export function slotsByEra(era) {
  return T56_SLOTS.filter((s) => s.era === era);
}

/* Validate a suite profile's `parts` map ({ slotId: part }).
   Returns { ok, unknown[], conflicts[] } where each conflict is
   { slot, conflictsWith }. Unknown slot ids are reported, never
   silently dropped — the UI lane decides how to surface them. */
export function validateCustomization(parts) {
  const ids = Object.keys(parts || {});
  const unknown = ids.filter((id) => !slotById(id));
  const conflicts = [];
  for (const id of ids) {
    const slot = slotById(id);
    if (!slot) continue;
    for (const other of slot.conflicts) {
      if (ids.includes(other)) conflicts.push({ slot: id, conflictsWith: other });
    }
  }
  // De-duplicate symmetric pairs (full-head<>head reported once
  // from the full-piece side is enough; keep both directions out).
  const seen = new Set();
  const deduped = [];
  for (const c of conflicts) {
    const key = [c.slot, c.conflictsWith].sort().join('|');
    if (seen.has(key)) continue;
    seen.add(key);
    deduped.push(c);
  }
  return { ok: unknown.length === 0 && deduped.length === 0, unknown, conflicts: deduped };
}
