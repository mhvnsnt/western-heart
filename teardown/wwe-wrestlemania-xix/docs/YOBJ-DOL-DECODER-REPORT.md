# YOBJ DOL Reverse-Engineering — Vertex Decode Report (2026-10-15)

**Analyst:** subagent yobj-dol-re (respawn; prior worker died without checkpoint)
**Target:** `main.dol` from WWE WrestleMania XIX (USA) GameCube ISO (GW9E78)
**DOL:** 3.3 MB, entry 0x80003154, text @0x80003100/0x8001E5C0, extracted via
`tools/wmxix_range_iso.py` GitHub range fetch (local ISO symlink was broken;
DOL not in FST — lives at fixed disc offset from header 0x420 = 0x1F700).
**Tools:** `tools/dol/dolmap.py`, `tools/dol/effscan.py`, `tools/dol/funcmap.py`
(Capstone PPC disassembly, effective-address xref scanner).

---

## 1. PROVEN: the game's vertex buffer builder (0x80078C6C)

A function at **0x80078C6C** builds the runtime vertex buffer used for rendering.
Its inner loop (0x80079348 / 0x80079400) is:

```
loop:
  lha r26, 0(r3)  / sth r26, 0(r22)    ; 6x s16 copied
  lha r26, 2(r3)  / sth r26, 2(r22)    ; VERBATIM, no scaling,
  lha r26, 4(r3)  / sth r26, 4(r22)    ; no transform,
  lha r26, 6(r3)  / sth r26, 6(r22)    ; no float conversion
  lha r26, 8(r3)  / sth r26, 8(r22)
  lha r26, 0xA(r3)/ sth r26, 0xA(r22)
  addi r3, r3, 0xC                       ; src += 12
  stw  r24, 0xC(r22)                     ; bone indices (u32)
  stw  r25, 0x10(r22)                    ; weights (u32)
  sth  r7, 0x14(r22) / sth  r7, 0x18(r22)  ; material/batch (s16)
  sth  r18, 0x16(r22)/ sth  r18, 0x1A(r22) ; vertex index (s16)
  addi r22, r22, 0x1C                    ; dst += 28
```

**Runtime vertex = 28 bytes:**
| Offset | Type | Meaning |
|---|---|---|
| 0x00 | s16 x3 | **POSITION** (verbatim from source) |
| 0x06 | s16 x3 | normal (verbatim from source) |
| 0x0C | u32 | packed bone indices |
| 0x10 | u32 | weights (from per-vertex stream, or 0) |
| 0x14,0x18 | s16 | material/batch index |
| 0x16,0x1A | s16 | vertex index |

**Source vertex = 12 bytes = 6x s16 = (position s16x3, normal s16x3).**
The copy is bit-exact. There is NO decode math on positions at build time.

## 2. PROVEN: bone/weight encoding (from the same function)

Per 16-byte draw record, two paths selected by record byte [3]:

- **Path 1** (`rec[3]==1`, single bone):
  `bone_u32 = bonemap[rec[0]] + 1`, weights = 0.
- **Path 2** (`rec[3]!=1`, multi-bone):
  `bone_u32 = ((bonemap[rec[2]]+1) << 16 if rec[3]!=3) | ((bonemap[rec[1]]+1) << 8) | (bonemap[rec[0]]+1)`
  weights_u32 = next u32 from a per-vertex stream (`lwz r25, 0(r15); addi r15, r15, 4`).

`bonemap` is a 256-byte table (`lbzx r24, r19, r24`) mapping file bone ids to runtime bone indices.

## 3. PROVEN: positions are s16x3 (vertex welding @0x800794D8)

After the copy loop, the function welds duplicate vertices by comparing
`s16 at +0x00, +0x02, +0x04` with an integer tolerance (`subf`/`abs`/`cmpw`/`bgt`),
then merges the material/index fields. This only makes sense if +0x00 is the
position. Normals at +0x06 are never compared.

## 4. PROVEN: no CPU float conversion of positions

A scan of all 2.9M text words found **zero** `lha`+`xoris 0x4330` (s16→float)
idioms. Positions stay s16 and are consumed directly by the GPU (GX s16 vertex
arrays); scale is applied at render time, not in the loader.

## 5. Supporting finds

- **Magic dispatch table** @0x8030E1B0: `(POF0,1) (YOBJ,2) (YANM,3) (POFE,-2) (DUMY,-1)`,
  followed by handler pointer tables. Scanner function @**0x8007A61C**
  (memcmp-based, called from the CCharaBase loader @0x80043ACC etc.).
- **YOBJ header parser** @0x80072510 region: reads header+0x5C (Table1) and
  header+0x60 (skin batches); `CCharaBase.cpp`, `CModelData`, `CMemoryObject`
  strings nearby; format strings `model/wrestler/%03d_%d.ymg`,
  `Can't load mode of wrestler.[no:%d, type:%d]`.
- File-type vtable @0x8030E220 (~60 entries, 0x8007xxxx/0x8008xxxx methods).

## 6. POSITION FORMULA

**`P = (s16_x, s16_y, s16_z)` — the raw signed 16-bit values, used directly.**

There is no decompression, no codebook lookup, and no arithmetic on the
position components in the vertex build path. The render-time scale (1/64,
per the elbow finding in YOBJ-SKINNING-DECODER-REPORT.md) is applied by the
GX pipeline, not the loader.

## 7. PRECISE BLOCKER (what remains)

The 12-byte source verts (6x s16) consumed by the builder have **not yet been
located in the YOBJ file**. Specifically:

1. The file's "skin batches" are 6-byte (s16x3) verts (606 in 000_0), not 12-byte.
   They cannot feed the builder directly.
2. Table1's 892 `(u16, 0)` payloads (153 unique values, heavily repeated) and
   Table2's 1026 `(u16, u16)` payloads (109/172 unique) are codebook-like, not
   vertex arrays. Only 5% of batch s16 values appear in the Table1 codebook.
3. The 16-byte runtime draw records consumed by the builder
   (`[0,1,2]=bone bytes, [3]=type, [4]=u32 count, [8]=u32 aux, [12]=u8 count,
   [13]=u8 flag`) do not byte-match the file's Table1 records, so a
   file→runtime record transform exists but its builder was not isolated.
4. The mesh struct fields feeding the builder (`+0xC`=source verts,
   `+0x14`=records, per 0x800792CC/0x800792D4) are written in the C++ setup
   path (e.g. `stw r15, 0xC(r25)` @0x800737E0) which was not fully traced.

## 8. Next concrete experiment

**A. Static (cheap):** In the 0x80072000–0x80074000 parser region, find the
function that writes the 16-byte runtime draw records (search for the
`bonemap` 256-byte table construction and the record writer that packs
`b8→[0]`, `variant→[3]`, `count→[4]`, `u0→[8]`). Its input pointers reveal
which file bytes become the 12-byte source verts.

**B. Empirical (decisive):** Run the game in Dolphin, break at the vertex
builder (0x80078C6C), dump the 28-byte runtime vertex buffer and the 12-byte
source buffer. Correlate source bytes with file offsets → the file→source
mapping falls out immediately, and the position formula can be verified
against known geometry.

**C. Data-side:** Re-examine the YOBJ file for 12-byte-aligned vertex data
outside the parsed batch/Table1/Table2 regions (the file has unaccounted
bytes; the parser may mis-split a 12-byte vertex region as 6-byte batches).

---

## Files

- `tools/dol/dolmap.py` — DOL section map + address helpers
- `tools/dol/effscan.py` — addis/addi effective-address xref scanner
- `tools/dol/funcmap.py` — function boundary detection
- `work/main.dol` (+`.map`) — extracted executable (3.3 MB)
- `work/dis_f_80078C6C.txt`, `work/dis_f_80080070.txt`, `work/dis_yobjparse.txt`,
  `work/dis_loader.txt`, `work/dis_caller80070.txt` — disassemblies
- `work/effpairs.json` — 8590 effective-address pairs
