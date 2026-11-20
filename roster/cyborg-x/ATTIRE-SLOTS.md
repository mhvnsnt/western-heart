# CYBORG X / CAPE JONES — Attire Slots (owner 2026-10-18)

Tripo 3D model = DEFAULT attire (owner law 2026-10-18).

| Slot | Display name | Contents |
|------|--------------|----------|
| 1 | **Cape Jones (Tripo)** | `game/assets/models/cape-jones.glb` — Tripo main attire (tripo-pull 2026-10-16). DEFAULT. Cape Jones = Cyborg X Attire 1 per canon 2026-10-16. |

- Render: `game/assets/models/renders/cape-jones.png` exists.
- RIG QA 2026-10-23 (muse/cape-jones-fight, tools/model-audit/rig_qa.py on the
  meshopt-decoded GLB): 49 joints, facing -Z, arm/leg sides OK, knees forward.
  Hand/arm weight-bleed heuristic flags hand-proximity verts only (no
  face→spine bleed). PASSED — no re-rig; staged as
  `roster/cyborg-x/attires/attire1/model-rigged.glb` (byte-identical to
  `game/assets/models/cape-jones.glb`), wired as MODEL_URLS
  `cape-jones-attire1` and the default ATTIRE_VARIANTS entry for `cyborgx`.
- NOTE: unrigged static per MODEL-STATUS.md — auto-rig before game wiring.
- AI transform: render goes to owner for proprietary Eastern Mind/Western Heart version.
