#!/usr/bin/env python3
"""Extract Tekken 3 fighter geometry using the PROVEN n0madic/tekken3remake pipeline.

Replicates the models/king95/ extraction (2026-10-12) BIT-EXACTLY (verified by
re-solving: all 20 parts reproduce king95_renderdata.pkl with maxerr=0.0):
  1. Slice 3DMK record bytes from TEKKEN3.BNS at model-inventory.json bns_offset
  2. Parse with n0madic kmd.parse (DO NOT reimplement slot mapping)
  3. Stitch seams with kmd_skin.simulate at IDENTITY (all origins (0,0,0),
     flip_z=False) -- "fragments under identity transform", per the docs
  4. renderdata.pkl = {part_k: (stitched verts, [ft3/gt3 faces as coord tuples])}
  5. <name>_parts.obj + <name>_parts_montage.png

Usage: extract_fighter.py <fighter-name> <p1-record-id>
"""
import sys, os, json, pickle
sys.path.insert(0, os.path.expanduser("~/workspace/tools/tekken3remake/tools/research"))
import kmd as kmdlib
import kmd_skin

T3 = os.path.expanduser("~/workspace/game-reverse-engineering/tekken3")
BNS = os.path.join(T3, "disc/files/TEKKEN3/TEKKEN3.BNS")
MODELS = os.path.join(T3, "models")
PART_ROW = kmdlib.PART_ROW

def extract(record_id):
    inv = json.load(open(os.path.join(T3, "model-inventory.json")))
    recs = {r["id"]: r for r in inv["records"]}
    r = recs[record_id]
    with open(BNS, "rb") as f:
        f.seek(r["bns_offset"])
        data = f.read(r["size"])
    assert data[8:12] == b"3DMK", f"record {record_id}: bad magic {data[8:12]!r}"
    kmd = kmdlib.parse(data)
    # IDENTITY authoring pose: all part origins (0,0,0) -- bit-exact vs king95
    origins = [(0.0, 0.0, 0.0)] * len(PART_ROW)
    slots_per_part, stat = kmd_skin.simulate(kmd, origins, False)
    return data, kmd, slots_per_part, stat

def build_renderdata(kmd, slots_per_part):
    """{part_k: (verts, [face coord-tuples])} matching king95_renderdata.pkl exactly."""
    out = {}
    for k, row_index in enumerate(PART_ROW):
        row = kmd.rows[row_index]
        if row.verts is None or not row.verts.coords:
            continue
        slots = slots_per_part.get(k)
        if not slots:
            continue
        verts = [(float(x), float(y), float(z)) for (x, y, z) in slots]
        faces = []
        if row.faces:
            for f in row.faces:
                # face slots are byte_offset/4; vertex array slots are 8 bytes
                # (SVECTOR) -> true index = slot // 2 (verified vs king95 pkl)
                # king95 kept ft3/gt3 only; here quads are triangulated (v0,v1,v2)+(v0,v2,3)
                # because Heihachi is quad-dominant (390 quads vs 102 tris) and
                # tri-only would discard ~45% of every fighter's mesh.
                idx = [s // 2 for s in f.verts]
                if max(idx) >= len(slots):
                    continue
                if f.kind in ("ft3", "gt3"):
                    faces.append(tuple(verts[i] for i in idx[:3]))
                else:  # ft4/gt4 quad -> two triangles
                    i0, i1, i2, i3 = idx[:4]
                    faces.append((verts[i0], verts[i1], verts[i2]))
                    faces.append((verts[i0], verts[i2], verts[i3]))
        out[k] = (verts, faces)
    return out

def write_obj(path, renderdata):
    with open(path, "w") as f:
        f.write("# Tekken 3 3DMK export (n0madic pipeline, identity authoring pose)\n")
        vo = 1
        for k in sorted(renderdata):
            verts, faces = renderdata[k]
            f.write(f"\ng part_{k}\n")
            for (x, y, z) in verts:
                f.write(f"v {x:.4f} {y:.4f} {z:.4f}\n")
            index = {}
            for i, v in enumerate(verts):
                index.setdefault(v, i)
            for tri in faces:
                try:
                    idxs = " ".join(str(index[v] + vo) for v in tri)
                    f.write(f"f {idxs}\n")
                except KeyError:
                    continue
            vo += len(verts)

def write_montage(path, renderdata, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    parts = sorted(renderdata.keys())
    n = len(parts)
    cols = 5
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(10, 10.4), dpi=100)
    flat = list(axes.flat) if n > 1 else [axes]
    for ax, k in zip(flat, parts):
        verts, faces = renderdata[k]
        tris = [[(v[0], v[1]) for v in tri] for tri in faces]
        if tris:
            ax.add_collection(PolyCollection(tris, facecolor="0.75", edgecolor="0.3", linewidths=0.3))
        if verts:
            xs = [v[0] for v in verts]; ys = [v[1] for v in verts]
            ax.set_xlim(min(xs) - 10, max(xs) + 10)
            ax.set_ylim(min(ys) - 10, max(ys) + 10)
        ax.set_aspect("equal")
        ax.set_title(f"part {k} ({len(verts)}v/{len(faces)}f)", fontsize=8)
        ax.set_xticks([]); ax.set_yticks([])
    for ax in flat[n:]:
        ax.axis("off")
    fig.suptitle(title, fontsize=12)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)

def main():
    name = sys.argv[1]
    rid = int(sys.argv[2])
    outdir = os.path.join(MODELS, f"{name}{rid}")
    data, kmd, slots_per_part, stat = extract(rid)
    renderdata = build_renderdata(kmd, slots_per_part)
    nverts = sum(len(v) for v, _ in renderdata.values())
    nfaces = sum(len(f) for _, f in renderdata.values())
    print(f"{name} rec {rid}: {len(renderdata)} parts, {nverts} verts, {nfaces} faces, "
          f"seam pairs={stat.pairs} unresolved={stat.unresolved} maxgap={stat.max_gap:.2f}", flush=True)
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, f"{name}.kmd"), "wb") as f:
        f.write(data)
    write_obj(os.path.join(outdir, f"{name}_parts.obj"), renderdata)
    with open(os.path.join(outdir, f"{name}_renderdata.pkl"), "wb") as f:
        pickle.dump(renderdata, f)
    write_montage(os.path.join(outdir, f"{name}_parts_montage.png"), renderdata,
                  f"{name} (BNS {rid}) -- parts, identity authoring pose")
    print(f"  wrote {outdir}/", flush=True)

if __name__ == "__main__":
    main()
