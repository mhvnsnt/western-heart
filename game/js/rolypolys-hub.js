// Roly-Polys World Hub — Banabana MK.1 travel + minigames for Western Heart.
//
// PURE CORE (no DOM): hub state machine, shooting / cooking / slot / bull-dodge
// scoring. Fully testable from node — see test/rolypolys-hub.test.mjs.
// DOM SHELL: mountRolyPolysHub(host) builds the hub UI inside one host element,
// following the mountShrineOS(host) pattern in ./shrine-os.js. Winnings pay out
// in Soul Shards through window.WHIdentity (addShards / spendShards / get),
// exactly like the Harvest and Chō-han prototypes on game/side-games.html.
//
// SOURCES (pulled whole): game/data/rolypolys-world.js — the verified disc
// catalog (7 areas, regions, scenes, ITEM system, endings, minigame shells,
// god-within anchors) from sato/rolypolys/WORLD-TOUR.md. WH characters only:
// RIN leads (disc's Pon), TOU hosts shooting (disc's Cho), KAI hosts cooking
// (disc's Mr. Okhotsk), the Trader hosts the slot (disc's Las Vegas Akiko).
// No complete working implementation of these games exists anywhere found
// (see checkpoint PULL-WORKING-COMPLETE assessment) — the playable shells
// below are WH-native builds from the verified disc structures, not clones.

import {
  ROLYPOLYS_WORLD,
  ROLYPOLYS_AREAS,
  ROLYPOLYS_ENDINGS,
  ROLYPOLYS_VIGNETTES,
} from '../data/rolypolys-world.js';

export const WORLD = ROLYPOLYS_WORLD;

// ---------------------------------------------------------------- seeded RNG
export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ------------------------------------------------------------------- catalog
export function areaById(world, areaId) {
  return (world.areas || []).find((a) => a.id === areaId) || null;
}

export function regionById(area, regionId) {
  if (!area) return null;
  return (area.regions || []).find((r) => r.id === regionId) || null;
}

export function listAreas(world) {
  return (world.areas || []).map((a) => a.id);
}

export function listRegions(world, areaId) {
  const area = areaById(world, areaId);
  return area ? area.regions.map((r) => r.id) : [];
}

export function listScenes(world, areaId, regionId) {
  const region = regionById(areaById(world, areaId), regionId);
  return region ? region.scenes.slice() : [];
}

export function totalScenes(world) {
  return (world.areas || []).reduce(
    (n, a) => n + a.regions.reduce((m, r) => m + r.scenes.length, 0),
    0,
  );
}

export function totalRegions(world) {
  return (world.areas || []).reduce((n, a) => n + a.regions.length, 0);
}

export function sceneExists(world, areaId, regionId, sceneId) {
  return listScenes(world, areaId, regionId).includes(sceneId);
}

export function endingForArea(world, areaId) {
  return (world.endings || {})[areaId] || null;
}

export function vignetteFor(world, letter) {
  const up = String(letter || '').toUpperCase();
  return (world.vignettes || []).find((v) => v.letter === up) || null;
}

// --------------------------------------------------------------- hub state
export function createHubState() {
  return {
    area: 'JAPAN', // home leg — the disc opens at RIN's house (JAPAN/PON/OPEN.DXR)
    region: null,
    scene: null,
    visited: [], // "AREA/REGION/SCENE" keys
    items: [], // one collectible per scene visited, named for the scene
    endings: [], // area ids whose ending cinematic is unlocked
    shardsEarned: 0,
  };
}

function visitKey(areaId, regionId, sceneId) {
  return areaId + '/' + regionId + '/' + sceneId;
}

export function sailTo(state, world, areaId) {
  if (!areaById(world, areaId)) return { ok: false, error: 'unknown area ' + areaId };
  state.area = areaId;
  state.region = null;
  state.scene = null;
  return { ok: true, area: areaId };
}

// Visit a scene: collects its ITEM (ITEM*.CXT system — one per region on disc,
// one collectible per scene in the WH slice). Visiting every scene in an area
// unlocks that area's ending cinematic exactly once.
export function visitScene(state, world, areaId, regionId, sceneId) {
  if (!sceneExists(world, areaId, regionId, sceneId)) {
    return { ok: false, error: 'unknown scene ' + areaId + '/' + regionId + '/' + sceneId };
  }
  const key = visitKey(areaId, regionId, sceneId);
  const firstVisit = !state.visited.includes(key);
  if (firstVisit) {
    state.visited.push(key);
    state.items.push(sceneId);
  }
  state.area = areaId;
  state.region = regionId;
  state.scene = sceneId;
  const progress = areaProgress(state, world, areaId);
  let ending = null;
  if (progress.visited === progress.total && !state.endings.includes(areaId)) {
    state.endings.push(areaId);
    ending = endingForArea(world, areaId);
  }
  return { ok: true, firstVisit, item: firstVisit ? sceneId : null, progress, ending };
}

export function areaProgress(state, world, areaId) {
  const area = areaById(world, areaId);
  if (!area) return { visited: 0, total: 0 };
  const total = area.regions.reduce((n, r) => n + r.scenes.length, 0);
  const prefix = areaId + '/';
  const visited = state.visited.filter((k) => k.startsWith(prefix)).length;
  return { visited, total };
}

// ------------------------------------------------------------ shooting gallery
// TOU's Shooting Gallery (disc: KOTOWAZA/SHOOTING.DXR, "Cho (Shooting)").
// 8 targets, 30 seconds, tap/click to shoot. Hit = 10 shards.
export const SHOOTING = { targets: 8, seconds: 30, shardsPerHit: 10, width: 640, height: 360 };

export function spawnTargets(rng, count, width, height) {
  const targets = [];
  for (let i = 0; i < count; i++) {
    targets.push({
      x: 40 + rng() * (width - 80),
      y: 40 + rng() * (height - 120),
      r: 16 + rng() * 10,
    });
  }
  return targets;
}

// Returns the hit target (removed from the array) or null.
export function shootingHit(targets, x, y) {
  for (let i = 0; i < targets.length; i++) {
    const t = targets[i];
    const dx = x - t.x, dy = y - t.y;
    if (dx * dx + dy * dy <= t.r * t.r) return targets.splice(i, 1)[0];
  }
  return null;
}

export function shootingShards(hits) {
  return Math.max(0, hits) * SHOOTING.shardsPerHit;
}

// --------------------------------------------------------------- cooking game
// KAI's Cooking School — Miso (disc: KOTOWAZA/MISO_KO.DXR).
// A marker sweeps a 0..100 meter; STOP it in the zone. 3 rounds.
export const COOKING = { rounds: 3, perfect: 5, good: 15, center: 50, shardsPerfect: 30, shardsGood: 10 };

export function cookingJudge(pos) {
  const d = Math.abs(pos - COOKING.center);
  if (d <= COOKING.perfect) return { grade: 'perfect', shards: COOKING.shardsPerfect };
  if (d <= COOKING.good) return { grade: 'good', shards: COOKING.shardsGood };
  return { grade: 'miss', shards: 0 };
}

export function createCooking() {
  return { round: 1, score: 0, done: false, last: null };
}

export function cookingRound(game, pos) {
  if (game.done) return { ok: false, error: 'cooking already done' };
  const judge = cookingJudge(pos);
  game.score += judge.shards;
  game.last = { round: game.round, pos, grade: judge.grade, shards: judge.shards };
  game.round += 1;
  if (game.round > COOKING.rounds) game.done = true;
  return { ok: true, judge, score: game.score, done: game.done };
}

// ---------------------------------------------------------------- slot machine
// The Trader's Slot (disc: Shockwave slot.dcr, OSD website 1997).
// Nine soul kanji + the Trader's mark. 3 of a kind pays 10x, 2 pays 2x.
export const SLOT_SYMBOLS = ['凛', '闘', '沙', '海', '刃', '烈', '禅', '行', '商'];
export const SLOT_PAYS = { three: 10, two: 2 };

export function spinSlot(rng) {
  const pick = () => SLOT_SYMBOLS[Math.floor(rng() * SLOT_SYMBOLS.length)];
  return [pick(), pick(), pick()];
}

export function slotPayout(symbols, bet) {
  const [a, b, c] = symbols;
  if (a === b && b === c) return { payout: bet * SLOT_PAYS.three, kind: 'three' };
  if (a === b || b === c || a === c) return { payout: bet * SLOT_PAYS.two, kind: 'two' };
  return { payout: 0, kind: 'none' };
}

// ------------------------------------------------------------------ bull dodge
// Bull Run — TOU's Ox Dodge (disc: EUROPA/SPANISH/OXGAME.DXR).
// Three lanes; the ox charges down one. Step aside or the run ends.
// Pure step core: bullY counts down from 10 to 0; at 0 the ox reaches the
// player row — same lane = gored, other lane = dodged, next ox spawns.
export const BULL = { lanes: 3, startY: 10, shardsPerDodge: 5 };

export function createBull(rng) {
  return {
    playerLane: 1,
    bullLane: Math.floor(rng() * BULL.lanes),
    bullY: BULL.startY,
    dodges: 0,
    over: false,
    gored: false,
  };
}

export function bullStep(game, move, rng) {
  if (game.over) return { ok: false, error: 'run over' };
  game.playerLane = Math.max(0, Math.min(BULL.lanes - 1, game.playerLane + (move || 0)));
  game.bullY -= 1;
  if (game.bullY > 0) return { ok: true, over: false, dodged: false };
  // Ox reaches the player row.
  if (game.bullLane === game.playerLane) {
    game.over = true;
    game.gored = true;
    return { ok: true, over: true, dodged: false, gored: true };
  }
  game.dodges += 1;
  game.bullLane = Math.floor(rng() * BULL.lanes);
  game.bullY = BULL.startY;
  return { ok: true, over: false, dodged: true, dodges: game.dodges };
}

export function bullShards(dodges) {
  return Math.max(0, dodges) * BULL.shardsPerDodge;
}

// ------------------------------------------------------------------ DOM shell
// el() builds a wrapper div around ALL top-level nodes in the HTML string.
// (The Sato slice this file was ported from used template.content.firstChild,
// which silently dropped every sibling after the first — the header's Area /
// Region / Scene selects and the SAIL / VISIT buttons never entered the DOM,
// so mount threw on areaSel.addEventListener and the whole hub died. Found by
// the C11 e2e console capture, run 45870176926. A wrapper div keeps every
// child, and the append-then-querySelector call sites still work.)
function el(html) {
  const d = document.createElement('div');
  d.innerHTML = html.trim();
  return d;
}

function identity() {
  return (typeof window !== 'undefined' && window.WHIdentity) || null;
}

function awardShards(state, n, source) {
  if (!n) return;
  state.shardsEarned += n;
  const I = identity();
  if (I && typeof I.addShards === 'function') I.addShards(n, source);
}

function loadProgress(state) {
  try {
    const raw = window.localStorage.getItem('wh-rolypolys-hub-v1');
    if (!raw) return;
    const saved = JSON.parse(raw);
    if (Array.isArray(saved.visited)) state.visited = saved.visited;
    if (Array.isArray(saved.items)) state.items = saved.items;
    if (Array.isArray(saved.endings)) state.endings = saved.endings;
    if (typeof saved.shardsEarned === 'number') state.shardsEarned = saved.shardsEarned;
    if (saved.area && areaById(WORLD, saved.area)) state.area = saved.area;
  } catch (e) { /* fresh start on bad save */ }
}

function saveProgress(state) {
  try {
    window.localStorage.setItem('wh-rolypolys-hub-v1', JSON.stringify({
      visited: state.visited, items: state.items, endings: state.endings,
      shardsEarned: state.shardsEarned, area: state.area,
    }));
  } catch (e) { /* storage unavailable — progress stays in memory */ }
}

export function mountRolyPolysHub(host) {
  if (!host || typeof document === 'undefined') return null;
  const state = createHubState();
  loadProgress(state);
  const world = WORLD;

  host.appendChild(el(
    // Art header (2026-11-26 art pass): the Banabana crossing the
    // violet sea at dawn. The old Ship paragraph was a text dump —
    // one short line now; the full rules live in the selects below.
    '<div class="gw-hub-head"><img src="assets/godwithin/banabana-sea.png" alt="Banabana MK.1 crossing the violet sea at dawn" />' +
    '<h3>BANABANA MK.1</h3>' +
    '<p>RIN sails the Nine Souls across 7 areas. One item per scene — winnings pay Soul Shards.</p></div>' +
    '<div class="wh-row"><label>Area <select id="rp-area"></select></label>' +
    '<label>Region <select id="rp-region"></select></label>' +
    '<label>Scene <select id="rp-scene"></select></label>' +
    '<button class="wh-btn" id="rp-sail">⛵ SAIL</button>' +
    '<button class="wh-btn" id="rp-visit">📍 VISIT SCENE</button></div>' +
    '<p id="rp-status" style="color:var(--wh-gold);font-weight:700"></p>' +
    '<p id="rp-progress"></p>' +
    '<p id="rp-items"></p>' +
    '<p id="rp-endings"></p>' +
    '<div id="rp-log" style="max-height:120px;overflow:auto;font-size:13px;opacity:.85"></div>',
  ));

  const areaSel = host.querySelector('#rp-area');
  const regionSel = host.querySelector('#rp-region');
  const sceneSel = host.querySelector('#rp-scene');
  const statusEl = host.querySelector('#rp-status');
  const progressEl = host.querySelector('#rp-progress');
  const itemsEl = host.querySelector('#rp-items');
  const endingsEl = host.querySelector('#rp-endings');
  const logEl = host.querySelector('#rp-log');

  function log(msg) {
    const d = document.createElement('div');
    d.textContent = msg;
    logEl.prepend(d);
  }

  function refreshSelects() {
    areaSel.innerHTML = listAreas(world).map((id) =>
      '<option value="' + id + '"' + (id === state.area ? ' selected' : '') + '>' + id + '</option>').join('');
    const regions = listRegions(world, state.area);
    if (!regions.includes(state.region)) state.region = regions[0] || null;
    regionSel.innerHTML = regions.map((id) =>
      '<option value="' + id + '"' + (id === state.region ? ' selected' : '') + '>' + id + '</option>').join('');
    const scenes = state.region ? listScenes(world, state.area, state.region) : [];
    if (!scenes.includes(state.scene)) state.scene = scenes[0] || null;
    sceneSel.innerHTML = scenes.map((id) =>
      '<option value="' + id + '"' + (id === state.scene ? ' selected' : '') + '>' + id + '</option>').join('');
  }

  function refreshStatus() {
    const p = areaProgress(state, world, state.area);
    progressEl.textContent = 'Area ' + state.area + ': ' + p.visited + '/' + p.total +
      ' scenes · ' + state.items.length + ' items · ' + state.endings.length +
      ' endings · ' + state.shardsEarned + ' shards';
    itemsEl.textContent = state.items.length
      ? 'Items: ' + state.items.slice(-12).join(', ') + (state.items.length > 12 ? ' …' : '')
      : 'Items: none yet — visit a scene to collect its item.';
    endingsEl.textContent = state.endings.length
      ? 'Endings unlocked: ' + state.endings.map((a) => {
        const e = endingForArea(world, a);
        return a + ' (' + (e ? e.movie : '?') + (e && e.kind === 'finale' ? ', finale' : '') + ')';
      }).join(' · ')
      : 'Endings: none yet — finish every scene in an area.';
  }

  areaSel.addEventListener('change', () => {
    const r = sailTo(state, world, areaSel.value);
    if (r.ok) { state.region = null; state.scene = null; refreshSelects(); refreshStatus(); log('⛵ Banabana sails to ' + areaSel.value + '.'); }
  });
  regionSel.addEventListener('change', () => { state.region = regionSel.value; state.scene = null; refreshSelects(); refreshStatus(); });
  sceneSel.addEventListener('change', () => { state.scene = sceneSel.value; });
  host.querySelector('#rp-sail').addEventListener('click', () => {
    const r = sailTo(state, world, areaSel.value);
    if (r.ok) { state.region = null; state.scene = null; refreshSelects(); refreshStatus(); statusEl.textContent = '⛵ Sailed to ' + areaSel.value + '.'; log('⛵ Banabana sails to ' + areaSel.value + '.'); }
  });
  host.querySelector('#rp-visit').addEventListener('click', () => {
    const r = visitScene(state, world, state.area, state.region, state.scene);
    if (!r.ok) { statusEl.textContent = r.error; return; }
    if (r.firstVisit) { statusEl.textContent = '📍 ' + state.scene + ' visited — item collected: ' + r.item + '.'; log('📍 ' + state.area + '/' + state.region + '/' + state.scene + ' — item ' + r.item + ' collected.'); }
    else { statusEl.textContent = '📍 ' + state.scene + ' revisited.'; }
    if (r.ending) {
      statusEl.textContent += ' 🎬 Ending unlocked: ' + r.ending.movie + (r.ending.kind === 'finale' ? ' (finale)' : '') + '!';
      log('🎬 ' + state.area + ' complete — ending ' + r.ending.movie + ' unlocked.');
    }
    saveProgress(state);
    refreshStatus();
  });

  // ---- Shooting gallery (TOU) ----
  host.appendChild(el(
    '<h3>🎯 TOU\'s Shooting Gallery <span class="root">· SHOOTING.DXR — 8 targets, 30 seconds, 10 shards a hit</span></h3>' +
    '<canvas id="rp-shoot" width="640" height="360"></canvas>' +
    '<div class="playrow"><button class="wh-btn" id="rp-shoot-start">BEGIN SHOOTING</button>' +
    '<span id="rp-shoot-score" style="align-self:center;color:var(--wh-gold);font-weight:800"></span></div>',
  ));
  mountShooting(host, state);

  // ---- Cooking (KAI) ----
  host.appendChild(el(
    '<h3>🍜 KAI\'s Cooking School — Miso <span class="root">· MISO_KO.DXR — stop the marker in the zone, 3 rounds</span></h3>' +
    '<div id="rp-cook-meter" style="position:relative;height:26px;background:#1d5c34;border-radius:13px;overflow:hidden">' +
    '<div style="position:absolute;left:45%;width:10%;height:100%;background:rgba(255,233,150,.55)"></div>' +
    '<div id="rp-cook-marker" style="position:absolute;left:50%;top:0;width:4px;height:100%;background:#fff"></div></div>' +
    '<div class="playrow"><button class="wh-btn" id="rp-cook-stop">STOP — TASTE IT</button>' +
    '<span id="rp-cook-score" style="align-self:center;color:var(--wh-gold);font-weight:800"></span></div>',
  ));
  mountCooking(host, state);

  // ---- Slot (the Trader) ----
  host.appendChild(el(
    '<h3>🎰 The Trader\'s Slot <span class="root">· slot.dcr, OSD 1997 — 3 of a kind pays 10×, 2 pays 2×</span></h3>' +
    '<div class="wh-row"><input id="rp-slot-bet" class="wh-input" type="number" min="10" value="10" style="max-width:130px" />' +
    '<button class="wh-btn" id="rp-slot-spin">SPIN</button>' +
    '<span class="wh-dice" id="rp-slot-r1">凛</span><span class="wh-dice" id="rp-slot-r2">闘</span><span class="wh-dice" id="rp-slot-r3">商</span>' +
    '<b id="rp-slot-msg" style="color:var(--wh-gold)"></b></div>',
  ));
  mountSlot(host, state);

  // ---- Bull dodge (OXGAME) ----
  host.appendChild(el(
    '<h3>🐂 Bull Run — TOU\'s Ox Dodge <span class="root">· OXGAME.DXR — dodge the charging ox, 5 shards a dodge</span></h3>' +
    '<canvas id="rp-bull" width="640" height="360"></canvas>' +
    '<div class="playrow"><button class="wh-btn" id="rp-bull-start">BEGIN THE RUN</button>' +
    '<span id="rp-bull-score" style="align-self:center;color:var(--wh-gold);font-weight:800"></span></div>' +
    '<p class="sub">Move with ← → or tap the left / right half of the field.</p>',
  ));
  mountBull(host, state);

  // ---- Lore vignettes (A–Z) ----
  const vig = el(
    '<h3>🔤 Lore Vignettes A–Z <span class="root">· A–Z.DXR + EXPA–EXPZ.DXR — WH-canon words, hosted by RIN</span></h3>' +
    '<div id="rp-vig-letters" class="wh-row" style="flex-wrap:wrap"></div>' +
    '<p id="rp-vig-text" style="color:var(--wh-gold)"></p>',
  );
  host.appendChild(vig);
  const lettersEl = vig.querySelector('#rp-vig-letters');
  const vigText = vig.querySelector('#rp-vig-text');
  ROLYPOLYS_VIGNETTES.forEach((v) => {
    const b = document.createElement('button');
    b.className = 'wh-btn';
    b.textContent = v.letter;
    b.addEventListener('click', () => {
      vigText.textContent = v.letter + ' — ' + v.word + ': ' + v.text;
    });
    lettersEl.appendChild(b);
  });
  vigText.textContent = 'Tap a letter. RIN reads the vignette.';

  // ---- God-within stages ----
  const god = el(
    '<h3>🜏 God-Within Stages <span class="root">· the disc\'s own mythic sites, proposed as WH stages</span></h3>' +
    '<div id="rp-god"></div>',
  );
  host.appendChild(god);
  const godEl = god.querySelector('#rp-god');
  WORLD.godWithin.forEach((g) => {
    const d = document.createElement('div');
    d.className = 'wh-game';
    d.innerHTML = '<div class="home">' + g.area + ' / ' + g.region + ' · ' + g.scene + '.DXR</div>' +
      '<h3>' + g.whStage + '</h3><p>God-within anchor from the World Tour disc — proposed WH stage.</p>';
    godEl.appendChild(d);
  });

  // ---- Embedded minigame shells ----
  const shells = el(
    '<h3>🕹️ Embedded Minigame Shells <span class="root">· *GAME.DXR on the disc</span></h3>' +
    '<div id="rp-shells"></div>',
  );
  host.appendChild(shells);
  const shellsEl = shells.querySelector('#rp-shells');
  WORLD.minigames.forEach((m) => {
    const d = document.createElement('div');
    d.className = 'wh-game';
    d.innerHTML = '<div class="home">' + m.area + ' / ' + m.region + ' · ' + m.id + '.DXR</div>' +
      '<h3>' + m.whName + ' ' + (m.status === 'playable' ? '🎮' : '⏳') + '</h3><p>' + m.note + '</p>';
    shellsEl.appendChild(d);
  });

  refreshSelects();
  refreshStatus();
  statusEl.textContent = '⛵ The Banabana waits at ' + state.area + ' — home leg Japan. Pick a destination and sail.';
  return { state, world };
}

function mountShooting(host, state) {
  const cv = host.querySelector('#rp-shoot');
  const ctx = cv.getContext('2d');
  const scoreEl = host.querySelector('#rp-shoot-score');
  const W = cv.width, H = cv.height;
  let running = false, targets = [], hits = 0, t0 = 0, raf = 0;

  function draw() {
    ctx.fillStyle = '#241335';
    ctx.fillRect(0, 0, W, H);
    targets.forEach((t) => {
      ctx.fillStyle = '#ffe996';
      ctx.beginPath(); ctx.arc(t.x, t.y, t.r, 0, 7); ctx.fill();
      ctx.strokeStyle = '#8b2bd8'; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.arc(t.x, t.y, t.r * 0.55, 0, 7); ctx.stroke();
      ctx.fillStyle = '#8b2bd8';
      ctx.beginPath(); ctx.arc(t.x, t.y, 4, 0, 7); ctx.fill();
    });
    ctx.fillStyle = 'rgba(255,255,255,0.75)';
    ctx.font = '13px sans-serif'; ctx.textAlign = 'center';
    ctx.fillText('hits: ' + hits + '   targets left: ' + targets.length, W / 2, 22);
    const left = Math.max(0, SHOOTING.seconds - (performance.now() - t0) / 1000);
    ctx.fillText(left.toFixed(0) + 's', W - 40, 22);
  }

  function step() {
    if (!running) return;
    if (performance.now() - t0 > SHOOTING.seconds * 1000 || targets.length === 0) { end(); return; }
    draw();
    raf = requestAnimationFrame(step);
  }

  function end() {
    running = false;
    cancelAnimationFrame(raf);
    draw();
    const shards = shootingShards(hits);
    awardShards(state, shards, 'rolypolys-shooting');
    scoreEl.textContent = 'final ' + hits + ' hits — ' + shards + ' shards.';
    const I = identity();
    if (I && typeof I.get === 'function') { const p = I.get(); p.stats.sideGames = (p.stats.sideGames || 0) + 1; I.save(); }
  }

  cv.addEventListener('pointerdown', (e) => {
    if (!running) return;
    const r = cv.getBoundingClientRect();
    const x = (e.clientX - r.left) * (W / r.width), y = (e.clientY - r.top) * (H / r.height);
    if (shootingHit(targets, x, y)) {
      hits += 1;
      awardShards(state, SHOOTING.shardsPerHit, 'rolypolys-shooting');
      scoreEl.textContent = 'hits ' + hits;
      draw();
    }
  });
  host.querySelector('#rp-shoot-start').addEventListener('click', () => {
    targets = spawnTargets(mulberry32((Date.now() % 2147483647) || 1), SHOOTING.targets, W, H);
    hits = 0;
    t0 = performance.now();
    running = true;
    scoreEl.textContent = '';
    step();
  });
  draw();
}

function mountCooking(host, state) {
  const marker = host.querySelector('#rp-cook-marker');
  const scoreEl = host.querySelector('#rp-cook-score');
  const game = createCooking();
  let pos = 0, dir = 1, raf = 0, running = false;

  function tick() {
    if (!running) return;
    pos += dir * 1.6;
    if (pos >= 100) { pos = 100; dir = -1; }
    if (pos <= 0) { pos = 0; dir = 1; }
    marker.style.left = 'calc(' + pos + '% - 2px)';
    raf = requestAnimationFrame(tick);
  }

  host.querySelector('#rp-cook-stop').addEventListener('click', () => {
    if (!running) {
      // Start a fresh cook.
      Object.assign(game, createCooking());
      pos = 0; dir = 1; running = true;
      scoreEl.textContent = 'Round 1 of 3 — stop it in the gold.';
      tick();
      return;
    }
    const r = cookingRound(game, pos);
    if (!r.ok) return;
    scoreEl.textContent = 'Round ' + game.last.round + ': ' + game.last.grade +
      ' (+' + game.last.shards + ') — total ' + game.score + '.';
    if (r.done) {
      running = false;
      cancelAnimationFrame(raf);
      awardShards(state, game.score, 'rolypolys-cooking');
      scoreEl.textContent += ' Done — ' + game.score + ' shards. Tap STOP to cook again.';
      const I = identity();
      if (I && typeof I.get === 'function') { const p = I.get(); p.stats.sideGames = (p.stats.sideGames || 0) + 1; I.save(); }
    }
  });
}

function mountSlot(host, state) {
  const msg = host.querySelector('#rp-slot-msg');
  host.querySelector('#rp-slot-spin').addEventListener('click', () => {
    const I = identity();
    const bet = Math.max(10, parseInt(host.querySelector('#rp-slot-bet').value, 10) || 10);
    if (I) {
      const p = I.get();
      if (p.shards < bet) { msg.textContent = 'Not enough ' + I.CURRENCY_NAME + '. Win battles first.'; return; }
      I.spendShards(bet);
    }
    const symbols = spinSlot(mulberry32((Date.now() % 2147483647) || 1));
    host.querySelector('#rp-slot-r1').textContent = symbols[0];
    host.querySelector('#rp-slot-r2').textContent = symbols[1];
    host.querySelector('#rp-slot-r3').textContent = symbols[2];
    const res = slotPayout(symbols, bet);
    if (res.payout > 0) {
      awardShards(state, res.payout, 'rolypolys-slot');
      msg.textContent = (res.kind === 'three' ? 'JACKPOT! ' : 'Pair! ') + 'The Trader pays ' + res.payout + '.';
    } else {
      msg.textContent = 'No match. The Trader keeps your ' + bet + '.';
    }
    if (I && typeof I.get === 'function') { const p = I.get(); p.stats.sideGames = (p.stats.sideGames || 0) + 1; I.save(); }
  });
}

function mountBull(host, state) {
  const cv = host.querySelector('#rp-bull');
  const ctx = cv.getContext('2d');
  const scoreEl = host.querySelector('#rp-bull-score');
  const W = cv.width, H = cv.height;
  let game = null, running = false, raf = 0, lastStep = 0;

  function draw() {
    ctx.fillStyle = '#3a2410';
    ctx.fillRect(0, 0, W, H);
    // lanes
    ctx.strokeStyle = 'rgba(255,255,255,0.25)';
    ctx.lineWidth = 2;
    for (let i = 1; i < BULL.lanes; i++) {
      ctx.beginPath(); ctx.moveTo((W / BULL.lanes) * i, 0); ctx.lineTo((W / BULL.lanes) * i, H); ctx.stroke();
    }
    if (!game) return;
    // ox
    const oxX = (game.bullLane + 0.5) * (W / BULL.lanes);
    const oxY = H - 40 - ((BULL.startY - game.bullY) / BULL.startY) * (H - 120);
    ctx.fillStyle = '#1a1a1a';
    ctx.beginPath(); ctx.arc(oxX, oxY, 26, 0, 7); ctx.fill();
    ctx.fillStyle = '#ffe996';
    ctx.beginPath(); ctx.arc(oxX - 10, oxY - 8, 4, 0, 7); ctx.fill();
    ctx.beginPath(); ctx.arc(oxX + 10, oxY - 8, 4, 0, 7); ctx.fill();
    // player (TOU)
    const px = (game.playerLane + 0.5) * (W / BULL.lanes);
    ctx.fillStyle = '#c0392b';
    ctx.beginPath(); ctx.arc(px, H - 40, 16, 0, 7); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.8)';
    ctx.font = '13px sans-serif'; ctx.textAlign = 'center';
    ctx.fillText('dodges: ' + game.dodges, W / 2, 22);
    if (game.over) ctx.fillText(game.gored ? 'GORED! The run ends.' : '', W / 2, 44);
  }

  function step(now) {
    if (!running) return;
    if (now - lastStep > 120) {
      lastStep = now;
      const r = bullStep(game, 0, mulberry32((Date.now() % 2147483647) || 1));
      if (r.dodged) awardShards(state, BULL.shardsPerDodge, 'rolypolys-bull');
      if (r.over) {
        running = false;
        cancelAnimationFrame(raf);
        const shards = bullShards(game.dodges);
        scoreEl.textContent = 'Gored after ' + game.dodges + ' dodges — ' + shards + ' shards.';
        draw();
        const I = identity();
        if (I && typeof I.get === 'function') { const p = I.get(); p.stats.sideGames = (p.stats.sideGames || 0) + 1; I.save(); }
        return;
      }
      scoreEl.textContent = 'dodges ' + game.dodges;
    }
    draw();
    raf = requestAnimationFrame(step);
  }

  function move(dir) {
    if (!running || !game) return;
    game.playerLane = Math.max(0, Math.min(BULL.lanes - 1, game.playerLane + dir));
    draw();
  }

  cv.addEventListener('pointerdown', (e) => {
    const r = cv.getBoundingClientRect();
    const x = e.clientX - r.left;
    move(x < r.width / 2 ? -1 : 1);
  });
  document.addEventListener('keydown', (e) => {
    if (!running) return;
    if (e.key === 'ArrowLeft') move(-1);
    if (e.key === 'ArrowRight') move(1);
  });
  host.querySelector('#rp-bull-start').addEventListener('click', () => {
    game = createBull(mulberry32((Date.now() % 2147483647) || 1));
    running = true;
    lastStep = performance.now();
    scoreEl.textContent = '';
    raf = requestAnimationFrame(step);
  });
  draw();
}
