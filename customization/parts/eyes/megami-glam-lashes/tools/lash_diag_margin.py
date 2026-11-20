"""V7 diagnostic: WHAT is the extracted margin loop, geometrically?
For each arc point: signed distance to the fitted eyeball surface
(|p-c| - R). A true eye-opening rim hugs the ball (skin wraps it);
a prim seam across the lid sits millimetres off the ball in front.
Also: arc midpoint height above the iris centre, and top<->bot gap."""
import numpy as np, json
g = np.load('work/lash_megami_geometry.npz', allow_pickle=True)
meta = json.loads(str(g['meta']))
for s in ('posx', 'negx'):
    c = g[f'{s}_ball_c']; R = meta[s]['ball_r']; iris = g[f'{s}_iris_c']
    print(f'== {s}: ball R={R*1000:.2f}mm iris_d={meta[s]["iris_d"]*1000:.2f}mm')
    for part in ('top', 'bot'):
        P = g[f'{s}_{part}']
        d = (np.linalg.norm(P - c, axis=1) - R) * 1000
        print(f'  {part}: n={len(P)} dist-to-ball mm: min {d.min():+.2f} '
              f'mean {d.mean():+.2f} max {d.max():+.2f}')
        print(f'       y above iris_c (mm): {(P[:,1]-iris[1]).min()*1000:+.2f}..'
              f'{(P[:,1]-iris[1]).max()*1000:+.2f}  mid-pt {((P[len(P)//2,1]-iris[1])*1000):+.2f}')
    top = g[f'{s}_top']; bot = g[f'{s}_bot']
    # closest top<->bot vertical gap near the middle x
    mid_top = top[np.argmin(np.abs(top[:, 0] - iris[0]))]
    mid_bot = bot[np.argmin(np.abs(bot[:, 0] - iris[0]))]
    print(f'  mid gap top-bot: {(mid_top[1]-mid_bot[1])*1000:.2f} mm '
          f'(iris_d {meta[s]["iris_d"]*1000:.2f})')
    # how far in FRONT (z) of the ball surface is the top-mid point?
    mt = top[len(top)//2]
    v = mt - c; vn = v/np.linalg.norm(v)
    print(f'  top-mid: radial off-ball {(np.linalg.norm(v)-R)*1000:+.2f} mm, '
          f'dir from centre (x,y,z)=({vn[0]:+.2f},{vn[1]:+.2f},{vn[2]:+.2f})')
