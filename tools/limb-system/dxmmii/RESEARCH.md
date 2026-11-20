# DXMMII Four-Arm Rig Research (2026-10-16)

Goal: rig DXMMII's 2 extra detachable arms — attach / hide / grow / retract
in-game, fighting gyro style or human style with 4, 3, or 2 arms.

## TL;DR recommendation

Build the extra arms as a **separate modular mesh parented to its own bone
chain** (not merged into the body), driven by **Rigify-style FK/IK controls**,
with three states per extra arm: ATTACHED (full scale, fighting),
RETRACTED (bone scale ~0.01, tucked inside torso), DETACHED (unparented,
floating — animated as an independent object, exactly like the reference
image). Use **blend shapes** on the shoulder stump for the "growing" moment
so the arm appears to push out of the body rather than pop. Study the Goro
MK Onslaught FBX (real game bones, 4-arm layout) as the anatomy reference.

---

## 1. Rig files found

| File | Format | Rigged? | Source | Notes |
|---|---|---|---|---|
| Goro (MK Onslaught, based on MKX look) by a9strack3d | FBX | YES — in-game bones, tested posing | [DeviantArt](https://www.deviantart.com/a9strack3d/art/Goro-Mortal-Kombat-Onslaught-3D-Model-956728529) (MediaFire link on page) | **Best lead.** Direct game rip converted in Noesis. 4-arm bone hierarchy intact. |
| Goro statue scan | OBJ / FBX / GLTF / GLB / DAE | No (statue) | [rigmodels.com](https://rigmodels.com/model.php?view=Goro_Mortal_Kombat-3d-model__da17b4e9509e4727ab47c9e1eb45df6f&searchkeyword=plage&manualsearch=1) (free) | 110k faces, 4K texture. Good anatomy reference, not a rig. |
| Goro & Kintaro (MK9) | .mdl (Garry's Mod) | YES (game bones) | [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=2041572715) | MK9 models. Needs GMod to extract; bones survive conversion to FBX via standard tools. |
| MK9 Goro & Kintaro (alt upload) | .mdl (Garry's Mod) | YES | [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=127570920) | 20k subscribers, well-tested upload. Same conversion path. |

**Not found:** no free Kintaro-only rig outside the two MK9 Steam packs above;
no Goro in XPS/XNALara format (DeviantArt XPS community has large MK
collections but no confirmed Goro XPS — check
[xnalara-customized gallery](https://www.deviantart.com/xnalara-customized/gallery/)
and [JoinSpider's MK XPS collection](https://www.deviantart.com/joinspider/favourites/84977028/mortal-kombat-xnalara-xps)
as a fallback). **Checked owner's repos: no Goro/Kintaro/Sheeva files exist
locally** (only false-positive matches in Python venvs) — these need pulling.

Machamp (4-armed Pokemon) models are all unrigged STL statues — not useful
as rigs.

---

## 2. Four-arm rigging technique

### Rigify (Blender, built-in, free) — handles extra arms natively
Blender's Rigify addon explicitly supports multi-limb characters: its modular
rig samples can generate a full FK/IK control system for "five arms and one
leg," and rigs can be re-generated to add more limbs (e.g. a sixth arm or
tail) without losing existing features or animation data. This is the fastest
proven path: build a Rigify meta-rig with 2 standard arm samples + 2 extra
arm samples parented to the upper chest/shoulder region.
Docs: https://docs.blender.org/manual/en/latest/addons/rigging/rigify.html

### Bone layout (from Goro anatomy)
- Main arms: standard Shoulder → UpperArm → Forearm → Hand chains off the chest.
- Extra arms: second pair of Shoulder → UpperArm → Forearm → Hand chains,
  parented to the **upper chest / trapezius area** (Goro's lower pair sprouts
  below the main pair; Machamp's upper pair sits on top of the shoulders).
  For DXMMII, socket them at the upper back/shoulders so the retracted state
  tucks them behind the torso.
- Keep each arm chain **unconnected** (free parent, not bone-connected) so
  extra arms can be repositioned or unparented without breaking the spine.

### IK/FK
Give each arm FK + IK with snapping (Rigify generates this). The extra arms
want IK most of the time (gyro style = big sweeping arcs, hands planting on
targets), FK for idle sway and the floating detached state.

---

## 3. Detach / hide / grow / retract mechanics

Three complementary techniques, used together:

1. **Modular mesh + bone visibility (attach/detach/hide).** The extra arms are
   their own mesh objects, skinned only to their own bones. Detach = unparent
   the arm bones from the torso and animate them as free objects (this is
   exactly the reference image: arms floating above the head). Hide = scale
   bones to ~0.01 and/or toggle mesh visibility. This is the standard game
   approach — no re-skinning needed, cheap at runtime.

2. **Bone scaling (grow/retract).** Animate the extra-arm root bone scale from
   0 → 1 for growing out, 1 → 0 for retracting. Cheap, works in any engine,
   and reads clearly in a fighting game. Pair with a slight shoulder-bulge
   so the growth has a physical origin point.

3. **Blend shapes / shape keys (grow transition + stump cap).** For the
   growing moment, a blend shape on the shoulder that opens a "socket" while
   the arm scales up sells the effect far better than a raw scale pop. Also
   use a blend shape for the stump cap when an arm is fully detached so you
   never see a hollow hole in the torso. (Source: multi-limb rigging notes —
   blend shapes for folded/unfolded/extended/retracted limb states.)

State machine per extra arm: `ATTACHED (fighting) ↔ RETRACTING ↔ HIDDEN ↔
GROWING ↔ ATTACHED`, plus `DETACHED (floating)` as an independent object
state. Each state is just bone transforms + visibility + one blend shape —
no special engine features required, works in Godot/Unity/Blender alike.

### Mechanical-rig note (DXMMII is a patchwork robot)
KatsBits' mechanical rigging guide is directly relevant: build limbs from
rigid parts, one mesh per part, each part parented to its bone, pivot axes on
grid points. DXMMII's stitched-plate body suits this better than smooth
skinning.
https://www.katsbits.com/site/gingerbread-rigging/

---

## 4. Open-source / free study material

- **Rigify** — ships with Blender, no download needed. Study its
  `limbs.arm` rig sample; generate a 4-arm meta-rig in minutes.
- **Blender manual: bone chains & parenting** — how unconnected chains and
  multi-child bones work:
  https://docs.blender.org/manual/en/latest/animation/armatures/structure.html
- **Skeletal animation (Wikipedia)** — hierarchy/parenting fundamentals:
  https://en.wikipedia.org/wiki/Skeletal_animation
- **Multi-limb rigging tips (LinkedIn community article)** — planning,
  FK/IK/spline-IK choice, weight painting + blend shapes for limb states:
  https://www.linkedin.com/advice/0/what-some-tips-rigging-skinning-character-multiple-zhude
- **XPS/XNALara addon for Blender** (for any XPS models pulled later):
  https://github.com/mayloglog/XNALaraMesh-blender4.4

---

## 5. Suggested next steps for the rig lane

1. Pull the Goro MK Onslaught FBX (DeviantArt → MediaFire link) — study its
   4-arm bone hierarchy and copy the layout.
2. Build DXMMII's extra arms as separate meshes + bone chains in Blender,
   generate controls with Rigify.
3. Implement the 5-state arm state machine (attached / retracting / hidden /
   growing / detached-floating).
4. Add shoulder-socket blend shapes for grow/detach transitions.
5. Retarget one gyro-style animation set onto the 4-arm rig as proof.
