# Default CAW Base Body

## How the base works in WMXIX (and No Mercy)

Neither wrestling game ships a single "blank body" mesh file. Instead, **"Create New Fighter" starts from a body TYPE selection**, and the base body is assembled from the game's internal body-type templates.

### WMXIX Body Types
The player picks from preset body types (tall, muscular, heavy, etc.). Each body type is a parametric template — height, shoulder width, waist, limb proportions — that generates the base mesh. The specific body-type mesh data lives in the game's code (not in edit_data/).

### No Mercy Body Types (documented in re-docs)
- **Male:** 14 types — Skinny 1/2, Medium 1/2, Thick 1/2, Fat 1/2, Austin, HBK, Rikishi, Rock, Hairy 1/2
- **Female:** 9 types — Chyna, Fit 1-4, Grannie, Jackie, Petit 1/2

### Western Heart implementation

For Western Heart's "New Fighter" flow:

1. **Start from a Tekken fighter base** — pick any of our 28 named fighters' base models as the starting body (Pantera's King frame, Thor's Ganryu frame, etc.)
2. **OR start from a parametric body** — define height/weight/build sliders that generate a base mesh (using the No Mercy body-type ranges as reference: Height 5'0"–7'11", Weight 100–599 lbs)
3. **Layer CAW parts on top** — all 3,372 parts in this directory attach to the base via the slot system

### The pipeline
```
New Fighter
  → Choose base (Tekken fighter model OR parametric body type)
  → Choose body type modifiers (height, weight, proportions)
  → Apply skin tone (8 tones, see skins/)
  → Add face (348 faces in faces/)
  → Add hair (156 styles in hair/)
  → Add attire per slot (upper_body/, lower_body/, shoes/, gloves/)
  → Add accessories (accessories/, gears/)
  → Tekken 4-slot overlay (Head/Upper/Lower/Other items)
  → Done → fighter JSON
```

### Files in this directory
This directory holds documentation. The actual base meshes are:
- Tekken fighter bases: `teardown/models/tekken7/` and `teardown/tekken3/models/`
- Parametric body templates: to be built (see CHARACTER-CREATION.md)
