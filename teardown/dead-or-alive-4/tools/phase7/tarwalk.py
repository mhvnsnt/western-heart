import sys, struct
sys.path.insert(0, '/home/hatch/workspace/_doa4p2-scratch/p6')
from fetch import fetch

def parse_hdr(b):
    if len(b) < 512 or b[257:262] != b'ustar':
        return None
    name = b[0:100].split(b'\0')[0].decode('utf-8','replace')
    prefix = b[345:500].split(b'\0')[0].decode('utf-8','replace')
    if prefix: name = prefix + '/' + name
    try: size = int(b[124:136].split(b'\0')[0].strip() or b'0', 8)
    except Exception: return None
    return name, size

def walk(start, steps=12):
    off = start
    for i in range(steps):
        b = fetch(off, 512)
        h = parse_hdr(b)
        print(f"hdr@{off} ({off:#x}): {h}")
        if h is None: 
            print("  raw:", b[:64]); return off
        name, size = h
        data = off + 512
        padded = (size + 511) // 512 * 512
        print(f"  data@{data} size={size} next_hdr@{data+padded}")
        off = data + padded
    return off

if __name__ == '__main__':
    start = int(sys.argv[1], 0)
    steps = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    walk(start, steps)
