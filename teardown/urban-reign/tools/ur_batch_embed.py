#!/usr/bin/env python3
"""Batch: embed each pmotNNN per-character bank into that character's
game GLB (per-character isolation) and write its native moveset JSON.

Usage: ur_batch_embed.py <motion-packs dir> <street-reign glb dir> <movesets dir>
Only characters WITH a pmot bank are touched; all others stay proxy
(their status is recorded in ur-native-index.json with the reason).
"""
import json, os, sys
sys.path.insert(0, '/home/hatch/workspace/ur-phase2-work/tools')
from ur_embed import embed
from ur_gyu import Bank, load_tables

def main(packs_dir, glb_dir, moveset_dir):
    index = {}
    for fn in sorted(os.listdir(packs_dir)):
        if not (fn.startswith('pmot') and fn.endswith('.ppk')): continue
        num = fn[4:7]
        char = f'char{num}'
        ppk = open(os.path.join(packs_dir, fn), 'rb').read()
        gyu_path = f'/tmp/_pmot{num}.gyu'
        open(gyu_path, 'wb').write(ppk[0x80:])
        glb = os.path.join(glb_dir, f'{char}.glb')
        if not os.path.exists(glb):
            index[char] = {'status': 'missing-glb'}
            continue
        embed(gyu_path, glb, glb)
        bank = Bank(gyu_path)
        clips = []
        for mi in range(bank.n_motions):
            trs = bank.tracks(mi)
            nframes = max((t.nkeys - 1) * t.fpk for t in trs) + 1
            clips.append({'name': f'ur_m{mi:03d}', 'motion': mi,
                          'frames': nframes, 'duration_s': round(nframes / 60, 3)})
        ms = {'schema': 2, 'fighter': f'ur-{char}', 'proxy': False,
              'animationSource': f'{fn} native .gyu bank (per-character)',
              'movesSource': 'engine-base (proxy) - movelist name mapping pending pmotID correlation',
              'bank': fn, 'motions': bank.n_motions, 'clips': clips}
        with open(os.path.join(moveset_dir, f'ur-{char}.json'), 'w') as f:
            json.dump(ms, f, indent=1)
        index[char] = {'status': 'native', 'bank': fn, 'motions': bank.n_motions}
    allchars = [f'char{i:03d}' for i in range(1, 73)]
    for c in allchars:
        if c not in index:
            index[c] = {'status': 'proxy',
                        'reason': 'no per-character pmot bank in the AFS set; general-pool banks converted separately (shared data, not per-character)'}
    with open(os.path.join(moveset_dir, 'ur-native-index.json'), 'w') as f:
        json.dump({'schema': 1, 'fighters': index}, f, indent=1)
    nat = sum(1 for v in index.values() if v['status'] == 'native')
    print(f'native {nat} / proxy {len(index) - nat}')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
