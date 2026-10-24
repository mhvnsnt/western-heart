// viewer.js — the Creation Suite v2 live stage.
//
// The editor-side twin of the game's in-fight consumer
// (game/js/customization-consumer.js). It attaches parts with the SAME
// shared code the fight uses — src/parts.js applyPart, src/attire.js
// attach/applyEdit, and the consumer's own exported placement helpers
// (effectivePlacement / UNIT_SCALE) — imported, never forked. Morphs
// preview through src/morphs.js applyMorphProxies (the shared proxy;
// baked shape keys remain the ground truth, per that module's header)
// and body-type scale through game/js/custom-fighter.js's own
// customFighterToRoster conversion. The only editor-local glue is the
// GLB fetch/clone/center block, which mirrors the consumer's steps
// line-for-line so editor and fight can never drift in result.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.js';
import { resolveProfileParts } from '../src/catalogs.js';
import { applyPart, removePart } from '../src/parts.js';
import { SLOTS as ATTIRE_SLOTS, applyEdit, detach } from '../src/attire.js';
import { clone as skeletonClone } from 'three/addons/utils/SkeletonUtils.js';
import { applyMorphProxies } from '../src/morphs.js';
import { effectivePlacement } from '../../../game/js/customization-consumer.js';
import { customFighterToRoster } from '../../../game/js/custom-fighter.js';

const ROOT = new URL('../../../', import.meta.url); // repo root, as served

function makeStageDressing() {
  // Stage dressing is OURS (labeled reconstruction in the theme ledger):
  // a dark void + glowing ring platform, the shape both Tekken's and
  // WWE's suites present. No extracted file is claimed for it.
  const g = new THREE.Group();
  const cvs = document.createElement('canvas'); cvs.width = cvs.height = 256;
  const ctx = cvs.getContext('2d');
  const grad = ctx.createRadialGradient(128, 128, 10, 128, 128, 128);
  grad.addColorStop(0, 'rgba(70,90,130,0.55)');
  grad.addColorStop(0.55, 'rgba(28,36,58,0.35)');
  grad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = grad; ctx.fillRect(0, 0, 256, 256);
  const tex = new THREE.CanvasTexture(cvs);
  const disc = new THREE.Mesh(
    new THREE.CircleGeometry(2.6, 48),
    new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false }));
  disc.rotation.x = -Math.PI / 2; disc.position.y = 0.001;
  const ring = new THREE.Mesh(
    new THREE.RingGeometry(1.06, 1.1, 64),
    new THREE.MeshBasicMaterial({ color: 0xff8c2e, transparent: true, opacity: 0.85, side: THREE.DoubleSide }));
  ring.rotation.x = -Math.PI / 2; ring.position.y = 0.002;
  g.add(disc, ring);
  return g;
}

function centerPiece(scene) {
  // The consumer's exact re-centering (game/js/customization-consumer.js
  // centerPiece): Box3 of the piece, geometry translated by -centre.
  const box = new THREE.Box3().setFromObject(scene);
  if (box.isEmpty()) return;
  const c = box.getCenter(new THREE.Vector3());
  scene.traverse((o) => { if (o.isMesh && o.geometry) o.geometry.translate(-c.x, -c.y, -c.z); });
}

export class Viewer {
  constructor(canvas) {
    this.canvas = canvas;
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, preserveDrawingBuffer: true });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x07080d);
    this.scene.background = new THREE.Color(0x0b0d16);
    this.scene.fog = new THREE.Fog(0x0b0d16, 9, 16);
    this.camera = new THREE.PerspectiveCamera(36, 1, 0.1, 60);
    this.scene.add(new THREE.HemisphereLight(0xdfe8ff, 0x201812, 1.35));
    const key = new THREE.DirectionalLight(0xffffff, 2.4); key.position.set(2.5, 3.6, 3.2);
    const rim = new THREE.DirectionalLight(0x86a8ff, 2.1); rim.position.set(-3, 2.2, -2.6);
    const fill = new THREE.DirectionalLight(0xffd9b0, 0.5); fill.position.set(-1.5, 1.2, 3);
    this.scene.add(key, rim, fill);
    this.scene.add(makeStageDressing());
    this.pivot = new THREE.Group();          // model offset (fighter stands right of the overlay menu)
    this.pivot.position.set(0.42, 0, 0);
    this.modelWrap = new THREE.Group();      // body-type scale lives here
    this.pivot.add(this.modelWrap);
    this.scene.add(this.pivot);
    this.model = null;
    this.charId = null;
    this.record = null;                      // customization.json-shaped record currently applied
    this.entries = [];
    this.registry = null;
    this.slotSockets = {};                   // suite_slot -> attire socket (live-edit routing)
    this.slotEdits = {};                     // attire socket -> full edit object (live-edit state)
    this._centeredCache = new Map();         // part glb -> centered base scene (see applyRecord)
    this.turntable = false;
    this.yaw = -0.3; this.pitch = 0.12; this.dist = 4.4; this.targetY = 1.0;
    this._drag = null;
    this._bindPointer();
    this._resize();
    addEventListener('resize', () => this._resize());
    this.renderer.setAnimationLoop(() => this._tick());
  }

  _bindPointer() {
    const c = this.canvas;
    c.style.touchAction = 'none';
    c.addEventListener('pointerdown', (e) => { this._drag = { x: e.clientX, y: e.clientY }; c.setPointerCapture(e.pointerId); });
    c.addEventListener('pointermove', (e) => {
      if (!this._drag) return;
      const dx = e.clientX - this._drag.x, dy = e.clientY - this._drag.y;
      this._drag = { x: e.clientX, y: e.clientY };
      this.yaw -= dx * 0.008; this.pitch = THREE.MathUtils.clamp(this.pitch + dy * 0.005, -0.15, 0.6);
      this.turntable = false;
    });
    c.addEventListener('pointerup', () => { this._drag = null; });
    c.addEventListener('wheel', (e) => { e.preventDefault(); this.dist = THREE.MathUtils.clamp(this.dist + e.deltaY * 0.003, 2.4, 7.5); }, { passive: false });
  }

  _resize() {
    const w = innerWidth, h = innerHeight;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
  }

  _tick() {
    if (this.turntable && !this._drag) this.yaw += 0.0035;
    const cy = Math.cos(this.pitch), sy = Math.sin(this.pitch);
    this.camera.position.set(
      Math.sin(this.yaw) * cy * this.dist,
      this.targetY + sy * this.dist,
      Math.cos(this.yaw) * cy * this.dist);
    this.camera.lookAt(0, this.targetY, 0);
    this.renderer.render(this.scene, this.camera);
  }

  _loader() {
    if (!this._gltf) {
      this._gltf = new GLTFLoader();
      try { this._gltf.setMeshoptDecoder(MeshoptDecoder); } catch (e) { /* non-meshopt still loads */ }
    }
    return this._gltf;
  }

  async _loadScene(url) {
    this._sceneCache ||= new Map();
    if (this._sceneCache.has(url)) return this._sceneCache.get(url);
    const gltf = await this._loader().loadAsync(url);
    this._sceneCache.set(url, gltf.scene);
    return gltf.scene;
  }

  async setFighter(glbPath, charId) {
    const url = new URL(glbPath, ROOT).href;
    const scene = await this._loadScene(url);
    if (this.model) { this.modelWrap.remove(this.model); }
    this.model = skeletonClone(scene);
    this.charId = charId;
    // ground + frame
    const box = new THREE.Box3().setFromObject(this.model);
    const size = box.getSize(new THREE.Vector3());
    this.model.position.y -= box.min.y;
    this.modelWrap.add(this.model);
    this.targetY = size.y * 0.52;
    this.dist = Math.max(3.4, size.y * 2.35);
    if (this.record) await this.applyRecord(this.record);
    if (this._state) this.applyMorphs(this._state, this._suiteRecord);
    return { height: size.y };
  }

  async applyRecord(record) {
    this.record = record;
    if (!this.model) return { applied: [], skipped: [] };
    const status = { applied: [], skipped: [] };
    // remove everything currently attached (shared removePart/detach)
    for (const id of Object.keys(this.model.userData.csParts || {})) {
      try { removePart(this.model, id); } catch (e) { /* already gone */ }
    }
    for (const socket of Object.keys(this.model.userData.csAttire || {})) {
      try { detach(this.model, socket); } catch (e) { /* already gone */ }
    }
    this.slotSockets = {}; this.slotEdits = {};
    // Attach reads socket WORLD matrices (attire.attach cancels the
    // socket's world scale/quaternion). Before the first rendered frame
    // those are stale — force a true update so the editor's attach is
    // computed exactly like the in-fight consumer's (which attaches
    // after frames have rendered).
    this.model.updateMatrixWorld(true);

    const resolved = resolveProfileParts(this.entries, record);
    for (const r of resolved) {
      const label = `${r.slot}:${r.part_id || '?'}`;
      if (r.status !== 'resolved' || !r.entry) { status.skipped.push(label); continue; }
      const entry = r.entry;
      try {
        if (entry.part_class === 'mesh_part' || r.glb) {
          if (!r.glb) throw new Error('no GLB yet');
          // Center ONCE per part, on a private geometry copy. The
          // consumer centers the shared cached geometry in place —
          // fine in-fight (attach-once per fighter load; the result is
          // its first-apply result), but the editor re-applies records
          // on every edit, and re-centering shared geometry walks the
          // piece a little further each time. Centering a private copy
          // once and cloning it per apply makes every editor apply
          // produce EXACTLY the consumer's first-apply result.
          let base = this._centeredCache.get(r.glb);
          if (!base) {
            const raw = await this._loadScene(new URL(r.glb, ROOT).href);
            base = raw.clone(true);
            base.traverse((o) => { if (o.isMesh && o.geometry) o.geometry = o.geometry.clone(); });
            centerPiece(base);
            this._centeredCache.set(r.glb, base);
          }
          const piece = base.clone(true);
          const placement = effectivePlacement(r.placement, entry, r.slot);
          const effEntry = { ...entry, placement };
          const colors = record.item_colors?.[r.slot] || [];
          const tint = colors.find((c) => c && c.toLowerCase() !== '#ffffff') || record.finishes?.[r.slot]?.tint || null;
          const finish = record.finishes?.[r.slot] || {};
          const edit = {};
          if (tint) edit.tint = tint;
          if (finish.roughness != null) edit.roughness = finish.roughness;
          if (finish.metalness != null) edit.metalness = finish.metalness;
          applyPart(this.model, effEntry, piece, { registry: this.registry, charId: this.charId, edit });
          this.slotSockets[r.slot] = placement.socket;
          this.slotEdits[placement.socket] = {
            offset: placement.offset || [0, 0, 0], rotation: placement.rotation || [0, 0, 0],
            scale: placement.scale ?? 1, ...edit,
          };
          status.applied.push(label);
        } else if (entry.part_class === 'texture_part') {
          status.skipped.push(label + ' (texture layer path)');
        } else {
          status.skipped.push(label);
        }
      } catch (e) {
        console.warn('[CS2] part failed', label, e.message || e);
        status.skipped.push(label);
      }
    }
    // texture layers
    for (const layer of record.textures || []) {
      const entry = this.entries.find((p) => p.id === layer.part_id);
      if (!entry || !layer.image) continue;
      try {
        const tex = await new THREE.TextureLoader().loadAsync(new URL(layer.image, ROOT).href);
        tex.colorSpace = THREE.SRGBColorSpace;
        applyPart(this.model, entry, tex, { registry: this.registry, charId: this.charId });
        status.applied.push(`texture:${layer.part_id}`);
      } catch (e) { status.skipped.push(`texture:${layer.part_id}`); }
    }
    this.lastStatus = status;
    return status;
  }

  // Live slider path: full-edit re-application on the attached piece,
  // exactly the game's applyEdit (base-relative, idempotent).
  liveEdit(suiteSlot, partial) {
    const socket = this.slotSockets[suiteSlot];
    if (!socket || !this.model) return false;
    const piece = this.model.userData.csAttire?.[socket]?.piece;
    if (!piece) return false;
    const cur = this.slotEdits[socket] || { offset: [0, 0, 0], rotation: [0, 0, 0], scale: 1 };
    const next = { ...cur, ...partial };
    this.slotEdits[socket] = next;
    applyEdit(piece, next);
    return true;
  }

  // Morphs + body type: shared proxies + the CAW loader's own conversion.
  applyMorphs(state, suiteRecord) {
    this._state = state;
    this._suiteRecord = suiteRecord;
    if (!this.model) return;
    const rosterObj = suiteRecord ? customFighterToRoster(suiteRecord) : null;
    if (rosterObj) this.modelWrap.scale.set(rosterObj.bodyWidth || 1, rosterObj.bodyScale || 1, rosterObj.bodyWidth || 1);
    applyMorphProxies(this.model, state.morphs || {});
  }
}
