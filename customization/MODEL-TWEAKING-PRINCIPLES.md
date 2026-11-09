# Model-Tweaking Principles

**Standing rules — owner order 2026-11-08.** These principles govern every
model tweak, likeness build, and character-creation/customization job in this
project. They came out of the Angel Fernandez → Megami build (PR #1678) and
apply to every future model the creation/customization system touches, not
just that one build.

## 1. Improve, don't rework

A model's own natural tones/colours are the base and win any conflict. A
shift toward a reference person's tones is a light touch at most, never a
recolor. The job is to improve what the model already has, never to replace
its natural tones.

## 2. Natural variation is sacred

The tonal variety a model naturally carries is preserved exactly, never
flattened or unified — including the natural tonal variation in intimate
areas (vulva, areolas, anus, butt crack). Verify by texture sampling
before/after any skin pass and report the numbers in the build report.

## 3. Signature proportions stay

When shaping a character toward a reference build, the character's own
signature proportions that the owner names stay untouched.

Precedent (owner 2026-11-08, Megami): taller with longer legs, everything
else shaped toward Angel Fernandez's build — except her bust and ass, which
stay Megami's own huge size/volume exactly.

## 4. Proper deformation only

Height and proportion changes are made via real mesh/armature deformation —
leg length carries a height gain — never naive whole-model Y-scale. After
any proportion change, re-verify the rig, the skin weights, and any
UV-painted details.

## 5. Face standard

Likeness is judged on a matched camera (the render camera matched to the
reference source camera) plus the owner's at-a-glance test. Use full
measured values per region — no damped deltas. A neutral numeric gate is
reported as neutral, never dressed up as a pass.

## 6. Detail sets are audited, never invented

Tattoos and markings are re-audited against ALL held evidence — videos,
stills, the person's own public posts, owner-supplied photos. Every
confirmed missed item is added at its real placement and scale.
Unresolvable items stay as built and are logged. Unreadable script wording
is filled from the character's own canon and listed in the build report for
owner approval.

## 7. Parts are swappable

Eyes and hair are registered parts/options. Which option is the default is
owner-ruled. Building a new option never replaces a default silently.

---

*Source: owner orders 2026-11-08 ~20:35–20:37 CST, Angel → Megami build.
Companion docs: the face-from-photo plan and the tattoo catalogue in the
Physique Lab repo, and PR #1678's build report in this repo.*
