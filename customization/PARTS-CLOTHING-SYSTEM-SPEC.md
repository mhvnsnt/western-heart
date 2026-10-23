# Western Heart — Parts & Clothing System Spec
## Creation Suite: Full Customization Architecture
**Date:** 2026-10-23  
**Owner directives:** 2026-10-23 ~07:05, ~07:06, ~07:07, ~07:08 CDT (verbatim below)  
**Sources:** WWE 2K CAW breakdown, Tekken 6/TTT2 customization research, existing `customization/` library

---

## Owner Directives (verbatim)

> "make all like I said their clothing items deletable hideable swappable make invisible recolorable label them all in the character creation suite parts and different like how WWE and Tekken labels and organizes their stuff use the teardown files to create that in the character editing and character creation in the creation suite so you can edit and modify all the clothes fully and add more like how WWE does the layer system you can add a bunch of different layers of upper body stuff lower body stuff shoes knee pads different accessories um fucking shin guards and um kick pads wrist guards wrist tape wrist stuff lower arm upper arm hand fingers fingernails Teeth eyes nose mouth eyebrows ears Hair different hair parts like how Tekken you can create the full hairstyle if you wanted to and Selectable hair parts like WWE eye color eye shape and type there's piercings jackets shirts bras panties underwear trunks different types of bottoms and tops different types of pants and underwear and shirts and accessories and different types of clothes different types of armwear legwear neck wear neck accessories back accessories torso accessories scars tattoos um images logos all the type of things like all of those get different types of things for all of those and make them all selectable and organized in different sub menus and everything just like Tekken does in its creation suite and how WWE does and wire it up fully using the teardown files and any open source or free stuff that you can get hold of"

> "Oh yeah I forgot like had masks face accessories face wear head wear glasses um different earrings piercings those types of things body piercings goddamn face piercings all types of different accessories and parts and pieces all those types of things fully wired up and labeled and organized"

> "really study those systems, the layouts, the organization, the UI, the user interface, all of that, like um and with WWE and Tekken and all the stuff I mentioned and then wire it up from the teardown files and open source and anything you can find and get a hold of through your research uh that's 2026 industry standard or high level or anything that'll fit really anything that will go with this no matter what it is for real"

> "oh yeah also makeup different types of makeup eye makeup uh lipstick um different types of teeth teeth color um teeth types and shapes um different types of uh face and um body morphing and templates different uh body part templates like WWE and Tekken and um motherfucking face paint different face paint options ability to add logos and face paint and create and generate um different designs and logos and paints and makeups and stuff like that all of that type of stuff and textures and things all that type of shit"

---

## Design Principle

**The system should FEEL like WWE 2K and Tekken had a baby.** Not a guess at their systems — built from their actual teardown data, menu structures, and organization paradigms.

- **WWE 2K** contributes: the layer system (multiple stacked items per body region), per-item color channels, material editor, logo placement, body morph sliders, left/right independent slots
- **Tekken** contributes: slot-based item categories, full-screen 3D preview, item equip/unequip flow, hair part combinations, per-character item eligibility

---

## Per-Item Operations (every item supports ALL of these)

Every clothing/accessory/part item in the system MUST support:

| Operation | Description |
|-----------|-------------|
| **Delete** | Remove the item from the character entirely |
| **Hide** | Toggle visibility off (item still equipped, just invisible) |
| **Show** | Toggle visibility on |
| **Swap** | Replace with a different item in the same slot |
| **Recolor** | Change color channels (primary, secondary, accent, trim) |
| **Material** | Change material finish (fabric, leather, metal, matte, glossy) |
| **Reposition** | Adjust position/rotation/scale offsets on the bone socket |
| **Layer up/down** | Change render order within the layer stack |

---

## Category Taxonomy

### HEAD & FACE

#### Hair
- **Full hairstyles** (Tekken-style: complete preset hairstyles)
- **Hairstyles** (100+ options: short, medium, long, curly, straight, wavy, afro, mohawk, etc.)
- **Hair parts** (WWE-style: selectable individual components)
  - Hair - Front
  - Hair - Front (Right) [Tekken slot]
  - Hair - Back [Tekken slot]
  - Hair - Top / Crown
  - Hair - Sides (Left / Right independent)
  - Bangs / Fringe
  - Ponytail / Braids / Dreadlocks (separate attachable parts)
- **Hair color** (full color picker + presets: natural, dyed, fantasy)
- **Hair dye** (two-tone, ombre, highlights, streaks, roots — WWE-style multi-color)
- **Hair material** (matte, glossy, wet-look)

#### Facial Hair
- **Beards** (full beard, goatee, chin strap, soul patch — layered, WWE-style)
- **Mustaches** (handlebar, chevron, pencil, horseshoe)
- **Stubble** (5 o'clock shadow, designer stubble — adjustable length)
- **Sideburns** (length, width, style)
- **Facial hair color** (match hair or custom)
- **Facial hair layering** (combine beard + mustache + stubble)

#### Face
- **Eyes**
  - Eye color (full picker + presets including universal eye library)
  - Eye shape (almond, round, narrow, wide, upturned, downturned)
  - Eye type (human, animal, glowing, cybernetic, etc.)
- **Eyebrows**
  - **Eyebrow types** (arched, straight, curved, angled, S-shaped)
  - Shape, thickness, color, angle
  - Individual brow customization (L/R independent)
- **Eyelashes**
  - **Eyelash types** (natural, dramatic, wispy, doll-like, lower lashes)
  - Length, volume, curl, color
  - Upper / Lower independent
- **Nose** (morph sliders: width, length, bridge, tip)
- **Mouth** (morph sliders: width, fullness, shape)
- **Teeth**
  - Visibility (visible/hidden)
  - **Teeth color** (natural white, bleached, gold, silver, black, custom)
  - **Teeth types** (human, vampire fangs, oni fangs, shark teeth, cybernetic, grillz)
  - **Teeth shapes** (straight, pointed, rounded, jagged, filed)
  - Individual tooth customization (WWE-style detail)
- **Ears** (shape, size, position)
- **Face morph sliders** (WWE-style: jaw width, cheek depth, brow, chin)

#### Face Wear & Accessories
- **Masks** (full-face, half-face, eye masks, luchador, oni, etc.)
- **Glasses** (sunglasses, reading glasses, goggles, monocle, visors)
- **Face accessories** (face chains, nose rings as face wear)

#### Makeup
- **Foundation** (coverage, finish: matte, dewy, full-coverage)
- **Eye makeup**
  - Eyeshadow (colors, styles: smokey, cut-crease, natural, dramatic)
  - Eyeliner (winged, tightline, graphic, colors)
  - Mascara / False lashes (length, volume, style)
- **Lipstick / Lip color** (matte, glossy, satin, metallic; full color picker)
- **Blush / Contour** (placement, intensity, color)
- **Highlighter** (placement, intensity)
- **Different makeup types** (natural, glam, goth, drag, theatrical, clown, etc.)
- **Makeup presets** (save/load full face combinations)

#### Face Paint
- **Different face paint options** (tribal, sugar skull, clown, warrior, animal, abstract)
- **Face paint layers** (base, details, accents — WWE-style layering)
- **Custom face paint creation** (see Creation Tools below)
- **Face paint opacity / blend modes**

#### Face Paint / Makeup Creation Tools
- **Logo designer**: create custom logos from shapes, text, uploaded images
- **Face paint designer**: draw/paint directly on face UV template
- **Makeup generator**: AI-assisted generation from text prompts or reference images
- **Design library**: save, share, browse community designs
- **Stamp/brush tools**: apply pre-made elements (stars, swirls, patterns)
- All designs exportable as PNG textures, applicable to any character

#### Piercings
- **Ear piercings**
  - Earrings (studs, hoops, danglers, gauges, cuffs — different types)
  - Left / Right independent
  - Multiple per ear (upper, lobe, tragus, helix)
- **Face piercings**
  - Nose (nostril L/R, septum, bridge)
  - Lip (labret, Monroe, Medusa, snake bites)
  - Eyebrow (L/R)
  - Tongue
- **Body piercings**
  - Nipple (L/R)
  - Navel / Belly button
  - Surface piercings

#### Head Wear
- **Hats** (caps, beanies, fedoras, top hats, etc.)
- **Headbands** / Bandanas
- **Hoods** (up/down toggle)
- **Helmets** / Head armor
- **Crowns** / Tiaras / Circlets
- **Horns** / Antlers (attachable)

### UPPER BODY

#### Layer System (WWE-style stacking)
Each upper body region accepts MULTIPLE stacked layers, rendered back-to-front:

**Layer 1 — Base/Skin**
- Bare torso (body mesh)
- Body paint / tattoos (see Body Art)

**Layer 2 — Underwear/Base**
- Bras (sports bra, regular, strapless — different types)
- Undershirts / Tank tops
- Binders / Compression

**Layer 3 — Tops**
- Shirts (t-shirt, button-up, polo — different types)
- Blouses
- Singlets / Wrestling singlets
- Crop tops

**Layer 4 — Outerwear**
- Jackets (denim, leather, bomber, blazer — different types)
- Vests
- Hoodies
- Coats / Robes
- Armor (chest plates, pauldrons)

#### Arms (Left / Right Independent)
- **Upper arm**: armbands, bicep bands, tattoos
- **Lower arm**: wrist guards, wrist tape, wristbands, gauntlets
- **Elbow**: elbow pads
- **Hands**: gloves (fingerless, full, MMA, boxing), hand wraps
- **Fingers**: rings (multiple per hand)
- **Fingernails**: color, length, style

### LOWER BODY

#### Layer System
**Layer 1 — Base/Skin**
- Bare legs (body mesh)

**Layer 2 — Underwear**
- Panties / Underwear (different types: briefs, boxers, thongs, etc.)
- Trunks
- Jockstraps
- Compression shorts

**Layer 3 — Bottoms**
- Pants (jeans, cargo, dress — different types)
- Shorts
- Skirts
- Tights / Leggings
- Wrestling trunks / Fight shorts

**Layer 4 — Leg Accessories**
- Knee pads (Left / Right independent)
- Shin guards (Left / Right independent)
- Kick pads
- Thigh straps / Garters

#### Feet
- **Shoes** (sneakers, boots, dress shoes — different types)
- **Boots** (combat, wrestling, knee-high)
- **Sandals** / Barefoot
- **Socks** (ankle, crew, knee-high)

### ACCESSORIES

#### Neck Wear
- **Necklaces** (chains, pendants, chokers)
- **Scarves**
- **Ties** / Bow ties
- **Collars** (with/without leash ring)

#### Torso Accessories
- **Belts** (with buckle options)
- **Suspenders**
- **Chest harnesses**
- **Sashes**

#### Back Accessories
- **Capes** / Cloaks
- **Wings** (angel, demon, cybernetic)
- **Backpacks**
- **Weapon sheaths** (sword on back, etc.)

#### Arm & Leg Wear (decorative)
- **Armwear**: arm sleeves, arm warmers
- **Legwear**: leg warmers, stockings

### BODY ART

- **Tattoos** (WWE-style: layered, placeable, scalable, rotatable — full body canvas)
- **Scars** (placeable, different types: cuts, burns, surgical)
- **Images** (custom image upload, placed on body)
- **Logos** (placeable on any attire piece, scalable/rotatable — WWE 2K19 feature)
- **Body paint** (full-body patterns)

---

## Menu Organization

### Top-Level Tabs (Creation Suite)

```
CREATE FIGHTER
├── BODY
│   ├── Body Templates (WWE/Tekken-style presets)
│   │   ├── Preset bodies (8+ base templates: athletic, heavyweight, cruiserweight, etc.)
│   │   ├── Gendered bases (male, female, androgynous)
│   │   └── Fantasy bases (demon, oni, cybernetic, etc.)
│   ├── Physique — Body Morphing
│   │   ├── Height / Weight sliders
│   │   ├── Muscle definition (chest, arms, legs, abs — individual)
│   │   ├── Shoulder width / Hip width
│   │   ├── Waist / Chest size
│   │   ├── Body fat distribution
│   │   └── Individual body part morphing (biceps, thighs, calves, etc.)
│   ├── Body Part Templates
│   │   ├── Pre-sculpted body parts (WWE-style: swap individual parts)
│   │   ├── Arm templates (different muscle shapes)
│   │   ├── Leg templates
│   │   ├── Torso templates
│   │   └── Mix-and-match parts across templates
│   ├── Skin (tone, texture, muscle definition overlay)
│   ├── Face — Face Morphing
│   │   ├── Full face morph sliders (WWE-style: dozens of parameters)
│   │   ├── Jaw (width, shape, chin projection)
│   │   ├── Cheeks (depth, width, cheekbone height)
│   │   ├── Brow (ridge, angle, depth)
│   │   ├── Eyes (spacing, size, angle, depth)
│   │   ├── Nose (bridge, tip, nostril, width, length)
│   │   ├── Mouth (width, fullness, lip shape)
│   │   ├── Chin (width, projection, cleft)
│   │   ├── Ears (size, position, angle)
│   │   └── Asymmetry controls (left/right independent tweaks)
│   └── Body Art (tattoos, scars — full body canvas)
│
├── HEAD
│   ├── Hair (full styles + individual parts + color + dye)
│   ├── Facial Hair (beards, mustaches, stubble, sideburns)
│   ├── Eyes (color, shape, type)
│   ├── Eyebrows (types, shape, thickness, color)
│   ├── Eyelashes (types, length, volume, curl)
│   ├── Nose / Mouth / Ears (morph + presets)
│   ├── Teeth (color, types, shapes)
│   ├── Makeup (foundation, eye makeup, lipstick, blush, presets)
│   └── Face Paint (options, layers, custom creation tools)
│
├── HEADWEAR & FACEWEAR
│   ├── Masks
│   ├── Glasses / Goggles / Visors
│   ├── Hats / Headbands / Hoods / Helmets
│   ├── Horns / Antlers / Ears (attachable)
│   └── Face Accessories
│
├── PIERCINGS
│   ├── Ears (L/R independent, multiple per ear)
│   ├── Face (nose, lip, eyebrow, tongue)
│   └── Body (nipple, navel, surface)
│
├── UPPER BODY (layered)
│   ├── Layer 1: Base (body paint layer)
│   ├── Layer 2: Underwear (bras, undershirts)
│   ├── Layer 3: Tops (shirts, singlets, crop tops)
│   ├── Layer 4: Outerwear (jackets, vests, armor)
│   └── Per-layer: color, material, logo placement
│
├── ARMS (L/R independent)
│   ├── Upper Arm (armbands, tattoos)
│   ├── Elbow (pads)
│   ├── Lower Arm (wrist guards, tape, gauntlets)
│   ├── Hands (gloves, wraps)
│   ├── Fingers (rings)
│   └── Fingernails (color, length, style)
│
├── LOWER BODY (layered)
│   ├── Layer 1: Base
│   ├── Layer 2: Underwear (panties, trunks, etc.)
│   ├── Layer 3: Bottoms (pants, shorts, skirts, tights)
│   └── Layer 4: Leg Accessories (knee pads, shin guards)
│
├── FEET
│   ├── Shoes / Boots / Sandals
│   └── Socks
│
├── ACCESSORIES
│   ├── Neck (necklaces, scarves, ties, collars)
│   ├── Torso (belts, suspenders, harnesses, sashes)
│   ├── Back (capes, wings, backpacks, sheaths)
│   └── Decorative (arm sleeves, leg warmers, stockings)
│
├── BODY ART
│   ├── Tattoos (layered, placeable, scalable)
│   ├── Scars (placeable, types)
│   ├── Images (custom upload)
│   └── Logos (placeable on attire)
│
└── PREVIEW
    ├── Full-screen 3D preview (Tekken-style)
    ├── Rotate / Zoom / Pan
    ├── Pose selector (T-pose, fighting stance, idle)
    └── Lighting controls
```

---

## Technical Architecture

### Part Format

**Mesh parts** (hair, clothes, accessories):
- Format: GLB (glTF 2.0)
- Attach at bone sockets with position/rotation/scale offsets
- Each part's MANIFEST entry names: default socket, offsets, layer, slot
- UI can reposition or snap back to defaults

**Texture-swap parts** (eyes, decals, face paint, tattoos):
- Format: standalone PNG
- `character_mappings` in MANIFEST: which texture/material/rect to composite into per character
- Universal by design — add a mapping → works on that character
- No geometry changes, no new art needed

### MANIFEST Entry Format

```json
{
  "id": "jacket-leather-black",
  "name": "Black Leather Jacket",
  "type": "outerwear",
  "category": "upper_body",
  "layer": 4,
  "slot": "upper_body_outer",
  "mesh": "jacket-leather-black.glb",
  "default_socket": "spine_02",
  "offsets": {"position": [0, 0, 0], "rotation": [0, 0, 0], "scale": [1, 1, 1]},
  "color_channels": ["primary", "secondary", "trim", "lining"],
  "materials": ["leather", "fabric", "denim"],
  "left_right": false,
  "notes": "Source: WWE 2K teardown / Tekken 7 / original"
}
```

### Directory Layout (under `customization/`)

```
customization/
├── parts/
│   ├── head/
│   │   ├── hair-full/          # Complete hairstyles (Tekken-style)
│   │   ├── hair-parts/         # Individual components (WWE-style)
│   │   │   ├── front/
│   │   │   ├── back/
│   │   │   ├── sides/
│   │   │   └── attachments/    # ponytails, braids, dreads
│   │   ├── eyes/
│   │   │   ├── color/
│   │   │   ├── shape/
│   │   │   └── type/
│   │   ├── eyebrows/
│   │   ├── nose/               # morph presets
│   │   ├── mouth/              # morph presets
│   │   ├── teeth/
│   │   └── ears/
│   ├── headwear/
│   │   ├── masks/
│   │   ├── glasses/
│   │   ├── hats/
│   │   ├── headbands/
│   │   ├── hoods/
│   │   ├── helmets/
│   │   └── horns/
│   ├── piercings/
│   │   ├── ears/
│   │   ├── face/
│   │   └── body/
│   ├── upper-body/
│   │   ├── layer2-underwear/
│   │   ├── layer3-tops/
│   │   └── layer4-outerwear/
│   ├── arms/
│   │   ├── upper-arm/
│   │   ├── elbow/
│   │   ├── lower-arm/
│   │   ├── hands/
│   │   ├── fingers/
│   │   └── fingernails/
│   ├── lower-body/
│   │   ├── layer2-underwear/
│   │   ├── layer3-bottoms/
│   │   └── layer4-leg-accessories/
│   ├── feet/
│   │   ├── shoes/
│   │   └── socks/
│   ├── accessories/
│   │   ├── neck/
│   │   ├── torso/
│   │   ├── back/
│   │   └── decorative/
│   ├── body-art/
│   │   ├── tattoos/
│   │   ├── scars/
│   │   ├── images/
│   │   └── logos/
│   └── PARTS-INDEX.json        # master index
```

---

## SmutBase 6 — Parts Inventory (Initial Population)

Each fighter's existing meshes become the first entries in the parts system:

### Ryusan (Mina Ashido) — `roster/mina-ashido/`
_From 4.4MB GLB, 8 meshes_

| Mesh | Category | Type | Swappable |
|------|----------|------|-----------|
| (extract mesh names from GLB) | | | |

### Tobi (Mirko) — `roster/miruko/`
_From 5.6MB GLB, 11 meshes, rabbit ears_

### Chatur (Rahkasa) — `roster/rahkasa/`
_From 3.7MB GLB, 1 mesh_

### Pond (Tsuyu) — `roster/tsuyu-asui/`
_From 5.8MB GLB, 9 meshes_

### Megami (Parvati) — `roster/parvati/`
_From 183MB GLB, 25 meshes_

| Mesh | Category | Type | Swappable | Notes |
|------|----------|------|-----------|-------|
| Belt | accessories/torso | belt | yes | |
| Body Suit | upper-body/layer3 | bodysuit | yes | |
| Bottom | lower-body/layer3 | bottoms | yes | |
| Bra | upper-body/layer2 | bra | yes | |
| Bra (2) | upper-body/layer2 | bra | yes | **RENAME**: duplicate label |
| Choker | accessories/neck | choker | yes | |
| Gaunlet | arms/lower-arm | gauntlet | yes | **RENAME**: typo → "Gauntlet" |
| Glove L | arms/hands | glove | yes | Left |
| Glove R | arms/hands | glove | yes | Right |
| Goggles | headwear | goggles | yes | |
| Full | body | base mesh | no | Body base |
| Eyebrow | head/eyebrows | eyebrow | yes | |
| Eyelashes | head/eyes | eyelashes | yes | |

### Menajerii (Vixen) — `roster/vixen/`
_From 630MB GLB, 29 meshes (Injustice 2)_

---

## Implementation Phases

### Phase 1: Spec & Foundation (this document)
- [x] Comprehensive spec written
- [ ] Spec pushed to repo (`customization/PARTS-CLOTHING-SYSTEM-SPEC.md`)
- [ ] SmutBase 6 mesh inventories extracted

### Phase 2: SmutBase 6 Parts Population
- [ ] Extract mesh names from each GLB
- [ ] Create PARTS.md per fighter with labeled inventory
- [ ] Apply labeling standard (fix typos, duplicates)
- [ ] Create MANIFEST entries for each part

### Phase 3: Teardown Parts Import
- [ ] WWE 2K parts (from `teardown/wwe-2k/`)
- [ ] Tekken 7 parts (from `teardown/tekken7/`)
- [ ] WMXIX parts (3,479 files, indexed)
- [ ] No Mercy parts (993 files, indexed)
- [ ] Def Jam parts

### Phase 4: Creation Suite UI
- [ ] Tab structure implemented
- [ ] Layer system UI
- [ ] Per-item operations (delete/hide/swap/recolor)
- [ ] 3D preview with real-time updates
- [ ] Left/right independent controls

### Phase 5: Full Roster Rollout
- [ ] Apply parts system to all 68 fighters
- [ ] Migrate existing customization to new system

---

## Open Source & 2026 Industry Standard Sources

_For the research lane to pull from:_

- **WWE 2K teardowns**: CAW part structures, menu layouts
- **Tekken 7/8 teardowns**: Item slot system, customization UI flow
- **Soulcalibur VI CaS**: Character creation system (in teardowns)
- **Blender**: Headless backend for part processing
- **Godot**: Potential UI framework reference
- **Three.js**: Current 3D preview renderer

## Research Catch-All: Deep Customization Survey

**Owner directive 2026-10-23 ~07:08 CDT:** _"anything else that you can find in your research that I'm missing from character customization in games in WWE games, in Tekken games, in any game that have character customization in depth and wire it all up pull it all in get any open source or stuff you can get a hold of and anything from the tear down files and all of them"_

**Principle:** If it exists in ANY game's character customization, it belongs in ours. This is a living checklist — the research lane adds to it.

### Games to Survey (with deep customization systems)

| Game | System | Key Features to Pull |
|------|--------|---------------------|
| WWE 2K series | Create-A-Superstar | Layer system, morph sliders, logo placement, material editor |
| Tekken 7/8 | Customization | Item slots, full-screen preview, per-character eligibility |
| Soulcalibur VI | Character Creation (CaS) | Race/species options, equipment with stats, style editor |
| Elden Ring / Dark Souls | Character Creator | Detailed face sculpting, age sliders |
| Cyberpunk 2077 | Character Creator | Genital options, nail customization, cyberware |
| Baldur's Gate 3 | Character Creator | Origin-based options, extensive face variety |
| Black Desert Online | Character Creator | Most detailed face/body sculpting in any game |
| Saints Row | Character Creator | Gender fluidity, voice options, walk styles |
| Fallout 4 | Character Creator | Layered face sculpting |
| Dragon's Dogma 2 | Character Creator | Pawn system, photogrammetry-based |
| Monster Hunter Wilds | Character Creator | Palico customization (for creature fighters) |
| The Sims 4 | Create-A-Sim | Aspiration/personality system, gallery sharing |
| Second Life | Avatar Creator | User-generated content marketplace model |
| VRChat | Avatar Systems | Full-body tracking compatibility, expression menus |

### Feature Checklist (anything found → add to spec)

- [ ] Voice customization (pitch, tone, accent)
- [ ] Walk/animation style (idle poses, walk cycles)
- [ ] Age sliders (NOT for minors — adult age variation only)
- [ ] Body hair (chest, arms, legs — density, style)
- [ ] Skin details (moles, freckles, wrinkles, stretch marks)
- [ ] Nail art (designs, not just color)
- [ ] Contact lenses (colored, patterned, sclera)
- [ ] Prosthetics / cybernetics (limbs, eyes, enhancements)
- [ ] Species options (for creature fighters: ears, tails, scales)
- [ ] Height/weight affecting gameplay (WWE-style weight classes)
- [ ] Outfit presets (save/load full looks)
- [ ] Randomize buttons (full outfit, face, etc.)
- [ ] Mirror symmetry toggle (for asymmetric designs)
- [ ] Import/export (share designs as files)
- [ ] Community gallery (browse/download others' creations)

---

## Notes

- **No Tekken/WWE names in user-facing canon** — technical files only
- **All adults** — no minor character parts
- **SmutBase 6 first**, then full roster rollout
- Every part ever added gets a MANIFEST entry — no exceptions
