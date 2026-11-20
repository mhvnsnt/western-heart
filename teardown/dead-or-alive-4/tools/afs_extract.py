#!/usr/bin/env python3
"""
Extract CRI Middleware AFS archives.
Standard AFS format (documented, used across Dreamcast/PS2/Xbox era games).

AFS layout:
  0x00: "AFS\0" magic (4 bytes)
  0x04: file count (u32 LE)
  0x08: file entries, 8 bytes each: (u32 offset, u32 size)
  After entries: (u32 attr_info_offset, u32 attr_info_size)
  At attr_info_offset: filename directory entries

Usage: python3 afs_extract.py <archive.afs> <output_dir>
"""
import struct
import sys
import os


def extract_afs(afs_path, out_dir):
    with open(afs_path, 'rb') as f:
        magic = f.read(4)
        if magic != b'AFS\x00':
            print(f"ERROR: Not a standard AFS file (magic={magic.hex()})")
            return 0

        count = struct.unpack('<I', f.read(4))[0]
        print(f"AFS: {count} files")

        # Read file entries
        entries = []
        for i in range(count):
            offset, size = struct.unpack('<II', f.read(8))
            entries.append((offset, size))

        # Read attribute info location
        attr_offset, attr_size = struct.unpack('<II', f.read(8))

        # Read filenames if present
        names = [f"file_{i:04d}.bin" for i in range(count)]
        if attr_offset and attr_size:
            f.seek(attr_offset)
            # Attribute entries: each is variable, but filenames are at known location
            # Standard: filename table follows the attribute entries
            # Each filename entry: u32 offset within name block, then names are null-terminated
            # Simplified: read the name block
            try:
                # The filename info is at attr_offset, format varies
                # Try to parse: first u32 is number of names, then offsets
                f.seek(attr_offset)
                # Actually for standard AFS, names are stored as:
                # at attr_offset: array of (u32 name_offset, u32 unknown) per file
                # then null-terminated strings
                name_offsets = []
                for i in range(count):
                    name_off, _ = struct.unpack('<II', f.read(8))
                    name_offsets.append(name_off)

                # Names are relative to start of name data area
                # The name data starts after the offset table
                name_data_start = f.tell()
                for i, name_off in enumerate(name_offsets):
                    if name_off == 0:
                        continue
                    f.seek(name_data_start + name_off)
                    name_bytes = b''
                    while True:
                        b = f.read(1)
                        if b == b'\x00' or not b:
                            break
                        name_bytes += b
                    if name_bytes:
                        try:
                            decoded = name_bytes.decode('ascii', errors='strict')
                            if decoded and all(32 <= ord(c) < 127 for c in decoded):
                                # Sanitize for filesystem
                                safe = "".join(c if c not in '<>:"/\\|?*' else '_' for c in decoded)
                                names[i] = safe
                        except:
                            pass
            except Exception as e:
                print(f"  (filename table parse: {e}, using generic names)")

        os.makedirs(out_dir, exist_ok=True)

        extracted = 0
        for i, (offset, size) in enumerate(entries):
            if offset == 0 and size == 0:
                continue
            f.seek(offset)
            data = f.read(size)
            out_path = os.path.join(out_dir, names[i])
            # Handle duplicate names
            base, ext = os.path.splitext(out_path)
            n = 1
            while os.path.exists(out_path):
                out_path = f"{base}_{n}{ext}"
                n += 1
            with open(out_path, 'wb') as out:
                out.write(data)
            extracted += 1

        print(f"Extracted {extracted}/{count} files to {out_dir}/")
        return extracted


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <archive.afs> <output_dir>")
        sys.exit(1)
    extract_afs(sys.argv[1], sys.argv[2])
