"""Round 7: directory structure of the decoded T6 PSP containers.
Type A (count=13, hdr=112): NDPP-bearing. Type B (count=6, hdr=64): NTPP-bearing.
Directory = header (count, hdrsize) + count x (chunk_size, cumulative_end) pairs
tiling the file contiguously from hdrsize to EOF (verified idx00/idx04 below).
Run against ~/workspace/_t6r4-work/decoded76/ (retained workdir, clean bytes)."""
import struct, glob, os
D='/home/hatch/workspace/_t6r4-work/decoded76/'
for name in ['idx00_entry454.bin','idx04_entry465.bin']:
    d=open(D+name,'rb').read()
    cnt,hdr=struct.unpack_from('<II',d,0)
    print(name, 'count',cnt,'hdr',hdr,'len',len(d))
    pos=hdr
    for i in range(cnt):
        size,end=struct.unpack_from('<II',d,8+i*8)
        magic=d[pos:pos+4] if size else b''
        print(f'  slot{i}: size={size} end={end} actual_pos={pos} magic={magic} ok={end==pos+size}')
        pos+=size
    print('  final pos', pos, '== EOF', pos==len(d))
