#!/usr/bin/env python3
"""Convert MyoSuite (MuJoCo) muscle/tendon XMLs to WH anatomy JSON.

MyoSuite ships its musculoskeletal models as MuJoCo XML: muscle actuators
in *_muscle.xml, tendon routing in *_tendon.xml, attachment sites parented
under bodies in *_chain.xml. This extracts every muscle's attachment
geometry plus Hill-type contraction parameters:

  - origin / insertion / via sites with parent bone + position
  - wrap geoms (muscle path routing around bones)
  - Hill-type params from the MuJoCo muscle parametrization
    (gainprm = range(2), force, scale, lmin, lmax, vmax, fpmax, fvmax;
     per the MuJoCo XML reference, actuator/muscle)

Coordinate conversion: MuJoCo is Z-up; WH / three.js is Y-up, so every
point is rotated (x, y, z) -> (x, z, -y) (handedness-preserving).

Output schema: wh.anatomy-muscles/1 (same as osim_to_anatomy.py) so both
sources feed the same consumers:
  1. tools/anatomy/generate_layers.py MUSCLE layer (origin/insertion drive
     the capsule endpoints instead of the procedural guesses)
  2. game/js vertex-shader muscle deformation (contraction math uses the
     Hill params: force scales with activation * force-length-velocity)

Source: MyoHub/myosuite + myo-sim pip package (Apache-2.0). Tested against
myo-sim 0.2.3 (346 muscles across leg/arm/torso).

Usage:
  python3 myosuite_to_anatomy.py --model-dir myo_sim/models \\
      --out myosuite_muscles.json
  # processes */assets/*_{muscle,tendon,chain}.xml under --model-dir

Only stdlib required (pure XML -> JSON pass).
"""
import argparse
import glob
import json
import os
import xml.etree.ElementTree as ET
from datetime import date

SCHEMA = "wh.anatomy-muscles/1"

# MuJoCo muscle gainprm layout (XML reference, actuator/muscle):
# range(2), force, scale, lmin, lmax, vmax, fpmax, fvmax
_GAIN_FIELDS = ["range0", "range1", "force", "scale", "lmin", "lmax",
                "vmax", "fpmax", "fvmax"]


def zup_to_yup(p):
    x, y, z = p
    return [x, z, -y]


def _floats(s):
    return [float(x) for x in s.split()]


def _side(name):
    if name.endswith("_r"):
        return "R"
    if name.endswith("_l"):
        return "L"
    return "C"


def load_sites(chain_path):
    """Map site name -> (body name, y-up position). Sites are nested under
    <body> elements; the nearest ancestor body owns the site."""
    tree = ET.parse(chain_path)
    sites = {}

    def walk(elem, body):
        if elem.tag == "body" and elem.get("name"):
            body = elem.get("name")
        for child in elem:
            if child.tag == "site" and child.get("name"):
                pos = child.get("pos")
                sites[child.get("name")] = {
                    "bone": body or "unknown",
                    "point": [round(v, 6) for v in zup_to_yup(_floats(pos))]
                    if pos else [0.0, 0.0, 0.0],
                }
            walk(child, body)

    walk(tree.getroot(), None)
    return sites


def load_tendons(tendon_path):
    """Map tendon name -> ordered path: [{'site': name} | {'wrap': geom}]."""
    tree = ET.parse(tendon_path)
    tendons = {}
    for spatial in tree.iter("spatial"):
        name = spatial.get("name")
        path = []
        for child in spatial:
            if child.tag == "site" and child.get("site"):
                path.append({"site": child.get("site")})
            elif child.tag == "geom":
                path.append({"wrap": child.get("geom", ""),
                             "sidesite": child.get("sidesite", "")})
        tendons[name] = path
    return tendons


def parse_gainprm(s):
    vals = _floats(s) if s else []
    out = {}
    for i, field in enumerate(_GAIN_FIELDS):
        out[field] = vals[i] if i < len(vals) else None
    if len(vals) > len(_GAIN_FIELDS):
        out["extra"] = vals[len(_GAIN_FIELDS):]
    return out


def convert_part(muscle_path, tendon_path, chain_path, part):
    sites = load_sites(chain_path)
    tendons = load_tendons(tendon_path)
    tree = ET.parse(muscle_path)
    muscles = []
    for gen in tree.iter("general"):
        cls = gen.get("class", "")
        if "muscle" not in cls:
            continue
        name = gen.get("name", "unnamed")
        tendon_name = gen.get("tendon", "")
        tpath = tendons.get(tendon_name, [])
        site_names = [p["site"] for p in tpath if "site" in p]
        wraps = [{"geom": p["wrap"], "sidesite": p["sidesite"]}
                 for p in tpath if "wrap" in p]
        pts = [sites.get(s, {"bone": "unknown", "point": [0.0, 0.0, 0.0]})
               for s in site_names]
        missing = [s for s, p in zip(site_names, pts)
                   if p["bone"] == "unknown"]
        origin = pts[0] if pts else {"bone": "unknown", "point": [0, 0, 0]}
        insertion = pts[-1] if len(pts) > 1 else {"bone": "unknown",
                                                 "point": [0, 0, 0]}
        gain = parse_gainprm(gen.get("gainprm", ""))
        lr = gen.get("lengthrange", "")
        muscles.append({
            "name": name,
            "part": part,
            "type": "MuJoCo-muscle",
            "side": _side(name),
            "origin": origin,
            "insertion": insertion,
            "via": pts[1:-1] if len(pts) > 2 else [],
            "wraps": wraps,
            "tendon": tendon_name,
            "unresolved_sites": missing,
            "hill": {
                # MuJoCo muscle gainprm: force = peak isometric force (N)
                "max_isometric_force": gain.get("force"),
                "lengthrange_m": [round(v, 6) for v in _floats(lr)] if lr else None,
                "norm_length_range": [gain.get("range0"), gain.get("range1")],
                "scale": gain.get("scale"),
                "lmin": gain.get("lmin"),
                "lmax": gain.get("lmax"),
                "max_contraction_velocity": gain.get("vmax"),
                "fpmax": gain.get("fpmax"),
                "fvmax": gain.get("fvmax"),
            },
        })
    return muscles


def find_parts(model_dir):
    """Find (muscle, tendon, chain) triples under <model-dir>/*/assets/."""
    parts = {}
    for mp in glob.glob(os.path.join(model_dir, "*", "assets", "*_muscle.xml")):
        base = mp[:-len("_muscle.xml")]
        tp = base + "_tendon.xml"
        cp = base + "_chain.xml"
        if not os.path.exists(cp):
            # e.g. myotorso_abdomen_*: no dedicated chain file; fall back to
            # any chain file in the same assets dir (shared body frames)
            sibs = sorted(glob.glob(os.path.join(os.path.dirname(mp),
                                                 "*_chain.xml")))
            cp = sibs[0] if sibs else cp
        if os.path.exists(tp) and os.path.exists(cp):
            part = os.path.basename(os.path.dirname(os.path.dirname(mp)))
            parts.setdefault(part, []).append((mp, tp, cp))
    return parts


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model-dir", required=True,
                    help="myo_sim/models dir (contains leg/ arm/ torso/ ...)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    all_muscles = []
    parts = find_parts(a.model_dir)
    for part in sorted(parts):
        for mp, tp, cp in parts[part]:
            ms = convert_part(mp, tp, cp, part)
            all_muscles.extend(ms)
            print(f"  {part}: {os.path.basename(mp)} -> {len(ms)} muscles")

    doc = {
        "schema": SCHEMA,
        "generated": date.today().isoformat(),
        "source": {
            "tool": "MyoSuite",
            "model": "myo_sim full-body parts (leg/arm/torso)",
            "license": "Apache-2.0",
            "repo": "MyoHub/myosuite (+ myo-sim pip package)",
        },
        "units": "meters",
        "conventions": {
            "up": "+Y (converted from MuJoCo Z-up: (x,y,z)->(x,z,-y))",
            "origin": "first tendon site, insertion: last tendon site",
            "side": "name suffix _r/_l, else C",
            "hill": "MuJoCo muscle gainprm: range(2), force, scale, lmin, "
                    "lmax, vmax, fpmax, fvmax",
        },
        "muscle_count": len(all_muscles),
        "muscles": all_muscles,
    }
    with open(a.out, "w") as f:
        json.dump(doc, f, indent=1)
    n_unresolved = sum(len(m["unresolved_sites"]) for m in all_muscles)
    print(f"wrote {a.out}: {doc['muscle_count']} muscles, "
          f"{n_unresolved} unresolved site refs")


if __name__ == "__main__":
    main()
