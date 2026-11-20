# Character tools — Blender runbook (creation-suite pipeline)

Wiring target: this doc lives in customization/ as the creation-suite
pipeline record. The addons themselves are NOT vendored into this repo:
they are large upstream Blender addons installed from their own pulls
(see workspace open-source lane), and tools/blender/ does not exist on
main. Install = Blender Preferences → Add-ons → Install → pick the
zip/dir → enable. None of these were executed inside Blender by the
open-source lane (no display on that box); the runbook is the one-step
path, and the Blender-version gate below is the gate before production
use. Headless addon-enable tests are still owed and are NOT claimed here.

Buttons, per standing rule: LP1 = Left Punch = Tekken 1, RP2 = Right
Punch = Tekken 2, LK3 = Left Kick = Tekken 3, RK4 = Right Kick = Tekken 4.

## 1. Rokoko Studio Live for Blender (retargeting)
- License: LGPL-3.0 (LICENSE.md in the addon checkout, confirmed).
- Use: retarget a source armature's animation onto a WH character rig.
  Steps (from the addon's documented workflow): open the Rokoko panel (N
  sidebar) → Retargeting shelf → set Source armature (animation owner)
  and Target armature (WH rig) → Build Bone List → map bones → tick
  "Use Pose: Rest" + "Auto Scale" → Retarget Animation → delete source
  armature, export the target as GLB.
- Caveat (read from user reports, not the README): the addon asks for a
  free Rokoko account sign-in for live streaming; the retargeting panel
  itself is the free part. If sign-in blocks headless use, fall back to
  the in-game retargeter (game/lib/retarget.js, three.js
  SkeletonUtils) — same bone-map idea, no account.
- WH hook: Blender step only. Output GLB goes through
  tools/glb-tools/validate.mjs before it ever reaches the game.

## 2. MB-Lab (parametric characters, Blender 4.0+)
- License, confirmed from license.txt in the checkout: code GPL-3.0.
  Its README carries an MIT badge, but that badge is stale/misleading —
  DO NOT ship MB-Lab-derived assets as "MIT". The generated-asset
  license is not stated in license.txt; that question stays open.
- State: last upstream update July 2024, built for Blender 4.0. On
  Blender 4.5 it may break on API changes — test on 4.0.2 first.
- Use for WH: generate base human bodies for the creation suite
  (phenotype sliders, age/muscle/tone morphs), finalize, export GLB,
  then retarget WH animations onto them. MB-Lab output is a BASE, not a
  finished WH fighter — canon styling happens after.

## 3. MPFB2 (MakeHuman Plugin for Blender 2) — preferred over MB-Lab
- License, confirmed from the checkout: code GPL-3.0 (LICENSE.CODE.md);
  bundled/generated assets CC0 (LICENSE.ASSETS.md).
- Why preferred: actively maintained (stable 2.08, 2025), Rigify
  support, and — critically — content it generates is CC0, which
  removes the MB-Lab license question for generated characters.
- Use for WH: same creation-suite role as MB-Lab, but first choice for
  any character that ships. Export formats include GLB via Blender.

## 4. CharMorph (MB-Lab rewrite, Rigify-native)
- License, confirmed from license.txt in the checkout: code GPL-3.0.
- Why it matters: full Rigify support with face rig, realtime clothing
  fitting (no MB-Lab "finalize then proxy-fit" step), Blender 4.4
  support in v0.4.0. If MPFB2's rig doesn't match the WH skeleton,
  CharMorph's Rigify output is the next candidate for the retarget map.
- Priority order for WH creation suite: MPFB2 → CharMorph → MB-Lab
  (last, license + staleness reasons above).

## Blender-version gate (run before adopting any of the above)
- Blender 4.0.2 and 4.5.3 headless version checks, then enable the addon
  headless and read its bl_info; if enable fails on 4.5, use 4.0.2 for
  that addon and record the pin.
- Every GLB an addon produces goes through tools/glb-tools/validate.mjs
  (validator first, optimizer second) before it reaches the game.
