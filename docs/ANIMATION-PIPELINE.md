# Western Heart — Animation Pipeline
## Retargeting plan: Quaternius + CMU mocap → Tekken skeletons

**Date:** 2026-10-13
**Sources:**
- Quaternius Universal Animation Library 1 (`assets/free-pull-1/quaternius/animations/UAL1_Standard.fbx`, 29MB)
- Quaternius glTF animations (`assets/free-pull-1/quaternius/gltf-animations/`)
- CMU mocap fighting clips (`assets/free-pull-1/cmu-mocap/fighting/`, 16 BVH files)
- Tekken 7 King reference skeleton (`~/workspace/game-reverse-engineering/tekken7/king/5PMH7G85GYN7P71W3BD1V0249.fbx`)

---

## 1. What We Have

### Quaternius UAL1 (FBX, Mixamo-compatible rig)
- Standard humanoid rig — same bone naming as Mixamo (Hips, Spine, Spine1, Spine2,
  Neck, Head, LeftUpLeg, LeftLeg, LeftFoot, LeftArm, LeftForeArm, LeftHand, etc.)
- Covers: idle, walk, run, jump, and general-purpose clips.
- **Key property:** Mixamo-compatible = zero retargeting needed between Quaternius
  and any Mixamo-rigged character.

### CMU Mocap Fighting Clips (BVH, 16 files)
| File | Content |
|---|---|
| 13_17.bvh, 14_01.bvh, 17_10.bvh | Boxing |
| 143_23.bvh, 143_24.bvh | Punching / kicking |
| 144_20.bvh, 144_13.bvh | Punch sequences |
| 144_05.bvh, 144_09.bvh | Front kicks |
| 144_07.bvh, 144_26.bvh | Blocks |
| 135_04.bvh, 135_07.bvh, 135_09.bvh, 135_11.bvh | Karate (mae-geri, mawashi-geri, oi-zuki, yoko-geri) |
| 86_06.bvh | Kicking / punching / knee |

BVH = pure rotation data, no mesh. Must retarget to target skeleton in Blender.

### Tekken 7 King Skeleton
- Full UE4-style humanoid skeleton from the FBX.
- 19+ meshes skinned to it (body parts).
- Bone naming follows UE4/Mixamo conventions (compatible with retargeting tools).

---

## 2. Retargeting Paths

### Path A: Quaternius → Tekken (EASY)
Quaternius uses Mixamo bone naming. Tekken 7 King uses UE4 naming (same convention).
- **Method:** Blender "Copy Transforms" or Rokoko plugin, or Godot's built-in retargeting.
- **Expected result:** Near-1:1 transfer. May need minor hip-height adjustment.
- **Use for:** Idle, walk, run, jump — the locomotion base layer.

### Path B: CMU BVH → Tekken (MEDIUM)
BVH has its own skeleton (CMU standard: different proportions, Z-up).
- **Method:**
  1. Import BVH into Blender.
  2. Align CMU skeleton to Tekken skeleton (match rest poses).
  3. Bake animation to Tekken armature via constraints.
  4. Export as FBX or Godot `.anim`.
- **Expected result:** Good with manual cleanup. Hand/foot sliding may need fixing.
- **Use for:** Signature moves — karate kicks (Demonio), boxing combos (Zui),
  blocks, punch sequences.

### Path C: tk IK Combat Layer → Godot (ADAPT)
The tk game doesn't use pre-baked punch/kick animations — it drives IK procedurally.
- **Method:** Reimplement the CCD IK solver from `fighter.js` in Godot.
  Godot has built-in `SkeletonIK3D` — configure two-bone chains for arms and legs.
- **Expected result:** Punches/kicks that adapt to each fighter's skeleton automatically.
- **Use for:** All standard attacks (jab, cross, kick). No per-character animation needed.

---

## 3. Per-Fighter Animation Plan

| Fighter | Base (Path A) | Signature (Path B) | Combat (Path C) |
|---|---|---|---|
| Pantera (King) | Quaternius idle/walk/run | CMU grappling refs | IK punches + King throws |
| Demonio (Jin) | Quaternius idle/walk/run | CMU karate (135_xx) | IK punches/kicks |
| Saku Ra (Xiaoyu) | Quaternius idle/walk/run | CMU kicks (144_05/09) | IK + evasive |
| Zui (Steve) | Quaternius idle/walk/run | CMU boxing (13_17, 14_01, 17_10) | IK boxing |
| BURGER (Bob) | Quaternius idle/walk/run | CMU punching (143_xx) | IK power moves |

---

## 4. Pipeline Steps (per fighter)

1. **Import** Tekken FBX into Blender. Verify skeleton.
2. **Retarget** Quaternius locomotion clips (Path A). Export.
3. **Retarget** CMU signature clips (Path B). Clean up sliding. Export.
4. **Configure** Godot SkeletonIK3D chains for arms/legs (Path C).
5. **Define** moveset in frame-data format (see TK-COMBAT-ANALYSIS.md).
6. **Test** in prototype: idle → walk → punch → kick → block → hit-react.

---

## 5. Tools Needed

- [x] Blender 4.0.2 (`~/workspace/tools/blender/`)
- [ ] Rokoko Blender plugin (free, for BVH retargeting) — to install
- [ ] Godot 4 (for SkeletonIK3D and final integration) — to set up
- [x] Quaternius FBX animations (in repo)
- [x] CMU BVH clips (in repo)
- [x] Tekken 7 King FBX with skeleton (on disk)

---

*Pipeline doc by wireup subagent, 2026-10-13.*
