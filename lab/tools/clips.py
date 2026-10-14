"""Combat clips authored on the WH-Canonical-22 skeleton (world-aligned rest).

Poses are given as world-space targets (hip offset, hand/foot targets, torso
rotations); arms and legs are solved with analytic 2-bone IK so feet stay
planted and strikes reach forward (+Z). Strike clips are normalised to 1.0 s:
0.0 stance -> 0.4 contact (active start) -> 0.5 active end -> 1.0 recovered;
the move interpreter seeks into them using real T3 frame data.
"""
import math
import numpy as np

def rx(a): c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def ry(a): c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def rz(a): c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
D = math.radians

def rot_between(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b)
    v = np.cross(a, b); c = float(np.dot(a, b))
    if c < -0.9999:
        ax = np.cross(a, [1, 0, 0]);
        if np.linalg.norm(ax) < 1e-6: ax = np.cross(a, [0, 1, 0])
        ax /= np.linalg.norm(ax); return 2 * np.outer(ax, ax) - np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx / (1 + c)

def quat(m):
    t = np.trace(m)
    if t > 0:
        s = math.sqrt(t + 1) * 2; return [(m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s, s / 4]
    i = int(np.argmax(np.diag(m))); j, k = (i + 1) % 3, (i + 2) % 3
    s = math.sqrt(1 + m[i, i] - m[j, j] - m[k, k]) * 2
    q = [0, 0, 0, 0]; q[i] = s / 4; q[j] = (m[j, i] + m[i, j]) / s; q[k] = (m[k, i] + m[i, k]) / s; q[3] = (m[k, j] - m[j, k]) / s
    return q

class Rig:
    def __init__(self, rig):
        self.n = rig["names"]; self.par = rig["parent"]; self.piv = np.asarray(rig["pivot"], float)
        self.i = {n: k for k, n in enumerate(self.n)}
        self.lead = "Left" if self.piv[self.i["LeftHand"]][2] > self.piv[self.i["RightHand"]][2] else "Right"
        self.rear = "Right" if self.lead == "Left" else "Left"
        self.leadleg = "Left" if self.piv[self.i["LeftFoot"]][2] > self.piv[self.i["RightFoot"]][2] else "Right"
        self.rearleg = "Right" if self.leadleg == "Left" else "Left"

    def solve(self, pose):
        """pose: hips (offset), root_rot, chest (R), head (R), hands {side: offset}, feet {side: offset}."""
        n = len(self.n); G = [None] * n; W = np.zeros((n, 3))
        hands, feet = pose.get("hands", {}), pose.get("feet", {})
        for b in range(n):
            nm = self.n[b]; p = self.par[b]
            if p < 0:
                G[b] = pose.get("root_rot", np.eye(3)); W[b] = self.piv[b] + pose.get("hips", np.zeros(3)); continue
            W[b] = W[p] + G[p] @ (self.piv[b] - self.piv[p])
            G[b] = G[p]
            if nm == "Chest": G[b] = pose.get("chest", np.eye(3)) @ G[p]
            if nm == "Head": G[b] = pose.get("head", np.eye(3)) @ G[p]
            for side, targets, a, m, e in ((s, hands, "Arm", "ForeArm", "Hand") for s in ("Left", "Right")):
                pass
            for side in ("Left", "Right"):
                for tgt, a, m, e, pole in ((hands, "Arm", "ForeArm", "Hand", np.array([0, -1, -0.3])), (feet, "UpLeg", "Leg", "Foot", np.array([0, 0, 1.0]))):
                    if nm == side + a and side in tgt and pose.get("ik", True):
                        ia, im, ie = self.i[side + a], self.i[side + m], self.i[side + e]
                        l1 = np.linalg.norm(self.piv[im] - self.piv[ia]); l2 = np.linalg.norm(self.piv[ie] - self.piv[im])
                        t = self.piv[ie] + np.asarray(tgt[side], float)
                        d = t - W[b]; L = np.linalg.norm(d); L = min(max(L, abs(l1 - l2) + 1e-4), l1 + l2 - 1e-4)
                        u = d / np.linalg.norm(d); t = W[b] + u * L
                        pv = pole - np.dot(pole, u) * u; pv /= np.linalg.norm(pv)
                        ca = (l1 * l1 + L * L - l2 * l2) / (2 * l1 * L); th = math.acos(max(-1, min(1, ca)))
                        knee = W[b] + l1 * (math.cos(th) * u + math.sin(th) * pv)
                        G[b] = rot_between(self.piv[im] - self.piv[ia], knee - W[b])
                        self._pending = (im, ie, knee, t, e)
                    if hasattr(self, "_pending") and b == self._pending[0] and nm == side + m:
                        im, ie, knee, t, e = self._pending
                        G[b] = rot_between(self.piv[ie] - self.piv[im], t - knee)
                    if nm == side + e and e == "Foot" and pose.get("flat_feet", True) and side in feet:
                        G[b] = pose.get("root_rot", np.eye(3))
        if hasattr(self, "_pending"): del self._pending
        L = []
        for b in range(n):
            p = self.par[b]; L.append(G[b] if p < 0 else G[p].T @ G[b])
        return L, W

    def clip(self, keys, root_motion=True):
        out = {}
        sols = [(t, self.solve(p), p.get("hips", np.zeros(3))) for t, p in keys]
        for b in range(len(self.n)):
            times = [t for t, _, _ in sols]
            qs = [quat(s[0][b]) for _, s, _ in sols]
            for k in range(1, len(qs)):  # hemisphere continuity
                if np.dot(qs[k], qs[k - 1]) < 0: qs[k] = [-x for x in qs[k]]
            tr = None
            if self.par[b] < 0 and root_motion:
                tr = [list(self.piv[b] + h) for _, _, h in sols]
            out[b] = (times, qs, tr)
        return out

def build_all(rig_desc):
    r = Rig(rig_desc); L, R = r.lead, r.rear; FL, FR = r.leadleg, r.rearleg
    z = np.zeros(3); H = lambda x, y, zz: np.array([x, y, zz], float)
    plant = {FL: z, FR: z}
    stance = {"hips": z, "feet": plant, "hands": {L: z, R: z}}
    def P(**kw):
        p = {"hips": z, "feet": dict(plant), "hands": {L: z, R: z}}; p.update(kw); return p
    clips = {}
    clips["idle"] = r.clip([(0, P()), (0.5, P(hips=H(0, -0.025, 0), chest=rx(D(3)), hands={L: H(0, -0.01, 0), R: H(0, -0.015, 0)})), (1.0, P())])
    # walk: hips bob, feet step in place (game moves the root); alternate lift
    def walk(sign):
        k = []
        for i, t in enumerate(np.linspace(0, 0.8, 9)):
            ph = t / 0.8 * 2 * math.pi
            lf = {FL: H(0, max(0, math.sin(ph)) * 0.08, sign * 0.08 * math.cos(ph)), FR: H(0, max(0, -math.sin(ph)) * 0.08, -sign * 0.08 * math.cos(ph))}
            k.append((float(t), P(hips=H(0, -0.03 - 0.015 * abs(math.sin(ph)), 0), feet=lf)))
        return r.clip(k)
    clips["walk_fwd"] = walk(1); clips["walk_back"] = walk(-1)
    # strikes, normalised 1.0 s; 0.4 contact .. 0.5 active end
    clips["light"] = r.clip([(0, P()), (0.25, P(hands={L: H(0, 0.06, 0.12), R: z})), (0.4, P(chest=ry(D(-14) if L == "Left" else D(14)), hands={L: H(-0.12 if L == "Left" else 0.12, 0.12, 0.42), R: H(0, 0.03, 0)})),
                             (0.5, P(chest=ry(D(-14) if L == "Left" else D(14)), hands={L: H(-0.12 if L == "Left" else 0.12, 0.12, 0.42), R: H(0, 0.03, 0)})), (1.0, P())])
    tw = D(28) if R == "Right" else D(-28)
    clips["medium"] = r.clip([(0, P()), (0.25, P(hips=H(0, -0.03, -0.03), chest=ry(-tw * 0.4), hands={L: z, R: H(0, 0, -0.08)})),
                              (0.4, P(hips=H(0, -0.04, 0.10), chest=ry(tw), hands={L: H(0, -0.05, -0.1), R: H(0.22 if R == "Right" else -0.22, 0.18, 0.62)})),
                              (0.5, P(hips=H(0, -0.04, 0.10), chest=ry(tw), hands={L: H(0, -0.05, -0.1), R: H(0.22 if R == "Right" else -0.22, 0.18, 0.62)})), (1.0, P())])
    kick_feet = lambda lift: {FL: z, FR: lift}
    clips["heavy"] = r.clip([(0, P()), (0.25, P(hips=H(0, -0.02, 0.02), chest=rx(D(-6)), feet=kick_feet(H(0, 0.35, 0.25)))),
                             (0.4, P(hips=H(0, 0.0, 0.05), chest=rx(D(-14)), feet=kick_feet(H(0, 0.75, 0.85)), flat_feet=True)),
                             (0.5, P(hips=H(0, 0.0, 0.05), chest=rx(D(-14)), feet=kick_feet(H(0, 0.75, 0.85)))),
                             (0.75, P(feet=kick_feet(H(0, 0.25, 0.25)))), (1.0, P())])
    clips["grab"] = r.clip([(0, P()), (0.4, P(hips=H(0, -0.08, 0.15), chest=rx(D(15)), hands={L: H(0.1, 0.1, 0.55), R: H(-0.1, 0.1, 0.75)})),
                            (0.5, P(hips=H(0, -0.08, 0.15), chest=rx(D(15)), hands={L: H(0.1, 0.25, 0.5), R: H(-0.1, 0.25, 0.7)})),
                            (0.75, P(hips=H(0, 0.0, 0.0), chest=rx(D(-25)), hands={L: H(0, 0.55, 0.0), R: H(0, 0.55, 0.0)})), (1.0, P())])
    clips["hit"] = r.clip([(0, P()), (0.08, P(hips=H(0, -0.04, -0.08), chest=rx(D(-22)), head=rx(D(-20)), hands={L: H(0, 0.05, -0.15), R: H(0, 0.05, -0.15)})), (0.4, P())])
    clips["block"] = r.clip([(0, P()), (0.1, P(hips=H(0, -0.06, -0.03), chest=rx(D(8)), hands={L: H(0.06 if L == "Right" else -0.06, 0.22, 0.05), R: H(-0.1 if R == "Right" else 0.1, 0.30, 0.20)})),
                             (0.3, P(hips=H(0, -0.06, -0.03), chest=rx(D(8)), hands={L: H(0.06 if L == "Right" else -0.06, 0.22, 0.05), R: H(-0.1 if R == "Right" else 0.1, 0.30, 0.20)}))])
    clips["ko"] = r.clip([(0, P()), (0.25, P(hips=H(0, -0.1, -0.2), chest=rx(D(-30)), head=rx(D(-30)))),
                          (0.8, P(ik=False, root_rot=rx(D(-85)), hips=H(0, -0.92, -0.9), feet={}, hands={})),
                          (1.2, P(ik=False, root_rot=rx(D(-90)), hips=H(0, -0.95, -0.95), feet={}, hands={}))])
    clips["win"] = r.clip([(0, P()), (0.5, P(hips=H(0, 0.02, 0), chest=rx(D(-10)), hands={L: H(0.0, 0.85, 0.05), R: H(0.0, 0.85, 0.05)})), (1.0, P(hips=H(0, 0.02, 0), chest=rx(D(-10)), hands={L: H(0.0, 0.9, 0.05), R: H(0.0, 0.9, 0.05)}))])
    return clips
