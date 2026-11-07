# Arm candy-wrapper twist audit — 2026-11-07

Owner order (2026-11-06 23:51 CST, verbatim): "Now gotta fix the wired candy wrapper shoulders, arms, elbows, and hands twists and wired stuff happening on every caharcters arms almost"

Scope: the arm chains (Shoulder / Arm / ForeArm / Hand, both sides) of every
T3 bank in `game/assets/anim/t3/`, the T7 stance/move path
(`game/assets/anim/t7/`), and the retarget engine `game/js/t3anims.js`.
Method mirrors the head/face audit of 2026-11-06 (PR #1620): census the
source data on its own skeleton, measure the target side through the real
retarget, rule mechanisms in or out by measurement, fix only what the
measurements convict, and split out what honestly belongs to another lane.

## Verdict in one paragraph

The banks' arm data is anatomical. The wrapper is created in transport:
the retarget's per-joint swing `A(c)` aligns bone **directions** exactly
(posed positions and directions are transported exactly) but cannot carry
the source frame's **roll**, so the roll split between adjacent arm locals
is scrambled by conjugation with per-joint constants that differ from
joint to joint. The forearm local absorbs a large **constant** twist
error — circular spread exactly 0.0° across stance, light and heavy
clips — which rolls the elbow's hinge axis (up to ~80° off anatomical)
and rolls the frame the hand sits in. The fix measures a constant roll
per arm joint per (bank, rig) from the bank's own stance at first
retarget and counter-rolls `G(joint)` about the joint's posed bone axis
in the frame loop — the same pattern as the head fix, with the constant
living on the per-model cache entry instead of the skeleton because the
error depends on the rig's rest pose as well as the bank. No positions
change, no bone directions change; only the roll split moves to where
the source put it.

## 1. Census — the source data on its own skeleton

Per bank, per arm joint: the stance local's twist about the bone's own
long axis (circular mean / spread), cross-checked on light and heavy
clips, plus the elbow hinge error of the composed stance (forearm
rotation axis vs the anatomical hinge implied by the posed bone
directions). Full tables: `census-results.json` in the lane scratch;
headline findings:

- **ForeArm twist ≈ 0.0° in 24 of 26 banks, in every clip.** The elbow
  is a pure hinge swing in the bake convention; no roll lives in the
  forearm local. Exceptions: the king bank (L +13.5 / R −21.1, constant,
  drift 0.1 — a constant of that bake) and xiaoyu (L +11.7 / R −14.9).
- **Hand twist is a large per-bank near-constant**, cross-clip drift
  0.0–0.3° in many banks (jin R −93.8 in stance, light and heavy alike;
  gunjack L +56.8 / R −56.9 with drift 0.0, near-perfect antisymmetry;
  lei L +65.8; ogre L +28.2; paul L −40.3). Hand locals are near-frozen
  per clip (within-clip RMS 0.0–0.1° across the stance/action family in
  jin, bosconovitch, gunjack, king): the hand barely animates in the
  bakes — its local is effectively a per-bank frame constant.
- **Arm (upper-arm) twist is large and per-bank**: near-constant across
  clips in bosconovitch R (−106…−115), jun (+119…+151), roger
  (+114…+154), nina R, raven R, lei R, paul L; acting-entangled
  (cross-clip drift 55–94°) in jin L, ogre, king, gon, yoshimitsu.
- **Shoulder twist shows no clean frame signature** (cross-clip drift
  large almost everywhere) — clavicle acting, not a frame constant.
- **Elbow hinge error on the bank's own skeleton: 0.0–0.5° in nearly
  every bank.** The source bakes bend anatomically. Two exceptions:
  king_on_pantera_leoman 8.4–13.7° (a real property of that bake), and
  **xiaoyu 28.9–33.2°** — her forearm flexion axis is rolled ~30° off
  anatomical *in the source data itself* (see §5, residuals).
- armorking's hand twists are exactly the king bank's — shared bake
  source, as with the head census.

## 2. Target side — what the retarget does to the arms

Harness: the head-frame test's canonical rig (Mixamo-shaped, identity
rest), real banks through the real `retargetT3Clips`, per-frame twist
error Δ = twist(target local) − twist(source local) about each side's
own bone axis, plus the flexion-weighted elbow hinge error on the
target (hingeT) vs the source (hingeS).

| bank | Δ ForeArm L / R (stance) | Δ Arm L / R (stance) | hingeT L / R | hingeS L / R |
|---|---|---|---|---|
| jin | −19.9 / **−154.1** | −42.7 / +50.2 | 13.7 / **79.7** | 0.4 / 0.4 |
| heihachi | −19.8 / **−154.1** | −46.9 / +17.9 | 16.8 / **80.1** | 1.0 / 0.2 |
| paul | +29.9 / **+84.2** | +26.3 / +16.6 | 18.3 / **46.6** | 0.3 / 0.8 |
| gunjack | +17.3 / −19.8 | −9.1 / +2.4 | 10.6 / 15.4 | 0.2 / 0.2 |
| bosconovitch | −1.2 / +4.3 | −9.5 / +6.8 | 0.8 / 2.4 | 0.1 / 0.1 |
| jun | 0.0 / 0.0 | 0.0 / 0.0 | — (straight elbows) | — |
| roger | 0.0 / 0.0 | 0.0 / 0.0 | — | — |
| xiaoyu | 0.0 / 0.0 | 0.0 / 0.0 | 29.1 / 33.1 | 29.1 / 33.1 |
| king (control) | 0.0 / 0.0 | 0.0 / 0.0 | 8.8 / 13.7 | 8.8 / 13.7 |

- **ForeArm Δ is an exact constant**: spread 0.0° within every clip and
  the same mean in stance, light and heavy (jin R −154.1 three times).
- **Hand Δ = 0.0 in every bank and clip on this rig.** `A(Hand) =
  A(ForeArm)`, so the hand local is transported by pure conjugation,
  which preserves twist about the mapped axis exactly. The wrist
  wrapper the owner sees is the forearm's rolled frame, not a hand
  error. (On rigs whose Hand rest quaternion differs from the
  ForeArm's, a hand Δ can appear — the fix's solve includes the Hand
  for exactly that case.)
- **Arm Δ is near-constant in the stance** (spread ~2°) but its mean
  wanders in big-swing move clips: the Arm error is a function of the
  local itself, and only its constant part is removable by a constant
  (see §5).
- **Shoulder Δ** appears even where the whole chain below it is exact
  (jun +28.4 / −29.8, roger +14.4 / −12.5, xiaoyu −19.3 / +20.6): that
  part is the deliberate torso-match re-split landing in the clavicle
  local (the torso match rotates `D.Chest` so the target's hips→head
  direction equals the source's; the shoulder's local is measured
  against that corrected chest). It is gated separately (§3).
- **King is the exact control**: Δ = 0.0 everywhere, hingeT == hingeS
  to the tenth of a degree. Where a bank's skeleton rest directions
  match the target rig's, transport is already exact — the defect is
  precisely the rest-direction mismatch, bank by bank, rig by rig.
- Xiaoyu's hingeT == hingeS: her in-source hinge error transports
  *faithfully*. It is not a transport defect and the fix must not —
  and does not — touch it.

### Mechanism, ruled in and out

- **Ruled in — swing-only transport (roll scrambling).** With
  `local(k) = Wrest(parent)⁻¹ · A(parent)⁻¹ · Φ(L_source) · A(k) ·
  Wrest(k)`, adjacent joints are conjugated by *different* constants,
  so the relative roll between their frames rotates: the elbow bend
  axis and the hand's frame land rolled by a per-(bank, rig, joint)
  constant. Every measurement above is that constant showing up.
- **Ruled out — source-geometry defect.** On their own skeletons the
  banks' elbows are anatomical (hinge error ≈ 0) and forearm locals
  are pure hinges. There is nothing to re-bake.
- **Ruled out — GLB rest-pose roll.** The head audit's 195-model
  census measured 0.0° rest twist on the roster GLBs, and the harness
  reproduces the full defect on a synthetic identity-rest rig.
- **Ruled out — a hand-track defect.** Hand locals transport exactly
  (Δ = 0.0) wherever `Wrest(Hand) = Wrest(ForeArm)`; the visible hand
  twist is inherited from the forearm frame.
- **Not this lane — skinning.** Any residual surface shear after the
  locals match the source is weight bleed / twist-bone absence in a
  specific GLB (the head audit split Yukihyo's weight bleed out the
  same way; that lane is still running). §5 names what was measured.

## 3. The fix — `game/js/t3anims.js`

`estimateArmCorr(rig, skel, stanceClip, probeClip, THREE)`, called from
`retargetT3Clips` at the first call that carries the bank's stance:

1. The stance is built once **uncorrected** through the real frame
   loop (the probe — torso match and all; a stance cached uncorrected
   by an earlier call serves as the probe). The action-loop body was
   factored into `buildClip(action, corr)` so probe and production
   share the exact frame math.
2. Per side, top-down (Shoulder, Arm, ForeArm, Hand): from the probe
   tracks (target locals) and the bank's raw stance (source locals),
   a constant roll θ about the joint's posed bone axis is bisected so
   the stance's circular-mean twist error becomes zero, with the
   already-solved parent roll factored in:
   `L'(j) = Rot(ownAxis(parent), −θ_parent) · Rot(d̂_j(f), θ_j) · L(j;f)`.
3. **Gates** (from the measured clusters — clean transports sit at
   0.0–4.7°, real constants at 17.3°+): a joint is corrected only when
   its stance twist error is ≥ 12°; the Shoulder, whose delta is
   entangled with the deliberate torso-match re-split, uses 25°.
4. The constants are cached on the **per-model retarget entry**
   (`c.armCorr`), not on the skeleton: the error lives in the
   A/Wrest conjugation, so it is a property of the (bank, rig) pair.
5. In the frame loop, each corrected joint's world rotation is
   rolled before `delta()`: `G'(j) = Rot(G(j)·â_j, θ_j) · G(j)` —
   the head fix's site and shape. Profile secondary chains
   (Chatur's waist pair) receive the same rolls on `G2` for the
   self-fill layer; donor-bank composites keep their own data.
6. **'t7:' skeletons are not exempt** — and do not need to be: the
   correction removes only the *difference* between target and
   source twists, so a T7 stance's own arm twists are reproduced,
   never flattened (measured in §4). Where a T7 transport is already
   exact, the gates leave it untouched.

A roll about a bone's own axis changes no joint position and no bone
direction — the posed skeleton is identical; only the roll split
between adjacent locals moves, which is precisely the skin-twist the
owner reported.

## 4. Proof — numbers after the fix (same harness)

| bank | stance Δ after | hinge after | note |
|---|---|---|---|
| jin | Arm/ForeArm/Hand → 0.0 | L 0.3 / R 0.1 (was 13.7 / 79.7) | light+heavy ForeArm/Hand stay 0.0, hinge ≤ 0.8 |
| heihachi | → 0.0 | R 0.1 (was ~80) | |
| paul | → 0.0 | R 0.1 (was 46.6) | |
| gunjack | ForeArm/Hand → 0.0 | 0.1 (was 15.4) | Arm under gate, unchanged |
| jun | Shoulder → 0.0, chain stays 0.0 | — | shoulder θ cascades: chain compensates at the same value |
| king | unchanged (no correction fired) | 8.8 / 13.7 = his data | |
| bosconovitch | unchanged | 0.8 / 2.4 | all deltas under gates |
| xiaoyu | unchanged | 29.1 / 33.1 = her source data | negative control holds |
| roger | unchanged | — | shoulder Δ 14.4 / −12.5 under the 25° gate |

**T7 path** (Pantera's real T7 king stance swapped onto the canonical
rig via `applyT7Stance`): pre-fix Δ Arm/ForeArm/Hand = 0.0, Shoulder
±6.9 (under all gates) — the TekkenMannequin skeleton's arm rest
directions match this rig, so its transport is already exact. Post-fix
identical; no correction fires. His stance's own arm twists
(L −57° / R +37°, the real side-on guard) are reproduced exactly.

**Tests**: `test/arm-frame-normalization.test.mjs` (new, 7 tests:
jin stance + move clips, paul, jun shoulder, king untouched, xiaoyu
source-true preserved, T7 exact) — 7/7 with the fix; the head-frame
suite stays 5/5. Against the UNMODIFIED engine, exactly the 4
defect-detecting tests in the new file fail and the 3 guard tests
(king, xiaoyu, T7) pass — the test file convicts the old engine and
clears the new one.

Full suites, run locally in the audit's (sparse) worktree before vs
after the fix, same tree both times:

- `test/`: 458 tests. Unmodified engine 29 fail; fixed engine 25
  fail. The failure-name sets differ ONLY by the 4 defect-detecting
  tests above flipping fail → pass. **Zero regressions.**
- `game/tests/`: 775 tests, 747 pass / 28 fail under BOTH engines —
  failure-name sets identical.

The remaining local failures are all in files this audit never
touches (teardown-state audits, music/jukebox, portraits, parts,
batch-key data audits, model-URL existence) and trace to data outside
the audit worktree's extracted set (the full repo tree is what CI
runs; the PR's CI result is the authoritative full-tree gate).
Environment note: the live-fight proof (`tools/proof-harness/
fight.mjs`) was attempted twice in the audit worktree and the full
game boot stalls before `window.__modes` in this sparse tree (it
needs the complete menu/data closure, which the audit tree does not
carry); the pose-lab bench, which loads the same fighters through
the same engine, runs fine in the same tree (§4 stills). The fight
proof is owed from a full checkout and is flagged as a deviation in
the PR.

**Stills** (textured models in fighting stance — no T-pose, no gray
clay; before = unmodified engine, after = this fix, same model, same
clip, same clip time; front row over side row):

- `pair_demonio_stance.png` — Demonio (jin bank, stance). The
  headline pair: pre-fix the side view's claw sprawls across his face
  on a wrung forearm (the 79.7° right-hinge error); post-fix the arm
  folds into the guard the source pose intends.
  `demonio_stance_poselab_full_after.png` is the full pose-lab frame
  (raw bank on its own rig at left) for the after state.
- `pair_demonio_jin_heavy.png` — Demonio, jin heavy at t=0.45: the
  raised striking arm is out of the elbow-readable zone in both
  frames; this pair is carried by the numbers (heavy ForeArm/Hand Δ
  ≤ 0.5°, hinge ≤ 0.8° post-fix).
- `pair_diablo_heihachi_stance.png` — Diablo (heihachi bank): his
  ornate design (sleeves, props, skirt armor) obscures the elbows in
  both frames; the pair shows the head/torso settling level, and the
  bank's fix rests on the harness numbers (hinge R ~80° → 0.1°) plus
  the correction firing on his own rig (constants logged in-browser:
  LeftArm 47.6°, LeftForeArm 67.4°, RightShoulder −173.0° — his
  model's shoulder rest frame is rolled near a half-turn from the
  bank skeleton's, which is exactly the per-(bank, rig) variation the
  cache placement exists for).
- `pair_samura1_gunjack_stance.png` — Sam-ur-a1 (gunjack bank): the
  subtle pair, matching gunjack's smaller constants — pre-fix the
  forearm cuffs and claw hands sit rolled off the guard axis;
  post-fix they sit on it.
- `pair_paulbank_on_demonio_stance.png` — the paul bank on Demonio's
  model (Tou, the paul-bank fighter, has no model — §5.5). At this
  frame the corrected guard crosses the face line in front view on
  Demonio's oversized claw geometry; the transport itself is exact
  (Δ = 0 by measurement), so the still is presented as-is rather than
  re-framed to flatter it.

## 5. Honest residuals — measured, named, not papered over

1. **Arm twist error during big-swing moves is swing-dependent, not
   constant.** A stance-measured constant zeroes the stance (the held
   guard — the pose a fighter sits in) and improves most move means,
   but individual move clips can keep or even trade error: jin light
   R Arm mean −21.7° pre-fix → −71.9° post-fix, while his heavy
   improves (+33.3° → −16.8°) and his stance goes +50.2° → 0.0°. The
   ForeArm and Hand — the elbow hinge and the wrist, where the
   wrapper is anatomical breakage — are exact in **every** clip
   measured. Removing the Arm's swing-dependent part would need a
   per-frame (non-constant) correction, which this fix deliberately
   does not do (the head audit rejected pooled-clip estimation for
   the same reason: it contaminates clean banks).
2. **Xiaoyu's elbow flexion axis is rolled 29–33° in her source
   data.** It transports faithfully (Δ = 0.0) and is left exactly as
   baked. If the owner wants it changed, that is a re-bake decision
   about her bank data, not a retarget fix.
3. **Shoulder deltas under the 25° gate stay** (roger ±12–15°,
   gunjack stance ±15°, bosconovitch ±12–14°, xiaoyu ±19–21°): these
   are dominated by the torso-match re-split, an engine feature with
   its own proof history; the clavicle skin span is short. Jun's
   28–30° pair crossed the gate and is corrected.
4. **The king bank's own small constants** (ForeArm twist +13.5 /
   −21.1 in its source locals; stance hinge error 8.8 / 13.7°) are
   that bake's real data — reproduced, not normalized (pinned by
   test).
5. **Tou, the paul-bank fighter, has no model** (roster entry
   `model: null`, no `roster/tou/` in the repo), so the paul bank's
   still is a bench shot on another fighter's model, labeled as
   such. The bank's fix itself is proven numerically above and by
   the paul test.
6. Skinning-side arm shear (weight bleed across the elbow/wrist,
   missing twist bones) cannot be fixed in the retarget and was not
   faked here; per-model skinning defects route to the weight-bleed
   lane, as Yukihyo's did in the head audit.
