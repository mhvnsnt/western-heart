# Creation Suite UI v2 — the file-derived front end (2026-10-21)

Owner correction that produced this build (2026-10-21 ~10:44 CDT): the v1
suite (PR #445) was rejected on presentation — "that's all hand tooled and
I can tell none of that came straight from the files." His requirements:
controls nested in submenus/subsets like Tekken and the WWE games; the
EXACT Tekken front-end layout; the CHARACTER VISIBLE while changing
everything; menus/sliders only partially on screen as overlays; built
from the games' actual front-end files and code — Tekken's suite mixed
with the WWE suite.

v2 keeps v1's data layer byte-for-byte (src/catalogs.js merge,
src/slotmap.js spine, ui/profile.js state contract, the
wh_creation_suite_v1 save record + customization.json v1 export) and
rebuilds only the presentation, in `packages/creation-suite/ui2/`.
v1's test suite passes unchanged against v2 (4/4, §7).

---

## 1. Front-end file inventory (evidence first)

Two read-only surveys were run over every held teardown
(`survey/tekken-frontend-inventory.md`, `survey/wwe-defjam-frontend-inventory.md`
in the lane's records; per-file JSON twins list 546 WWE/Def Jam entries).

### Tekken 6 (PSP) — structure and text are real; art is locked
- REAL: 9,440 item-name records (`customization/parts/tekken/tekken6-item-names.json`,
  from the decrypted bulk); 120 NTXL UI string tables (strings incl.
  "Select item to equip.", "Purchase item?", "Equip item?", "The hair
  item must be removed to equip this item." — the conflict prompt's own
  words); the customization classes in the decrypted EBOOT
  (`tcb_customize_mode_t`, `CUSTOMIZEPACK%d_%d`, `sbcustomize_item_t`).
- EXTRACTED ART: `PSP_GAME/PIC1.PNG` (480×272 key art) + `ICON0.PNG`
  (XMB icon) in `wh/teardown/tekken6/ui/`. That is all.
- ABSENT: every panel/frame/cursor/glyph/font/customization-screen
  texture. The UI art lives in the ISO's raw-sector tail and the
  decrypted bulk's GZIP/COM containers — 56 of 76 GZIP containers still
  fail to decode (the game's own inflate rejects them too), 0 GIM
  textures have ever been carved. T6's font is an `owfont` .fnt/.ntx
  pair referenced in the EBOOT only. No pixel layout/positions exist
  for any Tekken game in holdings.

### Tekken 7 — documented layout only; sprites INCOMING (W6)
- REAL: the 16-slot schema, SlotGroupID menu order (−254…−236),
  21-field item record, conflict rules (tekkenmods documentation,
  `tekken-customization-extraction/REPORT.md`; carried into
  src/slotmap.js by v1).
- ABSENT (stated plainly): Tekken 7's own UI sprites live in its
  un-acquired game paks — 0 T7 UI files in holdings at survey time.
  Per the owner's 2026-10-21 ~10:57 CDT order, acquisition is un-parked
  and running piecewise in the gap-closure lane (W6, target set #2 =
  front-end/UI files, straight to repo storage). v2's theme is built
  as asset slots so the T7 files drop in as a swap (§5).

### WWF No Mercy (N64) — THE front-end art source
- REAL: the ROM texture dump in this repo,
  `teardown/wwf-no-mercy/textures/` — 1,441 ROM PNGs, of which **429 are
  front-end** (main menu, character select, arena/championship/belt
  menus, HUD messages, lobby) + 64 menu-scene textures. The six
  edit-mode (CAW) tab graphics — Appearance, Moves, Fighting Style,
  Parameter, Profile/Music, Ally/Enemy — are the game's own
  creation-suite category art.
- CAVEAT (verified by viewing): the dump's filenames are unreliable for
  several character_select/main_menu files (e.g. the file named
  `..._Glowing_Character_Square_459D` contains the VS badge;
  `..._1P_Glow_45A3` contains "2P"; `Belt_Menu..._Background_458D`
  contains a WWF logo tile). Every file bound into the v2 theme was
  viewed and content-verified first; misfits were extracted, renamed
  to their true content, and left unbound (§3).

### WrestleMania XIX (GC) — content, not chrome
- 1,477 decoded textures in `customization/parts-converted/wmxix-textures/`
  are 100% CAW part textures (face/hair/clothes/gear). **Front-end
  subset: 0 of 1,477.** No fonts/icons/cursors. (7 arena-signage logos
  exist in `teardown/wmxix/textures/` — arena dressing, not menu art.)
  WMXIX's contribution to the suite is parts and face-paint content.

### Def Jam: Fight for NY (PS2) — front-end EMPTY
- 0 front-end files extracted anywhere. The ISO documents `SCREENS/`
  and `FONTS/` root folders; they were never range-extracted, and the
  ISO is not on local disk. Extraction is a new job (the W5 lane's
  surgical method), not an inventory pull. The Def Jam section of the
  suite is unskinned until then — stated, not papered over.

---

## 2. What the skin is made of (extraction manifest)

Bound into `packages/creation-suite/ui2/theme/` via `theme.json`
(asset slots — the skin is data, not hard-coded CSS). Each entry:
game, exact source path, method. All bound files were viewed by the
lane before binding.

| Theme slot / icon | File | Game · source |
|---|---|---|
| panelFrame | panel-frame-instructions-tile.png | No Mercy · `teardown/wwf-no-mercy/textures/rom/main_menu/Main_Menu_Z_Instructions_Background_458C.png` — a framed black panel tile (the game's own framed-box graphic), bound as the panel border-image |
| cursor (equipped marker) | character-select-1p-marker.png | No Mercy · `.../rom/character_select/Character_Select_1P_45A2.png` — the "1P" select marker, shown on the equipped row: the marker's own job |
| keyArt | tekken6-key-art-pic1.png | Tekken 6 PSP · `PSP_GAME/PIC1.PNG` from the ISO (byte-identical extracted copy) — fighter-select banner; PIC1 is the PSP's selection backdrop art |
| icon: appearance | icon-tab-appearance.png | No Mercy · `.../rom/edit_mode_tabs/Edit_Mode_Tabs_Appearance_4A3B.png` |
| icon: parameter | icon-tab-parameter.png | No Mercy · `.../Edit_Mode_Tabs_Parameter_4A41.png` |
| icon: fightingStyle | icon-tab-fighting-style.png | No Mercy · `.../Edit_Mode_Tabs_Fighting_Style_4A3F.png` |
| icon: profileMusic | icon-tab-profile-music.png | No Mercy · `.../Edit_Mode_Tabs_ProfileMusic_4A39.png` |

Extracted but deliberately NOT bound (content did not match the slot;
kept in theme/ as inventoried material, recorded in theme.json
`unbound[]`): the "Multi Play" main-menu tile (dump name claims a
header border), the belt-menu WWF logo tile (claims a background),
the VS badge (claims a glowing square), the "2P" marker (claims 1P
glow), a lobby environment pattern tile (claims a black box), a 16×16
PPV background tile (No Mercy backgrounds are tile/3D-scene
composites — no full-screen background file exists).

Reconstructions — LABELED, never presented as file-derived
(theme.json status "reconstruction", CSS fallback in suite2.css):
panel background fill, header plate, prompt-bar button glyphs (the
No Mercy recomp project's promptfont.ttf exists in the repo but is
the recomp project's own font, NOT original game art — deliberately
not bound), display font (no game font has ever been extracted; T6's
owfont pair is locked in the bulk), arrows, and the stage dressing
(dark void + ring platform drawn by viewer.js — the shape both
suites use, but ours).

## 3. Asset ledger (on-screen element → source)

| On-screen element | Source |
|---|---|
| Menu panel frame edge | EXTRACTED — No Mercy framed panel tile (panelFrame slot) |
| Panel background fill | reconstruction (labeled) — no background file exists (§1) |
| Category rows + order | Tekken SlotGroupID order + T6 sub-slots, from the documented schema (src/slotmap.js, v1) — structure from files/docs, not invented |
| BODY / FACE row chips | EXTRACTED — No Mercy APPEARANCE edit-mode tab graphic |
| PROFILE row chip | EXTRACTED — No Mercy PARAMETER tab graphic |
| PROFILE ▸ Fighting Style label | EXTRACTED — No Mercy FIGHTING STYLE tab graphic |
| WARDROBE row chip | EXTRACTED — No Mercy PROFILE/MUSIC tab graphic |
| Equipped-row marker | EXTRACTED — No Mercy "1P" character-select marker (cursor slot) |
| Fighter-select banner | EXTRACTED — Tekken 6 PIC1 key art (keyArt slot) |
| Top plate, prompt chips (Select/Back/Save text) | reconstruction (labeled) — layout follows Tekken's prompt-bar convention; no glyph files exist |
| Fighter model + attached parts | the game's real GLBs + catalog parts, attached by the shared consumer code path (§4) |
| Stage floor/ring | reconstruction (labeled) |

## 4. The rebuilt presentation

Viewport-first: the live stage (Three.js/WebGL) fills the screen;
every control is an overlay covering part of it.

- **Live character viewport** (`ui2/viewer.js`): renders the selected
  fighter's real GLB and attaches the profile's parts with the game's
  OWN code — `src/parts.js` applyPart/removePart, `src/attire.js`
  attach/applyEdit, and the consumer's exported `effectivePlacement`
  imported from `game/js/customization-consumer.js`. Imported, never
  forked. Morphs preview through `src/morphs.js` applyMorphProxies;
  body-type scale through `game/js/custom-fighter.js`
  customFighterToRoster — the same conversions the fight uses.
- **Nested drill-down** (Tekken's entry flow): FIGHTER → category list
  in SlotGroupID order → source SUBSETS (All / WMXIX / No Mercy /
  Def Jam / libraries — the per-game groupings) → item list → tap =
  TRY-ON on the live model → EQUIP commits, with the Replace/Cancel
  conflict sheet (FULL_HEAD/FULL_BODY rules from the documented
  schema; the prompt wording follows T6's own NTXL strings).
- **Detail sheet** (per part): bone-socket placement (pos m,
  pitch/yaw/roll °, scale — Tekken's PartPoser ranges), ≤5 color
  channels (channel 1 tints live), finish (roughness/metalness),
  mirror toggle — all applied live through applyEdit (the game's
  base-relative, idempotent edit path), committed to the profile on
  release. This is the in-suite placement control the owner ordered
  after the Kevin proof (placement must be doable by him in the
  suite).
- **BODY/FACE tool screens**: body type, the SKIN TONE tool row
  (SlotGroupID −237), body + face morph sliders (live proxies; the
  bake stays ground truth). INK: texture layers. WARDROBE: title pair
  + 10 look snapshots (options stack, never overwritten). PROFILE:
  name, archetype, parameters. 4 attires per fighter.
- Interaction laws kept from v1: tap → scroll → TAP to assign (no
  drag-and-drop anywhere), ≥48px targets, saves write the
  wh_creation_suite_v1 record + per-attire stash, customization.json
  v1 export.

### Two editor-side correctness notes (found + fixed in v2)
1. **Attach order**: attach cancels the socket's current world
   scale, and morph proxies SET bone scales — so the editor applies
   morphs BEFORE attaching, and re-attaches on morph-slider release.
   (In-fight the consumer attaches once against final bone scales;
   the editor now presents the identical result.)
2. **Center-once**: the consumer re-centers part geometry in place
   on the shared cached scene — correct for its attach-once use.
   The editor re-applies records continuously, and re-centering
   shared geometry walks the piece on every apply (measured: the
   piece's geometry centre moved (0,9,−13) → (0,−4,−22) between
   applies). The editor therefore centers a private geometry copy
   once per part and clones it per apply. First-apply results are
   identical to the consumer's (verified pixel-identical:
   boot render ≡ re-applied render). FLAG for the consumer's lane:
   the same walk would hit a second fighter equipping the same part
   in one game session.

## 5. Tekken 7 drop-in (W6)

The Tekken side is skinned through slots precisely so the incoming
T7 front-end files are a swap, not a rebuild: when a T7 UI file
lands in the repo (gap-closure W6, target set #2), copy it into
`ui2/theme/`, point the slot's `file` at it in theme.json, flip its
record to status "extracted", game "Tekken 7" — no CSS/JS change.
Expected slots: panelFrame, panelBg, headerPlate, glyphConfirm,
glyphBack, cursor, fontDisplay (theme.json `t7DropIn`).

## 6. Deviations and honest gaps

- Mirror toggle writes the profile flag and negates the live X
  offset; a true mirrored re-bake happens in the game's bake path,
  not in the preview. Labeled in the UI doc comment.
- Skin tone is stored and applied by the game's CAW path; a roster
  fighter's authored textures are never re-tinted in the viewport
  (the consumer's contract) — the swatch is state, not a live tint
  on roster models.
- No Mercy body-part shells attach as modeled — the AKI shells are
  sectional meshes (a chest shell includes its arms), identical to
  the in-fight consumer's result with the same record.
- Fighters whose GLBs are absent from a given tree surface an honest
  "model not available" toast; nothing is faked.
- Def Jam chrome: none exists (§1) — the Def Jam subset is a data
  filter today, unskinned until SCREENS/ extraction happens.
- WMXIX chrome: none exists (§1) — WMXIX appears as subsets/content.

## 7. Proof (own eyes, Playwright 390×844, character in every frame)

In `packages/creation-suite/ui2/proof/` (seeded with the same
UI-built Pantera profile the fighter-completeness lane proves
in-fight: No Mercy chest/back part at yaw 45°, channel-1 #c0241c,
muscle/shoulders/eye morphs, one eye layer, RAGING BEAST title):
- `01-root-character-visible.png` — root categories over the live
  fighter; No Mercy tab art bound on BODY/FACE rows.
- `02-items-upper.png` — Upper Body subset bar + search + item list;
  the equipped row carries the extracted 1P marker.
- `03-tryon-part-on-fighter.png` — try-on bar; the previewed No Mercy
  chest shell applied to the model, menu collapsed to a sliver
  (attach instrumented: `applied: [upper_body …model_116E], skipped: []`;
  the shell's collar section reads at the neck — AKI shells attach
  exactly as modeled, §6).
- `04-adjust-placement-color.png` — detail sheet over the try-on:
  placement yaw set to 60°, color channel 1 set red; both edits ride
  the shared live-edit path (applyEdit) on the attached piece.
- `05-morph-live.png` — BODY screen; muscle/bulk at max vs §boot
  (canvas lit-fraction 0.367 → 0.380; the model visibly widens).
- `06-drilldown-face-eyes.png` — three levels deep: root → FACE →
  EYES (Mesh), texture-ready eye parts with source subsets.
- `07-wardrobe.png` — title pair (RAGING / BEAST) + 10 look slots.
- `08-conflict-replace-cancel.png` — Replace/Cancel sheet: equipping
  a full-body skin against the equipped upper part.
- `09-fighters-keyart.png` — fighter select under the extracted
  Tekken 6 PIC1 key-art banner.
- `saved-profile.json` — the record the UI's Save wrote back
  (wh_creation_suite_v1 contract).
- Tests: v1 suite (`test/slotmap.test.js`) 4/4 PASS against the real
  catalogs — 7,791 parts merged, 2,869 equippable, 5,574 spine-mapped;
  profile resolves end-to-end and round-trips both save shapes.
  Boot ≡ re-apply pixel identity verified (attach/centering fix, §4).
