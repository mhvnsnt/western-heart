/* ============================================================
   WESTERN HEART — Shrine of the Blade (stage)
   Stone temple courtyard at dusk, per prototype/stages/shrine.json:
     • dusk lighting: warm directional #ff9a5c (setting sun) over
       cool ambient #2a2a4a
     • stone floor, dark wood panels behind the arena
     • paper lanterns (warm point lights) + tōrō stone lanterns
       at the arena edges
     • falling maple leaves particle system
     • gradient skybox: deep indigo → ember orange
   Arena 16.8 wide (fighters clamp at ±8.4).
   Built procedurally (canvas textures, no external images).
   ============================================================ */
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

export class Arena {
  constructor(canvas) {
    this.isMobile = /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent);

    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: !this.isMobile, powerPreference: 'high-performance' });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.15;

    this.scene = new THREE.Scene();
    this.scene.background = this._makeSky();
    this.scene.fog = new THREE.Fog(0x1a1428, 20, 65);

    this.camera = new THREE.PerspectiveCamera(45, 1, 0.1, 200);
    this.camera.position.set(0, 1.8, 7);
    this.camera.lookAt(0, 1.0, 0);

    this._lanterns = [];
    this._buildLights();
    this._buildArena();
    this._buildLeaves();

    this._shakeT = 0; this._shakeMag = 0; this._lookY = 1.0;

    this.composer = new EffectComposer(this.renderer);
    this.composer.addPass(new RenderPass(this.scene, this.camera));
    this.bloom = new UnrealBloomPass(new THREE.Vector2(256, 256), this.isMobile ? 0.6 : 0.85, 0.7, 0.8);
    this.composer.addPass(this.bloom);
    this.composer.addPass(new OutputPass());

    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  /* ---------- procedural textures ---------- */
  _makeSky() {
    const c = document.createElement('canvas'); c.width = 16; c.height = 256;
    const ctx = c.getContext('2d');
    const g = ctx.createLinearGradient(0, 0, 0, 256);
    g.addColorStop(0.0, '#120e33');  // deep indigo zenith
    g.addColorStop(0.45, '#3a2358'); // violet
    g.addColorStop(0.72, '#a34a3c');  // ember
    g.addColorStop(0.88, '#ff7a3c');  // ember orange at horizon
    g.addColorStop(1.0, '#2a1626');   // below-horizon ground haze
    ctx.fillStyle = g; ctx.fillRect(0, 0, 16, 256);
    const tex = new THREE.CanvasTexture(c);
    tex.colorSpace = THREE.SRGBColorSpace;
    return tex;
  }

  _makeStoneTexture(repeat) {
    const c = document.createElement('canvas'); c.width = c.height = 512;
    const ctx = c.getContext('2d');
    ctx.fillStyle = '#3a3440'; ctx.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 9000; i++) {
      const v = 30 + Math.random() * 55;
      ctx.fillStyle = `rgba(${v},${v - 4},${v - 2},${Math.random() * 0.4})`;
      ctx.fillRect(Math.random() * 512, Math.random() * 512, 2, 2);
    }
    ctx.strokeStyle = 'rgba(10,8,12,0.9)'; ctx.lineWidth = 4;
    const step = 128;
    for (let x = 0; x <= 512; x += step) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 512); ctx.stroke(); }
    for (let y = 0; y <= 512; y += step) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(512, y); ctx.stroke(); }
    ctx.strokeStyle = 'rgba(200,160,140,0.10)'; ctx.lineWidth = 1;
    for (let x = 0; x <= 512; x += step) { ctx.beginPath(); ctx.moveTo(x + 2, 0); ctx.lineTo(x + 2, 512); ctx.stroke(); }
    const tex = new THREE.CanvasTexture(c);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    tex.repeat.set(repeat, repeat);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 4;
    return tex;
  }

  _makeWoodTexture() {
    const c = document.createElement('canvas'); c.width = c.height = 256;
    const ctx = c.getContext('2d');
    ctx.fillStyle = '#241610'; ctx.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 46; i++) { // vertical planks
      const x = Math.random() * 256;
      ctx.fillStyle = `rgba(${10 + Math.random() * 24},${6 + Math.random() * 12},4,0.55)`;
      ctx.fillRect(x, 0, 2 + Math.random() * 5, 256);
    }
    ctx.fillStyle = 'rgba(0,0,0,0.35)';
    for (let x = 0; x < 256; x += 64) ctx.fillRect(x, 0, 2, 256);
    const tex = new THREE.CanvasTexture(c);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
    tex.colorSpace = THREE.SRGBColorSpace;
    return tex;
  }

  _buildLights() {
    // Cool ambient dusk (#2a2a4a) from above
    this.scene.add(new THREE.HemisphereLight(0x4a4a7a, 0x1a1426, 0.85));

    // Setting sun — warm directional #ff9a5c, the only shadow caster
    const sun = new THREE.DirectionalLight(0xff9a5c, 1.35);
    sun.position.set(-11, 6.5, 5);
    sun.castShadow = true;
    sun.shadow.mapSize.set(this.isMobile ? 1024 : 2048, this.isMobile ? 1024 : 2048);
    sun.shadow.camera.near = 1; sun.shadow.camera.far = 50;
    sun.shadow.camera.left = -12; sun.shadow.camera.right = 12;
    sun.shadow.camera.top = 12; sun.shadow.camera.bottom = -12;
    sun.shadow.bias = -0.0006;
    this.scene.add(sun);

    // Faint cool rim so fighter backs don't go black
    const rim = new THREE.DirectionalLight(0x5a6ab0, 0.4);
    rim.position.set(8, 6, -7); this.scene.add(rim);
  }

  _buildArena() {
    // --- Stone courtyard floor ---
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(140, 140),
      new THREE.MeshStandardMaterial({ map: this._makeStoneTexture(30), roughness: 0.9, metalness: 0.05, color: 0xa89a90 })
    );
    ground.rotation.x = -Math.PI / 2; ground.position.y = -0.05; ground.receiveShadow = true;
    this.scene.add(ground);

    // --- Raised stone fighting platform (16.8 wide per shrine.json) ---
    const platMat = new THREE.MeshStandardMaterial({ map: this._makeStoneTexture(7), roughness: 0.85, metalness: 0.08, color: 0xb5a498 });
    const plat = new THREE.Mesh(new THREE.CylinderGeometry(9.2, 9.6, 0.5, 8), platMat);
    plat.position.y = -0.25; plat.rotation.y = Math.PI / 8; plat.receiveShadow = true; this.scene.add(plat);

    // ember trim ring
    const trim = new THREE.Mesh(new THREE.TorusGeometry(8.9, 0.09, 12, 8),
      new THREE.MeshBasicMaterial({ color: 0xff7a3c }));
    trim.rotation.x = Math.PI / 2; trim.rotation.z = Math.PI / 8; trim.position.y = 0.02; this.scene.add(trim);

    // --- Dark wood temple panels behind the arena ---
    const woodMat = new THREE.MeshStandardMaterial({ map: this._makeWoodTexture(), roughness: 0.9, metalness: 0, color: 0x9a7a62 });
    for (let i = 0; i < 10; i++) {
      const a = (i / 10) * Math.PI * 2 + Math.PI / 10;
      const r = 13.5;
      const panel = new THREE.Mesh(new THREE.BoxGeometry(8.6, 4.6, 0.5), woodMat);
      panel.position.set(Math.cos(a) * r, 2.2, Math.sin(a) * r);
      panel.lookAt(0, 2.2, 0);
      panel.castShadow = false; panel.receiveShadow = true;
      this.scene.add(panel);
      // simple roof beam on each panel
      const beam = new THREE.Mesh(new THREE.BoxGeometry(9.4, 0.5, 1.2),
        new THREE.MeshStandardMaterial({ color: 0x17100a, roughness: 0.9 }));
      beam.position.set(Math.cos(a) * r, 4.7, Math.sin(a) * r);
      beam.lookAt(0, 4.7, 0);
      this.scene.add(beam);
    }

    // --- Paper lanterns on posts (warm point lights) ---
    const postMat = new THREE.MeshStandardMaterial({ color: 0x1c120a, roughness: 0.8 });
    const paperMat = new THREE.MeshStandardMaterial({
      color: 0xffd9a0, emissive: 0xff9a3c, emissiveIntensity: 1.6, roughness: 0.9,
    });
    for (let i = 0; i < 5; i++) {
      const a = (i / 5) * Math.PI * 2 + Math.PI / 5;
      const px = Math.cos(a) * 11.4, pz = Math.sin(a) * 11.4;
      const post = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.14, 3.0, 8), postMat);
      post.position.set(px, 1.5, pz); post.castShadow = true; this.scene.add(post);
      const lantern = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 0.62, 12), paperMat);
      lantern.position.set(px, 3.2, pz); this.scene.add(lantern);
      const capT = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.38, 0.08, 12), postMat);
      capT.position.set(px, 3.55, pz); this.scene.add(capT);
      const capB = capT.clone(); capB.position.y = 2.85; this.scene.add(capB);
      const light = new THREE.PointLight(0xff9a4d, 12, 20, 2);
      light.position.set(px, 3.2, pz); this.scene.add(light);
      this._lanterns.push({ light, base: 12, phase: Math.random() * 10 });
    }

    // --- Tōrō stone lanterns at the arena edges ---
    const stoneMat = new THREE.MeshStandardMaterial({ color: 0x6a6a70, roughness: 0.95 });
    const fireMat = new THREE.MeshStandardMaterial({ color: 0xffc27a, emissive: 0xff8a2a, emissiveIntensity: 2.2 });
    const toroAt = (x, z, ry, withLight) => {
      const g = new THREE.Group();
      const base = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.25, 0.9), stoneMat); base.position.y = 0.12; g.add(base);
      const pillar = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.26, 1.1, 8), stoneMat); pillar.position.y = 0.8; g.add(pillar);
      const mid = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.18, 0.8), stoneMat); mid.position.y = 1.44; g.add(mid);
      const firebox = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.5, 0.62), stoneMat); firebox.position.y = 1.78; g.add(firebox);
      const glow = new THREE.Mesh(new THREE.BoxGeometry(0.66, 0.2, 0.66), fireMat); glow.position.y = 1.78; g.add(glow);
      const roof = new THREE.Mesh(new THREE.ConeGeometry(0.72, 0.5, 4), stoneMat); roof.position.y = 2.28; roof.rotation.y = Math.PI / 4; g.add(roof);
      g.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
      if (withLight) {
        const light = new THREE.PointLight(0xff8a3a, 6, 9, 2);
        light.position.y = 1.78; g.add(light);
        this._lanterns.push({ light, base: 6, phase: Math.random() * 10 });
      }
      g.position.set(x, 0, z); g.rotation.y = ry;
      this.scene.add(g);
    };
    toroAt(-9.4, -2.6, 0.4, true); toroAt(9.4, 2.6, -2.7, false);
    toroAt(-9.4, 2.6, -0.4, false); toroAt(9.4, -2.6, 2.7, true);

    // --- Distant mountain silhouettes ---
    const mtnMat = new THREE.MeshBasicMaterial({ color: 0x0d0a20 });
    for (let i = 0; i < 7; i++) {
      const w = 14 + Math.random() * 16, h = 8 + Math.random() * 14;
      const m = new THREE.Mesh(new THREE.ConeGeometry(w / 2, h, 5), mtnMat);
      const a = Math.PI + (i / 6 - 0.5) * 1.6; // behind the shrine
      m.position.set(Math.sin(a) * 46, h / 2 - 1, -Math.cos(a) * 46);
      this.scene.add(m);
    }
  }

  /* ---------- Falling maple leaves (instanced quads) ---------- */
  _buildLeaves() {
    const N = this.isMobile ? 60 : 90;
    const geo = new THREE.PlaneGeometry(0.16, 0.16);
    const mat = new THREE.MeshBasicMaterial({ side: THREE.DoubleSide, transparent: true, opacity: 0.95 });
    this._leaves = new THREE.InstancedMesh(geo, mat, N);
    this._leaves.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    this._leaves.frustumCulled = false;
    const colors = [0xd43a1a, 0xe86a1e, 0xc9202a, 0xf0a030];
    this._leafData = [];
    const dummy = new THREE.Object3D();
    const col = new THREE.Color();
    for (let i = 0; i < N; i++) {
      this._leafData.push({
        x: (Math.random() - 0.5) * 26, y: Math.random() * 9, z: (Math.random() - 0.5) * 18,
        fall: 0.35 + Math.random() * 0.45, sway: Math.random() * 10, swayAmp: 0.4 + Math.random() * 0.8,
        rot: Math.random() * Math.PI * 2, rotV: (Math.random() - 0.5) * 3,
      });
      dummy.position.set(0, -99, 0); dummy.updateMatrix();
      this._leaves.setMatrixAt(i, dummy.matrix);
      col.setHex(colors[(Math.random() * colors.length) | 0]);
      this._leaves.setColorAt(i, col);
    }
    this.scene.add(this._leaves);
  }

  _updateLeaves(dt, t) {
    const dummy = Arena._dummy || (Arena._dummy = new THREE.Object3D());
    for (let i = 0; i < this._leafData.length; i++) {
      const L = this._leafData[i];
      L.y -= L.fall * dt;
      L.sway += dt * 1.6;
      L.rot += L.rotV * dt;
      if (L.y < 0) { L.y = 8 + Math.random() * 2; L.x = (Math.random() - 0.5) * 26; }
      dummy.position.set(
        L.x + Math.sin(L.sway) * L.swayAmp,
        L.y,
        L.z + Math.cos(L.sway * 0.7) * L.swayAmp * 0.5
      );
      dummy.rotation.set(L.rot, L.rot * 0.7, L.rot * 0.4);
      dummy.updateMatrix();
      this._leaves.setMatrixAt(i, dummy.matrix);
    }
    this._leaves.instanceMatrix.needsUpdate = true;
  }

  shake(mag = 0.25, dur = 0.18) { this._shakeMag = Math.max(this._shakeMag, mag); this._shakeT = Math.max(this._shakeT, dur); }

  update(dt, fighterA, fighterB) {
    const t = performance.now() * 0.001;
    // lantern flicker
    for (const ln of this._lanterns) {
      const f = 0.8 + Math.sin(t * 9 + ln.phase) * 0.12 + Math.sin(t * 21 + ln.phase) * 0.08;
      ln.light.intensity = ln.base * f;
    }
    // leaves drift
    this._updateLeaves(dt, t);

    // dynamic fighting camera
    let baseX = 0, baseZ = 7, baseY = 1.8, lookY = 1.0;
    if (fighterA && fighterB) {
      const mid = (fighterA.root.position.x + fighterB.root.position.x) / 2;
      const spread = Math.abs(fighterA.root.position.x - fighterB.root.position.x);
      baseZ = Math.max(5.6, Math.min(12, 5.4 + spread * 0.85));
      baseX = mid * 0.6;
      const maxY = Math.max(fighterA.root.position.y, fighterB.root.position.y);
      baseY = 1.75 + maxY * 0.45;
      lookY = 1.0 + maxY * 0.25;
    }
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
    this.camera.lookAt(this.camera.position.x - ox, this._lookY, 0);
  }

  resize() {
    const w = window.innerWidth, h = window.innerHeight;
    this.renderer.setSize(w, h, false);
    this.composer.setSize(w, h);
    this.camera.aspect = w / h; this.camera.updateProjectionMatrix();
  }

  render() { this.composer.render(); }
}
