# Roster wire-up lane (PRs #1710 + #1711), finished: Gyou re-rigged, Kai and Sha reach the live hosts, TOU's KO

The lane ("GYOU + KAI selectable", "Sha weight repair", "TOU on his own T7 Paul body") left one open item: the
fight-path check. Everything below was judged by eye in the game's own loader and retarget (`game/poselab.html`,
the same `showFighter` path the fight uses: attire-1 model, bound bank, own-slot bank, T7 stance), not from metrics alone.

## The bucket trap (why Kai and Sha needed new paths)

On localhost and on the GitHub Pages / Netlify shell, the loader tries the remote asset bucket
(`western-heart-assets.mhvnsnt.workers.dev`) **before** the page's own file (`game/js/asset-config.js`
`resolveAssetCandidates`). Nothing syncs that bucket on merge. It still serves main's `kai-body.glb`
(25,644,156 B: the unrepaired file) and main's `sha-body.glb`. So the lane's in-place repairs of those two files would
never have reached players on those hosts. My first Kai and Sha checks loaded the bucket copies as well: Kai was
blocked by the runtime material gate ("1 untextured", main's unrepaired hair), and Sha looked identical in both columns.

The repo's own rule (`tools/deploy/fit_cdn_budget.py`): a repaired model goes under a NEW path, so the bucket misses
and the loader falls through to the page copy / jsDelivr (<= 20 MB). Done here:

| key | was | now | size |
|---|---|---|---|
| `kai-body` | `assets/models/kai-body.glb` (repaired in place) | `assets/models/kai-body-cdn.glb` | 25.6 -> 14.2 MB |
| `sha-body` | `assets/models/sha-body.glb` (repaired in place) | `assets/models/sha-body-hairfix-cdn.glb` (see Sha) | 16.8 -> 14.0 MB |
| `gyou-attire1` | `roster/gyou/spirit-body/model-rigged.glb` (32.5 MB) | `roster/gyou/spirit-body/model-gamerig-cdn.glb` | 19.8 MB |
| `tou-body` | `assets/models/tou-body-cdn.glb` | same path (new in this PR), Spine1 reparented | 13.6 MB |

`kai-body.glb` and `sha-body.glb` are back to main's exact bytes (keep-both: the originals stay beside the fixes).
Kai and Sha were packed with `fit_cdn_budget.py` at JPEG q96, full chroma (Kai's normal maps: mean angle error
<= 1.58 deg; colour error <= 2.2/255). Reports: `data/kai_pack.json`, `data/sha_pack.json`.

## Gyou: arms that bend, legs that come apart

`gyou-before-after.jpg` (top: the shipped `model-rigged.glb`; bottom: this rig), stance / walk / guard / hit / KO /
1 / 4 on his own T7 Hwoarang data.

* **Before:** his arms never moved. 2.7% of the arm-region vertices rode arm bones; the rest were bound to Spine
  (the old skeleton sat 90 deg off his +X-facing mesh). He fought in a T-pose with his arms stuck out.
* **Rig:** the GameRig pipeline on his archived Tripo static (`tools/auto_rig/rig_tripo_static.py`'s steps:
  `gamerig_backend.py --facing +X --height 1.75`, then `limb_isolation.py`, `validate.py`, `anim_check.py`).
  **94.9%** of arm-region vertices now ride arm / hand bones.
  Smoothing (`smooth_weights.py`) was skipped: on his flame wisps it diverges (edge p99.9 12.1 -> 16.4 over 12
  rounds, `data/gyou_smoothing_diverged.log`). Limb isolation alone takes the official gate from 4.35 to
  **2.03 (<= 2.5 passes)**; validate passes.
  `anim_check` still lists two flags:
  * a 0/0 artifact on the zero-length pelvis bones (rest, min and max all 0.000 m);
  * 40 fast-moving thigh vertices in the stress clip's kick (0.35 m per step, the threshold is 0.35).
* **Fused legs:** the Tripo static stands with his legs touching, and flame sheets join them from the feet to the
  crotch (`gyou-rest-pose.jpg`). Every triangle joining the two legs stretched into a fan on the 4 kick
  (`gyou-kick-before-leg-split.jpg`, middle) and into a band at the feet in his stance (right). No weighting fixes a
  triangle that belongs to both legs, so the legs were cut apart the way a modeller would:
  `tools/auto_rig/split_fused_legs.py` removes exactly the triangles whose vertices are dominated by opposite legs:
  **2,238 of 1,938,092** (0.12%), nothing else changed (`data/gyou_split_fused_legs.json`).
* **After:** guard, punches and kicks bend naturally. The kick is clean, shoulders / neck / face intact
  (`gyou-upper-body-closeups.jpg`). Remaining: a small stretch at the hip under the kicking thigh at full extension.
* **Packing:** 19,829,004 B (<= 19.99 MB for jsDelivr). The 4096^2 base colour, a 6.0 MB near-lossless Tripo JPEG,
  is re-encoded at q88 full chroma (4.8 MB, mean error 1.6/255). This uses `fit_cdn_budget.py --jpeg-reencode-min`,
  new in this PR and opt-in; no texture resolution is reduced.
* **Card:** re-captured (`tools/portraits/capture.mjs gyou`) from the new rig. He now holds his real Hwoarang
  guard (`stanceSource: tekken-bank`) instead of the CMU fallback with the arm sticking out (`gyou-card-old-new.png`).

## Sha: the lane's repair broke her arms; kept only its hair half

`sha-lane-repair-vs-main*.jpg` (top: main, bottom: the lane's file, both loaded locally).

The lane's change was a "head-territory rebind, 926 -> 46" over 7,869 vertices. It did three things:

1. Hair 9-22 cm from the Head joint moved off the shoulder / arm bones onto Head / Spine2. Her hair stays on her head
   instead of shattering around a bare scalp. **The fix.**
2. **1,085 right-arm vertices**, 35-49 cm from the Head, were rebound to Head: the T-posed arm sits at head height. In
   every pose her forearm stretched out to a hand left where the T-pose had it. **A regression.**
3. Neck pieces 2-8 cm from the Head moved onto LeftShoulder. **A regression.**

`tools/auto_rig/territory_weight_merge.py` takes main's weights and accepts the lane's weights only inside the head's
territory: <= 30 cm from the Head joint and onto Head / Neck / Spine2 / Spine1. It decides per connected mesh island,
so no hair card or bracelet is cut in two. Result: 6,456 accepted; 1,133 rejected as far, 280 as moved onto a
shoulder (`data/sha_territory_merge.json`). `sha-territory-merge-vs-main*.jpg`: her arms match main in every pose, and
her hair is on her head.

**Still open:** one or two thin hair strands draw a line in some poses. Those cards are partly on the head and partly
on a shoulder in main already. A proper hair-card weight pass is the next step. Her card was re-captured
(`kai-sha-cards-old-new.png`): the old one showed a black mask-like scalp.

## Kai

From his repaired file for the first time: walk, guard, hit, KO and the capoeira 1 / 4 read right on the Eddy bank
(`tou-kai-fight-path.jpg`, bottom). His card was re-captured with the repaired dark-brown hair base.

## TOU: his KO hung his upper body in the air

`tou-ko-before-after-hierarchy-fix.jpg`: top is before, bottom is after.

TOU's real T7 skeleton keeps the legs and the upper body as siblings under BASE (BASE -> Hips -> legs,
BASE -> Spine1 -> chest / arms / head). Every clip drives root motion on Hips, the way the game's Tekken 3 / Mixamo
convention expects. So the Hips' drop moved only his legs. His KO ended with the pelvis on the floor and the upper body
~0.6 m above it on a stretched column.

`tools/auto_rig/reparent_joints.py --move Spine1:Hips` sets Spine1's local transform to inverse(Hips) x Spine1. Every
joint keeps its world bind transform (max change 4e-16), so the inverse bind matrices, weights and bind mesh are
unchanged. After: he falls back and lies flat in one piece. His standing moves are unchanged
(`tou-moves-before-after-hierarchy-fix.jpg`); face and hands intact (`tou-face.jpg`).

## Tests

* Unit suite (`test/*.test.mjs`): every file passes except `test/hitbox.test.mjs`. It fails identically on main with a
  full checkout: its Game stub lacks `ui.attackData`. CI skips that section because its sparse checkout leaves out
  `packages/creation-suite`.
* `game/tests/`: the failures here (batch / skull step plans, dw-retarget / dw-rollout teardown files) fail identically
  on main. `model-key-guard` fails locally only for zen / vainabel files absent from this sparse checkout.
* Menu touch e2e: PASS (menu -> select -> stage -> fight, rematch).
