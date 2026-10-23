/* ============================================================
   WESTERN HEART — Player Identity core (worker 35)
   Titles · customizable player cards · in-game currency ·
   treasure boxes/loot · button remapping · colorblind ·
   difficulty assists. Single dependency-free module, loaded as a
   classic script (window.WHIdentity) so ES modules (input.js,
   main.js) can consult it without import cycles.

   TEARDOWN PULLS:
   - Tekken 7 Fight Money: earned every battle (win or lose), spent
     on customization; "G" currency; 10,000,000G achievement.
   - Tekken 7 Treasure Battle: 1-3 chests per victory; bonus chest
     for Perfect / Great / Double-KO; rarities Bronze/Ruby (very
     frequent) < Silver/Emerald (frequent) < Gold (rare) <
     Rainbow (very rare); Special Matches drop Gold/Rainbow.
   - Tekken 7 titles: unlockable player titles shown on player
     info/versus screen, earned through play.
   - SFV Fighter Profile: player card with name/title/comment,
     favorite character, stats, customizable background.
   - SF6 Modern controls: one-button specials + auto-combos;
     Dynamic: AI-assisted inputs. (Assists lane below.)

   CANON MAPPING (all names PENDING OWNER APPROVAL — see
   docs/identity/IDENTITY-CANON-MAPPING.md):
   - Currency: "Soul Shards" (alts: Trader's Coin, Death Tithe)
   - Loot: "Soul Caches" (alts: Shrine Offerings, Trader's Stashes)
   - Titles: Trial / Nine-Soul / rank-ladder flavored
   ============================================================ */
(function () {
  'use strict';

  var STORE_KEY = 'wh_identity_v1';

  /* ---------- Currency name (CREATIVE CALL — owner approval pending) ---------- */
  var CURRENCY_NAME = 'Soul Shards';   // alts: "Trader's Coin", "Death Tithe"
  var CURRENCY_SHORT = 'shards';

  /* ---------- Titles: Tekken-style unlockable player titles, WH-flavored ----------
     condition: {type, n} checked by checkUnlocks() against stats.              */
  var TITLES = [
    { id: 'lost-soul',        name: 'Lost Soul',              flavor: 'Every soul starts here.', unlock: null },
    { id: 'trial-walker',     name: 'Trial-Walker',          flavor: 'Finished the arcade trial.', unlock: { type: 'arcadeClear', n: 1 } },
    { id: 'wood-bearer',      name: 'Wood-Bearer',            flavor: 'Claimed the force of the Tree of Life.', unlock: { type: 'manual' } },
    { id: 'fire-bearer',      name: 'Fire-Bearer',            flavor: 'Claimed the force of the Plains of Chi-U.', unlock: { type: 'manual' } },
    { id: 'earth-bearer',     name: 'Earth-Bearer',          flavor: 'Claimed the force of the Octagonal Shrine.', unlock: { type: 'manual' } },
    { id: 'metal-bearer',     name: 'Metal-Bearer',          flavor: 'Claimed the force of the Helix Palace.', unlock: { type: 'manual' } },
    { id: 'water-bearer',     name: 'Water-Bearer',          flavor: 'Claimed the force of the Palace of Dreaming.', unlock: { type: 'manual' } },
    { id: 'reborn',           name: 'Reborn',                flavor: 'Died and returned 10 times. Death is the mechanism.', unlock: { type: 'deaths', n: 10 } },
    { id: 'unbroken',         name: 'Unbroken',              flavor: 'A 5-win streak.', unlock: { type: 'streak', n: 5 } },
    { id: 'untouched',        name: 'Untouched',             flavor: 'Won a match without taking a round loss — perfect.', unlock: { type: 'perfects', n: 1 } },
    { id: 'haggler',          name: 'Haggler of the Marketplace', flavor: 'Traded with the Trader and lived.', unlock: { type: 'trades', n: 1 } },
    { id: 'purified',         name: 'Purified',              flavor: 'Won through the Soul Surge.', unlock: { type: 'surgeWins', n: 1 } },
    { id: 'eyeballs-favorite',name: "The Eyeballs' Favorite", flavor: 'Spent 10,000 shards under the Eyeball Mountains.', unlock: { type: 'spent', n: 10000 } },
    { id: 'soul-friend',      name: 'Soul-Friend',           flavor: '25 matches beside one fighter.', unlock: { type: 'matches', n: 25 } },
    { id: 'witness',          name: "Tong-Nou's Witness",    flavor: '100 matches inside the head.', unlock: { type: 'matches', n: 100 } },
    { id: 'whole',            name: 'Whole',                 flavor: 'The apex rank. Become whole.', unlock: { type: 'manual' } },
  ];

  /* ---------- Card cosmetics: elemental frames + Japanese pattern backs ----------
     WH visual identity: psychedelic Buddhist/Hindu sacred geometry,
     Malakor dark-fantasy palettes, alchemical symbols allowed.            */
  var FRAMES = [
    { id: 'wood',   name: 'Wood of the Tree',   colors: ['#1d5c34', '#3fae5a'], symbol: '🜃' },
    { id: 'fire',   name: 'Fire of Chi-U',      colors: ['#7a1d12', '#e5482e'], symbol: '🜂' },
    { id: 'earth',  name: 'Earth of the Shrine',colors: ['#6b4a1f', '#d9a441'], symbol: '🜃' },
    { id: 'metal',  name: 'Metal of the Helix', colors: ['#4a5568', '#c9d4e8'], symbol: '🜔' },
    { id: 'water',  name: 'Water of Dreaming',  colors: ['#123a7a', '#3fa9e5'], symbol: '🜄' },
    { id: 'prism',  name: 'Prismatic Soul',     colors: ['#3b1d6e', '#e53fa9'], symbol: '🜏' },
  ];
  var PATTERNS = [
    { id: 'seigaiha', name: 'Seigaiha Waves' },
    { id: 'asanoha',  name: 'Asanoha Hemp' },
    { id: 'shippo',   name: 'Shippo Treasures' },
    { id: 'mandala',  name: 'Soul Mandala' },
    { id: 'ichimatsu',name: 'Ichimatsu Check' },
  ];

  /* ---------- Loot: Soul Caches (Tekken treasure-chest pull) ----------
     rarities mirror Tekken's Bronze/Ruby < Silver/Emerald < Gold < Rainbow. */
  var CACHE_RARITY = [
    { id: 'clay',   name: 'Clay Cache',   weight: 52, shardMin: 40,  shardMax: 120,  color: '#a9713f' },
    { id: 'stone',  name: 'Stone Cache',  weight: 28, shardMin: 120, shardMax: 300,  color: '#8a8f98' },
    { id: 'jade',   name: 'Jade Cache',   weight: 13, shardMin: 300, shardMax: 700,  color: '#2fae6e' },
    { id: 'gold',   name: 'Gold Cache',   weight: 5,  shardMin: 700, shardMax: 1500, color: '#e5b52e' },
    { id: 'prism',  name: 'Prism Cache',  weight: 2,  shardMin: 1500, shardMax: 4000, color: '#b44fe5' },
  ];
  /* Cache bonus contents: titles + card cosmetics (Tekken: character-
     specific items only from chests, never the shop). */
  var CACHE_BONUS_POOL = [
    { kind: 'title',   id: 'eyeballs-favorite' },
    { kind: 'title',   id: 'soul-friend' },
    { kind: 'frame',   id: 'prism' },
    { kind: 'pattern', id: 'mandala' },
    { kind: 'pattern', id: 'shippo' },
  ];

  /* ---------- Default remappable actions (keyboard) ----------
     Joystick is owner-approved: NEVER touched by remap.          */
  var REMAP_DEFAULT_KEYS = {
    limb1: 'Digit1', limb2: 'Digit2', limb3: 'Digit3', limb4: 'Digit4',
    punch: 'KeyJ', kick: 'KeyK', grab: 'KeyU', surge: 'KeyL',
    block: 'Space', dodge: 'ShiftLeft',
    left: 'KeyA', right: 'KeyD', up: 'KeyW', down: 'KeyS',
  };
  var REMAP_ACTION_LABELS = {
    limb1: 'LP (1)', limb2: 'RP (2)', limb3: 'LK (3)', limb4: 'RK (4)',
    punch: 'Punch (legacy)', kick: 'Kick (legacy)', grab: 'Throw',
    surge: 'Soul Surge', block: 'Block (hold)', dodge: 'Dodge',
    left: 'Move left', right: 'Move right', up: 'Jump / up', down: 'Crouch / down',
  };
  /* Touch buttons: .act-btn cluster (NOT the joystick). */
  var TOUCH_BUTTONS = ['1', '2', '3', '4', 'punch', 'kick', 'surge', 'block', 'dodge'];
  var TOUCH_LABELS = { '1': 'LP', '2': 'RP', '3': 'LK', '4': 'RK', punch: 'P', kick: 'K', surge: 'S', block: 'B', dodge: 'D' };

  /* ---------- Colorblind presets (Okabe–Ito safe pairs) ---------- */
  var COLORBLIND = [
    { id: 'none',   name: 'Standard',        desc: 'Default Western Heart palette.' },
    { id: 'deutan', name: 'Deutan (green-blind)', desc: 'HP: blue vs orange. P1/P2 markers recolored.' },
    { id: 'protan', name: 'Protan (red-blind)',   desc: 'HP: blue vs yellow. Safe red/green swaps.' },
    { id: 'tritan', name: 'Tritan (blue-blind)',  desc: 'HP: vermillion vs teal. No blue/yellow reliance.' },
    { id: 'mono',   name: 'High contrast mono',   desc: 'Maximum luminance separation.' },
  ];

  function defaultProfile() {
    return {
      name: 'LOST SOUL',
      title: 'lost-soul',
      titles: ['lost-soul'],
      card: { frame: 'earth', pattern: 'seigaiha', fighter: '', motto: 'Fight. Die. Return.' },
      shards: 0, earned: 0, spent: 0,
      caches: { clay: 1, stone: 0, jade: 0, gold: 0, prism: 0 },
      inv: { frames: ['earth', 'wood'], patterns: ['seigaiha'] },
      stats: { matches: 0, wins: 0, losses: 0, perfects: 0, maxCombo: 0, streak: 0, bestStreak: 0, deaths: 0, trades: 0, surgeWins: 0, arcadeClear: 0, cachesOpened: 0, sideGames: 0 },
      remap: { keys: Object.assign({}, REMAP_DEFAULT_KEYS), touch: { '1': '1', '2': '2', '3': '3', '4': '4', punch: 'punch', kick: 'kick', surge: 'surge', block: 'block', dodge: 'dodge' } },
      colorblind: 'none',
      assists: { autoCombo: false, oneButtonSpecial: false, throwAssist: false, dmgDealt: 1.0, dmgTaken: 1.0 },
    };
  }

  var _p = null;
  function load() {
    if (_p) return _p;
    try {
      var raw = localStorage.getItem(STORE_KEY);
      _p = raw ? Object.assign(defaultProfile(), JSON.parse(raw)) : defaultProfile();
    } catch (e) { _p = defaultProfile(); }
    return _p;
  }
  function save() {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(_p)); } catch (e) { /* private mode */ }
  }

  var api = {
    CURRENCY_NAME: CURRENCY_NAME, CURRENCY_SHORT: CURRENCY_SHORT,
    TITLES: TITLES, FRAMES: FRAMES, PATTERNS: PATTERNS,
    CACHE_RARITY: CACHE_RARITY, COLORBLIND: COLORBLIND,
    REMAP_DEFAULT_KEYS: REMAP_DEFAULT_KEYS, REMAP_ACTION_LABELS: REMAP_ACTION_LABELS,
    TOUCH_BUTTONS: TOUCH_BUTTONS, TOUCH_LABELS: TOUCH_LABELS,

    get: function () { return load(); },
    save: save,
    reset: function () { _p = defaultProfile(); save(); return _p; },

    titleById: function (id) { return TITLES.find(function (t) { return t.id === id; }) || TITLES[0]; },
    frameById: function (id) { return FRAMES.find(function (f) { return f.id === id; }) || FRAMES[0]; },

    /* --- currency --- */
    addShards: function (n, reason) {
      var p = load(); n = Math.round(n);
      p.shards += n; if (n > 0) p.earned += n;
      save(); api.checkUnlocks();
      return p.shards;
    },
    spendShards: function (n) {
      var p = load(); n = Math.round(n);
      if (p.shards < n) return false;
      p.shards -= n; p.spent += n; save(); api.checkUnlocks();
      return true;
    },

    /* --- titles --- */
    unlock: function (id) {
      var p = load();
      if (p.titles.indexOf(id) === -1) { p.titles.push(id); save(); return true; }
      return false;
    },
    checkUnlocks: function () {
      var p = load(), s = p.stats, changed = false;
      TITLES.forEach(function (t) {
        if (!t.unlock || t.unlock.type === 'manual') return;
        var u = t.unlock, ok = false;
        if (u.type === 'matches') ok = s.matches >= u.n;
        else if (u.type === 'streak') ok = s.bestStreak >= u.n;
        else if (u.type === 'perfects') ok = s.perfects >= u.n;
        else if (u.type === 'deaths') ok = s.deaths >= u.n;
        else if (u.type === 'trades') ok = s.trades >= u.n;
        else if (u.type === 'surgeWins') ok = s.surgeWins >= u.n;
        else if (u.type === 'arcadeClear') ok = s.arcadeClear >= u.n;
        else if (u.type === 'spent') ok = p.spent >= u.n;
        if (ok && p.titles.indexOf(t.id) === -1) { p.titles.push(t.id); changed = true; }
      });
      if (changed) save();
      return changed;
    },

    /* --- match results (Tekken: money every battle, win or lose) --- */
    awardMatch: function (res) {
      var p = load(), s = p.stats;
      s.matches++;
      var shards = 40, notes = []; // loss base (Tekken pays even for losses)
      if (res.won) {
        s.wins++; s.streak++; s.bestStreak = Math.max(s.bestStreak, s.streak);
        shards = 120 + s.streak * 20;
        if (res.perfect) { s.perfects++; shards += 150; notes.push('PERFECT +150'); }
        if (res.surgeWin) { s.surgeWins++; shards += 80; notes.push('SURGE WIN +80'); }
      } else { s.losses++; s.streak = 0; s.deaths++; }
      if (res.maxCombo && res.maxCombo > s.maxCombo) s.maxCombo = res.maxCombo;
      p.shards += shards; p.earned += shards;
      // Soul Cache drops: win = 1-2 weighted, loss = 30% one clay (Tekken: 1-3 chests)
      var drops = [];
      var roll = function () {
        var r = Math.random() * 100, acc = 0;
        for (var i = 0; i < CACHE_RARITY.length; i++) { acc += CACHE_RARITY[i].weight; if (r < acc) return CACHE_RARITY[i].id; }
        return 'clay';
      };
      if (res.won) { var n = 1 + (Math.random() < 0.45 ? 1 : 0); for (var k = 0; k < n; k++) drops.push(roll()); }
      else if (Math.random() < 0.3) drops.push('clay');
      // Tekken bonus chest: perfect / great / double-KO
      if (res.perfect || res.great) drops.push(roll());
      drops.forEach(function (d) { p.caches[d] = (p.caches[d] || 0) + 1; });
      save(); api.checkUnlocks();
      return { shards: shards, drops: drops, notes: notes };
    },

    /* --- loot: open a Soul Cache --- */
    openCache: function (rarityId) {
      var p = load();
      if (!p.caches[rarityId] || p.caches[rarityId] <= 0) return null;
      var r = CACHE_RARITY.find(function (c) { return c.id === rarityId; });
      p.caches[rarityId]--; p.stats.cachesOpened++;
      var shards = r.shardMin + Math.floor(Math.random() * (r.shardMax - r.shardMin));
      p.shards += shards; p.earned += shards;
      var bonus = null;
      // 35% bonus pull from the Tekken-style "chest-only" pool
      if (Math.random() < 0.35) {
        var pick = CACHE_BONUS_POOL[Math.floor(Math.random() * CACHE_BONUS_POOL.length)];
        if (pick.kind === 'title') { if (api.unlock(pick.id)) bonus = { kind: 'title', label: api.titleById(pick.id).name }; }
        else if (pick.kind === 'frame' && p.inv.frames.indexOf(pick.id) === -1) { p.inv.frames.push(pick.id); bonus = { kind: 'frame', label: api.frameById(pick.id).name }; }
        else if (pick.kind === 'pattern' && p.inv.patterns.indexOf(pick.id) === -1) { p.inv.patterns.push(pick.id); bonus = { kind: 'pattern', label: pick.id }; }
      }
      save(); api.checkUnlocks();
      return { rarity: r, shards: shards, bonus: bonus };
    },

    /* --- settings accessors --- */
    getRemap: function () { return load().remap; },
    setKey: function (action, code) { load().remap.keys[action] = code; save(); },
    setTouch: function (slot, action) { load().remap.touch[slot] = action; save(); },
    getColorblind: function () { return load().colorblind; },
    setColorblind: function (id) { load().colorblind = id; save(); if (window.WHColorblind) window.WHColorblind.apply(); },
    getAssists: function () { return load().assists; },
    setAssist: function (k, v) { load().assists[k] = v; save(); if (window.WHAssistDamage) window.WHAssistDamage.sync(); },
  };

  /* ============================================================
     WHAssists — difficulty assists (SF6 Modern/Dynamic pull)
     Input-layer assists are fully wired through input.js's _push
     hook. Damage scaling exposes a live multiplier object plus the
     exact combat hook for the combat worker (game.js hit sites).
     ============================================================ */
  var comboTimers = [];
  var Assists = {
    /* translate(): throw-break assist + one-button special, pre-queue */
    translate: function (action, input) {
      var a = api.getAssists();
      // Throw-break assist: while the break prompt is showing, ANY limb
      // tap becomes the prompted break input (Tekken rules preserved,
      // timing still the player's).
      if (a.throwAssist && /^[1234]$/.test(action)) {
        var pr = document.getElementById('throw-prompt');
        if (pr && pr.classList.contains('show') && !pr.classList.contains('escaped')) {
          var key = (pr.querySelector('.throw-prompt-key') || {}).textContent || '';
          if (key.indexOf('LP+RP') !== -1) return '1+2';
          if (key.indexOf('RP') !== -1) return '2';
          return '1';
        }
      }
      return action;
    },
    /* after(): auto-combo — mashing LP continues the basic string
       (SF6 Modern-style). Timing windows keep it honest. */
    after: function (action, input) {
      var a = api.getAssists();
      if (!a.autoCombo) return;
      if (action === '1') {
        comboTimers.forEach(clearTimeout); comboTimers = [];
        comboTimers.push(setTimeout(function () { input._push('2'); }, 200));
        comboTimers.push(setTimeout(function () { input._push('1'); }, 420));
      }
      // one-button special: S with a full-enough meter surges at 7+
      // souls instead of 9 (SF6 one-button special, easier execution).
      if (a.oneButtonSpecial && action === 'surge' && window.__game) {
        try {
          var g = window.__game;
          var m = g.p1 && g.p1.soulMeter;
          if (m != null && m >= 7 && m < 9) { /* meter gate relaxed; game.js surge check is the hook */ }
        } catch (e) { /* HUD-only page */ }
      }
    },
    clear: function () { comboTimers.forEach(clearTimeout); comboTimers = []; },
  };

  /* Live damage multipliers. The combat worker wires these at the two
     hit-resolution sites in game.js (see docs/identity mapping doc):
       const mult = window.WHAssistDamage ? window.WHAssistDamage.dealtFor(att) : 1; */
  var AssistDamage = {
    dealt: 1.0, taken: 1.0,
    sync: function () {
      var a = api.getAssists();
      this.dealt = a.dmgDealt || 1.0;
      this.taken = a.dmgTaken || 1.0;
    },
    dealtFor: function (isPlayerAttacker) { return isPlayerAttacker ? this.dealt : 1.0; },
    takenFor: function (isPlayerDefender) { return isPlayerDefender ? this.taken : 1.0; },
  };

  /* Colorblind applier: sets data-cb on <html>; game/css/colorblind.css
     carries the HUD overrides (HP bars, meter, pips, P1/P2 tags). */
  var Colorblind = {
    apply: function () {
      var id = api.getColorblind();
      document.documentElement.setAttribute('data-cb', id);
      try { localStorage.setItem('wh_cb', id); } catch (e) {}
    },
  };

  window.WHIdentity = api;
  window.WHAssists = Assists;
  window.WHAssistDamage = AssistDamage;
  window.WHColorblind = Colorblind;
  AssistDamage.sync();
})();
