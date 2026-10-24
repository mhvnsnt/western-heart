import struct, sys

SECTOR = 2352
DATA_OFF = 24  # Mode2 Form1: 12 sync + 4 header + 8 subheader... actually 24 for XA; plain Mode2 = 24
# For raw 2352 Mode 2: user data at offset 24, length 2048 (Form1) — PVD check will validate

def read_sector(f, n):
    f.seek(n * SECTOR)
    return f.read(SECTOR)

def parse_dir_record(buf):
    # buf: 2048-byte directory data area
    recs = []
    off = 0
    while off < 2048:
        ln = buf[off]
        if ln == 0:
            break
        if off + ln > 2048:
            break
        rec = buf[off:off+ln]
        flags = rec[25]
        extent = struct.unpack('<I', rec[2:6])[0]
        size = struct.unpack('<I', rec[10:14])[0]
        namelen = rec[32]
        name = rec[33:33+namelen]
        recs.append((extent, size, flags, name))
        off += ln
    return recs

def clean_name(raw):
    if raw == b'\x00': return '.'
    if raw == b'\x01': return '..'
    s = raw.decode('ascii', errors='replace').rstrip()
    # strip version ;1
    if ';' in s: s = s.split(';')[0]
    return s

def main(path):
    f = open(path, 'rb')
    # Try PVD at sector 16 with 2048-byte sectors first (cooked), else raw 2352
    global SECTOR, DATA_OFF
    f.seek(16*2048); probe = f.read(7)
    if probe[1:6] == b'CD001':
        SECTOR, DATA_OFF, DSIZE = 2048, 0, 2048
    else:
        f.seek(16*2352+24); probe = f.read(7)
        assert probe[1:6] == b'CD001', f'no PVD found: {probe!r}'
        SECTOR, DATA_OFF, DSIZE = 2352, 24, 2048
    print(f'# sector={SECTOR} data_off={DATA_OFF}', file=sys.stderr)
    pvd = read_sector(f, 16)[DATA_OFF:DATA_OFF+2048]
    root_extent = struct.unpack('<I', pvd[156+2:156+6])[0]
    root_size = struct.unpack('<I', pvd[156+10:156+14])[0]
    vol_id = pvd[40:72].decode('ascii', errors='replace').strip()
    print(f'# volume: {vol_id}', file=sys.stderr)

    entries = []
    def walk(extent, size, prefix):
        nsec = (size + DSIZE - 1)//DSIZE
        data = b''
        for i in range(nsec):
            data += read_sector(f, extent+i)[DATA_OFF:DATA_OFF+DSIZE]
        for (ex, sz, flags, raw) in parse_dir_record(data[:size] if size < len(data) else data):
            nm = clean_name(raw)
            if nm in ('.', '..'): continue
            p = prefix + '/' + nm if prefix else '/' + nm
            entries.append((p, sz, 'd' if flags & 2 else 'f'))
            if flags & 2:
                walk(ex, sz, p)
    walk(root_extent, root_size, '')
    entries.sort()
    for p, sz, t in entries:
        print(f'{t} {sz:12d} {p}')
    print(f'# total entries: {len(entries)}', file=sys.stderr)

if __name__ == '__main__':
    main(sys.argv[1])
