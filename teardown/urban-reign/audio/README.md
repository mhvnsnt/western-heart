# Urban Reign — Audio Library

**Extracted:** 2026-10-13
**Files:** 1,033 (1,032 from AFS map + 1 split)
**Total:** ~16MB
**Source:** `DVD000.AFS` via surgical HTTP range-fetch from GitHub Release `urban-reign-iso-v1`

## Method

The AFS offset map (`../afs-map/dvd000_afs_map.json`) had correct per-file offsets,
but the ISO file listing had size/offset swapped for `DVD000.AFS`. Real offset found
by parsing ISO9660 from the release parts: **3,063,840,768** (not 1,077,082,112).

AFS magic verified, entry table matches map exactly. Files pulled via parallel
range-fetch (8 workers), no full ISO download needed.

Extractor: `~/workspace/agent-ops/ur-extract/ur_audio_parallel.py`

## Format

- `.pbd` — sound data blobs (SE, impacts, UI sounds)
- `.p3d` — descriptors/headers (tiny, 32–744 bytes)

## Naming

Original AFS paths flattened: `sound/ok_se/se/wp07.pbd` → `sound_ok_se_se_wp07.pbd`

One file had a truncated name in the map (`impact_00_start.p`); split into correct
`.pbd` (1,056 bytes) + `.p3d` (32 bytes) pair.

## Categories (from paths)

- `sound/ok_se/se/` — sound effects (weapons, impacts, character SE)
- `sound/ok_se/cs/` — cutscene audio
- `sound/ok_se/at/` — attack sounds
- `sound/ok_se/` — UI, missions, system sounds
