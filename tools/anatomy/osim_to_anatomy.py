#!/usr/bin/env python3
"""Convert OpenSim .osim muscle-attachment tables to WH anatomy JSON.

Reads an OpenSim model file (.osim XML) and extracts every muscle's
attachment geometry plus Hill-type parameters:

  - origin / insertion / via path-points with parent bone + location
  - wrap objects (muscle path routing around bones)
  - Hill-type params: max_isometric_force, optimal_fiber_length,
    tendon_slack_length, pennation_angle_at_optimal,
    max_contraction_velocity

Output schema: wh.anatomy-muscles/1 (see
docs/research/ANATOMY-TISSUE-PHYSICS-2026-10-23.md). The sidecar feeds:
  1. tools/anatomy/generate_layers.py MUSCLE layer (origin/insertion drive
     the capsule endpoints instead of the procedural guesses)
  2. game/js vertex-shader muscle deformation (contraction math uses the
     Hill params: force scales with activation * force-length-velocity)

Source: opensim-org/opensim-models (Apache-2.0). Tested against
Gait2392 (Millard2012EquilibriumMuscle) and subject01 (Thelen2003Muscle).

Usage:
  python3 osim_to_anatomy.py --osim gait2392_millard2012muscle.osim \\
      --out gait2392_muscles.json [--model-name Gait2392]

Only stdlib + no numpy required (pure XML -> JSON pass).
"""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date

SCHEMA = "wh.anatomy-muscles/1"

MUSCLE_TAGS = {
    "Millard2012EquilibriumMuscle",
    "Millard2012AccelerationMuscle",
    "Thelen2003Muscle",
    "Schutte1993Muscle",
    "Delp1990Muscle",
    "Muscle",
}


def _text(elem, tag, default=None):
    child = elem.find(tag)
    if child is None or child.text is None:
        return default
    return child.text.strip()


def _floats(s):
    return [float(x) for x in s.split()]


def _side(name):
    if name.endswith("_r"):
        return "R"
    if name.endswith("_l"):
        return "L"
    return "C"


def _bone_from_socket(socket_text):
    # socket_parent_frame looks like "/bodyset/femur_r" -> "femur_r"
    if not socket_text:
        return "unknown"
    return socket_text.strip().strip("/").split("/")[-1]


def parse_muscle(elem):
    name = elem.get("name", "unnamed")
    path = elem.find("GeometryPath")
    points = []
    wraps = []
    if path is not None:
        pps = path.find("PathPointSet")
        if pps is not None:
            objs = pps.find("objects")
            if objs is not None:
                for pp in objs:
                    loc = _text(pp, "location")
                    if loc is None:
                        continue
                    points.append({
                        "bone": _bone_from_socket(_text(pp, "socket_parent_frame")),
                        "point": [round(v, 6) for v in _floats(loc)],
                    })
        pws = path.find("PathWrapSet")
        if pws is not None:
            objs = pws.find("objects")
            if objs is not None:
                for w in objs:
                    wraps.append({
                        "type": w.tag,
                        "name": w.get("name", ""),
                        "body": _bone_from_socket(_text(w, "socket_frame")),
                    })
    origin = points[0] if points else {"bone": "unknown", "point": [0, 0, 0]}
    insertion = points[-1] if len(points) > 1 else {"bone": "unknown", "point": [0, 0, 0]}
    via = points[1:-1] if len(points) > 2 else []

    def fnum(tag):
        t = _text(elem, tag)
        return float(t) if t is not None else None

    hill = {
        "max_isometric_force": fnum("max_isometric_force"),
        "optimal_fiber_length": fnum("optimal_fiber_length"),
        "tendon_slack_length": fnum("tendon_slack_length"),
        "pennation_angle": fnum("pennation_angle_at_optimal"),
        "max_contraction_velocity": fnum("max_contraction_velocity"),
    }
    return {
        "name": name,
        "type": elem.tag,
        "side": _side(name),
        "origin": origin,
        "insertion": insertion,
        "via": via,
        "wraps": wraps,
        "hill": hill,
    }


def convert(osim_path, model_name=None):
    tree = ET.parse(osim_path)
    root = tree.getroot()
    muscles = []
    for elem in root.iter():
        if elem.tag in MUSCLE_TAGS:
            muscles.append(parse_muscle(elem))
    return {
        "schema": SCHEMA,
        "generated": date.today().isoformat(),
        "source": {
            "tool": "OpenSim",
            "model": model_name or os.path.basename(osim_path),
            "file": os.path.basename(osim_path),
            "license": "Apache-2.0",
            "repo": "opensim-org/opensim-models",
        },
        "units": "meters",
        "conventions": {
            "up": "+Y (OpenSim default; matches three.js / WH bind pose)",
            "origin": "first path-point (P1), insertion: last path-point",
            "side": "name suffix _r/_l, else C",
        },
        "muscle_count": len(muscles),
        "muscles": muscles,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--osim", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model-name", default=None)
    a = ap.parse_args()
    doc = convert(a.osim, a.model_name)
    with open(a.out, "w") as f:
        json.dump(doc, f, indent=1)
    n_via = sum(1 for m in doc["muscles"] if m["via"])
    n_wrap = sum(1 for m in doc["muscles"] if m["wraps"])
    print(f"wrote {a.out}: {doc['muscle_count']} muscles, "
          f"{n_via} with via-points, {n_wrap} with wrap objects")


if __name__ == "__main__":
    main()
