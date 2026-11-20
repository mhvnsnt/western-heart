/* ============================================================
   WESTERN HEART — WHLipSyncPlayer (mouth-cue playback)
   Tiny runtime: plays mouthCues JSON produced by the lip-sync pipeline
   (tools/character-voice/lipsync/ — lip-sync-engine, MIT, WASM
   Rhubarb-compatible) against a jaw bone / jaw morph.

   Cue format: { mouthCues: [{start, end, value}] } where value is one of
   X A B C D E F G H (Preston Blair visemes, Rhubarb convention).
   X = closed/idle. Each viseme maps to a jaw-open amount 0..1; the
   player lerps the jaw bone rotation (or morph weight) toward it.

   No dependencies. Wire: integration.js exposes WHLipSync; the voice
   lane calls play(fighter, 'assets/voice/dorowani/win1.cues.json').
   ============================================================ */

import * as THREE from 'three';

/* Viseme → jaw open amount. Tuned for creature + humanoid jaws. */
const VISEME_OPEN = {
  X: 0.02, // idle / closed
  A: 0.85, // open vowels
  B: 0.12, // m/b/p — lips together
  C: 0.45, // e
  D: 0.65, // a-ish
  E: 0.25, // f/v — teeth on lip
  F: 0.55, // th/l
  G: 0.05, // closed consonants
  H: 0.75, // o
};

export class WHLipSyncPlayer {
  constructor() {
    this._active = []; // {jaw, cues, t0, audio, morph}
  }

  /** Find a jaw bone on a fighter rig by name. */
  findJaw(fighterRoot) {
    let found = null;
    fighterRoot.traverse((o) => {
      if (!found && o.isBone && /jaw|chin|mouth/i.test(o.name)) found = o;
    });
    return found;
  }

  /** Play cues against a jaw bone. opts: {audio: HTMLAudioElement|null,
      jawAxis:'x', jawAmount: radians at full open, morph:{mesh,name}} */
  async play(fighterRoot, cuesUrl, opts = {}) {
    const res = await fetch(cuesUrl);
    const data = await res.json();
    const cues = data.mouthCues || [];
    if (!cues.length) return null;
    const jaw = opts.jawBone || this.findJaw(fighterRoot);
    const rec = {
      jaw, cues, t0: performance.now() / 1000,
      jawAxis: opts.jawAxis || 'x',
      jawAmount: opts.jawAmount ?? 0.35,
      audio: opts.audio || null,
      rest: jaw ? jaw.quaternion.clone() : null,
      open: 0,
    };
    if (rec.audio) { rec.audio.currentTime = 0; rec.audio.play().catch(() => {}); }
    this._active.push(rec);
    return rec;
  }

  stop(rec) {
    const i = this._active.indexOf(rec);
    if (i >= 0) {
      if (rec.jaw && rec.rest) rec.jaw.quaternion.copy(rec.rest);
      if (rec.audio) rec.audio.pause();
      this._active.splice(i, 1);
    }
  }

  update() {
    const now = performance.now() / 1000;
    for (let i = this._active.length - 1; i >= 0; i--) {
      const r = this._active[i];
      const t = now - r.t0;
      const cue = r.cues.find((c) => t >= c.start && t <= c.end);
      const target = cue ? (VISEME_OPEN[cue.value] ?? 0.1) : 0.02;
      r.open += (target - r.open) * 0.55; // snappy but not jittery
      if (r.jaw) {
        r.jaw.quaternion.copy(r.rest);
        const euler = new THREE.Euler(
          r.jawAxis === 'x' ? r.jawAmount * r.open : 0,
          r.jawAxis === 'y' ? r.jawAmount * r.open : 0,
          r.jawAxis === 'z' ? r.jawAmount * r.open : 0);
        r.jaw.quaternion.multiply(new THREE.Quaternion().setFromEuler(euler));
      }
      const last = r.cues[r.cues.length - 1];
      if (t > last.end + 0.4) this.stop(r);
    }
  }
}
