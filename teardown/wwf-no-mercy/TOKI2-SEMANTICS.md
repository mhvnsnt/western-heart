# Toki2 semantics — status (2026-10-13)

## The header
Every AkiAnimation file starts with 4 bytes ("Toki2" per VPWStudio
AkiAnimation.cs), then N×98-byte frames. File size is always exactly
`4 + N*98`.

## Measurements
- **Not CRC32**: tested against frame data (zlib.crc32) — no match.
- **Not unique**: 6 duplicate toki2 values in 0x2DD9–0x2E00 (39 files).
- **Not frame count**: correlation with frame count is −0.019 (n=103).
- **Duplicates are related**: files sharing toki2 usually have the SAME
  frame count (e.g. 5ff9ce29: two files, both 11f; 6efe132c: three files,
  all 8f). One case has different counts (a009d02b: 45f vs 70f).
- **Duplicate content**: sometimes identical (0x2DE4/0x2DE5: byte-identical
  frame data), sometimes different (0x2DE2/0x2DE3: same size, different data).

## Interpretation
Toki2 is likely a **move-family ID** or **authoring tag**, not a content
hash. Files with the same toki2 are variants of the same move
(e.g. left/right versions, different intensities, or exact duplicates).

"Toki" (時) means "time" in Japanese, but there's no evidence it encodes
a timestamp or duration. The values span the full u32 range and don't
increase with file ID.

Full semantics require the AKI animation player code (to see how toki2
is consumed). The ROM data alone doesn't reveal it.
