# BURGER — Attire Slots (owner 2026-10-19)

Canonical slot map. Burger is the Hunger Soul (Bob Richards base) — the
Appetite room's palace-claimed fighter. See CANON.md "BURGER — The Hunger
Soul".

| Slot | Display name | Status | Contents |
|------|--------------|--------|----------|
| 1 | **Burger — Demon Mode** (default) | ✅ wired | Tripo "fantasy ogre 3d model" by tzflo312 — https://studio.tripo3d.ai/3d-model/b3eed68b-90f2-4dc0-a1b5-80b35dd661bc (pulled 2026-10-19, 20.7MB meshopt). Demon mode, possessed by greed: ogre bulk, spiked shoulders, tattered cloth (owner 2026-10-19). `roster/burger/attires/attire1/model.glb`. Render: `docs/tpose-refs/burger/a1_front.png` (own-eyes verified). |
| 2 | **Burger — Cursed Human** | ✅ wired | Tripo "zombie character 3d model" by tzflo312 — https://studio.tripo3d.ai/3d-model/0832b962-ba38-45db-98ca-0af23eb441b0 (pulled 2026-10-19, 20.3MB meshopt). Gaunt hunger-state: blonde messy hair, red sweatpants, sneakers. `roster/burger/attires/attire2/model.glb`. Render: `docs/tpose-refs/burger/a2_front.png` (own-eyes verified). |
| 3 | **Burger — Feral Hunger** | ✅ wired | Tripo "zombie character 3d model" by tzflo312 — https://studio.tripo3d.ai/3d-model/9deaaa9d-bc78-449c-94d-bde1a49ff4b8 (pulled 2026-10-19, 20.8MB meshopt). Feral hunger-state: manic grin, same sweats. `roster/burger/attires/attire3/model.glb`. Render: `docs/tpose-refs/burger/a3_front.png` (own-eyes verified). |
| 4 | **Burger — Getting Hungry** | ✅ wired | Tripo "stylized zombie 3d model" by tzflo312 — https://studio.tripo3d.ai/3d-model/e7c33cfb-1005-415c-9e7a-2356b2aaa1fe (pulled 2026-10-19, 21.0MB meshopt). Early hunger-state: half-lidded eyes. `roster/burger/attires/attire4/model.glb`. Render: `docs/tpose-refs/burger/a4_front.png` (own-eyes verified). |
| 5+ | Big Bob / Slim Bob variants | 📦 planned | Owner 2026-10-19 ~15:34 CDT: need Big Bob + Slim Bob (Tekken) renders as reference to make Burger versions. Slim Bob = the uncursed attire (canon). Lane-owned. |

Ordering follows the Tripo Attachment Registry law (owner 2026-10-18):
Tripo 3D models are the main/default attires.

## Kusaregedo Moveset Wiring (2026-10-19)

Youkai Kusaregedo (Samurai Shodown V/VI, SNK) — giant hunger-cursed ghoul. Frame data
from DreamCancel wiki (Tekitogate). Owner confirmed 2026-10-19 ~18:41 CDT.

**Per-form movesets** (`game/assets/movesets/`):
| Form | File | Moves | Specials | Contents |
|------|------|-------|----------|----------|
| Demon (final, Attire 1) | `burger-demon.json` | 24 | 8 | FULL Kusaregedo kit (7 sigs + 16 normals) + mix of smaller forms' abilities (demon-dash, rapid-bites, mega-chomp, head-slam, hungry-eyes, feral-rend) + 2 exclusives (INFINITE HUNGER, Gaki's Feast) |
| Speed Demon | `burger-speed-demon.json` | 12 | 3 | Quick moves: Flying Head Butt (up/down), Quick Palm, Speed Boot, Backflip + speed kit |
| The Mouth | `burger-the-mouth.json` | 12 | 3 | Head/bite: Huge Headbutt, Mega Chomp, Head Slam, Tongue Lick/Sweep, Maw of Hunger grab |

**Transform chain** (roster-full.js `forms`): base -> speed-demon -> the-mouth -> demon.
Demon form is the ultimate: mix of ALL smaller forms' abilities + exclusives (owner 2026-10-19 ~18:43 CDT).
Extensible — new forms (Mini Tank, etc.) slot into the chain with their own moveset files.

**Sources:** https://dreamcancel.com/wiki/Samurai_Shodown_VI/Kusaregedo (frame data, gameplan),
https://snk.fandom.com/wiki/Youkai_Kusaregedo (powers, story).
