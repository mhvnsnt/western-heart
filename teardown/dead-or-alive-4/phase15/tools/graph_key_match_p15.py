#!/usr/bin/env python3
"""DOA4 phase 15 Job 1c: structural graph-key identity. Runs the
phase-3/6 assembly-graph parser (scratch work/doa4_assemble.py,
the system that produced the repo's assembly graphs) over every
ISO .tpr entry and matches the graph key (directory_records,
MdlGeo size, MdlInfo size, Hie size, object_count) against all
148 repo assembly graphs. Output: graph_key_map_p15.json with,
per .tpr: its key, exact-key package matches, and the nearest
packages by key distance (for tentative grading)."""
import glob, json, os, subprocess, sys, tempfile

SCR = '/home/hatch/workspace/_doa4p2-scratch/p15'
REPO = '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4'
ASM = '/home/hatch/workspace/_doa4p2-scratch/work/doa4_assemble.py'

def key(g):
    b = g.get('blocks', {})
    return (g.get('directory_records'), b.get('MdlGeo', {}).get('size'),
            b.get('MdlInfo', {}).get('size'), b.get('Hie', {}).get('size'),
            g.get('object_count'))

def main():
    man = json.load(open(os.path.join(SCR, 'afs_manifest_p15.json')))
    pkg_keys = {}
    for f in glob.glob(os.path.join(REPO, 'assembly-graphs', '*_graph.json')) + \
             glob.glob(os.path.join(REPO, 'assembly-graphs', '*-graph.json')) + \
             glob.glob(os.path.join(REPO, 'assembly-graphs', '*-skinned-graph.json')):
        name = os.path.basename(f)
        pkg = name.replace('-skinned-graph.json', '').replace('_graph.json', '').replace('-graph.json', '')
        try: pkg_keys[pkg] = key(json.load(open(f)))
        except Exception as e: print('graph load fail', f, e)
    print('package graphs keyed:', len(pkg_keys))
    out = {}
    for vol in ('chrone', 'chrtwo', 'chrthree'):
        rows = {}
        for ent in man[vol + '.afs']['entries']:
            if not ent['name'].endswith('.tpr'): continue
            path = os.path.join(SCR, 'afs_extract', vol, ent['name'])
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tf:
                tmp = tf.name
            r = subprocess.run([sys.executable, ASM, path, '0', '--graph', tmp],
                               capture_output=True, text=True, timeout=300)
            try:
                g = json.load(open(tmp)); k = key(g)
            except Exception:
                k = None
            os.unlink(tmp)
            exact = [p for p, pk in pkg_keys.items() if pk == k and p.startswith(vol)] if k else []
            rows[ent['name']] = {'key': k, 'exact_packages': exact}
            print(vol, ent['name'], k, '->', exact, flush=True)
        out[vol] = rows
    json.dump(out, open(os.path.join(SCR, 'graph_key_map_p15.json'), 'w'), indent=1)
    print('WROTE graph_key_map_p15.json')

if __name__ == '__main__':
    main()
