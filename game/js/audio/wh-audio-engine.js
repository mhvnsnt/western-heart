// WHAudio — Wwise-style event engine on Web Audio API (SKETCH, not yet wired into game/js)
// Design: see ../wh-audio-engine-design.md. Drop-in shape: game/js/audio/wh-audio.js
// No dependencies. One AudioContext, created/resumed on the first user gesture
// (browsers suspend contexts until interaction — OpenReplay/MDN pattern).

export class WHAudio {
  constructor(manifestUrl = 'game/assets/audio/audio-events.json') {
    this.ctx = null;
    this.buffers = new Map();   // bankFile -> AudioBuffer
    this.buses = {};            // name -> GainNode
    this.music = null;          // current music voice { sources:[], gains:[] }
    this.state = 'Menu';
    this.switches = { fighter: 'pantera', stage: 'default' };
    this.rtpc = { intensity: 0, distance: 0.5, healthLow: 0, crowd: 0 };
    this.manifestUrl = manifestUrl;
    this.manifest = null;
    this.played = {};           // eventName -> last variation index (no-repeat random)
  }

  // MUST be called from a click/tap/key handler (fight-start, select-confirm).
  async unlock() {
    if (!this.ctx) {
      this.ctx = new (window.AudioContext || window.webkitAudioContext)();
      const comp = this.ctx.createDynamicsCompressor(); // master limiter
      comp.threshold.value = -12; comp.ratio.value = 8;
      comp.connect(this.ctx.destination);
      for (const name of ['music', 'sfx', 'voice', 'ui', 'ambience']) {
        const g = this.ctx.createGain();
        g.connect(comp); this.buses[name] = g;
      }
      // Music bus gets a lowpass for Pause/muffle snapshots (State, below).
      this.musicFilter = this.ctx.createBiquadFilter();
      this.musicFilter.type = 'lowpass'; this.musicFilter.frequency.value = 20000;
      this.musicFilter.connect(this.buses.music);
    }
    if (this.ctx.state === 'suspended') await this.ctx.resume();
  }

  async load(manifest = null) {
    this.manifest = manifest || await (await fetch(this.manifestUrl)).json();
    // Pre-decode every bank file once; buffers are shared, sources are cheap
    // one-shot nodes created per trigger (AudioBufferSourceNode plays once).
    const files = [...new Set(Object.values(this.manifest.banks).flat())];
    for (const f of files) {
      const buf = await this.ctx.decodeAudioData(
        await (await fetch(`game/assets/audio/${f}`)).arrayBuffer());
      this.buffers.set(f, buf);
    }
  }

  // ---- Wwise concepts, mapped ----
  // postEvent(name, opts)  == AkSoundEngine.PostEvent / FMOD createInstance+start
  //   event = { container:'random'|'sequence'|'switch'|'blend', variations:[...] }
  //   variation = { bank, cue:[startSec, durSec] | null (whole file),
  //                 volume, pitch:{min,max}, bus, cooldownMs }
  postEvent(name, opts = {}) {
    const ev = this.manifest.events[name];
    if (!ev || !this.ctx) return null;
    const v = this._pick(ev, name);
    const t = this.ctx.currentTime + (opts.delay || 0);
    const src = this.ctx.createBufferSource();
    src.buffer = this.buffers.get(v.bank);
    if (v.cue) { src.start(t, v.cue[0], v.cue[1]); }
    else src.start(t);
    // Random pitch keeps repeated LP1/RP2/LK3/RK4 hits from sounding machine-gunned.
    if (v.pitch) src.playbackRate.value =
      v.pitch.min + Math.random() * (v.pitch.max - v.pitch.min);
    const g = this.ctx.createGain();
    g.gain.setValueAtTime(v.volume ?? 1, t);
    // Distance RTPC: simple pan + lowpass send per emitter (fight only).
    let node = src;
    if (opts.pan !== undefined) {
      const p = this.ctx.createStereoPanner(); p.pan.value = opts.pan;
      src.connect(p); node = p;
    }
    node.connect(g); g.connect(this.buses[v.bus || 'sfx']);
    return src;
  }

  _pick(ev, name) {
    if (ev.container === 'random') {
      // No-repeat random: never play the same variation twice in a row.
      let i; do { i = Math.floor(Math.random() * ev.variations.length); }
      while (ev.variations.length > 1 && i === this.played[name]);
      this.played[name] = i; return ev.variations[i];
    }
    if (ev.container === 'sequence') {           // e.g. throw-chain steps, KO sequence
      const i = (this.played[name] = ((this.played[name] ?? -1) + 1) % ev.variations.length);
      return ev.variations[i];
    }
    if (ev.container === 'switch') {             // Wwise Switch: pick by switch value
      const key = this.switches[ev.switchGroup];
      return ev.variations.find(v => v.switchValue === key) || ev.variations[0];
    }
    return ev.variations[0];
  }

  // setSwitch(group, value) == Wwise SetSwitch. Example: fighter voice bank,
  // stage ambience/BGM pool. Takes effect on the NEXT postEvent, not mid-clip.
  setSwitch(group, value) { this.switches[group] = value; }

  // setState(name) == Wwise SetState. Snapshot = bus gains + music filter.
  // Menu/Select/Fight/RoundEnd/KO/Pause. KO: duck music -18 dB, muffle via
  // lowpass; Pause: music -12 dB + lowpass 800 Hz; Fight: full.
  setState(name) {
    this.state = name;
    const t = this.ctx.currentTime, snap = this.manifest.states[name] || {};
    for (const [bus, db] of Object.entries(snap.busDb || {})) {
      const g = this.buses[bus]; if (g) g.gain.setTargetAtTime(dbToGain(db), t, 0.25);
    }
    if (snap.musicLowpassHz)
      this.musicFilter.frequency.setTargetAtTime(snap.musicLowpassHz, t, 0.3);
  }

  // setRTPC(name, value01) == Wwise SetRTPCValue. Values are 0..1 in the
  // manifest; curves live in rtpcCurves (see audio-events.json). Smoothing
  // via setTargetAtTime (timeConstant 0.15s) avoids zipper noise.
  // Intensity drives MUSIC LAYER gains (crossfade), not volume of one loop.
  setRTPC(name, value01) {
    this.rtpc[name] = Math.min(1, Math.max(0, value01));
    const curve = (this.manifest.rtpcCurves || {})[name];
    if (!curve || !this.music) return;
    const t = this.ctx.currentTime;
    for (const layer of this.music.layers) {
      const c = curve[layer.name]; if (!c) continue;
      const g = ramp(value01, c.inMin, c.inMax, c.outMin, c.outMax);
      layer.gain.gain.setTargetAtTime(g, t, 0.15);
    }
  }

  // Adaptive music: N layer loops started sample-synchronously (same ctx time),
  // each on its own GainNode. Intensity crossfades layers; bar-boundary
  // switching for pool rotation: schedule the NEXT track at the next loop
  // boundary (loopStart/loopEnd), never mid-bar. Stingers are one-shots on
  // the music bus with a duck envelope applied in setState('KO'/'RoundEnd').
  startMusic(poolName) {
    this.stopMusic(0.5);
    const pool = this.manifest.musicPools[poolName];
    const track = pool.tracks[Math.floor(Math.random() * pool.tracks.length)];
    const t = this.ctx.currentTime + 0.05, layers = [];
    for (const layer of track.layers) {
      const src = this.ctx.createBufferSource();
      src.buffer = this.buffers.get(layer.bank); src.loop = true;
      if (layer.loop) { src.loopStart = layer.loop[0]; src.loopEnd = layer.loop[1]; }
      const g = this.ctx.createGain(); g.gain.value = layer.baseGain ?? 0;
      src.connect(g); g.connect(this.musicFilter);
      src.start(t); layers.push({ name: layer.name, gain: g, src });
    }
    this.music = { track, layers };
    this.setRTPC('intensity', this.rtpc.intensity); // apply current intensity now
  }

  stopMusic(fadeSec = 0.5) {
    if (!this.music) return;
    const t = this.ctx.currentTime;
    for (const l of this.music.layers) {
      l.gain.gain.setTargetAtTime(0, t, fadeSec / 3);
      try { l.src.stop(t + fadeSec); } catch (_) { /* already stopped */ }
    }
    this.music = null;
  }
}

function dbToGain(db) { return Math.pow(10, db / 20); }
function ramp(x, inMin, inMax, outMin, outMax) {
  const k = Math.min(1, Math.max(0, (x - inMin) / (inMax - inMin)));
  return outMin + k * (outMax - outMin);
}
