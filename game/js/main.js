/* ============================================================
   WESTERN HEART — main bootstrap
   Screen flow, character select, HUD bindings (Nine-Soul Meter
   with 9 soul segments), Soul Surge screen flash.
   ============================================================ */
import { Game } from './game.js';
import { InputManager } from './input.js';
import { audio } from './audio.js';
import { assets } from './assets.js';
import { ROSTER, getCharacter } from './characters.js';
import { loadRealMovesets } from './fighter.js';
import { loadFighterMovesets } from './movesets.js';
import { loadT3Clips } from './t3anims.js';
import * as THREE from 'three';
import { whUiEnabled, mountWhUi } from './ui-wh-bridge.js';
import { getCustomFighter, customFighterToRoster } from './custom-fighter.js';
import { STAGES, STAGE_TIERS, getStage, randomStageId } from './stages.js';
import { ModeController } from './modes.js';

// Load REAL Tekken 3 moveset data (not hand-written frame data)
loadRealMovesets();
// Load per-fighter Tekken movelists (1/2/3/4, throws, strings, specials) — LANE 3
loadFighterMovesets();

const screens = {
  menu:   document.getElementById('screen-menu'),
  howto:  document.getElementById('screen-howto'),
  select: document.getElementById('screen-select'),
  stage:  document.getElementById('screen-stage'),
  result: document.getElementById('screen-result'),
  hud:    document.getElementById('hud'),
  stage:      document.getElementById('screen-stage'),
  reincarnate: document.getElementById('screen-reincarnate'),
  trader:  document.getElementById('screen-trader'),
  modewin: document.getElementById('screen-modewin'),
};
function show(name) {
  Object.values(screens).forEach(s => s.classList.remove('active'));
  if (screens[name]) screens[name].classList.add('active');
  // Tekken 99s select timer: runs only on the select screen, and only once the
  // ~30MB assets are loaded — slow phones don't lose selection time to loading.
  if (name === 'select') {
    maybeStartSelectTimer();
    // Start downloading both fighter models the moment select opens —
    // by the time the user picks and hits CONFIRM, they're usually cached.
    assets.preloadAll();
  }
  else { selectTimerArmed = false; stopSelectTimer(); }
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
  setTimer(v) { document.getElementById('timer').textContent = String(v).padStart(2, '0'); },
  setRounds(wins) {
    document.getElementById('p1-r1').classList.toggle('win', wins.p1 >= 1);
    document.getElementById('p1-r2').classList.toggle('win', wins.p1 >= 2);
    document.getElementById('p2-r1').classList.toggle('win', wins.p2 >= 1);
    document.getElementById('p2-r2').classList.toggle('win', wins.p2 >= 2);
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
  combo(n) {
    const pop = document.getElementById('combo-pop');
    document.getElementById('combo-num').textContent = n;
    pop.classList.remove('show'); void pop.offsetWidth;
    pop.classList.add('show');
    clearTimeout(this._comboT);
    this._comboT = setTimeout(() => pop.classList.remove('show'), 900);
  },
  matchOver(playerWon) {
    document.getElementById('result-title').textContent = playerWon ? 'YOU WIN!' : 'YOU LOSE';
    document.getElementById('result-sub').textContent = playerWon
      ? 'The multiverse remembers this one.'
      : 'The shrine is silent. Run it back.';
    show('result');
  },
};

/* ---------------- Bootstrap ---------------- */
const canvas = document.getElementById('game-canvas');
const input = new InputManager();
input.init();
const game = new Game(canvas, input, ui);
ui._buildMeter('p1');
ui._buildMeter('p2');

let selectedChar = null;
let assetsReady = false;

/* ---- Game modes (lane 5): versus / arcade / story(+reincarnation) / training.
   The controller owns mode state; main.js just routes menu + select events. */
/* ---- Game modes (lane 5) + stage select (lane 4) integration ----
   The mode controller owns mode state and fight setup; versus-mode fights
   route through the CHOOSE YOUR ARENA screen. Arcade/story/training keep
   their mode-dictated flow (stage comes from the mode, not the player). */
let pendingFight = null;
function startFightViaStage(p1, p2, opts = {}) {
  if (opts.mode !== 'versus') { startFight(p1, p2, opts); return; }
  pendingFight = { p1, p2, opts };
  buildStageSelect();
  show('stage');
  const hint = document.getElementById('stage-hint');
  const s = getStage(selectedStage);
  if (hint && s) hint.textContent = `${s.name} — ${s.description}`;
  const btn = document.getElementById('confirm-stage');
  if (btn) btn.disabled = false;
}
const modes = new ModeController({
  game, ui, show, startFight: startFightViaStage,
  roster: ROSTER, getChar: getCharacterWithCustom, audio,
});
window.__modes = modes;

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

/* Build character select cards — Tekken-style tiered grid */
function buildSelect() {
  const grid = document.getElementById('char-grid');
  grid.innerHTML = '';

  const tiers = [
    { label: 'THE NINE SOULS', fighters: ROSTER.slice(0, 9) },
    { label: 'MAIN ROSTER', fighters: ROSTER.slice(9, 16) },
    { label: 'BONUS ROSTER', fighters: ROSTER.slice(16) },
  ];

  // Custom fighter from the CAW suite (if one is saved)
  const customRaw = getCustomFighter();
  if (customRaw) {
    const custom = customFighterToRoster(customRaw);
    if (custom) {
      tiers.push({ label: 'CUSTOM', fighters: [custom] });
    }
  }

  tiers.forEach(({ label, fighters }) => {
    const tierHeader = document.createElement('div');
    tierHeader.className = 'tier-header';
    tierHeader.textContent = label;
    grid.appendChild(tierHeader);

    fighters.forEach((c) => {
      const card = document.createElement('div');
      card.className = 'char-card';
      card.dataset.id = c.id;
      const surgeName = c.surge ? c.surge.name : 'SOUL SURGE';
      // REAL portrait render from the 3D fighter model (game/assets/portraits/).
      // Tekken 2:3 center-crop convention (SELECTOR_CAROUSEL.md).
      card.innerHTML =
        `<div class="portrait"><img src="assets/portraits/${c.id}.png" alt="${c.name}" loading="lazy"></div>
         <div class="cname">${c.name}</div>
         <div class="cstyle">${c.style}</div>`;
      card.addEventListener('click', () => selectCard(card, c));
      grid.appendChild(card);
    });
  });
}
buildSelect();

/* Card selection (shared by mouse + keyboard) */
let focusedCardIdx = 0;
function allCards() { return [...document.querySelectorAll('.char-card')]; }
function selectCard(card, c) {
  audio.uiClick();
  document.querySelectorAll('.char-card').forEach(x => x.classList.remove('selected'));
  card.classList.add('selected');
  selectedChar = c.id;
  // Prefetch this fighter's 3D model while the user decides — Tekken 3
  // loads the character record when highlighted, not at boot.
  assets.prefetch(c.model || 'pantera');
  const surgeName = c.surge ? c.surge.name : 'SOUL SURGE';
  document.getElementById('select-hint').textContent = `${c.name} — ${c.style} · ${surgeName}`;
  document.getElementById('confirm-fighter').disabled = false;
}
function focusCard(i) {
  const cards = allCards();
  if (!cards.length) return;
  focusedCardIdx = (i + cards.length) % cards.length;
  cards.forEach(x => x.classList.remove('kb-focus'));
  const el = cards[focusedCardIdx];
  el.classList.add('kb-focus');
  el.scrollIntoView({ block: 'nearest' });
}
/* Keyboard navigation on the select screen */
document.addEventListener('keydown', (e) => {
  const sel = document.getElementById('screen-select');
  if (!sel || !sel.classList.contains('active')) return;
  const cards = allCards();
  if (!cards.length) return;
  // match the responsive CSS grid columns (2 phone portrait, 3 tablet, 4 desktop/landscape)
  const grid = document.getElementById('char-grid');
  const cols = grid ? getComputedStyle(grid).gridTemplateColumns.split(' ').length : 2;
  if (e.key === 'ArrowRight') { focusCard(focusedCardIdx + 1); e.preventDefault(); }
  else if (e.key === 'ArrowLeft') { focusCard(focusedCardIdx - 1); e.preventDefault(); }
  else if (e.key === 'ArrowDown') { focusCard(focusedCardIdx + cols); e.preventDefault(); }
  else if (e.key === 'ArrowUp') { focusCard(focusedCardIdx - cols); e.preventDefault(); }
  else if (e.key === 'Enter' || e.key === ' ') {
    const card = cards[focusedCardIdx];
    const c = ROSTER.find(x => x.id === card.dataset.id) || getCustomRosterEntry(card.dataset.id);
    if (c) {
      if (selectedChar === c.id) { confirmSelection(); } // Enter again = confirm
      else selectCard(card, c);
    }
    e.preventDefault();
  }
});
/* ---------------- Stage select (Lane 4) ----------------
   After the fighter is confirmed, pick the arena: 8 canon Eastern
   Mind lands + 15 Tekken 3 retro arenas (real teardown geometry). */
let selectedStage = 'shrine';

function buildStageSelect() {
  const grid = document.getElementById('stage-grid');
  if (!grid) return;
  grid.innerHTML = '';
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
      card.innerHTML =
        `<div class="swatch" style="background:linear-gradient(135deg, ${s.swatch[0]}, ${s.swatch[1]})"></div>
         <div class="sname">${s.name}</div>
         <div class="suniverse">${s.universe}</div>`;
      card.addEventListener('click', () => selectStageCard(card, s));
      grid.appendChild(card);
    }
  }
}
function selectStageCard(card, s) {
  audio.uiClick();
  document.querySelectorAll('.stage-card').forEach(x => x.classList.remove('selected'));
  card.classList.add('selected');
  selectedStage = s.id;
  const hint = document.getElementById('stage-hint');
  if (hint) hint.textContent = `${s.name} — ${s.description}`;
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
  el.scrollIntoView({ block: 'nearest' });
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
      if (selectedStage === s.id) { startFight(); }
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
      const card = document.querySelector(`.char-card[data-id="${pick.id}"]`);
      if (card) {
        selectCard(card, pick);
        const idx = Array.from(allCards()).indexOf(card);
        if (idx >= 0) focusCard(idx);
      }
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
  if (!id) return;
  const card = document.querySelector(`.char-card[data-id="${id}"]`);
  const c = ROSTER.find(x => x.id === id);
  if (card && c) selectCard(card, c);
})();

/* Random opponent different from the player */
function randomEnemy(excludeId) {
  const pool = ROSTER.filter(c => c.id !== excludeId);
  return pool[Math.floor(Math.random() * pool.length)];
}

/* ---------------- Menu button wiring ---------------- */
function unlockAudio() {
  audio.unlock();
  document.getElementById('tap-to-start').classList.remove('show');
}

document.body.addEventListener('pointerdown', unlockAudio, { once: true });
window.addEventListener('load', () => {
  setTimeout(() => document.getElementById('tap-to-start').classList.add('show'), 600);
});

document.querySelectorAll('[data-action]').forEach((el) => {
  el.addEventListener('click', () => {
    unlockAudio();
    audio.uiClick();
    const a = el.dataset.action;
    if (a === 'play' || a === 'mode-arcade') {
      modes.startMode('arcade');
    }
    else if (a === 'mode-versus') {
      modes.startMode('versus');
    }
    else if (a === 'mode-story') {
      modes.startMode('story');
    }
    else if (a === 'mode-training') {
      modes.startMode('training');
    }
    else if (a === 'mode-survival') {
      modes.startMode('survival');
    }
    else if (a === 'mode-timeattack') {
      modes.startMode('timeattack');
    }
    else if (a === 'mode-team') {
      modes.startMode('team');
    }
    else if (a === 'mode-qombat') {
      modes.startMode('qombat');
    }
    else if (a === 'mode-surge') {
      modes.startMode('surge');
    }
    else if (a === 'mode-trader') {
      modes.startMode('trader');
    }
    else if (a === 'mode-create') {
      // Character creation — launches the Create Fighter CAW suite.
      // Returns to game menu via the BACK TO GAME button in the creator.
      audio.uiClick();
      window.location.href = '../customization/create-fighter/index.html';
    }
    else if (a === 'howto') { show('howto'); }
    else if (a === 'back-menu') {
      // CLEAN-INIT: leaving fight → full state reset. No leaked fighters,
      // timers, or listeners carry into the menu.
      game.leaveFight();
      modes.clearState();
      show('menu');
      audio.stopMusic();
    }
    else if (a === 'back-select') {
      show('select');
    }
    else if (a === 'rematch') {
      if (modes.mode) modes.rematch();
      else startFight();
    }
  });
});

/* Confirm routing: the mode controller owns the select flow
   (versus needs a P1→P2 two-step; other modes start on confirm).
   Lane 4 integration: versus-mode fights route through the stage-select
   screen via startFightViaStage (wired as the ModeController's startFight
   dep below); arcade/story/training use their mode-dictated flow. */
function confirmSelection() {
  if (!selectedChar) return;
  audio.uiClick();
  modes.onConfirm(selectedChar);
  selectedChar = null; // always clear — versus P2 must click a card to pick
}

document.getElementById('confirm-fighter').addEventListener('click', confirmSelection);

/* Lane 4: stage-select screen handlers (CHOOSE YOUR ARENA). */
document.getElementById('confirm-stage').addEventListener('click', () => {
  if (!selectedStage || !pendingFight) return;
  audio.uiClick();
  const { p1, p2, opts } = pendingFight;
  pendingFight = null;
  startFight(p1, p2, { ...opts, stage: selectedStage });
});

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
  modes.clearState();
  show('menu');
  audio.stopMusic();
});

async function startFight(playerId, enemyId, opts = {}) {
  unlockAudio();
  if (typeof playerId === 'string') selectedChar = playerId;
  // Lane 4: stage-select may pass an explicit stage via opts.
  if (opts.stage && getStage(opts.stage)) selectedStage = getStage(opts.stage).id;
  // modes lane: opts may carry full char-entry overrides (force-buffed
  // player, scaled-AI foe, the Assembled Soul boss, training dummy).
  const player = opts.playerChar || getCharacterWithCustom(selectedChar || ROSTER[0].id);
  const enemy = opts.enemyChar ||
    (typeof enemyId === 'string' && enemyId !== player.id ? getCharacterWithCustom(enemyId) : randomEnemy(player.id));
  // On-demand: load only the 2 fighters for this fight (Tekken 3 pattern).
  // Models may already be prefetched from select-screen highlight.
  const need = [...new Set([player.model || 'pantera', enemy.model || 'pantera'])];
  const hint = document.getElementById('select-hint');
  const confirmBtn = document.getElementById('confirm-fighter');
  try {
    if (hint) hint.textContent = 'Entering the arena…';
    if (confirmBtn) confirmBtn.disabled = true;
    await assets.loadModels(need, (p, loaded, total) => {
      if (!hint) return;
      if (loaded && total) {
        const mbL = (loaded / 1048576).toFixed(1);
        const mbT = (total / 1048576).toFixed(1);
        hint.textContent = `Entering the arena… ${mbL}/${mbT} MB`;
      } else {
        hint.textContent = `Entering the arena… ${Math.round(p * 100)}%`;
      }
    });
    // Load REAL T3 animation clips (Grok's decoded T3 King motion).
    // Non-blocking for fight start; fighters use procedural fallback until ready.
    if (hint) hint.textContent = 'Loading real fight motion…';
    try {
      await loadT3Clips(THREE);
    } catch (e) {
      console.warn('[WH] T3 clips failed, using procedural fallback:', e.message || e);
    }
  } catch (err) {
    console.error('[WH] fight load failed:', err);
    if (hint) hint.textContent = 'Failed to load fighters. Check connection and try again.';
    if (confirmBtn) confirmBtn.disabled = false;
    return;
  }
  if (confirmBtn) confirmBtn.disabled = false;
  show('hud');
  game.paused = false;
  audio.startMusic();
  await game.startMatch(player, enemy, selectedStage, opts);
  // Control hints: show for 6s at fight start, H toggles
  const hints = document.getElementById('control-hints');
  if (hints) {
    hints.classList.remove('fade');
    clearTimeout(hints._t);
    hints._t = setTimeout(() => hints.classList.add('fade'), 6000);
  }
}
// H toggles control hints
document.addEventListener('keydown', (e) => {
  if (e.code === 'KeyH') {
    const hints = document.getElementById('control-hints');
    if (hints) hints.classList.toggle('fade');
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

// New Western Heart menu/UI (game/ui-wh/) behind a toggle; classic menus stay as fallback.
if (whUiEnabled()) mountWhUi({ game, ui, show, startFight, ROSTER });
