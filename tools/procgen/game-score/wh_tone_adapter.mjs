// wh_tone_adapter.mjs — browser adapter: WH adaptive score -> Tone.js (MIT).
// The composition core (wh_adaptive_music.mjs) is scheduler-agnostic; this file is the
// only place that touches Tone.js, so the synth rig can be swapped without recomposing.
// Usage (browser, type="module"):
//   import { WHScore } from './wh_tone_adapter.mjs';
//   const score = new WHScore(); await score.start('menu');
//   score.setState('combat'); // crossfades layers over 2 bars
import * as Tone from 'tone';
import { composeBars, layerGains, STATES } from './wh_adaptive_music.mjs';

export class WHScore {
  constructor() {
    this.state = 'menu';
    this.seed = (Math.random() * 1e9) | 0;
    this.barCount = 0;
    this.gains = {};
    this.synths = {};
    this.scheduled = null;
  }

  async start(state = 'menu') {
    await Tone.start();
    const comp = new Tone.Compressor(-18, 3).toDestination();
    // One gain node per layer -> click-free crossfades (ouigame/veilborn pattern).
    for (const layer of ['pad', 'bass', 'arp', 'kick', 'snare', 'hat', 'lead']) {
      const g = new Tone.Gain(0);
      g.connect(comp);
      this.gains[layer] = g;
    }
    this.synths = {
      pad: new Tone.PolySynth(Tone.Synth, { oscillator: { type: 'triangle' } }).connect(this.gains.pad),
      bass: new Tone.MonoSynth({ oscillator: { type: 'sawtooth' }, filter: { Q: 2, type: 'lowpass', rolloff: -24 } }).connect(this.gains.bass),
      arp: new Tone.Synth({ oscillator: { type: 'square' }, envelope: { attack: 0.005, decay: 0.1, sustain: 0.1, release: 0.2 } }).connect(this.gains.arp),
      lead: new Tone.Synth({ oscillator: { type: 'sawtooth' }, envelope: { attack: 0.02, decay: 0.2, sustain: 0.4, release: 0.4 } }).connect(this.gains.lead),
      kick: new Tone.MembraneSynth().connect(this.gains.kick),
      snare: new Tone.NoiseSynth({ noise: { type: 'white' }, envelope: { attack: 0.001, decay: 0.18, sustain: 0 } }).connect(this.gains.snare),
      hat: new Tone.MetalSynth({ envelope: { attack: 0.001, decay: 0.05, release: 0.02 } }).connect(this.gains.hat),
    };
    this.setState(state, true);
    Tone.getTransport().bpm.value = STATES[this.state].bpm;
    // Look-ahead scheduler: compose 4 bars, schedule, roll forward.
    const tick = (time) => {
      const { bpm, events } = composeBars(this.state, this.seed + this.barCount, 4);
      const beatSec = 60 / bpm; // events are in quarter-note beats
      for (const e of events) {
        const when = time + e.beat * beatSec;
        const note = Tone.Frequency(e.midi, 'midi').toNote();
        switch (e.layer) {
          case 'kick': this.synths.kick.triggerAttackRelease('C1', e.dur, when, e.vel); break;
          case 'snare': this.synths.snare.triggerAttackRelease(e.dur, when, e.vel); break;
          case 'hat': this.synths.hat.triggerAttackRelease(e.dur, when, e.vel); break;
          default: {
            const s = this.synths[e.layer];
            if (s) s.triggerAttackRelease(note, e.dur * beatSec, when, e.vel);
          }
        }
      }
      this.barCount += 4;
    };
    this.scheduled = Tone.getTransport().scheduleRepeat((time) => tick(time), '4m');
    Tone.getTransport().start();
  }

  // Crossfade layers from current state to `next` over `bars` bars.
  setState(next, immediate = false) {
    const from = this.state;
    this.state = next;
    const apply = (t) => {
      const g = layerGains(from, next, t);
      for (const [layer, v] of Object.entries(g)) {
        this.gains[layer]?.gain.rampTo(v * 0.8, 0.5);
      }
    };
    if (immediate) { apply(1); return; }
    const steps = 16;
    let i = 0;
    const iv = setInterval(() => { apply(++i / steps); if (i >= steps) clearInterval(iv); }, 125);
    Tone.getTransport().bpm.rampTo(STATES[next].bpm, 2);
  }

  stop() { Tone.getTransport().stop(); Tone.getTransport().cancel(this.scheduled); }
}
