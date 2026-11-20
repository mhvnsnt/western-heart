# Thor on his own canon base: Ganryu's real T7 stance and states, and the two weight bugs it exposed

Canon (`roster/thor/CANON.md`, owner verbatim): "Ganryu is Thor, the literal norse god of lightning". "Built on
Ganryu's sumo frame."

Owner on the 2026-11-09 re-rig (`docs/proof/2026-11-09/refit-thor/`): "that was barely a 5% change on thor u did not
fix it". That proof found the cause. He played the Tekken 3 Bryan stance, which his retarget cannot reproduce (head
twisted ~77 deg, torso 12.6 deg and arms 11-12 deg off). Its conclusion: "Fix: his own T7 data, not rig work."

## His own T7 data

* **Stance:** `T7_STANCES.thor` is Ganryu's own kamae (`game/assets/anim/t7/ganryu/`, 0xC8, ganrotsm clip 198,
  87 frames, FK self-check 0.000 m). `test/t7-stance.test.mjs` checks it like every other base: feet planted, torso
  upright, hands above the knees, loop seam < 3 cm.
* **Generic bank:** `T3_BANKS.t7_ganryu` + `OWN_SLOT_BANKS.thor` carry walk, dash, crouch, jumps, sidesteps, guard,
  hit, launch and KO, all from Ganryu's own T7 states, resolved from his motbin by
  `tools/anim/t7_generic_slots/gan.json`. The bake is `data/ganryu_bank_bake.log`: 16 slots, every FK self-check
  0.000 m. KO hips go 1.01 -> 0.15 m and stay down.
* **Not yet:** his 1 / 3 / 4 attacks stay on the bound Tekken 3 Bryan bank. Ganryu has no T7 move pack yet; that is
  the next step (`tools/anim/t7_move_bake.py`, the same path as Pantera's King moves).

`thor-stance-t3-bryan-vs-ganryu.jpg`: left, the Tekken 3 Bryan stance (head cocked, torso twisted); right, Ganryu's
sumo stance (upright, head forward, hands forward).

## Bug 1: his belt and skirt rode his thighs

`thor-t3-vs-ganryu-old-weights.jpg` and `thor-closeups-weights-progression.jpg` (top row): in the sumo stance his
belt and skirt splayed into a flat tray.

Cause: the refit's Hips deform bone is 3.7 cm long (1.092 -> 1.129 m). Bone heat weights by distance to each bone
segment, so the long thigh bones won the whole lower torso. From belt to hem the belly, belt and skirt carried
Hips 1% and thighs 69% (`data/pelvis_profile_before.txt`). From the belt (1.10 m) down to the hem (~0.62 m) they form
one outer shell at least 20 cm from the thigh axis, with no thigh layer under it.

Fix: `tools/auto_rig/pelvis_skirt_weights.py`, the standard no-extra-bones skirt weighting. It was measured with
`--profile` first. Run: `--belt-y 0.95 --hem-y 0.62 --hem-f 0.5 --hem-fade 10 --r-leg 0.16 --r-blend 0.08
--split-sigma 0.07` (`data/pelvis_skirt_weights.json`).

* The belt rides the Hips fully.
* Each skirt point follows the thighs part of the way, more toward the hem; below the hem it keeps half on the hips,
  since a flap hangs from the belt.
* The centre panel's thigh share is split evenly between both thighs.
* Vertices inside 16 cm of the thigh axis (the legs) are untouched.

A first pass with sharp hand-overs (5 cm shell band, 3.5 cm left/right split, pelvis share faded out under the hem)
raised the stress-clip stretch from 1.97 to 5.92 (`data/anim_check_pelvis_first_pass_rejected.json`). It was
rejected. The final, gentler pass measures 2.30 (<= 2.5 passes). The repo's stretch-driven smoothing was tried and
diverges on this dense Tripo mesh (7.6 -> 12.4), so it is not used.

## Bug 2: his shoulders, arms and bracers rode his head

`thor-bracer-fin-before.png`: with his hands forward, each studded forearm bracer stretched into a flat fin.

Cause: the refit's head-territory step gave the Head bone everything above a horizontal cut at the shoulder line.
Between 1.32 and 1.48 m every vertex out to the T-posed arms (|x| <= 0.70 m) was Head-dominant: his traps, deltoids,
upper arms and bracers. This is the same cut-by-height bug as the roster lane's Sha rebind
(`docs/proof/2026-11-10/roster-wireup/`).

Fix: `tools/auto_rig/head_territory_clean.py` (`data/head_territory_clean.json`).

* The head's territory is measured, not cut: the head and helmet above 1.50 m within 0.28 m of its axis, and below
  that only the neck / jaw column.
* Head weight outside it is removed from 105,647 vertices. 54,385 are renormalized; 51,262, mostly Head, are
  inpainted harmonically from their neighbours with the Head channel held at zero (the inpainting step of Robust Skin
  Weights Transfer).
* Their new dominant bones: shoulders 47.5k, upper arms 33.8k, forearms 19.8k, neck / upper spine 4k.
* Nothing inside the head's territory changed (`--profile`: 0 vertices outside it above 1.52 m).

## Result

* `thor-closeups-weights-progression.jpg` (Ganryu stance, two yaws, stance + guard):
  * row 1: old weights (tray + fins);
  * row 2: pelvis fix (tray gone, fins remain);
  * row 3: both fixes. The bracers are studded cylinders on his forearms again, his shoulders are round, and his helmet,
    face and neck are intact.
* `thor-main-vs-ganryu-fixed.jpg`, stance / walk / guard / hit / KO / 1 / 4:
  * top, main today: twisted head and torso, arms flung;
  * bottom: his own sumo stance, shuffle, guard and reactions.
* **Model:** `roster/thor/attires/attire1/model-pelvisfix-cdn.glb`, 19,386,208 B (<= 19.99 MB for jsDelivr; a NEW path,
  so the remote bucket cannot serve a stale copy). `model-rerig-refit.glb` stays beside it. The base colour was
  re-encoded at q90 full chroma (mean error 0.96/255) to fit (`data/pack.json`).
* **Gates:** anim_check edge p99.9 2.30 (`data/anim_check_final.json`). The 40-spike flag is present on the refit too
  (`data/anim_check_before.json`): fast-moving vertices in the stress clip.

## Select card

`thor-card-old-new.png`: re-captured through `tools/portraits/capture.mjs thor` from the model that ships (50 joints).
The select preview's shoulder-swing fit gate (`game/js/select-screen.js`, 0.6 rad cap when a clip carries no intrinsic
swing) rejects Ganryu's hunched sumo shoulders, so the card uses the CMU 14_01 guard fallback
(`stanceSource: cmu-14_01`). In the fight he stands in Ganryu's stance. The old card was the Tekken 3 Bryan stance on
an earlier 73-joint rig, with his head cocked and a hand at his helmet.
