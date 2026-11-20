# Tekken Parts

Owner directive 2026-10-18: Tekken parts pulled in, decoded, wired into the repo.

## What's here

`tekken7-slot-catalog.json` — Tekken 7's COMPLETE customization database schema,
ready for the Creation Suite to consume:

- **16 equipment slots** (HEAD, HAIR, FULL_HEAD, HAIR_ACC, GLA, FACE, FACE_HAIR,
  MAKE_UP, UPPER, FULL_BODY, LOWER, UPPER_ACC, LOWER_ACC, EXTRA, EFFECT, AURA)
  with asset types and game paths
- **Slot group IDs** for UI organization
- **21-field item CSV spec** — store WH items in Tekken's exact format
- **Asset prefixes** (EI signature items, ECI effects, ACI auras, CS sets, CCI
  items, CI item data)
- **Slot conflict rules** (FULL_HEAD blocks HEAD+HAIR+FACE…, FULL_BODY blocks
  UPPER+LOWER…)
- **Color system** (0–5 color slots per item)
- **WH-relevant character IDs** (King=2, Alisa=19, Asuka=12, Xiaoyu=5, Eddy=35,
  Steve=10, Zafina=51)

## What's NOT here (needs pulling)

The actual 3D item models and UI binaries — they live in Tekken 7's game
`.uasset` files, which we never pulled. The schema gives us "literally Tekken's
customization system" in architecture; Western Heart content populates it.
See `MANIFEST.json` → `needs_pulling`.
