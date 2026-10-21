# ZUI — Attire Slots (owner 2026-10-18)

Tripo 3D model = DEFAULT attire (owner law 2026-10-18).

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **Zui — Drunken Monk (Tripo)** | `roster/zui/attires/attire1/model.glb` — Tripo-generated Drunken Monk (owner Drive file, 20.7MB, tripo_node). DEFAULT. |
| 2 | **Zui — Rework v2** | `roster/zui/attires/attire2/model.glb` — rework v2 (bald, saffron/indigo, tattoo decals). |
| 3+ | **Steve Fox base + reskins** | `steve-fox` canon base + `zui_alt1` / `zui_alt2` (T7 Steve reskins) — selectable alternates via `ATTIRE_VARIANTS['zui']` (wired 2026-10-21). |

- Base: Steve Fox (canon). "Zooey" NOT in canon — flagged in TRIPO-REGISTRY.md.
- Render: Attire 1 T-pose render at `docs/tpose-refs/zui/a1_front.png` (2026-10-21, own-eyes verified) → owner generative-AI transform.
- Wiring (2026-10-21, model-key audit follow-up to PR #418): the two Tripo GLBs previously had NO MODEL_URLS keys and were unreachable in game. Now: `zui-attire1` / `zui-attire2` keys in `game/js/assets.js`, `ATTIRE_VARIANTS['zui']` in `game/js/attires.js` (Slot 1 = default), and roster `model:` = `zui-attire1` so the enemy/raw path loads the Tripo too. Steve Fox base stays a selectable alternate — not deleted, not the default.
