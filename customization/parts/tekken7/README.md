# Tekken 7 Parts

Owner order 2026-10-21: pull ALL Tekken 7 customization parts — generic AND
per-character — and wire them into the Creation Suite.

## What's here

- `CATALOG.json` — the Tekken 7 parts catalog in the Creation Suite's
  registry-entry shape (consumer: `packages/creation-suite/src/catalogs.js`,
  same pattern as `customization/parts/no-mercy/CATALOG.json`). It loads and
  merges today. **`parts` is empty and `named_gaps` carries the wanted set** —
  see the survey for why.
- `T7-CUSTOMIZATION-PARTS-SURVEY-2026-10-21.md` — the holdings survey: every
  source checked, counts per slot class, the skull-mask verdict, the exact
  acquisition route (game paks + umodel), and the import spec.
- `catalog.test.mjs` — test against the real runtime module and the real
  registry: the catalog loads, merges without disturbing the registry, and
  the skull-mask part_id resolves `unresolved` (reported, never silently
  dropped) until the real part lands.

## What's NOT here (named gap)

The actual 3D part meshes. Tekken 7 customization items live in the game's
`.uasset`/pak data (`Character/Items/Mesh/cmn` for the generic set, per-
character trees beside it). We have never held the game's paks: the ~47 GB
download was blocked in 2026-10 and the lane pivoted to character models
only. The complete DB **schema** lives one directory over, in
`customization/parts/tekken/tekken7-slot-catalog.json`.

When the paks are extracted, parts land at
`customization/parts/tekken7/<slot>/<item>/<item>.glb` and are appended to
`CATALOG.json` → `parts[]` in the shape templated in its `_meta` — no
consumer change needed.
