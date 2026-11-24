"""Contract check over all assembled previews (vectorized with numpy)."""
import json, glob, math
import numpy as np
files = sorted(glob.glob('previews/*.json'))
print(f"previews: {len(files)}")
bad_bones, hips_bad = [], []
worst_norm, worst_at = 0.0, None
durations, nperf = [], []
for f in files:
    d = json.load(open(f))
    durations.append(d['duration'])
    nperf.append(len(d['performers']))
    for p in d['performers']:
        tracks = p['tracks']
        if len(tracks) != 52:
            bad_bones.append((f, p['role'], len(tracks)))
        for b, keys in tracks.items():
            q = np.array([k['q'] for k in keys], dtype=float)
            n = np.linalg.norm(q, axis=1)
            dev = float(np.abs(n - 1.0).max()) if len(n) else 0.0
            if dev > worst_norm:
                worst_norm, worst_at = dev, (f, b)
        hips = tracks.get('mixamorigHips', [])
        if hips and 'p' in hips[0]:
            ps = np.array([k['p'] for k in hips], dtype=float)
            if ps[:, 1].min() < -1.5 or ps[:, 1].max() > 2.5:
                hips_bad.append((f, p['role'], round(float(ps[:, 1].min()), 2),
                                 round(float(ps[:, 1].max()), 2)))
print(f"bone-count violations (!=52): {len(bad_bones)} {bad_bones[:5]}")
print(f"worst |quat norm - 1|: {worst_norm:.4f} at {worst_at}")
print(f"Hips-y out-of-band (<-1.5 or >2.5): {len(hips_bad)}")
for h in hips_bad[:10]:
    print("   ", h)
print(f"durations: min {min(durations):.2f}s max {max(durations):.2f}s "
      f"total {sum(durations)/60:.1f} min; performers: {sorted(set(nperf))}")
