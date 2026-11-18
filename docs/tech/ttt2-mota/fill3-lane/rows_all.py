"""Fill 3 stage 5 driver: rows.pack.json + hit_frames.json for every
baked bank via the generalized ttt2_bank_rows_gen.py. Two banks in
parallel, --jobs 2 each. Skips banks whose rows report already exists.
Writes work/rows-summary.json.
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

W = os.path.expanduser('~/workspace/_fill3-ttt2-20261106')
TOOLS = os.path.join(W, 'tools')
D4 = '/home/hatch/workspace/_ttt2-motion-20261103/data004/data004-decoded.bin'
D5 = '/home/hatch/workspace/_ttt2-motion-20261103/join-cont/data005-decoded.bin'
D6 = '/home/hatch/workspace/_ttt2-motion-20261103/join-cont/data006-decoded.bin'

# bank stem -> (bracket char name, body_kmd)
BANKS = {}
for f in sorted(os.listdir(os.path.join(W, 'work', 'joins-final'))):
    j = json.load(open(os.path.join(W, 'work', 'joins-final', f)))
    char = j['character'].split(' (')[0]
    stem = f[:-len('-join.json')]
    BANKS[stem] = (char, char)


def run_one(stem):
    char, kmd = BANKS[stem]
    slots = json.load(open(os.path.join(W, 'work', 'slots', stem + '.json')))
    out_dir = os.path.join(W, 'work', 'out', stem)
    rep = os.path.join(W, 'work', 'rows-reports', stem + '.json')
    os.makedirs(os.path.dirname(rep), exist_ok=True)
    if os.path.exists(rep):
        r = json.load(open(rep))
        return {'bank': stem, 'rc': 0, 'pack_rows': r['pack_rows'], 'hit_rows': r['hit_rows'],
                'tail': ['(already done, skipped)']}
    label = stem + '_ttt2' if stem in {'anna', 'bosconovitch', 'bryan', 'eddy',
                                       'heihachi', 'hwoarang', 'jin', 'julia',
                                       'kuma', 'law', 'nina', 'ogre', 'paul',
                                       'raven', 'yoshimitsu'} else stem
    cmd = [sys.executable, os.path.join(TOOLS, 'ttt2_bank_rows_gen.py'),
           '--bank', label, '--char', char, '--body-kmd', kmd,
           '--offsets', os.path.join(W, 'work', 'record-offsets.json'),
           '--join', os.path.join(W, 'work', 'joins-final', stem + '-join.json'),
           '--bank-dir', out_dir, '--fighter', stem,
           '--out-dir', out_dir, '--report', rep,
           '--write-move-rows', '--jobs', '2',
           '--data004', D4, '--data005', D5, '--data006', D6,
           '--decoder64', os.path.join(TOOLS, 'ttt2_mota_decode64.py'),
           '--calib', os.path.join(TOOLS, 'ttt2-mannequin-calib.json'),
           '--root-affine', os.path.join(TOOLS, 'ttt2-root-affine.json'),
           '--rest', os.path.join(TOOLS, 'ttt2-mannequin-rest.json')]
    if slots['bank1_table'] is not None:
        cmd += ['--bank1-table', str(slots['bank1_table'])]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
    tail = (r.stdout + r.stderr).strip().splitlines()[-1:]
    repj = json.load(open(rep)) if os.path.exists(rep) else {}
    return {'bank': stem, 'rc': r.returncode, 'tail': tail,
            'pack_rows': repj.get('pack_rows'), 'hit_rows': repj.get('hit_rows')}


def main():
    only = sys.argv[1:] or None
    stems = [s for s in sorted(BANKS)
             if (only is None or s in only)
             and os.path.exists(os.path.join(W, 'work', 'slots', s + '.json'))
             and os.path.exists(os.path.join(W, 'work', 'out', s, 'bake-report.json'))]
    results = {}
    with ThreadPoolExecutor(max_workers=2) as ex:
        for res in ex.map(run_one, stems):
            results[res['bank']] = res
            print(res['bank'], res.get('pack_rows'), res.get('hit_rows'), res['tail'], flush=True)
    json.dump(results, open(os.path.join(W, 'work', 'rows-summary.json'), 'w'), indent=1)
    print('ROWS_ALL_DONE', len(results))


if __name__ == '__main__':
    main()
