# VF5 PS3 Motion Data — Gap Assessment

**Date:** 2026-10-22 | **Worker:** teardown-pull (subagent 37982ab1)
**Blocks:** Zen's Dural base-mix (owner: "Dural's stance is Zen's stance")

## Summary

VF5 PS3 motion data was never acquired. All pulled archives (release `vf5-ps3-v1`, 89 assets) contain character models and textures only. No motion/animation files exist in any accessible archive. The format is undocumented publicly.

## What was checked

1. **Release `vf5-ps3-v1` (89 assets):** 79× `.farc` (character models + stages), 2× `.bin` (obj/tex DBs), 8× `vf5-500m.part_*` (4GB split archive, high-entropy, not fully pulled).
2. **Dural specifically:** `dur.farc` (760B) + `duritm.farc` (25.5MB) extracted via `tools/farc_extract.py` — 28 entries, all `*_obj.bin` (models) and `*_tex.bin` (textures). Zero motion files.
3. **All 19 fighters:** same pattern — models and textures, no motion.
4. **Local archives** (`~/workspace/vf5-work/`): obj/tex only, no motion.
5. **Web research (2026-10-22):** No public documentation of VF5 PS3 motion file format. Xentax chrrox scripts cover models; MikuMikuLibrary covers VF5FS PC models. Neither covers PS3 motion.

## Where VF5 PS3 motion would live

Not in the pulled data. In a full PS3 dump (BLES00029), motion data would be in the game filesystem outside the character `.farc` archives. The 4GB `vf5-500m` split archive may contain motion files, but this is unverified (high-entropy, not fully downloaded).

## What's needed (in order)

1. **Acquire motion source:** Pull the full 4GB `vf5-500m` archive and identify motion files, or source a BLES00029 dump from archival sources (owner owns VF5 — authorized per ownership rule). Large files to Releases, not local disk.
2. **Reverse-engineer the format:** VF5 PS3 motion format is undocumented. Requires binary RE — header identification, bone track parsing, keyframe decompression. Estimated: days to weeks.
3. **Convert to usable format:** glTF animations or BVH, retargeted via `tools/anim-retarget/`.
4. **Wire Dural's stance + base movement** into Zen's kit per `docs/decisions/` Zen spec.

## Recommendation

Queue as a dedicated teardown lane. This is a multi-day RE project, not a single-session task.

Per the no-guessing law (`docs/RULES_NO_GUESSING.md`): do NOT procedurally fake Dural's motion. Report the gap (this document), don't fill it with invented animation.

## Related

- Dural model: `teardown/virtua-fighter-5/models/dur/README.md`
- Zen spec: `MEMORY.md` (ZEN MOVESET entry, 2026-10-22)
- VF5 teardown: `teardown/virtua-fighter-5/TEARDOWN.md`
