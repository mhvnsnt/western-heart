# Quaternius Modular Characters — AshLane Integration Manifest

## Source & License
- **Author:** Quaternius (@Quaternius) — https://quaternius.com
- **Packs:** Universal Base Characters [Standard], Universal Animation Library [Standard], Universal Animation Library 2 [Standard]
- **License:** **CC0 1.0 Universal** (Public Domain Dedication) — verified in bundled `QUATERNIUS_LICENSE_CC0.txt`
- **Commercial use:** YES — free for personal, educational, and commercial projects
- **Downloaded via:** GitHub mirror (itch.io blocks automated download); files verified byte-identical to official pack (SHA-256 `fdbf1804c90dfc1ea03e992bff7da2dfd1a79318e13270a660180f9308455f40` per community records)

## What's Actually in the Free Standard Pack (honest inventory)
The "6 base models / 20 hairstyles / 12 outfits" marketing describes the **paid Source tier**.
The free CC0 Standard tier contains:

| Category | Files | Notes |
|----------|-------|-------|
| Base bodies | `Superhero_Male_FullBody.glb` (15.5 MB), `Superhero_Female_FullBody.glb` (16 MB) | Self-contained GLB (textures embedded). ~13k triangles each. Regular/Teen proportions are Source-tier only. |
| Hairstyles | `Hair_Buns`, `Hair_Buzzed`, `Hair_BuzzedFemale`, `Hair_Long`, `Hair_SimpleParted` (50–223 KB each) | Geometry-only GLB (textures stripped; use flat dark material). Rigged to Head bone — attach to same skeleton. |
| Facial hair | `Hair_Beard.glb` (58 KB) | Same rig. |
| Eyebrows | `Eyebrows_Female.glb`, `Eyebrows_Regular.glb` | Same rig. |
| Animations | `UAL1_Standard.glb` (7.6 MB, 43 clips), `UAL2_Standard.glb` (8.1 MB, 43 clips) | **Work directly on the Quaternius rig — no retargeting needed.** See clip list below. |

**Not in free tier:** outfits/clothing parts (the "Modular Character Outfits" is a separate fantasy-themed pack), Regular/Teen body proportions.

## Rig: 65 Joints (Unreal-style naming)
The Quaternius rig is **NOT** Mixamo-named, but is hierarchy-compatible (same humanoid structure). Retargeting = name mapping.

### Quaternius → Mixamo 58-joint mapping
| Quaternius | Mixamo (`mixamorig:`) | Notes |
|------------|----------------------|-------|
| `root` | — | Drop (Mixamo has no root joint) |
| `pelvis` | `Hips` | |
| `spine_01` | `Spine` | |
| `spine_02` | `Spine1` | |
| `spine_03` | `Spine2` | |
| `neck_01` | `Neck` | |
| `Head` | `Head` | |
| `clavicle_l` / `clavicle_r` | `LeftShoulder` / `RightShoulder` | |
| `upperarm_l` / `_r` | `LeftArm` / `RightArm` | |
| `lowerarm_l` / `_r` | `LeftForeArm` / `RightForeArm` | |
| `hand_l` / `_r` | `LeftHand` / `RightHand` | |
| `thumb_01_l` → `LeftHandThumb1`, `thumb_02_l` → `LeftHandThumb2`, `thumb_03_l` → `LeftHandThumb3` | (same pattern `_r` → Right) | |
| `index_01_l` → `LeftHandIndex1`, `index_02_l` → `LeftHandIndex2`, `index_03_l` → `LeftHandIndex3` | (same pattern) | |
| `middle_01_l` → `LeftHandMiddle1/2/3` | (same pattern) | |
| `ring_01_l` → `LeftHandRing1/2/3` | (same pattern) | |
| `pinky_01_l` → `LeftHandPinky1/2/3` | (same pattern) | |
| `*_04_leaf_*` (finger tips, 10 joints) | — | Drop (Mixamo ends at digit 3; leaf bones are end-effectors) |
| `thigh_l` / `_r` | `LeftUpLeg` / `RightUpLeg` | |
| `calf_l` / `_r` | `LeftLeg` / `RightLeg` | |
| `foot_l` / `_r` | `LeftFoot` / `RightFoot` | |
| `ball_l` / `_r` | `LeftToeBase` / `RightToeBase` | |
| `ball_leaf_l` / `ball_leaf_r` | — | Drop (end-effectors) |

**Result:** 65 Quaternius joints → 52 mapped + 13 dropped (root + 12 leaf/end bones) = clean map onto the Mixamo 58-joint skeleton. The 6 Mixamo joints with no Quaternius source (`LeftHandThumb4`, etc. — Mixamo's 4th finger segments) can be left unmapped or copied from segment 3.

**Preferred path:** Use the Quaternius rig natively with UAL animations (zero retargeting). Map to Mixamo only when sharing clips with the 58-joint library.

## Animation Clips (86 total, all CC0, direct-fit)

### UAL1 (43) — locomotion, barehand combat, reactions
`Punch_Jab`, `Punch_Cross`, `Hit_Chest`, `Hit_Head`, `Death01`, `Roll`, `Crouch_Idle_Loop`, `Crouch_Fwd_Loop`, `Idle_Loop`, `Walk_Loop`, `Jog_Fwd_Loop`, `Sprint_Loop`, `Jump_Start`, `Jump_Loop`, `Jump_Land`, `Dance_Loop`, `Sword_Attack`, `Sword_Idle`, `Pistol_*` (6), `Swim_*` (2), `Sitting_*` (4), `Spell_Simple_*` (4), + idles/interacts

### UAL2 (43) — weapon combat, melee
`Melee_Hook`, `Melee_Hook_Rec`, `Sword_Regular_Combo`, `Sword_Heavy_Combo`, `Sword_Regular_A/B/C` (+ recovery variants), `Sword_Block`, `Sword_Dash`, `Shield_Dash`, `Hit_Knockback`, `NinjaJump_*` (3), `Slide_*` (3), `OverhandThrow`, `ClimbUp_1m`, + idles/zombie/farm

## Modular Character System (for the customization UI)
1. **Base:** load `Superhero_Male_FullBody.glb` or `Superhero_Female_FullBody.glb` (skinned, 65-joint rig).
2. **Hair:** load any `Hair_*.glb` — it carries the same 65-joint skeleton; bind it to the body's skeleton instance (same joint names = no remap). Hair mesh is weighted ~100% to `Head`.
3. **Beard/eyebrows:** same mechanism as hair.
4. **Skin/eye color:** the Source tier has shader customization; in the Standard tier, swap material `baseColorFactor` at runtime for skin-tone variants.
5. **Outfits:** NOT in this pack. Next pull: Quaternius "Modular Character Outfits" pack (fantasy) or author streetwear parts on the same rig.

## File Layout in AshLane
```
assets/characters/quaternius/
  QUATERNIUS_LICENSE_CC0.txt
  QUATERNIUS_MANIFEST.md        (this file)
  Superhero_Male_FullBody.glb
  Superhero_Female_FullBody.glb
  Hair_Buns.glb / Hair_Buzzed.glb / Hair_BuzzedFemale.glb
  Hair_Long.glb / Hair_SimpleParted.glb / Hair_Beard.glb
  Eyebrows_Female.glb / Eyebrows_Regular.glb
  UAL1_Standard.glb
  UAL2_Standard.glb
```
