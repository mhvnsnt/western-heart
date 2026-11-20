/* ============================================================
   WESTERN HEART — Face Rig (runtime morph driver + blink timer)

   Drives the canonical 10-morph face set (tools/auto_rig/backends/
   face_morphs.json) on a fighter's SkinnedMeshes:
     blink_L, blink_R, jawOpen, browUp, browDown,
     mouthSmile, mouthFrown, mouthOpen, eyesWide, eyesSquint

   - Blink timer: automatic blink every 3-6 s (randomized), 150 ms
     close-open, plus forced blink on hit reactions.
   - Expression API: setExpression(name, weight, fadeTime) for win
     poses, taunts, intro interactions, hit reactions.
   - Talking: setTalking(openAmount) drives jawOpen/mouthOpen for
     cutscenes and voice moments (Dorowani).

   Usage:
     const face = FaceRig.attach(root);   // root: THREE.Group with SkinnedMeshes
     face.update(dt, fighterState);        // call every frame after animation
     face.blink();                         // force a blink
     face.setExpression('mouthSmile', 1.0);
     face.setTalking(0.5);
     face.dispose();
   ============================================================ */

const BLINK_MIN = 3.0;   // seconds between blinks (min)
const BLINK_MAX = 6.0;   // seconds between blinks (max)
const BLINK_DUR = 0.15;  // 150 ms close-open

// Expression presets: morph name -> target weight
const EXPRESSIONS = {
  neutral:    {},
  happy:      { mouthSmile: 1.0, eyesSquint: 0.3 },
  sad:        { mouthFrown: 1.0, browUp: 0.4 },
  angry:      { browDown: 1.0, eyesSquint: 0.6 },
  surprised:  { eyesWide: 1.0, browUp: 0.8, mouthOpen: 0.5 },
  pain:       { browDown: 0.7, mouthFrown: 0.6, eyesSquint: 0.5 },
  taunt:      { mouthSmile: 0.7, browUp: 0.3 },
  victory:    { mouthSmile: 1.0, eyesSquint: 0.2 },
  ko:         { eyesSquint: 0.8, mouthOpen: 0.4 },
};

export class FaceRig {
  constructor() {
    this.meshes = [];      // SkinnedMeshes with morph targets
    this.morphIndex = {};  // morph name -> index (from first mesh)
    this.blinkT = BLINK_MIN + Math.random() * (BLINK_MAX - BLINK_MIN);
    this.blinkPhase = -1;  // -1 = not blinking, else 0..1 progress
    this.targets = {};     // morph name -> target weight
    this.current = {};     // morph name -> current weight
    this.talkAmount = 0;
    this.talkTarget = 0;
  }

  static attach(root) {
    const rig = new FaceRig();
    root.traverse(o => {
      if (o.isSkinnedMesh && o.morphTargetDictionary) {
        rig.meshes.push(o);
      }
    });
    if (rig.meshes.length > 0) {
      // Use the first mesh's dictionary as canonical
      const dict = rig.meshes[0].morphTargetDictionary;
      for (const name of Object.keys(dict)) {
        rig.morphIndex[name] = dict[name];
        rig.current[name] = 0;
        rig.targets[name] = 0;
      }
    }
    return rig;
  }

  get hasFace() {
    return this.meshes.length > 0 && Object.keys(this.morphIndex).length > 0;
  }

  blink() {
    if (this.blinkPhase < 0) this.blinkPhase = 0;
  }

  setExpression(name, weight = 1.0, fadeTime = 0.2) {
    const preset = EXPRESSIONS[name];
    if (!preset) return;
    // Clear other expression targets, set new ones
    for (const key of Object.keys(this.targets)) {
      if (!(key in preset)) this.targets[key] = 0;
    }
    for (const [morph, w] of Object.entries(preset)) {
      if (morph in this.targets) this.targets[morph] = w * weight;
    }
    this.fadeTime = fadeTime;
  }

  setTalking(amount) {
    this.talkTarget = Math.max(0, Math.min(1, amount));
  }

  update(dt, fighterState = null) {
    if (!this.hasFace) return;

    // Blink timer
    this.blinkT -= dt;
    if (this.blinkT <= 0) {
      this.blink();
      this.blinkT = BLINK_MIN + Math.random() * (BLINK_MAX - BLINK_MIN);
    }
    // Forced blink on hit
    if (fighterState === 'hitstun' || fighterState === 'knockdown') {
      if (this.blinkPhase < 0 && Math.random() < 0.1) this.blink();
    }

    // Blink phase: 0->1 over BLINK_DUR, weight = sin(pi * phase)
    let blinkW = 0;
    if (this.blinkPhase >= 0) {
      this.blinkPhase += dt / BLINK_DUR;
      if (this.blinkPhase >= 1) {
        this.blinkPhase = -1;
      } else {
        blinkW = Math.sin(Math.PI * this.blinkPhase);
      }
    }

    // Talking: smooth toward target
    this.talkAmount += (this.talkTarget - this.talkAmount) * Math.min(1, dt * 8);
    const talkW = this.talkAmount * (0.7 + 0.3 * Math.sin(Date.now() * 0.02));

    // Blend current toward targets
    const rate = Math.min(1, dt / (this.fadeTime || 0.15));
    for (const name of Object.keys(this.current)) {
      let target = this.targets[name] || 0;
      // Blink overrides
      if (name === 'blink_L' || name === 'blink_R') {
        target = Math.max(target, blinkW);
      }
      // Talking overrides
      if (name === 'jawOpen') target = Math.max(target, talkW * 0.8);
      if (name === 'mouthOpen') target = Math.max(target, talkW * 0.6);
      this.current[name] += (target - this.current[name]) * rate;
    }

    // Apply to all meshes
    for (const mesh of this.meshes) {
      const infl = mesh.morphTargetInfluences;
      if (!infl) continue;
      const dict = mesh.morphTargetDictionary;
      for (const [name, idx] of Object.entries(this.morphIndex)) {
        const localIdx = dict[name];
        if (localIdx !== undefined && infl[localIdx] !== undefined) {
          infl[localIdx] = this.current[name] || 0;
        }
      }
    }
  }

  dispose() {
    // Reset all morphs
    for (const mesh of this.meshes) {
      const infl = mesh.morphTargetInfluences;
      if (infl) infl.fill(0);
    }
    this.meshes.length = 0;
  }
}
