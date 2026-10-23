#!/usr/bin/env python3
"""DOA4 phase 15 Job 2: extract all 197 entries of mot.afs (from the
phase-14 ISO extract in release doa4-iso-extracts-20261022, container
sha256 asserted) to scratch, write a per-file sha256 manifest, and
run the table-A census over every entry: table entry count, default
(data-start) value, distinct targets, shared-block size, tiling
check (targets + EOF == file size coverage)."""
import hashlib, json, os, struct, sys

AFS = '/home/hatch/workspace/_doa4p2-scratch/p15/extracts/mot.afs'
AFS_SHA = '5329bc059f52e1662dc1bbeb0541a675fa806f4f6e14cdc8c666b079d411e97a'
OUT = '/home/hatch/workspace/_doa4p2-scratch/p15/mot_entries'
REPO_JSON = sys.argv[1] if len(sys.argv) > 1 else '/home/hatch/workspace/_doa4p2-scratch/p15/mot_manifest_p15.json'
SIG = bytes.fromhex('001c0000f526ffff')

def main():
    d = open(AFS, 'rb').read()
    assert hashlib.sha256(d).hexdigest() == AFS_SHA
    assert d[:4] == b'AFS\x00'
    cnt = struct.unpack('<I', d[4:8])[0]
    ents = [struct.unpack_from('<II', d, 8 + i * 8) for i in range(cnt)]
    ao, asz = struct.unpack_from('<II', d, 8 + cnt * 8)
    os.makedirs(OUT, exist_ok=True)
    man = {'container': 'mot.afs', 'container_sha256': AFS_SHA, 'count': cnt, 'entries': []}
    for i, (off, sz) in enumerate(ents):
        name = d[ao + i * 48:ao + i * 48 + 32].split(b'\x00')[0].decode()
        blob = d[off:off + sz]
        with open(os.path.join(OUT, name), 'wb') as f: f.write(blob)
        e = {'index': i, 'name': name, 'offset': off, 'size': sz,
             'sha256': hashlib.sha256(blob).hexdigest()}
        # table-A census for .mot files
        if name.endswith('.mot') and sz >= 64:
            W = lambda o: struct.unpack_from('>I', blob, o)[0]
            default = W(0)
            sig = blob.find(SIG)
            if sig > 8 and (sig - 8) % 4 == 0:
                n = (sig - 8) // 4
                tab = [W(j * 4) for j in range(n)]
                tg = sorted(set(tab))
                e['tableA'] = {'entries': n, 'data_start': default,
                               'distinct_targets': len(tg),
                               'default_count': tab.count(default),
                               'shared_block_size': default - 4 - sig,
                               'last_target': tg[-1],
                               'targets_tile_to_eof': tg[-1] < sz}
            else:
                e['tableA'] = {'entries': None, 'note': 'shared-block signature not found',
                               'data_start': default}
        man['entries'].append(e)
        if i % 50 == 0: print(i, name, flush=True)
    json.dump(man, open(REPO_JSON, 'w'), indent=1)
    print('WROTE', REPO_JSON, cnt, 'entries')

if __name__ == '__main__':
    main()
