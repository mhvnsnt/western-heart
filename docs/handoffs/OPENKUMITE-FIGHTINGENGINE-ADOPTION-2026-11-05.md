# Handoff — OpenKumite v0.1.2 + FightingEngine public rules + template layer → Western Heart

Date: 2026-11-05 (America/Chicago). Owner auth: **t369u / t372u / t373u / t374u / t375u**.
Agent: MoneyManBusch / Grok Bot. Claim: #866.

## Research trust brief (do not re-hunt)

| Source | Trust | Notes |
|---|---|---|
| OpenKumite https://github.com/openkumite/openkumite **v0.1.2** (MIT) | High | Packaging docs only; no Rust/game-data vendored. |
| https://fightingengine.com/ · hanmincho.com · Discord kMjN2rqyFu · Reddit 1xnqt6d | Public | Rules / context. |
| Tag Battle https://www.youtube.com/watch?v=Lko4SWLXVEU (@min2hound) | Public demo | Importer showcase only. |
| `docs/tech/STEAM-LIBRARY.md` | Owner library | Valid sources; no credentials; raw assets → private GRE. |

### FE embargo (t373u)

FE GitHub + playable builds **private until 2026-12-25**. Do not hunt leaks.

### Tag Battle demo cast — never WH roster

Hwoarang, Jin Kazama, Yugo the Wolf, Siegfried Schtauffen — FE importer demos only.

## Template layer (t374u / t375u)

WWE-style copy-moveset: import banks/movesets from teardowns → rename to **generic
hinting template ids** → attach to **WH characters**. Full map:

- `docs/movesets/MOVESET-TEMPLATE-INVENTORY-2026-11-05.md`
- `game/data/moveset-templates/index.json`

**Pantera** → `t7-grappler-jaguar-mask` (exact King T7). Keep WH visual identity
(no WWE logos on screen). Prefer existing GRE/WH teardown files over re-pulling
Steam depots.

## What WH already had

- Hit capsules ≠ pushboxes (`hitbox.js` / fighter push cylinders).
- Voronoi stage fracture + shard gravity (`destruction.js` / `stagebreaks.js`).
- cannon-es prop debris (`physics.js`) — visuals only.
- Fight camera level-follow (`fight-camera-math.js` / `scene.js`).
- Pantera T7 path + clipmap 467 + wiring diagnosis 2026-11-03.
- nipplejs mobile pad; apple-mobile-web-app meta.

## What this adoption lands

| Piece | Path | Status |
|---|---|---|
| Pipeline law (incl. templates + first-play) | `docs/PIPELINE-LAW.md` | new |
| This handoff | `docs/handoffs/OPENKUMITE-FIGHTINGENGINE-ADOPTION-2026-11-05.md` | new |
| Template inventory | `docs/movesets/MOVESET-TEMPLATE-INVENTORY-2026-11-05.md` + `game/data/moveset-templates/index.json` | new |
| Air blend FE 0.758 | `game/js/air-reaction-blend.js` + test + fighter hook | new |
| Hit/push debug | `game/js/hit-push-debug.js` (F4 / `?hitboxes=1`) | new |
| PWA shell | `game/manifest.webmanifest`, `game/sw.js`, index register | new |
| Camera edge clamp | `fight-camera-math.js` (`fightCameraDolly` / `CenterX`) + `scene.js` + tests | landed |
| Wall-break debris physics | `stagebreaks.js` breach chunks → `_debris` gravity/settle | landed |
| Pantera audit | `docs/movesets/PANTERA-KING-T7-AUDIT-2026-11-05.md` | new |
| AGENTS / CLAUDE / BUILD-LOG pointers | prepend only | updated |

## First-play leftovers (named)

- Expose `window.__whFight` from `game.js` so F4 overlay always finds fighters (overlay searches multiple globals today).
- Shard↔shard collision (DestructionSystem settles on rest plane only; no inter-shard contacts yet — cannon-es bridge optional follow-up).
- Crack-overlay floor markers before break are intentional; after break zone hides — verify every stage def.
- Real PNG app icons (manifest uses inline SVG data URL).
- Android APK recipe (OK `packaging/android` pattern) after PWA proven on device.
- Deeper FE reaction tables — wait for 2026-12-25 OSS.
- Attach more WH CAWs to `wwe2k-*` templates once GRE motion pacs are mapped (no superstar roster names).
- Other first-play glitches: log on #866 as found; prefer teardown/modding sources.

## Android plan (not binary in this PR)

OK v0.1.2: `cargo ndk` → `.so`, `aapt2`, one Java activity, `d8`, `zipalign`, `apksigner`, no Gradle.
WH: own keystore + own shell (TWA / WebView / future native) — never ship OK's APK or disc assets.

## Do not do

- Hunt FE leaks · add Tag Battle / WWE superstar names to roster · vendor OK Rust/data ·
  touch Muse #1096 / `tools/auto_rig` · claim Pantera 100% until audit remaining list is empty with proof ·
  re-download huge Steam depots without a documented missing file · print Steam credentials.
