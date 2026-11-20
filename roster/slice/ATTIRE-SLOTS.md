# SLICE — Attire Slots

_SLICE = Dragunov's body and kit, per owner canon (2026-10-13, `roster/bonus/BONUS-CHARACTERS.md`):_
_the maniacal secret agent, the third blade — Phantom is the supernatural blade, Scimitar the scheming_
_desert blade, Slice the unhinged surgical blade. He slices enemies with blade-like chops and strikes;_
_usually wears a skull mask to hide his identity and scars; sometimes his face is seen._

| Slot | Name | Status | Model |
|---|---|---|---|
| **Attire 1 (default)** | Skull Mask — Owner Tripo | ✅ WIRED 2026-10-21 | `attires/attire1/model.glb` |
| **Attire 2** | T7 Default — Beret (our Dragunov build) | ✅ WIRED 2026-10-21 (PR #433; was Attire 1, laddered back) | `attires/attire2/model.glb` |
| Attire 3+ | — | ⏳ reserved | Owner will make more Slice attires himself; future Tripo links land here per Tripo law, never as a gate (NO-GATE LAW) |

## Attire 1 — Skull Mask (OWNER TRIPO, MAIN DEFAULT)

Owner, 2026-10-21 ~08:42 CDT (verbatim): _"there is slice attire one where he has arm
blades coming out of his arms that are like jagged and chrome like he's a fucking baraka
wolverine prototype motherfucker mix he has the skull mask on his head and it looks like
it's blending into his head on the back and he has scars all over his body and he has
equipped blades on his belt buckle and on the side of his shoe and I'm going to make more
tires for him and then you can keep making your version of slice but this is his main
default attire one"_

- **Source**: owner's Tripo — "undead warrior 3d model" by tzflo312,
  https://studio.tripo3d.ai/3d-model/cf9cf660-1673-4585-ac1b-ce4fc92f1550 — pulled
  2026-10-21 via `tools/tripo-pull` (public API, no sign-in) and archived on release
  `slice-tripo-pulls-20261021` (asset size + sha256 digest verified against the pull).
- **File**: `attires/attire1/model.glb` — 18,884,292 B,
  sha256 `6cddd2c9697aead7abb4a7c61dd36e9f003bafad14fd9fd6d0e49ff851074337`.
  glTF 2.0 (gltfpack 1.2), EXT_meshopt_compression + KHR_mesh_quantization,
  1 mesh / 1 material / 3 embedded PBR textures. **Static — no skin, no joints**
  (typical Tripo); rig comes at the rig stage like the other Tripo mains
  (see `RIG-NOTES.md`).
- **Wiring**: `MODEL_URLS` keys `slice` + `slice-attire1` → this file (both the
  player/select path and the enemy/raw path resolve here); `ATTIRE_VARIANTS['slice']`
  lists it first as the default; guard OWNERSHIP `slice: own [slice, slice-attire1, slice-attire2]`.
- **Render**: `docs/tpose-refs/slice/a1_front.png` + `a1_back.png` (2048px,
  own-eyes verified — the back view shows the skull mask blending into the back
  of his head, per the owner's description).

## Attire 2 — T7 Default, Beret (OUR DRAGUNOV BUILD)

The owner on this build (2026-10-21): _"you can keep making your version of slice"_ —
it stays fully wired and selectable as Attire 2. It was Attire 1 from PR #433 until
the owner's Tripo landed the same day; the move was byte-identical (sha256 verified
before and after: `af51f6473e7764ac6f832d19a3e6a38ef89f924e3a1511f43c3b7531a01d94b0`).

- **Source**: Tekken 7 Dragunov teardown model — `dragunov-t7-rig.blend` from release
  `tekken-models-batch-2` (this repo), 73,766,856 B, Blender 2.93,
  sha256 `214dc98fcc364245cd75dc52b3538d463c21ed28e45b907c78803feb714e5efd`.
  Full Tekken 7 default costume: beret, military greatcoat with eagle embroidery, shirt, tie,
  gloves, trousers, shoes, plus face/eyes/teeth detail meshes — 17 meshes on the original
  Tekken 7 game skeleton (`SK_CH_dra_bdu_1P`, 198 joints in the exported GLB).
- **Conversion notes**: the source file's costume color is shader-side in Tekken 7 — the `_D`
  textures are grayscale luminance and the color lives in material tints selected by the `_M`
  mask maps (jacket: slate blue with gold design work and brass buttons, per the source file's
  own `MustardUI` color constants). The shipped GLB's diffuse maps are a texel-exact evaluation
  of the source files' own material node graphs (mask channels → tint selection → color-dodge
  over the luminance map, computed in linear space) — no recoloring, no invented color — paired
  with the source `_N` normal maps. (A Cycles diffuse bake of the same trees was attempted
  first and was repeatedly OOM-killed on the shared box; the graph evaluation is the same math
  the bake performs for the diffuse pass.) The 509-bone control rig in the source file is not
  in the GLB; the meshes bind the Tekken 7 game skeleton.
- **Render**: `docs/tpose-refs/slice/a2_front.png` + `a2_back.png` (2048px T-pose,
  own-eyes verified: slate-blue greatcoat, gold eagles, textured throughout, no clay).
- **Scale note** (from PR #433): GLB bounding box is 2.02 m in the rip's native
  units — kept at porter scale rather than rescaling on a guess; flagged for the
  rig/scale pass.

## Skull mask — canon status

Slice's canon look includes a **skull mask** (hides his identity and scars). As of
2026-10-21 the mask is **present in his default look**: the owner's own Tripo
(Attire 1) models it on, blending into the back of his head. The older named gap —
no skull-mask *part* in our Tekken teardown holdings (in T7 the mask is a separate
generic customization item, and no Dragunov customization parts exist in the
holdings) — still stands as a **Creation Suite piece goal**: when a T7 generic
customization skull-mask part is torn down, it becomes a placeable piece for the
Attire 2 Dragunov build and other characters. It is no longer a gap in Slice's
default appearance.
