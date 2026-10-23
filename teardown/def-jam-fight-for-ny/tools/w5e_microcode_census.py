#!/usr/bin/env python3
"""W5e microcode census of a local directory tree (see EAGL spec 7.9.4).
Censuses held Def Jam objects for a DEFINED (value != 0 or size != 0)
LitGouraud0__EAGLMicroCode / IrradTexture_Skin0__EAGLMicroCode symbol,
using the in-repo J4 ELF parser. W5e result over all held data: 0 defined.
Usage: w5e_microcode_census.py <root> <label> <out.json>
.o -> J4 RefPack+parse_elf symbol census; other files -> raw name scan
(+ ELF parse attempt when ELF magic). Incremental: writes JSON at end of
the single pass; progress lines to stderr every 500 files.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "customization", "tools"))
from eagl_refpack import refpack_decompress, find_refpack_offset
from convert_defjam_o import parse_elf

root, label, outp = sys.argv[1], sys.argv[2], sys.argv[3]
TARGETS = ("LitGouraud0__EAGLMicroCode", "IrradTexture_Skin0__EAGLMicroCode")
counts = {"o": 0, "other": 0}
hits, defined, raw_hits, errs = [], [], [], {}
n = 0
for dp, dns, fns in os.walk(root):
    for fn in sorted(fns):
        p = os.path.join(dp, fn); n += 1
        if n % 500 == 0: print(f"{label} {n} {counts}", file=sys.stderr)
        try: data = open(p, "rb").read()
        except Exception: continue
        if fn.endswith(".o"):
            counts["o"] += 1
            try:
                off = find_refpack_offset(data)
                dec = refpack_decompress(data[off:]) if off is not None else data
                elf = parse_elf(dec)
                for s in elf.get("symbols", []):
                    if "__EAGLMicroCode" in s["name"]:
                        r = {"file": os.path.relpath(p, root), "sym": s["name"],
                             "value": s["value"], "size": s["size"]}
                        hits.append(r)
                        if s["value"] != 0 or s["size"] != 0: defined.append(r)
            except Exception as e:
                errs[type(e).__name__] = errs.get(type(e).__name__, 0) + 1
        else:
            counts["other"] += 1
            for t in TARGETS + ("__EAGLMicroCode",):
                if t.encode() in data:
                    raw_hits.append({"file": os.path.relpath(p, root), "needle": t})
            if data[:4] == b"\x7fELF":
                try:
                    elf = parse_elf(data)
                    for s in elf.get("symbols", []):
                        if "__EAGLMicroCode" in s["name"]:
                            r = {"file": os.path.relpath(p, root), "sym": s["name"],
                                 "value": s["value"], "size": s["size"]}
                            hits.append(r)
                            if s["value"] != 0 or s["size"] != 0: defined.append(r)
                except Exception as e:
                    errs["elf_" + type(e).__name__] = errs.get("elf_" + type(e).__name__, 0) + 1
res = {"label": label, "root": root, "counts": counts, "symbol_hits_total": len(hits),
       "defined_hits": defined, "raw_name_hits": raw_hits, "errors": errs,
       "hits_by_sym": {}}
from collections import Counter
res["hits_by_sym"] = dict(Counter(h["sym"] for h in hits))
json.dump(res, open(outp, "w"), indent=1)
print(json.dumps({k: res[k] for k in ("label","counts","symbol_hits_total","defined_hits","errors","hits_by_sym")}, indent=1))
print("raw_name_hits:", raw_hits[:10], "total", len(raw_hits))
