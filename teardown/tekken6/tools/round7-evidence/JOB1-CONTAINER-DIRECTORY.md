# Tekken 6 PSP — ROUND 7 JOB 1 (interim): container directory cracked

Date: 2026-10-21, round 7 attempt 3. Inputs: clean `decoded76/`
(adler-exact, retained workdir). Script: `r7_container_dir.py`.

## The decoded containers are chunk-directory files (byte-proven)

Every non-COM decoded file (top-76 idx0–57 AND the 5,470 embedded
containers in the entry-87 slice — same first-4 classes) opens with:

| Word | Meaning |
|---|---|
| +0 u32 | slot count: **13** (NDPP type, header 112 B) or **6** (NTPP type, header 64 B) |
| +4 u32 | header size = 8 + 8×count (112 / 64) |
| then count × (u32 chunk_size, u32 cumulative_end_offset) | chunks tile the file **contiguously from header end to EOF**; empty slots have size 0 |

Verified exactly on idx00 (tiling: 112 +78,560 NDPP +8,032 +48
+17,024 NDPP +32 +1,664 = 105,472 = EOF) and idx04 (112 +896 NDPP
+10,768 +1,904 +48 +15,664 NDPP +16 +1,664 = 31,072 = EOF).

## Contents by slot (idx00 / idx04 evidence)

- Slot 0 chunk starts with `NDPP` (size = NDPP section size field).
- A second `NDPP` section appears later in the same file (idx00:
  @86,752 size 17,024; idx04: @13,728 size 15,664) — so each type-A
  file holds **2 NDPP sections** plus non-NDPP chunks between/after.
- The final chunk is **1,664 bytes in both files** — a constant-size
  tail (skeleton/bone-table candidate; under analysis).
- Type-B files hold `NTPP` sections (texture side): idx02 has NTPP
  at 64 and a run of NTPP magics spaced 1,136 B apart near EOF.

## Census over the top-76 decoded set (clean bytes)

- 58 non-COM files: 28 contain NDPP (46 NDPP magics total), 44
  contain NTPP (809 magics), 16 contain both, 2 tiny files neither
  (idx56: 336 B, idx57: 416 B — pure directory + small chunks).
- The 18 COM files remain moveset-only (round 6, still valid).

Status: directory layer SOLVED. NDPP section interior (descriptors →
geometry) is the next step; the earlier "no vertex arrays" negative
was withdrawn in round 6 and is being re-derived on clean bytes.
