#!/usr/bin/env python3
"""tkdata_unpack_tolerant.py — per-entry tolerant variant of the GRE-proven
t7_tkdata.py (itself a port of the community tkdata.bms v0.2.1). Identical
format logic (same key, same index walk, same per-file AES + zlib); the only
change: a bad entry is logged and skipped instead of aborting the unpack,
and every recovered file is hashed into unpack-report.json.

Usage: tkdata_unpack_tolerant.py <tkdata.bin> <outdir>
"""
import hashlib
import json
import os
import struct
import sys
import zlib

from Crypto.Cipher import AES

KEY = b'epsNJf#ut&v3fVrndlYkp&Sq@5Ry?BHA'


def aes(b):  # quickbms 'encryption aes' == ECB decrypt over full blocks
    n = len(b) // 16 * 16
    return AES.new(KEY, AES.MODE_ECB).decrypt(b[:n]) + b[n:]


def main():
    src, out = sys.argv[1], sys.argv[2]
    d = open(src, 'rb').read()
    assert d[:16] == b'_TEKKEN7CSFILES_', d[:16]
    off, size = struct.unpack_from('<qq', d, len(d) - 0x68)
    m = aes(d[off:off + size])
    if m[:8] != b'tsLniBNB':
        try:
            m = zlib.decompress(m)
        except Exception:
            pass
    assert m[:8] == b'tsLniBNB', m[:16]
    num, info, name = struct.unpack_from('<qqq', m, 8)
    os.makedirs(out, exist_ok=True)
    report = {"source": src, "source_sha256": hashlib.sha256(d).hexdigest(),
              "entries": [], "ok": 0, "failed": 0}
    for _ in range(num):
        nm = m[name:m.index(b'\0', name)].decode('latin1')
        name = m.index(b'\0', name) + 1
        fid, flags, _, fo, zs, us, _, _ = struct.unpack_from('<8q', m, info)
        info += 64
        fo += 0x10
        try:
            blob = aes(d[fo:fo + zs])
            if flags & 1:
                blob = zlib.decompress(blob)
            blob = blob[:us]
            p = os.path.join(out, nm.lstrip('/\\').replace('\\', '/'))
            os.makedirs(os.path.dirname(p) or out, exist_ok=True)
            open(p, 'wb').write(blob)
            report["entries"].append({"name": nm, "ok": True, "bytes": len(blob),
                                      "sha256": hashlib.sha256(blob).hexdigest()})
            report["ok"] += 1
        except Exception as e:  # noqa: BLE001 - tolerant by design
            report["entries"].append({"name": nm, "ok": False, "error": str(e)})
            report["failed"] += 1
    with open(os.path.join(out, "unpack-report.json"), "w") as f:
        json.dump(report, f, indent=1)
    print(f"files {num} ok={report['ok']} failed={report['failed']}")
    for e in report["entries"]:
        if not e["ok"]:
            print("FAILED:", e["name"], e["error"])


if __name__ == "__main__":
    main()
