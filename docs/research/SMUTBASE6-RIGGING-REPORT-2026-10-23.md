# SmutBase 6 — Rigging Track Report (2026-10-23)

Rigging assessment + auto-rig execution for the 6 SmutBase fighters.
Track: rigging. Related tracks (moveset/texture) run in parallel — no file conflicts
(this track only adds `model-rigged.glb` beside existing files).

## 1. Input assessment (all 6 models)

Parsed every GLB's JSON chunk directly (range reads for the 630 MB file — no full downloads).

| # | Model | Size | Meshes | Skins | Joints | Weighted prims | Source |
|---|-------|------|--------|-------|--------|----------------|--------|
| 1 | `roster/mina-ashido/attires/attire1/model.glb` | 4.4 MB | 8 | 0 | 0 | 0/62 | blend17-extract route |
| 2 | `roster/miruko/attires/attire1/model.glb` | 5.6 MB | 11 | 0 | 0 | 0/537 | blend17-extract route |
| 3 | `roster/rahkasa/attires/attire1/model.glb` | 3.7 MB | 1 | 0 | 0 | 0/938 | blend17-extract route |
| 4 | `roster/tsuyu-asui/attires/attire1/model.glb` | 5.8 MB | 9 | 0 | 0 | 0/157 | blend17-extract route |
| 5 | `~/workspace/smutbase-work/parvati-full.glb` | 183 MB | 25 | 0 | 0 | 0/71 | Blender 4.0 export |
| 6 | `~/workspace/smutbase-work/vixen-full.glb` | 630 MB | 29 | 0 | 0 | 0/72 | Blender 4.0 export |

**All 6 arrived with NO armature and NO skin weights.** The 4 extractor outputs are
mesh-only (the BLENDER17-01 extractor dumps meshes, not rigs). Parvati/Vixen's
`.blend` sources have GZM rigs, but the GLB exports dropped the armature
(Vixen's export kept 31 `GZM_*` viewport gizmos — not bones).

Two pre-existing data quirks found and handled:
- **Z-up coordinates.** The 4 extractor GLBs contain raw Blender Z-up coordinates
  (characters lying flat, height along Z). Verified by orthographic projection:
  T-pose clearly visible in the XZ plane. Fixed with a Z-up→Y-up pre-rotation
  `(x,y,z)→(x,z,−y)` before the pipeline.
- **Facing.** Nose-protrusion test on the body mesh: all 4 extractor models +
  Vixen face **−Z** (canonical, same as the in-game `pantera.glb` reference).
  Parvati was ambiguous (long hair); verified visually after rigging.

## 2. Game skeleton compatibility

The task brief said "Tekken-derived 53-joint skeleton". The repo's actual canonical
skeleton is **`tools/auto_rig/backends/skeleton_template.json`: 52 joints,
Mixamo-style, T-pose, 1.8 m reference height, faces −Z.** `game/js/fighter.js`
drives `bones.Hips / Spine1 / Spine2 / Head / LeftHand / RightHand / LeftFoot /
RightFoot`, and `game/js/assets.js` documents the canonical Mixamo rig
(`pantera.glb`) as what the T3 animation banks were baked against.
`this.lean.rotation.y = this.facing * Math.PI/2` assumes every model rests facing −Z —
so all outputs were built facing −Z.

None of the 6 inputs matched (no skeleton at all) → all 6 needed **full auto-rig**,
not retargeting or weight fixes.

## 3. Fix executed

Repo-standard pipeline (`tools/auto_rig`, `blender-heat` backend — the PR #264-proven
CPU path), plus two small pre/post steps of mine:
1. `zup_to_yup.py` — Z-up→Y-up conversion (extractor models only; bakes node transforms).
2. `reorder_meshes.py` — largest mesh first (pre-rig, so normalize sees the body;
   post-rig, because Blender's exporter alphabetizes meshes and `validate.py`'s
   height probe reads `meshes[0].primitives[0]`).
3. `normalize.py` — feet to y=0, uniform scale to 1.8 m.
4. `blender_heat.py` — build canonical 52-bone skeleton + heat-diffusion weights, ≤4 influences.
5. `validate.py` — the playable gate.
6. `render_poses.py` — front/back/side proof renders, **viewed by eye**.

Parvati/Vixen needed an extra step: at 183/630 MB they exceed GitHub's 100 MB
file limit (and the intake READMEs already note large staged bytes stay out of the
repo). Both are dense Genesis-8 sculpts with **zero textures** (all geometry), so
they were decimated in Blender (shape keys cleared — game builds don't use morphs;
full-res originals preserved in `~/workspace/smutbase-work/`):
- Parvati: 1,154,840 → 344,523 tris, 183 MB → **30.8 MB rigged**.
  Floating spare sandal pair (`Heels 3` / `temp` mesh — 16.5k verts hovering
  detached beside her feet in the source) removed from the game-ready file;
  full-res original in `~/workspace/smutbase-work/` keeps it.
- Vixen: 630 MB → decimated to ~10 MB input → **14.7 MB rigged**

## 4. Results

| Fighter | Output | Gate | Height | Notes |
|---------|--------|------|--------|-------|
| mina-ashido | `model-rigged.glb` (12 MB) | **PASS** | 1.625 m | clean T-pose, all 8 meshes weighted |
| miruko | `model-rigged.glb` (14.7 MB) | probe FAIL* | body 1.551 m | *see note — true body height in 1.5–2.2 m range |
| rahkasa | `model-rigged.glb` (9.8 MB) | **PASS** | 1.503 m | 4 arms rigged cleanly (single mesh) |
| tsuyu-asui | `model-rigged.glb` (16.4 MB) | **PASS** | 1.662 m | |
| parvati | `model-rigged.glb` (30.8 MB) | probe FAIL* | full body 1.80 m, feet y=0 | *hair mesh is meshes[0]; floating spare sandals removed, body correct |
| vixen | `model-rigged.glb` (14.7 MB) | probe FAIL* | full body 1.80 m, feet y=0 | *hair mesh is meshes[0]; body correct |

All outputs: 1 skin, 52/52 canonical joints, 0 missing bones, finger symmetry OK,
every primitive weighted, valid glTF 2.0.

\* **Probe limitation, not a model defect.** `validate.py`'s height probe reads only
`meshes[0].primitives[0]`. Miruko's body mesh has 2 primitives (bulk 0–1.368 m +
head 1.33–1.554 m); the full body is 1.551 m — inside the gate's 1.5–2.2 m intent.
Parvati's densest mesh is hair (`RenderStrandHairGeom`), which sorts first. The
models are correct; the probe heuristic under-reads multi-primitive / hair-dense
models (the same caveat `auto_rig.py` already documents for multi-part GLBs).

## 5. Proof

Pose renders (front/back/side, T-pose) viewed for all 6:
mina, miruko, rahkasa, tsuyu, parvati, vixen — standing clean, no tearing, no
detached parts, ears/hair/horns follow the head. Parvati's floating spare
sandals removed (see §3); re-rendered clean. Proof PNGs kept at
`~/workspace/proofs/` (per-model dirs).

Note: `render_poses.py`'s "front"/"back" labels are swapped relative to glTF
convention for −Z-facing models (its "front" camera shows the model's back).
Cosmetic tool quirk only — rigs verified against the −Z-facing `pantera.glb`
reference by direct vertex measurement.

## 6. Files committed (this PR)

- `roster/mina-ashido/attires/attire1/model-rigged.glb`
- `roster/miruko/attires/attire1/model-rigged.glb`
- `roster/rahkasa/attires/attire1/model-rigged.glb`
- `roster/tsuyu-asui/attires/attire1/model-rigged.glb`
- `roster/parvati/attires/attire1/model-rigged.glb` (new attire1 dir)
- `roster/vixen/attires/attire1/model-rigged.glb` (new attire1 dir)
- this report: `docs/research/SMUTBASE6-RIGGING-REPORT-2026-10-23.md`

Originals untouched (`model.glb` files never modified — new files only, per the
`model-rigged.glb` convention from the awa-pop batchrig).

## 7. Follow-ups (not this track)

- **Wiring into the game** (`game/js/assets.js` MODEL_URLS): needs the asset/move
  track's decision on model keys. Suggested wire lines follow the awa-pop pattern:
  `'<model-key>': '../roster/<fighter>/attires/attire1/model-rigged.glb'`.
- **Vixen moveset**: per her intake README, she needs a full Tekken-notation
  moveset rebuild (not Injustice 2 inputs) — moveset track.
- **anim_check with standard clips**: stretch gate is "unknown (no clips supplied)"
  for all 6; run `anim_check.py` against the 6 standard clips before wiring.
- **Miruko/Parvati probe**: consider a `validate.py` improvement (measure full
  meshes[0] or all meshes) — shared tooling, separate PR.
- **Full-res archives**: parvati/vixen full-res rigged versions exceed repo limits;
  if the owner wants them, they belong on Releases/external storage per the game
  ownership rule.
