"""List every SUB (subroutine) NAME in file order per bhb_ai file, with its
PROG/AAS2/CODE sizes. SUBs are top-level: DEFAULT_* hooks + named functions
(GetTrickID, CheckCritical, SetWarpPos, ...). The order defines the
function index the CODE bytecode calls."""
import struct, sys, os
CONTAINERS = {b"SUB ", b"STAT", b"STRT", b"AAS2", b"RUN ", b"STOP", b"DATA"}
LEAVES = {b"UPDT", b"NAME", b"ATR ", b"INFO", b"CODE", b"STR ", b"CTBL", b"FTBL", b"IFDT"}
def walk(buf, off, end, depth, out, cur_sub):
    while off + 8 <= end:
        tag = bytes(buf[off:off + 4])
        size = struct.unpack_from("<I", buf, off + 4)[0]
        if tag == b"SUB ":
            pay_end = min(off + 8 + size - 1, end)
            # NAME is the first child
            nm = bytes(buf[off + 16:off + 16 + 32]).split(b"\x00")[0].decode("latin1") if bytes(buf[off+8:off+12]) == b"NAME" else "?"
            out.append((off, depth, nm, size))
            walk(buf, off + 8, pay_end, depth + 1, out, nm)
            off = pay_end
        elif tag in CONTAINERS:
            pay_end = min(off + 8 + size - 1, end)
            walk(buf, off + 8, pay_end, depth + 1, out, cur_sub)
            off = pay_end
        elif tag == b"PROG":
            pay_end = min(off + 8 + size, end)
            pay = bytes(buf[off + 8:pay_end])
            if pay[:4] == b"AAS2" and len(pay) > 8:
                walk(buf, off + 8, pay_end, depth + 1, out, cur_sub)
            off = pay_end
        elif tag == b"DATA":
            pay_end_c = min(off + 8 + size - 1, end)
            # outer DATA has NAME/PROG children; inner is a raw table
            if bytes(buf[off + 8:off + 12]) in (b"NAME", b"PROG"):
                walk(buf, off + 8, pay_end_c, depth + 1, out, cur_sub)
                off = pay_end_c
            else:
                off = min(off + 8 + size, end)
        elif tag in LEAVES:
            off = min(off + 8 + size, end)
        else:
            break
for fn in sys.argv[1:]:
    buf = open(fn, "rb").read()
    out = []
    walk(buf, 8, len(buf), 0, out, None)
    print(f"===== {os.path.basename(fn)}: {len(out)} SUBs =====")
    for i, (off, depth, nm, size) in enumerate(out):
        print(f"  [{i:2d}] @{off:6d} depth={depth} size={size:4d} {nm}")
