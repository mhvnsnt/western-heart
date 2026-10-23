# DOA4 Phase 8 — Job 2: anm.afs head/index format — FINDINGS

File: `anm.afs`, 2,949,120 bytes (0x2D0000), copy in phase-7 scratch (`p7/data/anm.afs`, from release `doa4-mirror` @2898390016).
Head under study: `[0, 0x6B000)` = 438,272 bytes = 27,392 × 16-byte records. Head SHA-256: see `phase8/tools/anm_head_census.py` output in `phase8/ANM-CENSUS.txt`.
Method: full-file 4KB entropy scan, full head census (every field, every record — no sampling), per-position entropy/equality analysis, s16 channel decomposition, grid/smoothness tests, byte-exact round-trip test. Tools: `phase8/tools/anm_head_census.py`, `phase8/tools/anm_head_deep.py`, `phase8/tools/anm_head_s16.py` (committed; scratch originals in `~/workspace/_doa4p2-scratch/p8/work/`).

## 1. Region map (confirmed + refined)
- Head `[0, 0x6B000)`: uniform entropy 6.84 in every 4KB block (no internal transition) — one homogeneous transformed/structured region.
- `0x6B000` sharp transition to entropy 5.24 → plaintext BE float region `0x06B000–0x16B000` (phase 7).
- `0x16B000–~0x29D000`: low-entropy mixed/sparse-integer region (entropy 1.8–3.9, phase 7), with local high-entropy spikes (e.g. `0x1AB000` 6.91, `0x20D000` 7.24) — candidate additional structured chunks, NOT yet censused.
- Chunk at `0x2A1000`, length `0xE000`: entropy 3.54 by 4KB scan (phase 7's 6.82 reading was a single-block value) — its structure DIFFERS from the head: as 16B records its `+8` u32 is 0 in 2,912/3,584 records and takes 373 distinct values (head: 135). Sparse table, not the head's record type. Zero padding `0x2AD800–0x2AF000`.
- `0x2AF000–0x2CD000`: high-entropy (7.2–7.3) plaintext float region (phase 7); sample 8-float groups at `0x2B0000`: `[-0.0301, 0.0355, 0.0792, -0.7255, -0.5411, 0.4253, 0.3832, 0.8441]` — plausible animation-curve values, confirmed. Zero run `0x2CD800–0x2CE000`, floats continue to EOF.

## 2. Head census (all 27,392 records)
Distinct u32 values per field (BE): `+0`: 14,862 · `+4`: 12,711 · `+8`: **135** · `+12`: 8,349.
- CORRECTION to phase 7: the "+8 takes only 68 distinct values" figure is a PER-64KB-BLOCK count, not global. Per-block distinct counts: 76, 68, 75, 64, 83, 100, 87 (blocks at 0x00000–0x60000). Global = 135.
- `+8` decomposes cleanly: hi u16 = 22 distinct values, lo u16 = 21 distinct values (full enumerations in `ANM-CENSUS.txt`).
- Per-byte-position entropy is wildly non-uniform — the record has real internal structure: pos1 = 2.80 bits (0xFF in 18,632/27,392 = 68%), pos9 = 1.03 bits (0x1F 15,496 / 0xFF 11,766 / 0x3F 61), pos11 = 1.00 bits (0x1F 16,564 / 0xFF 10,736), pos8 = 3.08, pos10 = 3.03, pos0 = 6.04, all other positions ≈ 7.0–7.4.
- Within-record byte equalities: pos3==pos4 (0.72), pos2==pos7 (0.68), pos5==pos6 (0.65), pos13==pos15 (0.69), pos12==pos14 (0.57), pos1==pos9 (0.31), pos1==pos11 (0.27).
- Stream self-similarity: byte equality at lag 16 = 0.407, lag 32 = 0.124, all other lags ≤ 0.16 — the 16-byte record grid is REAL.

## 3. s16 channel decomposition (record = 8 × BE s16)
- ch4: min −31,745, max +31,775, mean −28,374 (≈ −0.866 in Q15); **99.7% of values satisfy (v+1) mod 32 == 0**; consecutive-record |step| mean 1,549; step==0 in 49.6%.
- ch5: min −31,745, max +31,807, mean +28,632 (≈ +0.874); **99.8% on the same (v+1) mod 32 grid**; step==0 in 48.9%.
- ch0: always ≤ −15 (min −19,969, mean −7,235); 69.2% on the (v+1) mod 32 grid.
- ch1, ch2, ch3, ch6, ch7: full-range, NOT on the grid (≤ 6%), large consecutive steps (mean |step| 12,283–14,661 of a 65,536 range).
- ch6 == ch7 exactly in 40.2% of records; |ch6 − ch7| ≤ 64 in 53.0%.
- No channel quadruple gives a unit quaternion: norm² medians for (0,1,2,3)=1.044 (p10 0.288 / p90 1.745), (4,5,6,7)=2.114, all others worse. NOT a raw quaternion stream.
- Records are NOT frame-sequential animation samples: median total |step| between consecutive records = 70,419 (of max ~524k); 20,114/27,391 consecutive pairs exceed a 20,000 total-step threshold. Whatever the records index, they are not ordered keyframes.

## 4. Interpretation (evidence-backed, semantics NOT proven)
- ch4/ch5 behave like a quantized PAIR: near-constant magnitudes ≈ ∓0.87, values on a 1/1024 grid stored as `v = 32k − 1`. The all-ones low 5 bits (the `−1`) are exactly what a BIT-PACKED field layout produces when the following field is frequently negative (its sign bits land in this field's low bits) — i.e. the true field boundaries likely do NOT sit on byte boundaries, and the 16B "record" is the byte-aligned shadow of a bit-packed stream. This also explains pos9/pos11 collapsing to {0x1F, 0xFF} (sign-extension patterns) and phase 7's exclusion of byte-aligned XOR/ADD period-16 generators.
- The structural parse (27,392 records × 8 × s16 BE) re-serializes BYTE-EXACT (round-trip test in census tooling: parse → pack == original, SHA-256 match). That proves the container grid only — any fixed-width parse round-trips — and is NOT claimed as a semantic decode.

## 5. Verdict + the exact missing piece (Job 3 gate)
The head's SEMANTIC format is **not decoded**: record semantics (what ch0–ch7 mean, which records belong to which clip/stream, how the head indexes the float body regions) remain unknown, and no honest clip can be built from it. Job 3 therefore ships NO clips (no speculative clips, per instructions).
Missing piece, exactly: **the bit-level field layout of the head stream and its record→stream mapping.** Decisive next route (not attempted this session — time-boxed after Jobs 1/4 evidence): trace the XEX anm READER from the CRI file-open path (filename/CRI strings) in the existing Ghidra project `~/workspace/ghidra-projects/doa4/` (DOA4.gpr present, verified this session) — the reader's shift/mask pattern will name the field widths directly. Secondary test: bit-unpack the head at candidate field widths (9–13 bits) and re-run the grid/smoothness census on the unpacked fields.
