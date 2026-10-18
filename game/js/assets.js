/* ============================================================
   WESTERN HEART — Assets
   Preloads the REAL rigged fighters (Mixamo-skeleton GLBs) and
   hands out skeleton-cloned, per-fighter-tinted instances.
   Self-contained: models live at game/assets/models/.
   Pantera = real P1 textured body (roster/pantera). Steve Fox =
   Tekken 7 base reskinned cold blue-white (see game/README.md).
   ============================================================ */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { clone as skeletonClone } from 'three/addons/utils/SkeletonUtils.js';
// Meshopt-compressed GLBs (Tripo outputs: cape-jones, thor, waterfall,
// saku-ra-main, purple-rain-main, kiko-tanaka*). Vendored locally —
// the game ships with no CDN (see index.html importmap).
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.js';

const MODEL_URLS = {
  pantera: 'assets/models/pantera.glb',
  'steve-fox': 'assets/models/steve-fox.glb',
  jin: 'assets/models/jin.glb',
  // Per-fighter models wired from teardown extractions + Tripo rescans.
  // Keys match FULL_ROSTER `model` ids in roster-full.js (lane 2).
  demonio: 'assets/models/demonio.glb',
  diablo: 'assets/models/diablo.glb',
  phantom: 'assets/models/phantom.glb',
  skull: 'assets/models/skull.glb',
  'sam-ur-a1': 'assets/models/sam-ur-a1.glb',
  'saku-ra': 'assets/models/saku-ra.glb',
  'awa-pop': 'assets/models/awa-pop.glb',
  'purple-rain': 'assets/models/purple-rain.glb',
  nightwolf: 'assets/models/nightwolf.glb',
  'king-tyrant': 'assets/models/king-tyrant.glb',
  kinpo: 'assets/models/kinpo.glb',
  waterfall: 'assets/models/waterfall.glb',
  'n3g4tiv0': 'assets/models/n3g4tiv0.glb',
  thor: 'assets/models/thor.glb',
  'doc-frank': 'assets/models/doc-frank.glb',
  'cyborg-x': 'assets/models/cyborg-x.glb',
  'cape-jones': 'assets/models/cape-jones.glb',
  // Bonus / music fighters and name-pending models (loadable, unassigned).
  mariposa: 'assets/models/mariposa.glb',
  zafina: 'assets/models/zafina.glb',
  dxmmii: 'assets/models/dxmmii.glb',
  rave: 'assets/models/rave.glb',
  lili: 'assets/models/lili.glb',   // NO WH name yet — do not assign
  baek: 'assets/models/baek.glb',   // NO WH name yet — do not assign
  // Lane C fighter-hunt (Round 2): per-fighter models from community rips,
  // retargeted to Mixamo skeleton. See docs/fighter-hunt/HUNT-LOG.md.
  star: 'assets/models/star.glb',
  torch: 'assets/models/torch.glb',
  michiko: 'assets/models/michiko.glb',
  // Created fighters use the Soldier.glb base from the CAW suite.
  // Relative path works on GitHub Pages (game/ -> customization/).
  custom: '../customization/create-fighter/assets/Soldier.glb',
};

class AssetManager {
  constructor() {
    this.gltfs = {};   // id -> gltf
    this.clips = {};   // id -> {name: clip}
    this.ready = false;
  }

  // TEKKEN 3 LESSON (teardown/tekken3/docs/TEKKEN3-ARCHITECTURE.md):
  // "Tekken 3 doesn't load everything at once. The BNS table is an index —
  // the game loads specific records on demand." We do the same: load only
  // the models needed for the current fight, not the whole roster at boot.
  //
  // CLEAN-INIT: a hung download must NEVER brick the game. Each model
  // gets a timeout + one retry; total failure rejects so the UI can
  // show a real error instead of spinning forever.
  async loadModels(ids, onProgress) {
    const need = [...new Set(ids)].filter(id => !this.gltfs[id]);
    let done = 0;
    const LOAD_TIMEOUT_MS = 90000;
    const loadOne = (id, attempt) => new Promise((resolve, reject) => {
      const loader = new GLTFLoader();
      loader.setMeshoptDecoder(MeshoptDecoder);
      const timer = setTimeout(() => reject(new Error(`timeout loading ${id} (attempt ${attempt})`)), LOAD_TIMEOUT_MS);
      loader.load(
        MODEL_URLS[id],
        (gltf) => {
          clearTimeout(timer);
          this.gltfs[id] = gltf;
          this.clips[id] = {};
          // Bind-pose Hips position (Z-up skeleton): animations must return
          // here, not to origin and not to the mis-retargeted offset.
          let hipsBind = null;
          gltf.scene.traverse((o) => {
            if (o.isBone && o.name === 'Hips' && !hipsBind) hipsBind = o.position.clone();
          });
          for (const clip of gltf.animations) {
            // FIX: Mis-retargeted Mixamo clips have a huge absolute root
            // offset in Hips.position (e.g. Z=-7.13) that buries the fighter
            // underground. The game drives root.position for locomotion, so
            // animations must be in-place: pin Hips.position to bind pose.
            for (const track of clip.tracks) {
              if (track.name === 'Hips.position' && hipsBind) {
                for (let i = 0; i < track.values.length; i += 3) {
                  track.values[i] = hipsBind.x;
                  track.values[i + 1] = hipsBind.y;
                  track.values[i + 2] = hipsBind.z;
                }
              }
            }
            this.clips[id][clip.name] = clip;
          }
          gltf.scene.traverse((o) => {
            if (o.isMesh) {
              o.castShadow = true;
              o.receiveShadow = true;
              o.frustumCulled = false;
            }
          });
          resolve();
        },
        (xhr) => {
          // Byte-level download progress: xhr.loaded / xhr.total
          if (xhr.total > 0 && onProgress) {
            const frac = done / Math.max(need.length, 1);
            const thisFrac = xhr.loaded / xhr.total / Math.max(need.length, 1);
            onProgress(Math.min(frac + thisFrac, 1), xhr.loaded, xhr.total, id);
          }
        },
        (err) => { clearTimeout(timer); reject(err); }
      );
    });
    const loadWithRetry = async (id) => {
      try { await loadOne(id, 1); }
      catch (e1) {
        console.warn(`[WH] ${id} load failed, retrying:`, e1.message || e1);
        await loadOne(id, 2); // throws to caller on second failure
      }
    };
    for (const id of need) {
      await loadWithRetry(id);
      done++;
      if (onProgress) onProgress(done / Math.max(need.length, 1));
    }
    if (Object.keys(this.gltfs).length > 0) this.ready = true;
    return this;
  }

  // Legacy: load all models (kept for compat, but boot no longer uses it).
  load(onProgress) {
    return this.loadModels(Object.keys(MODEL_URLS), onProgress);
  }

  // Fire-and-forget prefetch: warms the cache while the user browses select.
  prefetch(id) {
    if (!id || this.gltfs[id] || this._prefetching?.has(id)) return;
    this._prefetching = this._prefetching || new Set();
    this._prefetching.add(id);
    this.loadModels([id]).catch(e => console.warn('[WH] prefetch failed:', id, e.message || e))
      .finally(() => this._prefetching.delete(id));
  }

  // Preload the base models the moment the select screen opens.
  // Fighters with their own GLB use it; the rest fall back to the
  // pantera / steve-fox / jin bases (see MODEL-STATUS.md), so warming
  // those bases here means CONFIRM rarely waits on a download.
  // Per-fighter GLBs load on demand when their fight starts —
  // never all at once (TEKKEN 3 LESSON above).
  preloadAll() {
    for (const id of ['pantera', 'steve-fox', 'jin', 'custom']) this.prefetch(id);
  }

  /* { model, bones, mixer, actions } for one fighter.
     Per-fighter palette: suit color lerp + trim emissive accents. */
  createInstance(fighterId, suitColor, trimColor, tintStrength = 0.45) {
    const gltf = this.gltfs[fighterId];
    if (!gltf) throw new Error('unknown fighter model: ' + fighterId);
    const model = skeletonClone(gltf.scene);

    const suit = new THREE.Color(suitColor);
    const trim = new THREE.Color(trimColor);
    let skinnedCount = 0;
    model.traverse((o) => {
      // Bulletproof: never rely on clone preserving render flags.
      // Skinned meshes MUST NOT be frustum-culled (their bounds are wrong
      // after skinning) and MUST be visible.
      if (o.isMesh || o.isSkinnedMesh) {
        o.frustumCulled = false;
        o.visible = true;
      }
      if (o.isSkinnedMesh) skinnedCount++;
      if (o.isMesh && o.material) {
        o.material = o.material.clone();
        // tint toward the fighter's palette (real textures underneath)
        if (o.material.color) o.material.color.lerp(suit, tintStrength);
        o.material.emissive = o.material.emissive || new THREE.Color(0x000000);
        o.material.emissive.copy(trim).multiplyScalar(0.08);
        if (o.material.roughness !== undefined) o.material.roughness = 0.7;
        // Never ship a transparent fighter: a bad alpha kills visibility.
        if (o.material.transparent && o.material.opacity < 0.05) {
          o.material.transparent = false;
          o.material.opacity = 1;
        }
      }
    });
    if (skinnedCount === 0) {
      console.error(`[WH] createInstance(${fighterId}): ZERO skinned meshes — fighter will be invisible!`);
    }

    const bones = {};
    model.traverse((o) => {
      if (o.isBone) bones[o.name.replace(/^mixamorig:?/, '')] = o;
    });

    const mixer = new THREE.AnimationMixer(model);
    const actions = {};
    const clips = this.clips[fighterId] || {};
    for (const name of ['Idle', 'Walk', 'Run']) {
      if (clips[name]) {
        actions[name] = mixer.clipAction(clips[name]);
        actions[name].play();
        actions[name].setEffectiveWeight(name === 'Idle' ? 1 : 0);
      }
    }
    return { model, bones, mixer, actions, scale: 1.0 };
  }
}

export const assets = new AssetManager();
