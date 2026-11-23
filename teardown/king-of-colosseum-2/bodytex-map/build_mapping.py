#!/usr/bin/env python3
"""Build the KoC2 body-texture mapping for all 155 manifest wrestlers (variant 0).

Formula (proven by ELF tables at 0x32FC08/0x32FC58 + content verification):
  file(slot, part_id, sub) = base[slot] + count[slot]*part_id + sub
R/L pairs (knees/elbows/hands) share one interleaved block: R file = base_R + 2*id,
L file = base_L + 2*id (each ONE file; the "count 2" is the interleave stride).
"""
import json

SLOTS = {
    # slot: (category, base, count, dims per sub, roles)
    2:  ("chest",   9854, 4, ["128x128", "128x128", "64x64", "64x64"],
         ["torso front", "torso back", "R upper arm", "L upper arm"]),
    3:  ("waist",  11300, 3, ["128x128", "128x64", "128x64"],
         ["hips", "R thigh", "L thigh"]),
    4:  ("feet",   13007, 3, ["128x128", "128x128", "64x64"],
         ["R foot", "L foot", "heels (both)"]),
    5:  ("r_knee", 12491, 2, ["128x64"], ["R shin"]),
    6:  ("l_knee", 12492, 2, ["128x64"], ["L shin"]),
    7:  ("r_elbow", 10794, 2, ["64x64"], ["R forearm"]),
    8:  ("l_elbow", 10795, 2, ["64x64"], ["L forearm"]),
    9:  ("r_hand", 10898, 2, ["64x64"], ["R hand+fingers"]),
    10: ("l_hand", 10899, 2, ["64x64"], ["L hand+fingers"]),
    0:  ("face",    5136, 1, ["multi-pic TIM2"], ["face (already solved)"]),
    11: ("entrance_gear_type", 13412, 6, ["128x128"] * 6,
         ["entrance gear (out of scope for in-ring)"] * 6),
}

# TBP0 (from body .mdl, relative to model base 0x1a40) -> (part category, sub, sections)
TBP0_MAP = {
    0x1a44: ("waist", 0, [3, 7], "hips"),
    0x1a88: ("waist", 2, [4], "L thigh"),
    0x1b28: ("waist", 1, [8], "R thigh"),
    0x1aac: ("l_knee", 0, [5], "L shin"),
    0x1b4c: ("r_knee", 0, [9], "R shin"),
    0x1ad0: ("feet", 1, [6], "L foot"),
    0x1b70: ("feet", 0, [10], "R foot"),
    0x1b14: ("feet", 2, [6, 10], "heels (both feet)"),
    0x1bb4: ("chest", 0, [11, 12, 13, 26], "torso front (+neck sec39 on most bodies)"),
    0x1bf8: ("chest", 1, [11, 12, 13, 26], "torso back (+neck sec39 on some bodies e.g. 5664)"),
    0x1c3c: ("chest", 3, [14], "L upper arm"),
    0x1c78: ("chest", 2, [27], "R upper arm"),
    0x1c50: ("l_elbow", 0, [15], "L forearm"),
    0x1c8c: ("r_elbow", 0, [28], "R forearm"),
    0x1c64: ("l_hand", 0, list(range(16, 26)), "L hand+fingers"),
    0x1ca0: ("r_hand", 0, list(range(29, 39)), "R hand+fingers"),
}

def part_files(cat, pid):
    """Return {sub_index: file_id} for a part."""
    for slot, (c, base, count, dims, roles) in SLOTS.items():
        if c == cat:
            if cat in ("r_knee", "l_knee", "r_elbow", "l_elbow", "r_hand", "l_hand"):
                return {0: base + 2 * pid}
            if cat == "face":
                return {0: base + pid}
            return {s: base + count * pid + s for s in range(count)}
    raise KeyError(cat)

def main():
    manifest = json.load(open('/home/hatch/workspace/creator-koc2-renders/manifest.json'))
    db = json.load(open('/home/hatch/workspace/koc2-vpw2-moveside/work/koc2-rosterdb.json'))
    by_id = {w['id']: w for w in db['wrestlers']}
    out = {
        "formula": "file = base[slot] + count[slot]*part_id + sub; R/L pairs (knee/elbow/hand) are 1 file each: R = base_R + 2*id, L = base_L + 2*id",
        "archive": "KC2FIRE.001 (file ids below); raw files at https://raw.githubusercontent.com/mhvnsnt/western-heart/muse/koc2-raw/raw/king-of-colosseum-2/jp/kc2fire001/file%05d.bin",
        "decode": "tim2.py png <file> <out_prefix>  (~/workspace/koc2-vpw2-moveside/sources/koc2/github-kactusken/tools/tim2.py)",
        "slots": {str(s): {"category": c, "base": b, "count": n, "dims": d, "roles": r}
                  for s, (c, b, n, d, r) in sorted(SLOTS.items())},
        "tbp0_map": {hex(k): {"part": v[0], "sub": v[1], "sections": v[2], "name": v[3]}
                     for k, v in sorted(TBP0_MAP.items())},
        "caveats": [
            "Within-group L/R (waist subs 1/2, feet subs 0/1, chest subs 2/3) follows the R-before-L file convention (same as the R/L slot bases: R base < L base). Verify on the first color render; swap if a design reads mirrored.",
            "Sec 39 (neck) uses the chest FRONT texture (0x1bb4) on most bodies but the BACK (0x1bf8) on at least one (file 5664, Liger). Read sec 39's TBP0 from each body .mdl.",
            "Chest-detail -> upper-arm and elbow -> forearm assignments are by elimination + outfit-pairing evidence (Liger suit / Chairman suit pair chest+elbow suit parts); confirm on the first color render.",
            "The ELF index function 0x107ea8 returns base+id (its mult by count is dead in that function); the content-proven on-disk layout is base+id*count. A later stage presumably expands it; the mapping itself is verified by decoded content, not by the loader trace.",
        ],
        "wrestlers": [],
    }
    for m in manifest:
        w = by_id[m['koc2_id']]
        app = w['variants'][0]['appearance']
        parts = {}
        for cat in ("chest", "waist", "feet", "r_knee", "l_knee", "r_elbow", "l_elbow", "r_hand", "l_hand"):
            p = app[cat]
            parts[cat] = {"id": p['id'], "name_en": p.get('en'), "files": part_files(cat, p['id'])}
        parts['face'] = {"id": app['face']['id'], "name_en": app['face'].get('en'),
                         "files": part_files("face", app['face']['id'])}
        out['wrestlers'].append({
            "roster_id": m['roster_id'], "name": m['name'], "koc2_id": m['koc2_id'],
            "body_file": m['body_file'], "body_type": m['body_type'],
            "body_size": m['body_size'], "special_gear": m['special_gear'],
            "parts": parts,
        })
    json.dump(out, open('mapping.json', 'w'), indent=1, ensure_ascii=False)
    print(f"wrote mapping.json: {len(out['wrestlers'])} wrestlers")
    # sanity: Nakamura + Liger spot check
    for r in out['wrestlers']:
        if r['name'] in ('Shinsuke Nakamura', 'Jushin Thunder Liger'):
            print(r['name'], 'chest files:', r['parts']['chest']['files'],
                  'waist:', r['parts']['waist']['files'],
                  'feet:', r['parts']['feet']['files'],
                  'r_knee:', r['parts']['r_knee']['files'],
                  'l_knee:', r['parts']['l_knee']['files'],
                  'r_hand:', r['parts']['r_hand']['files'],
                  'r_elbow:', r['parts']['r_elbow']['files'])

if __name__ == '__main__':
    main()
