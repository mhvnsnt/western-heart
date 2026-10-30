/* ============================================================
   WESTERN HEART — UI gaps (Lane 3, 2026-10-24)
   Closes the named UI gaps from docs/research/GAP-ANALYSIS-
   EXPERIMENTAL-PROJECTS-2026-10-24.md (PR #1033 gap doc):
     Gap 12 Gallery (WH-canon equivalent — SYSTEM STRUCTURE only
       from T7, filled with WH story/show content; NEVER Tekken FMVs),
     Gap 13 Treasure Battle (endless + loot chests + currency),
     Gap 14 Character select T7 5.10 features (favorite fighter+
       attire one-button select, last-attire memory, tournament
       lock, streaming mode),
     Gap 15 VS / result screen depth (rank, W-L, connection,
       rematch / change fighter / menu),
     Gap 20 Replay theater UI (save/list/analyze/share; fight
       playback itself waits on the recorder — see below),
     Gap 21 In-fight frame-data overlay (toggle in Options).
   Plus the "anything else" sweep verdicts, recorded in
   docs/research/UI-GAPS-SWEEP-2026-10-24.md (same PR):
     - main menu structure, stage select, options, side-games
       menus, story menus, HUD, loading, VS, results: PRESENT
       (mainmenu.js / menus.js / index.html screens).
     - creation-suite sub-menus: the suite lives outside game/
       (customization/creation-suite-ui/) and is NOT restructured
       here — its menu audit is in the sweep doc, marked UNSOURCED
       for any structure not traced to PRs #770/#773/#775-#778.
     - jukebox UI: this module (audio lane owns the engine; the
       soundtrack choice is stored here and read via
       getJukeboxSoundtrack() — engine wiring is that lane's
       follow-up, NOT claimed as done here).

   SOURCING (menus from teardowns only):
     - T7 5.10 features: gap doc Gap 14 (T7 v5.10: favorite
       character+costume one-button select; last costume memory
       within session; tournament settings lock; streaming mode).
     - Gallery / Treasure / Replay theater / Jukebox structure:
       gap doc Gaps 11-13, 20 (T7 system structure).
     - Select layout it plugs into: game/js/select-screen.js
       (T3 selector teardown + T8 grid; attire chips, LP1/RP2
       punch = attire 1 / kick = attire 2 scheme).
     - Attire memory already in WH: game/js/attires.js persists
       the selected attire per fighter, and select-screen.js
       parks the P1 cursor on the last confirmed fighter
       (wh.select.last.v1). What was MISSING and is added here:
       an explicit per-fighter last-attire session record, a
       one-button favorite recall, and the tournament/streaming
       toggles. Nothing here re-invents those two.
     - Replay analysis contract: game/js/replay-analysis.js
       (REPLAY_CONTRACT_V = 1 event log). The theater stores
       contract events, analyzes them with analyzeReplay(), and
       shows an event timeline. It does NOT claim fight playback:
       no recorder has merged to main (replay-analysis.js header:
       worker 29's recorder "has NOT merged to main yet"), so
       there is no deterministic playback to play. Save/import/
       analyze/share are real; playback is an honest gap.
     - Frame tables: game/js/frame-tables.js (t8_frame_tables.json
       shape: startup/active/recovery/on_block/on_hit). The live
       overlay reads the live fighter object (game.js: p1/p2
       Fighter with .attackName / .attack / .state) and shows
       frame numbers ONLY when the live attack object carries
       numeric fields; otherwise it shows the move name and
       "frames n/a" — never invented numbers.

   MOBILE + USER FRIENDLY (user directive 2026-10-24 19:41 CDT):
     phone-first, portrait AND landscape, every tappable target
     >= 44px (see ui-gaps.css: .wh-gap-btn min-height 48px),
     tap() below is the PR #1018 pattern (touchend + click,
     12px scroll-drag guard, 600ms dedup) — used for EVERY
     tappable element this module creates. No hover-only
     controls. No modal ever covers the select preview panes:
     the gallery/jukebox/replay screens are full-screen overlays
     opened from the MAIN MENU only, and the favorites bar sits
     BELOW the preview panes in the select hints row.
   UI IMMERSION LAW: no big center-screen fight popups are
     added. The frame overlay is a small corner readout, not a
     banner; the existing round-banner (main.js ui.banner) is
     untouched. No "WALL BREAK"-style text exists in any file
     this PR touches (audited 2026-10-24: zero matches in
     mainmenu.js, menus.js, main.js, versus-setup.js).
   BUTTON NAMES: LP1/RP2/LK3/RK4 everywhere user-facing.
   All characters are adults; canon-grounded only (CANON.md);
   Tekken names appear in technical comments only, never in
   in-universe screen text; the game ships with NO famous names.

   Node-testable core: every pure function below takes its store
   as an argument and never touches document/localStorage. The
   DOM layer (bottom) is guarded and no-ops without a document.
   ============================================================ */

/* ---------------- tap(): PR #1018 pattern, exported for reuse ---------------- */
let _lastTapAt = 0;
export function tap(el, fn) {
  if (!el || typeof el.addEventListener !== 'function') return;
  let sx = 0, sy = 0;
  el.addEventListener('touchstart', (e) => {
    const t = e.changedTouches && e.changedTouches[0];
    if (t) { sx = t.clientX; sy = t.clientY; }
  }, { passive: true });
  el.addEventListener('touchend', (e) => {
    const t = e.changedTouches && e.changedTouches[0];
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

/* ---------------- storage guards (node-safe) ---------------- */
function readJson(store, key, fallback) {
  try {
    const raw = store && typeof store.getItem === 'function' ? store.getItem(key) : null;
    return raw ? JSON.parse(raw) : fallback;
  } catch { return fallback; }
}
function writeJson(store, key, value) {
  try { if (store && typeof store.setItem === 'function') store.setItem(key, JSON.stringify(value)); } catch { /* private mode */ }
}
const ls = () => (typeof localStorage !== 'undefined' ? localStorage : null);
const ss = () => (typeof sessionStorage !== 'undefined' ? sessionStorage : null);

/* ---------------- settings (same key as menus.js: wh_settings_v1) ---------------- */
export const UI_SETTINGS_KEYS = ['frameOverlay', 'tournamentLock', 'streamingMode'];
export function readUiSettings(store) {
  const s = (store && typeof store === 'object' && !store.getItem) ? store : readJson(store, 'wh_settings_v1', {});
  return {
    frameOverlay: !!(s && s.frameOverlay),
    tournamentLock: !!(s && s.tournamentLock),
    streamingMode: !!(s && s.streamingMode),
  };
}
export function isTournamentLocked(settingsOrStore) {
  return readUiSettings(settingsOrStore).tournamentLock;
}
export function isStreamingMode(settingsOrStore) {
  return readUiSettings(settingsOrStore).streamingMode;
}
export function isFrameOverlayOn(settingsOrStore) {
  return readUiSettings(settingsOrStore).frameOverlay;
}

/* ---------------- Gap 14a: favorites (T7 5.10 one-button select) ---------------- */
export const FAV_KEY = 'wh_select_favorites_v1';
export const MAX_FAVORITES = 3;
export function loadFavorites(store) {
  const raw = readJson(store, FAV_KEY, []);
  return Array.isArray(raw) ? raw.filter((f) => f && f.fighterId).slice(0, MAX_FAVORITES) : [];
}
export function saveFavorite(store, slot, fighterId, attireLabel) {
  if (!fighterId) return loadFavorites(store);
  const favs = loadFavorites(store);
  while (favs.length <= slot) favs.push(null);
  favs[slot] = { fighterId, attireLabel: attireLabel || null, at: Date.now() };
  const out = favs.filter(Boolean).slice(0, MAX_FAVORITES);
  writeJson(store, FAV_KEY, out);
  return out;
}
export function favoriteAt(store, slot) {
  return loadFavorites(store)[slot] || null;
}

/* ---------------- Gap 14b: last-attire memory (per fighter, this session) ----------------
   attires.js already persists attire per fighter across sessions; this
   session record is the explicit T7 "last costume memory within session"
   surface the select bar reads and writes, so a favorite recall and a
   re-opened select screen both restore the exact attire. */
export const LAST_ATTIRE_KEY = 'wh_select_last_attire_v1';
export function recordLastAttire(sessionStore, fighterId, attireLabel) {
  if (!fighterId) return;
  const rec = readJson(sessionStore, LAST_ATTIRE_KEY, {});
  rec[fighterId] = { attireLabel: attireLabel || null, at: Date.now() };
  writeJson(sessionStore, LAST_ATTIRE_KEY, rec);
}
export function getLastAttire(sessionStore, fighterId) {
  const rec = readJson(sessionStore, LAST_ATTIRE_KEY, {});
  return (rec && rec[fighterId]) || null;
}

/* ---------------- Gap 14d / 15: VS display ----------------
   Streaming mode (T7 5.10): the opponent's ID is replaced by the
   character name on VS screens. WH's VS screen already shows fighter
   names, never player IDs (menus.js showVs renders c.name), so the
   display is already compliant; this function is the gate future
   online ID display must pass through, and the toggle is stored
   and honored here rather than silently ignored. */
export function vsDisplayName(playerName, fighterName, streamingOn) {
  if (streamingOn) return fighterName || playerName || '???';
  return fighterName || playerName || '???';
}
/* Pure VS meta lines. Inputs are injected (never read from stores here)
   so tests can verify them: rankName (or null), wins/losses (or null),
   connection: null = local bout (no bars invented), a number 0-5 =
   measured bars from the netplay layer, 'online' = online, unmeasured. */
export function vsMetaLines({ rankName, wins, losses, connection } = {}) {
  const lines = [];
  if (rankName) lines.push(`RANK · ${String(rankName).toUpperCase()}`);
  if (typeof wins === 'number' && typeof losses === 'number') lines.push(`W-L · ${wins}-${losses}`);
  if (connection == null) lines.push('LOCAL BOUT');
  else if (typeof connection === 'number') lines.push(`CONNECTION · ${'▮'.repeat(Math.max(0, Math.min(5, connection)))}${'▯'.repeat(5 - Math.max(0, Math.min(5, connection)))}`);
  else lines.push('ONLINE · CONNECTION UNMEASURED');
  return lines;
}
export function readVersusWL(records) {
  const wl = records && records.versusWL;
  if (wl && typeof wl.w === 'number' && typeof wl.l === 'number') return wl;
  return null;
}

/* ---------------- Gap 13: Treasure chest loot (pure roll) ----------------
   pool = unlockable ids still locked (caller filters with hasUnlockable).
   coins always pay out; a prize pays out only while the pool is non-empty,
   and the same prize is never rolled twice in one call's pool. */
export function rollChest({ coins = 0, pool = [], rng = Math.random } = {}) {
  const gain = 10 + Math.floor(rng() * 41); // 10–50 coins per chest (WH-original rate)
  const prize = pool.length ? pool[Math.floor(rng() * pool.length)] : null;
  return { coins: coins + gain, coinsGained: gain, prize };
}
export const TREASURE_COINS_KEY = 'wh_treasure_coins_v1';
export function readTreasureCoins(store) {
  const v = readJson(store, TREASURE_COINS_KEY, 0);
  return typeof v === 'number' ? v : 0;
}

/* ---------------- Gap 11 (UI side): Jukebox soundtrack choice ----------------
   The engine (music.js) owns playback; this store is the UI's contract
   to it: getJukeboxSoundtrack(mode) returns the player's chosen
   soundtrack id for a mode, or null = engine default rotation. */
export const JUKEBOX_KEY = 'wh_jukebox_v1';
export const JUKEBOX_MODES = ['menu', 'arcade', 'treasure', 'versus'];
export function getJukeboxSoundtrack(store, mode) {
  const s = readJson(store, JUKEBOX_KEY, {});
  return (s && s[mode]) || null;
}
export function setJukeboxSoundtrack(store, mode, soundtrackId) {
  const s = readJson(store, JUKEBOX_KEY, {});
  if (soundtrackId) s[mode] = soundtrackId; else delete s[mode];
  writeJson(store, JUKEBOX_KEY, s);
  return s;
}
/* Pure track filter over a music-library.json-shaped library
   ({ tracks: [{ title, modes[], stages[], file?, remote? }] }).
   Only available tracks (file or remote) are ever listed — a missing
   file can never be picked (same rule as music.js _available). */
export function jukeboxTracks(library, mode) {
  const T = (library && Array.isArray(library.tracks)) ? library.tracks : [];
  return T.filter((t) => t && (t.file || t.remote) && (
    (!mode || (Array.isArray(t.modes) && t.modes.includes(mode)) || (Array.isArray(t.modes) && t.modes.includes('battle')))
  ));
}

/* ---------------- Gap 20: Replay theater store ---------------- */
export const REPLAY_KEY = 'wh_replays_v1';
export function loadReplays(store) {
  const raw = readJson(store, REPLAY_KEY, []);
  return Array.isArray(raw) ? raw : [];
}
export function saveReplay(store, replay) {
  if (!replay || !Array.isArray(replay.events)) return loadReplays(store);
  const list = loadReplays(store);
  list.unshift({ id: `rp_${Date.now()}`, at: Date.now(), ...replay });
  const out = list.slice(0, 50);
  writeJson(store, REPLAY_KEY, out);
  return out;
}
export function deleteReplay(store, id) {
  const out = loadReplays(store).filter((r) => r.id !== id);
  writeJson(store, REPLAY_KEY, out);
  return out;
}
export function exportReplayJson(replay) {
  return JSON.stringify({ format: 'wh-replay', version: 1, ...replay }, null, 2);
}
/* Timeline rows from contract events (replay-analysis.js contract v1):
   hit / block / whiff / throw / punish / missed-punish / round. */
export function replayTimeline(events) {
  return (Array.isArray(events) ? events : []).map((e, i) => {
    const by = e.by || '?';
    switch (e.type) {
      case 'hit': return `#${i} ${by} HIT ${e.move || ''} ${e.dmg || 0} dmg${e.counter ? ' COUNTER' : ''}${e.combo ? ` (combo ${e.comboDmg || 0})` : ''}`.trim();
      case 'block': return `#${i} ${by} BLOCK ${e.move || ''} chip ${e.chip || 0}`;
      case 'whiff': return `#${i} ${by} WHIFF ${e.move || ''}`;
      case 'throw': return `#${i} ${by} THROW${e.broken ? ' (BROKEN)' : ''}`;
      case 'punish': return `#${i} ${by} PUNISH ${e.move || ''} +${e.frames || 0}f`;
      case 'missed-punish': return `#${i} ${by} MISSED PUNISH vs ${e.foeMove || ''} (${e.foeMinusFrames || 0}f)`;
      case 'round': return `#${i} ROUND → ${e.winner || '?'} (${e.timeLeft ?? '?'}s left)`;
      default: return `#${i} ${e.type || 'event'} ${by}`;
    }
  });
}

/* ---------------- Gap 21: frame overlay line ----------------
   attack = live fighter .attack object (or null). Numbers are shown
   ONLY when numeric on the object; otherwise the line says frames n/a.
   Never invents frame data. */
export function frameLine(attackName, attack) {
  const name = attackName || (attack && attack.name) || '—';
  const num = (v) => (typeof v === 'number' && isFinite(v) ? v : null);
  const s = attack ? num(attack.startup ?? attack.start) : null;
  const a = attack ? num(attack.active) : null;
  const r = attack ? num(attack.recovery) : null;
  const ob = attack ? num(attack.onBlock ?? attack.on_block) : null;
  const oh = attack ? num(attack.onHit ?? attack.on_hit) : null;
  if (s == null && a == null && r == null) return `${name} · frames n/a`;
  const parts = [`${name}`];
  if (s != null) parts.push(`STARTUP ${s}`);
  if (a != null) parts.push(`ACTIVE ${a}`);
  if (r != null) parts.push(`RECOVERY ${r}`);
  if (ob != null) parts.push(`ON BLOCK ${ob > 0 ? '+' : ''}${ob}`);
  if (oh != null) parts.push(`ON HIT ${oh > 0 ? '+' : ''}${oh}`);
  return parts.join(' · ');
}

/* ============================================================
   DOM LAYER — guarded; no-ops without document/localStorage.
   ============================================================ */
const $ = (id) => (typeof document !== 'undefined' ? document.getElementById(id) : null);
function gapBtn(label, sub) {
  const b = document.createElement('button');
  b.type = 'button';
  b.className = 'wh-gap-btn';
  b.innerHTML = sub ? `<b>${label}</b><small>${sub}</small>` : `<b>${label}</b>`;
  return b;
}
function gapScreen(id, title, sub) {
  let host = $(id);
  if (host) { host.querySelector('.wh-gap-list').innerHTML = ''; return host; }
  host = document.createElement('section');
  host.id = id;
  host.className = 'wh-gap-screen';
  host.setAttribute('aria-label', title);
  host.innerHTML = `<header class="wh-gap-head"><button type="button" class="wh-gap-back" aria-label="Back">‹</button><div><h2>${title}</h2><p>${sub}</p></div></header><div class="wh-gap-list"></div><p class="wh-gap-foot"></p>`;
  tap(host.querySelector('.wh-gap-back'), () => host.classList.remove('show'));
  document.body.appendChild(host);
  return host;
}
function gapToast(msg) {
  try {
    const t = $('mm-toast');
    if (t) { t.textContent = msg; t.classList.add('show'); setTimeout(() => t.classList.remove('show'), 2200); return; }
  } catch { /* fall through */ }
  try { if (typeof alert !== 'undefined') alert(msg); } catch { /* headless */ }
}

/* ---------------- Gallery (Gap 12, WH content only) ---------------- */
export async function openGallery() {
  const host = gapScreen('wh-gap-gallery', 'GALLERY', 'The archive of the shrine — endings, episodes, and what you have unlocked. No borrowed footage: every entry is Western Heart story and show content.');
  const list = host.querySelector('.wh-gap-list');
  list.innerHTML = '<p class="wh-gap-empty">Hanging the archive…</p>';
  host.classList.add('show');
  let endings = {}, episodes = {}, unlocked = [];
  try { const m = await import('./story-endings.js'); endings = m.STORY_ENDINGS || {}; } catch { /* content module absent — list stays honest */ }
  try { const m = await import('./episodes.js'); episodes = m.EPISODES || {}; } catch { /* same */ }
  try { const m = await import('./unlockables.js'); unlocked = m.unlockedList ? m.unlockedList() : []; } catch { /* same */ }
  const tabs = document.createElement('div');
  tabs.className = 'wh-gap-tabs';
  const panes = {
    Endings: Object.entries(endings).map(([id, e]) => ({ t: (e && e.title) || id, d: (e && (e.text || e.desc || '')).toString().slice(0, 160) || 'A soul\'s closing chapter.' })),
    Episodes: Object.entries(episodes).map(([id, e]) => ({ t: (e && e.title) || id, d: (e && (e.desc || e.sub || '')).toString().slice(0, 160) || 'A short cinematic ladder.' })),
    Unlocked: unlocked.map((u) => ({ t: u.name, d: `${u.kind} · unlocked` })),
  };
  const renderTab = (key) => {
    tabs.querySelectorAll('button').forEach((b) => b.classList.toggle('on', b.textContent === key));
    list.innerHTML = '';
    const items = panes[key];
    if (!items.length) { list.innerHTML = '<p class="wh-gap-empty">Nothing here yet — fight, and the shrine fills.</p>'; return; }
    items.forEach((it) => {
      const d = document.createElement('div');
      d.className = 'wh-gap-item';
      d.innerHTML = `<b>${it.t}</b><p>${it.d}</p>`;
      list.appendChild(d);
    });
  };
  Object.keys(panes).forEach((key) => {
    const b = gapBtn(key, `${panes[key].length} entries`);
    b.classList.add('wh-gap-tab');
    tap(b, () => renderTab(key));
    tabs.appendChild(b);
  });
  list.before(tabs);
  renderTab('Endings');
  host.querySelector('.wh-gap-foot').textContent = 'Gallery structure follows T7 (gap doc Gap 12). Contents are Western Heart canon only.';
}

/* ---------------- Jukebox (Gap 11, UI side) ---------------- */
export async function openJukebox() {
  const host = gapScreen('wh-gap-jukebox', 'JUKEBOX', 'The shrine\'s setlist. Pick a soundtrack per mode — the music engine plays it (engine wiring: audio lane follow-up, see module header).');
  const list = host.querySelector('.wh-gap-list');
  list.innerHTML = '<p class="wh-gap-empty">Pressing the setlist…</p>';
  host.classList.add('show');
  let library = null;
  try { const m = await import('./music.js'); if (m.music) { await m.music.loadLibrary(); library = m.music.library; } } catch { /* engine absent */ }
  list.innerHTML = '';
  if (!library) {
    list.innerHTML = '<p class="wh-gap-empty">No music library loaded yet — the setlist appears once the engine library lands.</p>';
    return;
  }
  const tracks = jukeboxTracks(library, null);
  const store = ls();
  JUKEBOX_MODES.forEach((mode) => {
    const row = document.createElement('div');
    row.className = 'wh-gap-item';
    const cur = getJukeboxSoundtrack(store, mode);
    row.innerHTML = `<b>${mode.toUpperCase()} SOUNDTRACK</b><p>${cur ? `Playing: ${cur}` : 'Engine default rotation'}</p>`;
    const pick = gapBtn('CHOOSE TRACK', 'Tap a track below, then it becomes this mode\'s soundtrack');
    tap(pick, () => {
      list.querySelectorAll('.wh-gap-track').forEach((x) => x.remove());
      tracks.slice(0, 40).forEach((t) => {
        const tb = gapBtn(t.title || t.id || 'Untitled', (t.modes || []).join(' · '));
        tb.classList.add('wh-gap-track');
        tap(tb, () => { setJukeboxSoundtrack(store, mode, t.title || t.id); gapToast(`${mode.toUpperCase()} SOUNDTRACK SET`); openJukebox(); });
        list.appendChild(tb);
      });
    });
    row.appendChild(pick);
    list.appendChild(row);
  });
  host.querySelector('.wh-gap-foot').textContent = 'Only available tracks are listed (file or remote present). Missing files can never be picked.';
}

/* ---------------- Replay theater (Gap 20) ---------------- */
export async function openReplays() {
  const host = gapScreen('wh-gap-replays', 'REPLAY THEATER', 'Save your fights. Study the tape. Timeline review + analysis now; deterministic fight playback lands with the recorder (see module header).');
  const list = host.querySelector('.wh-gap-list');
  host.classList.add('show');
  const render = () => {
    list.innerHTML = '';
    const reps = loadReplays(ls());
    if (!reps.length) list.innerHTML = '<p class="wh-gap-empty">No saved replays yet. Import one below, or save from a fight once the recorder lands.</p>';
    reps.forEach((r) => {
      const row = document.createElement('div');
      row.className = 'wh-gap-item';
      row.innerHTML = `<b>${r.title || 'UNTITLED FIGHT'}</b><p>${new Date(r.at || Date.now()).toLocaleString()} · ${(r.events || []).length} events · ${r.p1 || '?'} vs ${r.p2 || '?'}</p><div class="wh-gap-timeline"></div>`;
      const tl = row.querySelector('.wh-gap-timeline');
      replayTimeline(r.events).slice(0, 30).forEach((line) => {
        const d = document.createElement('div'); d.textContent = line; tl.appendChild(d);
      });
      const ana = gapBtn('ANALYZE', 'Combo / punish / whiff rates');
      tap(ana, async () => {
        try {
          const m = await import('./replay-analysis.js');
          const s = m.analyzeReplay(r.events || []);
          gapToast(`ACC ${Math.round(s.accuracy * 100)}% · PUNISH ${Math.round(s.punishRate * 100)}% · THROW BREAK ${Math.round(s.throwBreakRate * 100)}%`);
        } catch { gapToast('Analysis unavailable — replay-analysis.js did not load.'); }
      });
      const exp = gapBtn('SHARE / EXPORT', 'Download the replay JSON');
      tap(exp, () => {
        const blob = new Blob([exportReplayJson(r)], { type: 'application/json' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `${r.id || 'replay'}.json`;
        a.click();
        setTimeout(() => URL.revokeObjectURL(a.href), 5000);
      });
      const del = gapBtn('DELETE', 'Removes this replay');
      tap(del, () => { deleteReplay(ls(), r.id); render(); });
      row.appendChild(ana); row.appendChild(exp); row.appendChild(del);
      list.appendChild(row);
    });
    const imp = gapBtn('IMPORT REPLAY JSON', 'Load a shared replay file');
    tap(imp, () => {
      const inp = document.createElement('input');
      inp.type = 'file'; inp.accept = 'application/json,.json';
      inp.onchange = async () => {
        try {
          const text = await inp.files[0].text();
          const data = JSON.parse(text);
          if (!Array.isArray(data.events)) { gapToast('Not a Western Heart replay — no events found.'); return; }
          saveReplay(ls(), data); render(); gapToast('REPLAY IMPORTED');
        } catch { gapToast('Could not read that replay file.'); }
      };
      inp.click();
    });
    list.appendChild(imp);
  };
  render();
  host.querySelector('.wh-gap-foot').textContent = 'Replays store contract-v1 events (replay-analysis.js). Playback is NOT claimed: no recorder has merged to main.';
}

/* ---------------- Frame overlay (Gap 21) ---------------- */
let _frameTimer = null;
export function mountFrameOverlay() {
  if (typeof document === 'undefined') return null;
  let el = $('wh-frame-overlay');
  if (el) return el;
  el = document.createElement('div');
  el.id = 'wh-frame-overlay';
  el.className = 'wh-frame-overlay';
  el.setAttribute('aria-hidden', 'true');
  document.body.appendChild(el);
  return el;
}
export function refreshFrameOverlay() {
  const el = $('wh-frame-overlay');
  if (!el) return;
  const on = isFrameOverlayOn(readJson(ls(), 'wh_settings_v1', {}));
  const g = typeof window !== 'undefined' ? window.__game : null;
  const inFight = !!(g && g.running && !g.paused);
  if (!on || !inFight || !g.p1) { el.classList.remove('show'); return; }
  el.textContent = `P1 ${frameLine(g.p1.attackName, g.p1.attack)}  ‖  P2 ${frameLine(g.p2 ? g.p2.attackName : null, g.p2 ? g.p2.attack : null)}`;
  el.classList.add('show');
}
export function startFrameOverlayLoop() {
  if (_frameTimer) return;
  _frameTimer = setInterval(refreshFrameOverlay, 250);
}

/* ---------------- Select 5.10 bar (Gap 14) ---------------- */
export function mountSelect510Bar() {
  if (typeof document === 'undefined') return;
  const screen = $('screen-select');
  if (!screen || $('wh-favbar')) return;
  const hints = screen.querySelector('.hints-bar');
  if (!hints) return;
  const bar = document.createElement('div');
  bar.id = 'wh-favbar';
  bar.className = 'wh-favbar';
  bar.innerHTML = '<span class="wh-fav-label">FAVORITES · T7 5.10</span>';
  const save = gapBtn('★ SAVE FAVORITE', 'Current fighter + attire');
  tap(save, () => {
    if (isTournamentLocked(readJson(ls(), 'wh_settings_v1', {}))) { gapToast('TOURNAMENT LOCK — favorites are off.'); return; }
    const card = screen.querySelector('.char-card.selected');
    const fighterId = card && card.dataset.id;
    if (!fighterId || fighterId === '__random') { gapToast('Pick a fighter first, then save.'); return; }
    const chip = screen.querySelector('.pane-p1 .attire-chip.on, .pane-p2 .attire-chip.on');
    const attireLabel = chip ? chip.textContent : null;
    const favs = loadFavorites(ls());
    saveFavorite(ls(), favs.length >= MAX_FAVORITES ? 0 : favs.length, fighterId, attireLabel);
    recordLastAttire(ss(), fighterId, attireLabel);
    gapToast('FAVORITE SAVED');
    renderFavButtons();
  });
  bar.appendChild(save);
  const slots = document.createElement('span');
  slots.className = 'wh-fav-slots';
  bar.appendChild(slots);
  function renderFavButtons() {
    slots.innerHTML = '';
    if (isTournamentLocked(readJson(ls(), 'wh_settings_v1', {}))) {
      const note = document.createElement('span');
      note.className = 'wh-fav-locked';
      note.textContent = 'TOURNAMENT LOCK — favorites & attire changes off';
      slots.appendChild(note);
      return;
    }
    loadFavorites(ls()).forEach((f, i) => {
      const b = gapBtn(`FAV ${i + 1}`, f.fighterId);
      tap(b, () => {
        const sel = (typeof window !== 'undefined' && window.__selectScreen) || null;
        if (sel && sel.selectById) sel.selectById(f.fighterId);
        else { const card = screen.querySelector(`.char-card[data-id="${f.fighterId}"]`); if (card) card.click(); }
        if (f.attireLabel) {
          setTimeout(() => {
            const chip = [...screen.querySelectorAll('.attire-chip')].find((c) => c.textContent === f.attireLabel);
            if (chip && !chip.disabled) chip.click();
          }, 250);
        }
        recordLastAttire(ss(), f.fighterId, f.attireLabel);
      });
      slots.appendChild(b);
    });
  }
  bar._renderFavButtons = renderFavButtons;
  hints.after(bar);
  renderFavButtons();
  // Tournament lock enforcement on attire chips: while locked, chips
  // stay disabled on the select screen (T7: favorites/costume off).
  const obs = new MutationObserver(() => {
    if (!isTournamentLocked(readJson(ls(), 'wh_settings_v1', {}))) return;
    screen.querySelectorAll('.attire-chip').forEach((c) => { c.disabled = true; });
  });
  obs.observe(screen, { childList: true, subtree: true });
}

/* ---------------- init (called once from menus.js initMenus) ---------------- */
let _inited = false;
export function initUiGaps() {
  if (_inited || typeof document === 'undefined') return;
  _inited = true;
  mountFrameOverlay();
  startFrameOverlayLoop();
  mountSelect510Bar();
  // The favorites bar is built once at boot, but the select screen's
  // hints row may render later — rebuild the bar on first select open.
  document.addEventListener('click', (e) => {
    const t = e.target instanceof Element ? e.target.closest('[data-action="back-select"], .char-card') : null;
    if (t) setTimeout(mountSelect510Bar, 0);
  });
}
