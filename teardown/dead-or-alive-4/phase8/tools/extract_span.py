import struct, os, sys
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
d = open(src, 'rb').read()
assert d[:4] == b'PK\x07\x08', d[:4]  # spanning signature
off = 4; ok = fail = 0
while d[off:off+4] == b'PK\x03\x04':
    (sig, ver, flags, method, mt, md, crc, csize, usize, nlen, elen) = struct.unpack_from('<IHHHHHIIIHH', d, off)
    name = d[off+30:off+30+nlen].decode()
    data_off = off + 30 + nlen + elen
    if flags & 0x08:  # data descriptor follows data; csize may be 0 in header -> use central dir sizes
        pass
    raw = d[data_off:data_off+csize]
    if len(raw) != csize or method != 0:
        print('FAIL', name, 'method', method, 'got', len(raw), 'want', csize); fail += 1
    else:
        open(os.path.join(dst, name), 'wb').write(raw); print('OK', name, csize); ok += 1
    off = data_off + csize + (12 if flags & 0x08 else 0)
print('DONE ok', ok, 'fail', fail, 'end off', off, 'filesize', len(d))
