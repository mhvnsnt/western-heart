# HAIR-FIT STANDARD — fitting hair systems to a character's own head

Standing method for every hair fit in this project (owner law 2026-11-09).
A hair system is **shaped by the head it sits on**: its edge is buried at the
character's natural hairline, its mass follows her skull, and nothing about it
may read as a separate object resting on the head. The failure this standard
exists to prevent is the owner's named one — hair *"floating around her head
like a helmet"*: any visible gap, cap edge, or ring at any proof distance is a
FAIL, and face-close frames are the evidence.

The fit is research-based, from two bodies of practice:

1. **How hair grows** — real hairline anatomy (front hairline shape, temple
   points, sideburn area, nape) and growth **direction** per scalp region.
2. **How wigs and weaves attach** — a cap built on the wearer's own head
   measurements, seated **on** the scalp line, its lace edge melted **into**
   the hairline; a weave anchored to tracks braided **on** the head.

## Per-character, never a template

- The fit surface is the character's **own closed head surface**, extracted
  from her own body mesh at its shipped state (morphs at shipped weights,
  bind pose). Never a shared head, never a generic offset.
- Her hairline boundary is **her own authored scalp** (the body's bundled
  scalp cap where one ships). Rim verdicts are reported per zone — FRONT /
  TEMPLES (incl. temporal peak) / SIDEBURN / NAPE — against that boundary.
- Female hairline anatomy is a **zone, not a line**: leading edge (irregular,
  lowest density), transition zone ~10–20 mm deep, temple points, lateral
  mounds (98% of women), widow's peak (81%), closed frontotemporal angle.
  A hard straight rim edge reads fake even at the right distance.

## The fit procedure (refit_v2 scheme)

1. **Closed surface first.** Build the head surface as a *closed* solid and
   validate it (ray-parity sign; probe points inside/outside must measure
   exactly). An open shell — e.g. a spherical cut around the head joint —
   makes every nearest-point projection near the cut snap to the boundary or
   the far side of the skull; no smoothing downstream can repair that field.
   *(This was the root cause of the 2026-11-09 afro "ribbons": the dome's
   temple-height equator ring tore because adjacent verts projected to
   divergent points across the cut.)*
2. **Real topology only.** All smoothing/diffusion runs on the mesh's real
   indexed, **welded** topology. Building a graph from sequential buffer
   triples is wrong for indexed meshes and was the second root cause of the
   ribbons — the fake graph could not reconcile divergent displacements.
3. **Delta field.** Take D = (previous best fit) − (original authored). It
   encodes where proven seating moved the edge and how the field fades into
   the mass. Diffuse D over the real welded topology until neighbour
   disagreement is small — a coherent field cannot tear the shell.
4. **Anchor the rim.** Verts whose *authored* distance to the scalp is within
   the anchor band are placed **exactly** on the offset surface along the
   surface normal. Standoff = cap thickness only: **1.5 mm**. This is the
   lace-front "melt" and the weave's perimeter track: the edge sits on the
   scalp line, buried, not hovering near it.
5. **Blend, don't project, above the band.** Above the anchor band, keep the
   authored shape plus the smoothed delta, faded by height, so the crown
   silhouette stays the author's. Projecting the whole cap flattens the
   style's inner volume (an afro dome's crown sits ~9–11 cm off the scalp
   *by design*, under the curls — it is not a seating surface).
6. **Push-out.** No vert may sit inside the scalp. Shallow violations are
   pushed radially to +0.5 mm; deep interior verts (inside the closed hair
   volume, invisible from outside) are left and **counted**, never hidden.
7. **Finalize.** Ship fitted POSITIONS with the part's **authored NORMALS**
   restored byte-for-byte — recomputed smooth normals change the authored
   shading of strand/curl cards. Everything else in the file (skins,
   materials, textures, other accessors) stays byte-identical to the
   shipped part; the audit is at accessor level.
8. **Continuous placement (refit_v5 scheme, 2026-11-09 lane 12).** Exact
   placement must respect topology: the nearest-surface point of a vert is
   NOT independent of its neighbours'. Where the cap interpenetrates a
   second scalp sheet (the body's own bundled scalp cap, drawn tighter than
   the skull the cap was authored on), the nearest-point map is
   discontinuous across the medial-axis fold between the sheets, and
   independent placement teleports neighbours to different sheets — the
   proven q-jump tear (verts 1292–1195: 15.63 mm authored, 92.85 mm fitted,
   both at perfect 1.4/1.5 mm signed distance). The fix: assign each weld
   group a surface triangle by coherent propagation (multi-source BFS from
   locally coherent seed groups over the welded graph + a surface walk that
   only descends), and place verts at the closest point **on their assigned
   triangle**. Detection and the gate stay on the global query. Proven on
   the straight cap (gate max growth 3.24 → 1.66, bad tris 16 → 0).
9. **Rim travel is a parametrization question, not a placement question.**
   If the authored rim sits far from the hairline it must end on (the afro
   dome's temple rim was authored under the ear, h ≈ −0.13, while her own
   scalp cap puts the temple hairline at h ≈ +0.05 — a ~90 mm climb), no
   placement method can fund that travel inside a ≤2.0× growth gate: the
   rim's vertex distribution must be re-spaced along the true hairline path
   first (the weave-track rebuild: rim verts placed by construction on the
   offset scalp-cap boundary at even arc spacing), then steps 3–8 blend the
   interior to it. Diagnose before fitting: compare authored rim heights
   per azimuth sector against the scalp-cap boundary; if rim travel exceeds
   what local edge slack can fund (~2× the local edge length), escalate to
   re-parametrization instead of iterating placement.

## Hard gate (refuses to write on failure)

Measured on the real welded topology, candidate vs original:

- edge growth max ≤ **2.0×**
- **zero** triangles with max edge > 50 mm and growth > 3×
- anchor-band verts: p95 |distance − standoff| ≤ **0.5 mm**
- **zero** anchor-band verts inside the scalp

A gate failure is a verdict, not an inconvenience: iterate the field or the
parameters and say what changed and why. Never weaken the gate silently.

## Measurement (the standard's evidence)

- **Rim gaps per zone** (front / temples / sideburn / nape): the rim band
  must sit ≈ **1–2 mm** off the scalp around the full perimeter.
- **Stretch test** on real topology (same numbers as the gate).
- **Hairline overlay**: the fitted cap rim vs the character's own scalp-cap
  boundary, per 15° azimuth sector — the rim must track her boundary.
- **Growth direction**: near-scalp strand/curl orientation vs the scalp
  growth field — the tangential direction away from the crown whorl centre
  (front: forward + down; sides: down; nape: down). Emergence within
  **~25°** of the field in the root zone. Follicles emerge *angled*, never
  perpendicular: 5–10° temporal hairline, 10–15° frontotemporal, 15–20°
  frontal hairline, 30–45° mid-scalp.
- **Proofs**, one at a time: face / face-¾ / front / three-quarter / top,
  on the standard dark stage. The face-close frames are the ring evidence;
  a ring verdict is given per hairstyle, in words, in the landing report.

## Research basis (summarised in our own words; nothing copied)

- Hairline design fundamentals — the hairline as a five-component zone
  (leading edge, transition zone, temple points, midpoint, sideburn
  transition). KORT SMP, "Hairline Design Fundamentals",
  https://www.kortsmp.com/courses/foundation/hairline-fundamentals
- Female hairline patterns in 360 women (widow's peak 81%, lateral mounds
  98%, temporal recessions 87%) — Nusbaum & Fuentefria, "Naturally occurring
  female hairline patterns", https://pubmed.ncbi.nlm.nih.gov/19397668/
- Female hairline correction, 5A5P principle (frontal, frontotemporal
  recess, temporal peak, infratemple, sideburns) — Plast Reconstr Surg Glob
  Open 2016, https://pubmed.ncbi.nlm.nih.gov/26894014/
- Female hairline in depth — rounded/bell macro shape, closed
  frontotemporal angle, multi-directional micro hairline. Lam Institute,
  https://www.hairtx.com/the-female-hairline-in-depth/
- Emergence angles by zone (above) — Charles Medical Group figures via
  AsiaPatient hair-direction guide,
  https://asiapatient.com/hair-transplant-guide/hair-direction/
- Hair whorl — follicles radiate from a (usually single, slightly
  off-centre) parietal whorl; orientation set developmentally.
  https://biologyinsights.com/what-is-a-hair-whorl-the-science-behind-your-hair-pattern/
- Lace-front construction — cap sized from the wearer's own measurements
  (circumference, front-to-nape, ear-to-ear, temple-to-temple); lace seated
  at the natural hairline and melted so no edge reads; front ~½ inch tied
  15–30% lighter for a graduated edge. WigPlace,
  https://www.wigplace.com/wig-types/lace-front/lace-front-wigs-for-beginners-what-to-know-before-you-buy
- Sew-in anchoring — wefts stitched onto cornrow tracks braided on the head,
  sewn nape-up; perimeter + nape anchor braids carry the perimeter; every
  track's support is the head's own surface.
  http://sewingtrip.com/how-to-do-a-sew-in-for-beginners/ and
  https://www.privatelabelextensions.com/blogs/bundles/sew-in-weave-techniques

Each finding maps to a fit parameter above: hairline-as-zone → per-zone rim
bands and verdicts; her own boundary → the authored scalp cap; emergence
angles → the 25° growth-field tolerance; whorl radiation → the growth
field's definition; cap-on-own-measurements + lace melt → the 1.5 mm
standoff and exact anchor placement on her closed surface; track anchoring
→ the push-out rule and perimeter-first seating.
