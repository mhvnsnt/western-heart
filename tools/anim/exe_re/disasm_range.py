import site, sys; sys.path.append(site.getusersitepackages())
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
p = sys.argv[1]
pe = pefile.PE(p, fast_load=True)
data = open(p, 'rb').read()
text = next(s for s in pe.sections if s.Name.startswith(b'.text'))
md = Cs(CS_ARCH_X86, CS_MODE_64)
for arg in sys.argv[2:]:
    b, e = (int(x, 16) for x in arg.split('-'))
    code = data[b - text.VirtualAddress + text.PointerToRawData: e - text.VirtualAddress + text.PointerToRawData]
    print('==== 0x%x' % b)
    for ins in md.disasm(code, b):
        print('  %x: %-8s %s' % (ins.address, ins.mnemonic, ins.op_str))
