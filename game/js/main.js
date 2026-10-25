/* ============================================================
   WESTERN HEART — main bootstrap
   Screen flow, character select, HUD bindings (Nine-Soul Meter
   with 9 soul segments), Soul Surge screen flash.
   ============================================================ */
import './t7-ui-private.js';
import './select-t7-layout.js';
import './menu-t7-layout.js';
import { Game } from './game.js';
import { InputManager } from './input.js';
import { audio } from './audio.js';
import { music } from './music.js';
import { assets } from './assets.js';
import { ROSTER, getCharacter } from './characters.js';
// LOADSPEED (2026-10-22): fighter.js / movesets.js / t3anims.js / modes.js
// are fight-or-preview-only — they load on demand through lazy.js so the
// menu shell paints without parsing them (Tekken 3 BNS lesson: the index
// loads first, records stream on demand). Warmed during idle at boot end.
import { lazy, warmIdle } from './lazy.js';
import { loadThrowTables } from './t3-throw.js';
import { mark } from './loadperf.js';
import * as THREE from 'three';
import { whUiEnabled, mountWhUi } from './ui-wh-bridge.js';
import { getCustomFighter, customFighterToRoster } from './custom-fighter.js';
import { resolveFighterAttire } from './attires.js';
import { createSelectScreen } from './select-screen.js';
import { STAGES, STAGE_TIERS, getStage, randomStageId } from './stages.js';
// LOADSPEED: stages.js (82KB data) stays static — buildStageSelect runs in
// the versus flow and getStage is needed by startFight; its parse cost is
// small next to the deferred modules. Stage THUMBS are the real cost there
// (see the thumb atlas, assets/stages/thumbs/atlas.png + thumbs.json).
import { initMenus } from './menus.js';
import './load-progress.js'; // real loading bar (owner pt134u)

// LOADSPEED: the real Tekken moveset JSONs (~300KB) used to fetch at boot.
// They are fight data — they load when a fight starts (startFight awaits
// them alongside the fighter GLBs), not while the menu is painting.

const screens = {
  menu:   document.getElementById('screen-menu'),
  howto:  document.getElementById('screen-howto'),
  select: document.getElementById('screen-select'),
  // PR #841 versus-setup: show() must hide this screen too — openVersusSetup()
  // adds .active directly, and without this entry show('select') left it
  // covering the select screen (menu-touch-e2e tap timeout on .char-card).
  vssetup: document.getElementById('screen-vssetup'),
  stage:  document.getElementById('screen-stage'),
  stageIntro: document.getElementById('screen-stage-intro'),
  result: document.getElementById('screen-result'),
  hud:    document.getElementById('hud'),
  reincarnate: document.getElementById('screen-reincarnate'),
  trader:  document.getElementById('screen-trader'),
  modewin: document.getElementById('screen-modewin'),
  online: document.getElementById('screen-online'),
  sidegames: document.getElementById('screen-sidegames'),
  collection: document.getElementById('screen-collection'),
  daily: document.getElementById('screen-daily'),
};
/* Tekken-style select screen controller (js/select-screen.js).
   Assigned once at bootstrap below; show() only runs on user
   interaction, after the whole module has been evaluated. */
let selectScreen = null;
function show(name) {
  mark(name === 'select' ? 'select-open' : name === 'stage' ? 'stage-open' : `show:${name}`);
  Object.values(screens).forEach(s => s.classList.remove('active'));
  if (screens[name]) screens[name].classList.add('active');
  // Tekken 99s select timer: runs only on the select screen, and only once the
  // ~30MB assets are loaded — slow phones don't lose selection time to loading.
  if (name === 'select') {
    maybeStartSelectTimer();
    // LOADSPEED (2026-10-22): the old code fired preloadAll() here — four
    // base GLBs (~26MB) the instant select opened, saturating the pipe the
    // user's first preview taps needed. Now the screen paints first and the
    // bases warm during idle; a highlight always preempts them (assets.js).
    // The custom-fighter base only matters when a custom fighter exists.
    assets.preloadBaseIdle(!!getCustomFighter());
    if (selectScreen) selectScreen.onShow(modes ? modes.mode : null);
    requestAnimationFrame(() => requestAnimationFrame(() => mark('select-interactive')));
  }
  else { selectTimerArmed = false; stopSelectTimer(); }
  // MUSIC (2026-10-24): Tekken screen-change rule — menu screens get their
  // own rotating theme; the fight itself gets the stage pool at fight
  // start (see startFight). Never throws; a missing library just falls
  // back to the procedural loop inside the engine.
  try {
    if (name === 'menu') music.playMenu('title');
    else if (name === 'select') music.playMenu('select');
    else if (name === 'stage') music.playMenu('versus');
    else if (name === 'online') music.playMenu('online');
  } catch (e) {}
}

const SOULS = 9; // Nine-Soul Meter segments

const ui = {
  _comboT: null,
  _segs: {},
  setNames(p1, p2) {
    document.getElementById('p1-name').textContent = p1;
    document.getElementById('p2-name').textContent = p2;
  },
  setStageName(name) {
    const el = document.getElementById('stage-label');
    if (el) el.textContent = name;
  },
  _buildMeter(id) {
    const wrap = document.getElementById(`${id}-meter`);
    wrap.innerHTML = '';
    this._segs[id] = [];
    for (let i = 0; i < SOULS; i++) {
      const s = document.createElement('div');
      s.className = 'soul-seg';
      wrap.appendChild(s);
      this._segs[id].push(s);
    }
  },
  updateHP(p1, p2) { this._hp('p1', p1); this._hp('p2', p2); },
  _hp(id, f) {
    const pct = Math.max(0, (f.hp / f.maxHp) * 100);
    const fill = document.getElementById(`${id}-hp`);
    const dmg = document.getElementById(`${id}-hp-dmg`);
    fill.style.width = pct + '%';
    dmg.style.width = pct + '%';
    fill.classList.toggle('low', pct < 30);
  },
  updateMeter(p1, p2) { this._meter('p1', p1); this._meter('p2', p2); },
  _meter(id, f) {
    const per = f.maxMeter / SOULS; // ~11 points per soul
    this._segs[id].forEach((s, i) => {
      s.classList.toggle('lit', f.meter >= (i + 1) * per - 0.001);
    });
    const wrap = document.getElementById(`${id}-meter`);
    wrap.classList.toggle('full', f.meter >= f.maxMeter - 0.001);
  },
  setTimer(v) {
    const t = document.getElementById('timer');
    t.textContent = (v === '∞' || v === Infinity || (typeof v === 'number' && !isFinite(v))) ? '∞' : String(v).padStart(2, '0');
  },
  setRounds(wins, target) {
    // Round pips rebuild to the match's round target (T7 HUD shows the
    // pips for the rounds actually needed, not a fixed pair).
    const t = Math.min(5, Math.max(1, target || 2));
    for (const side of ['p1', 'p2']) {
      const host = document.getElementById(side + '-pips');
      if (!host) continue;
      while (host.children.length < t) {
        const s = document.createElement('span');
        s.className = 'round-pip';
        host.appendChild(s);
      }
      while (host.children.length > t) host.removeChild(host.lastChild);
      for (let i = 0; i < host.children.length; i++) {
        host.children[i].classList.toggle('win', (wins[side] || 0) > i);
      }
    }
  },
  banner(text) {
    const b = document.getElementById('round-banner');
    b.textContent = text;
    b.classList.remove('show'); void b.offsetWidth;
    b.classList.add('show');
    setTimeout(() => b.classList.remove('show'), 1400);
  },
  surgeFlash(color, accent) {
    const el = document.getElementById('surge-flash');
    const c = '#' + color.toString(16).padStart(6, '0');
    const a = '#' + accent.toString(16).padStart(6, '0');
    el.style.background = `radial-gradient(circle at 50% 55%, ${a}cc 0%, ${c}88 34%, ${c}22 60%, transparent 78%)`;
    el.classList.remove('show'); void el.offsetWidth;
    el.classList.add('show');
    setTimeout(() => el.classList.remove('show'), 900);
  },
  surgeName(name) {
    const el = document.getElementById('surge-name');
    el.textContent = 'SOUL SURGE — ' + name;
    el.classList.remove('show'); void el.offsetWidth;
    el.classList.add('show');
    setTimeout(() => el.classList.remove('show'), 1600);
  },
  setRage(id, on) {
    const el = document.getElementById(`${id}-rage`);
    if (el) el.classList.toggle('on', !!on);
  },
  rageArtFlash() {
    const el = document.getElementById('rage-flash');
    if (!el) return;
    el.classList.remove('show'); void el.offsetWidth;
    el.classList.add('show');
    setTimeout(() => el.classList.remove('show'), 600);
  },
  setUrge(id, on) {
    const wrap = document.getElementById(`${id}-urge-wrap`);
    if (wrap) wrap.classList.toggle('on', !!on);
  },
  updateUrge(p1, p2) { this._urge('p1', p1); this._urge('p2', p2); },
  _urge(id, f) {
    const fill = document.getElementById(`${id}-urge`);
    if (!fill || !f) return;
    const pct = f._urgeOn ? Math.max(0, Math.min(100, (f._urgeT / 15) * 100)) : 0;
    fill.style.width = pct + '%';
  },
  combo(n) {
    const pop = document.getElementById('combo-pop');
    document.getElementById('combo-num').textContent = n;
    pop.classList.remove('show'); void pop.offsetWidth;
    pop.classList.add('show');
    clearTimeout(this._comboT);
    this._comboT = setTimeout(() => pop.classList.remove('show'), 900);
  },
  /* Stream 6: throw-break prompt. show=false clears. breakInput '1'/'2'/'1+2'
     tells the defender which limb button breaks the throw (Tekken rules). */
  throwBreakPrompt(show, breakInput) {
    const el = document.getElementById('throw-prompt');
    if (!el) return;
    clearTimeout(this._throwT);
    if (!show) { el.classList.remove('show'); return; }
    const label = breakInput === '1' ? 'TAP LP' : breakInput === '2' ? 'TAP RP' : 'TAP LP+RP';
    el.querySelector('.throw-prompt-key').textContent = label;
    el.classList.remove('show'); void el.offsetWidth;
    el.classList.add('show');
    this._throwT = setTimeout(() => el.classList.remove('show'), 900);
  },
  throwEscape(playerBroke) {
    const el = document.getElementById('throw-prompt');
    if (!el) return;
    clearTimeout(this._throwT);
    el.querySelector('.throw-prompt-key').textContent =
      playerBroke ? 'ESCAPED!' : 'THROW ESCAPED';
    el.classList.remove('show'); void el.offsetWidth;
    el.classList.add('show', 'escaped');
    this._throwT = setTimeout(() => el.classList.remove('show', 'escaped'), 900);
  },
  /* V-System (owner 2026-10-22). All user-facing names are «name TBD»
     placeholders pending user approval — flagged, not final. */
  vTrigger() {
    this.banner('V-TRIGGER «name TBD» — SOUL AWAKENED');
    this.surgeFlash(0xffd34d, 0xfff2b0);
  },
  vReversal() {
    this.banner('V-REVERSAL «name TBD»');
    this.surgeFlash(0x4da6ff, 0xbfe0ff);
  },
  vShift() { this.surgeFlash(0x7df9ff, 0xd8fbff); },
  vShiftBreak() {
    this.banner('V-SHIFT «name TBD» — BREAK!');
    this.surgeFlash(0xffffff, 0x7df9ff);
  },
  vParry() {
    this.banner('V-SKILL PARRY «name TBD»');
    this.surgeFlash(0x9fd8ff, 0xe8f6ff);
  },
  matchOver(playerWon) {
    document.getElementById('result-title').textContent = playerWon ? 'YOU WIN!' : 'YOU LOSE';
    document.getElementById('result-sub').textContent = playerWon
      ? 'The multiverse remembers this one.'
      : 'The shrine is silent. Run it back.';
    try { music.playVictory(); } catch (e) {}
    show('result');
  },
};

/* ---------------- Bootstrap ---------------- */
const canvas = document.getElementById('game-canvas');
const input = new InputManager();
input.init();
const game = new Game(canvas, input, ui);
// Photo mode (DOA-style): P/F9 pauses into a free camera anywhere in a
// fight. Loaded on demand; no-op until first toggled.
import('./photomode.js').then(({ installPhotoMode }) => installPhotoMode(game))
  .catch(() => {});
ui._buildMeter('p1');
ui._buildMeter('p2');

let selectedChar = null;
let assetsReady = false;

/* ---- Game modes (lane 5): versus / arcade / story(+reincarnation) / training.
   The controller owns mode state; main.js just routes menu + select events. */
/* LOADSPEED: modes.js (54KB) is the biggest menu-only module that boot
   doesn't need — no mode runs until a menu button is tapped. The
   controller is built on the first mode tap (getModes) and every use
   site awaits it. window.__modes is set then, as before. */
let modes = null;
let _modesPromise = null;
function getModes() {
  if (modes) return Promise.resolve(modes);
  if (!_modesPromise) {
    _modesPromise = lazy.modes().then(({ ModeController }) => {
      modes = new ModeController({
        game, ui, show, startFight: startFightViaStage,
        roster: ROSTER, getChar: getCharacterWithCustom, audio,
      });
      window.__modes = modes;
      return modes;
    }).catch((err) => {
      // A failed load must not permanently wedge every mode button for the
      // session: drop the rejected promise so the next tap retries the load.
      _modesPromise = null;
      throw err;
    });
  }
  return _modesPromise;
}
/* ---- Rank battle (worker 30): offline ranked ladder, lazy like modes ----
   RankBattleController lives in js/ranks.js and mirrors ModeController's
   deps. rankBattleSelect routes the select-screen confirm into it. */
let rankBattle = null;
let _rankBattlePromise = null;
let rankBattleSelect = false;
function getRankBattle() {
  if (rankBattle) return Promise.resolve(rankBattle);
  if (!_rankBattlePromise) {
    _rankBattlePromise = lazy.ranks().then((m) => {
      rankBattle = new m.RankBattleController({
        game, ui, show, startFight: startFightViaStage,
        roster: ROSTER, getChar: getCharacterWithCustom, audio,
      });
      return rankBattle;
    });
  }
  return _rankBattlePromise;
}
/* ---- Game modes (lane 5) + stage select (lane 4) integration ----
   The mode controller owns mode state and fight setup; versus-mode fights
   route through the CHOOSE YOUR ARENA screen. Arcade/story/training keep
   their mode-dictated flow (stage comes from the mode, not the player). */
let pendingFight = null;
function startFightViaStage(p1, p2, opts = {}) {
  // Versus SETUP: stage RANDOM skips the arena screen — the random stage
  // picked in modes.js _beginVersus rides opts.stage straight in.
  if (opts.mode !== 'versus' || opts.skipStage) { startFight(p1, p2, opts); return; }
  pendingFight = { p1, p2, opts };
  buildStageSelect();
  show('stage');
  requestAnimationFrame(() => requestAnimationFrame(() => mark('stage-interactive')));
  const hint = document.getElementById('stage-hint');
  const s = getStage(selectedStage);
  if (hint && s) hint.textContent = s.name;
  const btn = document.getElementById('confirm-stage');
  if (btn) btn.disabled = false;
}

/* TEKKEN 3 LESSON: don't load fighters at boot. Menu + select use PNG
   portraits — 3D models load on demand at fight start (see assets.js).
   Boot is instant; the "loading" overlay is skipped entirely. */
(function bootClean() {
  const overlay = document.getElementById('loading');
  assetsReady = true; // menu needs no 3D — enable immediately
  if (overlay) overlay.classList.add('hidden');
})();

/* Get custom fighter as roster entry (for lookups by ID) */
function getCustomRosterEntry(id) {
  if (id !== 'custom') return null;
  const raw = getCustomFighter();
  return raw ? customFighterToRoster(raw) : null;
}

/* Override getCharacter to include custom fighter */
const _origGetCharacter = getCharacter;
function getCharacterWithCustom(id) {
  if (id === 'custom') return getCustomRosterEntry('custom');
  return _origGetCharacter(id);
}

/* ---------------- Character select (Tekken-style, 2026-10-20) ----------------
   The select screen — bisected live-3D P1/P2 fighters zone,
   contained card strip, on-select attire switching (P = attire 1,
   K = attire 2) — lives in js/select-screen.js, built from the
   teardown selector record. main.js only wires it into the mode
   flow: a highlight mirrors selectedChar, and CONFIRM routes
   through the module's lock state before modes.onConfirm runs. */
function composedRoster() {
  const list = [...ROSTER];
  const customRaw = getCustomFighter();
  if (customRaw) {
    const custom = customFighterToRoster(customRaw);
    if (custom) list.push(custom);
  }
  return list;
}
selectScreen = createSelectScreen({
  roster: composedRoster,
  findChar: (id) => ROSTER.find(x => x.id === id) || getCustomRosterEntry(id),
  audio,
  onHighlight: (c) => { selectedChar = c ? c.id : null; },
});
window.__selectScreen = selectScreen; // QA hook (same pattern as __modes/__game)
selectScreen.build();

/* ---------------- Stage select (Lane 4) ----------------
   After the fighter is confirmed, pick the arena: 8 canon Eastern
   Mind lands + 15 Tekken 3 retro arenas (real teardown geometry). */
let selectedStage = 'shrine';

/* LOADSPEED: stage-thumb atlas (Urban Reign VGS lesson — Namco packs each
   menu screen into ONE tiled texture instead of dozens of files). The 41
   thumbs used to be 41 separate PNG requests on stage-select open; now one
   atlas.png + one tiny atlas.json serve them all via background-position.
   Cards render instantly with the palette swatch and upgrade to real thumbs
   when the single atlas arrives. Missing tiles keep the swatch. */
const THUMB_ATLAS_URL = 'assets/stages/thumbs/atlas.png';
let _thumbAtlasP = null;
function thumbAtlas() {
  if (!_thumbAtlasP) {
    _thumbAtlasP = fetch('assets/stages/thumbs/atlas.json')
      .then(r => (r.ok ? r.json() : null))
      .catch(() => null);
  }
  return _thumbAtlasP;
}
function buildStageSelect() {
  const grid = document.getElementById('stage-grid');
  if (!grid) return;
  grid.innerHTML = '';
  const paint = (atlas) => {
    for (const tier of STAGE_TIERS) {
      const stages = STAGES.filter(s => s.tier === tier);
      if (!stages.length) continue;
      const tierHeader = document.createElement('div');
      tierHeader.className = 'tier-header';
      tierHeader.textContent = tier;
      grid.appendChild(tierHeader);
      for (const s of stages) {
        const card = document.createElement('div');
        card.className = 'stage-card' + (s.id === selectedStage ? ' selected' : '');
        card.dataset.id = s.id;
        const o = atlas && atlas.offsets && atlas.offsets[s.id];
        // Atlas is a 7x6 tile grid: percentage positioning keeps the div
        // responsive (CSS: width 100%, aspect 16/9) at any card size.
        const visual = o
          ? `<div class="sthumb" role="img" aria-label="${s.name}" style="background-image:url('${THUMB_ATLAS_URL}');background-size:700% 600%;background-repeat:no-repeat;background-position:${(o.x / o.w / 6 * 100).toFixed(2)}% ${(o.y / o.h / 5 * 100).toFixed(2)}%;"></div>`
          : `<div class="swatch" style="background:linear-gradient(135deg, ${s.swatch[0]}, ${s.swatch[1]})"></div>`;
        card.innerHTML =
          `${visual}<div class="sname">${s.name}</div><div class="suniverse">${s.universe}</div>`;
        card.addEventListener('click', () => selectStageCard(card, s));
        grid.appendChild(card);
      }
    }
  };
  paint(null); // instant: swatches first, never waits on the atlas
  // Preview pane + scroll track the selected stage (main 2026-10-21/22); rerun after the
  // atlas repaint, which recreates the cards.
  const afterPaint = () => {
    const cur = getStage(selectedStage);
    if (cur) updateStagePreview(cur);
    const sel = grid.querySelector('.stage-card.selected');
    if (sel) scrollStageCardIntoView(sel);
  };
  afterPaint();
  thumbAtlas().then((atlas) => {
    const sc = document.getElementById('screen-stage');
    if (!atlas || !sc || !sc.classList.contains('active')) return;
    grid.innerHTML = '';
    paint(atlas); // upgrade: real thumbs once the single atlas arrives
    afterPaint();
  });
}
/* Bring a stage card into the grid's visible window by writing
   scrollTop directly. scrollIntoView relies on a smooth-scroll
   animation (the grid has scroll-behavior:smooth) whose timeline
   stalls whenever the main thread is busy — measured headless
   2026-10-21: scrollIntoView left scrollTop at 0 while a direct
   write scrolled instantly. Direct writes are frame-perfect on
   real hardware too. */
function scrollStageCardIntoView(el) {
  const grid = document.getElementById('stage-grid');
  if (!grid || !el) return;
  const gr = grid.getBoundingClientRect(), r = el.getBoundingClientRect();
  if (r.top < gr.top) grid.scrollTop -= (gr.top - r.top) + 8;
  else if (r.bottom > gr.bottom) grid.scrollTop += (r.bottom - gr.bottom) + 8;
}
/* Tekken pattern: the large preview pane (image + name + description,
   inside the layout) always tracks the highlighted stage — a card tap,
   a RANDOM roll, or keyboard focus all drive the same single state. */
function updateStagePreview(s) {
  const img = document.getElementById('stage-preview-img');
  const sw = document.getElementById('stage-preview-swatch');
  const showSwatch = () => {
    if (img) img.style.display = 'none';
    if (sw) {
      sw.hidden = false;
      sw.style.background = `linear-gradient(135deg, ${s.swatch[0]}, ${s.swatch[1]})`;
    }
  };
  if (img) {
    // W51: the preview pane markup now exists (index.html). Only set src
    // when there's a thumb AND it changed — most thumbs 404 (atlas tiles
    // serve the cards), and re-setting the same src flickers the pane.
    // Re-highlighting the same stage leaves img/swatch exactly as they are.
    if (s.thumb) {
      if (img.getAttribute('src') !== s.thumb) {
        img.style.display = '';
        img.onerror = showSwatch;
        if (sw) sw.hidden = true;
        img.src = s.thumb;
      }
    } else {
      showSwatch();
    }
    img.alt = s.name;
  }
  const nm = document.getElementById('stage-preview-name');
  if (nm) nm.textContent = s.name;
  const un = document.getElementById('stage-preview-universe');
  if (un) un.textContent = s.universe || '';
  const ds = document.getElementById('stage-preview-desc');
  if (ds) ds.textContent = s.description || '';
  const hint = document.getElementById('stage-hint');
  if (hint) hint.textContent = s.name;
}
function selectStageCard(card, s) {
  audio.uiClick();
  document.querySelectorAll('.stage-card').forEach(x => x.classList.remove('selected'));
  card.classList.add('selected');
  selectedStage = s.id;
  updateStagePreview(s);
  const btn = document.getElementById('confirm-stage');
  if (btn) btn.disabled = false;
}
function allStageCards() { return [...document.querySelectorAll('.stage-card')]; }
let focusedStageIdx = 0;
function focusStage(i) {
  const cards = allStageCards();
  if (!cards.length) return;
  focusedStageIdx = (i + cards.length) % cards.length;
  cards.forEach(x => x.classList.remove('kb-focus'));
  const el = cards[focusedStageIdx];
  el.classList.add('kb-focus');
  scrollStageCardIntoView(el);
  const s = getStage(el.dataset.id);
  if (s) updateStagePreview(s);
}
document.addEventListener('keydown', (e) => {
  const sc = document.getElementById('screen-stage');
  if (!sc || !sc.classList.contains('active')) return;
  const cards = allStageCards();
  if (!cards.length) return;
  const grid = document.getElementById('stage-grid');
  const cols = grid ? getComputedStyle(grid).gridTemplateColumns.split(' ').length : 2;
  if (e.key === 'ArrowRight') { focusStage(focusedStageIdx + 1); e.preventDefault(); }
  else if (e.key === 'ArrowLeft') { focusStage(focusedStageIdx - 1); e.preventDefault(); }
  else if (e.key === 'ArrowDown') { focusStage(focusedStageIdx + cols); e.preventDefault(); }
  else if (e.key === 'ArrowUp') { focusStage(focusedStageIdx - cols); e.preventDefault(); }
  else if (e.key === 'Enter' || e.key === ' ') {
    const card = cards[focusedStageIdx];
    const s = getStage(card.dataset.id);
    if (s) {
      // W51: same confirm path as the CONFIRM button — bare startFight()
      // here dropped pendingFight (wrong fighters, dead result screen).
      if (selectedStage === s.id) { confirmStageFromSelect(); }
      else selectStageCard(card, s);
    }
    e.preventDefault();
  }
});
/* Deep link: ?stage=<id> pre-selects that arena */
(function () {
  const id = new URLSearchParams(location.search).get('stage');
  if (id && getStage(id)) selectedStage = getStage(id).id;
})();

/* 99-second select timer (Tekken standard selector: starts at 99).
   The countdown starts only once assets are loaded (maybeStartSelectTimer),
   and at 0 it auto-highlights a random fighter — it never starts a fight
   without the user tapping CONFIRM. */
let selectTimerId = null;
let selectTimerArmed = false;
function maybeStartSelectTimer() {
  if (assetsReady && !selectTimerArmed) { selectTimerArmed = true; startSelectTimer(); }
}
function startSelectTimer() {
  stopSelectTimer();
  let t = 99;
  const el = document.getElementById('select-timer');
  el.textContent = t;
  el.classList.remove('low');
  selectTimerId = setInterval(() => {
    t--;
    el.textContent = Math.max(0, t);
    if (t <= 10) el.classList.add('low');
    if (t <= 0) {
      stopSelectTimer();
      // Tekken timeout behavior: cursor jumps to a random fighter, but the
      // match does NOT start — the user still taps CONFIRM to fight.
      const pool = ROSTER.filter(c => c.id !== selectedChar);
      const pick = pool[Math.floor(Math.random() * pool.length)];
      if (pick) selectScreen.selectById(pick.id);
      document.getElementById('select-hint').textContent = 'TIME UP — random fighter picked. Tap CONFIRM to fight.';
    }
  }, 1000);
}
function stopSelectTimer() {
  if (selectTimerId) { clearInterval(selectTimerId); selectTimerId = null; }
}
/* Deep link: ?fighter=<id> pre-selects that fighter on the select screen */
(function () {
  const id = new URLSearchParams(location.search).get('fighter');
  if (id) selectScreen.selectById(id);
})();

/* Random opponent different from the player */
function randomEnemy(excludeId) {
  // Never field a MODEL PENDING fighter (no own model; owner 2026-10-23).
  const pool = ROSTER.filter(c => c.id !== excludeId && !c.modelPending && c.model);
  // Owner pt213u: enemies wear attire 1 (owner model first), not the raw roster key.
  return resolveFighterAttire(pool[Math.floor(Math.random() * pool.length)]);
}

/* ---------------- Menu button wiring ---------------- */
function unlockAudio() {
  audio.unlock();
  music.unlock();
  document.getElementById('tap-to-start').classList.remove('show');
}

document.body.addEventListener('pointerdown', unlockAudio, { once: true });
window.addEventListener('load', () => {
  setTimeout(() => document.getElementById('tap-to-start').classList.add('show'), 600);
});

/* Menu tap failure toast (2026-10-24, menu tap fix): a tap must NEVER
   die silently. Mode loads that reject surface here instead of leaving
   the user on the menu wondering why nothing happened. */
function menuFail(msg) {
  const d = document.createElement('div');
  d.textContent = msg;
  d.style.cssText = 'position:fixed;left:50%;bottom:24px;transform:translateX(-50%);' +
    'background:#1a0b2e;color:#fff;border:1px solid #e63229;border-radius:12px;' +
    'padding:12px 18px;z-index:99999;font-size:14px;max-width:90vw;text-align:center;';
  document.body.appendChild(d);
  setTimeout(() => d.remove(), 3000);
}

/* Touch re-dispatch for data-action elements (2026-10-24, menu tap fix):
   phone taps must route even when the browser does not synthesize a
   click for the tap. A movement-guarded touchend on a [data-action]
   element preventDefaults the emulated click and dispatches one real
   click itself, which the delegated router below handles exactly once.
   Scroll drags (>12px) are ignored so scrolling never triggers a mode.
   mainmenu.js deliberately does NOT bind data-action elements, so this
   cannot double-fire with a card/rail handler. */
let _docTouchSX = 0, _docTouchSY = 0;
document.addEventListener('touchstart', (e) => {
  const t = e.changedTouches[0];
  if (t) { _docTouchSX = t.clientX; _docTouchSY = t.clientY; }
}, { passive: true });
document.addEventListener('touchend', (e) => {
  const t = e.changedTouches[0];
  if (!t) return;
  if (Math.hypot(t.clientX - _docTouchSX, t.clientY - _docTouchSY) > 12) return;
  const el = (e.target instanceof Element) ? e.target.closest('[data-action]') : null;
  if (!el) return;
  e.preventDefault(); // suppress the emulated click — the dispatched click below is the one
  el.click();
}, { passive: false });

/* Delegated data-action router (T8 menu, worker 37): one document-level
   listener covers both the static menu and submenu cards created
   dynamically by mainmenu.js. Previously a one-time forEach at eval. */
document.addEventListener('click', (e) => {
  const t = e.target;
  const el = (t instanceof Element) ? t.closest('[data-action]') : null;
  if (!el) return;
  {
    // Sound must never block navigation: a throwing audio path used to
    // kill the whole router before the mode started.
    try { unlockAudio(); audio.uiClick(); } catch { /* sound is optional */ }
    const a = el.dataset.action;
    if (a === 'play' || a === 'mode-arcade') {
      getModes().then(m => m.startMode('arcade')).catch(() => menuFail('Could not load ARCADE — tap again'));
    }
    else if (a === 'mode-versus') {
      getModes().then(m => m.startMode('versus')).catch(() => menuFail('Could not load VERSUS — tap again'));
    }
    else if (a === 'mode-story') {
      getModes().then(m => m.startMode('story')).catch(() => menuFail('Could not load STORY — tap again'));
    }
    else if (a === 'mode-training') {
      getModes().then(m => m.startMode('training')).catch(() => menuFail('Could not load TRAINING — tap again'));
    }
    else if (a === 'mode-fightlab') {
      getModes().then(m => m.startMode('fightlab')).catch(() => menuFail('Could not load FIGHTLAB — tap again'));
    }
    else if (a === 'mode-survival') {
      getModes().then(m => m.startMode('survival')).catch(() => menuFail('Could not load SURVIVAL — tap again'));
    }
    else if (a === 'mode-timeattack') {
      getModes().then(m => m.startMode('timeattack')).catch(() => menuFail('Could not load TIMEATTACK — tap again'));
    }
    else if (a === 'mode-team') {
      getModes().then(m => m.startMode('team')).catch(() => menuFail('Could not load TEAM — tap again'));
    }
    else if (a === 'mode-qombat') {
      getModes().then(m => m.startMode('qombat')).catch(() => menuFail('Could not load QOMBAT — tap again'));
    }
    else if (a === 'mode-surge') {
      getModes().then(m => m.startMode('surge')).catch(() => menuFail('Could not load SURGE — tap again'));
    }
    else if (a === 'mode-trader') {
      getModes().then(m => m.startMode('trader')).catch(() => menuFail('Could not load TRADER — tap again'));
    }
    else if (a === 'mode-treasure') {
      getModes().then(m => m.startMode('treasure')).catch(() => menuFail('Could not load TREASURE — tap again'));
    }
    else if (a === 'mode-gallery') {
      import('./ui-gaps.js').then(m => m.openGallery()).catch(() => menuFail('Could not load GALLERY — tap again'));
    }
    else if (a === 'mode-jukebox') {
      import('./ui-gaps.js').then(m => m.openJukebox()).catch(() => menuFail('Could not load JUKEBOX — tap again'));
    }
    else if (a === 'mode-replays') {
      import('./ui-gaps.js').then(m => m.openReplays()).catch(() => menuFail('Could not load REPLAYS — tap again'));
    }
    else if (a === 'mode-rankbattle') {
      rankBattleSelect = true;
      getRankBattle().then((rb) => rb.start()).catch(() => menuFail('Could not load RANKED — tap again'));
    }
    else if (a === 'show-ranks') {
      lazy.ranks().then((m) => m.initRanks().then(() => m.openRankHub())).catch(() => menuFail('Could not load RANK HALL — tap again'));
    }
    else if (a === 'mode-create') {
      // Character creation — launches the Create Fighter CAW suite.
      // Returns to game menu via the BACK TO GAME button in the creator.
      audio.uiClick();
      window.location.href = '../customization/creation-suite-ui/index.html';
    }
    else if (a === 'howto') { show('howto'); }
    else if (a === 'close-movelist') { toggleMovelist(false); }
    else if (a === 'back-menu') {
      // CLEAN-INIT: leaving fight → full state reset. No leaked fighters,
      // timers, or listeners carry into the menu.
      game.leaveFight();
      rankBattleSelect = false;
      if (rankBattle) rankBattle.clear();
      getModes().then(m => m.clearState());
      show('menu');
      audio.stopMusic();
    }
    else if (a === 'back-select') {
      rankBattleSelect = false;
      if (rankBattle) rankBattle.clear();
      show('select');
    }
    else if (a === 'rematch') {
      getModes().then(m => { if (m.mode) m.rematch(); else startFight(); });
    }
  }
});

/* T8 main menu router (data-mm, worker 36): the T8-style menu uses data-mm
   attributes, not data-action. This delegated listener wires them up.
   Each navigates to a real screen — no dead ends.
   SUBMENU REBUILD (worker-submenus): rail items (.mm-item) are owned by
   the T8 submenu controller in mainmenu.js — it opens the slide-in
   submenu panel. Yielding here keeps every submenu reachable; without
   this the mode starts underneath and the submenu never shows. */
document.addEventListener('click', (e) => {
  const t = e.target;
  const el = (t instanceof Element) ? t.closest('[data-mm]') : null;
  if (!el) return;
  if (el.classList && el.classList.contains('mm-item')) return; // submenu controller owns rail items
  unlockAudio();
  audio.uiClick();
  // T7 SubMenu_mc (owner, PR #901 follow-up): a main-menu rail item opens
  // its mode-select submenu (mainmenu.js) instead of jumping straight to a
  // mode; the submenu's cards then route through data-action as before.
  if (el.closest('#mm-list') && document.getElementById('mm-submenu')) return;
  const m = el.dataset.mm;
  if (m === 'story') {
    getModes().then(modes => modes.startMode('story')).catch(() => menuFail('Could not load STORY — tap again'));
  }
  else if (m === 'versus') {
    getModes().then(modes => modes.startMode('versus')).catch(() => menuFail('Could not load VERSUS — tap again'));
  }
  else if (m === 'online') {
    show('online');
  }
  else if (m === 'arcade') {
    getModes().then(modes => modes.startMode('arcade')).catch(() => menuFail('Could not load ARCADE — tap again'));
  }
  else if (m === 'sidegames') {
    show('sidegames');
  }
  else if (m === 'training') {
    getModes().then(modes => modes.startMode('training')).catch(() => menuFail('Could not load TRAINING — tap again'));
  }
  else if (m === 'creation') {
    window.location.href = '../customization/creation-suite-ui/index.html';
  }
  else if (m === 'collection') {
    show('collection');
  }
  else if (m === 'daily') {
    show('daily');
  }
  else if (m === 'options') {
    show('howto'); // Options: howto screen has settings
  }
});

/* Confirm routing: the mode controller owns the select flow
   (versus needs a P1→P2 two-step; other modes start on confirm).
   Lane 4 integration: versus-mode fights route through the stage-select
   screen via startFightViaStage (wired as the ModeController's startFight
   dep below); arcade/story/training use their mode-dictated flow. */
async function confirmSelection() {
  if (!selectedChar) return;
  const id = selectedChar;
  selectedChar = null; // clear synchronously BEFORE any await: a fast double-tap
  // used to re-enter here during the getModes() gap and confirm the same
  // fighter twice (P2 = P1), which startFight() turned into a random opponent.
  audio.uiClick();
  // Select-screen lock state first (P1 lock -> P2 cursor in versus),
  // then the mode controller routes the fight.
  selectScreen.notifyConfirm(id);
  if (rankBattleSelect) {
    rankBattleSelect = false;
    (await getRankBattle()).onConfirm(id);
    return;
  }
  (await getModes()).onConfirm(id);
}

document.getElementById('confirm-fighter').addEventListener('click', confirmSelection);

/* Lane 4: stage-select screen handlers (CHOOSE YOUR ARENA).
   P0 (2026-10-22): the old handler nulled pendingFight up front and never
   caught startFight rejections — any failure left the player on a dead
   stage screen with no feedback and no way to retry ("fight never starts").
   Now: visible loading state on the stage screen, failures surface there,
   and pendingFight is only consumed when the fight actually starts, so
   CONFIRM retries the same fight. W51: extracted so the keyboard Enter
   path runs the SAME confirm — a bare startFight() there used to ignore
   pendingFight, booting the wrong fighters with no versus onMatchEnd
   (dead result screen). */
function confirmStageFromSelect() {
  if (!selectedStage || !pendingFight) return;
  audio.uiClick();
  const { p1, p2, opts } = pendingFight;
  const btn = document.getElementById('confirm-stage');
  const hint = document.getElementById('stage-hint');
  if (btn) btn.disabled = true;
  if (hint) hint.textContent = 'Entering the arena…';
  startFight(p1, p2, { ...opts, stage: selectedStage }).then(
    (started) => {
      if (started) { pendingFight = null; return; }
      // startFight reported the failure on the hints already.
      if (btn) btn.disabled = false;
    },
    (err) => {
      console.error('[WH] stage-select: fight failed to start:', err);
      if (hint) hint.textContent = 'Could not start the fight — tap CONFIRM to retry.';
      if (btn) btn.disabled = false;
    }
  );
}

document.getElementById('confirm-stage').addEventListener('click', confirmStageFromSelect);

document.getElementById('random-stage').addEventListener('click', () => {
  audio.uiClick();
  selectedStage = randomStageId();
  const s = getStage(selectedStage);
  const card = document.querySelector(`.stage-card[data-id="${s.id}"]`);
  if (card) {
    selectStageCard(card, s);
    const idx = allStageCards().indexOf(card);
    if (idx >= 0) focusStage(idx);
  }
});

/* Training quit button (HUD, visible only in training mode) */
document.getElementById('training-quit').addEventListener('click', () => {
  audio.uiClick();
  game.leaveFight();
  getModes().then(m => m.clearState());
  show('menu');
  audio.stopMusic();
});

/* Stream 6: per-fighter movelist (training mode HUD button + M key).
   Overlay only — the fight keeps running underneath. */
const MOVESET_GROUPS = [
  ['signature', 'SIGNATURE'],
  ['throw', 'THROWS'],
  ['special', 'SPECIALS'],
  ['string', 'STRINGS'],
  ['strike', 'STRIKES'],
];
async function renderMovelist() {
  // LOADSPEED: movesets.js loads on demand (fight time), not at boot.
  const { getFighterMoveset, resolveMoveKey } = await lazy.movesets();
  const fid = game.p1 && game.p1.char.id;
  const ms = fid && getFighterMoveset(fid);
  const groups = document.getElementById('movelist-groups');
  document.getElementById('movelist-title').textContent =
    'MOVE LIST — ' + (ms ? (ms.display || fid.toUpperCase()) : '???');
  const inputs = ms ? Object.keys(ms.slots || ms.moves) : [];
  document.getElementById('movelist-sub').textContent =
    ms ? `${inputs.length} inputs · ${Object.keys(ms.moves).length} moves · ${ms.tekken_base || ''}` : 'no data';
  groups.innerHTML = '';
  if (!ms || !ms.moves) return;
  // One row per INPUT: the move that input fires for this fighter (moveset editor
  // loadout > default slots). Alternates stay in the file for the editor.
  const byClass = {};
  for (const notation of inputs) {
    const key = resolveMoveKey(fid, notation);
    const m = key && ms.moves[key];
    if (!m) continue;
    const cls = m.move_class || (m.throw ? 'throw' : 'strike');
    (byClass[cls] = byClass[cls] || []).push([notation, m]);
  }
  const shown = new Set();
  for (const [cls, label] of MOVESET_GROUPS) {
    const list = byClass[cls];
    if (!list || !list.length) continue;
    shown.add(cls);
    const g = document.createElement('div');
    g.className = 'movelist-group';
    g.innerHTML = `<h3>${label} (${list.length})</h3>`;
    for (const [key, m] of list) {
      const fr = Math.round((m.startup || 0) * 60);
      const brk = m.throw_break
        ? `<span class="ml-break">break ${m.throw_break === '1' ? 'LP' : m.throw_break === '2' ? 'RP' : 'LP+RP'}</span>` : '';
      const row = document.createElement('div');
      row.className = 'movelist-row';
      row.innerHTML = `<span class="ml-input">${key}</span>` +
        `<span class="ml-name">${m.name || ''} ${brk}</span>` +
        `<span class="ml-data">${m.damage}dmg ${fr}f</span>`;
      g.appendChild(row);
    }
    groups.appendChild(g);
  }
  // anything unclassified
  const rest = Object.entries(byClass).filter(([c]) => !shown.has(c))
    .flatMap(([, l]) => l);
  if (rest.length) {
    const g = document.createElement('div');
    g.className = 'movelist-group';
    g.innerHTML = '<h3>OTHER (' + rest.length + ')</h3>';
    for (const [key, m] of rest) {
      const row = document.createElement('div');
      row.className = 'movelist-row';
      row.innerHTML = `<span class="ml-input">${key}</span>` +
        `<span class="ml-name">${m.name || ''}</span>` +
        `<span class="ml-data">${m.damage}dmg</span>`;
      g.appendChild(row);
    }
    groups.appendChild(g);
  }
}
async function toggleMovelist(open) {
  const el = document.getElementById('screen-movelist');
  const willOpen = open === undefined ? !el.classList.contains('active') : open;
  if (willOpen) await renderMovelist();
  el.classList.toggle('active', willOpen);
}
document.getElementById('movelist-btn').addEventListener('click', () => {
  audio.uiClick(); toggleMovelist();
});

async function startFight(playerId, enemyId, opts = {}) {
  unlockAudio();
  if (typeof playerId === 'string') selectedChar = playerId;
  // Lane 4: stage-select may pass an explicit stage via opts.
  if (opts.stage && getStage(opts.stage)) selectedStage = getStage(opts.stage).id;
  // modes lane: opts may carry full char-entry overrides (force-buffed
  // player, scaled-AI foe, the Assembled Soul boss, training dummy).
  // Stream 4: the player's selected attire applies in every mode.
  const firstReady = (ROSTER.find(c => !c.modelPending && c.model) || ROSTER[0]).id;
  let player = resolveFighterAttire(
    opts.playerChar || getCharacterWithCustom(selectedChar || firstReady));
  // MODEL PENDING fighters (no own model yet) never enter a fight on another body.
  if (player.modelPending || !player.model) player = resolveFighterAttire(getCharacterWithCustom(firstReady));
  let enemy = opts.enemyChar ||
    (typeof enemyId === 'string' && enemyId !== player.id ? resolveFighterAttire(getCharacterWithCustom(enemyId)) : randomEnemy(player.id));
  if (!enemy || enemy.modelPending || !enemy.model) enemy = randomEnemy(player.id);
  // On-demand: load only the 2 fighters for this fight (Tekken 3 pattern).
  // Models may already be prefetched from select-screen highlight.
  const need = [...new Set([player.model, enemy.model].filter(Boolean))];
  // Mid-match transform targets must be preloaded (createInstance is sync).
  for (const c of [player, enemy]) {
    if (c.transform && c.transform.targetModel) need.push(c.transform.targetModel);
    if (c.forms) for (const fk of Object.keys(c.forms)) {
      const fe = c.forms[fk];
      const tgts = fe.target ? [fe] : [fe.up, fe.down].filter(Boolean);
      for (const t of tgts) if (t.target) need.push(t.target);
    }
  }
  const hint = document.getElementById('select-hint');
  const confirmBtn = document.getElementById('confirm-fighter');
  // FIGHT-LOAD FIX (2026-10-24): versus fights start from the STAGE screen,
  // so the stage hint is the visible one — mirror every load phase there.
  // On failure, hide the loading overlay (it otherwise traps the player on
  // the loading screen until its 45s safety timer) and name the asset that
  // failed instead of a generic message. pendingFight is kept so CONFIRM
  // retries the same fight.
  const stageHintEl = document.getElementById('stage-hint');
  const setPhase = (t) => { if (hint) hint.textContent = t; if (stageHintEl) stageHintEl.textContent = t; };
  const hideLoadOverlay = () => { const o = document.getElementById('wh-loading'); if (o) o.classList.remove('show'); };
  try {
    setPhase('Entering the arena…');
    // LOADSPEED: fight-only modules (fighter/movesets/t3anims) stream in
    // here — they are warmed during menu idle, so this usually resolves
    // from cache. The real-Tekken moveset JSONs (~300KB) also load here
    // instead of at boot (they are fight data, not menu data).
    const [F, MS, T3] = await Promise.all([lazy.fighter(), lazy.movesets(), lazy.t3anims()]);
    const { ensureMovesets } = MS;
    const { bankIdFor, loadRealMovesets } = F;
    const { loadT3Clips } = T3;
    setPhase('Loading move lists…');
    await Promise.all([loadRealMovesets(), MS.loadFighterMovesets()]);
    // Show the TRANSFORM touch button only for fighters that can transform.
    const tBtn = document.querySelector('.act-btn.transform');
    if (tBtn) tBtn.style.display = (player.transform || player.forms) ? '' : 'none';
    if (confirmBtn) confirmBtn.disabled = true;
    await assets.loadModels(need, (p, loaded, total, id) => {
      if (window.__whLoadProgress) window.__whLoadProgress(p, loaded, total);
      let t;
      if (loaded && total) {
        const mbL = (loaded / 1048576).toFixed(1);
        const mbT = (total / 1048576).toFixed(1);
        t = `Entering the arena… ${mbL}/${mbT} MB${id ? ` · ${id}` : ''}`;
      } else {
        t = `Entering the arena… ${Math.round(p * 100)}%`;
      }
      if (hint) hint.textContent = t;
      if (stageHintEl) stageHintEl.textContent = t;
    });
    // Load the REAL T3 animation banks for THIS match's two fighters —
    // each fighter's own moveset-source bank (per-bank wiring 2026-10-19).
    // Fighters whose source has no decoded bank are skipped here and
    // fall back to embedded locomotion + procedural combat. (Heihachi
    // source fighters have their own real bank since 2026-10-20.)
    // Full movesets for this fight (lazy since 2026-10-21; boot loads only the index).
    // Transform forms may switch moveset mid-fight, so theirs load too.
    setPhase('Loading move lists…');
    const msIds = [player.id, enemy.id];
    for (const c of [player, enemy]) {
      if (c.forms) for (const fk of Object.keys(c.forms)) {
        const fe = c.forms[fk];
        for (const t of (fe.target ? [fe] : [fe.up, fe.down].filter(Boolean))) if (t.moveset) msIds.push(t.moveset);
      }
    }
    await ensureMovesets(msIds);
    setPhase('Loading real fight motion…');
    try {
      const banks = [...new Set([bankIdFor(player.id), bankIdFor(enemy.id)].filter(Boolean))];
      await Promise.all(banks.map(b => loadT3Clips(THREE, b)));
    } catch (e) {
      console.warn('[WH] T3 clips failed, using procedural fallback:', e.message || e);
    }
    // TEKKEN GRAPPLE (2026-10-24): load the throw tables
    // (reactions.json) and this match's two reaction packs BEFORE
    // the fight starts, so a connecting grab can bind its file
    // pair immediately instead of falling back to the legacy
    // lock. A failure here is NOT fatal: throws keep the legacy
    // lock path and are logged UNMAPPED at connect time.
    setPhase('Loading throw pairs…');
    try {
      const { loadReactionPack } = T3;
      await loadThrowTables();
      const banks = [...new Set([bankIdFor(player.id), bankIdFor(enemy.id)].filter(Boolean))];
      await Promise.all(banks.map(b => loadReactionPack(THREE, b)));
    } catch (e) {
      console.warn('[WH] throw pairs unavailable, legacy throw lock:', e.message || e);
    }
  } catch (err) {
    console.error('[WH] fight load failed:', err);
    // Name the failing asset: a bare "check connection" hides a 404 for a
    // model path that only exists on one host (2026-10-24: every roster/
    // model 404'd on Netlify because its publish dir is game/ only and no
    // /roster/* proxy existed). P0 (2026-10-22) still holds: the stage
    // screen is where versus fights start, so the error must be visible
    // there, not only on the fighter-select hint.
    const detail = (err && (err.message || err)) || 'unknown error';
    const msg = `Failed to load fighters: ${detail} — tap CONFIRM to retry.`;
    if (hint) hint.textContent = msg;
    if (stageHintEl) stageHintEl.textContent = msg;
    hideLoadOverlay();
    if (confirmBtn) confirmBtn.disabled = false;
    const stageBtn = document.getElementById('confirm-stage');
    if (stageBtn) stageBtn.disabled = false;
    return false;
  }
  if (confirmBtn) confirmBtn.disabled = false;
  show('hud');
  game.paused = false;
  // MUSIC (2026-10-24): rotating stage pool. The engine falls back to
  // the procedural loop internally when no file track is available, so
  // the old direct audio.startMusic() call is replaced, not doubled.
  music.playBattle(selectedStage);
  // FIGHT-LOOP REPAIR (worker 54, 2026-10-22): startMatch ran OUTSIDE the
  // load try/catch — a throw inside it (Fighter build, arena setStage, AI
  // wiring) was an unhandled rejection that stranded the player on the
  // stage screen with "Entering the arena…". Surface it like the load
  // failures above instead of dying silently.
  try {
    await game.startMatch(player, enemy, selectedStage, opts);
  } catch (err) {
    console.error('[WH] startMatch failed:', err);
    const detail = (err && (err.message || err)) || 'unknown error';
    const msg = `Failed to start the fight: ${detail} — try again or pick different fighters.`;
    if (hint) hint.textContent = msg;
    if (stageHintEl) stageHintEl.textContent = msg;
    hideLoadOverlay();
    const stageBtn = document.getElementById('confirm-stage');
    if (stageBtn) stageBtn.disabled = false;
    show('stage');
    return false;
  }
  // Control hints: show for 6s at fight start, H toggles
  const hints = document.getElementById('control-hints');
  if (hints) {
    hints.classList.remove('fade');
    clearTimeout(hints._t);
    hints._t = setTimeout(() => hints.classList.add('fade'), 6000);
  }
  return true; // P0 (2026-10-22): stage-select handler needs to know the fight started
}
// H toggles control hints, M toggles the movelist (training)
document.addEventListener('keydown', (e) => {
  if (e.code === 'KeyH') {
    const hints = document.getElementById('control-hints');
    if (hints) hints.classList.toggle('fade');
  }
  if (e.code === 'KeyM') {
    const btn = document.getElementById('movelist-btn');
    if (btn && btn.style.display !== 'none') toggleMovelist();
  }
});

document.addEventListener('visibilitychange', () => {
  if (document.hidden) { game.paused = true; }
  else if (game.running) { game.paused = false; }
});

// expose for debugging / verification
window.__game = game;
window.__ui = ui;
window.__stages = STAGES;

// Stream 4: modes & menus — pause, options, loading, VS screen, records,
// The Heart and Mind Inside + Character Episodes controllers.
initMenus({ show, startFight: startFightViaStage, game, ui, ROSTER, getChar: getCharacterWithCustom, audio });

// New Western Heart menu/UI (game/ui-wh/) behind a toggle; classic menus stay as fallback.
if (whUiEnabled()) mountWhUi({ game, ui, show, startFight, ROSTER });

/* LOADSPEED: the menu shell is interactive now. Warm the fight-only
   modules during idle (Tekken: stream records while the player reads
   the menu) and stamp the boot->menu timing mark on first paint. */
warmIdle();
// QA hooks (window.__modes) and the first mode tap expect the controller soon after boot.
// Warm on a guaranteed timer, not only on idle: a busy/loaded page may never
// report an idle window, leaving the first mode tap to cold-load modes.js —
// a tap with no feedback. 800ms is safely post-first-paint and the dynamic
// import never blocks it.
setTimeout(() => { getModes().catch(() => {}); }, 800);
requestAnimationFrame(() => requestAnimationFrame(() => mark('menu-interactive')));

/* Menu routers above are bound (delegated data-action + data-mm listeners
   registered at module evaluation). The non-module fallback binder in
   index.html checks this flag and stays dormant when the module chain
   loaded fine. (PR #676 rebase, worker 55.) */
window.__whMenuBound = true;
