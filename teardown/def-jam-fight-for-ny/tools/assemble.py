#!/usr/bin/env python3
"""Wait for 8-seg Def Jam ISO download, assemble, verify, list tree."""
import os, time, sys, json, subprocess

W = os.path.expanduser("~/workspace/defjam-work/iso")
TOTAL = 4694573056
ISO = os.path.join(W, "SLUS_210.04.Def Jam - Fight for NY.iso")
LOG = os.path.join(W, "assemble.log")

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    open(LOG, "a").write(line + "\n")

def seg_total():
    t = 0
    for i in range(8):
        p = os.path.join(W, f"seg_{i}.part")
        if os.path.exists(p):
            t += os.path.getsize(p)
    return t

deadline = time.time() + 3 * 3600
while time.time() < deadline:
    t = seg_total()
    if t >= TOTAL:
        break
    log(f"downloaded {t}/{TOTAL} ({100*t/TOTAL:.1f}%)")
    time.sleep(120)

t = seg_total()
if t < TOTAL:
    log(f"TIMEOUT: only {t}/{TOTAL} bytes after 3h")
    sys.exit(1)

log("download complete, assembling...")
with open(ISO, "wb") as out:
    for i in range(8):
        p = os.path.join(W, f"seg_{i}.part")
        with open(p, "rb") as f:
            while True:
                b = f.read(8 * 1024 * 1024)
                if not b:
                    break
                out.write(b)
sz = os.path.getsize(ISO)
log(f"assembled size={sz} expected={TOTAL} match={sz == TOTAL}")
if sz != TOTAL:
    sys.exit(1)

# verify ISO9660 parses
r = subprocess.run(
    [sys.executable, os.path.expanduser("~/workspace/defjam-work/tools/iso_tree.py"), ISO],
    capture_output=True, text=True, timeout=600)
open(os.path.join(W, "iso_tree.txt"), "w").write(r.stdout + "\n---STDERR---\n" + r.stderr)
log("tree listing written to iso_tree.txt")
print("ASSEMBLE_DONE")
