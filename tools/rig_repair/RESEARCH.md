# Rig Auto-Fix Research — Production-Grade Stack Survey

Owner directive 2026-10-15: the rig pipeline becomes the UNIVERSAL standard across
every repo with 3D models. This document distills the deepest automatic
(proven, no hand-tooling) fixes from teardown data and open-source tooling,
ranked by: fully automatic, proven on game-rip meshes, measurable.

## 1. What the pipeline already is (baseline, on western-heart main)

`tools/rig_repair/` — 9 stages, every stage writes a versioned file, inputs never
touched (see `tools/rig_repair/README.md`):

| # | Stage | Method | Defect killed |
|---|-------|--------|---------------|
| 1 | detect | `rig_repair.py detect` | Unknown mesh/skin state → measured report |
| 2 | transfer | weight transfer from canonical skeleton | Unweighted / mislabeled meshes |
| 3 | refit | volume-mode skeleton refit (ray-cast joints to mesh volume center) | Skeleton outside mesh (the 5cm arm bug) |
| 4 | reskin | Surface-Heat-Diffuse-Skinning (MIT) or Blender bone heat, conditional | Missing/stale weights |
| 5 | separate | topology-based limb/body separation | Hands glued to legs, torso "wings" |
| 6 | armpit | de-bleed + contrast sharpen at transitions | Armpit→pec→bicep stretch |
| 7 | weldcap | recalc normals, HARD ASSERT zero open edges | Holes, ghost geometry |
| 8 | gate | p99.9 edge stretch vs 2.5, ground contact, hinge flips | Ships-or-not decision |
| 9 | proof | stress-pose clay renders, human eyes | The media proof standard |

Case-1 (provable from file): L/R joint swap — Pantera 5805/5805 mirrored verts →
0, arm stretch 11.95 → 2.11. Case-2 (in build: `transfer_weights.py`): authored
weight defects — cuffs on Spine, logo on Spine, pants on UpLegs-only.

## 2. Teardown-derived rules (how shipped fighting games do it)

From the western-heart teardown corpus (Tekken 7/3, WWF No Mercy, WrestleMania XIX,
Urban Reign) and the Tekken modding docs mirrored in `teardown/tekken7/`:

1. **4-influence hard cap, normalized.** UE4-era fighters skin with `ivec4`
   joint IDs + `vec4` weights per vertex, weights summing to 1. This is not a
   suggestion — it is the engine format. Pipeline rule: prune to top-4,
   renormalize, assert Σw=1 (|1−Σw| < 1e-5). (Already the pipeline's invariant.)
2. **Attachments bind to the nearest limb bone, never the spine.** Shipped
   characters' wristbands, belts, and chest emblems ride the limb/chest bones
   they sit on. A cuff weighted to Spine is not a "style" — it is a rip defect.
   Pipeline rule: any mesh whose verts sit >X from their dominant bone's segment
   gets flagged; case-2 transfer re-binds by proximity.
3. **Hips own the pelvis.** Pants/skirts blend Hips↔UpLeg across the hip joint;
   UpLegs-only weighting is never shipped. Pipeline rule: detect zero-Hips
   verts in the pelvis band, blend from torso/thigh.
4. **Validation is Range-of-Motion.** The pro standard (create3dcharacters,
   corroborated across rigging literature) is a ROM pass: every joint through
   its full range, ~1000 frames, watching for breakage. Our extreme-pose battery
   (arms overhead/crossed, deep crouch + wide stance, spine bend + twist,
   combined wrestler arch) is the automated, measurable form of this.

## 3. Open-source auto-fix tooling, ranked

### Tier 1 — use now (proven on game-rip meshes, fully automatic, scriptable)

1. **Blender Data Transfer / Transfer Weights** (built-in, GPL).
   Copies weights by nearest-vertex/projection from a correctly-weighted source.
   This IS the case-2 method (cuffs←arms, logo←torso, pants←torso/thigh).
   Verdict: the workhorse. Already chosen; keep as the default case-2 engine.
2. **Surface Heat Diffuse Skinning** (meshotline, MIT,
   `github.com/meshonline/Surface-Heat-Diffuse-Skinning`).
   Generates bone-heat-quality weights but never fails ("failed to find
   solution" is impossible). Scriptable: `bpy.ops.wm.surface_heat_diffuse()`,
   poll `bpy.context.scene.surface_job_finished`. Already wired as the reskin
   fallback. Verdict: keep; it is the safety net under every other method.
3. **cc_blender_tools — "Blend Body Weights"** (open).
   Blends clothing weights toward body-surface weights by distance — the exact
   pattern our case-2 transfer implements independently. Verdict: independent
   confirmation the approach is the industry pattern; no code needed.

### Tier 2 — port the detectors (automatic issue detection → new gate stages)

4. **SmartWeight** (GPL-3.0, Blender 4.2+).
   Automatic detectors worth porting as pipeline gate stages: candy-wrapper at
   parent/child joints, volume loss on deforming joints, weight leak across body
   regions, L/R asymmetry. Every threshold derives from rig size (works at any
   scale). Its fix operators (targeted fix per issue type, Laplacian smooth,
   auto-normalize to top-N) are the template for future auto-fix stages.
   Verdict: port the four detectors as `rigcheck/` stages; fixes stay in our
   transfer/refit engine.

### Tier 3 — watch, not yet (full re-rig, wrong problem)

5. **Neural auto-riggers** (RigNet SIGGRAPH 2020, Anymate Apache-2.0 2025,
   UniRig/SkinTokens/Puppeteer 2025–26). Full skeleton+weight prediction from
   scratch on CPU in minutes. Verdict: our models HAVE skeletons and clips;
   re-rigging from scratch would discard authored animation compatibility.
   Revisit only for unrigged intake (Tripo/AI-generated meshes).

## 4. The honest gap: the 2.5 gate

The pipeline team's own README calls 2.5 "aspirational for LBS without corrective
shapes" (Stick-Up v1: 27.7–44.7 → 10.7–15.1 after all 9 stages). Path to 2.5:

1. Case-2 transfer (in build) — kills the authored defects (cuffs/logo/pants).
2. SmartWeight-style detectors as gates — catches what transfer misses.
3. If a mesh still fails: surface-heat re-skin of that mesh only (never
   whole-model; full re-skin destroyed good weights in testing).
4. Last resort, still automatic: per-issue targeted operators (port from
   SmartWeight), never hand-painted.

No stage in this stack touches a weight by hand. Every fix is a program with a
before/after number.

## 5. Buildable pipeline stages (in priority order)

- [ ] `transfer_weights.py` — case-2 data-transfer (in build, Pantera-proven).
- [ ] Extreme-pose battery as `rigcheck/` gate (owner law 2026-10-15).
- [ ] Port SmartWeight's 4 detectors → `rigcheck/detect_*.py`.
- [ ] Per-mesh (not per-model) surface-heat re-skin fallback.
- [ ] 4-influence cap + Σw=1 assert as a hard gate (not just convention).
- [ ] ROM-battery proof renders wired into `proof.py`.

## Sources

- `tools/rig_repair/README.md` (western-heart main) — the 9-stage pipeline.
- `teardown/tekken7/tekkenmods-docs/` — UE4 ivec4/vec4 skinning format.
- Blender 4.1 Manual — Transfer Weights / Data Transfer.
- `github.com/meshonline/Surface-Heat-Diffuse-Skinning` (MIT).
- SmartWeight, Superhive (GPL-3.0) — detectors + fix operators.
- `github.com/yieryi/cc_blender_tools` — Blend Body Weights.
- `github.com/zeljkovranjes/auto-rigger` — neural rigger survey (RigNet,
  UniRig, Anymate Apache-2.0).
- create3dcharacters.com — ROM validation standard.
- `github.com/lebobo88/rlm-gaming` game-rigging SKILL.md — LBS/DQS + weight QC bar.
