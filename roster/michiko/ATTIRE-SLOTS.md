# MICHIKO — Attire Slots

Owner rule (Tripo-first ladder, restated 2026-10-21): a fighter's own Tripo
originals lead the ladder; source-game models and reskins ladder back.

| Slot | Attire | Model key | File | Source |
| --- | --- | --- | --- | --- |
| Attire 1 (default) | Bone Goddess | `michiko-attire1` | `roster/michiko/attires/attire1/model-rigged.glb` | Tripo original (below), auto-rigged via `tools/auto_rig/rig_tripo_static.py` |
| Attire 2 | Biker Chick | `michiko-attire2` | `roster/michiko/attires/attire2/model-rigged.glb` | Tripo original (below), auto-rigged via `tools/auto_rig/rig_tripo_static.py` |
| Fallback | Katarina base | `michiko` | `game/assets/models/michiko.glb` | Tekken Katarina-based source model (pre-2026-10-21 default; kept, never deleted) |

## Attire 1 — Bone Goddess

- Owner description (verbatim, 2026-10-21): "bone goddess amazonian M rated nude attire with bone accessories"
- Tripo: https://studio.tripo3d.ai/3d-model/d40da2e4-4400-4c98-8989-3162ad5b1864
- Raw pull archived: GitHub release `michiko-a1-tripo-20261021`, asset
  `michiko-a1-tripo-raw.glb` — 20,137,096 bytes,
  sha256 `74cee199ef0120ea3dde7656e118dfb897cb4e86a06c9aeba1074b45eae9295c`
  (3 embedded images, unrigged statue as pulled).
- Rig report: `docs/proof/claude-2026-10-22/auto-rig-michiko-a1/rig_report.json`

## Attire 2 — Biker Chick

- Owner description (verbatim, 2026-10-21): "biker chick"
- Tripo: https://studio.tripo3d.ai/3d-model/a7ef1da9-6bdb-4b31-99dc-bce5e0b2efc9
- Raw pull archived: GitHub release `michiko-a1-tripo-20261021`, asset
  `michiko-a2-tripo-raw.glb` — 22,722,580 bytes,
  sha256 `144307ab8ea58698fa29d3cd83d61885c789d04f27f7701029bc38b312cd4dbb`
  (3 embedded images, unrigged statue as pulled).
- Rig report: `docs/proof/claude-2026-10-22/auto-rig-michiko-a2/rig_report.json`

## Wiring

- Picker ladder: `game/js/attires.js` → `ATTIRE_VARIANTS['michiko']`
  (first entry is the default attire).
- Model URLs: `game/js/assets.js` → `MODEL_URLS['michiko-attire1']`,
  `MODEL_URLS['michiko-attire2']`; the fallback keeps the existing
  `MODEL_URLS['michiko']` entry.
