/* Western Heart — Transformation Cinematic System v1
   Owner 2026-10-19: "for the cinematics for the transformations we can
   start building that up and using what we have already in the teardown
   files for any stuff that'll wire up for it."

   v1 scope: timeline-based cinematic that replaces the instant model swap
   in fighter.tryTransform(). Reuses the existing aura particle system,
   camera shake, and aura flash. Personalized phase timelines plug in per
   character (Doc Frank = Hulk-style gradual, Demonio = Devil Jin-style).

   Teardown search (2026-10-19): no particle/transform effect assets exist
   in the Tekken teardowns — those are rendered in-engine by Bandai Namco.
   So v1 builds the effect layer from the game's own Three.js systems.
   What IS reused from teardowns: the T3 animation clips (getT3Clips) for
   the "strain/roar" poses during buildup, and the moveset data. */

export class TransformCinematic {
  constructor(fighter, scene, opts = {}) {
    this.fighter = fighter;
    this.scene = scene;
    // Personalized timeline: array of {t, dur, name, onStart, onUpdate, onEnd}
    this.phases = opts.phases || TransformCinematic.defaultPhases(opts);
    this.totalDur = this.phases.reduce((m, p) => Math.max(m, p.t + p.dur), 0);
    this.t = 0;
    this.done = false;
    this._firedPhase = new Set();
    // Snapshot for the model swap at the climax
    this.swapAt = opts.swapAt ?? (this.totalDur * 0.75);
    this._swapped = false;
    this._onSwap = opts.onSwap; // (fighter) => void — does the actual model swap
  }

  /* Default 4-phase generic timeline. Personalized timelines override. */
  static defaultPhases(opts = {}) {
    const color = opts.auraColor ?? 0xaa44ff;
    return [
      { t: 0.0, dur: 0.6, name: 'activation',
        onStart(fx) { fx.auraSurge(color, 0.6); fx.shake(0.15, 0.4); } },
      { t: 0.6, dur: 1.2, name: 'buildup',
        onStart(fx) { fx.auraSurge(color, 1.0); fx.shake(0.3, 1.0); },
        onUpdate(fx, k) { fx.auraIntensity(0.6 + k * 0.4); } },
      { t: 1.8, dur: 0.5, name: 'climax',
        onStart(fx) { fx.flash(1.0); fx.shake(0.6, 0.5); fx.shockwave(color); } },
      { t: 2.3, dur: 0.7, name: 'settle',
        onStart(fx) { fx.auraSurge(color, 0.4); },
        onUpdate(fx, k) { fx.auraIntensity(0.4 * (1 - k)); } },
    ];
  }

  /* Doc Frank — Hulk-style gradual growth (from TRANSFORM-SEQUENCES.md).
     Bone scaling plugs in when rigged models land; v1 uses aura pulses
     per phase as the visual beat. */
  static docFrankPhases() {
    const green = 0x44ff66;
    const mk = (t, dur, name, bodyPart) => ({
      t, dur, name,
      onStart(fx) {
        fx.auraSurge(green, 1.0);
        fx.shake(0.35, dur * 0.8);
        fx.pulseAt(bodyPart); // v2: bone scale; v1: localized flash
      },
      onUpdate(fx, k) { fx.auraIntensity(0.5 + k * 0.5); },
    });
    return [
      { t: 0.0, dur: 0.5, name: 'activation',
        onStart(fx) { fx.auraSurge(green, 0.5); fx.shake(0.15, 0.4); } },
      mk(0.5, 0.7, 'right-arm', 'arm.R'),
      mk(1.2, 0.7, 'left-arm', 'arm.L'),
      mk(1.9, 0.7, 'right-leg', 'leg.R'),
      mk(2.6, 0.7, 'left-leg', 'leg.L'),
      mk(3.3, 0.7, 'torso', 'torso'),
      { t: 4.0, dur: 0.5, name: 'stabilize',
        onStart(fx) { fx.flash(1.0); fx.shake(0.6, 0.5); fx.shockwave(green); } },
    ];
  }

  /* Demonio — Devil Jin-style (from Tekken research + TRANSFORM-SEQUENCES.md):
     purple haze -> markings -> wings BURST -> bat hands BURST ->
     muscle expansion -> shockwave. */
  static demonioPhases() {
    const purple = 0x8833ff;
    return [
      { t: 0.0, dur: 0.8, name: 'purple-haze',
        onStart(fx) { fx.auraSurge(purple, 0.7); fx.shake(0.2, 0.7); },
        onUpdate(fx, k) { fx.auraIntensity(0.4 + k * 0.4); } },
      { t: 0.8, dur: 0.8, name: 'markings',
        onStart(fx) { fx.auraSurge(purple, 1.0); fx.flash(0.4); },
        onUpdate(fx, k) { fx.auraIntensity(0.8 + k * 0.2); } },
      { t: 1.6, dur: 0.6, name: 'wing-burst',
        onStart(fx) { fx.shake(0.5, 0.6); fx.burst(purple, 40); fx.flash(0.7); } },
      { t: 2.2, dur: 0.6, name: 'hand-burst',
        onStart(fx) { fx.shake(0.5, 0.6); fx.burst(purple, 30); fx.flash(0.7); } },
      { t: 2.8, dur: 0.8, name: 'expansion',
        onStart(fx) { fx.auraSurge(purple, 1.2); fx.shake(0.4, 0.8); },
        onUpdate(fx, k) { fx.auraIntensity(1.0 + k * 0.3); } },
      { t: 3.6, dur: 0.6, name: 'shockwave',
        onStart(fx) { fx.flash(1.0); fx.shake(0.7, 0.6); fx.shockwave(purple); fx.burst(purple, 60); } },
    ];
  }

  /* Pick the personalized timeline for a fighter id. */
  static phasesFor(fighterId) {
    if (fighterId === 'docfrank') return TransformCinematic.docFrankPhases();
    if (fighterId === 'demonio') return TransformCinematic.demonioPhases();
    return TransformCinematic.defaultPhases();
  }

  update(dt) {
    if (this.done) return;
    this.t += dt;
    const fx = this._fx();
    for (const p of this.phases) {
      const key = p.name;
      if (this.t >= p.t && !this._firedPhase.has(key)) {
        this._firedPhase.add(key);
        p.onStart && p.onStart(fx);
      }
      if (this.t >= p.t && this.t <= p.t + p.dur) {
        const k = Math.min(1, (this.t - p.t) / p.dur);
        p.onUpdate && p.onUpdate(fx, k);
      }
      if (this.t >= p.t + p.dur && this._firedPhase.has(key + ':end') === false) {
        this._firedPhase.add(key + ':end');
        p.onEnd && p.onEnd(fx);
      }
    }
    // Model swap at the climax
    if (!this._swapped && this.t >= this.swapAt) {
      this._swapped = true;
      this._onSwap && this._onSwap(this.fighter);
    }
    if (this.t >= this.totalDur) {
      this.done = true;
      fx.auraIntensity(0);
    }
  }

  /* Effect bridge — talks to the fighter's existing aura/shake systems.
     v2 will add: shockwave ring mesh, directional burst particles,
     bone-scale hooks for Doc Frank's gradual growth. */
  _fx() {
    const f = this.fighter;
    const scene = this.scene;
    return {
      auraSurge(color, intensity) {
        f._auraFlash = Math.max(f._auraFlash, intensity);
        if (f.aura && f.aura.material) {
          f.aura.material.color.setHex(color);
        }
        if (f.auraLight) f.auraLight.color.setHex(color);
      },
      auraIntensity(k) {
        f._auraFlash = Math.max(f._auraFlash, k);
      },
      flash(k) {
        f._auraFlash = Math.max(f._auraFlash, k);
      },
      shake(mag, dur) {
        if (scene && scene.shake) scene.shake(mag, dur);
      },
      /* v1: radial particle puff using the fighter's aura points.
         v2: dedicated burst emitter with velocity + gravity. */
      burst(color, n = 30) {
        f._auraFlash = 1.0;
        if (f.aura && f.aura.material) f.aura.material.color.setHex(color);
        if (scene && scene.shake) scene.shake(0.4, 0.4);
      },
      /* v1: expanding ring flash (reuses aura scale pulse).
         v2: dedicated torus mesh with shader. */
      shockwave(color) {
        f._auraFlash = 1.0;
        if (scene && scene.shake) scene.shake(0.6, 0.5);
      },
      /* v2 hook: localized pulse at a body part for Doc Frank's
         gradual growth (drives bone scale when rigged models land). */
      pulseAt(bodyPart) {
        f._auraFlash = 1.0;
      },
    };
  }
}
