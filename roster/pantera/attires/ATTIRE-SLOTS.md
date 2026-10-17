# PANTERA — Attire Slots (owner 2026-10-17)

Canonical slot map. Slot ORDER is the law below; everything gets built and wired
at the same time — ordering is about slot positions, not schedule.

## The three locked slots

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **Pantera (P1 Original)** | `docs/tpose-refs/pantera-t7king/pantera-t7king.glb` — the NEW full-res Tekken 7 King reskin (14.7MB, 19 meshes / 19 materials / 54 embedded images). Black panther mask, yellow eyes, purple tights, black trunks with red PANTERA. This is the real original attire. |
| 2 | **Leo man** | `attires/leomon/` — the lion-head Leomon attire, RENAMED "Leo man" (proprietary to our universe). NOTE: directory is still `leomon/` on disk (restored by the 54k restore); rename the dir to `leo-man/` once the restore lands. Display name is "Leo man" everywhere the player sees it. |
| 3 | **Pantera — Snow Leopard** | `attires/snow-leopard/pantera-snow-leopard.glb` — reskin of the older classic build per owner 2026-10-17: purple tights → blue, black panther head → white with snow-leopard rosette spots, yellow eyes → blue, nose → pink. Same T7 King P1 source (NOT T6 PSP), Mixamo rig intact, trunk/boot/glove design untouched. Original classic kept at `attires/classic/pantera-classic.glb` (also in git history). |

## Slot-ordering law (owner 2026-10-17)

- **Early slots:** Western Heart / Eastern Mind-based attires — the forefront, original designs.
- **Later slots:** Tekken-based attires (ports, recolors, ripped variants).
- All attires get done and wired up at the same time; the law only governs slot positions.
- Every attire goes through the Tekken character customizer + customization suite to be modified and made proprietary. The owner does the creative customization himself — slots are wired clean, no creative changes by agents.

## Backlog — extra King attires to pull and wire (later Tekken slots)

- **T7 King P2 recolor** — `attires/p2/` (54-file drop-in pack + `recolor_p1_to_p2.py`, restored by the 54k restore). Black tights/trunks/boots, bronze tribal, red trim.
- **Tekken 3 King** — retro alt (per IDENTITY.md: "Tekken 3 as retro alt"). Model on hand; needs attire wiring.
- **Other in-game King attires** — pull every extra attire the games' Kings ship with, attach and modify as later slots.
- **PANTXRΛ-88 (cyborg)** — `attires/cyborg/CYBORG-88.md` concept on file; assets pending heavy-Leomon source. Western Heart-based → early slot when built.

## History

- 2026-10-17: slots defined by owner; forensics confirmed Slot 3's source is T7 King P1.
- 2026-10-17: Slot 3 reskinned to Snow Leopard colorway (blue tights / white rosetted head / blue eyes / pink nose); render at `docs/tpose-refs/pantera-snow-leopard/p1_front.png`.
