# Creation Suite Teardown Blueprint — Flow Map (2026-10-22)

**Owner directives driving this doc:**
1. (2026-10-22) "If we have any WWE Teardown files, use those to help us set up the creation suite — as well as the Tekken Teardown files help us organize and set up all the menus and submenus and everything based on those."
2. (2026-10-22 ~17:39 CDT) "Using the teardown files you'll be able to see how Tekken and WWE and Def Jam do accessories and organization and the menus, menu UI, menu art, menu layout, preview layout, live preview, how they let you navigate the character on screen. Convert it to touch/phone mobile controls."
3. (2026-10-22 ~17:44 CDT) 100% teardown coverage for character creation — every game's creation system fully wired in.

**The division (owner-locked):** Tekken teardowns → game menus, submenus, systems, flow. WWE teardowns → character creation suite structure, menus, submenus, flow. The suite nests inside Tekken's overall menu structure; WWE's CAW logic governs the creation flow's internal menu hierarchy.

---

## 1. Which WWE game's sequence we follow

**Primary: WWE 2K22.** It is the most recent fully-documented CAW flow (guides + research in repo), and its structure is the clearest expression of the CAW genre:

```
CREATIONS → SUPERSTAR
 ├─ NEW CUSTOM SUPERSTAR → weight class + archetype → Persona (outfit template, skippable) → editor
 ├─ WWE SUPERSTAR        → edit a roster wrestler's attire + menu pose (moveset/personal info locked)
 └─ EDIT CUSTOM SUPERSTAR → pick your CAW → full editor
```

**Editor tab order (2K22):** APPEARANCE (Face/Body) → ATTIRE (per slot: Type / Appearance / Clothing / Parts Color) → PERSONAL INFO → PERFORMANCE → STATISTICS.

**Layer/morph rules: WWE 2K26** (newest): 60 attire layers + 40 body/head layers (separate pools), body morphing with 40+ templates, two-tone hair, 200 CAW slots.

**Attire-slot model: WWF No Mercy** (4 independent attires sharing one moveset) — this predates and matches 2K22's 4 slots (Ring 1/2, Entrance 1/2). No Mercy is the origin of the model; 2K22 is the modern expression.

**Proportion sliders: WrestleMania XIX** (12 region W/L/D sliders) — the deepest parametric body model of the AKI/Yuke's era.

**Why 2K22 over 2K19:** 2K19's data (5,581 moves, pac structure) feeds our *parts/moveset* libraries; 2K22's *menu flow* (documented end-to-end in player guides) drives the hierarchy. Both are wired; they serve different layers.

---

## 2. Where we extend beyond WWE

| WWE has | We add (parametric freedom) |
|---|---|
| 40+ body templates, morph sliders | MB-Lab + MPFB2 + GNM + Build-A-Bod unified BODY system (tool-to-menu wiring law) |
| 165 facial hair, 261 hairstyles (fixed parts) | Hair/headwear as **library items** (worker 64's architecture) — any mesh, placed + scaled freely |
| 60 attire layers | Same layer budget, but layers accept **any library part** (Tekken/Def Jam/SC/No Mercy/WMXIX/CC0) |
| Fixed slot conflicts | T7 zone-conflict system (Replace/Cancel) across all libraries |
| Entrance editor | Repurposed → **cutscene creator + taunt creator** (owner directive; no full entrances) |
| Face/Heel victory scenes | Kept as win-pose/taunt variants |
| Per-attire Appearance (hair/eyes/facial hair) | Already structural: hair/eyes are parts equipped per attire, not per fighter |
| CAW slots | 4 No Mercy attire slots × 10 DOA wardrobe snapshots per attire |

**Universal mode** (tool unification law): the three access layers — (1) unified per-domain systems, (2) each original tool separately in its own menu, (3) one combined front-end for the full flow. The WWE hierarchy is layer (3)'s skeleton; the tools plug into it per the menu-to-tool map.

---

## 3. What Def Jam does differently (and what we take)

Def Jam organizes customization as **in-world shops**, not tabs:
- **SUS** (streetwear boutique) → our ATTIRE tab's WWE-REGION browse is the tab equivalent; the boutique *feel* (licensed-brand racks) maps to our LIBRARIES browse in the PARTS tab.
- **Jacob & Co. bling** → Accessories region; bling raises **Charisma** → we map Charisma to fighter presentation (crowd reaction + menu pose + heat aura tuning).
- **Manny's Tats / Stingray's** → tattoo/hair submenus (already in BODY/ATTIRE).
- **Stapleton gym** (Train Skills / Learn Styles / Learn Moves / Assign Moves) → our moveset + stats: Dev Points ≈ Fight Money spent on moves; "Assign Moves to stick directions" = our super/Blazin' mapping.
- **Key difference from WWE:** Def Jam's gear has *stats* (charisma). WWE's gear is pure cosmetics. We take both: cosmetics from WWE's hierarchy, stat-flavored presentation from Def Jam.

---

## 4. What Soulcalibur contributes (the gap we closed)

Soulcalibur was the missing game in the suite's coverage. What it adds:
- **Equipment slots with fantasy granularity** (Shoulder, Special1/2 for capes/horns/wings/tails) — mapped onto our T7 spine via `wh` fields in `SC_CAS_TREE`.
- **Adjust Equipment** (per-piece scale/move/rotate) — validates our PLACE_AXES placement dock as the genre-standard paradigm (Tekken 8, WMXIX GEAR, and SC all do this independently).
- **Layered Under/Mid/Outer** — the anti-clip rule our layer system follows.
- **16 races** — future extension: non-human body bases (fits our creature roster: Dorowani, Chatur).
- **Sticker/pattern editor + voice pitch + battle comments + photo→name** — the finishing-steps checklist every creation flow needs; ours: decals → voice (Dorowani precedent) → taunts → photo mode → name.

---

## 5. Touch/phone conversion (verify-by-playing law: phone portrait)

Every teardown UI was designed for gamepad/TV. The conversion rules (`TOUCH_MAP` in `menu-data.js`):

1. **Tap grammar (MDickie):** tap slot → scroll library → tap to assign. Tap once = inspect + live preview; tap again = enter/equip. NEVER drag-and-drop.
2. **Preview navigation:** swipe sideways = rotate fighter; pinch = zoom (auto-frames the picked slot's body region, pulls back on exit); fighter rotates slowly by default.
3. **Panels:** item grids + part detail slide up as **bottom sheets** — the fighter stays visible above, never covered (Tekken's full-screen preview law).
4. **Portrait layout:** the left rail becomes a **bottom tab bar**; breadcrumbs stay pinned (`Fighter › Attire N › Tab › Category`).
5. **Targets:** 48px minimum; buy→equip stays a two-step but touch-sized; long-press opens the part options sheet (color channels, placement, conflict info).
6. **Live preview everywhere:** No Mercy's move-preview-on-highlight becomes our rule — hovering/selecting ANYTHING (part, move, tattoo, pose) previews it on the fighter instantly.

---

## 6. The full flow (character → attire, all capabilities)

```
CREATE FIGHTER (inside Tekken's menu structure)
 ├─ NEW FIGHTER ─→ template select (WWE base bodies, never Mixamo)
 │    → BODY (WWE Appearance: Face/Body + WMXIX proportions + MB-Lab/MPFB/GNM)
 │    → ATTIRE ─→ pick attire slot 1-4 ─→ TEKKEN SLOTS ⇄ WWE REGIONS browse
 │    → WARDROBE (10 DOA snapshots per attire) → PROFILE (WWE Personal Info)
 │    → MOVESET → PERFORMANCE (cutscene/taunt) → STATISTICS
 │    → SAVE → photo mode → roster
 │
 └─ EDIT FIGHTER ─→ roster grid ─→ pick fighter ─→ pick attire 1-4 ─→ hub
      (roster fighters: BODY locked unless owner unlocks; ATTIRE/WARDROBE/PROFILE open)
      → edit current attire OR "+" empty slot (clones Attire 1) → SAVE → photo mode
```

Capability checklist (owner ~17:39 CDT):
- [x] Edit and save individual attires, characters, outfits (per-attire records, `F.records`)
- [x] Go to a character → see/edit their attires (roster mode: pick fighter → pick attire)
- [x] Create new character → create multiple attires (NEW FIGHTER → 4 attire slots)
- [x] Edit existing in-game OR user-created character's attire, or add extra attires (WWE SUPERSTAR door + "+" slot)
- [x] Pick character → pick attire flow (No Mercy / WWE / Tekken all do this; we do too)

---

## 7. Implementation (worker 65, this pass)

- `customization/creation-suite-ui/js/menu-data.js`: +10 MENU_SRC entries; +13 new trees/flows (WWE_ATTIRE_TREE, WWE_ENTRY_FLOW, WWE_FACE_TREE, WWE_BODY_TREE, WWE_PROFILE_TREE, WWE_PERFORMANCE_TREE, WWE_STATS_TREE, SC_CAS_TREE, SC_CAS_FLOW, DEFJAM_SHOP_TREE, DEFJAM_GYM_TREE, NM_CAW_TREE, WMXIX_CAW_TREE, TOUCH_MAP); ENTRY_FLOW extended.
- `customization/creation-suite-ui/js/suite.js`: ATTIRE tab gains **TEKKEN SLOTS ⇄ WWE REGIONS** browse toggle; `renderWweRegions` + `partsForWwe`; `renderPartGrid` supports per-part slot resolution (`cat.slotFor`) so WWE-region equips file under natural T7 slots. Default stays Tekken (no behavior change unless toggled).
- Docs: `docs/research/CREATION-SYSTEM-AUDIT-2026-10-22.md` (this audit's matrix), this blueprint.
- Coordination: worker 64 (clothing/accessory labeling + hair/headwear-as-library-items) — trees carry `wh`/`slots` mappings onto the shared T7 spine so their taxonomy plugs in without rework. Worker 61 (select-screen assets) feeds menu art per `UNIFIED-UI-SPEC.md` §8. Worker 62 (OSS games) — mined worker 22's OSS wave (game-hud UI kit → suite ui-kit; Material Maker/TEXTtoPBR → texture pipeline); no duplication.
