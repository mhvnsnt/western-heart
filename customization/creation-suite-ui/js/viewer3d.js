/* viewer3d.js — three.js preview viewport for the Creation Suite.
   three.js is MIT. GLTFLoader vendored at ../create-fighter/vendor/addons/loaders/GLTFLoader.js.
   Phone-first orbit: drag to rotate, pinch/wheel to zoom. Fighter stays full-screen, never covered. */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

/* suite socket -> anchor placement as fractions of the model's bounding box.
   Anchors are placed in model space; placement offsets apply on top. */
const SOCKET_ANCHORS = {
  head:  { pos:[0.5, 0.93, 0.5],  desc:"top of head" },
  face:  { pos:[0.5, 0.85, 0.98], desc:"front of face" },
  hands: { pos:[0.5, 0.55, 0.5],  desc:"hands (both)" },
  chest: { pos:[0.5, 0.72, 0.62], desc:"chest front" },
  waist: { pos:[0.5, 0.55, 0.55], desc:"waist front" },
};

export class SuiteViewer {
  constructor(canvas){
    this.canvas = canvas;
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias:true, alpha:true });
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
    requestAnimationFrame(()=>this._tick());
    const t=this.camTarget;
    this.camera.position.set(
      t.x + this.camDist*Math.sin(this.phi)*Math.sin(this.theta),
      t.y + this.camDist*Math.cos(this.phi),
      t.z + this.camDist*Math.sin(this.phi)*Math.cos(this.theta));
    this.camera.lookAt(t);
    this.renderer.render(this.scene, this.camera);
  }
  loadBase(url){
    return new Promise((res, rej)=>{
      this.loader.load(url, gltf=>{
        if(this.model) this.scene.remove(this.model);
        this.model = gltf.scene;
        this.scene.add(this.model);
        this.modelBox = new THREE.Box3().setFromObject(this.model);
        // auto-frame: fit the whole fighter in view (fighter stays fully visible)
        const sphere = this.modelBox.getBoundingSphere(new THREE.Sphere());
        this.camTarget.copy(sphere.center);
        this.camDist = sphere.radius / Math.tan(THREE.MathUtils.degToRad(this.camera.fov/2)) * 1.15;
        // ground the fighter: disc under feet, sized to the model
        this.disc.position.y = this.modelBox.min.y + 0.001;
        this.ring.position.y = this.modelBox.min.y + 0.002;
        const dr = Math.max(sphere.radius*0.9, 0.5);
        this.disc.scale.setScalar(dr/1.6); this.ring.scale.setScalar(dr/1.6);
        this.ready = true;
        this.onReady && this.onReady();
        res(this.model);
      }, undefined, rej);
    });
  }
  /* socket anchor in world space */
  socketPoint(socket){
    const a = SOCKET_ANCHORS[socket] || SOCKET_ANCHORS.head;
    const b = this.modelBox, out = new THREE.Vector3();
    if(!b) return out.set(0,1.6,0);
    out.set(
      b.min.x + (b.max.x-b.min.x)*a.pos[0],
      b.min.y + (b.max.y-b.min.y)*a.pos[1],
      b.min.z + (b.max.z-b.min.z)*a.pos[2]);
    return out;
  }
  /* attach a mesh part GLB at a socket with placement {px,py,pz,rx,ry,rz,s} */
  attachPart(partId, glbUrl, def, placement){
    return new Promise((res, rej)=>{
      this.loader.load(glbUrl, gltf=>{
        this.detachPart(partId);
        const g = new THREE.Group();
        g.add(gltf.scene);
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
    group.rotation.set(
      THREE.MathUtils.degToRad(p.rx||0) + (def.rotation?def.rotation[0]:0),
      THREE.MathUtils.degToRad(p.ry||0) + (def.rotation?def.rotation[1]:0),
      THREE.MathUtils.degToRad(p.rz||0) + (def.rotation?def.rotation[2]:0));
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
  setSkinTone(hex){ /* parametric preview: tint exposed materials */ }
  setProportions(p){
    if(!this.model) return;
    this.model.scale.set(0.92+0.16*(p.weight||1), 0.9+0.2*(p.height||1), 0.92+0.16*(p.weight||1));
  }
  snapshot(){
    this.renderer.render(this.scene, this.camera);
    return this.canvas.toDataURL('image/png');
  }
}
