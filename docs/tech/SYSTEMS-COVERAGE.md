# SYSTEMS-COVERAGE — every pulled system, wired or not (2026-10-23)

Law: [docs/rules/COMPLETE-WIRING-LAW.md](../rules/COMPLETE-WIRING-LAW.md). Source of truth: `tools/coverage/systems-coverage.json` (edit the JSON, then this table). CI `coverage-guard` fails if a row is removed or its status goes down. Companion: `docs/tech/WIRING-MAP.md` (PR #953).

**Totals: 68 rows — wired 11, partial 22, not-wired 35.**

Status: **wired** = data loaded, used in gameplay, tested, visible proof. **partial** = some of those missing or still in an open PR. **not-wired** = pulled but not in the game. Lane `UNCLAIMED` = claim it on #866 before starting.

| id | Source | System | Status | Code | Test | Lane |
|---|---|---|---|---|---|---|
| `t7-movesets` | Tekken 7 | Movesets / frame data (mothead active windows) | wired | `game/js/movesets.js` | `test/combat-contact.test.mjs` | combat (#951/#952) |
| `t7-command-input` | Tekken 7 | Command interpreter: inputs follow each move list, strings, combos | partial | `game/js/input.js` | `test/input-determinism.test.mjs` | combat (#951/#952) |
| `t7-hit-contact` | Tekken 7 | Hitboxes / contact / hit levels | partial | `game/js/combat-core.js` | `test/combat-contact.test.mjs` | combat (#951) |
| `t7-hit-reactions` | Tekken 7 | Hit reactions (stagger, launch, crumple, wall/floor) | partial | `game/js/combat-core.js` | `test/combat-contact.test.mjs` | combat (#951) |
| `t7-throws` | Tekken 7 | Throws / grabs connect + throw breaks | partial | `game/js/combat-core.js` | `test/combat-contact.test.mjs` | combat (#951) |
| `t7-select` | Tekken 7 | Select screen layout + 3D hero render | partial | `game/js/select-t7-layout.js` | `test/portraits.test.mjs` | select (#947 follow-ups) |
| `t7-menus` | Tekken 7 | Main menu / mode select / options layout | wired | `game/js/menu-t7-layout.js` | `test/e2e` | menus (#932/#943) |
| `t7-ui-private` | Tekken 7 | UI textures/fonts from private pack | wired | `game/js/t7-ui-private.js` | `test/e2e` | menus |
| `t7-customization` | Tekken 7 | Customization item tables -> attire/parts | wired | `game/js/customization-consumer.js` | `test/material-resolve.test.mjs` | creation suite |
| `t7-stages` | Tekken 7 | Stages (meshes via __WH_PRIVATE_ASSETS) | wired | `game/js/stages.js` | `test/e2e` | stages |
| `t7-anims` | Tekken 7 | Animation bank + show/move gate | wired | `game/js/anim-gate.js` | `test/anim-gate.test.mjs` | anims |
| `t7-rigs` | Tekken 7 | Rigs / skin weights for re-rigged fighters | partial | `game/js/assets.js` | `test/no-wrong-body.test.mjs` | re-rig (#954) |
| `t8-framedata` | Tekken 8 | T8 frame-data diffs for movesets | partial | `game/js/movesets.js` | `test/combat-contact.test.mjs` | moveset batches (#915-#945) |
| `t8-models` | Tekken 8 | T8 models (xiaoyu-t8 etc.) as attires | partial | `game/js/attires.js` | `test/no-wrong-body.test.mjs` | select / attire ladder |
| `t8-heat` | Tekken 8 | Heat system (URGE gauge, HEAT button) | wired | `game/js/combat-core.js` | `test/combat-contact.test.mjs` | combat |
| `ttt2-models` | TTT2 | TTT2 models/anims fallback bank | wired | `game/js/assets.js` | `test/no-wrong-body.test.mjs` | models |
| `ttt2-tag` | TTT2 | Tag / tag-assist / tag-throw mechanics | not-wired | — | — | UNCLAIMED |
| `ttt2-ghost-ai` | TTT2 | Ghost AI behaviour | partial | `game/js/ghost-ai.js` | — | UNCLAIMED |
| `t6-customization` | Tekken 6 | T6 customization catalog | partial | `game/js/customization-consumer.js` | `test/material-resolve.test.mjs` | creation suite (gap-closure W7) |
| `t6-bound` | Tekken 6 | Bound / scenario-campaign data | not-wired | — | — | UNCLAIMED |
| `t5-customization` | Tekken 5 | T5 customization catalog | partial | `game/js/customization-consumer.js` | `test/material-resolve.test.mjs` | creation suite (gap-closure W7) |
| `t5-devil-within` | Tekken 5 | Devil Within beat-em-up mode data | not-wired | — | — | UNCLAIMED |
| `t3-framedata` | Tekken 3 | Frame data (logged last resort, no models) | wired | `game/js/fighter.js` | `test/combat-contact.test.mjs` | combat |
| `fp-cpu` | Fire Pro | CPU personality (AIParam/AIPriorityAct) | partial | `game/js/ai/cpu-personality.js` | `test/wiring.test.mjs` | wiring (#953) |
| `fp-sim` | Fire Pro | Watch / Simulate mode | partial | `game/js/sim-match.js` | `test/wiring.test.mjs` | wiring (#953) |
| `fp-moveforge` | Fire Pro | Move Forge (edit/craft data) | not-wired | — | — | Muse (#879) |
| `yk-spirit` | Yakuza Kiwami | 魂 ACTION (Spirit Actions, context finishers) | partial | `game/js/spirit-actions.js` | `test/wiring.test.mjs` | wiring (#953) |
| `yk-motion` | Yakuza Kiwami | Show/cutscene clip bank (gated from movesets) | not-wired | — | — | Track 7 (#936) |
| `yk-story` | Yakuza Kiwami | Scenario / battle tables -> story brawler | not-wired | — | — | Muse (#883) |
| `2k19-parts` | WWE 2K19 | CAW parts + DDS textures -> creation suite | partial | `game/js/creation-parts-private.js` | `test/wiring.test.mjs` | wiring (#953) |
| `2k19-motion` | WWE 2K19 | Motion decode | not-wired | — | — | UNCLAIMED (decode blocked) |
| `gb-grab` | Gang Beasts | Grip / Hold + ragdoll release | partial | `game/js/grab-hold.js` | `test/wiring.test.mjs` | wiring (#953) + chrono (#955) |
| `gb-assets` | Gang Beasts | AssetRipper export | not-wired | — | — | UNCLAIMED (export pending) |
| `we-world` | Wrestling Empire | World / career / progress sim | not-wired | — | — | Muse (#884) |
| `we-editor` | Wrestling Empire | Character editor fields | not-wired | — | — | Muse (#884) |
| `soul-systems` | Owner design | KESSHOU / 九魂解放 / 霊放 / 試練の封 + per-fighter variants | partial | `game/js/soul-systems.js` | `test/soul-systems.test.mjs` | wiring (#953) |
| `nm-arenas` | WWF No Mercy | 17 arena assemblies | wired | `game/js/stages.js` | `test/e2e` | stages |
| `nm-parts` | WWF No Mercy | Parts catalog | wired | `game/js/customization-consumer.js` | `test/material-resolve.test.mjs` | creation suite |
| `nm-moves` | WWF No Mercy | Wrestling move bank | partial | `game/js/moveset-library.js` | — | UNCLAIMED |
| `wmxix-moves` | WWE WrestleMania XIX | Move bank + arenas | partial | `game/js/moveset-library.js` | — | UNCLAIMED |
| `defjam` | Def Jam | Parts catalog | partial | `game/js/customization-consumer.js` | — | UNCLAIMED |
| `doa-stagebreaks` | Dead or Alive 4 | Knock-through / danger zones | partial | `game/js/stagebreaks.js` | — | stages |
| `vf5-moves` | Virtua Fighter 5 | Move bank | partial | `game/js/moveset-library.js` | — | UNCLAIMED (bank pending) |
| `sc-models` | Soulcalibur | Models / motion-db / weapon tracks | not-wired | — | — | UNCLAIMED |
| `sfex-models` | Street Fighter EX | glb models + anims (phases 1-4) | not-wired | — | — | UNCLAIMED |
| `yyh` | Yu Yu Hakusho Dark Tournament | Models + decoded clips | not-wired | — | — | UNCLAIMED |
| `urban-reign` | Urban Reign | Multi-opponent brawl data | not-wired | — | — | UNCLAIMED |
| `nioh` | Nioh 1/2 | Character depth | not-wired | — | — | BLOCKED (disk) |

## Bannon (add-on layer — owner 2026-10-23)

Read-only audit of `mhvnsnt/Bannon` for Western Heart (no work on Bannon itself; no Brutal Fist/AshLane work). Rule: the real game system (Tekken first, then other pulled games / solid open-source) is the **base**; Bannon features **layer on top** as add-ons where they add something. Port clean into `game/js/`, credit `mhvnsnt/Bannon` + source path in the PR and here.

| id | Combo (base + Bannon add-on) | Base row | Bannon source | Status | Lane |
|---|---|---|---|---|---|
| `bannon-live-deform` | OWNER PICK #1 — Live deformation / muscle bulge on top of Tekken T7 rigs | `T7 rigs (t7-rigs)` | mhvnsnt/Bannon: godmode/src/engine/BiomechanicalPhysics.ts, native/include/bannon_rig.h | not-wired | UNCLAIMED |
| `bannon-active-ragdoll` | Active ragdoll balance touches on top of Gang Beasts grip/hold + Tekken hit reactions | `gb-grab, t7-hit-reactions` | mhvnsnt/Bannon: server/modes/activeRagdollSystem.ts, native/include/bannon_ragdoll.h | not-wired | UNCLAIMED |
| `bannon-grapple` | Grapple chains/leverage on top of Tekken throws + Gang Beasts hold | `t7-throws, gb-grab` | mhvnsnt/Bannon: server/modes/grappleSystem.ts, native/include/bannon_grapple.h | not-wired | UNCLAIMED |
| `bannon-strike` | Strike impulse / impact physics on top of Tekken hitboxes | `t7-hit-contact` | mhvnsnt/Bannon: native/include/bannon_strike.h, server/hitboxLogic.ts | not-wired | UNCLAIMED |
| `bannon-hit-clips` | 973 hit-reaction clip variants (DELAYED/HARD/KNEELING/MIRROR/SITOUT/SLOW/SNAP) layered on Tekken reactions | `t7-hit-reactions` | mhvnsnt/Bannon: assets/moves/clips/ | not-wired | UNCLAIMED |
| `bannon-weapon` | Weapon physics on top of Soulcalibur weapon tracks | `sc-models` | mhvnsnt/Bannon: native/include/bannon_weapon.h, app/src/main/cpp/engine/WeaponPhysics.cpp | not-wired | UNCLAIMED |
| `bannon-ik` | CCD IK foot/hand planting on top of Tekken anims | `t7-anims` | mhvnsnt/Bannon: assets/vendor/CCDIKSolver.js (three.js, MIT) | not-wired | UNCLAIMED |
| `bannon-caw-rig` | CAW auto-rigging pipeline on top of 2K19 creation parts | `2k19-parts` | mhvnsnt/Bannon: server/caw/RiggingPipeline.js, bannon_blender_rig.py | not-wired | UNCLAIMED |
| `bannon-combat-ai` | Combat AI touches on top of Fire Pro CPU personality | `fp-cpu` | mhvnsnt/Bannon: CombatAI.ts, godmode/src/physics/CombatEngine.ts | not-wired | UNCLAIMED |
| `bannon-ladder` | Ladder/spatial TLC physics on top of No Mercy/WMXIX arenas | `nm-arenas` | mhvnsnt/Bannon: app/src/main/cpp/rulesets/TLC_LadderSpatialPhysics.cpp | not-wired | UNCLAIMED |
| `bannon-combat-harness` | Playwright combat test harness on top of game-checks | `t7-hit-contact` | mhvnsnt/Bannon: godmode/src/lib/PlaywrightCombatHarness.ts | not-wired | UNCLAIMED |
| `bannon-pose-editor` | OWNER PICK #2 — Pose editor (poseStudio / studioApplyClipPose, studioBoneSnap): set idle/fight/select pose per fighter (worked for King); saved pose -> fighter pose slot; unique-pose rule; Buffalo Bill pose locked | `t7-select, t7-anims` | mhvnsnt/Bannon: drive-archive/google-ai-studio/BANNON_v78 (1)_1DMFEmj3.html; unreal/.../BannonPoseAuthorityComponent.cpp; tools/taunts/pose_orient.py | not-wired | UNCLAIMED |
| `bannon-creation-tools` | OWNER PICK #3 — Sculpt/shape/part editing (studioMorphSnap, BannonMorphPreviewer, PolymorphicRig) | `2k19-parts, t7-customization` | mhvnsnt/Bannon: drive-archive/google-ai-studio/BANNON_v78 (1)_1DMFEmj3.html; unreal/.../BannonMorphPreviewer.cpp; src/utils/PolymorphicRig.ts; src/modules/editor.js | not-wired | UNCLAIMED |
| `bannon-studio` | BANNON STUDIO — tabs Anim, Build, Clips, Presets, Scan, Memory, Chat (clip/move editing, presets, model scan) | `t7-customization, t7-anims` | mhvnsnt/Bannon: drive-archive/google-ai-studio/BANNON_v78 (1)_1DMFEmj3.html (openStudio/renderStudio/studioTabs) | not-wired | UNCLAIMED |
| `bannon-mocap-studio` | MOCAP STUDIO — capture/apply motion to fighter | `t7-anims` | mhvnsnt/Bannon: drive-archive/google-ai-studio/BANNON_v78 (1)_1DMFEmj3.html | not-wired | UNCLAIMED |
| `bannon-move-forge` | FORGE / MOVE FORGE / MOVE CREATOR — build custom moves | `fp-moveforge, t7-movesets` | mhvnsnt/Bannon: drive-archive/google-ai-studio/BANNON_v78 (1)_1DMFEmj3.html; src/engine/MoveCreatorCorePhysics.cpp | not-wired | UNCLAIMED |
| `bannon-strike-lab` | STRIKE LAB — tune strike impact/frames | `t7-hit-contact` | mhvnsnt/Bannon: drive-archive/google-ai-studio/BANNON_v78 (1)_1DMFEmj3.html | not-wired | UNCLAIMED |
| `bannon-dive-lab` | DIVE LAB — aerial/dive move tuning | `nm-moves` | mhvnsnt/Bannon: drive-archive/google-ai-studio/BANNON_v78 (1)_1DMFEmj3.html | not-wired | UNCLAIMED |
| `bannon-creation-suite` | CreationSuite page: Body Templates & Morphing, Head & Face, Face Details, Hair, Makeup & Facepaint, Masks, Clothing (Upper/Lower/Head/Foot), Accessories, Menu Screen Posing, Moveset, Entrance (Pyro & Effects, Lighting, Motion & Path), Fighting Style & AI DNA (Aggression/Defense/Patience/Risk/Range/Grapple/Showmanship), Injuries & Damage Persistence, Arena (Ring & Mat, Ropes & Apron, Barricades, Ringside) | `2k19-parts, t7-customization, fp-cpu` | mhvnsnt/Bannon: src/pages/CreationSuite.tsx; src/components/CreationShell.tsx; CharacterForge.ts | not-wired | UNCLAIMED |
| `bannon-forge-studio` | godmode ForgeStudio (artifact builder) + GameStudio ('ProWrestle AI Agent Studio': physics/graphics/rig compiler) — dev tools, mine for ideas only | `—` | mhvnsnt/Bannon: godmode/src/components/ForgeStudio.tsx, GameStudio.tsx (MlabStudio.tsx is a music studio, not WH) | not-wired | UNCLAIMED |

**UX rule for Bannon ports (owner):** Bannon's tools felt too technical. Port the capability, present it like the real games' menus (T7 customization, WWE 2K19 CAW, Fire Pro edit): category tabs, sliders, presets, turntable preview, phone touch (390x844 + 844x390), undo, save slots.

Note: no studio literally named "Model Studio" was found in Bannon's code; the model/build editing lives in BANNON STUDIO's Build/Scan tabs and the CreationSuite page.
