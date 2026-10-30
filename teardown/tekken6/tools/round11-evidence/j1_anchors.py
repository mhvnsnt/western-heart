#!/usr/bin/env python3
"""Round 11 Job 1 anchors: (a) locate GE bone-matrix identity template(s)
in the EBOOT image; (b) find code xrefs (lui/addiu pairs) to them;
(c) dump the model-class vtable 0x08b918b8; (d) scan for code words
building 0x2B000000 immediates (lui 0x2B00 patterns)."""
import struct

ELF = '/home/hatch/workspace/_t6r4-work/ghidra-r9/EBOOT.DECRYPTED.ELF'
data = open(ELF, 'rb').read()
BASE = 0x08803000
def v2o(v): return v - BASE
def o2v(o): return o + BASE

# GE imm24 float 1.0: float32 1.0 = 0x3F800000; GE arg encoding: word = cmd<<24 | (f32>>8)
# identity matrix 3x4 rows: [1,0,0,0][0,1,0,0][0,0,1,0] -> 0x2B words:
one = 0x3F800000 >> 8  # 0x3F8000
zero = 0
tmpl_row_id = [0x2B000000 | one, 0x2B000000, 0x2B000000, 0x2B000000]
tmpl = b''.join(struct.pack('<I', w) for w in tmpl_row_id)
print('template row bytes:', tmpl.hex())
hits = []
i = data.find(tmpl)
while i != -1:
    hits.append(i); i = data.find(tmpl, i + 1)
print('identity-row hits (file off / vaddr):', [(hex(h), hex(o2v(h))) for h in hits])

# search full 12-word identity fragment + END
full = []
for r in range(3):
    for c in range(4):
        full.append(0x2B000000 | (one if r == c else 0))
full.append(0x0B000000)
fullb = b''.join(struct.pack('<I', w) for w in full)
hits2 = []
i = data.find(fullb)
while i != -1:
    hits2.append(i); i = data.find(fullb, i + 1)
print('full identity fragment hits:', [(hex(h), hex(o2v(h))) for h in hits2])

# BONE cmd sequence without END (12 x 0x2B with identity lows)
full2 = fullb[:-4]
hits3 = []
i = data.find(full2)
while i != -1:
    hits3.append(i); i = data.find(full2, i + 1)
print('12-word identity matrix hits:', [(hex(h), hex(o2v(h))) for h in hits3])

# vtable dump
vt = 0x08b918b8
print(f'--- vtable at {vt:#x} (file off {v2o(vt):#x}) ---')
for k in range(40):
    w = struct.unpack_from('<I', data, v2o(vt) + 4 * k)[0]
    print(f'  [{k}] {w:#010x}')
    if w == 0 and k > 4: break

# lui/addiu xref scan for a target vaddr: lui rt, hi ; addiu rt, rt, lo (signed)
def xrefs(target):
    hi = (target + 0x8000) >> 16
    lo = target - (hi << 16)
    out = []
    n = len(data) // 4
    words = struct.unpack(f'<{n}I', data[:n * 4])
    for j, w in enumerate(words):
        if (w >> 26) == 0x0F and (w & 0xFFFF) == hi:  # lui
            rt = (w >> 16) & 0x1F
            # look ahead up to 8 insns for addiu with same rt, imm == lo (signed 16)
            for m in range(j + 1, min(j + 9, n)):
                w2 = words[m]
                if (w2 >> 26) == 0x09 and ((w2 >> 21) & 0x1F) == rt and ((w2 >> 16) & 0x1F) == rt:
                    imm = w2 & 0xFFFF
                    if imm == (lo & 0xFFFF):
                        out.append(o2v(j * 4))
                    break
    return out

for h in hits3 + hits2:
    t = o2v(h)
    print(f'xrefs to template {t:#x}:', [hex(x) for x in xrefs(t)][:20])
# also xrefs to vtable (ctor stores it)
print('xrefs to vtable 0x08b918b8:', [hex(x) for x in xrefs(0x08b918b8)][:20])
print('xrefs to ctor FUN_0886fe88 target check skipped (jal scan):')
n = len(data) // 4
words = struct.unpack(f'<{n}I', data[:n * 4])
jal_t = 0x0886fe88
callers = [hex(o2v(j * 4)) for j, w in enumerate(words) if (w >> 26) == 0x03 and ((w & 0x3FFFFFF) << 2) | 0x8000000 == jal_t]
print('jal callers of 0886fe88:', callers[:20])
