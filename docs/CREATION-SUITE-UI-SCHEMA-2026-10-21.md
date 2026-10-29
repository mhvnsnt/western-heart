# Creation Suite UI Schema — Tekken Base, Mobile-First, Mixed-Source

**Owner order (2026-10-21 ~08:20 CDT):** get the FULL UI and layout schema of
Tekken's creation suite — all menus, submenus, every tool — and build our front
end on it: user-friendly, **mobile-first with mobile controls**. Wire WWE + Def
Jam + every other teardown source into ONE mixed creation suite on the Tekken
base: body + face **MORPHING**, clothing, hair, skin color, tattoos,
images/decals. Then go **further**: our customization depth must end up deeper
than both WWE's and Tekken's.

**Evidence discipline:** everything in §1–§2 is mapped from our own teardown
materials, never from memory of the games. Sources are cited per claim:

- `~/workspace/tekken-customization-extraction/REPORT.md` (TekkenMods /
  TKDataPatcher database extraction: 16 slots, 21-field item spec, color slots,
  socket positioning, conflicts) — cited as **[T7-DB]**
- `customization/parts/tekken/tekken7-slot-catalog.json` (the same data in
  machine-readable form) — **[T7-CAT]**
- `customization/creation-suite-ui/UI-EXTRACTION-LOG.md` §1–§2 (T7 + T6 PSP
  flows/slots as extracted by the flagship lane) — **[XLOG]**
- `customization/UNIFIED-UI-SPEC.md` (the 2026-10-13 synthesized target this
  doc extends to mobile) — **[UNIFIED]**
- `customization/CREATION-SUITE-WIRING-AUDIT-2026-10-20.md` (runtime truth) —
  **[AUDIT]**
- `customization/CUSTOMIZATION-JSON-SCHEMA.md` (the profile contract) —
  **[PROFILE]**
- `packages/creation-suite/src/menu.js` (WWE 2K-blend menu tree, owner spec
  2026-10-14), `src/layering.js` (WWE 2K19 layering rules from
  `customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md`), `src/morphs.js`,
  `src/dna.js` — **[SRC]**
- `teardown/wwf-no-mercy/re-docs/docs/ui/menus/edit-a-superstar.md`
  (No Mercy's Edit-a-Superstar, read for the wiring audit) — **[NM-UI]**
- Catalogs on main, counted live for §6: `customization/PARTS-REGISTRY.json`,
  `customization/parts/no-mercy/CATALOG.json`,
  `customization/parts-converted/CATALOG.json`,
  `customization/parts-converted/defjam/CATALOG.json`,
  `customization/parts/tekken7/CATALOG.json` — **[CATS]**

Companion build: `packages/creation-suite/ui/` (the mobile app) +
`packages/creation-suite/src/slotmap.js` (the spine mapper, §5). The desktop
flagship (`customization/creation-suite-ui/`) and this schema's predecessor
[UNIFIED] remain in place; this doc is the mobile layout schema and the
mixed-source section map the new front end implements.

---

## 1. Tekken's creation suite — the menus, submenus, and tools (as documented)

### 1.1 Entry flow [XLOG §1, UNIFIED §2]

```
MAIN MENU → Customization → Character Customization
  → pick fighter → pick 1 of 10 save slots → category list (slot groups)
  → pick a slot group → item list → hover = try-on preview
  → confirm = BUY (if unowned) → confirm again = EQUIP
  → exit → PHOTO MODE (frame the fighter; the photo becomes the outfit icon)
```

Rules Tekken enforces that we keep:

1. **Fighter first, slot second, items third.** No item browsing without a
   fighter + attire slot context.
2. **Buy and equip are two separate steps.** Owned items equip in one press.
3. **Hover try-on:** the hovered item renders on the fighter before any
   commitment (mobile adaptation: tap-to-preview, §3).
4. **Exit triggers photo mode**; the thumbnail is part of the save.

### 1.2 The 16 equipment slots — the spine [T7-DB §2, T7-CAT]

Tekken 7 stores every customization item against one of 16 slot IDs (17 is the
last used ID; 16 is skipped). This table is the suite's data spine — our UI's
ATTIRE section is this list, in this order:

| ID | Slot | Asset type | In-pak path shape |
|----|------|-----------|-------------------|
| 1 | HEAD | CharacterItem | `Mesh/<CHAR>/Head/…` |
| 2 | HAIR | CharacterItem | `Mesh/<CHAR>/Hair/…` |
| 3 | FULL_HEAD | CharacterItem | `Mesh/<CHAR>/FullHead/…` |
| 4 | HAIR_ACC | CharacterItem | `Mesh/<CHAR>/HairAcc/…` |
| 5 | GLA (glasses) | CharacterItem | `Mesh/<CHAR>/Gla/…` |
| 6 | FACE | CharacterItem | `Mesh/<CHAR>/Face/…` |
| 7 | FACE_HAIR | CharacterItem | `Mesh/<CHAR>/FaceHair/…` |
| 8 | MAKE_UP | CharacterItem**Tex** | texture class, not a mesh |
| 9 | UPPER | CharacterItem | `Mesh/<CHAR>/Upper/…` |
| 10 | FULL_BODY | CharacterItem | `Mesh/<CHAR>/FullBody/…` |
| 11 | LOWER | CharacterItem | `Mesh/<CHAR>/Lower/…` |
| 12 | UPPER_ACC | CharacterItem | `Mesh/<CHAR>/UpperAcc/…` |
| 13 | LOWER_ACC | CharacterItem | `Mesh/<CHAR>/LowerAcc/…` |
| 14 | EXTRA | CharacterItem | `Mesh/<CHAR>/Extra/…` |
| 15 | EFFECT | **Effect**CharacterItem | effect class |
| 17 | AURA | **Aura**CharacterItem | aura class |

Asset-class prefixes in the game data [T7-DB §3]: `CCI` Customize Character
Item, `CI` Character Item, `CS` Character Set (whole outfit), `EI` Extra Item
(Negan's bat, Noctis' sword — signature items), `ECI` Effect Item, `ACI` Aura
Item. Generic items live under character abbreviation `cmn` with
`PlayerCusID 0` (see §1.4).

### 1.3 The menu's group ordering — SlotGroupIDs [T7-DB §2]

The in-game category list is not the slot-ID order; it is ordered by
**SlotGroupID**, negative IDs sorting the settings rows around the equipment
rows. The full group list, in menu order:

| Group | Menu row |
|-------|----------|
| −254 | Head |
| −253 | Hairstyle |
| −252 | Full Head |
| −251 | Hair Accessory |
| −250 | Glasses |
| −249 | Face |
| −247 | Face Paint (MAKE_UP) |
| −246 | Upper Body |
| −245 | Full Body |
| −244 | Lower Body |
| −243 | Upper Accessory |
| −242 | Lower Accessory |
| −240 | Effects |
| −238 | Aura |
| −237 | **Skin Tone** (a settings row, not an item slot) |
| −236 | **Mirroring** (a settings toggle, not an item slot) |

Two of Tekken's "menu rows" are tools, not item lists: **Skin Tone** and
**Mirroring**. Our UI keeps both as tools in the same list (§4) — skin tone in
BODY, mirroring in the placement editor — so the menu shape stays Tekken's
even where the tool lives elsewhere on mobile.

### 1.4 The item record — what every tile knows [T7-DB §
...[truncated 17489 chars]3, T7-CAT `item_csv_fields`]**

Every item is a 21-field record. The fields the UI surfaces:

| Field | Meaning | UI use |
|-------|---------|--------|
| A `ShopID` | shop identity | tile key |
| C `CCI_Reference` | `TekkenGame/Content/<Path>/<CHAR>/<SLOT>/<NAME>` | provenance |
| E `charId` | 0–56 character scope (57 characters) | per-fighter filter |
| F `slotId` | the §1.2 slot | category |
| H/I `NameByID` / `ItemName` | display name | tile label |
| K `SlotGroupID` | §1.3 menu group | list ordering |
| M `PlayerCusID` | 0 = generic, 1 = 1P, 2 = 2P | generic vs per-fighter badge |
| N `SlotColors` | **0–5 colorable channels on this item** | color editor size |
| P `Rarity` | rarity grade | tile stars |
| R `ItemCost` | Fight Money price | buy step |
| T `AdditionalText` | flavor text | detail sheet |

### 1.5 The tools inside the item flow [T7-DB §5–§6]

1. **Color editor** — items expose up to **5 color channels** (field N);
   picking a channel and a color re-renders the item live.
2. **Placement on accessories** — accessories carry position / rotation /
   scale offsets applied on a **bone socket** (the paradigm our PartPoser-style
   editor implements: pos XYZ, rot pitch/yaw/roll, scale, mirror toggle).
3. **Mirroring** — group −236 flips asymmetric items left/right.
4. **Conflicts** [T7-DB §"Conflicts"]: equipping **FULL_HEAD** unequips HEAD,
   HAIR, FACE, HAIR_ACC, GLA, FACE_HAIR; equipping **FULL_BODY** unequips
   UPPER and LOWER. The game never silently stacks over a conflict.
5. **Photo mode on exit** [XLOG §1, UNIFIED §6].

### 1.6 Tekken 6 (PSP) — subdivisions Tekken 7 merged away [XLOG §2]

T6 splits what T7 merged: **Upper Inner / Upper Outer** sub-slots, a separate
**Hands** slot, a separate **Feet** slot, and **Waist L / Waist R**. We restore
all five as sub-slots nested in the T7 spine (slots 9a INNER, 9b OUTER, H
HANDS, F FEET, WL/WR WAIST) — they are where WMXIX gloves/shoes and Def Jam
accessories naturally land. T6 item *names* (9,440 records, #416) exist as
data; T6 item meshes do not (§9).

### 1.7 Tekken 8 — noted, not built [T7-CAT]

T8 adds a FOOTWEAR slot, two accessory slots, and characters standing in the
suite. Recorded here as the direction the spine grows; not part of this build.

---

## 2. What the other sources contribute

| Source | What it gives the suite | Evidence |
|--------|------------------------|----------|
| **WWF No Mercy** (AKI) | Edit-a-Superstar flow: PROFILE page (name/alias/height/weight/music), **4 attire slots** (moves/style/parameters shared, appearance per attire), body types, 8 skin tones, face/hair lists — and 682 cataloged parts (303 mesh GLBs + 379 texture parts) with a complete AKI part taxonomy | [NM-UI], [CATS] |
| **WMXIX** (AKI) | CAW category taxonomy (Man/Woman/Face/Upper_Body/Face_op/Gears/Lower_Body/Shoes/Hair/Wrist/Gloves/Knee/Elbow…), 1,477 decoded part textures runtime-ready, 992 `.ymg` parts geometry-blocked (J3 eye-validation) | [AUDIT], [CATS] |
| **Def Jam: Fight for NY** (AKI lineage) | 2,624 CAW parts converted EAGL→GLB as **POINTS pools** (vertex order unproven — preview data, not wearable meshes yet), `AKI_CFG.XML`/WAZA structure shared with No Mercy | [CATS] (#411), gap-closure checkpoint |
| **WWE 2K** (design only — zero assets held, owner acquisition boundary) | The deep CAW shape: layered attire with **L/R independent** arm/leg slots, per-item color channels, material editor, logo placement/scale/rotation, tattoos as a placeable canvas; menu blend in [SRC] `menu.js` | [SRC], [AUDIT] |
| **DOA** | **Wardrobe loadouts**: costume+hair+glasses+title saved to **10 slots**, quick-swap at select | [UNIFIED §5.3], [AUDIT] |
| **Native WH libraries** | eye-library, decal-library (baek/lili/mariposa/pantera/zafina), reskin-library, superhero parts (batgirl/spaceghost/spidergirl incl. the repo's one mesh-eye GLB), CC0 hair + KayKit parts, per-fighter eye texture sets | [AUDIT], [CATS] |

The menu blend is already law in code [SRC `menu.js`, owner spec 2026-10-14]:
Main → suite → [Character Creation/Edit | Moveset] → character list → the
character's sub-menu: Presets, Body, Head & Face, Attire (layered), Paint &
Tattoos, Alternate Attires, Moveset, Profile & Style, Entrance. This schema
keeps that tree and lays it out for a phone (§3–§4).

---

## 3. The mobile adaptation (ours — the original is not a mobile UI)

The Tekken pattern that survives translation is **[UNIFIED §1]: the fighter is
always visible full-screen; menus float at the edges and never cover the
fighter.** On a phone that becomes:

```
┌─────────────────────────────┐
│ ‹ Fighter        Attire 2 ⚙ │  top bar: back, fighter, attire chips, SAVE
│                             │
│        FIGHTER STAGE        │  full-screen; look summary renders here
│      (never covered)        │  (equipped chips, morph bars, color dots)
│                             │
│ ┌─────────────────────────┐ │
│ │  BOTTOM SHEET (panel)   │ │  slides up over the backdrop only;
│ │  section content,       │ │  drag handle collapses it to a strip
│ │  its own scroll region  │ │
│ └─────────────────────────┘ │
│ BODY FACE ATTIRE INK WRD PRF│  bottom tab bar, thumb zone
└─────────────────────────────┘
```

Interaction laws (owner standing rules, applied):

1. **Tap → scroll → TAP to assign. Never drag-and-drop.** Every assignment in
   the suite is: tap a category → scroll the list → tap an item → tap EQUIP.
   Sliders are the only continuous controls, and they are thumb-sized.
2. **Tap-to-preview replaces hover.** Tapping an item tile previews it in the
   stage summary (name, source, status, color dots) without equipping;
   EQUIP is the separate confirming tap — Tekken's buy/equip two-step
   preserved (§1.1 rule 2; currency is out of scope for this front end, so
   owned/unowned collapses to equip/remove, and the two-step survives as
   preview → equip).
3. **Touch targets ≥ 48px**; every list scrolls inside its own sheet region;
   the stage never scrolls.
4. **Options-stacking, everywhere.** Attire slots 1–4, wardrobe snapshots
   1–10 per attire, saved profiles per fighter: saving writes the *selected*
   slot only and never overwrites another. There is no destructive save path.
5. **Conflicts ask, never silently replace** (§1.5 rule 4): equipping over a
   conflict opens a Replace / Cancel sheet naming the victim — Tekken's
   behavior, and [SRC] `layering.js` `resolveEquip` returns the victims so
   the UI can name them.

---

## 4. The mixed-source section map (what the built UI shows)

Six bottom tabs. Every row names its sources and what feeds it **today**
(counts in §6).

| Tab | Contents | Tekken anchor | Other sources wired in |
|-----|----------|---------------|------------------------|
| **BODY** | Body type presets (the 16 `BODY_TYPES` labels the game consumer reads [PROFILE consumer `game/js/custom-fighter.js`]); **13 body morph sliders**; **skin tone** swatches + free color; hair/skin color fields | group −237 Skin Tone | No Mercy body types + WMXIX proportions via morphs; DNA sliders [SRC] beneath the same profile |
| **FACE** | **12 face morph sliders**; **eyes** (mesh eye parts + legacy eye texture variants, labeled legacy); face parts; hair styles + hair color | slots 2 HAIR, 6 FACE | No Mercy faces (146 tex + 48 mesh), WMXIX faces, native eye-library + per-fighter eye sets |
| **ATTIRE** | The **16-slot Tekken spine** (§1.2) in SlotGroupID order (§1.3) + T6 sub-slots (§1.6); per-slot part browser with source filter; per-part detail sheet: color channels, **placement editor**, finish editor, mirror | the whole §1.2 table | No Mercy 303 mesh GLBs, WMXIX textures + gears, Def Jam (preview tier), native libraries (superhero/hair/KayKit/reskins) |
| **INK** | **Tattoo / image layers**: pick a decal/image entry → place with rect sliders (x, y, w, h) + target material → layer list (reorder = stacking) | slot 8 MAKE_UP (texture class) | decal-library per-fighter sets, WMXIX's 1,477 MAKE_UP textures, No Mercy face/skin textures |
| **WARDROBE** | **10 snapshot slots** per attire: save look / load look; **title pair** editor (two-phrase title) | — (Tekken has preset slots; the snapshot model is DOA's) | DOA loadouts [UNIFIED §5.3], No Mercy 4-attire model above it |
| **PROFILE** | Name, title pair, fighting-style archetype, parameters (arms offense / body defense — the fields the game consumer reads), **Save** (writes the suite profile), **Export** (downloads the per-attire `customization.json`) | — | No Mercy PROFILE page [NM-UI], [PROFILE] |

Fighter + attire context sits above the tabs at all times (Tekken §1.1 rule
1): the top bar carries the fighter name and **attire chips 1–4**; switching
attire loads that attire's own saved state (options-stacking).

---

## 5. The spine mapper — how 5 catalogs become one menu

The Phase-1 runtime [AUDIT] could only see `PARTS-REGISTRY.json` (1,148
entries); the per-source catalogs existed on disk with no runtime consumer,
and 80% of merged entries carry a *source* slot but no `suite_slot`, so a
slot-keyed UI would show almost nothing. `src/slotmap.js` (new, additive —
`catalogs.js` is untouched) closes that deterministically:

1. **Spine table** — the §1.2 slots + §1.6 T6 sub-slots, each with the
   `suite_slot` values that belong to it.
2. **`mapEntry(entry)`** — resolves an entry to a spine slot by, in order:
   explicit `suite_slot` → Tekken slot title in `slot` → source taxonomy map
   (No Mercy skins/bodies/faces/accessories; WMXIX categories
   gears/shoes/gloves/weapon/colors; Def Jam head/upper_body/lower_body/
   accessories) → `kind` fallback → the explicit **UNMAPPED** bucket. An
   entry is never dropped and never guessed into a slot the data doesn't
   support: Def Jam's 2,209 `unknown`-family entries stay UNMAPPED until the
   family codes are decoded (gap-closure lane).
3. **Readiness tiers** — computed from entry data only:
   - `ready-mesh` — a real GLB (registry mesh parts, No Mercy conversions);
   - `ready-texture` — a texture/image asset the bake can composite
     (texture parts, eye/decal variants, WMXIX converted textures);
   - `preview-only` — Def Jam POINTS pools (`topology_status:
     unproven_vertex_order`): browsable, **not equippable**, badged as such;
   - `blocked` — `blocked_ymg_decode`, `blocked_dumy_placeholder`,
     `no_valid_refpack_record`, `compiled_variant`, `pose_palette_only`,
     `not_converted`, `palette_only`: shown with their status named.
   Only `ready-*` entries can be equipped. A blocked part can never surface
   as equippable — the same honesty rule the J3 test enforces for `.ymg`.

---

## 6. Runtime-visible counts — before / after (measured, not estimated)

Measured 2026-10-21 with the repo's own `catalogs.js` over the real files
(reproduced by `packages/creation-suite/test/slotmap.test.js`):

| Measure | Count |
|---------|-------|
| Indexed across all teardown sources [AUDIT] | 25,784 |
| **Runtime-visible BEFORE** (registry only — the only file any code path loaded) | **1,148** |
| Merged by this build (`mergeCatalogs` over registry + No Mercy + WMXIX-converted + Def Jam + Tekken 7 catalogs; 35 file-dedupes, registry wins) | **7,791** |
| …of which mapped onto the Tekken spine by `slotmap.js` | **5,574** |
| …of which UNMAPPED (2,209 Def Jam unknown family + 8 WMXIX palette records — named, §5) | **2,217** |
| Equippable today (`ready-mesh` + `ready-texture`) | **2,869** |
| Preview-only (Def Jam POINTS pools) | **1,201** |
| Blocked (conversion pending, status named per entry) | **3,721** |
| Record-only (name/record, no asset — the tier T6 names will occupy) | **0** |

Per-slot highlights from the same run: MAKE_UP 1,478 entries / 1,477 ready
(the J2 texture decode); FACE 544 / 390 ready; FULL_BODY 694 / 693 ready;
UPPER 1,309 / 135 ready + 185 preview + 989 blocked (the WMXIX `.ymg`
population); EYES 13 / 13 ready (texture variants + the spidergirl mesh
lenses at GLA). The full per-slot table is asserted by the shipped test.

The remaining indexed-but-not-runtime sources (§9) are named with their
wiring step; nothing in this table is rounded or projected.

---

## 7. The profile format — one contract, additive extensions

The suite profile is `customization.json` **v1** [PROFILE] — unchanged. The
UI writes exactly its fields:

```jsonc
{ "version": 1, "app": "wh-creation-suite", "fighter": "...", "attire": "...",
  "base_glb": "...", "out_glb": "...",
  "body":    { "body_type": "...", "skin_tone": "#rrggbb" },
  "morphs":  { "<morphs.js id>": -1..1 },
  "parts":   { "<suite_slot>": { "part_id": "...", "glb": "...",
               "placement": { "px":0, "py":0, "pz":0, "rx":0, "ry":0, "rz":0, "s":1 } } },
  "textures":[ { "part_id": "...", "kind": "eye|decal|hair", "image": "...",
                 "material": "...", "rect": [x, y, w, h] } ],
  "colors":  { "hair": "#rrggbb", "skin": "#rrggbb" } }
```

**Additive keys the UI also writes** (ignored by today's consumers; the bake
adopts them without a format break — coordinated with the
fighter-completeness lane, which owns the in-fight consumer and this format):

| Key | Shape | Feeds |
|-----|-------|-------|
| `item_colors` | `{ "<suite_slot>": ["#hex", …up to 5] }` | §1.5 color channels per equipped part |
| `finishes` | `{ "<suite_slot>": { "roughness": 0..1, "metalness": 0..1, "tint": "#hex" } }` | [SRC] `attire.js` `applyEdit` already consumes exactly these |
| `mirrored` | `{ "<suite_slot>": true }` | group −236 mirroring per part |
| `wardrobe` | `{ "title": ["A","B"], "snapshots": { "1".."10": <look> } }` | §4 WARDROBE |
| `layers` | ordered suite_slot list | [SRC] layering order for stacked slots |

**Save targets.** (a) `localStorage["wh_creation_suite_v1"]` — the shape the
game's current consumer (`game/js/custom-fighter.js`) already reads:
`{ profile: { name, title: [A, B] }, body: { body_type, skin_tone },
parameters: { arms: { offense }, body: { defense } }, fighting_style:
{ archetype, aggression } }` — the UI writes that object *plus* the v1 fields
above in the same record; the consumer reads the fields it knows and ignores
the rest. (b) **Export** downloads the per-attire `customization.json` for
the bake path. Both are written from one state object by
`packages/creation-suite/ui/profile.js` (pure module, unit-tested), so the
two can never drift.

---

## 8. Deeper than both — the extensions

Each extension is named, and each is derived from data or code this repo
already holds — not from a wishlist.

- **D1 — Placement on EVERY mesh part.** Tekken exposes placement on
  accessories; WWE exposes none. Our profile schema [PROFILE] already carries
  placement on every part, so the editor (7 sliders + mirror) opens on every
  equipped mesh part.
- **D2 — Per-part finish.** Tint/roughness/metalness per part, continuous
  sliders — [SRC] `attire.js` `applyEdit` consumes these today. Tekken has no
  finish control; WWE's material editor is preset-based.
- **D3 — Cross-source mixing.** Any catalog part on any fighter (socket-fit
  rule [SRC] `parts.js` `usableOn`: mesh parts fit any rig). Tekken locks
  items per character (`charId`, `PlayerCusID`); WWE locks to its own
  roster. The Combot precedent [UNIFIED §5.5] generalized to parts.
- **D4 — L/R independent slots inside the Tekken spine.** WWE 2K's gloves /
  wrist / elbow / knee L/R independence [SRC `layering.js`
  `LR_INDEPENDENT`] + T6's Waist L/R (§1.6), expressed as paired sub-slots
  the spine mapper understands.
- **D5 — Mesh eyes as placeable parts.** Eyeball + lashes + brows are mesh
  parts at the eye position with D1 placement (owner law: eyes are real
  parts, never texture decals). Today the repo holds exactly one mesh-eye
  GLB (spidergirl) — the slot ships honestly sparse (§9) and fills as parts
  land.
- **D6 — A real decal canvas.** INK layers stack without a per-zone cap,
  each with rect + material targeting [PROFILE `textures[]`] — Tekken's
  MAKE_UP is fixed texture slots; WWE's logo tool is per-zone. Ours is a
  layer list.
- **D7 — The 25-slider morph stack, live with parts equipped.** 13 body +
  12 face morphs [SRC `morphs.js`] *plus* the DNA slider set [SRC `dna.js`]
  beneath one profile. Tekken 7 ships **zero** morph sliders.
- **D8 — 40 saved looks per fighter.** 4 attires (No Mercy) × 10 wardrobe
  snapshots (DOA), all options-stacked. Neither source game stacks both
  axes.
- **D9 — Aura / Effects as first-class slots.** Tekken reserves the slots
  (15/17) and the ECI/ACI asset classes exist in its data [T7-DB §3]; we
  surface them in the spine now so effect parts land in a ready menu the
  day they are converted (named gap until then, §9).
- **D10 — Honest readiness, in the UI.** Every tile carries its conversion
  status (§5 tiers). A creation suite that shows 7,791 entries and badges
  the blocked ones beats a suite that pretends — and beats both source
  games' silent per-character locks, because the player can see *why*.

---

## 9. Named gaps (what the UI honestly cannot show yet)

| Gap | State | Wiring step when it lands |
|-----|-------|----------------------------|
| **Tekken 7 item meshes** | ZERO in any holding (survey verdict, PR #437): T7 itself was never acquired; `parts/tekken7/CATALOG.json` loads with `parts: []` + `named_gaps[]` | Acquisition assigned to gap-closure lane (W6): T7 PC paks → umodel → classify vs [T7-CAT] → PSK→GLB. Entries resolve in this UI with **no consumer change** (the Slice skull-mask gap `tekken7:cmn:full_head:skull-mask` is the worked example) |
| **T6 item names** | 9,440 name records [CATS-adjacent `tekken6-item-names.json`]; not `parts[]`-shaped, no meshes | A catalog-shape pass over the names file (record-only tier) |
| **Def Jam unknown family** | 2,209 of 2,624 census entries carry family `unknown` | Family-code decode (gap-closure W5) → extend `slotmap.js` table |
| **Def Jam meshes** | Converted GLBs are POINTS pools; vertex order unproven (#411) | The converter's strip-mode proof; tier flips to `ready-mesh` automatically |
| **WMXIX `.ymg` geometry** | 998 blocked decode + 202 DUMY placeholders (J3) | YOBJ strip-order proof; same automatic tier flip |
| **Lash / brow mesh parts** | Do not exist yet; eye slot shows the one spidergirl mesh + labeled legacy texture variants | Creation-suite parts work; slot already exists (D5) |
| **DOA parts data** | Wardrobe *system* wired; DOA part data partial/unverified [AUDIT] | DOA4 keystream lane (#386) |
| **WWE 2K assets** | Zero by design (design evidence only) | Owner acquisition decision; layering rules already in [SRC] |
| **Photo mode** | Tekken's exit flow (§1.1 rule 4); the flagship has a 3D viewer, this mobile front end's stage is a data-true look summary | Binds to the same stage when the mobile 3D preview lands; export already carries everything the thumbnail step needs |
| **PartPoser (standalone)** | Not in this repo by that name; its paradigm is [T7-DB §6] + the [PROFILE] placement schema | The placement editor in this build implements the paradigm against the schema |
