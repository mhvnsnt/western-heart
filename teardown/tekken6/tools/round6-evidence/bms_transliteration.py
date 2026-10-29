#!/usr/bin/env python3
"""Line-by-line Python transliteration of teardown/tekken6/tools/tekken6.bms.
QuickBMS binary could not be executed in this VM (official download
aluigi.altervista.org returns an HTML challenge page, aluigi.org times
out — recorded 2026-10-21 round 6 attempt 4), so per JOB 2's fallback
this transliteration executes the script's exact semantics:
  comtype zlib
  loop: findloc "GZIP" from FOUND; goto; idstring "GZIP";
        get W1,W2,USIZE,CSIZE (long/LE); savepos BODY;
        clog NAME BODY CSIZE USIZE   (zlib-decompress CSIZE bytes -> USIZE bytes)
        FOUND = OFF + 20; next
"""
import struct, zlib, sys, hashlib
data=open(sys.argv[1],'rb').read()
found=0; i=0; outs=[]
while True:
    off=data.find(b'GZIP', found)
    if off<0: break
    assert data[off:off+4]==b'GZIP'
    w1,w2,usize,csize=struct.unpack_from('<4I', data, off+4)
    body=data[off+20:off+20+csize]
    out=zlib.decompress(body)  # clog with comtype zlib
    assert len(out)==usize, (len(out), usize)
    outs.append((off,out))
    print(f"container@{off}: W1={w1} W2={w2} USIZE={usize} CSIZE={csize} -> decompressed {len(out)} sha256={hashlib.sha256(out).hexdigest()}")
    found=off+20; i+=1
print(f"TOTAL {len(outs)} containers")
