#!/usr/bin/env python3
"""Extract .npy animation banks for the five AKI N64 games.

Reads each ROM in place via aki_extract.AKIRom, decodes every anim in
that game's *-anims.json manifest with aki_npy.decode_anim (validated
byte-exact against the VPW2 bank), and writes:
  banks/<game>/clips/anim_XXXX.npy
  banks/<game>/manifest.json   {clips: [{file_id, anim_id, frames}]}
  banks/<game>/extract-report.json
anim_id = fid - first_move_anim (None for pre-move anims like stances).
Resume-safe: existing .npy files are skipped unless --force.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/home/hatch/workspace/bannon-tier0-moves/aki-n64-five')
import numpy as np
from aki_extract import AKIRom, GAMES
from aki_npy import decode_anim

WORK = os.path.dirname(os.path.abspath(__file__))
FIVE = '/home/hatch/workspace/bannon-tier0-moves/aki-n64-five'
ROMS = {
    'nomercy': '/home/hatch/workspace/no-mercy-rom/WWF No Mercy (USA) (Rev-A).z64',
    'wm2k': FIVE + '/WWF WrestleMania 2000 (U) (V1.2).z64',
    'worldtour': FIVE + '/WCW vs. nWo - World Tour (USA) (Rev-A).z64',
    'revenge': '/home/hatch/workspace/vpw2-hidden25-renders/roms/WCW-nWo Revenge (Unlocked).z64',
    'vpw64': '/home/hatch/workspace/vpw2-hidden25-renders/roms/Virtual Pro Wrestling 64 (Japan).z64',
}


def extract_game(game, force=False):
    rom = AKIRom(game, ROMS[game])
    man = json.load(open(f'{FIVE}/{game}-anims.json'))
    anims = man['anims']
    outdir = os.path.join(WORK, 'banks', game, 'clips')
    os.makedirs(outdir, exist_ok=True)
    cfg = GAMES[game]
    report = {'game': game, 'rom': os.path.basename(ROMS[game]),
              'manifest_anims': len(anims), 'extracted': 0, 'skipped': 0,
              'failed': [], 'frames_total': 0}
    clips_meta = []
    for a in anims:
        fid = int(a['fid'], 16)
        name = f'anim_{fid:04X}.npy'
        path = os.path.join(outdir, name)
        if os.path.exists(path) and not force:
            report['skipped'] += 1
            clips_meta.append({'file_id': f'0x{fid:04X}',
                               'anim_id': (fid - cfg['first_move_anim']
                                           if fid >= cfg['first_move_anim'] else None),
                               'frames': a['frames']})
            report['frames_total'] += a['frames']
            continue
        try:
            data = rom.get(fid)
            arr = decode_anim(data)
        except Exception as e:
            report['failed'].append({'fid': f'0x{fid:04X}',
                                     'label': a.get('label', ''),
                                     'error': f'{type(e).__name__}: {e}'})
            continue
        np.save(path, arr)
        report['extracted'] += 1
        report['frames_total'] += arr.shape[0]
        clips_meta.append({'file_id': f'0x{fid:04X}',
                           'anim_id': (fid - cfg['first_move_anim']
                                       if fid >= cfg['first_move_anim'] else None),
                           'frames': int(arr.shape[0])})
        if (report['extracted'] + report['skipped']) % 1000 == 0:
            print(f'{game}: {report["extracted"] + report["skipped"]}/{len(anims)}', flush=True)
    json.dump({'clips': clips_meta},
              open(os.path.join(WORK, 'banks', game, 'manifest.json'), 'w'))
    json.dump(report, open(os.path.join(WORK, 'banks', game,
                                        'extract-report.json'), 'w'), indent=1)
    print(f'{game}: extracted {report["extracted"]}, skipped {report["skipped"]}, '
          f'failed {len(report["failed"])}, frames {report["frames_total"]}')
    for f in report['failed'][:10]:
        print('  FAIL', f)
    return report


if __name__ == '__main__':
    games = sys.argv[1:] or list(ROMS)
    force = '--force' in games
    games = [g for g in games if g != '--force']
    for g in games:
        extract_game(g, force=force)
