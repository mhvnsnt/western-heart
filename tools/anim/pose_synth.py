import json
import numpy as np
from scipy.spatial.transform import Rotation as Rot

JOINTS = ['BODY_SCALE__group', 'BASE', 'Spine1', 'Spine2', 'Neck', 'Head', 'Hip', 'R_Shoulder', 'R_Arm', 'R_ForeArm',
          'R_Hand', 'L_Shoulder', 'L_Arm', 'L_ForeArm', 'L_Hand', 'R_UpLeg', 'R_Leg', 'R_Foot', 'L_UpLeg', 'L_Leg',
          'L_Foot', 'R_Toe', 'L_Toe']
TRACK = {'BASE': 3, 'Spine1': 4, 'Hip': 5, 'Neck': 7, 'Head': 8, 'R_Shoulder': 9, 'R_Arm': 10, 'R_ForeArm': 11,
         'R_Hand': 12, 'L_Shoulder': 13, 'L_Arm': 14, 'L_ForeArm': 15, 'L_Hand': 16, 'R_UpLeg': 17, 'R_Leg': 18,
         'R_Foot': 19, 'L_UpLeg': 20, 'L_Leg': 21, 'L_Foot': 22}
PARENT = {'BASE': 'BODY_SCALE__group', 'Spine1': 'BASE', 'Spine2': 'Spine1', 'Neck': 'Spine2', 'Head': 'Neck',
          'Hip': 'BASE', 'R_Shoulder': 'Spine2', 'R_Arm': 'R_Shoulder', 'R_ForeArm': 'R_Arm', 'R_Hand': 'R_ForeArm',
          'L_Shoulder': 'Spine2', 'L_Arm': 'L_Shoulder', 'L_ForeArm': 'L_Arm', 'L_Hand': 'L_ForeArm',
          'R_UpLeg': 'Hip', 'R_Leg': 'R_UpLeg', 'R_Foot': 'R_Leg', 'R_Toe': 'R_Foot',
          'L_UpLeg': 'Hip', 'L_Leg': 'L_UpLeg', 'L_Foot': 'L_Leg', 'L_Toe': 'L_Foot'}
ORDER = JOINTS[1:]  # parents always appear before children in JOINTS order (BODY_SCALE__group first)


class Synthesizer:
    """Pose the TekkenMannequin from game triples in numpy.

    Per-joint local rotation L(j) = A(j) @ (ZYX-Euler(triple))^-1 @ B(j), with A/B
    calibrated on helper-posed 0xC8 clips (max fit err ~1e-7 rad). Joints without a
    track (Spine2, toes) keep their rest local, exactly as TekkenAnimHelper leaves
    them. BODY_SCALE__group takes the helper's location rule from tracks 0/1.
    """

    def __init__(self, calib_path, rest, root_affine_path):
        calib = json.load(open(calib_path))
        self.A = {j: np.array(calib[j]['A']) for j in calib}
        self.B = {j: np.array(calib[j]['B']) for j in calib}
        ra = json.load(open(root_affine_path))
        self.root_M = np.array(ra['M'])
        self.root_c = np.array(ra['c'])
        self.rest = rest
        self.rest_world_rot = {j: np.array(rest[j]['rot']) for j in JOINTS}
        self.rest_head = {j: np.array(rest[j]['head']) for j in JOINTS}
        self.rest_local = {}
        self.off_local = {}
        for j in ORDER:
            p = PARENT[j]
            self.rest_local[j] = self.rest_world_rot[p].T @ self.rest_world_rot[j]
            self.off_local[j] = self.rest_world_rot[p].T @ (self.rest_head[j] - self.rest_head[p])

    def pose(self, frames, convention='c8', root_override=None):
        """frames: list of per-frame track triples (23 x 3). Returns a posed dict
        in the same shape t7_bl_pose.py writes ({rest, frames:[{joint:{rot, head}}]}).

        convention 'c8': game local = (ZYX-Euler(triple))^-1  (0xC8 f32 tracks).
        convention '64': game local = ZXY-Euler((-t1, t2, t0) / 2)  (0x64 i16
        tracks store double-angle euler components permuted (c1, c2, c0) -- the
        sampler's per-track func 0x82289228 builds sin/cos of the stored values,
        i.e. they are half-angle inputs; calibrated on stance + walk anatomy).
        root_override: optional callable triple -> 3x3 matrix replacing the
        convention's map for track 3 (RootRot) only."""
        out_frames = []
        for fr in frames:
            flat = [v for t in fr[:23] for v in t]
            loc = np.array([flat[3] / 1000 + flat[0] / 1000,
                            flat[4] / 1000 - 1.15,
                            flat[5] / 1000 - flat[2] / 1000])
            Rw = {'BODY_SCALE__group': self.rest_world_rot['BODY_SCALE__group']}
            heads = {'BODY_SCALE__group': self.rest_head['BODY_SCALE__group'] + self.root_M @ loc + self.root_c}
            frame = {'BODY_SCALE__group': {'rot': Rw['BODY_SCALE__group'].tolist(),
                                           'head': heads['BODY_SCALE__group'].tolist(),
                                           'tail': heads['BODY_SCALE__group'].tolist()}}
            for j in ORDER:
                p = PARENT[j]
                if j in TRACK:
                    t = fr[TRACK[j]]
                    if root_override is not None and TRACK[j] == 3:
                        G = root_override(t)
                    elif convention == '64':
                        G = Rot.from_euler('ZXY', (-t[1] * 0.5, t[2] * 0.5, t[0] * 0.5),
                                           degrees=False).as_matrix()
                    else:
                        G = Rot.from_euler('ZYX', t, degrees=False).as_matrix().T
                    L = self.A[j] @ G @ self.B[j]
                else:
                    L = self.rest_local[j]
                Rw[j] = Rw[p] @ L
                heads[j] = heads[p] + Rw[p] @ self.off_local[j]
                frame[j] = {'rot': Rw[j].tolist(), 'head': heads[j].tolist(), 'tail': heads[j].tolist()}
            out_frames.append(frame)
        return {'rest': self.rest, 'frames': out_frames}
