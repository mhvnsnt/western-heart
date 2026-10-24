# WWF No Mercy — Teardown

## Game #3 in Western Heart Chimera Build
- **Role:** Wrestling systems, character customization, grappling animations
- **Engine:** AKI Corporation engine (same family as WCW/nWo Revenge, WrestleMania 2000, Virtual Pro Wrestling 2)
- **Platform:** Nintendo 64
- **ROM:** WWF No Mercy (Unlocked).zip from Internet Archive n64patchedwrestlingroms

## Community RE Resources (cloned locally)
- `re-docs/` — chaotix610/wwfnomercy-docs: game systems, move database, creation suite docs
- `recomp/` — Gadge64/WWFNoMercyRecomp: N64Recomp static recompilation project

## Creation Suite Architecture (from re-docs)

### Character Slots
- Each character slot has 4 attire slots
- All 4 attires share: Moves, Fighting Style, Parameters, Ally/Enemy
- Attires differ in: Profile/Music, Appearance

### Appearance System (modular parts)
- **Body:** 14 male types + 9 female types × 8 skin tones
- **Head:** 7 male + 3 female shapes
- **Face:** 98 male + 20 female textures
- **Hair:** 22 styles (+ 63 front hair options for marked styles)
- **Facial Hair:** 31 options
- **Masks/Accessories:** ~30 options
- **Ring Attire:** 5 categories (Short, Long, Wrestling, Pants, Full Body) — ~150 total
- **Upper Body:** 4 categories (No Sleeve, Sleeve S, Sleeve L, Others) — ~150 total
- **Tattoo:** 28 options
- **Gloves, Wrist Bands, Elbow Pads (L/R), Knee Pads (L/R), Feet:** modular per-limb
- **Entrance Attire + Weapons/Props:** separate layer

### Key Insight for Western Heart
The customization is FULLY MODULAR — body parts are separate meshes/textures swapped by ID.
This is the template for Western Heart's character customization system.

## Move System (from re-docs)

### Move Slots (positional/contextual)
- Front/Back grapple × Weak/Strong × 8 slots each
- Turnbuckle grapples, ground attacks, Irish whip follow-ups
- Taunts, double-team moves
- Each wrestler assigns moves from the master database to slots

### Fighting Styles
- Stance: Wrestling, Martial Arts, Shoot, Normal, Women
- Speed, Submission Skills, Recovery Rate, Endurance: parameterized
- Counter/Reversal types

### Parameters
- 10 values (Offensive/Defensive × Head/Body/Arms/Legs/Flying)
- 1-5 each, 30 points total to distribute

## Arena System
- Ring-based with ropes, turnbuckles, apron, ringside
- Different traversal than Tekken's open plane
- **Western Heart design:** This becomes the separate "Wrestling Mode"

## TODO (pending ROM download)
- [ ] Extract ROM, verify checksum
- [ ] Map file structure (N64 ROM layout)
- [ ] Extract character models (body part meshes)
- [ ] Extract animation data (grapple/move animations)
- [ ] Extract textures (attire pieces)
- [ ] Document creation suite save format (how custom characters stored)
- [ ] Test retargeting wrestling animations onto Tekken 3 models
