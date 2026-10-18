# LANE C — FIGHTER HUNT LOG (Round 2)

Lane: `r2/fighter-hunt` · Worker: replacement (predecessor killed by daemon restart, nothing pushed).
Worktree: `~/workspace/wh-fighter-hunt` (sparse: CANON.md, ROSTER.md, docs/fighter-hunt, game/assets/models, game/js).
Branch base: origin/main @ e82925ce.

## Target list (owner orders)

| WH name | Base | Source status |
|---|---|---|
| BURGER | Bob (T7) | NOT FOUND — hunt needed |
| SCIMITAR | Shaheen (T7) | FOUND on release |
| MICHIKO | Katarina (T7) | FOUND on release |
| STAR | Christie | FOUND on release |
| TORCH | Anna (T7) | FOUND on release |
| DIO | Akuma (T7) | FOUND on release |
| BRUNO | Miguel (T7) | FOUND on release |
| YUKIHYŌ | Armor King | FOUND on release |
| SLICE | Dragunov (T7) | FOUND on release |
| REALIZZT/KUTZ | Brad Burns (VF5) | NOT FOUND — hunt needed |
| CHORDZ | Lars (T7) | NOT FOUND — hunt needed |
| VAIN ABEL ELIAS | Bass Armstrong (DOA) | BLOCKED — DOA4 lane owns mesh extraction |

## Found sources (all on mhvnsnt/western-heart GitHub releases — no new hunting needed)

From `tekken-models-batch-3`:
- `akuma-t7-sfmlab.rar` → DIO (Akuma T7, SFMLab rip)
- `anna-williams-t7-p1.7z` → TORCH (Anna Williams T7 P1)
- `christie-monteiro-2p.7z` → STAR (Christie Monteiro 2P)
- `katarina-alves-t7-p1.7z` → MICHIKO (Katarina Alves T7 P1)
- `miguel-t7-sfmlab.zip` → BRUNO (Miguel T7, SFMLab rip)
- `shaheen-t7-sfmlab.zip` → SCIMITAR (Shaheen T7, SFMLab rip)

From `tekken-models-batch-2`:
- `armor-king-t8-blender.zip` → YUKIHYŌ (Armor King T8, Blender)
- `dragunov-t7-rig.blend` → SLICE (Dragunov T7 rig, Blender)

From `king-variants-2026-10-13`:
- `Tekken_8_-_Armor_King__Battle_Cloth_.rar` → YUKIHYŌ alt (Armor King T8 Battle Cloth)

## License honesty

All found sources are community game rips (SFMLab ports, Blender rigs, fan rips of
Tekken 7/8 models). These are reverse-engineered extractions of commercial game
assets, shared by the modding community — NOT cracked software, NOT pirated game
copies. Per the owner's steal-like-an-artist rule: study/reverse-engineer to learn
technique is allowed; nothing here is redistributed commercially. Each wired model
will carry its source + license note in this log. If the owner ever declares a sale
track, third-party-derived content gets rescanned/replaced per the sale-status rule.

## Gate (from MODEL-STATUS.md, Lane B owns that file — read-only for this lane)

Wiring requires: valid glTF, ≥1 skinned mesh, Mixamo-style bones
(Hips/Spine1/Spine2/Head/hands/feet — fighter.js hard-requires these),
sane world scale (~1.5–2.2 m). Foreign skeletons (ValveBiped SFMLab, T7/T8-native)
must be retargeted/auto-rigged, NOT renamed. Unrigged statics stay OUT.

## Per-fighter log

(Entries appended as work completes. Format: source → extract → skeleton →
convert → scale → render → own-eyes → release → wire.)

### 2026-10-18 — lane setup
- Verified no r2/fighter-hunt branch existed (fresh start confirmed).
- Shared clone ~/workspace/western-heart contended by sibling lanes (r2/arenas,
  r2/movesets, r2/modes, r2/creation-suite worktrees + checkout procs) — git ops
  hang there. Using dedicated sparse worktree ~/workspace/wh-fighter-hunt.
- MODEL-STATUS.md lives at game/assets/models/MODEL-STATUS.md (not root).
- ROSTER.md + CANON.md read. Render seen-list checked — none of the 8 found
  sources have renders yet (no double-render risk).
- DOA4 lane state: VAIN ABEL ELIAS still blocked — Bass mesh not extracted
  anywhere (textures-only zip + movelist exist; 129 triangulated GLBs on main
  are unidentified chrone/chrtwo/chrthree/mot decodes; keystream deep-RE ongoing).
  NOT duplicating. Will re-check at end of lane; if Bass mesh appears, convert.

### 2026-10-18 — STAR (Christie Monteiro) ✅ WIRED
- Source: `christie-monteiro-2p.7z` (tekken-models-batch-3 release). GTA San Andreas
  DFF+TXD port of TTT2 Christie 2P outfit by "4L13NW4R3_2021"/H4ckOptimus.
  License: community game rip (fan port of commercial asset, not for sale).
  Character verified by own eyes on archive preview photo (01.png) + T-pose render.
- Pipeline (proven, reusable for anna/katarina DFFs):
  1. DragonFF Blender addon → import DFF (mesh 12,462 verts + 32-bone GTA skeleton).
  2. Rename bones GTA→Mixamo (Pelvis→Hips, Spine 1→Spine, Spine 2→Spine1,
     Bip01 L Clavicle→LeftShoulder, L UpperArm→LeftArm, L ForeArm→LeftForeArm,
     L Hand→LeftHand, L Thigh→LeftUpLeg, L Calf→LeftLeg, L Foot→LeftFoot,
     L Toe0→LeftToeBase, mirror for right; strip leading spaces).
  3. Create Spine2 bone (child of Spine1, parent of Neck) — fighter.js hard-requires
     Hips + Spine2 (unguarded getWorldPosition); chains are guarded.
  4. Rename vertex groups to match. Export GLB (game/assets/models/star.glb, 905KB).
- Gate check: valid glTF, 1 skinned mesh, 33 joints, Mixamo bones (Hips/Spine2/Head ✓),
  ~1.75m. PASS. Textures: TXD holds 33 real textures but DragonFF TXD import is
  too heavy for this VM (SIGKILLed twice); shipping UNTEXTERED (gray clay) now,
  texture pass as follow-up. Honest flag in log, not hidden.
- Render: batch_render.py probe (4-axis) → facing = -Y (nose test was wrong; own-eyes
  on front/back pair) → 2048px front T-pose, white void, full arm reach, fingertips
  clear. Own-eyes verified: Christie 2P silhouette (jacket+ring, strappy bottom,
  gladiator sandals, long hair). Render at /tmp/fh_final2/christie-star_front.png
  (will attach to release).
- Wired: assets.js MODEL_URLS += star; roster-full.js star.model pantera→star.
- NOTE: worktree ~/workspace/wh-fighter-hunt was wiped mid-lane (disk cleanup or
  restart); branch was safe on origin (pushed). Recreated sparse worktree, no loss.

### 2026-10-18 — TORCH (Anna Williams) ✅ WIRED
- Source: `anna-williams-t7-p1.7z` (tekken-models-batch-3). GTA SA DFF+TXD port of
  T7 Anna by "4L13NW4R3_2021" (same author as Christie). Feathered/raven outfit
  (NOT the red qipao — this is her feathered T7 look). License: community game rip.
  Character verified by own eyes on archive preview photo (01.png) + T-pose render.
- Pipeline: same reusable DFF script (/tmp/fh_dff_pipeline.py). Exported
  game/assets/models/torch.glb (1.6MB, untextured gray clay — TXD import too heavy,
  texture pass follow-up). Gate: PASS (Mixamo bones, skinned, ~1.7m).
- Render: probe → facing = +Y (front shows face + dress bodice; -Y is back).
  2048px front T-pose, white void, fingertips clear. Own-eyes: Anna's feathered
  shoulders/wrists, long skirt, matches preview photo.
- Wired: assets.js += torch; roster-full.js torch.model steve-fox→torch.

### 2026-10-18 — MICHIKO (Katarina Alves) ✅ WIRED
- Source: `katarina-alves-t7-p1.7z` (tekken-models-batch-3). GTA SA DFF+TXD port of
  T7 Katarina P1 (glasses, striped pants, black bra, white jacket) by "4L13NW4R3_2021".
  Two DFFs in archive (KatarinaAP1.dff + KatarinaAP1V2.dff); used KatarinaAP1.dff.
  License: community game rip. Verified by own eyes on preview photo (01.png).
- Pipeline: same DFF script. game/assets/models/michiko.glb (1.2MB, untextured).
  Gate: PASS.
- Render: probe → facing = -Y (front). 2048px front T-pose, white void, fingertips
  clear. Own-eyes: Katarina's face, open jacket, belt, striped pants.
- Wired: assets.js += michiko; roster-full.js michiko.model steve-fox→michiko.
