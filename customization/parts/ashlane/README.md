# AshLane Parts (owner's library, mined 2026-10-22)

Character-customization parts from the owner's `mhvnsnt/AshLane-prototype`
(`public/models/`), wired into the creation suite's parts library by worker 61.

## Slots

| Dir | Suite slot | Files | Attach |
|---|---|---|---|
| `footwear/` | `shoes` | sneakers high/low, theory boots, wrestling boots (L/R pairs) | shoe bone / foot |
| `gloves/` | `gloves` | boxing, MMA, opera/theory, street (L/R pairs) | hand bones |
| `masks/` | `masks` | bandanas ×3, hollow superdragon, luchador ×3 | head |
| `hair/` | `hair` | long green/black, blond+beard, locs w/ beads, pinned locs | `mixamorig:Head` |
| `hoods/` | `head` | purple robe ×2 | head |
| `wristbands/` | `accessories` | pads, sweatbands, wraps (L/R pairs) | wrist/forearm |
| `accessories/` | `accessories` | 4 rigged chains (gold ashlane, wizard gang, diamond ice, bannon piece) | Neck/Spine2 |

## Attach conventions (from the upstream manifests)

- Each slot ships a `manifest.json` with per-part attach specs: bone, position,
  rotation, scale. The chains are skinned to Neck/Spine2 and ship ~8x oversize —
  the consumer rebinds them onto the fighter's matching bones and bakes the
  manifest `scale` into the geometry (see the `attach` blocks in
  `accessories/manifest.json`).
- Hair parts attach to `mixamorig:Head` at scale 1.0 (see `hair/manifest.json`).
- `FIT_NOTES.md` files carry per-slot tuning notes from the owner's customizer.
- For the bone-name rebind attach pattern (no retargeting), see the owner's
  `AshLane-prototype/src/game3d/quaternius.ts: attachPart` — the creation
  suite's part-attachment work follows that pattern inside the existing
  parts pipeline.

## License

Owner's own assemblies. Hair parts derived from Quaternius CC0 packs
(recolored); chains/masks/boots are owner-made. Provenance kept per part in
the suite index (`source_game: "ashlane"`).
