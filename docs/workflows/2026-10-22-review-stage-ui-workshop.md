# 2026-10-22 — Practice review stage + hit-feel tuner + UI Workshop (phase a)

Lane: DoggByte 99fca62a. Owner tasks: practice-mode review stage; hit-feel tuner
IN the game (not a separate page), deltas on teardown values; UI editor
("Unreal UMG inside our game") phase (a) UI ART first, then (b)/(c).

## What was built

**Hit-feel engine hook** (PR #537, merged 77267960):
- `game/js/game.js`: `this.feel = { hitstop: 1, shake: 1, knockback: 1, launch: 1 }`
  (1.0 = wired values untouched); all 6 hitstop sites and 5 `arena.shake` sites
  multiply by the live value; fighters get a `game` ref in `startMatch`.
- `game/js/fighter.js`: `this.game = null` default; `_feelMul(key)` helper;
  knockback (`vx`) and launch (`vy`) in `receiveHit` plus KO blowback scale.

**Practice review stage** (PR #538, merged 6c458de9): `game/review-stage.html`
- REVIEW tab: any fighter (roster picker) in fighting stance — bank `stance`
  clip by default, never a T-pose, no fit-gate (the reviewer sees the truth);
  clip buttons (stance/walkFwd/crouchHold/block + embedded Idle/Walk/Run +
  first 8 moveset strikes retargeted on demand); play/pause/step-1f/speed/loop;
  OrbitControls (orbit/zoom/pan).
- HIT FEEL tab: real training `Game` (`training=true`, passive dummy via
  `ai.passive`); 4 tuner sliders from `game/js/hit-feel.js` FEEL_PARAMS showing
  each param's wired base value; HIT DUMMY (jab via `tryAttack('1')`) + reset;
  EXPORT FEEL PATCH (`hitfeel_tune` kind) through the round-trip.
- Live: https://mhvnsnt.github.io/western-heart/game/review-stage.html?fighter=nightwolf

**Tweak-patch extensions** (PR #539 merged c160401b; PR #541):
- `hitfeel_tune` kind: hitstop/shake/knockback/launch multipliers in [0,4];
  applied to `customization/hit-feel/<fighter>.json` (versioned + history).
- `ui_screen_define` kind: `wh-ui-screen` v1 validation; `fighter: "ui"`
  namespace allowed for screen-only patches; applied to
  `customization/ui-screens/<screen-id>.json`.
- `customization/TWEAK-PATCH-SPEC.md` documents all three kinds.
- 28 importer unit tests, all pass (caught a real KeyError in kit auto-creation).

**UI Workshop phase (a)** (PR #540): `game/ui-workshop.html`
- First-class area: element palette (label/button/panel/image/card-grid),
  1280x720 canvas with click-select + drag-move, properties panel
  (position/size/text/colors/border/radius/weight/align, delete), screen
  picker, EXPORT SCREEN PATCH (`ui_screen_define`).
- `game/js/ui-screen.js`: wh-ui-screen v1 (validate/render/buildScreenPatch).
- `customization/ui-screens/stage-select.t8-template.json`: T8 stage-select
  layout RECREATION (marked as such — the holdings survey confirms no extracted
  T8 UI sprite set exists anywhere; `t8-source/` is reserved and the workshop
  prefers it when it lands).
- Sourcing order + remix doctrine in `customization/ui-screens/README.md`.
- Open-source power: MIT game-hud kit Fantasy (dark/gold) skin wired into the
  workshop chrome.
- Live: https://mhvnsnt.github.io/western-heart/game/ui-workshop.html

## Proof

- `node --check` on all new/edited JS + inline page modules: OK.
- 28/28 importer tests pass; ui-screen.js logic tested in node (validate,
  duplicate-id/bad-type rejection, patch shape); feelPatch() tested in node.
- Mechanical round trips proven: review-stage feelPatch -> importer --check
  valid -> applied; workshop buildScreenPatch (remixed stage-select) ->
  importer --check valid -> applied to customization/ui-screens/stage-select.json.
- Gitleaks clean. CI green (instruction-gate/deletion-guard/guard) on merged PRs.
- Merged via git_merge.py (real 3-way merges).

## Still open (needs live play — subagent has no browser)

Per the standing "verify by playing" directive (phone portrait, human-like
navigation: screenshot, look, scroll, THEN tap):
1. Review stage: open live URL, switch REVIEW/HIT FEEL tabs, play/pause/step a
   strike, orbit the fighter, move hitstop slider to 2.0, HIT DUMMY, feel it.
2. UI Workshop: open live URL, drag the title, restyle a card, EXPORT SCREEN
   PATCH, feed the file to `import_tweak_patch.py --pr`.
3. Then phases (b) flow designer and (c) wiring on user feedback.
