# PANTERA — Attire Slots (owner 2026-10-17)

Canonical slot map. Slot ORDER is the law below; everything gets built and wired
at the same time — ordering is about slot positions, not schedule.

## The locked slots

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **Pantera (P1 Original)** | `docs/tpose-refs/pantera-t7king/pantera-t7king.glb` — the NEW full-res Tekken 7 King reskin (14.7MB, 19 meshes / 19 materials / 54 embedded images). Black panther mask, yellow eyes, purple tights, black trunks with red PANTERA. This is the real original attire. |
| 2 | **Leo man** | `attires/leomon/` — the lion-head Leomon attire, RENAMED "Leo man" (proprietary to our universe). NOTE: directory is still `leomon/` on disk (restored by the 54k restore); rename the dir to `leo-man/` once the restore lands. Display name is "Leo man" everywhere the player sees it. Pantera Tripo model (if/when pulled) takes this slot per the TRIPO=MAIN exception — Leo man then moves back. |
| 3 | **Pantera — Snow Leopard** | `attires/snow-leopard/pantera-snow-leopard.glb` — reskin of the older classic build per owner 2026-10-17: purple tights → blue, black panther head → white with snow-leopard rosette spots, yellow eyes → blue, nose → pink. Same T7 King P1 source (NOT T6 PSP), Mixamo rig intact, trunk/boot/glove design untouched. Original classic kept at `attires/classic/pantera-classic.glb` (also in git history). |
| 4 | **Pantera — T7 P2** | `attires/p2-wired/pantera-attire4-p2.glb` — the official Tekken 7 Player 2 scheme wired onto the Slot 1 base GLB (P2 diffuse pack at `attires/p2/`): black tights with bronze tribal, black trunks with bronze KING logo, black boots with red trim, red/black gloves. Arms/gloves/mask unchanged (P2 keeps them). Render at `docs/tpose-refs/pantera-attire4-p2/p1_front.png`. Added 2026-10-18 (Pantera custom-attires lane). |
| 5 | **Pantera — Crimson Rage** | `attires/crimson-rage/pantera-attire5-crimson.glb` — NEW custom build via the Creation Suite (2026-10-18): deep crimson tights (custom composite, not a hue shift), black panther + RED scratch-marks decal from `customization/decal-library/pantera/` composited at the canonical placement (rect x=176,y=34,w=186,h=390 in 512×512 King_PantsLower_D), black trunks with red PANTERA, yellow tiger eyes from `customization/eye-library/` (owner's "I like" variant). Texture-only — zero rig/geometry changes (PANTERA RIG RULE). Render at `docs/tpose-refs/pantera-crimson-rage/p1_front.png`. |

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
