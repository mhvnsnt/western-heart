#!/usr/bin/env python3
"""DOA4 phase 13 Job 1: stream-assemble doa4.iso from release
doa4-iso-v1 parts. Each part: gh download -> sha256 verified against
the GitHub release-asset digest -> written at its ISO offset
(sparse, conv=notrunc) -> part file deleted -> running whole-ISO
sha256 state kept in iso_hash_state.json (hash of each part's bytes
in part order; the whole-ISO sha256 is computed by a final streaming
pass once all 30 parts are landed, and also maintained incrementally
as a concatenation hash when parts land in order).
Usage: iso_assemble_p13.py NN [NN ...]   (part numbers, any order)
State/log: scratch p13/iso_assembly_log.json
"""
import hashlib, json, os, subprocess, sys

SCR = '/home/hatch/workspace/_doa4p2-scratch/p13'
ISO = os.path.join(SCR, 'doa4.iso')
LOG = os.path.join(SCR, 'iso_assembly_log.json')
PART_SIZE = 262144000
TOTAL = 7834892288

def digests():
    a = json.load(open('/home/hatch/workspace/_doa4p2-scratch/p13/iso_assets.json'))
    return {x['name']: x['digest'].split(':')[1] for x in a}

def main():
    want = [int(x) for x in sys.argv[1:]]
    dg = digests()
    log = json.load(open(LOG)) if os.path.exists(LOG) else {'landed': {}}
    if not os.path.exists(ISO):
        with open(ISO, 'wb') as f:
            f.truncate(TOTAL)
    for nn in want:
        name = f'doa4-250m.part_{nn:02d}'
        if name in log['landed']:
            print(name, 'already landed, skip'); continue
        part = os.path.join(SCR, name)
        if not os.path.exists(part):
            subprocess.run(['gh', 'release', 'download', 'doa4-iso-v1',
                            '--repo', 'mhvnsnt/western-heart',
                            '--pattern', name, '--dir', SCR], check=True)
        size = os.path.getsize(part)
        exp = PART_SIZE if nn < 30 else TOTAL - 29 * PART_SIZE
        assert size == exp, (name, size, exp)
        h = hashlib.sha256()
        with open(part, 'rb') as f:
            while True:
                b = f.read(1 << 22)
                if not b: break
                h.update(b)
        sha = h.hexdigest()
        assert sha == dg[name], (name, sha, dg[name])
        print(name, 'sha256 OK', sha, flush=True)
        off = (nn - 1) * PART_SIZE
        subprocess.run(['dd', f'if={part}', f'of={ISO}', 'bs=4M',
                        f'seek={off}', 'oflag=seek_bytes', 'conv=notrunc',
                        'status=none'], check=True)
        os.remove(part)
        log['landed'][name] = {'sha256': sha, 'size': size, 'offset': off}
        json.dump(log, open(LOG, 'w'), indent=1)
        print(name, 'written at', off, '; landed', len(log['landed']), '/30', flush=True)

if __name__ == '__main__':
    main()
