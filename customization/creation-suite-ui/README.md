# Western Heart — Creation Suite UI

The flagship character customization suite (UNIFIED-UI-SPEC.md §2 flow):
FIGHTER SELECT → attire picker → hub (BODY / ATTIRE / PARTS / JIGGLE /
WARDROBE / PROFILE / MOVESET / DOME), with the fighter full-screen and never
covered. Catalog data is generated — do not hand-edit it:

- `data/roster-attires.json` ← `customization/build_roster_attires.py`
- `data/parts-catalog.json` ← `customization/build_suite_catalog.py`
  (PARTS-REGISTRY.json + parts-converted/CATALOG.json + parts/hair scans +
  eye-library; see the builder header for the full source list)

Per-attire records key on `fighter::attire_id` inside localStorage
`wh_creation_suite_v1`; `customization.json` (v1 schema) is the portable
per-attire file — Save to Attire downloads it, and dropping it into an
attire's repo folder makes the suite restore it on select.

## Eyes are parts, not decals (owner verdict, 2026-10-20 ~19:40 CDT)

The owner rejected a painted texture eye on a character ("looks funny, not
placed right; he also needs eyelashes and eyebrows... let it be a real eye
not just a decal on his face from hand tooling") and explicitly wants to
place eyes **himself** in this suite. The design rule for everything eye
related here:

- **Eyeball + eyelashes + eyebrows are real placeable MESH parts.** They
  equip through the normal parts system at an eye/head/face socket and are
  positioned with the suite's per-part placement controls (PLACE_AXES:
  position / rotation / scale), saved into the attire's placement record —
  exactly like any other mesh part. No hand-placed decals.
- **Eye-library texture entries** (`eye-yellow-tiger` etc., catalog field
  `eye_kind: "texture_variant"`) are **legacy texture swaps only**. They are
  labeled as texture variants in the UI and are never presented as the eye
  solution. Placeable eye parts carry `eye_kind: "placeable_part"` and are
  listed separately in the PARTS tab.
- **In-repo placeable assets today:** Spider-Girl eye lenses
  (`customization/parts/superhero/spidergirl/spidergirl-eyes.glb`, the
  existing mesh-eye precedent) and the CC0 eyebrows
  (`customization/parts/hair/cc0/Eyebrows_Regular.gltf`,
  `Eyebrows_Female.gltf`; mirrored under `parts/hair/quaternius/`).
- **Honest gap:** no eyelash mesh exists in-repo yet. When one is pulled
  in, it enters the catalog as a placeable part like the brows — it is not
  faked with a texture in the meantime.
- **Named test case: DEATHFANG (human form).** The owner named him as the
  test case for placeable eyes once eye parts exist. His character work
  belongs to another lane — this suite's job is only to make his case
  possible: a real eyeball/lash/brow part he can equip and place himself.
