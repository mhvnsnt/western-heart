# Hair Fit — Lane 13/14 Addendum: afro rim re-parametrization, the pit verdict, straight crown

Companion to REPORT.md and REPORT-ADDENDUM-lane12.md. Covers the v6 afro rim
re-parametrization (parent-approved escalation of lane 12's finding), the
straight crown restoration, and the full afro gate history through the v6c run.
Gate numbers are unchanged everywhere in this work: real-topology edge growth
max ≤ 2.0×, zero tris with max edge > 50 mm and growth > 3×, anchor-band verts
within 0.5 mm of the 1.5 mm standoff, zero anchor-band verts inside.

## Afro gate history (complete)

| run | method | growth max | max edge | bad tris | verdict |
|---|---|---|---|---|---|
| v2 | delta diffusion + exact anchor | 3.79 | 92.8 mm | 4 (553/554/1848/1849) | FAIL |
| v4 | v3 + reconcile diffusion | 3.80 | 92.9 mm | 4 (same) | FAIL |
| v5 | continuity-constrained placement | 3.83 | 93.6 mm | 4 (same) | FAIL |
| v6 | rim rebuild v3 (hairline track pins) + v5 refit | 3.70 | 93.6 mm | 4 (same) | FAIL |
| v6b | rim rebuild v4 ("pit re-sheeting") + v5 refit | 3.70 | 93.6 mm | 4 (same) | FAIL — see identity finding |
| v6c | rim rebuild v5 (true pit re-sheeting) + v5 refit | 3.24 | 91.3 mm | 1 (tri 534) | FAIL — pit theory confirmed |
| v6d | rim rebuild v6 (+ near-band re-sheet, PREV6 delta dropped for the set) + v5 refit | 3.11 | 75.1 mm | 1 (tri 553) | FAIL — one tri |
| v6e | rim rebuild v7 (fan re-spacing, R+L grow>2 fans of v6d) + v5 refit | 4.79 | 92.5 mm | 2 (1848/1849) | FAIL — failure moved to L |
| v6f | rim rebuild v8 (union fan re-spacing, Gfit from v6d) + v5 refit | 4.11 | 89.6 mm | 2 (1848/1849) | FAIL — afro lane closes |

## The v6 finding (lane 13)

Rebuilding the dome's rim band onto the true hairline track (the body's own
scalp-cap boundary: front h +0.098, temples +0.047/+0.055, nape +0.034) worked
as designed — the hairline segment's pins displaced p50 17 mm / max 46 mm —
and the gate still failed on the same 4 tris. Forensics on the v6 diag dump:
the bad tris' verts are SPIRAL-segment depth-0/1 groups at the temple pits,
authored INSIDE the head surface (sd −10..−15 mm) where two scalp sheets pass
within millimetres of each other (the medial-axis fold). Their fitted
positions move 15–71 mm onto different sheets.

## The v6b finding (lane 14): the pit re-sheeting never happened

Rebuild v4 pinned pit groups to `disp = (Gq + Goff) − G`, where
`Goff = group_mean(comp − q)`. That expression is an algebraic identity:
Gq + Goff ≡ G (measured residual 2.2e-13 mm), so the pit displacement was
exactly 0.000 mm for all 8 pit groups, and the 8 bad-tri verts moved only
0.0–1.5 mm in the rebuilt dome. V6b therefore re-ran the v3 field at the pit,
and its identical failure (3.70 / 93.6 mm) is what an unchanged input
predicts. **The pit-fold theory was not refuted by v6b — it was never
tested.** Final-state anatomy of the v6b dump: all 8 bad verts sit at
sd +1.5 mm (anchor-perfect) but their surface points scatter 28–91 mm apart —
placement across sheets, again.

## Rebuild v5: a true pit re-sheeting

Pit pin target = Gq + tangential(Goff) + Gn × 1.5 mm: the authored offset's
normal component (−10..−15 mm, inside the head) is replaced by the +1.5 mm
standoff along the group's own anchor-sheet normal; the along-sheet authored
offset is preserved. Pit displacement p50 13 mm (v4: 0.000 mm). The rebuilt
dome's self-ratio vs authored is unchanged from the v3/v4 audit (p50 1.00 /
p99 1.21 / max 2.42 at the two segment-junction tris 857/1471 — that
self-stretch lives in the rebuilt authored state, i.e. in the gate's
denominator, and is disclosed here); the 4 bad tris' own self-ratios are
0.75–1.15. Prediction recorded before the run: if the pit now enters the
refit as a single-sheet patch at standoff, the continuity assignment's
incoherent-group count drops below 7.

## V6c verdict — the pit theory confirmed

Growth max 3.24, bad tris 4 → 1, incoherent anchor groups 7 → 5 (the
recorded prediction held). The LEFT temple healed outright (tris
1848/1849: 3.22/3.70 → 0.91/1.56). The right temple improved (553:
3.30 → 2.88; 554: 3.67 → 2.02) but a neighbouring fan tri (534) became
the one bad tri: its vert 1194 (pit group 431) still flipped sheet —
PREV6 still carried FIT5's torn delta for the pit groups, so the
assignment (computed on the post-rounds state) saw a far-sheet entry
state. Copy-split was checked and ruled out (every weld group's final
spread is 0.0 mm).

## V6d verdict — one tri from passing

Rebuild v6 widened the re-sheet set to the near band (gsd < +5 mm,
depth ≤ 1; 16 groups total) and dropped FIT5's delta for the set in
PREV6 (prevfit := rebuilt). Incoherent groups fell to 2; tri 534 healed
(→ 1.41), tri 626 healed (→ 0.76). The last bad tri is 553 (growth
3.11, fitted edge 67.0 mm): its verts 1195/1192 now hold one sheet
together, but vert 1288 (group 1039) flipped — it sits spatially on the
fold's medial axis (bistable across runs: near-sheet in v6c, far in
v6d; its authored-state coherence test passes). A bistable vert has no
placement-side fix; the band must carry the length. Rebuild v7 therefore
re-spaces the fan stations toward their measured fitted loci (fan
groups w = 0.6, neighbours w = 0.3): rebuilt fan edges go from
21.6–28.0 mm to 34.2–51.2 mm (self-ratios vs the original authored
1.41–2.09 on those tris, disclosed — this is the re-parametrization the
method always contemplated: a new authored rim distribution, with the
gate still verifying seating, inside-ness, and growth against it).

## V6e / v6f verdicts — the fans are coupled; the afro lane closes

V6e re-spaced the fans that were over 2.0 in v6d: the entire R fan
healed (550 1.88 / 553 1.84 / 554 1.80, 1787 0.95) — and the failure
moved to the L classics (1848 3.49 / 1849 4.79), which had been healed
since v6c. V6f re-spaced the UNION fan (10 tris, fitted loci from
v6d): the whole union fan held (R 1.17–1.87; L fan 1.35–1.77) — and
1848/1849 flipped again (4.11 / 3.48), even though they were re-spaced
toward their own healed v6d loci. Conclusion, measured across nine
runs: the two temple fans are coupled through the shared diffused
field and the placement assignment; each fan's classic tris are
bistable, and displacing either side flips the other. Every run seats
every anchor perfectly (inside 0, standoff within 0.08 mm max) — the
fit is surface-true everywhere, and the growth term alone fails, on
one fan, on alternating sides. Best recorded state: v6d (growth max
3.11, one bad tri). **No afro candidate ships from this work** — the
gate is the gate. What would decide it next (parent/owner call, not
taken here): a waiver for the v6d-state dome, a different dome source,
or a fit method that optimises the fitted field against the growth
term directly instead of placing anchors exactly. The on-disk
REBUILT/PREV6 pair is restored to the v6 (v6d-input) state; FIT5
remains the afro candidate of record with its known dome tears.

## Straight crown — the honest numbers

Lane 13 proved the brief-literal crown restoration (cap 1.853 / strands
1.875 with the gate-passing rim kept) is jointly unsatisfiable: those
heights ARE the unseated state — the authored cap shell floats ~58 mm proud
of this head, and REFIT's rim seat and the authored heights are the same
field's two ends. What v6b (REFIT6B) does instead: strand verts re-hug the
seated cap at their authored standoff from it (exact per-vert cap
correspondence; cap + headband byte-identical to REFIT; only strand
POSITION accessors changed; strand gate = REFIT baseline or better).
Measured crown truth, not oversold: strand max-y 1.791 vs authored 1.8747;
verts above 1.80 = 0 (authored 26,422). The standoff restoration recovered
~8 mm of the ~91 mm height deficit. What it DID restore is coverage: in the
top proof, REFIT reads as a bald smooth dome (cap shell exposed, strands
pushed to the sides); REFIT6B's strand layer covers the crown with a visible
part line, the cap reading through only in a small patch near the front
hairline. Height: NOT restored (proven impossible with the rim seat).
Coverage: restored — final verdict on the full proof set is the parent's.

## Proofs

Straight REFIT6B, shot sequentially (one camera per session) on the
standing stage: straight-v6b-face.png, straight-v6b-face34.png,
straight-v6b-front.png, straight-v6b-top.png (top from lane 13, same
GLB). Lane 14's own-eyes read: the strand layer now covers the crown in
every frame — the bald-dome read of the REFIT proofs is gone — and the
rim seat is unchanged from the gate-passed REFIT. One honest defect
remains visible at face distance: a smooth black cap window at the
front hairline (clearest in the face frame), where the fringe-zone
strand coverage is thin and the seated cap shell reads through. That
is a coverage gap in the part's fringe zone, not a seating failure;
the headband was hidden by the stage in these frames (its 5.7–11.8 mm
float from FINAL is still unaddressed, as flagged in lane 12). No afro
proofs: no FIT6 exists (gate verdict above).
