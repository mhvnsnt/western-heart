# TTT2 Container Analysis — 2026-10-25 (watchdog resume)

**Lane:** `ttt2-resume-100` (TTT2 100% teardown into western-heart).
**Branch:** `feat/ttt2-teardown-100` @ `1dcc5a6` (extraction 72/72 CRC-verified).
**Samples:** 9 pulled bins in `~/workspace/_ttt2-work/pulls/` (sha256 in
`pulls/pull-manifest.json`): `data000/004/018/019/050/052/053.bin`,
`data026.bin`, `nrfo.bin`. All analysis below was run against those files,
2026-10-25 10:25 CDT. Disk was 87% (14G free) — no bulk pulls.

## 1. nrfo.bin — SOLVED: 42-file archive of NRFO-box files

- Bytes 0–3: big-endian u32 **count = 42**.
- Bytes 4–0x153: 42 × (offset, size) big-endian u32 pairs.
- Table ends at `0x154` — **exactly the first entry's offset**.
- Entries tile **contiguously with zero gaps/overlaps**; last entry ends
  exactly at EOF (`0x48ec8` = file length).
- Entry sizes 68–43,676 bytes.
- **Every entry starts with a 20-byte `ftyp` box**: size `0x14`, `'ftyp'`,
  `'nrfo'`, version `0x00010001`.
- So `nrfo.bin` is an index file: `[count][(offset,size) × N][N × ftyp-headed files]`.
- Strings inside also show `'nrfo'`, `'head'`, `'ofsi'`, `'ofsd'` boxes
  deeper in the entries — the per-file box layout is the next parse target.

## 2. data026.bin — NRFI box file, parses cleanly (256 bytes)

| Offset | Size | Type | Notes |
|---|---|---|---|
| 0x00 | 20 | `ftyp` | `'nrfi'`, version `0x00010001` |
| 0x14 | 28 | `head` | |
| 0x30 | 200 | `idgt` | |
| 0xF8 | 8 | `imge` | empty/tail box |

Total = 256 = file length. BMFF-style `[u32 size][4s type]` boxes,
big-endian, same family as the NRFO entries above.

## 3. The `0f f5 12 ed` containers — header + table-like head, encrypted/compressed payload

All 7 files (`data000/004/018/019/050/052/053.bin`) share a 12-byte header:

| Field | Value |
|---|---|
| magic | `0f f5 12 ed` |
| version | u32 LE = `1` |
| word2 | u32, differs per file — **not** CRC32/Adler32 of payload (`@12`), whole file, or payload `@16` (all tested, no match) |

After the header each file has a **structured low-entropy head** of
varying length, then a **high-entropy payload** (Shannon ~7.5 bits/byte
per 512-byte block, 0–2 zero bytes per block):

| File | Size | Approx. structured-head length |
|---|---|---|
| data019.bin | 31,624 | ~0x1C |
| data053.bin | 412,736 | ~0x28 |
| data018.bin | 557,332 | ~0x30 |
| data052.bin | 2,659,880 | ~0x40 |
| data004.bin | 4,075,114 | ~0x60 |
| data050.bin | 3,683,036 | ~0x90 |
| data000.bin | 4,064,970 | ~0xA0+ |

Head length grows with file size — consistent with a **file table whose
entry count scales with the container**. `data000`/`data050` heads show
repeating 4-byte groups with `0x00` high bytes (u24-style values); the
grouping is not yet decoded (no clean offset/size tiling found under
BE/LE u16/u32 reads at offsets 0x0C–0x10).

Negative results (all tested 2026-10-25):
- No zlib or LZMA stream at offsets 12, 16, 32, 64, 128, 256, 512, 1024.
- No printable ASCII strings ≥ 4 chars in `data019.bin` (payload is not plaintext).
- Word2 is not a CRC32/Adler32 of any obvious span.

Working hypothesis: head = plaintext (or lightly-obfuscated) file table;
payload = encrypted or custom-compressed (Namco X360 container family).

## 4. Next experiments (in order)

1. **LZX decompress** on the payload — LZX is the X360-native compression;
   try at the head/payload boundary per file.
2. **XOR keystream test**: XOR payload head against known plaintext
   (`ftyp`/`nrfo` box headers are the expected plaintext if the payload
   holds box files) and look for a repeating key.
3. **Head-entry count**: decode the `data000`/`data050` head groups and
   compare entry count vs. file size across all 7 files.
4. **Search QuickBMS / Xentax / X360 SDK tooling** for magic `0F F5 12 ED`.
5. Once the payload opens: apply the TKMovesets TTT2 struct reference
   (`docs/TTT2-MOVESET-STRUCT-REF.md`) to per-character move binaries;
   characters + moves first per owner order 2026-10-14.

## 5. Reproduce

```python
import struct
b = open('pulls/nrfo.bin','rb').read()
count = struct.unpack('>I', b[:4])[0]          # 42
entries = [struct.unpack('>II', b[4+i*8:12+i*8]) for i in range(count)]
assert entries[0][0] == 4 + count*8            # table ends at first offset
assert all(entries[i][0]+entries[i][1] == entries[i+1][0] for i in range(count-1))
assert entries[-1][0]+entries[-1][1] == len(b) # last entry ends at EOF
```

Status doc: `TEARDOWN-STATUS-20261025.md` (same dir). Bins are NOT committed
(repo AGENTS.md rule 8: public repo, no copyrighted game files); reproducible
from release `ttt2-7z-v1` via `tools/ttt2_virtual_god.py --pull`.

---

## 6. `0f f5 12 ed` = X360 LZX — SOLVED (2026-10-25 ~11:30 CDT, watchdog run)

The payload is **X360 LZX-compressed data** (`xbdecompress` format). Magic
`0F F5 12 ED` is the X360 LZX signature (HCS Forum / vgmstream, 2018:
"NFS: The Run on X360 has some SB files compressed with X360 LZX...
They start with magic number: 0F F5 12 ED").

### 6.1 Format

```
[12-byte header] [head] [chunk 0] [chunk 1] ... [chunk N-1]
  magic 0F F5 12 ED | version u32 LE = 1 | word2 u32 (per-file, not a CRC)
  head = per-file structured bytes (length scales with file size;
         data000 ~132 B, data004 ~84 B, data050 ~120 B, data019 8 B,
         data053/018 20 B, data052 60 B — exact head ends below)
  chunk = [u16 BE compressed-size][LZX block data]
```

- **Chunk framing:** each chunk is prefixed by a 2-byte big-endian
  compressed size. The chain tiles exactly to EOF (verified for all 7 files).
- **LZX stream:** MS-PATCH/WIM framing — 1-bit E8 flag (stream start only),
  then per block: 3-bit block type (1 = verbatim, 2 = aligned,
  3 = uncompressed) + 24-bit uncompressed block length. Window = **128 KB
  (2^17)** — the only window size that decodes (15/16/18/19/20/21 all fail).
- **Sections:** the file is divided into **128 KB (0x20000) compressed
  sections**; each section is an *independent* LZX stream (fresh state,
  E8 bit present). A chunk prefix landing exactly on a 128 KB file offset
  starts a new section. Sections may be padded with **2 zero bytes** before
  the boundary (data050 @393214, @1179646; data000 @1048574;
  data004 @3932158) — the chain resumes at the boundary.
- **Multi-block chunks:** a chunk may hold *multiple* LZX blocks
  (e.g. data018 chunk67 = 18453 + 14315 = 32768). Always request 32768
  bytes per chunk; fall back to the first block's peeked length only if
  that fails. Requesting only the first block's length leaves the window
  short and the *next* chunk fails.
- **Bit order:** 16-bit little-endian words, MSB-first (same as CAB/MS-PATCH).
- **Negatives that shaped this:** XOR (single-byte, 4-byte word2) is noise;
  no zlib/LZMA anywhere; raw LZX at any offset fails (the stream is
  chunk-framed, not raw); CAB-wrapper decode fails (not CAB framing);
  the bitstream does NOT continue across chunks (per-chunk fresh bit
  buffer is correct — a continuous-stream decode fails, including the
  data019 control).

### 6.2 Decoder

`tools/lzx-decode/` in this repo (built and verified this run):

- `lzx_chunks.c` — chunk-chain decoder (the tool). Usage:
  `lzx_chunks <file> <chunk_start_offset> <window_bits=17> <outdir>`.
  Handles sections, 2-byte padding, multi-block chunks.
- `lzx_try.c` — single-shot probe (`lzx_try <file> <offset> <window> <outlen>`).
- `reactos-lzx.c` / `lzx.h` — LZX decoder from ReactOS
  (`dll/win32/mspatcha/lzx.c`, cabextract-derived, Stuart Caie, LGPL).
- `windef.h` / `winbase.h` — minimal stubs so the ReactOS code builds on Linux.
- Build: `gcc -O2 -o lzx_chunks lzx_chunks.c -I.` (no deps beyond libc).

### 6.3 Decode results — all 7 files 100% decoded

| File | Compressed | Chunks | Sections | Decoded | First chunk data offset |
|---|---|---|---|---|---|
| data019.bin | 31,624 | 6 | 1 | 177,104 | 20 |
| data053.bin | 412,736 | 107 | 4 | 3,461,024 | 32 |
| data018.bin | 557,332 | 95 | 5 | 3,027,808 | 32 |
| data052.bin | 2,659,880 | 485 | 21 | 15,463,552 | 72 |
| data000.bin | 4,064,970 | 557 | 32 | 17,755,827 | 144 |
| data004.bin | 4,075,114 | 212 | 32 | 6,522,032 | 96 |
| data050.bin | 3,683,036 | 1,385 | 29 | 44,928,288 | 132 |
| **Total** | **~16.5 MB** | **2,849** | — | **~91.3 MB** | — |

Every decoded file starts with the same 20-byte NRFI `ftyp` box
(`00000014 66747970 6e726669 00010001`) followed by a `head` box — the
payloads are NRFI box files, same family as `data026.bin` / the `nrfo.bin`
entries (§1–2).

### 6.4 What is in the decoded data (spot checks)

- **data018** (3.0 MB): move list — 59 `MVLT` tags; move names in plain
  text: "Left Right Combo", "Reverse PDK Combo", "Jab Roundhouse",
  "Jab Sweep", "Piston Fire", "Quick PK Smash", "Hammer of the Gods",
  "Shoulder Tackle", "Lion's Roar", "Body Blow to Sway", "Phoenix Wings",
  "The Boot", "Hammer Punch", "Hang Over", "Bone Breaker",
  "Demolition Man", "Enma's Fury", "Inner Torment", " during hit ".
- **data000** (17.8 MB): moveset XML — `<?xml version="1.0"?>`,
  `<DirectionOffsets>`, `<KakeaiOffset>`, `imge paof`.
- **data004** (6.5 MB): `imge MOTA` (motion/animation data).
- **data050** (44.9 MB): `superX70P`, `Lunch Box?` — character/item names;
  75% zero bytes (sparse table region).
- **data019 / data053 / data052**: NRFI box files (`ftyp`/`head`/`idgt`/`imge`).

### 6.5 Reproduce

```sh
# pull the 9 bins (release ttt2-7z-v1) then decode, e.g. data018:
./tools/lzx-decode/lzx_chunks pulls/data018.bin 32 17 /tmp/dec018
# concatenate chunkNNN.bin in order for the full decoded file.
```

Decoded binaries are NOT committed (repo AGENTS.md rule 8: no copyrighted
game files). They are reproducible from the release via the tool above;
local copies live in `~/workspace/_ttt2-work/decoded-*.bin` (91 MB, 2026-10-25).

### 6.6 Next steps

1. Map `dataNNN.bin` → characters / moves (owner priority: characters +
   moves first, order 2026-10-14). data018 = move list; data000 = moveset
   XML; data004 = MOTA animation; data050 = names/sparse tables.
2. Apply the TKMovesets TTT2 struct reference
   (`docs/TTT2-MOVESET-STRUCT-REF.md`) to the decoded move binaries.
3. Pull the remaining 33 `dataNNN.bin` files one at a time (disk-gated)
   and decode with the same tool.
4. STFS/GoD teardown results → western-heart roster + moveset library,
   WH PIPELINE rename + RENAME-MAP.md, incremental commits + PR + merge.
5. TeraBox via parent browser lane.
