# Godot 4.7 (stable, Oct 2026) and the 4.8 / 5.0 roadmap as the engine for a native mobile 3D fighting game with a deep creation suite

Research date: 2026-10-22. "Stable" docs URLs (docs.godotengine.org/en/stable/...) were confirmed to serve the **Godot 4.7** documentation on that date. Unless marked otherwise, class/API claims are from the 4.7 stable docs. Items marked **[4.8 beta]** are in the pre-release 4.8 branch only, not in any stable build. Items marked **[unverified]** or **[general knowledge]** were not confirmed against a source in this session.

## 0. Version status: what is actually stable in October 2026

### Takeaway
Godot 4.7 is the current stable line (4.7.0 shipped around mid-June 2026, then the 4.7.1 and 4.7.2 maintenance releases). 4.8 reached **beta 1 on 15 Oct 2026** and is feature-frozen. No 5.0 has been announced.

### Cited Findings
- The 4.7 release is called "Lights, Camera, Action!". It credits over 300 contributors and more than 1,600 pull requests. — [Godot 4.7 release page](https://godotengine.org/releases/4.7/)
- One outlet dates 4.7 stable to **19 June 2026** (HDR output, Gradle-based Android build environment, 1,265+ fixes since 4.6). This is a single, less-established source, so treat the exact date as approximate. — [Cinevva news](https://app.cinevva.com/hi/news/2026-06-19-godot-4-7-released)
- 4.7.1 is a maintenance release with 78 fixes from 42 contributors. — [Godot blog: Maintenance release 4.7.1](https://godotengine.org/article/maintenance-release-godot-4-7-1/)
- 4.7.2 is a maintenance release with 57 fixes, reportedly dated 18 Aug 2026. — [GameDev.net](https://gamedev.net/news/5172-godot-engine-472-stable-released/) (secondary source)
- 4.6 was released in late January 2026. CG Channel's coverage is dated 27 Jan 2026. The release had close to 400 contributors and 2,001 commits. — [CG Channel](https://www.cgchannel.com/2026/01/discover-5-key-features-for-cg-artists-in-godot-4-6/); [Godot 4.6 release page](https://godotengine.org/releases/4.6/)
- The 4.5.2 builds are dated 19 Mar 2026, and the 4.4.1 builds are dated 26 Mar 2025. — [4.5 release page](https://godotengine.org/releases/4.5/); [4.4 release page](https://godotengine.org/releases/4.4/)
- **4.8 dev 7 (29 Sep 2026) marked feature freeze.** **4.8 beta 1 followed on 15 Oct 2026** and is "fully in feature-freeze". Its changelog totals 1,523 fixes from 340 contributors, and no final release date is given. — [4.8 dev 7](https://godotengine.org/article/dev-snapshot-godot-4-8-dev-7/); [4.8 beta 1](https://godotengine.org/article/dev-snapshot-godot-4-8-beta-1/)

### Inferences
- A 4.8 stable release is plausible around late 2026 or early 2027, based on the usual beta-to-RC cadence. This is an inference, not an announcement. A project starting now should begin on 4.7.x and plan to move to 4.8 when it ships, because 4.8 adds several features relevant here (Compatibility-renderer decals, mip-level texture streaming, touch fixes).

### Gaps
- I could not confirm whether a 4.7.3 exists as of 22 Oct 2026.
- The exact 4.7.0 release date was not confirmed on godotengine.org.

## 1. Mobile rendering, iOS/Metal, UI layout and touch input

### Takeaway
Godot 4.7 has two mobile-capable renderers:
- **Mobile** (Vulkan/Metal/D3D12). Official docs list it for "high-end" mobile.
- **Compatibility** (OpenGL ES 3.0 / WebGL 2). Official docs recommend it for older or low-end devices.

Mobile stability work from 4.4 to 4.6 focused on driver crashes (Mali/Adreno). Public performance data for mid-range Android is thin and anecdotal. 4.7 added a native `VirtualJoystick` node. Decals are **not** supported in Compatibility until 4.8.

### Cited Findings
**Renderer feature matrix (4.7 docs)**
- **Decals:** Compatibility *not supported*; Mobile and Forward+ supported. — [Overview of renderers](https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html)
- **Lights:** Mobile allows 8 Omni/Spot lights per mesh and 256 per view. Compatibility allows 8 per mesh.
- **SSAO:** Compatibility yes, Mobile **no**.
- **Not available on either Mobile or Compatibility:** volumetric fog, SSR, SSS, VoxelGI/SDFGI/SSIL.
- **PCSS:** Mobile supports it on Omni/Spot lights only. Compatibility does not support it, and its shadowed lights use multi-pass with less accurate blending.
- **ReflectionProbe:** Compatibility allows 2 per mesh, Mobile 8.
- **MSAA:** Compatibility supports it in 3D only.
- **Compute shaders:** Compatibility no; Mobile "supported, with a penalty on older devices".

[Overview of renderers](https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html)

**Renderer guidance and cost (4.7 docs)**
- The docs describe Mobile as "Fewer features, but renders simple scenes faster" but slower than Compatibility on old/low-end hardware. Its mobile support is listed as "Yes (high-end)".
- Compatibility is recommended for "older mobile devices" and is the only option for web. Forward+ on mobile is described as "poorly optimized".
- Cost model: Compatibility has a low base cost and high scaling cost; Mobile is medium on both. — [Overview of renderers](https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html)

**Renderer internals**
- The Mobile renderer is a single-pass-lighting forward renderer that uses sub-passes for tile-based GPUs. Glow and DoF, and anything that reads screen or depth textures, force a full write-out with "a notable performance penalty".
- Mobile defaults to the R10G10B10A2 format, and its light limits are hardcoded.
- "Compute shaders have very limited or no support on mobile GPUs", so the Mobile renderer uses raster shaders only.
- Compatibility has no HDR, and most post-processing is unavailable. — [Internal rendering architecture (4.7)](https://docs.godotengine.org/en/stable/engine_details/architecture/internal_rendering_architecture.html)

**Mobile changes by version**
- **4.4:**
  - Forward+ and Mobile automatically fall back to Compatibility on devices without Vulkan/D3D12/Metal (project-setting toggle).
  - Android gained **Swappy frame pacing**.
  - A per-material **vertex shading** option was added "to target lower-end devices".
  - **Ubershaders** were added to reduce shader-compile stutter.
  - 3D physics interpolation lets mobile games "lower the tick rate without compromising on smoothness". — [4.4 release page](https://godotengine.org/releases/4.4/)
- **4.5:**
  - The Mobile renderer explicitly requests **FP16** where the hardware supports it.
  - A **shader baker** pre-compiles shaders at export; the TPS demo showed a 20× load-time decrease on Metal and D3D12.
  - Android gained 16 KB page support "out of the box", an edge-to-edge export option and camera feed access. — [4.5 release page](https://godotengine.org/releases/4.5/)
- **4.6:**
  - "Mobile renderer (Vulkan) crash fixes" for certain Mali and Adreno GPUs.
  - Octahedral reflection/radiance probes reduce compute and memory cost.
  - Compressed textures are typically 4–6× smaller. — [4.6 release page](https://godotengine.org/releases/4.6/)
- **4.7:**
  - The Vulkan Mobile renderer gained subsampled images for foveated rendering. The release page says it "matches or even outperforms" Compatibility in some benchmarks, in the XR context.
  - HDR output was added, including iOS.
  - Perfetto is the default Android tracing tool. — [4.7 release page](https://godotengine.org/releases/4.7/)

**Official mobile update (Godot Foundation, 11 Apr 2026)**
- About **49% of Godot developers target mobile**.
- Foundation contractors fixed Vulkan API usage and found workarounds for broken GPU drivers. Crash rates for *Kamaeru: A Frog Refuge* and *Rift Riff* fell from "~4%" to "less than 1%".
- Android spans "more than 12,000 different devices". Testing on Firebase Test Lab is limited by its free tier. — [Godot mobile update, Apr 2026](https://godotengine.org/article/godot-mobile-update-apr-2026/)

**Mid-range Android performance data (all anecdotal or bug-report grade)**
- The FP16 PR (#107119) reported these GPU frame times:
  - Mali-G78: about 24.6 → 24.2 ms
  - Mali-G715: about 17.3 → 16.6 ms
  - Adreno 640: about 10% frame-time gain in the TPS demo — [GH PR #107119](https://github.com/godotengine/godot/pull/107119) (figures via search summary; PR not opened directly)
- Issue #123633 reports a Samsung Galaxy A35 (Mali-G68) at about **80–90 FPS** in the Mobile renderer, "matching Unity's Vulkan renderer" for the same scene. Setting 3D scaling to 0.7 *dropped* FPS to 48–50; the issue is open, so this is likely a bug. — [GH issue #123633](https://github.com/godotengine/godot/issues/123633) (via search summary)
- Issue #109251 reports a Mali-G52 MC2 on the Mobile renderer:
  - 60 FPS on 4.4.dev3, about 45 FPS from 4.4.dev4 onward.
  - Maintainer clayjohn judged it "almost certain[ly]" Swappy pacing, which halves a 90 Hz panel's rate when the game can't hold full rate.
  - Closed in Oct 2025 after the reporter moved to Android 15. — [GH issue #109251](https://github.com/godotengine/godot/issues/109251)
- A forum user on a Mali-G610 MC6 reported a 3D scene at about 15–20 FPS (no project details). — [Godot Forum](https://forum.godotengine.org/t/now-im-worried-performance-on-android/124716)

**iOS / Metal**
- A native Metal backend was added in 4.4, initially limited to Apple Silicon. MetalFX upscaling is an option. — [4.4 release page](https://godotengine.org/releases/4.4/)
- Metal 4 is used on iOS 26+ and macOS 26+ "when supported" (since 4.7), with fallback to Metal 3. MoltenVK is used when native Metal is unavailable. — [Internal rendering architecture](https://docs.godotengine.org/en/stable/engine_details/architecture/internal_rendering_architecture.html)
- The 4.5.2 notes say iOS exports using Metal default to restricting support to A12 or newer devices. — [4.5.2 RC1 notes](https://godotengine.org/article/release-candidate-godot-4-5-2-rc-1/) (via search summary)
- 4.7 moved iOS controllers to SDL3 mappings. — [4.7 release page](https://godotengine.org/releases/4.7/)

**UI (Control) changes relevant to portrait and landscape**
- 4.5: `FoldableContainer` (accordion), recursive focus/mouse behavior overrides, and experimental AccessKit screen-reader support. — [4.5 release page](https://godotengine.org/releases/4.5/)
- 4.6: `Control.pivot_offset_ratio`, which keeps the pivot proportional while the control resizes. — [4.6 release page](https://godotengine.org/releases/4.6/)
- 4.7: `Control` `offset_transform_*` (translate, rotate or scale without container interference), `PopupMenu` search, and `TextureRect` nine-patch tiling of `AtlasTexture`. — [4.7 release page](https://godotengine.org/releases/4.7/)
- [4.8 beta]: `Label`/`RichTextLabel` resize-to-fit through `auto_font_size`/`min_font_size`/`max_font_size` (GH-116791). — [4.8 beta 1](https://godotengine.org/article/dev-snapshot-godot-4-8-beta-1/)

**Touch and VirtualJoystick (4.7)**
- `VirtualJoystick` inherits `Control`. It is in the 4.7 stable class reference and not marked experimental. It came from GH-110933 by Kazox61.
- **Properties:** `action_up/down/left/right` (default `ui_*`), `deadzone_ratio`, `clampzone_ratio`, `joystick_size` (100 px), `tip_size` (50 px) and `initial_offset_ratio`.
- **Modes:** `joystick_mode` is `JOYSTICK_FIXED`, `JOYSTICK_DYNAMIC` or `JOYSTICK_FOLLOWING`. `visibility_mode` is `ALWAYS` or `WHEN_TOUCHED`.
- **Signals:** `pressed`, `released(input_vector)`, `tapped`, `flicked(input_vector)` and `flick_canceled`.
- **Theme properties (StyleBox):** `normal_joystick`, `normal_tip`, `pressed_joystick`, `pressed_tip`.
- It drives named InputMap actions rather than exposing a polled Vector2. — [VirtualJoystick class ref (4.7)](https://docs.godotengine.org/en/stable/classes/class_virtualjoystick.html); [GameFromScratch on 4.7 dev1/dev2](https://gamefromscratch.com/godot-4-7-dev1-and-dev2-released/)
- A community addon was renamed "Virtual Joystick CF" to avoid clashing with the native node. — [Asset library edit](https://www.godotengine.org/asset-library/asset/edit/23272)
- [4.8 beta] touch changes:
  - **Breaking:** fixes duplicated button press events on touch input (GH-120864).
  - Native touch for `TextEdit`/`CodeEdit` (GH-119706), `TabBar` (GH-122960) and `PopupMenu` (GH-123576).
  - AccessKit on Android (GH-117785) and iOS (GH-119750). — [4.8 dev 7](https://godotengine.org/article/dev-snapshot-godot-4-8-dev-7/); [4.8 beta 1](https://godotengine.org/article/dev-snapshot-godot-4-8-beta-1/)

### Inferences
- For a 2-fighter 3D scene on Snapdragon 6/7-series or Mali-G6x/G7x phones, the **Mobile renderer** is the likely choice: it supports decals and per-mesh lights, and Vulkan has been stabilized since 4.6. Keep **Compatibility as the automatic fallback** for non-Vulkan devices (4.4+). Any look that depends on decals or SSAO will differ between the two paths.
- Swappy frame pacing can lock to half the refresh rate (for example 45 FPS on a 90 Hz panel) when a frame budget is missed. A fighting game should budget for a hard 60 FPS on the lowest target device and test with the `swappy_mode` settings.
- Portrait and landscape layout uses the standard Control anchors/containers plus stretch settings. **[general knowledge, not re-verified this session]**: `InputEventScreenTouch`/`InputEventScreenDrag` with per-finger `index` carry multitouch and are long-standing Godot 4 classes.
- The "duplicated button press on touch" bug fixed in 4.8 (GH-120864) suggests 4.7 touch-button handling has a known double-fire issue. Verify on device before relying on `Button` for fight inputs.

### Gaps
- I found no controlled Godot benchmark on Snapdragon 6-series or 7-series (Adreno 6xx/7xx) phones, and no published case study of a 3D fighting game's frame time on mid-range Android.
- Which rendering driver is the default for iOS exports in 4.7 (native Metal vs MoltenVK) was not explicitly confirmed. The evidence (A12+ Metal restriction, Metal 4 on iOS 26) suggests Metal.
- The multiple-resolutions and `InputEventScreenTouch` docs were not fetched this session.

## 2. Runtime skeletal animation: retargeting, SkeletonModifier3D family, IK, AnimationTree, fixed-tick logic, Jolt

### Takeaway
Godot now has a substantial **runtime** skeleton-modifier stack:
- `RetargetModifier3D` (4.4) for realtime retargeting with original rests kept
- `LookAtModifier3D` and `SpringBoneSimulator3D` (4.4)
- Bone constraints: `AimModifier3D`/`CopyTransformModifier3D`/`ConvertTransformModifier3D` (4.5)
- A new IK framework, `IKModifier3D` with `TwoBoneIK3D`/`FABRIK3D`/`CCDIK3D`/`JacobianIK3D`/`SplineIK3D` (4.6)

`SkeletonIK3D` is deprecated. Physics runs at a fixed tick (default 60 Hz), and `AnimationMixer` can be stepped manually. Jolt is built in and is the default for new 3D projects (4.6). Godot itself makes **no determinism guarantees**.

### Cited Findings
**Retargeting**
- `RetargetModifier3D` (PR #97824, by TokageItLab, merged 26 Nov 2024, milestone **4.4**) does "realtime retarget to keep original rest". The parent skeleton uses the SkeletonProfile rest; the child skeleton keeps its DCC rest and carries the modifier.
- The importer gained an option to use it, which requires Rename Bone.
- **Use Global Pose on:** requires exactly equal bone lengths; a zero-length dummy bone can bridge rigs with different bone counts.
- **Use Global Pose off:** retargets position, rotation and scale separately and tolerates different bone lengths.
- A child Skeleton that is not a direct child of the modifier was not supported. — [GH PR #97824](https://github.com/godotengine/godot/pull/97824)
- 4.7 class ref: properties `enable` (TransformFlag bitfield, default 7), `profile` (SkeletonProfile, used for name-matched bone lists) and `use_global_pose`. The modifier "overwrites the child's mapped bone pose", so later edits need another SkeletonModifier3D on the target. — [RetargetModifier3D class ref](https://docs.godotengine.org/en/stable/classes/class_retargetmodifier3d.html)

**SkeletonModifier3D family**
- 4.4 added `LookAtModifier3D`, "partially replacing the deprecated SkeletonIK3D", and `SpringBoneSimulator3D` (VRM-style jiggle on SkeletonModifier3D). AnimationTree supports animation markers. — [4.4 release page](https://godotengine.org/releases/4.4/)
- `SpringBoneSimulator3D` (4.7 ref) inherits SkeletonModifier3D. Its settings:
  - Chains defined from a root bone to an end bone, with stiffness, drag, gravity (treated as a velocity), radius and damping curves.
  - Per-joint config through `set_individual_config()`, plus `external_force`.
  - Collision via child `SpringBoneCollision3D` nodes that are independent of PhysicsServer3D.

  Limitations:
  - No branched chains.
  - Scaled skeletons or bones "may not behave as expected".
  - Twist is not modeled. — [SpringBoneSimulator3D class ref](https://docs.godotengine.org/en/stable/classes/class_springbonesimulator3d.html)
- 4.5 added `BoneConstraint3D` with `AimModifier3D`, `CopyTransformModifier3D` and `ConvertTransformModifier3D`: "it is now possible to bind bones to other bones". — [4.5 release page](https://godotengine.org/releases/4.5/)

**IK**
- 4.6: "IK is back". `IKModifier3D` is built on SkeletonModifier3D, with solvers `TwoBoneIK3D`, `SplineIK3D`, `FABRIK3D`, `CCDIK3D` and `JacobianIK3D`.
- It adds constraints for joint twist and angular velocity, and "animation constraints can target 3D nodes". The release page noted that documentation was still in progress. — [4.6 release page](https://godotengine.org/releases/4.6/)
- 4.7 class ref: `IKModifier3D` direct subclasses are `ChainIK3D` and `TwoBoneIK3D`. `mutable_bone_axes` defaults to true; setting it to false caches axes from rest, which is faster. A tutorial, "Inverse Kinematics Returns to Godot 4.6", covers seven child classes. — [IKModifier3D class ref](https://docs.godotengine.org/en/stable/classes/class_ikmodifier3d.html)
- A community write-up says the Jacobian solver is costly to run every frame. — [TabNews](https://www.tabnews.com.br/zivaengine/godot-4-6-trouxe-o-ik-de-volta-pra-quem-faz-jogo-3d-isso-importa-mais-que-o-jolt) (community source)
- `SkeletonIK3D` is **deprecated** in 4.7: "This class may be changed or removed in future versions". For its `interpolation` property the docs say to use `SkeletonModifier3D.influence` instead. — [SkeletonIK3D class ref](https://docs.godotengine.org/en/stable/classes/class_skeletonik3d.html)
- [4.8 beta] breaking changes:
  - The inverted return value of `LookAtModifier3D.is_interpolating()` is fixed (GH-121391).
  - Bone Follower classes now default FTI off (GH-119509).
  - Makima interpolation was added (GH-123835). — [4.8 beta 1](https://godotengine.org/article/dev-snapshot-godot-4-8-beta-1/); [4.8 dev 7](https://godotengine.org/article/dev-snapshot-godot-4-8-dev-7/)

**AnimationPlayer/AnimationTree stepping (for fixed-tick fighting logic)**
- `AnimationMixer` is the base of AnimationPlayer and AnimationTree. Its `callback_mode_process` is `PHYSICS` (0), `IDLE` (1, default) or `MANUAL` (2: "Do not process animation. Use advance() to process the animation manually").
- `deterministic` (default false) makes blending use a non-normalized deterministic algorithm.
- Root motion is available through `root_motion_track` and `get_root_motion_position()`. — [AnimationMixer class ref](https://docs.godotengine.org/en/stable/classes/class_animationmixer.html)
- `Skeleton3D.modifier_callback_mode_process` can be `PHYSICS`, `IDLE` (default) or `MANUAL`. The `skeleton_updated` signal fires after all SkeletonModifier3D processing completes. — [Skeleton3D class ref](https://docs.godotengine.org/en/stable/classes/class_skeleton3d.html)

**Fixed tick and determinism**
- Physics runs at a fixed `physics_ticks_per_second`, default **60**. Physics interpolation decouples render from tick at a cost of 1–2 ticks of display lag.
- The docs warn that changing the tick rate changes behavior and that variable tick rates make bugs hard to reproduce. — [Physics interpolation intro](https://docs.godotengine.org/en/stable/tutorials/physics/interpolation/physics_interpolation_introduction.html)
- 4.5 moved 3D physics interpolation to SceneTree. — [4.5 release page](https://godotengine.org/releases/4.5/)

**Jolt**
- Jolt was added experimentally in 4.4 and is the **default for new 3D projects since 4.6**; existing projects keep their engine. — [4.4 release page](https://godotengine.org/releases/4.4/); [4.6 release page](https://godotengine.org/releases/4.6/)
- Differences from the GodotPhysics backend:
  - Some joint properties are unsupported (bias/softness/etc.).
  - Kinematic contacts are not reported by default.
  - `face_index` is -1 unless enabled.
  - Run-on-separate-thread is supported but labeled experimental. — [Using Jolt Physics (4.7)](https://docs.godotengine.org/en/stable/tutorials/physics/using_jolt_physics.html)
- **The Godot Jolt docs make no determinism statements.** — [Using Jolt Physics (4.7)](https://docs.godotengine.org/en/stable/tutorials/physics/using_jolt_physics.html)
- **Jolt upstream on determinism:**
  - The simulation is deterministic only if mutating APIs are called "in exactly the same order" and "the same binary code is used".
  - Cross-platform determinism needs the `CROSS_PLATFORM_DETERMINISTIC` CMake option, which is about 8% slower.
  - Listener callbacks arrive in non-deterministic order.
  - `SaveState`/`RestoreState` support rollback, but not when bodies are added or removed during replayed frames. — [Jolt Physics docs](https://jrouwe.github.io/JoltPhysics/index.html)
- [4.8 beta]: Jolt updated to 5.6.0 (GH-121260), plus non-allocating space queries (`intersect_ray_into`, `cast_motion_into`, GH-113970). — [4.8 beta 1](https://godotengine.org/article/dev-snapshot-godot-4-8-beta-1/)
- A third-party .NET addon, "Klotho", offers deterministic simulation with 32.32 fixed-point math, rollback and a deterministic physics module (Godot 4.4+ .NET). — [Godot Asset Store: Klotho](https://store.godotengine.org/asset/xpturn/xpturn-klotho/)

### Inferences
- **Runtime retargeting between differing rigs exists in stable** through `RetargetModifier3D`, but it is name-mapped through a SkeletonProfile (for example `SkeletonProfileHumanoid`). Every fighter rig would need bone names mapped to one profile (import-time BoneMap or renamed bones). Rigs with extra or missing bones need care (`use_global_pose` off, or dummy bones).
- For frame-exact fighting logic, the safe pattern is:
  - Run game state (hitboxes, frame data, inputs) in your own integer/fixed-point simulation stepped from `_physics_process` at 60 Hz.
  - Drive `AnimationTree` in `MANUAL` mode with `advance(1/60)` per sim tick.
  - Use Jolt only for cosmetic physics.

  Jolt's determinism depends on the build flags and call order. Godot's build flags for its bundled Jolt are not documented, so it cannot be assumed deterministic across devices.
- `SpringBoneSimulator3D` suits hair, cloth tails and accessories on fighters. Rewinding it during rollback would need custom state handling **[inference]**.

### Gaps
- I did not confirm whether Godot's bundled Jolt is compiled with `CROSS_PLATFORM_DETERMINISTIC`.
- I found no performance numbers for SkeletonModifier3D stacks (IK + spring bones + retarget) on mobile.
- The full IKModifier3D tutorial page was not fetched, so the exact solver class tree in 4.7 is only partly confirmed (`ChainIK3D` and `TwoBoneIK3D` are listed as direct subclasses).

## 3. Creation-suite features: runtime GLB, attachments, morphs, blend shapes, decals, materials, hidden-polygon culling

### Takeaway
Runtime glTF/GLB load and save, BoneAttachment3D, per-bone pose scale, blend shapes and per-surface material overrides are all stable APIs. **Decals do not work in Compatibility in 4.7** (they arrive in 4.8 beta). Decals are projected rather than skinned, so the docs say nothing about them following animated characters. I found no built-in hidden-polygon (body-under-clothing) culling feature.

### Cited Findings
**Runtime glTF**
- Runtime glTF 2.0 loading and saving is supported in exported projects through `GLTFDocument.append_from_file()` or `append_from_buffer()` into a `GLTFState`, then `generate_scene()`. Saving uses `append_from_scene()` with `write_to_filesystem()`/`generate_buffer()`.
- `.glb` is preferred because it is "faster to write and smaller". Buffer loads need `GLTFState.base_path` set for external textures.
- FBX loads at runtime through `FBXDocument` (4.3+) but cannot be saved.
- The docs warn not to use runtime loading for resources that are part of the project, because it is less efficient and bypasses the import pipeline. — [Runtime file loading and saving](https://docs.godotengine.org/en/stable/tutorials/io/runtime_file_loading_and_saving.html)

**Bones and attachments**
- `BoneAttachment3D` follows or overrides a bone (`bone_name`, `bone_idx`, `override_pose`, `use_external_skeleton`/`external_skeleton`). The docs warn that `override_pose` is an older signal-based design that "can cause unexpected behavior" alongside SkeletonModifier3D. — [BoneAttachment3D class ref](https://docs.godotengine.org/en/stable/classes/class_boneattachment3d.html)
- `Skeleton3D` provides `set_bone_pose_scale`, `set_bone_pose_position`, `set_bone_pose_rotation`, `set_bone_rest`, `reset_bone_poses`, `register_skin` and `create_skin_from_rest_transforms`.
- `get_bone_global_pose` may be overridden by modifiers later in the frame, so read the final value from `SkeletonModifier3D.modification_processed`.
- The global-pose-override methods are deprecated. — [Skeleton3D class ref](https://docs.godotengine.org/en/stable/classes/class_skeleton3d.html)

**Blend shapes and materials**
- `MeshInstance3D` provides `set_blend_shape_value`, `find_blend_shape_by_name`, `get_blend_shape_count`, `set_surface_override_material`, `get_active_material` and `skin`.
- The default of the `skeleton` property changed in 4.6.
- `bake_mesh_from_current_skeleton_pose` ignores blend shapes. — [MeshInstance3D class ref](https://docs.godotengine.org/en/stable/classes/class_meshinstance3d.html)

**Decals**
- Decals work in Forward+ and Mobile only, not Compatibility; the docs suggest Sprite3D for flat surfaces there.
- **Mobile renderer limit:** "only 8 decals can be applied on each individual Mesh resource".
- Decals cannot use custom shaders and affect only albedo, normal, ORM and emission.
- `cull_mask` limits which layers receive them.
- The page does **not** discuss skinned or animated meshes. — [Using decals](https://docs.godotengine.org/en/stable/tutorials/3d/using_decals.html)
- [4.8 beta]: **Decal support in the Compatibility renderer (GH-118070)** and **animated decals (GH-115653)**. — [4.8 beta 1](https://godotengine.org/article/dev-snapshot-godot-4-8-beta-1/)

**Texture painting**
- 4.7 added `DrawableTexture2D`, "a simpler API for drawing on textures" that replaces Viewport or RenderingDevice workarounds. — [4.7 release page](https://godotengine.org/releases/4.7/)

### Inferences
- Godot `Decal` is a box projector. On an animating fighter, a projected tattoo or logo would slide over the skin unless the decal is parented to a bone through `BoneAttachment3D`, and it would still distort at joints. **[inference: docs silent]** For tattoos, face paint and logos in a creation suite, painting into the character's texture (`DrawableTexture2D` in 4.7, or a SubViewport) is more robust and renderer-independent. It also avoids the Mobile 8-decals-per-mesh cap and the missing Compatibility decals in 4.7.
- **Body morphs:** `set_bone_pose_scale` scales child bones too in a standard bone hierarchy **[general knowledge, docs silent]**. Non-propagating morphs ("thicker arm without longer hand") need either blend shapes or helper or twist bones in the rig. RetargetModifier3D handles separate position, rotation and scale per bone when `use_global_pose` is off.
- **Hidden-polygon culling** (hiding body under clothing) has no engine feature. The options are:
  - split the body into per-region surfaces or meshes and toggle visibility or material per surface
  - an alpha-scissor mask texture on the body material driven by the equipped outfit

  These are design patterns, not sourced features.
- **Runtime GLB** is fine for user-imported parts. For a shipped roster, prefer pre-imported scenes or resources in the PCK so textures are VRAM-compressed at import (see section 6).

### Gaps
- I did not verify which texture format `GLTFDocument` produces for textures loaded at runtime on Android (uncompressed RGBA8 vs a compressed or Basis option). This matters for memory.
- I found no source on decal behavior on skinned meshes, or on blend-shape and skinning cost in the Compatibility renderer beyond issue #88954 (section 6).
- `ShaderMaterial` runtime parameter APIs were not re-fetched this session (standard API).

## 4. Headless CLI builds in Linux CI, text scene formats, web export

### Takeaway
Godot has a well-documented headless export path:
- `godot --headless --export-release "<preset>" <path>`
- export templates installed for the editor
- `--install-android-build-template` for Gradle builds
- keystore environment variables

`.tscn`/`.tres` are readable, diffable INI-like text that agents can edit. Web export is WebGL 2 through the Compatibility renderer only, with single-threaded export as the default.

### Cited Findings
**Export commands**
- `--export-release <preset> <path>` exports in release mode; the preset must match `export_presets.cfg`. It is available in editor builds only, and the target directory must exist.
- `--export-debug` is the same but uses the debug template and implies `--import`. `--export-pack` writes PCK or ZIP only. `--export-patch` with `--patches` writes changed files only.
- `--install-android-build-template` is "Used in conjunction with `--export-release` or `--export-debug`".
- `--headless` "is **required** on platforms that do not have GPU access", which covers CI.
- The binary must be the editor, and templates must be installed or a custom template set in the preset.
- Relative paths resolve against the `project.godot` directory, not the CWD. — [Command line tutorial](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html)

**Android toolchain**
- Recommended toolchain: **OpenJDK 17** (higher supported), Platform-Tools 35.0.0+, Build-Tools 35.0.1, Platform 35, CMake 3.10.2.4988404 and NDK r28b (28.1.13356709). Do not use distro SDK packages on Linux.
- Signing can be set through environment variables: `GODOT_ANDROID_KEYSTORE_RELEASE_PATH`/`_USER`/`_PASSWORD` (and the `_DEBUG_` equivalents) plus `GODOT_SCRIPT_ENCRYPTION_KEY`.
- The keystore password and key password currently **must be the same**.
- C# on Android is still "experimental". — [Exporting for Android](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html)
- 4.7 added a per-platform and per-architecture export template downloader. GABE (on-device Gradle builds) is now stable. — [4.7 release page](https://godotengine.org/releases/4.7/)
- [4.8 beta]: one-click Android and Java SDK download and management in the editor (GH-121849), and Android AAR export (GH-123574). — [4.8 beta 1](https://godotengine.org/article/dev-snapshot-godot-4-8-beta-1/); [4.8 dev 7](https://godotengine.org/article/dev-snapshot-godot-4-8-dev-7/)

**Text scene format**
- The format is "mostly human-readable and easy for version control systems to manage". Sections: `[gd_scene format=3 uid=...]`, then `ext_resource`, `sub_resource`, `node`, `connection`.
- Nodes carry `unique_id` in scenes saved with 4.6+. `load_steps` is deprecated.
- Hand-editing caveats:
  - Comments (`;`) and extra whitespace are discarded on save.
  - Properties equal to their defaults are dropped.
  - A scene needs exactly one root node.
  - Sub-resources must be declared before use. — [TSCN file format](https://docs.godotengine.org/en/stable/engine_details/file_formats/tscn.html)
- 4.6 added unique node IDs, so renaming or moving nodes is safer; older scenes need re-saving through Upgrade Project Files. — [4.6 release page](https://godotengine.org/releases/4.6/)
- [4.8 beta]: "Cleaner diffs for serialized objects (GH-92102)" and "Metadata in text scenes (GH-121920)". — [4.8 beta 1](https://godotengine.org/article/dev-snapshot-godot-4-8-beta-1/)

**Web export**
- Renderer: WebGL 2.0 through Compatibility only; "WebGPU is not yet available". Safari has WebGL 2 issues, so Chromium or Firefox is recommended.
- Threads need SharedArrayBuffer with COOP `same-origin` and COEP `require-corp`, or the PWA service-worker workaround.
- Since 4.3, **single-threaded export is the default**. It is more compatible (itch.io, Poki, CrazyGames, macOS/iOS) but slower.
- **C# projects cannot export to web.**
- Native mobile exports "perform significantly better" than web on phones.
- `.wasm` gzips to about a quarter of its size. — [Exporting for the Web](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html)
- 4.5 enabled WebAssembly SIMD by default. — [4.5 release page](https://godotengine.org/releases/4.5/)

### Inferences
- A Linux CI job needs:
  - the Godot 4.7.x editor binary plus matching export templates (`.tpz`)
  - JDK 17 and the Android SDK/NDK at the versions above
  - an `export_presets.cfg` committed to the repo (secrets passed through `GODOT_ANDROID_KEYSTORE_*` environment variables, not committed)
  - `godot --headless --path . --import`, then `--export-release "Android" build/game.apk`
  - for Gradle builds, add `--install-android-build-template` on first run
- AI agents can safely shell-edit `.tscn`/`.tres`, with two caveats: the editor normalizes the file on next save (strips comments and defaults), and UIDs and `unique_id`s must be kept consistent.
- A web build of the same project would lose decals (until 4.8) and Mobile-only effects. It is a demo or preview channel, not a parity target.

### Gaps
- I found no official CI recipe (for example a GitHub Actions template) in the docs. Community actions exist but were not evaluated.
- I did not verify mobile-browser (iOS Safari, Android Chrome) frame rates for Godot 4 web exports.

## 5. Added criterion: direct sideloaded APK (no store), signing, APK vs AAB, Gradle vs non-Gradle, install size

### Takeaway
For sideloading, the **default non-Gradle export already produces a signed, installable `.apk`** from Godot's prebuilt template. AAB and Gradle builds are only needed for Google Play or for native plugins and SDKs. Sign release builds with your own keystore through the preset or the `GODOT_ANDROID_KEYSTORE_RELEASE_*` variables. Ship arm64-only to keep size down. A minimal Godot 4 APK is roughly **13–19 MB**; this is anecdotal and from the 4.0–4.2 era.

### Cited Findings
**APK vs AAB, Gradle vs non-Gradle**
- AAB is required for Google Play uploads (since Aug 2021). **AAB export requires Gradle builds.** — [Exporting for Android](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html)
- A Gradle build installs an Android Java project at `res://android/build` and builds a fresh template on each export. It is useful for "Exporting an AAB file for Google Play", modifying the project, and "Adding external SDKs".
- Underscore-prefixed folders are excluded from the APK. — [Gradle builds for Android](https://docs.godotengine.org/en/stable/tutorials/export/android_gradle_build.html)

**Export options (EditorExportPlatformAndroid)**
- `gradle_build/use_gradle_build`: "Gradle build is used instead of pre-built APK".
- `gradle_build/export_format`: APK or AAB.
- `gradle_build/min_sdk` and `target_sdk`.
- `architectures/arm64-v8a`, `armeabi-v7a`, `x86`, `x86_64`.
- `package/signed`.
- `keystore/debug*` falls back to `EditorSettings.export/android/debug_keystore*` when empty.
- `keystore/release*` can be overridden by `GODOT_ANDROID_KEYSTORE_RELEASE_*` environment variables. — [EditorExportPlatformAndroid class ref](https://docs.godotengine.org/en/stable/classes/class_editorexportplatformandroid.html)

**Signing a release build**
- Generate a keystore with `keytool -v -genkey -keystore mygame.keystore -alias mygame -keyalg RSA -validity 10000`.
- Fill in Release, Release User and Release Password in the preset, and **uncheck "Export With Debug"** for release.
- The keystore and key passwords must currently match. — [Exporting for Android](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html)

**Install size**
- By default the APK includes both ARMv7 and ARMv8 libraries; unchecking `armeabi-v7a` leaves only arm64. A custom export template with only the needed features shrinks it further. — [Exporting for Android](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_android.html) (via search summary of the 4.x docs)
- Forum anecdotes (Godot 4.0–4.2 era, unverified):
  - A standard Godot 4 export is "about 19mb"; stripping most modules gives about 13 MB.
  - A project with about 9 MB of assets produced a **36 MB standard** vs **77 MB Gradle** APK, with the same installed size when arm64 only. — [Godot Forum thread](https://forum.godotengine.org/t/game-size-too-big-compared-to-apk/39416)
- Size-reduction build options:
  - `disable_3d` (about 15%, not usable here)
  - `optimize=size` / `size_extra` (4.5+)
  - `lto=full`
  - `build_profile`
  - disabling the advanced text server and unused modules
  - stripping (5–10×; use `debug_symbols=no` on Android) — [Optimizing a build for size](https://docs.godotengine.org/en/stable/engine_details/development/compiling/optimizing_for_size.html)
- 4.6 added **patch PCKs with delta encoding** ("patches contain only changed parts of resources"). — [4.6 release page](https://godotengine.org/releases/4.6/)

### Inferences
- **Recommended sideload path:**
  1. Non-Gradle export.
  2. `export_format` = APK, `arm64-v8a` only.
  3. Release template, signed with a project-owned release keystore kept out of the repo and supplied through CI environment variables.
  4. `godot --headless --export-release "Android" build/westernheart.apk`

  The debug keystore path works for internal testing only.
- **[general Android platform knowledge, not sourced this session]:**
  - Android only installs an update over an existing install when it is signed with the *same* key. Losing the release keystore strands every sideloaded user, so back it up.
  - Users must allow "install unknown apps" for the source app.
  - Play Protect may warn on unknown-signer APKs.
- The roster's assets (section 6), not the engine, will dominate APK size. The engine base is about 15–20 MB arm64.
- Patch PCKs (4.6) plus `ProjectSettings.load_resource_pack` could deliver content updates (new fighters) as small downloads without reinstalling the APK. **[inference: needs testing]**

### Gaps
- No measured 4.7 APK size for a minimal 3D project was found. Measure it by exporting an empty 3D scene, arm64 only.
- I did not confirm whether 4.7 auto-generates a debug keystore on first export (the class ref does not say).

## 6. Added criterion: memory and streaming for 50+ fighters (59 roster entries, ~100 skinned GLB models) on mid-range phones

### Takeaway
Godot provides:
- VRAM texture compression: ETC2 by default on mobile, ASTC in high-quality mode, about 4–6× savings
- threaded background loading through `ResourceLoader.load_threaded_*`
- mesh LOD
- [4.8 beta] **mip-level texture streaming**

A fighting game only needs 2 fighters resident in battle, so the large roster is a loading and streaming problem, not a rendering one. The key risks are:
- uncompressed textures from runtime-loaded GLBs
- the select or creation screen trying to keep many full models resident
- Compatibility-renderer skinning cost (open issue #88954)

### Cited Findings
**Texture compression**
- VRAM Compressed textures are smaller "usually by a factor between 4 and 6".
- Default mobile and web format is ETC2. With High Quality enabled, ASTC is used on mobile, but **high-quality compression is always disabled in the Compatibility renderer**.
- RGBA8 with mipmaps:

  | Size | Lossless | VRAM Compressed |
  |---|---|---|
  | 1024² | 5.33 MiB | 1.33 MiB |
  | 2048² | 21.33 MiB | 5.33 MiB |
  | 4096² | 85.33 MiB | 21.33 MiB |

- Mipmaps add about 33%.
- Textures larger than 4096² "usually can't be displayed" on mobile and web; Size Limit caps them at import.
- Basis Universal gives very small files with VRAM use similar to VRAM Compressed, at lower quality. — [Importing images](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_images.html)

**Loading and streaming**
- Background loading uses `ResourceLoader.load_threaded_request(path)`, then `load_threaded_get_status(path, progress)` and `load_threaded_get(path)`. `load_threaded_get()` **blocks** if loading hasn't finished. — [Background loading](https://docs.godotengine.org/en/stable/tutorials/io/background_loading.html)
- [4.8 beta]: **Mip-level texture streaming** (GH-113429) "loads only the needed mipmap level to reduce VRAM use", plus ASTC 6x6 and high-quality compression profiles (GH-115003, breaking). — [4.8 beta 1](https://godotengine.org/article/dev-snapshot-godot-4-8-beta-1/)
- Runtime glTF loading bypasses the import pipeline and is "less efficient"; it is not recommended for resources that are part of the project. — [Runtime file loading and saving](https://docs.godotengine.org/en/stable/tutorials/io/runtime_file_loading_and_saving.html)

**Skinning cost**
- Issue #88954, "`Skeleton3D` Animation performance is terrible on OpenGL" (open, confirmed, still reproduced on 4.5 beta):
  - About 100 animated skeletons ran at about 20 FPS on GLES3 vs over 100 FPS on Vulkan (RTX 4090 desktop).
  - An Android debug build on a Xiaomi Mi 10T Pro hit **28 FPS**.
  - Maintainer TokageItLab blamed "the Skeleton skin deformation process, not the Animation playback process". Calinou called the fix "nontrivial" because GLES3 calls stay on the main thread.
  - Suggested workarounds: stagger animation updates, pause distant characters, use impostors. — [GH issue #88954](https://github.com/godotengine/godot/issues/88954)

### Inferences
- **Back-of-envelope VRAM per fighter**, assuming albedo plus normal at 2048² each, VRAM-compressed with mips (2 × 5.33 MiB from the import table):
  - about 10.7 MiB of textures per fighter, before ORM or attire layers and mesh/skin buffers
  - all ~100 models resident would be about 1 GiB of textures alone, which is unrealistic on 4–6 GB-RAM mid-range phones
  - 2 fighters in battle plus 1–4 in a creation or preview scene is roughly 20–50 MiB, which is comfortable

  These figures are derived from the cited table; the asset assumptions are mine.
- **Recommended pattern:**
  - Ship the roster as pre-imported, VRAM-compressed scenes in the PCK, not raw GLBs loaded at runtime.
  - Use 2D portraits or low-poly LOD thumbnails for the 59-entry select grid.
  - `load_threaded_request` the two picked fighters during the VS screen.
  - Free them after the match.
  - Consider 1024² character textures on low-tier devices through feature tags or Size Limit.
- Prefer the Mobile (Vulkan) renderer for skinned characters on supported devices, given issue #88954's GLES3 skinning bottleneck. Two skinned fighters are far below the ~100-skeleton stress case, so Compatibility fallback should still hold 60 FPS **[inference: verify on device]**.
- Mip-level texture streaming in 4.8 would directly help a 100-model roster. That is a reason to target 4.8 once stable.

### Gaps
- I found no measured RAM or VRAM figures for Godot 4 skinned characters on mid-range Android, and no figures for the memory overhead of `Skeleton3D`/`Skin`/`AnimationTree` per instance.
- I could not confirm whether skinning and blend shapes run on GPU compute or CPU in the Mobile renderer. The architecture doc says Mobile avoids compute, so this matters for blend-shape-heavy face customization.
- Runtime-GLB texture compression on Android is unverified (see section 3).

## 7. License, cost when the game sells, governance, community, shipped mobile 3D and fighting games

### Takeaway
Godot is MIT-licensed and free for commercial use. The only obligation is to include Godot's copyright and license notice, for example in credits. The official pages describe no royalties or fees. The engine is hosted by the non-profit Godot Foundation. Shipped Godot mobile titles exist (*Kamaeru*, *Rift Riff*, *Spin Hero*), but **I found no shipped 3D fighting game on Godot for mobile**. The most notable Godot fighting game is the 2D, turn-based *Your Only Move Is HUSTLE* (PC).

### Cited Findings
**License and cost**
- "Godot is Free and open source Software available under the OSI-approved MIT license… free as in 'free speech' as well as in 'free beer'… free to download and use Godot for any purpose: personal, non-profit, commercial, or otherwise." — [Godot FAQ (4.7)](https://docs.godotengine.org/en/stable/about/faq.html)
- Games made with Godot are the developer's own; Godot's license "doesn't extend to content you make with it".
- The only condition is to include Godot's copyright notice and license text in the game's documentation or credits; a link to the license page is acceptable.
- Third-party components are listed in `COPYRIGHT.txt` under MIT-compatible licenses.
- The site is "Hosted by the Godot Foundation". — [Godot license page](https://godotengine.org/license/)
- Neither page mentions royalties or revenue fees. The FAQ's "free beer" wording and the MIT grant cover commercial sale. — [Godot FAQ](https://docs.godotengine.org/en/stable/about/faq.html); [License](https://godotengine.org/license/)
- "Godot is not owned by one person; it belongs to the community." — [Godot FAQ](https://docs.godotengine.org/en/stable/about/faq.html)
- The Foundation maintains Google Play Billing, Play Games Services and StoreKit 2 plugins. — [Godot mobile update, Apr 2026](https://godotengine.org/article/godot-mobile-update-apr-2026/)

**Community size**
- 4.6 had close to 400 contributors and 2,001 commits.
- Steam saw over 1,200 new Godot games in 2025; itch.io sees about 500 new Godot games per week. — [4.6 release page](https://godotengine.org/releases/4.6/)
- 4.7 had over 300 contributors and more than 1,600 PRs; 4.8 has 1,523 fixes from 340 contributors so far. — [4.7 release page](https://godotengine.org/releases/4.7/); [4.8 beta 1](https://godotengine.org/article/dev-snapshot-godot-4-8-beta-1/)

**Shipped mobile games**
- *Kamaeru: A Frog Refuge*, *Rift Riff* and *Spin Hero* (Google Play and App Store) are cited by the Foundation. — [Godot mobile update, Apr 2026](https://godotengine.org/article/godot-mobile-update-apr-2026/)
- A developer reported shipping the 3D game *Vlobs* on iOS and Android with the Godot 4.1 Mobile renderer. They later dropped Android over compatibility problems (early 4.x). — [Godot Forum](https://forum.godotengine.org/t/does-anyone-use-godot-4-for-mobile-games/43673)

**Fighting games**
- *Your Only Move Is HUSTLE* (Ivy Sly) is an online turn-based fighting game on Steam (app 2212330), engine listed as Godot, released 3 Feb 2023. — [Gamescrobbler](https://gamescrobbler.com/nl/games/your-only-move-is-hustle); [itch.io community](https://ivysly.itch.io/your-only-move-is-hustle/community?before=100)
- *Castagne* is a Godot fighting-game framework, presented at GodotCon 2024 ("Specializing Godot: Castagne framework for fighting games", Panthavma). — [GodotCon 2024 talk](https://talks.godotengine.org/godotcon-24/talk/FQA9Q7/)
- Other results were jam or prototype fighting games on itch.io (e.g. *Tekkengine*, made in 25 days). — [itch.io: Tekkengine](https://mizpah.itch.io/tekkengine)

### Inferences
- **Cost when Western Heart sells:** $0 to Godot. There are no royalties and no per-seat or revenue thresholds under MIT. Keep a credits or license line, and check any third-party addons or plugins separately.
- There is no direct precedent for a commercial 3D mobile fighting game on Godot. The project would be a pioneer: no public postmortem on frame-data, rollback or netcode on Godot mobile was found.

### Gaps
- I did not fetch the Godot Foundation governance page (board, decision process), and found no GitHub star count this session.
- I could not confirm which engine version YOMI Hustle used (likely Godot 3.x), or whether *Rift Riff*/*Kamaeru*/*Spin Hero* are 3D.
- No shipped 3D fighting game on Godot was found on any platform.

## 8. Godot 4.8 / 5.0 roadmap items relevant to this project

### Takeaway
4.8 (beta 1, 15 Oct 2026, feature-frozen) adds several items that directly address gaps found above:
- decals in Compatibility, and animated decals
- mip-level texture streaming
- ASTC 6x6
- touch-input fixes and native touch in UI controls
- Android SDK automation and AAR export
- Jolt 5.6
- non-allocating physics queries
- Trail3D (useful for hit trails)
- screen-space contact shadows

No official Godot 5.0 roadmap exists; community reports say the project plans to stay on 4.x for years.

### Cited Findings
**4.8 beta 1 items with PR numbers**
- Decals in Compatibility (GH-118070)
- Animated decals (GH-115653)
- Mip-level texture streaming (GH-113429)
- ASTC 6x6 and HQ compression profiles (GH-115003, breaking)
- Screen-space contact shadows for directional lights (GH-118045)
- Multi-bounce AO approximation (GH-115426)
- Directional lightmap specular (GH-109737)
- **Trail3D** (GH-117107)
- Jolt 5.6.0 (GH-121260)
- Non-allocating physics queries (GH-113970)
- `RigidBody3D.get_velocity_at_position` (GH-121122)
- Touch for TextEdit/CodeEdit (GH-119706), TabBar and PopupMenu
- Duplicate touch-press fix (GH-120864, breaking)
- `Label` auto font size (GH-116791)
- Android SDK automation (GH-121849)
- `OS.alert()` blocking on Android (breaking, GH-120800)
- .NET builds now require .NET 10
- Symbol renaming (experimental, GH-117949)
- Cleaner serialized diffs (GH-92102)

[4.8 beta 1](https://godotengine.org/article/dev-snapshot-godot-4-8-beta-1/)

**4.8 dev 7**
- AccessKit screen readers on iOS (GH-119750) and Android (GH-117785), partial parity
- Android AAR export (GH-123574)
- Makima interpolation (GH-123835)

[4.8 dev 7](https://godotengine.org/article/dev-snapshot-godot-4-8-dev-7/)

**Godot 5.0**
- A forum thread says no 5.0 has been announced. It relays (secondhand) that lead developer Emi said at Godot Tomorrow that the project plans to stay on 4.x "for a few more years". 5.x is where compatibility-breaking changes would go. — [Godot Forum](https://forum.godotengine.org/t/solved-will-upcoming-godot-engine-version-5-0-be-100-backward-compatible-with-version-4-x-x/137600) (unofficial)
- A GodotFest 2025 fireside chat framed next milestones around integrations, testing and CI, console support and maintenance. — [media.ccc.de: GodotFest 2025 fireside chat](https://media.ccc.de/v/godotfest2025-fireside-chat-godots-next-milestones/audio) (via search summary)
- The Foundation says mobile work will continue on "rendering, performance, testing infrastructure, plugin coverage, and development workflows". — [Godot mobile update, Apr 2026](https://godotengine.org/article/godot-mobile-update-apr-2026/)

### Inferences
- Starting on 4.7.x and upgrading to 4.8 stable is low-risk; 4.x minor releases "preserve compatibility" apart from listed breaking changes. Do it before building the decal and texture-streaming parts of the creation suite.
- No 5.0 migration risk is expected within a typical 1–2 year development window.

### Gaps
- I found no official public roadmap document for 4.9 or 5.0.
- The 4.8 stable date is not announced.
