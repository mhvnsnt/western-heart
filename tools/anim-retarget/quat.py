"""Quaternion / rotation utilities (numpy-only)."""

import numpy as np


def qnormalize(q):
    n = np.linalg.norm(q, axis=-1, keepdims=True)
    return q / np.clip(n, 1e-12, None)


def qmul(a, b):
    """Hamilton product, quaternions as [x, y, z, w]."""
    ax, ay, az, aw = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    bx, by, bz, bw = b[..., 0], b[..., 1], b[..., 2], b[..., 3]
    return np.stack(
        [
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
            aw * bw - ax * bx - ay * by - az * bz,
        ],
        axis=-1,
    )


def qconj(q):
    c = q.copy()
    c[..., :3] *= -1.0
    return c


def qapply(q, v):
    """Rotate vectors v (...,3) by quaternions q (...,4)."""
    qv = np.concatenate([v, np.zeros(v.shape[:-1] + (1,))], axis=-1)
    return qmul(qmul(q, qv), qconj(q))[..., :3]


def qmean(quats, weights):
    """Weighted quaternion mean (Markley et al.): principal eigenvector of
    sum_i w_i * q_i q_i^T. Handles antipodal double-cover."""
    quats = qnormalize(quats)
    # Flip to common hemisphere for stability.
    ref = quats[0]
    dots = quats @ ref
    quats = np.where((dots < 0)[..., None], -quats, quats)
    M = np.einsum("i,ij,ik->jk", weights, quats, quats)
    vals, vecs = np.linalg.eigh(M)
    return qnormalize(vecs[:, np.argmax(vals)])


def qto_6d(q):
    """6D rotation representation (Zhou et al. 2019), as used in paper F_m."""
    q = qnormalize(q)
    x, y, z, w = q[..., 0], q[..., 1], q[..., 2], q[..., 3]
    m = np.stack(
        [
            1 - 2 * (y * y + z * z),
            2 * (x * y + z * w),
            2 * (x * z - y * w),
            2 * (x * y - z * w),
            1 - 2 * (x * x + z * z),
            2 * (y * z + x * w),
            2 * (x * z + y * w),
            2 * (y * z - x * w),
            1 - 2 * (x * x + y * y),
        ],
        axis=-1,
    ).reshape(q.shape[:-1] + (3, 3))
    return m[..., :, :2].reshape(q.shape[:-1] + (6,))


def q6d_to_mat(r6):
    a1 = r6[..., 0:3]
    a2 = r6[..., 3:6]

    def _n(v):
        return v / np.clip(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12, None)

    b1 = _n(a1)
    b2 = a2 - (b1 * a2).sum(-1, keepdims=True) * b1
    b2 = _n(b2)
    b3 = np.cross(b1, b2)
    return np.stack([b1, b2, b3], axis=-1)


def fk(local_quats, X_l, root_pos):
    """Forward kinematics.

    local_quats: (J,4) local rotations (rest = identity, wh-anim/1 note).
    X_l: (J,3) parent-relative rest offsets.
    root_pos: (3,) root world position for this frame.
    Returns global joint positions (J,3).
    """
    J = len(X_l)
    order = _topo_order()
    gq = np.zeros((J, 4))
    gp = np.zeros((J, 3))
    gq[0] = local_quats[0]
    gp[0] = root_pos
    for i in order[1:]:
        p = _PARENTS[i]
        gq[i] = qmul(gq[p], local_quats[i])
        gp[i] = gp[p] + qapply(gq[p], X_l[i])
    return gp


# -- traversal state set by set_parents() -----------------------------------
_PARENTS = []
_CHILDREN = []


def set_parents(parents):
    global _PARENTS, _CHILDREN
    _PARENTS = list(parents)
    _CHILDREN = [[] for _ in parents]
    for i, p in enumerate(parents):
        if p >= 0:
            _CHILDREN[p].append(i)


def _topo_order():
    order = [i for i, p in enumerate(_PARENTS) if p < 0]
    for i in order:
        order.extend(_CHILDREN[i])
    return order
