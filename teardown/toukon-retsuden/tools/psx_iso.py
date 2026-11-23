#!/usr/bin/env python3
"""psx_iso.py — pure-Python PS1 BIN/CUE reader: list + extract ISO9660 files.

PS1 discs are raw 2352-byte sectors. Data tracks are Mode 2 Form 1: the
2048-byte user payload sits at offset 24 inside each sector. This module
converts raw sectors to cooked data and walks the ISO9660 filesystem.

Usage:
  python3 psx_iso.py list <game.bin> [game.cue]
  python3 psx_iso.py extract <game.bin> <outdir> [game.cue]
  python3 psx_iso.py extract-file <game.bin> <ISO-PATH> <outfile> [game.cue]
"""
import os
import re
import struct
import sys

RAW_SECTOR = 2352
COOKED = 2048


def parse_cue(cue_path):
    """Return list of (track_no, track_type, file, start_lba) from a .cue."""
    tracks = []
    cur_file = None
    cur_track = None
    cur_type = None
    with open(cue_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            m = re.match(r'FILE\s+"(.+?)"\s+(\S+)', line)
            if m:
                cur_file = m.group(1)
                continue
            m = re.match(r'TRACK\s+(\d+)\s+(\S+)', line)
            if m:
                cur_track = int(m.group(1))
                cur_type = m.group(2)
                continue
            m = re.match(r'INDEX\s+01\s+(\d+):(\d+):(\d+)', line)
            if m and cur_track is not None:
                mm, ss, ff = int(m.group(1)), int(m.group(2)), int(m.group(3))
                lba = (mm * 60 + ss) * 75 + ff
                tracks.append((cur_track, cur_type, cur_file, lba))
    return tracks


class PsxDisc:
    def __init__(self, bin_path, cue_path=None):
        self.bin_path = bin_path
        self.f = open(bin_path, "rb")
        self.size = os.fstat(self.f.fileno()).st_size
        # Detect sector size: raw 2352 (BIN) vs cooked 2048 (ISO).
        if self.size % RAW_SECTOR == 0 and self.size % COOKED != 0:
            self.sector = RAW_SECTOR
        elif self.size % COOKED == 0:
            # Could be either; check the PVD magic at sector 16.
            self.f.seek(16 * RAW_SECTOR + 24 + 1)
            if self.f.read(5) == b"CD001":
                self.sector = RAW_SECTOR
            else:
                self.sector = COOKED
        else:
            self.sector = RAW_SECTOR
        self.data_lba0 = 0  # LBA offset of the data track within the file
        if cue_path and os.path.exists(cue_path):
            for track_no, ttype, tfile, lba in parse_cue(cue_path):
                if "MODE2" in ttype or "MODE1" in ttype:
                    self.data_lba0 = 0  # first data track starts at file offset 0
                    break

    def read_sector(self, lba):
        """Return the 2048-byte cooked payload for logical sector `lba`."""
        if self.sector == COOKED:
            self.f.seek(lba * COOKED)
            return self.f.read(COOKED)
        self.f.seek(lba * RAW_SECTOR)
        raw = self.f.read(RAW_SECTOR)
        if len(raw) < RAW_SECTOR:
            return raw[24:24 + COOKED] if len(raw) > 24 else b""
        mode = raw[15]
        if mode == 2:
            submode = raw[18]
            form = submode & 0x20
            if form:  # Form 2: 2324 payload at offset 24 (video/audio, no EDC)
                return raw[24:24 + 2324]
            return raw[24:24 + COOKED]
        # Mode 1 (or Mode 0): payload at offset 16
        return raw[16:16 + COOKED]

    def read_extent(self, lba, size):
        out = bytearray()
        n = (size + COOKED - 1) // COOKED
        for i in range(n):
            out += self.read_sector(lba + i)
        return bytes(out[:size])

    # ---- ISO9660 ----
    def _parse_dir_record(self, buf, off):
        ln = buf[off]
        if ln == 0:
            return None, off + 1
        extent = struct.unpack_from("<I", buf, off + 2)[0]
        size = struct.unpack_from("<I", buf, off + 10)[0]
        flags = buf[off + 25]
        nlen = buf[off + 32]
        name_raw = buf[off + 33:off + 33 + nlen]
        if name_raw == b"\x00":
            name = "."
        elif name_raw == b"\x01":
            name = ".."
        else:
            name = name_raw.decode("ascii", "replace")
            name = name.split(";")[0]
        return (name, extent, size, bool(flags & 2)), off + ln

    def list_files(self):
        """Walk the ISO9660 tree; return [(path, lba, size)]."""
        pvd = self.read_sector(16)
        assert pvd[1:6] == b"CD001", "no ISO9660 PVD at sector 16"
        root_rec = pvd[156:156 + 34]
        root_extent = struct.unpack_from("<I", root_rec, 2)[0]
        root_size = struct.unpack_from("<I", root_rec, 10)[0]
        out = []
        stack = [("", root_extent, root_size)]
        while stack:
            prefix, extent, size = stack.pop()
            data = self.read_extent(extent, size)
            off = 0
            while off < len(data):
                rec, off = self._parse_dir_record(data, off)
                if rec is None:
                    # padding to next sector boundary
                    nxt = ((off // COOKED) + 1) * COOKED
                    off = nxt if nxt > off else off + 1
                    continue
                name, ext, sz, is_dir = rec
                if name in (".", ".."):
                    continue
                path = f"{prefix}/{name}" if prefix else name
                if is_dir:
                    stack.append((path, ext, sz))
                else:
                    out.append((path, ext, sz))
        return sorted(out)

    def extract_all(self, outdir):
        os.makedirs(outdir, exist_ok=True)
        for path, lba, size in self.list_files():
            dest = os.path.join(outdir, path)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(self.read_extent(lba, size))
        return len(self.list_files())

    def extract_file(self, iso_path, dest):
        for path, lba, size in self.list_files():
            if path.upper() == iso_path.upper():
                with open(dest, "wb") as f:
                    f.write(self.read_extent(lba, size))
                return size
        raise FileNotFoundError(iso_path)

    def close(self):
        self.f.close()


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    cmd = sys.argv[1]
    bin_path = sys.argv[2]
    cue = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3].endswith(".cue") else None
    disc = PsxDisc(bin_path, cue)
    if cmd == "list":
        for path, lba, size in disc.list_files():
            print(f"{size:>10}  LBA {lba:<7} {path}")
    elif cmd == "extract":
        outdir = sys.argv[3] if not cue else sys.argv[4]
        n = disc.extract_all(outdir)
        print(f"extracted {n} files to {outdir}")
    elif cmd == "extract-file":
        iso_path, dest = sys.argv[3], sys.argv[4]
        n = disc.extract_file(iso_path, dest)
        print(f"wrote {n} bytes to {dest}")
    disc.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
