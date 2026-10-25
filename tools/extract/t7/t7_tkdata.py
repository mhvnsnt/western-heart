#!/usr/bin/env python3
"""Unpack TEKKEN 7 tkdata.bin (port of the community tkdata.bms v0.2.1). usage: t7_tkdata.py tkdata.bin outdir [--list]"""
import sys, os, struct, zlib
from Crypto.Cipher import AES
KEY = b'epsNJf#ut&v3fVrndlYkp&Sq@5Ry?BHA'
def aes(b):  # quickbms 'encryption aes' == ECB decrypt over full blocks
    n = len(b)//16*16; return AES.new(KEY, AES.MODE_ECB).decrypt(b[:n]) + b[n:]
src, out = sys.argv[1], sys.argv[2]; lst = '--list' in sys.argv
f = open(src, 'rb'); d = f.read()
assert d[:16] == b'_TEKKEN7CSFILES_', d[:16]
off, size = struct.unpack_from('<qq', d, len(d)-0x68)
m = aes(d[off:off+size])
if m[:8] != b'tsLniBNB':
    try: m = zlib.decompress(m)
    except Exception: pass
assert m[:8] == b'tsLniBNB', m[:16]
num, info, name = struct.unpack_from('<qqq', m, 8)
for i in range(num):
    e = name; nm = m[name:m.index(b'\0', name)].decode('latin1'); name = m.index(b'\0', name)+1
    fid, flags, _, fo, zs, us, _, _ = struct.unpack_from('<8q', m, info); info += 64
    fo += 0x10
    if lst: print(nm, flags, zs, us); continue
    blob = aes(d[fo:fo+zs])
    if flags & 1: blob = zlib.decompress(blob)
    p = os.path.join(out, nm.lstrip('/\\').replace('\\', '/')); os.makedirs(os.path.dirname(p) or out, exist_ok=True)
    open(p, 'wb').write(blob[:us])
print('files', num)
