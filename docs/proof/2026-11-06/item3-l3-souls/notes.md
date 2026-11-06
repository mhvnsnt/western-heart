# Item 3 proof — L3: the seven missing-model souls (Wave 3, 2026-11-06)

The seven were `model: null, modelPending: true` in game/js/roster-full.js —
no attires, unselectable, unfightable (before-probe: "fight never reached
roundState=fight", fight-rin-before.json), sharing one 6,523 B placeholder
card. They are six of the Nine Souls plus Gyou, hidden by the 2026-10-22 Nine
Souls redesign "until they get their own models" — L3 is that condition.

## Where each model came from (their own data first; holdings second)

- rin -> `rin-body` — his own soul-body shell in game/assets/models/
  (MODEL-STATUS.md: "RIN soul body", rigged 49-bone, playable-gate PASS).
- byou -> `rave` (declared base) — the Lei Wulong base file, his declared
  base in roster-full.js. The base-shell pattern the other souls follow
  (a soul's own-named shell where one exists; the declared base file where
  not). Kiko Tanaka ladders the same file as her classic attire; her
  defaults are her Tripos. The model-key guard's rider test covers him.
- tou -> `pantera` (declared base) — MODEL-STATUS.md assigns the Tou soul to
  the pantera body and attires.js documents the soul riders on 'pantera'
  ("the souled vessels ride it"). No Paul model exists anywhere in the
  repo (verified: game/assets/models/ + code search).
- sha -> `sha-body` — her own soul-body shell (Xiaoyu body, 50-bone).
- kai -> `kai-body` — his own soul-body shell (Eddy body, 50-bone).
- retsu -> `retsu-body` — his own soul-body shell (Bryan body, 49-bone).
- gyou -> `gyou-attire1` (NEW) — his OWN spirit body: the Tripo "fiery
  humanoid" archived 2026-10-22 at roster/gyou/spirit-body/ (byte-verified
  sha256 a1bd1432… against the archive MANIFEST) whose SPEC.md schedules
  exactly this: "Rig lane: rig like other Tripo intakes when scheduled."
  Rigged on the auto_rig refit pipeline (template fit — he is T-posed;
  LeftHandThumb3 restored; fine-proxy heat bake; head-territory pass) at
  1.75 m, the soul-body class height. validate PASS (1.75 m, foot 0.0,
  fingers symmetric, 0 unweighted); seams PASS (0.0001); anim_check stretch
  p99.9 11.60 on the CMU stress clip — declared deviation (flame-wisp micro
  edges; in-game hwoarang motions clean, see stills). The archive bytes are
  untouched; the rig is the new file roster/gyou/spirit-body/model-rigged.glb
  per the archive's own usage rule. His spirit form ('gyou-spirit') is
  unchanged.

## Two source-file repairs (in place, geometry untouched)

- kai-body.glb: the material audit quarantined it ("1 untextured") —
  ModelHair_Base_Material017 carried no texture and no colour. Repaired
  with the authored flat colour sampled from the model's OWN hair texture
  (ModelHair map average RGB 0.197/0.153/0.106, warm dark brown), which the
  audit's authoredFlat rule accepts as an authored colour. JSON-chunk-only
  change (+44 B); material-status.js regenerated state (line removed).
- sha-body.glb: her pigtail/hair masses were bound to the shoulder/arm
  chains (head-zone audit: RightShoulder 3,644 / LeftShoulder 3,208
  dominant verts > 0.25), so arm-raising poses wrapped hair across her
  face. Repaired with a geodesic head-territory claim (weld by position,
  BFS from above the Head joint, arm capsules blocked; 10,793 verts
  claimed, 8,273 rebound onto the head/spine ladder). Weights-only;
  re-probe: 8/10 damage identical, inputs 4 and d+1 improved connections
  (15.3 -> 19.3, 19.3 -> 27.3; the animated-body hit-connection class),
  motion range 0.759 -> 0.809.

## Fights (fixed-step, live Pantera, 1.1 m; JSONs + stills in this folder)

All seven instance and fight on real banks with full damage tables:
rin jin (49 bones, stance 1.69 m), byou jin via his demonio moveset
(50 bones, 1.672 m), tou paul on the pantera body (49 bones, 1.671 m),
sha xiaoyu (50 bones, 1.574 m), kai eddy (50 bones, 1.587 m),
retsu bryan (49 bones, 1.62 m), gyou hwoarang (50 bones, 1.642 m).
Before this change none of them could start a fight at all.

## Cards + un-hide

Six cards recaptured via tools/portraits/capture.mjs and viewed true to
character (cards-contact-20261106.png): rin and byou pose on their own
tekken-bank (jin) stances; tou, kai, retsu, gyou on the cmu-14_01 fallback
(their bank stances are fit-gate rejected — the item-7 class). The seven
come off SELECT_HIDDEN in game/js/select-screen.js — the redesign's own
return condition (real bodies) is met; the soul-spirit toggle remains
their presence on other fighters. KNOWN-PLACEHOLDERS shrinks 7 -> 1.

SHA'S CARD IS THE ONE REMAINING GAP (documented, not hidden): her bank
stance is fit-rejected ("Right shoulder swung 0.99 rad from bind" — her
rig is authored in a dynamic idol pose, peace signs up) and the CMU aim
fallback (game/js/stance-aim.js) deforms her head/shoulders at bust
framing. Verified by isolation: with the aim step disabled in a
serve-tree diagnostic her posed card is clean (sha-fullframe.png); with
the standard tool it is not shippable, so her card stays the registered
placeholder, her manifest entry records the honest uncaptured state
(model sha-body, stance false), POSE-BLOCKERS carries her entry, and the
fix rides the Wave 3 item-7 stance class, which owns bank-stance fit and
the fallback path. She is selectable and fights correctly today.

Portraits gate on the post-change tree: "57 select fighters, 1 pose
blockers, 1 registered placeholders — PASS". Model-key guard: the two
resolution tests pass; the file-existence test fails locally only on
pre-existing fighters whose files are not materialized in this lane's
sparse checkout (zen/pantera/demonio/phantom paths) — none of the seven
souls is implicated; CI runs the full tree.
