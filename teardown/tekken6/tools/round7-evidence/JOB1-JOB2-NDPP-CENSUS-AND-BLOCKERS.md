# Tekken 6 PSP — ROUND 7 JOB 1/2: NDPP census, package formats, blockers

Date: 2026-10-21, round 7 attempt 3. Scripts in this directory:
`r7_container_dir.py`, `r7_census.py` (+ `r7_census.json`),
`r7_extract_boxes.py`, `r7_build_glb.py`. Inputs: verified clean
bytes only (regenerated bulk + `decoded76/`, retained workdir).

## JOB 1a — Container directory SOLVED (new this round)

Every non-COM decoded container is a chunk-directory file:
header `(u32 slot_count, u32 header_size)` + `slot_count ×
(u32 chunk_size, u32 cumulative_end_offset)`; chunks tile the
file exactly to EOF (type A: 13 slots / 112 B header; type B:
6 slots / 64 B header incl. 8 B trailing). Verified arithmetically
on the top-76 files; the census classifier uses the same layout.
Full writeup: `JOB1-CONTAINER-DIRECTORY.md`.

## JOB 1b — Package classification (byte-proven, top-76)

| Package | Count (top-76) | Slot layout |
|---|---|---|
| Character model | 12 | slot0 NDPP body section, slot1 `BONE` body skeleton (8,032 B; idx04: 10,768 B), slot2 optional float chunk, slot6 48 B table (starts u32 5), slot10 NDPP head section (~17 KB), slot11 name chunk (`kao_…` strings / `MODEL_HEAD`), slot12 `BONE` head skeleton (1,664 B, constant in 12/12) |
| Stage / object | 16 | slot0 NDPP 624 B (transform node: quaternion floats 0.707/±0.5, count words, offset 416 — NOT geometry), slot6 48 B table, slot7 2,384 B offset table (0x950-stride records), slot8 BE-headed chunk (counts 5/48/224/272…), slot9 LARGE payload (61–218 KB, big-endian control words `00000002 00000020 00000040 00000060…`, content 94.6% float-like — the stage geometry stream), slot11 `tfm_…` name chunk (e.g. `tfm_cmnglow000_O_OBJ_O_HIR_`) |
| Texture (NTPP) | 29 | slot0 `NTPP` main section, slots1–3 352 B sub-headers (start u32 42), slot4 texture payload. The 352 B entries also appear as sub-entries inside the NTPP span in the slice census |
| Stub / other | 2 tiny + fragments | directory + small chunks only |

`BONE` format (partial): magic, u32 version 1, u32 100, u16 1 +
u16 6, then a count word (146 in idx04's slot-1 chunk, 22 in the
1,664 B head chunk, 110 in the EBOOT-embedded default template at
ELF VA 0x08bdaab0), then per-bone data (floats incl. 1.0/−1.0
axis values in the template). Record stride not yet proven.

## JOB 1c — Full census of the entry-87 slice (clean bytes)

`r7_census.json` (5,470 containers, sha256 + slot maps each):

| Class | Count |
|---|---|
| A-model (directory + NDPP slot) | 3,702 |
| B-texture (directory + NTPP at header end) | 1,432 |
| dir-other (directories/stubs without NDPP/NTPP slot-0) | 336 |
| **Total (adler-exact)** | **5,470 / 5,470** |

NDPP literal occurrences in the slice: **1,565, all 1,565 with
sane size fields** (20 ≤ size, section fits in slice).

Scale note: 3,702 A-model packages for a ~40-character roster
means most are customization items / stage objects / per-costume
parts, NOT whole characters. Per-character assignment of embedded
packages is NOT yet proven (no name strings inside A-packages
except head/name chunks; assignment needs DATA401 index-order
analysis against the top-76 anchors — named blocker B3).

## JOB 1d — NDPP section interior: what is proven, what is not

Proven on clean bytes (idx00 body section, 78,560 B, flags
0x20001):
- Header 20 B; then exactly 2 descriptor records of 64 B
  (rec0: center floats + bbox `x[-90.3,90.3] y[1657.8,1906.5]
  z[-79.9,148.9]`, words (0, 48, 12, 5); rec1: second bbox,
  maxy 1894.5), then a count word **3120** at offset 148.
- The remaining ~78 KB is a dense interleaved stream: unit-normal
  float3 runs (norms 0.89–0.94) in groups, separated by ~48 B
  block headers carrying increasing counters/offsets (2832, 2784,
  4192→5232→5440…). A cell-type map of the whole section is in the
  lane's scratch analysis (normals throughout; NO float3 run
  matches the descriptor bbox as raw positions).

NOT proven (the remaining format fight):
- The vertex position/index encoding. Positions are not stored
  as plain float3 arrays in NDPP sections (cell-map evidence);
  candidates not yet excluded: quantized (s16) streams inside
  the interleaved blocks, or positions reconstructed from the
  block headers + normals + BONE transforms by the loader.
- `MOTA`-style GE-command patterns appear in stage NDPP tails
  (words like 0x80030001), suggesting part of the stream is
  PSP GPU display-list data; decoding needs the loader.

Blocker B1 (the NDPP mesh crack): EBOOT parser RE. Evidence
trail for the next lane: the EBOOT (decrypted ELF in
`teardown/tekken6/decrypted/`) contains NO `NDPP`/`MOTA` string
and no stored NDPP magic constant — sections are dispatched by
directory slot, not by magic. The `NTPP` default template
(VA 0x08b9c5b0) is referenced by an NTPP object constructor at
0x892fdf0 (stores template ptr at +0x64, vtables at +0x0/+0x5c);
the `BONE` default template (VA 0x08bdaab0, 110 bones) has no
direct lui/addiu xref within 64 B windows (base-register access
likely). A Ghidra pass (~/workspace/tools/ghidra/ 12.1.4) over
the model-loader class hierarchy around these constructors is
the scoped next step — it is a multi-hour job and did not fit
this lane's survival window; NOTHING about the vertex layout is
claimed beyond the evidence above.

## JOB 2 — Batch meshes: what shipped, what is blocked

Shipped (supersedes the incomplete round-2 GLB):
- `models/ndpp_bounding_volumes_r7.glb` — complete clean-bulk
  re-extraction with the round-2 validated box method:
  **1,222 sections with boxes, 11,663 boxes** (old GLB: 357
  sections / 1,103 boxes from corrupt bytes). GLB verified:
  1,147 section meshes (75 sections' boxes collapse under the
  builder's corner mapping — same behavior as the round-2
  builder), **images: 0** — bounding volumes carry no textures,
  so the textures-baked law has nothing to attach to here; this
  is stated, not hidden.
- Renders VIEWED by this lane: `renders/r7ndpp_grid.png`
  (complete grid) vs the original `models/previews/preview_grid.png`.
  ORIGINAL-COMPARISON: same construction, same orange-cuboid
  visual language; the R7 grid is the same data family at
  35×35 sections vs 19×19 — the boxes are the originals' boxes
  plus the ~10.5k the corrupt bytes hid. These are bounding
  volumes (collision/culling), NOT character meshes — the file
  and this doc say so wherever they are named.

Blocked (honest): per-character mesh GLBs. No character mesh can
be built until B1 (vertex/index layout) falls. Shipping the
bounding volumes AS meshes would be exactly the speculative
geometry this sweep forbids. Per-character mesh inventory is
likewise blocked on B1 + B3; the package-level inventory
(JOB 1b/1c) is the current byte-proven state.

## Textures (NTPP) status

NTPP packages are classified and counted (1,432 in slice + 29
top-76) but not yet decoded to images: NTPP section interior
(GIDX/CLUT-style data visible after the header in the EBOOT
template) is undecoded, so no texture can be baked into any GLB
yet. Pairing evidence for when it lands: DATA401 entry order —
character A-packages and B-texture packages interleave in entry
order (e.g. entries 457a=A-model, 457b=B-texture; 478a/478b,
520a/520b), the same pairing the top-76 index already shows.
