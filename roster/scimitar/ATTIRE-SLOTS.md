# SCIMITAR — ATTIRE SLOTS

Canon: Scimitar, the Desert Blade (Shaheen moveset; scimitar blade fused to
body/soul). Owner Tripo model, user-provided 2026-10-22.

## Slots

| Slot | Model key | File | Source |
|---|---|---|---|
| 1 (default) | `scimitar` | `roster/scimitar/attires/attire1/source/scimitar-a1-rigged.glb` (19,132,660 B, blob sha `bced063b…`) | Tripo `a3e76dd5-d471-4d0c-bf42-75e81c2ba2a3`, archived 2026-10-22; manifest `attires/attire1/source/manifest.json`. Source static `scimitar-a1.glb` 24,166,404 B (sha `940fe82e…`). Rigged by `tools/auto_rig/rig_tripo_static.py`. |
| 2 | `scimitar-classic` | `game/assets/models/scimitar.glb` (13,789,832 B, blob sha `1a76fd20…`) | Shaheen-based base mesh (was `scimitar-rigged.glb`). Ladders back per OBSOLETE-ORIGINALS. |

## History

- 2026-10-22: Tripo pull archived (`roster/scimitar/attires/attire1/source/`).
- 2026-11-06 (owner): "that not the correct scimitar glb model from my tripo
  imports" — the Tripo pull above is the correct one; the Shaheen base moved
  to the back slot.
- 2026-10-22 (owner queue): wrongly listed as "Needs model."
- 2026-11-21 (Lane F model audit): ladder added (`game/js/attires.js`
  `'scimitar'`), MODEL_URLS key `scimitar-classic` added, queue + registry
  corrected. No default change: slot 1 was already the roster default
  (`roster-full.js` model `scimitar`).
