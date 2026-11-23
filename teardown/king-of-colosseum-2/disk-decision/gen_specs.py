#!/usr/bin/env python3
"""Generate batch specs for the KoC2 raw landing (local phase).

Phases (run in order, with verify+delete checkpoints between):
  P1: B1 (small files) + B2a-f (JP ISO, 6 x ~800MB)
  P2: B3a-c (v02ref ISO, 3 x ~1.6GB)   [after JP ISOs deleted, headroom ~10G]
  P3: B4a-d (iso/ tree) + B5 (kc2fire000+001) + B6 (kc2fireafs) + B7 (mvs+hybrid.000)
      [after v02ref deleted, headroom ~15G, 3GB cap]
"""
import json
import os

SPECDIR = os.path.expanduser("~/workspace/koc2-disk-decision/specs")
EXTRACT = "/home/hatch/workspace/grok-declined-items/lane-koc2/extract"
M3 = "/home/hatch/workspace/koc2-english/work/m3"
KACTUS = os.path.join(M3, "sources/kactusken")
PIECE = 99_000_000

SHA = {
    "jp": "7daa1f8c950272f24e9888d26338645fdbac1974da8dbf43b30c0042ceed0511",
    "v02ref": "8184f07ac7559d1e1f5fd3695e7a308ded33688281a32433028fed3f41c5327d",
    "hybrid000": "89e5f0d6feda57c3dea166e532079d7147c11224f6b12659b281f58207e52f44",
    # iso/ DATA hashes filled from hashes-iso-data.txt at generation time
}

JP_ISO = os.path.join(EXTRACT, "King of Colosseum II (Japan).iso")
V02_ISO = os.path.join(KACTUS, "v02ref/kactusken-v0.2-english.iso")
HYB000 = os.path.join(M3, "work/KC2FIRE-hybrid.000")


def npieces(path):
    sz = os.path.getsize(path)
    return (sz + PIECE - 1) // PIECE


def iso_commits(name, src, dst_dir, dst_name, sha256, original, max_pieces,
                prefix, max_bytes):
    """Split one big file into sequential commits of <= max_pieces pieces."""
    n = npieces(src)
    specs = []
    idx = 0
    ci = 0
    while idx < n:
        take = list(range(idx, min(idx + max_pieces, n)))
        last = take[-1] == n - 1
        ci += 1
        specs.append({
            "name": f"{prefix}{ci}",
            "message": (f"KoC2 raw: {dst_name} pieces {take[0]}-{take[-1]} "
                        f"of {n}" + (" + manifest" if last else "")),
            "max_bytes": max_bytes,
            "split_files": [{
                "src": src, "dst_dir": dst_dir, "dst_name": dst_name,
                "pieces": take, "sha256": sha256,
                "original_name": original, "manifest": last,
            }],
        })
        idx = take[-1] + 1
    return specs


def write(spec):
    with open(os.path.join(SPECDIR, spec["name"] + ".json"), "w") as f:
        json.dump(spec, f, indent=1)
    print("wrote", spec["name"])


def main():
    os.makedirs(SPECDIR, exist_ok=True)
    # --- iso/DATA hashes (computed by background job) ---
    hpath = os.path.expanduser("~/workspace/koc2-disk-decision/hashes-iso-data.txt")
    data_sha = {}
    with open(hpath) as f:
        for line in f:
            h, p = line.split()
            data_sha[os.path.basename(p)] = h

    # --- B1: small files ---
    b1_files = []
    # kactusken patch
    b1_files.append({"src": os.path.join(KACTUS, "v0.2.zip"),
                     "dst": "raw/king-of-colosseum-2/kactusken-v0.2/v0.2.zip"})
    xdelta_rename = {
        "King of Colosseum II (English) (All Unlocked).xdelta":
            "King-of-Colosseum-II-English-All-Unlocked.xdelta",
        "King of Colosseum II (English).xdelta":
            "King-of-Colosseum-II-English.xdelta",
        "King of Colosseum II (Japan) (All Unlocked).xdelta":
            "King-of-Colosseum-II-Japan-All-Unlocked.xdelta",
    }
    for fn in sorted(os.listdir(os.path.join(KACTUS, "v0.2"))):
        dst_name = xdelta_rename.get(fn, fn)
        b1_files.append({
            "src": os.path.join(KACTUS, "v0.2", fn),
            "dst": f"raw/king-of-colosseum-2/kactusken-v0.2/v0.2/{dst_name}"})
    # extract/ top-level small files (skip JP ISO + big dirs; modules/ via dirs)
    skip = {"King of Colosseum II (Japan).iso", "iso", "kc2fire000",
            "kc2fire001", "kc2fireafs", "kc2firemvs", "modules"}
    for fn in sorted(os.listdir(EXTRACT)):
        if fn in skip:
            continue
        p = os.path.join(EXTRACT, fn)
        if os.path.isfile(p):
            b1_files.append({"src": p,
                             "dst": f"raw/king-of-colosseum-2/jp/{fn}"})
    write({"name": "B1-small", "message": "KoC2 raw: kactusken v0.2 patch + JP extract small files\n\nv0.2.zip + 3 xdelta patches + README, JP per-archive SHA-256 manifests,\nextraction logs, TIM2 test renders, modules/.",
           "max_bytes": 100_000_000,
           "files": b1_files,
           "dirs": [{"src": os.path.join(EXTRACT, "modules"),
                     "dst": "raw/king-of-colosseum-2/jp/modules"}]})

    # --- B2: JP ISO, 8 pieces/commit (~792MB) ---
    for s in iso_commits("jp", JP_ISO, "raw/king-of-colosseum-2/jp",
                         "King-of-Colosseum-II-Japan.iso", SHA["jp"],
                         "King of Colosseum II (Japan).iso", 8, "B2",
                         850_000_000):
        write(s)

    # --- B3: v02ref ISO, 16 pieces/commit (~1.6GB) ---
    for s in iso_commits("v02", V02_ISO, "raw/king-of-colosseum-2/kactusken-v0.2",
                         "kactusken-v0.2-english.iso", SHA["v02ref"],
                         "kactusken-v0.2-english.iso", 16, "B3",
                         1_700_000_000):
        write(s)

    # --- B4a: iso/ small files + KC2FIRE.000/.001 splits ---
    iso_data = os.path.join(EXTRACT, "iso/DATA")
    splits = []
    for fn in ["KC2FIRE.000", "KC2FIRE.001"]:
        splits.append({
            "src": os.path.join(iso_data, fn),
            "dst_dir": "raw/king-of-colosseum-2/jp/iso/DATA", "dst_name": fn,
            "pieces": "all", "sha256": data_sha[fn],
            "original_name": fn, "manifest": True})
    write({"name": "B4a-iso-small",
           "message": "KoC2 raw: iso/ filesystem (small files) + KC2FIRE.000/.001\n\nExtracted JP ISO tree minus the >100MB files (those get their own\ncommits); KC2FIRE.000/.001 split with manifests.",
           "max_bytes": 3_000_000_000,
           "dirs": [{"src": os.path.join(EXTRACT, "iso"),
                     "dst": "raw/king-of-colosseum-2/jp/iso"}],
           "split_files": splits})

    # --- B4b: KC2FIRE.AFS whole (19 pieces, 1.8GB) ---
    for s in iso_commits("afs", os.path.join(iso_data, "KC2FIRE.AFS"),
                         "raw/king-of-colosseum-2/jp/iso/DATA", "KC2FIRE.AFS",
                         data_sha["KC2FIRE.AFS"], "KC2FIRE.AFS", 19, "B4b",
                         3_000_000_000):
        write(s)
    # --- B4c: HELLO.FOR + GOOD.BYE (11 pieces each, ~2.1GB) ---
    write({"name": "B4c-movies",
           "message": "KoC2 raw: HELLO.FOR + GOOD.BYE (SFD movies, split)",
           "max_bytes": 3_000_000_000,
           "split_files": [
               {"src": os.path.join(iso_data, "HELLO.FOR"),
                "dst_dir": "raw/king-of-colosseum-2/jp/iso/DATA",
                "dst_name": "HELLO.FOR", "pieces": "all",
                "sha256": data_sha["HELLO.FOR"], "original_name": "HELLO.FOR",
                "manifest": True},
               {"src": os.path.join(iso_data, "GOOD.BYE"),
                "dst_dir": "raw/king-of-colosseum-2/jp/iso/DATA",
                "dst_name": "GOOD.BYE", "pieces": "all",
                "sha256": data_sha["GOOD.BYE"], "original_name": "GOOD.BYE",
                "manifest": True}]})

    # --- B5: kc2fire000 + kc2fire001 (~811MB, 23.5K files) ---
    write({"name": "B5-fire01",
           "message": "KoC2 raw: kc2fire000/ + kc2fire001/ extracted contents",
           "max_bytes": 3_000_000_000,
           "dirs": [
               {"src": os.path.join(EXTRACT, "kc2fire000"),
                "dst": "raw/king-of-colosseum-2/jp/kc2fire000"},
               {"src": os.path.join(EXTRACT, "kc2fire001"),
                "dst": "raw/king-of-colosseum-2/jp/kc2fire001"}]})

    # --- B6: kc2fireafs (1.8GB, 9003 files) ---
    write({"name": "B6-fireafs",
           "message": "KoC2 raw: kc2fireafs/ extracted contents",
           "max_bytes": 3_000_000_000,
           "dirs": [{"src": os.path.join(EXTRACT, "kc2fireafs"),
                     "dst": "raw/king-of-colosseum-2/jp/kc2fireafs"}]})

    # --- B7: kc2firemvs + KC2FIRE-hybrid.000 ---
    write({"name": "B7-mvs-hybrid000",
           "message": "KoC2 raw: kc2firemvs/ + hybrid KC2FIRE.000 pack",
           "max_bytes": 3_000_000_000,
           "dirs": [{"src": os.path.join(EXTRACT, "kc2firemvs"),
                     "dst": "raw/king-of-colosseum-2/jp/kc2firemvs"}],
           "split_files": [{
               "src": HYB000, "dst_dir": "raw/king-of-colosseum-2/hybrid",
               "dst_name": "KC2FIRE-hybrid.000", "pieces": "all",
               "sha256": SHA["hybrid000"], "original_name": "KC2FIRE-hybrid.000",
               "manifest": True}]})


if __name__ == "__main__":
    main()
