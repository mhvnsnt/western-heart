# Western Heart — Character Customization Research

**Owner-directed 2026-10-13.** Research on every torn-down game's character customization system, feeding the unified Create Fighter suite.

**Companion files:**
- `CUSTOMIZATION-FILES-INDEX.json` — every customization-related file in our teardowns (727 files)
- `CHARACTER-CREATION.md` — the combined WWE CAW + Tekken customization design doc
- `../moveset-library/UI-DESIGN-SPEC.md` — Create Fighter + Moveset UI blueprint
- `PARTS-INDEX.json` — master index of 3,372 extracted parts

---

## The Spectrum

Our nine teardown games fall on a customization spectrum:

| Tier | Games | System |
|---|---|---|
| **Full CAW** (create-a-fighter from scratch) | WWF No Mercy, WWE WrestleMania XIX | Body types, faces, hair, attire parts, movesets, AI, parameters |
| **Item-shop customization** (dress existing fighters) | Tekken 6, Tekken 7, Tekken Tag Tournament 2 | 4-slot item system, purchased with fight money |
| **Wardrobe loadouts** (costume+hair+glasses combos) | Dead or Alive 6 | 10 saved slots per character |
| **Costume-select only** (fixed outfits, unlock through play) | Tekken 3, DOA3, DOA4, DOA5/LR | P1/P2 or numbered costumes |
| **None** | Urban Reign, Soulcalibur II, Virtua Fighter 5 | Fixed character looks only |

**Key correction:** Soulcalibur II (PS2, 2002) has **NO character creation mode** — that debuted in Soulcalibur III (2005). SCII is character-select only.

---

## 1. WWF No Mercy (N64, 2000) — Full CAW

**Type:** Full create-a-wrestler. The deepest CAW in our set alongside WMXIX.

**System** (from `teardown/wwf-no-mercy/re-docs/docs/ui/menus/edit-a-superstar.md`, 722 lines):

Six pages of settings per character slot:
1. **Profile/Music** — Name, Short Name, Alias (attitude meter), 64×64 face picture, Height (5'0"–7'11"), Weight (100–599 lbs), entrance Music, Titantron video
2. **Appearance** — Body (14 male + 9 female types × 8 skin tones), Head (7M+3F shapes), Face (28M+20F textures), Hair, Attire parts
3. **Moves** — 176-slot unified moveset assignment
4. **Fighting Style** — AI behavior tendencies
5. **Parameters** — Offense/defense 1–10 per zone (Head/Body/Arms/Legs/Flying)
6. **Ally/Enemy** — relationships

**Attire slots:** 4 per character. All four share Moves/Fighting Style/Parameters/Ally-Enemy; Profile-Music and Appearance differ per attire.

**Extracted assets:**
- 5,029 PNG textures (`teardown/wwf-no-mercy/textures/rom/`) — ring attire, entrance attire, faces, hats, accessories
- 3,570 OBJ models (`teardown/wwf-no-mercy/models/`) — body parts, face/hair, attire parts, weapons
- 118 CAW faces visually verified
- 48 face/hair meshes

**File harvest:** 702 customization-related files in `teardown/wwf-no-mercy/` (see index).

---

## 2. WWE WrestleMania XIX (GameCube, 2003) — Full CAW

**Type:** Full create-a-wrestler. Deeper tree than No Mercy.

**System** (from `teardown/wwe-wrestlemania-xix/docs/CAW-EDIT-DATA-WMXIX.md`):
- Parametric body system (no blank mesh — starts from body-type selection)
- 2,690 CAW edit_data files: 476 upper body, 120 lower body, 50 shoes, 48 gloves, 154 faces, 156 hair, 140 gears, 94 accessories, 1,478 textures, 8 color palettes
- YOBJ mesh format, YANM animations

**Default CAW base:** Documented in `customization/parts/base/README.md`. This is the "New Fighter" starting point for Western Heart's Create Fighter.

**Extracted assets:** All in `customization/parts/wmxix/` (already in western-heart, not duplicated).

---

## 3. Tekken 6 (PSP/PS3, 2007/2009) — Item-Shop Customization

**Type:** Full item shop. Community consensus: the best customization in the series.

**Currency:** Fight Money ("G") — earned per battle in any mode.

**UI flow** (console): Player Settings → CUSTOMIZE → choose character → EQUIP (owned) or BUY (purchase + equip). Arcade bought blind at character select with no preview.

**Slot categories** (~20+ slots — richer than T7):
- Head, Glasses, Face, Other–Upper Body, Upper Body–Inner, Upper Body–Outer, **Arms, Hands** (separate!), **Lower Body, Feet** (separate!), Other–Head, Upper Body–Add., Back, Waist–Right, Waist–Left, Effect, Rage, Aura
- Hair–Base, Hair–Front (Left), Hair–Front (Right), Hair–Front (Left & Right), Hair–Back, Hair Color
- Default Costume Color 1/2/3 (three color channels)

**Unique to T6: hands and feet are SEPARATE slots** (later games merged them).

**Notable mechanics:**
- **Item Moves:** certain items (guns, sledgehammer, naginata, magic wands, row-of-ducks followers) trigger special moves/KOs in battle
- **Rage/Aura colors:** rage colors (white, yellow, black, fire, lightning, smoke) via "Super Roulette"; auras and ki effects purchasable
- **Scenario Campaign attributes:** items found in Scenario Campaign carry stat buffs; shop-bought copies are cosmetic only — duplicates can have different attributes
- Full color system on default costume (3 channels) + hair color — fans call T6 the customization peak

**Honest limitation:** 3D item meshes never extracted (PSP encryption). System documented from public sources + Tekken 6 design.

**Western Heart role:** The richest slot schema — T6's subdivisions (Inner/Outer upper, Waist L/R, Hands, Feet) map as subdivisions of T7's Upper/Lower/Head/Extra slots in our unified model.

---

## 4. Tekken 7 (2015/2017) — Item-Shop Customization

**Type:** Item-shop customization, refined from T6. More granular slots than T6's 4-slot system.

**Exact slot IDs** (from tekkenmods-docs TKDataPatcher — the actual game data, ideal for our unified model):

| Slot ID | Slot name | Internal |
|---|---|---|
| 1 | Head | HEAD |
| 2 | Hairstyle | HAIR |
| 3 | Full Head | FULL_HEAD |
| 4 | Hair Accessory | HAIR_ACC |
| 5 | Glasses | GLA |
| 6 | Face | FACE |
| 7 | Facial Hair | FACE_HAIR |
| 8 | Face Paint | MAKE_UP (texture type) |
| 9 | Upper Body | UPPER |
| 10 | Full Body | FULL_BODY |
| 11 | Lower Body | LOWER |
| 12 | Upper Accessory | UPPER_ACC |
| 13 | Lower Accessory | LOWER_ACC |
| 14 | Extra | EXTRA |
| 15 | Effects | (effect items) |
| 17 | Aura | (aura items) |

Plus settings: Skin Tone, Mirroring, Character Panel (VS-screen graphic).

**Item classes** (distinct data types): `CharacterCustomizeItem` (mesh), `CharacterItemTex` (face paint — texture type), `EffectCharacterItem`, `AuraCharacterItem`.

**Mechanics:**
- Each item costs Fight Money; buy then equip (two-step)
- **Conflict system:** overlapping zones can't combine (full-face mask blocks make-up)
- **10 save slots per character**; press Square at select to choose outfit
- Per-item color edit (up to 5 color slots; 0 = not colorable)
- Rarity stars 0–5 per item; Mirroring toggle flips asymmetric items
- Unlock: 2,000 total wins OR Treasure Battle chests; Heist Battles (mirror matches) unlock character-specific pieces; DLC characters unlock only via Treasure Battle
- Season Pass 2/3 added sets; v5.10 added free Character Panel Set + Favorite costume registration
- **No Item Moves** (unlike T6); **no separate hands/feet slots** (merged)

**Western Heart role:** Most recent Tekken customization we have — the base for Create Fighter's Tekken layer per UI-DESIGN-SPEC.md. The slot ID table (1–17) is the numeric spine for our unified item model.

---

## 5. Tekken Tag Tournament 2 (2011/2012) — Item-Shop + Combot

**Type:** Item-shop customization + Fight Lab/Combot (customizable fighter).

**Standard customization:** Full item shop, T6-derived. **Key structural change vs T6:** tops+gloves (hands) merged into single upper sets; bottoms+footwear (feet) merged into single lower sets. ~13 slots per character (10 + 3 overwritable).

**Currency:** Fight Money ("G"). Online wins can pay 2x/3x via lucky boxes; arcade "Jackpots" gauge toward 1,000,000 G.

**Unlocks:** Shop purchases + **Ghost Battle** (offline endless) special items + guest-artist DLC costume sets.

**Notable:** Decals (console, not 360), character panels, manga hit effects, Tekken Tunes (per-stage music), Item Moves return.

**Fight Lab / Combot** (the standout):
- Tutorial-as-mini-games starring **Combot**, Lee Chaolan's (as Violet) fighting robot
- **Moveset customization:** development points buy moves from other fighters — Nina's Blonde Bomb + Paul's Phoenix Smasher + Heihachi's Wind God Fist on ONE body. Split into Development Techniques (command moves) and Limited Techniques (special moves); same command strings can't collide
- Some moves change Combot's appearance (True Ogre's moves add tail/wings)
- Moves saved to **Combot Memory slots 1–4**; appearance customizable through normal customization
- Playable offline + non-ranked online only (never ranked)

**Why it matters for Western Heart:** Combot is the closest any Tekken game came to a chimera fighter — moves from different characters on one body. This is the direct precedent for Western Heart's moveset library (176-slot system where any move can go in any eligible slot).

**Roster note:** ~120+ attires — largest alt-costume library in our set. Dr. Bosconovitch is the Wii U-exclusive 60th fighter.

---

## 6. Tekken 3 (1997/1998) — Costume Select Only

**Type:** NO customization system. Punch button = outfit 1 (P1), kick button = outfit 2 (P2), per arcade manual.

**Third costumes** (unlockable, Start button):
- Law's Yellow Suit — beat game with Law AND Paul
- Gun-Jack's Jack-2 Costume — select Gun Jack 10+ times
- Eddy/Tiger — beat Arcade with 16 different characters
- Jin/Xiaoyu School Uniforms — play with character 50+ times
- Anna's Striped Suit — play with Anna 25+ times

No currency, no recoloring, no menus — pure unlock-then-button-press. (Anna is Nina's 3P costume in arcade.)

**Note:** The `teardown/tekken3/tools/tekken3recompiled/Outfit-Slots.md` documents a FAN MOD (tekken3recompiled) that adds an outfit carousel — this is NOT original Tekken 3.

**Files:** 19 outfit-related files in the recompiled tools (mod project, not original game data).

---

## 7. Dead or Alive 6 (2019) — Wardrobe Loadouts

**Type:** DOA Central Wardrobe — the series' only real customization.

**System:**
- Per character: **Costume + Hairstyle + Glasses + Title** (title = two combined phrases)
- **10 saved slots per character**, selectable at character select
- Hairstyles (~5,000 coins) and glasses (~2,000 coins) bought with Player Points
- Costumes use a parts system: random drops from Quest/Arcade/Survival → collect all parts → spend coins to purchase
- DLC costumes arrive fully unlocked (paid)

**Mechanics doc:** `teardown/dead-or-alive-6/DOA6-MECHANICS.md`

---

## 8. Dead or Alive 3/4/5 (2001–2015) — Costume Select Only

**Type:** Fixed outfits, unlocked through play. No customization.

| Game | Costumes | Unlock |
|---|---|---|
| DOA3 | ~3/char | Silver Xbox survival drops, special conditions |
| DOA4 | 5–8/char | One per Story Mode clear |
| DOA5/LR | ~20 base + DLC | One per Arcade/Time Attack/Survival run |

Button-triggered variants (hair up/down, glasses on/off) via select-screen button holds. No color picker, no parts mixing.

---

## 9. Soulcalibur II (PS2, 2002) — None

**Type:** Character-select only. **NO character creation.**

**Correction:** Character Creation debuted in Soulcalibur III (2005), not SCII. SCII contributes a *progression/economy pattern*, not a creation flow:
- **Weapon Master mode:** name your fighter, RPG quest, EXP → cosmetic rank titles, Gold → shops
- **Weapon shops:** ~12 unlockable weapons per character with real gameplay attributes (attack, defense, health recovery, special effects, joke weapons)
- A few characters have purchasable alternate costumes

**SCIII Create-A-Soul** (for the unified model's future — not in our teardown set):
- Flow: Gender → **Job/class** (Barbarian, Dancer, Monk, Saint, Ninja + unlockables) → 20+ equipment slots → dual-channel colors → face/voice → **Discipline (determines moveset)** → weapon → name/personality
- **The famous mechanic:** "Soul of X" disciplines give created fighters the EXACT moveset of a main-roster character (Soul of Mitsurugi, Soul of Taki, etc.); custom disciplines (Katana, Nunchaku, Tambourine...) are job-gated originals
- Level 1–30 per job unlocks more disciplines; equipment feeds a hidden personality/alignment system
- Ancestor of every later Soul creation mode (SC4 physique sliders + stat gear; SC5 height/power trade-offs; SC6 16 races)

**Roster note:** 25 fighters including Heihachi Mishima (PS2 guest — Tekken crossover).

**Teardown:** `teardown/soulcalibur-2/TEARDOWN.md` (PR #49). PS2 proprietary filesystem — extraction needs dedicated RE.

---

## 10. Urban Reign (PS2, 2005) — None

**Type:** Character-select only. Zero customization.

**Verified:** No costume menu, no color edit, no create-a-fighter, no alt outfits. Progression is character unlocks (60+ fighters), weapons, modes, and max stats.

**UI files:** `teardown/urban-reign/ui/character-select/` (face.vgs, select.ppk) — character select screen only.

---

## 11. Virtua Fighter 5 (PS3) — None (assumed)

**Type:** Character-select only. VF series has costume variations but no creation mode.

**Teardown:** `teardown/virtua-fighter-5/` — 7 priority fighters extracted.

---

## Unified Model — Western Heart Create Fighter

Combining all systems into one suite (see `CHARACTER-CREATION.md` and `UI-DESIGN-SPEC.md`):

### Layers (bottom to top)
1. **WWE CAW base** — Body type → Skin → Head → Face → Hair (No Mercy/WMXIX)
2. **WWE attire parts** — 3,372 extracted parts in `customization/parts/`
3. **Tekken item overlay** — T7's 17-slot system (Head 1 → Aura 17) with T6's subdivisions (Inner/Outer upper, Waist L/R, Hands, Feet) as sub-slots; item classes: mesh / face-paint-texture / effect / aura
4. **DOA6 wardrobe concept** — 10 saved loadout slots per fighter
5. **SCIII inspiration** — (Future) job → discipline borrowed movesets; Combot precedent for cross-roster move mixing

### Data model
```
Fighter {
  profile: {name, short_name, alias, height, weight, soul, element, land},
  caw: {body_type, skin_tone, head_shape, face_id, hair_id, attire_parts: [...]},
  tekken_items: {
    head: [...], hair: [...], full_head: [...], hair_acc: [...],
    glasses: [...], face: [...], face_hair: [...], face_paint: [...],  // texture class
    upper: [...], full_body: [...], lower: [...],
    upper_acc: [...], lower_acc: [...], extra: [...],
    effects: [...], aura: [...],  // effect/aura classes
    skin_tone, mirroring, panel
  },
  loadouts: [ ... ],  // DOA6-style: 10 saved slots
  moveset: {...},     // 176-slot system (Combot precedent)
  ai_style: {...},
  parameters: {...}
}
```

### Socket system
WWE CAW parts and Tekken 4-slot items use the SAME socket system — one unified wardrobe, no game-of-origin distinction for the player.

---

## File Harvest Summary

**727 customization-related files** in `teardown/` (see `CUSTOMIZATION-FILES-INDEX.json`):
- No Mercy: 702 files (textures, models, docs)
- Tekken 3: 19 files (recompiled mod tools)
- WMXIX: 4 files (catalogs, docs)
- TTT2/WWE: 1 file each

**3,682 files** already in `customization/` (wrestling CAW parts — referenced, not duplicated).

**Key documents:**
- `teardown/tekken6/TEARDOWN.md` — T6 4-slot system design
- `teardown/wwf-no-mercy/re-docs/docs/ui/menus/edit-a-superstar.md` — No Mercy CAW bible (722 lines)
- `teardown/wwe-wrestlemania-xix/docs/CAW-EDIT-DATA-WMXIX.md` — WMXIX edit data
- `teardown/wmxix/caw-parts/CATALOG.md` — WMXIX parts catalog
- `customization/CHARACTER-CREATION.md` — combined design doc
- `moveset-library/UI-DESIGN-SPEC.md` — Create Fighter UI blueprint
