import site, sys; sys.path.append(site.getusersitepackages())
import pefile, struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_MEM, X86_REG_RIP
p = sys.argv[1]
pe = pefile.PE(p, fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']])
data = open(p, 'rb').read()
base = pe.OPTIONAL_HEADER.ImageBase
def rva2off(r):
    for s in pe.sections:
        if s.VirtualAddress <= r < s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData):
            return r - s.VirtualAddress + s.PointerToRawData
iat = {}
for d in pe.DIRECTORY_ENTRY_IMPORT:
    for imp in d.imports:
        iat[imp.address - base] = (d.dll.decode(), imp.name.decode() if imp.name else str(imp.ordinal))
md = Cs(CS_ARCH_X86, CS_MODE_64); md.detail = True
b, e = int(sys.argv[2], 16), int(sys.argv[3], 16)
code = data[rva2off(b): rva2off(e)]
seen = set()
for ins in md.disasm(code, b):
    for op in ins.operands:
        if op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP:
            tgt = ins.address + ins.size + op.mem.disp
            if tgt in seen: continue
            seen.add(tgt)
            raw = data[rva2off(tgt): rva2off(tgt) + 16]
            fl = struct.unpack('<4f', raw); u = struct.unpack('<4I', raw)
            name = iat.get(tgt)
            print('%x: %-8s %-40s -> 0x%x %s floats %s u32 %s' % (ins.address, ins.mnemonic, ins.op_str, tgt, name or '', [round(x, 6) for x in fl], ['%08x' % x for x in u]))
# what are the call targets 0x25bcc78 / 0x25bcc7e?
for t in (0x25bcc78, 0x25bcc7e, 0x25bade0):
    c = data[rva2off(t): rva2off(t) + 16]
    for ins in md.disasm(c, t):
        s = '%x: %s %s' % (ins.address, ins.mnemonic, ins.op_str)
        for op in ins.operands:
            if op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP:
                tg = ins.address + ins.size + op.mem.disp
                s += '  -> 0x%x %s' % (tg, iat.get(tg))
        print('   ', s)
        break
