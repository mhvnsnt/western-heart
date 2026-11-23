#!/usr/bin/env python3
"""koc2_iso_patch.py — surgically replace a file inside the KoC2 PS2 ISO.

The KoC2 ISO is plain ISO9660 with ONLY a primary volume descriptor
(sector 16) + terminator (sector 17) — no Joliet/SVD — plus a 4096-byte
tail past the ISO9660 end. A full ISO rebuild risks breaking the PS2
boot structure, LBA layout, and the tail, so this tool patches in
place instead:

  1. Parse the PVD, walk root -> DATA -> KC2FIRE.000, and read the
     file's extent LBA + data_length from its directory record.
  2. Copy the ISO (streamed, chunk by chunk — the ISO is 4.6 GB),
     write the new archive at the same LBA (the new file MUST be <=
     the original size; English text is shorter than Shift-JIS, so
     the patched archive shrinks), zero-fill the leftover bytes of
     the old extent.
  3. Update the data_length field (both-endian u32) in the file's
     directory record. Path tables carry no file sizes and need no
     change; the volume space size is unchanged.

Everything is done with seeks + bounded reads/writes: the ISO is never
loaded into memory whole.

Verification (run after patching): re-parse the patched ISO and check
the record; extract KC2FIRE.000 with 7z and compare its hash with the
new archive; confirm every other byte of the ISO is unchanged.

Usage:
  koc2_iso_patch.py <original.iso> <new-KC2FIRE.000> <patched.iso>
  koc2_iso_patch.py --info <iso>   (print the KC2FIRE.000 record)

KoC2 English lane, 2026-11-19.
"""
import shutil
import struct
import sys
from pathlib import Path

SECTOR = 2048
CHUNK = 16 * 1024 * 1024


def both_u32(buf, off):
    """Read an ISO9660 both-endian u32 (LE at off, BE at off+4)."""
    le = struct.unpack_from("<I", buf, off)[0]
    be = struct.unpack_from(">I", buf, off + 4)[0]
    assert le == be, f"both-endian mismatch at {off}: {le} != {be}"
    return le


def parse_dir_records(data):
    """Yield (record_offset_within_data, extent_lba, size, flags, name)."""
    i = 0
    while i < len(data):
        ln = data[i]
        if ln == 0:
            # Pad to the next sector boundary within this directory.
            i = (i // SECTOR + 1) * SECTOR
            continue
        rec = data[i:i + ln]
        extent = both_u32(rec, 2)
        size = both_u32(rec, 10)
        flags = rec[25]
        name_len = rec[32]
        name = rec[33:33 + name_len]
        yield i, extent, size, flags, name
        i += ln


def read_at(fh, lba, size):
    fh.seek(lba * SECTOR)
    return fh.read(size)


def find_file(iso_path: Path, path_parts):
    """Walk the directory tree; return (record_abs_offset, lba, size)
    for the file at path_parts (e.g. ['DATA', 'KC2FIRE.000'])."""
    with open(iso_path, "rb") as fh:
        fh.seek(16 * SECTOR)
        pvd = fh.read(SECTOR)
        assert pvd[0] == 1 and pvd[1:6] == b"CD001", \
            "not a PVD at sector 16"
        root = pvd[156:156 + 34]
        cur_lba = both_u32(root, 2)
        cur_size = both_u32(root, 10)
        for depth, part in enumerate(path_parts):
            data = read_at(fh, cur_lba, cur_size)
            found = None
            for rec_off, extent, size, flags, name in parse_dir_records(data):
                nm = name.decode("ascii", errors="replace").split(";")[0]
                if nm == part:
                    found = (cur_lba * SECTOR + rec_off, extent, size)
                    break
            if found is None:
                raise ValueError(f"{part!r} not found at depth {depth}")
            rec_abs, cur_lba, cur_size = found
    return rec_abs, cur_lba, cur_size


def patch(iso_path: Path, new_file: Path, out_path: Path,
          target=("DATA", "KC2FIRE.000")):
    rec_abs, lba, old_size = find_file(iso_path, list(target))
    new_size = new_file.stat().st_size
    print(f"{'/'.join(target)}: LBA {lba}, old size {old_size}, "
          f"new size {new_size}")
    if new_size > old_size:
        raise ValueError(
            f"new file ({new_size}) is LARGER than the original "
            f"({old_size}) — in-place patch impossible")
    print(f"copying {iso_path} -> {out_path} ...")
    with open(iso_path, "rb") as src, open(out_path, "wb") as dst:
        shutil.copyfileobj(src, dst, CHUNK)
    start = lba * SECTOR
    with open(out_path, "r+b") as fh:
        # Write the new archive at the extent start.
        with open(new_file, "rb") as nf:
            fh.seek(start)
            shutil.copyfileobj(nf, fh, CHUNK)
        # Zero-fill the leftover bytes of the old extent.
        remaining = old_size - new_size
        fh.seek(start + new_size)
        zeros = b"\x00" * min(CHUNK, 1024 * 1024)
        while remaining > 0:
            step = min(remaining, len(zeros))
            fh.write(zeros[:step])
            remaining -= step
        # Update data_length in the directory record (both-endian u32
        # at record offsets 10..17).
        fh.seek(rec_abs + 10)
        fh.write(struct.pack("<I", new_size))
        fh.write(struct.pack(">I", new_size))
    print(f"wrote {out_path}")
    rec2, lba2, size2 = find_file(out_path, list(target))
    assert size2 == new_size and lba2 == lba
    print(f"re-parse OK: LBA {lba2}, size {size2}")


def main(argv):
    if len(argv) >= 3 and argv[1] == "--info":
        rec, lba, size = find_file(Path(argv[2]), ["DATA", "KC2FIRE.000"])
        print(f"KC2FIRE.000: record at file offset {rec} (0x{rec:x}), "
              f"LBA {lba}, size {size}")
        return 0
    if len(argv) < 4:
        print(__doc__.split("Usage:")[1].strip(), file=sys.stderr)
        return 2
    patch(Path(argv[1]), Path(argv[2]), Path(argv[3]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
