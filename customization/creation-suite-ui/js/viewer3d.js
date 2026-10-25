/* viewer3d.js — three.js preview viewport for the Creation Suite.
   three.js is MIT. GLTFLoader vendored at ../create-fighter/vendor/addons/loaders/GLTFLoader.js.
   Phone-first orbit: drag to rotate, pinch/wheel to zoom. Fighter stays full-screen, never covered. */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
/* Universal rig compatibility (owner directive 2026-10-24 19:54 CDT): sockets
   resolve through canonical bones, so T7 / Cape / Mixamo / Rigify / MB-Lab /
   Tripo rigs all place parts correctly instead of falling back to (0,1.6,0). */
import { resolveBonesFromObject3D, SOCKET_CANONICAL, BONE_ALIASES, normalizeBoneName } from 'wh-creation-suite/rig-adapter.js';

/* suite socket -> bone names (bone world positions are exact under skinning scale) */
const SOCKET_BONES = {
  head:  { bones:['Head'],            off:[0, 0.03, 0] },
  face:  { bones:['Head'],            off:[0, -0.01, 0.09] },
  hands: { bones:['RightHand'],       off:[0, 0, 0] },
  chest: { bones:['Spine2','Spine1'], off:[0, 0, 0.10] },
  waist: { bones:['Hips'],            off:[0, 0, 0.08] },
};

export class SuiteViewer {
  constructor(canvas){
    this.canvas = canvas;
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias:true, alpha:true, preserveDrawingBuffer:true });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0c0e14);
    this.camera = new THREE.PerspectiveCamera(38, 1, 0.01, 100);
    this.camTarget = new THREE.Vector3(0, 1.0, 0);
    this.camDist = 3.4; this.theta = 0.35; this.phi = 1.35;
    this.loader = new GLTFLoader();
    this.model = null; this.modelBox = null;
    this.parts = new Map(); // partId -> { group, def, placement }
    this.markers = new Map();
    this.ready = false; this.onReady = null;

    const hemi = new THREE.HemisphereLight(0xffffff, 0x223, 1.1); this.scene.add(hemi);
    const key = new THREE.DirectionalLight(0xffffff, 2.2); key.position.set(2.5, 4, 3); this.scene.add(key);
    const rim = new THREE.DirectionalLight(0x88aaff, 0.9); rim.position.set(-3, 2, -2.5); this.scene.add(rim);
    const fill = new THREE.DirectionalLight(0xffe0b8, 0.5); fill.position.set(0, 1, 4); this.scene.add(fill);

    // ground disc (arena feel, original art)
    const disc = new THREE.Mesh(
      new THREE.CircleGeometry(1.6, 48),
      new THREE.MeshStandardMaterial({ color:0x141926, roughness:0.9, metalness:0.1 }));
    disc.rotation.x = -Math.PI/2; disc.position.y = 0.001; this.scene.add(disc);
    const ring = new THREE.Mesh(
      new THREE.RingGeometry(1.55, 1.62, 64),
      new THREE.MeshBasicMaterial({ color:0xe8b64c, transparent:true, opacity:0.55, side:THREE.DoubleSide }));
    ring.rotation.x = -Math.PI/2; ring.position.y = 0.002; this.scene.add(ring);
    this.disc = disc; this.ring = ring;

    this._bindInput();
    this._resize();
    addEventListener('resize', ()=>this._resize());
    this._tick();
  }
  _resize(){
    const w = innerWidth, h = innerHeight;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w/h; this.camera.updateProjectionMatrix();
  }
  _bindInput(){
    let drag=null, pinch=0;
    const el = this.canvas;
    el.addEventListener('pointerdown', e=>{ el.setPointerCapture(e.pointerId); drag={x:e.clientX,y:e.clientY}; });
    el.addEventListener('pointermove', e=>{
      if(!drag) return;
      this.theta -= (e.clientX-drag.x)*0.008;
      this.phi = Math.min(1.65, Math.max(0.55, this.phi-(e.clientY-drag.y)*0.006));
      drag={x:e.clientX,y:e.clientY};
    });
    el.addEventListener('pointerup', ()=>drag=null);
    el.addEventListener('pointercancel', ()=>drag=null);
    el.addEventListener('wheel', e=>{ this.camDist=Math.min(8,Math.max(1.2,this.camDist+e.deltaY*0.002)); }, {passive:true});
    el.addEventListener('touchmove', e=>{
      if(e.touches.length===2){
        const d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX, e.touches[0].clientY-e.touches[1].clientY);
        if(pinch) this.camDist=Math.min(8,Math.max(1.2,this.camDist-(d-pinch)*0.008));
        pinch=d;
      }
    }, {passive:true});
    el.addEventListener('touchend', ()=>pinch=0);
  }
  _tick(){
    if(this.paused) return;
    requestAnimationFrame(()=>this._tick());
    this._frame();
  }
  _frame(){
    const t=this.camTarget;
    this.camera.position.set(
      t.x + this.camDist*Math.sin(this.phi)*Math.sin(this.theta),
      t.y + this.camDist*Math.cos(this.phi),
      t.z + this.camDist*Math.sin(this.phi)*Math.cos(this.theta));
    this.camera.lookAt(t);
    this.renderer.render(this.scene, this.camera);
  }
  pause(){ this.paused = true; this._frame(); }   // one last clean frame, then hold
  resume(){ if(this.paused){ this.paused=false; this._tick(); } }
  clearParts(){
    for(const pid of [...this.parts.keys()]) this.detachPart(pid);
    for(const key of [...this.markers.keys()]) this.clearMarker(key);
    if(this.texSwaps) for(const id of [...this.texSwaps.keys()]) this.restoreTexture(id);
    this._baseMeshState = null; // per-part toggle overrides (Phase 1: SmutBase-6 parts)
    this._baseNames = null;     // scene mesh-name index (rebuilt on next findBaseMeshes)
    this._skinOrig = null;      // skin-tone originals (reset per model)
    this.boneMap = null;        // canonical -> bone (reset per model)
    this.rigProfile = null;     // TOOLS tab display data (reset per model)
  }
  /* ---- Phase 1: per-part toggles on the BASE model (fighter's own meshes) ----
     Logical parts from data/fighter-parts.json map to GLB mesh names.
     Scene names vary by export: exact (model.glb), "<mesh>.###" GLTF dedup,
     "<mesh>_N" rig-export splits (tsuyu Holo_001 -> Holo_001_1/_2), and
     truncated long names (rigged tsuyu *_Body_bel -> *_Body_be).
     Rule: when the exact name exists in the scene, only exact (+dotted)
     matches count; otherwise fall back to _N-strip and long-prefix rules.
     (This keeps Mirko_001 distinct from the Mirko body while still finding
     Holo_001_1 for the Holo_001 part.) */
  _baseNameSet(){
    if(!this._baseNames && this.model){
      this._baseNames = new Set();
      this.model.traverse(o=>{ if(o.isMesh) this._baseNames.add(o.name||''); });
    }
    return this._baseNames || new Set();
  }
  _meshNameMatch(n, meshName, names){
    if(!n || !meshName) return false;
    if(n===meshName || n.startsWith(meshName+'.')) return true;
    if(names.has(meshName)) return false; // exact name exists: no fuzzy matching
    const m0 = n.match(/^(.*)_\d+$/);
    if(m0 && m0[1]===meshName) return true; // "<mesh>_N" split of the same part
    const m = Math.min(n.length, meshName.length);
    if(m >= 24 && n.slice(0, m)===meshName.slice(0, m)) return true; // truncated long name
    return false;
  }
  findBaseMeshes(meshName){
    const out = [];
    if(!this.model || !meshName) return out;
    const names = this._baseNameSet();
    this.model.traverse(o=>{
      if(!o.isMesh) return;
      if(this._meshNameMatch(o.name||'', meshName, names)) out.push(o);
    });
    return out;
  }
  baseMeshState(){
    if(!this._baseMeshState) this._baseMeshState = new Map(); // meshName -> {visible, deleted, color}
    return this._baseMeshState;
  }
  /* mode: 'shown' | 'hidden' | 'invisible' | 'deleted'. hidden/invisible/deleted
     all read as not-visible in the viewport; the mode is kept so the layering
     intent (invisible = slot still occupied) and restore semantics survive. */
  setBaseMeshMode(meshName, mode){
    const st = this.baseMeshState();
    const rec = st.get(meshName) || {};
    rec.mode = mode;
    st.set(meshName, rec);
    const vis = (mode==='shown');
    for(const o of this.findBaseMeshes(meshName)){
      o.visible = vis;
      if(o.userData) o.userData.whPartMode = mode;
    }
  }
  setBaseMeshColor(meshName, hex){
    const st = this.baseMeshState();
    const rec = st.get(meshName) || {}; st.set(meshName, rec);
    for(const o of this.findBaseMeshes(meshName)){
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      for(const m of mats){
        if(!m || !m.color) continue;
        if(m.userData._whOrigColor === undefined) m.userData._whOrigColor = m.color.getHex();
        if(hex) m.color.set(hex); else m.color.setHex(m.userData._whOrigColor);
        m.needsUpdate = true;
      }
    }
    if(hex) rec.color = hex; else delete rec.color;
  }
  resetBaseMeshes(){
    if(!this._baseMeshState) return;
    for(const [meshName, rec] of this._baseMeshState){
      for(const o of this.findBaseMeshes(meshName)){
        o.visible = true;
        if(o.userData) delete o.userData.whPartMode;
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        for(const m of mats){
          if(m && m.color && m.userData._whOrigColor !== undefined){ m.color.setHex(m.userData._whOrigColor); m.needsUpdate = true; }
        }
      }
    }
    this._baseMeshState = null;
  }
  loadBase(url){
    return new Promise((res, rej)=>{
      this.loader.load(url, gltf=>{
        this.clearParts();
        if(this.model) this.scene.remove(this.model);
        this.currentUrl = url;
        this.model = gltf.scene;
        this.scene.add(this.model);
        this.modelBox = new THREE.Box3().setFromObject(this.model);
        // bone lookup (mixamorig:/mixamorig prefixes stripped) — exact under skinning scale
        this.bones = {};
        this.model.traverse(o=>{ if(o.isBone) this.bones[o.name.replace(/^mixamorig:?/, '')] = o; });
        /* Universal rig compatibility: canonical bones for THIS model's
           skeleton + a plain-data profile for the TOOLS tab. Exact names
           still win everywhere; the adapter only fires when exact fails. */
        try{
          const rep = resolveBonesFromObject3D(this.model);
          this.boneMap = rep.bones || {};
          this.rigProfile = { boneCount: rep.boneCount, found: rep.found,
            total: rep.total, coverage: rep.coverage, missing: rep.missing,
            namingStyles: rep.namingStyles };
        }catch(e){ this.boneMap = {}; this.rigProfile = null; }
        // frame from the Head bone (bind-pose geometry bbox lies under bone scale)
        const headY = this.boneY('Head', 1.7);
        this.camTarget.set(0, headY*0.55, 0);
        this.camDist = headY*2.6;
        this.headHeight = headY;
        // ground the fighter under the feet, sized to the model
        this.disc.position.y = 0.002; this.ring.position.y = 0.003;
        const dr = Math.max(headY*0.35, 0.3);
        this.disc.scale.setScalar(dr/1.6); this.ring.scale.setScalar(dr/1.6);
        this.ready = true;
        this.onReady && this.onReady();
        res(this.model);
      }, undefined, rej);
    });
  }
  boneY(name, fallback){
    const b = (this.bones && this.bones[name]) || this._canonicalBone(name);
    if(!b) return fallback;
    const v = new THREE.Vector3(); b.getWorldPosition(v); return v.y;
  }
  /* Canonical fallback: a requested T7-style bone name ('LeftArm') resolves
     through the rig adapter to whatever this model's skeleton calls it
     ('upperarm_L' on Cape/MB-Lab rigs, 'upper_arm.L' on Rigify). */
  _canonicalBone(name){
    if(!this.boneMap) return null;
    const norm = normalizeBoneName(name);
    for(const c of Object.keys(BONE_ALIASES)){
      if((BONE_ALIASES[c]||[]).includes(norm) && this.boneMap[c]) return this.boneMap[c];
    }
    return null;
  }
  socketBone(socket){
    const canon = SOCKET_CANONICAL[socket] || SOCKET_CANONICAL.head;
    if(this.boneMap){ for(const c of canon){ if(this.boneMap[c]) return this.boneMap[c]; } }
    const s = SOCKET_BONES[socket] || SOCKET_BONES.head;
    for(const n of s.bones){ if(this.bones && this.bones[n]) return this.bones[n]; }
    return null;
  }
  socketPoint(socket){
    const s = SOCKET_BONES[socket] || SOCKET_BONES.head;
    const out = new THREE.Vector3(0, 1.6, 0);
    const bone = this.socketBone(socket);
    if(!bone) return out;
    bone.getWorldPosition(out);
    const k = (this.headHeight || 1.7) / 1.7;
    if(socket==='face' || socket==='chest' || socket==='waist'){
      const q = new THREE.Quaternion(); bone.getWorldQuaternion(q);
      const fwd = new THREE.Vector3(0,0,1).applyQuaternion(q); // bone-space forward
      const dist = (socket==='face' ? 0.10 : 0.09) * k;
      out.addScaledVector(fwd, dist);
      out.y += (socket==='face' ? -0.015 : 0) * k;
    } else {
      out.x += s.off[0]*k; out.y += s.off[1]*k; out.z += s.off[2]*k;
    }
    return out;
  }
  /* attach a mesh part GLB at a socket with placement {px,py,pz,rx,ry,rz,s}.
     Part geometry is normalized: its bbox center is moved to the group origin, so the
     socket anchor + user nudge fully determine placement even when the source file was
     modeled for a different character (e.g. cyborg-x coords). */
  attachPart(partId, glbUrl, def, placement){
    return new Promise((res, rej)=>{
      this.loader.load(glbUrl, gltf=>{
        this.detachPart(partId);
        const g = new THREE.Group();
        const inner = gltf.scene;
        const bb = new THREE.Box3().setFromObject(inner);
        const c = new THREE.Vector3(); bb.getCenter(c);
        inner.position.sub(c); // visual center -> group origin
        g.add(inner);
        g.userData.geomShift = c;
        this._applyPlacement(g, def, placement);
        this.scene.add(g);
        this.parts.set(partId, { group:g, def, placement:{...placement} });
        res(g);
      }, undefined, rej);
    });
  }
  _applyPlacement(group, def, p){
    const base = this.socketPoint(def.socket || 'head');
    const d = def.offset || [0,0,0];
    group.position.set(base.x + d[0] + (p.px||0), base.y + d[1] + (p.py||0), base.z + d[2] + (p.pz||0));
    // orient the part with the socket bone (part-local +Z = bone facing), then user euler on top
    const bone = this.socketBone(def.socket || 'head');
    const q = new THREE.Quaternion();
    if(bone) bone.getWorldQuaternion(q);
    const user = new THREE.Quaternion().setFromEuler(new THREE.Euler(
      THREE.MathUtils.degToRad(p.rx||0) + (def.rotation?def.rotation[0]:0),
      THREE.MathUtils.degToRad(p.ry||0) + (def.rotation?def.rotation[1]:0),
      THREE.MathUtils.degToRad(p.rz||0) + (def.rotation?def.rotation[2]:0)));
    group.quaternion.copy(q).multiply(user);
    const s = (p.s||1) * (def.scale||1);
    group.scale.setScalar(s);
  }
  updatePlacement(partId, placement){
    const e = this.parts.get(partId); if(!e) return;
    e.placement = {...placement};
    this._applyPlacement(e.group, e.def, e.placement);
  }
  detachPart(partId){
    const e = this.parts.get(partId);
    if(e){ this.scene.remove(e.group); this.parts.delete(partId); }
  }
  getPlacement(partId){ const e=this.parts.get(partId); return e?{...e.placement}:null; }
  /* texture-part marker: shows where a texture part applies (honest: geometry-pending parts) */
  setMarker(key, socket, color, label){
    this.clearMarker(key);
    const m = new THREE.Mesh(
      new THREE.SphereGeometry(0.035, 16, 12),
      new THREE.MeshBasicMaterial({ color:new THREE.Color(color), transparent:true, opacity:0.85 }));
    m.position.copy(this.socketPoint(socket));
    this.scene.add(m); this.markers.set(key, m);
    const n = document.getElementById('part-layer-note');
    if(n) n.textContent = label ? `◈ ${label} — texture part (applies at ${socket} socket)` : '';
  }
  clearMarker(key){ const m=this.markers.get(key); if(m){ this.scene.remove(m); this.markers.delete(key);} }
  /* texture-part swap, mirroring packages/creation-suite/src/parts.js
     swapTexture semantics: match materials by placement texture/material
     name, swap the map live, keep originals for one-call restore. */
  swapTexturePreview(partId, assetUrl, placement){
    if(!this.texSwaps) this.texSwaps = new Map();
    this.restoreTexture(partId);
    if(!this.model || !placement) return Promise.resolve(false);
    const wantTex=(placement.texture||'').toLowerCase(), wantMat=(placement.material||'').toLowerCase();
    const targets=[];
    this.model.traverse(o=>{ if(!o.isMesh) return;
      const mats=Array.isArray(o.material)?o.material:[o.material];
      for(const m of mats){ if(!m) continue;
        const texName=((m.map&&m.map.name)||'').toLowerCase();
        if((wantTex&&texName.includes(wantTex))||(wantMat&&(m.name||'').toLowerCase().includes(wantMat)))
          targets.push({material:m, original:m.map}); } });
    if(!targets.length) return Promise.resolve(false);
    return new Promise(res=>{
      new THREE.TextureLoader().load(assetUrl, tex=>{
        for(const t of targets){ t.material.map=tex; t.material.needsUpdate=true; }
        this.texSwaps.set(partId, {targets});
        res(true);
      }, undefined, ()=>res(false));
    });
  }
  restoreTexture(partId){
    const s=this.texSwaps && this.texSwaps.get(partId); if(!s) return;
    for(const t of s.targets){ t.material.map=t.original; t.material.needsUpdate=true; }
    this.texSwaps.delete(partId);
  }
  /* Skin tone preview (was an empty stub): tint materials whose name — or
     whose mesh's name — mentions skin/body. Meshes with no such material
     keep their authored look; the record still saves the tone for the MPFB
     bake, where skin is the ground truth. Null restores originals. */
  setSkinTone(hex){
    if(!this.model) return;
    if(!this._skinOrig) this._skinOrig = new Map();
    this.model.traverse(o=>{
      if(!o.isMesh) return;
      const mats = Array.isArray(o.material) ? o.material : [o.material];
      const hay = (o.name||'') + ' ' + mats.map(m=>(m&&m.name)||'').join(' ');
      if(!/skin|body|flesh/i.test(hay)) return;
      for(const m of mats){
        if(!m || !m.color) continue;
        if(!this._skinOrig.has(m)) this._skinOrig.set(m, m.color.getHex());
        m.color.setHex(hex ? parseInt(String(hex).replace('#',''), 16) : this._skinOrig.get(m));
        m.needsUpdate = true;
      }
    });
  }
  /* Universal OUTFIT: every mesh name on the loaded model, for per-part
     toggles on models with no fighter-parts inventory. */
  listBaseMeshes(){
    return [...this._baseNameSet()].filter(Boolean).sort();
  }
  setProportions(p){
    if(!this.model) return;
    this.model.scale.set(0.92+0.16*(p.weight||1), 0.9+0.2*(p.height||1), 0.92+0.16*(p.weight||1));
  }
  snapshot(){
    this.renderer.render(this.scene, this.camera);
    return this.canvas.toDataURL('image/png');
  }
}
