# Runtime retarget integration (`tools/anim-retarget/runtime/`)

`wh-retarget.js` retargets Mixamo/Rokoko animation GLBs onto a loaded WH
fighter **at runtime** using the vendored `three/addons/utils/SkeletonUtils.js`
(`retargetClip`, MIT, three r160 — already in `game/vendor/`).

## When to use runtime vs offline bake

| | Offline bake (`retarget_blender.py`) | Runtime (`wh-retarget.js`) |
|---|---|---|
| Output | `model@Clip.glb` shipped with the game | retargeted in memory at load |
| Cost at load | ~0 (clip plays as-is) | one retarget pass per clip |
| Use for | shipped moveset clips | iterating on new mocap, downloadable anim packs |

Ship with the bake. Iterate with the runtime.

## Integration (game/js/assets.js)

```js
import { loadRetargetedClips } from '../tools/anim-retarget/runtime/wh-retarget.js';

// inside AssetManager, after a fighter GLB loads:
async loadAnimPack(fighterId, animGlbUrl) {
  const gltf = this.gltfs[fighterId];
  const clips = await loadRetargetedClips(gltf.scene, animGlbUrl, { inPlace: true });
  Object.assign(this.clips[fighterId], clips);
  return clips;
}
```

Clips land in `assets.clips[fighterId][clipName]` — the same dict the game
already uses for embedded clips, so `fighter.js` needs no changes.

## Bone mapping

`buildNameMap(target, source)` matches by exact name, then by `mixamo:` /
`Mixamo:` prefix (Mixamo FBX exports). Kept in sync with
`bone_maps/mixamo_to_wh.json` — the offline script drops unmapped helper
bones (`*_End`, finger-4 segments); the runtime module keeps only bones
present on **both** skeletons.

## Root motion

- `inPlace: true` (default) pins `Hips.position` to the target's bind pose —
  matches `AssetManager.loadModels`, which does the same for embedded clips.
- `scaleRoot: true` (default) scales root translation by the hip-height
  ratio so a 6-foot mocap actor's stride doesn't moon-walk a short fighter.
