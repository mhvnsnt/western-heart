# SLICE — Attire Slots

_SLICE = Dragunov's body and kit, per owner canon (2026-10-13, `roster/bonus/BONUS-CHARACTERS.md`):_
_the maniacal secret agent, the third blade — Phantom is the supernatural blade, Scimitar the scheming
desert blade, Slice the unhinged surgical blade. He slices enemies with blade-like chops and strikes;
usually wears a skull mask to hide his identity and scars; sometimes his face is seen._

Attire 1 is Slice's FIRST OWN MODEL — he was a `steve-fox` fallback rider with no model of his own
(model-key audit, PR #418).

| Slot | Name | Status | Model |
|---|---|---|---|
| **Attire 1 (default)** | T7 Default — Beret | ✅ WIRED 2026-10-21 | `attires/attire1/model.glb` |
| Attire 2+ | — | ⏳ reserved | Tekken in-game attires / Creation Suite pieces ladder here later, never as a gate (NO-GATE LAW) |

## Attire 1 — T7 Default (Beret)

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
- **Render**: `docs/tpose-refs/slice/a1_front.png` + `a1_back.png` (2048px T-pose, own-eyes
  verified: slate-blue greatcoat, gold eagles, textured throughout, no clay).

## ⚠️ Canon gap — the skull mask is NOT in our holdings

Slice's canon look includes a **skull mask** (hides his identity and scars). The source blend's
full object inventory was searched: it contains the complete T7 default costume and face, but
**no skull mask** — in Tekken 7 that mask is a separate generic customization item, and no
Dragunov customization parts exist in our teardown holdings (Tekken 7 library + teardown
folders + releases searched 2026-10-21). The mask was **not fabricated**. Attire 1 ships as the
canon's other state — *"sometimes his face is seen"* (scarred face visible). When a T7 generic
customization skull-mask part is torn down or a Creation Suite mask part lands, it becomes a
Slice attire/piece — until then this stays a named gap, not a blocker.
