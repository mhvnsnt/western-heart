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

  update(dt, fighterA, fighterB) {
    const t = performance.now() * 0.001;
    if (this._stage) this._stage.update(dt, t, fighterA, fighterB);

    // dynamic fighting camera
    // Stream 3: stages may declare camDist (cage interiors, backstage rooms)
    // to pull the camera inside their geometry, and camAngle (degrees) to
    // orbit the camera around the target for cluttered stages.
    const camScale = ((this._stage && this._stage.def.camDist) || 7) / 7;
    const camAng = (((this._stage && this._stage.def.camAngle) || 0) * Math.PI) / 180;
    let baseX = Math.sin(camAng) * 7 * camScale, baseZ = Math.cos(camAng) * 7 * camScale;
    let baseY = 1.8, lookY = 1.0;
    if (fighterA && fighterB) {
      const mid = (fighterA.root.position.x + fighterB.root.position.x) / 2;
      const spread = Math.abs(fighterA.root.position.x - fighterB.root.position.x);
      baseZ = Math.max(5.6, Math.min(12, 5.4 + spread * 0.85)) * camScale;
      baseX = mid * 0.6;
      const maxY = Math.max(fighterA.root.position.y, fighterB.root.position.y);
      baseY = 1.75 + maxY * 0.45;
      lookY = 1.0 + maxY * 0.25;
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
    this.camera.position.x += (baseX - this.camera.position.x) * Math.min(1, dt * 4);
    this.camera.position.z += (baseZ - this.camera.position.z) * Math.min(1, dt * 3);
    this.camera.position.y += (baseY - this.camera.position.y) * Math.min(1, dt * 4);
    this._lookY += (lookY - this._lookY) * Math.min(1, dt * 4);

    let ox = 0, oy = 0;
    if (this._shakeT > 0) {
      this._shakeT -= dt;
      const k = Math.max(0, this._shakeT) * this._shakeMag * 14;
      ox = (Math.random() - 0.5) * k; oy = (Math.random() - 0.5) * k;
      if (this._shakeT <= 0) this._shakeMag = 0;
    }
    this.camera.position.x += ox; this.camera.position.y += oy;
    if (this._stage && this._stage.def && this._stage.def.camTgt) {
      const t = this._stage.def.camTgt;
      this.camera.lookAt(t[0], this._lookY, t[2]);
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

  render() { this.composer.render(); }
}
