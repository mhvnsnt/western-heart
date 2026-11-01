import site, sys; sys.path.append(site.getusersitepackages())
import pefile, struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
p = sys.argv[1]
pe = pefile.PE(p, fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXCEPTION']])
data = open(p, 'rb').read()
text = next(s for s in pe.sections if s.Name.startswith(b'.text'))
def rva2off(r): return r - text.VirtualAddress + text.PointerToRawData
funcs = sorted({(e.struct.BeginAddress, e.struct.EndAddress) for e in pe.DIRECTORY_ENTRY_EXCEPTION})
print('functions', len(funcs))
md = Cs(CS_ARCH_X86, CS_MODE_64); md.detail = False
hits = []
for b, e in funcs:
    if e - b > 20000 or not (text.VirtualAddress <= b < text.VirtualAddress + text.Misc_VirtualSize): continue
    code = data[rva2off(b): rva2off(e)]
    if b'\x64' not in code or b'\xc8' not in code: continue
    has64 = has_c8 = False
    n64 = []
    for ins in md.disasm(code, b):
        if ins.mnemonic == 'cmp':
            op = ins.op_str.split(', ')[-1]
            if op in ('0x64',): has64 = True; n64.append(ins.address)
            elif op in ('0xc8',): has_c8 = True
    if has64 and has_c8:
        hits.append((b, e, n64[:3]))
print('functions comparing against both 0x64 and 0xc8:', len(hits))
for b, e, a in hits[:60]:
    print('  0x%x-0x%x (%d bytes) cmp 0x64 at %s' % (b, e, e - b, ['0x%x' % x for x in a]))
