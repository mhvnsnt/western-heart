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
//
// CLOSET CONTROLS (2026-10-24, closet lane): the same stage doubles as
// the user-driven closet room (registry v2, packages/creation-suite/
// closet-registry.json). Added on top of the base stage, base behaviour
// untouched: per-slot toggle/swap (toggleSlot / setClosetSlot), part
// framing (focusPart / showFullBody), lighting presets (setLighting:
// studio / living_room / night — a closet control, never baked into a
// render), face-texture swap (swapFaceTexture, the creation-gaps lane's
// material chain: face/head mesh -> MBLab_skin material -> skin/body
// material -> first mapped material -> first material), and versioned
// recipe save/load (saveClosetRecipe / loadClosetRecipe via the pure
// ./closet-recipes.js module — saving never overwrites an earlier
// version). Pan is two-finger drag; one finger still orbits exactly as
// before, wheel/pinch still zooms.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.js';
import { resolveProfileParts } from '../src/catalogs.js';
import { applyPart, removePart } from '../src/parts.js';
import { SLOTS as ATTIRE_SLOTS, applyEdit, detach } from '../src/attire.js';
import { clone as skeletonClone } from 'three/addons/utils/SkeletonUtils.js';
import { applyMorphProxies } from '../src/morphs.js';
import { buildSecondaryRig } from '../src/secondary.js';
import { swapSkinnedPart, removeSwapped } from '../src/rigswap.js';
import { effectivePlacement } from '../../../game/js/customization-consumer.js';
import { customFighterToRoster } from '../../../game/js/custom-fighter.js';
import { createRecipe, saveRecipe, loadRecipe } from './closet-recipes.js';

const ROOT = new URL('../../../', import.meta.url);
// Suite body dials (src/morphs.js ids) -> secondary-physics region sliders
// (src/regions.js). Gates chest/glute springs and feeds the size scaling.
export function physicsSliders(m = {}) {
  const v = (k) => Number(m[k]) || 0;
  return { chest: v('chest'), belly: v('belly'), glutes: v('hips'), thighs: 0.5 * v('hips') + 0.5 * v('fat'), weight: v('fat') };
} // repo root, as served

// Closet lighting presets. studio = neutral, for judging color; living_room
// = the show room light, warm and dimmer; night = dark, for spooky surf
// vibe checks. Lighting is a closet control, not baked into any render.
export const LIGHTING_PRESETS = {
  studio: {
    background: 0x878a91, fog: null, exposure: 1.0,
    hemi: { sky: 0xdfe8ff, ground: 0x201812, intensity: 1.35 },
    key: { color: 0xffffff, intensity: 2.4, position: [2.5, 3.6, 3.2] },
    rim: { color: 0x86a8ff, intensity: 2.1, position: [-3, 2.2, -2.6] },
    fill: { color: 0xffd9b0, intensity: 0.5, position: [-1.5, 1.2, 3] },
  },
  living_room: {
    background: 0x1a1410, fog: [0x1a1410, 9, 16], exposure: 1.0,
    hemi: { sky: 0xffe0b8, ground: 0x1a120c, intensity: 0.9 },
    key: { color: 0xffd9a8, intensity: 1.6, position: [2.5, 3.6, 3.2] },
    rim: { color: 0x86a8ff, intensity: 1.2, position: [-3, 2.2, -2.6] },
    fill: { color: 0xffc890, intensity: 0.8, position: [-1.5, 1.2, 3] },
  },
  night: {
    background: 0x05060a, fog: [0x05060a, 9, 16], exposure: 0.9,
    hemi: { sky: 0x5a6ea8, ground: 0x05060a, intensity: 0.5 },
    key: { color: 0x8fb0ff, intensity: 1.0, position: [2.5, 3.6, 3.2] },
    rim: { color: 0x7a6cff, intensity: 1.8, position: [-3, 2.2, -2.6] },
    fill: { color: 0x8899cc, intensity: 0.3, position: [-1.5, 1.2, 3] },
  },
};

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
    // Closet lighting rig: same four lights the base stage used, now
    // named so setLighting() can retune them per preset.
    this.lights = {
      hemi: new THREE.HemisphereLight(0xdfe8ff, 0x201812, 1.35),
      key: new THREE.DirectionalLight(0xffffff, 2.4),
      rim: new THREE.DirectionalLight(0x86a8ff, 2.1),
      fill: new THREE.DirectionalLight(0xffd9b0, 0.5),
    };
    this.lights.key.position.set(2.5, 3.6, 3.2);
    this.lights.rim.position.set(-3, 2.2, -2.6);
    this.lights.fill.position.set(-1.5, 1.2, 3);
    this.scene.add(this.lights.hemi, this.lights.key, this.lights.rim, this.lights.fill);
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
    // Closet state: pan target (X/Z join targetY), per-slot mesh maps,
    // lighting preset, saved full-body view, versioned recipes.
    this.targetX = 0; this.targetZ = 0;
    this.closetSlots = {};                   // slot -> { meshes: universe, current: [mesh names] }
    this.closetSlotVisible = {};             // slot -> bool
    // Lighting preset currently applied by setLighting(); null = the base
    // stage look (dark void). The closet panel calls setLighting('studio')
    // on mount so the closet itself always opens neutral.
    this.lighting = null;
    this.focusedSlot = null;
    this._fullBodyView = null;
    this.recipes = [];
    this._drag = null;
    this._bindPointer();
    this._resize();
    addEventListener('resize', () => this._resize());
    this.renderer.setAnimationLoop(() => this._tick());
  }

  _bindPointer() {
    const c = this.canvas;
    c.style.touchAction = 'none';
    // One finger orbits (exactly the base behaviour); two fingers pan
    // (midpoint drag) + pinch-zoom. Pointer map keeps both gestures live.
    this._pointers = new Map();
    this._pinch = null;
    c.addEventListener('pointerdown', (e) => {
      this._pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
      c.setPointerCapture(e.pointerId);
      if (this._pointers.size === 1) {
        this._drag = { x: e.clientX, y: e.clientY };
      } else if (this._pointers.size === 2) {
        const [a, b] = [...this._pointers.values()];
        this._pinch = { d: Math.hypot(a.x - b.x, a.y - b.y), mx: (a.x + b.x) / 2, my: (a.y + b.y) / 2 };
        this._drag = null;
      }
    });
    c.addEventListener('pointermove', (e) => {
      if (!this._pointers.has(e.pointerId)) return;
      this._pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (this._pointers.size === 1 && this._drag) {
        const dx = e.clientX - this._drag.x, dy = e.clientY - this._drag.y;
        this._drag = { x: e.clientX, y: e.clientY };
        this.yaw -= dx * 0.008; this.pitch = THREE.MathUtils.clamp(this.pitch + dy * 0.005, -0.15, 0.6);
      } else if (this._pointers.size === 2 && this._pinch) {
        const [a, b] = [...this._pointers.values()];
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
        if (this._pinch.d > 0) this.dist = THREE.MathUtils.clamp(this.dist * (this._pinch.d / d), 0.4, 7.5);
        // Pan: midpoint drag moves the look target opposite the finger
        // along the camera's screen-right / screen-up axes (orbit-style).
        const dx = mx - this._pinch.mx, dy = my - this._pinch.my;
        const k = 0.002 * this.dist;
        const rx = Math.cos(this.yaw), rz = -Math.sin(this.yaw);
        this.targetX += -dx * k * rx;
        this.targetZ += -dx * k * rz;
        this.targetY += dy * k;
        this._pinch = { d, mx, my };
      }
    });
    const endPointer = (e) => {
      this._pointers.delete(e.pointerId);
      if (this._pointers.size < 2) this._pinch = null;
      if (this._pointers.size === 0) this._drag = null;
      else if (this._pointers.size === 1) {
        const [p] = [...this._pointers.values()];
        this._drag = { x: p.x, y: p.y };
      }
    };
    c.addEventListener('pointerup', endPointer);
    c.addEventListener('pointercancel', endPointer);
    c.addEventListener('wheel', (e) => { e.preventDefault(); this.dist = THREE.MathUtils.clamp(this.dist + e.deltaY * 0.003, 0.4, 7.5); }, { passive: false });
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
      this.targetX + Math.sin(this.yaw) * cy * this.dist,
      this.targetY + sy * this.dist,
      this.targetZ + Math.cos(this.yaw) * cy * this.dist);
    this.camera.lookAt(this.targetX, this.targetY, this.targetZ);
    const now = performance.now(), dt = this._last ? (now - this._last) / 1000 : 0; this._last = now;
    if (this.springs && dt > 0) { this.model?.updateMatrixWorld(true); this.springs.update(dt); }
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
    this.targetX = 0; this.targetZ = 0;
    this._fullBodyView = null; this.focusedSlot = null;
    if (this.record) await this.applyRecord(this.record);
    if (this._state) this.applyMorphs(this._state, this._suiteRecord);
    this.rebuildPhysics();
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
    for (const slot of Object.keys(this.model.userData.csSwapped || {})) removeSwapped(this.model, slot);
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
          if (entry.rig_swap) {
            // Tekken-style: rebind the part's skin to this rig by bone name.
            const raw = await this._loadScene(new URL(r.glb, ROOT).href);
            const res = swapSkinnedPart(this.model, skeletonClone(raw), r.slot);
            if (res.ok) { status.applied.push(label + ' (rig swap)'); continue; }
            // not this rig's bones: fall through to the socket attach
          }
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

  // Size-adaptive secondary physics (src/secondary.js): spring bones for
  // chest / glutes / belly / thighs, sized from the measured body and the
  // body sliders, rebuilt whenever the body changes.
  rebuildPhysics(sliders = physicsSliders(this._state?.morphs || {})) {
    this.springs = null;
    if (!this.model || this.physicsEnabled === false) return null;
    try { this.springs = buildSecondaryRig(this.model, { sliders }); }
    catch (e) { console.warn('[CS2] secondary physics unavailable:', e.message || e); }
    this.physicsCount = this.springs?.springs?.length || 0;
    return this.springs;
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

  // ---- Closet controls (registry v2) ----

  /** Retune the four stage lights + background/fog/exposure. Unknown preset: no change, returns null. */
  setLighting(preset) {
    const p = LIGHTING_PRESETS[preset];
    if (!p || !this.lights) return null;
    const apply = (light, spec) => {
      light.color.set(spec.color ?? spec.sky ?? 0xffffff);
      light.intensity = spec.intensity;
      if (spec.position) light.position.set(...spec.position);
      if (spec.ground !== undefined && light.isHemisphereLight) light.groundColor.set(spec.ground);
    };
    apply(this.lights.hemi, p.hemi);
    apply(this.lights.key, p.key);
    apply(this.lights.rim, p.rim);
    apply(this.lights.fill, p.fill);
    this.scene.background = new THREE.Color(p.background);
    this.scene.fog = p.fog ? new THREE.Fog(p.fog[0], p.fog[1], p.fog[2]) : null;
    this.renderer.toneMappingExposure = p.exposure;
    this.lighting = preset;
    return preset;
  }

  /** Match model meshes by registry mesh name (exact, or with a .dmx suffix stripped). */
  _closetMeshes(names) {
    const want = new Set(names || []);
    const base = (n) => n.replace(/\.dmx$/i, '');
    const out = [];
    if (!this.model) return out;
    this.model.traverse((o) => {
      if (!o.isMesh) return;
      if (want.has(o.name) || want.has(base(o.name))) out.push(o);
    });
    return out;
  }

  /** Register a slot's mesh universe (every item the slot can hold). First registration sets the current item. */
  registerClosetSlot(slotId, meshNames) {
    const cur = this.closetSlots[slotId];
    const universe = [...new Set([...(cur?.meshes || []), ...(meshNames || [])])];
    this.closetSlots[slotId] = { meshes: universe, current: cur ? cur.current : [...(meshNames || [])] };
    if (this.closetSlotVisible[slotId] === undefined) this.closetSlotVisible[slotId] = true;
    return this.closetSlots[slotId];
  }

  /** Swap a slot live: hide its whole universe, show exactly this item's meshes. null/[] = slot empty. */
  setClosetSlot(slotId, meshNames) {
    const slot = this.closetSlots[slotId];
    if (!slot) return false;
    for (const m of this._closetMeshes(slot.meshes)) m.visible = false;
    const next = [...(meshNames || [])];
    for (const m of this._closetMeshes(next)) m.visible = true;
    slot.current = next;
    this.closetSlotVisible[slotId] = true;
    return true;
  }

  /** Toggle one slot on/off individually. Presets are shortcuts; this is the truth. No arg = flip. */
  toggleSlot(slotId, on) {
    const slot = this.closetSlots[slotId];
    if (!slot) return false;
    const next = on === undefined ? !this.closetSlotVisible[slotId] : !!on;
    for (const m of this._closetMeshes(slot.current)) m.visible = next;
    this.closetSlotVisible[slotId] = next;
    return next;
  }

  /** Frame ONE slot's part alone so a swap can be judged up close. Remembers the full-body view. */
  focusPart(slotId) {
    const slot = this.closetSlots[slotId];
    if (!slot || !this.model) return null;
    let meshes = this._closetMeshes(slot.current).filter((m) => m.visible);
    if (!meshes.length) meshes = this._closetMeshes(slot.meshes);
    if (!meshes.length) return null;
    if (!this._fullBodyView) {
      this._fullBodyView = { yaw: this.yaw, pitch: this.pitch, dist: this.dist, targetX: this.targetX, targetY: this.targetY, targetZ: this.targetZ };
    }
    this.model.updateMatrixWorld(true);
    const box = new THREE.Box3();
    for (const m of meshes) box.expandByObject(m);
    if (box.isEmpty()) return null;
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const span = Math.max(size.x, size.y, size.z);
    this.targetX = center.x; this.targetY = center.y; this.targetZ = center.z;
    this.dist = THREE.MathUtils.clamp(span * 2.4, 0.5, 7.5);
    this.focusedSlot = slotId;
    return { slot: slotId, dist: this.dist, center: [center.x, center.y, center.z] };
  }

  /** One tap back to the full body (the view saved before the first focusPart). */
  showFullBody() {
    if (this._fullBodyView) {
      Object.assign(this, this._fullBodyView);
      this._fullBodyView = null;
    } else {
      this.targetX = 0; this.targetZ = 0;
    }
    this.focusedSlot = null;
    return true;
  }

  /** Swap the face/skin texture on the live model (creation-gaps lane chain).
   *  face/head mesh -> MBLab_skin material -> skin/body material ->
   *  first material with a map -> first material. Returns null when no
   *  material on the model can take a texture. The preset-number -> PNG
   *  table itself lives in src/face-texture-map.js (creation-suite lane);
   *  this method takes the resolved PNG URL so the two lanes stay decoupled
   *  until that file lands on main. */
  async swapFaceTexture(url) {
    if (!this.model || !url) return null;
    const mats = [];
    this.model.traverse((o) => {
      if (!o.isMesh) return;
      const list = Array.isArray(o.material) ? o.material : [o.material];
      for (const m of list) if (m && !mats.includes(m)) mats.push({ mesh: o.name, material: m });
    });
    if (!mats.length) return null;
    const byName = (re) => mats.find((e) => re.test(e.material.name || ''));
    const faceMesh = mats.find((e) => /face|head/i.test(e.mesh) && e.material.map);
    const pick = faceMesh
      || byName(/^MBLab_skin/i)
      || mats.find((e) => /skin|body/i.test(e.material.name || ''))
      || mats.find((e) => e.material.map)
      || mats[0];
    try {
      const href = /^https?:\/\//i.test(url) ? url : new URL(url, ROOT).href;
      const tex = await new THREE.TextureLoader().loadAsync(href);
      tex.colorSpace = THREE.SRGBColorSpace;
      pick.material.map = tex;
      pick.material.needsUpdate = true;
      return { material: pick.material.name || null, mesh: pick.mesh, url: href };
    } catch (e) {
      console.warn('[CS2] face texture failed', url, e.message || e);
      return null;
    }
  }

  /** Save the current closet state as a NAMED, VERSIONED recipe. Never overwrites an earlier version. */
  saveClosetRecipe(name) {
    if (!this.charId) throw new Error('no fighter loaded for a closet recipe');
    const toggles = {};
    for (const [slot, s] of Object.entries(this.closetSlots)) {
      toggles[slot] = { item: [...s.current], visible: this.closetSlotVisible[slot] !== false };
    }
    const recipe = createRecipe({
      name,
      character: this.charId,
      preset: this.record?.preset ?? null,
      toggles,
      colors: this.record?.item_colors || {},
      lighting: this.lighting || 'studio',
      camera: { yaw: this.yaw, pitch: this.pitch, dist: this.dist, target: [this.targetX, this.targetY, this.targetZ] },
    });
    this.recipes = saveRecipe(this.recipes, recipe);
    return this.recipes[this.recipes.length - 1];
  }

  /** Load a saved recipe (latest version, or the exact version when given) and apply it live. */
  loadClosetRecipe(name, version = null) {
    const rec = loadRecipe(this.recipes, name, version);
    if (!rec) return null;
    for (const [slot, t] of Object.entries(rec.toggles || {})) {
      if (this.closetSlots[slot]) {
        this.setClosetSlot(slot, t.item || []);
        this.toggleSlot(slot, t.visible !== false);
      }
    }
    if (rec.lighting) this.setLighting(rec.lighting);
    if (rec.camera) {
      this.yaw = rec.camera.yaw ?? this.yaw;
      this.pitch = rec.camera.pitch ?? this.pitch;
      this.dist = rec.camera.dist ?? this.dist;
      if (rec.camera.target) [this.targetX, this.targetY, this.targetZ] = rec.camera.target;
    }
    return rec;
  }
}
