/* ============================================================
   WESTERN HEART — Versus Banter
   Extends game/js/intro-interactions.js: where intros are the varied
   pre-fight exchange, VERSUS BANTER is the short, punchy 1–2 beat
   dialogue on the VERSUS screen itself — the last words before the
   Trial begins. Same beat contract { speaker, line, voice? }, same
   pair-key convention (ids sorted, "a|b"), same no-repeat selection.
   Canon rule (inherited): every beat grounded in CANON.md / docs /
   episodes.js / owner voice canon. Beats beyond established canon are
   marked [NEEDS-OWNER-REVIEW]; pairs whose fighter is not in the game
   yet are marked [AWAITING-FIGHTER] — data first, playable on arrival.
   The canon web (owner 2026-10-22):
     Jotei → Ryusan → Tobi → Pond → Dorowani → Chatur → Megami →
     Menajerii → Zen
   Notes: DOROWANI speaks ONLY Japanese word bursts, never sentences
   (owner voice canon 2026-10-22). RYUSAN is 15 (owner-authorized minor
   character) — all writing kept strictly to the crimes/truth, nothing
   else. ZEN is the still soul: "Stillness does not compete."
   ============================================================ */

/* Lazy intro fallback (worker 13's system) — dynamic import so this module
   stays node-testable and never hard-fails when the intro system is absent. */
async function _introFallback(p1Id, p2Id, ctx) {
  try {
    const m = await import('./intro-interactions.js');
    return { kind: 'intro-fallback', intro: m.pickIntroInteraction(p1Id, p2Id, ctx) };
  } catch {
    return { kind: 'intro-fallback', intro: { kind: 'versus', key: [p1Id, p2Id].sort().join('|') } };
  }
}

/* VERSUS_BANTER: pair key -> variants. Shorter than intros: 2-4 beats. */
export const VERSUS_BANTER = {
  /* ——— THE CANON WEB ——— */

  'jotei|ryusan': [ // [AWAITING-FIGHTER: jotei, ryusan]
    { id: 'jot-ryu-1', tags: ['crimes'], status: 'AWAITING-FIGHTER',
      source: 'intake canon: Jotei family soul-binding crimes; Ryusan is the living proof',
      beats: [
        { speaker: 'jotei', line: 'You carry my family\'s signature in your scars, child.' },
        { speaker: 'ryusan', line: 'Then read them out loud. Let the whole Trial hear what your family writes.' },
        { speaker: 'jotei', line: 'I came to collect. I did not come to confess.' },
      ] },
    { id: 'jot-ryu-2', tags: ['crimes'], status: 'AWAITING-FIGHTER',
      source: 'intake canon [NEEDS-OWNER-REVIEW: lines are archetype-consistent]',
      beats: [
        { speaker: 'ryusan', line: 'Acid remembers, Empress. It remembers every hand that held it.' },
        { speaker: 'jotei', line: 'Then we will see whose hands the Trial remembers.' },
      ] },
  ],

  'ryusan|tobi': [ // [AWAITING-FIGHTER: ryusan, tobi]
    { id: 'ryu-tob-1', tags: ['tip-off'], status: 'AWAITING-FIGHTER',
      source: 'intake canon: Tobi tipped off Ryusan',
      beats: [
        { speaker: 'tobi', line: 'You got my message, then. Fastest delivery I ever made.' },
        { speaker: 'ryusan', line: 'Fastest mouth, too. Now run — this part burns.' },
      ] },
    { id: 'ryu-tob-2', tags: ['tip-off'], status: 'AWAITING-FIGHTER',
      source: 'intake canon [NEEDS-OWNER-REVIEW]',
      beats: [
        { speaker: 'ryusan', line: 'Why warn me, courier? What\'s my truth worth to you?' },
        { speaker: 'tobi', line: 'Nothing. That\'s why I carried it free.' },
      ] },
  ],

  'pond|tobi': [ // [AWAITING-FIGHTER: pond, tobi]
    { id: 'pon-tob-1', tags: ['boundary'], status: 'AWAITING-FIGHTER',
      source: 'intake canon: Pond is the swamp boundary watcher',
      beats: [
        { speaker: 'tobi', line: 'Boundary coming up — I\'m through quick, no trouble.' },
        { speaker: 'pond', line: 'Everyone says quick. The swamp decides quick.' },
      ] },
  ],

  'dorowani|pond': [ // [AWAITING-FIGHTER: pond]
    { id: 'dor-pon-1', tags: ['egg'], status: 'AWAITING-FIGHTER',
      source: 'intake canon: Pond found Dorowani as an egg; owner voice canon (word bursts only)',
      beats: [
        { speaker: 'pond', line: 'I found you in the mud, smaller than my palm.' },
        { speaker: 'dorowani', line: 'Doro doro!', voice: 'intro-03' },
        { speaker: 'pond', line: 'Still loud. Still mine to watch.' },
      ] },
    { id: 'dor-pon-2', tags: ['egg'], status: 'AWAITING-FIGHTER',
      source: 'intake canon; owner voice canon [NEEDS-OWNER-REVIEW: Pond lines archetype-consistent]',
      beats: [
        { speaker: 'dorowani', line: 'Konnichiwa!', voice: 'intro-01' },
        { speaker: 'pond', line: 'Manners first, teeth second. Like I taught you.' },
        { speaker: 'dorowani', line: 'Ichiban!', voice: 'intro-02' },
      ] },
  ],

  'chatur|dorowani': [ // [AWAITING-FIGHTER: chatur]
    { id: 'cha-dor-1', tags: ['spirit'], status: 'AWAITING-FIGHTER',
      source: 'intake canon: Chatur anchors the spirit realm; owner voice canon',
      beats: [
        { speaker: 'chatur', line: 'Little hunger-spirit. The temple dancer sees your four hungers.' },
        { speaker: 'dorowani', line: 'Bankai!', voice: 'win-01' },
        { speaker: 'chatur', line: 'Refused to die, did you? We have that in common.' },
      ] },
  ],

  'chatur|megami': [ // [AWAITING-FIGHTER: chatur, megami]
    { id: 'cha-meg-1', tags: ['teacher'], status: 'AWAITING-FIGHTER',
      source: 'intake canon: Megami trained Chatur; grief in motion',
      beats: [
        { speaker: 'megami', line: 'You dance like I taught you. You grieve like I taught you too.' },
        { speaker: 'chatur', line: 'Then grade me, teacher. Four arms, no excuses.' },
      ] },
    { id: 'cha-meg-2', tags: ['sealed-door'], status: 'AWAITING-FIGHTER',
      source: 'intake canon: Megami guards a sealed door [NEEDS-OWNER-REVIEW]',
      beats: [
        { speaker: 'chatur', line: 'What\'s behind your door, Megami?' },
        { speaker: 'megami', line: 'The reason I never stop moving. Ask with your fists.' },
      ] },
  ],

  'megami|menajerii': [ // [AWAITING-FIGHTER: megami, menajerii]
    { id: 'meg-men-1', tags: ['spirits'], status: 'AWAITING-FIGHTER',
      source: 'intake canon: Menajerii carries beast spirits; Megami anchors temple grief',
      beats: [
        { speaker: 'menajerii', line: 'My passengers want to see your door, guardian.' },
        { speaker: 'megami', line: 'Then they can wait with me. Waiting is the whole art.' },
      ] },
  ],

  'menajerii|zen': [ // [AWAITING-FIGHTER: menajerii] — zen IS in game
    { id: 'men-zen-1', tags: ['stillness'], status: 'AWAITING-FIGHTER',
      source: 'CANON.md: ZEN — "Stillness does not compete."',
      beats: [
        { speaker: 'menajerii', line: 'So many beasts in me, and you — nothing moves in you at all.' },
        { speaker: 'zen', line: '...' },
        { speaker: 'menajerii', line: 'Right. Stillness. I\'ll take the hint.' },
      ] },
  ],

  /* ——— PLAYABLE NOW ——— */

  'dorowani|zen': [
    { id: 'dor-zen-1', tags: ['stillness'], status: 'PLAYABLE',
      source: 'CANON.md ZEN stillness; owner voice canon (Dorowani word bursts)',
      beats: [
        { speaker: 'dorowani', line: 'Konnichiwa!', voice: 'intro-01' },
        { speaker: 'zen', line: '...' },
        { speaker: 'dorowani', line: 'Doro doro?', voice: 'intro-03' },
      ] },
    { id: 'dor-zen-2', tags: ['motion'], status: 'PLAYABLE',
      source: 'CANON.md: GYOU is motion, ZEN is stillness [NEEDS-OWNER-REVIEW: Zen silence as beat]',
      beats: [
        { speaker: 'dorowani', line: 'Ichiban Bankai!', voice: 'win-01' },
        { speaker: 'zen', line: 'Stillness does not compete.' },
        { speaker: 'dorowani', line: 'Arigato!', voice: 'win-02' },
      ] },
  ],

  'jotei|zen': [ // [AWAITING-FIGHTER: jotei] — zen IS in game
    { id: 'jot-zen-1', tags: ['collect'], status: 'AWAITING-FIGHTER',
      source: 'intake canon: Jotei "coming to collect"; CANON.md ZEN refused the trial',
      beats: [
        { speaker: 'jotei', line: 'Even you, still one. The Trial collects us all.' },
        { speaker: 'zen', line: 'Stillness does not compete.' },
        { speaker: 'jotei', line: 'Then be still somewhere else, soul.' },
      ] },
  ],
};

/* Playable-now pairs (both fighters have roster entries). */
export function playableBanterPairs() {
  return Object.keys(VERSUS_BANTER).filter(k =>
    VERSUS_BANTER[k].some(v => v.status === 'PLAYABLE'));
}

const _lastBanter = new Map();
function _pickNoRepeat(key, variants) {
  if (!variants.length) return null;
  const last = _lastBanter.get(key);
  let pool = variants;
  if (variants.length > 1 && last) {
    const rest = variants.filter(v => v.id !== last);
    if (rest.length) pool = rest;
  }
  const v = pool[Math.floor(Math.random() * pool.length)];
  _lastBanter.set(key, v.id);
  return v;
}

/* Pure selection. Returns { kind:'banter', variant } | { kind:'fallback' }.
   Falls back to the intro-interaction picker for unscripted pairs.
   NOTE: async — the intro fallback lazy-loads worker 13's module. */
export async function pickVersusBanter(p1Id, p2Id, ctx = {}) {
  const key = [p1Id, p2Id].sort().join('|');
  const variants = (VERSUS_BANTER[key] || []).filter(v => v.status === 'PLAYABLE');
  if (variants.length) {
    return { kind: 'banter', key, variant: _pickNoRepeat('banter:' + key, variants) };
  }
  // fall back to worker 13's intro system (title-card 'versus' when unscripted)
  return _introFallback(p1Id, p2Id, ctx);
}
export function _resetBanterMemory() { _lastBanter.clear(); } // tests

/* Versus-screen presentation: compact 2-line card over the live scene.
   Reuses the intro overlay contract; resolves when done or skipped. */
export async function playVersusBanter(p1char, p2char, opts = {}) {
  const pick = pickVersusBanter(p1char && p1char.id, p2char && p2char.id, opts);
  if (pick.kind !== 'banter') return { kind: pick.kind, played: false };
  if (typeof document === 'undefined') return { kind: 'banter', variant: pick.variant.id, played: true, headless: true };
  // Minimal versus card — the full intro system owns the long-form overlay.
  return { kind: 'banter', variant: pick.variant.id, beats: pick.variant.beats, played: true };
}
