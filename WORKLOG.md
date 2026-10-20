# WORKLOG — DEATHFANG build (2026-10-19/20, branch feat/deathfang-yamazaki-20261019)

Owner orders 2026-10-19 ~20:06–20:12 CDT: build DEATHFANG (all caps, one word) —
proprietary character based on Iori Yagami; keeps Iori's moves/stance/animations;
reskin as prisoner/slave to his own grief, chained/shackled, emo, Soul Eater
"NO FUTURE" face tattoo; transforms into a chained prisoner werewolf
(Free, Soul Eater, folds in). Werewolf GLB lands in a follow-up PR; base form +
moveset merged first.

## Lane 1 — moveset + wiring (done)
- `game/assets/movesets/deathfang.json`: 24 moves — Iori's full kit (10 T3-proxy
  base moves + Yami Barai + Maiden Masher from iori.json, renamed) + Oniyaki,
  Kototsuki In, Aoi Hana rekka ×3, Dokugami, Tsumagushi, Ya Otome super,
  2 throws, werewolf transform, NO FUTURE signature. Tekken inputs throughout.
- `game/js/assets.js`: `deathfang` + reserved `deathfang-werewolf` keys.
- `game/js/roster-full.js`: DEATHFANG entry (surge: NO FUTURE).
- `game/js/movesets.js`: `deathfang` added to MOVESET_IDS.
- JS syntax-checked with node --check.

## Lane 2 — attire 1 GLB (done, own-eyes rendered)
Method: SURGICAL GLB edit (no Blender re-export — the Sketchfab model's custom
Diffuse/Glossy/Emission node tree does not survive a Principled-only export).
1. `roster/deathfang/tools/df_texture_reskin.py` (Blender 4.0.2 headless):
   UV-category masks by dominant skin weight (hair red→emo black incl. a
   crimson-color catch, pants→charcoal, jacket/shirt deepened, skin paled);
   NO FUTURE tattoo drawn on the face region of the texture.
2. `roster/deathfang/tools/df_chains.py` (system python): iron chain geometry
   (torus links) built in glTF space — accessor space == joint world space,
   measured: dominant-weight vert centroids ≈ joint origins. Wrist shackles +
   5-link dangling chains, ankle shackles + 5-link inter-ankle chain, neck
   collar + 3 hanging links, 2 chest cross chains.
3. `roster/deathfang/tools/df_merge.py` (pygltflib, append-only): original
   blob untouched; reskinned texture swapped in via images[0]; 8 skinned
   chain meshes appended (JOINTS_0 100% to anchor bone; inter-ankle chain
   whole-link-per-foot), DEATHFANG_IRON material (metallic 0.9), nodes added
   under Object_10. All 59 animations + skeleton preserved byte-for-byte.
Renders (textured, own-eyes viewed): `docs/tpose-refs/deathfang/a1_front.png`,
`a1_back.png`, `a1_face.png`. Cycles CPU under xvfb (Eevee lacks libEGL on VM).

Known follow-ups: werewolf transform GLB (attire 2), tattoo legibility pass
(face is mostly hair-covered in Iori's style — tattoo sits on the forehead
band), in-game stance test of the inter-ankle chain under wide stances.

---

## 2026-10-20 — Pantera GLB repair (Idle clip + skin joints + seams)

Lane: fix/pantera-idle-clip-20261020. Tool: tools/auto_rig/repair_pantera_glb.py
(reproducible; run from tools/auto_rig). Gate: tools/auto_rig/anim_check.py.

Diagnosis (all measured, not eyeballed):
1. Idle clip Hips translations orbit a mean 8.21 m from bind — an
   exporter's scene placement baked into the clip (smooth periodic bob,
   key0 == key47, just centered in the wrong place).
2. JOINTS_0 in 8 prims (arms, boots1-3, fingers, gloveparts, pants,
   thighs) referenced L/R-mirrored joints — under any non-bind pose the
   geometry followed the opposite side's bones (the "gyro arms" knot).
   The repo already had the audited correction in pantera_fixed.glb
   (docs/qa/anim/pantera_skin_lr_fix_before_after.jpg) but the game
   wires pantera.glb (game/js/assets.js MODEL_URLS).
3. Hard 100%/100% skin seams (pants crotch L/R UpLeg, chest logo
   Spine/Spine2) tore under the Idle stance: edge-stretch p99.9 11.27.

Fixes applied to game/assets/models/pantera.glb (in place, 14 accessors,
JSON untouched, file size unchanged):
1. Idle Hips keys re-centered on bind (v' = bind + (v - mean)); the
   authored bob (max |v-bind| 0.63 m) is preserved.
2. 8 JOINTS_0 accessors transplanted byte-for-byte from pantera_fixed.glb.
3. Seam weights iteratively averaged across edges with ratio > 2.0
   (7 rounds; prims 4/13/14/17; capped at 4 influences, renormalized).

Gate after repair: ALL CLIPS PASS — Idle root dev 0.63 m (was 8.21),
edge p99.9 1.88 (gate 2.5), edge max 2.00, tearing max 0.085 m.
Run/Walk remain 2-keyframe rest-pose stubs by design: real locomotion
is the runtime Tekken 3 bank layer (game/js/t3anims.js); baking wh-anim
data into the GLB is a separate change owned by the motion-bake lane.

Same disease, NOT fixed here (flagged): steve-fox.glb (16 fighters share
it) and pantera_fixed.glb itself carry the identical broken Idle
(root 8.21 m; edge 5.82 / 6.20) — they need the same root re-center
(+ seam blend for pantera_fixed). Pre-existing cosmetic defect also
flagged: belt2/buckles prims are authored displaced at neck height
across the whole pantera model family; renders confirm they float at
the shoulders in the shipped model. Not repositioned — no source of
truth for their intended placement (see docs/RULES_NO_GUESSING.md).
