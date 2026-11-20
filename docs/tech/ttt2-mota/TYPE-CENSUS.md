# TTT2 MOTA type census — all 6 nonzero tables (2026-11-03)

Source: `data004/data004-decoded.bin` (6,522,032 B, sha256
`18b18d0ff2356219e9fac852eaa48f6b0a839479ea41f6d4b94069b5f86b2b21`),
manifest `data004-decoded.bin.mota-manifest.json`. Classification by the BE
u16 start marker at each entry (100 = 0x64 compressed, 200 = 0xC8 raw);
frame counts for 0xC8 from header `+4` (BE u32), for 0x64 from the proven
header field at `+4+2N` (BE u16). Zero parse errors across all 1,970 slots.
Machine-readable detail: `type-census.json` (same folder).

## Totals (all 6 tables)

| class | entry slots | unique clips | frames (unique) | frames (all slot refs) |
|---|---|---|---|---|
| 0xC8 raw (fully decodable today) | 60 | 20 | 37,408 | 42,460 |
| 0x64 compressed (stream undecoded) | 1,892 | 1,143 | 81,189 | 122,399 |
| shared-offset refs (marker 16384, mid-clip) | 12 | 4 | — | — |
| null slot (index 0 of each table) | 6 | — | — | — |
| **total** | **1,970** | **1,167** | **118,597** | **164,859** |

## Per table

| table | @offset | slots | 0xC8 slots/unique | 0x64 slots/unique | 0xC8 frames (unique) | 0x64 frames (unique) | notes |
|---|---|---|---|---|---|---|---|
| 0 (big) | 256 | 1,875 | 42 / 3 | 1,820 / 1,077 | 848 | 80,019 | +12 shared-offset slots (4 unique); 1 null |
| 1 | 4,246,608 | 64 | 2 / 1 | 61 / 55 | 60 | 831 | 1 null |
| 2 | 4,502,200 | 12 | 0 / 0 | 11 / 11 | 0 | 339 | 1 null |
| 3 | 4,522,680 | 1 | 0 / 0 | 0 / 0 | 0 | 0 | null slot only |
| 4 | 4,584,448 | 17 | 16 / 16 | 0 / 0 | 36,500 | 0 | all 0xC8, **4 tracks**, F=2000–2500 |
| 5 | 6,460,448 | 1 | 0 / 0 | 0 / 0 | 0 | 0 | null slot only |

## Validation notes

- 0xC8 size formula `8 + 4N + 12·N·F` re-checked against the allocated span
  for all 20 unique 0xC8 clips: **19 exact**; the 1 exception is table 4's
  last entry (index 16), whose span runs to the next table and includes
  123,528 B of trailing data after its expected 115,224 B end — consistent
  with padding/trailing data, not a formula failure.
- The 42 big-table 0xC8 slots point at only **3 unique clips** (indices 685,
  725, 727 — N=23, F=128/360/360); heavy slot duplication is normal for this
  table (1,820 0x64 slots → 1,077 unique).

## What this decides — buildable today

- **Full-body (23-track) 0xC8 motion: only 4 unique clips, 908 frames**
  (big-table 685/725/727 + table-1's one 60-frame clip). These decode fully
  NOW with `ttt2_mota_decode.py`.
- Table 4's 16 0xC8 clips (36,500 frames) are **4-track** — long, low-channel
  clips (camera/face-class data, not 23-track body motion); decodable by the
  same layout but not fighter body banks.
- **The bulk of fighter motion — 1,143 unique 0x64 clips, 81,189 frames —
  is blocked** on the 0x64 compressed-stream decoder, for which no public
  decoder exists (Kiloutre + Blender importer implement 0xC8 only).
  Unblocking it = reverse the stream format or extract the game's own
  decompression routine from the X360 binary (Ghidra route).
