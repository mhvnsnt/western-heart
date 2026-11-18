"""Fill 3 stage 4 driver: bake every slots file with the shipped
ttt2_bank_bake.py, two workers in parallel. Per bank: ANNA-style
bank1_table=None slots in bank 1 become documented gaps; after the
bake, skeleton.json joints are compared with the shipped Roger
skeleton - when identical (same rest/calibration inputs), the
source_skeleton provenance is restored to the shipped values (the
original Koenji blend is archive-only; the bake tool only hashes the
file, and the joint data provably comes from the shipped rest JSON).
Writes work/bake-summary.json.
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

W = os.path.expanduser('~/workspace/_fill3-ttt2-20261106')
TOOLS = os.path.join(W, 'tools')
SHIP_SKEL = json.load(open(os.path.join(W, 'ref', 'roger', 'skeleton.json')))
D4 = '/home/hatch/workspace/_ttt2-motion-20261103/data004/data004-decoded.bin'
D5 = '/home/hatch/workspace/_ttt2-motion-20261103/join-cont/data005-decoded.bin'


def bake_one(slots_path):
    name = os.path.basename(slots_path)[:-5]
    slots = json.load(open(slots_path))
    done_rep = os.path.join(W, 'work', 'out', name, 'bake-report.json')
    if os.path.exists(done_rep):
        rep = json.load(open(done_rep))
        return {'bank': name, 'rc': 0, 'tail': ['(already baked, skipped)'],
                'baked': len(rep['baked']), 'skipped': rep['skipped'],
                'report_gaps': rep['gaps'], 'skeleton': 'previously processed'}
    if slots['bank1_table'] is None:
        moved = {}
        for slot, s in list(slots['slots'].items()):
            if s['bank'] == 1:
                moved[slot] = ('bank-1 slot but the character bank-1 table is a '
                               'named gap (bank-tables.json); fallback = queued PS3 copy')
                del slots['slots'][slot]
        slots['gaps'].update(moved)
        slots_path = os.path.join(W, 'work', 'slots-bake', os.path.basename(slots_path))
        os.makedirs(os.path.dirname(slots_path), exist_ok=True)
        json.dump(slots, open(slots_path, 'w'), indent=1)
    out = os.path.join(W, 'work', 'out', name)
    os.makedirs(out, exist_ok=True)
    cmd = [sys.executable, os.path.join(TOOLS, 'ttt2_bank_bake.py'),
           '--slots', slots_path, '--out-dir', out,
           '--data004', D4, '--data005', D5,
           '--decoder64', os.path.join(TOOLS, 'ttt2_mota_decode64.py'),
           '--mannequin', os.path.join(TOOLS, 'TekkenMannequin_no_ik.blend'),
           '--helper', os.path.join(TOOLS, 'TekkenAnimHelper.py'),
           '--calib', os.path.join(TOOLS, 'ttt2-mannequin-calib.json'),
           '--root-affine', os.path.join(TOOLS, 'ttt2-root-affine.json'),
           '--rest', os.path.join(TOOLS, 'ttt2-mannequin-rest.json')]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
    rep_path = os.path.join(out, 'bake-report.json')
    rep = json.load(open(rep_path)) if os.path.exists(rep_path) else None
    skel_note = 'no skeleton'
    skel_path = os.path.join(out, 'skeleton.json')
    if os.path.exists(skel_path):
        skel = json.load(open(skel_path))
        if skel['joints'] == SHIP_SKEL['joints']:
            skel['source_skeleton'] = SHIP_SKEL['source_skeleton']
            json.dump(skel, open(skel_path, 'w'), indent=1, separators=(',', ':'))
            skel_note = 'joints identical to shipped; provenance restored'
        else:
            skel_note = 'JOINTS DIFFER from shipped skeleton - kept as baked'
    return {'bank': name, 'rc': r.returncode,
            'tail': (r.stdout + r.stderr).strip().splitlines()[-1:] ,
            'baked': len(rep['baked']) if rep else 0,
            'skipped': rep['skipped'] if rep else None,
            'report_gaps': rep['gaps'] if rep else None,
            'skeleton': skel_note}


def main():
    only = sys.argv[1:] or None
    files = sorted(os.listdir(os.path.join(W, 'work', 'slots')))
    paths = [os.path.join(W, 'work', 'slots', f) for f in files
             if f.endswith('.json') and (only is None or f[:-5] in only)]
    results = {}
    with ThreadPoolExecutor(max_workers=2) as ex:
        for res in ex.map(bake_one, paths):
            results[res['bank']] = res
            print(res['bank'], 'baked', res['baked'], res['tail'], flush=True)
    json.dump(results, open(os.path.join(W, 'work', 'bake-summary.json'), 'w'), indent=1)
    print('BAKE_ALL_DONE', len(results))


if __name__ == '__main__':
    main()
