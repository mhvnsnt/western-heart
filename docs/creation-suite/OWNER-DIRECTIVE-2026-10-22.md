# Owner directive: creation suite, character select and customization (2026-10-22)

**Binding for every agent and lane.** These are the owner's own messages from 2026-10-22, recorded by the
Claude session (branch claude/amazing-keller-p8644u). Long pasted passages are kept close to verbatim.

## In the owner's words (summary quotes)
- "we still wanted to have the Tekken 8 layout and be built from all the files of like WWE No Mercy, WWE WrestleMania 19, Def Jam, Tekken 5, Tekken 6, and Tekken Tag Tournament 2 and some WWE 2K files. But we have to build it in the layout and set up of Tekken 8."
- "you'll have to tell the agents to work with my game roster and canon and files and not dumb it down or water it down to just what Tekken has, but we're just building on top of what Tekken 8 has in all these areas. We just putting my game Western Heart and my game stuff on top of this."
- "instead of Mixamo soldier it should be like different variations of the Def Jam creation templates, Tekken customization and creation templates, WWE game file templates for character creation and customization, like their default and template models that they build on, and then the option to actually use pieces and parts from the characters that are in game or to edit them"
- "I want to be able to see everything that I'm working on while I'm in portrait mode too" (landscape is an option). "All the little menus and sub options need to be in tabs and only open when you tap them." "Nothing I'm tapping is even appearing or changing anything on screen": every pick must visibly change the model.
- Tripo-first law, restated for Doc Frank: "all the Tripo 3D models should be at the forefront for the characters". Source-game (Tekken, Bosconovitch, etc.) attires and reskins go to the back of the ladder.

## Hard architectural mandate (from the owner's pasted directive)
Tekken 8 is **only** the visual presentation layer and spatial layout template:
- the docking drawer (~25%) and the 3D viewport (~75%);
- the 3-tier menu flow;
- the orbital touch matrix.

All logic, assets and engine math belong to Western Heart and its canon roster. Never strip out the multi-game legacy pipeline:
- No Mercy bone scaling;
- Def Jam bling and jewelry physics;
- TTT2 decal projection;
- Tekken 6 segmented hair and gear.

Zero regression to default Tekken presets.

> **Engine (owner, 2026-10-22):** "WebGL and Three.js are permanently stripped from the architecture; Western Heart operates exclusively on Godot 4's native mobile rendering pipeline" (Vulkan / GLES3, standalone mobile executable). Also: "Or even whatever's better than that for what we're building here based on research, deep research, even if Godot is the best one but there might be better." The repo's existing Godot 4.3 project is `lab/game` (Lab track, milestones 1–3: T3 importer, MoveTable, playable 1v1 slice with touch) plus `tools/netcode/godot` (rollback netcode). Owner, same day: some details in the pasted specs were AI hallucinations; the direction is the Godot work already under way, "higher and better ... using all of these teardown files". The "36-fighter" grid figure comes from the pasted text; the real roster (game/js/roster-full.js) is used in full.

## Tekken 8 presentation reference (as the owner gave it)

**Editor layout**
- Left column, 25% width: the category list (Head, Upper Body, Lower Body, Shoes, Accessories) over a dark translucent gradient.
- 3D viewport, 75% width: the character stands center-right in a static neutral idle. No looping combat stance.
- Footer, bottom 10%: a persistent button legend.

**Submenu flow**
- Picking a category replaces the list with a 3-column item grid in the same 25% footprint.
- The color button opens a floating palette next to the grid: recent colors, presets, and HSV/RGB sliders.
- Equipping an accessory opens Scale / Rotation / Translation (X/Y/Z) sliders that place it on a bone.
- Up to two accessories anywhere on the body.
- Unequipping everything leaves a clean baseline (plain tee, jeans, sneakers), not underwear.
- Shoes are their own slot.

**Touch (the owner's unified touch-first spec)**
- Landscape: viewport 65–70% of the width. Category rail on the left (~15%), plus a slide-out context selector (~20%).
- Every slot shows `< Name >` tap-to-cycle (MDickie style). Tapping the name opens a 3-column grid.
- A quick color pill on each item opens a non-blocking HSV wheel.

**Camera gestures**
- 1-finger drag: orbit (pitch clamped −30° to +60°).
- Pinch: zoom.
- 2-finger vertical drag: pan.
- Double-tap a body region: focus on it.
- Accessory gizmo drag: Move / Rotate / Scale.

**Bottom HUD:** Undo, Redo, Pose/Taunt, Save, Exit, plus an Action Preview that scrubs poses and tests moves on a dummy.

**Portrait (owner requirement):** the viewport stays fully visible. The same rail and selector dock below or beside it without covering the fighter.

## Western Heart deep systems (owner directive)
- **Base morphology and chimeras:**
  - Skeletal morph sliders: No Mercy proportions on the native rigs.
  - Head chimeras and masks: Pantera's head, wolf and dog variants, masks.
- **Layered attire, 4 tiers (Tekken 6 fragmented schema):**
  - Base underlayer.
  - Core garment.
  - Outer layer.
  - Limb modifiers.
  - Z-index auto-culling of hidden polygons.
  - Tekken 6 modular hair: base, bangs, sides/crown, ponytails/extensions.
- **Street bling and weapons:**
  - Def Jam physics sockets: chains, medallions, rings, belts.
  - Weapons flagged Cosmetic or Usable Command Move.
- **Decals, logos and inks:**
  - TTT2-style decal projector.
  - Western Heart iconography library (turf logos, tags, tribal, Ed Hardy-style), not generic shapes.
  - Material sliders: roughness, metallic, normal depth, skin alpha.
  - Layer stack ordering (WWE 2K).
- **Photo booth on save:**
  - Pose from Western Heart's real combat keyframes and win poses.
  - Camera framing.
  - Thumbnail per save slot.
- **Serialization:** JSON with equipped mesh IDs, material overrides, decal UV transforms and accessory socket offsets.

## Character select (Tekken 8 shell, Western Heart content)
- **Roster grid:** bottom center, the full Western Heart roster.
- **3D models:**
  - Hovering streams the fighter's real Western Heart model.
  - P1 big on the left, P2 on the right, idle animation.
- **Stat blocks** flush to the far left (P1) and far right (P2), with Western Heart canon stats: True Name, Home Turf, Weight Class, Archetype, Move Archetype.
- **Lock-in:** an animation and voice line.
- **Custom slot toggle:** a pop-up cycles default outfits and saved custom slots before lock-in.

## Customization routing (Tekken 8 shell)
Main Menu → Customization (Character Customization / Avatar / Player) → Character chooser → Slot submenu → Editor.
- **Character chooser:** the same roster grid on a neutral studio background.
- **Slot submenu:**
  - Defaults are the fighter's canon attires, uneditable, with a "Use as Base" button.
  - Slot 01 is the canon 1P attire and Slot 02 the canon 2P attire, following the Tripo-first ladder.
  - Custom slots 03–10.
- **Editor:** the docking drawer and viewport described above.
- **Photo booth on save.**

## Sources the content must come from (never invented)
- Teardown data in the repo: Tekken 5/6/TTT2/7, WWE No Mercy, WrestleMania XIX, WWE 2K, Def Jam, DOA and Urban Reign, with their decoded catalogs.
- The owner's Tripo models.
- Western Heart canon: CANON.md and game/ui-wh/roster_canon.json.

Missing data is named as a gap. It is never faked.
