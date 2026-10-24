# WWE 2K22 Teardown — Pull Plan

**Game:** WWE 2K22 | **Steam App ID:** 1255630 | **Owned:** YES (vil3m, 49.2h)
**Status:** Awaiting extraction via DepotDownloader (delisted — needs Steam auth)

## What we're pulling (user priorities)

1. **Animations** — full animation library for wrestling moves
2. **Rigs** — character rig structures
3. **Customization** — creation suite parts, categories, slots
4. **Creation suite** — full CAW system structure
5. **Community creations** — format/structure for sharing

## Directory layout (when files land)

```
teardown/wwe2k22/
├── README.md              (this file)
├── PULL-LOG.md            (what was pulled, when, from where)
├── animations/            (raw animation data → PRIVATE repo)
├── rigs/                  (rig definitions → PRIVATE repo)
├── caw-parts/             (creation parts → cataloged, derivatives to public)
├── customization/         (customization system docs + structure)
└── research/              (analysis docs → public repo)
```

## Private repo rule

Raw game files (models, textures, animations, proprietary formats) go in the
user's PRIVATE repo, never in public western-heart. Only our proprietary
wiring, catalogs, and derivatives go in public.

## Wiring targets

| Pull | Wires into |
|------|-----------|
| Animations | `game/assets/anim/` via animation bank system |
| Rigs | Rig reference for creation suite |
| CAW parts | `packages/creation-suite/src/catalogs.js` (per-source catalog) |
| Customization structure | `packages/creation-suite/src/` (slotmap, layering, menu) |

## Coordination

- Extraction: via DepotDownloader (Steam auth required)
- Research: top-5 coordinator (c481024a)
- Receiving/wiring: pull-wiring coordinator (this lane)
- Status updates: issue #866
