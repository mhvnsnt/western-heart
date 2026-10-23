/* ============================================================
   WESTERN HEART — Music Engine (file-based BGM system)
   Drives game/assets/music/ through game/data/music-library.json.

   What it pulls from the teardown games' music systems:
   • Tekken convention — one BGM per stage, separate themes for
     title / character-select / versus / results; music keeps
     playing across rounds and only changes on screen/stage change.
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
    const T = lib.tracks;
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
        setTimeout(() => { try { o.src.stop(); } catch (e) {} try { o.gain.disconnect(); } catch (e) {} }, fadeMs + 120);
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

  /* Battle: stage-tagged track (Tekken rule), intensity reset. */
  async playBattle(stageId) {
    await this.loadLibrary();
    const track = this.pickTrack({ stage: stageId, mode: 'battle' });
    this.setIntensity(0.55);
    if (track) await this._playTrack(track);
    else this._fallback();
  }

  /* Menus: 'title' | 'select' | 'versus' | 'results' | 'credits'. */
  async playMenu(which) {
    await this.loadLibrary();
    const track = this.pickTrack({ mode: which === 'title' ? 'title' : which });
    this.setIntensity(0.35);
    if (track) await this._playTrack(track);
    else this._fallback();
  }

  /* Victory jingle: one-shot, no loop. */
  async playVictory() {
    await this.loadLibrary();
    const track = this.pickTrack({ mode: 'victory' });
    this.setIntensity(0.4);
    if (track) await this._playTrack(track, { once: true });
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
