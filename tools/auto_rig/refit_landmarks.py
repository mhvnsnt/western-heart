#!/usr/bin/env python3
"""tools/auto_rig/refit_landmarks.py — re-fit a refit skeleton's joints from the mesh's own anatomical landmarks.

Why (Negativo, 2026-10-31; the owner's "cone face", "head and neck weighted toward his pelvis", "arms crushed like a
steamroller"): refit_skeleton.py scales the template skeleton to the mesh's FULL height. A big hair mass (or a hat,
horns, a crest) makes that height far taller than the body, so the joints land too high. Negativo (fit space,
height 0.98 incl. ~0.12 of hair):
  * arms at y 0.828 vs the mesh arm at 0.653; Spine1 at mouth height, Spine2 at the eyes, Neck/Head in the hair
    -> bone heat skins the face to chest bones (cone face) and the arms to bones 0.18 m above them (crushed arms);
  * hip joints (UpLeg) at 0.565 and Hips at 0.594 while the legs split at 0.395 -> the thighs pivot inside the
    belly and own the abdomen (every kick bends the belly).

Method (every number is measured on the mesh, or is a fixed human proportion; nothing is placed by hand):
  arms, per side (T-pose, character's left = +x):
    * a reference slice 1.5 hand lengths in from the fingertip holds only arm; from there, slices walk out to
      the tip and in toward the body inside a band around the arm's centre (|dy| < 0.06 H), and stop where
      the slice suddenly thickens (hair over the shoulder / the torso);
    * centreline = least-squares line through the clean slices' bbox centres (y and z against x);
    * armpit = the torso's half-width just under the arm's underside; shoulder joint (Arm) = armpit + 0.015 H
      on the centreline (humeral head sits just outside the rib cage);
    * wrist (Hand) = the thinnest arm cross-section 0.08-0.14 H in from the fingertip (human hand ~0.105 H);
    * elbow (ForeArm) at --elbow-frac of shoulder->wrist (upper arm : forearm ~ 1.15 : 1);
    * finger joints ride with the hand, offsets scaled so the fingertips stay inside the mesh.
  hips and legs:
    * crotch = the lowest point of the body on the mid-line (|x - cx| < 0.004 H), searched between the fitted
      knee and hips; hip joints (UpLeg) at crotch + 0.16 x (arm line - crotch) (human hip joint ~0.53 H, crotch
      ~0.47 H, shoulder ~0.82 H), on each thigh's centre just under the crotch (Negativo: crotch 0.38 vs
      fitted hip joints 0.565);
    * Hips keeps the template's offset above the hip joints; knees (Leg) keep the template's fraction of the
      ankle -> hip span, re-centred in the leg's cross-section; ankles, feet and toes are untouched;
    * skipped (template legs kept, reported) when no crotch is found in that window (skirts, long coats).
  spine / neck / head (front profile = front-most z of the mid-sagittal slab |x - cx| < 0.012 H):
    * neck base = first height above the arm line where the profile steps back from the chest by 0.02 H;
    * chin = first height above that where it steps forward again by 0.02 H; Neck joint at the neck base,
      Head joint at the chin (the whole jaw then belongs to the head bone);
      no clear throat (e.g. a beard) -> the template's offsets from the arm line instead;
    * Spine/Spine1/Spine2 keep their template fractions of Hips->Neck;
    * every spine/neck/head joint is centred front-to-back between the front surface and the next surface
      behind it in that slab (so hair hanging down the back cannot pull the spine backwards);
    * Left/RightShoulder (clavicles) keep their template offset above the arm line, z halfway between
      Spine2 and the arm; the Head bone's tail = 60% of the way from the Head joint to the mesh top.

usage: python3 tools/auto_rig/refit_landmarks.py --fit fit.json --out fit_landmarks.json [--no-legs]
       (fit.json from refit_skeleton.py, which also names the static mesh it wrote in "static_mesh")
then:  blender -b --factory-startup --python tools/auto_rig/backends/heat_rebind.py -- \\
           --in <static_mesh> --fit fit_landmarks.json --out MODEL-refit.glb [--donor <bvh> for the gate clip]
"""
import argparse
import json
import struct

import numpy as np


def mesh_in_fit_space(fit):
    """The static mesh's vertices turned and floored exactly as refit_skeleton.py did (same rot_y)."""
    b = open(fit['static_mesh'], 'rb').read()
    l0 = struct.unpack_from('<I', b, 12)[0]
    js = json.loads(b[20:20 + l0])
    binb = b[20 + l0 + 8:]
    out = []
    for mesh in js['meshes']:
        for prim in mesh['primitives']:
            a = js['accessors'][prim['attributes']['POSITION']]
            bv = js['bufferViews'][a['bufferView']]
            if bv.get('extensions'):
                raise SystemExit('compressed mesh: decode first (tools/anim/gltf_codec.mjs decode)')
            P = np.ndarray(shape=(a['count'], 3), dtype=np.float32, buffer=binb,
                           offset=bv.get('byteOffset', 0) + a.get('byteOffset', 0),
                           strides=(bv.get('byteStride') or 12, 4)).astype(np.float64)
            out.append(P)
    P = np.concatenate(out)
    th = np.radians(fit.get('mesh_rot_y_deg', 0))
    c, s = np.cos(th), np.sin(th)
    Q = P @ np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]).T
    Q[:, 1] -= Q[:, 1].min()
    return Q


def arm_slices(Q, sgn, H, step):
    """Clean arm slices (x, ylo, yhi, zlo, zhi) from the fingertip in toward the body."""
    X = Q[:, 0] * sgn
    x_tip = X.max()
    x_ref = x_tip - 1.5 * 0.105 * H
    ref = Q[np.abs(X - x_ref) < step]
    if len(ref) < 20:
        raise SystemExit('arm: no mesh at the forearm reference slice x=%.3f (not a T-pose?)' % (sgn * x_ref))
    yc = float(np.median(ref[:, 1]))
    rows = {}
    for direction in (+1, -1):
        y_c, x0, exts = yc, x_ref, []
        while (x0 <= x_tip) if direction > 0 else (x0 > 0):
            m = (np.abs(X - x0) < step * 0.8) & (np.abs(Q[:, 1] - y_c) < 0.06 * H)
            if m.sum() < 8:
                if direction > 0:
                    x0 += step
                    continue
                break
            S = Q[m]
            r = (x0, S[:, 1].min(), S[:, 1].max(), S[:, 2].min(), S[:, 2].max())
            ext = max(r[2] - r[1], r[4] - r[3])
            if direction < 0 and len(exts) >= 3 and ext > 1.5 * float(np.median(exts)):
                break  # hair over the shoulder / the torso
            exts.append(ext)
            rows[round(x0, 6)] = r
            y_c = (r[1] + r[2]) / 2
            x0 += direction * step
    return np.array([rows[k] for k in sorted(rows)]), x_tip


def contiguous_half_width(Q, cx, y, H, sgn):
    m = np.abs(Q[:, 1] - y) < 0.0015 * H
    v = np.sort((Q[m, 0] - cx) * sgn)
    v = v[v >= 0]
    if not len(v):
        return None
    g = np.nonzero(np.diff(v) > 0.01 * H)[0]
    return float(v[g[0]] if len(g) else v[-1])


def fit_arm(Q, sgn, H, cx, elbow_frac, step=0.005):
    R, x_tip = arm_slices(Q, sgn, H, step)
    x, ylo, yhi, zlo, zhi = R.T
    cy, cz = (ylo + yhi) / 2, (zlo + zhi) / 2
    x_clean0 = float(x.min())
    # wrist: thinnest cross-section 0.08-0.14 H in from the fingertip
    w = (x > x_tip - 0.14 * H) & (x < x_tip - 0.08 * H)
    x_wrist = float(x[w][np.argmin(((yhi - ylo) * (zhi - zlo))[w])]) if w.sum() >= 3 else x_tip - 0.105 * H
    # centreline from the clean slices between the body side and the wrist
    k = x <= x_wrist + 1e-9
    by = np.polyfit(x[k], cy[k], 1)
    bz = np.polyfit(x[k], cz[k], 1)
    # armpit: torso half-width just under the arm's underside at the innermost clean slice
    y_under = float(ylo[0])
    x_pit = contiguous_half_width(Q, cx, y_under - 0.01 * H, H, sgn)
    x_arm = min(x_pit + 0.015 * H, x_clean0) if x_pit is not None else x_clean0
    x_elbow = x_arm + elbow_frac * (x_wrist - x_arm)
    at = lambda xx: np.array([cx + sgn * xx, np.polyval(by, xx), np.polyval(bz, xx)])
    return {'arm': at(x_arm), 'elbow': at(x_elbow), 'wrist': at(x_wrist), 'x_tip': float(x_tip),
            'x_clean0': x_clean0, 'x_armpit': x_pit, 'y_arm_line': float(np.polyval(by, x_arm))}


def front_back(Q, cx, y, H):
    """Front-most z of the mid-sagittal slab at height y, and the next surface behind the front one."""
    m = (np.abs(Q[:, 0] - cx) < 0.012 * H) & (np.abs(Q[:, 1] - y) < 0.0015 * H)
    z = np.sort(Q[m, 2])[::-1]
    if len(z) < 6:
        return None, None
    g = np.nonzero(-np.diff(z) > 0.012 * H)[0]
    return float(z[0]), (float(z[g[0] + 1]) if len(g) else None)


def centre_z(Q, cx, y, H, fallback):
    f, b = front_back(Q, cx, y, H)
    return (f + b) / 2 if f is not None and b is not None else fallback


def leg_centre(Q, cx, y, H, sgn):
    """Centre (x, z) of one leg's horizontal cross-section at height y (the interval on that side of the mid-line)."""
    m = (np.abs(Q[:, 1] - y) < 0.002 * H) & ((Q[:, 0] - cx) * sgn > 0.002 * H)
    S = Q[m]
    if len(S) < 8:
        return None
    x = np.sort((S[:, 0] - cx) * sgn)
    g = np.nonzero(np.diff(x) > 0.01 * H)[0]
    x_out = x[g[0]] if len(g) else x[-1]          # the leg's interval starts at the mid-line side
    S = S[(S[:, 0] - cx) * sgn <= x_out + 1e-9]
    return np.array([(S[:, 0].min() + S[:, 0].max()) / 2, (S[:, 2].min() + S[:, 2].max()) / 2])


def fit_legs(Q, J0, H, cx, y_arm):
    """Crotch-anchored hip joints, Hips and knees. Returns ({joint: pos}, report) or ({}, report) when skipped."""
    y_lo, y_hi = min(J0['LeftLeg'][1], J0['RightLeg'][1]), max(J0['LeftUpLeg'][1], J0['RightUpLeg'][1])
    mid = np.abs(Q[:, 0] - cx) < 0.004 * H
    cand = Q[mid & (Q[:, 1] > y_lo) & (Q[:, 1] < y_hi + 0.1 * H), 1]
    if not len(cand):
        return {}, {'skipped': 'no body on the mid-line between the fitted knee and hips'}
    y_crotch = float(cand.min())
    if y_crotch <= y_lo + 0.005 * H:  # the mid-line is filled down to the knee: skirt / coat, can't see the crotch
        return {}, {'skipped': 'mid-line filled down to the knee (skirt/coat?): crotch not measurable'}
    y_hip = y_crotch + 0.16 * (y_arm - y_crotch)
    out = {}
    for side, sgn in (('Left', 1.0), ('Right', -1.0)):
        c = leg_centre(Q, cx, y_crotch - 0.03 * H, H, sgn)
        if c is None:
            return {}, {'skipped': '%s thigh not found under the crotch' % side}
        out[side + 'UpLeg'] = np.array([c[0], y_hip, c[1]])
        ank = J0[side + 'Foot']
        f = (J0[side + 'Leg'][1] - ank[1]) / max(J0[side + 'UpLeg'][1] - ank[1], 1e-6)
        yk = ank[1] + f * (y_hip - ank[1])
        ck = leg_centre(Q, cx, yk, H, sgn)
        out[side + 'Leg'] = np.array([ck[0], yk, ck[1]]) if ck is not None else np.array([J0[side + 'Leg'][0], yk, J0[side + 'Leg'][2]])
    up = (J0['Hips'][1] - (J0['LeftUpLeg'][1] + J0['RightUpLeg'][1]) / 2)
    yh = y_hip + up
    out['Hips'] = np.array([cx, yh, centre_z(Q, cx, yh, H, J0['Hips'][2])])
    return out, {'crotch_y': round(y_crotch, 4), 'hip_joint_y': round(float(y_hip), 4),
                 'template_hip_joint_y': round(float((J0['LeftUpLeg'][1] + J0['RightUpLeg'][1]) / 2), 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fit', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--elbow-frac', type=float, default=0.535, help='elbow position along shoulder->wrist')
    ap.add_argument('--no-legs', action='store_true', help='keep the template hips/legs')
    a = ap.parse_args()
    fit = json.load(open(a.fit))
    joints = fit['joints']
    J0 = {j['name']: np.array(j['pos'], dtype=float) for j in joints}
    J = {k: v.copy() for k, v in J0.items()}
    H = fit.get('height_m') or float(max(p[1] for p in J0.values()))
    cx = float(J0['Hips'][0])
    Q = mesh_in_fit_space(fit)
    rep = {'tool': 'tools/auto_rig/refit_landmarks.py'}

    # arms
    arms = {}
    for side, sgn in (('Left', 1.0), ('Right', -1.0)):
        r = fit_arm(Q, sgn, H, cx, a.elbow_frac)
        arms[side] = r
        J[side + 'Arm'], J[side + 'ForeArm'], J[side + 'Hand'] = r['arm'], r['elbow'], r['wrist']
        fingers = [n for n in J0 if n.startswith(side + 'Hand') and n != side + 'Hand']
        old_reach = max([abs(J0[n][0] - J0[side + 'Hand'][0]) for n in fingers] + [1e-6])
        new_reach = max(r['x_tip'] - abs(r['wrist'][0] - cx), 1e-6) * 0.92
        k = min(1.0, new_reach / old_reach)
        for n in fingers:
            J[n] = r['wrist'] + (J0[n] - J0[side + 'Hand']) * k
        rep[side + '_arm'] = {'armpit_x': None if r['x_armpit'] is None else round(r['x_armpit'], 4),
                              'clean_from_x': round(r['x_clean0'], 4), 'fingertip_x': round(r['x_tip'], 4),
                              'finger_scale': round(float(k), 3)}
    y_arm_old = (J0['LeftArm'][1] + J0['RightArm'][1]) / 2
    y_arm = (arms['Left']['y_arm_line'] + arms['Right']['y_arm_line']) / 2

    # hips + legs
    if not a.no_legs:
        legs, rep['legs'] = fit_legs(Q, J0, H, cx, y_arm)
        J.update(legs)
    else:
        rep['legs'] = {'skipped': '--no-legs'}

    # neck base + chin from the front profile above the arm line
    ys = np.arange(y_arm - 0.01 * H, y_arm + 0.15 * H, 0.002 * H)
    F = np.array([v if v is not None else np.nan for v in (front_back(Q, cx, y, H)[0] for y in ys)])
    f_chest = np.nanmax(F[ys <= y_arm]) if np.any(ys <= y_arm) else np.nan
    y_neck = y_chin = None
    if np.isfinite(f_chest):
        i = np.nonzero((ys > y_arm) & (F < f_chest - 0.02 * H))[0]
        if len(i):
            y_neck = float(ys[i[0]])
            f_min = np.inf
            for y, f in zip(ys[ys > y_neck], F[ys > y_neck]):
                if not np.isfinite(f):
                    continue
                f_min = min(f_min, f)
                if f > f_min + 0.02 * H:
                    y_chin = float(y)
                    break
    if y_neck is None or y_chin is None:  # no clear throat: keep the template's offsets from the arm line
        y_neck = J0['Neck'][1] - y_arm_old + y_arm
        y_chin = J0['Head'][1] - y_arm_old + y_arm
        rep['neck_head_from'] = 'template offsets from the arm line (no clear throat in the front profile)'
    else:
        rep['neck_head_from'] = 'front profile: neck base y %.4f, chin y %.4f' % (y_neck, y_chin)
    z_neck = centre_z(Q, cx, y_neck, H, J0['Neck'][2])
    z_throat = centre_z(Q, cx, (y_neck + y_chin) / 2, H, z_neck)
    J['Neck'] = np.array([cx, y_neck, z_neck])
    J['Head'] = np.array([cx, y_chin, z_throat])
    # spine chain: template fractions of Hips->Neck (from the re-fitted Hips), centred front-to-back
    hy0, ny0, hy = J0['Hips'][1], J0['Neck'][1], J['Hips'][1]
    for n in ('Spine', 'Spine1', 'Spine2'):
        if n in J0:
            f = (J0[n][1] - hy0) / max(ny0 - hy0, 1e-6)
            y = hy + f * (y_neck - hy)
            J[n] = np.array([cx, y, centre_z(Q, cx, y, H, J0[n][2])])
    # clavicles: template offset above the arm line, z between Spine2 and the arm
    for side in ('Left', 'Right'):
        n = side + 'Shoulder'
        if n in J0:
            J[n] = np.array([J0[n][0], arms[side]['y_arm_line'] + (J0[n][1] - J0[side + 'Arm'][1]),
                             (J['Spine2'][2] + arms[side]['arm'][2]) / 2])
    y_top = float(Q[np.abs(Q[:, 0] - cx) < 0.05 * H, 1].max())
    fit.setdefault('leaf_tail', {})['Head'] = [round(cx, 5), round(J['Head'][1] + 0.6 * (y_top - J['Head'][1]), 5),
                                               round(float(J['Head'][2]), 5)]

    moved = {}
    for j in joints:
        n = j['name']
        d = float(np.linalg.norm(J[n] - J0[n]))
        j['pos'] = [round(float(v), 5) for v in J[n]]
        if d > 1e-4 and not (n.startswith(('LeftHand', 'RightHand')) and n not in ('LeftHand', 'RightHand')):
            moved[n] = {'from': [round(float(v), 4) for v in J0[n]], 'to': j['pos'][:], 'moved_m': round(d, 4)}
    rep['arm_line_y'] = {'template_fit': round(float(y_arm_old), 4), 'mesh': round(float(y_arm), 4)}
    rep['moved'] = moved
    fit.setdefault('notes', {})['landmark_refit'] = rep
    json.dump(fit, open(a.out, 'w'), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != 'moved'}, indent=1))
    for n, v in moved.items():
        print('%-14s %s -> %s  (%.3f m)' % (n, v['from'], v['to'], v['moved_m']))


if __name__ == '__main__':
    main()
