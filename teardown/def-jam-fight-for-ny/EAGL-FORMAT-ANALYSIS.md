# Def Jam FFNY EAGL .o Format Analysis

**Date:** 2026-10-15
**Status:** Format partially mapped. Full .o → glTF conversion requires additional RE.

## File Structure

```
0x00: 10 fb          SHPS magic (EA proprietary)
0x02: 00 95          Size/type field (varies per file)
0x06: 7f 45 4c 46   ELF magic (borrowed, NOT standard ELF)
0x0A: 01             ELF class (32-bit)
0x0B: 01             ELF data (little-endian)
0x0C: 01             ELF version
0x0D: 00            padding
0x0E: 14 00          e_type (NOT 0xE100 as teardown doc suggested for all files)
0x10: 03 03          e_machine (NOT 0xC730 for all files)
...
0x490f: ".data"      Section name string (varies by file)
```

**Note:** The teardown doc's claim of e_type=0xE100/e_machine=0xC730 does not
match the CAW part .o files sampled (V2CP_110_0001_A.o, V2CP_110_0001_B.o).
Those values may apply to fighter .o files (V2IP_xxx.o) but not CAW parts,
or the doc sampled different files. Per-file validation needed.

## Observed Data Patterns

### Index/vertex-like region (0x30–0x130)
Repeating 4-byte pattern: `XX 8b 40 0f` where XX increments (0x03, 0x04, 0x05...).
This is likely a triangle index buffer or display list with a fixed stride.
The `8b 40 0f` bytes may be opcodes or packed vertex references.

### Float regions
Sparse plausible float triplets found at 0x1c8+ (e.g., 0.505, -9.195).
Not dense enough to be a straightforward vertex array — may be
bone positions, bounding volumes, or compressed data.

## What .o Files Contain (per teardown)

| File | Size | Contents |
|------|------|----------|
| `V2IP_xxx.o` | ~5KB | Skeleton/rig definition |
| `V2IP_xxx_F.o` | ~1.4KB | Face; references `__PosePaletteBank` |
| `V2CP_xxx.o` | ~20KB | CAW part geometry + rig refs |

## .ssh Files

SHPS containers. Some are meshes (~47-55KB for CAW parts), some are
tiny metadata files (518 bytes, e.g. shop catalog entries with
"Buy ERTS" strings). The mesh .ssh files were not sampled in this pass.

## What's Needed for Full Conversion

1. **EAGL section header parsing** — locate .data, .rel, __EAGL_TOOLLIB_VERSION
2. **Vertex format identification** — stride, component types (float/half/int16?)
3. **Index buffer location** — the `8b 40 0f` pattern needs decoding
4. **UV/normal channels** — not yet located
5. **Bone weight/palette mapping** — __PosePaletteBank references
6. **Texture binding** — .ssh texture files pair with .o geometry

## Recommendation

The .o → glTF pipeline is a multi-day RE project, not a single-session task.
Priorities for unblocking:
1. Sample a mesh .ssh file (47-55KB) — may be easier than .o
2. Compare multiple .o files to identify the vertex stride
3. Look for existing EAGL tools in the modding community

## Files Analyzed
- `V2CP_110_0001_A.o` (20,346 bytes, SHA a2fb7dce...)
- `V2CP_110_0001_B.o` (20,138 bytes)
- `V2CP_110_9999_A01_01.ssh` (518 bytes, metadata only)
