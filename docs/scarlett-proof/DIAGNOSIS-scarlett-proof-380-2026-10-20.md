# Diagnosis — why the PR #380 Scarlett Wiggle 2 proof looked "deformed and crazy"

Owner verdict on #380 (2026-10-20 ~14:00 CDT): "that still looks really bad on the
rig and mesh deformation and the model is looking crazy… I can't validate that
cause I can't tell what's happening."

## Verdict up front

The owner was right about the deliverable and wrong about nothing he could see:
the #380 proof was unjudgeable. But the failure was **render presentation and
freeze-frame selection, not the model, not the rig, and not the Wiggle bake.**
Every layer underneath the render checks out (details + evidence below).

## 1. What #380 actually rendered with (wiggle-scratch/render_stills.py)

- 320×320 px, EEVEE with **4 TAA samples**
- World color **(0.05, 0.05, 0.05)** — a near-black void
- Three small point lights, no ambient/world fill, no GTAO
- Stills taken at frames 10/30/50/70 of a CMU lambada — f30/f50 are the deepest
  back-arch frames of the phrase

At 320² in near-darkness, any character reads as a gray scribble. The two front
stills (vid_front_f30.png, vid_front_f50.png) show exactly that: a pale-black
contorted silhouette, face unreadable.

## 2. The model is not deformed — three independent checks

1. **Skinning**: PR #364's diagnosis (tools/anim-retarget/DIAGNOSIS-star-scarlett)
   verified production quality: weights normalized, max 4 influences, no
   cross-body strays. Re-confirmed this run on scarlett_base.blend: **0 of 1,111
   pose bones differ from rest** in the saved file.
2. **The "spike" is her tail.** The blade-like protrusion visible at the hip in
   stills is a tail: raw-geometry audit found its verts 100% weighted to
   `DEF-tail.008`, rooted exactly where a tail roots. In freeze frames it reads
   as a spear; in motion it reads as a tail.
3. **The contortion is the mocap.** CMU 55-02 (lambada) contains deep-arch,
   leg-split phrases. A single still at the bottom of the arch looks broken; at
   24 fps it reads as dance. #380's chosen stills maximized the effect.

## 3. The Wiggle 2 bake is exactly scoped — fcurve audit (this run)

Compared the baked action in scarlett_wiggle2.blend against the pre-wiggle
mocap action in scarlett_mocap.blend, curve by curve (SHA-256 over keyframe
points per fcurve):

- **Face: never keyed by anything.** Neither action contains a single face-bone
  fcurve (no brow/lid/jaw/lips/nose/cheek/tongue curves exist to change).
  "Face untouched" is not a claim — there is nothing in either file that moves
  her face.
- **Wiggle changed only the jiggle chains**: DEF-breast.L/R + .001 curves
  modified, deeper segments (.002/.003) added; Butt_L/R + .001 modified,
  .002–.004 added. 18 jiggle bones total.
- **Every other bone's curves are hash-identical** between the mocap and baked
  actions. The bake did nothing outside its remit.

For that reason this run re-verified the existing bake instead of re-running
it: a re-bake would reproduce the same action; the audit is the stronger proof.

## 4. Her look in this file (why she renders black-and-white)

The surviving blends are a *reduced working copy*, and their material state is
part of why she doesn't read as "a woman" in any render:

- Body materials' Base Color = **vertex colors** (Mix node, factor 1.0 → the
  Color Attribute input) — a black-and-white pattern painting. That is her
  design in this file (snake-pattern skin; she also has the tail and goth
  makeup textures), but it means no lighting setup can make her skin-toned:
  there is no skin-tone layer in the chain to reveal.
- Metallic and Coat Weight are driven by texture channels (sweat-bump maps),
  which is why dim renders go mirror/chrome instead of matte.
- The texture set is a composite (OsoSnakefolk pattern mask, Kaede9 face,
  goth lip map, HF_TH nail maps…); the packed 4K Tripo material in the file
  is assigned to no object, and its "color" texture is a red/yellow emblem
  graphic, not skin.
- The full master — Scarlett_tqZQxX.blend, 36 textures incl. skin micro-bump —
  is the TeraBox file (blocked lane). This run did not invent a recolor:
  fabricating her "real" look would be hand-tooling a new design the owner
  never approved. What is proven here is the animation on the real rig.

Also found: scarlett_base.blend ships with **every mesh hide_render=True** and
contains no camera or lights. Run #2's "baseline" rendered a blank gray frame
for that reason (plus a bound_box framing bug) — that blank is part of how the
bad proof propagated.

## 5. The re-proof (this run)

- Same baked blend (scarlett_wiggle2.blend), rendered properly: bright studio
  world (0.55), large soft area key/fill/rim + soft sun, GTAO, TAA 16,
  480×600, all 72 frames → scarlett-jiggle-proof-v2-20261020.mp4.
- Baseline: scarlett_base.blend at rest, same studio family at 640×800 →
  scarlett-baseline-look-20261020.png (she stands coherent, pattern + tail
  visible — the same woman as the video, at rest).
- In motion the arch frames pass in 1–2 frames and the jiggle reads on the
  chest and glute chains the bake actually drives — which is what the owner
  was asked to judge and couldn't.

## 6. Source protection

star_bound.blend / ~/workspace/star-rig-work/ was lost to disk cleanup while
disk sat ~96%. Before any render work this run, the surviving foundation was
stored to GitHub, hash-verified with a pull-back check:
release `scarlett-source-blends-v1` on mhvnsnt/western-heart —
scarlett_base.blend (sha256 cd4087b0…), scarlett_mocap.blend (52366ca2…),
scarlett_mocap.blend1 (c0ea5058…), scarlett_wiggle2.blend (f79ce8f0…).
Her foundation cannot vanish again.
