# Session 2026-10-23 — SmutBase 6 Full Pipeline + Parts System Spec

## SmutBase 6 Full Pipeline (user 2026-10-23 ~07:02 CDT, verbatim)

"So we need to get all of the six that are um from the renders here and the intake we need to get them fully rigged full move sets to their canon and that um whatever characters that they pulled from their stances and move sets and all their um attacks but with Tekken inputs and any other types of moves we can add to them that'll give them more to their canon and their character and their attacks and um full combos and move lists and everything and all their character parts and clothing parts all labeled and documented organized selectable interchangeable being able to add layers to it layers of clothing remove layers delete articles add accessories swap them out change the color add decals and logos and things like that all different types of shit like that all pulled in wired up and pushed to the repo merge clean without clogging anything on any side"

**Scope per fighter:**
1. Fully rigged
2. Full movesets from Tekken sources (Tekken inputs):
   - Ryusan (Mina Ashido) → Lucky Chloe
   - Tobi (Mirko) → Hwoarang
   - Chatur (Rahkasa) → True Ogre
   - Pond (Tsuyu) → Raven
   - Megami (Parvati) → Jun Kazama
   - Menajerii (Vixen) → Roger Jr.
3. Stances, attacks, combos, full move lists (Tekken inputs, Tekken feel)
4. Canon moves layered on top (proprietary, fit each character)
5. Full canon (bio/story/connections)
6. Character parts + clothing parts system (see below)

## Texture Fixes (user 2026-10-23 ~07:05 CDT)

- Vixen (Menajerii): missing textures fully — get them on her
- Parvati (Megami): missing clothing textures — get them on her

## Parts/Clothing System — Full Spec

### Core operations (every clothing item)
Deletable, hideable, swappable, invisible toggle, recolorable.

### Organization
Labeled in creation suite, organized like WWE + Tekken. Use teardown files for structure.
WWE-style layer system: multiple layers for upper body, lower body.

### Categories

**Body gear:** shoes, knee pads, shin guards, kick pads, wrist guards, wrist tape, wrist items,
lower arm, upper arm, hand, fingers, fingernails

**Face:** teeth (color, types, shapes), eyes (color, shape, type), nose, mouth, eyebrows
(types), eyelashes (types), ears

**Hair:** hair color, hair dye, hairstyles, different hair parts, full hairstyle creation
(Tekken-style), selectable hair parts (WWE-style), facial hair

**Clothing:** jackets, shirts, bras, panties, underwear, trunks, different types of
bottoms/tops/pants/underwear/shirts

**Accessories:** armwear, legwear, neckwear, neck accessories, back accessories,
torso accessories, piercings (body, face — all types), earrings (different types)

**Head/face wear:** masks, face accessories, face wear, head wear, glasses

**Body art:** scars, tattoos, images, logos

**Cosmetics:** makeup (different types), eye makeup, lipstick, face paint (different
options, custom design generation)

**Morphing:** face morphing, body morphing, body part templates (WWE/Tekken-style)

**Custom creation:** ability to create and generate custom designs, logos, paints,
makeups, textures

### Sub-menu organization
All selectable, organized in sub-menus like Tekken + WWE creation suites.

### Research directive (user 2026-10-23 ~07:07 CDT, verbatim)

"really study those systems, the layouts, the organization, the UI, the user interface,
all of that, like um and with WWE and Tekken and all the stuff I mentioned and then wire
it up from the teardown files and open source and anything you can find and get a hold of
through your research uh that's 2026 industry standard or high level or anything that'll
fit really anything that will go with this no matter what it is for real"

- Deep-study WWE (2K) and Tekken creation suites: layouts, organization, UI, menus
- Pull from teardowns: WWE 2K, Tekken 7/8, Soulcalibur CaS, all fighting game creation systems
- Open source: character customization tools, UI frameworks, 3D editors
- 2026 industry standard: current, high-level, best-in-class
- Research catch-all: survey ALL games with deep customization, pull in anything missing

### Documentation law (user 2026-10-23 ~07:09 CDT, verbatim)

"make sure everything we say back and forth to each other gets documented in the repo
and pushed and merged and everything that we work on everything that we're doing is
getting pushed and merged clean without clobbering anything on either side"

- Every conversation documented in the repo, pushed, merged
- All work pushed and merged clean, no clobbering either side
