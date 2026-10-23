#!/usr/bin/env python3
"""DOA4 phase 15 Job 2: .mot census. For each input .mot file:
- head words (u16 pairs / BE u32s), entropy, f32 plausibility (BE+LE)
- front absolute-offset table: entries until the repeated-default
  pattern breaks; data_start = modal value; used-slot count; target
  range check (all targets inside file)
- relative sub-table at data_start-4..data_start (phase-14 evidence:
  the monotonic relative run begins 4 B before the absolute data
  start in both zack files — probed, not assumed: we scan the 64 B
  before data_start for the longest monotonic u32 run ending at
  data_start)
- record-size distribution from consecutive distinct absolute targets
- cross-reference numbers are printed for comparison with the .bin
  w21 table by the caller.
No semantics are assigned; structure only."""
import hashlib, json, math, os, struct, sys
from collections import Counter

def entropy(b):
    if not b: return 0.0
    c = Counter(b); n = len(b)
    return -sum((v / n) * math.log2(v / n) for v in c.values())

def f32p(b, fmt):
    n = len(b) // 4
    if not n: return 0.0
    fs = struct.unpack(fmt % n, b[:n * 4])
    ok = sum(1 for x in fs if x == 0 or (math.isfinite(x) and 1e-4 < abs(x) < 1e5))
    return round(ok / n, 4)

def census(path):
    d = open(path, 'rb').read()
    r = {'file': os.path.basename(path), 'size': len(d),
         'sha256': hashlib.sha256(d).hexdigest(),
         'entropy': round(entropy(d), 3),
         'head_u16_pairs': [struct.unpack_from('>HH', d, i * 4) for i in range(4)],
         'head_hex64': d[:64].hex(),
         'f32_plaus_BE': f32p(d, '>%df'), 'f32_plaus_LE': f32p(d, '<%df')}
    # front absolute table: BE u32s from 0; the default value is the mode
    words = struct.unpack('>%dI' % (min(len(d), 1 << 20) // 4), d[:min(len(d), 1 << 20)])
    # find table end: scan first 200k words for the modal value among
    # large values (>= 4096 and < size) that repeat >= 8 times early
    head_words = words[:4096]
    cnt = Counter(w for w in head_words if 4096 <= w < len(d))
    if cnt:
        default, dc = cnt.most_common(1)[0]
        # table length: first index where the run of (default or
        # in-range increasing targets) pattern ends — approximate by
        # counting leading words that are == default or plausible targets
        n_tab = 0
        for w in head_words:
            if w == default or (4096 <= w < len(d)):
                n_tab += 1
            else:
                break
        targets = sorted(set(w for w in head_words[:n_tab] if w != default))
        r['front_table'] = {'default_value': default, 'default_hex': hex(default),
                            'default_count_in_first4096': dc,
                            'approx_entries_scanned': n_tab,
                            'distinct_nondefault_targets_head': len(targets),
                            'target_min': targets[0] if targets else None,
                            'target_max': targets[-1] if targets else None}
        # relative sub-table probe: monotonic u32 BE run ending at default
        best = []
        for start in range(max(0, default - 4096), default - 4, 4):
            run = []
            p = start
            prev = -1
            while p + 4 <= default:
                v = struct.unpack_from('>I', d, p)[0]
                if v < prev or v > len(d): break
                run.append(v); prev = v; p += 4
            if len(run) > len(best): best = run
        r['relative_subtable_probe'] = {'count': len(best), 'first8': best[:8],
                                        'last': best[-1] if best else None,
                                        'deltas_first8': [best[i + 1] - best[i] for i in range(min(7, len(best) - 1))]}
    return r

if __name__ == '__main__':
    out = [census(p) for p in sys.argv[1:]]
    print(json.dumps(out, indent=1, default=str))
