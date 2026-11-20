# L2 proof — Gashadokuro re-rig + Star rig (Roster-100 Wave 3, 2026-11-06)

Base: main `47e37b430ec4881ba92c420db5d1487b29efd644` (the M3 merge).
All serves were pinned to that ref through a local caching proxy; the asset
resolver's remote candidates were neutralized in the serve copies only
(asset-config.js, serve-tree-only — no repo file changed for it), so every
model byte in every probe/capture below came from the pinned tree or the
lane overlay. Fight probes: fixed-step harness (S5/S7 pattern,
`g._update(1/120)`, AI frozen, HP refilled per trial, P1 placed at 1.1 m
from a live Pantera unless noted).

## Gashadokuro — from statue to fighter

BEFORE (current main, unrigged kuma-a1.glb static): bones 0, no T3 bank
bound (t3dir null, 0 actions), stance height 0.891 m with min-y −0.445 —
a 0.89 m statue sunk to its waist ("tiny flat skeleton" of the #1565
inventory, quantified). Fight record: `fight-gashadokuro-before.json`.

Rig: his OWN Tripo static (roster/kuma attires, Tripo 421f4f05 — "white
bone dragon", rainbow eyes) through the repo refit pipeline
(tools/auto_rig): codec decode → pantera-template skeleton fit →
landmark pass → MEASURED fit correction (16 joints from mesh slice
centroids: the mesh's tail-weight channel is all-zero, so the automatic
leg windows landed inside the tail — LeftFoot at z −0.147 — and the
spine/head windows centred on belly/snout mass; corrected values and
method are recorded inside the fit and in `gashadokuro-gates.json`) →
bone heat (voxel proxy 0.006 m / 80k faces; 50 bones, 0 unweighted
verts) → head territory → codec encode. Height 1.95 m, anchored on
aotsuki (same bear-bank family, authored ~1.95 m; his canon-sizing
entry is 280 cm, apply:false). Head pivot sits mid-skull: the first
bake's skull-base pivot made portrait-capture frame a ~0.22 m window
(its Head–Hips metric) and cropped the skull out of his card —
`gashadokuro-card-v1-misframed.png` is that rejected capture; the
shipped bake's card frames his face (rainbow eye, nose horn, teeth).

Gates (`gashadokuro-gates.json`): validate PASS (1.95 m, foot_y 0.0,
fingers symmetric); seams PASS (0 disagreeing copies); official
anim_check on the CMU 135_04 boxing stress clip p99.9 3.29 vs the 2.5
gate — a documented deviation: absolute elongations are small (median
over-2× edge 5.35 mm, p90 11.28 mm), the 40 tearing spikes are all the
RightFoot kick-motion class the shipped aotsuki rig also shows (40),
and refit_rig.py itself records 30–80 foot spikes on every rig under
this root-pinned clip. seam_safe_smooth was attempted twice and died
silently mid-rounds both times on this 8 GB VM (its log plateaued
5.104 → 4.395 over 18 rounds on the v1 bake); it is not in the shipped
path and that is recorded, not hidden. Posed renders viewed:
`gashadokuro-pose-kick-front.png`, `gashadokuro-pose-spine-side.png` —
kick/spine/head poses deform cleanly, horns rigid on Head, tail rides
the pelvis (no tail bones in the template set; secondary_chains was
run and rejected — it mis-detected dorsal plates/back/tail as hair).

AFTER (rigged successor wired in assets.js): bones 50, T3 kuma bank
binds (t3dir kuma, 22 actions), stance animates (bone-motion range:
hands 0.52 m, hips bob 0.223 m over 2 s of stance; before: 0), stance
height 1.81–1.90 m by sampling phase, min-y 0.017 — grounded.
`fight-gashadokuro-after.json`. Damage vs Pantera at 1.1 m, before →
after: 1: 2.8 → 2.8 · 2: 5.5 → 5.5 · 3: 12.8 → 12.8 · 4: 22.1 → 18.1 ·
d+1: 2.8 → 2.8 · d+2: 3.7 → 3.7 · d/f+1: 2.8 → 2.8 · d/f+2: 5.5 → 5.5 ·
1+3: 17.4 → 17.4 · 2+4: 17.4 → 17.4. Eight of ten identical; both
throws keep their 17.4 total and their execution path UPGRADES from
the legacy lock (before: lock, no pair) to the paired path (after:
pair binds, no lock). Input 4's total varies with animated-body hit
connection — the shipped-rig control (aotsuki, same move class, same
victim/spacing) deals 10.1, and gashadokuro at 0.75 m deals 10.1; the
resolved move and its data are identical in every run
(`fight-gashadokuro-control-aotsuki.json`). Stills viewed:
`gashadokuro-fight-20261106-stance.png`, `-attack.png`.

## Star — rig for her card (and her fight)

Her POSE-BLOCKERS entry was blocked on L2 (the M3 record: both wait on
"a rig in place"). Source: her OWN Tripo static (ea73eeb3, red latex —
blonde afro puffs, red gloves, leg holster, tattoos; verified against
roster/star/CANON.md by eye). Same refit pipeline; the TEMPLATE fit
was used and the landmark pass was not (its left-arm chain degenerated
to a vertical line inside the torso and it dropped her hips 0.15 m —
`star-fit.png` shows both fits against her mesh). The pantera template
itself lacks LeftHandThumb3 (the missing-mirror class validate.py's
docstring records); the fit restores it mirrored from the right thumb,
and the finger chains were symmetrized (her mesh is bilaterally
symmetric). Height 1.59 m, anchored on michiko's authored 1.582 m
(167 cm canon vs her 168 cm Christie entry).

Gates (`star-gates.json`): validate PASS; official anim_check p99.9
1.459 — PASSES the 2.5 gate (shipped aotsuki baseline: 1.784); seams
PASS. Posed render viewed: `star-pose-front.png` (twist + elbow + knee
+ holster all follow, no tears).

Fight (`fight-star-before.json`, `fight-star-after.json`): before —
bones 0, no bank, legacy-lock throws. After — xiaoyu bank binds
(22 actions, 50 bones), stance animates (left foot sweeps 0.48 m in
her capoeira stance), stance height 1.502 m, min-y 0.014. Dealt
damage before → after: seven of ten identical (1: 2.8, 2: 3.7, d+2:
3.7, d/f+1: 6.4, d/f+2: 7.3, 1+3: 17.4, 2+4: 17.4); 3 (27.5 → 8.3),
4 (7.3 → 15.3) and d+1 (19 → 11) changed because resolution switched
from the generic fallback rows to her real bank rows (plans row:343 /
row:279 / row:301) — the intended effect of binding the bank. Her
throws stay on the legacy lock path at identical damage (xiaoyu↔king
pair coverage is bank data, unchanged by a model rig; same flag class
as S7's bank-coverage observation). Data-layer note, NOT fixed here:
her moveset JSON's per-input t3_row labels and the engine's resolved
bank rows do not line up one-for-one (e.g. input 2 resolves plan
row:51; her JSON labels r51 under input 1) — recorded for the
data/owner adjudication list, moveset data untouched. Stills viewed:
`star-fight-20261106-stance.png`, `-attack.png`.

## Cards

`tools/portraits/capture.mjs gashadokuro,star` on the post-change
tree: both record bones 50, stance:true (roster-standard cmu-14_01
select stance; both bank stances are rejected by the PreviewPane fit
gate — gashadokuro's kuma stance: left shoulder 0.72 rad from bind,
the same fit class as Pantera 0.66 / Demonio 0.71 from S4; that class
is Wave 3 item 7), framed:true, armDeg 23/12. Both cards viewed
before shipping (`cards-contact-20261106.png`): his rainbow eye /
skull face, her puffs / red latex / gloves — true to character.
POSE-BLOCKERS: gashadokuro + star entries removed (3 remain:
kingtyrant, nightwolf, cainelias). Gate re-run on the post-change
tree: `portraits: 50 select fighters, 3 pose blockers, 7 registered
placeholders` — PASS.

Deletions: none. The unrigged source statics stay in place
(kuma-a1.glb, star model.glb); the rigged successors sit beside them.
Size delta: +38,869,564 B (gashadokuro-a1-rigged.glb) + 26,306,404 B
(star model-rigged.glb) in-repo; live Pages tree untouched by this PR.
