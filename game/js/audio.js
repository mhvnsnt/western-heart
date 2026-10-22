/* ============================================================
   WESTERN HEART — Audio Engine (fully procedural, Web Audio API)
   No external files: impacts, whooshes, K.O. stinger and the
   battle loop are all synthesized at runtime.
   Battle loop leans shrine-of-the-blade: deep taiko-ish drums
   under a breathy shakuhachi-flavoured lead line.
   ============================================================ */

class AudioEngine {
  constructor() {
    this.ctx = null;
    this.master = null;
    this.musicGain = null;
    this.sfxGain = null;
    this.enabled = false;
    this._musicTimer = null;
    this._musicStep = 0;
  }

  /* Must be called from a user gesture (mobile autoplay policy). */
  unlock() {
    if (this.ctx) {
      if (this.ctx.state === 'suspended') this.ctx.resume();
      return;
    }
    const AC = window.AudioContext || window.webkitAudioContext;
    this.ctx = new AC();
    this.master = this.ctx.createGain();
    this.master.gain.value = 0.9;
    this.master.connect(this.ctx.destination);

    this.musicGain = this.ctx.createGain();
    this.musicGain.gain.value = 0.28;
    this.musicGain.connect(this.master);

    this.sfxGain = this.ctx.createGain();
    this.sfxGain.gain.value = 0.85;
    this.sfxGain.connect(this.master);

    this.enabled = true;
  }

  get now() { return this.ctx ? this.ctx.currentTime : 0; }

  _osc(type, freq, t0, t1, gain, dest) {
    if (!this.enabled) return;
    const o = this.ctx.createOscillator();
    const g = this.ctx.createGain();
    o.type = type;
    o.frequency.setValueAtTime(freq, t0);
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.exponentialRampToValueAtTime(gain, t0 + 0.006);
    g.gain.exponentialRampToValueAtTime(0.0001, t1);
    o.connect(g); g.connect(dest || this.sfxGain);
    o.start(t0); o.stop(t1 + 0.02);
    return o;
  }

  _noise(t0, dur, gain, filterFreq, dest) {
    if (!this.enabled) return;
    const len = Math.floor(this.ctx.sampleRate * dur);
    const buf = this.ctx.createBuffer(1, len, this.ctx.sampleRate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < len; i++) data[i] = (Math.random() * 2 - 1) * (1 - i / len);
    const src = this.ctx.createBufferSource();
    src.buffer = buf;
    const bp = this.ctx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.frequency.value = filterFreq || 1200;
    bp.Q.value = 0.8;
    const g = this.ctx.createGain();
    g.gain.value = gain;
    src.connect(bp); bp.connect(g); g.connect(dest || this.sfxGain);
    src.start(t0);
    return src;
  }

  /* ---------- SFX library ---------- */
  punch() {
    const t = this.now;
    this._osc('sine', 160, t, t + 0.12, 0.5);
    this._osc('triangle', 90, t, t + 0.16, 0.4);
    this._noise(t, 0.09, 0.35, 1700);
  }

  kick() {
    const t = this.now;
    this._osc('sine', 110, t, t + 0.18, 0.6);
    this._osc('square', 70, t, t + 0.14, 0.25);
    this._noise(t, 0.12, 0.4, 900);
  }

  grab() {
    const t = this.now;
    this._noise(t, 0.14, 0.4, 800);            // cloth & slam
    this._osc('sine', 95, t + 0.08, t + 0.3, 0.55);
    this._osc('sawtooth', 60, t + 0.08, t + 0.24, 0.2);
  }

  soulSurge(kind) {
    const t = this.now;
    // kind: 'pantera' = deep roar-rise, 'demonio' = cold shimmer-rise
    const base = kind === 'demonio' ? 320 : 180;
    const o = this.ctx && this.ctx.createOscillator();
    if (o) {
      const g = this.ctx.createGain();
      o.type = kind === 'demonio' ? 'sine' : 'sawtooth';
      o.frequency.setValueAtTime(base, t);
      o.frequency.exponentialRampToValueAtTime(base * 5, t + 0.35);
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(0.5, t + 0.05);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.55);
      o.connect(g); g.connect(this.sfxGain); o.start(t); o.stop(t + 0.6);
    }
    if (kind === 'demonio') this._noise(t + 0.28, 0.32, 0.3, 4200);
    else this._noise(t + 0.3, 0.3, 0.45, 2200);
    this._osc('sine', 70, t + 0.32, t + 0.6, 0.6);
  }

  block() {
    const t = this.now;
    this._noise(t, 0.06, 0.3, 3200);
    this._osc('square', 320, t, t + 0.05, 0.18);
  }

  whiff() {
    const t = this.now;
    this._noise(t, 0.12, 0.18, 2600);
  }

  grunt(pitch = 1) {
    const t = this.now;
    this._osc('triangle', 150 * pitch, t, t + 0.16, 0.35);
    this._osc('sawtooth', 90 * pitch, t, t + 0.12, 0.15);
  }

  ko() {
    const t = this.now;
    this._osc('sine', 200, t, t + 0.8, 0.6);
    this._osc('sine', 100, t + 0.05, t + 0.9, 0.5);
    this._noise(t, 0.5, 0.4, 600);
  }

  bell() { // round start
    const t = this.now;
    this._osc('sine', 880, t, t + 0.5, 0.4);
    this._osc('sine', 1320, t, t + 0.4, 0.2);
  }

  uiClick() {
    const t = this.now;
    this._osc('square', 520, t, t + 0.05, 0.15);
  }

  /* ---------- Eastern Mind soundtrack (real Osamu Sato CD audio) ----------
     The 1994 Eastern Mind CD tracks, converted to MP3 for web delivery
     (WAV masters preserved in teardown/eastern-mind/soundtrack/).
     User directive: Tong-Nou Theme plays AS-IS — it is literally our god's
     theme. Other tracks placed per the registry below. Procedural music
     yields while a real track plays. */
  playEMTrack(id) {
    const T = AudioEngine.EM_TRACKS[id];
    if (!T || !this.enabled) return false;
    this.stopMusic();
    this.stopEMTrack();
    const el = new Audio(T.file);
    el.loop = !!T.loop;
    el.volume = T.volume != null ? T.volume : 0.5;
    el.play().catch(() => {});
    this._emTrack = el;
    this._emTrackId = id;
    return true;
  }

  stopEMTrack() {
    if (this._emTrack) {
      try { this._emTrack.pause(); } catch (e) {}
      this._emTrack = null;
      this._emTrackId = null;
    }
  }

  get emTrackPlaying() { return this._emTrackId; }

  /* ---------- Eastern Mind SFX library (229 real game sounds) ----------
     8-bit/22kHz mono WAVs from the original game, decoded on demand and
     cached. Slots are catalogued in game/data/eastern-mind-sfx.json
     (acoustic categorization — a listening pass refines semantics). */
  playEMSfx(id) {
    const path = AudioEngine.EM_SFX[id];
    if (!path || !this.enabled) return;
    if (this._emSfxCache && this._emSfxCache[id]) {
      this._playDecodedSfx(this._emSfxCache[id]);
      return;
    }
    fetch(path).then((r) => r.arrayBuffer())
      .then((ab) => this.ctx.decodeAudioData(ab))
      .then((buf) => {
        this._emSfxCache = this._emSfxCache || {};
        this._emSfxCache[id] = buf;
        this._playDecodedSfx(buf);
      }).catch(() => {});
  }

  _playDecodedSfx(buf) {
    if (!this.enabled) return;
    const src = this.ctx.createBufferSource();
    src.buffer = buf;
    src.connect(this.sfxGain);
    src.start(this.now);
  }

  /* ---------- Battle loop: taiko drums + shakuhachi-ish lead ---------- */
  startMusic() {
    if (!this.enabled || this._musicTimer) return;
    const bpm = 128;
    const step = 60 / bpm / 2; // eighth notes
    // D minor (shakuhachi colour): breathy lead phrase
    const lead = [293.7, 349.2, 440, 392, 349.2, 293.7, 261.6, 293.7,
                  349.2, 440, 523.3, 440, 392, 349.2, 293.7, 261.6];
    this._musicStep = 0;
    const tick = () => {
      if (!this.enabled) return;
      const t = this.now + 0.02;
      const s = this._musicStep;
      // taiko: big skin hit on 1, smaller on the "and" of 2
      if (s % 8 === 0 || s % 8 === 3) {
        const big = s % 8 === 0;
        const o = this.ctx.createOscillator(); const g = this.ctx.createGain();
        o.frequency.setValueAtTime(big ? 95 : 120, t);
        o.frequency.exponentialRampToValueAtTime(42, t + 0.14);
        g.gain.setValueAtTime(big ? 0.65 : 0.4, t);
        g.gain.exponentialRampToValueAtTime(0.001, t + 0.22);
        o.connect(g); g.connect(this.musicGain); o.start(t); o.stop(t + 0.25);
        this._noise(t, 0.05, big ? 0.22 : 0.12, 900, this.musicGain);
      }
      // shime tick on off-beats
      if (s % 2 === 1) this._noise(t, 0.03, 0.07, 5200, this.musicGain);
      // shakuhachi-ish lead: sine + breath noise, sparse
      if (s % 2 === 0) {
        const f = lead[(s / 2) % lead.length];
        this._osc('sine', f, t, t + step * 1.7, 0.13, this.musicGain);
        this._noise(t, step * 1.2, 0.03, f * 2, this.musicGain);
      }
      // low drone
      if (s % 16 === 0) this._osc('triangle', 73.4, t, t + step * 14, 0.16, this.musicGain);
      this._musicStep = (s + 1) % 32;
    };
    tick();
    this._musicTimer = setInterval(tick, step * 1000);
  }

  stopMusic() {
    if (this._musicTimer) { clearInterval(this._musicTimer); this._musicTimer = null; }
  }

  setMusicVolume(v) { if (this.musicGain) this.musicGain.gain.value = v; }
}

/* Eastern Mind soundtrack registry. Files: game/assets/audio/eastern-mind/
   (MP3 web derivatives; WAV masters in teardown/eastern-mind/soundtrack/).
   Placements per the owner directive: Tong-Nou Theme as-is on the main
   menu; esoteric mix on select screens; transmigration over story endings;
   ending theme under reincarnation/cutscene endings. */
AudioEngine.EM_TRACKS = {
  'tong-nou-theme': {
    file: 'assets/audio/eastern-mind/tong-nou-theme.mp3',
    title: 'Tong-Nou Theme (4:29)', loop: true, volume: 0.5,
    placement: 'main menu — the head-world theme, plays as-is',
  },
  'tong-nou-esoteric-mix': {
    file: 'assets/audio/eastern-mind/tong-nou-esoteric-mix.mp3',
    title: 'Tong-Nou Esoteric Mix (8:01)', loop: true, volume: 0.45,
    placement: 'character/stage select — long-form browsing music',
  },
  'transmigration-ending': {
    file: 'assets/audio/eastern-mind/transmigration-ending.mp3',
    title: 'Transmigration Ending Theme (5:16)', loop: false, volume: 0.5,
    placement: 'story ending / credits',
  },
  'ending-theme': {
    file: 'assets/audio/eastern-mind/ending-theme.mp3',
    title: 'Ending Theme', loop: true, volume: 0.45,
    placement: 'reincarnation screen / cutscene endings',
  },
};

/* Eastern Mind SFX slot map. Paths are the real extracted sounds
   (teardown/eastern-mind/...), relative to game/index.html.
   Full 229-file catalog: game/data/eastern-mind-sfx.json. */
AudioEngine.EM_SFX = {
  'ui.click': '../teardown/eastern-mind/prologue-ending/sounds/D_FACE/D_FACE_s005.wav',
  'ui.back': '../teardown/eastern-mind/prologue-ending/sounds/SHARED/SHARED_s007.wav',
  'reincarn.death': '../teardown/eastern-mind/incarnation-system/sounds/R_JIN/R_JIN_s000.wav',
  'reincarn.rebirth': '../teardown/eastern-mind/incarnation-system/sounds/R_SHA/R_SHA_s000.wav',
  'trader.open': '../teardown/eastern-mind/stage-5-phantom-marketplace/sounds/D_MERCHA/D_MERCHA_s000.wav',
  'stage.intro.tree-of-life': '../teardown/eastern-mind/stage-4-tree-of-life/sounds/L_TONNEL/L_TONNEL_s000.wav',
  'stage.intro.plains-of-chi-u': '../teardown/eastern-mind/stage-1-plains-of-chi-u/sounds/F_KING/F_KING_s005.wav',
  'stage.intro.helix-palace': '../teardown/eastern-mind/stage-2-helix-palace/sounds/G_CHIFA2/G_CHIFA2_s001.wav',
  'stage.intro.palace-of-dreaming': '../teardown/eastern-mind/stage-3-palace-of-dreaming/sounds/W_AUN/W_AUN_s002.wav',
  'stage.intro.phantom-marketplace': '../teardown/eastern-mind/stage-5-phantom-marketplace/sounds/D_MARKET/D_MARKET_s000.wav',
  'stage.intro.octagonal-shrine': '../teardown/eastern-mind/stage-6-octagonal-shrine-par-fang/sounds/E_LAST/E_LAST_s000.wav',
  'shrine.ambient': '../teardown/eastern-mind/stage-6-octagonal-shrine-par-fang/sounds/E_LAST/E_LAST_s000.wav',
};

export const audio = new AudioEngine();
