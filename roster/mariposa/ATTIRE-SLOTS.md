# MARIPOSA — Attire Slots (owner 2026-10-18)

Canonical slot map. (Proprietary name: Mariposa — "Zafina" retired per owner
2026-10-18 ~19:37 CDT. Paths under `roster/zafina/` predate the rename and stay
as-is on disk; display name is Mariposa everywhere the player sees it.)

## Slots

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **Mariposa — Butterfly Default** | `roster/mariposa/attires/butterfly-default/mariposa-butterfly-default.glb` — REAL default attire, ~30%+ changed like Pantera's Attire 1 (owner work 2026-10-18). Proprietary butterfly persona, NOT a recolor of the T6 outfit: new dark hair silhouette (real T6 hair parts reshaped, ponytail + roses removed), butterfly wing makeup painted on head diffuse, plum lips, yellow tiger eyes (owner's universal "I like" variant), near-black bustier with iridescent blue/violet butterfly wings, violet scarf, flared skirt-morph shorts, butterfly eyespot gloves/boots. MPFB2-class body morph + GNM-class face morphs baked in. Built inside the wired pipeline (PARTS-REGISTRY.json `mariposa` mapping, decal-library/mariposa, parts/mariposa-default originals). |
| 2 | *(reserved)* | Future Tripo main attire (registry law). |
| 3 | **Mariposa — Golden Pharaoh** | `roster/zafina/attires/golden-pharaoh/zafina-golden-pharaoh.glb` — custom colorway reskin of her Tekken 6 outfit: butterfly top pink → metallic gold on black, teal scarf + lapis-blue roses kept, gold ring belt, yellow tiger eyes. Texture-only; rig intact. Moved to slot 3 per the slot-ordering law (early slots = Western Heart / Eastern Mind-based attires). Untouched by the Slot 1 build. |

## Tripo model (recorded, unwired)

- `game/assets/models/mariposa.glb` — Tripo butterfly-woman pull (2026-10-17, 21MB, 1M verts, no rig). Have-not-wired: no skeleton, no slot render proof as an attire. Per the Tripo Attachment Registry law it takes a main slot once rigged/wired; until then Slot 1 stays the pipeline-built Butterfly Default per owner work order 2026-10-18. OPEN for owner: confirm slot order when the Tripo is wired.

## Slot-ordering law

- Early slots: Western Heart / Eastern Mind-based attires and Tripo mains.
- Later slots: Tekken-based attires (ports, recolors, ripped variants).
- Every attire goes through the Tekken character customizer + customization
  suite; the owner does the creative customization himself.

## Options wired

- Eyes: `customization/parts/mariposa-default/` (original dark brown saved) +
  universal `customization/eye-library/` (yellow tiger applied).
- Top/scarf/shorts/hair: `customization/decal-library/mariposa/` — butterfly-default (applied) + originals (restore).
- Hair meshes: `customization/parts/mariposa-default/mariposa-hair-original-opt.glb` (ponytail + roses, removed for Slot 1).
- Morphs: `mpfb2_body_curvy`, `gnm_face_butterfly`, `hair_butterfly_silhouette`, `skirt_flare` — definitions in `customization/parts/mariposa-default/MANIFEST.json`, baked into the Slot 1 GLB.

## History

- 2026-10-18: Golden Pharaoh merged as slot 1 (#262); proprietary rename Mariposa landed (#267).
- 2026-10-19: Slot 1 Butterfly Default built (this PR) — Golden Pharaoh shifted to slot 3 per ordering law, untouched on disk.
