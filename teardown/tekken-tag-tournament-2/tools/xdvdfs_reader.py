#!/usr/bin/env python3
"""
XDVDFS (Xbox 360 GDF) filesystem reader over a sector-read callback.

Format reference: xdvdfs (antangelo, MIT) — layout verified from
xdvdfs-core/src/{layout,read}/*.rs.

On-disk structures (all little-endian):
- Volume descriptor at byte 32*0x800 (sector 32):
    0x00: "MICROSOFT*XBOX*MEDIA" (20 bytes), repeated at 0x7ec
    0x14: root directory table sector (u32)
    0x18: root directory table size in bytes (u32)
- Directory entry node (14 bytes at table-relative byte offset):
    0x0: left_entry_offset  (u16) -> child at byte 4*value (0/0xffff = none)
    0x2: right_entry_offset (u16) -> child at byte 4*value
    0x4: data sector (u32)        -> file data or subdir table
    0x8: data size in bytes (u32)
    0xC: attributes (u8)          -> bit 4 (0x10) = directory
    0xD: filename_length (u8)
    0xE: filename bytes (windows-1252, filename_length bytes)
- Empty nodes are all-0x00 or all-0xFF.

Usage:
    reader = XdvdfsReader(read_sector_fn)  # fn(sector:int)->bytes (0x800)
    for path, is_dir, sector, size in reader.walk():
        ...
    data = reader.read_file(sector, size)  # bytes
"""
from __future__ import annotations
import struct

SECTOR_SIZE = 0x800
VOLUME_SECTOR = 32
MAGIC = b"MICROSOFT*XBOX*MEDIA"
ATTR_DIRECTORY = 0x10


class XdvdfsError(Exception):
    pass


class XdvdfsReader:
    def __init__(self, read_sector):
        """read_sector(sector:int) -> bytes of length SECTOR_SIZE."""
        self._rs = read_sector
        self._cache = {}
        self.root_sector, self.root_size = self._read_volume()

    # ---- low level ----
    def _sector(self, n):
        if n not in self._cache:
            data = self._rs(n)
            if len(data) < SECTOR_SIZE:
                data = data.ljust(SECTOR_SIZE, b"\x00")
            self._cache[n] = data
        return self._cache[n]

    def _read_at(self, byte_off, length):
        """Read `length` bytes starting at absolute image byte offset."""
        out = bytearray()
        while length > 0:
            sector = byte_off // SECTOR_SIZE
            inner = byte_off % SECTOR_SIZE
            chunk = self._sector(sector)[inner:inner + length]
            if not chunk:
                raise XdvdfsError(f"short read at sector {sector}")
            out += chunk
            byte_off += len(chunk)
            length -= len(chunk)
        return bytes(out)

    # ---- volume ----
    def _read_volume(self):
        sec = self._sector(VOLUME_SECTOR)
        if sec[0:20] != MAGIC or sec[0x7EC:0x800] != MAGIC:
            raise XdvdfsError("bad XDVDFS magic at sector 32")
        root_sector, root_size = struct.unpack_from("<II", sec, 0x14)
        if root_size == 0:
            raise XdvdfsError("empty root table")
        return root_sector, root_size

    # ---- directory walk ----
    def _read_node(self, table_byte_base, node_off):
        """Return (left,right,sector,size,attrs,name) or None if empty."""
        abs_off = table_byte_base + node_off
        raw = self._read_at(abs_off, 14)
        if raw == b"\x00" * 14 or raw == b"\xff" * 14:
            return None
        left, right, sector, size, attrs, nlen = struct.unpack("<HHIIBB", raw)
        name = self._read_at(abs_off + 14, nlen)
        try:
            name = name.decode("windows-1252")
        except Exception:
            name = name.decode("windows-1252", errors="replace")
        return (left, right, sector, size, attrs, name)

    def _walk_table(self, table_sector, table_size, parent_path):
        base = table_sector * SECTOR_SIZE
        # iterative DFS over the binary tree; root node at table offset 0
        stack = [0]
        seen = set()
        while stack:
            off = stack.pop()
            if off in seen or off >= table_size:
                continue
            seen.add(off)
            node = self._read_node(base, off)
            if node is None:
                continue
            left, right, sector, size, attrs, name = node
            for child in (right, left):  # push right first so left pops first
                if child not in (0, 0xFFFF):
                    stack.append(4 * child)
            is_dir = bool(attrs & ATTR_DIRECTORY)
            path = f"{parent_path}/{name}" if parent_path else name
            yield (path, is_dir, sector, size)
            if is_dir and size:
                yield from self._walk_table(sector, size, path)

    def walk(self):
        """Yield (path, is_dir, sector, size) for every entry, depth-first."""
        yield from self._walk_table(self.root_sector, self.root_size, "")

    def list_files(self):
        """Return [(path, sector, size)] for regular files only."""
        return [(p, s, z) for (p, d, s, z) in self.walk() if not d]

    # ---- file data ----
    def read_file(self, sector, size):
        return self._read_at(sector * SECTOR_SIZE, size)

    def read_file_to(self, sector, size, dest_path, chunk_sectors=256):
        """Stream file data to disk (low memory)."""
        with open(dest_path, "wb") as out:
            remaining = size
            sec = sector
            while remaining > 0:
                batch = min(chunk_sectors, (remaining + SECTOR_SIZE - 1) // SECTOR_SIZE)
                for i in range(batch):
                    data = self._sector(sec + i)
                    take = min(len(data), remaining)
                    out.write(data[:take])
                    remaining -= take
                    if remaining <= 0:
                        break
                sec += batch
