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
import { whUiEnabled, mountWhUi } from './ui-wh-bridge.js';

// Load REAL Tekken 3 moveset data (not hand-written frame data)
loadRealMovesets();

const screens = {
  menu:   document.getElementById('screen-menu'),
  howto:  document.getElementById('screen-howto'),
  select: document.getElementById('screen-select'),
  result: document.getElementById('screen-result'),
  hud:    document.getElementById('hud'),
};
function show(name) {
  Object.values(screens).forEach(s => s.classList.remove('active'));
  if (screens[name]) screens[name].classList.add('active');
  // Tekken 99s select timer: runs only on the select screen, and only once the
  // ~30MB assets are loaded — slow phones don't lose selection time to loading.
  if (name === 'select') maybeStartSelectTimer();
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
let gameMode = 'arcade'; // arcade | versus | story — versus: no reincarnation; story: death = reincarnation

/* TEKKEN 3 LESSON: don't load fighters at boot. Menu + select use PNG
   portraits — 3D models load on demand at fight start (see assets.js).
   Boot is instant; the "loading" overlay is skipped entirely. */
(function bootClean() {
  const overlay = document.getElementById('loading');
  assetsReady = true; // menu needs no 3D — enable immediately
  if (overlay) overlay.classList.add('hidden');
})();

/* Build character select cards — Tekken-style tiered grid */
function buildSelect() {
  const grid = document.getElementById('char-grid');
  grid.innerHTML = '';

  const tiers = [
    { label: 'THE NINE SOULS', fighters: ROSTER.slice(0, 9) },
    { label: 'MAIN ROSTER', fighters: ROSTER.slice(9, 16) },
    { label: 'BONUS ROSTER', fighters: ROSTER.slice(16) },
  ];

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
    const c = ROSTER.find(x => x.id === card.dataset.id);
    if (c) {
      if (selectedChar === c.id) { startFight(); } // Enter again = confirm
      else selectCard(card, c);
    }
    e.preventDefault();
  }
});
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
    if (a === 'play' || a === 'mode-arcade' || a === 'mode-versus') {
      gameMode = a === 'mode-versus' ? 'versus' : 'arcade';
      show('select');
    }
    else if (a === 'mode-story') {
      gameMode = 'story';
      show('select');
      // Story mode: pick your soul, death = reincarnation (per owner 2026-10-13)
      document.getElementById('select-hint').textContent = 'STORY: Choose your soul. Death is not the end — it is reincarnation.';
    }
    else if (a === 'mode-create') {
      // Character creation — wired to western-heart/customization/ when built
      document.getElementById('select-hint').textContent = 'CREATE FIGHTER coming soon — wired to the CAW suite.';
      show('select');
    }
    else if (a === 'howto') { show('howto'); }
    else if (a === 'back-menu') {
      // CLEAN-INIT: leaving fight → full state reset. No leaked fighters,
      // timers, or listeners carry into the menu.
      game.leaveFight();
      show('menu');
      audio.stopMusic();
    }
    else if (a === 'rematch') { startFight(); }
  });
});

document.getElementById('confirm-fighter').addEventListener('click', () => {
  if (!selectedChar) return;
  audio.uiClick();
  startFight();
});

async function startFight(playerId, enemyId) {
  unlockAudio();
  if (typeof playerId === 'string') selectedChar = playerId;
  const player = getCharacter(selectedChar || ROSTER[0].id);
  const enemy = typeof enemyId === 'string' && enemyId !== player.id ? getCharacter(enemyId) : randomEnemy(player.id);
  // On-demand: load only the 2 fighters for this fight (Tekken 3 pattern).
  // Models may already be prefetched from select-screen highlight.
  const need = [...new Set([player.model || 'pantera', enemy.model || 'pantera'])];
  const hint = document.getElementById('select-hint');
  const confirmBtn = document.getElementById('confirm-fighter');
  try {
    if (hint) hint.textContent = 'Entering the arena…';
    if (confirmBtn) confirmBtn.disabled = true;
    await assets.loadModels(need, (p) => {
      if (hint) hint.textContent = `Entering the arena… ${Math.round(p * 100)}%`;
    });
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
  game.startMatch(player, enemy);
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

// New Western Heart menu/UI (game/ui-wh/) behind a toggle; classic menus stay as fallback.
if (whUiEnabled()) mountWhUi({ game, ui, show, startFight, ROSTER });
