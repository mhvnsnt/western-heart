# CHARGER — Blanka replacement (owner 2026-10-20)

Proprietary Western Heart fighter. The owner, verbatim: *"Blanka replacement
model from tripo attire 1: CHARGER (his name is charger cause of blankas
attacks and movesets will be attach to him but he's got powers of ice and
electricity)".*

CHARGER takes Blanka's roster slot. Blanka's own files stay in the repo
(`roster/blanka/`, `game/assets/movesets/blanka.json`, `sf-blanka.json`) —
only the playable fighter entry changed. Logged in `RENAME-MAP.md`.

## Attires (owner-made Tripo models, pulled with tools/tripo-pull)

- **Attire 1 — "The Ice Monster"**: `attires/attire1/model.glb`
  Tripo project "ice monster 3d model" by eqqq57218 —
  https://studio.tripo3d.ai/3d-model/b91318ce-2ccd-43eb-8691-d675b3ee8b10
  (spiky white hair, light blue body, red patterned belt, chained ankles)
  Pull record: `~/workspace/tripo-recovery/charger_attire1/` (manifest + sha256).
- **Attire 2 — "The Wild Current"**: `attires/attire2/model.glb`
  Tripo project "green spiky creature 3d model" by eqqq57218 —
  https://studio.tripo3d.ai/3d-model/f87e24eb-0c0b-4444-9409-4f4dabc0bb32
  (green spiky humanoid, muscular, white chest fur, red sneakers)
  Pull record: `~/workspace/tripo-recovery/charger_attire2/`.

Both GLBs are the raw Tripo outputs (EXT_meshopt_compression +
KHR_mesh_quantization, 3 textures each), validated with
`tools/render-prep/render-prep.py` — all textures decode, no NaN geometry.
The game decodes meshopt at load (MeshoptDecoder in `game/js/assets.js`),
same as the KRONOS/KORESHI Tripo wires.

## Moveset

`game/assets/movesets/charger.json` — Blanka's FULL set (199 moves, post-#363
union) with inputs and frame data identical to `blanka.json` (script-verified).
Signature names carry his ice+electric identity: the Electric Thunder family
is now **Cryo Thunder**, the Rolling family is now **Frostcharge Roll** (full
old→new list in the JSON's `canon_rename_map` and in `RENAME-MAP.md`).
Animation bank: `bryan` (Blanka's T3 source bank) via `game/js/fighter.js`.
