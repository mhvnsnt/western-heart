#!/usr/bin/env python3
# Standalone ELF matrix hunter — no Ghidra needed.
# Parses big-endian MIPS ELF, scans PT_LOAD segments for 4x4/3x4 float affine
# matrices (skeleton bind poses), reports VIRTUAL addresses for Ghidra xref.
import struct, math, sys

def u16(b): return struct.unpack( '<H', b)[0]
def u32(b): return struct.unpack( '<I', b)[0]

def is_affine16(f):
    # row-major: last row ~= (0,0,0,1)
    row_major = (abs(f[12]) <= 0.01 and abs(f[13]) <= 0.01 and abs(f[14]) <= 0.01
                 and abs(f[15] - 1.0) <= 0.01)
    # column-major (OpenGL style): last column ~= (0,0,0,1)
    col_major = (abs(f[3]) <= 0.01 and abs(f[7]) <= 0.01 and abs(f[11]) <= 0.01
                 and abs(f[15] - 1.0) <= 0.01)
    if not (row_major or col_major): return False
    for v in f:
        if math.isnan(v) or math.isinf(v) or abs(v) > 1e7: return False
    # 3x3 part depends on layout
    if row_major:
        rows = [(f[0],f[1],f[2]), (f[4],f[5],f[6]), (f[8],f[9],f[10])]
    else:
        rows = [(f[0],f[4],f[8]), (f[1],f[5],f[9]), (f[2],f[6],f[10])]
    norms = [math.sqrt(a*a+b*b+c*c) for (a,b,c) in rows]
    if max(norms) < 0.05: return False
    if max(norms) > 1e4: return False
    nz = [n for n in norms if n > 0.05]
    if nz and max(nz)/min(nz) > 500: return False
    return True

def is_affine12(f):
    # 3x4 row-major: 3 rows of (3x3 | t)
    for v in f:
        if math.isnan(v) or math.isinf(v) or abs(v) > 1e7: return False
    norms = [math.sqrt(f[r*4]**2+f[r*4+1]**2+f[r*4+2]**2) for r in range(3)]
    if max(norms) < 0.05 or max(norms) > 1e4: return False
    return True

def main(path):
    data = open(path,'rb').read()
    assert data[:4] == b'\x7fELF', 'not ELF'
    assert data[5] == 1, 'not little-endian'
    phoff = u32(data[0x1C:0x20]); phentsize = u16(data[0x2A:0x2C]); phnum = u16(data[0x2C:0x2E])
    print(f'phoff=0x{phoff:x} phnum={phnum}')
    segs = []
    for i in range(phnum):
        o = phoff + i*phentsize
        p_type, p_offset, p_vaddr = u32(data[o:o+4]), u32(data[o+4:o+8]), u32(data[o+8:o+12])
        p_filesz = u32(data[o+16:o+20])
        if p_type == 1:  # PT_LOAD
            segs.append((p_offset, p_vaddr, p_filesz))
            print(f'LOAD seg {i}: fileoff=0x{p_offset:x} vaddr=0x{p_vaddr:08x} filesz=0x{p_filesz:x}')
    hits16 = []
    hits12 = []
    for (off, vaddr, fsz) in segs:
        seg = data[off:off+fsz]
        nwords = len(seg)//4
        floats = struct.unpack('<'+'f'*nwords, seg[:nwords*4])
        for i in range(0, nwords-15, 4):
            w = floats[i:i+16]
            if is_affine16(w):
                hits16.append((vaddr + i*4, w))
        for i in range(0, nwords-11, 4):
            w = floats[i:i+12]
            if is_affine12(w):
                hits12.append((vaddr + i*4, w))
    hits16.sort(); hits12.sort()
    print(f'\n16-float affine hits: {len(hits16)}')
    print(f'12-float affine hits: {len(hits12)}')
    # cluster: consecutive, stride 64
    clusters = []
    cur = []
    for h in hits16:
        if cur and h[0]-cur[-1][0] == 64: cur.append(h)
        else:
            if len(cur) >= 3: clusters.append(cur)
            cur = [h]
    if len(cur) >= 3: clusters.append(cur)
    print(f'clusters (>=3 consecutive 64B matrices): {len(clusters)}')
    out = open('/tmp/ghidra-out/matrix_hits.txt','w')
    out.write(f'16-float affine hits: {len(hits16)}\nclusters: {len(clusters)}\n\n')
    for c in clusters:
        out.write(f'CLUSTER @ 0x{c[0][0]:08x} count={len(c)}\n')
        m = c[0][1]
        for r in range(4):
            out.write('  %10.4f %10.4f %10.4f %10.4f\n' % tuple(m[r*4:r*4+4]))
        out.write('\n')
    out.write('\n--- lone hits (first 60) ---\n')
    in_cl = set(h[0] for c in clusters for h in c)
    n = 0
    for h in hits16:
        if h[0] in in_cl: continue
        out.write('0x%08x\n' % h[0]); n += 1
        if n >= 60: break
    out.close()
    print('wrote /tmp/ghidra-out/matrix_hits.txt')

if __name__ == '__main__':
    main(sys.argv[1])
