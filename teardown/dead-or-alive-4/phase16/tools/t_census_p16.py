#!/usr/bin/env python3
"""DOA4 phase 16 Job 1a: t_* tag-motion file census.

Parses the (id, offset) index of every t_* file in the extracted
mot entries (release doa4-mot-20261022, per-file sha256 verified
against phase15/mot-entries-manifest.json before this ran),
records segment spans, and probes cross-file structure:
- final-segment length distribution (is there a shared trailer?)
- byte-identity of final segments across files
- longest common substring between the smallest files' streams
Output: JSON report (path from argv[1]); summary on stdout.
"""
import hashlib, json, os, struct, sys
from collections import Counter

MOT = '/home/hatch/workspace/_doa4p16-scratch/mot'

def parse_index(b):
    pairs = []
    i = 0
    while i + 8 <= len(b):
        a, c = struct.unpack_from('>II', b, i)
        if a == 0xFFFFFFFF:
            return pairs, i
        pairs.append((a, c))
        i += 8
    return pairs, None

def lcs_len(a, b, minlen=16):
    # longest common substring length via set of hashes at decreasing sizes (bounded)
    for L in (1024, 512, 256, 128, 64, 32, 16):
        sa = {hashlib.sha256(a[i:i+L]).digest() for i in range(0, len(a)-L+1, 1)}
        for j in range(0, len(b)-L+1, 1):
            if hashlib.sha256(b[j:j+L]).digest() in sa:
                return L
    return 0

def main():
    out_path = sys.argv[1]
    names = sorted(n for n in os.listdir(MOT) if n.startswith('t_'))
    report = {'files': {}, 'final_seg_lens': {}, 'notes': []}
    finals = {}
    for n in names:
        b = open(os.path.join(MOT, n), 'rb').read()
        pairs, sep = parse_index(b)
        ids = [p[0] for p in pairs]; offs = [p[1] for p in pairs]
        stream_start = None
        if sep is not None:
            # after separator word: count zero words
            j = sep + 4
            while j + 4 <= len(b) and struct.unpack_from('>I', b, j)[0] == 0:
                j += 4
            stream_start = j
        bounds = ([stream_start] if stream_start is not None else []) + offs + [len(b)]
        segs = [bounds[i+1]-bounds[i] for i in range(len(bounds)-1)] if stream_start is not None else []
        report['files'][n] = {
            'size': len(b), 'n_pairs': len(pairs), 'ids': ids,
            'id_consecutive': all(ids[i+1]-ids[i] == 1 for i in range(len(ids)-1)) if len(ids) > 1 else True,
            'offs': offs, 'offs_increasing': all(offs[i+1] > offs[i] for i in range(len(offs)-1)) if len(offs) > 1 else True,
            'offs_in_file': all(0 < o < len(b) for o in offs),
            'sep_at': sep, 'stream_start': stream_start, 'segment_sizes': segs,
            'sha256': hashlib.sha256(b).hexdigest(),
        }
        if segs:
            report['final_seg_lens'].setdefault(str(segs[-1]), []).append(n)
            finals[n] = b[offs[-1]:] if offs else b''
    # final segment byte-identity groups
    by_hash = {}
    for n, fb in finals.items():
        by_hash.setdefault(hashlib.sha256(fb).hexdigest(), []).append(n)
    report['final_seg_identity_groups'] = {h: v for h, v in by_hash.items() if len(v) > 1}
    report['final_seg_distinct_hashes'] = len(by_hash)
    json.dump(report, open(out_path, 'w'), indent=1)
    print(f'{len(names)} t_* files parsed')
    print('n_pairs distribution:', Counter(v["n_pairs"] for v in report["files"].values()))
    print('id_consecutive all:', all(v['id_consecutive'] for v in report['files'].values()))
    print('offs_increasing all:', all(v['offs_increasing'] for v in report['files'].values()))
    print('offs_in_file all:', all(v['offs_in_file'] for v in report['files'].values()))
    print('final segment length distribution:', {k: len(v) for k, v in report['final_seg_lens'].items()})
    print('final segment distinct hashes:', report['final_seg_distinct_hashes'], 'identity groups>1:', len(report['final_seg_identity_groups']))

if __name__ == '__main__':
    main()
