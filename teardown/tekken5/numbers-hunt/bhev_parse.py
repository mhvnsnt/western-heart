import struct, sys
LEAVES = {b"UPDT", b"NAME", b"ATR ", b"INFO", b"CODE", b"STR ", b"CTBL", b"FTBL"}
CONTAINERS = {b"SUB ", b"STAT", b"STRT", b"AAS2", b"RUN ", b"STOP", b"DATA"}  # span = 8+size-1
# PROG: span = 8+size; payload is either a full AAS2 chunk tree or an 8-byte reference
def parse(buf, off, end, depth, out):
    while off + 8 <= end:
        tag = bytes(buf[off:off + 4])
        size = struct.unpack_from("<I", buf, off + 4)[0]
        if tag in LEAVES:
            pay_end = min(off + 8 + size, end)
            pay = bytes(buf[off + 8:pay_end])
            extra = ""
            if tag == b"FTBL":
                vals = struct.unpack("<%dI" % (len(pay)//4), pay) if len(pay) % 4 == 0 else ()
                fl = struct.unpack("<%df" % (len(pay)//4), pay) if len(pay) % 4 == 0 else ()
                extra = f" u32={vals} f32={fl}"
            if tag == b"DATA":
                vals = struct.unpack("<%dI" % (len(pay)//4), pay) if len(pay) % 4 == 0 else ()
                extra = f" u32[{len(vals)}]={vals[:24]}"
            out.append("  " * depth + f"@{off} {tag.decode('latin1')} size={size}{extra} {pay[:40]!r}")
            off = pay_end
        elif tag in CONTAINERS:
            pay_end = min(off + 8 + size - 1, end)
            out.append("  " * depth + f"@{off} {tag.decode('latin1')} size={size} (span to {pay_end})")
            parse(buf, off + 8, pay_end, depth + 1, out)
            off = pay_end
        elif tag == b"PROG":
            pay_end = min(off + 8 + size, end)
            pay = bytes(buf[off + 8:pay_end])
            if pay[:4] == b"AAS2" and len(pay) > 8:
                out.append("  " * depth + f"@{off} PROG size={size} (span to {pay_end})")
                parse(buf, off + 8, pay_end, depth + 1, out)
            else:
                out.append("  " * depth + f"@{off} PROG size={size} ref={pay!r}")
            off = pay_end
        else:
            out.append("  " * depth + f"@{off} UNKNOWN tag={tag!r} size={size} -- STOP")
            break
    if off != end:
        out.append("  " * depth + f"trailing {end - off} bytes at {off}: {bytes(buf[off:end])[:32].hex()}")
for fn in sys.argv[1:]:
    buf = open(fn, "rb").read()
    print(f"== {fn} len={len(buf)} BHEV-u32={struct.unpack_from('<I', buf, 4)[0]} ==")
    out = []
    parse(buf, 8, len(buf), 0, out)
    print("\n".join(out))
