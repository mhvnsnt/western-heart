# DOA parts — GAP (2026-10-13)

**Status:** No DOA part files exist in this repo. Nothing was invented to
fill the gap.

## Exactly what's missing

- **Zero extracted part files.** `teardown/dead-or-alive-6/` contains only
  `DOA6-MECHANICS.md` + `TEARDOWN.md` (combat mechanics, federated as a
  layer). No character models, no costume meshes, no hair/glasses parts,
  no texture rips — the DOA teardown is mechanics-only so far (~15%
  overall; model pull never started).
- **No open-source part packs found** with redistributable DOA costume
  parts suitable for the suite (checked 2026-10-13).

## Why

The DOA6 PC pull is **blocked on disk**: ~50–80 GB install, machine was at
93% when the teardown lane checked (2026-10-13). No DOA6 copy on
Archive.org either. Without game files there is nothing to extract parts
*from*.

## Where the parts will come from

1. **Acquire DOA6 PC** (Steam purchase / repack) on a machine with 80 GB+
   free — flagged for the DOA teardown lane.
2. **Map the install:** character `.g1m` models, `.g1t` textures
   (Koei Tecmo proprietary formats — documented in
   `teardown/dead-or-alive-6/TEARDOWN.md`).
3. **Convert:** open-source parsers exist —
   [Switch-Toolbox](https://github.com/KillzXGaming/Switch-Toolbox)
   (GPL-3.0) ships `File_Format_Library/FileFormats/HyruleWarriors/G1M`
   + `G1T` C# parsers for the Koei Tecmo model/texture family DOA6 uses
   (verified present in the repo tree 2026-10-13). Community DOA5/6
   converters are the fallback per the PULL-IN DIRECTIVE. Caveat: the
   parsers were authored against Hyrule Warriors-era files; DOA6
   variants may need validation against real `.g1m` samples.
4. **Register:** drop converted parts here, list them in `manifest.json`,
   rebuild the index (`python3 ../build_parts_index.py`).

## What IS here meanwhile

- `DOA-WARDROBE-SYSTEM.md` — the full DOA6 wardrobe/menu system extracted
  from repo research, mapped to UNIFIED-UI-SPEC §5.3 slots. The suite's
  WARDROBE tab is specified against this; it is not blocked on part files.
- `manifest.json` — empty part manifest; `build_parts_index.py` already
  reads it, so the first real part lands in PARTS-INDEX.json with no
  builder changes.
