# KoC2 MVS motion files — structural survey

Source: `kc2firemvs/` — 16,660 files. Surveyed 2026-11-19 (lane W2)
with `tools/koc2_mvs_survey.py`. The bitstream itself is NOT decoded;
this documents the structure found so far.

## Headline facts

- **16,660 files, only 8,205 distinct contents** (max 36 copies of one
  motion). Shared motions are stored per (wrestler, move) slot;
  duplicate groups are scattered across the file index (only 14/8455
  duplicate pairs are adjacent), so the file index is a global motion
  ID, not grouped by content.
- **Sizes**: 197–12,503 bytes, mean 2,392, median 2,063. No size
  alignment (mod 4 uniform) — consistent with a bitstream, not
  fixed-size records.
- **Every sampled file ends with a 0x00 byte** (bitstream zero padding).
- **Byte 1 is very likely a frame (or keyframe) count**: in the
  dominant header combo (n=10,784), corr(byte 1, file size) = 0.83,
  size ≈ 596 + 16.1 × byte 1. Byte 1 range 5–255 (≈0.08–4.25 s at
  60 fps). Marginal cost ≈16 bytes/frame — far too small for dense
  per-frame joint data (26 joints × 3 axes would be ~150 B/frame),
  so the format is keyframed/sparse or delta-compressed.

## Header families (bytes 2–3)

| Bytes 2–3 | Count | Notes |
|-----------|-------|-------|
| (0x00, 0x02) | 15,672 | Family A (main) |
| (0x01, 0x00) | 964 | Family B (larger files, mean ~5,000 B) |
| (0x02, 0x00) | 20 | Rare |
| (0x03, 0x00) | 4 | Rare |

Top header combos (off0, off2, off3, off4, off6, off7):

| Combo | Count |
|-------|-------|
| 0x6B, 0, 2, 0x00, 0x02, 0x10 | 10,784 |
| 0xEB, 0, 2, 0xC0, 0x0A, 0x50 | 3,170 |
| 0xEB, 0, 2, 0xC0, 0x06, 0x90 | 1,330 |
| 0xDF, 1, 0, 0x00, 0x03, 0x00 | 618 |
| 0xEF, 1, 0, 0x00, 0x10, 0x00 | 198 |

Byte 0 low bits are near-constant within a family (Family A: bits
0–1 = 11; Family B: low 5 bits = 11111) — the header is likely
bit-packed, not byte-aligned fields. Byte 5 is a small count (1–10,
frequency falling with value) that does NOT scale the bytes/frame
(22–27 B/frame across all values), so it is not a joint/channel
count — more likely a subtype or a count of something fixed-size.

Bytes 6–7 form a pair: in the 0xEB family, off6 + (off7 >> 4) = 15
(off6 ∈ {4,6,7,8,9,10} → off7 ∈ {0xB0,0x90,0x80,0x70,0x60,0x50});
in the 0x6B family off6=2, off7=0x10 (sum 3). The pairing suggests
two counts that sum to a constant, or one number plus a complement
— not yet understood.

## Open work

- Decode the bitstream: needs the ELF `MotionBase` loader
  (xref at 0x1189B8) disassembled, or a known-plaintext attack
  (e.g., a motion whose frames are known, such as an idle stance).
- Map motion IDs to (wrestler, move): file 01999's move-group table
  (255 groups × 4 motion IDs = 1020 slots) is the link; the
  `MotionBase` chunk maps IDs to MVS file indices.
- Compare against the AKI/No Mercy 26-joint animation work in
  western-heart (proven retarget pipeline) for layout ideas — the
  per-frame cost rules out a dense No Mercy-style layout.
