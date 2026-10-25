# Doc Frank feet splayed sideways: fixed (2026-10-22, Claude session)

Owner: "the feet are sticking out to the side, both feet are sticking out to the side instead of forward ...
I feel like they're pointing like almost 90° angles out to the side".

**Cause (measured).** The bosconovitch bank's `foot_tip` in `game/assets/anim/t3/bosconovitch/skeleton.json` is the
centroid of the T3 rig's foot-part vertices. Dr. B's decoded foot part is scattered: 27 vertices spanning 45 cm on a
0.35 m leg, from the KMD seam-vertex gap noted in `lab/README.md`. So the centroid sits **0.52 leg-lengths** from the
ankle. In the other 16 banks it sits 0.05–0.21. The retarget swung his feet toward that point, which is ~50° outward
each. Doc Frank's own models were fine.

**Fix.** In `game/js/t3anims.js` `sourceInfo()`, a source foot centroid more than 0.3 leg-lengths from the ankle is
treated as not a foot. That foot keeps the fighter's own authored foot-to-shin relation (the same rule already used for
template feet whose toe points backwards). Only bosconovitch trips it.

| foot yaw vs facing (deg) | before L / R | after L / R |
|---|---|---|
| doc-frank stance | 53.0 / −49.6 | −7.0 / 27.2 |
| doc-frank-machine-shop stance | 53.0 / −49.6 | −7.0 / 27.2 |
| doc-frank-hood stance | 49.1 / −44.7 | −9.6 / 28.2 |
| control demonio-a1 (jin bank) | 4.8 / 16.3 | 4.8 / 16.3 (unchanged) |
| control pantera (king bank) | −8.7 / 20.2 | −8.7 / 20.2 (unchanged) |

`before_after_stance.png`: front and side views, old code vs new code (viewed). Still open and not touched here: the Hood
model's long coat swings as a rigid slab, a weighting issue in that model.
