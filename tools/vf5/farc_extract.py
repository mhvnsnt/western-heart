#!/usr/bin/env python3
"""Extract VF5 PS3 .farc archives (FArC magic, BE u32 entries, gzip payloads).
Usage: farc_extract.py <archive.farc> <outdir>
Writes each inner file decompressed; prints a manifest.
"""
import gzip
import os
import struct
import sys


def parse_farc(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:4] == b"FArC", f"bad magic in {path}"
    hdr1, hdr2 = struct.unpack(">II", data[4:12])
    entries = []
    pos = 12
    while pos < len(data):
        end = data.index(b"\x00", pos)
        name = data[pos:end].decode("ascii", "replace")
        p = end + 1
        a, b, c = struct.unpack(">III", data[p:p + 12])
        p += 12
        entries.append((name, a, b, c))
        pos = p
        # stop when the next bytes look like payload (gzip magic) not a name
        if data[pos:pos + 2] == b"\x1f\x8b":
            break
        # also stop if remaining bytes can't hold another entry
        if pos + 16 > len(data):
            break
    return hdr1, hdr2, entries, data


def main():
    src, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    hdr1, hdr2, entries, data = parse_farc(src)
    print(f"{src}: hdr=({hdr1:#x},{hdr2:#x}) entries={len(entries)}")
    for name, a, b, c in entries:
        # field order hypothesis: (offset, comp_size, decomp_size)
        off, comp, decomp = a, b, c
        blob = data[off:off + comp]
        ok_gzip = blob[:2] == b"\x1f\x8b"
        try:
            raw = gzip.decompress(blob) if ok_gzip else blob
        except Exception as e:
            print(f"  !! {name}: gzip fail ({e})")
            raw = blob
        status = "OK " if (ok_gzip and len(raw) == decomp) else "?? "
        print(f"  {status} {name}: off={off} comp={comp} decomp_field={decomp} "
              f"actual={len(raw)} gzip={ok_gzip}")
        with open(os.path.join(outdir, name), "wb") as f:
            f.write(raw)


if __name__ == "__main__":
    main()
