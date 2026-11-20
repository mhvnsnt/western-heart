# MINI house49 wire-up + Star textures (2026-10-21)

Follow-up to PR #481 (the HOUSE-49 re-template). Owner directives: wire the
re-templated models into the game, and the 2026-10-21 ~20:42 CDT texture law —
"if a source model has textures, the shipped model carries them baked in."

## Wiring (`game/js/assets.js`)

- **Star**: `star` now resolves to `assets/models/star-house49.glb` (was
  `star.glb`). Original `star.glb` stays in place, untouched, as the fallback.
- **Diablo**: NO CHANGE, by evidence. The `diablo` / `diablo-attire1` keys
  already resolve to `roster/diablo/attires/attire1/model-rigged.glb` — the
  canon Tripo Attire 1 rigged by Lane 4 rig batch 2 (commit 19ce8349) onto a
  53-joint HOUSE-named skeleton (Hips/Spine/Spine1/Spine2/...), textured
  (3 images). The file `diablo-house49.glb` was re-templated from,
  `game/assets/models/diablo.glb` (the MINI-32 Heihachi conversion), is loaded
  by no key — it is the ladder-back conversion, and repointing the default to
  it would replace the Tripo original with the conversion (against the
  Tripo-first ladder law). `diablo-house49.glb` stays on main beside its
  original for any future ladder-back wiring.
- **Michiko / Torch**: not touched by this lane — dedicated Tripo wire-in
  lanes own their slots (owner sent Michiko A1/A2 and Torch A1 Tripo
  originals on 2026-10-21). Their `-house49` files stay in place as fallbacks.

## Star textures — restored from her own source archive

The shipped `star.glb` is a GTA San Andreas DFF port of TTT2 Christie 2P
(fighter-hunt log, docs/fighter-hunt/HUNT-LOG.md). It shipped untextured
because the DragonFF TXD import was too heavy for the VM at hunt time; her
authored textures (33) sat in the TXD inside `christie-monteiro-2p.7z` on
release `tekken-models-batch-3`. The Tripo attires (roster/star) are a
different mesh and cannot texture this one — verified by vertex/UV
fingerprint (shipped mesh: 14,506 verts; Tripo mesh: ~1M verts).

Method (pure data surgery on `star-house49.glb`; no rig/geometry change):

1. TXD extracted with a purpose-written DXT1/DXT3 decoder — all 31 model
   textures to PNG. Decode verified by eye (face, jacket).
2. DFF parsed directly: 35 materials with texture names; the binmesh plugin
   is the authoritative per-triangle material partition (23,107 triangles).
3. Shipped `star.glb` matched to the DFF: frame transform (x, z, −y), no UV
   flip. **14,506 / 14,506 vertices matched** (position exact, UV < 1e-3
   after position-tie break by UV). **23,086 / 23,086 triangles assigned a
   material** — 22,622 by exact vertex triple, 464 by centroid
   (max distance 1.9e-06).
4. `star-house49.glb`'s index + UV buffers asserted byte-identical to the
   shipped `star.glb` (the re-template preserved order), then its single
   primitive was split into one primitive per material and the TXD PNGs
   embedded as `baseColorTexture` (30 images / 35 materials; REPEAT wrap —
   her UVs tile well outside 0..1). Positions, normals, joints, weights,
   skins, nodes: untouched (the build only appends to the binary chunk).
5. Alpha, per measured texture alpha: cutout cards (eyelashes, eyebrows,
   hair, hair2) = `MASK` cutoff 0.5; face overlays authored to blend in the
   source game (lips, eyesA, eye shading, tear duct) = `BLEND`; everything
   else opaque.

Result: `star-house49.glb` 906,224 B → 4,550,552 B, images 0 → 30,
joints 53 (unchanged). Proof: `star-textured-front.png` in this folder —
software-rasterizer render of the actual shipped file's data in bind pose
(front; a back view was also rendered and checked): the Christie 2P outfit
reads on every part — jacket flame pattern, face, hair, gloves, strappy
bottom, ribbons, sandals — feet on the floor line, body intact.

## Playtest (this branch's build, headless Chromium, versus mode)

Served tree = main tree + this branch's `game/js` + this branch's model
files; driven menu → select → stage → fight with inputs, per fighter:

- STAR (textured house49, full UI path menu → select → stage → fight, two
  controlled runs): PASS. Fight samples: root y = 0; Head world y 1.569 →
  1.526 (stance animating); LeftFoot world y 0.047 → 0.082 — feet on the
  floor, body intact, facing her opponent. 0 page errors in both runs.
  Canvas capture at fight+6s shows her textured, planted, mid-stance
  (pink jacket / white bottom / sandals read under stage lighting).
  The PRISTINE (untextured, on-main) house49 file was run through the same
  probe as an isolation control: also PASS (identical head/foot heights),
  so the wiring premise itself is sound in-game, not just the data checks
  from PR #481. (One earlier uncontrolled duplicate run reported her sunk
  ~3.1 m under the floor; it raced this lane's serve-tree assembly and the
  result did not reproduce in either controlled run — the sunk-fighter
  symptom is also on the owner's pre-existing triage list for the live
  build with the original models.)
- DIABLO (current main wiring, model-rigged.glb — untouched by this lane):
  NOT VERIFIED IN-FIGHT ON THIS BOX — environment-blocked, recorded
  honestly rather than passed over. Four attempts: two through the full
  select-screen UI (renderer crashed while the select screen held ~60 live
  previews including his 989,472-vert model) and two through the game's own
  ModeController training entry (model downloads completed — progress hint
  reached "18.6/18.6 MB" — then the SwiftShader renderer crashed during
  fight setup). Zero JS page errors preceded every crash; lighter fighters
  (14.5k-vert Star included) complete the identical flow on the same box.
  The file itself is structurally sound (53-joint HOUSE-named skeleton,
  textured, validated by inspection), and no wiring change was made to
  him, so there is nothing to roll back. Flag for the team: a ~1M-vert
  skinned model is a mobile-performance risk in its own right, independent
  of this lane — worth a decimation pass before the native build.
