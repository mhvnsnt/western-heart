#!/usr/bin/env python3
"""Pick the highest-hip-energy 3s window from a CMU BVH, decimate to 24fps."""
import sys, math

src, dst = sys.argv[1], sys.argv[2]
lines = open(src).read().splitlines()
hi = lines.index('MOTION')
frames_i = next(i for i,l in enumerate(lines) if l.startswith('Frames:'))
n_frames = int(lines[frames_i].split(':')[1])
ft = float(lines[next(i for i,l in enumerate(lines) if l.startswith('Frame Time:'))].split(':')[1])
motion = lines[hi+3:]  # after MOTION, Frames:, Frame Time:
motion = [l for l in motion if l.strip()]
assert len(motion) >= n_frames, (len(motion), n_frames)
motion = motion[:n_frames]
data = [[float(x) for x in l.split()] for l in motion]
# Hips = first 6 channels: Xpos Ypos Zpos Zrot Xrot Yrot (Y-up: Ypos is height)
fps_src = round(1/ft)
win = 3 * fps_src  # 3 seconds
best, best_e = 0, -1
for s in range(0, n_frames - win, fps_src // 2):
    seg = data[s:s+win]
    e = 0.0
    for a, b in zip(seg, seg[1:]):
        e += abs(b[1]-a[1]) * 3.0          # vertical hip bounce, weighted
        e += abs(b[0]-a[0]) + abs(b[2]-a[2])  # lateral sway
        e += abs(b[3]-a[3]) * 0.05 + abs(b[5]-a[5]) * 0.05  # hip rotation
    if e > best_e:
        best_e, best = e, s
print(f"window: frames {best}..{best+win} (t={best/fps_src:.1f}s) energy={best_e:.1f}")
step = fps_src // 24
picked = list(range(best, best+win, step))
out = lines[:hi+1]
out.append(f"Frames:\t{len(picked)}")
out.append("Frame Time:\t0.0416667")
for i in picked:
    out.append(motion[i])
open(dst, 'w').write("\n".join(out) + "\n")
print(f"wrote {dst}: {len(picked)} frames @24fps")
