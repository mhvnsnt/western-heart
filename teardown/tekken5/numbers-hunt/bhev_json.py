"""Extract bhb_ai_*.dat into JSON: per file -> states (STAT NAME + STRT/RUN/STOP
CODE sizes + FTBL floats), data blocks (outer DATA NAME -> inner tables),
comments (CTBL), function names are in STR chunks (none found as separate
chunks; strings live in CTBL/NAME)."""
import struct, sys, os, json

LEAVES = {b"UPDT", b"NAME", b"ATR ", b"INFO", b"CODE", b"STR ", b"CTBL", b"FTBL", b"IFDT"}
CONTAINERS = {b"SUB ", b"STAT", b"STRT", b"AAS2", b"RUN ", b"STOP"}

def try_children(buf, off, end):
    o = off
    while o + 8 <= end:
        tag = bytes(buf[o:o + 4])
        size = struct.unpack_from("<I", buf, o + 4)[0]
        if tag in LEAVES or tag in CONTAINERS or tag in (b"PROG", b"DATA"):
            if tag in LEAVES:
                o += 8 + size
            elif tag in CONTAINERS:
                o += 8 + size - 1
            elif tag == b"PROG":
                o += 8 + size
            else:
                o += 8 + size - 1
            if o > end:
                return False
        else:
            return False
    return o == end

def cstr(b):
    return b.split(b"\x00")[0].decode("latin1")

def parse(buf, off, end, ctx, acc):
    while off + 8 <= end:
        tag = bytes(buf[off:off + 4])
        size = struct.unpack_from("<I", buf, off + 4)[0]
        if tag in LEAVES:
            pay_end = min(off + 8 + size, end)
            pay = bytes(buf[off + 8:pay_end])
            if tag == b"NAME":
                ctx["name"] = cstr(pay)
                if ctx.get("in_stat"):
                    acc.setdefault("states", []).append({"name": ctx["name"], "at": off})
            elif tag == b"CODE":
                acc.setdefault("code", []).append({"at": off, "size": size,
                    "state": ctx.get("state"), "phase": ctx.get("phase"),
                    "hex": pay.hex()})
            elif tag == b"FTBL" and len(pay) % 4 == 0:
                acc.setdefault("ftbl", []).append({"at": off,
                    "f32": list(struct.unpack("<%df" % (len(pay)//4), pay)),
                    "state": ctx.get("state"), "phase": ctx.get("phase")})
            elif tag == b"CTBL":
                acc.setdefault("comments", []).append({"at": off, "text": cstr(pay)})
            elif tag == b"IFDT" and len(pay) % 4 == 0:
                acc.setdefault("ifdt", []).append({"at": off,
                    "u32": list(struct.unpack("<%dI" % (len(pay)//4), pay))})
            off = pay_end
        elif tag in CONTAINERS:
            pay_end = min(off + 8 + size - 1, end)
            nctx = dict(ctx)
            if tag == b"STAT":
                nctx["in_stat"] = True
            if tag in (b"STRT", b"RUN ", b"STOP"):
                nctx["phase"] = tag.decode().strip()
                # current state name = last state appended
                if acc.get("states"):
                    nctx["state"] = acc["states"][-1]["name"]
            parse(buf, off + 8, pay_end, nctx, acc)
            off = pay_end
        elif tag == b"PROG":
            pay_end = min(off + 8 + size, end)
            pay = bytes(buf[off + 8:pay_end])
            if pay[:4] == b"AAS2" and len(pay) > 8:
                parse(buf, off + 8, pay_end, dict(ctx), acc)
            off = pay_end
        elif tag == b"DATA":
            pay_end_c = min(off + 8 + size - 1, end)
            if try_children(buf, off + 8, pay_end_c) and bytes(buf[off + 8:off + 12]) in (b"NAME", b"PROG"):
                nctx = dict(ctx)
                parse(buf, off + 8, pay_end_c, nctx, acc)
                # the NAME parsed inside sets ctx name; capture block
                off = pay_end_c
            else:
                pay_end = min(off + 8 + size, end)
                pay = bytes(buf[off + 8:pay_end])
                n = len(pay) // 4
                u32 = list(struct.unpack("<%dI" % n, pay[:n * 4])) if n else []
                f32 = list(struct.unpack("<%df" % n, pay[:n * 4])) if n else []
                nm = ctx.get("name", f"DATA@{off}")
                acc.setdefault("tables", []).append({"name": nm, "at": off,
                    "size": size, "u32": u32, "f32": f32,
                    "state": ctx.get("state"), "phase": ctx.get("phase")})
                off = pay_end
        else:
            break

result = {}
for fn in sys.argv[1:]:
    buf = open(fn, "rb").read()
    acc = {"file": os.path.basename(fn), "len": len(buf),
           "updt": None}
    # UPDT + root NAME
    acc["updt"] = cstr(buf[16:48])
    parse(buf, 8, len(buf), {}, acc)
    result[os.path.basename(fn)] = acc
print(json.dumps(result, indent=1))
