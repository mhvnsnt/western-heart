# WWE 2K20 Teardown — Pull Plan

**Game:** WWE 2K20 | **Steam App ID:** 1015500 | **Owned:** YES (vil3m, 57.3h)
**Status:** Awaiting extraction via DepotDownloader (delisted — needs Steam auth)

## What we're pulling

Same priority set as 2K22, plus 2K20-specific content:
1. **Animations** — 2K20's animation library (may differ from 2K22)
2. **Rigs** — character rig structures
3. **Customization/CAW** — creation suite parts unique to 2K20
4. **Showcase/story content** — structure reference

## Directory layout

```
teardown/wwe2k20/
├── README.md
├── PULL-LOG.md
├── animations/
├── rigs/
├── caw-parts/
└── research/
```

## Private repo rule

Raw game files → PRIVATE repo. Proprietary wiring/derivatives → public.

## Wiring targets

Same as 2K22: animation banks, creation suite catalogs, rig references.
2K20 parts merge into the unified catalog with `source_game: "wwe2k20"`.

## Coordination

- Extraction: DepotDownloader (Steam auth)
- Status: issue #866
