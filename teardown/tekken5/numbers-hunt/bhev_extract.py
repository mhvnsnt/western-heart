"""BHEV extractor: full chunk tree + all inner DATA tables (u32/float) +
all strings, for every bhb_ai_*.dat. DATA chunks are dual-form: outer
(NAME+PROG>AAS2) or inner raw numeric table."""
import struct, sys, os

LEAVES = {b"UPDT", b"NAME", b"ATR ", b"INFO", b"CODE", b"STR ", b"CTBL", b"FTBL", b"IFDT"}
CONTAINERS = {b"SUB ", b"STAT", b"STRT", b"AAS2", b"RUN ", b"STOP"}

def try_children(buf, off, end):
    """Try parsing [off:end] as chunk tree; return (ok, items)."""
    items = []
    o = off
    while o + 8 <= end:
        tag = bytes(buf[o:o + 4])
        size = struct.unpack_from("<I", buf, o + 4)[0]
        if tag in LEAVES or tag in CONTAINERS or tag == b"PROG" or tag == b"DATA":
            items.append((o, tag, size))
            if tag in LEAVES or tag == b"IFDT":
                o += 8 + size
            elif tag in CONTAINERS:
                o += 8 + size - 1
            elif tag == b"PROG":
                o += 8 + size
            else:  # DATA: try both spans
                o += 8 + size - 1
            if o > end:
                return False, []
        else:
            return False, []
    return (o == end), items

def parse(buf, off, end, depth, out, tables, path):
    while off + 8 <= end:
        tag = bytes(buf[off:off + 4])
        size = struct.unpack_from("<I", buf, off + 4)[0]
        if tag in LEAVES:
            pay_end = min(off + 8 + size, end)
            pay = bytes(buf[off + 8:pay_end])
            extra = ""
            if tag == b"FTBL" and len(pay) % 4 == 0:
                fl = struct.unpack("<%df" % (len(pay)//4), pay)
                extra = f" f32={fl}"
            if tag == b"IFDT" and len(pay) % 4 == 0:
                extra = f" u32={struct.unpack('<%dI' % (len(pay)//4), pay)}"
            out.append("  " * depth + f"@{off} {tag.decode('latin1')} size={size}{extra} {pay[:40]!r}")
            off = pay_end
        elif tag in CONTAINERS:
            pay_end = min(off + 8 + size - 1, end)
            out.append("  " * depth + f"@{off} {tag.decode('latin1')} size={size}")
            parse(buf, off + 8, pay_end, depth + 1, out, tables, path)
            off = pay_end
        elif tag == b"PROG":
            pay_end = min(off + 8 + size, end)
            pay = bytes(buf[off + 8:pay_end])
            if pay[:4] == b"AAS2" and len(pay) > 8:
                out.append("  " * depth + f"@{off} PROG size={size}")
                parse(buf, off + 8, pay_end, depth + 1, out, tables, path)
            else:
                out.append("  " * depth + f"@{off} PROG size={size} ref={pay!r}")
            off = pay_end
        elif tag == b"DATA":
            pay_end_c = min(off + 8 + size - 1, end)
            ok, _ = try_children(buf, off + 8, pay_end_c)
            if ok and bytes(buf[off + 8:off + 12]) in (b"NAME", b"PROG"):
                pay_end = pay_end_c
                pay = bytes(buf[off + 8:pay_end])
                out.append("  " * depth + f"@{off} DATA size={size} (outer)")
                parse(buf, off + 8, pay_end, depth + 1, out, tables, path + [f"DATA@{off}"])
            else:
                # inner raw table: full size payload (span 8+size)
                pay_end = min(off + 8 + size, end)
                pay = bytes(buf[off + 8:pay_end])
                n = len(pay) // 4
                u32 = struct.unpack("<%dI" % n, pay[:n * 4]) if n else ()
                f32 = struct.unpack("<%df" % n, pay[:n * 4]) if n else ()
                nm = path[-1] if path else f"DATA@{off}"
                out.append("  " * depth + f"@{off} DATA size={size} TABLE {nm} u32={list(u32)}")
                tables.append((nm, list(u32), list(f32)))
            off = pay_end
        else:
            out.append("  " * depth + f"@{off} UNKNOWN tag={tag!r} size={size} -- STOP")
            break
    if off != end:
        out.append("  " * depth + f"trailing {end - off} bytes at {off}")

for fn in sys.argv[1:]:
    buf = open(fn, "rb").read()
    out, tables = [], []
    parse(buf, 8, len(buf), 0, out, tables, [os.path.basename(fn)])
    print(f"===== {fn} len={len(buf)} =====")
    print("\n".join(out))
    print(f"--- tables: {len(tables)} ---")
