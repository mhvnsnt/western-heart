/* preview3d.js — full-screen fighter preview.
   Vendored three.js (./vendor/three.module.js + GLTFLoader). Soldier.glb base rig
   for NEW FIGHTER; roster fighters load their real GLB from game/assets/models/
   via loadModel() (data/ROSTER-BASE.json). Fighter ALWAYS visible, full-body,
   centered slightly left of screen so the right rail never covers it.
   Slow auto-rotate, drag-orbit, scroll/pinch zoom.
   Equip visuals: labeled socket-proxy rings (honest placeholders — real ymg/obj
   meshes are not wired yet). */
import * as THREE from 'three';
import { GLTFLoader } from '../vendor/addons/loaders/GLTFLoader.js';
import { clone as skeletonClone } from '../vendor/addons/utils/SkeletonUtils.js';

const SKIN_TONES = ['#f7c2a1','#e8a87c','#c98d5e','#a06a42','#7c4a2d','#5d3320','#3d2114','#2a150c'];
const SOLDIER_GLB = 'assets/Soldier.glb';

export class Preview3D {
  constructor(canvas){
    this.canvas = canvas;
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias:true, alpha:false, preserveDrawingBuffer:true });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
    this.clock = new THREE.Clock();
    this.mixers = [];
    this.proxyRings = new Map();   // slotId -> ring mesh
    this.dummy = null;
    this.onReady = null;
    this.modelUrl = null;          // currently loaded base model
    this._loading = false;

    // orbit state
    this.az = 0.5; this.el = 0.06; this.dist = 4.6;
    this.targetAz = this.az; this.targetEl = this.el; this.targetDist = this.dist;
    this.autoRotate = true;
    this.focus = new THREE.Vector3(-0.35, 1.05, 0); // fighter offset left-of-center

    this._buildStage();
    this._bindInput();
    this._resize();
    addEventListener('resize', ()=>this._resize());
    this._animate();
    this._loadFighter();
  }

  _buildStage(){
    // gradient backdrop (arena-neutral) + floor
    const c = document.createElement('canvas'); c.width = c.height = 512;
    const g = c.getContext('2d');
    const grad = g.createLinearGradient(0,0,0,512);
    grad.addColorStop(0,'#1b2233'); grad.addColorStop(.55,'#10141d'); grad.addColorStop(1,'#07090d');
    g.fillStyle = grad; g.fillRect(0,0,512,512);
    const tex = new THREE.CanvasTexture(c);
    this.scene.background = tex;

    const floor = new THREE.Mesh(
      new THREE.CircleGeometry(9, 48),
      new THREE.MeshStandardMaterial({ color:0x141a26, roughness:.9, metalness:.05 })
    );
    floor.rotation.x = -Math.PI/2; floor.position.x = -0.35;
    floor.receiveShadow = true;
    this.scene.add(floor);
    const ring = new THREE.Mesh(
      new THREE.RingGeometry(1.15, 1.22, 64),
      new THREE.MeshBasicMaterial({ color:0xe8b64c, transparent:true, opacity:.5, side:THREE.DoubleSide })
    );
    ring.rotation.x = -Math.PI/2; ring.position.set(-0.35, 0.01, 0);
    this.scene.add(ring);

    this.scene.add(new THREE.HemisphereLight(0xbfd4ff, 0x1a1410, 1.05));
    const key = new THREE.DirectionalLight(0xffffff, 2.2);
    key.position.set(3, 6, 4); key.castShadow = true;
    key.shadow.mapSize.set(1024,1024);
    this.scene.add(key);
    const rim = new THREE.DirectionalLight(0x7fd4ff, 1.1);
    rim.position.set(-4, 3, -4); this.scene.add(rim);

    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  }

  _bindInput(){
    const cv = this.canvas;
    let dragging = false, lx=0, ly=0;
    cv.addEventListener('pointerdown', e=>{ dragging=true; lx=e.clientX; ly=e.clientY; this.autoRotate=false; cv.setPointerCapture(e.pointerId); });
    cv.addEventListener('pointermove', e=>{
      if(!dragging) return;
      const dx=e.clientX-lx, dy=e.clientY-ly; lx=e.clientX; ly=e.clientY;
      this.targetAz -= dx*0.008;
      this.targetEl = THREE.MathUtils.clamp(this.targetEl + dy*0.005, -0.15, 0.6);
    });
    const end = ()=>{ dragging=false; setTimeout(()=>{ if(!dragging) this.autoRotate=true; }, 4000); };
    cv.addEventListener('pointerup', end); cv.addEventListener('pointercancel', end);
    cv.addEventListener('wheel', e=>{
      e.preventDefault();
      this.targetDist = THREE.MathUtils.clamp(this.targetDist + Math.sign(e.deltaY)*0.35, 2.2, 9);
    }, { passive:false });
    // pinch zoom
    let pinchD = 0;
    cv.addEventListener('touchmove', e=>{
      if(e.touches.length===2){
        const d = Math.hypot(e.touches[0].clientX-e.touches[1].clientX, e.touches[1].clientY-e.touches[1].clientY);
        if(pinchD) this.targetDist = THREE.MathUtils.clamp(this.targetDist - (d-pinchD)*0.01, 2.2, 9);
        pinchD = d;
      }
    }, { passive:true });
    cv.addEventListener('touchend', ()=>{ pinchD = 0; });
  }

  _resize(){
    const w = innerWidth, h = innerHeight;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w/h;
    this.camera.updateProjectionMatrix();
  }

  _loadFighter(){
    this.loadModel(SOLDIER_GLB);
  }

  /* ---- dynamic base-model loading: roster GLBs from game/assets/models/ ----
     Disposes the old fighter + dummy, loads the new GLB, re-collects materials
     and bones, plays Idle (or first clip). On failure falls back to the Soldier
     base rig so the suite never bricks on a missing model. */
  loadModel(url){
    if(!url || url===this.modelUrl || this._loading) return;
    this._loading = true;
    this.modelUrl = url;
    if(this.fighter){ this.scene.remove(this.fighter); this._disposeObj(this.fighter); this.fighter=null; this.mats=null; this.baseColors=null; this.bones=null; }
    if(this.dummy){ this.scene.remove(this.dummy); this.dummy=null; }
    this.clearAllProxies();
    this.mixers = [];
    new GLTFLoader().load(url, glb=>{
      this.fighter = glb.scene;
      this.fighter.position.set(-0.35, 0, 0);
      this.fighter.traverse(o=>{ if(o.isMesh){ o.castShadow = true; } });
      this.scene.add(this.fighter);
      // collect materials for skin-tone control (custom base only)
      this.mats = [];
      this.fighter.traverse(o=>{ if(o.isMesh){ (Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{ if(!this.mats.includes(m)) this.mats.push(m); }); } });
      this.baseColors = this.mats.map(m=>m.color.clone());
      // Idle animation so the fighter is ALIVE, never T-posed
      if(glb.animations && glb.animations.length){
        const idle = glb.animations.find(a=>/idle/i.test(a.name)) || glb.animations[0];
        const mixer = new THREE.AnimationMixer(this.fighter);
        mixer.clipAction(idle).play();
        this.mixers.push(mixer);
      }
      // bone lookup for socket anchors (mixamorig prefix stripped when present)
      this.bones = {};
      this.fighter.traverse(o=>{ if(o.isBone) this.bones[o.name.replace('mixamorig:','')] = o; });
      this._loading = false;
      this._hideLoader();
      if(this.onReady) this.onReady();
    }, undefined, err=>{
      console.error('model failed to load:', url, err);
      this._loading = false;
      this._hideLoader();
      if(url!==SOLDIER_GLB){ this.modelUrl=null; this.loadModel(SOLDIER_GLB); }
    });
  }

  _disposeObj(root){
    root.traverse(o=>{
      if(o.isMesh){
        if(o.geometry) o.geometry.dispose();
        const ms = Array.isArray(o.material)?o.material:[o.material];
        ms.forEach(m=>{ if(m && m.dispose) m.dispose(); });
      }
    });
  }

  _hideLoader(){ const l=document.getElementById('loader'); if(l) l.style.display='none'; }

  /* ---- appearance controls ---- */
  setSkinTone(hex){
    if(!this.mats) return;
    const tone = new THREE.Color(hex);
    this.mats.forEach((m,i)=>{
      // skin tone tints the body toward the chosen tone (mix with original so armor reads)
      m.color.copy(this.baseColors[i]).lerp(tone, 0.72);
    });
  }
  setProportions({ height=1, weight=1, muscle=1 }={}){
    if(!this.fighter) return;
    this.fighter.scale.set(weight*(1+(muscle-1)*0.5), height, weight*(1+(muscle-1)*0.5));
  }
  setBodyType(preset){
    // No Mercy body-type presets -> scale recipes
    this.setProportions(preset);
  }

  /* ---- socket proxy rings (honest placeholders for pending part geometry) ---- */
  _anchorPos(anchorName){
    if(this.bones && this.bones[anchorName]){
      const v = new THREE.Vector3();
      this.bones[anchorName].getWorldPosition(v);
      return v;
    }
    return new THREE.Vector3(-0.35, 1.2, 0);
  }
  setProxy(slotId, anchorName, colorHex, label){
    this.clearProxy(slotId);
    if(!anchorName) return;
    const pos = this._anchorPos(anchorName);
    const geo = new THREE.TorusGeometry(0.22, 0.022, 12, 40);
    const mat = new THREE.MeshBasicMaterial({ color:new THREE.Color(colorHex||'#e8b64c'), transparent:true, opacity:.9 });
    const ring = new THREE.Mesh(geo, mat);
    ring.position.copy(pos);
    ring.userData.slotId = slotId;
    ring.userData.label = label || slotId;
    ring.userData.phase = Math.random()*Math.PI*2;
    this.scene.add(ring);
    this.proxyRings.set(slotId, ring);
  }
  clearProxy(slotId){
    const r = this.proxyRings.get(slotId);
    if(r){ this.scene.remove(r); r.geometry.dispose(); r.material.dispose(); this.proxyRings.delete(slotId); }
  }
  clearAllProxies(){ [...this.proxyRings.keys()].forEach(k=>this.clearProxy(k)); }

  /* ---- moveset dummy opponent (WWE two-fighter preview) ---- */
  setDummyVisible(show){
    if(show && !this.dummy && this.fighter){
      // SkeletonUtils.clone rebinds the skinned mesh to the CLONED bones —
      // plain .clone() shares the original skeleton and the dummy collapses
      // onto the fighter's position instead of rendering at its own.
      this.dummy = skeletonClone(this.fighter);
      this.dummy.traverse(o=>{ if(o.isMesh){ o.material = o.material.clone(); o.material.color.multiplyScalar(0.55); o.castShadow=true; } });
      this.scene.add(this.dummy);
    } else if(!show && this.dummy){
      this.scene.remove(this.dummy); this.dummy = null;
    }
  }

  snapshot(){
    this.renderer.render(this.scene, this.camera);
    return this.canvas.toDataURL('image/jpeg', 0.85);
  }

  _animate(){
    requestAnimationFrame(()=>this._animate());
    const dt = Math.min(this.clock.getDelta(), 0.05);
    this.mixers.forEach(m=>m.update(dt));
    if(this.autoRotate) this.targetAz += dt*0.25;
    this.az += (this.targetAz-this.az)*0.08;
    this.el += (this.targetEl-this.el)*0.08;
    this.dist += (this.targetDist-this.dist)*0.1;
    const t = performance.now()*0.001;
    // pulse proxy rings
    for(const r of this.proxyRings.values()){
      const s = 1 + Math.sin(t*3 + r.userData.phase)*0.08;
      r.scale.set(s,s,s);
      r.rotation.y = t*0.8;
      r.material.opacity = 0.65 + Math.sin(t*3 + r.userData.phase)*0.25;
    }
    const fx = this.focus.x + Math.sin(this.az)*Math.cos(this.el)*this.dist;
    const fz = this.focus.z + Math.cos(this.az)*Math.cos(this.el)*this.dist;
    const fy = this.focus.y + Math.sin(this.el)*this.dist;
    this.camera.position.set(fx, fy, fz);
    this.camera.lookAt(this.focus);
    // dummy opponent holds a fixed screen offset from the fighter (orbits with the camera):
    // offset along the camera's screen-left axis, same depth as the fighter -> same apparent size
    if(this.dummy && this.fighter){
      const lx = -Math.cos(this.az), lz = Math.sin(this.az);
      this.dummy.position.set(
        this.fighter.position.x + lx*1.75, 0,
        this.fighter.position.z + lz*1.75);
      this.dummy.lookAt(this.fighter.position.x, 1.0, this.fighter.position.z);
    }
    this.renderer.render(this.scene, this.camera);
  }
}

export { SKIN_TONES };
