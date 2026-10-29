# JOB 2 VERDICT — VTYPE color-format 7 layout: CRACKED AND SHIPPED

**Status: COMPLETE. All 405 round-13 parts failures recovered.**

## The layout (from the VTYPE word, GE stream order)

```
weights   nw * wf bytes     VTYPE bits 14-16 = nw-1, bits 9-10 = wf (1 = u8)
uv        2 bytes           tc=1 (u8 x2)
color     4 bytes RGBA8888  offset aligned to 4
normal    3 bytes s8 x3     nrm=1 (6 bytes s16 x3 when nrm=2)
position  6 bytes s16 x3    pos=2, offset aligned to 2
          (12 bytes f32 x3  pos=3, offset aligned to 4)
stride    total aligned to 4
```

Round 9's decoder failed because its `COL_SZ` table has no entry for
color-format 7 — every `0x*31d`/`0x*33d`-family VTYPE raised
`IndexError` before a single vertex was read. Format 7 is the GE
RGBA8888 color format: 4 bytes, 4-byte field alignment. Every vertex
in the family carries the constant color bytes `80 80 80 ff`
(neutral grey) at the aligned offset — first visible in the raw
records of bulk3 (round-14 probe).

## Validation (before any GLB was written)

Over every col-7 unit in the 400 failed packages (validator:
full-bulk scan, units parsed per section):

- **10,648 units, 112,160 vertices**
- computed stride == pair-delta stride: **10,648 / 10,648**
- u8 weight sets sum to 128: **111,386 / 111,386**
- s8 normals unit length (|n| in [100,150] of 127): **58,453 / 58,453**
- descriptor-bbox containment (2% slack): **112,157 / 112,160**
  (3 outliers at descriptor float-rounding scale)
- distinct VTYPEs covered: 0x11d, 0x31d, 0x33d, 0x431d, 0x433d,
  0x831d, 0x833d, 0xc31d, 0xc33d, 0x1031d, 0x1033d, 0x1431d,
  0x1433d, 0x1831d, 0x1833d, 0x1c31d — weight counts 1–8, with and
  without normals.

Decoder parity: `tools/r14_ndpp_decode.py` delegates all non-7
formats to the round-9 layout — output on idx00 slot 0/10 is
byte-identical to r9 (3,217/821 verts, 1,897/489 tris, verts+tris+
normals equal).

## Two extra failure classes resolved on the way

- **KeyError-'pos' packages (4)** and **bulk955/bulk3715**: sections
  contain units with no position field and/or signature false
  positives. A unit whose pair offsets land outside the section is a
  false GE-signature match inside another unit's vertex stream —
  proven instance: bulk3745's "VTYPE 0x476bfd" claims pair offset
  5,859,594 in a 79,616-byte section. The r14 decoder skips
  out-of-section units and pos-less units (they carry no geometry).
  The round-13 truncated failure was the same class.
- The real units of bulk3745 decode normally once the false match is
  skipped.

## Batch result

- Attempted: 405 (400 IndexError + 4 KeyError + 1 truncated)
- **Recovered: 405 / 405** — 355,725 verts, 196,773 tris,
  11,237,548 GLB bytes, under `models/parts/seg{NN}/` as
  `bulk{NNNN}_slot0_r14.glb`
- Determinism: two independent batch runs produce sha256-identical
  GLB sets (405/405).
- Manifest: `r13_parts_manifest.json` gained an additive
  `round14_recovery` section (per-GLB sha256 + the round-13 failure
  each replaces); no original key touched (diff = insertions only).
- **Gate render VIEWED:** `r14_gate_bulk1934.png` (in this folder) —
  bulk1934_slot0_r14.glb (5,692 verts / 2,996 tris) renders as a
  coherent humanoid upper body: torso with chest/abs, shoulder
  armor, both arms ending in hands with fingers, T-pose. Not noise.

## Residual

None for this job. The col-7 family is fully decoded; together with
round 13 the slice now stands at 3,039 + 405 = **3,444 of 3,444
part sections decoded** (of 3,438 packages; multi-section packages
account for the difference — see r13 manifest).
