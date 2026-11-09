# Tekken 7 Parts

Owner order 2026-10-21: pull ALL Tekken 7 customization parts — generic AND
per-character — and wire them into the Creation Suite.
Owner order 2026-11-08: ALL hair (and then all clothing/items) from all held
games wired into the suite, organized the source games' way, hair rigged and
alive with physics.

## What's here

- `CATALOG.json` — the Tekken 7 parts catalog in the Creation Suite's
  registry-entry shape (consumer: `packages/creation-suite/src/catalogs.js`).
  `parts[]` now carries **34 landed parts**: the skull mask (FULL_HEAD,
  2026-10-21) and **33 hair items landed 2026-11-08** (31 HAIR slot 2 +
  2 FACE_HAIR slot 7) from the held Steam teardown in
  mhvnsnt/game-reverse-engineering `teardown/tekken7-steam/pakchunk0/`.
  Every hair item ships its real GLB(s) — multi-piece items keep ALL their
  component GLBs (e.g. Asuka's 10-part har system) — plus the texture maps
  the teardown holds, at
  `customization/parts/tekken7/<slot>/<item-slug>/`.
- `catalog.test.mjs` — tests against the real runtime module and the real
  registry: catalog loads, merges without disturbing the registry (by-file
  dedupe: registry copies of the hair items win), every hair part_id
  resolves, physics metadata present.
- `T7-CUSTOMIZATION-PARTS-SURVEY-2026-10-21.md` — the original holdings
  survey (predates the GRE Steam teardown landing; its "meshes never held"
  verdict is superseded for the item trees the teardown carries).

## Hair physics

Every hair item carries the game's own swing-bone chains (T7 `SWG_` /
`Hair_OPT` bones, measured per item into each entry's `physics` block) and
is driven in game by the generic spring-bone system
`game/js/hair-spring.js` — gravity, inertia, wind, head collision — the
same architecture the source games use. Items the source game weighted to
the head only (rigid styles) are marked `physics.rigid: true` and follow
the head exactly as in Tekken 7.

## Known gaps (logged, never fabricated)

- Texture extraction in the held teardown is partial: 33 hair texture maps
  across the 33 items (some items hold only a normal/specular map; Lili
  holds none). Entries list exactly the maps held; the rest await the GRE
  texture-extraction completion pass.
- Per-item CCI color-slot counts are not yet extracted; `color_slots` is
  null (unknown), never guessed.
- Character codes `arb`, `bs7`, `dnc`, `frv`, `ltn`, `mut` are not resolved
  to names in any held doc; entries keep the raw codes.
- The remaining T7 item slots (UPPER / LOWER / HEAD / FACE / EXTRA /
  FULL_BODY …) land in follow-up PRs from the same held tree.
