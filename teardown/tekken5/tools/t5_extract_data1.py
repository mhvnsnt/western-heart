#!/usr/bin/env python3
"""Extract Tekken 5 (PS2) TK5DATA1.BIN via the TK5DATA3.BIN code overlay.

Port of the community flow in smb123w64gb/Tekken5_Tools
(TK5AssetRipPS2.py + FileTableGetPS2.py + decNLZ1.py +
package_fmt_pkg.py), stdlib only, credited inline. No pycdlib needed:
the BINs come out of the ISO with the repo's own
tools/iso9660_extract.py first.

Flow:
  1. Parse TK5DATA3.BIN as a PKG container (u32 count, then
     count x (offset u32, size u32) mappings; files are the data at
     those offsets). files[5] is the NLZ1-compressed "Code" blob.
  2. NLZ1-decompress files[5] -> Code blob (LZSS, 11-bit offset,
     5-bit length, 2048-byte window — same family as tk5psp_dec).
  3. Read the PS2 LUT from Code at TABLESTART 0x0027B5B0
     (1571 entries, 8 bytes each: offset u32 x 0x800, size u32) and
     the u32 checksum array at CHECKSTART 0x0027E838.
  4. For each entry, slice TK5DATA1.BIN; if the u32 word-sum matches
     the stored checksum, write raw; else decrypt with the sector
     cipher (seed = entry index) and re-check; else report failure.
  Output files are named %04i.bin (index only — the table carries no
  filenames). Raw archive bytes stay OUT of git.

Usage:
  python3 t5_extract_data1.py TK5DATA3.BIN TK5DATA1.BIN --out outdir
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from romd_extract import decrypt_sector_data_fast, word_sum  # noqa: E402

SECTOR = 0x800
TABLESTART = 0x0027B5B0
CHECKSTART = 0x0027E838
TABLECOUNT = 1571


# ---------------------------------------------------------------- NLZ1
def unpack_sc3game(src):
    """Port of decNLZ1.unpack_sc3game (Tekken5_Tools). LZSS: flag byte,
    bit=1 literal, bit=0 back-reference token (offset 11 bits,
    length 5 bits, 0 means 32/2048). Flag byte 0 terminates."""
    src_pos = 0
    dst = bytearray()
    while True:
        flags = src[src_pos]
        src_pos += 1
        if flags == 0:
            break
        while flags > 1:
            if flags & 1:
                dst.append(src[src_pos])
                src_pos += 1
            else:
                token = (src[src_pos] << 8) | src[src_pos + 1]
                src_pos += 2
                offset = token & 0x7FF
                if offset == 0:
                    offset = 0x800
                length = (token >> 11) & 0x1F
                if length == 0:
                    length = 0x20
                pos = len(dst) - offset
                if pos < 0:
                    raise ValueError(
                        f"invalid backref offset={offset} length={length} "
                        f"dstlen={len(dst)}")
                for _ in range(length):
                    dst.append(dst[pos])
                    pos += 1
            flags >>= 1
    return bytes(dst)


# ---------------------------------------------------------------- PKG
def pkg_read(data):
    """Port of package_fmt_pkg.PKG.read (Tekken5_Tools). Returns the
    list of file blobs. Layout: u32 count, then count x (offset u32,
    size u32); files are the data at those offsets."""
    count = struct.unpack_from("<I", data, 0)[0]
    if count >= 30:
        raise ValueError(f"PKG count {count} >= 30 — not a PKG container?")
    mappings = []
    for i in range(count):
        off, size = struct.unpack_from("<II", data, 4 + i * 8)
        mappings.append((off, size))
    return [data[off:off + size] for off, size in mappings]


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("code_bin", help="TK5DATA3.BIN")
    ap.add_argument("data_bin", help="TK5DATA1.BIN")
    ap.add_argument("--out", default="tk5data1_out")
    ap.add_argument("--no-decrypt", action="store_true")
    args = ap.parse_args()

    code_data = Path(args.code_bin).read_bytes()
    data_blob = Path(args.data_bin).read_bytes()
    print(f"code archive: {args.code_bin} ({len(code_data)} bytes)")
    print(f"data archive: {args.data_bin} ({len(data_blob)} bytes)")

    files = pkg_read(code_data)
    print(f"PKG: {len(files)} files")
    if len(files) <= 5:
        print("FAIL: PKG has <= 5 files, files[5] does not exist")
        return 1
    print(f"files[5]: {len(files[5])} bytes (NLZ1-compressed Code blob)")
    code = unpack_sc3game(files[5])
    print(f"Code blob decompressed: {len(code)} bytes")
    if len(code) < CHECKSTART + TABLECOUNT * 4:
        print("FAIL: Code blob too small for the PS2 LUT + checksum array")
        return 1

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    raw_ok = dec_ok = fail = skipped = 0
    for indx in range(TABLECOUNT):
        sector, size = struct.unpack_from("<II", code, TABLESTART + indx * 8)
        if size == 0xFFFFFFFF:
            skipped += 1
            continue
        off = sector * SECTOR
        chunk = data_blob[off:off + size]
        if len(chunk) != size:
            print(f"  {indx:04d}: entry runs past end of data archive")
            fail += 1
            continue
        cksum = struct.unpack_from("<I", code, CHECKSTART + indx * 4)[0]
        if word_sum(chunk, size) == cksum:
            (outdir / f"{indx:04d}.bin").write_bytes(chunk)
            raw_ok += 1
        elif not args.no_decrypt:
            buf = bytearray(chunk)
            decrypt_sector_data_fast(buf, indx, size)
            if word_sum(bytes(buf), size) == cksum:
                (outdir / f"{indx:04d}.bin").write_bytes(bytes(buf))
                dec_ok += 1
            else:
                print(f"  {indx:04d}: checksum mismatch even after decrypt "
                      f"(size {size})")
                fail += 1
        else:
            print(f"  {indx:04d}: checksum mismatch (decrypt disabled)")
            fail += 1
    print(f"done: raw {raw_ok}, decrypted {dec_ok}, failed {fail}, "
          f"empty {skipped} -> {outdir}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
