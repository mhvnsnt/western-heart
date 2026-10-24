# Broad Customization Research — Best Systems in ALL Games
**Date:** 2026-10-23  
**Owner directive (verbatim):** "do research on what games have the most freedom in character customization and morphing and clothing items and all of that stuff... it doesn't have to be wrestling games or fighting games but any games that have customization studios and suites."

## Winners by Category

### 🏆 Most Morphing Freedom — Black Desert Online
- Universally cited as "the best character creation system of all time" / "uncontested champion of sheer aesthetic depth and control"
- Sliders for nearly every part of the body (nose, chin, thighs, calves, waist...)
- **Direct manipulation**: touch a point on the face/body and drag it, or use sliders
- Eyelash LENGTH slider (not just type)
- Per-section hair editing: cut/extend sections, curl degree, asymmetric lengths, per-section colors
- **What to pull**: direct-manipulation UI paradigm, slider density/organization, hair-section editing

### 🥈 Most Detailed Physical Creator — Dragon's Dogma 2
- "The most detailed physical creator ever shipped" (PlayStation Universe)
- Nearly every part of physical appearance tweakable, down to body hair type
- **Body sliders affect gameplay**: height→reach, weight→climb speed/stamina
- Separate character-creation app; community shares creations
- **What to pull**: body slider taxonomy, the build-affects-animation concept (fighter builds affecting move animations)

### 🥉 New Gold Standard (2025) — inZOI
- UE5 photoreal, drag-and-pull facial sculpting "with precision rarely seen in the genre"
- Modern culturally-relevant fashion, makeup, accessories
- Traits/ambitions/personality affecting behavior
- **What to pull**: drag-and-pull sculpting UI, modern fashion parts library organization

### 🏆 Most Clothing Items — Saints Row (The Third / series)
- "Overwhelming amount of clothing options" — stores each with different stock (preppy vs casual vs...)
- Sliders pushed "into the unhinged range" — extreme body proportions
- Even walk style customizable
- **What to pull**: clothing store organization by style, layering system, extreme slider ranges

### 🏆 Biggest Wardrobe (RPG) — Cyberpunk 2077
- "Insanely detailed" — cyberware, body tweaks, voice, style; vast near-future fashion wardrobe
- Style-driven clothing system where appearance reflects build
- **What to pull**: wardrobe organization, style-as-identity system

### 🏆 Layered Armor System — Monster Hunter Wilds (2025)
- Most detailed MH creator ever: facial structures, scars, tattoos, voice, personality expressions
- **Layered armor creates thousands of unique designs** — armor pieces as fashion layer over stats
- Even the Palico companion is customizable
- **What to pull**: layered-armor-as-fashion system (maps directly to our attire ladder)

### Notable Others
| Game | System strength | What to study |
|------|----------------|---------------|
| **Starfield** | Bethesda's deepest: tons of precise face sliders, trait system with gameplay impact | Slider precision, trait→gameplay |
| **Fallout 4** | Face sculpting with real-time influence, scar/facial structure detail | Sculpting UI |
| **Dragon Age: The Veilguard** | BioWare's deepest creator: face, hair, body, skin, tattoos, scars, fantasy races | Fantasy-race morphing (relevant for our non-human fighters) |
| **APB Reloaded** | Custom clothing graphics creator (upload your own designs), deep body sliders + tattoos | Player-created clothing graphics → our decal/logo system |
| **GTA Online** | Parent-blend face creator (blend two parents → unique face) | Genetic blending → random fighter generator |
| **The Sims / Project Rene** | Quantum leap promised in Create-A-Sim, genetics for offspring | Genetics system for NPC/variant generation |
| **Elden Ring** | Minimalist done right — face + class + name → millions of unique builds | Less-is-more lesson: don't overwhelm |
| **SmackDown vs Raw 2006-07** | Best WWE morphing (see MORPHING-FREEDOM-RESEARCH.md) | Per-area sliders |

## What Gets Pulled Into WH Creation Suite

### Study (design reference)
1. **Black Desert** — direct manipulation UI, slider organization, hair-section editing
2. **Saints Row** — clothing store organization, extreme slider ranges, layering
3. **inZOI** — drag-and-pull sculpting, modern fashion library
4. **Dragon's Dogma 2** — body slider taxonomy, build-affects-animation

### Pull assets/data where available
1. **APB-style custom clothing graphics** → our decal/logo creation tools (already in spec)
2. **GTA-style parent blending** → random fighter generator
3. **MH-style layered armor** → our attire ladder system (already planned)

### Implementation priority
1. BDO direct-manipulation UI paradigm on top of MB-Lab engine (already planned)
2. Saints Row-style clothing store organization for parts library
3. DD2-style body slider taxonomy merged with SvR slider taxonomy
4. Parent-blend random generator (phase 5)

## Combined Master Plan

```
WH CREATION SUITE =
  SvR 2007 per-area sliders          (WWE morphing freedom)
  + BDO direct manipulation          (touch-and-drag sculpting)
  + Saints Row clothing organization (stores by style, extreme ranges)
  + MB-Lab parametric engine         (hundreds of targets, fuzzy logic)
  + 2K26/2K25 parts library          (thousands of meshes/textures)
  + APB custom graphics              (player-made decals/logos)
  + GTA parent blending              (random fighter generator)
```

## Sources
- XModHub top 30 character creation games (2025)
- G2A 27 games with character creation 2026
- XboxPlay best character customization
- Eneba 22 games with character creation 2026
- GameRant: RPGs better than Cyberpunk, best single-player creators
- GameRanx best customization games
- CBR: RPGs ranked, fantasy RPGs, most player customization
- PSU: why character creation matters
- Player.One: 8 best systems 2026
- NeoGAF character creator depth thread
