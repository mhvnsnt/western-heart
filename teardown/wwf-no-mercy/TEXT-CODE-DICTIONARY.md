# No Mercy text-code dictionary — status (2026-10-13)

## What was known (from b421508)
Two classes: Class A (zero-width codes: FF, EF, 01, 19, 7F, DF, F7, FB, BF...)
and Class B (dictionary-expansion: AA 01→"ERICAN", 1C→"Buh").

## New findings (2026-10-13)

### AA 01 → "ERICAN" is UNIQUE
- Only ONE occurrence of `AA 01` in a text string in the entire ROM:
  `0x168D8A1`: `"R?EAL AM<AA><01>!` → "REAL AMERICAN!"
- All other `AA 01` byte pairs in the ROM are in binary/compressed data,
  not text strings.
- The substring "ERICAN" (or "AMERICAN", "MERICAN") does NOT exist anywhere
  in the ROM as a standalone string.

### 1C → "Buh" is context-dependent
- `0x168DEEA`: `Buh <1C>` → "Buh Buh" (expansion).
- But `1C` at the START of a music-table record is the music_id byte
  (e.g. `<1C>CHYNA` = id 0x1C, not a token). The expansion only happens
  mid-string.
- Other `1C` bytes in text banks are music_ids or binary data.

### Conclusion
These are NOT a general dictionary. They appear to be SPECIAL-CASE codes:
- `AA 01` might be "insert substring X" where X is hardcoded in the
  text renderer (not in a data table).
- `1C` mid-string might be "repeat previous word" (not a dict reference).
- OR the dictionary is in the executable code, not the text banks.

Full resolution REQUIRES the AKI text renderer (find via recomp/syms
cross-ref, or trace in an emulator). The ROM data alone does not contain
the expansion targets.

## Traps (from b421508, confirmed)
1. Music-table `1C`/`1E`/`1D` are ids, not tokens.
2. Literal `0x3F '?'` in "R?EAL AM" (ROM 0x168D89A) — possibly a typo.
3. Multi-byte `FD F0`, `FB F0`, etc. are record terminators, not text codes.
