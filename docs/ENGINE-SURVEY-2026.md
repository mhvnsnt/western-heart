# Game Engine + Web Framework Survey — October 2026

Researched 2026-10-16. Western Heart is **Three.js on web now, Godot 4 target**.
This doc keeps the engine decision current: what's new in 2026, what changed
that affects us, and what's worth pulling. Real research (GitHub API, release
notes, news) — not training-data guesses.

**Tracking:** every finding below ends in ✅ documented (this doc) or
❌ excluded with reason, per the RESEARCH-TO-REPO law. Engine *sources* are
not vendored (100s of MB–GBs each); the wiring for engines is version pins +
concrete recommendations in §8.

---

## 1. Godot 4.x — our target (MIT, 118k stars, pushed daily)

**Current: 4.7 "Director's Cut" (June 18, 2026).** 4.6 shipped Jan 2026.
Local tools already carry 4.7.2.

What matters for Western Heart:
- **Jolt Physics is a built-in option** (since 4.5, replaces Bullet) — use
  Jolt for the fighting-game hitboxes; it's the same solver family as
  Brutal.Jolt (§6).
- **New Asset Store** (4.7) replaces the Asset Library — re-check for
  fighting-game plugins (rollback netcode, hitbox editors).
- **AreaLight3D**, **DrawableTexture2D** (paint-on-texture API), HDR output
  on all desktop platforms, Steam Frame / Android XR day-one support.
- **VirtualJoystick** node (4.7) — mobile controls without plugins.
- Editor: inspector copy/paste of whole sections, collapsible animation
  track groups, Path3D collision snapping, vertex snapping.
- ⚠️ Breaking changes in 4.7 (device IDs, RichTextLabel renames, removed
  tap_back_pos/Android OBB) — read the migration guide before upgrading any
  lane past 4.5.
- 2D: one-way collision direction, conic gradients, AtlasTexture tiling.

**Verdict:** stay on the Godot 4 target; upgrade lanes to 4.7 deliberately,
not blindly. ✅ documented.

## 2. Bevy (Apache-2.0/MIT, 49k stars, pushed daily)

**Current: 0.19.1** (0.19 released June 19, 2026; 0.20 RC in flight).
Data-driven Rust ECS engine. 0.19 highlights: next-gen scene system (BSN
declarative scene format), GPU-offloaded rendering (skinned-mesh culling,
instancing), render recovery on device loss. Still **no official visual
editor** (code-first). ~3-month cadence with routine breaking changes.

**Verdict:** best-in-class Rust ECS, but no editor + churn makes it wrong
for our team velocity. Watch only. ❌ excluded — not our stack (Godot 4
target stands).

## 3. Unreal Engine — proprietary, document-only

**UE 5.8 is the last UE5** (MegaLights, Mesh Terrain, Lumen Lite for
Switch 2, MetaHuman Animator/Crowds, experimental MCP plugin). **UE6 early
access targets late 2027.** Epic's license is source-available, **not open
source** — cannot be pulled. ❌ excluded (proprietary license).

Relevance: none for Western Heart directly; note the industry direction
(MCP-in-engine, Nanite dynamic tessellation) as things Godot/Bevy will
chase.

## 4. Mid-tier open engines

| Engine | License | 2026 state | Verdict |
|---|---|---|---|
| **Stride** (7.8k ⭐) | MIT | Active (pushed 2026-10-16), C# | Interesting C# alternative, but smaller community than Godot. Watch. ❌ excluded — Godot target stands |
| **O3DE** (9.7k ⭐) | Apache-2.0 | Active (2026-10-14) | AAA-ambition, heavy. ❌ excluded — overkill |
| **FlaxEngine** (7k ⭐) | **Custom source-available, NOT OSI open source** | Active (2026-10-15) | ❌ excluded — license (not open source) |
| **Cocos Creator / COCOS 4** (9.8k ⭐) | MIT (engine) | v4 open-sourced early 2026, AI-native pitch, PinK IDE in dev | Mobile/web strength, but our web is Three.js and target is Godot. ❌ excluded — not our stack |

## 5. Legacy open engines (inform the Godot target)

- **ioquake3** (GPL-2.0, 2.8k ⭐, pushed 2026-10-12) — still maintained.
  The Quake 3 networking model (snapshot/delta, client prediction) is the
  textbook reference if Western Heart ever needs rollback/multiplayer.
- **Xash3D FWGS** (2.8k ⭐, pushed 2026-10-16) — GoldSrc-compatible,
  active. License field empty in API — verify before pulling anything.
- **id Tech 4 (BFG)** — GPL-3.0, the classic "real" 3D codebase to study
  (rendering, collision). Study reference only.

✅ documented as study references; nothing pulled (not our runtime).

## 6. NEW in 2026 — worth knowing

### BRUTAL (ahwootech/BRUTAL, 1.4k ⭐, created 2026-10-14)

Dean Hall (DayZ) / RocketWerkz C# **framework** (not engine): custom C#
interop layer, Vulkan 1.3, .NET 10, obsessive low-allocation design.
Shipped in 6 projects (Kitten Space Agency direct; RimWorld's new Waylith
engine built on it). Libraries as NuGet packages: **Brutal.Jolt** (3D
physics), Box2D, glTF, maths, concurrency, etc.
**License: MIT-based with added attribution** (copyright notice in credits
+ logo before gameplay + ship NOTICE.txt) — **not yet OSI-approved**.
Free for commercial use otherwise.

Relevance: the *philosophy* (own your stack, no royalties) matches ours;
**Brutal.Jolt** is a data point for our physics choice. Not our runtime
(C# framework, no editor, day-old). ✅ documented. ❌ not pulled —
framework, not engine; license has attribution strings attached.

### Carbon (Fenris Creations, ex-CCP)

The EVE Online engine framework open-sourced **July 2026**: Destiny
(physics/pathfinding), Trinity (graphics), networking, UI, audio —
20+ years of persistent-world tech. Study reference for netcode/scale.
(Repo location not yet pinned — re-check.) ✅ documented, pull pending
repo location.

### COCOS 4

Open-sourced early 2026 with an AI-native pitch (MCP/agent workflows) and
the PinK IDE in development. See §4 verdict. ✅ documented.

## 7. Web game frameworks (our current runtime)

- **Three.js** (MIT, 116k ⭐, pushed daily) — **WebGL + WebGPU renderers are
  both core** in 2026; TSL (Three Shading Language) is the path for WebGPU
  post-processing. This is our web runtime — stay current via npm.
- **Physics: Rapier vs cannon-es** — **Rapier** (`@dimforge/rapier3d-compat`,
  Apache-2.0, pushed 2026-10-10) is the 2026 default for web games
  (deterministic, WASM, active). **cannon-es** (MIT) is in maintenance mode
  (last push 2024-01) — fine for light use, but new work should pick Rapier.
  **Recommendation: standardize new web lanes on Rapier.**
- **PlayCanvas** (MIT, 17k ⭐, engine v2.23.0 Oct 2026, editor MCP server
  exists) — the mature web-engine alternative. Our Three.js stack stands;
  PlayCanvas is the fallback if we ever need an editor-centric web engine.
- **Post-processing:** `pmndrs/postprocessing` remains the library;
  TSL-based post for WebGPU is the 2026-native route.

✅ documented. No pulls — these are npm deps, pulled per-lane when a lane
needs them (not vendored in this repo).

## 8. Wiring / recommendations for Western Heart

1. **Godot 4 target stands.** Upgrade lanes to 4.7 deliberately; adopt
   **Jolt Physics** for hitboxes; use **VirtualJoystick** for mobile.
2. **Web lanes: Rapier** for new physics work (not cannon-es).
3. **ioquake3 networking model** is the study reference if multiplayer/
   rollback ever lands on the roadmap.
4. **BRUTAL/Carbon**: study references for engine independence; not our
   runtime.
5. Re-check quarterly: Godot 4.8/5.0, Bevy 0.20+, BRUTAL maturity.

---

## Finding tracker (RESEARCH-TO-REPO law)

| Finding | Status |
|---|---|
| Godot 4.7 state, Jolt, migration warnings | ✅ documented (§1), wired as recommendations (§8) |
| Bevy 0.19.1 | ✅ documented (§2); ❌ excluded — not our stack |
| Unreal 5.8 / UE6 roadmap | ✅ documented (§3); ❌ excluded — proprietary license |
| Stride / O3DE / Flax / Cocos 4 | ✅ documented (§4); ❌ excluded — not our stack / license (Flax) |
| ioquake3 / Xash3D / idTech4 | ✅ documented as study refs (§5) |
| BRUTAL | ✅ documented (§6); ❌ not pulled — framework not engine + attribution license |
| Carbon | ✅ documented (§6); 🔄 pull pending (repo location TBD) |
| Three.js WebGPU / Rapier / cannon-es / PlayCanvas | ✅ documented (§7); wired as recommendations (§8); npm pulls per-lane |
