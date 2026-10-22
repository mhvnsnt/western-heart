/* ============================================================
   WESTERN HEART — Intro Interaction System
   Tekken-style pre-fight character interactions — but VARIED:
   multiple different exchanges per matchup, rotating, never one
   fixed script per pairing. Builds backstory and canon over time.

   Contract: docs/INTRO-INTERACTION-SYSTEM.md
   • Data: INTRO_INTERACTIONS (pair key "a|b", ids sorted) — each pair
     holds MULTIPLE variants. GENERIC_INTROS — per-fighter solo beats
     used when no pair entry exists.
   • Selection: pickIntroInteraction() — random variant, never repeats
     the last-played variant for a pair; ctx flags (rivalry, storyState)
     can weight the pool. Pure logic — unit-testable, no DOM.
   • Presentation: playIntroInteraction() — in-engine, real-time (the two
     fighters are already spawned and idle in the arena; dialogue plays
     over the live scene). NOT pre-rendered video. Skippable.
   • Canon rule: every beat is grounded in CANON.md / docs / episodes.js.
     Beats that go beyond established canon are marked
     [NEEDS-OWNER-REVIEW] in the system doc — never presented as canon.
   ============================================================ */
import { voice } from './voice.js';

/* Beat: { speaker } = fighter id (or 'p1'/'p2' alias), { line } subtitle,
   { voice } = optional voice manifest clip id for that fighter. */

export const INTRO_INTERACTIONS = {
  /* ——— DOROWANI (pilot) ———
     Canon: kappa-yokai crocodile demon, Eastern Mind swamp, hungry
     mischievous trickster; speaks Japanese word bursts, no sentences.
     (Owner voice canon 2026-10-22.) */

  'dorowani|pantera': [
    { id: 'doro-pant-1', tags: ['first-meeting'], source: 'owner voice canon 2026-10-22',
      beats: [
        { speaker: 'dorowani', line: 'Konnichiwa!', voice: 'intro-01' },
        { speaker: 'pantera', line: '...It talks.' },
        { speaker: 'dorowani', line: 'Ichiban!', voice: 'intro-02' },
      ] },
    { id: 'doro-pant-2', tags: ['swamp'], source: 'owner voice canon 2026-10-22',
      beats: [
        { speaker: 'pantera', line: 'You smell like a swamp.' },
        { speaker: 'dorowani', line: 'Doro doro!', voice: 'intro-03' },
      ] },
  ],

  'demonio|dorowani': [
    { id: 'doro-dem-1', tags: ['first-meeting'],
      source: 'owner voice canon 2026-10-22; demonio discipline (episodes.js)',
      beats: [
        { speaker: 'demonio', line: 'A swamp spirit. Do you know why you were summoned?' },
        { speaker: 'dorowani', line: 'Konnichiwa!', voice: 'intro-01' },
        { speaker: 'demonio', line: '...I will take that as a no.' },
      ] },
    { id: 'doro-dem-2', tags: ['herald'],
      source: 'owner voice canon 2026-10-22',
      beats: [
        { speaker: 'dorowani', line: 'Dorowani!', voice: 'taunt-02' },
        { speaker: 'demonio', line: 'You announce yourself like a herald.' },
        { speaker: 'dorowani', line: 'Arigato!', voice: 'win-02' },
      ] },
  ],

  'dorowani|skull': [
    { id: 'doro-sku-1', tags: ['first-meeting'],
      source: 'owner voice canon 2026-10-22; skull "targets" (episodes.js)',
      beats: [
        { speaker: 'skull', line: 'Another target.' },
        { speaker: 'dorowani', line: 'Ichiban!', voice: 'intro-02' },
        { speaker: 'skull', line: '...Loud target.' },
      ] },
    { id: 'doro-sku-2', tags: ['size'],
      source: 'owner voice canon 2026-10-22; skull "targets" (episodes.js)',
      beats: [
        { speaker: 'skull', line: 'You are small.' },
        { speaker: 'dorowani', line: 'Doro doro!', voice: 'intro-03' },
        { speaker: 'skull', line: 'Small. Loud. Muddy.' },
      ] },
  ],

  /* ——— KEY MATCHUPS (canon-grounded) ——— */

  'demonio|diablo': [
    { id: 'dem-dia-1', tags: ['rivalry'],
      source: 'episodes.js: "He bows to every opponent. He has never once bowed to Diablo."',
      beats: [
        { speaker: 'demonio', line: 'I bow to every soul in this trial.' },
        { speaker: 'diablo', line: 'Then bow, little saint.' },
        { speaker: 'demonio', line: 'Not to you.' },
      ] },
    { id: 'dem-dia-2', tags: ['rivalry'],
      source: 'episodes.js: "the true demon versus the pretender"',
      beats: [
        { speaker: 'diablo', line: 'Still polishing that code, boy?' },
        { speaker: 'demonio', line: 'Still pretending to be what I refuse to become.' },
      ] },
  ],

  'demonio|pantera': [
    { id: 'dem-pan-1', tags: ['respect'],
      source: 'episodes.js: "the only soul he respects without reservation. PANTERA."',
      beats: [
        { speaker: 'demonio', line: 'If this trial is an exam, let the first question be the hardest one I admire.' },
        { speaker: 'pantera', line: 'Then ask.' },
      ] },
    { id: 'dem-pan-2', tags: ['respect'],
      source: 'episodes.js: demonio/Pantera respect [NEEDS-OWNER-REVIEW: Pantera lines are archetype-consistent, not quoted canon]',
      beats: [
        { speaker: 'demonio', line: 'I respect you too much to bow. You know what that costs me.' },
        { speaker: 'pantera', line: 'Fight like it.' },
      ] },
  ],

  'cyborgx|docfrank': [
    { id: 'doc-cyb-1', tags: ['family'],
      source: 'episodes.js: "CYBORG X: his daughter, his masterpiece... He pretends the pride is scientific. It is not."',
      beats: [
        { speaker: 'docfrank', line: 'Subject 9. Detachable parts, my stubbornness. State your hypothesis.' },
        { speaker: 'cyborgx', line: 'Hypothesis: the old man talks too much.' },
        { speaker: 'docfrank', line: '...Noted. For the paper.' },
      ] },
    { id: 'doc-cyb-2', tags: ['family'],
      source: 'episodes.js: docfrank/cyborgx [NEEDS-OWNER-REVIEW: lines are archetype-consistent, not quoted canon]',
      beats: [
        { speaker: 'cyborgx', line: 'Are you going to take notes while I hit you?' },
        { speaker: 'docfrank', line: 'I take notes ESPECIALLY while you hit me.' },
      ] },
  ],

  'docfrank|samura1': [
    { id: 'doc-sam-1', tags: ['the-question'],
      source: 'episodes.js: "SAM-UR-A1 keeps asking what it fights for... \\"data.\\""',
      beats: [
        { speaker: 'docfrank', line: 'SAM-UR-A1. What do you fight for?' },
        { speaker: 'samura1', line: 'Data.' },
        { speaker: 'docfrank', line: 'We will revisit this after I win.' },
      ] },
    { id: 'doc-sam-2', tags: ['the-question'],
      source: 'episodes.js: docfrank/samura1 "what do you fight for" dynamic (flipped)',
      beats: [
        { speaker: 'samura1', line: 'Query: what do YOU fight for, Doctor?' },
        { speaker: 'docfrank', line: '...Peer review. Next question.' },
        { speaker: 'samura1', line: 'Data.' },
      ] },
  ],

  'diablo|mariposa-monarch': [
    { id: 'dia-mar-1', tags: ['intruder'],
      source: 'episodes.js: "The intruder tore his way in... He knows. He performs for me." / "DIABLO — the crowbar"',
      beats: [
        { speaker: 'mariposa-monarch', line: 'You tore your way in here, crowbar.' },
        { speaker: 'diablo', line: 'And you watched, little locksmith.' },
        { speaker: 'mariposa-monarch', line: 'I watch everything. Especially you.' },
      ] },
    { id: 'dia-mar-2', tags: ['intruder'],
      source: 'episodes.js: mariposa keeper / diablo intruder [NEEDS-OWNER-REVIEW: lines are archetype-consistent, not quoted canon]',
      beats: [
        { speaker: 'diablo', line: 'Hatchling. The Tree leaks, and you blame the crowbar?' },
        { speaker: 'mariposa-monarch', line: 'I do not blame. I watch. And I remember.' },
      ] },
  ],
};

/* Per-fighter solo beats — used when the pair has no scripted exchange.
   Solo (one speaker) so we never put words in an arbitrary foe's mouth. */
export const GENERIC_INTROS = {
  dorowani: [
    { id: 'doro-gen-1', source: 'owner voice canon 2026-10-22',
      beats: [
        { speaker: 'dorowani', line: 'Konnichiwa!', voice: 'intro-01' },
        { speaker: 'dorowani', line: 'Arigato!', voice: 'win-02' },
      ] },
    { id: 'doro-gen-2', source: 'owner voice canon 2026-10-22',
      beats: [
        { speaker: 'dorowani', line: 'Ichiban!', voice: 'intro-02' },
        { speaker: 'dorowani', line: 'Bankai!', voice: 'win-01' },
      ] },
    { id: 'doro-gen-3', source: 'owner voice canon 2026-10-22',
      beats: [
        { speaker: 'dorowani', line: 'Doro doro!', voice: 'intro-03' },
        { speaker: 'dorowani', line: 'Dorowani!', voice: 'taunt-02' },
      ] },
  ],
};

const _lastVariant = new Map(); // pairKey -> variant id (no immediate repeats)

function _pickNoRepeat(key, variants) {
  if (!variants.length) return null;
  const last = _lastVariant.get(key);
  let pool = variants;
  if (variants.length > 1 && last) {
    const rest = variants.filter(v => v.id !== last);
    if (rest.length) pool = rest;
  }
  // ctx weighting: rivalry/story tags first when requested
  const v = pool[Math.floor(Math.random() * pool.length)];
  _lastVariant.set(key, v.id);
  return v;
}

/* Pure selection logic — no DOM, unit-testable.
   ctx: { rivalry?: boolean, storyState?: object (future) }
   Returns { kind: 'pair'|'generic'|'versus', variant?, fighter? }. */
export function pickIntroInteraction(p1Id, p2Id, ctx = {}) {
  const key = [p1Id, p2Id].sort().join('|');
  const variants = INTRO_INTERACTIONS[key];
  if (variants && variants.length) {
    let pool = variants;
    if (ctx.rivalry) {
      const tagged = variants.filter(v => (v.tags || []).includes('rivalry'));
      if (tagged.length) pool = tagged;
    }
    const v = _pickNoRepeat('pair:' + key, pool);
    return { kind: 'pair', key, variant: v };
  }
  const g = []
    .concat(GENERIC_INTROS[p1Id] || [])
    .concat(GENERIC_INTROS[p2Id] || []);
  if (g.length) {
    const v = _pickNoRepeat('generic:' + key, g);
    return { kind: 'generic', key, variant: v };
  }
  return { kind: 'versus', key }; // title-card fallback: names only, no invented words
}

export function _resetIntroMemory() { _lastVariant.clear(); } // tests

/* ---------------- presentation (in-engine, real-time) ---------------- */

const OVERLAY_ID = 'wh-intro';
const STYLE_ID = 'wh-intro-style';
let _overlay = null;

function _ensureStyle() {
  if (typeof document === 'undefined' || document.getElementById(STYLE_ID)) return;
  const st = document.createElement('style');
  st.id = STYLE_ID;
  st.textContent = `
#wh-intro { position: fixed; inset: 0; z-index: 214; display: none;
  align-items: flex-end; justify-content: center; pointer-events: auto;
  background: linear-gradient(180deg, rgba(10,5,18,.12) 0%, rgba(10,5,18,.82) 72%); }
#wh-intro.show { display: flex; }
.wh-intro-kicker { position: absolute; top: 7vh; left: 0; right: 0; text-align: center;
  color: var(--accent2, #b48cff); letter-spacing: 5px; font-size: 13px;
  text-shadow: 0 2px 12px #000; }
.wh-intro-name { color: var(--gold, #ffb14d); font-weight: 800; letter-spacing: 2px;
  font-size: 14px; margin-bottom: 6px; }
.wh-intro-line { color: #fff; font-size: 17px; line-height: 1.5; }
.wh-intro-hint { text-align: right; color: rgba(255,255,255,.4); font-size: 11px;
  margin-top: 10px; letter-spacing: 1px; }
.wh-intro-card { width: min(96vw, 620px); margin-bottom: max(6vh, 28px);
  background: var(--panel, rgba(20,12,32,.92)); border: 1px solid rgba(255,177,77,.4);
  border-radius: 14px; padding: 18px 20px; animation: wh-intro-in .3s ease; }
@keyframes wh-intro-in { from { transform: translateY(24px); opacity: 0; } }
.wh-intro-skip { position: absolute; bottom: max(6vh, 28px); right: 4vw;
  background: rgba(20,12,32,.8); color: #fff; border: 1px solid rgba(255,255,255,.25);
  border-radius: 10px; padding: 10px 16px; font-size: 12px; letter-spacing: 2px;
  min-height: 44px; }
@media (max-width: 520px) { .wh-intro-card { margin-bottom: 14px; padding: 14px; } }`;
  document.head.appendChild(st);
}

function _ensureOverlay() {
  if (_overlay || typeof document === 'undefined') return _overlay;
  _ensureStyle();
  _overlay = document.getElementById(OVERLAY_ID);
  if (_overlay) return _overlay;
  _overlay = document.createElement('div');
  _overlay.id = OVERLAY_ID;
  _overlay.setAttribute('aria-hidden', 'true');
  _overlay.innerHTML =
    '<div class="wh-intro-kicker">INTRODUCTION</div>' +
    '<div class="wh-intro-card">' +
    '<div class="wh-intro-name"></div>' +
    '<div class="wh-intro-line"></div>' +
    '<div class="wh-intro-hint">TAP TO CONTINUE</div>' +
    '</div>' +
    '<button class="wh-intro-skip" type="button">SKIP ▸▸</button>';
  document.body.appendChild(_overlay);
  return _overlay;
}

function _namesFor(p1char, p2char) {
  const m = {};
  if (p1char) m[p1char.id] = p1char.name || p1char.id;
  if (p2char) m[p2char.id] = p2char.name || p2char.id;
  return m;
}

/* Play the pre-fight interaction. Resolves when done or skipped.
   opts: { skip } — when true, resolves immediately (modes lane). */
export async function playIntroInteraction(game, p1char, p2char, opts = {}) {
  if (opts.skip) return { skipped: true };
  const p1Id = p1char && p1char.id, p2Id = p2char && p2char.id;
  if (!p1Id || !p2Id) return { skipped: true, reason: 'no-fighters' };
  const names = _namesFor(p1char, p2char);
  const ctx = { rivalry: !!(opts.rivalry || (game && game.introRivalry)) };
  const pick = pickIntroInteraction(p1Id, p2Id, ctx);

  const ov = _ensureOverlay();
  if (!ov) return { skipped: true, reason: 'no-dom' };
  const nameEl = ov.querySelector('.wh-intro-name');
  const lineEl = ov.querySelector('.wh-intro-line');

  let skipped = false;
  let advanceTap = null;
  let resolveSkip = null;
  const skipPromise = new Promise(r => { resolveSkip = r; });
  const onTap = (e) => {
    if (e && e.target && e.target.classList && e.target.classList.contains('wh-intro-skip')) {
      skipped = true;
      if (resolveSkip) resolveSkip();
      return;
    }
    if (advanceTap) { const f = advanceTap; advanceTap = null; f(); }
  };
  ov.addEventListener('click', onTap);
  const skipBtn = ov.querySelector('.wh-intro-skip');
  const onSkipBtn = () => { skipped = true; if (resolveSkip) resolveSkip(); };
  if (skipBtn) skipBtn.addEventListener('click', onSkipBtn);

  const showBeat = (speakerId, line) => {
    const label = names[speakerId] || String(speakerId || '').toUpperCase();
    nameEl.textContent = label;
    lineEl.textContent = line;
    ov.classList.add('show');
  };
  const hide = () => ov.classList.remove('show');

  try {
    if (pick.kind === 'versus') {
      // Title-card fallback: no scripted words, just the matchup.
      showBeat('', `${names[p1Id]}  ⚔  ${names[p2Id]}`);
      await Promise.race([
        new Promise(r => setTimeout(r, 1400)),
        skipPromise,
      ]);
      return { kind: 'versus', skipped };
    }
    const beats = pick.variant.beats;
    for (const b of beats) {
      if (skipped) break;
      const speaker = b.speaker === 'p1' ? p1Id : b.speaker === 'p2' ? p2Id : b.speaker;
      showBeat(speaker, b.line);
      // Voice line plays; tap races it so the beat stays snappy, and the
      // skip button races the whole interaction.
      const lineDone = voice.playLine(speaker, b.voice, b.line);
      await Promise.race([
        lineDone.then(() => 'line'),
        skipPromise.then(() => 'skip'),
        new Promise(r => { advanceTap = r; }),
      ]);
      if (skipped) break;
    }
    return { kind: pick.kind, variant: pick.variant.id, skipped };
  } finally {
    hide();
    ov.removeEventListener('click', onTap);
    if (skipBtn) skipBtn.removeEventListener('click', onSkipBtn);
  }
}
