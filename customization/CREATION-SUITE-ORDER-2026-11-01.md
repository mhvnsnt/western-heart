# Creation suite — owner order and build plan (2026-11-01)

**Status:** in progress. Phase 5 (POSE & PICTURE) LANDED 2026-11-01: the suite's POSE tab plays the fighter's own bank clips (retargeted by the game's own pipeline) and TAKE PICTURE saves the posed preview to the on-device portrait store the select screen reads. Every agent working on
the creation suite reads this first. Names law applies to everything a player sees: no Tekken / WWE / teardown
character names in the UI (the source games are named only in docs about pulling their data).

## The order (verbatim, 2026-11-01)

> okay now those second ones save those as the new default ones and then in the character creation editor like the
> character customization get all of the Tekken Creation suite hooked up and all of the WWE stuff that you came from
> the most recent WWE game you either have in my steam or in my tear down files get that plus the tech and stuff
> wired up so we can one create a brand new fighter just like you can in WWE with with templates and all the body and
> face morphing and everything and two so you can edit the existing fighters and save like a tires and new versions
> and stuff and that it's a friendly user interface real clean and made from the menu code in those games in the UI
> and layout code in the hood code in those games and not handled b******* cuz we wanted to look good and
> professional easy for the user to use like all the windows and sub windows and I'm sub menus and menus in it and we
> want to be able to add or pose them and be able just like you can do in WWE 2K and then taking be able to post them
> and take a new picture for the character select screen you see so it all ties in together and then you can fully
> flush that out so I can customize and make new fighters and customize the and edit the existing fighters and save a
> tires and edit current and tires in such and such and so forth and that'll help me turn people like Jenkins or
> people yeah like you know like it'll let me turn people like gin kazama into demonio or it'll let me turn people
> like heyhachi into Diablo, etc, u see what I'm sayin. Log that down into the repo and so everyone I'm in the repo
> working on it nose and the handoff documents make sure everything is landing and keep working on all of that

> And make sure in the Creation suite when you're creating a fighter that it's not mixable soldier as the default
> template make sure it's like a WWE style default template with all their options and we Google G&M and mfpb or MF
> body replacer or whatever those things are like all of those things we have a bunch of stuff in the repo bunch of
> tools audit and wire up everything where it needs to go 100% to where it actually works so nothing's empty stubs

> And make sure you're getting all of this pushed in staged into the deployable build as you get it done

## What it means (acceptance)

1. **Select-screen cards:** the re-captured cards of fixed models are the defaults (`game/assets/portraits/<id>.png`);
   draft 1 stays archived in `game/assets/portraits/draft1/`. Every later re-capture keeps the previous card as the
   next draft.
2. **Create a brand-new fighter like WWE 2K:** CREATE starts at a TEMPLATE SELECT of WWE-style base bodies
   (Heavyweight / Cruiserweight / Women's divisions), never the stock "Soldier" model. Then real **body morphing**
   (height, weight, muscle, shoulders, chest, waist, arms, legs, ...) and **face morphing** (jaw, cheeks, brow, nose,
   eyes, mouth, chin, ears, ...) live on the 3D fighter, skin, hair, facial hair, attire layers, colors / materials,
   profile, moveset.
3. **Edit existing fighters:** pick any roster fighter, edit an attire, **save it as a new attire / version** (or over
   the current one); the game's select screen and fights use the saved attire. This is how a placeholder base model is
   turned into the WH fighter it stands in for (the owner's examples: the Jin-based body into Demonio, the
   Heihachi-based body into Diablo).
4. **Pose + new select-screen picture:** a pose mode (stance / pose library, camera framing) and a TAKE PICTURE button
   that becomes that fighter's (or attire's) select-screen card. Everything ties together: suite -> save -> select
   screen -> fight.
5. **Professional UI:** menus, sub-menus, windows and sub-windows modeled on the source games' menu / layout / HUD
   structure (WWE 2K CAW editor flow, Tekken 7 customization layout), clean on a phone in portrait and landscape,
   no overlapping text, no developer notes on screen.
6. **No empty stubs:** every creation tool in the repo is audited and either wired so it actually works or listed as
   blocked with the reason (see the tool audit below).
7. **Lands live:** each finished piece merges and deploys to the live build as it lands.

## Where things are (facts checked 2026-11-01)

| Piece | Where | State |
|---|---|---|
| Suite the game menu opens (CREATE) | `customization/creation-suite-ui/` (`index.html`, `js/suite.js`, `js/viewer3d.js`, `js/menu-data.js`) | live; NEW FIGHTER defaulted to the stock Soldier model in T-pose; top bar overlaps on a phone; body-type buttons carried real wrestler / Tekken names |
| Older prototype with the WWE template flow | `customization/create-fighter/` (`js/creation-flow.js` TEMPLATE SELECT, TOOLS tab job specs) | not linked from the game menu |
| WWE-style base bodies | `customization/templates/body-templates.json` + `meshes/*.glb` (9 templates: 3 Heavyweight, 3 Cruiserweight, 3 Women's; MB-Lab bake, 71-joint MB-Lab skeleton) | exist; **no morph targets** (shape keys applied at bake), so body / face sliders cannot be real blend shapes yet |
| Morph catalogs, DNA sliders, face morphs, layering, slot map, T7 layout / material, WWE 2K22 move slots | `packages/creation-suite/src/` (`morphs.js`, `dna.js`, `facemorphs.js`, `layering.js`, `slotmap.js`, `t7layout.js`, `t7material.js`, `wwe2k22-caw-slots.js`, `rigpose.js`, `rigswap.js`, `secondary.js`) | partly wired into the suite (sliders drive bone proportions + morph proxies) |
| Parts | `customization/creation-suite-ui/data/parts-catalog.json` (4,523), `customization/create-fighter/data/PARTS-INDEX.json` (7,920) | real meshes for No Mercy (303) + DOA4 (272) + hair; most WMXIX / Def Jam parts still GEOMETRY PENDING |
| WWE CAW structure | `customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md`, `CAW-STRUCTURE-2026-10-19.md`, `COMBINED-CREATION-SUITE.md` | documented (WWE 2K19 / 2K22 menus, layers, sliders) |
| WWE 2K raw files | `teardown/wwe2k19`, `wwe2k20`, `wwe2k22` | **not pulled**: those releases are delisted and the pull needs the owner's Steam login (agents never log into Steam); work from the documented structure |
| Tekken customization structure | `teardown/tekken7-steam-ui/T7-UI-LAYOUT.md`, `teardown/ttt2-customization-research.md`, `teardown/tekken6-customization-research.md`, `packages/creation-suite/src/t7layout.js` | documented + partly in code |
| Body tools | `tools/mb-lab` (MB-Lab headless bake), `tools/mpfb2` (MPFB2 / MakeHuman, CC0), `customization/body-morphs/apply_mpfb_morphs.py`, `game/js/creation-tool-map.js` | need Blender (not on the cloud VM by default) |
| Select-screen portraits | `tools/portraits/capture.mjs` + `game/portrait-capture.html`; suite POSE tab TAKE PICTURE → `game/js/user-portraits.js` | works for repo fighters; in-suite TAKE PICTURE landed 2026-11-01 (phase 5) — a suite picture becomes the fighter's select-screen card on that device, repo card stays the fallback |

## Build plan (each phase merges + deploys when it lands)

1. **Template-first CREATE** in `creation-suite-ui`: TEMPLATE SELECT of the 9 WWE-style bodies replaces the Soldier
   default; template names and body types are generic (no real-person / Tekken names); the phone top bar stops
   overlapping.
2. **Tool audit** (`customization/CREATION-TOOLS-AUDIT-2026-11-01.md`): every creation tool / module in the repo, what
   it does, where it is wired, what is a stub, what it needs; then wire them one by one.
3. **Real body + face morph targets**: re-bake the template bodies with shape keys kept (MPFB2 / MakeHuman targets are
   CC0; MB-Lab's are AGPL) and export them as glTF morph targets, so every slider is a real blend shape on the live
   fighter (the WWE 2K / industry approach), with bone proportions for height / limb length.
4. **Edit existing fighters -> save attire / version**: roster mode saves a named attire (or a new version of one);
   the game's attire picker lists saved attires and fights load them (`game/js/customization-consumer.js`).
5. **Pose + TAKE PICTURE**: pose library (the fighter's own stance + idle / victory clips) and camera framing; the
   picture becomes the select-screen card (user cards override the repo card on that device; repo cards are re-captured
   with `tools/portraits/capture.mjs`).
6. **WWE / Tekken-style menus**: CAW-editor menu tree (Create / Edit / Template / Body / Face / Hair / Attire layers /
   Paint / Moveset / Profile / Pose & Picture) with sub-windows, laid out from the T7 layout rules and the WWE CAW
   flow; phone portrait + landscape proof shots for every screen.

## Phase status

| Phase | State | Where |
|---|---|---|
| 1. Template-first CREATE | **done**. TEMPLATE SELECT of the 9 base bodies replaced the Soldier default on main (#1475). The remainder of Claude's draft PR #1486 (generic template names/body types in `customization/templates/body-templates.json`, the left sliding panel per `customization/UNIFIED-UI-SPEC.md` §1 in `css/suite-t7.css` + `js/suite.js`, the landscape-phone top bar fix, and the select-screen attire-cycling fix) was salvaged onto current main by the Claude-WIP completion lane (2026-11-02) after a hunk-by-hunk supersession audit — see `docs/handoffs/CLAUDE-WIP-COMPLETION-2026-11-02.md`. | main (#1475 + salvage PR) |
| 2. Tool audit | not started | `customization/CREATION-TOOLS-AUDIT-2026-11-01.md` (to write) |
| 3. Real body + face morph targets | **done — LANDED via the Claude-WIP completion lane (2026-11-02, successor PR to draft #1489)**. The 9 template GLBs are re-baked with Blender 4.3.2 + MB-Lab (`tools/mb-lab/bake_all_templates.sh`): each template's real body settings applied (the old bakes were six identical male and three identical female meshes), 84 sliders exported as 168 glTF morph targets (`customization/templates/morph-sliders.json`: Body Morphing 32 sliders in 10 regions, Face Deformation 52 sliders in 12 parts), same 71-joint MB-Lab skeleton, gltfpack 2.03-2.10 MB each. Suite BODY tab on a template body follows the WWE 2K22 Appearance window structure as a T7 category list; values save to `body.morph_targets` (+ `frame`, `template`, `height`) and the suite preview applies them live (`js/morph-targets.js`). Proof: `customization/creation-suite-ui/proof-pass/phase3-morphs/`. | main |
| 4b. Created fighters in the game (template body + morphs on select screen and in fights) | **LANDED 2026-11-02 (Phase 4b PR)**: the in-fight/select model now resolves to the fighter's chosen template GLB (`custom-template-<id>` in `game/js/assets.js` MODEL_URLS), the MB-Lab bones are renamed to T3 names on load (`remapMblabBones`, same contract as the Vega/Slice remaps), morphs bake once at build (never per-frame), and a created fighter with no custom moveset falls back explicitly to the jin bank (logged once in `bankIdFor`) with generic frame data — custom moveset slots still TODO. Fight-animation proof on the MB-Lab rig: `test/custom-template-fight.test.mjs` 5/5 — jin stance holds (head above hips, feet on floor), attack row:32 moves a limb 0.959 m from rest. Still owed: roster-mode edits still fight on the legacy Soldier slot (their attire GLB has no MODEL_URLS key; ORDER Phase 4), and the material gate for template bodies is not proven by the Node test (Node cannot decode the embedded PNG textures) — see `docs/handoffs/PHASE-4B-CREATED-FIGHTERS-IN-FIGHTS-2026-11-02.md`. No deploy: rides the held republish. | main |
| 4. Edit existing fighters -> save attire / version | not started | |
| 5. Pose + TAKE PICTURE | **LANDED** (#1490, 2026-11-01) — see Status line above | main |
| 6. WWE / Tekken-style menus | not started | |

## Owner direction for the parts / clothing phases (2026-11-01)

The owner's direction for everything after body + face (parts, hair, clothing, accessories, tattoos, scars, eyes):
the menus, windows, options and the part / clothing structure follow **WWE 2K Create-A-Superstar and Tekken
customization, built from their game code and the repo's teardowns** (not hand-invented). Verbatim:

> pretty much everything that WWE has and everything that Tekken has, use their game code to build it and fir how it
> looks UI and hud and menu and window and option wise and for parts and clothing etc

Structure sources to start from: `customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md`, `CAW-STRUCTURE-2026-10-19.md`,
`COMBINED-CREATION-SUITE.md`, `customization/PARTS-CLOTHING-SYSTEM-SPEC.md`, `teardown/tekken7-steam-ui/T7-UI-LAYOUT.md`,
`teardown/ttt2-customization-research.md`, `teardown/tekken6-customization-research.md`.
