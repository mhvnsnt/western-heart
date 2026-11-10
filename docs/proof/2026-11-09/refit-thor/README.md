# Thor attire 1 re-rig: wired, NOT a fix of the crushed look (2026-11-09)

Owner (verbatim): "Arms at shoulders, forearms, and hands are all crushed and twisted some have extreme weight painting
issues all over and some have twisted necks or stretched faces evaluate and fix it all".

## Pipeline

1. `roster/thor/attires/attire1/model-rerig.glb` (kept, keep-both) went through the repo pipeline
   `tools/auto_rig/refit_rig.py`:
   - the template skeleton fitted inside his own body from its landmarks;
   - Blender bone heat re-skin;
   - head territory;
   - gates.

   It ran with `--facing +Z --height 1.8`, measured from the model (`batch_refit.facing_and_height`).
2. The result was packed by `tools/deploy/fit_cdn_budget.py`:
   - PNG to full-chroma JPEG at q88 (his 4096^2 normal map: 4.37 MB to 1.02 MB, mean channel error 0.56);
   - gltfpack -cc.

   30.9 MB became 19.96 MB, so Cloudflare Pages serves it directly and it is under jsDelivr's 20 MB.
3. The packed result is now `model-rerig-refit.glb`, and `game/js/assets.js` `thor:` points at it.

## Judged by eye

The images come from `tools/model-audit/weight_compare.mjs`: the game's own loader and retarget, the old model on the
left and the re-rig on the right.

- **Owner's verdict (2026-11-09):** "that was barely a 5% change on thor u did not fix it". Against his base model at
  rest, the in-fight Thor is still squashed: a short torso, the head sunk between hunched shoulders, tucked arms. The
  re-rig only changed his weights and joints.
- **Cause, checked by eye:** Thor has no T7 stance, so he plays the Tekken 3 Bryan stance. The retarget does not
  reproduce that source faithfully: the torso is 12.6 deg off and the arms 11-12 deg off. It also stacks three
  correction layers on the old data (head-frame 77 deg, spine-pitch -12.9 deg, arm rolls 48-76 deg). Switching them
  off in poselab (`__WH_RETARGET_LAYERS`) makes his upper body more upright but exposes the raw T3 head, twisted about
  77 deg. No layer setting fixes it. The fix is his own T7 data.
- **Torn vertices** (stretch >= 2x and >= 1 cm):

  | Clip | Before | After |
  |---|---|---|
  | Stance | 25,703 | 5,191 |
  | Light | 45,558 | 16,904 |
  | Hit | 41,575 | 13,843 |

- **Packed vs unpacked:** visually identical (`refit-vs-packed-stance.png`).

## Pipeline gates

Validate and seams pass, and so does the official anim_check (p99.9 1.88 against 2.5). The strict stretch gate fails
(4.91; the foot spikes the pipeline notes on every rig). It is wired on the by-eye result, per the owner's rule (judge
by eye).

His light clip still leans far forward. Thor's actions come from the Tekken 3 Bryan bank; the fix for that is his own
T7 actions, which need the T7 paks.
