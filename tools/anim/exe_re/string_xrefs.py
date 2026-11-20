import site, sys; sys.path.append(site.getusersitepackages())
import pefile, re, struct
p = sys.argv[1]
pe = pefile.PE(p, fast_load=True)
base = pe.OPTIONAL_HEADER.ImageBase
data = open(p, 'rb').read()
def off2rva(o):
    for s in pe.sections:
        if s.PointerToRawData <= o < s.PointerToRawData + s.SizeOfRawData:
            return o - s.PointerToRawData + s.VirtualAddress
text = next(s for s in pe.sections if s.Name.startswith(b'.text'))
T = data[text.PointerToRawData: text.PointerToRawData + text.SizeOfRawData]
trva = text.VirtualAddress
targets = {}
for pat in sys.argv[2:]:
    for enc in ('ascii', 'utf-16-le'):
        b = pat.encode(enc)
        for m in re.finditer(re.escape(b), data):
            # walk back to the string start (previous NUL)
            o = m.start()
            st = o
            step = 2 if enc != 'ascii' else 1
            while st - step >= 0 and data[st - step: st] != b'\0' * step:
                st -= step
            r = off2rva(st)
            s_ = data[st: st + 80]
            s_ = s_.decode('utf-16-le' if enc != 'ascii' else 'ascii', errors='replace').split('\0')[0]
            targets[r] = (pat, enc, s_)
for r, v in sorted(targets.items()):
    print('string rva 0x%x %s %r' % (r, v[1], v[2]))
# RIP-relative references: any 32-bit displacement d at text offset i with next_ip = trva+i+4 (+ imm bytes) == target
# scan all positions (disp at i, next ip = rva(i)+4 for lea/mov without immediates)
import numpy as np
arr = np.frombuffer(T, dtype=np.uint8)
d = arr[:-3].astype(np.int64) | (arr[1:-2].astype(np.int64) << 8) | (arr[2:-1].astype(np.int64) << 16) | (arr[3:].astype(np.int64) << 24)
d = np.where(d >= 2**31, d - 2**32, d)
nxt = trva + np.arange(len(d)) + 4
tgt = nxt + d
for r in sorted(targets):
    idx = np.nonzero(tgt == r)[0]
    print('xrefs to 0x%x (%r): %d' % (r, targets[r][2], len(idx)), ['0x%x' % (trva + i - 3) for i in idx[:10]])
