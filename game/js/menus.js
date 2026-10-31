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
import { lazy, preloadNextFight } from './lazy.js';
import { voice } from './voice.js';
import { initMainMenu } from './mainmenu.js';
import { initVersusSetup } from './versus-setup.js';
// Clothing layer system (worker 64): per-mesh clothing toggles, in-game.
import { loadClothingConfig, getLayers, setLayerVisible, isLayerVisible, CLOTHING_CATEGORIES } from './clothing-layers.js';


/* ---------------- Settings ---------------- */
const SETTINGS_KEY = 'wh_settings_v1';
export const DEFAULT_SETTINGS = {
  master: 0.9, music: 0.28, sfx: 0.85,
  muted: false, quality: 'high', hints: true,
  soundOn: true, jukebox: 'default',
  // Lane 3 UI gaps (Gap 14 / Gap 21): T7 5.10 tournament lock +
  // streaming mode toggles, in-fight frame overlay toggle.
  frameOverlay: false, tournamentLock: false, streamingMode: false,
};
export function getSettings() {
  try {
    return { ...DEFAULT_SETTINGS, ...(JSON.parse(localStorage.getItem(SETTINGS_KEY)) || {}) };
  } catch { return { ...DEFAULT_SETTINGS }; }
}
export function applySettings() {
  const s = getSettings();
  // SOUND toggle (2026-10-24, tap-for-audio removal): audio on/off lives
  // in Settings, not behind a separate tap. soundOn:false silences exactly
  // like muted; both keys are honoured so older saves keep working.
  const off = s.muted || s.soundOn === false;
  if (audio.ctx) {
    if (audio.master) audio.master.gain.value = off ? 0 : s.master;
    if (audio.setMusicVolume) audio.setMusicVolume(off ? 0 : s.music);
    else if (audio.musicGain) audio.musicGain.gain.value = off ? 0 : s.music;
    if (audio.sfxGain) audio.sfxGain.gain.value = off ? 0 : s.sfx;
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
  // Lane 3 UI gaps (Gap 15): rank / W-L / connection meta under the
  // VS cards. Rank resolves async via lazy.ranks (same store mainmenu
  // reads); W-L is the versusWL record modes.js writes on every
  // versus bout. Local bouts show LOCAL BOUT — no bars invented.
  let meta = o.querySelector('.wh-vs-meta');
  if (!meta) { meta = document.createElement('div'); meta.className = 'wh-vs-meta'; o.appendChild(meta); }
  meta.textContent = '';
  (async () => {
    try {
      const { vsMetaLines, readVersusWL } = await import('./ui-gaps.js');
      const rec = JSON.parse(localStorage.getItem('wh_records') || '{}');
      let rankName = null;
      try {
        const r = await lazy.ranks(); await r.initRanks();
        const store = JSON.parse(localStorage.getItem('wh_ranks') || '{}');
        let best = -1;
        for (const track of ['offline', 'online']) {
          const tt = store[track] || {};
          for (const id of Object.keys(tt)) { const fr = tt[id]; if (fr && fr.tierId) best = Math.max(best, r.tierIndexById(fr.tierId)); }
        }
        if (best >= 0) rankName = r.displayName(r.tierAt(best));
      } catch { /* rank stays blank */ }
      const wl = readVersusWL(rec);
      meta.textContent = vsMetaLines({ rankName, wins: wl ? wl.w : null, losses: wl ? wl.l : null, connection: null }).join(' · ');
      // Lane 3 UI gaps (Gap 15, versus-banter UI side): banter data
      // existed (versus-banter.js) but no screen rendered it. The VS
      // screen now shows the picked exchange under the cards.
      try {
        const vb = await import('./versus-banter.js');
        const pick = await vb.pickVersusBanter(pChar && pChar.id, eChar && eChar.id);
        if (pick && pick.kind === 'banter' && pick.variant && pick.variant.beats) {
          let ban = o.querySelector('.wh-vs-banter');
          if (!ban) { ban = document.createElement('div'); ban.className = 'wh-vs-banter'; o.appendChild(ban); }
          ban.textContent = pick.variant.beats.map((b) => `${String(b.speaker || '').toUpperCase()}: ${b.line}`).join('  ·  ');
        }
      } catch { /* banter stays blank, VS screen still works */ }
    } catch { /* meta stays blank, VS screen still works */ }
  })();
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
  sheet.insertBefore(toggleRow('SOUND', 'soundOn'), back);
  sheet.insertBefore(segRow('JUKEBOX', 'jukebox',
    [['default', 'STAGE ROTATION'], ['cape-jones', 'CAPE JONES'], ['nosferatu', 'NOSFERATU']]), back);
  sheet.insertBefore(toggleRow('CONTROL HINTS', 'hints'), back);
  // Lane 3 UI gaps (Gap 14 / Gap 21).
  sheet.insertBefore(toggleRow('FRAME DATA OVERLAY (IN FIGHT)', 'frameOverlay'), back);
  sheet.insertBefore(toggleRow('TOURNAMENT LOCK (NO FAVORITES / ATTIRE)', 'tournamentLock'), back);
  sheet.insertBefore(toggleRow('STREAMING MODE (FIGHTER NAME, NO PLAYER ID)', 'streamingMode'), back);
  o.classList.add('show');
  audio.uiClick && audio.uiClick();
}
export function closeOptions() {
  const o = document.getElementById('wh-options');
  if (o) o.classList.remove('show');
}

/* ---------------- Clothing (worker 64) ----------------
   In-game clothing layers: nested in the pause menu per the integration
   law (no new screen — a sheet like OPTIONS). Lists P1/P2's registered
   clothing layers with live toggles; choices persist per attire
   (wh_clothing_v1) and apply to the live fight instances immediately. */
function clothingModelKeyOf(fighter) {
  return (fighter && fighter.char && fighter.char.model) || 'pantera';
}
export async function openClothing() {
  const o = document.getElementById('wh-clothing');
  if (!o) return;
  const list = o.querySelector('.wh-clothing-list');
  list.innerHTML = '<div class="wh-sub">loading layers…</div>';
  const g = window.__game;
  const fighters = g && g.p1 && g.p2 ? [g.p1, g.p2] : [];
  await loadClothingConfig();
  list.innerHTML = '';
  if (!fighters.length) {
    list.innerHTML = '<div class="wh-sub">No fight running.</div>';
  }
  for (const f of fighters) {
    const key = clothingModelKeyOf(f);
    const layers = getLayers(key);
    const name = (f.char && (f.char.name || f.char.id) || key).toUpperCase();
    const head = el('div', 'wh-sub', `<b>${esc(name)}</b>`);
    head.style.marginTop = '10px';
    list.appendChild(head);
    if (!layers.length) {
      list.appendChild(el('div', 'wh-sub', 'No clothing layers registered for this attire yet.'));
      continue;
    }
    for (const l of layers) {
      const cat = CLOTHING_CATEGORIES[l.category] || (l.category || '').toUpperCase();
      const vis = isLayerVisible(f.model, key, l.label);
      const row = el('div', 'wh-toggle' + (vis ? ' on' : ''),
        `<span>${esc(l.display || l.label)}<small> · ${esc(cat)} · ${esc(l.label)}</small></span><span class="pill"></span>`);
      row.setAttribute('role', 'switch');
      row.setAttribute('aria-checked', vis ? 'true' : 'false');
      row.addEventListener('click', () => {
        audio.uiClick && audio.uiClick();
        const now = !row.classList.contains('on');
        const res = setLayerVisible(f.model, key, l.label, now);
        if (res.error) { console.warn('[WH] clothing toggle:', res.error); return; }
        row.classList.toggle('on', now);
        row.setAttribute('aria-checked', now ? 'true' : 'false');
      });
      list.appendChild(row);
    }
  }
  document.getElementById('wh-pause').classList.remove('show');
  o.classList.add('show');
  audio.uiClick && audio.uiClick();
}
export function closeClothing() {
  const o = document.getElementById('wh-clothing');
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
    if (!b.charId) { img.style.display = 'none'; img.removeAttribute('src'); } // model-pending: no borrowed portrait
    else img.src = `assets/portraits/${b.charId}.png`;
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
        <button class="btn-ghost" data-wh="pause-clothing">CLOTHING</button>
        <button class="btn-ghost" data-wh="pause-options">OPTIONS</button>
        <button class="btn-ghost" data-wh="pause-freecam">FREE CAMERA</button>
        <button class="btn-ghost" data-wh="quit">QUIT TO MENU</button>
      </div>
    </div>
    <div id="wh-clothing" role="dialog" aria-label="Clothing">
      <div class="wh-sheet">
        <h2>CLOTHING</h2>
        <div class="wh-sub">Take off / put on each fighter's layers — live, saved per attire</div>
        <div class="wh-clothing-list"></div>
        <button class="btn-primary" data-wh="back" style="width:100%;margin-top:14px;min-height:48px;">BACK</button>
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
  document.querySelector('[data-wh="pause-clothing"]').addEventListener('click', openClothing);
  document.querySelector('[data-wh="pause-options"]').addEventListener('click', () => {
    document.getElementById('wh-pause').classList.remove('show');
    openOptions();
  });
  // Free camera lives behind PAUSE (owner 2026-10-31), never as a floating button over menus or the HUD.
  // The fight keeps playing while the camera is free (free-camera.js contract), so this resumes first.
  document.querySelector('[data-wh="pause-freecam"]').addEventListener('click', () => {
    const g = window.__game;
    resumeGame();
    if (g && g.freeCamera && !g.freeCamera.active) g.freeCamera.enter();
  });
  document.querySelectorAll('#wh-options [data-wh="back"], #wh-records [data-wh="back"], #wh-clothing [data-wh="back"]')
    .forEach((b) => b.addEventListener('click', () => {
      audio.uiClick && audio.uiClick();
      closeOptions(); closeRecords(); closeClothing();
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

  // Special actions dispatch to their controllers, built on first tap
  // (LOADSPEED: heartmind.js / episodes.js stream via lazy.js, not boot).
  // Delegated (T8 menu, worker 37): also covers submenu cards created
  // dynamically by mainmenu.js.
  if (!document._whSpecialDelegated) {
    document._whSpecialDelegated = true;
    document.addEventListener('click', async (e) => {
      const t = e.target;
      const b = (t instanceof Element) ? t.closest('[data-action="mode-options"],[data-action="mode-records"],[data-action="mode-heartmind"],[data-action="mode-episodes"]') : null;
      if (!b) return;
      const a = b.dataset.action;
      audio.unlock();
      if (a === 'mode-options') { audio.uiClick && audio.uiClick(); openOptions(); }
      else if (a === 'mode-records') { audio.uiClick && audio.uiClick(); openRecords(); }
      else if (a === 'mode-heartmind') {
        audio.uiClick && audio.uiClick();
        await ensureHeartmind();
        window.__heartmind && window.__heartmind.beginSelect();
      }
      else if (a === 'mode-episodes') {
        audio.uiClick && audio.uiClick();
        await ensureEpisodes();
        window.__episodes && window.__episodes.beginSelect();
      }
    });
  }
}

/* ---------------- Mode tag ---------------- */
export function setModeTag(text) {
  const t = document.getElementById('wh-mode-tag');
  if (!t) return;
  t.textContent = text || '';
  t.classList.toggle('show', !!text);
}

/* ---------------- Hooks ---------------- */
/* ---------------- Announcer + rematch preload (2026-10-24) --------
   voice.announce() existed but had ZERO call sites — round/KO calls never
   played. Wrapped here (same pattern as hookStartMatch) so game.js — which
   the music-rotation lane touches — is not edited. Every call is
   fire-and-forget and guarded: a voice failure can never break a round.
   Announcer clips are subtitle-only placeholders until the proprietary
   announcer is recorded (game/data/voices/announcer.json; the exact line
   list is in docs/decisions/2026-10-24-audio-jukebox-streaming.md).
   Round call: 'final-round' when the match is at match point (the same
   _musicFinal flag the music lane sets in _startRound), else round-N.
   'fight' fires on the same 1100 ms beat as the FIGHT! banner, guarded by
   roundState so a paused/ended round never announces. End call: both
   down -> double-ko; timer at 0 -> time-up (the loop zeroes the timer
   before _timeOut); otherwise the winner at full HP -> perfect, else ko.
   Match end: you-win only when the player (P1) took the match — the
   manifest has no you-lose line, so a loss stays silent. */
function hookAnnouncer(g) {
  if (!g || g._whAnnouncerHooked) return;
  g._whAnnouncerHooked = true;
  try { voice.unlock(); } catch (e) {}
  const origStart = g._startRound.bind(g);
  g._startRound = function () {
    const r = origStart();
    try {
      voice.announce(g._musicFinal ? 'final-round' : `round-${g.round}`);
      setTimeout(() => {
        try { if (g.running && !g.paused && g.roundState === 'fight') voice.announce('fight'); } catch (e) {}
      }, 1100);
    } catch (e) {}
    return r;
  };
  const origEnd = g._endRound.bind(g);
  g._endRound = function () {
    const was = g.roundState;
    const r = origEnd();
    try {
      if (was === 'fight' && g.roundState === 'over') {
        const p1Down = g.p1.hp <= 0, p2Down = g.p2.hp <= 0;
        if (p1Down && p2Down) voice.announce('double-ko');
        else if (g.timer <= 0) voice.announce('time-up');
        else {
          const winner = p1Down ? g.p2 : g.p1;
          voice.announce(winner.hp >= winner.maxHp ? 'perfect' : 'ko');
        }
      }
    } catch (e) {}
    return r;
  };
  if (typeof g._afterRound === 'function') {
    const origAfter = g._afterRound.bind(g);
    g._afterRound = function () {
      const r = origAfter();
      try { if (!g.running && g.wins.p1 > g.wins.p2) voice.announce('you-win'); } catch (e) {}
      return r;
    };
  }
}

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
  let lastPair = null;
  g.startMatch = function (pChar, eChar, stageId, opts = {}) {
    hideLoading();
    const modeLabel = (opts.mode || '').toUpperCase().replace('HEARTMIND', 'THE HEART AND MIND INSIDE');
    showVs(pChar, eChar, stageNameFor(stageId), modeLabel);
    // STREAMING (2026-10-24): while the VS screen breathes, warm the
    // rematch pair (see lazy.preloadNextFight). The outro preload below
    // warms the same pair again after leaveFight, so REMATCH rarely waits.
    lastPair = [pChar, eChar];
    try { preloadNextFight([pChar, eChar]).catch(() => {}); } catch (e) {}
    hookAnnouncer(g);
    const r = orig(pChar, eChar, stageId, opts);
    setModeTag(modeLabel || '');
    setTimeout(hideVs, 2200); // VS breathes over the ROUND 1 intro
    return r;
  };
  const origLeave = g.leaveFight.bind(g);
  g.leaveFight = function () { setModeTag(''); hideVs(); hideLoading(); if (lastPair) { try { preloadNextFight(lastPair).catch(() => {}); } catch (e) {} } return origLeave(); };
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
  initMainMenu(); // T8-style main menu controller (additive; no-ops if markup absent)
  initVersusSetup(); // versus rules screen (additive; no-ops if markup absent)
  hookAudioUnlock();
  // JUKEBOX (2026-10-24): install the pool wrapper once at boot. Dynamic
  // import so the menu graph stays lean; a failed install leaves the
  // default stage rotation untouched (never throws into boot).
  try { import('./jukebox.js').then((m) => { try { m.installJukebox(); } catch (e) {} }).catch(() => {}); } catch (e) {}
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
  // Lane 3 UI gaps: favorites bar, frame overlay, gallery/jukebox/
  // replay screens (dynamic import — never blocks menu boot).
  import('./ui-gaps.js').then((m) => m.initUiGaps()).catch(() => {});
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
