#!/usr/bin/env python3
"""Extract Sega .farc (FArC) archives from Virtua Fighter 5.
Format: magic 'FArC'(4) + hdr_size BE u32(4) + ??? BE u32(4),
then per entry: [name\0][offset BE u32][comp_size BE u32][uncomp_size BE u32].
Data is zlib-compressed if comp_size < uncomp_size.
"""
import struct, sys, os, gzip

def extract_farc(path, outdir):
    with open(path, 'rb') as f:
        data = f.read()
    assert data[:4] == b'FArC', f"Not a FArC file: {path}"
    pos = 12  # skip magic + 2 header u32s
    entries = []
    filesize = len(data)
    while pos < filesize:
        if data[pos:pos+4] == b'\x00' * 4:
            break
        try:
            end = data.index(b'\x00', pos)
        except ValueError:
            break
        # Sanity: name should be reasonable length and printable
        if end - pos > 256 or end - pos == 0:
            break
        try:
            name = data[pos:end].decode('ascii')
        except:
            break
        if not all(32 <= ord(c) < 127 or c in '/_.' for c in name):
            break
        pos = end + 1
        if pos + 12 > filesize:
            break
        offset, comp_size, uncomp_size = struct.unpack('>III', data[pos:pos+12])
        pos += 12
        if offset + comp_size > filesize:
            print(f"  WARNING: {name} out of bounds, stopping")
            break
        entries.append((name, offset, comp_size, uncomp_size))

    os.makedirs(outdir, exist_ok=True)
    for name, offset, comp_size, uncomp_size in entries:
        raw = data[offset:offset+comp_size]
        if comp_size < uncomp_size:
            try:
                raw = gzip.decompress(raw)
            except Exception as e:
                print(f"  {name}: decompress failed ({e}), saving raw")
        outpath = os.path.join(outdir, os.path.basename(name))
        with open(outpath, 'wb') as out:
            out.write(raw)
        print(f"  {name} ({len(raw)} bytes)")
    return entries

if __name__ == '__main__':
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + '_extracted'
    entries = extract_farc(src, dst)
    print(f"Extracted {len(entries)} files from {src}")
