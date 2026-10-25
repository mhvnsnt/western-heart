/* ============================================================
   WESTERN HEART — Shrine体系 (Shrine + 体系 "system")
   The shrine terminal of the Octagonal Shrine Par-fang.

   IN-UNIVERSE (canon): a sacred computer-system kept in the
   shrine's room for arriving, where arriving souls are read
   before they are weighed. It speaks in sixteen colors and
   with one voice at a time, draws three-word oracle readings
   from the nine soul kanji, the trial inscription and the
   five lands, and keeps festival pastimes for the souls.

   TECHNICAL PROVENANCE (this file only, never in canon
   writing or in-game text): adapted from TempleOS, a public
   domain operating system by Terry A. Davis (last release
   5.03, 2017; repo github.com/cia-foundation/TempleOS).
   What WH takes from it: the 640x480 16-color VGA aesthetic,
   the single-voice audio idea, the HolyC-style command line,
   the Oracle concept (pseudorandom readings), the sprite
   editor concept, the music-toy concept, and the bundled
   games list — Black Diamond (downhill dodge) becomes the
   slope-descent mini-game. No HolyC source is vendored or
   executed here: this is a browser adaptation, not a port.
   The in-game name is Shrine体系, never the source name.

   This module is importable by Node (game unit tests) AND
   mountable in the browser. No top-level document/window
   access: all DOM work lives inside mountShrineOS().
   ============================================================ */

// ---- Identity ------------------------------------------------
export const SHRINE_OS = {
  name: 'Shrine体系',
  shortName: 'Shrine',
  kanji: '体系',
  kanjiReading: 'taikei',
  kanjiMeaning: 'system',
  stage: 'octagonal-shrine',
  stageName: 'OCTAGONAL SHRINE PAR-FANG',
  sideGamesAnchor: 'shrine-os',
};

// ---- The sixteen colors --------------------------------------
// Standard 16-color VGA palette, the shrine machine's whole
// world. Index order matches the classic VGA text-mode order.
export const VGA16 = [
  { i: 0, name: 'black', hex: '#000000' },
  { i: 1, name: 'blue', hex: '#0000AA' },
  { i: 2, name: 'green', hex: '#00AA00' },
  { i: 3, name: 'cyan', hex: '#00AAAA' },
  { i: 4, name: 'red', hex: '#AA0000' },
  { i: 5, name: 'magenta', hex: '#AA00AA' },
  { i: 6, name: 'brown', hex: '#AA5500' },
  { i: 7, name: 'light gray', hex: '#AAAAAA' },
  { i: 8, name: 'dark gray', hex: '#555555' },
  { i: 9, name: 'light blue', hex: '#5555FF' },
  { i: 10, name: 'light green', hex: '#55FF55' },
  { i: 11, name: 'light cyan', hex: '#55FFFF' },
  { i: 12, name: 'light red', hex: '#FF5555' },
  { i: 13, name: 'light magenta', hex: '#FF55FF' },
  { i: 14, name: 'yellow', hex: '#FFFF55' },
  { i: 15, name: 'white', hex: '#FFFFFF' },
];

// ---- Oracle words (canon only) -------------------------------
// Nine soul kanji + trial inscription + five lands + elements.
// No outside scripture, no invented words: every word below
// already exists in CANON.md.
export const ORACLE_WORDS = [
  '凛 RIN', '病 BYOU', '闘 TOU', '沙 SHA', '海 KAI',
  '刃 JIN', '烈 RETSU', '禅 ZEN', '行 GYOU',
  'FIGHT', 'DIE', 'RETURN', 'CLAIM', 'FORGE', 'BECOME WHOLE',
  'MING-KEN', 'SHI-CHIENG', 'PAR-FANG', 'YUI-WANG', 'MON-CHIEN',
  'WOOD', 'FIRE', 'EARTH', 'METAL', 'WATER', 'PURIFIER',
];

// Draw three distinct oracle words. rand defaults to
// Math.random; tests inject a deterministic sequence.
export function oracleDraw(rand) {
  const r = typeof rand === 'function' ? rand : Math.random;
  const pool = ORACLE_WORDS.slice();
  const out = [];
  for (let k = 0; k < 3 && pool.length > 0; k++) {
    const idx = Math.floor(r() * pool.length);
    out.push(pool.splice(idx, 1)[0]);
  }
  return out;
}

// ---- Command line --------------------------------------------
export const COMMANDS = [
  { cmd: 'HELP', desc: 'list commands' },
  { cmd: 'ORACLE', desc: 'the shrine reads three words' },
  { cmd: 'SPRITE', desc: 'draw in sixteen colors' },
  { cmd: 'MUSIC', desc: 'single-voice shrine hymns' },
  { cmd: 'GAME', desc: 'descend the mountain (dodge game)' },
  { cmd: 'SHARDS', desc: 'your Soul Shards balance' },
  { cmd: 'CLEAR', desc: 'clear the terminal' },
  { cmd: 'EXIT', desc: 'the terminal sleeps' },
];

// Parse one typed line. Case-insensitive, extra spaces ignored.
// Returns { raw, command, args, known, empty }.
export function parseCommand(input) {
  const raw = typeof input === 'string' ? input : '';
  const parts = raw.trim().toUpperCase().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return { raw, command: '', args: [], known: false, empty: true };
  const command = parts[0];
  const known = COMMANDS.some((c) => c.cmd === command);
  return { raw, command, args: parts.slice(1), known, empty: false };
}

// ---- Sprite board (16-color editor toy) ----------------------
// A grid of color indices 0-15. serialize() writes one hex
// digit per cell (0-9, A-F), so a 16x16 board is 256 chars.
export function createSpriteGrid(cols, rows) {
  const W = cols || 16;
  const H = rows || 16;
  const cells = new Array(W * H).fill(0);
  const at = (x, y) => y * W + x;
  return {
    cols: W,
    rows: H,
    cells,
    paint(x, y, color) {
      if (x < 0 || y < 0 || x >= W || y >= H) return false;
      if (color < 0 || color > 15) return false;
      cells[at(x, y)] = color;
      return true;
    },
    get(x, y) {
      if (x < 0 || y < 0 || x >= W || y >= H) return -1;
      return cells[at(x, y)];
    },
    clear() { cells.fill(0); },
    serialize() {
      return cells.map((c) => c.toString(16).toUpperCase()).join('');
    },
    deserialize(s) {
      if (typeof s !== 'string' || s.length !== W * H) return false;
      for (let k = 0; k < s.length; k++) {
        const v = parseInt(s[k], 16);
        if (Number.isNaN(v)) return false;
        cells[k] = v;
      }
      return true;
    },
  };
}

// ---- Single-voice hymns --------------------------------------
// One note at a time, never chords: the shrine speaks with
// one voice. Each pattern is a flat list of { f: frequency,
// b: beats }. Frequencies are equal-tempered Hz.
export const MUSIC_PATTERNS = {
  arrival: [
    { f: 220.00, b: 2 }, { f: 261.63, b: 2 }, { f: 329.63, b: 2 },
    { f: 392.00, b: 3 }, { f: 329.63, b: 2 }, { f: 261.63, b: 3 },
  ],
  trial: [
    { f: 220.00, b: 1 }, { f: 220.00, b: 1 }, { f: 261.63, b: 1 },
    { f: 220.00, b: 1 }, { f: 293.66, b: 1 }, { f: 261.63, b: 1 },
    { f: 220.00, b: 2 }, { f: 196.00, b: 2 },
  ],
  purified: [
    { f: 261.63, b: 1 }, { f: 329.63, b: 1 }, { f: 392.00, b: 1 },
    { f: 523.25, b: 2 }, { f: 392.00, b: 1 }, { f: 523.25, b: 1 },
    { f: 659.25, b: 3 },
  ],
};

// ---- Slope descent (Black Diamond adaptation) ----------------
// Descend the Central Mountain: the stairs count the climber
// back, and the mountain puts rocks and trees in the way.
// Player sits on the bottom row; obstacles scroll down.
// step(move): move -1 (left), 0 (stay), +1 (right). Returns a
// snapshot { alive, score, distance, speed, playerLane,
// playerRow, obstacles }. Tests may push obstacles into
// state.obstacles directly: { lane, row, width }.
export function createSlopeGame(opts) {
  const o = opts || {};
  const rand = typeof o.rand === 'function' ? o.rand : Math.random;
  const LANES = 9;
  const ROWS = 12;
  const PLAYER_ROW = ROWS - 1;
  const state = {
    lanes: LANES,
    rows: ROWS,
    playerRow: PLAYER_ROW,
    playerLane: 4,
    distance: 0,
    score: 0,
    speed: 1,
    alive: true,
    crashed: false,
    obstacles: [],
  };
  function step(move) {
    if (!state.alive) return snapshot();
    if (move === -1 && state.playerLane > 0) state.playerLane -= 1;
    if (move === 1 && state.playerLane < LANES - 1) state.playerLane += 1;
    state.distance += state.speed;
    state.score = state.distance;
    state.speed = Math.min(3, 1 + state.distance / 500);
    // Obstacles advance toward the player.
    state.obstacles.forEach((ob) => { ob.row += 1; });
    // Spawn a new obstacle at the top.
    if (rand() < 0.5) {
      const lane = Math.floor(rand() * LANES);
      const width = rand() < 0.3 ? 2 : 1;
      state.obstacles.push({ lane, row: 0, width });
    }
    state.obstacles = state.obstacles.filter((ob) => ob.row <= PLAYER_ROW);
    // Collision: obstacle on the player row covering the lane.
    const hit = state.obstacles.some((ob) =>
      ob.row === PLAYER_ROW &&
      state.playerLane >= ob.lane &&
      state.playerLane < ob.lane + ob.width);
    if (hit) { state.alive = false; state.crashed = true; }
    return snapshot();
  }
  function snapshot() {
    return {
      alive: state.alive,
      crashed: state.crashed,
      score: state.score,
      distance: state.distance,
      speed: state.speed,
      playerLane: state.playerLane,
      playerRow: state.playerRow,
      obstacles: state.obstacles.map((ob) => ({ lane: ob.lane, row: ob.row, width: ob.width })),
    };
  }
  function reset() {
    state.playerLane = 4;
    state.distance = 0;
    state.score = 0;
    state.speed = 1;
    state.alive = true;
    state.crashed = false;
    state.obstacles = [];
  }
  return { state, step, snapshot, reset };
}

// ---- Browser mount -------------------------------------------
// Builds the terminal inside el. Safe to call once per element;
// a second call on the same element is a no-op.
export function mountShrineOS(el) {
  if (!el || typeof document === 'undefined') return null;
  if (el.getAttribute('data-shrine-mounted') === '1') return null;
  el.setAttribute('data-shrine-mounted', '1');

  const I = (typeof window !== 'undefined' && window.WHIdentity) ? window.WHIdentity : null;
  const grid = createSpriteGrid(16, 16);
  let selColor = 14; // yellow
  let game = null;
  let gameTimer = null;
  let gameMove = 0;
  let audioCtx = null;
  let musicTimers = [];
  let musicOn = false;

  const root = document.createElement('div');
  root.style.cssText = 'background:#000000;color:#AAAAAA;font-family:monospace;' +
    'border:2px solid #00AAAA;padding:10px;max-width:640px;margin:0 auto;text-align:left;';
  const out = document.createElement('div');
  out.style.cssText = 'min-height:220px;max-height:340px;overflow-y:auto;' +
    'white-space:pre-wrap;word-break:break-word;font-size:14px;line-height:1.45;';
  const inputRow = document.createElement('div');
  inputRow.style.cssText = 'display:flex;gap:8px;margin-top:10px;';
  const input = document.createElement('input');
  input.type = 'text';
  input.placeholder = 'Type HELP, then ENTER';
  input.autocapitalize = 'characters';
  input.style.cssText = 'flex:1;min-height:44px;background:#000000;color:#FFFF55;' +
    'border:1px solid #00AAAA;font-family:monospace;font-size:16px;padding:0 10px;';
  const runBtn = document.createElement('button');
  runBtn.textContent = 'RUN';
  runBtn.style.cssText = 'min-height:44px;min-width:64px;background:#00AAAA;color:#000000;' +
    'border:none;font-family:monospace;font-weight:bold;font-size:16px;';
  inputRow.appendChild(input);
  inputRow.appendChild(runBtn);

  const quickRow = document.createElement('div');
  quickRow.style.cssText = 'display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;';
  const quickBtns = {};
  COMMANDS.forEach((c) => {
    const b = document.createElement('button');
    b.textContent = c.cmd;
    b.style.cssText = 'min-height:44px;padding:0 14px;background:#111111;color:#55FFFF;' +
      'border:1px solid #555555;font-family:monospace;font-size:14px;';
    b.addEventListener('click', () => runCommand(c.cmd));
    quickRow.appendChild(b);
    quickBtns[c.cmd] = b;
  });

  // Panels (hidden until their command runs).
  const spritePanel = document.createElement('div');
  spritePanel.style.cssText = 'display:none;margin-top:12px;';
  const spriteCanvas = document.createElement('canvas');
  spriteCanvas.width = 256;
  spriteCanvas.height = 256;
  spriteCanvas.style.cssText = 'width:100%;max-width:320px;height:auto;' +
    'image-rendering:pixelated;border:1px solid #555555;background:#000000;touch-action:none;';
  const paletteRow = document.createElement('div');
  paletteRow.style.cssText = 'display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;';
  const paletteBtns = [];
  VGA16.forEach((c) => {
    const b = document.createElement('button');
    b.title = c.name;
    b.style.cssText = 'width:44px;height:44px;background:' + c.hex +
      ';border:2px solid ' + (c.i === selColor ? '#FFFFFF' : '#555555') + ';';
    b.addEventListener('click', () => {
      selColor = c.i;
      paletteBtns.forEach((pb, k) => { pb.style.borderColor = (k === selColor ? '#FFFFFF' : '#555555'); });
    });
    paletteRow.appendChild(b);
    paletteBtns.push(b);
  });
  const spriteBtnRow = document.createElement('div');
  spriteBtnRow.style.cssText = 'display:flex;gap:8px;margin-top:8px;';
  const spriteClear = document.createElement('button');
  spriteClear.textContent = 'CLEAR BOARD';
  const spriteSave = document.createElement('button');
  spriteSave.textContent = 'SAVE (PRINT CODE)';
  [spriteClear, spriteSave].forEach((b) => {
    b.style.cssText = 'min-height:44px;padding:0 14px;background:#111111;color:#55FFFF;' +
      'border:1px solid #555555;font-family:monospace;font-size:14px;';
  });
  spriteBtnRow.appendChild(spriteClear);
  spriteBtnRow.appendChild(spriteSave);
  spritePanel.appendChild(spriteCanvas);
  spritePanel.appendChild(paletteRow);
  spritePanel.appendChild(spriteBtnRow);

  const musicPanel = document.createElement('div');
  musicPanel.style.cssText = 'display:none;margin-top:12px;';
  const musicRow = document.createElement('div');
  musicRow.style.cssText = 'display:flex;flex-wrap:wrap;gap:8px;';
  const musicBtns = {};
  Object.keys(MUSIC_PATTERNS).forEach((key) => {
    const b = document.createElement('button');
    b.textContent = key.toUpperCase();
    b.style.cssText = 'min-height:44px;padding:0 14px;background:#111111;color:#55FFFF;' +
      'border:1px solid #555555;font-family:monospace;font-size:14px;';
    b.addEventListener('click', () => playPattern(key));
    musicRow.appendChild(b);
    musicBtns[key] = b;
  });
  const musicStop = document.createElement('button');
  musicStop.textContent = 'STOP';
  musicStop.style.cssText = 'min-height:44px;padding:0 14px;background:#111111;color:#FF5555;' +
    'border:1px solid #555555;font-family:monospace;font-size:14px;';
  musicStop.addEventListener('click', stopMusic);
  musicRow.appendChild(musicStop);
  musicPanel.appendChild(musicRow);

  const gamePanel = document.createElement('div');
  gamePanel.style.cssText = 'display:none;margin-top:12px;text-align:center;';
  const gameCanvas = document.createElement('canvas');
  gameCanvas.width = 270;
  gameCanvas.height = 360;
  gameCanvas.style.cssText = 'width:100%;max-width:320px;height:auto;' +
    'image-rendering:pixelated;border:1px solid #555555;background:#000000;';
  const gameScore = document.createElement('div');
  gameScore.style.cssText = 'color:#FFFF55;font-size:16px;margin:8px 0;';
  gameScore.textContent = 'score 0';
  const gameBtnRow = document.createElement('div');
  gameBtnRow.style.cssText = 'display:flex;gap:8px;justify-content:center;';
  const btnLeft = document.createElement('button');
  btnLeft.textContent = '◀ LEFT';
  const btnStart = document.createElement('button');
  btnStart.textContent = 'START DESCENT';
  const btnRight = document.createElement('button');
  btnRight.textContent = 'RIGHT ▶';
  [btnLeft, btnStart, btnRight].forEach((b) => {
    b.style.cssText = 'min-height:44px;padding:0 14px;background:#111111;color:#55FFFF;' +
      'border:1px solid #555555;font-family:monospace;font-size:14px;';
  });
  gameBtnRow.appendChild(btnLeft);
  gameBtnRow.appendChild(btnStart);
  gameBtnRow.appendChild(btnRight);
  gamePanel.appendChild(gameCanvas);
  gamePanel.appendChild(gameScore);
  gamePanel.appendChild(gameBtnRow);

  root.appendChild(out);
  root.appendChild(inputRow);
  root.appendChild(quickRow);
  root.appendChild(spritePanel);
  root.appendChild(musicPanel);
  root.appendChild(gamePanel);
  el.appendChild(root);

  function print(text) {
    const line = document.createElement('div');
    line.textContent = text;
    out.appendChild(line);
    out.scrollTop = out.scrollHeight;
  }
  function hidePanels() {
    spritePanel.style.display = 'none';
    musicPanel.style.display = 'none';
    gamePanel.style.display = 'none';
    stopGame();
  }
  function boot() {
    out.innerHTML = '';
    hidePanels();
    print('SHRINE体系 — OCTAGONAL SHRINE TERMINAL');
    print('Central Mountain. Earth. The Source.');
    print('The shrine machine sees in sixteen colors');
    print('and speaks with one voice at a time.');
    print('Type HELP, or tap a command below.');
  }
  function runCommand(rawCmd) {
    const parsed = parseCommand(rawCmd);
    if (parsed.empty) return;
    if (!parsed.known) {
      print('? ' + parsed.command + ' — unknown. Type HELP.');
      return;
    }
    const cmd = parsed.command;
    if (cmd === 'HELP') {
      print('— COMMANDS —');
      COMMANDS.forEach((c) => print('  ' + c.cmd + ' — ' + c.desc));
      return;
    }
    if (cmd === 'CLEAR') { out.innerHTML = ''; return; }
    if (cmd === 'EXIT') {
      hidePanels();
      print('The terminal sleeps. The shrine keeps the reading.');
      const reboot = document.createElement('button');
      reboot.textContent = 'BOOT SHRINE体系';
      reboot.style.cssText = 'min-height:44px;padding:0 14px;margin-top:10px;background:#00AAAA;' +
        'color:#000000;border:none;font-family:monospace;font-weight:bold;font-size:16px;';
      reboot.addEventListener('click', () => { reboot.remove(); boot(); });
      root.appendChild(reboot);
      return;
    }
    if (cmd === 'ORACLE') {
      const words = oracleDraw();
      print('— THE SHRINE READS —');
      print('  ' + words.join(' · '));
      print('A reading, not a command. Carry it down.');
      return;
    }
    if (cmd === 'SPRITE') {
      hidePanels();
      spritePanel.style.display = 'block';
      drawSprite();
      print('Sprite board open. Tap the board to paint.');
      return;
    }
    if (cmd === 'MUSIC') {
      hidePanels();
      musicPanel.style.display = 'block';
      print('Hymns open. One voice at a time.');
      return;
    }
    if (cmd === 'GAME') {
      hidePanels();
      gamePanel.style.display = 'block';
      print('The descent: dodge what the mountain puts in the way.');
      print('Tap LEFT / RIGHT, or use arrow keys. START DESCENT to begin.');
      return;
    }
    if (cmd === 'SHARDS') {
      if (I) {
        const p = I.get();
        print('Soul Shards: ' + p.shards + '.');
      } else {
        print('The shrine keeps no prices. Nothing here is bought or sold.');
      }
      return;
    }
  }

  // ---- Sprite board ----
  function drawSprite() {
    const ctx = spriteCanvas.getContext('2d');
    const cell = 16;
    for (let y = 0; y < 16; y++) {
      for (let x = 0; x < 16; x++) {
        ctx.fillStyle = VGA16[grid.get(x, y)].hex;
        ctx.fillRect(x * cell, y * cell, cell, cell);
      }
    }
  }
  spriteCanvas.addEventListener('pointerdown', (e) => {
    const r = spriteCanvas.getBoundingClientRect();
    const x = Math.floor((e.clientX - r.left) * (16 / r.width));
    const y = Math.floor((e.clientY - r.top) * (16 / r.height));
    if (grid.paint(x, y, selColor)) drawSprite();
  });
  spriteClear.addEventListener('click', () => { grid.clear(); drawSprite(); });
  spriteSave.addEventListener('click', () => {
    print('Sprite code: ' + grid.serialize());
    print('Sixteen colors, one board. The shrine remembers it.');
  });

  // ---- Single-voice music ----
  function stopMusic() {
    musicOn = false;
    musicTimers.forEach((t) => clearTimeout(t));
    musicTimers = [];
    if (audioCtx) { audioCtx.close().catch(() => {}); audioCtx = null; }
  }
  function playPattern(key) {
    stopMusic();
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) { print('No audio on this device. The hymn stays silent.'); return; }
    audioCtx = new AC();
    musicOn = true;
    const notes = MUSIC_PATTERNS[key];
    let t = 0;
    const BEAT = 0.42;
    notes.forEach((n) => {
      const at = t;
      musicTimers.push(setTimeout(() => {
        if (!musicOn || !audioCtx) return;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.value = n.f;
        gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + n.b * BEAT);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + n.b * BEAT);
      }, at * 1000));
      t += n.b * BEAT;
    });
    musicTimers.push(setTimeout(() => { if (musicOn) playPattern(key); }, t * 1000));
    print('Playing: ' + key + ' (one voice, on loop until STOP).');
  }

  // ---- Slope game ----
  function drawGame() {
    if (!game) return;
    const snap = game.snapshot();
    const ctx = gameCanvas.getContext('2d');
    const cw = gameCanvas.width;
    const ch = gameCanvas.height;
    const cellW = cw / 9;
    const cellH = ch / 12;
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, cw, ch);
    ctx.fillStyle = '#555555';
    for (let l = 0; l <= 9; l++) ctx.fillRect(l * cellW, 0, 1, ch);
    snap.obstacles.forEach((ob) => {
      ctx.fillStyle = '#AA0000';
      for (let w = 0; w < ob.width; w++) {
        ctx.fillRect(ob.lane * cellW + 2 + w * cellW, ob.row * cellH + 2, cellW - 4, cellH - 4);
      }
    });
    ctx.fillStyle = '#FFFF55';
    ctx.fillRect(snap.playerLane * cellW + 4, snap.playerRow * cellH + 4, cellW - 8, cellH - 8);
    gameScore.textContent = 'score ' + snap.score + (snap.alive ? '' : ' — THE MOUNTAIN STOPS YOU');
  }
  function stopGame() {
    if (gameTimer) { clearInterval(gameTimer); gameTimer = null; }
  }
  function tickGame() {
    if (!game) return;
    const snap = game.step(gameMove);
    gameMove = 0;
    drawGame();
    if (!snap.alive) {
      stopGame();
      print('Descent ended at ' + snap.score + ' steps.');
      if (I) {
        const pay = Math.floor(snap.score / 100);
        if (pay > 0) I.addShards(pay, 'shrine-slope');
        const p = I.get();
        p.stats.sideGames = (p.stats.sideGames || 0) + 1;
        I.save();
        print('The shrine pays ' + pay + ' Soul Shards.');
      }
    }
  }
  btnStart.addEventListener('click', () => {
    stopGame();
    game = createSlopeGame();
    drawGame();
    gameTimer = setInterval(tickGame, 150);
    print('Descending…');
  });
  btnLeft.addEventListener('click', () => { gameMove = -1; if (game && !gameTimer) tickGame(); });
  btnRight.addEventListener('click', () => { gameMove = 1; if (game && !gameTimer) tickGame(); });
  document.addEventListener('keydown', (e) => {
    if (!game || !gameTimer) return;
    if (e.target && e.target.tagName === 'INPUT') return;
    if (e.key === 'ArrowLeft') gameMove = -1;
    if (e.key === 'ArrowRight') gameMove = 1;
  });

  runBtn.addEventListener('click', () => {
    const v = input.value;
    input.value = '';
    print('> ' + v);
    runCommand(v);
    input.focus();
  });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const v = input.value;
      input.value = '';
      print('> ' + v);
      runCommand(v);
    }
  });

  boot();
  return { root, runCommand, print };
}

if (typeof window !== 'undefined') {
  window.WHShrineOS = {
    SHRINE_OS, VGA16, ORACLE_WORDS, oracleDraw, parseCommand,
    createSlopeGame, createSpriteGrid, MUSIC_PATTERNS, COMMANDS, mountShrineOS,
  };
}
