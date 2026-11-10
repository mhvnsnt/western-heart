#!/usr/bin/env python3
"""t7_graph_bake.py: batch-bake EVERY animation clip a fighter's imported T7 graph reaches (t7_graph_import.py
--coverage reachable_clips), through the same community path as every other in-game T7 clip
(tools/anim/t7_c8_stance_bake.py: 0x64 clips via the game's own sampler when T7_EXE is set, Kiloutre's applier on
Koenji's mannequin, FK self-check). Resumable + cached: one file per source clip, <bank>_<clip>.json in --cache; a clip
whose file exists is never re-baked (re-running continues where it stopped). Failures are recorded, never substituted.
usage: T7_EXE=<exe> python3 tools/anim/t7_graph_bake.py --graph game/assets/anim/t7/king/graph.json \
         --coverage game/assets/anim/t7/king/graph.coverage.json --mothead <mothead> --code kin \
         --mannequin <blend> --helper <py> --blender <blender> --cache <dir> [--limit N]"""
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ARC = {'rotsm': 'mask/{code}rotsm.arc', 'motbin': 'bin/{code}mot.bin', 'common': 'mask/common.arc'}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ('--graph', '--coverage', '--mothead', '--code', '--mannequin', '--helper', '--blender', '--cache'):
        ap.add_argument(k, required=True)
    ap.add_argument('--character', default='King (Tekken 7)'); ap.add_argument('--fighter', default='pantera')
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    g = json.load(open(a.graph)); cov = json.load(open(a.coverage))
    os.makedirs(a.cache, exist_ok=True)
    logp = os.path.join(a.cache, 'bake-log.jsonl')
    by_clip = {}
    for mid in cov['reachable_moves']:
        m = g['moves'][mid]; by_clip.setdefault((m['bank'], m['clip']), m)
    done = fail = skip = 0
    for (bank, clip), m in sorted(by_clip.items(), key=str):
        if bank not in ARC or clip is None or m['fmt'] not in ('0x64', '0xC8'):
            skip += 1; continue
        name = '%s_%d' % (bank, clip); out = os.path.join(a.cache, name + '.json')
        if os.path.exists(out): skip += 1; continue
        if a.limit and done + fail >= a.limit: break
        cmd = [sys.executable, os.path.join(HERE, 't7_c8_stance_bake.py'), '--arc',
               os.path.join(a.mothead, ARC[bank].format(code=a.code)), '--clip', str(clip), '--anim', m['anim'],
               '--moves', m['name'], '--character', a.character, '--fighter', a.fighter, '--mannequin', a.mannequin,
               '--helper', a.helper, '--blender', a.blender, '--out-dir', a.cache, '--name', name]
        t = time.time(); p = subprocess.run(cmd, capture_output=True, text=True)
        rec = {'clip': name, 'move': m['name'], 'anim': m['anim'], 'fmt': m['fmt'], 'ok': p.returncode == 0,
               'sec': round(time.time() - t, 2), 'msg': (p.stdout.strip() or p.stderr.strip())[-300:]}
        open(logp, 'a').write(json.dumps(rec) + '\n')
        if p.returncode == 0: done += 1
        else: fail += 1
    print('GRAPH_BAKE', 'baked', done, 'failed', fail, 'cached/skipped', skip, 'unique', len(by_clip))


if __name__ == '__main__':
    main()
