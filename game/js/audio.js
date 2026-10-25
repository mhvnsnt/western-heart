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

  /* ---------- Voice banks (real character voice, file-based) ---------- */
  // Pantera voice: King bank clips wired from game/assets/audio/voice/.
  // grunt(pitch, fighterId): when fighterId has a loaded voice bank, a
  // real voice clip plays instead of the procedural grunt. When no bank
  // is loaded (or loading failed), the procedural grunt plays — never
  // silence, never a wrong fighter's voice. Bank loading is
  // fire-and-forget on first use, so the first grunt may still be
  // procedural while the bank decodes; later grunts use the real voice.
  async loadVoiceBank(fighterId) {
    if (!this.ctx || !fighterId) return null;
    if (!this._voiceBanks) this._voiceBanks = {};
    if (this._voiceBanks[fighterId]) return this._voiceBanks[fighterId];
    const p = (async () => {
      try {
        const res = await fetch(`assets/audio/voice/${fighterId}/manifest.json`);
        if (!res.ok) return null;
        const man = await res.json();
        const set = man.sets && man.sets[man.preferred_set];
        if (!set) return null;
        const bufs = [];
        for (const clip of set.clips) {
          if (clip.duration_s > 2.0) continue; // grunt-sized only; roars reserved
          try {
            const r = await fetch(clip.file);
            if (!r.ok) continue;
            const ab = await r.arrayBuffer();
            bufs.push(await this.ctx.decodeAudioData(ab));
          } catch (e) { /* one bad clip never kills the bank */ }
        }
        return bufs.length ? { manifest: man, buffers: bufs, next: 0 } : null;
      } catch (e) { return null; }
    })();
    this._voiceBanks[fighterId] = p;
    p.then((b) => { this._voiceBanks[fighterId] = b; });
    return p;
  }

  voiceGrunt(fighterId) {
    if (!this.enabled || !fighterId || !this._voiceBanks) return false;
    const bank = this._voiceBanks[fighterId];
    if (!bank || typeof bank.then === 'function' || !bank.buffers || !bank.buffers.length) return false;
    const buf = bank.buffers[bank.next % bank.buffers.length];
    bank.next += 1;
    const src = this.ctx.createBufferSource();
    src.buffer = buf;
    const g = this.ctx.createGain();
    g.gain.value = 0.9;
    src.connect(g); g.connect(this.sfxGain);
    src.start(this.now);
    return true;
  }

  grunt(pitch = 1, fighterId = null) {
    if (fighterId) {
      if (this.voiceGrunt(fighterId)) return;
      if (this.ctx && (!this._voiceBanks || !this._voiceBanks[fighterId])) this.loadVoiceBank(fighterId);
    }
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

  rage() { // Tekken-style rage ignition: rising snarl + sub thump
    const t = this.now;
    this._osc('sawtooth', 90, t, t + 0.5, 0.4);
    this._osc('sawtooth', 135, t + 0.05, t + 0.55, 0.3);
    this._osc('sine', 55, t + 0.1, t + 0.7, 0.65);
    this._noise(t + 0.15, 0.4, 0.35, 1400);
  }

  urge() { // Soul Urge ignition (T8 Heat): bright rising surge + shimmer
    const t = this.now;
    this._osc('sawtooth', 220, t, t + 0.4, 0.3);
    this._osc('sawtooth', 330, t + 0.04, t + 0.45, 0.25);
    this._osc('sine', 110, t + 0.08, t + 0.6, 0.5);
    this._noise(t + 0.1, 0.35, 0.3, 3600);
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

export const audio = new AudioEngine();
