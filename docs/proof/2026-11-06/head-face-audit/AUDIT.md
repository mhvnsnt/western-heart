# Roster head/neck twist + face-stretch audit — 2026-11-06

Owner report (2026-11-06 ~18:06 CST): some characters — "more than the ones in
naming, but kinpo, zui, and others" — have a twisted neck and head where they are
facing 3/4 towards the cam in an odd way instead of facing their opponents; he
didn't know how many it's happening to. "Yukihyō has some face stretch issues
during match and so do many others, evaluate and fix them all."

## Verdict in one paragraph

One engine defect explains the twist roster-wide, and it also drives most of
the visible face stretch. The banks were baked on each source character's own
part rig, whose head joint frame is itself rotated. The head is the one driven
joint in `retargetT3Clips` with no rest-direction correction, so that constant
lands raw on every target rig: the neck chain follows the chest, the head
follows the twisted track, and the skin between them shears. 24 of the 26 T3
bank skeletons carry a constant ≥ 37°; only king (0.0°, the one canonically
baked bank — Pantera, the reference-good fighter) and bosconovitch (16.2°)
fall under the fix's 20° threshold. The fix measures each bank's constant from
its own stance at load and counter-rotates it out of the head's world rotation
in the chest frame — no authored values, no per-model edits, every clip's real
head acting preserved. A residual face-stretch component on a few auto-rigged
models is a skin-weight property of the shipped GLBs (not the retarget) and is
quantified below as a follow-up for the rig-repair weight-transfer pipeline.

## The bank census (the scope of the twist)

Head-vs-chest rotation of each bank's own neutral stance, composed down the
bank's own skeleton (circular mean over the stance's frames; the head locals
are near-constant across stance frames, spread 1.4–5.0° — a frame constant,
not acting):

| bank | constant | bank | constant |
|---|---|---|---|
| heihachi | 114.6° | lei | 54.6° |
| yoshimitsu | 96.5° (roll −96°) | kuma | 54.4° (pitch −52°) |
| jin | 90.9° | paul | 53.6° |
| jun (TTT2) | 85.9° (roll −85°) | armorking | 45.6° |
| bryan | 77.2° | anna | 44.5° |
| eddy | 74.9° | luckychloe (T7) | 40.1° |
| forestlaw | 74.5° | ogre | 37.5° |
| roger (TTT2) | 74.5° (roll −72°) | nina | 37.4° |
| gunjack | 73.5° | gon | 63.3° |
| julia | 72.0° | hwoarang | 65.3° |
| raven (T7) | 69.3° | law | 60.9° |
| xiaoyu | 61.1° | bosconovitch | 16.2° (under threshold) |
| king | **0.0°** | heihachi_ownrig | 78.7° (unused duplicate bank dir) |

Two bake families sit inside single banks and both carry it: the 22-bone
canonical action clips and the 18-bone own-rig data (the neutral files of
jin/xiaoyu/bryan/gunjack/yoshimitsu, all of heihachi_on_jin, and every bank's
rows pack). Because the retarget composes everything through the one skeleton
and one head driver, correcting the head in the engine's own composition frame
corrects both families as the engine actually plays them (verified on jin
action clips AND jin rows: post-fix row head-vs-chest yaw ≈ 0°).

Owner-named fighters, resolved from their own moveset data (`t3_source`):
**kinpo → jin bank (90.9°)**, **zui → jin bank (90.9°)** — both confirmed
twisted and fixed. **yukihyo → king bank (0.0°)** — his head data is clean
(stance and rows measured in the target frame: head-vs-chest yaw 0–4°); his
symptom is the stretch component below. Also verified end-to-end in the
harness: demonio (jin), dio (heihachi, 114.6° — the worst bank), pantera
(king, control — behavior byte-unchanged), chatur (ogre, 37.5°, her existing
retarget tests stay green).

## Evidence the constant is a bake frame, not acting

- In every canonical bake the Neck track is EXACTLY the Chest's rotation
  (chest→neck = 0.00° for all 19 canonical neutrals measured): the source data
  has no independent neck motion — the neck is rigid with the chest and the
  head carries a fixed frame offset against it.
- Bryan's per-clip head constants cluster tightly (~34° family mean across 17
  clips); king's spread loosely 0–54° the way real acting does. A constant
  that never varies is a coordinate frame, not a performance.
- Composed on its own skeleton, jin's stance head faces ~86° off the body's
  facing (sideways, toward the camera in the side view) while its knees/body
  face the opponent — the owner's description, in the bank's own data.
- Control: Pantera's retargeted stance head delta EXACTLY equals his bank's
  head delta (yaw −4.0°, pitch 22.0°) — the retarget is faithful; what it
  faithfully reproduces on other banks is the baked-in frame.

## Ruled out (measured, not assumed)

- **Rest-pose twist in the shipped GLBs:** all 195 MODEL_URLS models were
  header-censused. kinpo/zui/yukihyo rest head-vs-chest yaw = 0.0°. Not it.
- **Scale keys on head bones:** the retarget never emits scale tracks; the 66
  models with embedded CMU clips carry Head/Neck/HeadTop scale tracks, and
  the values read back through GLTFLoader are 1.000–1.000 (yukihyo, kinpo,
  pantera sampled). Not it.
- **Non-uniform sizing:** canon-sizing's root scale applies to burger forms
  and custom fighters only; head-chain bone scales are unit across the census.
- **Look-at/procedural head code:** none exists in fighter.js; faceRig.js
  drives morph influences only.
- **The 't7:' stance/move skeletons:** T7 king's stance carries a 40° head
  offset that is REAL acting (side-on wrestling stance, head on the opponent,
  proper jointed-rig bake). The fix exempts 't7:' skeletons — Pantera and the
  other T7-stance fighters are owner-approved as-is and stay untouched.

## Face stretch — two components, honestly separated

Measured by real skinning (pairwise-distance distortion of Head-dominant
vertices near the head joint, rest vs posed, via SkinnedMesh.applyBoneTransform):

| fighter | stance mean distortion | notes |
|---|---|---|
| pantera (king) | 0.1% before / 0.1% after | face is 100% Head-weighted — rigid |
| kinpo (jin) | **17.0% before → 5.6% after** | rows/moves drop ~3× across the board |
| yukihyo (king) | 3.5% before / 3.5% after | no twist component — see below |

1. **The twist shear (FIXED):** with the head held ~90° off the neck's driver,
   every vertex blended between Head and Neck/Chest bones shears. Removing the
   constant removes this — kinpo's stance distortion falls 17.0% → 5.6%, and
   her move rows fall similarly.
2. **Auto-rig weight bleed (NOT an engine defect — follow-up):** on the
   75-node template / AdvancedSkeleton auto-rigs, head-area vertices are never
   fully Head-weighted (yukihyo: Head max weight 0.48, with LeftShoulder at
   0.46 and Neck/Spine bones spread across the same vertices). The source's
   genuine head turns (canonical banks: chest→head 37–75°) then smear across
   that broad blend — worst during big arm swings, which is why it reads as
   "during match." The retarget cannot change skin weights, and the neck's
   driver is source-true (neck track == chest in the data), so there is no
   honest engine-side correction for this component. Its fix belongs to the
   rig-repair pipeline stage (automatic weight transfer from correctly-weighted
   reference verts, per the standing no-hand-tooling law) — recommended as a
   follow-up lane for the worst measured models, yukihyo first.

## The fix (game/js/t3anims.js)

Following the file's own bankFacing/standingIdle pattern — a whole-bank
constant measured from the bank's own data at load, nothing authored:

- `estimateHeadOffset(skel, t3Clips, THREE)`: on the first retarget call that
  carries the bank's stance clip, compose the stance on the bank skeleton
  exactly as the frame loop composes G and take the circular mean of
  G(Chest)⁻¹·G(Head). Cached on the skeleton; rows retargeted lazily later
  reuse it.
- In the frame loop, before deltas are consumed:
  G′(Head) = [G(Chest) · offset⁻¹ · G(Chest)⁻¹] · G(Head) — the stance's
  head-vs-chest becomes the king-bank value (identity) while every frame's
  variation around the constant is preserved.
- Threshold 20°: king (0.0°) and bosconovitch (16.2°) keep their data exactly.
  't7:' skeletons exempt (above).
- One rejected design, recorded: pooling stance+walk+block+crouch-hold for
  the estimate measured a phantom 24.4° for king (his crouch-hold tucks the
  head 54°, his block 30° — real acting) and the correction then MOVED
  Pantera's verified head. The stance clip alone is the reference pose; it
  reproduces the census constants exactly (jin 90.9, heihachi 114.6, ogre 37.5).

## Verification

- Harness (real retarget in Node, shipped GLBs): kinpo/zui/demonio stance
  head world-delta went from yaw +86…87°, pitch −33° to yaw +6.0°, pitch
  +16.0° (aligned with the chest's own delta); pantera/yukihyo unchanged.
- New CI test `test/head-frame-normalization.test.mjs` (5 tests): kinpo and
  zui stance head yaw within tolerance + no scale tracks + head world scale
  == 1.0; kinpo/zui move-row heads stay on the opponent; yukihyo's king bank
  is NOT normalized (its real 3.4° offset reproduced, not zeroed).
- Chatur regression suite stays 8/8 with the fix (ogre bank corrected 37.5°,
  her gate geometry still passes).
- Before/after captures in this folder (serve-harness, opponent-side front
  view, textured, posed — no T-poses): kinpo stance + heavy, zui stance,
  dio stance (profile → facing the opponent in every fixed frame);
  yukihyo stance pair is identical across engines, as a clean bank should be.

## Honest leftovers

- The weight-bleed stretch component (above) needs the model-side
  weight-transfer pipeline; it is measured and scoped here, not fixed here.
- A separate, older composition mismatch stands as previously documented:
  canonical 22-bone action clips are composed down the 18-joint skeletons, so
  Spine/Neck source tracks don't reach G. This fix is defined in the engine's
  own composition frame and corrects heads under that composition; it does
  not re-architect the composition.
- Dio's rest orientation in his GLB is an axis-permuted outlier (120° class)
  handled by the existing model-facing path; his bank twist (heihachi
  114.6°) is fixed by this change and his stance capture is in this folder.
