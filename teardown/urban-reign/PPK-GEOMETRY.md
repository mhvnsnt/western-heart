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

### 4. Bone bind pose — CORRECTED 2026-10-14
Record at ~0x660: 28 zero floats + 4×4 **identity matrix** (row-major).
**Correction:** only 3–4 such records exist in the whole file (char001:
0x670, 0x780, 0x850, 0xbf0) — it is NOT a repeating per-bone table.
Bone translations not yet located.

### 5. Normal runs (type 0x0002 chunk)
float32 xyz runs with EXACT unit length (char001: 68/70/50/70/56 verts).
0..1 "color"-like runs and unit-cube OTHER runs in the same chunk —
semantics open (vertex colors? morph data?).

### 6. Bone-name strings — CORRECTED 2026-10-14: FALSE POSITIVE
**No `__L_` / `__R_` strings exist in ANY of the 72 char PPKs
(count = 0 everywhere).** The "863 strings" in earlier notes were float
bytes misread as ASCII by the old extractor heuristic. Bone names are
not stored in the char PPKs — the skeleton likely lives in the `.gyu`
motion files, stage PPKs, or elsewhere on the ISO.

## NEGATIVE RESULTS (documented so the next pass doesn't redo them)

- "s16 region" @0x2971 (type 0x8001, 16KB): no int32 value 67 anywhere in
  the chunk and no 96-byte record structure reproduces — the earlier
  "96-byte records with `0,67` signatures" claim does not hold. Chunk is
  mostly noise at every tested alignment; not a bone table.
- Chunk 9 (type 0x865 @0x8001, 2935B): denormal/garbage floats, not a
  bone table (a few skeleton-plausible triples are false positives).
- Chunk 8 (type 0x8 @0x6880, 6KB): **another vertex blob** in the same
  128-separator format (70 verts parsed) — not bone data.
- Non-normal xyz float runs in the 0x0002 chunk are denormal/zero
  misreads — not positions. Positions live in the 0x8001-type float chunks
  (see §2).
- The `(-32768, 63)` s16 pair is **not** float 1.0 (endianness trap:
  `00 80 3f 00` LE = 0.747f; 1.0f = `00 00 80 3f`).
- Strided float32 xyz scans of the 0x0002 chunk find only false positives
  from re-reading normal arrays at wrong strides.
- No u16 index buffers found near geometry (likely non-indexed / strip order).

## WATCHDOG ATTEMPT 3 (2026-10-14) — bone-translation hunt

Tool: `tools/ur_bone_hunt.py` (committed; reproduces every check below).

- **Two-bone translation-constraint test REFUTES the pure-translation
  model.** If influence positions were the same rest point in two bone
  frames, d = pos_a − pos_b would be constant per bone pair (T_b − T_a).
  Measured on char001: **615 distinct exact d vectors over 1555 two-bone
  verts** (top cluster only 6 verts). The two positions are NOT related
  by a per-pair translation — either bind-pose bone rotations are
  involved, or the record layout needs re-interpretation.
- **Cross-fighter chunk census (all 72 PPKs): no constant-size
  shared-skeleton chunk exists**; tag types vary per fighter (e.g. vertex
  chunks are 0x8001 in char001 but 0x5c00 in char002). Detect chunks by
  content (128-separator probe), never by type.
- Point-cloud render of influence-0 positions (char001): amorphous
  0.5m blob, no human shape — confirms positions are not model-space.
- Recommended next: parse `.gyu` motion files for skeleton (bone
  count/names); check stage PPKs/ISO for a shared rig; topology (index
  order) is needed before per-bone rigid alignment can be attempted.

## STILL OPEN

1. Bone translations → world-space positions (no bone table found in char
   PPKs; pure-translation two-frame model refuted — see attempt 3 above).
2. 4-bone verts (~20% non-unit normals) + 12/28-float block edge cases.
3. Index/topology (triangle order) for the extracted verts.
4. Integer 0x8001 chunk @0x2971 semantics (96-byte records).
5. Textures/UV→texture mapping, material assignment.
6. Mesh ↔ bone assembly (which bones each influence references — bone
   indices not yet located; cf. type 0xae00 "byte/integer patterns").
7. World-space verification: render a fighter with bone transforms applied.
