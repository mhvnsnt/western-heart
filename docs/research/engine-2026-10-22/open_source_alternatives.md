# Open-source / source-available alternatives to Godot 4.7 for Western Heart (native mobile 3D fighter + deep character creation), state as of 22 Oct 2026

Scope: Cocos Creator 3.8 and COCOS 4, Stride, O3DE, Bevy 0.19/0.20, Defold, Flax Engine, Fyrox, plus 2026 newcomers (BRUTAL, Carbon, Babylon Native). Each key question lists the engines in the same order: **Cocos Creator 3.8 / COCOS 4 / Stride / O3DE / Bevy / Defold / Flax / Fyrox / Newcomers**.

Constraints the coordinator added on 2026-10-22, applied throughout: (a) distribution is a **direct, sideloaded APK** (no app store at first), so the questions are whether each engine can produce a *signed* APK headlessly and what licence text must ship with it; (b) what each engine costs a small team once the game sells; (c) the roster is **50+ distinct fighters (59 roster entries)**, not 36.

Tags: **[older]** means the source predates 2026. **[unverified]** means a single secondary source or a search snippet only. **[conflict]** means sources disagree.

Research limits: the GitHub REST API (`gh api`) was blocked for these repos in this session, so GitHub facts come from WebFetch of the public pages. A tool session limit also interrupted the work midway. Some official doc pages returned 404 or only navigation text; those cases are listed under Gaps.

---

## 1. License, governance, release cadence/stability, current version (Oct 2026)

### Takeaway
Every candidate except Flax is free of royalties. Cocos (3.8 and COCOS 4), Stride and Fyrox use MIT; Bevy uses MIT/Apache-2.0; O3DE ships Apache-2.0 and MIT licence files; Defold uses its own Apache-derived licence. Flax is source-available and charges 4% of quarterly earnings above $250k. On stability, the engines split into two groups. Fast-breaking: Bevy (0.x with breaking releases about every 3 months) and COCOS 4 (fresh MIT fork, editor in alpha). Steadier: Cocos Creator 3.8 LTS, Defold, Flax, O3DE (two majors a year) and Stride (4.4 just shipped with many breaking changes).

### Cited Findings
**Cocos Creator 3.8 (the legacy all-in-one editor, still the production line)**
- The `cocos/cocos-engine` repo shows an MIT licence badge, describes itself as "a free, open-source, cross-platform game engine", and its newest tag is **v3.8.9** (no date shown on the page). — [GitHub cocos/cocos-engine](https://github.com/cocos/cocos-engine)
- 3.8.8 was released 16 Dec 2025 **[unverified, download-mirror site]**. — [FileHorse old versions](https://mac.filehorse.com/download-cocos-creator/old-versions/)
- 3.8 is an LTS line. It was released 2 Aug (2023) and added an AOT optimisation option **[older]**. — [Huawei Central](https://huaweicentral.com/cocos-creator-3-8-lts-brings-open-source-harmonyos-4-platform-support)
- The 3.8.6 official release (April 2025) brought package-size optimisation, Box2D native C++, HarmonyOS NEXT performance and other changes **[older]**. — [Cocos blog 3.8.6](https://www.cocos.com/en/post/f539c7888e620701228458d6b89b80c7)
- The official FAQ says Cocos Creator is free with no royalty fees and that "all money you make with the game stays with you". — [Cocos FAQ](https://www.cocos.com/en/10-common-faqs-on-cocos-creator)

**COCOS 4 (open-sourced January 2026)**
- SUD, a Chinese gamification company, bought Cocos for about $72M in November 2025. On 5 Jan 2026 COCOS 4 was announced as fully open source under standard MIT, with "all commercial-related clauses originally included in Cocos Creator" removed. — [It's FOSS](https://itsfoss.com/news/cocos-4-game-engine/); [PR Newswire](https://www.prnewswire.com/news-releases/cocos-4-is-here-fully-open-source-302652264.html)
- Engine and editor are now separate products. "COCOS" is the engine only; the editor is a separate IDE called **PinK**, and the headless tooling is **cocos-cli**. — [DEV Community analysis](https://dev.to/pht1991/cocos-4-is-open-source-but-is-it-time-to-leave-cocos-creator-38-577m); [It's FOSS](https://itsfoss.com/news/cocos-4-game-engine/)
- COCOS 4 follows SemVer with a minimum six-month deprecate-to-remove window. 3.x projects will not migrate for free because of API cleanup. PinK is an alpha available only behind activation codes. The author still treats 3.8 as the stable choice for production. — [DEV Community](https://dev.to/pht1991/cocos-4-is-open-source-but-is-it-time-to-leave-cocos-creator-38-577m)
- The repo `cocos/cocos4` is MIT, with a C++ core and TypeScript scripting. The current tag/default branch is **v4.0.0**, the Releases section is empty, and the page shows about 1.5k stars and 22,545 commits. — [GitHub cocos/cocos4](https://github.com/cocos/cocos4)
- cocos-cli **0.0.1-alpha.44** was published 19 Oct 2026 and includes a breaking change to preview play/pause/step. PRs #954 and #990 were merged 16 Oct 2026 to extract a private PinK scene-editor runtime from the CLI, and #954 warns against releasing to existing PinK installs **[unverified, from search snippets of the PR pages]**. — [cocos-cli release alpha.44](https://github.com/cocos/cocos-cli/releases/tag/0.0.1-alpha.44); [PR #954](https://github.com/cocos/cocos-cli/pull/954); [PR #990](https://github.com/cocos/cocos-cli/pull/990)

**Stride**
- Licence is MIT ("unless stated otherwise" for copied third-party files). Copyright is "© .NET Foundation and Contributors" and funding comes through Open Collective. The repo has about 7.9k stars. — [GitHub stride3d/stride](https://github.com/stride3d/stride); [Stride blog](https://www.stride3d.net/blog/announcing-stride-4-4/)
- **Current version: 4.4.0 (9 Oct 2026), then 4.4.1 (17 Oct 2026, more than 200 fixes).** 4.4 contains about 3,200 commits since the previous version. — [Stride release notes (latest)](https://doc.stride3d.net/latest/en/releasenotes/); [Stride blog index](https://www.stride3d.net/blog/)
- 4.4 has heavy breaking changes: a rewritten SDSL shader compiler, D3D12 now requires Enhanced Barriers, a reworked Bepu character controller, removed Game Settings overrides, dropped 32-bit, and **OpenGL and OpenGL ES removed**. — [Stride 4.4 release notes](https://doc.stride3d.net/latest/en/releasenotes/); [Announcing Stride 4.4](https://www.stride3d.net/blog/announcing-stride-4-4/)
- 4.3 shipped 14 Nov 2025 with .NET 10 / C# 14 and Bepu physics (Bullet still the default). — [Stride 4.3 release notes](https://doc.stride3d.net/4.3/en/ReleaseNotes/); [Wikipedia](https://en.wikipedia.org/wiki/Stride_(game_engine))
- **[conflict]** Wikipedia still lists 4.3 as stable, and GameDev.net reported 4.4.0-beta8 on 19 Sep 2026. The official docs and blog show 4.4.0 final on 9 Oct. — [GameDev.net](https://gamedev.net/news/stride-samples440-released-r5904/)

**O3DE (Open 3D Engine)**
- The repo describes itself as "Apache 2.0-licensed" and ships both `LICENSE_APACHE2.TXT` and `LICENSE_MIT.TXT`. It has about 9.8k stars. — [GitHub o3de/o3de](https://github.com/o3de/o3de)
- Governance sits with the Open 3D Foundation under the Linux Foundation. The project keeps a "predictable release cadence" of two majors a year, and 26.5.0 and 26.10.0 are planned for 2026. Downloads grew 87.82% in 2025 over 2024. — [O3DE 2025 in review](https://o3de.org/o3de-2025-in-review-and-a-look-into-2026/)
- **Current version: 26.05.0 (27 May 2026).** It added an experimental native particle system, AgX / PBR Neutral tonemapping, and auto-LOD for FBX imports. — [CG Channel](https://www.cgchannel.com/?p=176448); [O3DE release notes index](https://www.docs.o3de.org/docs/release-notes/)
- As of 22 Oct 2026 I found no announcement of 26.10. The only trace is a Fedora COPR page preparing an `/opt/O3DE/26.10.0/` path. For comparison, 25.10 was announced 21 Oct 2025. — [Fedora COPR](https://copr.fedorainfracloud.org/coprs/hellaenergy/o3de-stabilization/)

**Bevy**
- Dual-licensed MIT or Apache-2.0. The README says it is "still in the early stages of development" and ships breaking releases "approximately once every 3 months" with migration guides. It has about 49.2k stars. — [GitHub bevyengine/bevy](https://github.com/bevyengine/bevy)
- **Current version: 0.20 (8 Oct 2026).** Earlier releases: 0.19 on 19 Jun 2026, 0.18 on 13 Jan 2026, 0.17 on 30 Sep 2025. — [Bevy news index](https://bevy.org/news/)
- A 0.19.1 patch shipped. — [GameDev.net](https://gamedev.net/news/5064-bevy-engine-v0191-released/)
- **[conflict]** One indie guide claims 0.18 shipped in March 2026; the official news page says 13 Jan 2026. — [StraySpark guide](https://www.strayspark.studio/blog/bevy-rust-game-engine-2026-indie-guide)
- 0.20 merged 817 PRs from about 226–227 contributors (the post gives both numbers). — [Bevy 0.20](https://bevy.org/news/bevy-0-20/)

**Defold**
- Licence is "The Defold License, Version 1.0", derived from Apache 2.0 and royalty-free. You may sell games, but you may not commercialise the editor or engine "as a Game Engine Product". You must include the Defold licence and copyright notice somewhere: a credits screen, a licence popup, the startup log, a text file, or a manual. The Foundation states it will never request royalties or move to subscriptions. — [Defold License](https://defold.com/license/)
- The Defold Foundation runs the project. 1.11.0 shipped 8 Sep 2025 and 1.13.0 on 29 Jun 2026 (the blog announced it 22 Jun). 1.13.1 then added Light components and more editor scripting. — [Defold forum 1.13.0](https://forum.defold.com/t/defold-1-13-0-has-been-released/82980); [Defold blog](https://defold.com/blog?tag=blog)
- **Current version: 1.14.0 stable, released 12 Oct (2026).** The GitHub releases page omits years; the footer shows 2026. — [GitHub defold releases](https://github.com/defold/defold/releases)
- One report says 1.14.0 added official Xbox support **[unverified, single secondary source]**. — [ifeng tech](https://tech.ifeng.com/c/8xDH6f8B7cZ)
- 1.13.0 had breaking changes: Collada removed, `js-web` removed, default winding order changed to CCW, and automatic model re-centering removed. — [Defold forum 1.13.0](https://forum.defold.com/t/defold-1-13-0-has-been-released/82980)

**Flax Engine**
- Source-available, not OSI open source. Shipped games pay **4% of earnings above $250,000 per calendar quarter**. Users must accept the Flax EULA; custom licences exist for other industries. Full source is on GitHub. — [Flax licensing](https://flaxengine.com/licensing/)
- **Current version: 1.13 (blog 21 Oct 2026; GitHub tag 1.13.7012).** It has 999+ commits and 130 merged PRs. Earlier: 1.12 around April–May 2026 (GitHub 1.12.6912 on 18 May) and 1.11 around October 2025. — [Flax 1.13 released](https://flaxengine.com/blog/flax-1-13-released/); [Flax blog](https://flaxengine.com/blog/); [GitHub releases](https://github.com/FlaxEngine/FlaxEngine/releases)
- Published roadmap: 1.14 in Q1 2027 (new editor style, UI/input/scripting, branching for 2.0), 1.15 in Q3 2027 (bug fixes), and 2.0 in late 2027 with backward compatibility as a goal. — [Flax 1.13 released](https://flaxengine.com/blog/flax-1-13-released/)
- Development also happens on a self-hosted git server at git.flaxengine.com. — [git.flaxengine.com](https://git.flaxengine.com/Flax/FlaxEngine)

**Fyrox**
- MIT licence, written in Rust, about 9.6k stars. Funding comes from Patreon/Boosty and a JetBrains OSS licence. The README states no AI or LLM was used in development. — [GitHub FyroxEngine/Fyrox](https://github.com/FyroxEngine/Fyrox)
- **Current version: 1.0.x.** 1.0.0 is the "first stable release" after 7 years; the blog dates it 24 Mar 2026 while the GitHub release list shows 29 Mar **[conflict, minor]**. docs.rs lists 1.0.1. Release candidates came in Oct 2025 and Feb 2026. — [Fyrox 1.0.0 blog](https://fyrox.rs/blog/post/fyrox-game-engine-1-0-0/); [GitHub releases](https://github.com/FyroxEngine/Fyrox/releases); [docs.rs fyrox](https://docs.rs/crate/fyrox/latest)
- The 1.0 announcement itself warns that the team is small with little funding and that bugs may remain. — [Fyrox 1.0.0 blog](https://fyrox.rs/blog/post/fyrox-game-engine-1-0-0/)

**Newcomers**
- **BRUTAL** (Ahwoo / RocketWerkz, Dean Hall) was open-sourced 15 Oct 2026. It is a C# framework used by Kitten Space Agency and RimWorld's Waylith engine. Its founder says it is "a framework, not a game engine". The licence is a modified MIT that requires attribution, with no royalties. — [GameFromScratch](https://gamefromscratch.com/brutal-c-game-framework-now-free/); [gaming.net](https://www.gaming.net/brutal-game-framework-released-as-open-source-free-for-commercial-use/); [DevOps.com](https://devops.com/dean-hall-open-sources-brutal-to-give-game-studios-a-way-out-of-engine-lock-in)
- **Carbon** (the EVE Online engine; Fenris Creations, formerly CCP) had its source made public 1 Jul 2026. Its modules include Trinity (graphics) and Destiny (physics/pathfinding), and it is built for persistent online worlds. The coverage I read names no licence. — [GamingOnLinux](https://www.gamingonlinux.com/2026/07/carbon-engine-framework-powering-eve-online-is-now-open-source/); [Game Developer press release](https://www.gamedeveloper.com/press-release/fenris-creations-opens-carbon-engine-to-the-world); [OpenSourceForU](https://www.opensourceforu.com/2026/07/fenris-creations-carbon-game-engine-goes-open-source-on-github/)
- **Babylon Native / Babylon React Native** has no stable release. Babylon React Native describes itself as "in the early phase of its development" (Android/iOS, with Windows experimental) and lags several React Native versions. — [Babylon forum status thread](https://forum.babylonjs.com/t/react-native-babylonjs-what-is-the-current-status/58315/3); [BabylonReactNative summary](https://gittrend.io/repo/BabylonJS/BabylonReactNative); [Babylon forum release-date thread [older]](https://forum.babylonjs.com/t/will-the-babylon-native-have-a-release-date/16138)

### Inferences
- **Stability ranking for a multi-year, 59-entry fighter**, most stable first: Defold and Cocos Creator 3.8 LTS (both mature and incremental) > Flax and O3DE (scheduled majors) > Stride (stable licence, but 4.4 just broke a lot and the editor port is in progress) > Fyrox (1.0 only seven months old, tiny team) > Bevy (breaking every ~3 months, editor still unreleased) ≈ COCOS 4 (engine v4.0.0, CLI at alpha.44, editor in gated alpha).
- **COCOS 4 vs 3.8:** the MIT relicensing removes the commercial clauses, but the production toolchain today is still 3.8. Choosing COCOS 4 now means building on an alpha CLI and an unreleased editor.
- **Flax** is the only candidate with a revenue share. At 4% above $250k per quarter, it costs nothing until a quarter's earnings exceed $250k.

### Gaps
- I could not read the actual LICENSE text of `cocos-engine` 3.8 or the Cocos Creator **editor binary EULA**, which may carry terms separate from the MIT engine source. The FAQ says no royalties, but splash or attribution rules are unconfirmed.
- Carbon's licence is unconfirmed; the coverage I read doesn't name it.
- The exact wording of BRUTAL's "modified MIT" attribution clause was not retrieved.
- I found no official O3DE 26.10 release as of 22 Oct 2026. It may be imminent.

---

## 2. Native mobile 3D: Android/iOS export maturity, renderer, mid-range Android performance, shipped mobile 3D games

### Takeaway
Cocos Creator 3.8 has by far the deepest record of shipped mobile titles, including 3D. Its renderer uses Vulkan on Android (GLES fallback per Cocos docs, not verified here) and Metal on iOS. Defold is mobile-first and now defaults to Vulkan on Android, but its 3D feature set is thin. O3DE has a dedicated mobile pipeline and one studio talk about shipping a mobile game, but iOS is still marked experimental. Flax supports Android (Vulkan) and iOS with a desktop-class feature set. Bevy, Fyrox and Stride all run on mobile, but there is little evidence of shipped 3D mobile games. Stride 4.4 removed OpenGL ES, so Android now needs Vulkan. The newcomers (BRUTAL, Carbon, Babylon Native) are not viable mobile engines today.

### Cited Findings
**Cocos Creator 3.8**
- Targets: Windows, Mac, iOS, Android, HarmonyOS, Web, Facebook Instant Games, WeChat, and TikTok mini-games. The GFX layer "uses Vulkan on Windows and Android, Metal on Mac OS and iOS, and WebGL on Web". — [GitHub cocos-engine](https://github.com/cocos/cocos-engine)
- Shipped 3D: Tencent's "The Strongest Demon Fighter" is a WeChat title on Cocos Creator 3D with 3D characters on 2D scenes (an auto-shooter, not a fighter). — [Cocos blog](https://www.cocos.com/en/post/ec7ef75f2cd16ee29bc709fd3c655e1e)
- Official samples include instanced-skinning (GPU instancing for "massive skinning models"), a knight animation scene, and pre-integrated SSS skin. — [example-3d](https://github.com/linshunjun/example-3d)
- One forum report shows a 3.8.0 Android native CMake build failing in Android Studio **[older; anecdotal]**. — [Cocos forum](https://forum.cocos.org/t/topic/160529)

**COCOS 4**
- Android, iOS, web, Windows and macOS are listed, with Vulkan on Windows/Android, Metal on macOS/iOS and WebGL on web. — [GitHub cocos4](https://github.com/cocos/cocos4)
- Native platforms are "covered broadly". WeChat mini-game support is rolling out gradually, and Steam-class native targets are on the roadmap. — [DEV Community](https://dev.to/pht1991/cocos-4-is-open-source-but-is-it-time-to-leave-cocos-creator-38-577m)

**Stride**
- In 4.4, "All platforms have been brought back into shape". The announcement shows "A Stride sample running on a physical iPhone", but the release notes never mention Android specifically. — [Stride 4.4 release notes](https://doc.stride3d.net/latest/en/releasenotes/); [Announcing Stride 4.4](https://www.stride3d.net/blog/announcing-stride-4-4/)
- "OpenGL and OpenGLES have been removed". Vulkan moved to 1.3, which the notes warn "might break support for older devices and users with outdated drivers". Metal is reached via SPIRV-Cross. — [Announcing Stride 4.4](https://www.stride3d.net/blog/announcing-stride-4-4/); [Release notes](https://doc.stride3d.net/latest/en/releasenotes/)
- NuGet metadata for 4.4.0-beta2 lists `net10.0-android36.0` and `net10.0-ios26.0` targets **[unverified, metadata signal only]**. — [NuGet 4.4.0-beta2](https://www.nuget.org/packages/Stride.Core.MicroThreading/4.4.0-beta2)
- The 4.3 requirements page still lists Xamarin for Android and iOS, so the docs are outdated. — [Stride 4.3 requirements](https://doc.stride3d.net/4.3/en/manual/install-and-update/requirements.html)
- The repo shows build badges for Windows, Linux and iOS, but no Android badge. — [GitHub stride](https://github.com/stride3d/stride)
- Best-known shipped title: Distant Worlds 2, a PC strategy game, not mobile. — [Stride blog](https://www.stride3d.net/blog/)

**O3DE**
- Targets Windows, Linux and Android; macOS and **iOS are experimental** (per Wikipedia). — [Wikipedia O3DE](https://en.wikipedia.org/wiki/Open_3D_Engine)
- 24.09 introduced a dedicated mobile rendering pipeline, claimed up to 400% faster on mobile, and a Project Export UI with full export for iOS and Android. — [Linux Foundation press release](https://www.linuxfoundation.org/press/open-3d-foundation-announces-the-launch-of-the-open-3d-engine-24.09.0-release)
- In 2025, contributors improved "compatibility, performance, and stability for iOS, Android". 25.10.1 added the latest Android SDK (AGP 8.13). — [O3DE 2025 look-back](https://o3de.org/a-look-back-at-2025-and-what-to-look-forward-to-in-2026/); [25.10.1 release notes](https://docs.o3de.org/docs/release-notes/archive/2510-1-release-notes/)
- Shipped mobile: Carbonated Inc. (CEO Travis Boatman, CTO Lloyd Tullues) gave the talk "Lessons Learned Shipping a Mobile Game With O3DE" on 19 Nov 2025. Their CTO called O3DE's render pipeline "a godsend". — [O3DE event page](https://o3de.org/lessons-learned-shipping-a-mobile-game-with-o3de/)

**Bevy**
- Android builds use `cargo-ndk` plus Gradle with GameActivity (minSdk 26, targetSdk 37); NativeActivity is possible for older APIs. iOS builds use Xcode/`make run` for device and simulator. — [Bevy examples README](https://github.com/bevyengine/bevy/blob/main/examples/README.md)
- The renderer is wgpu, so Vulkan or GLES on Android and Metal on iOS depending on device (backend mapping not quoted in the sources I read). 0.19 added partial bindless on Metal and a `RenderErrorHandler` for device-loss recovery. — [Bevy 0.19](https://bevy.org/news/bevy-0-19/)
- 0.20 added ASTC output in the texture-compression backend, which matters for mobile textures. — [Bevy 0.20](https://bevy.org/news/bevy-0-20/)
- History: initial Android support came in 0.3 (2020). The first Bevy iOS App Store app was Noumenal in June 2022 **[older]**. — [Bevy 0.3](https://bevy.org/news/bevy-0-3/); [Bevy's 2nd birthday](https://bevy.org/news/bevys-second-birthday/)
- I found no shipped 3D Bevy game on the Play Store with documented performance. — [itch.io Android+Bevy tag](https://itch.io/games/new-and-popular/platform-android/tag-bevy)

**Defold**
- 1.13.0: "Android will from now on use Vulkan as the primary graphics adapter", with OpenGL as fallback (switchable in the manifest). iOS/macOS gained GameController support. — [Defold forum 1.13.0](https://forum.defold.com/t/defold-1-13-0-has-been-released/82980)
- Size: dead-stripping cut about 354 KB (about 7.7%) from the Android engine. One user reported an empty-project release APK growing from about 3.5 MB to 6.8 MB **[anecdotal]**. — [Defold forum 1.13.0](https://forum.defold.com/t/defold-1-13-0-has-been-released/82980)
- No shipped 3D mobile fighter found. Defold's mobile track record is mostly 2D (no source found listing 3D mobile hits).

**Flax**
- Platforms: Windows, Xbox One/Series, PS4/PS5, Linux, Android, Switch, macOS, iOS, Web. Backends: DX11/DX12, Vulkan, WebGPU. — [Flax platforms](https://docs.flaxengine.com/manual/platforms/index.html)
- Android uses Vulkan (minimum 1.0) and needs API level 24 / Android 7+. — [Flax Android docs](https://docs.flaxengine.com/manual/platforms/android.html)
- Android work by release:
  - 1.8: ASTC support and Android orientation settings.
  - 1.10: AAB bundling and Android device deploy/log tools.
  - 1.11: 16 KB page-size support.
  - 1.12: NDK 27 and "preloading reduction" on Android/iOS.
  - 1.13: Android builds from macOS.
  — [GitHub Flax releases](https://github.com/FlaxEngine/FlaxEngine/releases)
- 1.13 adds hardware instancing for animated models (5,000 animated characters at 60 fps on an RTX 2080 Ti, a desktop GPU) and occlusion culling. — [Flax 1.13](https://flaxengine.com/blog/flax-1-13-released/)
- I found no shipped Flax mobile 3D game. The 1.13 post features *Homeostasis* (a Steam game). — [Flax 1.13](https://flaxengine.com/blog/flax-1-13-released/)

**Fyrox**
- 1.0's export-cli targets `pc`, `android` and `wasm`. Android has 32- and 64-bit build targets and is cross-compiled from desktop. The book's Shipping chapter covers PC, WebAssembly, Android and CI/CD, with **no iOS chapter**. — [Fyrox 1.0.0](https://fyrox.rs/blog/post/fyrox-game-engine-1-0-0/); [Fyrox book SUMMARY](https://github.com/fyrox-book/fyrox-book.github.io/blob/main/src/SUMMARY.md)
- **[conflict]** A search snippet says the Fyrox site lists Android and iOS, but the fetched page and the book show no iOS path. — [fyrox.rs](https://fyrox.rs)
- **[older]** The original Android port needed OpenGL ES 3.0 (2015+ devices), and the dev blog said the PC-oriented renderer made complex 3D "quite bad" on mobile, with a lightweight mobile renderer planned. — [This Week in Fyrox #17](https://fyrox.rs/blog/post/twif17)
- 1.0-rc.1 isolated OpenGL into a separate crate "to prepare for modern graphics APIs". The repo now contains `fyrox-graphics-gl` and `fyrox-graphics-wgpu` crates. — [Fyrox 1.0 rc.1](https://fyrox.rs/blog/post/fyrox-game-engine-1-0-0-rc-1/); [GitHub Fyrox](https://github.com/FyroxEngine/Fyrox)

**Newcomers**
- **BRUTAL**: Vulkan-based. One source lists Windows, Linux and macOS only, and I found no confirmed iOS or Android support. — [GameFromScratch](https://gamefromscratch.com/brutal-c-game-framework-now-free/); [Kitten Space Agency wiki](https://kittenspaceagency.wiki.gg/wiki/BRUTAL)
- **Carbon**: described only as "cross-platform", with no mobile mentioned. — [GamingOnLinux](https://www.gamingonlinux.com/2026/07/carbon-engine-framework-powering-eve-online-is-now-open-source/)
- **Babylon React Native**: Android/iOS only, early phase. — [Babylon forum](https://forum.babylonjs.com/t/react-native-babylonjs-what-is-the-current-status/58315/3)

### Inferences
- For a **sideloaded APK on mid-range Android**, Cocos 3.8 and Defold have the strongest mobile-first credentials. Defold's 3D animation is too thin for a fighter (see §3). O3DE's mobile pipeline exists but has one public studio case. Flax's per-frame cost on mid-range phones is unknown: its marketing numbers come from desktop GPUs.
- Stride 4.4 is now Vulkan-1.3-only on Android, which excludes older or low-end devices whose drivers lack Vulkan 1.3. That is a real risk for a sideloaded APK sent to arbitrary phones.
- Fyrox's mobile 3D story is not proven for a 3D fighter, and iOS is undocumented.

### Gaps
- I found no independent mid-range Android benchmarks (fps or thermals on, say, a Snapdragon 6-series or Helio G-series phone) for any of these engines in 2025–2026.
- Cocos 3.8's GLES3 fallback on Android is not confirmed in the sources fetched; the README mentions only Vulkan.
- I could not retrieve O3DE's official supported-platforms page (404) or the content of the Carbonated talk.

---

## 3. Skeletal animation and character customization: skinning, blend trees/state machines, IK, runtime retargeting, physics bones/springs, blend shapes, runtime glTF, bone attachments, decals on skinned meshes

### Takeaway
O3DE (EMotion FX) and Flax (Anim Graph) have the most complete built-in animation suites. Both offer state machines, blend spaces, IK, retargeting, morph targets and physics-driven bones (O3DE "simulated objects", Flax "Spring Bone Physics"). Cocos 3.8 Marionette offers state machines, layers, masks, and an *experimental* pose graph with two-bone IK. Bevy has a blend-graph core with masks, additive blending and morph targets, but no built-in state machine, IK or retargeting (third-party crates only). Fyrox has a state machine (ABSM), blend spaces, root motion, blend shapes and ragdoll. Stride's blend trees are code-only and it has no morph targets yet (work in progress). Defold can only play one baked clip at a time, with no blending graph or IK.

### Cited Findings
**Cocos Creator 3.8**
- Skinning: there is a `SkinnedMeshRenderer`, plus a `SkinnedMeshBatchRenderer` that batches sub-skinned models under one skeletal animation component. — [Cocos 3.0 mesh docs [older]](https://docs.cocos.com/creator/3.0/manual/en/module-map/mesh/)
- **Marionette** (introduced in 3.5) controls skeletal animation via state machines, using Animation Graph assets, layers, masks, graph variants and state transitions. States must use skeletal clips imported from `.fbx`, `.gltf` or `.glb`. — [Cocos 3.8 Marionette](https://docs.cocos.com/creator/3.8/manual/en/animation/marionette/)
- **Procedural animation / pose graph** is "experimental… use it with caution" and is enabled through the Laboratory settings. It supports additive animation, auxiliary curves and pose stash. — [Cocos 3.8 procedural animation](https://docs.cocos.com/creator/3.8/manual/en/animation/marionette/procedural-animation/)
- The pose graph's modify nodes are Apply Transform, Copy Transform, Set Auxiliary Curves, and **Double Skeleton IK (two-bone IK solver with pole target)**. No aim or look-at IK node is listed. — [Cocos 3.8 Modify Poses](https://docs.cocos.com/creator/3.8/manual/en/animation/marionette/procedural-animation/pose-graph/pose-nodes/modify-pose.html)
- The official sample list includes "Marionette Animation Examples" (state machines, pose graphs, events, IK) and a material sample with skin, hair and eyeball shaders. — [Cocos cases & tutorials](https://docs.cocos.com/creator/manual/en/cases-and-tutorials/)
- The example-3d repo demonstrates GPU-instanced skinning for crowds. — [example-3d](https://github.com/linshunjun/example-3d)

**COCOS 4**
- It is an evolution of the 3.x engine, so it presumably keeps Marionette, but API cleanup means 3.x projects won't port for free. — [DEV Community](https://dev.to/pht1991/cocos-4-is-open-source-but-is-it-time-to-leave-cocos-creator-38-577m)

**Stride**
- Animation uses skeleton + skinned model + clip assets. Game Studio "can't visualize skeletons". The docs have pages for additive animation, procedural animation, custom blend trees and **model node links** (bone attachment). — [Stride animation manual](https://doc.stride3d.net/latest/en/manual/animation/index.html)
- **Blend trees are code-only.** You implement `IBlendTreeBuilder` and push and blend clips on a stack each frame. The docs mention no visual editor, state machine or IK. — [Stride custom blend trees](https://doc.stride3d.net/latest/en/manual/animation/custom-blend-trees.html)
- **Morph targets are not shipped.** Issue #339 is open (roadmap "Todo"), the assignee posted a progress video on 8 Oct 2026, and the Open Collective bounty is $800. — [GitHub issue #339](https://github.com/stride3d/stride/issues/339); [Open Collective bounty](https://opencollective.com/stride3d/projects/morph-targets)

**O3DE (EMotion FX)**
- The documentation covers:
  - Anim graphs with state machines and blend trees (Blend N, Blend Two, Blend Two Additive, Pose Subtract).
  - **Blend spaces**.
  - **Ragdoll** (setup, anim-graph integration).
  - **Simulated objects**: physics-driven secondary motion with colliders and an anim-graph node.
  - **Morph targets** ("Using Morph Targets to Deform Characters").
  - **Retargeting Motions**.
  - **Multiple skin attachments**.
  - Actor LODs, cloth colliders, motion events and root motion.
  — [O3DE animation docs](https://www.docs.o3de.org/docs/user-guide/visualization/animation/); [EMotion FX gem](https://docs.o3de.org/docs/user-guide/gems/reference/animation/emotionfx/)

**Bevy**
- Built-in examples cover Animated Mesh, Animated Mesh Control, Animation Events, **Animation Graph**, **Animation Masks**, **Morph Targets** and Custom Skinned Mesh. — [Bevy examples README](https://github.com/bevyengine/bevy/blob/main/examples/README.md)
- 0.19 made skinned meshes compute bounds from actual joint positions, so animated characters aren't culled by rest pose. It also batched morph-target rendering (roughly 2x in one example). Neither 0.19 nor 0.20 mentions blend trees, state machines, IK or retargeting. — [Bevy 0.19](https://bevy.org/news/bevy-0-19/); [Bevy 0.20](https://bevy.org/news/bevy-0-20/)
- Third-party `bevy_animation_graph` adds animation graphs, **state machines**, a graphical editor and partial ragdoll. It does not mention IK or retargeting. — [bevy_animation_graph](https://github.com/mbrea-c/bevy_animation_graph)
- Runtime glTF: glTF is loaded through the asset server (a `load_gltf` example exists). Moving the glTF loader onto the new BSN scene system is listed as future work. — [Bevy examples README](https://github.com/bevyengine/bevy/blob/main/examples/README.md); [Bevy 0.19](https://bevy.org/news/bevy-0-19/)

**Defold**
- Defold "currently supports only baked skeletal animations" (one matrix per bone per keyframe) with linear interpolation. "A model component can only play one model animation at a time."
- Bones are exposed as game objects, so things can be attached to them.
- Morph-target weights can be read and set from script (`model.get_blend_weights` / `model.set_blend_weights`). Morph targets need a custom vertex shader, don't preview in the editor, and don't run on GLES2.
- The model-animation manual describes no cross-fade, blend tree, state machine or IK.
— [Defold model animation](https://defold.com/manuals/model-animation/)
- 1.13 added glTF morph targets but "an animation can drive either a skinned animation or a morph target animation, not both". — [Defold 1.13.0](https://forum.defold.com/t/defold-1-13-0-has-been-released/82980)

**Flax**
- The Anim Graph includes a State Machine and Multi Blend 1D/2D, now up to 255 points and taking custom inputs in 1.13.
- **Blend With Mask** with skeleton masks, root-motion extraction modes, anim events, and additive blending (fixes noted).
- **Two Bone IK**, with fixes in 1.8.
- **Retargeting**: Base Model preview with retargeting, and copy/paste of skeleton retargeting between models (1.10).
- **Blend shapes**: fixes noted in 1.8.
- **Spring Bone Physics** node (1.12).
- In 1.13, skinned models can be drawn from code using an Animated Model's pose.
— [GitHub Flax releases](https://github.com/FlaxEngine/FlaxEngine/releases)
- The IK docs describe Two Bone IK (adjusts the node, its parent and grandparent, with a joint target for elbow/knee direction) and Aim IK. — [Flax IK docs](https://docs.flaxengine.com/manual/animation/anim-graph/inverse-kinematics.html); [Flax forum Aim/2-bone IK](https://forum.flaxengine.com/t/aim-ik-and-2-bone-ik/388)
- 1.12 headlines included jiggle physics (spring bones). — [GameDev.net Flax 1.12](https://gamedev.net/news/3431-flax-engine-112-released/)

**Fyrox**
- The book covers the Animation Editor, Animation Blending, the **ABSM editor** (animation blending state machine), Signals and Root Motion. Physics includes **Ragdoll**. — [Fyrox book SUMMARY](https://github.com/fyrox-book/fyrox-book.github.io/blob/main/src/SUMMARY.md)
- 0.30 added a blend space editor, root motion and **blend shape** support **[older, 2023]**. — [GameFromScratch Fyrox 0.30](https://gamefromscratch.com/fyrox-rust-game-engine-0-30-release/)

**Newcomers**
- BRUTAL is a low-level library set (maths, memory, jobs, logging, localisation, interop) with no animation system mentioned. — [GameFromScratch](https://gamefromscratch.com/brutal-c-game-framework-now-free/)

### Inferences
- For a **deep character-creation suite** (sliders, outfit swaps across 59 roster entries, attachments), the deciding features are morph targets plus a skeleton shared or retargeted across bodies, bone attachments, and multiple skinned meshes on one skeleton.
  - O3DE (morph targets, retargeting, multiple skin attachments) and Flax (blend shapes, retargeting, Spring Bone, IK) cover all of this natively.
  - Cocos 3.8 covers state machines and attachments; IK is experimental.
  - Bevy covers morph targets and masks but needs third-party crates or custom code for a state machine, IK and retargeting.
  - Stride lacks morph targets today, a blocker for face and body sliders.
  - Defold's "skin OR morph per animation" and "one animation at a time" rules are blockers for a fighter (no blending, no layered upper/lower body).
- **59-entry roster:** Defold's baked per-bone matrix clips grow memory linearly with clips × bones × fighters. Engines with retargeting (O3DE, Flax) let one shared move bank drive many bodies, which matters for 59 entries.
- None of the sources I read confirms **decals on skinned meshes** for any engine (see Gaps).

### Gaps
- **Runtime glTF/GLB loading** (loading user or modded characters after build) is unconfirmed for Cocos 3.8/4, Stride, O3DE (which imports offline through the Asset Processor), Defold, Flax and Fyrox. Only Bevy's runtime asset-server loading is evidenced.
- **Decals on skinned meshes**: no source found for any engine.
- **Runtime retargeting** (as opposed to editor-time or import-time) is unconfirmed for O3DE and Flax; the docs list retargeting but I didn't verify that it works at runtime.
- I could not confirm whether O3DE EMotion FX ships two-bone or look-at IK nodes; the docs pages fetched did not list them.
- I did not reach Fyrox's IK or retargeting status.

---

## 4. UI system for touch (portrait/landscape anchoring) and multitouch gestures

### Takeaway
Cocos 3.8 has the most mobile-native UI: a Canvas with fit width/height plus Widget anchoring, an explicit large-screen/foldable guidance page, and per-touch IDs. Other engines' touch UI evidence is thinner. Bevy 0.19–0.20 added real text input, IME and new UI units but no gesture layer. Flax, Fyrox and Stride have general-purpose UI systems without documented mobile gesture handling.

### Cited Findings
**Cocos Creator 3.8**
- The Canvas plus **Widget** alignment provides multi-resolution adaptation. Fit Width and Fit Height in Project Settings work together with Widget. — [Cocos multi-resolution](https://docs.cocos.com/creator/manual/en/ui-system/components/engine/multi-resolution.html)
- For large and folding Android screens, the docs recommend setting the Widget Align Mode to `ON_WINDOW_RESIZE` or `ALWAYS`. — [Cocos 3.8 large-screen](https://docs.cocos.com/creator/3.8/manual/en/ui-system/components/engine/large-screen.html)
- Touch events (`TOUCH_START` etc.) work via `input.on` or `node.on`. `Touch.getID` identifies points for multi-touch logic (documented in 3.2). — [Cocos 3.8 touch tutorial](https://docs.cocos.com/creator/3.8/manual/en/getting-started/first-game-2d/touch.html); [Cocos 3.2 Event API [older]](https://docs.cocos.com/creator/3.2/manual/en/engine/event/event-api.html)

**COCOS 4**
- No UI-specific changes documented; it is presumably inherited from 3.x.

**Stride**
- The only UI change noted in 4.4 is that `ScrollViewer.ScrollOfInternal` became private, plus the Avalonia launcher. — [Stride 4.4 release notes](https://doc.stride3d.net/latest/en/releasenotes/)

**O3DE**
- No touch-UI source retrieved.

**Bevy**
- 0.19 added `EditableText` (IME, selection, clipboard, multiline), Feathers widgets, and text via parley. — [Bevy 0.19](https://bevy.org/news/bevy-0-19/)
- 0.20 added `Val::Em`/`Val::Rem` units, `FixedNode` (positions UI relative to the camera viewport), headless tab widgets, more Feathers widgets and contextual theming. — [Bevy 0.20](https://bevy.org/news/bevy-0-20/)
- Feathers is described as "opinionated editor-centric". — [Bevy 0.20](https://bevy.org/news/bevy-0-20/)

**Defold**
- No source retrieved this session on GUI layouts or multitouch.

**Flax**
- Android orientation settings (1.8), a changeable default screen orientation (1.7), and in 1.13 `RenderToTextureControl` can draw UI with a custom material. — [GitHub Flax releases](https://github.com/FlaxEngine/FlaxEngine/releases); [Flax 1.13](https://flaxengine.com/blog/flax-1-13-released/)

**Fyrox**
- The UI book has 33 widget pages (Button, Canvas, Dropdown, Tree, Window, …). 1.0 adds an input box, text ellipsis, tooltips and image buttons. — [Fyrox book SUMMARY](https://github.com/fyrox-book/fyrox-book.github.io/blob/main/src/SUMMARY.md); [Fyrox 1.0.0](https://fyrox.rs/blog/post/fyrox-game-engine-1-0-0/)

### Inferences
- A touch fighter needs a virtual stick and buttons with multitouch, plus a portrait-or-landscape creation suite. Cocos is the only engine here whose documented UI was designed around phone screens. Every other engine would need custom gesture code; that is feasible but is scope Godot or Cocos would not need.

### Gaps
- No sources were retrieved for multitouch gesture APIs (pinch, swipe) in Stride, O3DE (LyShine), Bevy, Defold (GUI layouts), Flax or Fyrox. This needs a follow-up if touch UI is a scoring axis.
- I could not confirm whether Cocos 3.8's multitouch API differs from 3.2's `getID`.

---

## 5. Tooling: headless CLI build of Android APK/AAB on Linux, text-based scene formats, editor availability, scripting language

### Takeaway
Best headless Linux Android pipelines:
- **Defold**: `bob.jar` (Java) builds APK or AAB with keystore flags.
- **Bevy**: `cargo-ndk` plus Gradle, pure CLI, no editor exists.
- **Fyrox**: `export-cli` crate with an `android` target, aimed at CI/CD.
- **Stride 4.4**: new `stride` CLI and `dotnet new`; Linux builds "now work the same as Windows", though Android isn't named.
- **Cocos 3.8**: CLI documented but **"still needs the GUI environment"**.
- **COCOS 4**: headless cocos-cli exists but is alpha.
- **Flax and O3DE**: Android builds documented through editor UIs or generated Gradle projects, and Linux-host Android builds are historically shaky (Flax) or unconfirmed (O3DE).

### Cited Findings
**Cocos Creator 3.8**
- Command: `CocosCreator --project <path> --build "platform=…;debug=…"`, with `stage=build|make`, `buildPath` and `configPath`. Exit codes: 32 = invalid parameters, 34 = unexpected error, 36 = success.
- "Cocos Creator still needs the GUI environment when running from the command line." The docs suggest running Jenkins in agent mode for headless servers.
- The page documents no Android keystore or AAB options.
- Scripting is TypeScript.
— [Cocos 3.8 publish in command line](https://docs.cocos.com/creator/3.8/manual/en/editor/publish/publish-in-command-line.html)
- A community skill shows `--project . --build "platform=android"` for 3.8.x **[unverified, third-party]**. — [skillsmp Cocos CLI build automation](https://skillsmp.com/creators/chrislamdev/cocos-creator-debug-skills/skills-cocos-cli-build-automation-setup)

**COCOS 4**
- Engine build: `npm install` and `npm run build` (Node.js plus gulp-cli). — [GitHub cocos4](https://github.com/cocos/cocos4)
- cocos-cli provides headless mode, and core editing functions are moving to CLI operations. — [DEV Community](https://dev.to/pht1991/cocos-4-is-open-source-but-is-it-time-to-leave-cocos-creator-38-577m); [It's FOSS](https://itsfoss.com/news/cocos-4-game-engine/)
- The latest CLI is 0.0.1-alpha.44, which includes a ZIP export of project assets **[unverified snippet]**. — [cocos-cli alpha.44](https://github.com/cocos/cocos-cli/releases/tag/0.0.1-alpha.44)

**Stride**
- New `stride` CLI commands include `stride sdk install` and `stride new topdownrpg`, plus `dotnet new stride-game -n MyGame`. "Building projects on Linux and macOS now works the same as it does on Windows." The engine is NativeAOT- and trimming-friendly. — [Stride 4.4 release notes](https://doc.stride3d.net/latest/en/releasenotes/); [Announcing Stride 4.4](https://www.stride3d.net/blog/announcing-stride-4-4/)
- The editor (Game Studio) is Windows-native, being ported from WPF to Avalonia, and runs on Linux only via Proton/Wine ("isn't as solid"). Scripting is C# on .NET 10. — [Announcing Stride 4.4](https://www.stride3d.net/blog/announcing-stride-4-4/)

**O3DE**
- Building from source needs Visual Studio 2019 16.9.2+, CMake 3.25+ and Git LFS (Windows requirements on the README). — [GitHub o3de](https://github.com/o3de/o3de)
- Android uses a "Generating Android Project" flow (a Gradle project). The doc navigation slug suggests a Windows host **[unverified]**. 25.10.1 fixed setup of Android build nodes for Automated Review on GitHub Actions. — [O3DE release notes index](https://www.docs.o3de.org/docs/release-notes/); [25.10.1 notes](https://docs.o3de.org/docs/release-notes/archive/2510-1-release-notes/)
- 24.09 added a Project Export UI with full export for iOS and Android. — [Linux Foundation press release](https://www.linuxfoundation.org/press/open-3d-foundation-announces-the-launch-of-the-open-3d-engine-24.09.0-release)

**Bevy**
- Android: `rustup target add aarch64-linux-android`, `cargo install cargo-ndk`, then `cargo ndk build -t arm64-v8a -P 26 -o …/jniLibs` followed by `./gradlew installDebug` or `./gradlew build`. Needs `ANDROID_HOME`, JDK 21 and the SDK. — [Bevy examples README](https://github.com/bevyengine/bevy/blob/main/examples/README.md)
- Scenes: BSN (Bevy Scene Notation) is available via the `bsn!` macro. Asset-based `.bsn` text files are not yet shipped (loader in progress), and 0.20 refined BSN syntax. — [Bevy 0.19](https://bevy.org/news/bevy-0-19/); [Bevy 0.20](https://bevy.org/news/bevy-0-20/)
- There is no shipped editor: an entity inspector was prototyped and the editor is being built as a Bevy app. Scripting is Rust. — [Bevy 0.19](https://bevy.org/news/bevy-0-19/)

**Defold**
- `bob.jar` is the CLI builder, downloaded from GitHub releases; Defold 1.9.6+ needs OpenJDK 21. Flags: `-bf/--bundle-format apk|aab`, `-ks` keystore, `-ksa` alias, `-ksp` keystore password, `-kp` key password. — [Defold bob manual](https://defold.com/manuals/bob)
- Without a keystore, Defold generates a debug keystore. — [Defold Android manual](https://defold.com/llms/manuals/android.md)
- Release assets include `bob.jar`, `defoldsdk.zip` and Linux builds. — [GitHub defold releases](https://github.com/defold/defold/releases)
- 1.13 lets you pass command-line args to an Android app via `adb` and adds initial on-device Android tests. Editor and bob share parallel dependency downloads. — [Defold 1.13.0](https://forum.defold.com/t/defold-1-13-0-has-been-released/82980)
- Scripting is Lua.
- **[older]** One forum user had an AAB built from the command line rejected as unsigned. — [Defold forum](https://forum.defold.com/t/i-get-the-resource-cannot-be-null-error-in-the-latest-version-of-the-engine/70503?page=2)

**Flax**
- Android builds come from the Game Cooker window, which outputs a Gradle project. The docs cover no CLI cooking or signing. — [Flax Android docs](https://docs.flaxengine.com/manual/platforms/android.html)
- 1.10 added AAB bundling; 1.13 added Android builds from **macOS**. — [GitHub Flax releases](https://github.com/FlaxEngine/FlaxEngine/releases)
- **[older]** Building Android from Linux was unsupported in the 1.5 era ("Build platform Android ARM64 is not supported"; fix promised). — [Flax forum](https://forum.flaxengine.com/t/configure-linux-to-export-apk-and-aab/928)
- The Linux editor runs on Vulkan and X11. Scripting is C# (.NET 10 as of 1.13) and C++. — [Flax Linux docs](https://docs.flaxengine.com/manual/platforms/linux.html); [Flax 1.13](https://flaxengine.com/blog/flax-1-13-released/)

**Fyrox**
- Each project includes an `export-cli` crate. Options: `--target-platform pc|android|wasm`, build target, destination (`./build/`), used-assets-only, and converting scenes and UIs to binary. It is aimed at CI/CD. — [Fyrox 1.0.0](https://fyrox.rs/blog/post/fyrox-game-engine-1-0-0/); [GameFromScratch Fyrox 1.0](https://gamefromscratch.com/after-7-years-of-development-fyrox-1-0-is-here/)
- There is a native editor plus project manager. Scripting is Rust via a `Plugin` trait. — [Fyrox 1.0.0](https://fyrox.rs/blog/post/fyrox-game-engine-1-0-0/)

**Newcomers**
- BRUTAL has "no editor, no scene graph". — [Kitten Space Agency wiki](https://kittenspaceagency.wiki.gg/wiki/BRUTAL); [GameFromScratch](https://gamefromscratch.com/brutal-c-game-framework-now-free/)

### Inferences
- **Agent and CI-friendliness on a Linux box** (this repo's agents work headless), best first: Bevy ≈ Defold ≈ Fyrox (pure CLI) > Stride 4.4 (CLI now first-class, Android path unproven) > COCOS 4 (headless by design, alpha) > Cocos 3.8 (needs a display, e.g. a virtual X server — that workaround is my inference, not documented) > Flax and O3DE (editor- or Windows-centric Android flows).
- Text-diffable scenes matter for agent edits. Bevy BSN is code-macro text today (file assets pending), and Fyrox can store scenes as text (export-cli offers "convert to binary", implying a non-binary source format; unverified). I didn't confirm Stride, Cocos, Defold or O3DE scene file formats this session.

### Gaps
- No source confirms **Cocos 3.8 Android keystore and AAB CLI parameters**, or that its CLI works under a virtual display.
- No source confirms Stride 4.4's Android build path or signing via the CLI.
- No source confirms O3DE Android builds on a Linux host.
- Flax's current Linux-host Android support is unconfirmed (only old forum evidence of it being unsupported, plus 1.13 adding macOS).
- Scene file formats (text vs binary) for Cocos, Stride, O3DE, Defold and Flax were not retrieved this session. My training data suggests Cocos `.scene`/`.prefab` JSON, Stride YAML `.sdscene`, Defold protobuf-text `.collection`/`.go`, and O3DE JSON `.prefab`, all **unverified**.

---

## 6. Web export (secondary target)

### Takeaway
Cocos (WebGL, WebGPU listed), Defold (`wasm-web` only after removing `js-web`), Bevy (WebGL2 stable, WebGPU experimental), Flax (new WebGPU web target in 1.12) and Fyrox (wasm) all export to the web. Stride and O3DE have no web target in the sources found.

### Cited Findings
- **Cocos 3.8**: WebGL on web; repo topics also list WebGL2 and WebGPU. — [GitHub cocos-engine](https://github.com/cocos/cocos-engine)
- **COCOS 4**: WebGL on web. — [GitHub cocos4](https://github.com/cocos/cocos4)
- **Stride**: no web target mentioned in the 4.4 notes. — [Stride 4.4 release notes](https://doc.stride3d.net/latest/en/releasenotes/)
- **O3DE**: no web target found.
- **Bevy**: `wasm32-unknown-unknown` plus wasm-bindgen. WebGPU is experimental, and the `webgpu` feature overrides `webgl2`. Browser audio is single-threaded and can stutter. — [Bevy examples README](https://github.com/bevyengine/bevy/blob/main/examples/README.md)
- **Bevy 0.20**: mesh shaders are unsupported on web, and Basis Universal (UASTC) remains the best cross-platform texture format including WebGPU. — [Bevy 0.20](https://bevy.org/news/bevy-0-20/)
- **Defold**: 1.13 removed `js-web` "in favour of fully committing to wasm-web". The splash image now fits inside the canvas. — [Defold 1.13.0](https://forum.defold.com/t/defold-1-13-0-has-been-released/82980)
- **Flax**: 1.12 added web export, a WebGPU backend and basis_universal textures. — [GitHub Flax releases](https://github.com/FlaxEngine/FlaxEngine/releases); [GameDev.net Flax 1.12](https://gamedev.net/news/3431-flax-engine-112-released/)
- **Fyrox**: wasm through export-cli, "tested only with `wasm32-unknown-unknown`". Demo projects run in the browser. — [Fyrox 1.0.0](https://fyrox.rs/blog/post/fyrox-game-engine-1-0-0/); [GitHub Fyrox](https://github.com/FyroxEngine/Fyrox)
- **Babylon**: the Babylon.js web engine is the natural web target; Babylon Native is its native counterpart (immature, see §1). — [Babylon forum](https://forum.babylonjs.com/t/react-native-babylonjs-what-is-the-current-status/58315/3)

### Inferences
- If the existing Western Heart web build matters as a secondary channel, Cocos and Defold have the longest-proven web pipelines. Flax's web target is under six months old, and Stride and O3DE drop web entirely.

### Gaps
- No web performance data for 3D skinned characters on any engine.
- Cocos 3.8's WebGPU status (experimental or not) is unconfirmed.

---

## 7. Fighting-game ecosystem: rollback netcode libraries, deterministic simulation, shipped fighting games

### Takeaway
Only **Bevy** has a maintained, engine-integrated rollback library: `bevy_ggrs`, a GGRS port of GGPO's model with P2P, spectator and SyncTest sessions. It pairs with Avian physics' optional cross-platform-determinism feature. C# engines (Stride, Flax) can use **Backdash**, a GGPO-inspired MIT C# library. C++ engines (O3DE, Cocos native) could integrate **GGPO** (MIT), whose build is still Windows-only. I found no shipped commercial 3D fighting game on any of these engines; only game-jam-level fighters exist (Cocos "Beat Him", Defold "Librarian Barbarians").

### Cited Findings
**Cocos Creator 3.8 / COCOS 4**
- No Cocos rollback library found.
- "Beat Him" is a 3D fighting game made in Cocos Creator for Ludum Dare 47 (HTML5, in development). — [itch.io Beat Him](https://d119.itch.io/beat-him)

**Stride / Flax (C#)**
- **Backdash** is "a fully C# Rollback Netcode implementation heavily inspired on GGPO" under MIT, distributed on NuGet (`dotnet add package Backdash`). Later builds target net10.0. Demos exist for MonoGame and Godot, not Stride or Flax. — [Backdash NuGet](https://feed.nuget.org/packages/Backdash.Utils/0.5.6-preview); [MonoGame community post](https://community.monogame.net/t/backdash-new-c-rollback-netcode-library/20343)

**O3DE / C++ engines**
- **GGPO** is MIT licensed; "Building GGPO is currently only available on Windows" (Visual Studio 2019 plus CMake). It has about 3.6k stars. — [GitHub pond3r/ggpo](https://github.com/pond3r/ggpo)

**Bevy**
- **bevy_ggrs** is MIT/Apache, with P2P, spectator and SyncTest sessions. Systems in `GgrsSchedule` must be deterministic, and only registered components and resources are snapshotted. It ships docs on pitfalls and on debugging desyncs. — [GitHub bevy_ggrs](https://github.com/gschup/bevy_ggrs)
- Compatibility: Bevy 0.19 maps to bevy_ggrs 0.22 / GGRS 0.13.0. **There is no Bevy 0.20 row yet.** — [GitHub bevy_ggrs](https://github.com/gschup/bevy_ggrs); [docs.rs bevy_ggrs 0.22](https://docs.rs/crate/bevy_ggrs/0.22.0)
- Avian (Bevy physics) has an optional `enhanced-determinism` feature for "cross-platform deterministic math". Users report choosing it for rollback **[anecdotal]**. — [docs.rs avian3d](https://docs.rs/avian3d); [r/bevy thread](https://redlib.hbubli.cc/r/bevy/comments/1j5trxc/any_2d_platformers_with_avian)

**Defold**
- No Defold rollback library found. — (search returned only other-engine libraries: [Klotho for Godot .NET](https://godotengine.org/asset-library/asset/edit/23204), [GameMaker lockstep](https://meseta.itch.io/lockstep/purchase))
- "Librarian Barbarians" is a simple Defold fighting game (HTML5/Windows; 3D unconfirmed). — [itch.io](https://kklear.itch.io/librarian-barbarians)

**Fyrox**
- No rollback library found. GGRS is a plain Rust crate (engine-agnostic), so it could in principle be used. That is an inference: I found no source showing GGRS used with Fyrox.

### Inferences
- A fighter's simulation (hitboxes, frame data, state) is normally a custom fixed-tick integer or fixed-point loop separate from engine physics, so the engine's own determinism matters less than having rollback snapshotting and a clean fixed-update hook.
  - Bevy's ECS plus bevy_ggrs is the most turnkey of this group.
  - C# engines would use Backdash.
  - Cocos (TypeScript) or Defold (Lua) would need a hand-rolled rollback layer.
- **Version lag risk:** bevy_ggrs had not published Bevy 0.20 support two weeks after 0.20 shipped. Third-party crates in a fast-breaking engine can pin you to old engine versions.

### Gaps
- No evidence found of any commercially shipped 3D fighting game on Cocos, Stride, O3DE, Bevy, Defold, Flax or Fyrox.
- I didn't verify GGPO's or Backdash's 2026 maintenance activity or Android/iOS (ARM) builds.

---

## 8. (Added criterion) Direct sideloaded APK: can each engine produce a signed APK headlessly, and what licence text must ship with it?

### Takeaway
**Defold** is the only engine with documented, first-party, headless signed-APK flags (`bob.jar -bf apk -ks … -ksa … -ksp …`), and its licence *requires* shipping the Defold notice. **Bevy** and **Fyrox** produce APKs through standard Android tooling (Gradle or export-cli) on Linux; they owe only MIT/Apache notices. Cocos 3.8 needs a GUI session for its CLI. COCOS 4, Stride, Flax and O3DE have no documented headless signed-APK path on Linux in the sources found.

### Cited Findings
- **Cocos Creator 3.8**: the CLI build exists but "still needs the GUI environment"; the publish page documents no keystore or APK parameters. Licence text: the repo shows an MIT badge, and editor EULA terms were not retrieved. — [Cocos 3.8 CLI](https://docs.cocos.com/creator/3.8/manual/en/editor/publish/publish-in-command-line.html); [GitHub cocos-engine](https://github.com/cocos/cocos-engine)
- **COCOS 4**: headless cocos-cli is alpha, and Android is listed as a platform. Licence text: MIT (commercial clauses removed). — [GitHub cocos4](https://github.com/cocos/cocos4); [It's FOSS](https://itsfoss.com/news/cocos-4-game-engine/)
- **Stride**: the CLI and `dotnet new` are new in 4.4, and Linux builds work like Windows, but Android packaging isn't described. Licence text: MIT plus third-party notices (`THIRD PARTY.md`). — [Stride 4.4 release notes](https://doc.stride3d.net/latest/en/releasenotes/); [GitHub stride](https://github.com/stride3d/stride)
- **O3DE**: Android goes through a generated Gradle project (Export UI since 24.09), and the Linux-host status is unconfirmed. Licence text: Apache-2.0 and MIT licence files ship in the repo. — [Linux Foundation 24.09](https://www.linuxfoundation.org/press/open-3d-foundation-announces-the-launch-of-the-open-3d-engine-24.09.0-release); [GitHub o3de](https://github.com/o3de/o3de)
- **Bevy**: `cargo ndk build` plus `./gradlew build` on Linux, macOS or Windows, so APK signing is a normal Gradle step (that last point is inference). Licence text: MIT/Apache-2.0, and bundled assets carry the other licences listed in CREDITS.md. — [Bevy examples README](https://github.com/bevyengine/bevy/blob/main/examples/README.md); [GitHub bevy](https://github.com/bevyengine/bevy)
- **Defold**: `bob.jar` supports `--bundle-format apk`, `-ks`, `-ksa`, `-ksp` and `-kp`, and generates a *debug* keystore if none is given. Licence text: **you must include the Defold licence and copyright notice** (credits, licence popup, startup log or text file). — [Defold bob](https://defold.com/manuals/bob); [Defold Android](https://defold.com/llms/manuals/android.md); [Defold License](https://defold.com/license/)
- **Flax**: the Game Cooker outputs a Gradle project; there are no CLI or signing docs; macOS-host Android builds arrived in 1.13 and Linux-host support is unconfirmed. Licence text: the Flax EULA must be accepted before use; its in-game notice requirements were not retrieved. — [Flax Android](https://docs.flaxengine.com/manual/platforms/android.html); [GitHub Flax releases](https://github.com/FlaxEngine/FlaxEngine/releases); [Flax licensing](https://flaxengine.com/licensing/)
- **Fyrox**: `export-cli --target-platform android` is designed for CI/CD; signing details were not retrieved. Licence text: MIT. — [Fyrox 1.0.0](https://fyrox.rs/blog/post/fyrox-game-engine-1-0-0/); [GitHub Fyrox](https://github.com/FyroxEngine/Fyrox)
- **BRUTAL**: no Android support found. Licence text: modified MIT **requiring attribution**. — [GameFromScratch](https://gamefromscratch.com/brutal-c-game-framework-now-free/)

### Inferences
- **For a sideloaded APK built by agents on Linux, ranked:** Defold (documented end to end, but its 3D animation is unsuitable) > Bevy ≈ Fyrox (standard Rust/Gradle toolchains, no GUI) > Stride 4.4 (likely possible through .NET Android tooling, but undocumented and Vulkan-1.3-only on device) > COCOS 4 (alpha CLI) > Cocos 3.8 (needs a GUI session) > Flax and O3DE.
- **Sideload compatibility caveat:** a sideloaded APK reaches whatever phones users own, including older ones. Two engines narrow the device range: Stride 4.4 (Vulkan 1.3 required, OpenGL ES removed) and Bevy (minSdk 26 with audio). Defold (Vulkan with GL fallback) and Cocos are more forgiving.
- **Licence strings in practice:** every option needs a third-party notices screen or file. MIT and Apache require reproducing the notice; that is standard licence practice, not sourced here. Defold additionally makes it explicit, and BRUTAL requires attribution.

### Gaps
- Cocos 3.8 keystore and APK settings in a CLI build config, Stride's `dotnet publish` Android signing, and Flax's and O3DE's command-line cooking were not documented in the retrieved sources.
- Whether the Flax EULA requires an in-game logo or credit line was not retrieved.

---

## 9. (Added criterion) What each engine costs a small team once the game sells; plus implications of the 50+ fighter / 59-entry roster

### Takeaway
Engine cost once sold:
- **$0 royalties:** Cocos 3.8 (per the FAQ), COCOS 4 (MIT), Stride (MIT), O3DE (Apache-2.0/MIT), Bevy (MIT/Apache), Defold (royalty-free with a mandatory notice), Fyrox (MIT), BRUTAL (no royalties, attribution required).
- **Flax:** 4% of revenue above $250k per calendar quarter.

For a 59-entry roster with deep customization, the engines with built-in retargeting, morph targets, attachments and animated-model instancing (O3DE, Flax) scale content best. Cocos has GPU-instanced skinning samples. Defold's baked single-clip model scales worst.

### Cited Findings
- **Cocos Creator 3.8**: "free to use and has no royalty fees… all money you make with the game stays with you". — [Cocos FAQ](https://www.cocos.com/en/10-common-faqs-on-cocos-creator)
- **COCOS 4**: standard MIT, with all commercial-related clauses from Cocos Creator removed. — [It's FOSS](https://itsfoss.com/news/cocos-4-game-engine/)
- **Stride**: MIT. — [GitHub stride](https://github.com/stride3d/stride)
- **O3DE**: Apache-2.0 and MIT licence files. — [GitHub o3de](https://github.com/o3de/o3de)
- **Bevy**: MIT or Apache-2.0. — [GitHub bevy](https://github.com/bevyengine/bevy)
- **Defold**: royalty-free; "will never request royalty payments", no subscriptions or fees; notice required. — [Defold License](https://defold.com/license/)
- **Flax**: "pay a 4% royalty on earnings exceeding $250,000 (per calendar quarter)". — [Flax licensing](https://flaxengine.com/licensing/)
- **Fyrox**: MIT. — [GitHub Fyrox](https://github.com/FyroxEngine/Fyrox)
- **BRUTAL**: free, including commercial use, with no royalties and attribution required. — [gaming.net](https://www.gaming.net/brutal-game-framework-released-as-open-source-free-for-commercial-use/); [GameFromScratch](https://gamefromscratch.com/brutal-c-game-framework-now-free/)
- Roster-scale features:
  - Flax 1.13 has hardware instancing for animated models (5,000 characters at 60 fps on an RTX 2080 Ti). — [Flax 1.13](https://flaxengine.com/blog/flax-1-13-released/)
  - O3DE has actor LODs and retargeting. — [O3DE animation docs](https://www.docs.o3de.org/docs/user-guide/visualization/animation/)
  - Cocos has `SkinnedMeshBatchRenderer` and instanced-skinning samples. — [Cocos 3.0 mesh docs](https://docs.cocos.com/creator/3.0/manual/en/module-map/mesh/); [example-3d](https://github.com/linshunjun/example-3d)
  - Bevy has joint-based skinned culling and batched morph targets. — [Bevy 0.19](https://bevy.org/news/bevy-0-19/)
  - Defold stores baked per-bone matrices per keyframe and plays one animation at a time. — [Defold model animation](https://defold.com/manuals/model-animation/)

### Inferences
- **Cost:** for a small team selling a sideloaded APK directly, every engine except Flax costs $0 in fees. Flax costs nothing until a quarter's earnings exceed $250k, then 4% of the excess. Example arithmetic: $400k in a quarter gives (400k − 250k) × 4% = $6,000. The real costs are engineering time, notably:
  - building a rollback layer (all engines except Bevy);
  - building state machine, IK and retargeting (Bevy, Stride, Defold);
  - building morph targets (Stride, until #339 lands).
- **59 entries:** a fighter only renders two characters plus a select screen, so instancing hundreds of characters is not the bottleneck. What matters:
  - **content pipeline scale**: shared skeleton, retargeted move banks, per-fighter morph and attire variants;
  - **install size and memory**: APK size plus per-fighter asset streaming.
  O3DE and Flax have the strongest built-in retargeting and attachment stories. Cocos needs custom work for retargeting (none found). Bevy needs third-party crates.
- **Scoring snapshot vs Godot 4.7.** Each row is my synthesis of the findings above, not a single source; Godot itself was not researched here.

| Engine (Oct 2026 version) | Licence / cost when sold | Mobile 3D maturity | Fighter-grade animation (SM / IK / retarget / morph / spring bones) | Headless Linux signed APK | Rollback ecosystem | Main risk |
|---|---|---|---|---|---|---|
| Cocos Creator 3.8.x (v3.8.9 tag) | MIT engine, no royalties (editor EULA unverified) | High (Vulkan/Metal, many shipped mobile titles) | SM yes / two-bone IK experimental / retarget not found / morph not verified / springs not found | CLI needs GUI | none found (TS, hand-roll) | legacy line now that COCOS 4 exists |
| COCOS 4 (v4.0.0; cli alpha.44) | MIT | Inherits 3.x renderer; tooling alpha | inherits 3.x (API changes) | headless CLI, alpha | none found | editor (PinK) gated alpha |
| Stride 4.4.1 | MIT | Unproven on Android; Vulkan 1.3 only | SM no (code blend trees) / IK not found / retarget not found / **no morph** (WIP) | CLI new; Android undocumented | Backdash (C#) | morph targets missing; Windows editor |
| O3DE 26.05 | Apache-2.0/MIT | Mobile pipeline; iOS experimental; 1 studio case | SM, blend spaces, ragdoll, simulated objects, morph, retarget, skin attachments (IK unverified) | Gradle export; Linux host unverified | GGPO (C++, Windows build) | heavy engine, small mobile track record |
| Bevy 0.20 | MIT/Apache | Works (cargo-ndk/Gradle); no shipped 3D mobile evidence | graph + masks + morph built in; SM via 3rd-party; IK/retarget not built in | yes (pure CLI) | **bevy_ggrs** (no 0.20 row yet) + Avian determinism | breaking every ~3 months; no editor |
| Defold 1.14.0 | Royalty-free, **notice required** | Mobile-first, Vulkan default Android | **one baked clip at a time; skin XOR morph; no IK** | **yes, documented flags** | none found | 3D animation too thin for a fighter |
| Flax 1.13 | **4% > $250k/quarter**, EULA | Android Vulkan / iOS; no shipped mobile evidence | SM, Multi Blend, two-bone + aim IK, retarget, blend shapes, Spring Bone | Game Cooker; Linux-host Android unconfirmed | Backdash (C#) | royalty; desktop-first reputation |
| Fyrox 1.0.1 | MIT | Android (OpenGL ES 3 historically), no iOS docs | ABSM, blend spaces, root motion, blend shapes, ragdoll (IK/retarget not found) | yes (export-cli android) | GGRS usable in principle | tiny team; mobile 3D perf poor historically |
| BRUTAL / Carbon / Babylon Native | modified-MIT + attribution / licence unknown / not checked | not mobile-ready | n/a | n/a | n/a | framework-only, desktop, or pre-release |

### Gaps
- No total cost-of-ownership data (support contracts, paid plugins, CI minutes) for any engine.
- No APK-size baselines for 3D content beyond Defold's empty-project anecdote. I didn't check per-engine runtime size for Cocos, Bevy, Flax, Stride, O3DE or Fyrox.
- Whether Cocos 3.8's editor EULA or Flax's EULA adds splash-screen or logo obligations is unverified.
