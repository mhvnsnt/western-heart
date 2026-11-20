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
| `yobj.py` | YOBJ character-model parser (bones, skin weights, morph heads, tri-strip faces; rest orientations + offsets + `rest_fk()`). |
| `yobj_to_gltf.py` | Converts a `.yobj` model to glTF 2.0 (`.glb`): skinned mesh, 421-joint skeleton with the true bind pose (v2), facial morph targets. |
| `yanm.py` | YANM animation-clip parser (bone table, part offsets). |
| `yanm_decode.py` | YANM keyframe decoder: frame counts (dt-sum vote), Part A rotation tracks, bone hash mapping. |
| `yanm_root.py` | J_Hips Part B root-motion decoder: 8-byte displacement records, per-frame root trajectory in cm (shared pair frame). See `docs/YOBJ-YANM.md` § Root motion. |
| `yanm_to_gltf.py` | Converts a YOBJ + YANM clip to an animated `.glb` (rotation keyframes per joint; see `docs/YOBJ-YANM.md` for the decode). |
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

# Decode a clip's keyframes (frame count, rotation tracks)
python3 yanm_decode.py 00800000.yanm

# Animate a model with a clip -> animated .glb
python3 yanm_to_gltf.py 0000.yobj 00100000.yanm wrestler-kick.glb --no-morphs

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
- **YOBJ -> glTF (v2)**: `ch10002` converts with the true bind
  pose (rest orientations + parent-relative offsets, full
  inverse bind matrices) — the FK reproduces the true joint
  pivots (knee height 58.2 cm, wrist within 2 cm of its
  centroid) and the bind pose renders identically to v1 in
  Blender. Morph bones (332 parentless leaves with heavy skin
  weights) attach to their nearest skeleton bone so the mesh
  holds together under animation. 42/47 entrance-prop YOBJs
  convert (7.1 MB of GLBs: kendo stick, casket, pyro cannon,
  Undertaker hat, Fiend lantern, Del Rio car, ...); 5 fail on
  truncated files / out-of-range indices.
- **YANM**: 18,862 clips parsed; 497/500 sampled clips fully
  validate (all part ranges in bounds). 18,528 clips carry the
  standard 23-bone table; 188 carry a 61-bone variant whose entry
  layout differs (see `docs/YOBJ-YANM.md`).
- **YANM keyframe decode (2026-11-19)**: frame counts from the
  per-part dt sums (197/200 clips fully agree; 293/300 trusted
  by majority vote). Part A = Euler angles, 1 unit = 360/256
  degrees, R_anim = Rx(v2) @ Ry(v0) @ Rz(v1), joint rotation =
  R_rest @ R_anim — validated by FK stick figures over 96
  composition/order/permutation/sign combinations (the winning
  formula is the only one giving coherent human poses) and by
  Blender mesh renders of an animated GLB (ch10002 + a
  110-frame kick clip: coherent kicking figure, limbs attached,
  no shredding). Elbow -128 flags and the leg-twist 180-degree
  offset are handled (see `docs/YOBJ-YANM.md`).
- **YANM root motion (2026-11-19)**: J_Hips Part B decoded —
  8-byte records (i16 dx/dy/dz + u16 dt), displacement over
  [frame, frame+dt), dt-sum = frame count on 274/279 primary
  clips, scale + absolute start from the J_Hips trailing floats.
  Validated on runs, dives, suplexes and dances (see
  `docs/YOBJ-YANM.md` § Root motion). `yanm_decode.py`
  `hips_b_track()` now reads the full track (the length field
  counts 8-byte records, so the span is length×8, not length×4).

## Known limits

- YANM Part B values and the knee (StartingID 0x0001) blocks are
  not decoded yet, and root motion is not yet wired into
  `yanm_to_gltf.py` — animation is Part A rotations only, in
  place, with straight knees. See `docs/YOBJ-YANM.md` § Still
  open (J_Hips Part B itself is decoded — § Root motion).
- No textures are embedded in the GLBs (the texture-name -> DDS
  mapping lives in the ch PACs). The ch `.bin` files carry a
  header + texture-name string at offset 16 (`all_color`,
  `all_color_mr`, ...) — a lead for the texture work.
- OODL decode above 12 MB uncompressed is unverified (see above).

## References

- WrestleMINUS (pozzum/WrestleMINUS, MIT) — format reference for
  HSPC/SHDC/EPK8, YOBJ, and YANM structure. Studied, not copied.
- YukesBPE (xhp-creations/YukesBPE) — BPE reference.
- ooz (zao/ooz) — Oodle Kraken-compatible decompressor.
- Luigi Auriemma's unrrbpe notes — BPE algorithm documentation.
