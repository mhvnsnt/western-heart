/* ============================================================
   WESTERN HEART — Jukebox pool selection (2026-10-24)
   T7 Jukebox rule, WH shape: the player picks a soundtrack pool in
   Settings (menus.js JUKEBOX row, stored in wh_settings_v1.jukebox).
   'default' delegates to music.js rotation untouched. A named pool
   wins over stage rotation for battle music only — menu modes are
   never overridden.

   Coordination (no clobber): this module does NOT edit
   game/data/music-library.json (the music-rotation lane, PR #1030,
   owns it). Pools are defined once in game/data/jukebox-pools.json
   and library tracks are read at runtime, so either lane can land
   first: pre-#1030, a nosferatu pool with no library tracks simply
   delegates; post-#1030 it resolves to the nos-t* tracks.

   Cape Jones pool: main track leads each rotation cycle (Ghost Surf
   Rock), then the battle pool interchanges around it.
   Pending pieces are flagged in jukebox-pools.json, never faked:
   the Ghost Surf Rock file (pending-file) and the Cape Jones arena
   stage (pending-stage). Until the file lands, music.js falls back
   to its procedural loop for that track — never silence, never a
   crash. Until the arena lands, the pool is still selectable in
   Settings, so it is playable/testable now.

   No top-level DOM/window/fetch work: importing this module is
   side-effect free, so node tests can import it directly.
   ============================================================ */
const SETTINGS_KEY = 'wh_settings_v1';
const STATE_KEY = 'wh_jukebox_v1';

export function getJukeboxPoolId() {
  try {
    const raw = (typeof localStorage !== 'undefined')
      ? localStorage.getItem(SETTINGS_KEY) : null;
    const s = raw ? JSON.parse(raw) : {};
    return (s && typeof s.jukebox === 'string') ? s.jukebox : 'default';
  } catch (e) { return 'default'; }
}

export function setJukeboxPoolId(id) {
  try {
    const raw = (typeof localStorage !== 'undefined')
      ? localStorage.getItem(SETTINGS_KEY) : null;
    const s = raw ? JSON.parse(raw) : {};
    s.jukebox = id;
    if (typeof localStorage !== 'undefined') localStorage.setItem(SETTINGS_KEY, JSON.stringify(s));
  } catch (e) { /* private mode: in-memory only */ }
  return id;
}

function loadState() {
  try {
    const raw = (typeof localStorage !== 'undefined')
      ? localStorage.getItem(STATE_KEY) : null;
    return raw ? JSON.parse(raw) : {};
  } catch (e) { return {}; }
}

function saveState(st) {
  try {
    if (typeof localStorage !== 'undefined') localStorage.setItem(STATE_KEY, JSON.stringify(st));
  } catch (e) { /* private mode */ }
}

/* Pure pool resolution (unit-tested, no I/O).
   pools: parsed jukebox-pools.json. libraryTracks: music.library.tracks.
   state: loadState() object; mutated + returned so callers can persist it.
   Returns a track object, or null = delegate to music.js rotation.
   Track objects for library ids are the library's own objects (same shape
   music._playTrack expects); the Cape Jones main track is the pools file's
   own object (same fields: id/file/remote/loop/gain/modes/stages). */
export function resolveJukeboxTrack({ poolId, stage, libraryTracks, pools, state }) {
  const st = state || {};
  const list = (pools && pools.pools) || [];
  const pool = list.find((p) => p.id === poolId);
  if (!pool || poolId === 'default') return null;
  const tracks = Array.isArray(libraryTracks) ? libraryTracks : [];
  const available = (t) => t && (t.file || t.remote);
  if (pool.id === 'cape-jones') {
    // Rotation cycle = [main, ...battle pool], repeating: the main track
    // leads each cycle and the battle tracks interchange around it.
    // State is keyed per stage so two stages never share a counter.
    const key = `cape:${stage || 'any'}`;
    const rest = tracks.filter(available).filter((t) => t.id !== pool.mainTrack.id);
    const cycle = [pool.mainTrack, ...rest];
    const idx = (st[key] == null) ? 0 : (st[key] % cycle.length);
    st[key] = (idx + 1) % cycle.length;
    return cycle[idx];
  }
  if (pool.id === 'nosferatu') {
    const ids = pool.trackIds || [];
    const ordered = ids.map((id) => tracks.find((t) => t.id === id)).filter(available);
    if (!ordered.length) return null; // pre-#1030 library: delegate, don't fail
    const idx = ((st.nos || 0) % ordered.length + ordered.length) % ordered.length;
    st.nos = (idx + 1) % ordered.length;
    return ordered[idx];
  }
  return null;
}

/* Runtime install (browser only): wrap the music engine's rotation pick
   so a named pool wins for battle music. Installed once, from menus.js
   at boot; every step is guarded so a failure leaves stage rotation. */
let _installed = false;
export async function installJukebox() {
  if (_installed) return true;
  _installed = true;
  try {
    const res = await fetch('data/jukebox-pools.json', { cache: 'force-cache' });
    if (!res.ok) return false;
    const pools = await res.json();
    const { music } = await import('./music.js');
    if (!music) return false;
    const origRotation = (typeof music.pickRotationTrack === 'function')
      ? music.pickRotationTrack.bind(music) : null;
    const origPick = music.pickTrack.bind(music);
    const pick = (opts = {}) => {
      const poolId = getJukeboxPoolId();
      if (poolId === 'default') return null;
      const st = loadState();
      const t = resolveJukeboxTrack({
        poolId, stage: opts.stage,
        libraryTracks: (music.library && music.library.tracks) || [],
        pools, state: st,
      });
      saveState(st);
      return t;
    };
    if (origRotation) {
      music.pickRotationTrack = (opts = {}) => pick(opts) || origRotation(opts);
    }
    // Pre-#1030 music.js has no pickRotationTrack: playBattle uses
    // pickTrack, so wrap that too — battle mode only, menus untouched.
    const prevPick = music.pickTrack;
    music.pickTrack = (opts = {}) => {
      if (opts.mode && opts.mode !== 'battle') return prevPick(opts);
      if (!origRotation) {
        const t = pick(opts);
        if (t) return t;
      }
      return prevPick(opts);
    };
    void origPick;
    return true;
  } catch (e) { return false; }
}
