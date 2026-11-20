# Tekken 6 (PSP) Parts

Owner order 2026-10-21 ~09:39 CDT: the legacy Tekken parts program —
customization parts from T5 + T6 + TTT2 (the games already in teardown) —
becomes the active program, Tekken 7 parked for later. T6 PSP is the lead
source.

## What's here

- `CATALOG.json` — the Tekken 6 (PSP) parts catalog in the Creation
  Suite's registry-entry shape (consumer:
  `packages/creation-suite/src/catalogs.js`, same pattern as
  `customization/parts/tekken7/CATALOG.json`). It loads and merges
  today. **`parts` is empty and `named_gaps` carries the wanted set** —
  see the survey for why.
- `T6-CUSTOMIZATION-PARTS-SURVEY-2026-10-21.md` — the mesh hunt: the
  mesh store located (2,546 embedded containers in the `bin_e6.2`
  archive), the one decode defect that walls them off (emulator-proven),
  what NDPP actually is, the skull-mask verdict from the game's own
  item tables, the T6→registry slot mapping with divergences, and the
  continuation state.
- `catalog.test.mjs` — test against the real runtime module and the
  real registry: the catalog loads, merges without disturbing the
  registry, and the skull-mask part_id resolves `unresolved` (reported,
  never silently dropped) until the real part lands.

## What's NOT here (named gaps)

The actual 3D part meshes. They are located — inside the decrypted
DATA401 bulk, as 2,546 embedded custom-DEFLATE containers — but that
deflate variant is encoded against a decode context no held decoder
provides yet (the game's own inflate fails on the same streams; PR
#413). The crack is owned by the teardown sweep's PPSSPP live-trace
lane. The GMO→GLB pipeline behind the wall is already proven (PR #388).

Also not located yet: the `sbcustomize_item_t` definition array that
joins the 9,440 held item names
(`customization/parts/tekken/tekken6-item-names.json`) to slots,
characters, and model packs.

When the decode lands, parts land at
`customization/parts/tekken6/<slot>/<item>/<item>.glb` and are appended
to `CATALOG.json` → `parts[]` in the shape templated in its `_meta` —
no consumer change needed.
