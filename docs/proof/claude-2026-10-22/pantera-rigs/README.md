# Pantera A1 / A2 rigs, and two main-branch breakages (2026-10-22, Claude session)

Owner, on Leopard King (A2): "once you get down to the forearm and the hands it starts to stretch and has weight
issues ... the legs are all crumpled up ... the right leg is in the opposite direction of the left leg the hand
looks weighted to the tail and the same thing for A1 if you can fix all of that".

## A1 Leo man: turned around by the game (FIXED here)

`pantera-leoman` had no entry in `game/assets/models/model-facing.json`, so the game fell back to its feet cue.
His tail hangs to the floor behind his feet, so the cue read "facing −Z" and the game turned him 180° at load.
His limbs then followed the T3 King data in world space while his body faced the other way. That is the
crumpled, backwards-bending legs and the back of the mane toward the opponent.

- Fix: `"pantera-leoman": "+Z"`, verified on the raw rest render (the face is visible from +Z, same file
  as the king bank's source rig).
- `leoman_rest_stance_before_after.png`: top = the game's rest pose, before (back to camera) and after (face to
  camera); bottom = the T3 stance in-game, before and after. After the fix, his foot yaw equals the decoded
  source on every check (`footYaw` src = tgt: L −5.9°, R −56°).

## A2 Leopard King: skeleton outside the body (FIXED: re-rig wired as `model-refit.glb`)

`tools/model-audit/rig_qa.py` on the shipped `model-rigged.glb` (see `rig_qa.json`):
- arm and leg sides SWAPPED;
- knees BACKWARD;
- 26,512 vertices weighted to bones far from them (Spine → forearm 10,370; Spine → upper arm 5,434;
  leg → tail 3,746).

`leopard_king_bind_overlay_shipped.png` shows why: the whole skeleton sits about 0.25 m behind the body. The
spine runs along the back surface, the toes point backwards and the tail chain runs outside the tail.
`leopard_king_stance_shipped.png` is the in-game result: the tail is a stretched slab and the limbs smear.

`leopard_king_bind_overlay_refit.png` is the re-rig made with the new tools below. King's 49-joint skeleton
is centred in the mesh's own cross-sections, Left* sits on the character's left, toes run along the sole, and
the tail chain follows the tail's medial curve. It is skinned by Blender bone heat. rig_qa on it: sides ok,
knees forward, weight bleed 1,010 (all at the hips).

**Wired after the in-game check** (`'pantera-leopard-king'` → `roster/pantera/attires/leopard-king/model-refit.glb`,
32,679,076 B meshopt, sha256 `20695690affccdc4…`; the 2026-10-21 `model-rigged.glb` stays beside it). Also
`"pantera-leopard-king": "+Z"` in model-facing.json, because his tail fooled the feet cue the same way Leo man's did.
- `leopard_king_refit_rest_and_stance_before_after.png`: left = the game's rest pose (+Z and +X cameras, facing
  forward); middle = the shipped rig in the T3 King stance; right = the re-rig in the same stance. Bone
  directions match the decoded source within 0.4 deg, and the feet match exactly (L -6.0 / R -56.1 vs -5.9 / -56).
- `leopard_king_refit_attacks.png`: the re-rig mid-attack, front and side, at 35% and 60% of King rows 44 (1),
  203 (2), 54 (3), 216 (4), 220, 117, 127 (1+3 throw), 82 and 290 — no tearing or limb stretch. Row 220 (wired
  as `2,1`) is upside down in the decoded SOURCE too (head 0.64 m below the hips): that is a move-to-row
  mapping problem in the moveset, not the rig. It is being chased in the inputs/moveset work.

## Main-branch breakages found by `game/tests/*.test.mjs` (FIXED here)

- **Zen could not load.** `3942b8584` ("Lane 4 rig batch 1") deleted his whole `MODEL_URLS` block (`zen`,
  `zen-attire1`, `zen-spirit`, `zen-tentacle`, `zen-oversoul`) in `game/js/assets.js`. The block is restored
  verbatim from `e09288722` + `292ca2b17`. In a smoke fight (Zen vs Tou), Zen loads `zen-attire1` again. That
  Tripo spirit body is an unrigged static, so it is queued for the auto-rig pass.
- **The souls riding Pantera's body** (TOU, KAI, RETSU, GYOU) loaded Leo man after Pantera's Tripo-first
  reorder. `attiresFor()` now skips a model-keyed ladder when that model is another fighter's own body.
  Resolution is unchanged for every other fighter (checked across FULL_ROSTER).
- Results: `model-key-guard` 3/3 (main: 1/3) and `fighter-completeness` 4/4 (main: 3/4).

## New tools

- `tools/model-audit/rig_qa.py`: structural rig check (facing from the feet; sides per arm/leg chain; knee
  direction; weight bleed by bone pair).
- `tools/model-audit/rig_overlay.py`: bind-pose overlay with the mesh coloured by its weight map, the
  skeleton on top, and Left joints red / Right joints blue; `--fit` draws a refit in green.
- `tools/proof-harness/rig_sheet.mjs` + `tools/model-audit/tile_sheet.py`: the in-game rest render and T3
  stance for every `MODEL_URLS` key, plus the game's facing decision, tiled into labelled sheets.
- `tools/auto_rig/refit_skeleton.py` (numpy) + `tools/auto_rig/backends/heat_rebind.py` (Blender): fit a
  canonical skeleton inside a mesh from the mesh's own cross-sections, then skin it with bone heat.
- `tools/auto_rig/backends/gamerig_backend.py` `heat_via_proxy`: the proxy is cleaned before the heat solve
  (merge by distance; drop islands under 1%). A few duplicate vertices plus 3–5 vertex specks had made Blender's
  solve fail for every vertex (Leopard King: 24,006/24,006 unweighted → 0). This was also the failure on two
  Doc Frank statics.
- `game/poselab.html`: `footYaw()` (per-foot yaw vs hips, source and target), and `rest()` now returns
  the game's facing.
- `tools/proof-harness/fight.mjs`: `ATTIRES` env picks attires the way the select screen saves them.
