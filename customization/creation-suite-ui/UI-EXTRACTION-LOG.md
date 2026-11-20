# Creation Suite UI — Extraction Log

Owner order 2026-10-18 ~23:47 CDT: "the real menus and sub-menus, the UI and layout pulled
VERBATIM from the teardown games." This log records exactly what came from which game files,
and where the honest gaps are. No invented UI — every menu node in `js/menu-data.js` carries
its source tag.

## What "verbatim" means here

The actual `.uasset` menu-layout binaries and UI pixel layouts are NOT in any teardown we
hold (see §6). What IS verbatim: the **information architecture** — menu trees, category
names, slot IDs, UI group ordering, conflict rules, color systems, buy/equip flows, slider
sets. Those come straight from the game data files below.

## 1. Tekken 7 — item schema + UI organization (VERBATIM)

**Source files (in repo):**
- `customization/parts/tekken/tekken7-slot-catalog.json` — 17 slots with UI titles
  (HEAD/HAIR/FULL_HEAD/HAIR_ACC/GLA/FACE/FACE_HAIR/MAKE_UP/UPPER/FULL_BODY/LOWER/
  UPPER_ACC/LOWER_ACC/EXTRA/EFFECT/AURA), slot-group IDs (-236..-254, the actual
  in-game UI group ordering), zone-conflict rules, 21-field item CSV spec, 0-5
  color-slot system, asset prefixes (EI/ECI/ACI/CS/CCI/CI), T8 additions.
- `~/workspace/tekken-customization-extraction/REPORT.md` (2026-10-16) — the
  extraction report: positioning paradigm (position X/Y/Z + rotation
  pitch/yaw/roll + scale per accessory — the same paradigm as PartPoser's
  10 sliders), socket-based attachment, color system.

**What the UI takes verbatim:** the ATTIRE category tree (`js/menu-data.js`
ATTIRE_TREE) uses T7's slot IDs and UI titles exactly; conflict prompts use T7's
zone rules; color editing offers up to 5 channels; the entry flow (pick fighter →
pick slot → category list) and buy/equip two-step + hover try-on + exit→photo
mode follow T7's verified behavior.

## 2. Tekken 6 PSP — subdivisions (VERBATIM structure)

**Source:** Tekken 6 PSP teardown (`~/workspace/game-reverse-engineering/tekken6/`,
816MB ISO + extracted/DATA401.IDX) via UNIFIED-UI-SPEC.md §5.2.

**What the UI takes verbatim:** Upper Inner/Outer sub-slots, separate Hands slot
(T7 merged it away), separate Feet slot, Waist L/R — nested under the T7 spine
in ATTIRE_TREE.

## 3. Tekken 8 — additions (VERBATIM from research)

**Source:** `tekken7-slot-catalog.json` → `tekken8_additions`.

**What the UI takes verbatim:** separate Footwear slot, 30 shared slots note,
2-accessory-slots-per-area rule.

## 4. WWE 2K — CAW editor flows (RESEARCHED, not extracted)

**Status:** WWE 2K19/2K18 game files are NOT on disk (`customization/wwe2k-caw/PULL-PLAN.md`
— 51GB pull blocked on TeraBox verification). No `pac/edit/` binaries to extract from.

**Source files (in repo):**
- `moveset-library/MOVESET-EDITOR-RESEARCH.md` — WWE 2K Create-A-Moveset flow:
  Creations tab → Move-Set → pick superstar → Moves → category → position →
  select empty slot → select move from list → assigned. Slot-first, strict slot
  eligibility, NO drag-and-drop anywhere. Fighting style inside the editor
  (2K16: Aerialist/Brawler/Giant/Powerhouse/Showboat/Striker/Technician) +
  personality sliders.
- `customization/wwe2k-caw/PULL-PLAN.md` — pac/edit targets (bbtemplate/default/
  edit/sample.pac, slots 256/257 base bodies).

**What the UI takes verbatim:** the tap-to-assign law (tap slot → scroll library →
tap to assign, from MDickie's tap grammar in the same research doc), slot-first
assignment in every picker, fighting-style + personality sliders in PROFILE,
positional move categories. The WWE CAW *screen layouts* themselves are not
extracted — honest gap, documented here.

## 5. WWF No Mercy / WrestleMania XIX — body + profile (VERBATIM)

**Source:** `teardown/wwf-no-mercy/re-docs/docs/ui/menus/edit-a-superstar.md`
(via `customization/UNIFIED-UI-SPEC.md` §2/§4/§5.1).

**What the UI takes verbatim:** 4 attire slots per fighter; moveset/AI shared
across attires (lock icons); profile page 1 fields; 14M+9F body types, 8 skin
tones, 7M+3F head shapes, 28M+20F faces; WMXIX parametric proportions
(Height/Weight/Muscle/Shoulder/Chest/Waist/Hips/Arms/Legs).

## 6. DOA6 — wardrobe (VERBATIM structure)

**Source:** research via `customization/UNIFIED-UI-SPEC.md` §5.3.

**What the UI takes verbatim:** 10 wardrobe slots per fighter (Costume +
Hairstyle + Glasses + Title snapshots), two-phrase titles, quick-swap at
fighter select.

## HONEST GAPS (not extracted — do not claim otherwise)

1. **Tekken 7 `.uasset` UI layout binaries** — menu pixel layouts, fonts, icon
   textures. Not in any teardown. The UI's visual design is original.
2. **WWE 2K `pac/edit/` binaries** — game files never landed; CAW flows are
   researched, not extracted.
3. **Exact min/max ranges for Tekken accessory placement** — unknown; the UI
   uses ±0.5m position / ±180° rotation / 0.1–3× scale as sane bounds.
4. **Kenney UI Pack** — donation-gated download, could not pull without a
   payment flow; Say_K GUI pack lacks a clean license; Godot asset library
   refused the connection. UI art is original (zero license risk), documented
   in WORKLOG.md. three.js (MIT) viewports via the repo's vendored copy.

## Free/available industry-standard pieces wired in

| Piece | License | Where |
|---|---|---|
| three.js r1xx (3D viewport) | MIT | `customization/create-fighter/vendor/three.module.js` (already in repo) |
| GLTFLoader | MIT | `customization/create-fighter/vendor/addons/loaders/GLTFLoader.js` (already in repo) |
| Tap-to-assign grammar | MDickie design pattern (documented) | every picker in `js/suite.js` |
| Spring-bone jiggle model | industry standard (research) | `data/jiggle-schema.json` — real params land with the jiggle lane |
