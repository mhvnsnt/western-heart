import site, sys; sys.path.append(site.getusersitepackages())
import pefile
p = sys.argv[1]; lo, hi = int(sys.argv[2], 16), int(sys.argv[3], 16)
pe = pefile.PE(p, fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXCEPTION']])
for e in pe.DIRECTORY_ENTRY_EXCEPTION:
    b, en = e.struct.BeginAddress, e.struct.EndAddress
    if lo <= b <= hi or (b <= lo < en):
        ui = getattr(e, 'unwindinfo', None)
        chained = bool(ui and getattr(ui, 'Flags', 0) & 4)
        print('0x%x-0x%x size %d chained=%s' % (b, en, en - b, chained))
