"""Lane 1D: convert GTAinside DOA6->GTA:SA .ifp packs (ANP3) to WH wh-anim/1 JSON bank.
Uses rwfury (PyPI) as the ANP3 parser — industry-standard, bit-exact, validates
declared frame-data size. Output shape follows game/assets/anim/t7/*/graph-clips/clips.NN.json
(format wh-anim/1) and game/assets/anim/t3/*/*.json (per-clip wh-anim/1).
Bones stay the 29-bone GTA SA ped skeleton as exported (names + GTA bone IDs);
NO retarget to WH rigs is performed or implied — retarget is a separate job.
Root translation: rwfury translations (/1024, GTA units == metres).
Quats: rwfury rotations (/4096), xyzw floats. Times: raw frame index / 60;
fps detected per clip from the raw_time step (60/step; step 1 -> 60fps, step 2 -> 30fps).
EDGE CASE (proven on KAS00246_KAS.ifp, 1/322 in Kasumi pack): file carries 19,528
trailing bytes after the first 29 objects — 18 extra type-4 objects (duplicated
finger/leg bones + Belly + 5 Nub bones) — and a declared frame_data_size 2x the
first animation's. Fallback: truncate to the first animation's end (found by
walking [header][frames] objects), patch the declared size + file size in the
in-memory copy, parse with rwfury, and record the trailing bytes in provenance.
"""
import io, json, math, zipfile, hashlib, sys, os, struct
import rwfury

def first_anim_end(data):
    """Walk [obj header 36B][frames] objects from offset 72; return end offset of
    the first animation's object block, or None if the walk breaks early."""
    off = 72
    seen = 0
    try:
        while off + 36 <= len(data):
            name = data[off:off+24].split(b'\x00')[0]
            ftype, fcount, bone_id = struct.unpack('<III', data[off+24:off+36])
            if ftype not in (3, 4) or fcount > 5000 or not name:
                # end of the first animation's object block (trailing data follows)
                return off if seen else None
            rec = 16 if ftype == 4 else 10
            off += 36 + fcount * rec
            seen += 1
        return off
    except Exception:
        return off if seen else None

def parse_ifp_first_anim(data):
    """Return (generic_anim, trailing_bytes, patched_bool)."""
    try:
        g = list(rwfury.Ifp.from_bytes(data).iter_generic_animations())[0]
        return g, 0, False
    except ValueError as e:
        if 'frame data size mismatch' not in str(e):
            raise
    end = first_anim_end(data)
    if end is None or end > len(data):
        raise ValueError('size mismatch and first-animation walk failed')
    # end == len(data) is fine: complete file, declared size just wrong (exporter bug)
    # truncate + patch declared frame_data_size (offset 60) and file size (offset 4)
    trunc = bytearray(data[:end])
    # recompute declared frame data size: sum over objects
    off = 72; total = 0
    while off < end:
        ftype, fcount, bone_id = struct.unpack('<III', trunc[off+24:off+36])
        total += fcount * (16 if ftype == 4 else 10)
        off += 36 + fcount * (16 if ftype == 4 else 10)
    struct.pack_into('<I', trunc, 64, total)
    struct.pack_into('<I', trunc, 4, len(trunc) - 8)
    g = list(rwfury.Ifp.from_bytes(bytes(trunc)).iter_generic_animations())[0]
    return g, len(data) - end, True

def clip_to_wh(name, data_bytes, src_zip, src_sha256):
    g, trailing, patched = parse_ifp_first_anim(data_bytes)
    bones = []
    rot = {}
    trans = {}
    bone_ids = {}
    root_t = None
    step = 1
    for t in g.tracks:
        bname = t.name.strip()
        bones.append(bname)
        bone_ids[bname] = t.bone_id
        n = t.keyframe_count
        qs = [[round(float(t.rotations[4*i+j]), 6) for j in range(4)] for i in range(n)]
        rot[bname] = qs
        # type-4 (ROOT) bones carry translations; keep every bone's own track.
        # root_t (WH-reader compat) is ONLY the 'Normal' root bone's translation.
        if t.translations is not None:
            tr = [[round(float(t.translations[3*i+j]), 6) for j in range(3)] for i in range(n)]
            trans[bname] = tr
            if bname == 'Normal':
                root_t = tr
        if t.raw_times and len(t.raw_times) > 1:
            step = t.raw_times[1] - t.raw_times[0]
    fps = 60.0 / step if step else 60.0
    clip = {
        "format": "wh-anim/1",
        "fps": fps,
        "anim_set": "FIGHT",
        "source": {
            "game": "Dead or Alive 6 (Team Ninja, 2019)",
            "pack": "GTAinside DOA6->GTA:SA .ifp by GTAV06",
            "zip": src_zip,
            "zip_sha256": src_sha256,
            "ifp_file": name,
            "ifp_sha256": hashlib.sha256(data_bytes).hexdigest(),
            "parser": "rwfury (ANP3, bit-exact)",
            "skeleton": "GTA:SA ped (29 bones, GTA bone IDs); NOT a WH rig — retarget is a separate job",
            "trailing_bytes_after_first_anim": trailing,
            "header_patched_for_parse": patched,
        },
        "bones": bones,
        "bone_ids": bone_ids,
        "rot_xyzw": rot,
        "loop": '(loop)' in name,
    }
    if trans:
        clip["trans_xyz"] = trans
    if root_t is not None:
        clip["root_t"] = root_t
    return clip

def convert_zip(zip_path, out_json_path):
    zsha = hashlib.sha256(open(zip_path, 'rb').read()).hexdigest()
    zname = os.path.basename(zip_path)
    clips = {}
    failed = []
    with zipfile.ZipFile(zip_path) as zf:
        ifps = sorted(n for n in zf.namelist() if n.lower().endswith('.ifp'))
        for n in ifps:
            data = zf.read(n)
            # key by zip-relative path (Normal/ vs Custom/ variants share basenames)
            clip_name = os.path.splitext(n)[0]
            try:
                clips[clip_name] = clip_to_wh(n, data, zname, zsha)
            except Exception as e:
                # one bad .ifp must not lose the whole pack; record and continue
                failed.append({"ifp_file": n, "error": type(e).__name__ + ": " + str(e),
                               "ifp_sha256": hashlib.sha256(data).hexdigest(),
                               "ifp_bytes": len(data)})
    with open(out_json_path, 'w') as f:
        json.dump({"format": "wh-doa6-ifp-bank/1", "source_zip": zname, "source_zip_sha256": zsha,
                   "clips": clips, "failed": failed}, f, separators=(',', ':'))
    return len(clips), os.path.getsize(out_json_path)

if __name__ == '__main__':
    zip_path, out = sys.argv[1], sys.argv[2]
    n, size = convert_zip(zip_path, out)
    print(f"{zip_path}: {n} clips -> {out} ({size} bytes)")
