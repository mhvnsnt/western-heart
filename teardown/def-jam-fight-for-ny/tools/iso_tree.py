#!/usr/bin/env python3
"""List the full file tree of a PS2 ISO9660 image (via pycdlib), with sizes."""
import sys, pycdlib

iso = pycdlib.PyCdlib()
iso.open(sys.argv[1])

files = []
dirs = ['/']
def walk(path):
    for child in iso.list_children(iso_path=path):
        name = child.file_identifier().decode('latin1').rstrip(';').rstrip('.')
        if name in ('.', '..'):
            continue
        full = (path.rstrip('/') + '/' + name)
        if child.is_dir():
            walk(full)
        else:
            files.append((full, child.data_length))

for d in dirs:
    walk(d)

total = sum(s for _, s in files)
files.sort(key=lambda x: -x[1])
print(f"files={len(files)} total_bytes={total} ({total/1e9:.2f} GB)")
for f, s in files[:80]:
    print(f"  {s:>12}  {f}")
big = sum(s for f, s in files if s > 100_000_000)
print(f"files>100MB bytes: {big/1e9:.2f} GB")
exts = {}
for f, s in files:
    e = f.rsplit('.', 1)[-1].upper() if '.' in f else 'NONE'
    exts.setdefault(e, [0, 0])
    exts[e][0] += 1; exts[e][1] += s
print("\nby extension:")
for e, (c, s) in sorted(exts.items(), key=lambda x: -x[1][1])[:25]:
    print(f"  {e:>6}  count={c:<6} bytes={s/1e6:>9.1f} MB")
iso.close()
