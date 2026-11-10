# HOW THESE LASHES WERE MADE — Megami glam lashes v7 (the standing method)

Owner approval: 2026-11-10 — "That's it that good lashes save those to
the repo and how u made them." v7 is the lash build of record. Six
earlier builds (v1–v6) failed for ONE reason, found and fixed in v7.
This document exists so no future lash work repeats those six failures.
Plain language first, numbers after. The full lane record is in
`LASH-FIX2-REPORT.md` next to this file; the exact builder/diagnostic
scripts are in `tools/` next to this file, copied verbatim.

## The files

- `lashes_glam_megami.glb` — the standalone lash part (this folder).
  981,556 B, sha256
  `f85ccd5934064245d9a577ec11297634cbbd1a4b8439fa9af908c5b7f685809b`
- The merged build (the same lashes merged onto the corr3_a / body-v5
  carrier, `megami-angel-gnmface-v2-lashfix.glb`, 59,748,225 B,
  sha256 `ab88c5b3740819a703211185d6011c908a60e46548a54702f53aad14ae06ab40`)
  is too big for git. It is preserved as a release asset:
  https://github.com/mhvnsnt/western-heart/releases/tag/megami-lashfix-v7-20261110
  (streamed back down and hash-verified at landing time).
- `proof/` — the four gate frames (front, q34, both eye close-ups) and
  the two marker-verification frames described below.

**Preservation only.** This folder saves an approved part and its
method. The lashes are NOT wired into any roster entry, profile, or
game loader by this landing, and nothing here combines them with the
glam/face/hair lines. The face hold still applies.

## Spec (unchanged from the approved glam set)

Style of record: the owner-approved glam set — long and winged.

- 27 lid stations + 8 wing stations per eye
- Band rise (band height): 1.05 × iris diameter
- Wing: 0.60 eye-widths long, rising 0.55 × iris diameter
- Base offset (root distance off the margin, along its normal): 0.55 mm
- Lowers: subtle by spec — length 0.11 × the eye aperture

Geometry of the shipped part: 11,466 verts / 19,898 tris, built by
`tools/lash_build7.py` into geometry, written by
`tools/lash_write_glb7.py`.

## Why v1–v6 failed: the roots were on the wrong curve

Every earlier build rooted the lashes on an extracted "lid margin"
loop. That loop is real geometry, but it is NOT the line lashes grow
from. It is the **seam between the Face-2 and EyeSocket-2 prims**, and
it sits **on the eyeball, deep inside the socket**:

- Distance from that loop to the eyeball surface: mean ≈ 0 mm — it
  hugs the ball.
- Its opening (aperture) measures 16.0 mm (posx eye) — almost twice
  the visible opening of the eye (7.66 mm).
- Markers placed on it are **completely invisible** in an eye
  close-up: the lid fold covers the whole loop from any camera.

So strands rooted on that seam travelled *inside the lid skin* and
only poked out at the lid fold. That is exactly how v1–v6 read on
screen: roots appearing to stop at the crease, a bare pink band of lid
below them, a straight curtain instead of a lash line. The old
root measurement (0.549 mm) was accurate — it was measured against a
curve the eye never sees.

How far off: the visible lash line sits **mean 3.96 mm / max 4.98 mm**
away from that seam loop. Every build before v7 was rooted ~4 mm
under the fold.

Diagnostics that proved it (in `tools/`): `lash_diag_margin.py` and
`lash_diag_loops.py` (the numeric check), `lash_diag_overlay.py` and
`lash_diag_overlay2.py` (markers rendered in screen space — invisible
on the seam, on the visible edge on the real line).

## The fix: extract the VISIBLE lash line

`tools/lash_margin_visible.py` finds the line the eye actually shows:

1. Work in the eye-local frame. Fire a dense grid of rays from the
   front of the eye.
2. Classify each ray: does it hit the **eyeball first**, or the
   **skin first**?
3. Per lateral column, the visible margin is the skin hit just
   outside the run of ball-visible points — the edge where the
   opening of the eye actually is.
4. **Marker-verify in screen space before building anything:**
   markers placed on the extracted curve must trace the visible edge
   of the eyeball opening exactly in a rendered close-up, on both
   eyes. Those frames are `proof/diag2_eye_posx.png` and
   `proof/diag2_eye_negx.png`. If the markers don't trace the visible
   edge, the curve is wrong — do not build on it.

Visible aperture measured this way: posx 7.66 mm / negx 3.40 mm
(the negx eye reads narrower because the corr3_a face morph narrows
that lid — a face fact, not a lash fact; both eyes get the identical
lash treatment).

v7 roots sit on this visible margin. Measured on the shipped
geometry (n = 70 clump roots, `tools/lash_measure_roots.py`):

- Root to visible margin: **0.550 mm mean / 0.550 mm max** — the spec
  base offset, by construction.
- Root to the old seam loop: mean 4.72 mm / max 16.41 mm (the max is a
  far wing root stepping away along the temple, by design).

## Construction (what v7 does, step by step)

### Fan — the growth direction rotates by station

v6 grew every strand straight up (world-up), which is why it read as
a curtain of slats. v7 rotates the growth direction smoothly along
the lid:

- Outer corner: **+54°** (toward the wing)
- Quarter station: +30°
- Centre: ~0°
- Then −16°, and **−36°** at the inner corner

Length compensation is sqrt-cos: outer strands end up ≈ 1.3× the
centre length (a constant up-rise would force 1.87×). Tips drift
further in the lean direction, so the band radiates instead of
standing in a row.

### Curl — cubic bezier paths, skin is only a floor

Each strand path is a cubic bezier:

- It emerges mostly **forward** off the lid: 0.80 forward / 0.55
  growth-direction mix at the start.
- Forward bow: **0.36 × rise** at mid-path, **0.30 × rise** at the tip.
- The skin surface is used ONLY as a minimum forward-clearance floor
  (a precomputed surface grid + 0.9 mm). It never shapes the path —
  in v6 the path copied the lid wall, which flattened the curl.

### Clumps — 6 strands, ONE root

- One clump per station: **6 strands sharing a single root**
  (root jitter ±0.06 mm).
- Per-strand direction jitter ±5° / ±4°, length jitter 0.84–1.00.
- Strand root diameter 0.116 mm, tapering to a point.
- Roots bundle tight and dark; tips splay; the gaps fall between
  stations (station pitch ≈ 0.71 mm).

### Falsie strip

A thin ribbon seated on the visible margin itself (0.75 mm up-slope)
runs under the roots, so the root line reads as one dense dark line —
the physical band a real false lash has. Without it the roots read as
separate dots.

### Wing — a continuation of the lid, not a separate piece

There is no second anchor curve for the wing. Wing roots step along
the temple **from the outer corner itself**:

- Spacing grows as f^1.25 — the first wing root is 0.97 mm past the
  last lid root.
- Rise grows as f^1.6.
- Fan angle continues 54° → 80°.
- Strand length tapers down to 0.45×.
- Every wing path point is surface-contained: **≤ 1.2 mm off the
  skin** in the shipped build.

This took three rounds: v7a (92° angle cap) threw three loose bars
past the silhouette; v7b (80° + 2.2 mm containment) killed the bars
but left two edge ticks; v7c (1.2 mm containment) is the shipped
build.

### Lowers

3-strand mini-clumps on the visible bottom margin, extracted with
the same ray method, spec length 0.11 × aperture. Subtle on purpose.

### Colour

Near-black and opaque: **RGB 0.012, alpha 1.0** on every ring, alpha
0.85 only at the single tip point. v6 used alpha 0.80 on the top ring,
which is what washed grey. Feathering comes from taper + splay +
length spread only — never from transparency.

## Two bugs that were NOT the design — both fixed, both checkable

1. **GLB writer index-count bug (found in v6).** The writer set the
   index accessor count to the *triangle* count (3,288) instead of
   the *index* count (9,864). Three.js then drew only the first 1,096
   triangles — zero triangles of one whole eye were ever rasterised,
   while file-side checks looked fine. Fix: after EVERY write, verify
   the index accessor count equals the actual element count. On the
   shipped v7 files: **59,694 == 59,694, both GLBs.**
2. **Skinning joint-index bug (caught in v7).** The first margin
   extraction blended JOINTS/WEIGHTS by interpolating joint *indices*
   — an index is a label, not a number you can average — and the part
   came out naming 139 nonsense joints (toes, tongue, …). Fine at
   bind pose, wrong under animation. Fix: accumulate weights per
   joint id and keep the top 4. The shipped part skins to **32
   joints, all head / eyelid / gaze / brow / cheek.**

## Standing method — for every future lash build, on any model

1. **Never root lashes on a prim seam.** A mesh-boundary loop near the
   eye is a construction seam until proven otherwise. The Face /
   EyeSocket seam sits on the eyeball, ~4 mm from the line lashes
   grow from.
2. **Extract the visible margin** with the front-ray method
   (ball-first vs skin-first classification) and **marker-verify it
   in screen space** — the markers must trace the visible eyeball
   edge exactly, both eyes — BEFORE building strands.
3. **Root on the visible margin** at the spec offset (0.55 mm) and
   report root distances against the visible margin (reporting them
   against a seam loop is how six bad builds passed their own
   numbers).
4. Grow with a **rotating fan** (+54° outer → 0° centre → −36°
   inner), **bezier curl** (forward emergence, bow 0.36/0.30 × rise,
   skin as clearance floor only), **6-strand clumps on one root**,
   a **falsie strip** on the margin, and the **wing as a continuation
   of the corner** with ≤ 1.2 mm surface containment.
5. **Opaque near-black** (RGB 0.012, alpha 1.0; 0.85 at the tip point
   only). No transparency feathering.
6. After every GLB write: **verify index accessor count == element
   count**, and verify the skin touches only plausible joints
   (accumulate weights per joint id, top 4 — never interpolate
   indices).

## Honest limits (as recorded by the v7 lane)

- The band is at the spec's 1.05 iris Ø rise; on this head that is a
  tall, dramatic glam band — tips approach the brow at centre.
- At extreme close-up the clumps read slightly spidery; at face
  distance they read dense. Thickening strand diameter or adding an
  offset half-row is a style dial — construction would not change.
- The far wing tip can sit up to the 1.2 mm containment off the
  temple surface.
- Lower lashes remain subtle by spec.
