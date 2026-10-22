# TORCH — Attire Slots (owner 2026-10-21)

## Ladder rule (owner 2026-10-21, restated for every character)

Torch's **Tripo original is Attire 1 at the FOREFRONT**, and her default
resolves to Attire 1. The Anna Williams base model ladders **BACK** behind
it — never the forefront, never the default.

## Slots

| Slot | Display name | Provenance | Status | Contents |
|------|--------------|-----------|--------|----------|
| 1 | **Valkyrie of Flame** | **Tripo** original (300d0c63-c7c8-4972-b08e-b2e9c169254f, pulled 2026-10-21) | ✅ wired (picker first entry + main roster entry model) | Owner's description, verbatim: "fully nude and blue skin but controls fire that is normal colored and can control different colors of fire too, red windswept hair and Valkyrie helm, blue furry nude crotch and little hairs flaring off her fat hips and glutes". Raw pull (19,456,040 B, sha256 4f24f0c325b222658247325848dfee2d03164d30d9a61cf001404d976bd0f66d, 3 embedded textures, unrigged statue) archived in release `torch-a1-tripo-20261021`; auto-rigged via `tools/auto_rig/rig_tripo_static.py` → `game/assets/models/torch-tripo-a1.glb`, key `torch-tripo-a1`. This attire settles her canon appearance: blue skin, red windswept hair, Valkyrie helm; fire in normal + multiple flame colors. |
| 2 | **Anna Base** | **Tekken base** (Anna Williams) | ✅ wired (ladder-back alternate) | The base model `game/assets/models/torch.glb` (key `torch`) — her original Anna-based model (incl. its HOUSE-49 re-template at `game/assets/models/torch-house49.glb`). NOT a default; a ladder-back alternate, same as every other character's Tekken base. |

## Provenance notes (read before naming any model's origin)

- Slot 1 is a Tripo original generated for Torch — not a reskin, not a
  retexture, not the Anna model. Do not call slot 2 a Tripo model.
- The picker ladder lives in `game/js/attires.js` (`ATTIRE_VARIANTS['torch']`);
  the main roster entry in `game/js/roster-full.js` resolves to slot 1's
  model key (`torch-tripo-a1`) per the ladder rule.
