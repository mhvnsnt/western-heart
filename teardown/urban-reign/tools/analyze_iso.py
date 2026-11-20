#!/usr/bin/env python3
"""Urban Reign PS2 ISO analyzer — file structure mapping + stage data identification.
Usage: python3 analyze_iso.py "Urban Reign (USA).iso"
Writes: iso-file-listing.txt, stage-candidates.txt
"""
import sys, os
import pycdlib

ISO = sys.argv[1]
OUTDIR = os.path.dirname(os.path.abspath(ISO))

def walk(iso):
    entries = []
    stack = ['/']
    while stack:
        path = stack.pop()
        for child in iso.list_children(iso_path=path):
            name = child.file_identifier().decode('utf-8', 'replace').split(';')[0]
            if name in ('.', '..'):
                continue
            full = path.rstrip('/') + '/' + name
            is_dir = child.is_dir()
            size = 0 if is_dir else child.get_data_length()
            entries.append((full, size, is_dir))
            if is_dir:
                stack.append(full)
    return entries

def main():
    iso = pycdlib.PyCdlib()
    iso.open(ISO)
    print('Walking ISO tree...')
    entries = walk(iso)

    dirs = [e for e in entries if e[2]]
    files = [e for e in entries if not e[2]]
    total = sum(f[1] for f in files)
    print(f'Directories: {len(dirs)}, Files: {len(files)}, Total bytes: {total:,}')

    with open(os.path.join(OUTDIR, 'iso-file-listing.txt'), 'w') as fh:
        fh.write(f'# Urban Reign (USA) PS2 ISO file listing\n')
        fh.write(f'# Files: {len(files)}, Dirs: {len(dirs)}, Total: {total:,} bytes\n\n')
        for full, size, is_dir in sorted(entries):
            tag = 'DIR ' if is_dir else 'FILE'
            fh.write(f'{tag} {size:>12,}  {full}\n')

    # Stage/arena candidate heuristics
    keywords = ['stage', 'arena', 'map', 'field', 'area', 'level', 'bg', 'room',
                'alley', 'bar', 'roof', 'china', 'junk', 'street', 'city']
    exts = ('.bin', '.dat', '.arc', '.pak', '.mdl', '.geo', '.map')
    cands = []
    for full, size, is_dir in files:
        low = full.lower()
        if any(k in low for k in keywords) or low.endswith(exts):
            cands.append((full, size))
    cands.sort(key=lambda x: -x[1])
    with open(os.path.join(OUTDIR, 'stage-candidates.txt'), 'w') as fh:
        fh.write(f'# Stage/arena candidates ({len(cands)})\n\n')
        for full, size in cands:
            fh.write(f'{size:>12,}  {full}\n')

    # Top-level dirs + biggest files
    print('\nTop-level directories:')
    for full, size, is_dir in sorted(entries):
        if is_dir and full.count('/') == 1:
            print('  ' + full)
    print('\nLargest 20 files:')
    for full, size, _ in sorted(files, key=lambda x: -x[1])[:20]:
        print(f'  {size:>12,}  {full}')

    iso.close()
    print(f'\nWrote iso-file-listing.txt and stage-candidates.txt to {OUTDIR}')

if __name__ == '__main__':
    main()
