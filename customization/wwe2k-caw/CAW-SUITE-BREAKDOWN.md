# WWE 2K Create-A-Superstar (CAW) Suite — Full Breakdown for Western Heart

**Source:** WWE 2K19 (most recent fully documented) + WWE 2K14 (parts extraction in progress)
**Purpose:** This is the character creation system the owner wants in Western Heart's Create Fighter suite.
**Date:** 2026-10-13

---

## 1. Creation Suite Overview

The WWE 2K Creation Suite is the deepest character creator in sports gaming. It has 8 major editors:

| Editor | What it does |
|--------|--------------|
| **Custom Superstar** | Full CAW — body, face, attire, moveset, entrance, victory, AI |
| **Custom Entrance** | Entrance choreography, lighting, pyro, Titantron video |
| **Custom Victory** | Face AND Heel victory scenes (separate) |
| **Custom Moveset** | Hundreds of moves across all positions |
| **Custom Championship** | Belt designer — strap to plate |
| **Custom Arena** | Arena designer |
| **Custom Show** | Brand/show creator for Exhibition + Universe |
| **Custom Video** | Titantron video editor (record highlight reels in-match) |
| **Custom MITB** | Money in the Bank briefcase designer |

---

## 2. Custom Superstar — Menu Structure

### 2.1 Personal Info
- Name, nickname, hometown, gender (male/female)
- **Crowd Reaction:** Face / Heel / Tweener — affects victory scenes, crowd audio, MyCareer storylines
- Weight class (see §5)
- Fighting style (see §6)

### 2.2 Appearance

**Head/Face:**
- Face morph sliders (dozens: jaw width, cheek depth, brow, nose, eyes, mouth, chin, ears)
- Skin tone (multiple shades)
- Facial hair (beards, goatees, stubble — layered)
- Hair styles (100+ options, layered on head)
- Makeup / face paint / masks
- Eyes (color, shape)

**Body:**
- Body type presets (8+ base bodies)
- Body morph sliders: height, weight, muscle definition, shoulder width, chest, waist, arms, legs
- Skin textures (muscle definition overlays)
- Tattoos (layered, placeable, scalable, rotatable — full body canvas)

**Attire (layered system):**
The attire system uses **layers** — each body region accepts multiple stacked items:
- Head: hats, masks, headbands, glasses
- Upper body: shirts, jackets, vests, singlets, bare
- Arms: gloves, wrist tape, elbow pads, arm bands (left/right independent)
- Hands: (separate slot)
- Lower body: pants, tights, shorts, trunks
- Legs: knee pads, shin guards (left/right independent)
- Feet: boots, shoes (separate slot)
- Accessories: belts, chains, jewelry

**Key 2K19 features:**
- **Attire Randomizer** — one button builds a complete matching outfit
- **Mirror Attire** — copy left-side items to right (retains logos, colors, materials)
- **Block Bodies** — Minecraft-style blocky body option
- **Per-item color** — every attire piece has independent color channels
- **Material editor** — fabric, leather, metal, matte finishes per piece
- **Logo placement** — custom logos placeable on any attire piece, scalable/rotatable

### 2.3 Moveset
- Hundreds of moves across positions: standing, grappling, ground, corner, apron, diving, running
- **Preset movesets** based on real wrestlers (e.g., "The Suplex Machine" = Tazz)
- **Quick Edit** fighting style templates
- Taunts (4 slots), victory scenes (face + heel separate)

### 2.4 Entrance
- Motion (walk, run, etc.)
- Titantron video (custom or preset)
- Lighting, pyro, camera angles
- Music

### 2.5 AI / Tendencies
- AI behavior sliders (how the CPU plays your CAW)
- Signature/Finisher assignments

### 2.6 Attributes
- Overall rating (calculated from attributes)
- Individual attributes: striking, grappling, submissions, speed, stamina, durability, etc.
- Skills and Abilities (paybacks, resiliency, etc.)

---

## 3. Body Morph System (Technical)

The CAW body uses **parametric morph targets** on a base mesh:
- **Base templates:** Male default (slot 256), Female default (slot 257)
- **Morph sliders** adjust vertex positions proportionally
- **Muscle definition** is a texture overlay, not geometry
- **Height/weight** scale the skeleton, not just the mesh

**File locations (WWE 2K19):**
```
pac/edit/bbtemplate.pac    — body templates
pac/edit/default.pac       — default parts
pac/edit/edit.pac          — edit mode parts
pac/edit/sample.pac        — sample parts
pac/edit/ch/               — character parts (masks, normals)
pac/edit/body/             — body part meshes
pac/profile/profile_dat.pac — CAW metadata, hometown data
```

**CAW save format:** `.pofo` files (extracted from game memory via Custom Character Tools)
**Texture format:** `txXXXXX.pac` (CAW defaults use slots 256=male, 257=female)

---

## 4. Face / Heel / Tweener Alignment

| Alignment | Crowd reaction | Victory scenes | MyCareer impact |
|-----------|---------------|----------------|-----------------|
| **Face** (good guy) | Cheers | Heroic celebrations | Fan-favorite storylines |
| **Heel** (bad guy) | Boos | Arrogant/taunting celebrations | Villain storylines |
| **Tweener** | Mixed | Neutral | Can go either way |

**Western Heart mapping:** This maps directly to our character alignment system. Pantera = Face, Diablo = Heel, etc.

---

## 5. Weight Classes

| Class | Weight range | Gameplay effect |
|-------|-------------|-----------------|
| **Cruiserweight** | Under 205 lbs | Faster, can be lifted by anyone, aerial moves |
| **Heavyweight** | 205+ lbs | Standard, balanced |
| **Super Heavyweight** | 300+ lbs (men) | Cannot be lifted by cruisers, power moves |
| **Women's Heavyweight** | Up to 280 lbs | Added in 2K19 |

**Gameplay rule:** A cruiserweight with low lifting strength CANNOT pick up a heavyweight for slam moves. The game swaps in alternative "struggle" animations.

---

## 6. Fighting Styles (WWE 2K19)

**5 main styles, each with 2 sub-styles:**

### Powerhouse
- **Beast:** Grapple style, damage recovery
- **Hero:** Reversal offense, strike speed
- *Attributes:* Power, Grappling

### Cruiser
- **Technician Cruiser:** Grapples, submissions
- **Luchador:** Aerial combat
- *Attributes:* Speed, Agility

### Technician
- **UK Strong Style:** Arm power, environmental offense
- **Shooter:** Submission, stamina
- *Attributes:* Technique, Grappling

### Striker
- **Brawler:** Movement, outside-the-ring combat
- **Strong Style:** Leg power, durability
- *Attributes:* Striking (highest damage), Stamina

### Giant
- **Monster:** Durability, power
- **Big Man:** Agility, aerial offense
- *Attributes:* Power, Toughness

**Western Heart mapping:** These map to our fighter archetypes. A Tekken-style fighter = Striker/Brawler. A grappler = Powerhouse/Beast.

---

## 7. What We're Extracting

### From WWE 2K14 (1.17GB, downloading):
- [ ] `pac/edit/` — all CAW part meshes and textures
- [ ] Base male/female body templates
- [ ] Hair, attire, accessory parts catalog

### From WWE 2K19 (47GB, TeraBox pipeline):
- [ ] `pac/edit/*.pac` — complete CAW parts (newer generation)
- [ ] `pac/profile/profile_dat.pac` — CAW metadata structure
- [ ] Updated body morph targets

### Documentation (this file):
- [x] Full menu structure
- [x] Fighting styles + sub-styles
- [x] Weight classes + gameplay effects
- [x] Face/Heel/Tweener alignment
- [x] File locations for extraction
- [x] .pofo save format reference

---

## 8. Integration with UNIFIED-UI-SPEC.md

The WWE 2K CAW suite becomes the **BODY tab** in Western Heart's Create Fighter:
- Body morph sliders → BODY tab, "Physique" section
- Attire layers → ATTIRE tab (merged with Tekken item system)
- Fighting style → FIGHTER INFO tab (informs base stats)
- Weight class → FIGHTER INFO tab (affects grapple interactions)
- Face/Heel → PERSONALITY tab (affects story mode + crowd)
- Moveset editor → MOVESET tab (already spec'd)

**Design principle:** Tekken's full-screen preview stays. WWE's depth fills the menus.

---

## Sources
- WWE 2K19 PC Online Manual (2K Games, official)
- WWE 2K Creation Suite blog (2K, via Fightful)
- SmackTalks.org modding community (pac/edit structure, .pofo format, CAW slots)
- GamingBolt WWE 2K19 Guide (fighting styles)
- Bleacher Report MyCareer guide (fighting style attributes)
- CriticalClub (weight classes, climbing mechanics)
