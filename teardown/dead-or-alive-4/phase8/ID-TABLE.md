# DOA4 Phase 8 — Job 1: package → character ID table

Method: front bind-pose render of each phase-6 skinned GLB (Blender 4.0.2, Cycles, grey studio world, percentile-framed; renders `phase8/renders/` in this PR, unique filename per package), viewed by this agent; cross-checked against per-GLB geometry stats (verts / skin joints / bbox / height-band profile — `phase8/tools/glb_stats.py`, output `phase8/CHRONE-STATS.txt` for the chrone batch), the phase-6 package inventories, and costume-group structure (consecutive packages with near-identical stats = same fighter, different costumes).
Rules: a name is claimed only with evidence; `unidentified` is a valid final state for a row. Confidence: certain | strong | tentative (tentative rows list competing candidates).
IMPORTANT STRUCTURAL FACT (from the renders + stats): the phase-6 GLBs contain NO head geometry — every chrone front render ends at a collar/neck cluster, arms are sleeved cylinders in T-pose, and lower bodies are costume-dependent. Identification therefore rests on costume silhouette + proportions + texture color schemes, never on faces.

## chrone (30 packages) — renders viewed, ID pass in progress
| package | verts | joints | silhouette evidence (from viewed render) | identification | confidence |
|---|---|---|---|---|---|
| chrone-pkg00 | 45237 | 58 | vest/coat torso, bow at neck, waist pouch, wide sleeve cylinders, single tapered leg column | unidentified | — |
| chrone-pkg01 | 37076 | 60 | (render viewed — see renders/) | unidentified | — |
| chrone-pkg02 | 37545 | 64 | wide-sleeved long dress (X width 0.94, widest of chrone) | unidentified | — |
| chrone-pkg03 | 52101 | 62 | pending | unidentified | — |
| chrone-pkg04 | 50956 | 62 | pending (stats ≈ pkg03: same-fighter group candidate) | unidentified | — |
| chrone-pkg05 | 39035 | 60 | pending | unidentified | — |
| chrone-pkg06 | 78589 | 63 | pending (tall group 06–09, Ymax 0.59) | unidentified | — |
| chrone-pkg07 | 84744 | 61 | pending (tall group) | unidentified | — |
| chrone-pkg08 | 81841 | 61 | pending (tall group) | unidentified | — |
| chrone-pkg09 | 83561 | 61 | pending (tall group) | unidentified | — |
| chrone-pkg10 | 33366 | 66 | pending (wide band-5 flare 0.92) | unidentified | — |
| chrone-pkg11 | 61369 | 84 | pending (84 joints — extra hair/cloth bones) | unidentified | — |
| chrone-pkg12 | 63506 | 86 | pending (86 joints) | unidentified | — |
| chrone-pkg13 | 25819 | 64 | pending (long lower body, Ymin −0.64) | unidentified | — |
| chrone-pkg14 | 28313 | 66 | pending (stats ≈ pkg15/16: same-fighter group) | unidentified | — |
| chrone-pkg15 | 28313 | 66 | pending (same-fighter group) | unidentified | — |
| chrone-pkg16 | 28320 | 66 | pending (same-fighter group) | unidentified | — |
| chrone-pkg17 | 32129 | 64 | pending | unidentified | — |
| chrone-pkg18 | 50937 | 58 | pending (deep Z extent −0.58: train/cape behind) | unidentified | — |
| chrone-pkg19 | 38931 | 86 | pending (86 joints) | unidentified | — |
| chrone-pkg20 | 30539 | 63 | pending | unidentified | — |
| chrone-pkg21 | 24883 | 62 | pending | unidentified | — |
| chrone-pkg22 | 56125 | 61 | pending | unidentified | — |
| chrone-pkg23 | 81576 | 70 | pending (stray outlier verts to Y −2.00 — framing uses percentile bbox) | unidentified | — |
| chrone-pkg24 | 82414 | 67 | pending (outlier verts) | unidentified | — |
| chrone-pkg25 | 63306 | 74 | pending (outlier verts to Z −500) | unidentified | — |
| chrone-pkg26 | 68793 | 67 | pending (outlier verts to Z −500) | unidentified | — |
| chrone-pkg27 | 78937 | 66 | pending | unidentified | — |
| chrone-pkg28 | 83667 | 66 | pending | unidentified | — |
| chrone-pkg29 | 2913 | 65 | tiny package (2,913 verts, 7 meshes per phase-6 inventory) — NOT a full character costume; accessory/prop-class package | unidentified (non-character package) | strong |

## chrtwo (68 packages) / chrthree (50 packages)
Not yet rendered in this session — see PHASE8-STATE.md log. Rows land per-AFS as batches complete (same method, same table format).
