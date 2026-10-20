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
  // NOTE (owner canon 2026-10-19): Tekken's Jin = DEMONIO — the old `jin:` key was removed;
  // `demonio: 'assets/models/demonio.glb'` (below) is the canonical model.
  // Per-fighter models wired from teardown extractions + Tripo rescans.
  // Keys match FULL_ROSTER `model` ids in roster-full.js (lane 2).
  demonio: 'assets/models/demonio.glb',
  diablo: 'assets/models/diablo.glb',
  // Tripo pulls wired 2026-10-19 (owner: stop saying "not in the repo").
  phantom: '../roster/phantom/attires/attire1/model.glb',
  skull: '../roster/skull/attires/attire1/model.glb',
  // SAM-UR-A1 Attire 1 (owner 2026-10-19): Tripo pull replaces the fan-rip placeholder.
  'sam-ur-a1': '../roster/sam-ur-a1/attires/attire1/model.glb',
  'saku-ra': '../roster/sakura/attires/attire1/model.glb',
  'awa-pop': 'assets/models/awa-pop.glb',
  'purple-rain': '../roster/purplerain/attires/attire1/model.glb',
  nightwolf: 'assets/models/nightwolf.glb',
  'king-tyrant': 'assets/models/king-tyrant.glb',
  kinpo: 'assets/models/kinpo.glb',
  waterfall: '../roster/waterfall/attires/attire1/model.glb',
  'n3g4tiv0': 'assets/models/n3g4tiv0.glb',
  thor: '../roster/thor/attires/attire1/model.glb',
  // Thor Attire 2: phantom-mimic oni mask (owner 2026-10-19).
  'thor-attire2': '../roster/thor/attires/attire2/model.glb',
  'doc-frank': 'assets/models/doc-frank.glb',
  // Doc Frank post-transform bigger form (owner 2026-10-19, Tripo pull).
  'doc-frank-big': '../roster/doc-frank/attires/attire1/post-transform/model.glb',
  // Wave 2 (2026-10-19): Wowomomo Attire 2, Hood Scientist Attire 3, Demonio forms, Dxmmii Attire 2.
  'doc-frank-wowomomo': '../roster/doc-frank/attires/attire2/base/model.glb',
  'doc-frank-wowomomo-big': '../roster/doc-frank/attires/attire2/transformed/model.glb',
  'doc-frank-hood': '../roster/doc-frank/attires/attire3/base/model.glb',
  'doc-frank-hood-big': '../roster/doc-frank/attires/attire3/transformed/model.glb',
  'demonio-a1': '../roster/demonio/attires/attire1/model.glb',
  'demonio-winged': '../roster/demonio/attires/winged-devil/model.glb',
  'demonio-human': '../roster/demonio/attires/human/model.glb',
  'dxmmii-a2': '../roster/dxmmii/attires/attire2/model.glb',
  'cyborg-x': 'assets/models/cyborg-x.glb',
  'cape-jones': 'assets/models/cape-jones.glb',
  // Bonus / music fighters and name-pending models (loadable, unassigned).
  mariposa: 'assets/models/mariposa.glb',
  // Mariposa Slot 2: the real Tripo pull (owner 2026-10-19; Butterfly Default is Slot 1).
  'mariposa-slot2': '../roster/mariposa/attires/slot2/model.glb',
  zafina: 'assets/models/zafina.glb',
  dxmmii: 'assets/models/dxmmii.glb',
  rave: 'assets/models/rave.glb',
  // Cain Elias — Vain Abel's brother, Undertaker archetype (owner 2026-10-19, Tripo pulls).
  'cain-elias': '../roster/cain-elias/attires/attire1/model.glb',
  'cain-elias-attire2': '../roster/cain-elias/attires/attire2/model.glb',
  // Burger — Demon mode, possessed by greed (owner 2026-10-19, Tripo pull).
  burger: '../roster/burger/attires/attire1/model.glb',
  // Burger hunger-state variants (owner 2026-10-19, Tripo pulls).
  'burger-attire2': '../roster/burger/attires/attire2/model.glb',
  'burger-attire3': '../roster/burger/attires/attire3/model.glb',
  'burger-attire4': '../roster/burger/attires/attire4/model.glb',
  lili: 'assets/models/lili.glb',   // NO WH name yet — do not assign
  baek: 'assets/models/baek.glb',   // NO WH name yet — do not assign
  // Round-2 auto-rig wave (lane B): re-rigged per-fighter variants + Tripo
  // attires, all passing the playable gate (valid glTF, skinned, Hips, 1.5-2.2m).
  'demonio-body': 'assets/models/demonio-body.glb',
  'kai-body': 'assets/models/kai-body.glb',
  'king-tyrant_alt1': 'assets/models/king-tyrant_alt1.glb',
  'kinpo-t8': 'assets/models/kinpo-t8.glb',
  'kinpo_alt1': 'assets/models/kinpo_alt1.glb',
  'phantom-t8': 'assets/models/phantom-t8.glb',
  'pantera_alt1': 'assets/models/pantera_alt1.glb',
  'pantera-body': 'assets/models/pantera-body.glb',
  'retsu-body': 'assets/models/retsu-body.glb',
  'saku-ra_alt1': 'assets/models/saku-ra_alt1.glb',
  'saku-ra-main': 'assets/models/saku-ra-main.glb',
  'sam-ur-a1-body': 'assets/models/sam-ur-a1-body.glb',
  'sha-body': 'assets/models/sha-body.glb',
  'zen-body': 'assets/models/zen-body.glb',
  'zui_alt1': 'assets/models/zui_alt1.glb',
  'zui_alt2': 'assets/models/zui_alt2.glb',
  'kiko-tanaka': 'assets/models/kiko-tanaka.glb',
  'kiko-tanaka_alt1': 'assets/models/kiko-tanaka_alt1.glb',
  'purple-rain-main': 'assets/models/purple-rain-main.glb',
  // Lane C fighter-hunt (Round 2): per-fighter models from community rips,
  // retargeted to Mixamo skeleton. See docs/fighter-hunt/HUNT-LOG.md.
  star: 'assets/models/star.glb',
  torch: 'assets/models/torch.glb',
  michiko: 'assets/models/michiko.glb',
  dio: 'assets/models/dio.glb',
  bruno: 'assets/models/bruno.glb',
  yukihyo: 'assets/models/yukihyo.glb',
  scimitar: 'assets/models/scimitar.glb',   // Shaheen-based base mesh — NO-GATE: wired as-is, clothing via Creation Suite as an option
  // Created fighters use the Soldier.glb base from the CAW suite.
  // Relative path works on GitHub Pages (game/ -> customization/).
  custom: '../customization/create-fighter/assets/Soldier.glb',
  // Reskin wave (2026-10-19): first custom attires, wired as selectable fighters.
  // Jin Bloodline Ember + Doc Frank Machine Shop are rigged drop-ins from their
  // lanes; Baek/Mariposa/Dxmmii are texture-transplants onto their rigged bases
  // (reskin lanes dropped the skins on buffer rebuild) — *-rigged.glb.
  'demonio-bloodline-ember': '../roster/demonio/attires/bloodline-ember/demonio-bloodline-ember.glb',
  'doc-frank-machine-shop': '../roster/doc-frank/attires/machine-shop/doc-frank-machine-shop-rigged.glb',
  'baek-master-white': '../roster/baek/attires/master-white/baek-master-white-rigged.glb',
  'mariposa-monarch': '../roster/mariposa/attires/monarch/mariposa-monarch-rigged.glb',
  'dxmmii-patchwork': '../roster/dxmmii/attires/patchwork-dj/dxmmii-patchwork-rigged.glb',
  // Sketchfab intake (owner 2026-10-19): Zangief, Blanka, Vega, Iori, Armor King.
  // WH names pending owner pick from INTAKE-PROPOSAL.md — working names for now.
  // Licenses: Zangief CC-BY (johnny136), Blanka Free Standard (allanromanreyes),
  // Vega CC-BY (pierodsoto01), Iori CC-BY (0xo), Armor King CC-BY (theamazingdonovan207).
  zangief: '../roster/zangief/attires/attire1/model.glb',
  blanka: '../roster/blanka/attires/attire1/model.glb',
  vega: '../roster/vega/attires/attire1/model.glb',
  iori: '../roster/iori/attires/attire1/model.glb',
  'armor-king': '../roster/armor-king/attires/attire1/model.glb',
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
  // pantera / steve-fox / demonio bases (see MODEL-STATUS.md), so warming
  // those bases here means CONFIRM rarely waits on a download.
  // Per-fighter GLBs load on demand when their fight starts —
  // never all at once (TEKKEN 3 LESSON above).
  preloadAll() {
    for (const id of ['pantera', 'steve-fox', 'demonio', 'custom']) this.prefetch(id);
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
