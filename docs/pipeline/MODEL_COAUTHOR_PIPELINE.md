# Model Co-Author Pipeline: teardown or download → Western Heart original

**Goal (owner):** no model ships the way it came out of a teardown or download. Every model (Tekken 3/6/TTT2/7/8,
WWF No Mercy, Def Jam, Urban Reign, WWE, or anything Muse downloads) gets **rescanned and co-authored**
into a Western Heart universe original, without destroying the source. Originals stay under
`teardown/` and `lab/source_assets/original/`. Every derived file is new and lives next to the character in `roster/<character>/`.

This is the exact flow the owner used for **Pantera P1** (Leomon refs plus King in T-pose → Tripo 3D → the in-game `game/assets/models/pantera.glb`).

## Steps
1. **T-pose reference sheet.** Render the source model as a 1:1 2048² T-pose on pure white, following
   `docs/tpose-refs/MUSE_TPOSE_SPEC.md` (one-command script: `docs/tpose-refs/_tools/tpose_render.py`).
   Owner and art direction get mixed in here: AI or generative passes, Canva, paint-overs, and mash-ups of several refs
   (Leomon plus King was the Pantera mix). Save the final concept as `docs/tpose-refs/<character>/<attire>_concept.png`.
2. **Tripo 3D.** The owner feeds the concept image into Tripo 3D to get a brand-new mesh and texture. This is the
   "rescan": geometry and UVs are new, not copied from the donor.
3. **Auto-rig** (Tripo's auto-rig, or Blender Rigify/Mixamo-style) onto the **Western Heart humanoid skeleton**:
   `Root, Hips, Spine, Chest, Neck, Head, Left/Right{Shoulder, Arm, ForeArm, Hand, UpLeg, Leg, Foot, ToeBase}`.
   That's the same bone set as `pantera_leoman.glb` and `t3_king.glb`, so the Pantera animations retarget 1:1.
4. **Cut into body segments, the way Tekken does it** (see below), so attires, damage, and creation-suite parts swap per segment.
5. **Retarget the existing Pantera P1 animation set** (idle, walk_fwd, walk_back, light, medium, heavy, block, grab, hit, ko,
   win, as in `lab/game/assets/pantera_leoman.glb` actions) onto the new rig. The bone names match, so it's a straight copy.
6. **Co-author** in Blender (sculpt, retexture, logos, colorway), then in the **creation suite** and **move creator**
   (Repo Co Dev's claim: `customization/`, `customization/create-fighter/`. Reference them, don't edit them from this lane).
   Save as `roster/<character>/attires/<attire>/<character>_<attire>.glb` and add it to the T-pose checklist.
7. **Re-render the T-pose sheet** of the finished model (step 1 again) as the canonical sheet and mark it `DONE`.

## How the Tekken teardown models are segmented (documented for step 4)
| Source | Segmentation found in this repo |
|---|---|
| **Tekken 3** (`teardown/tekken3/models/king95/`) | **Rigid-part rig, "clay pieces on a wire skeleton."** `king95_parts.obj` has **20 separate rigid parts** (`part_1..part_20`), each bound 100% to one bone with no weight painting. The GLB version (`lab/game/assets/t3_king.glb`) maps them onto a 17-bone skeleton: Root, Hips, Chest, Head, L/R Shoulder, Arm, ForeArm, Hand, UpLeg, Leg, Foot. Without its pose tables the parts sit apart (the "pieces" problem), which is why T3 King is `BLOCKED-rig` for T-pose refs. |
| **Tekken 6** (`teardown/tekken6/TEARDOWN.md`) | Models are still encrypted (PSP DATA401). The documented structure is a **base body plus layered customization items** that attach to named **sockets** (`head_socket`, `hand_L`, `back`, ...) and render on top of the base. |
| **TTT2** (`teardown/tekken-tag-tournament-2/`) | Still inside Xbox 360 STFS blobs, not extracted yet. Expected to use the same Namco family as T6 (base plus socket items). |
| **Tekken 7** (`teardown/tekken7/king/`) | One skinned mesh split by **material slot** per region: Head, Torso, Arms, Hand, ArmBelt, ArmProtectors, Neck, PantsUpper, PantsLower, PantsLogo, BootProtector1/2, FootAcc, MaskFur, Eye, Teeth. |
| **Tekken 8** (King S2/1P release rips) | Separate skinned meshes per **body slot** sharing one skeleton: `fac` (face/head), `bdu` (upper body), `bdl` (lower body), `bdf` (full/feet), plus Head/Torso/Legs/Feet FBX parts. |

**Western Heart segment standard** (merging the T3 rigid parts, the T6 sockets, and the T7/T8 body slots):
`head` (mask), `torso`, `arm_upper_L/R`, `arm_lower_L/R`, `hand_L/R`, `hips/trunks`, `leg_upper_L/R`, `leg_lower_L/R`, `foot_L/R`,
plus sockets `head_socket`, `back`, `hand_L`, `hand_R`, `tail`. Each segment is a **separate skinned mesh on the shared skeleton**
(skinned like T7/T8, not rigid like T3, so it deforms cleanly), named `seg_<segment>`, so the creation suite can swap them.

## Rules
- Never overwrite or delete the source/teardown file; derived files are new.
- Co-authoring must change silhouette, texture, and logos enough that no one can say "that's King."
- Track what's still raw donor content in each character's README before commercial release.
