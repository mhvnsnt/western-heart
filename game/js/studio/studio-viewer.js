/* Shared 3D viewer for every studio: stage, light, drag-orbit, pinch zoom,
   loaders for roster fighters (the game's own assets.js — same model,
   textures and attire ladder as select/fight) and for files from any game
   (GLB/GLTF, FBX, BVH clips). */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { assets } from '../assets.js';

export class StudioViewer {
  constructor(host){
    this.host = host; this.renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
    this.renderer.setPixelRatio(Math.min(2, devicePixelRatio || 1)); this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    host.appendChild(this.renderer.domElement);
    this.scene = new THREE.Scene(); this.scene.background = new THREE.Color(0x1a0f09);
    this.camera = new THREE.PerspectiveCamera(32, 1, 0.05, 100);
    this.scene.add(new THREE.HemisphereLight(0xfff1dc, 0x2a1a10, 1.4));
    const key = new THREE.DirectionalLight(0xffffff, 2.2); key.position.set(2, 4, 3); this.scene.add(key);
    const rim = new THREE.DirectionalLight(0xffb070, 1.2); rim.position.set(-3, 2, -2); this.scene.add(rim);
    const floor = new THREE.Mesh(new THREE.CircleGeometry(1.6, 48), new THREE.MeshStandardMaterial({ color: 0x2b1a10, roughness: .9 }));
    floor.rotation.x = -Math.PI / 2; this.scene.add(floor);
    this.yaw = 0.35; this.pitch = 0.08; this.dist = 3.4; this.target = new THREE.Vector3(0, 0.95, 0);
    this.model = null; this.mixer = null; this.onFrame = null; this._bindOrbit(); this._resize();
    addEventListener('resize', () => this._resize());
    const clock = new THREE.Clock();
    const loop = () => { const dt = Math.min(0.05, clock.getDelta());
      if (this.mixer) this.mixer.update(dt); if (this.onFrame) this.onFrame(dt);
      this._cam(); this.renderer.render(this.scene, this.camera); requestAnimationFrame(loop); };
    requestAnimationFrame(loop);
  }
  _resize(){ const w = this.host.clientWidth || 1, h = this.host.clientHeight || 1; this.renderer.setSize(w, h, false); this.camera.aspect = w / h; this.camera.updateProjectionMatrix(); }
  _cam(){ const c = Math.cos(this.pitch); this.camera.position.set(this.target.x + Math.sin(this.yaw) * c * this.dist, this.target.y + Math.sin(this.pitch) * this.dist, this.target.z + Math.cos(this.yaw) * c * this.dist); this.camera.lookAt(this.target); }
  _bindOrbit(){
    const el = this.renderer.domElement; const pts = new Map(); let pd = 0;
    el.addEventListener('pointerdown', e => { el.setPointerCapture(e.pointerId); pts.set(e.pointerId, [e.clientX, e.clientY]); });
    el.addEventListener('pointerup', e => pts.delete(e.pointerId)); el.addEventListener('pointercancel', e => pts.delete(e.pointerId));
    el.addEventListener('pointermove', e => { const p = pts.get(e.pointerId); if (!p) return;
      if (pts.size === 1) { this.yaw -= (e.clientX - p[0]) * 0.01; this.pitch = Math.max(-0.4, Math.min(1.0, this.pitch + (e.clientY - p[1]) * 0.006)); }
      else if (pts.size === 2) { const [a, b] = [...pts.values()]; const d = Math.hypot(a[0] - b[0], a[1] - b[1]); if (pd) this.dist = Math.max(1.2, Math.min(7, this.dist * pd / d)); pd = d; }
      pts.set(e.pointerId, [e.clientX, e.clientY]); if (pts.size < 2) pd = 0; });
    el.addEventListener('wheel', e => { this.dist = Math.max(1.2, Math.min(7, this.dist * (1 + Math.sign(e.deltaY) * 0.08))); e.preventDefault(); }, { passive: false });
  }
  _place(obj){
    if (this.model) this.scene.remove(this.model);
    this.model = obj; this.scene.add(obj);
    const bb = new THREE.Box3().setFromObject(obj); const s = bb.getSize(new THREE.Vector3());
    if (s.y > 0.01) { const k = s.y > 5 ? 1.8 / s.y : 1; obj.scale.multiplyScalar(k); const bb2 = new THREE.Box3().setFromObject(obj); obj.position.y -= bb2.min.y; this.target.y = (bb2.max.y - bb2.min.y) * 0.55; this.dist = Math.max(2.2, (bb2.max.y - bb2.min.y) * 1.9); }
  }
  async loadFighter(modelId){
    await assets.loadModels([modelId]);
    const inst = assets.createInstance(modelId, 0xffffff, 0x888888, 0);
    this._place(inst.model); this.mixer = null; this.inst = inst; return inst.model;
  }
  async loadFile(file){
    const url = URL.createObjectURL(file); const ext = file.name.split('.').pop().toLowerCase();
    try {
      if (ext === 'glb' || ext === 'gltf') { const g = await new GLTFLoader().loadAsync(url); this._place(g.scene); this.clips = g.animations; this.mixer = null; return g.scene; }
      if (ext === 'fbx') { const { FBXLoader } = await import('three/addons/loaders/FBXLoader.js'); const o = await new FBXLoader().loadAsync(url); this._place(o); this.clips = o.animations; return o; }
      throw new Error('unsupported: ' + ext);
    } finally { setTimeout(() => URL.revokeObjectURL(url), 5000); }
  }
  async loadUrl(url){ const g = await new GLTFLoader().loadAsync(url); this._place(g.scene); this.clips = g.animations; this.mixer = null; return g.scene; }
  async exportGLB(){ const { GLTFExporter } = await import('three/addons/exporters/GLTFExporter.js'); return new GLTFExporter().parseAsync(this.model, { binary: true, animations: this.clips || [] }); }
  snapshot(){ return this.renderer.domElement.toDataURL('image/jpeg', 0.85); }
}
