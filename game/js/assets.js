/* ============================================================
   WESTERN HEART — Assets
   Preloads the rigged 3D fighter (Mixamo-skeleton GLB) once and
   hands out skeleton-cloned, per-fighter-tinted instances.
   Self-contained: the model lives at game/assets/models/.
   ============================================================ */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { clone as skeletonClone } from 'three/addons/utils/SkeletonUtils.js';

const MODEL_URL = 'assets/models/pantera.glb';

class AssetManager {
  constructor() {
    this.gltf = null;
    this.clips = {};
    this.ready = false;
  }

  load(onProgress) {
    return new Promise((resolve, reject) => {
      const loader = new GLTFLoader();
      loader.load(
        MODEL_URL,
        (gltf) => {
          this.gltf = gltf;
          for (const clip of gltf.animations) this.clips[clip.name] = clip;
          gltf.scene.traverse((o) => {
            if (o.isMesh) {
              o.castShadow = true;
              o.receiveShadow = true;
              o.frustumCulled = false; // fighters are always near the camera
              if (o.material) {
                o.material = o.material.clone();
                o.material.roughness = 0.65;
                o.material.metalness = 0.05;
              }
            }
          });
          this.ready = true;
          resolve(this);
        },
        (e) => { if (onProgress && e.total) onProgress(e.loaded / e.total); },
        (err) => reject(err)
      );
    });
  }

  /* { model, bones, mixer, actions } for one fighter.
     Per-fighter palette: suit color lerp + trim emissive accents. */
  createInstance(suitColor, trimColor) {
    const model = skeletonClone(this.gltf.scene);

    const suit = new THREE.Color(suitColor);
    const trim = new THREE.Color(trimColor);
    model.traverse((o) => {
      if (o.isMesh && o.material) {
        o.material = o.material.clone();
        // body suit tint
        o.material.color.lerp(suit, 0.55);
        // small emissive trim pop so the two fighters read apart
        o.material.emissive = o.material.emissive || new THREE.Color(0x000000);
        o.material.emissive.copy(trim).multiplyScalar(0.06);
      }
    });

    // Model stands ~1.6 units; nudge feet flush to y=0.
    model.position.y -= 0.12;

    const bones = {};
    model.traverse((o) => {
      if (o.isBone) bones[o.name.replace(/^mixamorig:?/, '')] = o;
    });

    const mixer = new THREE.AnimationMixer(model);
    const actions = {};
    for (const name of ['Idle', 'Walk', 'Run']) {
      if (this.clips[name]) {
        actions[name] = mixer.clipAction(this.clips[name]);
        actions[name].play();
        actions[name].setEffectiveWeight(name === 'Idle' ? 1 : 0);
      }
    }
    return { model, bones, mixer, actions, scale: 1.0 };
  }
}

export const assets = new AssetManager();
