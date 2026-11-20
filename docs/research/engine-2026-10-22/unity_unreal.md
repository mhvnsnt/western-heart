# Unity 6.x vs Unreal Engine 5.8 (and UE6 plans) for a native mobile 3D fighting game with a deep creation suite — state as of 22 Oct 2026

Scope notes for the report writer:
- Project context from the coordinator: direct sideloaded APK distribution at first (no app store); roster is 50+ distinct fighters (59 roster entries); team = AI coding agents working through a Linux shell.
- "OLDER" marks information dated before 2025 or from earlier engine versions. Secondary or blog sources are flagged where they matter. unrealengine.com pages (license, EULA change log, 5.8 news post) returned HTTP 403 to my fetcher, so Unreal licensing terms below come from Epic docs on dev.epicgames.com, search-indexed snippets of Epic pages, and press coverage. They are not the live EULA text.
- Current versions: Unity 6.3 LTS (released 4 Dec 2025, support to 4 Dec 2027, latest patch 6000.3.27f1 on 20 Oct 2026) and Unity 6.6 (released 31 Aug 2026, latest 6000.6.7f1 on 21 Oct 2026). Unity 6.0 LTS security support ended 16 Oct 2026 — [endoflife.date](https://endoflife.date/unity). Unity says 6.5 "progresses toward 6.7 LTS" — [Unity Discussions](https://discussions.unity.com/t/unity-6-5-is-now-available/1723176). UE 5.8 released 17 Jun 2026 — [Epic forums](https://forums.unrealengine.com/t/unreal-engine-5-8-released/2729274). The 5.8.1 hotfix (260+ fixes) shipped 28 Jul 2026 — [Epic forums](https://forums.unrealengine.com/t/5-8-1-hotfix-released/2738864).

## Licensing in 2026: Unity tiers and splash screen, Unreal royalty and source terms, UE6 plans

### Takeaway
Unity 2026 is seat-based only. Personal is free under $200k of revenue plus funding in the trailing 12 months, and its splash screen is optional in Unity 6. Pro is $2,310 per seat per year from 12 Jan 2026. The Runtime Fee (per-install) was cancelled in Sept 2024. Unreal is free until a product passes $1M lifetime gross, then takes a 5% royalty on gross above that (3.5% under "Launch Everywhere with Epic"). Its source is available through GitHub under the EULA. No 2026 change to the royalty was found. UE 5.8 is the last planned major UE5 release, and UE6 Early Access is targeted for the end of 2027.

### Cited Findings
**Unity**
- Personal: free, "No credit card required." It is for individuals and small businesses with less than $200K USD in revenue or funds raised in the prior 12 months. Pro is "Required for businesses with over $200K in funding or annual revenue." Enterprise is "Required for businesses with more than $25M in annual revenue." Pro is listed at $210/month or "from $2,310.00 /yr." Industry is required for non-game apps above $1M — [Unity pricing](https://unity.com/pricing)
- "Unity Pro and Enterprise will see a 5% price increase, starting January 12th, 2026." The 2026 Pro price is "$2,310/yr per seat, prepaid yearly." Existing subscribers' prices update at the next renewal on or after 12 Jan 2026 — [Unity pricing updates](https://unity.com/products/pricing-updates)
- Runtime Fee: "As of September 12, 2024, we decided to cancel it." Personal is listed with "Splash screen optional with Unity 6" (marked available now) — [Unity pricing updates](https://unity.com/products/pricing-updates)
- The cancellation post (12 Sep 2024, OLDER but still the governing announcement) says "cancel the Runtime Fee for our games customers, effective immediately." It doubled the Personal ceiling "from $100,000 to $200,000 USD" and said "The Made with Unity splash screen will become optional for Unity Personal games made with Unity 6." It also announced an 8% Pro increase to $2,200 per seat per year and a 25% Enterprise increase, effective 1 Jan 2025 (since superseded by the 2026 +5%) — [Unity blog](https://unity.com/blog/unity-is-canceling-the-runtime-fee)
- Other 2026 changes: "Starting with Unity 6.3, Havok Physics will no longer be included with Pro, Enterprise, or Industry." Seat charges are being removed for cloud-hosted Unity Version Control, with DevOps pricing changes effective 1 Mar 2026 — [Unity pricing updates](https://unity.com/products/pricing-updates)
- Metered cloud add-ons (only if used): Asset Manager storage $0.75/GB; standard storage $0.10/GB for 25–100 GB; egress $0.10/GB after 100 GB per month; build compute is per-minute — [Unity pricing](https://unity.com/pricing)

**Unreal**
- Standard terms: free until a product passes $1M lifetime gross revenue, then 5% of the excess. The threshold is per product — [Promise Legal overview](https://blog.promise.legal/game-engine-license-agreements-unreal-unity-godot/); [300mind](https://300mind.studio/blog/unreal-engine-licensing-royalties/) (the 300mind article, dated 2 Oct 2026, contradicts itself on "lifetime vs calendar year," so treat it as low quality)
- Epic's license page (search snippet; the page itself returned 403) says lifetime gross revenue above $1M per product carries a 5% royalty "regardless of who collects it," and that revenue from Epic Games Store sales is royalty-free — [Unreal license page](https://www.unrealengine.com/license)
- "Launch Everywhere with Epic" (EULA update 20): 3.5% instead of 5% from 1 Jan 2025 for games released on the Epic Games Store "before or at the same time" as other stores on PC, Mac and Android (consoles too if launched concurrently). The rate reverts to 5% if the game is on another PC or Android store without also being on EGS for that platform. The iOS EGS requirement is temporarily waived because of Apple's Core Technology Fee, with at least 4 months' notice before that changes — [GameFromScratch](https://gamefromscratch.com/unreal-engine-launch-everywhere-with-epic/); [CG Channel, Oct 2024](https://www.cgchannel.com/2024/10/epic-games-to-cut-royalty-rate-on-unreal-engine-games/); [Unreal EULA change log (snippet)](https://www.unrealengine.com/eula-change-log/unreal)
- Seat pricing applies only to non-game commercial use. Runtime apps licensed to third parties stay on the royalty track — [Epic pricing update blog (2024, OLDER)](https://www.unrealengine.com/blog/we-are-updating-unreal-engine-twinmotion-and-realitycapture-pricing-in-late-april)
- Source-available: sign in with a verified Epic account, link GitHub under Apps & Accounts, and accept the EULA. The C++ source is "fully accessible" for studying, customizing and debugging. The EULA forbids combining engine code with copyleft code in ways that would put the engine under other terms — [Unreal on GitHub](https://www.unrealengine.com/en-US/ue-on-github)
- MetaHuman licensing changed with UE 5.6 (June 2025, OLDER). MetaHuman characters can be used in any engine or DCC, including Unity and Godot, commercially. Rendering MetaHumans outside UE at more than $1M annual gross requires a UE seat — [CG Channel, Jun 2025](https://www.cgchannel.com/2025/06/you-can-now-sell-metahumans-or-use-them-in-unity-or-godot/) (the $1M seat rule comes from a Reddit quote of the EULA, per search summary)

**UE6 plans**
- UE 5.8 was presented as the last planned major UE5 release. At the State of Unreal 2026 keynote (17 Jun 2026, Unreal Fest Chicago), Epic set a UE6 Early Access target of end of 2027. Coverage describes UE6 as merging UE5 with UEFN, with Verse as the core gameplay language — [Strafe](https://www.strafe.com/news/read/state-of-unreal-2026-all-the-key-takeaways-from-the-epic-keynote/); [GameEngineTracker](https://gameenginetracker.com/unreal-engine-6-release-date/). Wikipedia dates the UE6 announcement to 24 May 2026 at the RLCS Paris Major, which conflicts with the 17 Jun keynote framing — [Wikipedia](https://en.wikipedia.org/wiki/Unreal_Engine)
- A claim that Epic pledged to keep 5% unchanged into UE6 appears only in a promotional article. I could not verify it with Epic — [Tech Insider](https://tech-insider.org/unreal-engine-6-state-of-unreal-2026/)

### Inferences
- For a sideloaded indie title with little revenue, both engines cost $0 at launch. The Unity Personal splash is removable in Unity 6, so splash rules no longer separate the engines.
- Unity's threshold tracks the company (revenue plus funding, trailing 12 months), so a funding round alone can force Pro seats. Unreal's threshold tracks the product's lifetime gross, so the first $1M is free no matter how fast it arrives.
- UE6 Early Access is more than a year away, and a full release likely comes later still. A project starting now on Unreal would ship on UE5.x and face a UE5→UE6 migration decision mid-life. Coverage says Blueprint deprecation is planned later in the UE6 cycle (search summary), which matters if agents author logic in Blueprint, which is binary.

### Gaps
- I could not read the live Unreal EULA (403). The exact definition of "gross revenue" (treatment of payment-processor fees, refunds and taxes) is unverified. One blog says those are excluded, while the official snippet says "regardless of who collects it."
- I found no primary Epic statement on UE6 licensing.
- Unity's rule on whether every seat in an organization must be Pro once it crosses $200k was not confirmed from the Editor Software Terms text.

## What each engine costs once the game sells — worked examples ($50k / $500k / $2M lifetime)

### Takeaway
Unity costs a fixed $2,310 per seat per year, and only once the company passes $200k of trailing-12-month revenue plus funding. It never takes a revenue share or per-install fee. Unreal costs nothing until a product passes $1M lifetime gross, then 5% (or 3.5%) of everything above $1M, including direct APK and in-app sales. At $2M lifetime, Unreal costs $50,000 at 5%. Unity costs $2,310 × seats × years above the threshold, for example $20,790 for 3 seats over 3 years.

### Cited Findings
- Unity Pro is $2,310 per seat per year prepaid, or $210 per month, from 12 Jan 2026. Personal is free under $200k revenue plus funding in the prior 12 months. There is no Runtime/per-install fee — [Unity pricing](https://unity.com/pricing); [Unity pricing updates](https://unity.com/products/pricing-updates)
- An industry blog agrees: "There is no per-install fee." Its author works at a Unity studio — [Ocean View Games, May 2026](https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games)
- Unreal: 5% of lifetime gross above $1M per product, "regardless of who collects it." Revenue earned on the Epic Games Store is royalty-free — [Unreal license page (snippet)](https://www.unrealengine.com/license)
- Gross is computed before store cuts. Example: $1.5M gross on Steam is taxed on the full $1.5M, not the roughly $1.05M received. Direct-to-consumer sales, IAP, DLC and season passes all count, and pre-release revenue counts too. Studios self-report quarterly and pay within 45 days of quarter end, and Epic can audit — [300mind, Oct 2026](https://300mind.studio/blog/unreal-engine-licensing-royalties/) (blog characterization, not EULA text). Another guide lists direct sales, IAP, ads and DLC as gross — search summary of [Getgud](https://www.getgud.io/blog/does-unreal-engine-cost-money/)
- 3.5% applies only if the game is also released on the Epic Games Store at the same time on that platform — [GameFromScratch](https://gamefromscratch.com/unreal-engine-launch-everywhere-with-epic/)

**Worked examples.** These are my arithmetic on the cited terms. They assume 1 product, a team of 3 Unity seats, no outside funding, no EGS sales, and US dollars.

| Lifetime revenue | Unity 6 | Unreal 5.8 |
|---|---|---|
| **$50k** | $0. Personal, under $200k/yr. Splash optional. | $0. Under $1M. |
| **$500k** | $0 if no 12-month window (revenue + funding) exceeds $200k, e.g. ~$167k/yr over 3 years. If ≥$200k lands in one 12-month window: Pro for the following year = 3 × $2,310 = **$6,930/yr** (1 seat: $2,310/yr). | **$0.** Under $1M lifetime. |
| **$2M** (e.g. ~$667k/yr over 3 yrs) | Pro every year above threshold: 3 seats × $2,310 × ~3 yrs ≈ **$20,790** total (1 seat ≈ $6,930). No revenue share. | 5% × ($2M − $1M) = **$50,000**. At 3.5% (Launch Everywhere, needs simultaneous EGS Android release) = **$35,000**. Calculated on gross, before payment-processor or store cuts (per blog reading). |

### Inferences
- Break-even (3 seats, 3 paid years ≈ $20,790): Unreal's 5% royalty equals that at about $1.42M lifetime gross. Below that, Unreal is cheaper. Above it, Unity is cheaper, and the gap widens linearly. With 1 seat over 3 years ($6,930), break-even is about $1.14M.
- For direct APK sales through a web payment processor, Unreal's royalty base is probably the full customer price, not the post-processor payout. Budget the 5% on top of a typical 3–5% processor fee.
- Unity costs scale with headcount, not success. If AI agents run under one human's seat, one Pro seat may suffice. I did not verify Unity's seat-counting rules for automation or CI users (see Gaps).

### Gaps
- Not verified against live EULA text: whether payment-processing fees, refunds and taxes are excluded from Unreal "gross."
- Whether a direct website APK counts as an "Android store" for Launch Everywhere's reversion clause. Neither GameFromScratch nor any other source defines "store."
- Unity's rules for CI/build-machine seats versus human seats were not found. The GameCI PR says Personal seats now activate only through the online licensing client (see the CI section).

## Direct sideloaded APK distribution: license, splash, activation and signing implications

### Takeaway
Neither engine's license depends on the storefront. A sideloaded APK has the same Unity Personal/Pro and Unreal royalty obligations as a store release, and Unreal's royalty still applies to direct sales. I found no documented runtime license check in either engine's shipped player. The real sideload constraints are Android ones. Every APK must be signed, and losing the key ends updates. Google's developer-verification regime began on 30 Sep 2026 in four countries for participating stores. It is slated to expand globally from 2027, with adb and an "advanced flow" remaining for unregistered apps.

### Cited Findings
- Unity: Personal's splash is optional with Unity 6, and the Runtime Fee (which would have counted installs) is cancelled — [Unity pricing updates](https://unity.com/products/pricing-updates)
- Unity editor activation (developer side, not player side): Unity "removed offline/manual activation for Personal licenses." license.unity3d.com/manual now says "Offline activation is available only for Enterprise and Industry seats." GameCI added a `personal` strategy using the licensing client with undocumented flags `--activate-all --include-personal`. PR #246 was opened 4 Sep 2026 and merged 5 Sep 2026 — [game-ci/cli PR #246](https://github.com/game-ci/cli/pull/246); [Unity Discussions thread](https://discussions.unity.com/t/best-practice-for-ci-account-activation/1721692)
- Unreal: royalty applies to gross "regardless of who collects it," so direct web sales count. EGS revenue is royalty-free — [Unreal license page (snippet)](https://www.unrealengine.com/license). Epic's Android store was announced for 2024 with an 88/12 split and waived UE royalties on Epic-processed sales (OLDER announcement) — [Tom's Guide](https://tomsguide.com/phones/iphones/epic-games-store-to-go-mobile-in-2024)
- Android signing: "Android requires that all APKs be digitally signed with a certificate before they are installed on a device or updated." Debug certificates are "insecure by design." With self-managed keys, "If you lose or misplace your key, you will not be able to publish updates to your existing app. You cannot regenerate a previously generated key." Recommended key validity is 25+ years — [Android Developers: app signing](https://developer.android.com/studio/publish/app-signing)
- Both engines expose APK vs AAB output. For example, GameCI's `androidExportType` is `androidPackage` for APK and `androidAppBundle` for AAB, and Android Keystore options must be set — [GameCI builder docs](https://game.ci/docs/github/builder/)
- Google developer verification: protections "take effect on September 30, 2026, starting with users in Brazil, Indonesia, Singapore, and Thailand." Enforcement begins with 7 stores: Google Play, HONOR, OPPO, Samsung Galaxy Store, Transsion Palm Store, vivo V-Appstore and Xiaomi GetApps. "Unregistered apps can be sideloaded with Android Debug Bridge (adb) or advanced flow." Free "limited distribution" accounts allow up to 20 devices with no ID or fee. Global expansion is planned for "2027 and beyond" — [Android Developers Blog, Jun 2026](https://android-developers.googleblog.com/2026/06/android-developer-verification.html)
- Press says a website APK install "isn't subject to the September 30 verification requirements." The advanced flow includes warnings and a one-day waiting period — [Android Authority](https://www.androidauthority.com/android-sideloading-developer-verification-first-wave-rollout-3717921/); [Gadget Hacks](https://android.gadgethacks.com/news/google-android-sideloading-restrictions-sept-30-explained/)
- Installed size exceeds APK size on Android. Native libs are extracted on install: a Unity empty scene was 20 MB APK and 62 MB installed. A UE4 build was 41 MB APK and 160 MB+ installed because of OBB data (both OLDER) — [Unity Discussions](https://discussions.unity.com/t/apk-size-of-empty-scene-is-20mb-after-installation-on-phone-its-62mb/653413); [Epic forum](https://forums.unrealengine.com/t/how-to-reduce-mobile-file-size/349473)

### Inferences
- Engine choice does not change sideload legality. Both produce a self-signed release APK from a project keystore. The keystore must be generated once, backed up, and kept out of git. Per the repo's no-secrets law, it belongs in CI secrets.
- Register as a verified Android developer before the 2027 global rollout. Otherwise, users on certified devices may face the advanced-flow friction (warnings plus a 1-day wait), whichever engine is used.
- Unreal's default Android packaging can split data into OBB. For a single-file sideload, the team must make sure data is packaged inside the APK. Unity's default single APK is simpler for sideloading. (Neither engine's setting was fetched; see Gaps.)

### Gaps
- I found no source either confirming or ruling out a runtime license/online check in Unity 6 or UE 5.8 players. None is documented in the pricing or licensing pages read.
- I did not fetch Epic's doc on "Package game data inside .apk" or Unity's "Split Application Binary" defaults. APK size limits for very large single sideloaded APKs, relevant for 59 roster entries, were not researched.

## Mobile 3D rendering on mid-range Android, APK/AAB size, thermal/perf reputation

### Takeaway
UE 5.8 makes multi-pass deferred the default mobile renderer. It adds mobile SSAO, SSR, deferred decals and contact shadows, plus FP16 shaders. The floor is Android 8 / API 26, 64-bit Arm, GLES 3.2 or Vulkan 1.1 (on Android 10+). Unity URP has a stronger mobile reputation and a far smaller minimal APK (roughly 10–50 MB versus Unreal's ~40–300 MB), but every size figure is anecdotal or biased. I found no rigorous thermal benchmark.

### Cited Findings
- UE 5.8 mobile renderer: "Multi-pass deferred rendering as the default path across mobile platforms," with forward still opt-in. "Mobile support for SSAO, SSR, deferred decals, contact shadows, and higher-quality water rendering." New CVar `r.Mobile.Upscale.Quality`. "UE 5.8 introduces half-precision (FP16) shader usage in targeted materials and global shader passes" — [Tom Looman](https://tomlooman.com/unreal-engine-5-8-performance-highlights/); [UE 5.8 release notes](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes?lang=en-US)
- UE 5.8 Android: "Simpler automated setup of developer workstations using Turnkey." Unreal Engine Remote now runs on Android. Controller mapping is improved — [UE 5.8 release notes](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes?lang=en-US)
- UE 5.8 Android requirements: Android Studio Koala 2024.1.2 P1, target SDK 35 (min compile 34), NDK r27c, build-tools 35.0.1, OpenJDK 21.0.3. Minimum install API 26 ("Android 8 or higher"), 64-bit Arm. GPUs: Mali T8xx+, Adreno 5xx–8xx, PowerVR Rogue/IMG B-series+, Samsung Xclipse 5xx/9xx. OpenGL ES 3.2, or Vulkan 1.1 on Android 10+ — [Epic: Android development requirements (5.8)](https://dev.epicgames.com/documentation/unreal-engine/android-development-requirements-for-unreal-engine)
- Conflict: the Rendering Features Reference lists Mobile Deferred for Metal, Vulkan and Switch only — [Epic](https://dev.epicgames.com/documentation/unreal-engine/rendering-features-reference). The Mobile Deferred Shading page says it is supported on Android GLES too — [Epic](https://dev.epicgames.com/documentation/unreal-engine/using-the-mobile-deferred-shading-mode-in-unreal-engine?lang=en-US)
- Reputation (Unity-biased author): URP is "purpose-built for mobile," while Unreal's mobile renderer "was designed top-down from a desktop-first perspective." "Lumen and Nanite do not run on mobile devices." The table rates thermals as "URP optimised for ARM" versus "Desktop-first adapted," but gives no measurements. Unity powers "more than 70% of the top 1,000 mobile games" (Apptopia, Jan 2025) — [Ocean View Games, May 2026](https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games)
- Minimal build size: Unity "approximately 30 to 50 MB" versus Unreal "roughly 150 to 300 MB" (no methodology) — [Ocean View Games](https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games). A stripped empty Unity project can be under 15 MB, and an Unreal "Hello World" exceeds 80–100 MB — [MetaDesign Solutions](https://metadesignsolutions.com/blog/unity-vs-unreal-engine-mobile-game-development). UE4-era forum reports put an empty UE 4.25 C++ shipping APK at about 80 MB and Epic-guided reductions at about 40–60 MB (OLDER) — [Epic forum](https://forums.unrealengine.com/t/reducing-build-size-an-attempt-to-get-the-smallest-size-empty-project-packaged/121027); [Epic forum](https://forums.unrealengine.com/t/how-to-reduce-android-apk-file-size/106086)
- Tekken Mobile (Unity, CEDEC 2018, OLDER): Unity's convenience cost CPU time. The team baked stage lighting, used custom character lighting and shadows, and was CPU-bound, not GPU-bound — [gamebiz.jp CEDEC 2018](https://gamebiz.jp/news/218774)

### Inferences
- With 59 roster entries, each with attire and creation parts, content will dominate package size. Unreal's roughly 50–150 MB larger engine overhead matters less than texture/mesh budgets, but it still hits a sideloaded download hardest.
- UE 5.8's deferred default plus mobile decals closes much of the old feature gap. Mid-range Android devices on GLES-only or older Mali/Adreno parts remain the risk, and the docs disagree on GLES deferred.

### Gaps
- No measured Unity 6 URP or UE 5.8 empty-project APK/AAB sizes, and no controlled thermal or frame-time benchmark on a named mid-range device. A test build in both engines is the only reliable answer.
- I did not find Unity 6.x URP mobile release-note specifics (e.g. GPU Resident Drawing on Vulkan mobile) in this pass.

## Skeletal animation: runtime retargeting, state machines, IK, jiggle, fixed-tick determinism, rollback

### Takeaway
Both engines can retarget at runtime. Unity uses Humanoid avatars, which can be built at runtime with `AvatarBuilder.BuildHumanAvatar`. Unreal uses the Retarget Pose From Mesh node with an IK Retargeter asset, and 5.8 adds runtime-selectable override sets. Jiggle is covered by Magica Cloth 2 (Unity) and KawaiiPhysics, which is MIT-licensed and supports UE 5.3–5.8. Unity has the far stronger off-the-shelf deterministic rollback story: Photon Quantum 3 explicitly targets fighting games, and UFE 2 Pro includes rollback. Unreal's options are a young Fab plugin (v0.3.0) plus Epic's Mover/Network Prediction, which is not a fighting-game framework.

### Cited Findings
- Unity `AvatarBuilder.BuildHumanAvatar` creates a humanoid avatar from a `HumanDescription` (bone mapping plus twist and stretch retarget parameters). Unity's doc example calls it from `Start()`, which implies runtime use. Results should be checked with `Avatar.isValid` — [Unity Scripting API](https://docs.unity3d.com/6000.3/Documentation/ScriptReference/AvatarBuilder.BuildHumanAvatar.html)
- Unreal runtime retargeting: the "Retarget Pose From Mesh" AnimGraph node applies an IK Retargeter asset at runtime, taking poses from another skeletal mesh component ("Use Attached Parent"). It also accepts a custom retarget profile at runtime — [Epic: runtime IK retargeting](https://dev.epicgames.com/documentation/unreal-engine/runtime-ik-retargeting-in-unreal-engine)
- UE 5.8 IK Retargeter: override sets let "a single IK retargeter asset to handle different retarget relationships," and you can "Set which override set to use when running IK retargeter for runtime retargeting." It also adds a foot plane and toes definition — [UE 5.8 release notes](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes?lang=en-US)
- IK Rig chain mapping handles different bone counts, e.g. 3 spine bones to 5 — [Cosindra guide](https://cosindra.ai/guides/ue5-ik-retargeter)
- UE 5.8 also moves Control Rig Physics to Beta and adds ChaosMover "trajectory prediction for motion-matching workflows" — [UE 5.8 release notes](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes?lang=en-US)
- Jiggle in Unity: Magica Cloth 2 requires Burst, Collections and Mathematics and "works on all platforms except WebGL." It "cannot be applied to vertices that are deformed with BlendShape" — [MagicaCloth2 Readme (third-party mirror of vendor file)](https://kindnick-git.duckdns.org/kindnick/Streamingle_URP/media/branch/main/Assets/External/MagicaCloth2/Readme.txt). The developer warns that MeshCloth is CPU-heavy on mobile and BoneCloth is fine (Magica Cloth 1 thread, OLDER) — [Unity Discussions](https://discussions.unity.com/t/released-magica-cloth/773425?page=49)
- Jiggle in Unreal: KawaiiPhysics is a "simple pseudo-physics plugin" AnimGraph node for hair, skirts and chest. It is "PhysX-free," MIT-licensed, supports UE 5.3–5.8, and provides sphere, capsule and plane collision, wind and gravity, and bone constraints — [GitHub: KawaiiPhysics](https://github.com/pafuhana1213/KawaiiPhysics)
- Photon Quantum 3: a "high-performance deterministic ECS" in which clients exchange only input. It uses predict/rollback, is "ideal for latency-sensitive online games like sports games, fighting games, & FPS," and decouples the simulation from Unity, which handles presentation. It is Unity-only, and development is free — [Photon Quantum docs](https://doc.photonengine.com/quantum/v3/quantum-intro). It became a Unity Verified Solution in Sep 2024 — [Photon blog](https://blog.photonengine.com/the-evolution-of-deterministic-multiplayer-photon-quantum-now-a-unity-verified-solution/). Free tier is 100 CCU, and a "Plus" tier is about $95/yr for 200 CCU (secondary) — [DEV Community](https://dev.to/aplusgamesstudio/photon-vs-unity-netcode-vs-mirror-for-multiplayer-2026-4fl2)
- UFE 2: rollback netcode comes in Pro ($349) and Source. It uses native GGPO-like rollback with custom deterministic physics wrapping Unity's, because "Unity's system isn't deterministic." The latest seen is v2.7.1 — [UFE pricing](https://ufe3d.com/ufe2/pricing.html); [UFE netcode docs](https://Www.Ufe3D.Com/doku.php/global:netcode); [UFE forum](https://www.ufe3d.com/forum/viewtopic.php?id=2496); [Payhip](https://payhip.com/b/a5fM)
- Unreal rollback: Rollback Core Pro (GregOrigin) is a GGPO-style deterministic rollback framework for UE5 on Fab, at v0.3.0 ("not yet production-ready for some use cases"). It includes a 2D demo, and a free open-source variant exists — [Fab listing](https://www.fab.com/listings/03aa010f-2413-4a98-91b1-4fa67d0aedd4); [Epic forum](https://forums.unrealengine.com/t/gregorigin-rollback-core-pro-accessible-netcode-framework-for-fighting-platform-games/2728262)
- UE 5.8 Network Prediction/Mover: layered moves can be scheduled ahead, "optional Iris replication support in Network Prediction," and "adaptive time dilation to reduce client predict-ahead." Rollback support is described as expanded — [UE 5.8 release notes](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes?lang=en-US)

### Inferences
- In either engine, a deterministic 60 Hz fighting core should live in a fixed-point or integer simulation separate from engine physics and animation. Quantum ships this for Unity, while on Unreal it is custom C++ or an immature plugin. A fighting game rarely needs engine physics in the sim, so this is less decisive if the game logic is hand-rolled.
- Humanoid retargeting is the pragmatic route for Unity runtime-loaded rigs: map the bones, call BuildHumanAvatar, and play shared Humanoid clips. Non-humanoid fighters (owl body, souls/vessels) fall outside Humanoid and would need Generic rigs or custom retargeting. On Unreal, IK Rig chains handle non-standard topologies more flexibly.

### Gaps
- Not researched in this pass: Unreal AnimDynamics/RigidBody node mobile cost; Dynamic Bone status in Unity 6; Unity Animation Rigging versus UE Full-Body IK and Control Rig mobile cost; GGPO C library integrations for either engine.
- UFE 2 compatibility with Unity 6 is unconfirmed.

## Creation-suite features: runtime glTF, sockets/bone scaling, blend shapes, skinned-mesh decals, clothing, Mutable/MetaHuman

### Takeaway
Runtime glTF is solid in both engines: glTFast is Unity's package, and glTFRuntime is MIT-licensed for UE. glTFast cannot hand animation straight to Mecanim/Humanoid. Unreal has the stronger built-in customization system: Mutable is declared production-ready in 5.8. MetaHuman scales down to mobile only at LOD 3 and with hair cards. URP decals on mobile must use the Screen Space technique, since DBuffer doesn't support GLES and is costly on tile-based GPUs, and skinned-mesh decal support is murky.

### Cited Findings
- glTFast (`com.unity.cloud.gltfast`, 6.14 docs) supports all platforms and URP, HDRP and Built-in. It handles runtime import and export and KTX/Basis, Draco and meshopt compression — [glTFast manual](https://docs.unity3d.com/Packages/com.unity.cloud.gltfast@6.14/manual/index.html). Skins and joints ✅. Morph targets ✅. Sparse accessors only for "morph targets and vertex positions." KHR_materials_variants and KHR_texture_transform ✅. Animation only "via legacy Animation System." Mecanim is partial: "Animation clips can be imported Mecanim compatible, but they won't be assigned and cannot be played back without further work." The Playables API is not supported, and Humanoid is not mentioned — [glTFast features](https://docs.unity3d.com/Packages/com.unity.cloud.gltfast@6.14/manual/features.html)
- glTFRuntime (UE): MIT, UE 4.25+ including UE5. Free on GitHub and also sold on the marketplace. It has tutorials for assigning existing animations to a glTF SkeletalMesh (skeleton remapping) and for runtime animation retargeting, and extension plugins for FBX, OBJ and Draco — [GitHub: glTFRuntime](https://github.com/rdeioris/glTFRuntime)
- Mutable: "Mutable in UE 5.8 release reaches production readiness with stability, performance, and pipeline improvements." It adds dataless customizable objects (runtime parameter handling) and refactors the system tick to cut game-thread time — [UE 5.8 release notes](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes?lang=en-US). This conflicts with a third-party tracker listing the plugin as Beta for 5.5–5.8 — [Unreal Directive](https://unrealdirective.com/resources/engine-plugins/mutable/). Dataless objects are listed as Experimental on the roadmap — [Epic roadmap](https://portal.productboard.com/epicgames/1-unreal-engine-public-roadmap/c/2195-dataless-mutable-experimental-). The sample broke in 5.8 (`CustomizableInstanceLODManagement` removed), and Epic staff said an updated sample was coming — [Epic forum](https://forums.unrealengine.com/t/mutable-sample-doesnt-work-in-5-8/2738480)
- Mutable runtime costs: runtime builds cost CPU, mostly on worker threads, plus "working memory." WorkingMemory is a soft cap and UObject memory is untracked. Editor-only use has no runtime cost — [Epic: Mutable runtime resources](https://dev.epicgames.com/documentation/unreal-engine/mutable-resource-usage-at-runtime-in-unreal-engine). In shipped builds, graphs are converted and packed in .pak/.ucas — [Epic: packaging Mutable](https://dev.epicgames.com/documentation/unreal-engine/packaging-mutable-projects-in-unreal-engine)
- MetaHuman on iOS/Android: best LOD 3, hair Cards, max texture 2048, no ray tracing. LOD 3 head has 2,500 verts and 283 joints with 8 influences. LOD 3 body has 1,507 verts and 4 influences, with no correctives. Physics is "No" at LOD 3–7. Strand grooms (LOD 0–1) are "not suitable for platforms like mobile" — [Epic: MetaHuman platform support/LODs](https://dev.epicgames.com/documentation/metahuman/platform-support-and-lod-specifications-for-metahumans?lang=en-US)
- UE 5.8 MetaHuman Collections (experimental) let you "build collections of modular components (head, body, hair, clothing)," marketed as "hundreds of MetaHumans on mobile devices" — [UE 5.8 release notes](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes?lang=en-US); [DSOGaming](https://www.dsogaming.com/news/unreal-engine-5-8-released-fully-detailed/)
- URP decals (Unity 6.6 docs): DBuffer "does not support the OpenGL and OpenGL ES API" and "requires the DepthNormal prepass, which makes the technique less efficient on GPUs that implement tile-based rendering." "Screen space decals are recommended for mobile platforms that use tile-based rendering." Enabling Rendering Layers forces a DepthNormal prepass. Screen Space supports only normal blending — [Unity Decal Renderer Feature reference](https://docs.unity.com/en-us/engine/6000.6/manual/visual-effects/decals/renderer-feature-decal/reference). Decals don't project on transparent surfaces and don't support the SRP Batcher — [Unity Decal Projector](https://docs.unity3d.com/6000.3/Documentation/Manual/urp/renderer-feature-decal.html)
- URP decals on skinned meshes: only low-quality, contradictory guides were found (Receive Decals, decal layers, and pre-skinning bounds clipping decals at limb extremes) — [bugnet.io](https://bugnet.io/blog/fix-unity-urp-decal-projector-not-on-skinned-mesh). Unity's issue UUM-59946 covers decals not displaying on skinned meshes in HDRP — [Unity Issue Tracker](https://issuetracker.unity3d.com/issues/decals-not-displaying-on-skinned-mesh-renderers-in-the-game-view)
- Unreal mobile decals: 5.8 adds deferred decals to the mobile renderer (release notes above). An older doc says mobile forward on GLES 3.2 does not support GBuffer decals and approximates them with BaseColor and Emissive only (OLDER) — [Epic: Decal Materials](https://dev.epicgames.com/documentation/unreal-engine/decal-materials-in-unreal-engine?lang=en-US)

### Inferences
- For tattoos and logos on fighters, baking decals into a per-character texture (render-to-texture at edit time) is safer on both engines than live projected decals on skinned meshes, especially on GLES devices.
- Mutable is the strongest built-in fit for a deep creation suite: layered clothing, mesh removal, texture compositing and parameterized morphs. Its mobile cost (CPU and working memory during character build) is undocumented, so a test build with 59 roster entries plus attire layers is mandatory. Unity has no first-party equivalent, so the suite would be custom code on SkinnedMeshRenderer, BlendShapes and material property blocks.
- MetaHuman at mobile LOD 3 (283 head joints, RigLogic) is heavy for a 2-fighter 60 fps game with 59 stylized roster entries. Its main use would be as a mesh and morph source, not as the runtime character system.

### Gaps
- Bone sockets/attachments, bone-scale morphs, blend-shape editing, layered-clothing culling and material color editing were not separately sourced. These are standard in both engines but unverified here.
- I found no Mutable mobile memory/perf data and no official Mutable "supported platforms" statement.
- Unity runtime glTF → Humanoid pipeline examples were not found.

## Headless/CI builds on Linux and text-friendliness for AI agents

### Takeaway
Unity is far friendlier to shell-driven AI agents. Scenes and prefabs are YAML (Force Text is the default). The Linux editor builds Android in GameCI Docker images (`unityci/editor`). The 2026 catch is that Personal seats can no longer be activated offline, so CI must use the licensing client online (GameCI added this Sept 2026). Unreal on Linux can build and cook Android with RunUAT BuildCookRun, but it needs a ~20–30 GB precompiled install (or ~225 GB from source with 32 GB+ RAM). Its assets are binary .uasset, and editing them by agent requires the Python editor API, commandlets or the new experimental MCP plugin.

### Cited Findings
- Unity Asset Serialization Mode "is set to **Force Text** by default." A "Reduce version control noise" option writes references on one line — [Unity Editor settings](https://docs.unity3d.com/6000.3/Documentation/Manual/class-EditorManager.html). Text scene files "can be merged more easily than binary files," and tools can generate and parse them — [Unity text scene format](https://docs.unity3d.com/6000.3/Documentation/Manual/TextSceneFormat.html)
- GameCI: default image `unityci/editor`. `androidExportType` takes `androidPackage` (APK) or `androidAppBundle` (AAB). Library caching "could speed up your build by more than 50%." Pro needs `UNITY_SERIAL`, and floating license servers are supported. The docs still say Personal needs "a one-time manual activation step," which is stale — [GameCI builder](https://game.ci/docs/github/builder/)
- Personal offline activation was removed. GameCI's licensing-client `personal` strategy uses undocumented flags, merged 5 Sep 2026 — [game-ci/cli PR #246](https://github.com/game-ci/cli/pull/246)
- Unity's official MCP Server (Unity AI open beta, May 2026) connects agents such as Claude Code and Copilot to the Unity Editor. It requires Unity 6+, the AI Assistant package, a Unity Cloud-connected project and a subscription or trial. It is configured under Project Settings > AI > Unity MCP — [Unity blog](https://unity.com/blog/unity-ai-mcp-how-to-get-started). Coverage says to treat it as experimental — [GameDev.net](https://gamedev.net/news/4376-unity-ai-open-beta-how-to-get-started-with-mcp/)
- Unreal Linux: the precompiled build is a download-and-unzip of about 20–30 GB. A source build grew to "a good 225 GB," and dependencies add about 29 GB. "If you have less than 32 GB of RAM, you shouldn't even try" compiling from source. "Linux only allows compilation for Linux itself and Android" (author's own research, Jan 2026) — [SomethingLikeGames](https://www.somethinglikegames.de/en/blog/2026/linux_06_ue/)
- Epic's Linux quickstart gives BuildCookRun via RunUAT as the command-line packaging route. Minimums are Rocky/RHEL 8+, kernel 4.18+ and glibc 2.28+ — [Epic Linux quickstart](https://dev.epicgames.com/documentation/unreal-engine/linux-development-quickstart-for-unreal-engine?lang=en-US). UE 5.8 Android setup is automated via Turnkey — [UE 5.8 release notes](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes?lang=en-US)
- UE 5.8 ships "a new experimental **MCP (Model Context Protocol)** plugin for the Unreal Editor" — [UE 5.8 release notes](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes?lang=en-US)
- Unreal text options: a `UTextAssetCommandlet` exists, but its format is not documented as an editable spec — [Epic API](https://dev.epicgames.com/documentation/unreal-engine/API/Editor/UnrealEd/UTextAssetCommandlet). `UDiffAssetsCommandlet` exports assets to text for diffing (UE4.26 doc, OLDER) — [Epic API](https://docs.unrealengine.com/4.26/API/Editor/UnrealEd/Commandlets/UDiffAssetsCommandlet/index.html). Community tools include the runreal MCP server (runs Python, queries assets, exports to text) — [mcp.directory](https://mcp.directory/servers/unreal-engine) — and a Rust `uasset` parser — [docs.rs](https://docs.rs/uasset)
- Iteration speed (Unity-biased author): Unity incremental script compile "typically 3 to 10 seconds." Unreal Blueprint/C++ "15 to 60 seconds," and PIE startup "5 to 15 seconds." Mobile builds are longer because of C++ compilation and packaging — [Ocean View Games](https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games)

### Inferences
- For AI agents in a Linux shell, Unity lets agents read and diff scenes, prefabs, animator controllers and materials directly. Unreal forces most content edits through a running or headless editor (Python, commandlets, MCP), and Blueprint graphs are opaque binary. This is the biggest practical difference for this team, after rollback tooling.
- Unity Personal CI now depends on undocumented licensing-client flags and Unity's online service. That is a fragility risk. Paying for one Pro seat (serial-based activation) may be worth it for CI reliability alone.

### Gaps
- No measured clean or incremental Android build times, or RAM/disk figures, for Unity 6 or UE 5.8 on Linux CI runners.
- Not verified: whether Epic's precompiled Linux build includes Android target support out of the box, or whether a source build is needed for Android cooking on Linux.
- Epic's official Linux container images (ghcr.io, gated behind Epic–GitHub linking) were not researched.

## Web export

### Takeaway
Unity has a supported web target. WebGL 2 is the default, and WebGPU became fully supported (not default) in Unity 6.6 on 24 Aug 2026. Burst-dependent assets such as Magica Cloth 2 don't run on web, and mobile-browser WebGPU coverage is GPU-dependent. I did not re-verify Unreal's lack of an official web export this pass.

### Cited Findings
- "as of Unity 6000.6, the WebGPU graphics API is no longer experimental — it is now a fully supported feature." "WebGPU is not enabled by default." "WebGL 2 remains the default for the time being." Removing WebGL 2 means no fallback. Compute features (VFX Graph, GPU Resident Drawing, APV) "work in the browser." Compute skinning is enabled via the "GPU Skinning" setting. Wasm64 can't use multithreading yet (28 Sep 2026). Posted 24 Aug 2026 — [Unity Discussions](https://discussions.unity.com/t/webgpu-out-of-experimental-in-unity-6-6/1734694)
- Android Chrome WebGPU: Chrome 121+ on Android 12+ with ARM, Qualcomm or Intel GPUs, and Chrome 139+ for Imagination on Android 16+ (secondary) — [Cinevva](https://app.cinevva.com/guides/webgl-webgpu-not-supported-fix)
- Magica Cloth 2 excludes WebGL because Burst doesn't compile there — [MagicaCloth2 Readme mirror](https://kindnick-git.duckdns.org/kindnick/Streamingle_URP/media/branch/main/Assets/External/MagicaCloth2/Readme.txt)

### Inferences
- The project's existing web build (gh-pages) could be continued by a Unity port with a single codebase, while a UE port would lose the web target.

### Gaps
- No source fetched this pass confirms the current status of Unreal web export. It is widely reported that official HTML5 support was removed in the UE4 era and left to the community, but I did not re-verify this.

## Shipped mobile fighting games and their engines

### Takeaway
The big licensed mobile fighters split between the engines. Marvel Contest of Champions, Shadow Fight 2/3 and Tekken Mobile run on Unity. NetherRealm's Mortal Kombat Mobile and Injustice 2 mobile run on UE4.

### Cited Findings
- Marvel Contest of Champions (Kabam): Unity — [Wikipedia](https://en.wikipedia.org/wiki/Marvel_Contest_of_Champions). One forum user claims Unreal based on a job listing (anecdotal) — [MCOC forum](https://forums.playcontestofchampions.com/en/discussion/218083/is-mcoc-run-on-unreal-engine)
- Mortal Kombat Mobile (NetherRealm, 2015–): Unreal Engine 4 — [Wikipedia](https://en.wikipedia.org/wiki/Mortal_Kombat_Mobile). MK11's mobile version is UE4 while console uses custom UE3, per an NRS programming lead — [DSOGaming](https://www.dsogaming.com/news/mortal-kombat-11-uses-custom-unreal-engine-3-mobile-version-powered-by-unreal-engine-4/)
- Injustice 2 mobile: Unreal Engine 4. Console is UE3 — [Wikipedia](https://en.wikipedia.org/wiki/Injustice_2)
- Shadow Fight 2: Unity from v2.0.0, Marmalade earlier (citation-needed tag) — [Wikipedia](https://en.wikipedia.org/wiki/Shadow_Fight_2). Shadow Fight 3: "developed on the basis of the Unity engine" per a Nekki partner studio's tech artist — [Game Developer](https://gamedeveloper.com/design/rendering-process-in-shadow-fight-3). Nekki recruited Unity developers for SF3 and uses in-house Cascadeur for animation — [Nekki vacancy](https://nekki.com/vacancy/sf3-shablon)
- Tekken Mobile (Bandai Namco, March 2018; servers closed 15 Feb 2019): Unity, chosen for Android/iOS device fragmentation — [gamebiz.jp CEDEC 2018](https://gamebiz.jp/news/218774); [Wikipedia](https://en.wikipedia.org/wiki/Tekken_Mobile). Console Tekken 7 is UE4 — [Epic blog 2014](https://www.unrealengine.com/blog/ue4-powered-tekken-7-announced-at-evo-2014)

### Inferences
- Both engines have shipped AAA-licensed 3D mobile fighters, but all the Unreal examples are UE4-era NetherRealm titles from a studio with deep in-house Unreal expertise. The Unity examples include independent studios (Nekki), which is closer to this team's profile.

### Gaps
- The engine for Shadow Fight 4: Arena is unconfirmed (Unity is plausible given Nekki's history). The engine for Mortal Kombat: Onslaught was not researched.
- No 2025–2026 UE5 mobile fighting game was found.
