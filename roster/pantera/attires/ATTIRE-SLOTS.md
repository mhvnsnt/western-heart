# PANTERA — Attire Slots (owner 2026-10-17)

Canonical slot map. Slot ORDER is the law below; everything gets built and wired
at the same time — ordering is about slot positions, not schedule.

## The locked slots

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **Pantera (P1 Original)** | `docs/tpose-refs/pantera-t7king/pantera-t7king.glb` — the NEW full-res Tekken 7 King reskin (14.7MB, 19 meshes / 19 materials / 54 embedded images). Black panther mask, yellow eyes, purple tights, black trunks with red PANTERA. This is the real original attire. |
| 2 | **Leo man** | `attires/leomon/` — **THIS IS THE TRIPO MODEL** (owner-confirmed 2026-10-19: "Leo man is the tripo model for that attire slot 2, the one we had in game for so long and the original tripo model and the one we put in the pictures"). The lion-head Leomon attire, RENAMED "Leo man" (proprietary to our universe). NOTE: directory is still `leomon/` on disk. The restore landed 2026-10-21 (main a457d34ac) with his model at `attires/leomon/model.glb` (the canonical T3-rigged build, wired as 'pantera-leoman'), keeping the `leomon/` directory name. Display name is "Leo man" everywhere the player sees it. Per the PANTERA exception, his Tripo model sits at Attire 2 (not Attire 1 — Attire 1 is the in-game reskin he did first). |
| 3 | **Pantera — Snow Leopard** | `attires/snow-leopard/pantera-snow-leopard.glb` — reskin of the older classic build per owner 2026-10-17: purple tights → blue, black panther head → white with snow-leopard rosette spots, yellow eyes → blue, nose → pink. Same T7 King P1 source (NOT T6 PSP), Mixamo rig intact, trunk/boot/glove design untouched. Original classic kept at `attires/classic/pantera-classic.glb` (also in git history). |
| 4 | **Pantera — Leopard King** | `attires/leopard-king/model.glb` — Tripo model (https://studio.tripo3d.ai/3d-model/094c2f37-1c61-43fb-82ff-7124100a1021, "tiger humanoid" by jaywillf69, 23.3MB, 1 mesh / 3 textures, meshopt-compressed static). Snow-leopard head with fangs bared, spotted white/black rosette tights, spotted tail with dark tip, big spotted paw gloves, spotted boots with black trim. **RIGGED 2026-10-20** (owner swap: Leopard King pushed up from Slot 6 to Slot 4): rigged build at `attires/leopard-king/model-rigged.glb` — WH canonical 49-joint Pantera skeleton + 4-bone tail chain (Tail1–4, skinning follow; no authored tail animation exists), donor Idle + Tekken 3 King stance/grab clips baked; see `attires/leopard-king/WORKLOG.md` 2026-10-20 section for method + gate numbers. Render at `docs/tpose-refs/pantera-leopard-king/p1_front.png`. Added 2026-10-19 (owner: "Pantera Leopard King attire"); moved to Slot 4 on 2026-10-20 (owner swap with Slot 6). |
| 5 | **Pantera — Crimson Rage** | `attires/crimson-rage/pantera-attire5-crimson.glb` — NEW custom build via the Creation Suite (2026-10-18): deep crimson tights (custom composite, not a hue shift), black panther + RED scratch-marks decal from `customization/decal-library/pantera/` composited at the canonical placement (rect x=176,y=34,w=186,h=390 in 512×512 King_PantsLower_D), black trunks with red PANTERA, yellow tiger eyes from `customization/eye-library/` (owner's "I like" variant). Texture-only — zero rig/geometry changes (PANTERA RIG RULE). Render at `docs/tpose-refs/pantera-crimson-rage/p1_front.png`. |
| 6 | **Pantera — T7 P2** | `attires/p2-wired/pantera-attire4-p2.glb` — the official Tekken 7 Player 2 scheme wired onto the Slot 1 base GLB (P2 diffuse pack at `attires/p2/`): black tights with bronze tribal, black trunks with bronze KING logo, black boots with red trim, red/black gloves. Arms/gloves/mask unchanged (P2 keeps them). Render at `docs/tpose-refs/pantera-attire4-p2/p1_front.png`. Added 2026-10-18 (Pantera custom-attires lane) at Slot 4; moved to Slot 6 on 2026-10-20 (owner swap — Leopard King pushed up to Slot 4; the filename keeps its historical `pantera-attire4-p2.glb` name). |

## Slot-ordering law (owner 2026-10-17)

- **Early slots:** Western Heart / Eastern Mind-based attires — the forefront, original designs.
- **Later slots:** Tekken-based attires (ports, recolors, ripped variants).
- All attires get done and wired up at the same time; the law only governs slot positions.
- Every attire goes through the Tekken character customizer + customization suite to be modified and made proprietary. The owner does the creative customization himself — slots are wired clean, no creative changes by agents.

## Backlog — extra King attires to pull and wire (later Tekken slots)

- **Tekken 3 King** — retro alt (per IDENTITY.md: "Tekken 3 as retro alt"). Model on hand; needs attire wiring.
- **Other in-game King attires** — pull every extra attire the games' Kings ship with, attach and modify as later slots.
- **PANTXRΛ-88 (cyborg)** — `attires/cyborg/CYBORG-88.md` concept on file; assets pending heavy-Leomon source. Western Heart-based → early slot when built.

## History

- 2026-10-17: slots defined by owner; forensics confirmed Slot 3's source is T7 King P1.
- 2026-10-17: Slot 3 reskinned to Snow Leopard colorway (blue tights / white rosetted head / blue eyes / pink nose); render at `docs/tpose-refs/pantera-snow-leopard/p1_front.png`.
- 2026-10-18: Slot 4 (T7 P2 scheme) + Slot 5 (Crimson Rage, custom Creation Suite build) wired in by the Pantera custom-attires lane. Renders own-eyes verified.
- 2026-10-19: CORRECTION — owner confirmed Slot 2 "Leo man" IS Pantera's ORIGINAL Tripo model (in-game for so long, the one in the pictures); the "NOT ON RECORD" registry note was wrong. Slot 6 "Leopard King" (Tripo 094c2f37) wired. Render own-eyes verified.
- 2026-10-20: OWNER SLOT SWAP — Leopard King pushed up from Slot 6, swapped with Slot 4: Slot 4 = Leopard King (Tripo), Slot 6 = T7 P2. Leopard King rigged the same day (see `attires/leopard-king/WORKLOG.md`). Pure reorder — all six attires remain wired; nothing deleted.
