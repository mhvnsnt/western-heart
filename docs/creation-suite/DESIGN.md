# Shared Creation Suite: design (v0)

One character creation suite for all of the owner's games, deeper than the WWE 2K
Creation Suite and Tekken Customization. Western-heart ships it first, then Bannon,
AshLanev2 and brutalfistgrokversionten. Every game keeps its default roster; the suite
reshapes and dresses them and makes new ones. Most models come from **Tripo 3D**, so
nothing assumes authored blend shapes or extra bones.

## 1. Chosen base (survey, 2026-10-14)
Searched every mhvnsnt repo (`gh search code --owner mhvnsnt` for "creation suite",
"moveset editor", "create a wrestler", "customizer", "morphTargetInfluences").

| Source | What it has | Use |
|---|---|---|
| **mhvnsnt/Bannon** `docs/DNA_SCHEMA.md`, `bannon_customizer.js` (84 KB), `docs/CREATION_SUITE.md`, `docs/CUSTOMIZER.md` | DNA recipe v1 (morphs + boneScale + spec), live CAW hub, drop-in GLB → UniRig → skinqa gate | **BASE.** DNA v2 here is a strict superset; `migrate()` reads v1 saves. |
| Bannon `assets/moves/moveset_schema.json` + `tools/moves/build_moveset_schema.cjs` | WWE-2K Create-a-Moveset as data, uncapped: 25 categories, 439 slots, AI priority/repetition/timing, styles | **BASE for the moveset editor.** Pulled into the shared package next PR, not rebuilt. |
| Bannon `assets/customizer/{masks,hair,hoods,gloves,footwear,chains,wristbands}/manifest.json` | attire catalogue with attachBone/offset/scale | Feeds the attire slots (same keys). |
| Bannon `docs/2K26_caw_moveset_gaps.md` | 2K26 CAW feature list | Checklist for depth. |
| Bannon `tools/character-customizer`, `tools/texture-customizer` | paint/texture tools | Paint & Tattoos tab. |
| western-heart Lab (PR #112/#113, open #116 `grok/lab-playable-slice`) | canonical skeleton, T3 importer, move-table interpreter, `attire.gd` + Bannon mask manifest | Canonical bone names + mask manifest are reused as-is. Not modified by this PR. |
| TRIPPEDD-Production-studios `tools/pocket-studio-v2/tools-data/game-assets.json` | asset index | Library source. |

Teardown inputs (see `docs/western-heart/INVENTORY.md`): AshLane's Urban Reign teardown
(fighters, attire meshes; bone translations still open, PR #105), Def Jam and WWE files
(attire/hair/accessory meshes, CAW part lists), Tekken 3 (36 fighters, real frame data,
#103), Tekken 6 / TTT2 (cipher work in progress, #102/#104). These become **library
entries** (hair, accessories, attire parts, moves), each tagged with its source game.
License-clean add-ons: VRM spring-bone model (pixiv/three-vrm, MIT) for the spring
math; glTF morph targets / blend shapes (Khronos spec) for authored sliders.

## 2. Menu flow (owner spec)
Main menu → **per-game suite name** (`Create a Fighter` western-heart/brutalfist,
`Create a Wrestler` Bannon, `Create a Brawler` AshLane) → **Character Creation/Edit** or
**Moveset** → character list → pick a character → that character's sub-menu.
Data lives in `packages/creation-suite/src/menu.js` (`suiteMenu(game)`).

50/50 blend:
- From **WWE 2K**: deep part slots, layered attire, paint/tattoo layers, Create-a-Moveset
  categories and slots with AI priority/repetition/timing, profile/style, entrances.
- From **Tekken**: fast per-character list, preset/saved-look slots, item category tabs,
  always-on live preview, command list with frame data.

Character sub-menu: Presets · Body (Body Type, Frame, Mass, Physics) · Head & Face ·
Attire (layered) · Paint & Tattoos · Alternate Attires · Moveset · Profile & Style · Entrance.
Moveset screens (WWE style): Move Library → Categories → Slot Edit → Command List → Preview.

## 3. Body sliders (`src/body.js`, `src/dna.js`)
- **Frame (bone scale):** height, armLen, legLen, torsoLen, shoulders, headSize.
- **Mass (morph targets):** weight, muscle, belly, chest, glutes, hips, thighs, arms, neck.
- Body-type presets: `default`, `heavy`, `muscular`, `female`, `femaleCurvy`.
- Tripo models have no blend shapes, so at load each body region (`src/regions.js`)
  becomes a **procedural morph target** `cs_<region>`: vertices inside the region's
  ellipse are pushed along their normal with a smooth falloff. Regions are anchored to
  canonical bones and sized in torso units (Hips→Head), so they fit any model scale.
  Front/back regions take the whole surface half (bodies vary a lot in depth).
  The model's facing (+Z or -Z) is detected from the toes.
- If a model *does* ship a morph named like a slider (`belly`, `chest`…), that is used
  instead.

## 4. Size-adaptive secondary physics (`src/secondary.js`)
Per character, after sliders: measure each region's girth → decide whether it gets a
spring bone and how heavy/loose it is (`physicsFor`: mass ∝ (girth/ref)³, stiffness ∝
1/√mass, max offset ∝ √mass). Chest and glute springs also need the slider pushed
(a flat male chest never bounces). Spring bones are **generated** and the region's
vertices are re-skinned onto them (85% × falloff), then a damped spring runs per frame
(VRM-springbone style). Families: belly, chest L/R, glute L/R, thigh L/R; hair and
cloth chains use the same spring with their own base tuning (`PHYSICS_BASE`).
Measured on Pantera Leo-Man: default → 1 spring (belly); heavy → 7; female curvy → 7,
with heavier/looser glutes.

## 5. Attire slots (`src/attire.js`)
Slots: face, head, hair, torso, jacket, arms, hands, waist, legs, feet, accessory.
Sockets resolve through bone aliases (canonical, Mixamo, Bip01, VRM). `attach()` cancels
socket scale, auto-fits to the head size, and `applyEdit()` edits tint, roughness,
metalness, offset, rotation, scale and visibility per character.
**Bannon mask** is `UNIVERSAL_PIECES.bannon_mask` (face slot), using the Lab manifest
`lab/game/attire/bannon_mask/bannon_mask.manifest.json`: it attaches to every
character in every game and is editable.

## 6. Shared package layout
```
packages/creation-suite/
  package.json        @mhvnsnt/creation-suite (ESM, peer three >=0.160)
  src/dna.js          DNA v2 recipe, sliders, body types, v1 migration (no three)
  src/regions.js      body regions + physics tuning (no three; Godot port reads the same table)
  src/body.js         sliders on a SkinnedMesh (procedural morphs + bone scale)
  src/secondary.js    generated spring bones + SpringSystem
  src/attire.js       slots, sockets, attach/edit, universal pieces
  src/menu.js         menu tree + per-game labels
  test/               node --test
  proof/              headless render harness + report
```
Other repos import it with a git dependency (sparse), e.g.
`"@mhvnsnt/creation-suite": "github:mhvnsnt/western-heart#<sha>&path:packages/creation-suite"`
or vendor-copy `src/` under `vendor/creation-suite/` with the commit SHA recorded.
Western-heart's Godot Lab gets a GDScript port of `regions.js` + `secondary.js`
(same data) after Lab #116 lands, so it does not collide with `attire.gd`.

## 7. Next PRs
1. Moveset: pull Bannon `moveset_schema.json` into the package + WWE-style library/editor screens.
2. Teardown library index: hair/accessories/attire parts from UR, Def Jam, WWE, Tekken.
3. Godot port for western-heart Lab; then wire into Bannon, AshLanev2, brutalfist.
4. Hair/cloth chain auto-detection on Tripo meshes; neck region (girth measures 0 on Leo-Man's mane).
