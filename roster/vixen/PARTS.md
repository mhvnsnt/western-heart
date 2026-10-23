# MENAJERII — Parts Documentation (PARTS.md)

**Fighter:** MENAJERII (メナジェリー, The Menagerie Soul) · **Roster dir:** `roster/vixen/`
**Attire 1 model:** `roster/vixen/attires/attire1/model.glb`
(29 meshes; meshopt-compressed from the SmutBase Vixen intake GLB, 629.7 MB → 41.7 MB.
Original archived on the release — see ATTIRE-SLOTS.md.)

## Labeling standard

Clean, descriptive, consistent labels. Intake (`.blend`) names normalized to
the suite convention (`Pantie` → **Panties**, `Stocking ×2` → **Stockings —
left/right**). Every row maps the GLB mesh name → the clean creation-suite
label. Confidence is marked where a mesh's role is inferred from material
names / mirrored bounding boxes rather than verified in Blender.

**Layer order (outermost → innermost):** boots → stockings → panties → suit →
bodystocking → bra/top → harness → body. Accessories (choker, necklace) sit
above their anchor layer.

## Body / face (base — not swappable)

| Clean label | GLB mesh | Intake name | Description | Layer |
|---|---|---|---|---|
| Body — Vixen Mesh | `geometry-1` | Vixen Mesh | Base body mesh, 18 primitives / palette materials. The rig target. | base |

## Hair (headwear)

| Clean label | GLB mesh | Description | Swappable | Layer |
|---|---|---|---|---|
| Hair — cap | `Hair` | Hair cap. | yes | hair |
| Hair — strands (main) | `RenderStrandHairGeom` | Primary strand-hair volume. | yes | hair |
| Hair — strands (secondary) | `RenderStrandHairGeom-1` | Secondary strand-hair volume. | yes | hair |
| Hair — strands (tertiary) | `RenderStrandHairGeom-2` | Tertiary strand-hair detail. | yes | hair |

## Tops

| Clean label | GLB mesh | Intake name | Description | Swappable | Layer |
|---|---|---|---|---|---|
| Top | `Top-1` | (top) | Structured top. | yes | top |
| Bra — variant 1 | `geometry-13` | Bra | Bra variant (mirrored-bbox pair with geometry-15 region). | yes | top |
| Bra — variant 2 | `geometry-15` | Bra | Bra variant. | yes | top |
| Lace top | `VALASB4Lace` | (lace set) | Lace lingerie piece. | yes | top |

## Bottoms / underwear

| Clean label | GLB mesh | Intake name | Description | Swappable | Layer |
|---|---|---|---|---|---|
| Panties — variant 1 | `geometry-12` | Pantie | Panties. | yes | underwear |
| Panties — variant 2 | `geometry-14` | Pantie 3 | Panties variant. | yes | underwear |

## Full-body

| Clean label | GLB mesh | Intake name | Description | Swappable | Layer |
|---|---|---|---|---|---|
| Bodysuit | `Suit` | Body Suit | Full bodysuit. | yes | full-body |
| Bodystocking | `Bodystocking-1` | (bodystocking) | Full bodystocking. | yes | full-body |
| BDSM harness | `BDSM harness` | BDSM harness | Full-torso harness (36,967 verts — the signature piece). | yes | full-body |
| Harness neck ring | `BDSM harness neck ring-1` | (harness set) | Neck ring for the harness. | yes | accessory |

## Hosiery

| Clean label | GLB mesh | Intake name | Description | Swappable | Layer |
|---|---|---|---|---|---|
| Stockings — left | `geometry-17` | Stocking | Stocking (mirrored pair with geometry-18; L/R to verify in Blender). | yes | hosiery |
| Stockings — right | `geometry-18` | Stocking | Stocking (mirrored pair with geometry-17). | yes | hosiery |

## Gloves

| Clean label | GLB mesh | Intake name | Description | Swappable | Layer |
|---|---|---|---|---|---|
| Glove — left | `geometry-10` | Glove L | Glove (mirrored pair with geometry-11; 12,337 verts). | yes | gloves |
| Glove — right | `geometry-11` | Glove R | Glove (mirrored pair with geometry-10; 12,319 verts). | yes | gloves |
| Arm warmers | `Arms-3` | (arms set) | Arm covering (inferred; verify in Blender). | yes | gloves |

## Footwear

| Clean label | GLB mesh | Intake name | Description | Swappable | Layer |
|---|---|---|---|---|---|
| Boots | `Boots` | Boots | Boots. | yes | footwear |

## Accessories

| Clean label | GLB mesh | Intake name | Description | Swappable | Layer |
|---|---|---|---|---|---|
| Choker | `The Choker` | Choker | Choker. | yes | accessory |
| Necklace | `Necklace` | Necklace | Necklace. | yes | accessory |
| Belt | `geometry-20` | Belt | Belt (inferred from size/position; verify in Blender). | yes | accessory |
| Merged accessory set | `ForDAzMerged2` | (merged) | Merged accessory geometry, 4 primitives (inferred; verify in Blender). | yes | accessory |

## Unresolved (verify in Blender before suite wiring)

| GLB mesh | Notes |
|---|---|
| `geometry-9` | 6,841 verts, 7 primitives — multi-part piece; candidate for layered trim set. |
| `geometry-16` | 13,131 verts, 3 primitives — large; candidate for skirt/overskirt or cape. |
| `geometry-19` | 10,543 verts — large torso-region piece; candidate for jacket/oversuit. |
| `Plane` | 4 verts — scene ground plane, not a costume part. Excluded from the suite. |

**GZM_ rig objects:** the intake notes GZM_ widget-rig objects in the `.blend`
(fully rigged + body morphs); they do not export to the GLB and are not
costume parts — excluded.
