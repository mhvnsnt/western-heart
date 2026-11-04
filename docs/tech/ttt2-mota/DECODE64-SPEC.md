# TTT2 MOTA 0x64 — DECODE SPEC (cracked from Default.xex, 2026-11-04)

The 0x64 motion format (1,143 unique clips / 81,189 frames in data004 alone)
had no public decoder. It is now reverse-engineered from the game's own
code and reimplemented as `tools/ttt2_mota_decode64.py`.

## Provenance — the XEX

- Source: owner's TTT2 Xbox 360 Games-on-Demand package (Archive.org item
  `tekken-tag-tournament-2_202609`, Title ID 4E4D0859, EU). GOD chunks via
  the wh-ttt2 surgical GOD reader; `Default.xex` lies entirely in Data0048
  (release `ttt2-work-archive-2026-10-30`).
- `Default.xex`: 15,941,632 B, sha256
  `e74e57de3e205517e5447cacdba68624544fbd313ddb8c5f174b8e3ff43283d8`,
  magic XEX2, image base 0x82000000, entry 0x82BD3D28, encryption NORMAL,
  compression BASIC. PE extracted independently with the `xex2` crate
  (18,481,152 B, sha256 `a793b684…`) — section table matches XEXLoaderWV's
  log exactly.
- RE stack: Ghidra 12.2 PUBLIC (sha256 `2c2cd776…`, NSA release) + JDK 25,
  XEX loader = zeroKilo/XEXLoaderWV (SaveEditors fork, release "12.1.3",
  sha256 `afdaf425…`; no LICENSE file in the repo — recorded honestly).
  Program: 31,820 functions (PowerPC:BE:64:A2ALT-32addr).
- The game never dispatches on the "MOTA" fourcc (zero occurrences in the
  xex). The animation sampler is `Function_8228B850`; the 0x64 frame
  expander is **`Function_822897D0`**; the 0xC8 path is
  `Function_8228F618`. Everything below is from the expander's decompile
  AND its disassembly (the two disagree in places; disassembly wins).

## Clip layout (all big-endian; clip = one MOTA table entry, u16 type 100)

```
u16 type=100, u16 N (tracks)
N x u16 track types            (4..7 = i16 tracks, >=8 = f32 tracks)
u16 F (frames), u16 A (shifts), u16 K (= number of f32 tracks)
K x f32 BE scales              (per f32 track, by f32-track ordinal)
initial pose (= frame 0): per track 3 x i16 (types 4..7) or 3 x f32
block index: nb x u32 BE offsets relative to index start,
             nb = ((F-2)>>4)+1  (F>=2); block streams at idx_start + ib[b]
```

A = shift field: hi byte → i16 tracks (pose pre-shift `>> (A_hi & 0x7f)`,
final `<< (A_hi & 0x3f)`); lo byte → f32 final `<< (A_lo & 0x3f)`.
Kiloutre's ByteSwap.py (independent) uses block count `(F + 14) >> 4` —
the same formula; it byte-swaps headers/poses/index only and contains no
decompressor, confirming none existed publicly.

## Frame model

Frame 0 = the stored initial pose. Block b's keyframe symbol yields frame
16b+1; its step symbols yield frames 16b+2 .. 16b+16 (capped at F-1).
The expander computes, for target frame g ≥ 1: block = (g-1)>>4, steps =
(g-1)&0xf — so at most 15 step symbols per block are ever read.

## Component streams

Per block, per track, per component (3, track-major order):

- byte0: `len = byte0 >> 2`; the stream pointer advances by `len`
  (disasm 0x82289FD4: stream += len). Bitstream is MSB-first, primed with
  (byte0 & 3) followed by the stream bytes — one continuous bitstream.
- Symbols, 4-bit code. (len, base) coding state persists across
  components within a block; resets per block.
  - 0 → (0, 0), delta 0
  - 1..12 → VLC: 1:(2,+1) 2:(2,-4) 3:(4,+5) 4:(4,-20) 5:(6,+21)
    6:(6,-84) 7:(8,+85) 8:(8,-340) 9:(10,+341) 10:(10,-1364)
    11:(12,+1365) 12:(12,-5460); delta = base + read(len)
  - 13 → raw signed i16
  - 14 → repeat-coding: cnt = read(4); this step plus (cnt-1) following
    steps each RE-READ a fresh value with the PREVIOUS symbol's
    (len, base). (Previous len 0 → delta 0; len 99 → terminate.)
  - 15 → terminate; remaining frames of the block hold the last pose.
- Keyframe symbol: stored_pose = shifted_initial + delta; velocity = 0.
- Step symbols: **velocity += delta; stored_pose += velocity** (double
  integration — disasm 0x82289E28/0x82289E38). Stored pose is an i16
  (wraps on store). The signature is unmistakable in real data: a dash
  encodes as keyframe offset + one large first acceleration + a decaying
  ~0 acceleration tail (constant velocity).
- Static component canonical form: bytes `08 3c` (len 2, delta 0, end).

## Final conversion (per frame)

- i16 track: `out = (stored << (A_hi & 0x3f)) * (pi/32768)`
  (constant at VA 0x82010CE4 = 9.58738019107841e-05). Frame 0 uses the
  unshifted initial instead.
- f32 track: `out = initial_f32 + (stored << (A_lo & 0x3f)) * scale[ord]`.
  Note: some f32 tracks carry ~0 scale (e.g. track 6 in many clips) —
  a real trait of the data, not a decode error.

Triples are per-axis Euler components (radians): hinge tracks prove it —
type-6 elbow/knee tracks move on exactly component 2 (components 0/1 are
identically zero over whole clips), matching the validated 0xC8 sample
(clip 685) structure. Track identities (Kiloutre labels): 0 Movement,
1 Position, 2 Unknown(fields 7-9, zero), 3 RootRot, 4 Spine1, 5 Hip,
6 Spine2 (f32, often ~0-scale), 7 NeckA, 8 NeckB/Head, 9/13 inner
shoulders, 10/14 arms, 11/15 elbows, 12/16 hands, 17/20 upper legs,
18/21 knees, 19/22 feet.

## Validation (data004, all six MOTA tables, 2026-11-04)

- 1,369 sized 0x64 entries parsed; 440k+ components decoded.
- Strict oracle (length-prefix walk lands exactly on every block end; all
  frames covered or terminated; decoder bits never exceed capacity + 24
  bits of reader prefetch slack): **432,337 components OK; ~90% of clips
  fully clean, zero exceptions.**
- Anatomical signature on decoded output (clip 621, entry 621, F=100):
  elbow/knee tracks (11/15/18/21) have component ranges
  [0.0, 0.0, 1.60..1.82] — single-axis hinges exactly as in the Kiloutre-
  validated 0xC8 data. Limb rotation max frame step 0.216 rad (smooth).
  Root channels use nearly the full i16 stored range (±32767) over long
  clips — exactly what the game's i16 pose storage implies.
- Moving render: entry 977 (F=30) decoded and played in a three.js
  skeleton viewer (headless Chromium): coherent humanoid, feet planted,
  upper-body motion reads cleanly. Proof video + decoded JSONs in
  `docs/proof/2026-11-04/ttt2-decode64/` and the lane report. The ad-hoc
  viewer's bone axes are approximate (Tekken bind conventions need the
  Blender/TekkenAnimHelper retarget for production banks) — the decoded
  channel data itself is what is validated here.

## Residual gap (honest)

~10% of clips (contiguous entry-index families, e.g. 27-32, 128-130,
507-514 in table 0) contain some components whose symbols exceed the
length capacity under the model above (5,724 of 440k components). No
correlation with the A field or track count. An encoder variant in those
families is not yet identified; those clips are reported by the tool's
accounting path, never silently mangled. The remaining ~90% — including
every clip needed for a first Roger/Jun bank shortlist — decode exactly.

## The join (status)

JOIN-SEARCH-ROUND3.md (this PR) completes the container sweep: data003,
005, 006, 019, 050, 051, 053 contain no per-move→MOTA join either
(data005/006 hold additional MOTA tables — the decoder above serves them
unchanged). Combined rounds 1-3: the join is in NO file container; it is
assigned when the game builds the motbin in memory (Kiloutre reads
`move:anim_addr` from live memory). Remaining routes, in order: (1) find
the motbin builder in Default.xex and trace how anim_addr is assigned
from bxml/mvlt data; (2) RPCS3 live-memory extraction. Neither was
reached this session — the decompressor consumed the lane. Banks for
Roger Jr./Jun are therefore NOT built yet; no mapping has been guessed.
