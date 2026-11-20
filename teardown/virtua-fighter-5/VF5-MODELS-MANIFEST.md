# VF5 Model Library — Manifest

**19 fighters + 38 stages** from Virtua Fighter 5 (PS3), extracted 2026-10-13/14.

## Files

Due to GitHub's file size limits, the model binaries are hosted on the
[vf5-model-library-v1 Release](https://github.com/mhvnsnt/western-heart/releases/tag/vf5-model-library-v1):

| Archive | Contents | Size |
|---|---|---|
| `vf5-models-a.tar` | lau, wol, jef, jak, aoi, lio, bra, shu (8 fighters) | 394MB |
| `vf5-models-b.tar` | lei, msk, kag, goh, van, sar, mon, pai, aki, dur, akixx, common + README (11 fighters + common) | 386MB |
| `vf5-stages.tar` | All 38 stages | 462MB |

**Total**: 1.3GB, 108 files

## Already in repo

- `teardown/virtua-fighter-5/TEARDOWN.md` — extraction methodology
- `teardown/virtua-fighter-5/docs/` — per-fighter/stage docs, VF5-MECHANICS.md
- `teardown/virtua-fighter-5/tools/` — farc_extract.py and other tools

## Usage

Download and extract the tar files into `teardown/virtua-fighter-5/`:
```
tar -xf vf5-models-a.tar -C teardown/virtua-fighter-5/
tar -xf vf5-models-b.tar -C teardown/virtua-fighter-5/
tar -xf vf5-stages.tar -C teardown/virtua-fighter-5/
```
