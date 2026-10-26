# lzx-decode — X360 LZX decoder for TTT2 `0f f5 12 ed` containers

Decodes the `0F F5 12 ED` files from Tekken Tag Tournament 2 (X360 GoD).
Format cracked 2026-10-25 (worker-watchdog run): see
`../CONTAINER-ANALYSIS-20261025.md` §6 for the full spec.

## Format (short)

- 12-byte header: magic `0F F5 12 ED`, version u32 LE = 1, word2 u32.
- Per-file head (length scales with file size), then chunks:
  `[u16 BE compressed-size][LZX block data]`, tiling exactly to EOF.
- LZX: MS-PATCH/WIM framing, 1-bit E8 flag at stream start only,
  3-bit block type + 24-bit block length, **128 KB (2^17) window**.
- File = 128 KB compressed sections; each section is an independent LZX
  stream (fresh state, E8 bit present). A chunk prefix on a 128 KB file
  offset starts a new section. Up to 2 zero bytes may pad before a
  section boundary.
- A chunk may hold multiple LZX blocks — always request 32768 bytes
  per chunk (fall back to the first block's peeked length only on failure).

## Build

```sh
gcc -O2 -o lzx_chunks lzx_chunks.c -I.
gcc -O2 -o lzx_try lzx_try.c -I.
```

No dependencies beyond libc. `reactos-lzx.c` / `lzx.h` are the LZX decoder
from ReactOS (`dll/win32/mspatcha/lzx.c`, cabextract-derived, Stuart Caie,
LGPL); `windef.h` / `winbase.h` are minimal stubs so it builds on Linux.

## Usage

```sh
# Decode a whole file (chunk_start = offset of the first chunk-size prefix)
./lzx_chunks <file> <chunk_start> 17 <outdir>
# chunkNNN.bin files appear in <outdir>; concatenate in order for the
# full decoded file.

# Probe a single offset/window (rc=0 + sane output = valid LZX start)
./lzx_try <file> <offset> 17 32768
```

Known chunk starts (first chunk-size prefix offset):

| File | Chunk start |
|---|---|
| data019.bin | 20 |
| data053.bin | 32 |
| data018.bin | 32 |
| data052.bin | 72 |
| data000.bin | 144 |
| data004.bin | 96 |
| data050.bin | 132 |
| data007.bin | 2812 |

Decoded binaries are NOT committed (repo AGENTS.md rule 8: no copyrighted
game files). Reproduce from release `ttt2-7z-v1` via
`tools/ttt2_virtual_god.py --pull`, then run this tool.
