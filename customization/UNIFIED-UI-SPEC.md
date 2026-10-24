# Western Heart — Unified Customization Suite UI Spec

**Owner-directed 2026-10-13.** The complete design spec for the combined character
customization UI. Tekken's customization FEEL is the base; wrestling's depth, DOA's
wardrobe, and TTT2's Combot precedent are mixed in.

**Companion files:**
- `CUSTOMIZATION-RESEARCH.md` — per-game system research (all 9 games)
- `CUSTOMIZATION-FILES-INDEX.json` — 727 teardown files indexed
- `CHARACTER-CREATION.md` — combined WWE CAW + Tekken design doc
- `../moveset-library/UI-DESIGN-SPEC.md` — Create Fighter + Moveset blueprint (menu names, preview rules)

---

## 0. Design Philosophy — It Ships Feeling Finished

**Owner directive:** this must feel like a COMPLETE game, not a prototype. Everything
wired up from the teardowns should feel finished. New additions arrive feeling like
**DLC or patch updates**, never like prototype features.

What this means in practice:

1. **No placeholder screens.** Every menu in the flow works end-to-end on day one,
   even if its item catalog is small. A category with 3 items that all equip,
   preview, color-edit, conflict-check, and save correctly feels finished. A
   category with 300 items where half don't preview feels like a prototype.
2. **New content = DLC drops.** When a new teardown yields new parts (e.g. the next
   Tekken item batch, new CAW parts), they arrive as a named content drop
   ("ATTIRE PACK 02 — Tekken 6 items") with a version bump, not silently.
3. **Menu art from teardown assets.** Until proprietary art exists, ALL menu art,
   UI panels, HUDs, backgrounds, and thumbnails are built from real teardown
   assets mixed together: TTT2 character cards, Urban Reign UI screens, T6 key art,
   No Mercy/WMXIX menu frames. Section 8 maps which assets go where.

---

## 1. The Central Pattern — Full-Screen Preview, Floating Menus

**Owner directive:** Tekken's customization has a FULL-SCREEN character preview with
the menus layered on top of it. That is the key UI pattern and it is central to
this design.

**How Tekken 7 actually does it** (verified from guides + TKDataPatcher game data
in our teardown):
- The character stands **large, full-body, filling the right ~2/3 of the screen**,
  in fighting stance, on a neutral stage backdrop.
- The category list is a **slim vertical panel on the left edge**. Item thumbnails
  open as a **grid panel sliding in from the left**, never covering the character's
  torso.
- Every selection updates the 3D character **instantly, in place** — you never leave
  the preview to see a change.
- When you finish, the game enters a **photo mode**: you frame the character and
  take the outfit thumbnail yourself. That photo becomes the costume icon at
  character select.

**Western Heart rule (hard):**
- The fighter is **always visible, full-body, full-screen**, on every customization
  screen. No exceptions.
- All menus are **translucent floating panels pinned to the screen edges**
  (left rail, right rail, bottom bar). They may overlap the backdrop but **never
  the fighter's body**.
- The fighter **rotates slowly by default**; player can grab-drag to orbit, scroll
  to zoom. Zooming into a slot (e.g. picking Head items) auto-frames that body
  region, then pulls back out.
- This matches the existing UI-DESIGN-SPEC.md preview laws: "Preview is king" and
  "Nothing covers the character."

```
+------------------------------------------------------------------+
|  FULL-SCREEN 3D FIGHTER (rotating, full body, never covered)      |
|                                                                  |
| [left rail]                                          [right rail]|
|  BODY                                                (context    |
|  ATTIRE   <-- floating, translucent                   panel:     |
|  WARDROBE      panels over the                        item grid / |
|  PROFILE       backdrop, never                       sliders /   |
|  MOVESET       over the fighter                       colors)    |
|                                                                  |
| [bottom bar: breadcrumbs  Fighter > Attire 2 > Attire > Upper ]   |
+------------------------------------------------------------------+
```

---

## 2. Entry Flow — How You Get In

Modeled on **Tekken 7's actual flow** (main menu → Customization → Character
Customization → fighter → slot), extended with No Mercy's attire slots:

```
MAIN MENU
  └─ CREATE FIGHTER                      (menu name locked per UI-DESIGN-SPEC.md)
       ├─ NEW FIGHTER                    → WMXIX default CAW base (parametric body)
       └─ EDIT FIGHTER                   → roster grid (see §3)
            └─ pick fighter
                 └─ ATTIRE 1 / 2 / 3 / 4 → No Mercy 4-slot model (§4)
                      └─ CUSTOMIZATION HUB (§5 — the main screen)
```

**Tekken 7's real behavior we keep:**
- You pick the fighter FIRST, then the save slot, then you customize. (T7: pick
  fighter → pick 1 of 10 slots → category list.)
- Buying and equipping are **two separate steps**: select item → BUY (spends
  currency) → press again to EQUIP. Owned items equip in one press.
- Exiting the hub triggers **photo mode** for the outfit thumbnail (T7 behavior).

**No Mercy behavior we add:**
- 4 attire slots per fighter. Moves, fighting style, parameters, and ally/enemy
  are **shared across all 4**; profile/music and appearance differ per attire.
  (Verified from `teardown/wwf-no-mercy/re-docs/docs/ui/menus/edit-a-superstar.md`.)

---

## 3. Screen 1 — Fighter Select (Base)

- Roster grid of Western Heart fighters (Pantera, Demonio, ... Yukihyō, Slice,
  Doc Frank, etc.), each card showing its **photo-mode thumbnail**.
- Bottom row: **NEW FIGHTER** card (blank silhouette) → starts from the WMXIX
  default CAW base.
- Menu art: TTT2 character cards (`teardown/tekken-tag-tournament-2/` ROSTER.md
  art) as the card frame style; Urban Reign `face.vgs` portraits as the layout
  reference.
- Selecting a fighter → attire slot select (§4).

---

## 4. Screen 2 — Attire Slots (No Mercy 4-Slot)

```
+--------------------------------------------------+
|  PANTERA                          [FIGHTER CARD] |
|                                                  |
|   [ATTIRE 1]  [ATTIRE 2]  [ATTIRE 3]  [ATTIRE 4]  |
|   thumbnail   thumbnail   thumbnail   thumbnail   |
|   "Pantera"   "Leomon"    (empty)      (empty)    |
|                                                  |
|   Shared across attires: Moveset · AI Style ·     |
|   Parameters (locked icon)                       |
+--------------------------------------------------+
```

- Each attire has its own photo thumbnail, name, and full appearance.
- Empty slots show a "+" — picking one clones Attire 1 as a starting point.
- The shared-vs-per-attire split is shown explicitly with lock icons so the
  player understands what carries over (No Mercy's actual rule).

---

## 5. Screen 3 — Customization Hub (The Main Screen)

This is where the player spends 90% of their time. **Full-screen fighter** (§1
pattern). Four tabs on the left rail, context panel on the right.

### 5.1 Tab: BODY (wrestling CAW — No Mercy / WMXIX)

The deep body editor. This tab does what Tekken never did.

```
BODY
 ├─ Body Type      → 14M + 9F types (No Mercy list) — full-body morphs
 ├─ Skin Tone      → 8 tones (No Mercy hex list)
 ├─ Proportions    → WMXIX parametric sliders: Height, Weight, Muscle,
 │                    Shoulder width, Chest, Waist, Hips, Arms, Legs
 ├─ Head Shape     → 7M + 3F shapes
 ├─ Face           → 28M + 20F textures (118 visually verified in teardown)
 ├─ Hair           → No Mercy hair list + Front Hair variants
 │                    (T7 Hairstyle slot items also appear here)
 └─ Details        → scars, tattoos, face paint (T7 MAKE_UP texture class)
```

**Functional behavior:**
- Changing Body Type **re-morphs the preview instantly**; attire items stay
  equipped and re-fit (socket system — §7).
- Sliders move live; the fighter never leaves the screen.
- Skin Tone is a single tap — 8 swatches, instant apply.

### 5.2 Tab: ATTIRE (Tekken item shop — T7 base, T6 depth)

**This tab must FEEL like Tekken's customization.** The category list, the
buy/equip two-step, the conflict messages, the rarity stars — all of it.

**Category list** (T7's real 17 slot IDs as the spine, T6's subdivisions restored
as sub-slots — verified from TKDataPatcher data in our teardown):

```
ATTIRE
 ├─ Head            (T7 slot 1)
 ├─ Hairstyle       (T7 slot 2 — mirrors BODY > Hair)
 ├─ Full Head       (T7 slot 3 — masks/helmets; CONFLICTS with Face Paint)
 ├─ Hair Accessory  (T7 slot 4)
 ├─ Glasses         (T7 slot 5 — DOA glasses also live here)
 ├─ Face            (T7 slot 6)
 ├─ Facial Hair     (T7 slot 7)
 ├─ Face Paint      (T7 slot 8 — texture class, not mesh)
 ├─ Upper Body      (T7 slot 9)
 │    ├─ Inner      (T6 subdivision — undershirt/base layer)
 │    └─ Outer     (T6 subdivision — jacket/armor over it)
 ├─ Full Body       (T7 slot 10 — CONFLICTS with Upper+Lower)
 ├─ Lower Body      (T7 slot 11)
 ├─ Hands          (T6 slot — SEPARATE, restored; T7 merged it away)
 ├─ Feet           (T6 slot — SEPARATE, restored; T7 merged it away)
 ├─ Upper Accessory (T7 slot 12)
 ├─ Lower Accessory (T7 slot 13)
 ├─ Waist L / Waist R (T6 subdivision)
 ├─ Extra           (T7 slot 14)
 ├─ Effects         (T7 slot 15 — effect class)
 └─ Aura            (T7 slot 17 — aura class)
     + Skin Tone, Mirroring toggle, Character Panel (T7 settings)
```

**Functional behavior — the Tekken loop, exactly:**
1. Pick a category → item grid slides in (right rail). Each tile: thumbnail,
   name, rarity stars (0–5), price (Fight Money) or OWNED badge.
2. Hover/select an item → **preview equips it instantly** (try-before-you-buy —
   this is how T7 actually works; the item shows on the fighter before purchase).
3. Press confirm:
   - If owned → EQUIP (one press, instant).
   - If not owned → BUY (spends Fight Money) → press again to EQUIP.
4. **Conflict check on equip** (T7's real system): if the item's zone overlaps an
   equipped item (e.g. full-face mask vs face paint), the game shows
   "CONFLICTS WITH: [item]" and offers **Replace / Cancel**. Replacing unequips
   the old item (it stays owned).
5. **Color edit** (T7): colorable items show up to 5 color channels. Pick
   channel → color picker → live preview. (T6's 3-channel default-costume color
   maps to channels 1–3.)
6. **Mirroring toggle** (T7): flips asymmetric items left/right.
7. Back out of the category → grid slides away, fighter stays.

**Item Moves (T6):** items flagged as Item Moves (weapons, special props) show a
"TRIGGERS SPECIAL MOVE" badge and are equippable in the Extra/Upper Accessory
slots. One Item Move at a time (T8 refines this to back-accessory-only; we keep
T6's behavior).

### 5.3 Tab: WARDROBE (DOA loadouts — do NOT skip DOA)

**Owner directive: DOA's customization parts, menus, and systems go in too.**

DOA6's actual system (verified from research): per character, a loadout =
**Costume + Hairstyle + Glasses + Title**, saved to **10 slots**, selectable at
character select. Costumes come from a parts-drop economy; hairstyles/glasses
are bought with Player Points.

How it maps into the hub:

```
WARDROBE (10 slots per fighter — DOA6 model)
 ├─ Slot 1..10: each stores {all ATTIRE slots + BODY hair/glasses + Title}
 ├─ SAVE CURRENT LOOK → writes current hub state into selected slot
 ├─ LOAD → instantly applies a saved look (full preview swap)
 ├─ Title → two-phrase title (DOA6: pick 2 phrases, e.g. "RAGING" + "BEAST")
 └─ At FIGHTER SELECT: quick-swap between wardrobe slots (DOA6 behavior)
```

**Functional behavior:**
- Wardrobe slots are **snapshots**, not separate attires: saving is instant, no
  photo mode needed (thumbnail auto-captures).
- The 4 No Mercy attire slots (§4) are the "deep" slots (full appearance rebuilds);
  the 10 wardrobe slots are "quick" slots (loadout snapshots). Both coexist:
  each attire slot gets its own 10 wardrobe slots.
- DOA's parts-drop economy maps to our unlock flow: play modes → earn parts →
  complete sets → new items appear in the ATTIRE shop.

### 5.4 Tab: PROFILE (No Mercy page 1)

- Name, Short Name, Alias (attitude meter), 64×64 face picture (auto from photo
  mode, or pick), Height/Weight display (from BODY sliders), entrance Music,
  Titantron video.
- Soul / Element / Land (Western Heart canon fields — from CANON.md).

### 5.5 MOVESET link

The left rail's fifth entry jumps to the **Moveset** menu (separate spec in
`../moveset-library/UI-DESIGN-SPEC.md`): 176-slot system, WWE layout, Tekken
striking depth, live two-fighter preview. Combot precedent (TTT2): cross-roster
move mixing is allowed — any move in any eligible slot.

---

## 6. Screen 4 — Save / Photo Mode (Tekken 7 behavior)

**How T7 actually does it** (verified from player guides): when you finish
customizing and exit, the game enters **photo mode** — you frame your fighter
and take the picture that becomes the outfit thumbnail at character select.
If you skip the photo, the outfit doesn't save properly.

Our flow:
1. Back out of the hub → "SAVE ATTIRE?" prompt.
2. Confirm → **photo mode**: fighter on neutral backdrop, free orbit/zoom,
   take the shot → thumbnail generated.
3. Thumbnail + attire name → written to the attire slot (§4).
4. Wardrobe quick-slots (§5.3) skip photo mode (auto-thumbnail).

---

## 7. Unified Slot System (data spine)

T7's numeric slot IDs are the spine. T6 subdivisions nest under them. Wrestling
body slots and DOA wardrobe sit alongside. One socket system — no
game-of-origin distinction for the player (per CHARACTER-CREATION.md).

| ID | Slot | Source | Class | Conflicts with |
|----|------|--------|-------|----------------|
| B1 | Body Type | No Mercy/WMXIX | body | — |
| B2 | Skin Tone | No Mercy / T7 | body | — |
| B3 | Head Shape | No Mercy | body | — |
| B4 | Face | No Mercy / T7-6 | body/mesh | — |
| B5 | Hair | No Mercy / T7-2 | body/mesh | — |
| B6 | Proportions | WMXIX parametric | body | — |
| 1 | Head | T7 | mesh | — |
| 2 | Hairstyle | T7 | mesh | (mirrors B5) |
| 3 | Full Head | T7 | mesh | 8 (Face Paint) |
| 4 | Hair Accessory | T7 | mesh | — |
| 5 | Glasses | T7 / DOA | mesh | — |
| 6 | Face | T7 | mesh | — |
| 7 | Facial Hair | T7 | mesh | — |
| 8 | Face Paint | T7 | texture | 3 (Full Head) |
| 9 | Upper Body | T7 | mesh | 10 (Full Body) |
| 9a | Upper Inner | T7-9 / T6 | mesh | 10 |
| 9b | Upper Outer | T7-9 / T6 | mesh | 10 |
| 10 | Full Body | T7 | mesh | 9, 9a, 9b, 11 |
| 11 | Lower Body | T7 | mesh | 10 |
| H | Hands | T6 (restored) | mesh | — |
| F | Feet | T7-11 / T6 (restored) | mesh | — |
| 12 | Upper Accessory | T7 | mesh | zone check |
| 13 | Lower Accessory | T7 | mesh | zone check |
| WL/R | Waist L/R | T6 | mesh | zone check |
| 14 | Extra | T7 | mesh/effect | zone check |
| 15 | Effects | T7 | effect | — |
| 17 | Aura | T7 | aura | — |
| W1-10 | Wardrobe slots | DOA6 | snapshot | — |

**Conflict zones** (T7's real system): each mesh item carries a zone mask
(head, face, torso, arms, legs...). Equip runs a zone-overlap check against
equipped items; overlap → Replace/Cancel prompt. Accessories (12/13/14/WL/R)
use finer zone granularity.

---

## 8. Menu Art Sourcing — Teardown Assets Only (for now)

Per owner: until proprietary art exists, all menu art/UI/HUD comes from teardown
assets mixed together. Mapping:

| UI element | Source asset | Location in teardown |
|------------|--------------|----------------------|
| Hub backdrop | T6 key art (Heihachi/Jin/Kazuya + logo) | `tekken6/ui/psp_PIC1.png` |
| Fighter card frames | TTT2 character cards | `tekken-tag-tournament-2/` (ROSTER.md art) |
| Menu panel style | Urban Reign menu screens | `urban-reign/ui/menus/` (VGS) |
| Character select layout | Urban Reign char select | `urban-reign/ui/character-select/` |
| Title/mode select art | T3 title screens | `tekken3/ui/title-screens/` |
| Fonts/banners | T3 font sets | `tekken3/ui/fonts-text/` |
| Item thumbnails | No Mercy/WMXIX part renders | `customization/parts/` (3,372 parts) |
| Photo-mode backdrop | WMXIX arena (neutral) | `teardown/wmxix/arenas/` |
| UI sound | Kenney / freesound pulls | `assets/free-pull-1/` |

**Rule:** art is composited, never stretched out of ratio; the fighter is never
covered (§1).

---

## 9. Flow Diagrams

### 9.1 New fighter, end to end

```
CREATE FIGHTER
  → NEW FIGHTER → BODY tab (pick body type, skin, head, face, hair)
  → ATTIRE tab (dress from shop; buy/equip loop)
  → WARDROBE tab (save look to slot 1)
  → PROFILE tab (name it)
  → MOVESET menu (176 slots; Combot-style cross-roster mixing allowed)
  → AI STYLE + PARAMETERS (No Mercy pages 4–5)
  → SAVE → photo mode → roster
```

### 9.2 Edit existing fighter's attire

```
CREATE FIGHTER → EDIT FIGHTER → pick fighter → pick attire slot (1–4)
  → HUB (BODY locked for roster fighters; ATTIRE/WARDROBE/PROFILE open)
  → SAVE → photo mode → done
```

(Roster fighters' bodies are canon — BODY tab shows but edits are disabled
unless owner unlocks. New fighters get full BODY access.)

### 9.3 Quick wardrobe swap at select

```
FIGHTER SELECT → highlight fighter → shoulder buttons cycle wardrobe slots
  → preview thumbnail updates → confirm → fight
```

---

## 10. Wireframes (ASCII)

### 10.1 Customization hub — ATTIRE tab, category open

```
+----------------------------------------------------------------------+
| CREATE FIGHTER                                  Pantera · Attire 2  X |
+------+------------------------------------------------+--------------+
| BODY |                                                |  UPPER BODY  |
|      |                                                |--------------|
| AT-  |         F I G H T E R                          | [thumb] Jacket|
| TIRE |      (full-screen, rotating,                   | [thumb] Vest  |
|      |       never covered)                           | [thumb] Armor |
| WARD-|                                                | [thumb] Shirt |
| ROBE |                                                |   ★★★  500G   |
|      |                                                |  [OWNED] equip|
| PRO- |                                                |--------------|
| FILE |                                                | Color: [1][2] |
+------+------------------------------------------------+--------------+
| < Fighter   Attire 2   Attire >            Fight Money: 12,400G      |
+----------------------------------------------------------------------+
```

### 10.2 Customization hub — BODY tab

```
+----------------------------------------------------------------------+
| CREATE FIGHTER                                  New Fighter        X |
+------+------------------------------------------------+--------------+
| BODY |                                                | BODY TYPE    |
|      |         F I G H T E R                          | [14M][9F]    |
| AT-  |      (morphs live as you pick)                 |--------------|
| TIRE |                                                | SKIN  (8 sw)  |
|      |                                                |--------------|
| WARD-|                                                | HEIGHT  ===o  |
| ROBE |                                                | WEIGHT  ==o=  |
|      |                                                | MUSCLE  ===o  |
| PRO- |                                                | ...            |
| FILE |                                                |--------------|
+------+------------------------------------------------+--------------+
| < New Fighter   Body >                       [Random] [Reset]        |
+----------------------------------------------------------------------+
```

### 10.3 Wardrobe tab

```
+----------------------------------------------------------------------+
| CREATE FIGHTER                                  Pantera · Attire 1 X |
+------+------------------------------------------------+--------------+
| BODY |                                                | WARDROBE     |
|      |         F I G H T E R                          | [1][2][3][4] |
| AT-  |      (snapshot applies instantly)              | [5][6][7][8] |
| TIRE |                                                | [9][10]      |
|      |                                                |--------------|
| WARD-|                                                | Title:       |
| ROBE |                                                | [RAGING] +   |
|      |                                                | [BEAST]      |
| PRO- |                                                |--------------|
| FILE |                                                | [SAVE LOOK]  |
+------+------------------------------------------------+--------------+
| < Pantera   Attire 1   Wardrobe >                                   |
+----------------------------------------------------------------------+
```

---

## 11. What Makes It Feel Finished (checklist)

Every tab must satisfy all of these before it ships:

- [ ] Fighter visible full-screen on every screen, never covered
- [ ] Every action previews live and instantly (no blind edits)
- [ ] Buy → equip two-step works; owned items equip in one press
- [ ] Conflicts detected with Replace/Cancel (no silent overwrites)
- [ ] Color editing on every colorable item, live preview
- [ ] Photo mode fires on attire save; thumbnail appears at select
- [ ] Wardrobe save/load is instant and correct
- [ ] Currency (Fight Money) deducts and persists
- [ ] New content arrives as a named drop with version bump (DLC framing)
- [ ] All art is teardown-sourced, correctly ratioed, never stretched

---

## 12. Open Questions for Owner

1. **Currency name** — Tekken calls it Fight Money (G). Keep that, or Western
   Heart rename?
2. **BODY lock on roster fighters** — §9.2 locks BODY for canon fighters. Confirm?
3. **Item Moves** — T6's special-move items: in scope for launch, or DLC drop?
4. **SCIII discipline system** — documented as future; want it in the launch
   design or later?

---

*Spec version 1.0 — 2026-10-13. Tekken feel is the base; wrestling depth, DOA
wardrobe, and Combot mixing are layered in. Full-screen preview with floating
menus is the non-negotiable central pattern.*
