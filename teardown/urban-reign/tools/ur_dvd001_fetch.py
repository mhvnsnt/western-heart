#!/usr/bin/env python3
"""Urban Reign DVD001.AFS audio extraction via range-fetch.
Maps DVD001.AFS entry table (fetched via ranges), then pulls all
sound/ok_adx/adx/*.adx files (~995 files, ~367MB) into the teardown tree.
Also usable for any DVD001 entry list.
Usage:
  python3 ur_dvd001_fetch.py --map          # build afs-map/dvd001_afs_map.json
  python3 ur_dvd001_fetch.py --audio OUTDIR # fetch all ADX into OUTDIR
  python3 ur_dvd001_fetch.py --list filelist.txt OUTDIR  # fetch named entries
"""
import json, os, struct, sys, urllib.request

RELEASE = "https://github.com/mhvnsnt/western-heart/releases/download/urban-reign-iso-v1"
PART_NAMES = [f"urban-reign-500m.part_a{chr(ord('a')+i)}" for i in range(7)] + ["urban-reign-500m.part_ah"]
PART_SIZE = 524_288_000
LAST_PART_SIZE = 470_908_928
TEARDOWN = os.path.expanduser("~/workspace/western-heart/teardown/urban-reign")
MAP_PATH = os.path.join(TEARDOWN, "afs-map", "dvd001_afs_map.json")
UA = {"User-Agent": "Mozilla/5.0"}

def part_for_offset(abs_off):
    idx = abs_off // PART_SIZE
    intra = abs_off % PART_SIZE
    if idx < 7:
        return PART_NAMES[idx], intra
    if abs_off >= 7 * PART_SIZE + LAST_PART_SIZE:
        raise ValueError(f"offset {abs_off} beyond ISO end")
    return PART_NAMES[7], intra

def fetch_range(part_name, start, length):
    url = f"{RELEASE}/{part_name}"
    req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{start+length-1}", **UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        data = r.read()
    if len(data) != length:
        raise IOError(f"short read: got {len(data)}, want {length} from {part_name}@{start}")
    return data

def fetch_iso_range(abs_off, length):
    out = b""
    remaining, cur = length, abs_off
    while remaining > 0:
        part, intra = part_for_offset(cur)
        psize = PART_SIZE if not part.endswith("_ah") else LAST_PART_SIZE
        chunk = min(remaining, psize - intra)
        out += fetch_range(part, intra, chunk)
        cur += chunk
        remaining -= chunk
    return out

def get_afs_base(name):
    cache = os.path.expanduser(f"~/workspace/agent-ops/ur-extract/{name.lower()}_base.txt")
    if os.path.exists(cache):
        return int(open(cache).read().strip())
    pvd = fetch_iso_range(16 * 2048, 2048)
    assert pvd[1:6] == b"CD001", "not ISO9660"
    root_ext = struct.unpack("<I", pvd[156+2:156+6])[0]
    root_len = struct.unpack("<I", pvd[156+10:156+14])[0]
    root = fetch_iso_range(root_ext * 2048, root_len)
    pos = 0
    found = None
    while pos < len(root):
        reclen = root[pos]
        if reclen == 0:
            nxt = ((pos // 2048) + 1) * 2048
            if nxt <= pos:
                break
            pos = nxt
            continue
        rec = root[pos:pos+reclen]
        ext = struct.unpack("<I", rec[2:6])[0]
        fnlen = rec[32]
        nm = rec[33:33+fnlen].split(b";")[0].decode("ascii", "replace")
        if nm.upper() == name.upper():
            found = ext * 2048
            break
        pos += reclen
    assert found, f"{name} not found in root dir"
    open(cache, "w").write(str(found))
    return found

def parse_afs(base):
    hdr = fetch_iso_range(base, 16)
    assert hdr[0:4] == b"AFS\x00", f"bad AFS magic: {hdr[0:4]!r}"
    count = struct.unpack("<I", hdr[4:8])[0]
    assert count < 100000, f"implausible count {count}"
    tbl = fetch_iso_range(base + 8, count * 8)
    entries = [struct.unpack("<II", tbl[i*8:(i+1)*8]) for i in range(count)]
    nt_off, nt_size = struct.unpack("<II", hdr[8:16])
    names = []
    if nt_off and nt_size and nt_size < 20_000_000:
        raw = fetch_iso_range(base + nt_off, nt_size)
        field = nt_size // count if count else 32
        field = 48 if abs(field - 48) < abs(field - 32) else 32
        for i in range(count):
            chunk = raw[i*field:(i+1)*field]
            names.append(chunk.split(b"\x00")[0].decode("ascii", "replace") or f"file_{i:05d}.bin")
    else:
        names = [f"file_{i:05d}.bin" for i in range(count)]
    return [{"name": names[i] if i < len(names) else f"file_{i:05d}.bin",
             "afs_off": e[0], "size": e[1]} for i, e in enumerate(entries)]

def build_map():
    base = get_afs_base("DVD001.AFS")
    print(f"DVD001.AFS base = {base} (0x{base:x})", file=sys.stderr)
    m = parse_afs(base)
    json.dump(m, open(MAP_PATH, "w"), indent=1)
    print(f"wrote {MAP_PATH}: {len(m)} entries", file=sys.stderr)
    return base, m

def fetch_entry(base, entry, dest):
    data = fetch_iso_range(base + entry["afs_off"], entry["size"])
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "wb").write(data)

def cmd_audio(outdir):
    base = get_afs_base("DVD001.AFS")
    m = (json.load(open(MAP_PATH)) if os.path.exists(MAP_PATH)
         else parse_afs(base))
    adx = [e for e in m if e["name"].lower().endswith(".adx")]
    print(f"{len(adx)} ADX entries, total {sum(e['size'] for e in adx):,} bytes", file=sys.stderr)
    ok, fail = 0, []
    for e in adx:
        fname = e["name"].split("/")[-1]
        dest = os.path.join(outdir, fname)
        if os.path.exists(dest) and os.path.getsize(dest) == e["size"]:
            print(f"EXISTS {fname}", file=sys.stderr); ok += 1; continue
        try:
            fetch_entry(base, e, dest)
            print(f"OK {e['size']:>10,}  {fname}", file=sys.stderr); ok += 1
        except Exception as ex:
            print(f"FAIL {fname}: {ex}", file=sys.stderr); fail.append(fname)
    print(f"done: {ok} ok, {len(fail)} failed", file=sys.stderr)
    for f in fail:
        print(f"  FAILED: {f}", file=sys.stderr)

def cmd_list(listfile, outdir):
    base = get_afs_base("DVD001.AFS")
    m = (json.load(open(MAP_PATH)) if os.path.exists(MAP_PATH)
         else parse_afs(base))
    by_name = {e["name"]: e for e in m if e["size"] > 0}
    targets = [l.strip() for l in open(listfile) if l.strip() and not l.startswith("#")]
    ok, fail = 0, []
    for t in targets:
        e = by_name.get(t)
        if not e:
            print(f"SKIP (not in map): {t}", file=sys.stderr); fail.append(t); continue
        dest = os.path.join(outdir, t.replace("/", "_"))
        if os.path.exists(dest) and os.path.getsize(dest) == e["size"]:
            print(f"EXISTS {t}", file=sys.stderr); ok += 1; continue
        try:
            fetch_entry(base, e, dest)
            print(f"OK {e['size']:>10,}  {t}", file=sys.stderr); ok += 1
        except Exception as ex:
            print(f"FAIL {t}: {ex}", file=sys.stderr); fail.append(t)
    print(f"done: {ok} ok, {len(fail)} failed", file=sys.stderr)

if __name__ == "__main__":
    if sys.argv[1] == "--map":
        build_map()
    elif sys.argv[1] == "--audio":
        cmd_audio(sys.argv[2])
    elif sys.argv[1] == "--list":
        cmd_list(sys.argv[2], sys.argv[3])
    else:
        sys.exit("usage: --map | --audio OUTDIR | --list filelist.txt OUTDIR")
