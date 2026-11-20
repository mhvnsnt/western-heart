# Yakuza Kiwami (Legacy) Teardown — Pull Plan

**Game:** Yakuza Kiwami | **Steam App ID:** 834530 | **Owned:** YES (vil3m, 26.7h)
**Status:** Research in progress (top-5 coordinator)

## What we're pulling (user priority)

"Perfect for heart and mind within"

1. **Beat-em-up combat** — how does Yakuza do 3D brawling? Combat feel,
   heat actions, environmental interaction.
2. **City/world design** — Kamurocho as a fighting space. How to build
   dense, alive arenas.
3. **Story structure** — chapter flow, cutscene integration.

## Directory layout

```
teardown/yakuza-kiwami/
├── README.md
├── PULL-LOG.md
├── COMBAT.md
├── WORLD-DESIGN.md
└── research/
```

## Wiring targets

| Pull | Wires into |
|------|-----------|
| Beat-em-up combat | Heart and Mind Within (story mode combat) |
| World design | Arena pipeline (dense, alive spaces) |

## Private repo rule

Raw game files → PRIVATE repo. Technique docs → public.

## Coordination

- Research: top-5 coordinator
- Status: issue #866
