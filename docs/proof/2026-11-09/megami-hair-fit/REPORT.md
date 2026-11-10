# Megami hair fit pass — Angel afro + Angel straight scalp seating (2026-11-09)

Owner verdicts answered (2026-11-09): both Angel hairstyles are SAVED as Megami options, but
both were ruled "not fitted to the head enough" (afro ~09:19 CST, straight ~09:19 CST, afro
again ~09:20 CST). Addendum (~09:21 CST): a visible circle around the whole head "like a
helmet strap" reads amateur — whether it comes from the cap edge, the dome arc, or the
seating gap, it must be gone. This pass is a FIT PASS ONLY: the two builds (afro = PR #1689
build12, straight = PR #1688 strand build) are otherwise byte-for-byte the same parts —
same meshes, materials, skins, textures and normals; only vertex positions moved.

## Method (pipeline math, zero hand edits)

- **Head surface**: extracted from the Pilot 2 body (`megami-angel-pilot2-v2fix.glb`) main
  mesh — morphs applied at their shipped weights (AngelFace=1, AngelBody=1), skinned at
  bind; the head surface is the body-mesh verts within 0.21 m of the Head joint, with a
  frame from the Head/Neck axis and the nose vert.
- **Composition**: each hair part is composed onto that body by the head-joint delta — the
  game's own composition rule (afro delta (0, −0.1423, +0.001), matching the hero lane's
  measured value). All measurements are taken in this composed space.
- **Refit — straight**: cap verts are projected onto the head surface at a **+1.5 mm
  standoff** — two projection passes with a welded Laplacian smooth of the displacement
  field between them. The field is extended to the strand mass and the headband with an
  inverse-distance blend faded out between 10 mm and 140 mm from the cap (the straight's
  cap field is near-rigid — the whole cap sat off in one coherent direction — so the
  strands follow it without shear; verified in the final proofs). A clamp pass lifts any
  vert left inside the skin or closer than 0.5 mm out to +0.5 mm (corrections capped at
  3 mm; deeper verts are interior, invisible from outside, counted in the open below).
- **Refit — afro**: the DOME is projected the same way, band-weighted around the dome:
  only the dome's lower band seats onto the scalp; the dome crown keeps its shape — it
  is the afro's inner volume shell, covered by the curl mass. The curl MASS is seated by
  its own gap field (finisher repair, see Deviations): each mass vert moves along its
  exact nearest-point vector toward a +2 mm standoff, pull capped at 18 mm, weight
  fading out between 30 mm and 55 mm of gap, weld-group averaged for seam continuity,
  then the same clamp pass. The outer volume (76% of verts) does not move at all.
- **Finalize**: the shipped files carry the fitted POSITIONS with the parts' original
  authored NORMALS restored byte-for-byte (the refit's recomputed smooth normals changed
  the authored shading of the strand/curl cards; positions are identical either way).
- **Audit** (accessor level, original part vs fitted part): straight — 4 POSITION
  accessors changed, all 20 other accessors byte-identical, JSON diffs limited to
  POSITION min/max; afro — 2 POSITION accessors changed, all 13 other accessors
  byte-identical, JSON diffs limited to POSITION min/max. Nodes, skins, materials,
  animations identical. The input GLBs were verified byte-identical to the parts on main
  before fitting (git blob 2bf343a3… afro, 0c3d67aa… straight).

## Measurements

Unsigned gap (mm) from the hair to the head surface, in composition space (measure2
instrument; zones by azimuth around the head — FRONT |az|≤45°, TEMPLE 45–115°, NAPE
>115°, CROWN = verts ≥75 mm above the head joint). "Before" = the shipped parts;
"after" = the fitted FINAL files (re-measured on the FINAL files by the finisher lane;
numbers reproduce the predecessor lane's after-runs exactly, as positions are identical).

### Straight (PR #1688 build) — seating surface = the scalp cap itself

Cap, ALL verts (n=2,413):

| zone | before p50 | before max | after p50 | after max |
|---|---|---|---|---|
| ALL | 58.4 | 103.1 | 1.5 | 1.8 |
| FRONT | 75.6 | 96.4 | 1.5 | 1.5 |
| TEMPLE | 48.8 | 97.3 | 1.5 | 1.8 |
| NAPE | 59.3 | 103.1 | 1.5 | 1.5 |
| CROWN | 66.3 | 103.1 | 1.5 | 1.8 |

Cap rim: max gap 70.2 mm before → **1.5 mm** after. Cap verts inside the skin: 2.2% → 0.0%.
Cap displacement applied: mean 55.9 mm, max 105.9 mm; clamp adjusted 1,317 verts
(11,346 deep-interior verts left, inside the hair volume).
Strand root-zone (roots within 4 mm of the cap, n=14,835): after p50 3.0 mm, max 5.7 mm —
roots ride on the 1.5 mm cap plus the strand base, as authored.
Headband prim: gap p50 76.4 mm → 6.1 mm (max 95.7 → 11.7). The band was not a projection
target; it followed the faded field and now rides on the strand mass ~6 mm off the skin —
the hair thickness beneath it (see the band-on face proof).

### Afro (PR #1689 build12) — seating surface = the dome rim + lower band

The afro's cap is a 4,680-vert dome shell. Its crown is the style's inner volume
(~9–11 cm off the scalp by design, under the curls) and is not a seating surface; the
dome RIM (lowest 3% of cap verts per azimuth sector, n=165) is what seats:

| zone | before p50 | before max | after p50 | after max |
|---|---|---|---|---|
| ALL | 42.8 | 98.8 | 0.8 | 1.7 |
| FRONT | 92.3 | 93.0 | 1.7 | 1.7 |
| TEMPLE | 12.5 | 98.8 | 0.5 | 1.5 |
| NAPE | 48.3 | 72.5 | 0.9 | 1.5 |
| CROWN sectors | 93.0 | 98.8 | 1.7 | 1.7 |

Rim verts >2 mm off the scalp: 98.8% before → **0.0%** after; rim verts inside the skin:
14.2% → 0.0%. Lower side band of the dome (TEMPLE cap zone): p50 102.0 mm → 1.5 mm
(dome fit carried unchanged into the shipped file; rim re-measured on the shipped file:
ALL p50 0.8, max 1.7 mm).

Curl mass, **tracked same-vertex bands** (identical sampled verts measured before and
after — the like-for-like instrument for the mass; snapshot medians over different vert
subsets are never compared):

| before-gap band | zone | n | after p50 | after p90 |
|---|---|---|---|---|
| 2–5 mm | TEMPLE | 155 | **1.6 mm** | 2.0 mm |
| 5–15 mm | TEMPLE | 1,141 | **1.0 mm** | 2.0 mm |
| 5–15 mm | NAPE | 88 | **1.3 mm** | 2.0 mm |
| 15–25 mm | TEMPLE | 1,512 | **3.1 mm** | 6.4 mm |
| 15–25 mm | NAPE | 741 | **4.9 mm** | 6.7 mm |
| 25–45 mm | FRONT | 273 | 25.4 mm | 28.9 mm |
| 25–45 mm | TEMPLE | 6,904 | 18.0 mm | 25.3 mm |
| 25–45 mm | NAPE | 4,991 | 18.8 mm | 25.3 mm |

Before the fit the mass inner shell sat at p50 17.6 mm off the scalp (TEMPLE 15.6,
NAPE 22.3) and the fringe further out. After: the contact bands read **1.0–1.6 mm p50**,
the 15–25 mm band lands at 3–5 mm (pull capped at 18 mm by design), and the 25–45 mm
fringe band is drawn in by 10–17 mm while the ball keeps its volume — mass bounding box
unchanged (x −0.204..0.207 → −0.204..0.204, height identical), mass displacement p50
0.0 mm (the outer three quarters of the afro never move). Clamp: 3,718 verts adjusted;
10,392 deeper interior verts left — curl segments enclosed inside the closed hair
volume (the source build's curls occupy the head region under the dome), not on any
visible surface; the face proofs show no skin penetration.

## Verdicts

- **Straight — FITS.** Cap and rim seat at 1.5 mm (worst point 1.8 mm, TEMPLE/CROWN) in
  every zone, inside the 1–2 mm gate. No ring: the before state read as a floating halo
  around a bare forehead (proof: straight-before-face); after, the mass hugs the skull on
  all sides. **Ring verdict: none present, seating closed.**
- **Afro — FITS (shipped file = the finisher's FIT5 build, see Deviations).** The dome
  rim seats at 0.2–1.7 mm in every azimuth sector (worst point 1.7 mm, FRONT and crown
  sectors), inside the 1–2 mm gate, with zero rim penetration; the curl inner shell
  seats at 1.0–1.6 mm p50 in the contact bands with the silhouette unchanged.
  **Ring verdict: GONE.** The "helmet strap" was this rim: floating 43–99 mm off the
  scalp, its arc read as a hard circle around the head above the curl line (in the
  before face proof the tan dome arc is directly visible above the forehead, and the
  grey dome shows behind the ears). The rim now sits on the scalp, buried under the
  curl mass — evidence: afro-fit5-face and afro-fit5-face34 against afro-before-face.
- **Residual (straight, pre-existing, not a fit defect):** at the centre-front part, the
  dark cap sheet shows through the sparse authored part line at close range
  (straight-final-hairline-zoom). The cap is seated (1.5 mm) — what shows is the build's
  authored strand coverage at the part, which a fit pass does not change. Flagged for the
  parent/owner eye, not silently buried.
- The straight "after" proof set was shot from the raw refit output (recomputed
  normals); positions in the after, fit2 and FINAL files are byte-identical (verified
  by accessor byte-compare) — **the straight ships the FINAL file** (fitted positions +
  authored normals), and the final proof set was shot from it.
- **Deviation — the predecessor's afro FINAL does not ship.** Its dome projection was
  correct and is carried into the shipped file unchanged, but its mass treatment (the
  cap's displacement field extended through the whole curl volume) destroyed the
  silhouette: finisher-measured mass displacement p50 61.2 mm / max 128.0 mm, bounding
  box shrunk ~3 cm per side, and the finisher's verification render
  (afro-final-front.png, kept in the proof set as the failure record) shows a torn
  fan/crown with the face veiled. The finisher rebuilt the mass seating from the
  ORIGINAL afro with an own-gap field; three iterations were rejected by the
  tracked-band instrument (graph-diffusion dilution; a scalar clip that truncated
  inward pulls to 0.5 mm; a radial-direction field whose displacement ran tangential
  to the surface at the jaw/temple corner — per-vertex evidence: 9.6 mm applied,
  2.5 mm along the surface normal) before the exact nearest-point projection passed
  every band. The shipped afro = predecessor dome fit + repaired mass, POSITION-only
  (audit: 2 POSITION accessors changed, 13 others byte-identical).

## Files

- `customization/parts/megami-hair/megami-hair-angel-afro/megami-hair-angel-afro.glb` —
  fitted (81,320,784 B, same size as before; registry size unchanged).
- `customization/parts/megami-hair/megami-hair-angel-straight/megami-hair-angel-straight.glb` —
  fitted (11,606,864 B).
- Registry reconciliation: part counts unchanged (registry 1,192 / suite 7,744 /
  create-fighter index 8,002). The straight part's recorded size was stale at 11,607,996
  (the shipped file was 11,606,856); corrected to the fitted file's true size 11,606,864
  in PARTS-REGISTRY.json, create-fighter PARTS-INDEX.json and creation-suite-ui
  parts-catalog.json. Afro size unchanged.
- Proofs + measurement JSONs under `docs/proof/2026-11-09/megami-hair-fit/`.
