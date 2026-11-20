#!/usr/bin/env python3
"""tools/portraits/record_facing.py: record which way models' meshes face in game/assets/models/model-facing.json.

The game assumes a mesh faces +Z. assets.js turns a '-Z' model a half turn and a '+X' / '-X' model a quarter turn
(facingYaw) when it creates the instance that both the select card and the fight use. An unlisted model falls back
to a feet cue that only tells +Z from -Z, so a sideways (+X) mesh is never turned: its card shows a profile and it
fights side-on.

Read the facing BY EYE first (tools/portraits/facing_probe.mjs, rest pose, camera at yaw 0/90/180/270: the yaw that
shows the face is the facing; 90 = +X, 270 = -X, 180 = -Z). Then record it here with the evidence:

    python3 tools/portraits/record_facing.py --facing +X --ids bf-bannon,bf-titan \\
        --why "rest renders: face at yaw 90, back at yaw 270" --proof docs/proof/<date>/<dir>/sheet.png

The file is rewritten in its own JSON layout (byte-identical apart from the new entries). An existing record is
only replaced with --replace.
"""
import argparse
import json
import os
import sys

FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                    'game/assets/models/model-facing.json')


def layout(data, raw):
    for ind in (2, 1, 4):
        for ea in (True, False):
            for nl in ('\n', ''):
                if json.dumps(data, indent=ind, ensure_ascii=ea) + nl == raw:
                    return ind, ea, nl
    raise SystemExit('cannot reproduce %s byte for byte; refusing to rewrite it' % FILE)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--facing', required=True, choices=['+Z', '-Z', '+X', '-X'])
    ap.add_argument('--ids', required=True)
    ap.add_argument('--why', required=True)
    ap.add_argument('--proof', required=True)
    ap.add_argument('--date', default='2026-11-11')
    ap.add_argument('--replace', action='store_true')
    a = ap.parse_args()
    raw = open(FILE, encoding='utf-8').read()
    data = json.loads(raw)
    fmt = layout(data, raw)
    models, notes = data['models'], data.setdefault('corrections', {})
    changed = []
    for i in [x for x in a.ids.split(',') if x]:
        if i in models and not a.replace:
            sys.exit('%s already recorded as %s (use --replace)' % (i, models[i]))
        models[i] = a.facing
        notes[i] = '%s: unlisted -> %s. %s Proof: %s.' % (a.date, a.facing, a.why, a.proof)
        changed.append(i)
    open(FILE, 'w', encoding='utf-8').write(json.dumps(data, indent=fmt[0], ensure_ascii=fmt[1]) + fmt[2])
    print('recorded %s for %d models: %s' % (a.facing, len(changed), ', '.join(changed)))


if __name__ == '__main__':
    main()
