#!/usr/bin/env python3
"""Batch-decode every VGS file to PNG + inventory CSV.
Usage: python3 vgs_batch_decode.py <vgs_dir> <out_dir>
Writes <out_dir>/<basename>.png (+ texture_8bit_w320.png raw) and
<out_dir>/VGS-INVENTORY.csv: name,size,grid,columns,sprites,blob_off,blob_len.
Files that fail magic check are recorded with status=bad_magic, not dropped.
"""
import csv, os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vgs_decode import parse_vgs, find_texture_blob, decode_texture, MAGIC

def main():
    vgs_dir, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    ok = fail = 0
    for name in sorted(os.listdir(vgs_dir)):
        if not name.lower().endswith(".vgs"):
            continue
        path = os.path.join(vgs_dir, name)
        base = name[:-4]
        size = os.path.getsize(path)
        try:
            d, info = parse_vgs(path)
        except Exception as ex:
            rows.append([name, size, "", "", "", "", "", f"bad_magic: {ex}"])
            fail += 1
            continue
        W, H = info["grid"]
        nspr = sum(len(c["sprites"]) for c in info["columns"])
        blob = find_texture_blob(d, info)
        status = "ok"
        if blob:
            blob_len = len(d) - blob
            try:
                decode_texture(d, out_dir, blob, width=320)
                raw = os.path.join(out_dir, "texture_8bit_w320.png")
                dest = os.path.join(out_dir, base + ".png")
                if os.path.exists(dest):
                    os.remove(dest)
                os.rename(raw, dest)
            except Exception as ex:
                status = f"decode_fail: {ex}"
                fail += 1
        else:
            blob_len = ""
            status = "no_blob"
        rows.append([name, size, f"{W}x{H}", len(info["columns"]), nspr,
                     hex(blob) if blob else "", blob_len, status])
        ok += 1
    with open(os.path.join(out_dir, "VGS-INVENTORY.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "size", "grid", "columns", "sprites",
                    "texture_blob_off", "texture_blob_len", "status"])
        w.writerows(rows)
    print(f"decoded: {ok} ok, {fail} failed/no-blob out of {ok+fail}")
    print(f"inventory: {os.path.join(out_dir, 'VGS-INVENTORY.csv')}")

if __name__ == "__main__":
    main()
