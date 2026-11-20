#!/usr/bin/env python3
"""Extract VF5 PS3 obj.bin -> OBJ (positions + strip indices).
Chunk: +0x54 block -> vcount @+0x20, pos_rel @+0x24, end_rel @+0x28.
Index buffers: found by scanning for u16 runs (all < 3000), mapped to chunk
by max_index < vcount and file order.
"""
import struct
import sys


def u32(d, o):
    return struct.unpack("<I", d[o:o + 4])[0]


def parse_chunks(d):
    n = u32(d, 4)
    chunks = []
    for i in range(n):
        cb = u32(d, 0x40 + i * 4)
        h2 = cb + 0x54
        vcount = u32(d, h2 + 0x20)
        pos_rel = u32(d, h2 + 0x24)
        end_rel = u32(d, h2 + 0x28)
        assert pos_rel + vcount * 12 == end_rel, f"chunk{i} size mismatch"
        pos_base = cb + pos_rel
        verts = [struct.unpack("<3f", d[pos_base + v * 12:pos_base + v * 12 + 12])
                 for v in range(vcount)]
        chunks.append({"idx": i, "base": cb, "vcount": vcount,
                       "pos_base": pos_base, "verts": verts})
    return chunks


def find_index_runs(d):
    """Global scan for u16 index runs (fallback)."""
    sz = len(d)
    runs = []
    i = 0
    nu16 = sz // 2
    while i < nu16:
        v = struct.unpack("<H", d[i * 2:i * 2 + 2])[0]
        if v < 3000:
            start = i
            mx = v
            while i < nu16:
                v = struct.unpack("<H", d[i * 2:i * 2 + 2])[0]
                if v >= 3000:
                    break
                if v > mx:
                    mx = v
                i += 1
            length = i - start
            if length >= 100:
                runs.append((start * 2, length, mx))
        else:
            i += 1
    return runs


def scan_gap_for_indices(d, gap_start, gap_end, vcount):
    """Scan a byte range for the chunk's index strip (u16s < vcount)."""
    runs = []
    lo = gap_start // 2
    hi = min(gap_end, len(d)) // 2
    j = lo
    while j < hi:
        v = struct.unpack("<H", d[j * 2:j * 2 + 2])[0]
        if v < vcount:
            s = j
            mx = v
            while j < hi:
                v = struct.unpack("<H", d[j * 2:j * 2 + 2])[0]
                if v >= vcount:
                    break
                mx = max(mx, v)
                j += 1
            length = j - s
            if length >= 50 and mx > 10:
                runs.append((s * 2, length, mx))
        else:
            j += 1
    # prefer longest
    runs.sort(key=lambda r: -r[1])
    return runs[0] if runs else None


def strip_to_tris(idxs):
    tris = []
    for i in range(len(idxs) - 2):
        a, b, c = idxs[i], idxs[i + 1], idxs[i + 2]
        if a == b or b == c or a == c:
            continue
        tris.append((a, b, c) if i % 2 == 0 else (b, a, c))
    return tris


def main():
    src = sys.argv[1]
    out = sys.argv[2]
    only = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
    d = open(src, "rb").read()
    assert u32(d, 0) == 0x05062500, "bad magic"
    chunks = parse_chunks(d)
    runs = find_index_runs(d)
    print(f"{len(chunks)} chunks, {len(runs)} index runs")
    # map runs to chunks: run must start after chunk pos buffer, max < vcount
    # choose the run with largest length that fits
    # sort chunks by base; for each chunk, the index run is the first run
    # starting after the chunk's position buffer end and before next chunk base
    chunks_sorted = sorted(chunks, key=lambda c: c["base"])
    with open(out, "w") as f:
        voff = 1
        for ci, ch in enumerate(chunks_sorted):
            if only is not None and ch["idx"] not in only:
                voff += ch["vcount"]
                continue
            for v in ch["verts"]:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            pos_end = ch["pos_base"] + ch["vcount"] * 12
            next_base = (chunks_sorted[ci + 1]["base"]
                         if ci + 1 < len(chunks_sorted) else len(d))
            cands = [r for r in runs
                     if pos_end <= r[0] < next_base
                     and 50 < r[2] < ch["vcount"] * 4]
            if cands:
                cands.sort(key=lambda r: r[0])
                roff, rlen, rmax = cands[0]
            else:
                # fallback: scan the gap directly for a strip of this chunk
                gap = scan_gap_for_indices(d, pos_end, next_base, ch["vcount"])
                if gap:
                    roff, rlen, rmax = gap
                    print(f"  chunk{ch['idx']}: gap-scan found run@{roff}")
                else:
                    roff = None
            if roff is not None:
                idx = struct.unpack("<%dH" % rlen, d[roff:roff + rlen * 2])
                # keep only indices valid for this chunk
                idx = [v for v in idx if v < ch["vcount"]]
                tris = strip_to_tris(idx)
                f.write(f"g chunk{ch['idx']}\n")
                for a, b, c in tris:
                    f.write(f"f {a + voff} {b + voff} {c + voff}\n")
                print(f"  chunk{ch['idx']}: {ch['vcount']}v + run@{roff} "
                      f"({rlen} idx, max {rmax}) -> {len(tris)} tris")
            else:
                print(f"  chunk{ch['idx']}: {ch['vcount']}v, NO index run")
            voff += ch["vcount"]
    print("wrote", out)


if __name__ == "__main__":
    main()
