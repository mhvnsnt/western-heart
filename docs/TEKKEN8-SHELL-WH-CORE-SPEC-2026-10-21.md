# TEKKEN 8 SHELL / WESTERN HEART CORE — LOCKED ARCHITECTURE

Owner directive 2026-10-21 ~19:24 CDT. This document is the governing spec for the
character select + creation suite. It supersedes the layout wording in all earlier
briefs (including docs/CREATION-SUITE-UI-SCHEMA-2026-10-21.md, which remains the
record-level schema reference only).

## PRINCIPLE

Owner's words in substance: **"build it in the layout and set up of Tekken 8"** BUT
**"work with my game roster and canon and files — do not dumb it down or water it
down to just what Tekken has. We're putting Western Heart on top of this."**

Tekken 8 = presentation shell ONLY. Content and logic = Western Heart canon plus the
multi-game teardown files: **WWF No Mercy, WrestleMania XIX, Def Jam, Tekken 5,
Tekken 6, Tekken Tag Tournament 2, and some WWE 2K.**

Platform (owner directive 2026-10-21 ~19:32 CDT — this OVERRIDES the earlier
"build in the web stack" note): **Three.js/WebGL is PERMANENTLY OUT** — owner's
words: "we're not going to use 3js… we're going higher and better than 3js… using
all of these teardown files and whatever engine we can use for mobile games."
Western Heart moves to a **NATIVE mobile engine** producing a standalone
executable. **Godot 4 is the owner's named frontrunner**, but the final pick is
made by the owner's deep-research directive (Godot 4 vs Unreal vs Unity vs Flax,
judged on OUR criteria: skinned GLB pipeline, retargeting, bone morphs, decals,
physics accessories, touch UI, direct-APK distribution, licensing). Until the
verdict lands, work proceeds on the **engine-agnostic layers only**: parts
registry + provenance, slot/JSON serialization schema, the bake/swap engine,
template normalization. **No new UI is built in the web stack.** This spec still
governs WHAT gets built — only the implementation target changed.

Blueprint caution: the Godot blueprint the owner forwarded is **Gemini-generated
reference material with known oversells** (e.g. BoneAttachment3D is rigid
attachment, not skinned deformation). Its feature claims are UNVERIFIED until the
research run and our own tests confirm them. The same caution applies to every
number/detail from the pasted blocks: if it didn't come from the owner or the
repo, verify it before it enters this spec.

Roster scale (owner correction 2026-10-21 ~19:37 CDT): the "36-fighter canon"
figure in the pasted directive is a Gemini hallucination — STRUCK. The select
grid + suite cover the **full Western Heart roster** and must be designed to
**scale as the roster grows** (grid adjusts like T8's does with DLC — never a
hard-coded count). Citable counts are the repo-verified audits only (see
VERIFIED COUNTS below).

Standing-law conflict rule: where any sub-feature below conflicts with a standing
owner law, the standing law wins and this doc says so (e.g. moveset editing and all
assignment flows are **tap / scroll + tap-to-assign, NEVER drag-and-drop**; decal
placement by touch-glide is a *placement* gesture on the mesh, not an assignment
drag — layer reordering is by tap controls, not dragging).

ALL-MENUS RULE (owner directive 2026-10-21 ~19:47 CDT, generalized from the
stage-select playtest, §F): **EVERY menu in the game — main menu, character
select, stage select, customization, pause — takes its layout from the Tekken
games' teardown files.** Hand-tooled menu inventions are banned across the
board, not just in the suite. A menu whose layout cannot be traced to the
teardown files is a defect, the same as a control that does not change the
preview.

## (A) CHARACTER SELECT — replaces the current select layout

Tekken 8 structure:

- Roster **GRID** as a tight block, bottom center-right, floating above the bottom
  edge. The grid is formatted to the **WH canon roster** (not Tekken's roster).
- Highlighting a fighter streams the **actual WH 3D model walking into frame** —
  P1 on the left half, P2 on the right half — with a fluid idle animation.
  NOT portraits. NOT the old bisected-preview / card-strip layout (PRs #384/#387
  layout is replaced by this section).
- Stat blocks sit flush at the FAR edges and carry **WH canon fields**:
  **True Name, Home Turf, Weight Class, Archetype (Grappler / Striker / Chimera…),
  Active Move Archetype.** (T8 shows name/rank/style/nationality/height/weight —
  the WH fields replace them; Tekken roster data is never shown.)
- CONFIRM = lock-in animation + voice line.
- BEFORE lock-in, a pop-up over the portrait cycles attire/custom slots:
  **Slot 01 = canon 1P attire, Slot 02 = canon 2P attire, Slots 03–10 = custom
  outfits** (see serialization, §E).

## (B) CUSTOMIZATION FLOW — T8 routing exactly

Main Menu → **Customization tab** (Character Customization / Avatar / Player
Customization sub-menus) → **Character Chooser** = the same roster grid on a neutral
studio-lit background → **SLOT BRIDGE**: a save-slot grid first (default slots are
uneditable; **"Use as Base"** copies a default into a custom slot; picking an
empty/custom slot boots the editor) → **EDITOR** → on Save, **PHOTO BOOTH exit**:
pose taken from WH's actual combat keyframes / win poses, camera angle + background
pick, capture becomes that slot's portrait thumbnail.

## (C) EDITOR — T8 spatial law

- **25% left docking drawer / 75% 3D viewport** (landscape). The model stands in a
  **clean idle** (no looping combat stance) so clipping is visible.
- Category list → item grid swaps **within the same 25% footprint**.
- **Footer legend** (bottom ~10%) states what each control does in the current state.
- Color = **floating palette overlay** beside the grid: recents + presets + exact
  HSV/RGB sliders + material reflection controls.
- **Shoes are their own slot.**
- Unequip baseline = **clean street baseline** (white tee / jeans / sneakers class),
  not underwear.
- **PORTRAIT ADAPTATION (owner standing law):** on the owner's portrait phone the
  same structure reflows — drawer becomes tap-open sheets, the viewport is NEVER
  blocked, everything is usable vertical. Landscape keeps the classic 25/75.
  All menus/sub-options live in **tabs/sheets that open only when tapped**.
- **The preview must obey taps:** every selection (body type, hair, clothes,
  accessories, skin tone) visibly changes the preview immediately. A control that
  does not change the preview is a defect, not a placeholder.
- **Creation base templates** (owner directive 2026-10-21 ~19:09 CDT): the base is
  NEVER the Mixamo soldier. The base-template picker offers **variations of the
  games' own creation templates** — Def Jam creation (CAW) templates, Tekken
  customization/creation templates, WWE game character-creation templates (their
  default/template models those games build on) — PLUS two more modes:
  (a) build from pieces/parts of the in-game characters, (b) **edit the in-game
  characters themselves directly.** Parts editing covers template builds and
  existing roster characters alike.
- **Owner-control parity law:** every edit capability used from the tooling end
  (cuts, placements, tone matching, rig edits) must exist as the owner's in-game
  control, wired for real. If it isn't in the game, it isn't done.

## (D) THE DEEP STACK — inside the drawer (watering down is banned here)

- **MORPHS & CHIMERAS:** bone-scaling sliders (No Mercy proportions — giant
  torso / tiny legs class) via rest-pose offsets on our template rigs; head
  chimeras/masks (animal heads, wolf/dog variants) with eye-glow, jaw hinge, fur
  cards; direct-touch face-sculpt zones (nose / jaw / brow / cheeks); injury/aging
  layers (scars, cauliflower ear, vascularity, grit).
- **ATTIRE 4-TIER LAYERING (Tekken 6 fragmented schema):** Base Underlayer / Core
  Garment / Outer Layer / Limb Modifiers as separate sub-slots. Hair is MODULAR
  like T6 — Base + Bangs + Sides + Ponytail/Extensions cycle independently, with
  dual-tone root/tip gradients. Z-index layer ordering with **AUTO-CULLING** of
  hidden polys under outer layers (no clipping, no hand fixes). 1P/2P/3P
  model-state selection like T6.
- **BLING & WEAPONS (Def Jam):** chains / medallions / rings / belts ride physics
  bone sockets (neck / spine / wrist) with inertia + torso collision — they swing
  when the model rotates. Equippable weapons carry the flag: **Cosmetic Display**
  vs **Usable Command Move** (usable injects the move into the character's
  command list).
- **DECALS (TTT2 projector + 2K layering):** decal projector placed by touch on the
  mesh (glide over UVs, two-finger twist = rotate, pinch = scale); layer stack
  with ordering; material sliders (roughness / metallic / normal depth / skin
  alpha — faded vs fresh ink). The decal LIBRARY is pre-populated with **Western
  Heart iconography** — turf logos, graffiti tags, gang signs, tribal markings,
  Ed Hardy-style art — never generic stars/hearts.
- **BROWSING (MDickie tap loops):** per-slot **< Name >** inline tap-cycling for
  instant flipping; tap-the-name expands the 3-column thumbnail grid for deep
  libraries; quick-color pill per item; **NO modal full-screen takeovers**;
  persistent bottom dock: **Undo / Redo / Pose-Taunt / Action Preview / Save /
  Exit**.
- **ACTION PREVIEW (in-suite testing):** pose scrubber (A-pose, idle, clinch,
  back-bump keyframes) to check coats/chains/hair for clipping in motion; **Move
  Tester** — tapping a move executes it on a sparring dummy in the viewport,
  in-suite (owner law: he tests where he builds).
- **CAMERA (touch matrix):** 1-finger orbit (pitch clamped), pinch zoom (face
  close-up to full body), 2-finger vertical pan, double-tap a body region =
  smart focus/zoom to that region.

## (E) SERIALIZATION

Saves are JSON: equipped mesh IDs, material/color overrides, decal UV coords +
transform matrices, accessory socket offsets (XYZ translation / rotation / scale),
morph values — stored **per fighter per slot** under `roster/<id>/slots/slot_<n>.*`,
with thumbnails captured by the photo booth. This extends (does not replace) the
existing per-attire `customization.json` record: slots 1–2 map to the canon
attires, slots 3–10 to custom slot files.

## (F) STAGE / ARENA SELECT — Tekken pattern (owner directive 2026-10-21 ~19:47 CDT)

Stage select is under the SAME law as character select (§A) and the suite:
its layout comes from the **Tekken games' teardown files**, never a hand-tooled
menu. It sits in the flow between character confirm (§A lock-in) and the fight,
and it is a gate, not a dead end: a player who reaches it can always see every
stage, pick one, and continue.

**Required pattern (Tekken stage select):**

- **Scrollable thumbnail grid** of stages. Every stage in the game is reachable
  by touch scrolling, in portrait AND landscape. A stage that exists but cannot
  be scrolled to does not count as offered.
- **Large live preview that tracks the highlight.** Highlighting a stage
  immediately shows THAT stage in the preview. The preview, the highlighted
  card, and the name/description must always agree — never a banner naming one
  stage while another is highlighted.
- **Name/description INSIDE the layout** — in a fixed layout region sized for
  the text (wraps, never runs off the screen edge), never a floating overlay
  banner covering the preview.
- **Unique thumbnail per stage**, captured from that stage itself. Two stages
  sharing one thumbnail image is a defect.
- **A Random option** in the grid, like Tekken's.
- **An always-visible confirm path into the fight.** Confirm is on screen at
  all times (not scrolled away, not hidden behind the preview or a banner);
  tapping a highlighted stage and confirming starts the match on that stage.
- **Portrait law applies in full** (same as §C): on the owner's portrait phone
  the grid, the preview, and confirm are ALL visible/usable — the grid may
  reflow as a sheet, but the preview is never the only thing on screen and
  confirm never disappears.
- **Content + provenance:** stages are Western Heart's stages, drawn from the
  teardown libraries (the current list is the WWF No Mercy arena set —
  SmackDown, Royal Rumble, King of the Ring, SummerSlam, Backlash, Armageddon —
  plus WH-original stages such as Shrine of the Blade). Every stage card
  carries its TRUE source (e.g. "WWF No Mercy (N64)"), same provenance law as
  parts.

**Playtest evidence (owner, live site, 2026-10-21 ~19:46 CDT —
`~/workspace/user/files/1000176061_0_8bqs.png`,
`~/workspace/user/files/1000176060_1_waxj.png`,
`~/workspace/user/files/1000176059_2_fghu.png`; verified with my own eyes
2026-10-21):** the current hand-tooled stage select is a DEAD END —

1. The stage list **cannot be scrolled**; not all stages can be seen, and in
   portrait (1000176059) the grid is not visible at all — only the preview and
   a description strip.
2. There is **no visible way to continue to the fight** from this screen.
3. The description banner **overlays mid-screen** and its text **runs off the
   right edge** ("ARMAGEDDON — The real No Mercy Armageddon arena. Extracted
   from th…", "…Paper lanterns cast warm lig…").
4. **Every stage card shows the SAME thumbnail** (one identical red-rope ring
   image on SmackDown / Royal Rumble / King of the Ring / SummerSlam /
   Backlash / Armageddon).
5. **Preview/description disagree with the highlight:** the banner reads
   "SHRINE OF THE BLADE" while ARMAGEDDON is the highlighted card
   (1000176060), and the preview behind the grid is a near-empty dark space
   with floating quads rather than the highlighted stage.

## PARTS PROVENANCE LAW (owner, standing)

Parts come from ALL teardown libraries, wired in AND usable: **No Mercy,
WrestleMania XIX, WWE 2K, Tekken, DOA, Def Jam.** Every part record carries its
TRUE provenance (if a part is from No Mercy, its record says No Mercy — the owner
approved the "red chest plate" naming where the No Mercy origin is real).

## HEAD-SWAP RECORD (owner verdict 2026-10-21 ~18:55 CDT, on the Kevin→Master White proof)

The swap is graded CLOSE. Required corrections, which are also standing controls:

1. **CUT LOWER** — the cut clipped the chin; the FULL chin/jaw comes with the head.
   In-game form: a CUT control (cut height/plane on a part) usable on ANY part of
   ANY model, saved per-attire.
2. **Match the BODY's skin tone** (the big skin tone — neck/chest) **to Kevin's
   head skin tone.**
3. **Seat the head on properly, facing forward.**

## VERIFIED COUNTS (numbers rule — owner 2026-10-21 ~19:39 CDT)

The ONLY citable counts are the repo-verified audits:

- **Roster (model-key audit): 58 roster entries** — 33 own-model, 10
  base-by-design, 13 wrong→fixed, 2 no-model.
- **Movesets: 57 fighters.**
- **Attire provenance sheet: 101 attire rows** — 53 Tripo-original, 4 Tripo
  reskin-of-source, 13 source-game models, 12 retextures, 10 community rips,
  9 unclassified; 79 wired / 19 not wired / 3 broken.
- **Parts (in-tree registry): 1,150** in `customization/PARTS-REGISTRY.json`.
  The "4,523 parts" figure is UNVERIFIED — never cite it or any other session's
  unverified recount (e.g. "59/50"). The suite runtime catalog
  (`customization/creation-suite-ui/data/parts-catalog.json`) must be recounted
  from the file whenever it is cited.

A consolidated census doc is being produced by a dedicated lane
(`docs/ROSTER-COUNT…`); when it lands, cite it. Until then, the audits govern.

## PHASING (implementation order inside this shell)

**Until the engine verdict lands (platform section above), only the
engine-agnostic layers are built:**

0a. Slot/JSON serialization schema (§E) — engine-neutral data, per fighter per
    slot, incl. the CUT control's fields (cut plane per region swap) and the
    rig section landed by PR #462.
0b. Parts registry + true provenance for all teardown libraries; verified
    counts only.
0c. Bake/swap engine corrections: head-swap redo (cut lower — full chin/jaw;
    body skin tone matched to the head's tone; forward seat) with LOUD failure
    on empty grafts; template normalization per the Rig & Pose Studio standard.
0d. Base-template DEFINITIONS as data: the games' own creation-template
    families (Def Jam CAW / Tekken creation / WWE CAW) + roster characters —
    as registry entries the future engine UI will consume. No web UI is built.

**After the engine verdict, inside the chosen native engine:**

1. Preview obeys taps on authored bases (no Soldier-class default anywhere).
2. Editor spatial law (§C): 25/75 landscape drawer/viewport + footer legend;
   portrait tap-open sheets; preview never blocked.
3. Slot bridge + base-template picker (template families + roster characters).
4. In-game CUT control + placement surface (bake already honors the fields).
5. Select screen (§A), stage select (§F — scrollable grid, tracking preview,
   in-layout description, random, always-visible confirm), and photo booth
   (§B exit). Every other menu (main menu, pause) is laid out from the Tekken
   teardown files per the ALL-MENUS RULE — no hand-tooled menus anywhere.
6. Deep-stack systems (§D) in drawer order: morphs/chimeras → 4-tier layering +
   modular hair → bling sockets → decals → action preview.
