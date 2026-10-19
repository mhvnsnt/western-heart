# BAEK — Attire Slots (owner 2026-10-18)

Canonical slot map. Slot ORDER is the law below; everything gets built and
wired at the same time — ordering is about slot positions, not schedule.

> **Conflict-resolution note (overnight-idle-pipeline, 2026-10-19):** this file
> predates the Kevin replacement canon. Slots corrected to match the merged
> `roster/baek/ATTIRE-SLOTS.md` (owner 2026-10-18: Baek's model was boring —
> REPLACED by KEVIN from the God Molecule show). No lane content removed.

## The locked slots

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **KEVIN (DEFAULT)** | Tripo 3D "human figure 3d model" — canonical God Molecule character. `attires/attire1/model.glb`. Live-game default swaps to Kevin after the auto-rig pass. |
| 2 | **Original Baek** | `game/assets/models/baek.glb` (RigModels fan rip, untouched). |
| 3 | **Baek — Master's White** | `attires/master-white/baek-master-white.glb` — custom Western Heart reskin of the Baek build (`game/assets/models/baek.glb`): cream dobok → crisp white, black trim → Western Heart dark red, black belt kept, brown eyes default (yellow tiger saved as option). Geometry/rig untouched. Original build untouched at `game/assets/models/baek.glb` (also in git history). |

## Slot-ordering law (owner 2026-10-17)

- **Early slots:** Western Heart / Eastern Mind-based attires — the forefront, original designs.
- **Later slots:** Tekken-based attires.

Baek's canon vessel is the **Master Soul**; the Master's White is a proprietary
Western Heart master look on the Tekken-based base. The **Fallen Master**
(near-black dobok, oxblood trim) is saved as a swap option in
`customization/decal-library/baek/`, not a separate slot.
