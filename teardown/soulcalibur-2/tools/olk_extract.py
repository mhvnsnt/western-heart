#!/usr/bin/env python3
"""Soulcalibur II (Xbox) root.olk extractor.
Namco OLK format: 16-byte header (u32 version, 'olnk' magic, u32 data_off, u32 flags)
+ (version+1) 16-byte entry quads (offset, size, timestamp, 0), null-terminated.
File offsets are relative to (archive_base + data_off); files packed 0x800-aligned.
Recurses into nested archives. Run: python3 Olk_extract.py root.olk outdir
"""
import os, struct, sys, mmap

def parse_archive(mm, base, size):
    version, magic, data_off, flags = struct.unpack_from('<IIII', mm, base)
    assert magic == 0x6b6e6c6f, f"bad magic at {base:#x}"
    entries = []
    for i in range(version + 1):
        o, s, ts, z = struct.unpack_from('<IIII', mm, base + 16 + i * 16)
        if o == 0 and s == 0 and ts == 0 and z == 0:
            # stop only on double-zero (isolated zero = empty slot)
            o2, s2, ts2, z2 = struct.unpack_from('<IIII', mm, base + 16 + (i + 1) * 16)
            if o2 == 0 and s2 == 0 and ts2 == 0 and z2 == 0:
                break
            continue
        entries.append((o, s, ts))
    return {"base": base, "version": version, "data_off": data_off,
            "entries": entries, "dbase": base + data_off}

def find_archives(mm, size):
    found = []
    for base in range(0, size, 0x800):
        if mm[base + 4:base + 8] == b'olnk':
            try:
                a = parse_archive(mm, base, size)
                found.append(a)
            except Exception as e:
                print(f"  ! parse failed @{base:#x}: {e}")
    return found

def main():
    src, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    size = os.path.getsize(src)
    print(f"source {src} ({size} bytes)", flush=True)
    f = open(src, 'rb')
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    archives = find_archives(mm, size)
    print(f"found {len(archives)} archives", flush=True)
    manifest = []
    for ai, a in enumerate(archives):
        if ai == 0:
            print(f"arch {ai}: master index skipped (containers only)", flush=True)
            continue
        adir = os.path.join(outdir, f"arch_{ai:02d}@{a['base']:#x}_v{a['version']}")
        os.makedirs(adir, exist_ok=True)
        n = 0
        # drop descriptor entries (range contains other entries' ranges)
        spans = [(a['dbase']+o, a['dbase']+o+s) for (o,s,ts) in a['entries'] if s]
        def is_descriptor(k):
            s0,e0 = spans[k]
            return sum(1 for j,(s1,e1) in enumerate(spans) if j!=k and s1>=s0 and e1<=e0) >= 1
        desc = set(k for k in range(len(spans)) if is_descriptor(k))
        nz = [e for e in a['entries'] if e[1]]
        for ei, (o, s, ts) in enumerate(nz):
            if ei in desc:
                continue  # archive descriptor, not a real file
            start = a['dbase'] + o
            end = start + s
            if end > size:
                print(f"  ! arch{ai} entry{ei} out of range [{start:#x},{end:#x})", flush=True)
                continue
            blob = mm[start:end]
            # nested archive? recurse logically by naming; still dump raw
            nested = blob[4:8] == b'olnk' if len(blob) >= 8 else False
            fn = f"f{ei:03d}_{'OLK' if nested else 'dat'}_{start:#x}_{s:#x}.bin"
            with open(os.path.join(adir, fn), 'wb') as out:
                out.write(blob)
            manifest.append(f"{adir}/{fn} ts={ts:#x}{' NESTED' if nested else ''}")
            n += 1
        print(f"arch {ai}: base={a['base']:#x} v={a['version']} files={n}", flush=True)
    with open(os.path.join(outdir, "MANIFEST.txt"), 'w') as mf:
        mf.write("\n".join(manifest))
    print(f"total files: {len(manifest)}", flush=True)

if __name__ == "__main__":
    main()
