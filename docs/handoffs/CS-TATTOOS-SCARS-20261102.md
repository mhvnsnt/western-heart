# Creation suite — TATTOOS + SCARS phase (2026-11-02, draft PR #1527)

Owner instruction (verbatim): "find a way to use blender, show me it all, and do all the rest"

## Where things are
| What | Path |
|---|---|
| Layer model, regions, projection, THREE bridge, wear hook | `game/js/decal-layers.js` |
| Blender-authored default placements (9 templates x 12 regions) | `customization/templates/decal-placements.json` |
| Blender authoring script | `tools/creation-suite/decals/author_placements_blender.py` (`run_author.sh`) |
| GLB reader / meshopt stripper (Node, vendored decoder) | `tools/creation-suite/decals/glb-skin.mjs`, `decode_glb.mjs` |
| Scar generator + set (CC0) | `tools/creation-suite/decals/make_scars.py`, `customization/decal-library/scars/` |
| Catalog wiring (idempotent) | `tools/creation-suite/decals/wire_catalog.py` |
| Proof pipeline (game projection -> OBJ -> Blender render) | `export_decal_proof.mjs`, `render_decal_proof_blender.py` |
| Proof renders | `customization/creation-suite-ui/proof-pass/tattoos-scars/` |
| Suite UI | `customization/creation-suite-ui/js/{menu-data,suite,viewer3d}.js` |
| In-fight apply / wear | `game/js/customization-consumer.js` (applyBodyDecals), `game/js/fighter.js` (receiveHit) |
| Tests | `test/decal-layers.test.mjs` |

## How a layer lands
Region canvas from the template skeleton: v along the region's bone axis (0 start joint, 1 end joint),
u around it (0 front +Z, 0.5 back). The anchor is a ray from the axis at (u, v) onto skin triangles
majority-weighted to the region's bones; if that skin is missing (women's templates: no skin under the
underwear mesh at the bra band) it searches v to the nearest region skin, then any skin. The patch is
the skin clipped by an oriented box (DecalGeometry method); every patch vertex keeps its source triangle +
barycentrics so skin weights and morph targets carry over.

## Findings
- Blender 4.3's glTF importer refuses EXT_meshopt_compression (all template GLBs are gltfpack -cc).
- Template skins have no TEXCOORD_0 (MB-Lab skin material has no texture), so decals cannot be painted
  into the body's UV map; region canvases + projected patches are the working route.
- gltfpack folds dequantisation into the inverse bind matrices: bone bind positions = mesh-node TRS
  applied to inverse(IBM) origin.
- Some No Mercy tattoo PNGs have no alpha (opaque dark background) -> they render as rectangles.

## Still owed
- Browser look-check of the layer editor at phone size (not run in this sandbox).
- Roster (non-template) bodies: different skeleton names; layers are saved but not drawn.
- Colour-key pass for the opaque No Mercy tattoos.
- Fight harness run (`tools/proof-harness/fight.mjs`) with a created fighter wearing layers.
