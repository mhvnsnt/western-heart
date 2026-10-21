# ZUI — Attire Slots (owner 2026-10-18)

Tripo 3D model = DEFAULT attire (owner law 2026-10-18).

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **Zui — Drunken Monk (Tripo)** | `roster/zui/attires/attire1/model.glb` — Tripo-generated Drunken Monk (owner Drive file, 20.7MB, tripo_node). DEFAULT. |
| 2 | **Zui — Rework v2** | `roster/zui/attires/attire2/model.glb` — rework v2 (bald, saffron/indigo, tattoo decals). |
| 3+ | **Steve attires** | Other Steve Fox attires — pending wiring. |

- Base: Steve Fox (canon). "Zooey" NOT in canon — flagged in TRIPO-REGISTRY.md.
- Render: Attire 1 needs T-pose render → owner generative-AI transform.

## Stance System (2026-10-21 — owner: "stance switch from boxing to drunken fist and Steve's other stances")
Zui's moveset (`game/assets/movesets/zui.json`) carries Steve Fox's **complete T7 set** (286/287 rows; WALL BOUND skipped — mechanic row, no input) plus Lei Wulong's **drunken fist** as a distinct stance group. Data-level stances — entry moves resolve through the input buffer, gated moves by exact-notation lookup (`stances` block in zui.json; engine has no stance flag — see `docs/movesets/ZUI-STANCE-SYSTEM-2026-10-21.md`).

| Stance | Entry (touch) | Notes |
|---|---|---|
| BOX — Boxing (default) | — | all non-gated Steve moves |
| DCK — Ducking | `f+3` | 10 gated moves |
| LWV / RWV — Weaves | `3` / `4` from Ducking | 14 / 5 |
| FLK — Flicker | `b+3+4` | 23 |
| PKB — Peekaboo | via `,F` transitions (entry row preserved `f+3+4_r198`) | 42 — `f+3+4` chord fires Drunken Master Walk instead |
| SWY — Swaying | `b+3` | 3 |
| ALB — Albatross | `3+4` | 5 |
| **DRU — Drunken Fist (Drunken Master)** | **`f+3+4` (Drunken Master Walk)** | 40 Lei T7 moves verbatim; exit `DRU b`; sustain `DRU 1+2` (Tiger Sip) |

Fits the canon: Attire 1 is the Drunken Monk, title "Drunken Master", style "Boxing/Drunken".
