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

/* Preload the rigged 3D fighter model before play is allowed. */
(function preload() {
  const fill = document.getElementById('loading-fill');
  const text = document.getElementById('loading-text');
  const overlay = document.getElementById('loading');
  assets.load((p) => { fill.style.width = Math.round(p * 100) + '%'; })
    .then(() => {
      fill.style.width = '100%';
      assetsReady = true;
      setTimeout(() => overlay.classList.add('hidden'), 250);
    })
    .catch((err) => {
      console.error(err);
      text.textContent = 'Failed to load fighters. Please refresh.';
    });
})();

/* Build character select cards */
function buildSelect() {
  const grid = document.getElementById('char-grid');
  grid.innerHTML = '';
  ROSTER.forEach((c) => {
    const card = document.createElement('div');
    card.className = 'char-card';
    card.dataset.id = c.id;
    const suit = '#' + c.colors.suit.toString(16).padStart(6, '0');
    const trim = '#' + c.colors.trim.toString(16).padStart(6, '0');
    card.innerHTML =
      `<div class="char-avatar" style="background:radial-gradient(circle at 35% 30%, ${suit}, ${trim} 70%, #0b0b14)"></div>
       <div class="cname">${c.name}</div>
       <div class="cstyle">${c.style}</div>
       <div class="csoul">${c.soul}</div>`;
    card.addEventListener('click', () => {
      audio.uiClick();
      document.querySelectorAll('.char-card').forEach(x => x.classList.remove('selected'));
      card.classList.add('selected');
      selectedChar = c.id;
      document.getElementById('select-hint').textContent = `${c.name} — ${c.style} · Soul Surge: ${c.surge.name}`;
      document.getElementById('confirm-fighter').disabled = false;
    });
    grid.appendChild(card);
  });
}
buildSelect();

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
    if (a === 'play') { show('select'); }
    else if (a === 'howto') { show('howto'); }
    else if (a === 'back-menu') { show('menu'); audio.stopMusic(); game.running = false; game.paused = true; }
    else if (a === 'rematch') { startFight(); }
  });
});

document.getElementById('confirm-fighter').addEventListener('click', () => {
  if (!selectedChar) return;
  audio.uiClick();
  startFight();
});

function startFight() {
  if (!assetsReady) return;
  unlockAudio();
  const player = getCharacter(selectedChar || ROSTER[0].id);
  const enemy = randomEnemy(player.id);
  show('hud');
  game.paused = false;
  audio.startMusic();
  game.startMatch(player, enemy);
}

document.addEventListener('visibilitychange', () => {
  if (document.hidden) { game.paused = true; }
  else if (game.running) { game.paused = false; }
});

// expose for debugging / verification
window.__game = game;
window.__ui = ui;
