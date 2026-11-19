# WWE 2K19 toolchain

Unpack 2K19 `.pac` archives, convert YOBJ character models to glTF,
and read YANM animation clips. Everything here was rebuilt from
publicly documented formats (see References); no game code was
copied and no closed software was decoded beyond the documented
container formats.

## Tools

| File | What it does |
|---|---|
| `pac_unpack.py` | Unpacks `.pac` files (HSPC/SHDC/EPK8/EPAC/PACH/YANMPack containers; ZLIB, Yukes BPE, and Oodle Kraken decompression). Writes a sha256 manifest. |
| `yuke_bpe.py` | Pure-Python Yukes BPE decompressor (the `BPE ` wrapper). |
| `oodle_krk.py` | ctypes wrapper for libooz (`Ooz_Decompress`) with an `ooz` CLI fallback. Needs the ooz build (see Install). |
| `yobj.py` | YOBJ character-model parser (bones, skin weights, morph heads, tri-strip faces). |
| `yobj_to_gltf.py` | Converts a `.yobj` model to glTF 2.0 (`.glb`): skinned mesh, 421-joint skeleton, facial morph targets. |
| `yanm.py` | YANM animation-clip parser (bone table, part offsets). Keyframe values are not decoded yet — see `docs/YOBJ-YANM.md`. |
| `catalog_yanm.py` | Catalogs every `.yanm` under given roots into JSON. |
| `install.sh` | Builds the ooz (Oodle) helper from source. |

## Install

```sh
./install.sh        # clones zao/ooz, builds liblibooz.so + ooz CLI
```

Python 3.8+ with no third-party packages. `pac_unpack.py` works
without ooz for everything except `OODL` (Oodle Kraken) chunks; with
no ooz present those chunks are reported as errors instead of
crashing the run.

## Use

```sh
# Unpack one PAC (or a whole tree) -- output mirrors the input paths
python3 pac_unpack.py path/to/50_mpc.pac --out unpacked
python3 pac_unpack.py path/to/pac --out unpacked --root path/to/pac

# List the container tree without writing anything
python3 pac_unpack.py path/to/50_mpc.pac --out /tmp/x --list

# Batch-1 layout: keep YANMPack / TextureLibrary parts as .bin leaves
python3 pac_unpack.py path/to/pac --out unpacked --root path/to/pac --flat

# Convert a character model to glTF
python3 yobj_to_gltf.py 0000.yobj wrestler.glb
python3 yobj_to_gltf.py 0000.yobj wrestler.glb --no-morphs

# Inspect an animation clip
python3 yanm.py 00800000.yanm

# Catalog all clips under a tree
python3 catalog_yanm.py unpacked/moves yanm-catalog.json
```

## What is verified (2026-11-19)

- **Moves pack** (66 PACs, 180 MB): 217,901 files, 179,890,161
  bytes, 28,828 containers, 174,460 BPE + 6 ZLIB decompressions,
  **0 skipped, 0 errors**. The `--flat` output for `50_mpc.pac`
  matches the earlier batch-1 extraction byte-for-byte on 906/1000
  files (the other 94 are the ported-moves mod's replacements).
- **Entrance pack** (920 PACs, 720 MB, recovered from the original
  Archive.org ZIP after the release tarball turned out truncated):
  22,069 files written (22,067 unique — two clips are stored twice
  with identical bytes), 1,597,019,074 bytes, 7,734 containers,
  355 ZLIB + 2,394 BPE + 180 OODL decompressed, **0 skipped,
  0 errors**. Contents: 13,837 YANM clips, 6,128 .bin leaves,
  2,053 DDS textures, 49 YOBJ prop models.
- **BPE**: 25/25 small chunks and the 10 largest (up to 1.45 MB ->
  19.2 MB) decompress with sizes matching their headers.
- **OODL**: round-trip verified via ooz up to 12 MB uncompressed.
  ooz's own compressor fails at 15 MB+, so OODL decode above 12 MB
  is unverified against real Oodle-encoded data (no such chunk
  exists in either pack here; re-verify against real ch/edit PACs
  when the full game data lands).
- **YOBJ -> glTF**: `ch10002` (19 MB model) converts to a 9.4 MB
  GLB — 23 meshes, 25,026 verts, 45,099 tris, 421 joints, 660
  morph targets — and renders in Blender as a complete upright
  1.96 m wrestler. Every skeleton bone's weighted vertex centroid
  lands on its anatomical position (hips (0,-106,2), head
  (0,-181,-12), eyes (+/-3.3,-184.7,-13.9) in file cm). The
  converter also handles prop models: the entrance pack's kendo
  stick (818 verts, 2 joints) converts to a valid 53 KB GLB.
- **YANM**: 18,862 clips parsed; 497/500 sampled clips fully
  validate (all part ranges in bounds). 18,528 clips carry the
  standard 23-bone table; 188 carry a 61-bone variant whose entry
  layout differs (see `docs/YOBJ-YANM.md`).

## Known limits

- YANM keyframe *values* (per-frame rotations/translations) are
  not decoded yet — the parser reads the structure and exposes the
  raw keyframe blobs. Build plan in `docs/YOBJ-YANM.md`.
- YOBJ joint rotations are identity in v1 (bind pose renders
  correctly; the rotation fields are not decoded yet), and no
  textures are embedded (the texture-name -> DDS mapping lives in
  the ch PACs).
- OODL decode above 12 MB uncompressed is unverified (see above).

## References

- WrestleMINUS (pozzum/WrestleMINUS, MIT) — format reference for
  HSPC/SHDC/EPK8, YOBJ, and YANM structure. Studied, not copied.
- YukesBPE (xhp-creations/YukesBPE) — BPE reference.
- ooz (zao/ooz) — Oodle Kraken-compatible decompressor.
- Luigi Auriemma's unrrbpe notes — BPE algorithm documentation.
