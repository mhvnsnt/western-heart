# URBAN REIGN — PPK Character Geometry Decode

Source: `ppks/chars/char001..072.ppk`. Tools: `tools/ur_parse_vertices.py`
(vertex extractor), `tools/ur_extract_meshes.py` (legacy float-run census).

## PROVEN

### 1. PPK container + tag table (corrected 2026-10-14)
- Magic `ppk\0`, @4 = total size − 8, @8 = data offset (0x80 in char PPKs).
- Header tag table at 0x20: null-terminated u32 entries, `(type << 16) | offset`.
  Offsets are chunk starts; chunk size = next-sorted-offset − offset (last
  chunk runs to EOF). 14 entries in char001, but the table is PER-FILE
  (char002 has 5 entries with different types) — never assume a fixed layout.
- Earlier doc error corrected: the "344KB s16 region" was wrong. The file is a
  sequence of typed chunks; e.g. char001: `0x8001@0x2971` (16KB, integer
  records), `0x8001@0x8b78` (14.7KB, float32 vertices), `0x0002@0xe800`
  (717KB geometry blob: normal runs, color runs, strings).

### 2. Skinned vertex record format — DECODED 2026-10-14 (char001)
Float32 chunks (type varies per file: `0x8001` in char001, `0x5c00` in
char002 — detect by content, not type) hold variable-length vertex records
separated by `128.0 ×4`:

```
per vertex:  N bone influences × 8 floats  +  UV row (4 floats)  +  sep 128×4
  influence: (px, py, pz, weight) + (nx·w, ny·w, nz·w, 0.0)
  UV row:    (u, v, 1.0, 0.0)
N = 1 → 12 floats (rigid, weight 1.0)
N = 2 → 20 floats
N = 3 → 28 floats   (weights sum to 1.0)
```

- **Blended normal = Σ influence normal rows → EXACT unit length.**
  Verified 91/91 two-bone + all rigid/three-bone verts in char001;
  192,371 / 242,569 unit (79.3%) across all 72 fighters (remainder are
  likely 4-bone verts or variant layouts — open).
- Positions are **bone-local**; world transform needs bone matrices.
- Parser: `tools/ur_parse_vertices.py <charXXX.ppk> <outdir>` → per-fighter
  OBJs (influence-0 positions, blended normals, UVs) + `_vmanifest.json`.

### 3. Roster-wide extraction — DONE 2026-10-14
All 72 char PPKs parsed: **242,569 verts** into `models/char001/` …
`models/char072/` (OBJ + manifest each) and `models/ROSTER.json`
(per-fighter vert counts + rigid/2-bone/3-bone split).

### 4. Bone bind pose
Repeating record from ~0x660: 7 zero float4s + 4×4 **identity matrix**
(row-major). (Earlier "identity quats" note corrected — they are matrices.)
Bone translations not yet located.

### 5. Normal runs (type 0x0002 chunk)
float32 xyz runs with EXACT unit length (char001: 68/70/50/70/56 verts).
0..1 "color"-like runs and unit-cube OTHER runs in the same chunk —
semantics open (vertex colors? morph data?).

### 6. Bone-name strings
ASCII strings with `__L_` / `__R_` left/right pairs (863 in char001).

## NEGATIVE RESULTS (documented so the next pass doesn't redo them)

- "s16 region" @0x2971 (type 0x8001, 16KB) is **integer records**, not s16
  positions: no stride/field/scale gives spatial coherence; 96-byte records
  with `0,67` bone-weight-like signatures — semantics open (skin index data?).
- Non-normal xyz float runs in the 0x0002 chunk are denormal/zero
  misreads — not positions. Positions live in the 0x8001-type float chunks
  (see §2).
- The `(-32768, 63)` s16 pair is **not** float 1.0 (endianness trap:
  `00 80 3f 00` LE = 0.747f; 1.0f = `00 00 80 3f`).
- Strided float32 xyz scans of the 0x0002 chunk find only false positives
  from re-reading normal arrays at wrong strides.
- No u16 index buffers found near geometry (likely non-indexed / strip order).

## STILL OPEN

1. Bone translations → world-space positions (bind matrices are identity;
   translations must be in another chunk/record).
2. 4-bone verts (~20% non-unit normals) + 12/28-float block edge cases.
3. Index/topology (triangle order) for the extracted verts.
4. Integer 0x8001 chunk @0x2971 semantics (96-byte records).
5. Textures/UV→texture mapping, material assignment.
6. Mesh ↔ bone assembly (which bones each influence references — bone
   indices not yet located; cf. type 0xae00 "byte/integer patterns").
7. World-space verification: render a fighter with bone transforms applied.
