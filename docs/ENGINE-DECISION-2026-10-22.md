# Western Heart: which engine for the native mobile build

Date: 2026-10-22. Built from five research notes in `docs/research/engine-2026-10-22/`. No new web research. One contradiction between notes was settled by reading a file already in the repo (see Corrections).

## The answer

**Stay on Godot.** Upgrade `lab/game` from Godot 4.3 to 4.7.x now. Move to 4.8 when it ships stable. Build a signed APK for sideloading from a Linux CI job. Keep building in the direction you were already going.

You asked whether anything is better. The research found nothing better for this build overall. Unity beats Godot on one thing (ready-made online play tools) and Unreal on another (built-in character-creator tools). Neither advantage is worth the price and a restart from zero.

### The five reasons that decide it

1. **It costs nothing, at any sales level.** Godot uses the MIT license. There are no royalties and no seat fees. The only duty is a credits line ([Godot license](https://godotengine.org/license/); [Godot FAQ](https://docs.godotengine.org/en/stable/about/faq.html)). At $2M in lifetime sales, Unity would cost about $20,790 and Unreal $50,000 (worked out below).
2. **Your game already runs in it.** `lab/game` is a playable Godot 1v1 slice with headless tests and decoded T3 clips inside its GLBs. Three GDScript netcode addons are already vendored next to it ([lab/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/README.md); [tools/netcode/godot/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/netcode/godot/README.md)). Every other engine starts the game code from zero.
3. **It suits AI agents working in a Linux shell.** Scenes are plain text files ([TSCN format](https://docs.godotengine.org/en/stable/engine_details/file_formats/tscn.html)). One headless command builds the APK ([command line](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html)). Unreal stores content in binary files and needs a 20–30 GB Linux install ([SomethingLikeGames](https://www.somethinglikegames.de/en/blog/2026/linux_06_ue/)). Unity's free tier now needs online license activation in CI, using undocumented flags ([game-ci/cli PR #246](https://github.com/game-ci/cli/pull/246)).
4. **The creation-suite building blocks are in stable Godot now.** That covers live retargeting (`RetargetModifier3D`, 4.4), spring-bone jiggle (4.4), a new IK set (4.6), a native touch joystick (4.7), runtime GLB loading and texture painting (`DrawableTexture2D`, 4.7) ([4.4](https://godotengine.org/releases/4.4/); [4.6](https://godotengine.org/releases/4.6/); [4.7](https://godotengine.org/releases/4.7/)). The 4.8 beta fills the last gaps: decals on the low-end renderer, texture streaming and touch fixes ([4.8 beta 1](https://godotengine.org/article/dev-snapshot-godot-4-8-beta-1/)).
5. **The hardest parts are hard in every engine.** On any engine, the fight logic must be your own whole-number ("fixed-point") 60 Hz simulation so every phone computes the same result. Even Unity's best tool, Photon Quantum, is a separate simulation of this kind ([Photon Quantum](https://doc.photonengine.com/quantum/v3/quantum-intro)). Tattoos are safest painted into the skin texture on every engine. That shrinks Unity's and Unreal's head start.

### Where something else is better (honest version)

- **Unity** has the best ready-made online play: Photon Quantum 3 (fixed-point, rollback, used on phones) and UFE 2 Pro ($349, with rollback) ([UFE pricing](https://ufe3d.com/ufe2/pricing.html)). It also has real mobile-fighter history. Tekken Mobile was Unity ([gamebiz.jp CEDEC 2018](https://gamebiz.jp/news/218774)), and Shadow Fight 3/4 likely were (indirect evidence, [Nekki vacancy](https://nekki.com/vacancy/sf3-shablon)). If online play at launch were your top need, Unity would be the closest rival.
- **Unreal** has the strongest built-in creator tools: Mutable, the runtime IK Retargeter and mobile decals in 5.8 ([UE 5.8 release notes](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes?lang=en-US)). But the Unreal mobile fighters (Mortal Kombat Mobile, Injustice 2) came from NetherRealm on UE4 ([Wikipedia](https://en.wikipedia.org/wiki/Mortal_Kombat_Mobile)). And UE6 Early Access is targeted for end-2027, which forces a mid-project migration choice ([Strafe](https://www.strafe.com/news/read/state-of-unreal-2026-all-the-key-takeaways-from-the-epic-keynote/)).
- **Godot's real weakness:** no commercial 3D fighter has shipped on Godot, on any platform. The best-known Godot fighter is the 2D, turn-based *Your Only Move Is HUSTLE* on Godot 3.5 ([itch.io forum](https://itch.io/t/2632153/what-game-engine-you-used)). You would be first, so treat phone performance as unproven until Milestone 1 proves it.

## Side-by-side against this build

Good / OK / Weak is scored against Western Heart's needs, not engine quality in general. Flax and Bevy are the two open-source alternatives the notes support best: Flax has the fullest animation feature set and Bevy the best command-line and rollback story.

| Need | Godot 4.7 → 4.8 | Unity 6.x | Unreal 5.8 | Flax 1.13 | Bevy 0.20 |
|---|---|---|---|---|---|
| Signed sideload APK from Linux CI | **Good.** One headless command; keystore from env vars ([Android export](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html)) | **OK.** GameCI Docker; free-tier activation online-only ([GameCI](https://game.ci/docs/github/builder/)) | **Weak.** Huge install; Android cook on precompiled Linux unverified | **Weak.** Editor "Game Cooker"; Linux-host Android unconfirmed ([Flax Android](https://docs.flaxengine.com/manual/platforms/android.html)) | **Good.** cargo-ndk + Gradle ([Bevy examples](https://github.com/bevyengine/bevy/blob/main/examples/README.md)) |
| Cost at $50k / $500k / $2M lifetime | **$0 / $0 / $0** | **$0 / $0–$6,930 a year / ≈$20,790** ([pricing](https://unity.com/pricing)) | **$0 / $0 / $50,000** ($35,000 at 3.5%) ([license](https://www.unrealengine.com/license)) | **$0 unless a quarter tops $250k**, then 4% of the excess ([licensing](https://flaxengine.com/licensing/)) | **$0 / $0 / $0** ([repo](https://github.com/bevyengine/bevy)) |
| Skinned roster + runtime retarget of shared T3 banks | **Good.** `RetargetModifier3D` maps every rig to one bone profile ([class ref](https://docs.godotengine.org/en/stable/classes/class_retargetmodifier3d.html)) | **OK.** Runtime Humanoid avatars; non-human fighters fall outside ([AvatarBuilder](https://docs.unity3d.com/6000.3/Documentation/ScriptReference/AvatarBuilder.BuildHumanAvatar.html)) | **Good.** Runtime IK Retargeter ([Epic](https://dev.epicgames.com/documentation/unreal-engine/runtime-ik-retargeting-in-unreal-engine)) | **OK.** Retargeting listed; runtime use unverified ([releases](https://github.com/FlaxEngine/FlaxEngine/releases)) | **Weak.** No built-in retarget, IK or state machine |
| Bone-morph sliders | **OK.** Per-bone scale + blend shapes ([Skeleton3D](https://docs.godotengine.org/en/stable/classes/class_skeleton3d.html)); may need helper bones | **OK.** No first-party system; open-source UMA "DNA" sliders ([UMA](https://gittrend.io/repo/umasteeringgroup/UMA)) | **Good.** Mutable; mobile cost undocumented | **OK.** Blend shapes | **OK.** Morph targets built in ([0.19](https://bevy.org/news/bevy-0-19/)) |
| Decals/tattoos on skinned bodies | **OK.** Paint into texture; projected decals limited ([decals](https://docs.godotengine.org/en/stable/tutorials/3d/using_decals.html)) | **OK.** Mobile needs screen-space decals; skinned support murky ([Unity decals](https://docs.unity.com/en-us/engine/6000.6/manual/visual-effects/decals/renderer-feature-decal/reference)) | **Good.** 5.8 mobile decals; Mutable sample does tattoos ([Epic news](https://www.unrealengine.com/news/the-mutable-sample-project-is-now-available)) | **Unknown** | **Unknown** |
| Physics bling (jiggle, chains) | **Good.** Built-in `SpringBoneSimulator3D` ([class ref](https://docs.godotengine.org/en/stable/classes/class_springbonesimulator3d.html)) | **Good.** Magica Cloth 2, third-party ([readme](https://kindnick-git.duckdns.org/kindnick/Streamingle_URP/media/branch/main/Assets/External/MagicaCloth2/Readme.txt)) | **Good.** KawaiiPhysics, MIT ([GitHub](https://github.com/pafuhana1213/KawaiiPhysics)) | **Good.** Spring Bone node | **Weak.** None built in |
| Portrait touch suite | **Good.** Anchored UI; native `VirtualJoystick` ([class ref](https://docs.godotengine.org/en/stable/classes/class_virtualjoystick.html)) | Not researched | Not researched | **Weak.** No gesture docs | **Weak.** UI is "editor-centric" ([0.20](https://bevy.org/news/bevy-0-20/)) |
| Rollback (online) path | **OK.** MIT GDScript addons, none shipped on mobile ([Snopek](https://store.godotengine.org/asset/snopek-games/godot-rollback-netcode/); [Delta Rollback](https://godotengine.org/asset-library/asset/3107)) | **Best.** Photon Quantum 3, UFE 2 Pro | **Weak.** Rollback Core verified on Windows only ([GitHub](https://github.com/gregorik/Rollback-Core)) | **OK.** Backdash, C# ([GitHub](https://github.com/lucasteles/Backdash)) | **Good.** bevy_ggrs; no 0.20 support yet ([GitHub](https://github.com/gschup/bevy_ggrs)) |
| Agent/shell friendliness | **Good.** Text scenes; Lab tests already headless | **Good.** YAML text scenes by default ([Unity](https://docs.unity3d.com/6000.3/Documentation/Manual/class-EditorManager.html)) | **Weak.** Binary assets and Blueprints | **Weak.** Editor-centric | **Mixed.** All code, no editor |
| Migration cost from this repo | **Low.** Lab, tests, netcode already here | **High.** Rewrite in C# | **Highest.** Rewrite in C++/Blueprint | **High.** Rewrite in C# | **High.** Rewrite in Rust |

**How the cost row was worked out.** It assumes one product, 3 Unity seats, no outside funding and no Epic Games Store sales. Unity Pro is $2,310 per seat per year. It is needed only once revenue plus funding passes $200k in any 12-month window, and there is no revenue share ([Unity pricing updates](https://unity.com/products/pricing-updates)). The $500k range depends on whether one 12-month window passes $200k. The $2M figure assumes about 3 paid years. Unreal takes 5% of lifetime gross above $1M, and that includes direct APK sales "regardless of who collects it". The 3.5% rate needs a simultaneous Epic Games Store release ([GameFromScratch](https://gamefromscratch.com/unreal-engine-launch-everywhere-with-epic/)). For Flax, one $400k quarter would cost $6,000. The two big engines break even at about $1.42M lifetime.

**Other engines ruled out:**
- Cocos Creator 3.8: its command-line build "still needs the GUI environment" ([Cocos CLI](https://docs.cocos.com/creator/3.8/manual/en/editor/publish/publish-in-command-line.html)).
- COCOS 4: its editor is a gated alpha ([DEV Community](https://dev.to/pht1991/cocos-4-is-open-source-but-is-it-time-to-leave-cocos-creator-38-577m)).
- O3DE: iOS is experimental and it has one public mobile ship ([Carbonated talk](https://o3de.org/lessons-learned-shipping-a-mobile-game-with-o3de/)).
- Stride 4.4: it has no morph targets yet ([issue #339](https://github.com/stride3d/stride/issues/339)) and needs Vulkan 1.3 on Android ([Stride 4.4](https://www.stride3d.net/blog/announcing-stride-4-4/)).
- Defold: it plays one baked clip at a time, with no blending or IK ([Defold](https://defold.com/manuals/model-animation/)).
- Fyrox: 1.0 is seven months old and comes from a small team ([Fyrox 1.0](https://fyrox.rs/blog/post/fyrox-game-engine-1-0-0/)).
- BRUTAL, Carbon and Babylon Native are not mobile-ready.

## What carries over from this repo

**Carries over unchanged** (all JSON or glTF; counts are from local repo scans):
- 99 fighter moveset files with 40,673 moves. Their timings are in seconds, so convert them to 60 fps frames when loading ([pantera.json](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/assets/movesets/pantera.json)).
- 17 decoded T3 animation banks: 37 MB and 3,176 packed rows ([t3anims.js decoder](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/js/t3anims.js)). The same clips are already inside the Lab's `*_t3real.glb` files, which Godot imports natively.
- Models: 62 game GLBs (59 skinned), 53 Lab GLBs and 1,521 converted part GLBs.
- Data files: roster canon, heights, the 1,150-part registry ([PARTS-REGISTRY.json](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/customization/PARTS-REGISTRY.json)) and the attire manifests.
- All Python/Blender pipelines: auto-rig, T3 bake, moveset merge and the Lab importers.
- The Lab's 745 lines of GDScript and its headless tests, after a 4.3 → 4.7 upgrade check.

**Ports almost line for line** (about 3,000 lines of JS to GDScript):
- the TekkenBuffer and notation code
- the T3 guard and hit-word rules
- `ai.js`
- roster and attire data
- mode logic
- the whole-number reference sim `fighter-sim.js`, which ran with 0 desyncs ([game/netplay/README.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/netplay/README.md))

**Must be rewritten:**
- stages, camera and scene setup
- the three.js retarget in `t3anims.js` (it becomes `RetargetModifier3D` or an import-time BoneMap)
- the CCD-IK layer
- the select screen and asset loading
- all HTML menus, including the `ui-wh` iframe, rebuilt as Godot Control nodes
- the synthesized Web Audio
- the Lab's own fighter code, which uses floats and must move to fixed-point

The web game also runs combat at 120 Hz while the Lab runs at 60 Hz. Pick one canonical 60 Hz whole-number sim.

**Known defects that come along:**
- `pantera_leoman_t3real.glb` fails the rig check today: it tears and sinks below the floor ([test_rig_check.py](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/lab/tests/test_rig_check.py), run 2026-10-22).
- `demonio.glb` shows T-pose arms in Godot 4.3.
- `pantera.glb` has a mirrored skin ([PROCEDURAL_AUDIT.md](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/anim/PROCEDURAL_AUDIT.md)).
- Six models are 86–92 MB each.
- The repo is 6 GB without LFS.

## First three milestones

1. **Toolchain and a phone build of the existing slice.**
   - Pin Godot 4.7.x and check its breaking changes.
   - Add an Android preset: non-Gradle, APK format, arm64-v8a only.
   - Use the Mobile (Vulkan) renderer, with Compatibility (OpenGL ES 3) as the automatic fallback. The Lab forces Compatibility everywhere today.
   - Generate the release keystore once and back it up.
   - Add a Linux CI job that runs `test_move_table.gd`, `run_match_headless.sh`, `qa_playtest.gd` and `test_rig_check.py`, then exports the signed APK.
   - Fix or gate the failing Pantera rig check.
   - *Done when:* the APK installs on a real mid-range phone and a screen recording shows the slice holding 60 fps.
2. **One canonical fight simulation.**
   - Port `fighter-sim.js`, the TekkenBuffer, the guard/hit words and the schema-v2 moveset loader into a fixed-point 60 Hz GDScript sim.
   - Drive animation with `AnimationTree` in MANUAL mode, stepping it once per sim tick ([AnimationMixer](https://docs.godotengine.org/en/stable/classes/class_animationmixer.html)).
   - Store hitboxes as per-frame data tables, not physics.
   - *Done when:* a mirror-style checksum test in CI shows 0 desyncs.
3. **Roster import and portrait touch shell.**
   - Convert the roster and attires to JSON.
   - Import the 62 GLBs: map bones to one profile, apply facing from `model-facing.json` and set a size budget for the 86–92 MB models.
   - Prove `RetargetModifier3D` on 49/50-bone rigs and native rigs, and fix the demonio T-pose.
   - Build a portrait select screen and a `VirtualJoystick` fight HUD.
   - Load only the 2 fighters in a match, using threaded loading ([background loading](https://docs.godotengine.org/en/stable/tutorials/io/background_loading.html)).

The creation suite and online play follow, after the move to 4.8.

## Risks and what to do about them

| Risk | Mitigation |
|---|---|
| No 3D fighter has shipped on Godot. Mid-range Android numbers are anecdotal. Frame pacing can drop a 90 Hz phone to 45 fps after one missed frame ([#109251](https://github.com/godotengine/godot/issues/109251)). | Milestone 1 ends with a recorded on-device 60 fps run. Test the `swappy_mode` settings on the lowest target phone. |
| Decals: the Compatibility renderer has none until 4.8. The Mobile renderer allows 8 per mesh. Projected decals likely slide on moving skin (docs silent). 4.8 is at beta 1 (15 Oct 2026) with no release date. | Paint tattoos into the body texture. Move to 4.8 stable before building the decal tool. |
| Determinism: Godot physics and its bundled Jolt give no cross-device guarantee ([Jolt docs](https://jrouwe.github.io/JoltPhysics/index.html); [GDQuest](https://www.gdquest.com/library/glossary/deterministic_simulation)). | Use a fixed-point sim on any engine. Jolt and spring bones are for looks only. |
| Rollback addons are young. Rollback costs CPU: NetherRealm saw about 3x frame cost before optimizing ([Edgegap summary](https://edgegap.com/blog/game-backend-deep-dive-mortal-kombat-x-injustice-2-rollback)). | Ship offline and CPU play first, as most mobile fighters did. Add online later with a short rollback window. |
| Losing the signing key means no update can ever reach sideloaded players. Godot requires the keystore and key passwords to match ([Android signing](https://developer.android.com/studio/publish/app-signing)). | Generate the key once with 25+ years of validity. Keep offline backups in two places and a CI secret. Never put it in git, and run gitleaks before every push. |
| Google developer verification began 30 Sep 2026 in four countries and goes global in "2027 and beyond". Unregistered apps can still install through adb or an "advanced flow" with warnings and a one-day wait ([Android blog](https://android-developers.googleblog.com/2026/06/android-developer-verification.html); [Android Authority](https://www.androidauthority.com/android-sideloading-developer-verification-first-wave-rollout-3717921/)). | Register as a verified developer before 2027. The free "limited distribution" option covers 20 test devices. |
| Size and memory: about 1 GB of fighter GLBs. Each fighter needs roughly 10.7 MiB of compressed textures (an estimate), so the whole roster can't stay in memory. | Ship pre-imported, VRAM-compressed assets. Use 1024² textures on low-end phones and 4.8 texture streaming ([importing images](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_images.html)). |
| Touch buttons may fire twice in 4.7; the fix (GH-120864) is in 4.8. | Test on a device. Use `VirtualJoystick` and raw touch events for fight inputs. |

## Corrections to things in the repo and spec

- The roster has **58 `FULL_ROSTER` entries, 49 distinct display names and 50 distinct model keys** on current main ([roster-full.js](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/game/js/roster-full.js)). Some research notes say 59; the repo scan could not reproduce that.
- `tools/netcode/godot/README.md` calls the Snoring Cat addon "peer-to-peer rollback (GGPO-shaped)". The vendored addon's own README says "Client-side prediction with server reconciliation", so it needs a server ([vendored README](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/tools/netcode/godot/snoringcat-rollback-netcode/README.md)).
- [`docs/ENGINE-SURVEY-2026.md`](https://github.com/mhvnsnt/western-heart/blob/research/engine-survey-20261016/docs/ENGINE-SURVEY-2026.md) recommends Jolt for hitboxes. Don't do that, because of the determinism risk above. It also names 4.7 "Director's Cut", but [Godot's release page](https://godotengine.org/releases/4.7/) calls it "Lights, Camera, Action!".
- [`docs/ANIMATION-PIPELINE.md`](https://github.com/mhvnsnt/western-heart/blob/e3ae81b76/docs/ANIMATION-PIPELINE.md) plans to use `SkeletonIK3D`, which is deprecated in 4.7 ([class ref](https://docs.godotengine.org/en/stable/classes/class_skeletonik3d.html)). Use the `IKModifier3D` family instead.
- "Tekken uses Unreal" is true for Tekken 7 and 8 ([Wikipedia](https://en.wikipedia.org/wiki/Tekken_8)). But Mortal Kombat 1 is a customized UE4, not UE5 ([Multiplayer.it](https://multiplayer.it/notizie/mortal-kombat-1-non-gira-unreal-engine-5-ed-boon-non-esclude-injustice-3-in-futuro.html)). Rivals of Aether II is UE5 with server-based SnapNet ([Wikipedia](https://en.wikipedia.org/wiki/Rivals_of_Aether_II); [Edgegap](https://edgegap.com/blog/rivals-of-aether-2-how-is-its-online-experience-is-so-good-netcode-rollback-dedicated-server-orchestration)). None of them is a small team's 3D mobile fighter.

## Unverified: check before building on these

- The minimal Godot APK size of 13–19 MB comes from forum posts in the 4.0–4.2 era.
- The 4.8 stable date is a guess (late 2026 to early 2027).
- Whether Godot bone scaling spreads to child bones is general knowledge; the docs are silent.
- No engine documents how its decals behave on skinned meshes.
- Phone cost of retarget + IK + spring bones is unknown in every engine.
- The definition of Unreal's "gross revenue", and whether a website APK counts as a "store", are unverified because the live EULA was blocked.
- Unity's seat rules for CI machines are unverified.
- Unity and Unreal touch-UI tooling was not researched.
- Flax builds for Android on a Linux host are unconfirmed.
- The repo survey's claim that 4.7 removed Android OBB support is unverified.
- The Lab tests were last recorded passing on 2026-10-14. There was no Godot binary in this container to re-run them.
