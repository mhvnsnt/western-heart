# Fighting-Game Technical Ecosystem Across Engines (Godot 4, Unity 6, Unreal 5, others): state as of Oct 2026

Research date: 2026-10-22. Method: web search plus page fetches of GitHub, GitLab, the Godot Asset Library and Asset Store, Photon and Unity docs, Epic docs, Wikipedia and Wikidata. I also queried the GitLab API and the Wikidata SPARQL endpoint directly. GDC Vault was in maintenance, PCGamingWiki blocked the fetcher (Cloudflare 403), and the GitHub API was blocked in this session. Repo activity dates for GitHub projects therefore come from page fetches, which often did not show commit dates. Items marked **[older]** predate 2025.

**Corrections to the assignment's assumptions:**
- Rivals 2 runs on **Unreal Engine 5**, not Unity.
- Virtua Fighter 5 R.E.V.O. runs on RGG's **Dragon Engine**, not Unreal.
- Them's Fightin' Herds runs on Lab Zero's **Z-Engine**, not Unity.
- Dead or Alive 6 runs on Koei Tecmo's **Katana Engine**.
- Mortal Kombat 1 runs on a **customized UE4**, not UE5.

---

## 1. Rollback netcode per engine: maturity, license, maintenance, mobile use

### Takeaway
Godot 4 has several active MIT-licensed rollback addons. Snopek's addon reached v1.0.0 in June 2026, but its publisher still marks it "unstable". BimDav's Delta Rollback was updated in October 2026. None has a shipped commercial 3D fighting game or documented mobile use. Unity has the most production-proven path: Photon Quantum 3 is deterministic, uses fixed-point math, targets mobile and has shipped mobile hits. UFE 2 adds a fighting-game toolkit with rollback in its Pro and Source editions. Unreal has no official GGPO-style solution: GGPOUE is UE4-era and Windows-only, and the new Rollback Core (UE5.5+, MIT) is verified only on Win64. AAA studios (NetherRealm, Bandai Namco, Capcom) all built rollback in-house.

### Cited Findings

**Godot 4**
- **Snopek "Rollback Netcode"**: the Godot Asset Store lists v1.0.0. The publisher marks this version unstable. It is MIT-licensed, needs at least Godot 4.2, and was last updated 9 June 2026. Features: input gathering, state save/load, message sending, mismatch detection, support for timers, animation, RNG and sound, and debugging tools. It is a free download of about 86 KB — [Godot Asset Store](https://store.godotengine.org/asset/snopek-games/godot-rollback-netcode/)
- The Snopek GitLab repo was created 2021-07-09. Its last activity was 2026-06-06, and it has 96 stars (GitLab API) — [GitLab snopek-games/godot-rollback-netcode](https://gitlab.com/snopek-games/godot-rollback-netcode)
- An older Godot 4 Asset Library entry for the same addon was "1.0.0-alpha", targeting Godot 4.2 and submitted December 2023 **[older]** — [Godot Asset Library #2450](https://godotengine.org/asset-library/asset/2450)
- A forum post calls Snopek's addon "probably the closest to a production-ready starting point for Godot 4". This is community opinion, not authoritative — [Moonjump forum](https://moonjump.com/forum/coding/rollback-netcode-in-godot-4-anyone-actually-done-this-or-is-it-just-theory-on-reddit-41365c)
- **Delta Rollback** (BimDav) is described as "a very fast addon for implementing rollback and prediction netcode". It is MIT-licensed, v0.11.0, targets Godot 4.2, and its listing is dated 2026-10-14 — [Godot Asset Library #3107](https://godotengine.org/asset-library/asset/3107). On the GitLab API, the repo was created 2024-05-22, last active 2026-10-14, and has 50 stars — [GitLab BimDav/delta-rollback](https://gitlab.com/BimDav/delta-rollback/)
- Delta Rollback came out of the action game *Jewel Run*, not a fighting game. This comes from a search summary of the author's Medium post, which returned 403 when fetched — [Medium: Delta Rollback](https://medium.com/@david.dehaene/delta-rollback-new-optimizations-for-rollback-netcode-7d283d56e54b)
- **Cerbere fork** (BimDav): a speed-focused fork of Snopek's addon. It needs a custom Godot build, so critical loops can be rewritten in C++, and it depends on a fork of SG Physics 2D — [GitLab cerbere-main](https://gitlab.com/BimDav/godot-rollback-netcode/-/tree/cerbere-main)
- **C# options**:
  - Fractural's GodotRollbackNetcodeMono is a C# wrapper over Snopek's addon for Godot 4.4 — [GitHub](https://github.com/Fractural/GodotRollbackNetcodeMono). Fractural's own earlier C# rollback solution is deprecated in favor of that wrapper — [GitHub](https://github.com/Fractural/FracturalRollbackNetcode)
  - **Klotho** requires Godot 4.4+ with .NET 8. It covers rollback, lockstep and client prediction, built on 32.32 fixed-point (FP64) math with a seeded RNG — [Godot Asset Library edit](https://godotengine.org/asset-library/asset/edit/23037)
  - **Backdash** is an MIT C# rollback SDK, "heavily inspired by GGPO", with async IO. It ships MonoGame and Godot samples, but no Unity sample. It has 176 stars, and the repo now lives under Delta3-Studio — [GitHub Backdash](https://github.com/lucasteles/Backdash)
- **SnoringCat godot-rollback-netcode** describes itself as "frame-synchronous client prediction + server reconciliation". It has pluggable ENet, WebSocket and WebRTC transports. It is a server-reconciliation framework, not GGPO-style peer-to-peer — [GitHub](https://github.com/SnoringCatGames/godot-rollback-netcode)
- **netfox** (Fox's Sake) is an MIT suite with a RollbackSynchronizer node for client prediction and server reconciliation, plus TickInterpolator and lag compensation. The listed latest version is 1.35.3 — [Godot Asset Library netfox](https://godotengine.org/asset-library/asset/edit/13402). A maintainer says Godot physics isn't deterministic, so RigidBodies "can't really participate in rollback". The bundled example uses CharacterBody3D and ShapeCast3D instead — [netfox discussion #272](https://github.com/foxssake/netfox/discussions/272)
- **GGPO in Godot**:
  - FlutterTal/godot_ggpo compiles GGPO in as a custom C++ engine module with SCons. This is not GDExtension, and it may target older Godot versions — [godot_ggpo (mirror)](https://backiee.wasmer.app/https_github_com/FlutterTal/godot_ggpo)
  - marcello505's *godot-ggrs-wrapper* is a Rust GDNative project (Godot 3 era) wrapping GGRS **[older]** — [GitHub profile](https://www.Github.com/marcello505)
  - I found no maintained GDExtension GGPO port for Godot 4.
- **Shipped Godot rollback titles**:
  - *Retro Tank Party* (Snopek's own game, on Steam and itch.io) rewrote its netcode as rollback in v1.2 **[older]** — [itch.io devlog](https://dsnopek.itch.io/retro-tank-party/devlog/330853/retro-tank-party-v12-rollback-netcode)
  - *Rakugaki Rumble* is a small Godot 4.2 fighting game using Snopek's addon. It is on itch.io; no Steam release was found — [itch.io devlog](https://dermondhase.itch.io/rakugaki-rumble/devlog/761404/rakugaki-rumble-is-live)

**Unity 6**
- **Photon Quantum 3** is described as "a deterministic realtime multiplayer engine for Unity", aimed at MOBAs, RTS, brawlers, sports and fighting games. Clients exchange only inputs; local actions run with zero lag while remote inputs are predicted and rolled back. Photon says its ECS runs physics-heavy multiplayer "on mobile phones" — [Photon Quantum](https://www.photonengine.com/quantum)
- Photon says Quantum powers the mobile hit *Stumble Guys* — [GDC 2024 exhibitor page](https://gdc.german-pavilion.com/en/sites/exhibitors/102743). An older showreel lists brawler-style Quantum games, including *Lego Brawls* (Red Games), *Bullet League*, *HeroVS* (thevs) and *Heroes Strike 3×3* (Wolfun) **[older]** — [Photon Quantum Showreel](https://blog.photonengine.com/photon-quantum-showreel)
- **Quantum pricing**: 100 CCU free for development and commercial use, limited to Fusion/Quantum games and one app per customer — [Photon blog](https://blog.photonengine.com/?p=5466). A "Plus" package gives 200 CCU (100 paid + 100 free) for $95 for one year — [Photon blog](https://blog.photonengine.com/new-200-ccu-plus-package-100-paid-100-free/)
- **Quantum Fighting Sample** (Quantum 2): includes a "HitBox editor using Animation Frames", an InputBufferSystem for special moves (about 10 frames by default), a tick-accurate Custom Animator, and character select inside the simulation. It targets Unity 2020.3.20f1, and its platforms are PC/Mac **and Android**. It requires a Gaming Circle or Industries Circle subscription, and its bundled third-party assets need separate licenses — [Photon docs: Fighting overview](https://doc.photonengine.com/quantum/v2/game-samples/fighting/overview); [input](https://doc.photonengine.com/quantum/v2/game-samples/fighting/input). The latest listed version is 2.1.7 (27 June 2023) **[older]**. No Quantum 3 port was confirmed — [Photon docs: download](https://doc.photonengine.com/quantum/v2/game-samples/fighting/download)
- **Quantum caveat**: every client holds the full game state, so hidden information is hard to protect. Photon calls a fully cheat-proof game "an utopian idea" (Quantum 2 docs) — [Photon cheat protection](https://doc.photonengine.com/quantum/v2/manual/cheat-protection)
- **UFE 2 (Universal Fighting Engine)**:
  - A Unity toolkit for 2D, 2.5D and 3D fighters, in Lite, Basic, Standard, Pro and Source tiers. "Rollback Netcode" is listed under Pro; Standard has only "Network". The site says "Tested with Unity 2021.3 and Unity 6", and the page shows a move editor — [UFE site](https://www.ufe3d.com/ufe2/)
  - The UFE 2 announcement says its biggest additions were "native netcode with deterministic physics" — [UFE forum](https://www.ufe3d.com/forum/viewtopic.php?id=1434)
  - The 2.6.0 changelog tells rollback users to rerun MapRecorder on each character after updating — [UFE forum changelog](https://www.ufe3d.com/forum/viewtopic.php?id=4305)
  - The Lite listing ($59) mentions "Network support (Frame Delay and Rollback)" — [Payhip UFE Lite](https://payhip.com/b/4yc6)
  - Store pages call UFE "mobile friendly", but no source tests rollback on phones. One source warns that rollbacks "can be heavy on the CPU" — [Unity Discussions UFE2](https://discussions.unity.com/t/universal-fighting-engine-2/708738)
- **SnapNet** (High Horse Entertainment) is a server-authoritative netcode SDK for Unreal (standalone plugin) and Unity (UPM). For fighting games it can "rollback and resimulate the entire game state (like GGPO)", and it states "strict determinism not required". Pricing comes by contacting the company; mobile is not mentioned — [snapnet.dev](https://www.snapnet.dev/)

**Unreal Engine 5**
- **Rollback Core** (gregorik):
  - Deterministic GGPO-style rollback for UE 5.5–5.8, MIT-licensed. Verified on Windows 10/11 x64 only; other platforms are "unverified", and mobile isn't mentioned.
  - Features: fixed tick (60 Hz default, configurable 15–240), state capture through `UPROPERTY(SaveGame)` into a ring buffer, and UDP with 8-frame input redundancy. Supports up to 4 peers by default (protocol cap 8).
  - Has no NAT traversal. Matchmaking, a frame-scrubber debugger and a desync inspector are only in the paid "Pro" version on Fab.
  - 22 stars and 15 commits; verification noted 2026-09-16.
  - Explicitly unsafe for rollback: CharacterMovementComponent, Chaos physics on rolled-back actors, latent Blueprint nodes, FTimerManager, unseeded RNG and async loads. GAS is only "partially" compatible.
  - Source: [GitHub gregorik/Rollback-Core](https://github.com/gregorik/Rollback-Core); [UE forum: Rollback Core Pro](https://forums.unrealengine.com/t/gregorigin-rollback-core-pro-accessible-netcode-framework-for-fighting-platform-games/2728262)
- **GGPOUE** (BwdYeti) is a "UE4 plugin port of GGPO". It is MIT-licensed and **Windows-only**, because GGPO's network layer uses Win32 APIs. It has 57 stars, no releases, and a sample project (VectorWar UE) **[older, UE4-era]** — [GitHub BwdYeti/GGPOUE4](https://github.com/BwdYeti/GGPOUE4)
- **GGPO upstream** is MIT and about 3.6k stars. "Building GGPO is currently only available on Windows", and a port to other platforms is described as "efforts being made". There is no official mobile build — [GitHub pond3r/ggpo](https://github.com/pond3r/ggpo)
- **Night Sky Engine** is an MIT open-source 2D/2.5D fighting framework in UE (requires UE 5.7). It bundles the GGPOUE4 plugin, has a collision editor, targets consoles and high-end PCs, has a `lowend` branch, and 335 stars — [GitHub NightSkyEngineRewrite](https://github.com/WistfulHopes/NightSkyEngineRewrite)
- **Epic's own Mover plugin** does rollback networking on top of the Network Prediction plugin or Chaos Networked Physics. It is server-authoritative prediction and resimulation, not peer-to-peer GGPO, and Epic marks it "experimental" — [Epic docs: Mover](https://dev.epicgames.com/documentation/en-us/unreal-engine/mover-in-unreal-engine)
- A UE forum reply argues that the built-in Character Movement rollback "is not the same rollback we see in fighting games" — [UE forum](https://forums.unrealengine.com/t/how-to-implement-rollback-netcode-on-ue5/1175132/1)
- **Arcforged's Bolt Framework** (UE4) is described as fully deterministic and geared to rollback netplay, with cross-platform rollback as a stated aim — [arcforged.itch.io](https://arcforged.itch.io/)

**AAA in-house rollback (the reference implementations)**
- **NetherRealm** (MKX/Injustice 2, custom UE3), from GDC 2018's "8 Frames in 16ms" by Michael Stallone, via a secondary write-up — [GDC Vault](https://gdcvault.com/play/1025021/8-Frames-in-16ms-Rollback); [Edgegap summary](https://edgegap.com/blog/game-backend-deep-dive-mortal-kombat-x-injustice-2-rollback) **[older]**:
  - A 7-frame rollback window with 3 frames of fixed input delay.
  - Idle frame cost went from 9–10 ms to about 30 ms after the first rollback build, then down to about 13 ms after "several man-years" of optimization.
  - Parallelizing state restore cut it from 2.7 ms to 1.3 ms for twice the data.
  - Particles were the biggest spike. A predictive particle re-simulation system plus a 100 MB particle cache handled them.
  - Desyncs came largely from IK and physics systems that ran once per tick instead of per simulated frame.
  - The shipped desync rate was under 1.1%.
- **Tekken 8** (UE5) has rollback with user settings: Standard, Prioritize Graphics and Prioritize Response — [EventHubs](https://eventhubs.com/news/2023/jul/22/tekken-8-rollback-settings). Wikipedia notes that Arika handles ongoing development "excluding rollback netcode" — [Wikipedia: Tekken 8](https://en.wikipedia.org/wiki/Tekken_8). In 2020, Harada said rollback in Tekken 7 caused problems with 3D animations (secondary report) **[older]** — [SI.com](https://videogames.si.com/news/tekken-8-crossplay-rollback-netcode)
- **Street Fighter 6** (RE Engine) "supports cross-platform play and rollback netcode" — [Wikipedia: SF6](https://en.wikipedia.org/wiki/Street_Fighter_6). The director said the netcode was built from scratch rather than carried over from SFV (2022 report) — [goclecd.fr](https://www.goclecd.fr/street-fighter-6-inclut-un-netcode-rollback-et-du-cross-play-a-06-2022/)
- **VF5 R.E.V.O.** added rollback to "13-year-old source code". The producer said it "seemed impossible at first" — [Automaton](https://automaton-media.com/en/news/virtua-fighter-5-revo-adding-rollback-netcode-to-13-year-old-source-code-seemed-impossible-at-first-but-we-knew-it-was-necessary/)
- **Rivals of Aether II** (UE5) uses SnapNet with authoritative dedicated servers on Edgegap. It re-simulates without strict determinism. This is Edgegap marketing — [Edgegap blog](https://edgegap.com/blog/rivals-of-aether-2-how-is-its-online-experience-is-so-good-netcode-rollback-dedicated-server-orchestration)

### Inferences
- For a Godot 4 *3D mobile* fighter, the rollback layer would be mostly first-party work. The addons supply the frame loop, input exchange, save/load hooks and debug tools. But the state you roll back (character transforms, hitboxes, animation time) has to be your own deterministic data, because Godot's physics and AnimationTree are not rollback-safe. The netfox maintainer and Rollback Core's unsafe-systems list say the same for their engines.
- GGPO itself is effectively Windows-only. Any mobile peer-to-peer rollback would use a pure-script or C# implementation (Snopek or Delta in GDScript, Backdash or Klotho in C#, Quantum) or a custom one.
- NetherRealm's numbers show the CPU cost of rolling back a 3D fighter: about 3x frame cost before heavy optimization. On mobile CPUs, budget for a shorter rollback window, cheap state snapshots and non-simulated VFX.

### Gaps
- No GitHub commit dates could be retrieved for GGPOUE, Night Sky, Fray, Backdash or GGPO, because the GitHub API was blocked and the pages didn't show dates. Maintenance status for those is unconfirmed.
- No documented case of Snopek, Delta Rollback or netfox running a shipped *mobile* game.
- No public rollback performance numbers for UFE 2 or Quantum on phones.
- Photon's current paid-tier prices were not confirmed on official pages.
- The GDC Vault was in maintenance, so the Stallone talk itself wasn't viewed; details come from the Edgegap summary.

---

## 2. Determinism: fixed-point libraries, fixed-tick patterns, ARM vs x86 floats per engine

### Takeaway
Shipped cross-platform rollback relies on one of two approaches. The first is integer or fixed-point simulation: Photon Quantum uses Q48.16 fixed-point, and SG Physics 2D uses fixed-point. The second is careful same-order float math on matching hardware, which is NetherRealm's approach. Server-authoritative resimulation (SnapNet) avoids strict determinism entirely. Unity 6 Burst has an official `FloatMode.Deterministic` for 64-bit targets. Godot's built-in physics is not deterministic. Rapier (third-party) claims cross-platform determinism, while Godot's built-in Jolt integration makes no guarantee. For ARM phones playing x86 PCs, the safe pattern is fixed-point gameplay state, with floats used only for rendering.

### Cited Findings
- **Photon Quantum** uses an FP struct in Q48.16 format: 48 integer bits and 16 fractional bits stored in one `long`. It replaces float and double to guarantee cross-platform determinism. Quantum 3's float-conversion helpers are flagged non-deterministic and should be avoided in simulation code — [Quantum 2 FP docs](https://doc.photonengine.com/quantum/v2/manual/quantum-ecs/fixed-point); [Quantum 3 FP API](https://doc-api.photonengine.com/en/quantum/current/struct_photon_1_1_deterministic_1_1_f_p.html)
- **Unity Burst `FloatMode.Deterministic`** makes float math "consistent across all supported platforms". It is only supported on 64-bit architectures. It switches to deterministic math functions, disables some optimizations and flushes subnormals to zero, which can cost performance (Unity 6.6 manual) — [Unity Manual: Burst float determinism](https://docs.unity3d.com/Manual/burst/float-precision-determinism.html)
- A Unity staff reply said Unity Physics is "deterministic per architecture", not necessarily across architectures, and that game code still needs "considerable work" **[older, ~2020]** — [Unity forum](https://forum.unity.com/threads/what-is-the-current-state-of-the-cross-platform-determinism-of-unity-physics.922055/)
- **Godot built-in physics** "extensively uses floating-point numbers", making it "unsuitable for deterministic simulation". GDQuest suggests writing fixed-point code yourself, using Vector2i, Vector3i and PackedInt64Array for integer math — [GDQuest glossary](https://www.gdquest.com/library/glossary/deterministic_simulation)
- **SG Physics 2D** (Snopek) is a "deterministic 2D physics engine for Godot based on fixed-point math", "useful for… rollback netcode". It is MIT-licensed, was last active 2026-07-26, and has 52 stars (GitLab API). It is 2D only — [GitLab sg-physics-2d](https://gitlab.com/snopek-games/sg-physics-2d)
- **Godot Rapier**: the Rapier library is cross-platform deterministic. The addon supports state serialization through `import_binary`, and cross-platform determinism carries an unquantified performance penalty. Godot-side inputs (animation, scripting) must be controlled by the developer. The page points to "Balaur" (v0.1) for a fixed 60 Hz tick, per-tick digests and rollback — [godot.rapier.rs determinism](https://godot.rapier.rs/docs/documentation/determinism)
- **Jolt in Godot**: built into Godot 4.4+ as a module. A search summary reports that the Godot Jolt docs say Jolt itself is deterministic but "Godot Jolt is not able to make such guarantees". I couldn't fetch the primary doc for this — [Godot forum thread](https://forum.godotengine.org/t/what-3d-physics-engine-should-i-use-both-integrated-and-plugins-included/105757)
- **Klotho** (Godot .NET) uses 32.32 fixed-point math and a seeded RNG — [Godot Asset Library](https://godotengine.org/asset-library/asset/edit/23037). **FixedMathSharp** is a .NET fixed-point library with a seedable RNG, usable in Unity; a Godot forum user says it "really has no documentation" — [NuGet FixedMathSharp](https://www.nuget.org/packages/FixedMathSharp); [Godot forum](https://forum.godotengine.org/t/best-way-to-make-a-deterministic-algorithm-in-godot/123754)
- **Unreal Rollback Core**: rolled-back state should be plain `SaveGame` properties. It uses fixed-step integration and a seeded `FRandomStream` (seed = frame index). Visuals are not rolled back — [GitHub Rollback-Core](https://github.com/gregorik/Rollback-Core)
- **NetherRealm**: "the vast majority of the game is bit-for-bit deterministic". Float operations run in the same order on every machine, thousands of "fencepost" checks verify sync, and any match can be replayed offline from recorded input **[older]** — [Edgegap summary of GDC talk](https://edgegap.com/blog/game-backend-deep-dive-mortal-kombat-x-injustice-2-rollback)
- **ARM vs x86**: x86 (PC, Xbox) and ARM (Switch, mobile) can produce subtly different float results. Causes include rounding, fused multiply-add and compiler optimizations. Suggested fixes: fixed-point math, disabling fast-math and FMA, and per-frame checksums. These are developer blogs, lower authority — [Bugnet blog](https://bugnet.io/blog/how-to-debug-floating-point-determinism-across-platforms)
- A forum commenter argues that ARM-to-x86 determinism requires restricting yourself to basic arithmetic and reimplementing everything else — [Unity Discussions IL2CPP thread](https://discussions.unity.com/t/are-floating-point-numbers-deterministic-on-the-same-architecture-il2cpp/892251)
- **SnapNet** avoids strict determinism by being server-authoritative and resimulating — [snapnet.dev](https://www.snapnet.dev/)
- A search-surfaced anecdote: a Unity fighting-game developer found that hitboxes attached to animated joints broke determinism. The fix was to precompute hitbox positions per animation frame. The exact source page was not verified — related thread: [Godot forum: determinism for my fighting game](https://forum.godotengine.org/t/need-help-understanding-and-implementing-determinism-for-my-fighting-game/144694)

### Inferences
- For a 3D fighter, the practical pattern is to keep the simulation in fixed-point or integer units:
  - positions, velocities and facing
  - frame counters
  - hitbox and hurtbox volumes baked per animation frame into data tables
- The skinned skeleton, physics accessories (hair, cloth) and VFX stay on the render side and are never fed back into the simulation. This matches NetherRealm's split between deterministic simulation and non-deterministic particles, Rollback Core's "visuals not rolled back" rule, and the netfox advice.
- This pattern is engine-agnostic. It removes most of the per-engine determinism risk, at the cost of writing your own collision and movement for fighters.

### Gaps
- No primary source on whether Godot's built-in Jolt module is compiled with Jolt's cross-platform determinism flag.
- No measured ARM-vs-x86 desync data for any Godot or Unity fighting game.
- How Tekken 8 and SF6 achieve determinism is not publicly documented.

---

## 3. Hitbox/hurtbox editors, frame-data tools and input buffers per engine

### Takeaway
Unity has the most turnkey fighting-game tooling: UFE 2's move and hitbox editors, and Quantum's Fighting Sample with an animation-frame hitbox editor and input buffer. Godot 4 has modular MIT pieces: Fray for state machines, motion/charge inputs and hit states, plus several 2D hitbox addons. There is no 3D frame-data editor. Unreal has templates (n00dFighter, Fighting Games Template) and the open-source Night Sky Engine with a collision editor, mainly 2D/2.5D. Every serious 3D fighter studio uses internal tools.

### Cited Findings

**Godot 4**
- **Fray** (Pyxus) is an MIT "modular Godot 4 addon" for Godot 4.2+. It has a hierarchical state machine, composite input detection (directional, motion, charge, sequence), input buffering, and hitbox "hit states" keyed in AnimationPlayer. It is "currently in an alpha state", has no releases, and has 312 stars — [GitHub Pyxus/fray](https://github.com/Pyxus/fray); [Godot Asset Library](https://godotengine.org/asset-library/asset/1594)
- **Framitor** binds hitboxes to AnimatedSprite2D frames, with per-frame damage, knockback, hitstop and shake. It is 2D only — [GitHub Godot-Framitor](https://github.com/0xEvsky/Godot-Framitor)
- **Combat Collider** is a 2D hitbox/hurtbox addon driven by animation call-method tracks — [Godot Asset Library](https://godotengine.org/asset-library/asset/3696). **Active-Frame-Hitbox** is a Godot 4.x hitbox/hurtbox/health component — [GitHub](https://github.com/MisterOsoo/Active-Frame-Hitbox)
- **Frame Data Kit** ($4) lets you draw hit, hurt and push boxes per frame on Aseprite layers. It exports JSON/CSV, and a Godot 4 helper builds the areas. It was tested on Godot 4.7.2 and is 2D — [itch.io announcement](https://itch.io/t/7110528/frame-data-kit-hitboxes-frame-data-for-aseprite-with-a-godot-4-helper-4-tool)
- An open-source hobby 3D fighter in Godot 4 has 4 fighters, 4 stages, and Arcade, Versus and Training modes. It could serve as a reference — [GitHub clintcan/3d-fighter](https://github.com/clintcan/3d-fighter)

**Unity**
- **UFE 2** has a move editor and documentation for hit logic, armor and projectiles. Store listings mention a "Custom Hitbox Editor" and "Precision Hitboxes" — [UFE site](https://www.ufe3d.com/ufe2/); [Payhip UFE Lite](https://payhip.com/b/4yc6)
- **Quantum Fighting Sample** has a "HitBox editor using Animation Frames" and an InputBufferSystem with about 10 frames of tolerance by default — [Photon docs](https://doc.photonengine.com/quantum/v2/game-samples/fighting/overview); [input](https://doc.photonengine.com/quantum/v2/game-samples/fighting/input)

**Unreal**
- **n00dFighter Template** has modular hurtbox components, a "hitbox designer for animations", AI, and rounds. It lists UE 5.3 — [UE Marketplace](https://www.unrealengine.com/marketplace/en-US/product/n00dfighter-template-plugin)
- The **Fighting Games Template Project** aims for minimal Blueprint editing. Its third generation supports UE 5.4+ — [UE Marketplace](https://www.unrealengine.com/marketplace/en-US/product/fighting-games-template-project)
- **Night Sky Engine** has a collision editor and is MIT, 2D/2.5D, UE 5.7 — [GitHub](https://github.com/WistfulHopes/NightSkyEngineRewrite)
- The **FightingGame-UE5** hobby project covers command inputs and hitbox/hurtbox systems — [GitHub](https://github.com/stackOverflower92/FightingGame-UE5)

### Inferences
- No engine offers a mature, maintained *3D* frame-data editor off the shelf; UFE 2 comes closest. For Western Heart, a custom data-table approach is engine-portable: per-move frame ranges, hitbox volumes per frame relative to the root, cancel windows and input buffer windows. Data extracted from teardowns would map more directly onto such tables than onto any addon's format.

### Gaps
- Godot hitbox addons are almost all 2D; I found no Godot 3D hitbox or frame-data editor.
- UFE's 3D hitbox workflow and current changelog after 2.6 were not retrieved, because the site is JS-heavy.

---

## 4. Shipped fighting games and their engines (3D, indie, mobile): what they teach

### Takeaway
AAA 3D fighters use Unreal (Tekken 7 on UE4, Tekken 8 on UE5, MK1 on custom UE4, Soulcalibur VI on UE4) or proprietary engines (SF6 on RE Engine, DOA6 on Katana, VF5 on Dragon Engine). Mobile 3D fighters split between Unreal (NetherRealm's MK Mobile and Injustice 2 Mobile on UE4) and Unity (Shadow Fight 3/4, likely MCOC). Godot's shipped fighting games are 2D or small: YOMIH on Godot 3.5, and Bow-wow Battle on Godot 4 in early access since May 2026. No commercial 3D fighter on Godot 4 was found. Most successful mobile fighters avoided real-time peer-to-peer rollback: MCOC fights AI, and Tekken Mobile was single-player.

### Cited Findings

**3D AAA**

| Game | Engine | Netcode | Source |
|---|---|---|---|
| Tekken 7 | Unreal Engine 4 | — | [Wikidata Q17378799](https://www.wikidata.org/wiki/Q17378799) |
| Tekken 8 (Jan 2024; PS5/Xbox Series/PC) | Unreal Engine 5 | rollback | [Wikipedia](https://en.wikipedia.org/wiki/Tekken_8) |
| Street Fighter 6 (June 2023; Switch 2 June 2025) | RE Engine | rollback + crossplay | [Wikipedia](https://en.wikipedia.org/wiki/Street_Fighter_6) |
| Mortal Kombat 1 | customized UE4 (moved from MK11's heavily modified UE3) | rollback | [Multiplayer.it](https://multiplayer.it/notizie/mortal-kombat-1-non-gira-unreal-engine-5-ed-boon-non-esclude-injustice-3-in-futuro.html); [Tecmundo](https://www.tecmundo.com.br/voxel/265084-mortal-kombat-1-nao-usa-unreal-engine-5-veja-graficos-feitos.htm); [Everyeye](https://www.everyeye.it/notizie/mortal-kombat-1-avra-supporto-rollback-netcode-652249.html) |
| Soulcalibur VI | Unreal Engine 4 | — | [Wikidata Q45080517](https://www.wikidata.org/wiki/Q45080517) |
| Dead or Alive 6 | Katana Engine (in-house) | — | [Wikipedia](https://en.wikipedia.org/wiki/Dead_or_Alive_6); [DualShockers](https://www.dualshockers.com/dead-or-alive-6-interview-part-2/) |
| VF5 Ultimate Showdown / R.E.V.O. | Dragon Engine (RGG + AM2) | rollback added in R.E.V.O. | [GamerBraves](https://gamerbraves.com/?p=203453); [FightersGeneration](https://fightersgeneration.com/games/vf5revo.html) |

- **Tekken 8 production**: Maya for modeling, MotionBuilder for mocap, and UE5 linked through LiveLink. The team needed to hold 60 fps during stage destruction, so destruction was keyframed in Pulldownit rather than physics-simulated because physics was "too resource-heavy" — [Autodesk blog](https://blogs.autodesk.com/media-and-entertainment/2025/01/28/tekken-8-legacy-meets-innovation-with-the-combined-power-of-maya-and-unreal-engine/)
- **Dead or Alive 6**: built by Koei Tecmo's technical support division together with Team Ninja. It replaced the Soft Engine, which was known for jiggle physics — [DualShockers](https://www.dualshockers.com/dead-alive-6-wont-use-soft-engine/)
- **Guilty Gear Strive** and **Dragon Ball FighterZ** run on Unreal Engine 4 (2.5D, for reference) — [Wikidata Q85863730](https://www.wikidata.org/wiki/Q85863730); [Wikidata Q30246735](https://www.wikidata.org/wiki/Q30246735)

**Indie and AA fighters**

| Game | Engine | Notes | Source |
|---|---|---|---|
| Rivals of Aether II (Oct 2024, PC) | Unreal Engine 5 | SnapNet + dedicated servers; the original Rivals used GameMaker | [Wikipedia](https://en.wikipedia.org/wiki/Rivals_of_Aether_II) |
| Pocket Bravery (PC Aug 2023, consoles Apr 2025) | Unity | rollback | [Wikipedia](https://en.wikipedia.org/wiki/Pocket_Bravery) |
| Your Only Move Is Hustle | Godot 3.5 (GodotSteam 3.5.1 fork) | Godot asset library lists a mod assistant for it | [itch.io forum](https://itch.io/t/2632153/what-game-engine-you-used); [YOMI modding docs](https://yomi-docs.readthedocs.io/en/latest/_sources/tutorials/start.rst.txt); [Godot Asset Library](https://godotengine.org/asset-library/asset/edit/11431) |
| Them's Fightin' Herds | Lab Zero's Z-Engine (Skullgirls), not Unity | GGPO rollback | [Wikipedia](https://en.wikipedia.org/wiki/Them%27s_Fightin%27_Herds) |
| Omen of Sorrow | Unreal Engine 4 | GGPO rollback | [Wikidata Q58875446](https://www.wikidata.org/wiki/Q58875446); [Xbox Store](https://www.xbox.com/en-US/games/store/a/9PPM6VDD4G82) |
| Nickelodeon All-Star Brawl (Ludosity) | Unity | — | [Wikidata Q107530622](https://www.wikidata.org/wiki/Q107530622) |
| Fraymakers | engine not confirmed | early access Jan 2023; FrayTools editor; Switch/Switch 2 planned | [Wikipedia](https://en.wikipedia.org/wiki/Fraymakers) |
| Bow-wow Battle (M.Katsu) | Godot 4 | early access on Steam 1 May 2026; 2D/3D unstated; full release planned late 2026–early 2027 | [Wikipedia](https://en.wikipedia.org/wiki/Bow-wow_Battle) |

- **Pocket Bravery**: the rollback library used was not found.
- **Your Only Move Is Hustle**: the engine claim comes from community and modding sources, not a developer statement. It is a turn-based simultaneous-input fighter, not a real-time one.
- **Them's Fightin' Herds**: Lab Zero supplied the Z-Engine after Mane6 outgrew Fighter Maker 2D.
- **Nickelodeon All-Star Brawl**: one article speculates it shares an engine with Ludosity's *Slap City*.
- **Fraymakers**: devs say rollback was designed in from the start (Kickstarter coverage) — [Gematsu](https://www.gematsu.com/2020/11/kickstarter-campaign-launched-for-customizable-platform-fighting-game-fraymakers-for-pc)

**Mobile fighters**

| Game | Engine | Combat / PvP | Source |
|---|---|---|---|
| Injustice 2 Mobile (May 2017) | UE4 (console version UE3) | Arena PvP | [Wikipedia](https://en.wikipedia.org/wiki/Injustice_2); [Wikidata](https://www.wikidata.org/wiki/Q24717189) |
| Mortal Kombat Mobile (ex-MKX Mobile, 2015) | UE3 at launch, UE4 from the Feb 2019 2.0 update | — | [Wikipedia](https://en.wikipedia.org/wiki/Mortal_Kombat_Mobile); [DSOGaming](https://www.dsogaming.com/news/mortal-kombat-11-uses-custom-unreal-engine-3-mobile-version-powered-by-unreal-engine-4) |
| Marvel Contest of Champions (Dec 2014; Steam June 2025) | Unity (unconfirmed by Kabam) | 3D arena on a 2D plane; Arena opponents are AI-controlled; Battlegrounds is 1v1 and deck-based | [Wikipedia](https://en.wikipedia.org/wiki/Marvel_Contest_of_Champions) |
| Shadow Fight 3 (2017) / Shadow Fight 4: Arena (Nov 2020) | Unity (indirect evidence) | SF4: Arena is billed as "the first mobile fighting game featuring real-time synchronous PvP", 3-hero teams | [App Store](https://apps.apple.com/us/app/-/id1479050948) |
| Tekken Mobile (Mar 2018 – Feb 2019) | not found | single-player, gacha "Waza Cards" | [Wikipedia](https://en.wikipedia.org/wiki/Tekken_Mobile) |
| Brawlhalla (mobile Aug 2020) | Adobe AIR | faithful port of PC/console | [Wikipedia](https://en.wikipedia.org/wiki/Brawlhalla); [BlueStacks review](https://www.bluestacks.com/blog/app-reviews/brawlhalla-mobile-review-en.html) |
| Dragon Ball Legends (2018) | not found | real-time global PvP; Google Cloud for networking | [Hardcore Gamer](https://hardcoregamer.com/previews/gdc-2018-everyones-saiyan-dragon-ball-legends-could-dominate-mobile-combat/294416/); [Lowyat](https://lowyat.net/2018/158219/bandai-namco-unveils-dragon-ball-legends-mobile-game-focuses-multiplayer-pvp) |
| KOF ALLSTAR (Netmarble) | not found | beat-'em-up RPG, simplified touch; shut down Oct 30, 2024 | [Gematsu](https://gematsu.com/2018/05/action-rpg-the-king-of-fighters-all-star-announced-for-smartphones); [Giant Bomb](https://www.giantbomb.com/games/3030-69015/) |
| Smash Legends (5minlab/LINE Games, Apr 2021) | not found | mobile/PC crossplay; Duel, 3v3, 8-player modes | [Inven Global](https://www.invenglobal.com/articles/13801/line-games-launches-smash-legends-mobile-game-worldwide) |

- **Injustice 2 Mobile**: NetherRealm took the console models and optimized them for mobile — [Android Central](https://androidcentral.com/injustice-2-hands)
- **Mortal Kombat Mobile**: NRS's Jon Greenberg confirmed the mobile team uses UE4 (March 2019).
- **Marvel Contest of Champions**: the Unity claims come only from a player post and a forum thread blaming a "Unity engine update" for bugs — [Unity Discussions](https://discussions.unity.com/t/problems-with-a-mobile-game-that-uses-unity/860107); [MCOC forums](https://forums.playcontestofchampions.com/en/discussion/132470/is-the-unity-engine-update-the-source-of-all-the-bugs). It made $100M in 7 months **[older, 2015]** — [Deconstructor of Fun](https://www.deconstructoroffun.com/blog//2015/12/how-kabams-contest-of-champions-made.html)
- **Shadow Fight series**:
  - Shadow Fight 3 and 4: Arena were developed by Banzai.Games and published by Nekki — [Wikipedia: Shadow Fight](https://en.wikipedia.org/wiki/Shadow_Fight_3)
  - Unity evidence is indirect: Nekki "Unity Developer" vacancies naming Shadow Fight 3, and "Mobile, Unity" vacancies for SF4: Arena — [Nekki vacancy](https://nekki.com/vacancy/sf3-shablon); [Habr vacancy](https://career.habr.com/vacancies/1000033800); [hh.ru vacancy](https://hh.ru/vacancy/137382718)
  - Shadow Fight 2 is listed as Marmalade on Wikidata, and as Unity from v2.0.0 on Wikipedia, which is tagged "citation needed" — [Wikidata Q28839147](https://www.wikidata.org/wiki/Q28839147); [Wikipedia SF2](https://en.wikipedia.org/wiki/Shadow_Fight_2)

### Inferences
- **Unreal on mobile**: the only AAA-quality 3D fighters on mobile with console-derived assets (Injustice 2, MK Mobile) came from NetherRealm on UE4. That is a large studio running a separate mobile team and engine branch.
- **Unity on mobile**: Unity's mobile fighters (Shadow Fight, MCOC) were built mobile-first with simplified combat and mostly asynchronous or AI PvP. Shadow Fight 4: Arena is the notable real-time synchronous PvP case.
- **Godot**: there is no precedent for a commercial 3D fighting game on Godot 4, on mobile or anywhere else. Choosing Godot means pioneering, not following.
- **Netcode for a first mobile release**: real-time peer-to-peer rollback is not something successful mobile fighters relied on. Shipping offline/AI play first and adding PvP later is the dominant pattern.

### Gaps
- No confirmed engine for Tekken Mobile, Dragon Ball Legends, KOF ALLSTAR, Smash Legends, Slap City or Fraymakers.
- No official Kabam or Unity confirmation for MCOC.
- No netcode details for Shadow Fight 4: Arena.
- No mobile performance postmortems (frame rate or thermal targets) were found for any mobile fighter.

---

## 5. Touch controls for 3D fighters on mobile (shipped schemes)

### Takeaway
Shipped mobile fighters use three families of control:
- **Gesture ("swipe fighter")**: Injustice and MCOC use tap to attack and swipe for movement and specials, plus a block button or two-finger block, and a meter icon for supers.
- **Virtual stick plus buttons**: Shadow Fight 3 and Brawlhalla.
- **Stick plus card or skill buttons**: Dragon Ball Legends, Tekken Mobile's Waza Cards.

Console fighters address accessibility with simplified schemes; SF6 Modern assigns specials to one button plus a direction.

### Cited Findings
- **Injustice 2 Mobile** (official guide):
  - Tap for a standard attack.
  - Swipe up for a jump attack, down for a crouch attack, right for a dash attack, left to evade.
  - Left swipe then tap for a ranged attack.
  - Block with a bottom-left button or two fingers on the screen.
  - Tap the glowing yellow icon for an unblockable super when the meter is full.
  - Source: [WB Games support](https://dcgamessupport.wbgames.com/hc/en-us/articles/360001902528-Injustice-2-Mobile-Beginner-Guide)
- **Marvel Contest of Champions** controls are built for touch, not on-screen buttons or virtual joysticks. They cover light, medium and heavy attacks, block, dodge, back-shuffle and forward-sprint — [Wikipedia](https://en.wikipedia.org/wiki/Marvel_Contest_of_Champions)
- **Shadow Fight 3**: joystick at bottom left, punch and kick buttons on the right, direction-plus-button combos, and a dedicated shadow-ability button. These come from secondary guides — [BlueStacks SF3 guide](https://www.bluestacks.com/blog/game-guides/shadow-fight-3/sf3-combat-guide-en.html)
- **Dragon Ball Legends**: virtual thumbstick, attacks by tapping attack cards, and a swipe to dodge — [Hardcore Gamer](https://hardcoregamer.com/previews/gdc-2018-everyones-saiyan-dragon-ball-legends-could-dominate-mobile-combat/294416/); [GamesBeat](https://gamesbeat.com/dragon-ball-legends-launches-as-no-1-free-game-on-apple-app-store/)
- **Tekken Mobile**: combat and controls were designed for touchscreens. The 9-card "Waza Card" deck picks attacks by card color. Reviewers call the scheme simple and responsive, with less precision — [Wikipedia](https://en.wikipedia.org/wiki/Tekken_Mobile); [PPE.pl](https://www.ppe.pl/gry/Tekken-Mobile/10302); [Multiplayer.it](https://multiplayer.it/recensioni/195299-tekken-mobile-la-recensione-di-tekken-mobile.html)
- **Virtual buttons versus swipe**: virtual-button ports (Street Fighter, MK, KOF) "worked surprisingly well". The "swipe fighter" model (Injustice, MCOC) traded depth for touch-native input — [TouchArcade](https://toucharcade.com/?p=246470). Critics call such games "dumbified to tap, swipe" (forum opinion) — [TouchArcade forum](https://toucharcade.com/community/threads/i-dont-understand-mobile-fighters.305444/)
- A **KAIST study** found tap-only virtual controllers limiting. Its prototype showed flick and multi-touch input to be effective for touch fighting games — [KAIST DSpace](https://dspace.kaist.ac.kr/handle/10203/195736?mode=full)
- **Hybrids**:
  - Cool Clash: tap for light hits, diagonal swipes for heavy high/low hits, block and throw, and tap-hold-drag for specials — [TouchArcade](https://toucharcade.com/?p=138294)
  - HeroVersus: left virtual joystick with swipe actions on the right (pre-release press) — [GuruGamer](https://gurugamer.com/mobile-games/mobile-fighting-game-heroversus-now-in-open-beta-998-998-998-998-998-998-998-998-998-998-998-998-998-998-998-998/amp)
- **SF6 Modern controls** use a simplified four-button layout, with specials on one button plus a direction — [Wikipedia: SF6](https://en.wikipedia.org/wiki/Street_Fighter_6)

### Inferences
- A Tekken-style 3D fighter on phones probably needs a two-tier scheme. Option one: a "Modern" style with buttons plus direction and a single special button, an SF6-style accessibility layer. Option two: a classic virtual pad. Gesture swipes could serve as an alternative.
- Input buffering windows should probably be *longer* on touch than on a controller, because touch input has no tactile feedback. This is my inference; no source quantified it.

### Gaps
- No official Shadow Fight or Mortal Kombat Mobile control documentation was retrieved.
- No shipped mobile game was found that offers full Tekken-style 4-limb plus 8-direction input; Tekken Mobile used cards instead.
- No latency or input-buffer numbers for touch fighters.

---

## 6. Character creation systems in shipped fighters: how they're built

### Takeaway
Little first-party technical documentation exists for fighting-game creators. The best primary sources are:
- **Tekken 8** (Autodesk case study): masked part IDs with grayscale textures recolored in UE5, and per-combination "squeezing bones" so upper body, lower body and shoes fit across characters.
- **Epic's modular-character docs**: Leader Pose, Copy Pose and Skeletal Mesh Merge trade-offs, including that merged meshes lose morph targets.
- **Mutable** (UE5, beta since 5.5): runtime generation of meshes, materials and textures for customization.
- **UMA** (Unity, open-source): merges meshes, textures and rigs into one draw call, with "DNA" sliders.

WWE 2K documents only its user-facing logo and face-photo upload pipeline. Def Jam and Soulcalibur creator internals are undocumented publicly.

### Cited Findings
- **Tekken 8**:
  - Each costume part is assigned an ID with masks, and the final look is set by coloring grayscale textures in UE.
  - Detail maps add fine texture, and UV guidelines keep sizes constant with minimal distortion and consistent orientation.
  - Skinning used "squeezing bones" for each upper-body, lower-body and shoe combination, so outfits fit different characters without poking through. Motions were tested in UE and weights fixed in Maya.
  - Source: [Autodesk blog (Jan 2025)](https://blogs.autodesk.com/media-and-entertainment/2025/01/28/tekken-8-legacy-meets-innovation-with-the-combined-power-of-maya-and-unreal-engine/)
- **Tekken 8 customization**: a character wears either one full-body outfit or an outfit of customizable clothing, and the two can't be mixed. Items cover dozens of upper, lower, hair, hat, glasses and accessory slots. A reviewer suspects technical limits — [GGRecon](https://ggrecon.com/guides/tekken-8-customisation-character-player-avatar)
- **Unreal modular characters** (Epic docs):
  - Leader Pose: cheap on the game thread, but high render-thread cost, and draw calls are not reduced.
  - Copy Pose: allows per-part physics, but costs more on both threads.
  - Skeletal Mesh Merge: a single draw call per character (50 characters × 3 parts drops from 150 to 50 draw calls), but morph targets are not supported directly. A workaround uses `FMorphTargetDelta`.
  - Source: [Epic docs](https://dev.epicgames.com/documentation/en-us/unreal-engine/working-with-modular-characters-in-unreal-engine)
- **Mutable** (UE plugin): generates dynamic skeletal meshes, materials and textures at runtime for character customization. It was experimental from UE 5.1 and became beta in 5.5. Epic claims lower memory, shader cost and draw calls. A free sample on Fab covers clothing, hair, makeup, tattoos and stickers — [Epic news](https://www.unrealengine.com/news/the-mutable-sample-project-is-now-available); [80.lv](https://80.lv/articles/epic-games-released-ue5-5-mutable-plug-in-sample-project)
- **UMA** (Unity Multipurpose Avatar): builds characters from "recipes" with DNA (body sliders) and wardrobe slots. It combines meshes, textures and rigs "for the fastest rendering possible". The project was last pushed in April 2026 — [GitTrend UMA](https://gittrend.io/repo/umasteeringgroup/UMA); [Asset Store](https://assetstore-fallback.unity.com/packages/3d/characters/uma-2-35611); [GameDev Academy tutorial](https://gamedevacademy.org/unity-multipurpose-avatar-tutorial/)
- **General creator techniques**:
  - Most creators are "based around morph targets", with sliders blending between meshes; some bake the final mesh instead of blending at runtime — [Polycount](https://polycount.com/discussion/144702/character-creator-and-animations)
  - A GDC 2011 talk, "Ultimate Customization in Character Creation" by Brad Stokan of Cryptic, exists, but its content was not viewed **[older]**.
  - A Game Developer article lists customization modifiers (mesh merging, morphing, color and normal-map effects). It stresses build time and memory limits, and notes how hard the system is to change once built — [Game Developer](https://www.gamedeveloper.com/programming/on-character-customization-part-0-)
- **WWE 2K logos and faces**:
  - WWE 2K16: the companion app uploads face photos, with tokens valid for 20 minutes — [GamesBeat](https://gamesbeat.com/?p=113502)
  - WWE 2K17: a Logo Manager token, and uploads in .jpg, .png or .tga, used on clothing, videos and the ring center — [Player.One](https://www.player.one/wwe-2k17-creation-suite-generate-logo-token-start-uploading-custom-images-562307)
  - WWE 2K22: images come in through the Image Manager's "Incoming" tab, and face photos are applied as a texture layer — [Prima Games](https://primagames.com/gaming/wwe-2k22-caw-create-a-superstar-guide); [WIN.gg via Nordot](https://nordot.app/875393587548176384)
  - WWE 2K23 added 600+ new Create-A-Superstar parts — [SportsGamersOnline](https://www.sportsgamersonline.com/games/wrestling/wwe-2k23-bulks-up-creation-suite/amp/)
- **Soulcalibur VI** (UE4): Create-A-Soul returned. Players report clipping "largely unchanged from 5", fewer items, gender-locked items, a waist slider, muscle definition and wrinkle makeup — [Destructoid](https://destructoid.com/expect-guest-characters-and-creator-mode-in-soulcalibur-vi); [Steam thread](https://steamcommunity.com/app/544750/discussions/0/1735468061766478818)
- **Street Fighter 6** World Tour has an avatar creator with "a ridiculous number of body, eye, hair, nose, and voice options" (PCMag via Wikipedia) — [Wikipedia: SF6](https://en.wikipedia.org/wiki/Street_Fighter_6)
- **DOA physics** was user-tunable jiggle physics in the Soft Engine, scaled back in DOA6's new engine — [Siliconera](https://www.siliconera.com/2018/08/27/dead-or-alive-6-producer-on-whether-the-new-engine-will-have-proper-jiggle-physics/)

### Inferences
- The shared-skeleton, modular-mesh pattern is the common denominator: one fighter skeleton, swappable upper, lower, shoes, hair and accessory meshes, and mask- or ID-based recoloring of grayscale textures. Tekken 8 and UMA both use it, and Unreal's own docs describe it. It ports to Godot: a Skeleton3D with multiple MeshInstance3D skins plus shader-based mask recoloring. But Godot has no first-party equivalent of Mutable or UMA for runtime mesh merging, so on mobile, where draw calls matter, that would be custom work.
- **Logo projection**: decals or texture-layer compositing would work for user logos. WWE's pipeline uploads images to a texture layer, not a projected decal.
- Tekken 8's "squeezing bones" per outfit combination suggest Bandai Namco solved clipping with skinning, not runtime cloth. That approach is cheaper and more mobile-friendly than physics cloth.

### Gaps
- No GDC talk or postmortem was found on the internals of WWE 2K CAW (morph system, part layering), Def Jam's creator, or Soulcalibur's Create-A-Soul.
- The Unreal Engine spotlight on Soulcalibur VI returned 403.
- No primary source documents Tekken 8's runtime layering or slot system beyond the Autodesk case study.
- Mutable's and UMA's mobile support and performance were not confirmed by sources.
