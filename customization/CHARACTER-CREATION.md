# Western Heart — Character Creation Suite

**Combined from:** WWF No Mercy CAW + WWE WrestleMania XIX CAW + Tekken 6/7/TT2 customization.

The owner directive: a full character customization suite just like the WWE games and Tekken games combined.

---

## 1. Profile

From No Mercy / WMXIX (re-docs `edit-a-superstar.md`):

| Field | Range / Options |
|---|---|
| Name | Free text |
| Short Name | Abbreviated display name |
| Alias | Shown on in-match meter (blank = Short Name) |
| Picture | 64x64 PNG, face, transparent background |
| Height | 5'0" – 7'11" |
| Weight | 100 – 599 lbs |
| Music | Entrance theme (audio file reference) |
| Titantron | Entrance video (video file reference, optional) |

**Western Heart addition:** Soul assignment (which of the Nine Souls, if any), Element (Wood/Fire/Earth/Metal/Water), Land of origin.

---

## 2. Appearance (WWE CAW system)

### Body
- **Body type:** 14 male + 9 female types (No Mercy: Skinny 1/2, Medium 1/2, Thick 1/2, Fat 1/2, Austin, HBK, Rikishi, Rock, Hairy 1/2 / Chyna, Fit 1-4, Grannie, Jackie, Petit 1/2)
- **Skin tone:** 8 tones (#f7c2a1 through #541910)
- **Western Heart extension:** Tekken body proportions (tall/lanky King frame vs stocky Ganryu frame) as additional body-type options

### Head & Face
- **Head shape:** 7 male + 3 female options
- **Face:** 28 male + 20 female face textures
- **Extracted assets:** 118 CAW faces in `teardown/wwf-no-mercy/textures/rom/` (98M + 20F, visually verified), 48 face/hair models in `teardown/wwf-no-mercy/models/face/`

### Hair
- 48 face/hair meshes extracted (`teardown/wwf-no-mercy/models/face/`)
- WMXIX: 1,200 YOBJ CAW meshes in `teardown/wmxix/caw-parts/` (hair, gear, accessories)

### Attire Parts
- **220 CAW body parts** (`teardown/wwf-no-mercy/models/body_parts/`)
- **Attire parts** (`teardown/wwf-no-mercy/models/attire_parts/`) — 2,431 wrestler attire meshes
- **Weapons** (`teardown/wwf-no-mercy/models/weapon/`) — 34 weapon models
- **WMXIX edit_data:** 2,690 files cataloged (`teardown/wmxix/caw-parts/CATALOG.md`) — 1,470 textures, 1,200 meshes

### Tekken Customization Layer (Tekken 6/7 system)

From `teardown/tekken6/TEARDOWN.md` — Tekken uses a **4-slot layered system** on top of the base model:

| Slot | Categories |
|---|---|
| Head | Hats, helmets, masks, glasses, hairstyles |
| Upper Body | Jackets, shirts, armor, tattoos |
| Lower Body | Pants, skirts, belts, shoes |
| Other | Auras, effects, weapons, companions |

**Technical:** Items are separate meshes attached to named bone anchor points (sockets). Layered rendering on top of base model. Stored as item-ID lists per slot per character.

**Western Heart implementation:**
1. Define socket points on each fighter's rig (`head_socket`, `hand_L`, `hand_R`, `back`, `waist`, `feet`)
2. WWE CAW parts and Tekken customization items both attach via the same socket system
3. Player loadout = `{caw_parts: [...], tekken_items: {head: [...], upper: [...], lower: [...], other: [...]}}`
4. Render as additional mesh layers on the base character

---

## 3. Moves (see MOVE-SLOTS.json)

Moves are assigned per slot using the unified 176-slot system. See `movesets/MOVE-SLOTS.json` and `movesets/MOVE-DATABASE.json`.

No Mercy rule preserved: all four attire slots share the same Moves, Fighting Style, Parameter, and Ally/Enemy — only Profile/Music and Appearance differ between attires.

---

## 4. Fighting Style

From No Mercy CAW:
- AI behavior tendencies (aggression, grapple vs strike preference, high-flyer tendency, etc.)
- How the character acts and what they do in-ring

**Western Heart extension:** Tekken fighting archetype (rushdown, turtle, grappler, zoner, stance-dancer) as a parallel axis.

---

## 5. Parameters

From No Mercy CAW — offensive/defensive strength per body zone:

| Zone | Offense (1-10) | Defense (1-10) |
|---|---|---|
| Head | | |
| Body | | |
| Arms | | |
| Legs | | |
| Flying | | |

**Western Heart extension:** Tekken-style frame data lives in the move entries (damage, startup frames, hit level). Parameters scale the base damage.

---

## 6. Data Format

```json
{
  "profile": {
    "name": "PANTERA",
    "short_name": "PANT",
    "alias": "The Black Panther",
    "height": "6'2\"",
    "weight": 240,
    "music": "entrance/pantera-theme.mp3",
    "titantron": "entrance/pantera-tron.mp4",
    "soul": "TOU",
    "element": "Wood",
    "land": "Tree of Life"
  },
  "appearance": {
    "body_type": "tekken_king_frame",
    "skin_tone": "#8a5240",
    "head_shape": "male_3",
    "face_texture": "teardown/wwf-no-mercy/textures/rom/face_023.png",
    "caw_parts": ["body_parts/torso_014.obj", "attire_parts/pants_032.obj"],
    "tekken_items": {
      "head": ["panther_head_v2"],
      "upper": ["tribal_paint_gold"],
      "lower": ["purple_tights"],
      "other": ["tail_rig"]
    }
  },
  "moveset": "movesets/pantera-moveset.json",
  "fighting_style": {"archetype": "grappler", "aggression": 8, "high_flyer": 3},
  "parameters": {
    "head": {"offense": 7, "defense": 8},
    "body": {"offense": 8, "defense": 9},
    "arms": {"offense": 9, "defense": 7},
    "legs": {"offense": 6, "defense": 7},
    "flying": {"offense": 4, "defense": 5}
  }
}
```

---

## 7. Asset Inventory

**All CAW parts now consolidated in `customization/parts/` — 3,372 parts total.**

| Source | Parts | Location |
|---|---|---|
| WMXIX CAW (all categories) | 2,690 files | `customization/parts/wmxix/` |
| No Mercy body parts | 220 meshes | `customization/parts/no-mercy/body_parts/` |
| No Mercy faces (textures) | 146 PNGs | `customization/parts/no-mercy/faces/` |
| No Mercy face/hair (meshes) | 48 meshes | `customization/parts/no-mercy/face/` |
| No Mercy skins | 233 PNGs | `customization/parts/no-mercy/skins/` |
| No Mercy weapons | 34 meshes | `customization/parts/no-mercy/weapon/` |
| Master index | 3,372 entries | `customization/parts/PARTS-INDEX.json` |
| Default base docs | — | `customization/parts/base/README.md` |

### By slot (from PARTS-INDEX.json)

| Slot | Count | Description |
|---|---|---|
| upper_body | 476 | Shirts, jackets, armor, tops |
| faces | 348 | Face meshes + face textures |
| skins | 233 | Skin tone textures |
| bodies | 220 | Body part meshes |
| hair | 156 | Hair styles |
| gears | 140 | Equipment, belts, gear |
| lower_body | 120 | Pants, shorts, skirts |
| accessories | 94 | Wrist, knee, elbow pads, misc |
| shoes | 50 | Boots, shoes |
| gloves | 48 | Gloves, hand gear |
| colors | 8 | Color palettes |
| textures | 1,478 | Raw textures (to be sorted into slots) |
| attire | 1 | Attire meshes |

---

## 8. "New Fighter" Pipeline

This is the exact flow when a player hits **Create New Fighter** in Western Heart
(worker 38 menu pass, 2026-10-22 — WWE-template-first, owner directive 2026-10-22):

```
1. TEMPLATE SELECT  ← FIRST SCREEN, never a fixed default
   → Owned by js/creation-flow.js (worker 37), data-driven from
      customization/templates/body-templates.json: WWE 2K-style picks with
      MB-Lab-baked base meshes, teardown-pulled. The Mixamo soldier is dead
      as a default — the stage stays empty until the user picks a template.
   → This lane ships NO competing select: the TEMPLATE tab is a thin wrapper
      (current pick + change button → the flow module's select).

2. BODY (Step 2)
   → Template recipe applied; adjust height, weight, muscle (WMXIX parametric sliders)
   → MPFB2 body morphs (13 macro + 12 face-shape) — live preview, bake to shape keys

3. HEAD / FACE (Step 3)
   → Head shape (7M + 3F) + GNM face system (20 semantic params + presets)
   → Face parts (348) equip into the Face slot with the buy/equip loop

4. SKIN (Step 4)
   → 8 No Mercy tones + 233 No Mercy skin textures + 1,477 WMXIX decoded textures
   → SKIN SYSTEM (TOOLS tab): Fluid Painter paints detail onto the skin set

5. HAIR (Step 5)
   → 165 styles (incl. 9 universal CC0 with real meshes)

6. FACIAL HAIR (Step 6)
   → Beards live in the AKI face-texture parts + head parts → T7 slot 7

7. ATTIRE (Step 7)
   → The full 7,920-part library: WWE (No Mercy 303 real meshes + 379 textures,
      WMXIX 2,690 + 1,477 decoded textures), Def Jam 2,624 CAW parts, DOA4 272
      real costume GLBs — browsable, categorized, buy/equip, conflict-checked
   → Tekken overlay slots (Head/Upper/Lower/Other) share the same socket system

8. WARDROBE (Step 8) → DOA6-style 10 quick slots + two-phrase titles

9. PROFILE (Step 9) → name/alias/music/titantron + Soul/Element/Land canon

10. MOVESET → 176-slot system, Combot cross-roster rule
11. LIMBS → DXMMII 4-arm system
12. TOOLS → three access layers:
      LAYER 1 UNIFIED: BODY / FACE / SKIN / RIG / IMPORT / EXPORT systems
      LAYER 2 SEPARATE: MB-Lab, Build-A-Bod, MPFB2, GNM, GameRig, NaughTyRig,
                        Fluid Painter, Tripo Intake, Export — each its own menu,
                        writing job-spec JSONs the pipeline consumes
      LAYER 3 UNIVERSAL MODE: one combined 9-step wizard for the whole flow

13. SAVE → fighter JSON (see example in section 6) → photo mode → roster
```

**The key principle:** WWE CAW parts and Tekken customization items use the SAME socket system. A jacket from WMXIX and a Tekken 7 customization item both attach to the same `upper_body` anchor points. The player doesn't care which game a piece came from — it's all one wardrobe.

---

## 9. What's Still Needed

1. **CAW save-record byte layout** — blocked on a real emulator save dump (documented in `teardown/wwf-no-mercy/CAW-SAVE-RECORD-STATUS.md`)
2. **WMXIX CAW UI flow** — the in-game creation menus beyond the file catalog
3. **Tekken 7 item meshes** — full game never acquired; item system documented from Tekken 6
4. **Per-move animation linking** — 5,932 clips indexed; individual move→clip links populated as moves are assigned
5. **Texture-to-slot sorting** — 1,478 WMXIX textures need sorting from `textures/` into specific slots
