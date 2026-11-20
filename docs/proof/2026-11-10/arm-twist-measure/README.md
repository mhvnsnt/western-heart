# Arm-twist measure: rig-frame independent (every Tekken 3 bank fighter), 2026-11-10

Owner (verbatim): "Arms at shoulders, forearms, and hands are all crushed and twisted some have extreme weight painting
issues all over and some have twisted necks or stretched faces evaluate and fix it all".

## What was wrong

The arm-frame normalization (`estimateArmCorr`, `game/js/t3anims.js`, added 2026-11-07) measures, per arm joint, the
twist of the fighter's POSED LOCAL rotation against the source's, and rolls the arm to cancel the difference.

- On an identity-rest rig (what its tests used) the posed local is the motion, so the measure is the transport error.
- On real exported rigs (Blender / Tripo / Mixamo) the posed local also contains the rest local's own roll: how the
  rig's author happened to orient each bone. The measure read that roll as an error and "corrected" it, rolling the
  arms in every clip of the bank.
- The same bug rolled the arms of 16 T7-stance fighters by 40-200 deg (fixed for T7 data in `70e90b4`,
  `docs/proof/2026-11-10/t7-arm-roll/`). This fixes it for the Tekken 3 banks every other fighter plays.

## The fix

The twist is now read from the motion relative to the bone's rest local (posed local x rest local^-1):

- identical on identity-rest rigs, so every genuine constant the 2026-11-07 audit pinned is unchanged (jin right
  forearm -154 deg, paul +84 deg on the canonical rig) and all its tests pass untouched;
- independent of how a rig's bones are rolled at rest, so only genuine transport differences are corrected (swing
  alignments that differ between a parent and its child when the bank's rest pose differs from the rig's).

## Proof

- **Test** (`test/arm-frame-normalization.test.mjs`): the same bank on the same skeleton geometry, identity-rest rig
  vs a rig with Blender-style rolled rest frames, must pose every arm joint the same in world space. Before the fix:
  jin 124 deg, paul 150, bryan 133, gunjack 149 apart. After: under 1 deg. Arm tests 12/12.
- **By eye** (`before-after-1.jpg` .. `-8.jpg`, most-changed first): all 60 renderable T3-bank fighters in their stance,
  the game before this fix and after it, front and three-quarter. `kai` and `bf-maime` cannot be judged: poselab's
  material gate refuses their untextured models.
  - Clearly better (11): kronos (crushed crossed forearms -> clean raised-hands stance); zui (palm-up wrist -> guard);
    the torn shoulder flaps on bf-stan-combs, bf-tyneshia, bf-kobra, bf-viper, bf-static, bf-edwin-kennedy and
    bf-master-sensei; demonio and michiko slightly.
  - Same (~39).
  - Different but not judgeable (~10): slice, bruno, baek-master-white, ryuji-rock, cainelias, cyborgx, samura1,
    dorowani, megami, scimitar. Their arm JOINTS are in identical places before and after (checked numerically on
    bruno and slice: every shoulder / elbow / wrist position equal to the millimetre). A roll moves no joint, so the
    visible difference is geometry weighted to the wrong bone (a fist or blade on the upper arm) swinging with the
    roll. Those models need their weights fixed; neither render is right.
  - Clearly worse: none.
- **Broken rigs this sweep exposed (not this fix, both renders broken):** bf-jager, bf-onyx, bf-hollow,
  bf-tarzanian-devil, bf-triple-xxx (head), rave, charger, waterfall (accessory sheet), rin (upper arms stay straight
  out at the sides), and the torn arm shards on bf-cipher / bf-echo / bf-finxsse / bf-stick-up / bf-hall-nighter.

Renderer: `game/poselab.html` driven by Playwright (stance at 0.5 s, `closeup` upper body); "before" served from
`origin/main` (f5f7b242), "after" from this branch, same models.
