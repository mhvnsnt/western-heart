# MEGAMI — Parts Documentation (PARTS.md)

**Fighter:** MEGAMI (The Shrine Soul) · **Roster dir:** `roster/parvati/`
**Attire 1 model:** `roster/parvati/attires/attire1/model.glb`
(25 meshes; meshopt-compressed from the SmutBase Parvati intake GLB, 191.6 MB → 23.5 MB.
Original archived on the release — see ATTIRE-SLOTS.md.)

## Labeling standard

Clean, descriptive, consistent labels. Intake (`.blend`) typos fixed:
"Bra (2)" → **Bra — variant 2**; "Gaunlet" → **Gauntlets**. Every row maps the
GLB mesh name → the clean creation-suite label. Confidence is marked where a
mesh's role is inferred from material names rather than verified in Blender.

**Layer order (outermost → innermost):** footwear → stockings → garter →
bottom → bodystocking → bra/top → body. Accessories (choker, goggles) sit
above their anchor layer.

## Body / face (base — not swappable)

| Clean label | GLB mesh | Intake name | Description | Layer |
|---|---|---|---|---|
| Body — Full | `geometry-5` | Full | Base body mesh, multi-material (arms, torso, eyes). The rig target. | base |
| Eyebrow | `brow10` | Eyebrow | Eyebrow geometry. | face |
| Eyelashes | `Lashes` | Eyelashes | Eyelash strips. | face |

## Hair (headwear)

| Clean label | GLB mesh | Description | Swappable | Layer |
|---|---|---|---|---|
| Hair — cap | `Flora Hair Genesis 8 Female` | Genesis 8 "Flora" hair cap (bangs, front, back, side sections). | yes | hair |
| Hair — strands | `RenderStrandHairGeom` | Render strand hair volume. | yes | hair |

## Headwear

| Clean label | GLB mesh | Intake name | Description | Swappable | Layer |
|---|---|---|---|---|---|
| Goggles | `24_+headgear.Material39_1_0_0.001` | Goggles | Headgear/goggle piece. Worn on the head over hair. | yes | headwear |

## Tops

| Clean label | GLB mesh | Intake name | Description | Swappable | Layer |
|---|---|---|---|---|---|
| Bra — variant 1 | `geometry-12` | Bra | Bra with bow + metal trim. | yes | top |
| Bra — variant 2 | `Top-1` | Bra (2) → Bra — variant 2 | Structured top (main + straps). | yes | top |

## Bottoms

| Clean label | GLB mesh | Intake name | Description | Swappable | Layer |
|---|---|---|---|---|---|
| Bottom | `geometry-14` | Bottom | Bottom with bow. | yes | bottom |
| Panties | `geometry-11` | (sheer robe/panties set) | Panties mesh. | yes | underwear |

## Full-body

| Clean label | GLB mesh | Intake name | Description | Swappable | Layer |
|---|---|---|---|---|---|
| Bodystocking | `Bodystocking-1` | Body Suit | Full bodystocking. | yes | full-body |
| Sheer robe | `temp` | (sheer robe) | Large sheer robe mesh (inferred from size + material; verify in Blender). | yes | full-body |

## Underwear / hosiery

| Clean label | GLB mesh | Description | Swappable | Layer |
|---|---|---|---|---|
| Garter belt | `geometry-15` | Garter with bows + metal trim. | yes | hosiery |
| Stockings | `geometry-13` | Socks/stockings. | yes | hosiery |

## Gloves

| Clean label | GLB mesh | Intake name | Description | Swappable | Layer |
|---|---|---|---|---|---|
| Glove — left | `geometry-16` | Glove L | Glove (mirrored pair with geometry-17; L/R assignment to verify in Blender). | yes | gloves |
| Glove — right | `geometry-17` | Glove R | Glove (mirrored pair with geometry-16). | yes | gloves |
| Gauntlets | `geometry-18` | Gaunlet → Gauntlets | Armored gauntlet mesh (DM04 material). | yes | gloves |

## Footwear

| Clean label | GLB mesh | Description | Swappable | Layer |
|---|---|---|---|---|
| Heels — left | `geometry-8` | High-heel shoe with insole + metal trim (pair with geometry-9). | yes | footwear |
| Heels — right | `geometry-9` | High-heel shoe with buckle + heel tip (pair with geometry-8). | yes | footwear |

## Accessories

| Clean label | GLB mesh | Intake name | Description | Swappable | Layer |
|---|---|---|---|---|---|
| Choker | `The Choker` | Choker | Leather + metal choker. | yes | accessory |

## Unresolved (verify in Blender before suite wiring)

| GLB mesh | Notes |
|---|---|
| `24_Material43_0.25_0_0` | 9,987 verts — likely skin/body-shell segment or trim set. |
| `24_Material44_0.25_0_0` | 4,134 verts — likely trim/skin segment. |
| `24_Material43_0.25_0_0.001` | 3,094 verts — duplicate-suffix mesh; probable variant of the above. |
| `24_Material42_0.25_0_0` | 6,647 verts — likely skin/trim segment. |
| `25_Material40_1_0_0` | 26,492 verts — large; candidate for **Belt** (intake name) — verify. |

**GZM_ rig objects:** the intake notes GZM_ rig/widget objects in the `.blend`;
they do not export to the GLB and are not costume parts — excluded.

**Parvati UDIM quirk (recorded):** Torso-3 UVs sit at U 1.03–2.67 (unbaked
UDIM) — invisible under the bodystocking; noted for the texture lane.
