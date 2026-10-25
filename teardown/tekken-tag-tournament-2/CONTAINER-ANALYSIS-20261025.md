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
