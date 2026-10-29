# CREATION-SUITE UI WIRING — round 2 map (2026-10-21)

What the suite's front end does, which game's pattern it comes from, and
where it lives. Round 1 (PRs #396/#399/#404/#438 + #445) built the spine;
this map covers the round-2 additions (owner orders 2026-10-21 ~11:46 CDT)
and pins the older patterns so future lanes wire *more* of the same, not
parallel inventions.

Code: `packages/creation-suite/ui/` (`index.html`, `suite.js`,
`profile.js` — state is pure, the DOM file only renders/routes) and
`packages/creation-suite/src/` (shared math/catalog layer). Bake truth:
`customization/CUSTOMIZATION-JSON-SCHEMA.md`.

## Round 2 additions

| Suite surface | Pattern source | Behaviour | Code |
|---|---|---|---|
| **PIECES tab** | Tekken 7/8 customization "parts from other characters" + WWE 2K body-part swapping | Five region rows (HEAD / TORSO / ARM L / ARM R / LEGS). Tap a region → tap a source fighter's model from `customization/region-sources.json` → assigned. CHANGE re-picks, RESTORE removes (restore = remove + re-bake; the record is the save). One source per region. | `suite.js renderPieces`, `profile.js setRegionSwap/removeRegionSwap` → record key `region_swaps`, bake step (a3) |
| **Placement nudge steppers** | PartPoser (the owner's named placement tool) + Tekken's fine-adjust | Every placement slider gets tap steppers: ±0.01 m position, ±1° rotation, plus per-axis scale sliders (X/Y/Z) beside uniform Scale, and RESET PLACEMENT (0 = the part's native seat on the bone — placement is exact bone-local since round 2, see the schema doc). | `suite.js openDetail` placement block + `nudge`/`place-reset` actions, `profile.js setPlacement` |
| **Hide base hair toggle** (PIECES tab) | Tekken's "hide default hair when a hairstyle is equipped" behaviour | Writes `hide_meshes: ["hair"]` to the record; the bake drops matching base meshes from the *output only*. | `profile.js setHideBaseHair`, bake step (a2) |
| **CLOTHING LAYERS section** (ATTIRE tab, worker 64) | Tekken 7/8 customization "parts on/off" + the owner's undress directive | The attire's OWN clothing meshes as toggleable layers with library-standard labels (`<category>_<item>_<variant>`); HIDE/SHOW per layer, saved per attire in profile state (`clothing`) → `clothing_layers.hidden` on the v1 record → mirrored to the game engine's `wh_clothing_v1` store so the choice is live in game/preview without a bake. Runtime engine: `game/js/clothing-layers.js`, config `game/data/clothing-layers.json`. In-game surface: pause menu CLOTHING sheet (`game/js/menus.js`). | `suite.js renderClothingLayers` + `clothing-toggle` action + `mirrorClothingToGame`, `profile.js setClothingHidden/isClothingHidden`, `assets.js createInstance` hook |
| **Stage swap count** | — | Stage meta line counts active piece swaps so a swapped look is never invisible state. | `suite.js renderStage` |

## The standing Tekken / WWE map (round 1, still the contract)

| Suite surface | Pattern source |
|---|---|
| ATTIRE tab: 16-slot spine in Tekken menu order, T6 sub-slots restored | Tekken 6/TTT2 customization slot layout (`src/slotmap.js`) |
| Tap → detail sheet → EQUIP; conflicts ask Replace/Cancel first | Tekken equip-conflict sheet |
| BODY tab: body-type row + single-tap skin tone | Tekken's group −237 colour settings row; No Mercy's 8-tone row |
| Color channels (up to 5 per item) + finish (roughness/metalness/tint) | Tekken per-item colour channels; extension D2 finish layer |
| WARDROBE: 4 attires × 10 look snapshots, explicit overwrite taps | DOA snapshot model on No Mercy attire slots |
| INK: stacked image layers with placed rects | WWE 2K logo/design layer stack (the D6 decal canvas) |
| PROFILE: name/title/style/parameters | WWE CAW profile block |
| Mobile shape: stage pinned top, sheet below, tab bar in the thumb zone, tap→scroll→TAP to assign — **never drag-and-drop** (owner law) | Tekken menu shape, phone-first |

## Rules for the next wiring lane

1. New surfaces go through `profile.js` state + `toCustomizationJson` —
   if it isn't in the bake record, it isn't a feature.
2. Every pattern added gets a row in this map with its source game.
3. The Rig & Pose Studio lane builds the suite's rig/pose mode on the
   **same** record/schema (checkpoint `rig-pose-studio.json`) — one
   control surface, two modes, never a fork.
