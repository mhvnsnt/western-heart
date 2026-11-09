/* ============================================================
   WESTERN HEART — Arena (stage-agnostic shell)
   Owns renderer/camera/composer and the dynamic fight camera.
   Stage content comes from game/js/stages.js (Lane 4: every stage
   from the canon lands + Tekken 3 retro panoramas). Switch arenas
   with setStage(id) — old stage GPU resources are disposed.
   ============================================================ */
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { getStage, buildStage, disposeStage } from './stages.js';
import { fightCameraY, fightCameraDolly, fightCameraCenterX } from './fight-camera-math.js';
// Per-stage color grade (worker 27 lighting rig): tone-mapping exposure +
// bloom strength from the stage's lighting.grade block. Serves the bible's
// "luminous darkness" — each land gets its own grade.
import { applyGrade } from './lighting-rig.js';

const NEAR_CLIP_M = 2.5; // floor rings closer than this in front of the camera are not drawn (see the constructor)

export class Arena {
  constructor(canvas, stageId = 'shrine') {
    this.isMobile = /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent);

    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: !this.isMobile, powerPreference: 'high-performance' });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.45;
    /* NEAR-CAMERA CLIP for decorative floor rings (2026-11-02): in portrait the fight camera pulls back to fit both
       fighters and ends up right over the near side of a stage's glowing edge ring, which then filled the bottom of the
       phone screen behind the touch controls as a thick orange band. Meshes the stage builders flag userData.nearClip
       are cut by a plane NEAR_CLIP_M in front of the camera (updated every render), so only the stretch between the
       camera and the fight disappears and the far edge keeps glowing behind the fighters. */
    this.renderer.localClippingEnabled = true;
    this._nearClip = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);
    this._nearClipOn = false;

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(45, 1, 0.1, 200);
    this.camera.position.set(0, 1.8, 7);
    this.camera.lookAt(0, 1.0, 0);

    this.composer = new EffectComposer(this.renderer);
    this.composer.addPass(new RenderPass(this.scene, this.camera));
    this.bloom = new UnrealBloomPass(new THREE.Vector2(256, 256), this.isMobile ? 0.6 : 0.85, 0.7, 0.8);
    this.composer.addPass(this.bloom);
    this.composer.addPass(new OutputPass());

    this.resize();
    window.addEventListener('resize', () => this.resize());

    canvas.addEventListener('webglcontextlost', (e) => {
      e.preventDefault();
      console.error('[WH] WebGL context lost — attempting restore');
      const el = document.getElementById('round-banner');
      if (el) { el.textContent = 'GRAPHICS PAUSED — RESTORING…'; el.classList.add('show'); }
    }, false);
    canvas.addEventListener('webglcontextrestored', () => {
      console.log('[WH] WebGL context restored');
      const el = document.getElementById('round-banner');
      if (el) el.classList.remove('show');
      this.renderer.compile(this.scene, this.camera);
    }, false);

    this._shakeT = 0; this._shakeMag = 0; this._lookY = 1.0;
    this.freeCameraActive = false;  // game/js/free-camera.js takeover gate
    /* HEART AND MIND WITHIN (worker 20, 2026-10-22): camera override hook.
       When set to a function, update() calls camOverride(dt, camera,
       shakeOffset) INSTEAD of the versus fight camera — the 3D brawler
       drives its own third-person camera through this. Null = classic. */
    this.camOverride = null;
    // Tekken CameraRig state (teardown/tekken3/tools/tekken3recompiled/
    // native/src/camera.cpp — CameraRig::reset(0)): smoothed midpoint of the
    // two fighters and smoothed fighter span. See update() for the port.
    this._camCenterX = 0; this._camSpan = 5.0;

    this._stage = null;      // built stage { group, update, def, skyTex, fog }
    this._stageToken = 0;    // guards against out-of-order async builds
    this.setStage(stageId);
  }

  /* Swap the arena. Async (Tekken retro stages fetch their OBJ shell).
     Old stage group is removed + GPU-disposed. Safe to call rapidly:
     only the latest request wins. */
  async setStage(stageId) {
    const token = ++this._stageToken;
    const def = getStage(stageId);
    try {
      const built = await buildStage(def, this);
      if (token !== this._stageToken) { disposeStage(built.group); return; }
      if (this._stage) {
        this.scene.remove(this._stage.group);
        disposeStage(this._stage.group);
        if (this._stage.skyTex) this._stage.skyTex.dispose();
      }
      this._stage = built;
      this._nearClipOn = false;
      built.group.traverse((o) => {
        if (!o.userData || !o.userData.nearClip || !o.material) return;
        for (const m of [].concat(o.material)) m.clippingPlanes = [this._nearClip];
        this._nearClipOn = true;
      });
      this.scene.add(built.group);
      this.scene.background = built.skyTex;
      this.scene.fog = built.fog;
      console.log(`[WH] stage loaded: ${def.name} (${def.id})`);
    } catch (e) {
      console.error(`[WH] stage ${stageId} failed to build:`, e);
    }
  }

  get stageDef() { return this._stage ? this._stage.def : getStage('shrine'); }

  shake(mag = 0.25, dur = 0.18) { this._shakeMag = Math.max(this._shakeMag, mag); this._shakeT = Math.max(this._shakeT, dur); }

  /* Free-camera gate (game/js/free-camera.js): while the user drives
     the camera, the authored fight camera must not overwrite it. */
  setFreeCamera(active) { this.freeCameraActive = !!active; }

  /* Per-frame impact shake offsets (shared by the fight camera and any
     camOverride driver, e.g. the brawler's third-person camera). */
  shakeOffset(dt) {
    let ox = 0, oy = 0;
    if (this._shakeT > 0) {
      this._shakeT -= dt;
      const k = Math.max(0, this._shakeT) * this._shakeMag * 14;
      ox = (Math.random() - 0.5) * k; oy = (Math.random() - 0.5) * k;
      if (this._shakeT <= 0) this._shakeMag = 0;
    }
    return { ox, oy };
  }

  update(dt, fighterA, fighterB, groundY = 0) {
    const t = performance.now() * 0.001;
    if (this._stage) this._stage.update(dt, t, fighterA, fighterB);
    // Free-camera takeover (game/js/free-camera.js): the authored fight
    // camera is procedural (recomputed from the fighters every frame),
    // so gating it here overwrites nothing — on return the next update()
    // recomputes it and eases back in.
    if (this.freeCameraActive) return;

    // Brawler camera override (Heart and Mind Within): the mode drives the
    // camera itself; shake offsets are handed over so impacts still kick.
    if (this.camOverride) {
      this.camOverride(dt, this.camera, this.shakeOffset(dt));
      return;
    }

    // dynamic fighting camera — Tekken CameraRig port
    // (teardown/tekken3/tools/tekken3recompiled/native/src/camera.cpp):
    // track the FULL midpoint of both fighters and zoom so the fighter span
    // always fits the horizontal frustum. Vertical FOV is invariant; horizontal
    // FOV derives from the live aspect — portrait AND landscape keep both
    // fighters in frame. Replaces the old aspect-blind linear zoom that left
    // fighters off-screen in portrait (NDC |x| up to 3.4).
    // Stream 3: stages may declare camDist (cage interiors, backstage rooms)
    // to pull the camera inside their geometry, and camAngle (degrees) to
    // orbit the camera around the target for cluttered stages.
    const camScale = ((this._stage && this._stage.def.camDist) || 7) / 7;
    const camAng = (((this._stage && this._stage.def.camAngle) || 0) * Math.PI) / 180;
    let baseX = Math.sin(camAng) * 7 * camScale, baseZ = Math.cos(camAng) * 7 * camScale;
    let baseY = 1.8, lookY = 1.0;
    // Stage wall distance (fighters clamp at ±wallDistance; Tekken
    // standard 8.4 for a 16.8-wide arena). Hoisted here so the shaken
    // camera below can be re-clamped against the same wall (Bug 5).
    const wallD = (this._stage && this._stage.def && this._stage.def.dims && this._stage.def.dims.wallDistance) || 8.4;
    if (!this._camRig) this._camRig = { centerX: 0, span: 5.0 };
    if (fighterA && fighterB) {
      const p1x = fighterA.root.position.x, p2x = fighterB.root.position.x;
      const desiredCenter = (p1x + p2x) * 0.5;
      const desiredSpan = Math.max(Math.abs(p2x - p1x), this.camera.aspect < 1 ? 2.6 : 4.5);
      const k = 1 - Math.exp(-Math.max(dt, 0) * 7.5);
      this._camRig.centerX += (desiredCenter - this._camRig.centerX) * k;
      this._camRig.span += (desiredSpan - this._camRig.span) * k;
      if (this._baseFov === undefined) this._baseFov = this.camera.fov;
      // Edge-safe dolly (owner t374u 2026-11-05): cap distance inside the
      // arena shell; widen FOV when the span no longer fits — never shove
      // the camera through / behind walls. Landscape used to force min
      // 10.5 m (wall line); now both aspects share fightCameraDolly().
      // (wallD is hoisted above this block — see Bug 5 note below.)
      const dolly = fightCameraDolly({
        span: this._camRig.span,
        aspect: this.camera.aspect || 1,
        baseFov: this._baseFov,
        camScale,
      });
      if (Math.abs(dolly.fov - this.camera.fov) > 0.05) {
        this.camera.fov = dolly.fov;
        this.camera.updateProjectionMatrix();
      }
      baseZ = dolly.dist;
      baseX = fightCameraCenterX(this._camRig.centerX, wallD, 1.2);
      const maxY = Math.max(fighterA.root.position.y, fighterB.root.position.y);
      // Level-following vertical framing (owner 2026-10-25: camera stayed
      // up top after floor/balcony breaks): anchor to the current ground
      // and track only height above it — see fight-camera-math.js.
      const _cy = fightCameraY(groundY, maxY);
      baseY = _cy.baseY;
      lookY = _cy.lookY;
    }
    if (camAng) {  // orbit the camera around the target (cluttered stages)
      const rx = baseX * Math.cos(camAng) + baseZ * Math.sin(camAng);
      const rz = -baseX * Math.sin(camAng) + baseZ * Math.cos(camAng);
      baseX = rx; baseZ = rz;
    }
    // Stream 3: explicit camera pose override for stages where the default
    // fighting camera sits inside geometry (dense backstage areas).
    const def = this._stage && this._stage.def;
    if (def && def.camPos) { baseX = def.camPos[0]; baseY = def.camPos[1]; baseZ = def.camPos[2]; }
    let lookX = 0, lookZ = 0;
    if (def && def.camTgt) { lookX = def.camTgt[0]; lookY = def.camTgt[1]; lookZ = def.camTgt[2]; }
    if (fighterA && fighterB && this._camRig && !camAng) {
      this.camera.position.x = baseX;
      this.camera.position.z = baseZ;
    } else {
      this.camera.position.x += (baseX - this.camera.position.x) * Math.min(1, dt * 4);
      this.camera.position.z += (baseZ - this.camera.position.z) * Math.min(1, dt * 3);
    }
    this.camera.position.y += (baseY - this.camera.position.y) * Math.min(1, dt * 4);
    this._lookY += (lookY - this._lookY) * Math.min(1, dt * 4);

    let { ox, oy } = this.shakeOffset(dt);
    this.camera.position.x += ox; this.camera.position.y += oy;
    // Piece 1 re-test Bug 5 (camera clips inside/behind pillars and walls
    // after 00): the impact shake was added AFTER the wall clamp, with no
    // clamp on the shaken position. A heavy hit (mag 0.6, dur 0.5) shoves
    // the camera up to ±2.1 m sideways/down — at the stage edge the camera
    // already sits at its clamped corner (Shrine: 12.73 m from center vs
    // the panel ring's 13.25 m inner face, 0.5 m of clearance), so the
    // shake pushed it through the shell, behind the wood panels, and the
    // fighters vanished behind the wall. After 00 the fight ran ~25 min
    // with the fighters piled at the walls, so the camera sat at that
    // corner for minutes with every heavy hit shaking it through. Fix:
    // re-clamp the shaken position against the same wall (same
    // fightCameraCenterX the unshaken position uses) and keep it above
    // the current floor (groundY + 0.5 m) — the shake keeps its kick,
    // it just cannot leave the shell. The look target keeps its
    // counter-shake (-ox) so framing is unchanged.
    if (!camAng) {
      this.camera.position.x = fightCameraCenterX(this.camera.position.x, wallD, 1.2);
      this.camera.position.y = Math.max(groundY + 0.5, this.camera.position.y);
    }
    if (this._stage && this._stage.def && this._stage.def.camTgt) {
      const t = this._stage.def.camTgt;
      this.camera.lookAt(t[0], this._lookY, t[2]);
    } else if (fighterA && fighterB && this._camRig) {
      this.camera.lookAt(this._camRig.centerX - ox, this._lookY, 0);
    } else {
      this.camera.lookAt(this.camera.position.x - ox, this._lookY, 0);
    }
  }

  resize() {
    const w = window.innerWidth, h = window.innerHeight;
    this.renderer.setSize(w, h, false);
    this.composer.setSize(w, h);
    this.camera.aspect = w / h; this.camera.updateProjectionMatrix();
  }

  render() {
    if (this._nearClipOn) {
      const f = this._ncF || (this._ncF = new THREE.Vector3()), p = this._ncP || (this._ncP = new THREE.Vector3());
      this.camera.getWorldDirection(f); f.y = 0;
      if (f.lengthSq() > 1e-6) {
        f.normalize();
        p.copy(this.camera.position).addScaledVector(f, NEAR_CLIP_M);
        this._nearClip.setFromNormalAndCoplanarPoint(f, p);
      }
    }
    this.composer.render();
  }
}
