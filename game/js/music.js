/* ============================================================
   WESTERN HEART — Music Engine (file-based BGM system)
   Drives game/assets/music/ through game/data/music-library.json.

   What it pulls from the teardown games' music systems:
   • Tekken convention — stage BGM POOLS rotate (Tekken jukebox rule:
     tracks are assigned by stage / mode / mood tags and the pool rotates
     per fight), separate themes for title / character-select / versus /
     results; music keeps playing across rounds and only changes on
     screen/stage change. T7 match-point rule: the deciding round
     crossfades to the current track's finalRound variant when one is
     assigned (see playFinalRound). Ep1 fight cue plays as an ordered
     sequence (see playSequence + library sequences).
   • Crossfade transitions on every switch (no hard cuts).
   • Battle intensity scaling — Tekken raises the mix as the fight
     heats up (final round, low HP); we do it with a lowpass +
     gain ramp, and optionally per-track STEMS (layers faded in).
   • Jukebox-style assignment — tracks are picked by stage / mode /
     mood TAGS in the library JSON, so swapping a song never
     touches code (see docs/MUSIC-PIPELINE.md).
   • Voice ducking — the announcer/voice lines dip the music ~8 dB
     while they speak (hooked via voice.onSpeech).

   Fallback: if the library or a track file is missing, the engine
   delegates to the procedural battle loop in audio.js, so the game
   never goes silent.

   Crowd reactions: deliberately NOT built (owner 2026-10-22 — our
   stages have no crowds; reactions ship with the crowd system).
   ============================================================ */
import { audio } from './audio.js';

const LIB_URL = 'data/music-library.json';
const XFADE_MS = 1600;
const DUCK_DB = -8;

class MusicEngine {
  constructor() {
    this.library = null;          // parsed music-library.json
    this.buffers = new Map();     // url -> AudioBuffer
    this._loading = new Map();    // url -> in-flight promise
    this.current = null;          // { track, src, gain, filter, stems[] }
    this.intensity = 0.55;
    this.enabled = true;
    this._duckGain = null;        // created on unlock, sits before musicGain
    this._ducked = false;
    this._procedural = false;     // true while the audio.js fallback loop runs
    this._boundVoice = false;
    this._rotation = {};          // pool key -> next index (persisted)
    this._rotationLoaded = false;
    this._seq = null;             // active playSequence state
    this._lastStage = null;       // stage of the last battle (sequence resume)
    this._afterVictory = null;    // menu mode to play after the victory jingle
  }

  /* Must be called from a user gesture (mobile autoplay policy).
     Safe to call repeatedly; headless/test tolerant. */
  unlock() {
    try { if (typeof audio.unlock === 'function') audio.unlock(); } catch (e) { /* no window */ }
    try {
      if (audio.ctx && !this._duckGain) {
        this._duckGain = audio.ctx.createGain();
        this._duckGain.gain.value = 1;
        this._duckGain.connect(audio.musicGain);
      }
    } catch (e) { /* headless */ }
    this._bindVoice();
  }

  /* Duck the music while the announcer / voice lines speak. Lazy so
     music.js never hard-depends on voice.js at import time. */
  _bindVoice() {
    if (this._boundVoice) return;
    this._boundVoice = true;
    try {
      import('./voice.js').then(m => {
        if (m && m.voice) m.voice.onSpeech = (active) => this.duck(active);
      }).catch(() => {});
    } catch (e) { /* voice module unavailable */ }
  }

  setEnabled(on) { this.enabled = !!on; }

  /* ---- library ---- */

  async loadLibrary() {
    if (this.library) return this.library;
    try {
      const res = await fetch(LIB_URL, { cache: 'force-cache' });
      if (res.ok) this.library = await res.json();
    } catch (e) { /* offline / not authored yet -> fallback path */ }
    return this.library;
  }

  /* Tekken jukebox rule: stage assignment wins, then mode, then mood,
     then the first battle-tagged track. Never throws, never null —
     worst case it returns null and the caller falls back. */
  pickTrack({ stage, mode, mood } = {}) {
    const lib = this.library;
    if (!lib || !Array.isArray(lib.tracks) || !lib.tracks.length) return null;
    /* First-match picks go through the same availability rule as the
       rotation pools: a pending-download slot is NEVER picked, even
       when it is the first stage/mode match. (Rotation pools already
       filtered this way; pickTrack did not — a latent pick of a
       file:null slot that only the procedural fallback saved.) */
    const T = lib.tracks.filter(t => this._available(t));
    if (stage) {
      const hit = T.find(t => Array.isArray(t.stages) && t.stages.includes(stage));
      if (hit) return hit;
    }
    if (mode) {
      const hit = T.find(t => Array.isArray(t.modes) && t.modes.includes(mode));
      if (hit) return hit;
    }
    if (mood) {
      const hit = T.find(t => Array.isArray(t.moods) && t.moods.includes(mood));
      if (hit) return hit;
    }
    return T.find(t => Array.isArray(t.modes) && t.modes.includes('battle')) || T[0];
  }

  /* ---- rotation pools (Tekken jukebox rule, extended) ----
     A pool is every AVAILABLE track (file or remote present) in library
     order for the requested mode. For battles, tracks tagged with the
     stage come first, then the rest of the battle pool — so a stage's
     own theme still opens its rotation, and the soundtrack pool keeps
     every stage rotating. Pending entries (file:null, remote:null —
     e.g. Tekken audio not yet downloaded) are never picked, so a missing
     file can never silence or break a fight: the pool just rotates over
     what exists, and _fallback() covers an empty pool. Never throws. */
  /* A track is available only with a file/remote AND a status other
     than 'pending-download' (the 5 Tekken data-only slots). 'pending-file'
     tracks (file field set, bytes not yet in the repo — Cape Jones MP3s)
     stay available: a failed fetch falls back to the procedural loop. */
  _available(t) { return !!(t && (t.file || t.remote) && t.status !== 'pending-download'); }

  _poolFor({ stage, mode } = {}) {
    const lib = this.library;
    if (!lib || !Array.isArray(lib.tracks)) return [];
    const avail = lib.tracks.filter(t => this._available(t));
    if (mode && mode !== 'battle') {
      return avail.filter(t => Array.isArray(t.modes) && t.modes.includes(mode));
    }
    const battle = avail.filter(t => Array.isArray(t.modes) && t.modes.includes('battle'));
    if (!stage) return battle;
    const tagged = battle.filter(t => Array.isArray(t.stages) && t.stages.includes(stage));
    const rest = battle.filter(t => !(Array.isArray(t.stages) && t.stages.includes(stage)));
    return [...tagged, ...rest];
  }

  _loadRotation() {
    if (this._rotationLoaded) return;
    this._rotationLoaded = true;
    try {
      const raw = localStorage.getItem('wh-music-rotation');
      if (raw) this._rotation = JSON.parse(raw) || {};
    } catch (e) { /* headless / private mode: in-memory rotation only */ }
  }

  _saveRotation() {
    try { localStorage.setItem('wh-music-rotation', JSON.stringify(this._rotation)); } catch (e) {}
  }

  _nextRotation(key, pool) {
    if (!pool.length) return null;
    if (this.library && this.library.rotation && this.library.rotation.mode === 'shuffle') {
      let pick = pool[Math.floor(Math.random() * pool.length)];
      if (pool.length > 1 && this._rotation[key] != null) {
        const last = pool[this._rotation[key]];
        if (pick === last) pick = pool[(this._rotation[key] + 1) % pool.length];
      }
      this._rotation[key] = pool.indexOf(pick);
      this._saveRotation();
      return pick;
    }
    const idx = ((this._rotation[key] || 0) % pool.length + pool.length) % pool.length;
    this._rotation[key] = (idx + 1) % pool.length;
    this._saveRotation();
    return pool[idx];
  }

  /* Rotation pick: pool of >1 rotates (and persists across sessions);
     pool of 1 plays it; empty pool falls back to pickTrack (which may
     still return null -> caller falls back to procedural). */
  pickRotationTrack({ stage, mode } = {}) {
    this._loadRotation();
    const pool = this._poolFor({ stage, mode });
    if (!pool.length) return this.pickTrack({ stage, mode });
    const key = stage ? `stage:${stage}` : `mode:${mode || 'battle'}`;
    return this._nextRotation(key, pool);
  }

  /* ---- Jukebox UI choices (PR #1056 contract, engine side) ----
     The UI lane (game/js/ui-gaps.js, PR #1056) stores one soundtrack
     choice per UI mode in localStorage key wh_jukebox_v1:
       { menu: <track title or id>, arcade: ..., treasure: ..., versus: ... }
     or null = engine default rotation. This engine reads that SAME key
     directly — no import of ui-gaps.js, so this file works whether
     #1056 has landed or not, and there is no import cycle (ui-gaps.js
     itself imports music.js). The stored value is a track title, with
     id as fallback (see ui-gaps.js setJukeboxSoundtrack), so resolution
     tries exact id first, then exact title. If an id matches at all,
     the title fallback is NOT tried: a stored choice naming a
     pending-download track must fall back to rotation, never play a
     different track that happens to share the title. A choice that
     does not resolve, or that resolves to a pending-download track,
     returns null and the caller falls back to rotation — a missing
     file can never silence or break a fight, and a stale choice
     (track removed from the library) degrades to rotation, not
     to silence. UI-mode mapping: playMenu title/select/online use
     the 'menu' choice, playMenu versus uses the 'versus' choice,
     credits/results have no owning UI mode and stay on rotation;
     playBattle uses opts.uiMode when the caller knows it
     ('arcade' | 'versus' | 'treasure'), else the arcade choice if
     set, else the versus choice (bare startFight calls carry no
     mode; arcade is the default fight path). 'treasure' has no music
     call site yet, so a stored treasure choice is read but currently
     unplayed — recorded, not faked. The victory jingle is untouched. */
  _readJukeboxChoice(uiMode) {
    try {
      const raw = localStorage.getItem('wh_jukebox_v1');
      if (!raw) return null;
      const s = JSON.parse(raw);
      const v = s && s[uiMode];
      return (typeof v === 'string' && v) ? v : null;
    } catch (e) { return null; }
  }

  _resolveJukeboxChoice(choice) {
    const lib = this.library;
    if (!lib || !Array.isArray(lib.tracks) || !choice) return null;
    const byId = lib.tracks.find(t => t.id === choice);
    if (byId) return this._available(byId) ? byId : null;
    const byTitle = lib.tracks.find(t => t.title === choice);
    return (byTitle && this._available(byTitle)) ? byTitle : null;
  }

  _jukeboxBattleTrack(uiMode) {
    const modes = uiMode ? [uiMode] : ['arcade', 'versus'];
    for (const mm of modes) {
      const t = this._resolveJukeboxChoice(this._readJukeboxChoice(mm));
      if (t) return t;
    }
    return null;
  }

  /* ---- buffers (local file first, remote URL fallback) ---- */

  async _bufferFor(track) {
    if (!track || !audio.ctx || !audio.ctx.decodeAudioData) return null;
    const urls = [track.file, track.remote].filter(Boolean);
    for (const u of urls) {
      if (this.buffers.has(u)) return this.buffers.get(u);
      if (this._loading.has(u)) {
        const b = await this._loading.get(u);
        if (b) return b;
        continue;
      }
      const p = (async () => {
        try {
          const res = await fetch(u, { cache: 'force-cache' });
          if (!res.ok) return null;
          const raw = await res.arrayBuffer();
          const buf = await audio.ctx.decodeAudioData(raw);
          this.buffers.set(u, buf);
          return buf;
        } catch (e) { return null; }
        finally { this._loading.delete(u); }
      })();
      this._loading.set(u, p);
      const buf = await p;
      if (buf) return buf;
    }
    return null;
  }

  /* ---- transport ---- */

  _filterFor(intensity) {
    // 700 Hz (muffled, low stakes) -> 16 kHz (full-bore final round)
    return 700 + intensity * 15300;
  }

  _gainFor(intensity) { return 0.65 + intensity * 0.35; }

  _duckTarget() {
    return this._ducked ? Math.pow(10, DUCK_DB / 20) : 1;
  }

  async _playTrack(track, { fadeMs = XFADE_MS, once = false } = {}) {
    if (!this.enabled) return;
    const buf = await this._bufferFor(track);
    if (!buf || !audio.ctx || !audio.enabled) { this._fallback(); return; }
    this._procedural = false;
    const t = audio.ctx.currentTime;
    const fadeS = fadeMs / 1000;

    // crossfade the old track out
    const old = this.current;
    if (old) {
      try {
        old.gain.gain.cancelScheduledValues(t);
        old.gain.gain.setValueAtTime(Math.max(0.0001, old.gain.gain.value), t);
        old.gain.gain.linearRampToValueAtTime(0.0001, t + fadeS);
        const o = old;
        setTimeout(() => { try { o.src.onended = null; } catch (e) {} try { o.src.stop(); } catch (e) {} try { o.gain.disconnect(); } catch (e) {} }, fadeMs + 120);
      } catch (e) { /* already stopped */ }
    }

    const src = audio.ctx.createBufferSource();
    src.buffer = buf;
    src.loop = !once && track.loop !== false;
    if (track.loopStart != null) src.loopStart = track.loopStart;
    if (track.loopEnd != null) src.loopEnd = track.loopEnd;
    const filt = audio.ctx.createBiquadFilter();
    filt.type = 'lowpass';
    filt.frequency.value = this._filterFor(this.intensity);
    const g = audio.ctx.createGain();
    g.gain.value = 0.0001;
    src.connect(filt); filt.connect(g);
    g.connect(this._duckGain || audio.musicGain);
    try { src.start(); } catch (e) { this._fallback(); return; }
    // Sequence advance + after-victory chaining ride on the natural track
    // end. Looping tracks never end, so this only fires for once/sequence
    // tracks. (Crossfaded-out sources get onended cleared above, so a
    // crossfade can never falsely advance a sequence.)
    if (once || this._seq) {
      try {
        src.onended = () => {
          if (this._seq) { this._playSequenceNext(); return; }
          if (this._afterVictory) {
            const m = this._afterVictory; this._afterVictory = null; this.playMenu(m);
          }
        };
      } catch (e) {}
    }
    const peak = (track.gain != null ? track.gain : 1) * this._gainFor(this.intensity);
    g.gain.linearRampToValueAtTime(Math.max(0.0001, peak), t + fadeS);
    this.current = { track, src, gain: g, filter: filt };
    this._applyDuck();
    console.info(`[WH music] now playing: ${track.title} — ${track.artist || 'unknown'} (${track.license || 'see library'})`);
  }

  /* Procedural fallback: the taiko/shakuhachi loop in audio.js. The
     game is never silent just because a file is missing. */
  _fallback() {
    if (this._procedural) return;
    this._procedural = true;
    try { audio.startMusic(); } catch (e) {}
    console.info('[WH music] file track unavailable — procedural fallback loop');
  }

  /* ---- public API ---- */

  /* Battle: rotating stage pool (Tekken jukebox rule), intensity reset.
     The pool advances per fight and persists across sessions, so the same
     stage does not repeat the same track every fight. */
  async playBattle(stageId, opts = {}) {
    await this.loadLibrary();
    this._seq = null;
    if (stageId) this._lastStage = stageId;
    const chosen = this._jukeboxBattleTrack(opts.uiMode);
    const track = chosen || this.pickRotationTrack({ stage: stageId, mode: 'battle' });
    this.setIntensity(0.55);
    if (track) await this._playTrack(track);
    else this._fallback();
  }

  /* Menus: 'title' | 'select' | 'versus' | 'results' | 'credits' |
     'online'. Menu pools rotate too, keyed by mode. */
  async playMenu(which) {
    await this.loadLibrary();
    this._seq = null;
    const mode = which === 'title' ? 'title' : which;
    const uiMode = (which === 'versus') ? 'versus'
      : (['title', 'select', 'online'].includes(which) ? 'menu' : null);
    const chosen = uiMode ? this._resolveJukeboxChoice(this._readJukeboxChoice(uiMode)) : null;
    const track = chosen || this.pickRotationTrack({ mode });
    this.setIntensity(0.35);
    if (track) await this._playTrack(track);
    else this._fallback();
  }

  /* Victory jingle: one-shot, no loop. When it ends, the results
     theme takes over (chained via onended, not a timer). */
  async playVictory() {
    await this.loadLibrary();
    this._seq = null;
    const track = this.pickTrack({ mode: 'victory' });
    this.setIntensity(0.4);
    if (track) {
      this._afterVictory = 'results';
      await this._playTrack(track, { once: true });
    }
  }

  /* T7 match-point rule: when the deciding round starts, crossfade to the
     current track's finalRound variant (if it names one and it's
     available). No-op otherwise — the base track keeps playing under
     the intensity lift. Returns true when a variant swap happened. */
  async playFinalRound() {
    await this.loadLibrary();
    const cur = this.current && this.current.track;
    if (!cur || !cur.finalRound) return false;
    const lib = this.library;
    const target = lib && lib.tracks.find(t => t.id === cur.finalRound && this._available(t));
    if (!target) return false;
    await this._playTrack(target);
    return true;
  }

  /* Ordered cue sequence (Ep1 fight arc): plays the named library tracks
     in order, one shot each, advancing on natural track end. When the
     sequence ends, battle rotation resumes on the last battle stage. */
  async playSequence(name) {
    await this.loadLibrary();
    const seq = this.library && this.library.sequences && this.library.sequences[name];
    if (!seq || !seq.length) return false;
    const tracks = seq.map(id => this.library.tracks.find(t => t.id === id && this._available(t))).filter(Boolean);
    if (!tracks.length) return false;
    this._seq = { list: tracks, i: 0 };
    await this._playTrack(tracks[0], { once: true });
    return true;
  }

  async _playSequenceNext() {
    const sq = this._seq;
    if (!sq) return;
    sq.i++;
    if (sq.i >= sq.list.length) {
      this._seq = null;
      if (this._lastStage) await this.playBattle(this._lastStage);
      return;
    }
    await this._playTrack(sq.list[sq.i], { once: true });
  }

  /* Battle intensity 0..1 — ramps the lowpass + gain, Tekken-style.
     Call sites: round start 0.55, FIGHT 0.7, final round 0.85,
     KO/time-up 0.3, fighter under 25% HP 1.0. Never throws. */
  setIntensity(x) {
    this.intensity = Math.max(0, Math.min(1, x == null ? 0.55 : x));
    try {
      if (this.current && audio.ctx && audio.enabled) {
        const t = audio.ctx.currentTime;
        this.current.filter.frequency.cancelScheduledValues(t);
        this.current.filter.frequency.setValueAtTime(this.current.filter.frequency.value, t);
        this.current.filter.frequency.linearRampToValueAtTime(this._filterFor(this.intensity), t + 0.8);
        this.current.gain.gain.cancelScheduledValues(t);
        this.current.gain.gain.setValueAtTime(Math.max(0.0001, this.current.gain.gain.value), t);
        const peak = (this.current.track.gain != null ? this.current.track.gain : 1) * this._gainFor(this.intensity);
        this.current.gain.gain.linearRampToValueAtTime(Math.max(0.0001, peak), t + 0.8);
      }
    } catch (e) { /* headless / not playing */ }
  }

  /* Duck under voice (driven by voice.onSpeech). */
  duck(on) {
    this._ducked = !!on;
    this._applyDuck();
  }

  _applyDuck() {
    try {
      if (this._duckGain && audio.ctx) {
        const t = audio.ctx.currentTime;
        this._duckGain.gain.cancelScheduledValues(t);
        this._duckGain.gain.setValueAtTime(this._duckGain.gain.value, t);
        this._duckGain.gain.linearRampToValueAtTime(this._duckTarget(), t + 0.25);
      }
    } catch (e) { /* headless */ }
  }

  /* Fade out and stop everything. */
  stop() {
    this._seq = null;
    this._afterVictory = null;
    if (this._procedural) {
      try { audio.stopMusic(); } catch (e) {}
      this._procedural = false;
    }
    const cur = this.current;
    this.current = null;
    try {
      if (cur && audio.ctx) {
        const t = audio.ctx.currentTime;
        cur.gain.gain.cancelScheduledValues(t);
        cur.gain.gain.setValueAtTime(Math.max(0.0001, cur.gain.gain.value), t);
        cur.gain.gain.linearRampToValueAtTime(0.0001, t + 0.8);
        setTimeout(() => { try { cur.src.stop(); } catch (e) {} }, 950);
      }
    } catch (e) { /* headless */ }
  }
}

export const music = new MusicEngine();
