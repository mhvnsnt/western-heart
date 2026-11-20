# Doc Frank sideways feet — root-cause diagnosis and fix

Owner report (2026-10-21 ~22:53 CDT, on the PR #483 proof render
`docs/proof-docfrank-ladder-20261021/docfrank-a1-bosco-stance-front.png`):

> "That's really close, but the feet are sticking out to the side, both feet
> are sticking out to the side instead of forward, so you gotta fix that,
> I don't know if that means the feet are twisted or backwards, everything
> else is pretty close and if you can get that on all his models it'll
> probably be pretty close."

## The plain answer to "which layer was wrong, and why did the hand-tweaking keep happening"

The wrong layer was the **animation bank's reference skeleton data** —
one vector, `foot_tip`, inside `game/assets/anim/t3/bosconovitch/skeleton.json`,
produced by the generator `tools/anim/t3_bank_skeleton.py`. Not the clip
decode. Not the retarget math. Not any model's bind pose.

`foot_tip` is the direction the runtime retarget (`game/js/t3anims.js`,
`retargetT3Clips` → `sourceInfo`) swings **every** fighter's feet to, on
**every** frame, for **every** model animated from that bank. The generator
derived it as the centroid of the vertices skinned to the foot joint of the
T3 import model. Bosconovitch's T3 foot part is a wide, flat blob of
27 vertices whose centroid sits ~0.20 m outboard of the ankle pivot —
so the stored "toe" pointed **+92° (left) / −109° (right)** off the rig's
forward: sideways. Every Doc Frank model, whatever its own bind, got its
feet re-aimed at that sideways reference by the shared animation path.
That is why per-model hand-tweaks never held: the models were never the
defect, and the retarget re-imposed the defect downstream of every fix.
One shared input was wrong; the fix had to land in the generator and the
generated data, once, for all models at once.

## Measured evidence (game's own code path, same clip, same frame)

Harness: `measure.mjs` in this folder — drives the repo's real
`game/js/t3anims.js` (`loadT3Clips` → `retargetT3Clips` →
`createT3Actions` → THREE mixer), stance clip at 40%, toe direction =
Foot→ToeBase world direction, yaw vs the model's forward (+Z in file
space; both test models rest with toes at 0°).

| Test | Left toe | Right toe |
|---|---|---|
| Doc Frank A1 at rest (own bind) | 0° | 0° |
| Leo man at rest (own bind) | 0° | 0° |
| Doc Frank Attire 3 base at rest | 0° | 0° |
| A1 + bosco bank, BEFORE (original data) | **+62.0°** | **−55.8°** |
| Leo man + bosco bank, BEFORE | **+62.0°** | **−55.8°** |
| Source FK of the bank's own clip + its `foot_tip`, frame 0 | +64.0° | −50.5° |
| The clip's foot-BONE orientation (no `foot_tip` involved), guard clip | −6° | +36° |
| Same, neutral clip mid-frames | −10° | −4° |
| A1 + jin bank (healthy reference), posed vs source FK | +5.5° = +5.5° | +11.3° = +11.3° |

Read-out:

- Two different models show the **identical** splay to 0.1° → not the models.
- The splay already exists in the bank's reference data (source FK row) →
  the retarget transmits the bank faithfully; it is not the retarget.
- The decoded foot-bone motion itself stays near the body (−6/+36 guard,
  −10/−4 neutral) → the clip decode is sane. The +36° right value is
  Bosconovitch's genuine guard turnout, present in the bone data.
- With a healthy bank (jin), posed == source exactly → the whole path is
  faithful end-to-end when the reference is right.

Cross-bank scan of the stored `foot_tip` yaw (same defect class):
anna −54/−140, armorking +45/−33, **bosconovitch −79/+79** (stored frame),
bryan −33/−105, eddy −48/−59, gunjack +18/−32, heihachi +25/+3,
hwoarang +11/−34, jin −2/−15, julia +92/−50, lei +46/+4, nina −10/+19,
paul +27/−2, xiaoyu −24/+13, yoshimitsu +41/+23. The generator's centroid
method is only as good as each character's foot-part shape; wide parts
break it. Banks with real ToeBase joints (king) are unaffected.

## What PR #508 did, and the gap it left

PR #508 (merged while this lane was measuring) found the same layer,
fixed the tool's derivation (keep the centroid only when its yaw agrees
with the WH-Canonical-22 template toe within 60°, else use the template
toe rotated into the bank frame), rotated the sideways foot geometry of
five unrigged Tripo statics (a separate, real bind defect in those source
assets), and edited bosconovitch's six `foot_tip` numbers.

The gap: that edit landed on a `skeleton.json` that had been **pre-turned
offline** (the file's own note: "2026-10-22 facing fix: baked −Z … turned
180 about Y + L/R relabelled offline to +Z"). The bank's clips were never
turned. With the skeleton pre-turned, the runtime's `bankFacing` stopped
detecting the bank as turned, and the retarget paired the turned joint
names against the unturned clip tracks. Measured on current main after
#508 (same harness):

| Test (post-#508 main) | Left toe | Right toe | vs source FK |
|---|---|---|---|
| A1 + bosco bank | +44.6° | −16.6° | source +29.6/−7.1 — no match |
| Leo man + bosco bank | +55.7° | −25.7° | feet floating (ankle y 0.18–0.29 vs 0.05–0.08 planted) |
| A1 + jin bank | +5.5° | +11.3° | exact match (jin untouched, still consistent) |

(#508's own validation probe ran on `doc-frank.glb`, the Bosconovitch
base model, and read faithful there; it did not cover A1 or Leo man.)

## This fix

Regenerate every bank's `skeleton.json` with the fixed generator
(`python3 tools/anim/t3_bank_skeleton.py`, the tool as merged by #508 —
no further tool change needed). 11 of 17 banks regenerate byte-identical.
Six change:

- `bosconovitch`: joints return to the GLB-native frame the clips were
  baked in (reverting the offline pre-turn baked into the file; the
  runtime's own `bankFacing`/`turnSkeleton` — PR #455 — detects and turns
  the bank at load again, knee −179.45°) **and** the `foot_tip` becomes
  the corrected canonical toe in that frame.
- `anna`, `bryan`, `eddy`, `julia`, `yoshimitsu`: `foot_tip` only —
  their centroid tips also failed the tool's 60° template gate (anna's
  right tip pointed −140°, bryan's −105°, julia's +92°).

No runtime code change. No GLB edits. The fix is entirely in the shared,
generated bank data, so it lands on every current and future model on
those banks at once.

## After (same harness, same clip, same frame)

| Test | Left toe | Right toe |
|---|---|---|
| Source FK, stance @40% | −6.0° | +35.9° |
| Doc Frank A1 posed @40% | **+3.8°** | **+27.5°** |
| Leo man posed @40% (bosco bank) | **+11.8°** | **+23.6°** |
| Doc Frank Attire 3 base posed @40% | **+2.7°** | **+28.2°** |
| Leo man + king bank (regression; bank byte-identical) | unchanged numbers vs pre-lane baseline | |

The remaining right-foot turnout (~24–36°) is Bosconovitch's own stance,
present in the decoded foot-bone orientations with no reference involved
(−6/+36 above). Posed values sit within ~8–18° of the single-frame
source FK (mixer frame interpolation scale); both feet point forward.

Proof renders in this folder, all viewed before shipping:

- `before_after_stance.png` — PR #483 proof (owner complaint) vs after-fix,
  same stance. Before: both shoes sideways. After: both shoes forward.
- `sidebyside_original_vs_posed.png` — the original A1 model at its own
  rest (feet forward, as pulled) vs after-fix posed. Body-integrity gate:
  proportions, coat/tie/hair, and deformation match the original; only
  the pose (and the corrected feet) differ.
- `docfrank-a1-stance-after-front.png`, `docfrank-a1-original-rest-front.png`
  — the full-size frames the panels were built from.

Reproduce: serve the repo root on :8791, then
`GAME_ROOT=<repo> node measure.mjs <glb> bosconovitch <modelKey> stance`
and `pose_dump.mjs` + `tools/../bake` pipeline as recorded in this lane's
checkpoint (`agent-ops/checkpoints/docfrank-feet-rootcause-20261021.json`).

## Not in this PR

- The five static Tripo GLBs whose bind geometry itself has sideways feet
  were already geometry-fixed by PR #508; the unrigged statics are being
  rigged by the Tripo forefront lane, and once rigged they animate from
  this same bank data.
- Banks whose centroid tip passes the 60° gate keep their measured
  centroid by the tool's design (jin at −2/−15° is near-forward and its
  posed output matches its source exactly).
