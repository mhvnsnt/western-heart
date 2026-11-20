# WWE 2K19 Teardown — Pull Plan

**Game:** WWE 2K19 | **Steam App ID:** 846350 | **Owned:** YES (vil3m, 113 min)
**Status:** Batch 1 landed (PRs #1480/#1481/#1483, 1,677 files, merged 2026-11-01); YOBJ→glTF conversion, YANM motion decode, and further batches still owed (see PULL.md)

## What we're pulling

1. **Animations** — 2K19's animation library
2. **CAW parts** — creation parts unique to 2K19
3. **Showcase content** — structure reference

## Directory layout

```
teardown/wwe2k19/
├── README.md
├── PULL-LOG.md
├── animations/
├── caw-parts/
└── research/
```

## Private repo rule

Raw game files → PRIVATE repo. Proprietary wiring/derivatives → public.

## Wiring targets

Animation banks, creation suite catalogs (`source_game: "wwe2k19"`).

## Coordination

- Extraction: DepotDownloader (Steam auth)
- Status: issue #866
