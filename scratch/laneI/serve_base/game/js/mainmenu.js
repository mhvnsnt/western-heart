/* ============================================================
   WESTERN HEART — T8-style main menu controller (worker 37)
   Drives the Tekken 8-adapted main menu: rail list, slide-in
   submenus, player card, Soul Urge pips, "in the forge" panels,
   news ticker.

   Wiring contract (additive):
   - menus.js calls initMainMenu() once from initMenus().
   - Working mode cards carry data-action="mode-*" and are routed
     by main.js's delegated data-action listener (covers dynamic
     cards) and menus.js's delegated special-action listener
     (mode-heartmind / mode-episodes / mode-options / mode-records).
   - Ranked modes ride worker 30's rank system (js/ranks.js +
     game/data/ranks.json): mode-rankbattle starts Rank Battle,
     show-ranks opens the Rank Hall (53-tier ladder). Rank names
     are NEVER hardcoded here — the JSON is the source of truth.
   - Modes still being built open the forge panel — visible,
     honest, T8-locked-content style.
   ============================================================ */
import { audio } from './audio.js';
import { lazy } from './lazy.js';
import { openVersusSetup, initVersusSetup } from './versus-setup.js';

/* ---------------- Player state ---------------- */
const PLAYER_KEY = 'wh_player_v1';
export function getPlayer() {
  try {
    return {
      name: 'WANDERER', title: 'Lost Soul',
      ...(JSON.parse(localStorage.getItem(PLAYER_KEY)) || {}),
    };
  } catch { return { name: 'WANDERER', title: 'Lost Soul' }; }
}
export function setPlayer(patch) {
  try {
    localStorage.setItem(PLAYER_KEY, JSON.stringify({ ...getPlayer(), ...patch }));
  } catch { /* private mode */ }
  renderTopbar();
}

const TITLES = [
  'Lost Soul', 'Shrine Drifter', 'Trial Walker', 'Nine-Soul Seeker',
  'Soul Forger', 'Heart of the West', 'Mind of the East',
  'Trader\'s Bane', 'Qombat Survivor', 'Assembled',
];

/* ---------------- Submenu data ----------------
   card: { t, d, badge: 'live'|'hot'|'soon', action } — action is a
   data-action routed by the existing delegated handlers;
   { forge } opens the forge dialog. */
const SUBMENUS = {
  story: { title: 'STORY', cards: [
    { t: 'THE TRIAL', d: 'Seven lands. Five forces. Death is not failure — it is reincarnation. Climb to the Shrine and face the Assembled Soul.', badge: 'live', action: 'mode-story' },
    { t: 'CHARACTER EPISODES', d: 'Every soul, their story. Short cinematic ladders for the whole roster.', badge: 'live', action: 'mode-episodes' },
    { t: 'HEART AND MIND WITHIN', d: 'Per-character 3D beat-em-up campaigns, Tekken 5 Devil Within style. Pick a soul and descend.', badge: 'hot', action: 'mode-heartmind' },
  ]},
  versus: { title: 'VERSUS', cards: [
    { t: '1V1 VERSUS', d: 'Two souls, one shrine. Local versus — set the rules, then fight.', badge: 'live', setup: 'versus' },
    { t: 'TEAM BATTLE', d: 'Pick 3 fighters. Winner stays on. Tekken Tag rules, Western Heart souls.', badge: 'live', action: 'mode-team' },
  ]},
  online: { title: 'ONLINE', cards: [
    { t: 'RANKED BATTLE', d: 'Offline ranked vs the CPU. Wins and losses move your per-character rank — promotion series are best-of-N.', badge: 'live', action: 'mode-rankbattle' },
    { t: 'RANK HALL', d: 'The full 53-tier ladder, offline and online tracks, leaderboards. Your climb, carved in the shrine stones.', badge: 'live', action: 'show-ranks' },
    { t: 'TOURNAMENT', d: 'Single-elimination brackets, local and online. Eight souls enter.', badge: 'soon', forge: 'tournament' },
  ]},
  arcade: { title: 'ARCADE', cards: [
    { t: 'ARCADE LADDER', d: 'Six fights. One life. Diablo waits near the top… almost.', badge: 'live', action: 'mode-arcade' },
    { t: 'SURVIVAL', d: 'One round each, health carries over. How many souls can you put down?', badge: 'live', action: 'mode-survival' },
    { t: 'TIME ATTACK', d: 'Eight fights, one round each, against the clock. Go fast.', badge: 'live', action: 'mode-timeattack' },
    { t: 'SOUL SURGE GAUNTLET', d: 'Nine fights. Nine souls will channel through you.', badge: 'hot', action: 'mode-surge' },
  ]},
  sidegames: { title: 'SIDE GAMES', cards: [
    { t: '不死 QOMBAT', d: "Sun Rā's realm. No reincarnation here. Win and eat — or be eaten.", badge: 'hot', action: 'mode-qombat' },
    { t: "TRADER'S MIMIC", d: 'Three bouts. The Trader wears your moveset like a borrowed coat.', badge: 'live', action: 'mode-trader' },
  ]},
  training: { title: 'TRAINING', cards: [
    { t: 'TRAINING', d: 'Pick your fighter. The dummy will not fight back. Drill strings, punishment, Soul Surge.', badge: 'live', action: 'mode-training' },
    { t: 'GUNGAKU FIGHT LAB', d: '軍楽 — the programmable training dummy. Record sequences, set reactions, compose your war music.', badge: 'live', action: 'mode-fightlab' },
  ]},
  collection: { title: 'COLLECTION', cards: [
    { t: 'GALLERY', d: 'Unlocked endings, concept art, arena drafts. The archive of the shrine.', badge: 'soon', forge: 'gallery' },
    { t: 'JUKEBOX', d: 'Every stage theme, every character motif. The shrine\'s setlist.', badge: 'soon', forge: 'jukebox' },
    { t: 'REPLAYS', d: 'Save your fights. Study the tape. Steal your own habits back.', badge: 'soon', forge: 'replays' },
  ]},
  options: { title: 'OPTIONS', cards: [
    { t: 'OPTIONS', d: 'Sound, graphics, controls.', badge: 'live', action: 'mode-options' },
    { t: 'PLAYER CARD', d: 'Your name, your title. Shown on the top bar, the VS screen and the leaderboards.', badge: 'live', panel: 'card' },
    { t: 'RECORDS', d: 'Local legends, carved in the shrine stones.', badge: 'live', action: 'mode-records' },
    { t: 'HOW TO PLAY', d: 'Limbs, throws, Soul Surge. The whole shrine manual.', badge: 'live', action: 'howto' },
  ]},
};

const FORGE = {
  daily: { title: 'DAILY CHALLENGES', desc: 'A new trial every day at midnight: a fixed fighter, a fixed foe, one cruel modifier. Streaks earn exclusive titles. The challenge board is being carved — check back tomorrow.' },
  tournament: { title: 'TOURNAMENT', desc: 'Single-elimination brackets for eight souls — local pass-and-play first, online brackets to follow. The brackets are being drawn.' },
  gungaku: { title: 'GUNGAKU FIGHT LAB', desc: '軍楽 — "war music". The programmable training dummy: record the dummy\'s sequences, script its reactions, drill your punishment until it sings. The composition is underway.' },
  gallery: { title: 'GALLERY', desc: 'Endings, concept art, arena drafts, the T8 select grid decodes — the shrine\'s archive is being hung on the walls.' },
  jukebox: { title: 'JUKEBOX', desc: 'Stage themes, character motifs, the Trader\'s market loop. The setlist is being pressed.' },
  replays: { title: 'REPLAYS', desc: 'Save fights, scrub the timeline, steal your own habits back. The recorder is being threaded.' },
};

const NEWS = [
  'RANKED SEASON 1 — climb all 53 tiers from Lost Soul',
  'NEW — Heart and Mind Within: per-soul beat-em-up campaigns',
  'IN THE FORGE — Gungaku fight lab, Daily Challenges, Tournament',
  'SOUL URGE is live — fill all 9 souls, then unleash it',
];

/* ---------------- DOM helpers ---------------- */
const $ = (id) => document.getElementById(id);
const click = () => { try { audio.uiClick && audio.uiClick(); } catch { /* no audio yet */ } };

/* ---------------- Touch tap (2026-10-24, menu tap fix) ----------------
   Phone taps must navigate even when the browser does not synthesize a
   click for the tap (suppressed compatibility mouse event, a touch-action
   conflict, or a slow module graph). tap() binds touchend WITH a
   scroll-drag guard: a finger that moved >12px was scrolling, not
   tapping, so it does not fire. On a real tap it preventDefaults the
   emulated click and runs the handler once; the click listener stays
   for mouse/keyboard and is deduped against the touch within 600ms.
   Data-action elements are NOT bound here on purpose: the document-level
   router in main.js owns them, and main.js also re-dispatches them on
   touchend — binding them here too would double-fire. */
let _lastTapAt = 0;
function tap(el, fn) {
  if (!el) return;
  let sx = 0, sy = 0;
  el.addEventListener('touchstart', (e) => {
    const t = e.changedTouches[0];
    if (t) { sx = t.clientX; sy = t.clientY; }
  }, { passive: true });
  el.addEventListener('touchend', (e) => {
    const t = e.changedTouches[0];
    if (t && Math.hypot(t.clientX - sx, t.clientY - sy) > 12) return; // scroll drag, not a tap
    e.preventDefault(); // suppress the emulated click — the handler runs now
    _lastTapAt = Date.now();
    fn(e);
  }, { passive: false });
  el.addEventListener('click', (e) => {
    if (Date.now() - _lastTapAt < 600) return; // touch already ran this tap
    fn(e);
  });
}

/* ---------------- Top bar ---------------- */
function renderTopbar() {
  const p = getPlayer();
  const nameEl = $('mm-pname'), titleEl = $('mm-ptitle'), avEl = $('mm-avatar');
  if (nameEl) nameEl.textContent = (p.name || 'WANDERER').toUpperCase();
  if (titleEl) titleEl.textContent = p.title || 'Lost Soul';
  if (avEl) avEl.textContent = ((p.name || 'W')[0] || 'W').toUpperCase();
  // Soul Urge pips: the Nine-Soul Meter's menu surface. Unlit at rest —
  // they ignite in-fight as souls fill (see fighter.js).
  const pips = $('mm-pips');
  if (pips && !pips.children.length) {
    for (let i = 0; i < 9; i++) pips.appendChild(document.createElement('i'));
  }
  refreshRankBadge();
}

/* Best offline/online rank across the roster, from worker 30's store.
   Rank names come from game/data/ranks.json — never hardcoded here. */
let _rankRefresh = null;
export function refreshRankBadge() {
  const rn = $('mm-rank-name'), rs = $('mm-rank-sub');
  if (!rn) return;
  if (_rankRefresh) return _rankRefresh;
  _rankRefresh = (async () => {
    try {
      const r = await lazy.ranks();
      await r.initRanks();
      const store = JSON.parse(localStorage.getItem('wh_ranks') || '{}');
      let best = -1;
      for (const track of ['offline', 'online']) {
        const t = store[track] || {};
        for (const id of Object.keys(t)) {
          const fr = t[id];
          if (fr && fr.tierId) best = Math.max(best, r.tierIndexById(fr.tierId));
        }
      }
      if (best >= 0) {
        rn.textContent = r.displayName(r.tierAt(best)).toUpperCase();
        rs.textContent = `RANK ${best + 1} / ${r.tierCount()}`;
      }
    } catch { /* keep the default LOST SOUL badge */ }
    _rankRefresh = null;
  })();
  return _rankRefresh;
}

/* ---------------- Submenu ---------------- */
function openSubmenu(key) {
  const def = SUBMENUS[key];
  if (!def) return;
  // Loud failure, never a silent dead tap: if the panel markup is absent,
  // say so instead of leaving the user on the menu wondering.
  if (!$('mm-submenu') || !$('mm-cards') || !$('mm-sub-title')) {
    toast('Menu panel missing — reload the game and try again');
    return;
  }
  click();
  document.querySelectorAll('.mm-item').forEach((b) => b.classList.remove('sel'));
  const btn = document.querySelector(`.mm-item[data-mm="${key}"]`);
  if (btn) btn.classList.add('sel');
  $('mm-sub-title').textContent = def.title;
  const wrap = $('mm-cards');
  wrap.innerHTML = '';
  def.cards.forEach((c) => {
    const b = document.createElement('button');
    b.className = 'mm-card' + (c.badge === 'hot' ? ' hot' : '');
    const badgeCls = c.badge === 'live' ? 'live' : c.badge === 'soon' ? 'soon' : '';
    const badgeTxt = c.badge === 'live' ? 'PLAY' : c.badge === 'hot' ? 'NEW' : 'SOON';
    b.innerHTML = `<span class="mm-badge ${badgeCls}">${badgeTxt}</span><h3>${c.t}</h3><p>${c.d}</p>`;
    if (c.action) b.dataset.action = c.action; // routed by the delegated document handlers
    // Data-action cards are owned by the document-level router (main.js),
    // which also re-dispatches them on touchend — no own listener here,
    // so a tap can never double-fire or be swallowed by this card.
    if (!c.action) tap(b, () => {
      if (c.panel === 'card') { openCardEditor(); return; }
      if (c.forge) { openForge(c.forge); return; }
      if (c.setup === 'versus') { openVersusSetup(); return; }
    });
    wrap.appendChild(b);
  });
  $('mm-submenu').hidden = false;
}
function closeSubmenu() { click(); $('mm-submenu').hidden = true; }

/* ---------------- Player card editor ---------------- */
function openCardEditor() {
  click();
  const p = getPlayer();
  $('mm-name-input').value = p.name || '';
  const sel = $('mm-title-input');
  sel.innerHTML = '';
  TITLES.forEach((t) => {
    const o = document.createElement('option');
    o.value = t; o.textContent = t;
    if (t === p.title) o.selected = true;
    sel.appendChild(o);
  });
  $('mm-cardpanel').hidden = false;
}
function saveCard() {
  const name = ($('mm-name-input').value || 'WANDERER').trim().toUpperCase().slice(0, 16) || 'WANDERER';
  setPlayer({ name, title: $('mm-title-input').value });
  toast('PLAYER CARD SAVED');
  $('mm-cardpanel').hidden = true;
}

/* ---------------- Forge / toast ---------------- */
let toastTimer = null;
export function toast(msg) {
  const t = $('mm-toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2200);
}
function openForge(key) {
  const f = FORGE[key];
  if (!f) return;
  click();
  $('mm-forge-title').textContent = f.title;
  $('mm-forge-desc').textContent = f.desc;
  $('mm-forge').hidden = false;
}

/* ---------------- News ticker ---------------- */
function startNews() {
  const n = $('mm-news');
  if (!n) return;
  let i = 0;
  const tick = () => { n.textContent = '◆ ' + NEWS[i % NEWS.length]; i++; };
  tick();
  setInterval(tick, 6000);
}

/* ---------------- Boot ---------------- */
let booted = false;
export function initMainMenu() {
  if (booted) return;
  booted = true;
  const menu = $('screen-menu');
  if (!menu || !menu.classList.contains('mm')) return; // menu markup not present
  renderTopbar();
  startNews();
  const ver = $('mm-ver');
  if (ver) ver.textContent = 'WESTERN HEART · BUILD 2026-10-22';

  // Rail items: submenu keys open panels; data-action items ride the
  // existing delegated router; data-mm-forge opens the forge directly.
  // NOTE: #mm-rank carries data-action="show-ranks" — the delegated
  // router opens worker 30's Rank Hall; we only stop it marking sel.
  document.querySelectorAll('.mm-item').forEach((b) => {
    if (b.dataset.action) return; // routed by the delegated data-action handler (+ its touchend re-dispatch)
    tap(b, () => {
      const key = b.dataset.mm;
      const forge = b.dataset.mmForge;
      if (forge) {
        document.querySelectorAll('.mm-item').forEach((x) => x.classList.remove('sel'));
        b.classList.add('sel');
        openForge(forge);
      } else if (key) {
        openSubmenu(key);
      }
    });
  });

  tap($('mm-sub-back'), closeSubmenu);
  tap($('mm-card-back'), () => { click(); $('mm-cardpanel').hidden = true; });
  tap($('mm-forge-ok'), () => { click(); $('mm-forge').hidden = true; });
  // Tapping the forge scrim dismisses it.
  tap($('mm-forge'), (e) => {
    if (e.target.id === 'mm-forge') { click(); $('mm-forge').hidden = true; }
  });

  // Top bar shortcuts.
  tap($('mm-pcard'), openCardEditor);
  tap($('mm-card-save'), saveCard);
  // Soul Urge meter: tap for a reminder of what it is.
  tap($('mm-soulurge'), () => {
    click();
    toast('SOUL URGE — fill all 9 souls, then unleash it');
  });
  // Coming back to the menu (quit, rematch end) refreshes the rank badge.
  document.addEventListener('click', (e) => {
    const t = e.target;
    const b = (t instanceof Element) ? t.closest('[data-action="back-menu"]') : null;
    if (b) setTimeout(() => refreshRankBadge(), 400);
  });
}
