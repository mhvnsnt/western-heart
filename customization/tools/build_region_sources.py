#!/usr/bin/env python3
"""Build customization/region-sources.json — the Creation Suite piece-swap
source index: every roster attire GLB a region can be cut FROM.

Sources are enumerated from `git ls-tree` (authoritative, works in sparse
checkouts); when a GLB is present on disk it is enriched from its JSON
chunk (skinned? bone count? meshopt/quantized?) — enrichment fills in on a
full checkout, everything else stays null and the bake inspects at import.

Usage: python3 customization/tools/build_region_sources.py [--repo-root .]
"""
import json, os, struct, subprocess, sys

def glb_json(path):
    with open(path, 'rb') as f:
        head = f.read(20)
        if len(head) < 20 or head[:4] != b'glTF':
            return None
        clen = struct.unpack('<I', head[12:16])[0]
        return json.loads(f.read(clen))

def enrich(path):
    g = glb_json(path)
    if not g:
        return {}
    nodes = g.get('nodes', [])
    skins = g.get('skins', [])
    bones = []
    if skins:
        bones = [nodes[j].get('name') for j in skins[0].get('joints', [])]
    return {
        'skinned': bool(skins),
        'bones': len(bones),
        'extensions': g.get('extensionsUsed', []),
        'meshes': len(g.get('meshes', [])),
    }

def main():
    root = '.'
    if '--repo-root' in sys.argv:
        root = sys.argv[sys.argv.index('--repo-root') + 1]
    root = os.path.abspath(root)
    entries = []
    try:
        out = subprocess.run(['git', 'ls-tree', '-r', '-l', 'HEAD', 'roster/'],
                             cwd=root, capture_output=True, text=True, check=True,
                             timeout=120).stdout
        for line in out.splitlines():
            meta, path = line.split('\t', 1)
            parts = meta.split()
            if not path.lower().endswith('.glb'):
                continue
            entries.append({'path': path, 'bytes': int(parts[3])})
    except Exception:
        entries = []
    if not entries:
        # Fallback: the GitHub trees API (local object stores can be too
        # contended for ls-tree on the full roster tree).
        try:
            raw = subprocess.run(['gh', 'api', 'repos/mhvnsnt/western-heart/git/trees/main:roster?recursive=1'],
                                 capture_output=True, text=True, check=True, timeout=180).stdout
            tree = json.loads(raw)
            if not tree.get('truncated'):
                for t in tree.get('tree', []):
                    if t.get('type') == 'blob' and t['path'].lower().endswith('.glb'):
                        entries.append({'path': 'roster/' + t['path'],
                                        'bytes': int(t.get('size', 0))})
        except Exception:
            entries = []
    if not entries:
        entries = []
        for dirpath, _dirs, files in os.walk(os.path.join(root, 'roster')):
            for fn in files:
                if fn.lower().endswith('.glb'):
                    p = os.path.join(dirpath, fn)
                    entries.append({'path': os.path.relpath(p, root),
                                      'bytes': os.path.getsize(p)})
    sources = []
    for e in sorted(entries, key=lambda x: x['path']):
        rel = e['path'].replace(os.sep, '/')
        seg = rel.split('/')
        rec = {
            'path': rel,
            'fighter': seg[1] if len(seg) > 3 else None,
            'attire': seg[3] if len(seg) > 4 else None,
            'file': seg[-1],
            'bytes': e['bytes'],
        }
        disk = os.path.join(root, rel)
        if os.path.exists(disk):
            rec.update(enrich(disk))
        sources.append(rec)
    doc = {
        'generated_by': 'customization/tools/build_region_sources.py',
        'note': 'Piece-swap sources for the Creation Suite region_swaps. '
                'skinned/bones/extensions enrich when the GLB is on disk; '
                'null fields are inspected by the bake at import time.',
        'count': len(sources),
        'sources': sources,
    }
    dest = os.path.join(root, 'customization', 'region-sources.json')
    with open(dest, 'w', encoding='utf-8') as f:
        json.dump(doc, f, indent=1)
    print(f'wrote {dest}: {len(sources)} sources '
          f'({sum(1 for s in sources if s.get("skinned"))} known skinned)')

if __name__ == '__main__':
    main()
