# Nioh: Complete Edition Teardown — Pull Plan

**Game:** Nioh: Complete Edition | **Steam App ID:** 485510 | **Owned:** YES (vil3m, 3.1h)
**Status:** Research in progress (top-5 coordinator)

## What we're pulling (user priority)

"Perfect for character depth and customization plus heart and mind inside
and code and lore for Japanese and mythology and eastern mind type canon
building"

1. **Character depth systems** — how does Nioh build deep characters?
   Stats, skills, builds, progression.
2. **Customization** — visual and mechanical customization systems.
3. **Mythology structure** — HOW Nioh structures Japanese mythology into
   game systems. The STRUCTURE and TECHNIQUE, never the lore itself.
4. **Code architecture** — how systems interconnect.

## Canon rule (CRITICAL)

Our canon comes from CANON.md ONLY. Nioh is reference for STRUCTURE and
TECHNIQUE of mythology-building, never for lore content. Do not copy
yokai, spirits, or stories. Learn how they systematize mythology, then
apply that method to Eastern Mind canon.

## Directory layout

```
teardown/nioh/
├── README.md
├── PULL-LOG.md
├── CHARACTER-DEPTH.md
├── CUSTOMIZATION.md
├── MYTHOLOGY-STRUCTURE.md   (technique only, no lore copying)
└── research/
```

## Wiring targets

| Pull | Wires into |
|------|-----------|
| Character depth | Creation suite (stats/builds), fighter progression |
| Customization | `packages/creation-suite/` |
| Mythology structure | Canon-building tools (methodology docs) |

## Coordination

- Research: top-5 coordinator
- Status: issue #866
