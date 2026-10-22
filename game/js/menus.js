/* ============================================================
   WESTERN HEART — Stream 4: Modes & Menus
   Pause menu · options/settings · loading screen · VS screen ·
   records/rankings · story dialogue · mode menu wiring.
   Mobile-first: everything is touch-driven, targets >= 44px.

   Wiring contract (additive — touches nothing existing):
   - main.js calls initMenus() once at boot (2-line hook).
   - Reads window.__game / window.__modes (set by main.js).
   - Imports { audio } (same singleton main.js uses).
   - LOADSPEED: modes.js / heartmind.js / episodes.js are NOT boot code —
     they stream through lazy.js on first use (records screen, their mode
     buttons). See game/js/lazy.js.
   ============================================================ */
import { audio } from './audio.js';
import { lazy } from './lazy.js';

/* ---------------- Settings ---------------- */
const SETTINGS_KEY = 'wh_settings_v1';
export const DEFAULT_SETTINGS = {
  master: 0.9, music: 0.28, sfx: 0.85,
  muted: false, quality: 'high', hints: true,
};
export function getSettings() {
  try {
    return { ...DEFAULT_SETTINGS, ...(JSON.parse(localStorage.getItem(SETTINGS_KEY)) || {}) };
  } catch { return { ...DEFAULT_SETTINGS }; }
}
export function applySettings() {
  const s = getSettings();
  if (audio.ctx) {
    if (audio.master) audio.master.gain.value = s.muted ? 0 : s.master;
    if (audio.setMusicVolume) audio.setMusicVolume(s.muted ? 0 : s.music);
    else if (audio.musicGain) audio.musicGain.gain.value = s.muted ? 0 : s.music;
    if (audio.sfxGain) audio.sfxGain.gain.value = s.muted ? 0 : s.sfx;
  }
  applyQuality(s.quality);
}
export function setSettings(patch) {
  try { localStorage.setItem(SETTINGS_KEY, JSON.stringify({ ...getSettings(), ...patch })); } catch { /* private mode */ }
  applySettings();
}
/* Graphics quality: pixel-ratio scaling (+ shadow toggle). Real effect,
   no asset reload. low = 0.75x, med = 1x, high = min(dpr,2). */
export function applyQuality(q) {
  const g = window.__game;
  if (!g || !g.arena || !g.arena.renderer) return;
  const r = g.arena.renderer;
  const dpr = window.devicePixelRatio || 1;
  if (q === 'low') { r.setPixelRatio(Math.min(dpr, 0.75)); r.shadowMap.enabled = false; }
  else if (q === 'med') { r.setPixelRatio(Math.min(dpr, 1)); r.shadowMap.enabled = true; }
  else { r.setPixelRatio(Math.min(dpr, 2)); r.shadowMap.enabled = true; }
}

/* ---------------- DOM helpers ---------------- */
const el = (tag, cls, html) => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  return e;
};
/* Classic screen switcher (mirrors main.js show()). */
export function showScreen(name) {
  document.querySelectorAll('.screen').forEach((s) => s.classList.remove('active'));
  const t = document.getElementById(name === 'hud' ? 'hud' : `screen-${name}`);
  if (t) t.classList.add('active');
}

/* ---------------- Loading overlay ---------------- */
let loadTimer = null;
const TIPS = [
  'Fill all 9 souls, then unleash your Soul Surge.',
  'Blocking still builds soul — patience is a weapon.',
  'Dodge has i-frames. Time it like you mean it.',
  'The Trader buys and sells elemental forces. All transactions are final.',
  'Death is not failure. It is the mechanism.',
];
export function showLoading(status) {
  let o = document.getElementById('wh-loading');
  if (!o) return;
  o.querySelector('.wh-load-status').textContent = status || 'ENTERING THE ARENA…';
  o.querySelector('.wh-load-tip').textContent = TIPS[Math.floor(Math.random() * TIPS.length)];
  const fill = o.querySelector('.wh-load-fill');
  fill.style.width = '8%';
  o.classList.add('show');
  clearTimeout(loadTimer);
  loadTimer = setTimeout(hideLoading, 45000); // safety: never trap the player
}
export function setLoadingProgress(p) {
  const f = document.querySelector('#wh-loading .wh-load-fill');
  if (f) f.style.width = `${Math.round(Math.max(0.08, Math.min(1, p)) * 100)}%`;
}
export function hideLoading() {
  clearTimeout(loadTimer);
  const o = document.getElementById('wh-loading');
  if (o) o.classList.remove('show');
}

/* ---------------- VS screen ---------------- */
export function showVs(pChar, eChar, stageName, modeLabel) {
  const o = document.getElementById('wh-vs');
  if (!o) return;
  const card = (c, side) => `
    <div class="wh-vs-card ${side}">
      <div class="portrait"><img src="assets/portraits/${c.portrait || c.id}.png" alt=""
        onerror="this.style.display='none'"></div>
      <div class="vname">${c.name || '???'}</div>
      <div class="vtitle">${c.title || ''}</div>
    </div>`;
  o.querySelector('.wh-vs-inner').innerHTML =
    card(pChar, 'left') +
    `<div class="wh-vs-mid"><div class="vsburst">VS</div></div>` +
    card(eChar, 'right');
  o.querySelector('.wh-vs-mode').textContent = modeLabel || '';
  let st = o.querySelector('.wh-vs-stage');
  if (!st) {
    st = document.createElement('div');
    st.className = 'wh-vs-stage';
    o.querySelector('.wh-vs-inner').after(st);
  }
  st.textContent = stageName || '';
  o.classList.remove('hide');
  o.classList.add('show');
}
export function hideVs() {
  const o = document.getElementById('wh-vs');
  if (!o) return;
  o.classList.add('hide');
  setTimeout(() => o.classList.remove('show', 'hide'), 380);
}

/* ---------------- Pause ---------------- */
export function pauseGame() {
  const g = window.__game;
  if (!g || g.paused) return;
  // Brawler (worker 20): the descent pauses too (game.running is false
  // while the brawler owns the sim).
  if (!g.running && !g.brawler) return;
  g.pause(true);
  const o = document.getElementById('wh-pause');
  if (o) o.classList.add('show');
  audio.uiClick && audio.uiClick();
}
export function resumeGame() {
  const g = window.__game;
  const o = document.getElementById('wh-pause');
  if (o) o.classList.remove('show');
  if (g && (g.running || g.brawler)) g.pause(false);
  audio.uiClick && audio.uiClick();
}
export function quitToMenu() {
  const g = window.__game, m = window.__modes;
  const o = document.getElementById('wh-pause');
  if (o) o.classList.remove('show');
  hideVs(); hideLoading();
  if (g) g.leaveFight();
  if (m) m.clearState();
  if (window.__heartmind) window.__heartmind.clear();
  if (window.__episodes) window.__episodes.clear();
  showScreen('menu');
  audio.stopMusic && audio.stopMusic();
  audio.uiClick && audio.uiClick();
}

/* ---------------- Options ---------------- */
function sliderRow(label, key, fmt) {
  const s = getSettings();
  const row = el('div', 'wh-row');
  row.innerHTML = `<label>${label}<output>${fmt(s[key])}</output></label>`;
  const inp = el('input');
  inp.type = 'range'; inp.min = '0'; inp.max = '100'; inp.value = Math.round(s[key] * 100);
  inp.setAttribute('aria-label', label);
  inp.addEventListener('input', () => {
    const v = inp.value / 100;
    row.querySelector('output').textContent = fmt(v);
    setSettings({ [key]: v });
  });
  row.appendChild(inp);
  return row;
}
function segRow(label, key, options) {
  const s = getSettings();
  const row = el('div', 'wh-row', `<label>${label}</label>`);
  const seg = el('div', 'wh-seg');
  options.forEach(([val, text]) => {
    const b = el('button', s[key] === val ? 'sel' : '', text);
    b.addEventListener('click', () => {
      audio.uiClick && audio.uiClick();
      seg.querySelectorAll('button').forEach((x) => x.classList.remove('sel'));
      b.classList.add('sel');
      setSettings({ [key]: val });
    });
    seg.appendChild(b);
  });
  row.appendChild(seg);
  return row;
}
function toggleRow(label, key) {
  const s = getSettings();
  const row = el('div', 'wh-toggle' + (s[key] ? ' on' : ''), `<span>${label}</span><span class="pill"></span>`);
  row.addEventListener('click', () => {
    audio.uiClick && audio.uiClick();
    const v = !getSettings()[key];
    row.classList.toggle('on', v);
    setSettings({ [key]: v });
  });
  return row;
}
export function openOptions() {
  const o = document.getElementById('wh-options');
  if (!o) return;
  const sheet = o.querySelector('.wh-sheet');
  sheet.querySelectorAll('.wh-row, .wh-toggle').forEach((x) => x.remove());
  const back = sheet.querySelector('[data-wh="back"]');
  const pct = (v) => `${Math.round(v * 100)}%`;
  sheet.insertBefore(sliderRow('MASTER VOLUME', 'master', pct), back);
  sheet.insertBefore(sliderRow('MUSIC VOLUME', 'music', pct), back);
  sheet.insertBefore(sliderRow('SFX VOLUME', 'sfx', pct), back);
  sheet.insertBefore(segRow('GRAPHICS QUALITY', 'quality',
    [['low', 'LOW'], ['med', 'MED'], ['high', 'HIGH']]), back);
  sheet.insertBefore(toggleRow('MUTE ALL', 'muted'), back);
  sheet.insertBefore(toggleRow('CONTROL HINTS', 'hints'), back);
  o.classList.add('show');
  audio.uiClick && audio.uiClick();
}
export function closeOptions() {
  const o = document.getElementById('wh-options');
  if (o) o.classList.remove('show');
}

/* ---------------- Records ---------------- */
export async function openRecords() {
  const o = document.getElementById('wh-records');
  if (!o) return;
  const { whGetRecords } = await lazy.modes();
  const rec = whGetRecords();
  const list = o.querySelector('.wh-rec-list');
  list.innerHTML = '';
  const rows = [
    ['SURVIVAL — BEST WAVE', rec.survival ? `${rec.survival} waves` : null],
    ['TIME ATTACK — BEST', rec.timeattack ? fmtMs(rec.timeattack) : null],
    ['IMMORTAL QOMBAT — BEST WAVE', rec.qombat ? `${rec.qombat} waves` : null],
    ['SOULS FED TO SUN RĀ', rec.qombatEaten ? `${rec.qombatEaten}` : null],
  ];
  let any = false;
  for (const [k, v] of rows) {
    if (!v) continue;
    any = true;
    list.appendChild(el('div', 'wh-rec-row', `<span>${k}</span><span class="rv">${v}</span>`));
  }
  // Stream-4 records (heartmind/episodes) render when those modules register.
  const extra = document.getElementById('wh-rec-extra');
  if (extra) { list.appendChild(extra); if (extra.children.length) any = true; }
  if (!any) list.appendChild(el('div', 'wh-empty', 'No records yet. Fight something.'));
  o.classList.add('show');
  audio.uiClick && audio.uiClick();
}
export function closeRecords() {
  const o = document.getElementById('wh-records');
  if (o) o.classList.remove('show');
}
function fmtMs(ms) {
  const s = Math.floor(ms / 1000);
  return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
}

/* ---------------- Story dialogue ----------------
   beats: [{ name, charId, text }]. Tap anywhere to advance.
   done() fires after the last beat. */
export function playStoryBeats(beats, done, kicker) {
  const o = document.getElementById('wh-story');
  if (!o || !beats || !beats.length) { done && done(); return; }
  let i = 0;
  const kick = o.querySelector('.wh-story-kicker');
  if (kick) kick.textContent = kicker || '';
  const render = () => {
    const b = beats[i];
    o.querySelector('.wh-story-name').textContent = b.name || '';
    o.querySelector('.wh-story-text').textContent = b.text || '';
    const img = o.querySelector('.wh-story-card .sportrait img');
    img.style.display = '';
    img.src = `assets/portraits/${b.charId || 'pantera'}.png`;
    img.onerror = () => { img.style.display = 'none'; };
    o.querySelector('.wh-story-hint').textContent =
      `TAP TO CONTINUE · ${i + 1}/${beats.length}`;
  };
  const advance = (e) => {
    e && e.stopPropagation();
    audio.uiClick && audio.uiClick();
    i++;
    if (i >= beats.length) {
      o.classList.remove('show');
      o.removeEventListener('click', advance);
      done && done();
    } else render();
  };
  o.addEventListener('click', advance);
  render();
  o.classList.add('show');
}

/* ---------------- Build all overlays ---------------- */
function buildOverlays() {
  if (document.getElementById('wh-loading')) return; // already built
  const body = document.body;

  body.insertAdjacentHTML('beforeend', `
    <div id="wh-loading" aria-hidden="true">
      <div class="wh-load-title">WESTERN<span>HEART</span></div>
      <div class="wh-load-bar"><div class="wh-load-fill"></div></div>
      <div class="wh-load-status">ENTERING THE ARENA…</div>
      <div class="wh-load-tip"></div>
    </div>
    <div id="wh-vs" aria-hidden="true">
      <div class="wh-vs-mode"></div>
      <div class="wh-vs-inner"></div>
    </div>
    <div id="wh-pause" role="dialog" aria-label="Paused">
      <div class="wh-dialog">
        <h2>PAUSED</h2>
        <div class="wh-sub">The shrine holds its breath.</div>
        <button class="btn-primary" data-wh="resume">RESUME</button>
        <button class="btn-ghost" data-wh="pause-options">OPTIONS</button>
        <button class="btn-ghost" data-wh="quit">QUIT TO MENU</button>
      </div>
    </div>
    <div id="wh-options" role="dialog" aria-label="Options">
      <div class="wh-sheet">
        <h2>OPTIONS</h2>
        <div class="wh-sub">Sound · graphics · controls</div>
        <button class="btn-primary" data-wh="back" style="width:100%;margin-top:14px;min-height:48px;">BACK</button>
      </div>
    </div>
    <div id="wh-records" role="dialog" aria-label="Records">
      <div class="wh-sheet">
        <h2>RECORDS</h2>
        <div class="wh-sub">Local legends, carved in the shrine stones</div>
        <div class="wh-rec-list"></div>
        <div id="wh-rec-extra"></div>
        <button class="btn-primary" data-wh="back" style="width:100%;margin-top:14px;min-height:48px;">BACK</button>
      </div>
    </div>
    <div id="wh-story" role="dialog" aria-label="Story">
      <div class="wh-story-kicker"></div>
      <div class="wh-story-card">
        <div class="sportrait"><img alt=""></div>
        <div class="wh-story-body">
          <div class="wh-story-name"></div>
          <div class="wh-story-text"></div>
          <div class="wh-story-hint">TAP TO CONTINUE</div>
        </div>
      </div>
    </div>`);

  // HUD: pause button + mode tag
  const hud = document.getElementById('hud');
  if (hud && !document.getElementById('wh-pause-btn')) {
    const pb = el('button', '', '❚❚');
    pb.id = 'wh-pause-btn';
    pb.setAttribute('aria-label', 'Pause');
    pb.addEventListener('click', (e) => { e.stopPropagation(); pauseGame(); });
    hud.appendChild(pb);
    const tag = el('div', '', '');
    tag.id = 'wh-mode-tag';
    hud.appendChild(tag);
  }

  // Overlay button wiring
  document.querySelector('[data-wh="resume"]').addEventListener('click', resumeGame);
  document.querySelector('[data-wh="quit"]').addEventListener('click', quitToMenu);
  document.querySelector('[data-wh="pause-options"]').addEventListener('click', () => {
    document.getElementById('wh-pause').classList.remove('show');
    openOptions();
  });
  document.querySelectorAll('#wh-options [data-wh="back"], #wh-records [data-wh="back"]')
    .forEach((b) => b.addEventListener('click', () => {
      audio.uiClick && audio.uiClick();
      closeOptions(); closeRecords();
      // If we came from pause, go back to pause.
      const g = window.__game;
      if (g && (g.running || g.brawler) && g.paused && !document.getElementById('wh-pause').classList.contains('show')) {
        document.getElementById('wh-pause').classList.add('show');
      }
    }));
}

/* ---------------- Menu buttons ---------------- */
function addMenuButton(label, sub, action, ghost) {
  const wrap = document.querySelector('#screen-menu .menu-buttons');
  if (!wrap || wrap.querySelector(`[data-action="${action}"]`)) return null;
  const b = el('button', ghost ? 'btn-ghost' : 'btn-primary mode-new',
    sub ? `${label}<small>${sub}</small>` : label);
  b.dataset.action = action;
  return b;
}
function buildMenuButtons() {
  const trader = document.querySelector('[data-action="mode-trader"]');
  const howto = document.querySelector('[data-action="howto"]');
  const mk = (label, sub, action, ghost, after) => {
    const b = addMenuButton(label, sub, action, ghost);
    if (b && after && after.parentNode) after.parentNode.insertBefore(b, after.nextSibling);
    return b;
  };
  // New modes ride with the mode list; utility under How To Play.
  mk('THE HEART AND MIND INSIDE', 'a descent · beat-em-up', 'mode-heartmind', false, trader);
  mk('CHARACTER EPISODES', 'every soul, their story', 'mode-episodes', false,
    document.querySelector('[data-action="mode-heartmind"]') || trader);
  mk('OPTIONS', null, 'mode-options', true, howto);
  mk('RECORDS', null, 'mode-records', true,
    document.querySelector('[data-action="mode-options"]') || howto);

  document.querySelectorAll('[data-action="mode-options"]').forEach((b) =>
    b.addEventListener('click', () => { audio.unlock(); openOptions(); }));
  document.querySelectorAll('[data-action="mode-records"]').forEach((b) =>
    b.addEventListener('click', () => { audio.unlock(); openRecords(); }));
  // New-mode entries dispatch to their controllers, built on first tap
  // (LOADSPEED: heartmind.js / episodes.js stream via lazy.js, not boot).
  document.querySelectorAll('[data-action="mode-heartmind"]').forEach((b) =>
    b.addEventListener('click', async () => {
      audio.unlock(); audio.uiClick && audio.uiClick();
      await ensureHeartmind();
      window.__heartmind && window.__heartmind.beginSelect();
    }));
  document.querySelectorAll('[data-action="mode-episodes"]').forEach((b) =>
    b.addEventListener('click', async () => {
      audio.unlock(); audio.uiClick && audio.uiClick();
      await ensureEpisodes();
      window.__episodes && window.__episodes.beginSelect();
    }));
}

/* ---------------- Mode tag ---------------- */
export function setModeTag(text) {
  const t = document.getElementById('wh-mode-tag');
  if (!t) return;
  t.textContent = text || '';
  t.classList.toggle('show', !!text);
}

/* ---------------- Hooks ---------------- */
function hookStartMatch() {
  const g = window.__game;
  if (!g || g._whMenusHooked) return;
  g._whMenusHooked = true;
  const orig = g.startMatch.bind(g);
  const stageNameFor = (id) => {
    try {
      const st = window.__stages && window.__stages.find((s) => s.id === id);
      return st ? st.name : (g._stageName || '');
    } catch { return g._stageName || ''; }
  };
  g.startMatch = function (pChar, eChar, stageId, opts = {}) {
    hideLoading();
    const modeLabel = (opts.mode || '').toUpperCase().replace('HEARTMIND', 'THE HEART AND MIND INSIDE');
    showVs(pChar, eChar, stageNameFor(stageId), modeLabel);
    const r = orig(pChar, eChar, stageId, opts);
    setModeTag(modeLabel || '');
    setTimeout(hideVs, 2200); // VS breathes over the ROUND 1 intro
    return r;
  };
  const origLeave = g.leaveFight.bind(g);
  g.leaveFight = function () { setModeTag(''); hideVs(); hideLoading(); return origLeave(); };
}
function hookConfirm() {
  const cf = document.getElementById('confirm-fighter');
  if (cf && !cf._whHooked) {
    cf._whHooked = true;
    cf.addEventListener('click', () => {
      const m = window.__modes;
      // Versus routes to stage select (no model load yet); everything else loads now.
      if (m && m.mode && m.mode !== 'versus') showLoading('ENTERING THE ARENA…');
    });
  }
  const cs = document.getElementById('confirm-stage');
  if (cs && !cs._whHooked) {
    cs._whHooked = true;
    cs.addEventListener('click', () => showLoading('ENTERING THE ARENA…'));
  }
}
function hookAudioUnlock() {
  if (audio._whHooked) return;
  audio._whHooked = true;
  const orig = audio.unlock.bind(audio);
  audio.unlock = function () {
    orig();
    setTimeout(applySettings, 60); // apply persisted volumes post-unlock
  };
}

/* ---------------- Boot ---------------- */
let booted = false;
let _cdeps = null;
/* LOADSPEED: controller deps captured at initMenus; the modules stream
   on first use. Concurrent taps share one import promise each. */
let _hmPromise = null, _epPromise = null;
export function ensureHeartmind() {
  if (window.__heartmind) return Promise.resolve(window.__heartmind);
  if (!_hmPromise) {
    _hmPromise = lazy.heartmind().then(({ HeartmindController }) => {
      window.__heartmind = new HeartmindController(_cdeps);
      return window.__heartmind;
    }).catch((e) => { _hmPromise = null; throw e; });
  }
  return _hmPromise;
}
export function ensureEpisodes() {
  if (window.__episodes) return Promise.resolve(window.__episodes);
  if (!_epPromise) {
    _epPromise = lazy.episodes().then(({ EpisodesController }) => {
      window.__episodes = new EpisodesController(_cdeps);
      return window.__episodes;
    }).catch((e) => { _epPromise = null; throw e; });
  }
  return _epPromise;
}
export function initMenus(deps = {}) {
  if (booted) return;
  booted = true;
  buildOverlays();
  buildMenuButtons();
  hookAudioUnlock();
  // Stream-4 mode controllers (standalone; they reuse Game patterns).
  // LOADSPEED: built on first tap via ensureHeartmind/ensureEpisodes —
  // not at boot. The card-tracking + confirm hooks are cheap and run now.
  _cdeps = {
    game: deps.game || window.__game,
    ui: deps.ui || window.__ui,
    show: deps.show || showScreen,
    startFight: deps.startFight,
    roster: deps.ROSTER || [],
    getChar: deps.getChar || ((id) => null),
    audio: deps.audio || audio,
  };
  hookCardTracking();
  hookConfirmIntercept();
  // game/modes arrive on window a beat after module eval — hook when present.
  const tryHook = () => {
    if (window.__game) { hookStartMatch(); hookConfirm(); applySettings(); }
    else setTimeout(tryHook, 150);
  };
  tryHook();
  // Respect persisted hint visibility.
  if (!getSettings().hints) {
    const h = document.getElementById('control-hints');
    if (h) h.classList.add('fade');
  }
}

/* Track char-card taps (capture phase) so standalone modes know the pick.
   main.js's own selectCard still runs — this only records the id. */
function hookCardTracking() {
  const grid = document.getElementById('char-grid');
  if (!grid || grid._whTrackHooked) return;
  grid._whTrackHooked = true;
  grid.addEventListener('click', (e) => {
    const card = e.target.closest('.char-card');
    if (!card || !card.dataset.id) return;
    if (window.__heartmind) window.__heartmind.trackCard(card.dataset.id);
    if (window.__episodes) window.__episodes.trackCard(card.dataset.id);
  }, true);
}
/* Confirm interception: main.js's listener runs first (added at boot);
   ModeController.onConfirm ignores unknown modes, then we route. */
function hookConfirmIntercept() {
  const cf = document.getElementById('confirm-fighter');
  if (!cf || cf._whRouteHooked) return;
  cf._whRouteHooked = true;
  cf.addEventListener('click', () => {
    const m = window.__modes;
    if (!m || !m.mode) return;
    if (m.mode === 'heartmind' && window.__heartmind) window.__heartmind.onConfirm();
    else if (m.mode === 'episodes' && window.__episodes) window.__episodes.onConfirm();
  });
}
