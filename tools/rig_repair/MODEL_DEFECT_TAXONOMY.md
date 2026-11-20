# MODEL DEFECT TAXONOMY — the definitive catalog

Owner doctrine (2026-10-15): perfect ONE model to learn every defect class, then
apply it to every model in every game. **UNASKED DEFORMATION = BUG.** Any mesh
deformation, tear, webbing, stretch, or separation that was not explicitly asked
for is a glitch — never a feature. Nothing ships with any of these.

Every defect below: exact name, what it looks like, root cause, the AUTOMATIC
fix (proven open-source, no hand-painted weights — owner law), and how it is
verified. Sources: the Pantera repair saga (case-1 → v2 → v3), the Stick-Up
pipeline validation, `tools/rig_repair/PR*_NOTES.md`, `README.md`,
`RESEARCH.md` (draft PR #182).

---

## 1. Mirrored skinning
**Aliases:** L/R swapped skin, mirrored weights, cross-bound skinning.
**Looks like:** every animation tears the limbs across the body — arms rip
diagonally through the torso on Idle. (`rig-a-20261015-150616/out/visuals/final_before.png`)
**Root cause:** side verts bound to opposite-side bones (left verts on Right*
bones and vice versa). Pantera: 5,805 of 5,805 side-weighted verts (|x|>0.15m)
on the wrong side — a rip-authoring defect.
**Automatic fix:** `swap_lr_joints.py` — remaps each `JOINTS_0` index to the
mirrored bone name. Positions, weights, IBMs, nodes, clips untouched. Refuses
to run unless ≥99% of side verts are wrong (won't touch a correct model).
**Verified:** opposite-side verts 5805 → 0; arm mesh stretch 11.95 → 2.11
(gate 2.5). Output byte-identical to the pipeline team's validated artifact.

## 2. Skeleton misfit
**Aliases:** bones outside the mesh, skeleton outside skin, joint dislocation.
**Looks like:** limbs bend around empty air; joints visibly outside the body
surface; Grok's rig-gate measured p99.9 stretch 16.6–52.9 on Stick-Up v1.
**Root cause:** joint bind positions don't sit inside the mesh volume (Stick-Up:
arm bones ~5cm outside the mesh). Weights follow the wrong pivots.
**Automatic fix:** `refit.py` — volume-mode skeleton refit: ray-cast each
joint through the mesh on 3 axes; inside → move to shortest-chord midpoint;
outside → nearest surface + half inward thickness; clamp 0.10m; recompute
inverse bind matrices on export so existing clips play unchanged.
**Verified:** joints inside mesh volume; Stick-Up stretch 27.7–44.7 → 10.7–15.1
after full pipeline. (Known limit: single-mesh raycast — multi-mesh models need
the fixed version; see case-2 notes.)

## 3. Floating attachments
**Aliases:** detached accessories, unbound attachments, ghost cuffs.
**Looks like:** accessory meshes hover in mid-air where the limb USED to be —
Pantera's red/black wrist cuffs (meshes `belt2`, `buckles`) floated at T-pose
wrist positions while the arms moved away. (`defect-shots/v2/pair_cuffs_S1.png`
BEFORE: cuffs in empty air, arms raised without them.)
**Root cause:** attachment verts weighted 100% to a distant bone (cuffs → 100%
Spine/Spine1) instead of the limb they sit on. A cuff weighted to Spine is not a
style — shipped fighters bind attachments to the nearest limb bone (RESEARCH.md
teardown rule 2); this is a rip defect.
**Automatic fix:** `transfer_weights.py` — k-NN inverse-distance weight copy
from nearest correctly-weighted body verts (cuffs ← arms mesh). Zero
hand-painted weights.
**Verified:** cuff-to-wrist tracking 0.78m → 0.39m; AFTER picture shows cuffs
riding the raised wrists, nothing floating.

## 4. Attachment stretch
**Aliases:** emblem smear, logo warp, decal stretch.
**Looks like:** the chest/waistband logo smears and distorts when the torso
moves — Pantera's `logo` mesh hit 21–31× edge stretch on spine bend.
**Root cause:** attachment weighted to the wrong bone chain (`logo` → Spine/Spine2);
spine rotation shears the decal verts.
**Automatic fix:** `transfer_weights.py` — logo ← torso mesh nearest-vert copy.
**Verified:** 31.72 → 1.43 (bend), 24.09 → 1.39 (twist) — under the 2.5 gate;
waistband stays put in bent-spine renders.

## 5. Hip tear / pelvis split
**Aliases:** crotch tear, hip separation, pants rip.
**Looks like:** in wide stances the pants split open at the crotch — background
shows through the tear. (`defect-shots/v2/pair_pants_S3.png` BEFORE: white slit
at crotch.) Thighs showed the same class (8.49×).
**Root cause:** `pants` weighted to UpLegs only, zero Hips weight — the pelvis
band has no blend across the hip joint. Shipped fighters always blend Hips↔UpLeg
(RESEARCH.md teardown rule 3); UpLegs-only is never shipped.
**Automatic fix:** `transfer_weights.py` — pants hip region ← torso/thigh
nearest-vert blend.
**Verified:** 15.56 → 1.37 (stance), 19.32 → 1.26 (crouch); thighs 8.49 → 1.02;
AFTER picture: crotch covered, no tear.

## 6. Armpit webbing tear
**Aliases:** armpit hatch, armpit split, shoulder tear. (Owner-spotted on v2.)
**Looks like:** raising the arm opens the armpit like a hatch — a wedge-shaped
gap where the arm meets the torso. (`defect-shots/v3/armpit_v2.png`)
**Root cause:** verts in the armpit fold are hard-split — 100% arm or 100%
torso, no blend zone. The arm-weighted group swings with the arm; the
torso-weighted group stays; they peel apart. See WEBBING DOCTRINE below: this
is a *webbing tear*, the bug form of anatomical webbing.
**Automatic fix:** `armpit.py` — de-bleed (arm weights → 0 beyond 0.14m of arm
segments, redistributed to torso) + contrast sharpen (p=1.6) of the arm/torso
blend in the transition zone + topology smooth + normalize + 4-influence cap.
Fully automatic (numpy/scipy).
**Verified:** no visible hatch in arms-raised renders (`defect-shots/v3/armpit_v3.png`);
stretch < 2.5 in the zone. (v3 in progress at time of writing.)

## 7. Inner-thigh / legpit webbing tear
**Aliases:** groin hatch, thigh split. (Owner-spotted on v2.)
**Looks like:** wide stance opens the inner thigh like a hatch.
(`defect-shots/v3/thigh_v2.png`)
**Root cause:** same as #6 at the hip fold — hard-split UpLegs vs Hips/torso
weights, no gradient across the groin fold.
**Automatic fix:** legpit logic — the `armpit.py` method applied to the hip
fold (de-bleed + sharpen + smooth + normalize). Automatic only.
**Verified:** same bar as #6 (v3 in progress).

## 8. Candy-wrapper (twist collapse)
**Aliases:** twisting collapse, joint pinching.
**Looks like:** rotating a limb (forearm, thigh) collapses the mesh into a
twisted candy-wrapper pinch at the joint.
**Root cause:** linear blend skinning (LBS) interpolates rotations linearly;
large twists collapse volume. Exacerbated by hard-split weights at the twist
joint.
**Automatic fix:** SmartWeight's candy-wrapper detector ported as a `rigcheck/`
gate stage (RESEARCH.md Tier 2); targeted fix operators (Laplacian smooth,
auto-normalize) — never hand-painted. Dual-quaternion skinning reduces it
engine-side but the weights must be right first.
**Verified:** detector reports 0 candy-wrapper joints; twist poses render clean.

## 9. Weight bleed
**Aliases:** torso "wings", limb weights on body, cross-region leak.
**Looks like:** torso skin flies with the arm in crucifix pose ("wings");
patches of body follow the wrong limb.
**Root cause:** k-NN / heat skinning bled limb weights onto torso verts far
from the limb (measured 24–29× stretch on Stick-Up).
**Automatic fix:** `armpit.py` de-bleed (arm weights → 0 beyond 0.14m) +
`separate.py` (>0.20m → nearest plausible bone of correct region).
**Verified:** "wings" visually gone in crucifix; stretch 28–45 → 9.5–13.3.

## 10. Wrong-region binding
**Aliases:** hands glued to legs, cross-bound verts.
**Looks like:** a hand follows the leg, or fingers stick to the thigh, during
animation.
**Root cause:** verts weighted to a bone in the wrong body region (measured:
812 hand-region verts >0.5 weighted to leg bones; 2,675 verts >25cm from their
dominant bone).
**Automatic fix:** `separate.py` — topology + skeleton-geometry reassignment to
the nearest plausible bone of the correct body region (arm/leg/torso via joint
synonym tables). Loud skip on non-Mixamo, never silent.
**Verified:** mis-bound verts → 0; stretch 28–45 → 9.5–13.3 (with refit).

## 11. Zero-weight verts
**Aliases:** unweighted verts, dead verts.
**Looks like:** verts stay frozen at the bind pose while the mesh moves — or
collapse to the origin.
**Root cause:** no bone influences on the vert (weight sum = 0).
**Automatic fix:** `detect` flags them; `transfer_weights.py` / reskin assigns
by proximity. **Verified:** 0 zero-weight verts (detect JSON).

## 12. NaN weights
**Aliases:** corrupt weights.
**Looks like:** exploding triangles, verts flying to infinity.
**Root cause:** NaN values in the weight array (bad export/toolchain).
**Automatic fix:** `detect` flags; stage rebuilds the affected influences.
**Verified:** 0 NaN (detect JSON).

## 13. Over-influenced verts (>4)
**Aliases:** too many bones per vert.
**Looks like:** nothing visible in DCC — breaks at engine import (UE4-era
fighters use ivec4 joint IDs + vec4 weights; extra influences are dropped
arbitrarily, causing pops).
**Root cause:** more than 4 non-zero influences per vert.
**Automatic fix:** pipeline invariant — prune to top-4, renormalize.
**Verified:** max influences ≤ 4 on every vert, always asserted.

## 14. Unnormalized weights (Σw≠1)
**Aliases:** weight sum drift.
**Looks like:** verts shrink toward / grow away from joints (scale drift under
deformation).
**Root cause:** influences don't sum to 1.
**Automatic fix:** normalize; hard assert |1−Σw| < 1e-5.
**Verified:** normalized on every vert, always asserted.

## 15. Open edges / holes
**Aliases:** mesh tears, boundary holes, see-through mesh.
**Looks like:** background shows through where body should be (the 2026-10-11
missing-torso incident: a rectangular chunk of torso gone).
**Root cause:** unwelded verts / cut topology.
**Automatic fix:** `weldcap.py` — weld by POSITION (never `bmesh.remove_doubles`,
which manufactured 19 holes in testing), recalc normals, HARD ASSERT
`boundary_edges_holes == 0`. Fails loudly; never blind auto-cap.
**Verified:** assertion passes on the exported file.

## 16. Non-manifold edges
**Aliases:** bad topology edges.
**Looks like:** shading seams, physics/deformation glitches.
**Root cause:** edges shared by ≠2 faces.
**Automatic fix:** `weldcap.py` asserts non-manifold count does not increase
vs input. **Verified:** assertion on export.

---

## WEBBING DOCTRINE (owner law 2026-10-15)

**Anatomical webbing is CORRECT and REQUIRED.** Where the body folds — armpit,
groin/inner thigh, elbow pit, knee pit, finger webs — the skin must flow as a
smooth natural gradient from one part to the next. This is not a defect; it is
anatomy. Reference: Tekken 7 teardown models' fold weighting.

**Two forms, opposite verdicts:**

| | Anatomical webbing (TARGET) | Webbing tear (BUG) |
|---|---|---|
| Weights | Smooth blended gradient across the fold (e.g. arm→torso shares 70/30 … 30/70 across the band) | Hard split: 100% one side / 100% the other, no transition |
| Motion | Fold stretches like skin, one piece flowing into the next | Fold opens like a hatch — wedge gap, background shows through |
| Fix | The gradient IS the fix (`armpit.py` sharpen + smooth) | De-bleed the leak, build the gradient |

**Rule:** webbing is fixed by getting the gradient right across the fold —
never by deleting geometry, never by hand-painting. The fold must look natural
in every pose of the extreme battery.

---

## GATE STANDARD — the bar every model clears

No model ships to video, cutscenes, promos, or shows without ALL of these:

1. **2.5 max edge stretch** — p99.9 per mesh, per clip, across the 6 standard
   clips (idle, walk, jab, kick, hit_react, knockdown) AND the 8-pose battery.
2. **8-pose extreme-pose battery** — arms full overhead, arms crossed tight,
   wide stance + deep crouch, spine bent hard forward, spine twisted, combined
   wrestler arch, finger-gun stress, rest. Every mesh < 2.5 in every pose; zero
   floating/detached parts; zero explosions. (The automated, measurable form of
   the industry ROM pass — RESEARCH.md.)
3. **4-influence cap** — max 4 bones per vert, always.
4. **Σw = 1** — |1−Σw| < 1e-5 on every vert, hard-asserted.
5. **0 zero-weight, 0 NaN** — asserted by `detect`.
6. **0 open edges** — welded by position, hard-asserted by `weldcap.py`.
7. **Proof pictures required** — before/after in identical stress poses, opened
   and checked with human eyes (media proof standard). A worker's "verified" is
   a claim, not a fact.
8. **Owner per-model OK** — no model swaps merge without the owner's explicit
   per-model approval.

---

## PIPELINE SCOPE — where this is going

**Today:** the pipeline (9 stages + `transfer_weights.py` case-2 + armpit/legpit)
repairs models that HAVE skeletons and weights. Every stage writes a versioned
file; inputs are never touched.

**Next: unrigged intake.** The pipeline must eventually take completely
UNSKINNED/UNRIGGED fresh models straight through and output working-perfect
models — auto-rig + auto-skin + all fix stages, fully automatic.

- **Exists today:** `refit.py` (volume-mode skeleton fit — positions joints
  inside the mesh by ray-cast; the auto-rig core) and `reskin_heat.py`
  (Blender bone-heat auto-skin) / `reskin.py` (Surface-Heat-Diffuse, MIT —
  never fails, the safety net).
- **Missing:** the orchestrated unrigged→rigged→fixed path in `pipeline.py`
  (detect-no-skeleton → refit → heat-skin → separate → armpit → gate → proof),
  plus SmartWeight's four detectors as `rigcheck/` stages (RESEARCH.md Tier 2).
- **Rejected:** neural re-riggers (RigNet, Anymate) for existing models — they'd
  discard authored animation compatibility. Revisit only for AI-generated
  meshes that arrive with no skeleton at all.

**Standing laws this document serves:** NO hand-tooling (proven OSS automatic
methods only); UNASKED DEFORMATION = BUG; proof pictures before any render;
owner merges nothing manually — clean green PRs merge themselves.
