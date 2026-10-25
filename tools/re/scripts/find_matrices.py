# PyGhidra script: hunt skeleton bind matrices in data sections.
# Looks for 4x4 float matrices (16 consecutive floats, last row ~= [0,0,0,1])
# and 3x4 float matrices (12 consecutive floats). Writes hits to a file.
# Run: analyzeHeadless <proj> UR -process <prog> -noanalysis -postScript find_matrices.py
import struct, math, os

OUT = "/tmp/ghidra-out/matrix_hits.txt"

def get_floats(block, nwords):
    data = block.getData()
    if data is None: return None
    buf = bytearray(nwords * 4)
    try:
        got = data.getBytes(block.getStart(), buf)
    except Exception:
        return None
    if got != nwords * 4: return None
    # PS2 ELF is big-endian
    return struct.unpack('>' + 'f' * nwords, bytes(buf))

def is_affine16(f):
    # last row ~= (0,0,0,1)
    if abs(f[12]) > 0.01 or abs(f[13]) > 0.01 or abs(f[14]) > 0.01: return False
    if abs(f[15] - 1.0) > 0.01: return False
    # sanity: no NaN/Inf, magnitudes bounded
    for v in f:
        if math.isnan(v) or math.isinf(v) or abs(v) > 1e7: return False
    # 3x3 part: at least one |v| > 0.05 (not all zeros) and row norms sane
    n0 = math.sqrt(f[0]**2 + f[1]**2 + f[2]**2)
    n1 = math.sqrt(f[4]**2 + f[5]**2 + f[6]**2)
    n2 = math.sqrt(f[8]**2 + f[9]**2 + f[10]**2)
    if n0 < 0.05 and n1 < 0.05 and n2 < 0.05: return False
    if max(n0, n1, n2) > 1e4: return False
    return True

def is_affine12(f):
    # 3x4: rows of 4, no explicit last row; check bounded + non-degenerate 3x3
    for v in f:
        if math.isnan(v) or math.isinf(v) or abs(v) > 1e7: return False
    n0 = math.sqrt(f[0]**2 + f[1]**2 + f[2]**2)
    n1 = math.sqrt(f[4]**2 + f[5]**2 + f[6]**2)
    n2 = math.sqrt(f[8]**2 + f[9]**2 + f[10]**2)
    if n0 < 0.05 and n1 < 0.05 and n2 < 0.05: return False
    if max(n0, n1, n2) > 1e4: return False
    return True

mem = currentProgram.getMemory()
hits = []
blocks = [b for b in mem.getBlocks() if b.isInitialized() and not b.isExecute()]
print("Scanning %d data blocks" % len(blocks))
for b in blocks:
    size = int(b.getSize())
    nwords = size // 4
    if nwords < 16: continue
    floats = get_floats(b, nwords)
    if floats is None: continue
    base = b.getStart().getOffset()
    # 16-float windows, step 4 (word-aligned matrix starts)
    for i in range(0, nwords - 15, 4):
        w = floats[i:i+16]
        if is_affine16(w):
            # cluster check: count consecutive matrices (bone palettes come in runs)
            hits.append((base + i*4, 16, w))
    for i in range(0, nwords - 11, 4):
        w = floats[i:i+12]
        # skip ones already caught as 16 (avoid double count noise): only keep 12s not part of 16s
        if is_affine12(w):
            hits.append((base + i*4, 12, w))

# cluster consecutive 16-float hits (stride 64 bytes) -> likely bone palettes
hits16 = sorted([h for h in hits if h[1] == 16])
clusters = []
cur = []
for h in hits16:
    if cur and h[0] - cur[-1][0] == 64:
        cur.append(h)
    else:
        if len(cur) >= 3: clusters.append(cur)
        cur = [h]
if len(cur) >= 3: clusters.append(cur)

with open(OUT, 'w') as f:
    f.write("16-float affine hits: %d\n" % len(hits16))
    f.write("12-float affine hits: %d\n" % len([h for h in hits if h[1] == 12]))
    f.write("clusters (>=3 consecutive 64-byte matrices): %d\n\n" % len(clusters))
    for c in clusters:
        f.write("CLUSTER @ 0x%08x count=%d\n" % (c[0][0], len(c)))
        # dump first matrix of cluster
        m = c[0][2]
        for r in range(4):
            f.write("  %10.4f %10.4f %10.4f %10.4f\n" % tuple(m[r*4:r*4+4]))
        f.write("\n")
    f.write("\n--- lone 16-float hits (first 40) ---\n")
    clustered = set(h[0] for c in clusters for h in c)
    n = 0
    for h in hits16:
        if h[0] in clustered: continue
        f.write("0x%08x\n" % h[0])
        n += 1
        if n >= 40: break
print("wrote " + OUT)
