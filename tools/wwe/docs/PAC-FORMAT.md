# WWE 2K19 PAC container formats

Reversed from public sources and verified against real 2K19 PACs
(the 66-PAC moves pack and the 920-PAC entrance pack). All integers
are little-endian unless noted. The unpacker is `pac_unpack.py`.

## HSPC (2K17+ primary container)

- Magic `HSPC` at 0.
- File count: u32 @0x38.
- Name table at 0x800: 8-byte names, 0x14 stride, 16-hex uppercase
  (e.g. `49A7B83B6A6A23E8`).
- Info table at `round_down(u32@0x18, 0x800) + 0x1000`: 0xC-byte
  entries (offset x0x800, length x0x100).
- The "FileNames" footer formula from WrestleMINUS (u32@0x3C +
  0x2000) does NOT point at real data in 2K19 PACs — it lands inside
  the last entry. Skip it (the original tool skipped it too).

## SHDC (2K17+ secondary container)

- Magic `SHDC` at 0.
- Flavour u32 @0xC: 1 = plain, table at u32@0x1C; 0x10 = 0x10
  spacer; 0x800 = 0x800-scaled.
- Info length u32 @0x20; 0x10-byte entries (name u32 hex, skip
  FFFFFFFF; offset u32; length u64).
- **Part count is u32 @0x38** (proven by probing — the count field
  wins over info_len//0x10 when sane; the byte length at 0x20 is
  the table's *allocated* size and can exceed count*0x10, which is
  what nested SHDCs inside `_param` files do).
- Count = min(u32@0x38, info_len//0x10, room in file).
- Skip entries named `0x42494C5A` ("ZLIB"): a footer/index record,
  not a data part — its "length" u64 packs (stream_len,
  uncompressed_len) of the first ZLIB part, and its "offset" points
  inside that part's stream (verified exactly on RandyOrtonTitle2belt:
  entry [9] low32 0x1964 / high32 0x5720 = entry [0]'s ZLIB wrapper
  values). Skipping loses nothing.

## EPK8 (2K15/16 container)

- Magic `EPK8` at 0. Directory tree at 0x800, count u16/4,
  0x10 stride, offset x0x800 + 0x4000, length x0x100.
- Part names can contain slashes — tree paths like `EVP3/109`
  (entrance script) and `EVZ2/109` (entrance zone data).

## EPAC

- Magic `EPAC` at 0. Count u16/3, 4-char names, 0xC stride.

## PACH

- Magic `PACH` at 0. Count u32 @4, 0xC entries at 0x8, data after
  the table.

## YANMPack (animation clip container)

- Big-endian. YANM length u32 @4, header length u32 @0xC.
- Entries from 0x70, 0x28 stride: name 8 chars at +4, offset
  BE u32 at +0x24 (plus header length), length BE u16 at +2
  (x0x20 bytes).
- Entries point at `YANM`-magic clips. A motion `.bin` block is a
  YANMPack: proven by exact arithmetic (header 192 + clip1 14688 +
  clip2 10144 = 25024 = part length).

## ZLIB wrapper

- `ZLIB` + `30 12 00 00`, u32 @8 compressed length, u32 @12
  uncompressed length, zlib stream at 0x10. Standard library
  `zlib` decodes it.
- Quirk: in some EVZ2 SHDCs the part length counts the ZLIB stream
  only, not the 16-byte wrapper header, so the part slice is 16
  bytes short of the full stream (the tail sits in the gap before
  the next part). The unpacker extends the slice from the parent
  buffer using the wrapper's declared compressed length.

## BPE wrapper (Yukes BPE)

- `BPE ` magic, u32 @8 compressed size, u32 @12 uncompressed
  size, stream at 0x10.
- Stream = blocks of (256-entry pair table, u16 LE payload
  length, payload). The pair table is run-length coded (control
  byte c <= 127 -> c+1 explicit pairs; c > 127 -> c-127 identity
  pairs + 1 explicit pair). Expansion uses a push-down stack.
  Output is zero-padded to the declared size.
- See `yuke_bpe.py` (pure Python re-implementation from the
  publicly documented algorithm).

## OODL wrapper (Oodle Kraken)

- v6: `OODL` + 4 zero bytes + `30 00 06 2E` + `KRKN`,
  u32 @0x10 uncompressed length, u32 @0x14 compressed length,
  raw Kraken stream at 0x18.
- v7 swaps the length fields (compressed at 0xC, uncompressed at
  0x14; no `KRKN` at 0xC).
- Decoded with libooz (`Ooz_Decompress`) via `oodle_krk.py`.
  Note: the ooz CLI prepends an 8-byte u64 uncompressed-size
  header to its own compressed output — strip it before feeding a
  stream to the decoder.

## Unpacker behaviour

- Recursive: containers inside containers are unpacked in place.
  Compressed parts are decompressed inline (looping for nested
  compression) — a container result gets a subdirectory, a leaf
  is written directly under the parent outdir.
- `--flat` keeps YANMPack / TextureLibrary parts as `.bin` leaves
  (the batch-1 layout).
- `--list` prints the container tree without writing.
- Every run writes a `FILES-SHA256.txt` manifest (sha256 of every
  output file) in the output root.
- `write_leaf` creates the file's real parent directory (EPK8
  leaf names contain slashes, e.g. `EVP3/109`).

## Verified unpacks (2026-11-19)

**Moves pack** — 66 PACs, 180 MB (34 motion PACs, 2K15–2K20):
217,901 files, 179,890,161 bytes, 28,828 containers, 174,460 BPE +
6 ZLIB decompressed, 0 skipped, 0 errors. Type tally: bpe 174,460;
bin 24,535; shdc 23,893; yanm 18,862; yanmpack 4,862; hspc 66;
zlib 6; pach 1.

**Entrance pack** — 920 PACs, 720 MB (445 wrestler-named entrance
PACs + victory/particle/prop/gimmick PACs, recovered from the
original Archive.org ZIP after the GitHub release tarball turned
out truncated at 175 MB): 22,069 files written (22,067 unique —
two Dean Ambrose clips are stored twice with identical bytes),
1,597,019,074 bytes, 7,734 containers, 355 ZLIB + 2,394 BPE + 180
OODL decompressed, 0 skipped, 0 errors. Contents: 13,837 YANM,
6,128 .bin, 2,053 DDS, 49 YOBJ. Three format quirks were found and
fixed along the way (see above): the `EVP3/109` directory creation,
the ZLIB 16-byte slice extension, and the SHDC `ZLIB` footer record.

**`50_mpc.pac` `--flat` check** — 906/1000 files byte-identical to
the earlier batch-1 extraction; the 94 differences are the
ported-moves mod replacing those motion blocks (batch-1 files are
0 or 128 bytes there; the mod pack has real content). 0 missing,
0 extra. Entry hash names match batch-1 exactly.
