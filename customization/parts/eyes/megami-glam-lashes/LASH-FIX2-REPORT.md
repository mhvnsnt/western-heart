# LASH FIX 2 (v7) — glam lashes rebuilt: fan, curl, true clumps, roots on the VISIBLE lash line

Date: 2026-11-09/10. Lane: LASH-FIX v7 successor (parent gate failed v6).
Style of record unchanged: owner-approved glam set (PP PR #149 /
GLAM-LASHES.md) — long, winged. Spec parameters unchanged: 27 lid + 8
wing stations per eye, band rise 1.05 iris Ø, wing 0.60 eye-widths
rising 0.55 iris Ø, base offset 0.55 mm. Holds respected: **no PR, no
merge, PR #1701 untouched**, no glam/hair combining. The v6 writer
index-count fix is kept and re-verified after every write (below).

## The headline finding: v1–v6 roots were on the WRONG CURVE

The parent asked whether the extracted "lid margin" is actually the
visible lash line. It is not. Three instruments, one verdict:

1. **Numeric** (`scripts/lash_diag_margin.py`, `lash_diag_loops.py`):
   the extracted loop hugs the eyeball (distance-to-ball mean ≈ 0 mm)
   because it is the **Face-2 / EyeSocket-2 prim seam**, which sits ON
   the ball deep in the socket. Both prims share the identical loop;
   the combined skin surface has no boundary at the eye at all. Its
   aperture (posx 16.0 mm) is nearly twice the visible opening.
2. **Screen-space** (`scripts/lash_diag_overlay.py` →
   `proof/diag_nolash_eye_posx.png`, `diag_lash_eye_posx.png`): markers
   placed on the extracted top arc are **completely invisible** in the
   eye close-up — the loop is occluded by the lid fold from any camera.
   Strands rooted there travel inside the lid skin and emerge at the
   fold, which is exactly the v6 read ("roots stop at the crease, bare
   pink band below"). The 0.549 mm measurement was accurate — against
   a curve the eye never sees.
3. **The visible line, extracted and marker-verified**
   (`scripts/lash_margin_visible.py`): in the eye-local frame, a dense
   front-ray grid classifies each ray ball-first vs skin-first; per
   lateral column, the skin hit just outside the ball-visible run is
   the visible margin. Visible aperture: **posx 7.66 mm / negx 3.40 mm**
   (vs seam 16.01 / 11.19). Markers on this curve
   (`proof/diag2_eye_posx.png`, `diag2_eye_negx.png`) trace the visible
   edge of the eyeball opening **exactly**, both eyes. The visible
   margin sits **mean 3.96 mm / max 4.98 mm** away from the old seam
   loop — that is how far off the lash line every previous build was
   rooted, underneath the fold.

v7 roots sit on the visible margin. Root reporting, both numbers, as
ordered: **root-to-visible-margin 0.550 mm mean / 0.550 mm max** (the
spec base offset along the margin normal, by construction, n = 70
clump roots, re-measured on the shipped geometry);
**root-to-old-seam-loop mean 4.72 mm / max 16.41 mm** (max is a far
wing root stepping away along the temple, by design; lid roots sit
≈ 4 mm from the seam). Root seat is also verified visually: in both
close-ups the dark root line traces the eyeball's edge with no bare
lid band — compare the v6 frames, same cameras.

## What changed in construction (v6 → v7)

- **Direction field (the fan).** v6 grew every strand along world-up.
  v7 rotates the growth direction by station: +54° toward the wing at
  the outer corner, +30° at quarter, ~0° at centre, −16°, −36° toward
  the inner corner (smooth interpolation), with a sqrt-cos length
  compensation (outer strands ≈ 1.3× centre, not the 1.87× a constant
  up-rise would force) and tips drifting further in the lean direction.
  In the front frame the band now radiates; in q34 the corner strands
  sweep.
- **Curl.** Paths are cubic beziers: emerge mostly forward off the lid
  (0.80 fwd / 0.55 growth-dir mix), forward bow 0.36 × rise at mid-path,
  0.30 × at the tip. The skin surface is used only as a minimum
  forward-clearance floor (precomputed surface grid + 0.9 mm) — it no
  longer shapes the path, so the band no longer copies the lid wall.
- **Clumps.** One clump per station = **6 strands sharing one root**
  (root jitter ±0.06 mm), per-strand direction jitter ±5°/±4° and
  length jitter 0.84–1.00, strand root Ø 0.116 mm tapering to a point.
  Roots bundle tight and dark; tips splay; the gaps fall between
  stations (pitch ≈ 0.71 mm). A thin **falsie strip** ribbon seated on
  the visible margin (0.75 mm up-slope) makes the root line read as one
  dense dark line — the physical band a real falsie has.
- **Wing as continuation.** No separate anchor curve. Wing roots step
  along the temple from the corner itself: spacing grows as f^1.25
  (first root 0.97 mm past the last lid root), rise as f^1.6, fan angle
  continuing 54° → 80°, strand length tapering to 0.45×, and every wing
  path point surface-contained (≤ 1.2 mm off the skin in the shipped
  build). Three iteration rounds were needed here and are recorded in
  PROGRESS.md: v7a (92° cap) threw three bars past the silhouette;
  v7b (80° + 2.2 mm containment) killed the bars, left two edge ticks;
  v7c (1.2 mm) is the ship.
- **Colour/alpha.** RGB 0.012, alpha 1.0 on every ring, 0.85 at the
  single tip point. v6's 0.80 top ring was the grey wash; feathering is
  now taper + splay + length spread only.
- **Lowers.** 3-strand mini-clumps on the visible bottom margin
  (extracted with the same ray method), spec length 0.11 × aperture.
- **Skinning correctness (bug caught in this lane).** The first v7
  margin extraction blended JOINTS/WEIGHTS by interpolating joint
  *indices* — the written part named 139 nonsense joints (toes, tongue,
  labia). Harmless at bind pose, wrong under animation. Fixed by
  accumulating weights per joint id and taking the top 4: the shipped
  part skins to 32 head / eyelid / gaze / brow / cheek joints only.

Kept from v6, as ordered: the writer index-count fix — verified after
every write on the shipped files (index accessor count 59,694 ==
59,694 elements, both GLBs); the near-shut negx eye is the corr3_a
AngelFace morph itself (proven last lane; not touched — lash treatment
is identical on both eyes, and the negx fan reads correctly over the
morph's lid).

## Shipped build (v7c)

- Builder `scripts/lash_build7.py` → `work/lashes_megami_geom7.npz`
  (11,466 verts / 19,898 tris); writer `scripts/lash_write_glb7.py`.
- `work/lashes_glam_megami.glb` — standalone part, 981,556 B,
  sha256 f85ccd59…
- `work/megami-angel-gnmface-v2-lashfix.glb` — merged on corr3_a/v5,
  59,748,225 B, sha256 ab88c5b3…
- v6 GLBs preserved alongside as `*_v6.glb`.

## Proof set (gate stage, matched cameras, single build v7c)

- `megami-lash-fix2-front.png` — both eyes read as winged glam fans;
  wings sweep inside the silhouette, seated at the corners.
- `megami-lash-fix2-q34.png` — near-eye curl silhouette off the lid
  edge; wing connected, sweeping back along the temple.
- `megami-lash-fix2-eye-posx.png` — root line on the visible lash
  line; clump bundles dark at the root, splayed feathered tips; fan
  rotates inner→outer; wing lies on the temple to the corner.
- `megami-lash-fix2-eye-negx.png` — same treatment over the
  morph-narrowed eye (see the standing F-3 note in the v6 report);
  judge the eyelid with the face line, the lashes here.

## Honest limits

- The band is at the spec's 1.05 iris Ø rise; on this head that is a
  tall, dramatic glam band — tips approach the brow at centre, per the
  GLAM-LASHES envelope (the remaining 2.83 iris Ø envelope belongs to
  liner/shadow, which the holds keep out of this lane).
- At extreme close-up the clumps read slightly spidery — long, fine,
  well-separated strands (dramatic glam), denser at face distance.
  Thickening strand Ø or adding an offset half-row is a style dial if
  the parent wants the band heavier; construction would not change.
- The far wing tip can sit up to the 1.2 mm containment off the temple
  surface; at the negx silhouette edge one sub-pixel fibre shows at
  brow-tail height in the close-up. It is attached to the wing sweep,
  not a detached element.
- Lower lashes remain subtle by spec.
