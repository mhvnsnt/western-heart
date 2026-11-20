# Tekken 6 PSP — ROUND 13 JOB 4: COM B4 binary command encoding

Date: 2026-10-22, round 13. Inputs: round-7 moveset JSONs
(`teardown/tekken6/movesets/`, 18 files) + the COM plaintexts in the
retained workdir `decoded76/` (idx58–75). Census data:
`tools/round13-evidence/r13_com_census.json` (per file: count word,
name-record count, tail stubs verbatim, MOTA chunk words, and all 31
pointer-table slots classified by offset/length/entropy/zero
fraction/first 16 bytes).

## (a) The 4×20B tail records — CENSUS VERDICT: empty MOTA stubs, not commands

All 72 tail records (4 per file × 18 files) are **byte-identical** —
exactly one distinct value in the whole set:

```
4d4f5441 01000000 14000000 00000000 00000000 00000100
"MOTA"   ver = 1  size = 20  0          word = 256
```

They are empty MOTA chunk headers (a 20-byte chunk whose declared
size is its own header), not per-move command records. The round-6/7
"108 records" total decomposes as 36 real MOTA chunks (2 per file)
+ 72 of these stubs. Correlation against the real MOTA chunks they
follow: none — the stubs are identical in every file regardless of
the preceding chunks' parameters (e.g. ARMOR_KING's real chunks carry
parameter words 0 and 33; its stubs are the same bytes as JIN's).
They read as placeholder/terminator slots for animation chunks the
PSP build does not populate. **The tail is closed: no command data
lives there.**

The two real MOTA chunks per file share the header shape
`MOTA, ver 1, hdrsize 20, param, 256, …` followed by u16-pair tables
(chunk 1: repeated `0x0008` entries after a `0x0100/0x0001/0x000f/
0x0048` prologue; chunk 2: repeated `0x04fc` entries) — animation
track tables, consistent with rounds 6–7, not command records.

## (b) The 32-slot pointer table — section classification (all 18 files)

Slot 31 is the (0,0) terminator in every file; slots 20–22 are
zero-word_a aliases of slot 19's section in every file. Classes by
size range / entropy / first bytes (full table in the census JSON):

| slot | len range | entropy | reading |
|---|---|---|---|
| 0 | 15,520–33,680 | 2.6–3.3 | localized string data (starts mid-UTF-8 Japanese text; the pointer lands inside the string region) |
| 1 | 7,288–11,912 | 2.1–2.2 | zero-led sparse table (74% zeros) |
| 2 | 4,704–8,424 | 2.1–2.2 | sparse table, u32-led (`60 00 00 00 05 00 00 00 8d 01…`) |
| 3 | 2,316–2,484 | 2.6–2.7 | small record table (`2a 00 00 00 … f1 00 00 00` repeating frame) |
| 4 | 3,052–3,276 | 3.0 | dense small records; len/word_a is a constant 15.725 across files (both scale together; not an integer stride) |
| 5 | 166,368–219,072 | 2.0–2.2 | **largest section**: s16 sequence tables (descending runs `0x96 0x96 0x82 0x78 0x64 0x46 0x3c 0x1e…`) — curve/track data |
| 6 | 41,984–82,176 | 2.2–2.3 | u32-led structured table |
| 7 | 172–216 | 1.6–2.2 | tiny table with 0x7fff constants |
| 8 | 34,500–88,008 | 2.4–2.6 | u32 record table (strong size scaling) |
| 9 | 252–636 | 1.9–2.0 | tiny index table (`2d 00 00 00 50 80 00 00 01…`) |
| 10 | 108–348 | 1.5–1.8 | tiny index table |
| 11 | 92,928–146,960 | 3.1–3.2 | second-largest: u32 offset/record stream (`24 00 00 00 91 80 00 00 02 74…`) |
| 12 | 3,456–4,844 | 2.7–2.8 | mixed data, lowest zero fraction of the low slots |
| 13 | 1,168–1,296 | 3.0–3.2 | `19 00 00 01 ff ff ff ff` framed records |
| 14 | 6,176–7,088 | 1.9 | paired-u16 table (`3b 00 09 00 c8 01 00 00` frame) |
| 15 | 21,660–23,316 | 4.9–5.1 | mid-entropy structured data; len tracks name count at r=0.96 (size scaling, see (c)) |
| 16 | 1,840–4,740 | 1.8–2.2 | sparse table; word_a tracks name count at r=0.96 (see (c)) |
| 17 | 6,236–23,484 | 2.3–2.4 | record table, strong scaling |
| 18 | 5,312–12,352 | 4.1–4.5 | mid-entropy records |
| 19–22 | 1,572–2,364 | 3.1–3.3 | one section, four slots (20–22 aliases): u32 stream `06 71 00 00 23 71 00 00 41 71…` (incrementing 0x71xx values — index/offset ladder) |
| 23 | 160–280 | 1.9–2.5 | tiny table |
| 24 | 20 | 0.9–2.6 | **single 20-byte record** in every file |
| 25 | 1,812–2,652 | 5.5–6.1 | high-entropy — compressed/encoded candidate |
| 26 | 4,168–4,708 | 7.1–7.4 | **near-random entropy** — compressed or encrypted candidate |
| 27–29 | 20 each | 3.7–4.3 | three 20-byte high-entropy records (hash-like) |
| 30 | 644 | 6.9–7.1 | fixed 644 bytes in every file, high entropy |

## (c) Encoding-hypothesis tests against the name vocabulary — NOT PROVEN

Tests run across all 18 files (name counts N = 210–943 per file from
the round-7 JSONs):

- **No slot in any file** satisfies word_a == N, and no slot
  satisfies len/stride == N for stride ∈ {8, 12, 16, 20, 24, 28, 32,
  40, 48, 64} (one coincidence: RAVEN slot 0, a string section).
  The brief's primary hypothesis — a fixed-stride command section
  whose record count equals the name count, first field = name
  ordinal — is **falsified** for the pointer-table sections.
- Strongest correlations with N are size-scaling artifacts: slot 15
  len r=0.96, slot 16 word_a r=0.96, slots 17/18 r≈0.92 — but none
  is an exact or integer relationship (slot 16's word_a spans only
  5,415–5,829 while N spans 213–943; it behaves like a base value
  plus a small per-move increment, not a count).
- **Where the input notation demonstrably lives:** inside the
  per-move name records themselves. A glyph census over all 7,341
  record hexes finds a Private Use Area alphabet — U+E000–U+E020+
  codepoints occurring thousands of times (U+E018 ×6,162, U+E01C
  ×5,830, U+E016 ×5,450, U+E015 ×4,920, U+E004 ×3,999, …) in runs
  like `ee8095 ee8096` (U+E015 U+E016). These are the game font's
  button/direction glyphs: the localized description strings inside
  each move record carry the move's input notation as glyph
  codepoints. Decoding them to Tekken notation needs the font's
  glyph→button map (the font texture + its glyph table) — the same
  NTPP texture problem as Job 1, font instance.

**Verdict: binary command encoding NOT PROVEN this round.** The
pointer-table sections contain no name-indexed fixed-stride command
list (falsified, not merely untested). Exact residual, two named
hops (not chained this round): (1) the PUA glyph map — extract the
font glyph table and map U+E000–U+E02x to buttons/directions, then
every move's notation is readable from its own record; (2) the
high-entropy slots 25/26/30 — deflate/zlib probes and an entropy
profile per file to test whether they are compressed command/property
blobs (slot 26 at entropy 7.1–7.4 with a structured 16-byte head
`10 00 01 00 00 01 00 07 …` is the prime candidate).

## (d) The count-word "176" — verdict: still unproven, narrowed

Per-file count words @+12: 7–16, sum 176 (the "176" is just the
sum). Tested against: name-record count (r=−0.11), file size
(r=−0.13), ASCII string count (r=−0.08), UTF-8 run count (r=−0.13),
nonzero word_a slots (constant 22), distinct slot offsets (constant
28), MOTA offsets (constant 6). It matches **nothing** in the file's
own census and does not scale with moveset size. Bounded hypothesis:
it is a small structural count of something outside the COM file's
own tables — e.g. the count of sub-entries in the character's
DATA401 directory record, or a category count (throws/strings
classes) defined by the game's external move-category table. It is
NOT a moveset-size measure and must never be used as one.
