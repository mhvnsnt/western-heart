# DOA4 Phase 16 — Job 1: .mot expansion grammar

Source bytes: the 197 entries of release `doa4-mot-20261022`
(tar sha256 `026592a07c…21c` re-verified this lane; every entry
re-verified against `phase15/mot-entries-manifest.json`: 197/197
sha256 + size match). Tools: `phase16/tools/mot_parse_p16.py`
(record parser), `phase16/tools/t_census_p16.py`,
`phase16/tools/mot_items_p16.py`, `mot_items2_p16.py`,
`mot_items3_p16.py`. Grades as before.

## §1 The record layer is SOLVED — and phase 15's framing is corrected (PROVEN)

Phase 15 read the 44-entry descriptor as sitting *before* each
record with table A pointing *past* it. A monotonic-run census
over zack.mot (385 runs >= 20 words) shows the true layout,
identical in fighter files and t_* files:

- **A record = 44 sub-blocks followed by a 44-entry descriptor.**
  The descriptor holds u32 BE **absolute file offsets** of the
  44 sub-block starts, **in channel order** (not sorted order:
  in t_kl_gy rec 661 channel 33's block is the second in the
  span). A channel's sub-block size = (next larger descriptor
  value, or the descriptor start) − its descriptor value.
- **Table A (fighter) / the (id, offset) index (t_*) points at
  the DESCRIPTOR START.** Record k's sub-blocks tile
  [previous descriptor end, descriptor_k start); the last
  descriptor ends at EOF. Every file checked tiles exactly:
  zack triple (376 / 26 / 2 records), all 124 t_* files
  (530 records, 23,320 sub-blocks).
- The fighter **default record's sub-block span is the
  per-fighter shared front block** (zack: descriptor at
  data_start 22,936, values from 4,008; 44 sub-blocks of
  176–672 B totalling 18,928 B = the 18,924 B shared block + the
  4 B separator word). Phase 15's "degenerate 0-based descriptor
  at data_start−4" is this descriptor read from 4 B early: its
  values are absolute, starting at the shared block's start.
- t_* files carry NO table A / front block: index (2–12 pairs)
  + records in exactly the same framing. This answers Job 1(a)'s
  "decode its payload fully" at the record layer: a t_* file is
  fully segmented into (record, channel, offset, size) — the
  payload *inside* each sub-block is §3's residual.
- 88 sub-blocks are EMPTY (size 0, repeated descriptor value),
  all in m_zack's two trailing records (targets 579,200 and
  662,472, total span 0 + descriptor) — placeholder records.

## §2 Cross-class correlation (Job 1b) (PROVEN)

- Default-record size profiles are identical across zack /
  m_zack / c_zack (already known byte-identical).
- **c_zack's only real record (target 32,192) is byte-identical
  to zack.mot's record at target 1,151,992**: all 44 channel
  size profiles match exactly (distance 0) AND all 44 sub-block
  byte strings are equal. Where plain and c_ overlap, the
  encoding is not merely consistent — the bytes are the same
  record object. (Same pattern as the kasumi/rtm duplicates.)
- **m_zack's 25 real records are NOT the plain records at a
  different encoding**: no exact size-profile match exists, and
  the best cosine-similar plain candidates have per-channel
  size ratios scattered around ~2 (range 1.5–3.2) rather than a
  constant sampling factor — they are different (longer)
  motions. So the plain/m_/c_ classes hold mostly *disjoint*
  motion sets; "the same motion at different encodings" does
  not occur in the zack triple beyond literal copies. The
  descriptor-field question is thereby answered directly: each
  descriptor field *is* the absolute start of one channel's
  sub-block; what it "counts" is that channel's packed byte
  length (via sorted deltas), which §3 shows is not a simple
  multiple of a key count.

## §3 The payload layer (EVIDENCED structure; expansion RESIDUAL)

Sub-block payload facts (corpus: 41,096 sub-blocks from the
zack triple + all t_* records):

- Sizes are multiples of 4 B in the fighter files (16,500
  sub-blocks: all sizes ≡ 0 mod 4; 83% ≡ 0 mod 8) and multiples
  of 8 B in t_* files. First byte is 0x00 (83%) or 0xF0 (17%).
- The u16 vocabulary is heavily concentrated: 0x000C, 0x0000,
  0xFFFF, 0x0005, 0xF00C, 0xFF00, 0x00FF, 0x0010 alone are ~28%
  of all u16 words, at BOTH word parities (even-index share of
  "tag-like" words 0.332 vs odd-index 0.300 — **no fixed 4 B
  item framing**).
- Hand parses of many blocks show an item-like cadence of
  (u16 tag, 1–2 data u16s): with the best simple rule
  (k=2 iff tag low byte ∈ {0x0C,0x0E,0x10,…,0x3C}) **51.65% of
  blocks tile exactly** (uniformly ~51% across default/clip/t_/
  00-start/F0-start classes — no dialect split). But the rule
  is **falsified as a pure function of the tag**: constraint
  propagation (forward/backward tiling DP) shows tag 0x000C is
  *forced* to k=1 in some blocks and k=2 in others; low-byte
  vote shares on short blocks are ~55/45 for every low byte.
  Item length is therefore **stateful/contextual**, not
  tag-local.
- Delta-stream decodings are **refuted with controls**:
  byte-s8 / nibble-s4 / u16-s16 cumulative-sum smoothness on
  real payloads is statistically indistinguishable from the
  same metric on shuffled payloads (0.178 vs 0.183; 0.081 vs
  0.088; 0.227 vs 0.272). The payload is not a plain delta
  stream at byte, nibble, or u16 granularity.
- Constant channels exist and are recognizable: 8 B sub-blocks
  of the form `[00, X, V, 00|F0, 00, V]` (V a u16 value repeated
  at +2 and +6; byte 5 always 0x00) — e.g. value 0xF56F recurs
  as the constant of channels 31/33/39/41 across many zack
  records. So the encoding *can* express a constant channel in
  8 B; animated channels grow from there. This is evidence the
  payload is a key list whose per-key cost varies, not a
  fixed-rate sample stream.

**Exact residual (what defeats expansion):** the per-item
length rule inside a sub-block. All static evidence says items
exist (tag vocabulary + cadence + constant-channel form), but
their lengths depend on state the file bytes alone have not
yet yielded (preceding-item state, a per-channel mode set by
the record's first item, or a bit-level control stream
interleaved with the u16 data). Until that rule is known, no
value stream can be extracted without guessing, and **no clip
is assembled (gate G4 stays open)**. The two named routes to
the rule: (1) the XEX .mot *file-side* decoder — the same
frontier as Job 2's file-side writer (see `W21-TRACE.md` §3);
(2) a dynamic trace (Xenia) of one record's expansion.

## §4 What IS delivered for the clip lane
- `mot_parse_p16.py`: complete, exact segmentation of every
  .mot file into records/channels/sub-block byte ranges
  (the input any future expander consumes).
- The zack record inventory with per-channel sizes
  (in `t-census.json` for t_*; fighter records reproducible
  from the parser in seconds).
- The proven cross-class identity (§2) — any future grammar
  must expand zack@1,151,992 and c_zack@32,192 identically;
  they are the same bytes, so this is a parser regression test,
  not a grammar test. The grammar's real cross-class test will
  be: one rule expanding both a plain record and an m_ record
  (disjoint motions, same encoding family) to plausible curves.
