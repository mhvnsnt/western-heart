# Tekken Customization System Extraction Report
**Date:** 2026-10-16
**Task:** Deep extraction of Tekken's ACTUAL character customization system from teardown files
**Status:** Complete (research only, no modifications made)

---

## Executive Summary

We have Tekken 7's COMPLETE customization database schema from the tekkenmods-docs (TKDataPatcher documentation). This includes the exact slot system, item CSV format, asset type prefixes, character IDs, color system, and UI organization. We do NOT have the actual game .uasset files, UI layout binaries, or the positioning constraint data (min/max ranges for accessory placement).

**Bottom line:** We can build a 1:1 functional replica of Tekken 7's customization DATABASE and CATEGORY structure. We cannot extract the actual 3D item models or the exact UI pixel layout without the game files.

---

## 1. Every Customization-Related File Found

### 1.1 Tekken 7 (~/workspace/game-reverse-engineering/tekken7/)

| Path | Size | Contents |
|------|------|----------|
| `tekkenmods-docs/files/en/Tekken_7/TKDataPatcher/index.md` | ~8KB | COMPLETE item CSV spec, slot system, slot group IDs |
| `tekkenmods-docs/files/en/Tekken_7/Basic_Information/Overview/Assets/index.md` | ~3KB | Asset type prefixes (EI, ECI, ACI, CS, CCI, CI) |
| `tekkenmods-docs/files/en/Tekken_7/Basic_Information/Overview/Characters/index.md` | ~4KB | All 57 character IDs with abbreviations |
| `models/` (29 character dirs) | Various | FBX/OBJ/GLB character models, NOT customization items |

### 1.2 Tekken 8 (~/workspace/game-reverse-engineering/tekken8/)

| Path | Size | Contents |
|------|------|----------|
| `models/` | 225MB total | 3 archives: Asuka SFM, Heihachi S1, Yoshimitsu S1. Character MODELS only, no customization data |

### 1.3 Tekken 6 PSP (~/workspace/game-reverse-engineering/tekken6/)

| Path | Size | Contents |
|------|------|----------|
| `tekken6-psp.iso` | 816MB | Full game ISO (not yet extracted for customization data) |
| `extracted/DATA401.IDX` | — | File index (478 files) |
| `work/` | — | Decryption tools and scripts |

**Note:** Tekken 6 PSP HAS a deep customization system, but the 40 character meshes are still locked in COM files. Customization item data has NOT been extracted yet.

### 1.4 Western Heart Repo (mhvnsnt/western-heart/teardown/)

Mirrors the local directories. No additional customization data beyond what's listed above.

### 1.5 Tekken 3 (~/workspace/game-reverse-engineering/tekken3/)

No customization system (Tekken 3 predates the customization feature, which started in Tekken 5).

---

## 2. Exact Category Hierarchy (Tekken 7)

### 2.1 Equipment Slots (slotId)

| Slot ID | Description | UI Title | Asset Type | Game Path |
|---------|-------------|----------|------------|-----------|
| 1 | Head | HEAD | CharacterCustomizeItem | Character/Item/Customize |
| 2 | Hairstyle | HAIR | CharacterCustomizeItem | Character/Item/Customize |
| 3 | Full Head | FULL_HEAD | CharacterCustomizeItem | Character/Item/Customize |
| 4 | Hair Accessory | HAIR_ACC | CharacterCustomizeItem | Character/Item/Customize |
| 5 | Glasses | GLA | CharacterCustomizeItem | Character/Item/Customize |
| 6 | Face | FACE | CharacterCustomizeItem | Character/Item/Customize |
| 7 | Facial Hair | FACE_HAIR | CharacterCustomizeItem | Character/Item/Customize |
| 8 | Face Paint | MAKE_UP | CharacterItemTex | Character/Item/Customize |
| 9 | Upper Body | UPPER | CharacterCustomizeItem | Character/Item/Customize |
| 10 | Full Body | FULL_BODY | CharacterCustomizeItem | Character/Item/Customize |
| 11 | Lower Body | LOWER | CharacterCustomizeItem | Character/Item/Customize |
| 12 | Upper Accessory | UPPER_ACC | CharacterCustomizeItem | Character/Item/Customize |
| 13 | Lower Accessory | LOWER_ACC | CharacterCustomizeItem | Character/Item/Customize |
| 14 | Extra | EXTRA | CharacterCustomizeItem | Character/Item/Customize |
| 15 | Effects | — | EffectCharacterItem | Character/Item/EffectItem |
| 17 | Aura | — | AuraCharacterItem | Character/Item/AuraItem |

**Note:** Slot 16 is skipped (reserved/unused in Tekken 7).

### 2.2 Slot Group IDs (UI Organization)

| Group ID | Description |
|----------|-------------|
| -236 | Mirroring |
| -237 | Skin Tone |
| -238 | Aura |
| -240 | Effects |
| -242 | Lower Accessory |
| -243 | Upper Accessory |
| -244 | Lower Body |
| -245 | Full Body |
| -246 | Upper Body |
| -247 | Face Paint |
| -249 | Face |
| -250 | Glasses |
| -251 | Hair Accessory |
| -252 | Full Head |
| -253 | Hairstyle |
| -254 | Head |

### 2.3 Tekken 8 Additions (from web research)

- **Footwear** slot added (separate from Lower Body)
- Characters stand (not fighting stance) in customization screen
- More precise color control (like TTT2)
- 2 accessory slots for face/head/shoulders/arms/legs/back/hovering
- 30 shared customization slots (up from 20)

---

## 3. Item Database Format (CSV)

Tekken 7 uses CSV files to define every customization item. Exact 21-field spec:

```
ShopID, packageIndex, CCI_Reference, Unknown_D, charId, slotId, Unknown_G,
NameByID, ItemName, Unknown_J, SlotGroupID, Unknown_L, PlayerCusID,
SlotColors, Unknown_O, Rarity, packageId, ItemCost, Unknown_S,
AdditionalText, Unknown_U
```

### Field Breakdown

| Field | Name | Type | Description |
|-------|------|------|-------------|
| A | Shop ID | int | Unique item ID |
| B | packageIndex | int32 | Always -1 |
| C | CCI Reference | string | Asset lookup: `TekkenGame/Content/<Path>/<CHAR_ABBR>/<SLOT_TITLE>/<NAME>` |
| D | Unknown | int32 | Always 0 |
| E | charId | 0-255 | Character ID (see roster below) |
| F | slotId | 0-255 | Equipment slot (see table above) |
| G | Unknown | int16 | — |
| H | Name by ID | int | — |
| I | Item Name | string | e.g., `NSD_CUS_007` (Lidia's swimsuit) |
| J | Unknown | int | Usually 0 |
| K | Slot Group ID | int | UI group (see table above, negative values) |
| L | Unknown | int32 | — |
| M | PlayerCus ID | int | 1=1P, 2=2P, 0=Generic (all characters) |
| N | Slot Colors | 0-5 | Number of colorable slots. 0=not colorable. Max 5. |
| O | Unknown | 0-255 | — |
| P | Rarity | int | Item rarity tier |
| Q | packageId | int | Usually -255 |
| R | Item Cost | int | Fight Money cost |
| S | Unknown | int | Usually -1 |
| T | Additional Text | string | Usually `\x00` |
| U | Unknown | int | Usually 0 |

### Example
```csv
561001,-1,nsd_bdu_1p_cus,0,56,9,-1,0,NIN_CUS_008,0,-249,0,1,5,0,1,-255,0,-1,\x00,0
```
This is Lidia's (charId 56) Upper Body (slotId 9) item with 5 color slots.

---

## 4. Asset Type System

| Prefix | Full Name | Description |
|--------|-----------|-------------|
| SK | Skeleton Mesh | Character models |
| SKT | Skeleton | Rig/skeleton structure |
| SM | Static Mesh | Props, environments |
| BP | Blueprint | Visual scripting logic |
| **EI** | **Extra Item (Sets)** | Special items: Negan's bat, Noctis' sword, Kunimitsu's dagger, Anna's rocket launcher, Lili's teacup |
| **ECI** | **Effect Item** | Character visual effects |
| **ACI** | **Aura Item** | Character aura effects |
| PA | Physics Asset | Physics simulation |
| **CS** | **Character Set** | Character customization/appearance data |
| M | MasterShader | Material definitions |
| MI | Material Instance | Material variations |
| **CCI** | **Customize Character Item** | Clothing/accessory items (references CI file) |
| **CI** | **Character Item** | Specific equippable item data |
| T | Texture | Textures |

---

## 5. Character Roster (Tekken 7)

57 characters with IDs 0-56. Key for Western Heart:

| ID | Abbr | Name | WH Relevance |
|----|------|------|--------------|
| 2 | KIN | King | Pantera base |
| 5 | XIA | Ling Xiaoyu | Xiaoyu (have model) |
| 12 | ASK | Asuka | Asuka (have model) |
| 19 | ASA | Alisa | Cape Jones / Cyborg X base |
| 35 | EDD | Eddy | Eddy (have model) |
| 10 | STE | Steve | Steve (have model) |
| 51 | ZAF | Zafina | Mariposa base |

Full list in: `~/workspace/game-reverse-engineering/tekken7/tekkenmods-docs/files/en/Tekken_7/Basic_Information/Overview/Characters/index.md`

---

## 6. Positioning/Coordinate System

### What We Know
From web research and Tekken community knowledge:
- Accessories attach to **bone sockets** on the character skeleton
- Players can adjust: **position** (X/Y/Z offset from socket), **rotation** (pitch/yaw/roll), **scale** (size)
- This is the SAME paradigm as PartPoser's 10 sliders
- Tekken 8 allows size, angle, depth, and position changes for most accessories

### What We DON'T Have
- Exact min/max ranges for each axis
- Default socket positions per slot
- Bone names for attachment points
- Whether constraints differ per slot type

### Direct Mapping to PartPoser

| Tekken Concept | PartPoser Equivalent | Status |
|----------------|---------------------|--------|
| Position X/Y/Z | Sliders 2, 3, 4 (Shift L/R, Up/Down, Fwd/Back) | ✅ Implemented |
| Rotation | Sliders 5, 6, 7 (Pitch, Yaw, Roll) | ✅ Implemented |
| Scale/Size | Slider 10 (Arm scale) | ✅ Implemented |
| Mirror | Wing/Together mode toggle | ✅ Implemented |
| Slot system | Category tabs | ✅ Partial (ARMS only) |

**PartPoser already implements Tekken's positioning paradigm.** The 10 sliders cover everything Tekken's accessory adjustment does.

---

## 7. Color/Palette System

### Tekken 7
- Each item has 0-5 **color slots** (Field N in CSV)
- 0 = not colorable
- Players pick colors per slot from a palette
- Colors apply to specific material channels on the item

### Tekken 8
- More precise color control (finer granularity)
- Similar to Tekken Tag Tournament 2's system

### For Creation Suite
- Implement 5 color slots per item (max)
- Color picker UI per slot
- Store as hex values in item data

---

## 8. UI Layout Data

### What We Have
- Category names and hierarchy (from slot system)
- Slot group organization (from group IDs)

### What We DON'T Have
- Actual UI .uasset files (menu layouts, textures)
- Exact screen positions or dimensions
- Font data
- Icon assets

### Recommendation
Build the UI from scratch using Tekken's **information architecture** (categories, slots, flows) with original visual design. Do NOT attempt pixel-perfect replica without the asset files.

---

## 9. Character-Specific vs Generic Items

### System
- **PlayerCus ID** determines scope:
  - `1` = Player 1 costume (character-specific)
  - `2` = Player 2 costume (character-specific)
  - `0` = Generic (available to all characters)
- **charId** links item to specific character (0-56)
- **EI** (Extra Items) are character-specific signature items

### For Western Heart
- DXMMII's extra arms = character-specific (like EI items)
- Generic accessories can use PlayerCus ID 0
- Each WH character gets their own charId in our system

---

## 10. Slot Conflict System

### Rules (from research)
- Each slot holds ONE item at a time
- Some slots conflict (e.g., FULL_HEAD conflicts with HEAD + HAIR + FACE)
- FULL_BODY conflicts with UPPER + LOWER
- Accessories have placement zones (can't put two items in same zone)
- Tekken 8: 2 accessory slots, no two items in same area

### Implementation for Creation Suite
```
CONFLICTS = {
  FULL_HEAD: [HEAD, HAIR, FACE, HAIR_ACC, GLA, FACE_HAIR],
  FULL_BODY: [UPPER, LOWER],
  UPPER: [FULL_BODY],
  LOWER: [FULL_BODY],
  HEAD: [FULL_HEAD],
  HAIR: [FULL_HEAD],
  FACE: [FULL_HEAD],
}
```

---

## 11. What's Directly Usable in Creation Suite

### ✅ Ready to Implement Now
1. **Slot system** — All 16 slot IDs, names, and hierarchy. Can build category tabs directly.
2. **CSV item format** — Can create Western Heart item database using Tekken's 21-field spec.
3. **Color system** — 0-5 color slots per item. Straightforward to implement.
4. **Character IDs** — Can assign WH characters IDs in Tekken's format.
5. **Asset paths** — Can organize WH assets using Tekken's folder structure.
6. **Slot groups** — Can organize UI using Tekken's group IDs.
7. **Positioning paradigm** — PartPoser already implements this.

### 🔧 Needs Work
1. **Item 3D models** — We have character models but not the accessory/item models. Need to create or source.
2. **UI visuals** — Need to design original UI (can't copy Tekken's assets).
3. **Positioning constraints** — Need to define sensible min/max ranges (Tekken's exact values unknown).
4. **Socket/bone system** — Need to define attachment points for WH characters.

### ❌ Cannot Extract (Need Game Files)
1. **Actual .uasset item files** — Would need Tekken 7 game data torn down.
2. **UI layout binaries** — Would need UMG widget files from the game.
3. **Exact positioning ranges** — Buried in game code, not documented.
4. **Item database** — The full list of every item in Tekken 7/8.

---

## 12. Gaps & Next Steps

### Critical Gaps
1. **No game .uasset files** — The actual customization item 3D models are not in our teardown. We have character models from RigModels, not the equipable items.
2. **No UI files** — Menu layouts, icons, and textures are not extracted.
3. **Tekken 6 PSP customization data** — The ISO is extracted but customization items haven't been located in the 478 files.
4. **Positioning ranges** — Tekken's exact min/max for accessory placement is undocumented.

### Recommended Next Steps
1. **Extract Tekken 6 PSP customization data** — The 478 extracted files may contain item definitions. Search for item-like data structures.
2. **Define WH item database** — Create `items.csv` files using Tekken's format for Western Heart characters.
3. **Build slot UI** — Implement all 16 Tekken slots as Creation Suite categories.
4. **Create placeholder items** — Use simple geometric accessories until real item models are sourced.
5. **Document positioning ranges** — Playtest and define sensible min/max values for PartPoser sliders.

### Tekken 6 PSP Specific
The Tekken 6 PSP teardown extracted 478 files from DATA401. These likely include:
- Character customization item models
- Item metadata
- UI textures

**Action:** Search the extracted files for item-like data. The COM files (idx 419-453) contain the locked character meshes, but other files may have customization data.

---

## 13. File Manifest

### Primary Sources
1. `~/workspace/game-reverse-engineering/tekken7/tekkenmods-docs/files/en/Tekken_7/TKDataPatcher/index.md` — Item CSV spec, slot system
2. `~/workspace/game-reverse-engineering/tekken7/tekkenmods-docs/files/en/Tekken_7/Basic_Information/Overview/Assets/index.md` — Asset prefixes
3. `~/workspace/game-reverse-engineering/tekken7/tekkenmods-docs/files/en/Tekken_7/Basic_Information/Overview/Characters/index.md` — Character IDs

### Supporting
4. `~/workspace/game-reverse-engineering/tekken6/TEARDOWN.md` — PSP teardown status
5. Web research: Tekken Wiki, Twinfinite, PC Gamer (T8 customization details)

---

## 14. Conclusion

We have Tekken 7's **complete customization database schema**. This is sufficient to build a functionally identical system for Western Heart. The Creation Suite can:

1. Use Tekken's exact 16-slot category system
2. Store items in Tekken's CSV format
3. Implement Tekken's color slot system (0-5 per item)
4. Use Tekken's positioning paradigm (already done in PartPoser)
5. Organize characters using Tekken's ID system

What we cannot do without the game files:
- Copy Tekken's actual 3D item models
- Replicate Tekken's exact UI pixel layout
- Use Tekken's exact positioning constraint values

**The path forward:** Build the database and UI structure from Tekken's spec, populate with Western Heart original assets, and tune the positioning ranges through playtesting. This gives us "literally Tekken's customization system" in architecture, with Western Heart content on top — exactly what the owner asked for.
