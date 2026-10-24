#!/usr/bin/env python3
"""Urban Reign (SLUS-212.09) character decoder.

Decodes one character PPK (.ppk = 0x80 fncc header + .vmd model) into a
self-contained skinned GLB: bind-pose mesh, skeleton, per-vertex
joint/weight skinning, UVs. Every run keeps ALL state local to the one
character being decoded -- no shared rig, no cross-character state
(per-character isolation: a fix for one character cannot move another).

FORMAT (proven from the data, cross-checked against the game's own
decompiled code paths -- see docs/urban-reign/URBAN-REIGN-SKINNING.md):

* The .vmd vertex stream is a set of pre-baked VU1 DMA packets. The
  packet table lives in the .vmd header (32-byte descriptors
  [u32 0x30|qwc, u32 packet_off, 0, 0, 0x10000000, 0,0,0], groups
  separated by 0x60000000 markers). Each packet = one strip of one
  mesh object ("DMA group"); slots are palette-local to the group.
* Vertex record = N influence pairs + UV row + GS color row.
  Influence pair: (w*px, w*py, w*pz, w) + (w*nx, w*ny, w*nz, slotbits),
  slotbits = (0x8000 if last influence) | slot*4.
  POSITIONS AND NORMALS ARE STORED PREMULTIPLIED BY THE WEIGHT: the
  VU1 skinning program (ELF .vutext, microprogram at VU1 addr 0x1D98)
  sums M_bone * stored directly ("bone matrix addressed by the w of
  the weight" -- urban-reign-recomp docs/PROGRESS.md). World position
  of a vertex = sum_k W[slot_k] @ stored_k where W are the bones'
  world (bind) matrices; W's translation term is implicitly weighted
  because stored positions carry w.
* Bind matrices are not stored per-vertex. For a pair of slots blended
  on the same vertex, q_b = R q_a + t holds EXACTLY (float precision)
  for the unpremultiplied local points/normals, with (R, t) the
  relative bind transform W_b^-1 W_a. Fitting those relations per
  group (Kabsch, reflections allowed) and chaining them recovers
  every bone's world matrix up to one frame per connected component.
* Slots map to global bones through per-piece palettes. The .vmd
  header graph stores three palette records (27/16/6 entries); each
  DMA group (or contiguous sub-piece of one -- a group can batch two
  sub-objects with different palettes) uses one palette at one
  window offset, forward or reversed. The assignment is recovered
  by trusted-skeleton growth (see assign_by_trusted_fit): a piece
  joins the skeleton only when one of its candidates maps its local
  bone frames onto the trusted skeleton's frames with residual
  < 0.02 (true assignments fit to float precision; wrong ones are
  off by tenths), so placement is self-validating, and every
  piece's fit residual is reported in the stats. Assembly places
  each piece by its own fitted frame -- relations are never pooled
  across pieces, so an unproven piece cannot tear a proven one.

Usage: ur_decode.py char001.ppk char001.glb [--obj char001.obj]
"""
import struct, sys, math, json
from collections import defaultdict, deque
import numpy as np

# The three palette records found in chr01's .vmd header graph
# (file offsets in chr01.vmd: 0x116 n=27, 0xaa n=16, 0x7e n=6).
# These tables are the engine-standard candidate families: they
# validated across every character tested. Each character's header
# ALSO carries its own list records (permutations of the same bone
# sets, at character-specific offsets), and some characters use
# pieces with more slots than any record covers -- so decode()
# unions these with the character's own parsed header records and
# an identity (node-order) family. Frame-fit validation is the
# arbiter: a wrong family simply never fits.
PALETTES = {
    'P27': [0,1,8,9,43,10,11,44,45,4,5,6,7,46,47,48,2,3,49,50,12,17,51,13,52,53,54],
    'P16': [35,30,36,31,37,38,33,39,32,34,40,41,42,1,2,3],
    'P6':  [10,11,44,6,7,46],
}
_ACTIVE_PALETTES = None  # set per character by decode()

def _palettes():
    return _ACTIVE_PALETTES if _ACTIVE_PALETTES is not None else PALETTES

def parse_node_max(vmd):
    """Largest node id in the header graph's child-list records
    (`01 <tag> 07 <n>` with 0xff-separated child ids). This is the
    loader's own bound on legal bone ids for the character.
    Falls back to a loose 0xff-run scan of the graph zone, then
    to 57 (chr01's proven bound)."""
    best = None
    for i in range(0x40, min(0x2000, len(vmd) - 4)):
        if vmd[i] == 0x01 and vmd[i+2] == 0x07:
            n = vmd[i+3]
            if 3 <= n <= 64 and i + 4 + n <= len(vmd):
                vals = [b for b in vmd[i+4:i+4+n] if b != 0xff]
                if vals and all(b <= 70 for b in vals):
                    m = max(vals)
                    best = m if best is None else max(best, m)
    if best is None:
        run = []
        for i in range(0x40, min(0x2000, len(vmd))):
            b = vmd[i]
            if b == 0xff or b <= 70:
                run.append(b)
            else:
                ff = run.count(0xff)
                ids = [x for x in run if x != 0xff]
                if ff >= 2 and ids:
                    m = max(ids)
                    best = m if best is None else max(best, m)
                run = []
    return best if best is not None else 57

def parse_header_palettes(vmd):
    """Scan the .vmd header graph zone for palette list records
    `01 <tag> 03 <n> <n bone ids>` (n in 6..40, ids <= 63, followed
    by zero padding or another record start). Returns
    {'H<offset>': [ids]} deduplicated by content."""
    out = {}
    seen = set()
    for i in range(0x40, min(0x2000, len(vmd) - 4)):
        if vmd[i] == 0x01 and vmd[i+2] == 0x03:
            n = vmd[i+3]
            if 6 <= n <= 40 and i + 4 + n <= len(vmd):
                vals = list(vmd[i+4:i+4+n])
                if all(b <= 63 for b in vals) and len(set(vals)) >= 5:
                    tail = vmd[i+4+n:i+6+n]
                    if tail in (b'\x00\x00', b'\x00\x01', b'\x01\x01',
                                b'\x01\x02', b'\x01\x03'):
                        key = tuple(vals)
                        if key not in seen:
                            seen.add(key)
                            out[f'H{i:x}'] = vals
    return out

# ---------------------------------------------------------------- PPK --

def read_vmd(ppk_bytes):
    """PPK = 0x80 header + .vmd verbatim."""
    if len(ppk_bytes) > 0x80 and ppk_bytes[0x10:0x14] == b'fncc':
        return ppk_bytes[0x80:]
    return ppk_bytes  # already a bare .vmd

# ------------------------------------------------------- DMA packet table --

def find_dma_table(d):
    i = 0
    n = len(d)
    while i + 32 <= n:
        w0, w1 = struct.unpack('<II', d[i:i+8])
        if (w0 >> 24) == 0x30 and 0 < w1 < n and (w0 & 0xff) > 0:
            j = i; cnt = 0
            while j + 32 <= n:
                c0, c1, c2, c3 = struct.unpack('<4I', d[j:j+16])
                if (c0 >> 24) == 0x30 and c2 == 0 and c3 == 0: cnt += 1; j += 32
                elif c0 == 0x60000000: j += 16
                else: break
            if cnt >= 8: return i
        i += 4
    return None

def parse_dma_table(d, start):
    groups = []
    cur = []
    j = start
    n = min(len(d), 0x2000)
    while j + 32 <= n:
        c0, c1, c2, c3 = struct.unpack('<4I', d[j:j+16])
        if (c0 >> 24) == 0x30 and c2 == 0 and c3 == 0 and 0 < c1 < len(d):
            cur.append((c1, c0 & 0xff))
            j += 32
        elif c0 == 0x60000000:
            if cur: groups.append(cur); cur = []
            j += 16
        else:
            j += 16
    if cur: groups.append(cur)
    return groups

# ------------------------------------------------------------ vertex parse --

def _is_color_row(fl, i):
    r, g, b, a = fl[i], fl[i+1], fl[i+2], fl[i+3]
    return (abs(a - 128.0) < 0.01 and -0.01 <= r <= 128.01
            and -0.01 <= g <= 128.01 and -0.01 <= b <= 128.01)

def parse_packet(d, off, size):
    """One DMA packet (strip): 32-byte header + vertex records.
    Returns list of vertices; parser state never crosses packets."""
    start = off + 32
    seg = d[start:off+size]
    nf = len(seg) // 4
    fl = struct.unpack(f'<{nf}f', seg[:nf*4])
    iu = struct.unpack(f'<{nf}I', seg[:nf*4])
    verts = []
    i = 0
    while i + 12 <= nf:
        j = i
        infs = []
        ok = False
        while j + 8 <= nf:
            px, py, pz, w = fl[j], fl[j+1], fl[j+2], fl[j+3]
            nx, ny, nz = fl[j+4], fl[j+5], fl[j+6]
            if not all(math.isfinite(v) and abs(v) < 1e4
                       for v in (px, py, pz, w, nx, ny, nz)):
                break
            if not (0.0 <= w <= 1.001):
                break
            infs.append((px, py, pz, w, nx, ny, nz, iu[j+7]))
            j += 8
            if (j + 8 <= nf and abs(fl[j+2] - 1.0) < 0.01
                    and _is_color_row(fl, j+4)):
                if abs(sum(x[3] for x in infs) - 1.0) < 0.02 and 1 <= len(infs) <= 8:
                    verts.append({'infs': [list(x) for x in infs],
                                  'uv': [fl[j], fl[j+1]], 'uvflag': iu[j+3],
                                  'color': list(fl[j+4:j+8]),
                                  'off': start + i*4})
                    i = j + 8
                    ok = True
                break
            if len(infs) > 8:
                break
        if not ok:
            i += 1
    return verts

def parse_groups(vmd):
    """Returns (groups, runs): groups = per-DMA-group flat vertex
    lists; runs[gi] = [(start, count), ...] vertex runs, one per DMA
    packet (strip). Faces may only be built INSIDE a run -- triples
    spanning two packets join unrelated surface patches."""
    start = find_dma_table(vmd)
    if start is None:
        raise ValueError("DMA descriptor table not found")
    out = []
    runs = []
    for grp in parse_dma_table(vmd, start):
        gverts = []
        gruns = []
        for (poff, imm) in grp:
            pv = parse_packet(vmd, poff, imm*16)
            gruns.append((len(gverts), len(pv)))
            gverts.extend(pv)
        out.append(gverts)
        runs.append(gruns)
    return out, runs

# --------------------------------------------------------- relation fitting --

def slot_of(inf):
    return (inf[7] & 0x7fff) // 4

def _kabsch(A, B):
    """Row-form Kabsch (reflections allowed): R minimising |A@R - B|.
    R = U @ Vt for A.T@B = U S Vt. NOTE: the transpose V@U.T is the
    classic bug here -- it is masked whenever R is symmetric (identity
    and axis flips fit either way), so verify on a general rotation."""
    U, S, Vt = np.linalg.svd(A.T @ B)
    return U @ Vt

def fit_pairs(verts):
    """Directed slot-pair relations (a->b): q_b = q_a @ R + t for the
    unpremultiplied local points. Clustered by translation; returns
    {(a, b): (R, t, n_obs, n_total)} for the dominant consistent
    cluster of each pair."""
    obs = defaultdict(list)
    for v in verts:
        infs = v['infs']
        if len(infs) < 2: continue
        d = {}
        for inf in infs:
            w = inf[3]
            if w < 1e-6: continue
            d[slot_of(inf)] = (np.array(inf[0:3])/w, np.array(inf[4:7])/w)
        ks = sorted(d)
        for a in ks:
            for b in ks:
                if a != b:
                    obs[(a, b)].append((d[a], d[b]))
    rel = {}
    for (a, b), lst in obs.items():
        if len(lst) < 3: continue
        NA = np.array([x[0][1] for x in lst])
        NB = np.array([x[1][1] for x in lst])
        QA = np.array([x[0][0] for x in lst])
        QB = np.array([x[1][0] for x in lst])
        R = _kabsch(NA, NB)
        if np.abs(NA @ R - NB).max() > 0.01: continue
        T = QB - QA @ R
        med = np.median(T, axis=0)
        dev = np.linalg.norm(T - med, axis=1)
        core = dev < 0.01
        if core.sum() < 3: continue
        R2 = _kabsch(NA[core], NB[core])
        if np.abs(NA[core] @ R2 - NB[core]).max() > 0.002: continue
        T2 = QB[core] - QA[core] @ R2
        t = np.median(T2, axis=0)
        if np.linalg.norm(T2 - t, axis=1).max() > 0.002: continue
        rel[(a, b)] = (R2, t, int(core.sum()), len(lst))
    return rel

# ------------------------------------------------------ palette assignment --

def _candidates(maxslot):
    out = []
    for name, P in _palettes().items():
        for w0 in range(0, len(P) - maxslot):
            out.append((name, w0, False))
            out.append((name, w0, True))
    return out

def _mapping(cand, slots):
    name, w0, rev = cand
    P = _palettes()[name][::-1] if rev else _palettes()[name]
    return {s: P[w0+s] for s in slots}

def _chain(pool, bones):
    adj = defaultdict(list)
    for (a, b), (R, t) in pool.items():
        M = np.eye(4); M[:3, :3] = R.T; M[:3, 3] = t
        adj[b].append((a, M)); adj[a].append((b, np.linalg.inv(M)))
    W = {}
    parent = {}
    for root in sorted(bones, key=lambda b: -len(adj[b])):
        if root in W: continue
        W[root] = np.eye(4); parent[root] = -1
        q = deque([root])
        while q:
            cur = q.popleft()
            for nxt, M in adj[cur]:
                if nxt not in W:
                    W[nxt] = W[cur] @ M; parent[nxt] = cur; q.append(nxt)
    return W, parent

def _frame_fit(L, W, shared):
    """Rigid (or reflected-rigid) transform F mapping local bone
    frames L[s] onto global frames W[bone] over the shared slots,
    least squares over frame origins + axis tips. Falls back to the
    single most-shared bone's exact frame when <2 shared bones."""
    if len(shared) == 1:
        s, bone = shared[0]
        return W[bone] @ np.linalg.inv(L[s]), 0.0
    A = []
    B = []
    for s, bone in shared:
        for k in range(4):
            tip = np.zeros(3) if k == 0 else np.eye(3)[k-1] * 0.2
            A.append(L[s][:3, :3] @ tip + L[s][:3, 3])
            B.append(W[bone][:3, :3] @ tip + W[bone][:3, 3])
    A = np.array(A); B = np.array(B)
    best = None
    for refl in (False, True):
        # row-form Kabsch: R_row minimises |A @ R_row - B|
        H = (A - A.mean(axis=0)).T @ (B - B.mean(axis=0))
        U, S, Vt = np.linalg.svd(H)
        R = U @ Vt
        if refl and np.linalg.det(R) > 0:
            U2 = U.copy(); U2[:, -1] *= -1; R = U2 @ Vt
        if not refl and np.linalg.det(R) < 0:
            U2 = U.copy(); U2[:, -1] *= -1; R = U2 @ Vt
        t = B.mean(axis=0) - A.mean(axis=0) @ R
        resid = np.abs(A @ R + t - B).max()
        if best is None or resid < best[1]:
            # convert to the column-vector 4x4 convention used by the
            # rest of this module: p' = F @ p  =>  F_rot = R_row.T
            F = np.eye(4); F[:3, :3] = R.T; F[:3, 3] = t
            best = (F, resid)
    return best

_PIECE_CACHE = {}

def _piece_data(groups, runs, gi, lo, hi):
    """One processing piece: a contiguous run of packets of one DMA
    group. Pieces are the palette-assignment unit -- a DMA group can
    batch two sub-objects with different palettes (proven on chr01
    grp14/grp15), so groups are split into pieces when they do not
    fit the trusted skeleton whole. Results are memoised: the
    trusted-fit growth re-requests the same pieces across seeds and
    split scans, and the per-piece relation fit is the expensive
    kernel. The cache key includes id(groups) so it can never leak
    across characters (each decode parses a fresh groups list)."""
    key = (id(groups), gi, lo, hi)
    if key in _PIECE_CACHE:
        return _PIECE_CACHE[key]
    out = _piece_data_compute(groups, runs, gi, lo, hi)
    _PIECE_CACHE[key] = out
    return out

def _piece_data_compute(groups, runs, gi, lo, hi):
    verts = []
    pruns = []
    for (s, c) in runs[gi][lo:hi]:
        pruns.append((len(verts), c))
        verts.extend(groups[gi][s:s+c])
    grel = fit_pairs(verts)
    gslots = sorted({slot_of(i) for v in verts for i in v['infs']})
    lpool = {(a, b): (R, t) for (a, b), (R, t, n, tot) in grel.items()}
    lbones = sorted({x for p in lpool for x in p} | set(gslots))
    L, lparent = _chain(lpool, lbones)
    # Islands: connected components of the relation graph. Relations
    # only form between slots blended on a shared vertex, so a
    # piece's slots split into islands whose local frames are exact
    # internally but mutually unconstrained. All fitting is therefore
    # per island; the vertex transform itself is island-free (it uses
    # the global skeleton W directly).
    adj = defaultdict(set)
    for (a, b) in grel:
        adj[a].add(b); adj[b].add(a)
    islands = []
    seen = set()
    for s0 in gslots:
        if s0 in seen: continue
        comp = set(); dq = deque([s0])
        while dq:
            x = dq.popleft()
            if x in comp: continue
            comp.add(x); dq.extend(adj[x])
        seen |= comp
        islands.append(sorted(comp))
    # Per-slot influence data for fast vectorised placement, and the
    # piece's ADC-strip triangles (local vertex indices) for fast
    # surface scoring.
    slot_data = {}
    for vi, v in enumerate(verts):
        for inf in v['infs']:
            s = slot_of(inf)
            ent = slot_data.setdefault(s, ([], [], []))
            ent[0].append(vi)
            ent[1].append(inf[0:3])
            ent[2].append(inf[3])
    slot_data = {s: (np.array(a[0]), np.array(a[1], dtype=np.float64),
                     np.array(a[2], dtype=np.float64))
                 for s, a in slot_data.items()}
    strip_tris = []
    for (rs, rc) in pruns:
        seq = [(rs+k, verts[rs+k]['uvflag']) for k in range(rc)]
        segs = []
        cur = []
        for item in seq:
            if item[1] == 1 and cur:
                segs.append(cur); cur = []
            cur.append(item)
        if cur: segs.append(cur)
        for seg in segs:
            for k in range(len(seg) - 2):
                a, b, c = seg[k][0], seg[k+1][0], seg[k+2][0]
                if k % 2 == 1: a, b = b, a
                strip_tris.append((a, b, c))
    return {'verts': verts, 'runs': pruns, 'grel': grel,
            'gslots': gslots, 'L': L, 'lparent': lparent,
            'islands': islands, 'slot_data': slot_data,
            'strip_tris': np.array(strip_tris, dtype=np.int64)
            if strip_tris else np.zeros((0, 3), dtype=np.int64),
            'src': gi, 'lo': lo, 'hi': hi}

def assemble(pieces, assign, W, parent):
    """Vertex placement by the global skinning formula itself:
    world = sum_k W[bone_k] @ stored_k, with W the trusted skeleton
    built during assignment growth (extended by leftover pieces'
    island fits). No per-piece frame is applied to vertices, so a
    piece can never be torn by its own fit, and skinning is
    consistent with the exported skeleton by construction. Faces =
    consecutive triples inside each packet run. Vertices referencing
    bones absent from W are dropped (and counted in the stats via
    placed vs parsed). Returns (W, parent, verts, faces, resid)
    where resid[pid] is the worst validated-island fit of the
    piece's assigned candidate against the final W (-1 = the piece
    has no validated island)."""
    verts = []
    faces = []
    resid = {}
    for pid in sorted(pieces):
        if pid not in assign: continue
        pd = pieces[pid]
        mp = _mapping(assign[pid], pd['gslots'])
        worst = None
        for isl in pd['islands']:
            shared = [(s, mp[s]) for s in isl
                      if mp[s] in W and s in pd['L']]
            if len(shared) >= 2:
                _F, r = _frame_fit(pd['L'], W, shared)
                worst = r if worst is None else max(worst, r)
        resid[pid] = -1.0 if worst is None else float(worst)
        grp_idx = []
        for v in pd['verts']:
            p = np.zeros(3); nrm = np.zeros(3); good = True
            joints = []; weights = []
            for inf in v['infs']:
                s = slot_of(inf)
                bone = mp[s]
                if bone not in W: good = False; break
                M = W[bone]
                p += M[:3, :3] @ np.array(inf[0:3]) + M[:3, 3] * inf[3]
                nrm += M[:3, :3] @ np.array(inf[4:7])
                joints.append(bone); weights.append(inf[3])
            if good:
                grp_idx.append(len(verts))
                verts.append({'p': p, 'n': nrm, 'uv': v['uv'],
                              'joints': joints, 'weights': weights})
            else:
                grp_idx.append(None)
        for (rstart, rcount) in pd['runs']:
            # PS2 GS topology: each packet is a triangle strip; a
            # vertex whose UV-row flag (the GS ADC bit) is 1 starts a
            # new strip segment. Triangles alternate winding along
            # the strip. (Proven empirically: with list triples the
            # clean groups tear; with ADC strips grp5/7/14/15/16 have
            # ZERO long-edge faces in local assembly.)
            seq = [(grp_idx[rstart+k], pd['verts'][rstart+k]['uvflag'])
                   for k in range(rcount)]
            segs = []
            cur = []
            for item in seq:
                if item[1] == 1 and cur:
                    segs.append(cur); cur = []
                cur.append(item)
            if cur: segs.append(cur)
            for seg in segs:
                for k in range(len(seg) - 2):
                    a, b, c = seg[k][0], seg[k+1][0], seg[k+2][0]
                    if a is None or b is None or c is None:
                        continue
                    if k % 2 == 1:
                        a, b = b, a
                    faces.append((a, b, c))
    return W, parent, verts, faces, resid

def _piece_positions(pd, cand, W):
    """World positions of one piece's vertices under a palette
    candidate (vectorised): bones present in W use W; the piece's
    other bones are framed by its island fits onto W (exact anchor
    for 1-shared islands). Returns an (n,3) array, or None where a
    referenced bone cannot be framed."""
    mp = _mapping(cand, pd['gslots'])
    Wl = dict(W)
    for isl in pd['islands']:
        shared = [(s, mp[s]) for s in isl if mp[s] in W and s in pd['L']]
        if len(shared) >= 2:
            F, _r = _frame_fit(pd['L'], W, shared)
        elif len(shared) == 1:
            s0, b0 = shared[0]
            F = W[b0] @ np.linalg.inv(pd['L'][s0])
        else:
            continue
        for s in isl:
            bone = mp[s]
            if bone not in Wl and s in pd['L']:
                Wl[bone] = F @ pd['L'][s]
    pos = np.zeros((len(pd['verts']), 3))
    covered = np.zeros(len(pd['verts']), dtype=bool)
    for s, (vidx, spos, w) in pd['slot_data'].items():
        bone = mp[s]
        if bone not in Wl:
            return None
        M = Wl[bone]
        pos[vidx] += spos @ M[:3, :3].T + w[:, None] * M[:3, 3]
        covered[vidx] = True
    if not covered.all():
        return None
    return pos

def _strip_bad(pd, pos):
    """(bad, total) ADC-strip faces whose longest edge exceeds 0.25
    (authored surface median edge ~0.02-0.07; torn placements
    produce 0.25-0.95 edges). Fully vectorised."""
    tris = pd['strip_tris']
    if len(tris) == 0 or pos is None:
        return (0, 0) if pos is not None else (10**9, 0)
    P = pos[tris]
    e = np.maximum(np.linalg.norm(P[:, 0] - P[:, 1], axis=1),
                   np.maximum(np.linalg.norm(P[:, 1] - P[:, 2], axis=1),
                              np.linalg.norm(P[:, 2] - P[:, 0], axis=1)))
    return int((e > 0.25).sum()), len(tris)

def polish_by_faces(pieces, assign, W, parent, rounds=2):
    """Surface-verified candidate polish. Frame fits alone can be
    fooled (bind frames are near-axis-aligned, so a wrong palette
    can fit bone frames yet tear the surface). For each piece,
    every palette candidate is scored by the piece's ADC-strip
    long-edge face count against the current skeleton -- with the
    piece's exclusively-owned bones removed, so the test is honest
    leave-one-out. A flip only touches the piece's own vertices and
    its exclusive bones' frames; other pieces are unaffected.
    Iterates to a fixed point (max `rounds`)."""
    def usage():
        u = defaultdict(set)
        for pid, cand in assign.items():
            mp = _mapping(cand, pieces[pid]['gslots'])
            for s in pieces[pid]['gslots']:
                u[mp[s]].add(pid)
        return u
    for _ in range(rounds):
        changed = False
        u = usage()
        for pid in sorted(assign, key=lambda p: -len(pieces[p]['verts'])):
            pd = pieces[pid]
            excl = {b for b, ps in u.items() if ps == {pid}}
            Wbase = {b: M for b, M in W.items() if b not in excl}
            cur_bad, _t = _strip_bad(pd, _piece_positions(pd, assign[pid],
                                                          Wbase))
            if cur_bad == 0:
                continue  # surface already clean -- nothing to fix
            best = (cur_bad, assign[pid])
            for cand in _candidates(max(pd['gslots'])):
                if cand == assign[pid]: continue
                if cand[0] == 'ID' and assign[pid][0] != 'ID':
                    continue  # provenance beats a surface tie-break
                vv = _piece_positions(pd, cand, Wbase)
                if vv is None: continue
                b, _t = _strip_bad(pd, vv)
                if b < best[0]:
                    best = (b, cand)
            if best[1] != assign[pid]:
                assign[pid] = best[1]
                changed = True
                for b in excl:
                    W.pop(b, None)
                mp = _mapping(best[1], pd['gslots'])
                for isl in pd['islands']:
                    shared = [(s, mp[s]) for s in isl
                              if mp[s] in W and s in pd['L']]
                    if len(shared) >= 2:
                        F, _r = _frame_fit(pd['L'], W, shared)
                    elif len(shared) == 1:
                        s0, b0 = shared[0]
                        F = W[b0] @ np.linalg.inv(pd['L'][s0])
                    else:
                        continue
                    for s in isl:
                        bone = mp[s]
                        if bone not in W and s in pd['L']:
                            W[bone] = F @ pd['L'][s]
                            parent.setdefault(bone, -1)
                u = usage()
        if not changed:
            break
    return assign, W, parent

def _eval_candidate(pd, cand, W):
    """Evaluate one palette candidate for a piece against skeleton W,
    per island. Returns (mp, island_frames, worst, n_validated,
    all_anchored, total_shared): island_frames = [(island, F|None)]
    with F the island's fit onto W (exact anchor for 1-shared
    islands); worst = max fit residual over islands with >=2 shared
    bones (None if no island is validated); all_anchored = every
    island shares >=1 bone with W."""
    mp = _mapping(cand, pd['gslots'])
    island_frames = []
    worst = None
    n_validated = 0
    all_anchored = True
    total_shared = 0
    for isl in pd['islands']:
        shared = [(s, mp[s]) for s in isl
                  if mp[s] in W and s in pd['L']]
        total_shared += len(shared)
        if len(shared) >= 2:
            F, r = _frame_fit(pd['L'], W, shared)
            island_frames.append((isl, F))
            n_validated += 1
            worst = r if worst is None else max(worst, r)
        elif len(shared) == 1:
            s, bone = shared[0]
            F = W[bone] @ np.linalg.inv(pd['L'][s])
            island_frames.append((isl, F))
        else:
            island_frames.append((isl, None))
            all_anchored = False
    return mp, island_frames, worst, n_validated, all_anchored, total_shared

def assign_by_trusted_fit(groups, runs):
    """Assignment by trusted-skeleton growth over pieces, with
    per-island validation. The largest piece seeds a skeleton under
    each of its palette candidates in turn. A piece joins as PROVEN
    only when a candidate anchors every island (>=1 shared bone) and
    every validated island (>=2 shared bones) fits the trusted
    skeleton to <0.02 (true assignments fit to float precision;
    wrong ones are off by tenths). Joining pieces extend the
    skeleton island by island. When growth stalls, unplaced
    multi-packet pieces are split at packet boundaries where the
    slot set changes (a DMA group can batch two sub-objects with
    different palettes) and growth resumes. The first seed proving
    every parsed vertex wins outright; otherwise the seed proving
    the most vertices wins. Leftovers get their best-scoring
    candidate (anchored first, then most validated islands, then
    lowest residual) and extend the skeleton the same way; their
    residuals (or -1 when unvalidated) are reported in the stats.
    Returns (pieces, assign, fitted, W, parent, shared_ct)."""
    base_pieces = {}
    for gi, g in enumerate(groups):
        if g:
            pid = (gi, 0, len(runs[gi]))
            base_pieces[pid] = _piece_data(groups, runs, gi, 0, len(runs[gi]))
    total_verts = sum(len(g) for g in groups)
    cand_cache = {}
    def cands_of(pd):
        key = max(pd['gslots'])
        if key not in cand_cache:
            cand_cache[key] = _candidates(key)
        return cand_cache[key]
    def packet_slots(gi):
        out = []
        for (s, c) in runs[gi]:
            out.append({slot_of(i) for v in groups[gi][s:s+c] for i in v['infs']})
        return out
    pkt_slots = {gi: packet_slots(gi) for gi in range(len(groups)) if groups[gi]}
    def split_points(pid):
        gi, lo, hi = pid
        pts = []
        for mid in range(lo+1, hi):
            if pkt_slots[gi][mid] != pkt_slots[gi][mid-1]:
                pts.append(mid)
        return pts or list(range(lo+1, hi))
    def try_join(pd, W):
        """(proven, best_any): proven = (worst, cand, island_frames,
        mp, total_shared) with worst < 0.02, every island anchored
        and at least one validated; best_any scored for leftovers."""
        proven = None
        best_any = None
        for cand in cands_of(pd):
            mp, iframes, worst, nval, anchored, tshared = \
                _eval_candidate(pd, cand, W)
            if anchored and nval >= 1 and worst is not None and worst < 0.02:
                key = (1 if cand[0] == 'ID' else 0, worst)
                if proven is None or key < proven[0]:
                    proven = (key, cand, iframes, mp, tshared)
            score = (0 if anchored else 1,
                     1 if cand[0] == 'ID' else 0, -nval,
                     worst if worst is not None else 9e9)
            if best_any is None or score < best_any[0]:
                best_any = (score, cand, iframes, mp, worst, tshared)
        return proven, best_any
    def extend_W(pd, mp, iframes, W, parent):
        for isl, F in iframes:
            if F is None: continue
            for s in isl:
                bone = mp[s]
                if bone not in W and s in pd['L']:
                    W[bone] = F @ pd['L'][s]
                    lp = pd['lparent'].get(s, -1)
                    parent[bone] = mp[lp] if lp in mp else -1
    def grow(pieces, seed_pid, seed_cand):
        assign = {seed_pid: seed_cand}
        fitted = {}
        shared_ct = {}
        proven_pids = {seed_pid}
        pd0 = pieces[seed_pid]
        mp0 = _mapping(seed_cand, pd0['gslots'])
        W = {}
        parent = {}
        for isl in pd0['islands']:
            for s in isl:
                if s in pd0['L']:
                    bone = mp0[s]
                    W[bone] = pd0['L'][s]
                    lp = pd0['lparent'].get(s, -1)
                    parent[bone] = mp0[lp] if lp in mp0 else -1
        remaining = set(pieces) - {seed_pid}
        atomized = False
        bone_union = {}
        def union_of(pid):
            if pid not in bone_union:
                u = set()
                for cand in cands_of(pieces[pid]):
                    u |= set(_mapping(cand, pieces[pid]['gslots']).values())
                bone_union[pid] = u
            return bone_union[pid]
        eval_cache = {}
        eval_bones = {}
        def join_eval(pid):
            wb = set(W)
            if pid in eval_cache:
                newb = wb - eval_bones[pid]
                if not (newb & union_of(pid)):
                    return eval_cache[pid]
            res = try_join(pieces[pid], W)
            eval_cache[pid] = res
            eval_bones[pid] = wb
            return res
        while True:
            progress = False
            for pid in sorted(remaining):
                proven, _ba = join_eval(pid)
                if proven:
                    _key, cand, iframes, mp, tshared = proven
                    worst = _key[1]
                    assign[pid] = cand
                    fitted[pid] = worst
                    shared_ct[pid] = tshared
                    proven_pids.add(pid)
                    extend_W(pieces[pid], mp, iframes, W, parent)
                    remaining.discard(pid)
                    progress = True
            if progress: continue
            split_done = False
            for pid in sorted(remaining):
                gi, lo, hi = pid
                if hi - lo < 2: continue
                _pp, pba = join_eval(pid)
                p_anchored = pba is not None and pba[0][0] == 0
                for mid in split_points(pid):
                    a = (gi, lo, mid); b = (gi, mid, hi)
                    newkids = []
                    for child in (a, b):
                        if child not in pieces:
                            pieces[child] = _piece_data(groups, runs, *child)
                            newkids.append(child)
                    pa, ba = join_eval(a)
                    pb, bb = join_eval(b)
                    a_anch = ba is not None and ba[0][0] == 0
                    b_anch = bb is not None and bb[0][0] == 0
                    if pa or pb or (a_anch and b_anch and not p_anchored):
                        remaining.discard(pid)
                        remaining.add(a); remaining.add(b)
                        split_done = True
                        break
                    for child in newkids:
                        del pieces[child]
                        eval_cache.pop(child, None)
                        eval_bones.pop(child, None)
                if split_done: break
            if not split_done:
                if not atomized:
                    # Stage 2: a group can batch sub-objects whose
                    # packets do not share one palette, and a split
                    # is only kept when a child proves immediately --
                    # mutually dependent children deadlock that rule.
                    # Atomise every remaining multi-packet piece to
                    # single packets and let iterative growth sort
                    # them out against the trusted skeleton.
                    atomized = True
                    for pid in sorted(remaining):
                        gi, lo, hi = pid
                        if hi - lo < 2: continue
                        remaining.discard(pid)
                        for mid in range(lo, hi):
                            child = (gi, mid, mid+1)
                            if child not in pieces:
                                pieces[child] = _piece_data(groups, runs,
                                                            *child)
                            remaining.add(child)
                    continue
                break
        # NO leftover claiming inside a component: a piece leaves
        # the pool only by PROVING against a component skeleton.
        # Unproven pieces are handled by later components or by the
        # driver's final placement pass.
        placed = sum(len(pieces[pid]['verts']) for pid in assign)
        proven_verts = sum(len(pieces[pid]['verts']) for pid in proven_pids)
        return proven_verts, placed, assign, fitted, W, parent, shared_ct
    import os, time as _t
    _dbg = os.environ.get('UR_DEBUG')
    if _dbg: print(f'[dbg] pieces built {_t.process_time():.1f}s', file=sys.stderr, flush=True)
    def seed_choices(pd):
        """Seed candidates: growth outcomes are invariant under the
        seed's palette window/reversal (a shift relabels every
        joining candidate's window correspondingly), so only the
        palette FAMILY and the window edges matter. Try, per family:
        first window fwd/rev and last window fwd/rev.
        UR_FORCE_SEED='P27,0,False' restricts to one candidate
        (diagnostics: compare global solutions by face quality)."""
        forced = os.environ.get('UR_FORCE_SEED')
        if forced:
            nm, w0, rev = forced.split(',')
            return [(nm, int(w0), rev == 'True')]
        allc = cands_of(pd)
        seen = set()
        out = []
        fams = []
        for (name, w0, rev) in allc:
            if name not in fams: fams.append(name)
        for name in fams:
            ws = [w0 for (n2, w0, r2) in allc if n2 == name]
            for w0 in sorted({min(ws), max(ws)}):
                for rev in (False, True):
                    c = (name, w0, rev)
                    if c in allc and c not in seen:
                        seen.add(c); out.append(c)
        return out
    # Component driver: a character's pieces can reference several
    # disjoint bone sets (e.g. a body and a separately rigged
    # sub-object -- proven on chr01, whose grp0/1/2 island relations
    # match no bone pair of the main skeleton). Grow one trusted
    # component at a time, seeded by the largest unconsumed piece.
    # Consumption is tracked per (group, packet): when split or
    # atomised children of a group are assigned, the parent piece is
    # consumed too and can never be re-seeded or double-assembled.
    consumed = set()  # (gi, packet_idx)
    def pid_overlap(pid):
        gi, lo, hi = pid
        return sum(1 for k in range(lo, hi) if (gi, k) in consumed)
    def rebuild_remaining():
        """Assignment units must PARTITION the packets: drop fully
        consumed pieces, and replace partially consumed parents by
        per-packet pieces for their unconsumed packets only."""
        out = {}
        for pid, pd in remaining_pieces.items():
            gi, lo, hi = pid
            ov = pid_overlap(pid)
            if ov == 0:
                out[pid] = pd
            elif ov < hi - lo:
                for mid in range(lo, hi):
                    if (gi, mid) not in consumed:
                        child = (gi, mid, mid+1)
                        out[child] = _piece_data(groups, runs, *child)
        return out
    def seedable(pid):
        """A piece can only validate (and thus seed a component) if
        at least one of its islands has >=2 slots."""
        return any(len(isl) >= 2
                   for isl in remaining_pieces[pid]['islands'])
    remaining_pieces = dict(base_pieces)
    used = {}
    assign = {}
    fitted = {}
    sct = {}
    W = {}
    parent = {}
    n_comp = 0
    while remaining_pieces and n_comp < 8:
        remaining_pieces = rebuild_remaining()
        seedable_pids = [pid for pid in remaining_pieces if seedable(pid)]
        if not seedable_pids:
            break
        n_comp += 1
        seed_pid = max(seedable_pids,
                       key=lambda pid: len(remaining_pieces[pid]['verts']))
        comp_total = sum(len(pd['verts'])
                         for pd in remaining_pieces.values())
        best = None       # best real-record seed result
        best_id = None    # best identity-window seed result
        stale = 0
        for cand in seed_choices(remaining_pieces[seed_pid]):
            pieces = dict(remaining_pieces)
            proven, placed, a_c, f_c, W_c, p_c, s_c = \
                grow(pieces, seed_pid, cand)
            score = (proven, placed)
            if _dbg: print(f'[dbg] comp{n_comp} seed {seed_pid} {cand} proven={proven} placed={placed} cpu={_t.process_time():.1f}s', file=sys.stderr, flush=True)
            tgt = 'best_id' if cand[0] == 'ID' else 'best'
            cur = best_id if tgt == 'best_id' else best
            if cur is None or score > cur[0]:
                if tgt == 'best_id':
                    best_id = (score, pieces, a_c, f_c, W_c, p_c, s_c)
                else:
                    best = (score, pieces, a_c, f_c, W_c, p_c, s_c)
                stale = 0
            else:
                stale += 1
            if proven >= comp_total:
                break
            ref = best if best is not None else best_id
            if stale >= 3 and ref is not None and ref[0][0] >= 0.95 * comp_total:
                break
        if best is not None and best_id is not None and \
                best[0][0] < 0.95 * best_id[0][0]:
            best = best_id  # identity seed proves dramatically more
        elif best is None:
            best = best_id
        if best is None:
            break  # no candidate family covers the seed piece;
            # its pieces fall through to final placement / counted
        _score, pieces, a_c, f_c, W_c, p_c, s_c = best
        for bone, M in W_c.items():
            if bone not in W:
                W[bone] = M
                parent[bone] = p_c.get(bone, -1)
        for pid in a_c:
            used[pid] = pieces[pid]
            assign[pid] = a_c[pid]
            if pid in f_c: fitted[pid] = f_c[pid]
            if pid in s_c: sct[pid] = s_c[pid]
            gi, lo, hi = pid
            for k in range(lo, hi):
                consumed.add((gi, k))
            remaining_pieces.pop(pid, None)
        if not a_c:
            break  # cannot happen (seed always assigns) -- safety
    # Final placement pass: any piece never proven (e.g. single-slot
    # accessories, which can never validate -- their only island has
    # one slot) is placed per packet by its best-scoring candidate
    # against the merged skeleton, extending W island by island.
    # Residuals are reported in the stats; nothing here is silent.
    remaining_pieces = rebuild_remaining()
    for pid in sorted(list(remaining_pieces)):
        gi, lo, hi = pid
        for mid in range(lo, hi):
            child = (gi, mid, mid+1)
            if (gi, mid) in consumed:
                continue
            pd = _piece_data(groups, runs, *child)
            proven, ba = try_join(pd, W)
            pick = proven if proven else ba
            if pick is None:
                continue
            if proven:
                _key, cand, iframes, mp, tshared = proven
                worst = _key[1]
                fitted[child] = worst
            else:
                _sc, cand, iframes, mp, worst, tshared = ba
                if ba[0][0] != 0:
                    continue  # not anchored to the merged skeleton
                fitted[child] = -1.0 if worst is None else worst
            used[child] = pd
            assign[child] = cand
            sct[child] = tshared
            for isl, F in iframes:
                if F is None: continue
                for s in isl:
                    bone = mp[s]
                    if bone not in W and s in pd['L']:
                        W[bone] = F @ pd['L'][s]
                        lp = pd['lparent'].get(s, -1)
                        parent[bone] = mp[lp] if lp in mp else -1
            consumed.add((gi, mid))
    return used, assign, fitted, W, parent, sct

def write_glb(path, W, parent, verts, faces, char_name):
    # Export skeleton must be reflection-free: several bind frames
    # are mirrored (det -1), which armature importers (Blender)
    # cannot represent as bone transforms and explode the skin.
    # Negating one basis column of each mirrored frame makes det
    # +1 while keeping the joint translation; the vertex positions
    # are already in bind world space and the inverse-bind matrices
    # are computed from these same frames, so the skinned result
    # (sum w * NodeWorld * IBM * p = p) is unchanged exactly.
    W = {b: (M if np.linalg.det(M[:3, :3]) > 0 else
             M @ np.diag([-1.0, 1.0, 1.0, 1.0])) for b, M in W.items()}
    bones = sorted(W)
    bidx = {b: i for i, b in enumerate(bones)}
    n = len(verts)
    pos = np.array([v['p'] for v in verts], dtype=np.float32)
    nrm = np.array([v['n'] for v in verts], dtype=np.float32)
    ln = np.linalg.norm(nrm, axis=1, keepdims=True); ln[ln == 0] = 1
    nrm = (nrm / ln).astype(np.float32)
    uv = np.array([v['uv'] for v in verts], dtype=np.float32)
    joints = np.zeros((n, 4), dtype=np.uint16)
    weights = np.zeros((n, 4), dtype=np.float32)
    for i, v in enumerate(verts):
        for k in range(min(4, len(v['joints']))):
            joints[i, k] = bidx[v['joints'][k]]
            weights[i, k] = v['weights'][k]
        s = weights[i].sum()
        if s > 0: weights[i] /= s
    idx = np.array(faces, dtype=np.uint32).ravel()
    # glTF matrices are column-major in the buffer: store transposed.
    ibm = np.array([np.linalg.inv(W[b]).T for b in bones], dtype=np.float32)
    blobs = []
    views = []
    accessors = []
    def add(data, target, ctype, atype, count, minmax=None):
        raw = data.tobytes()
        off = sum(len(b) for b in blobs)
        blobs.append(raw)
        views.append({'buffer': 0, 'byteOffset': off, 'byteLength': len(raw),
                      'target': target})
        acc = {'bufferView': len(views)-1, 'componentType': ctype,
               'count': count, 'type': atype}
        if minmax: acc['min'], acc['max'] = minmax
        accessors.append(acc)
        return len(accessors)-1
    a_pos = add(pos, 34962, 5126, 'VEC3', n,
                (pos.min(axis=0).tolist(), pos.max(axis=0).tolist()))
    a_nrm = add(nrm, 34962, 5126, 'VEC3', n)
    a_uv = add(uv, 34962, 5126, 'VEC2', n)
    a_j = add(joints, 34962, 5123, 'VEC4', n)
    a_w = add(weights, 34962, 5126, 'VEC4', n)
    a_idx = add(idx, 34963, 5125, 'SCALAR', len(idx))
    a_ibm = add(ibm, None, 5126, 'MAT4', len(bones))
    def _par(b):
        # A recorded parent that is not itself in the skeleton
        # (possible when a piece's local parent slot maps to a bone
        # no piece placed) degrades to a root link; the world
        # matrices -- and therefore the skin -- are unaffected.
        p = parent.get(b, -1)
        return p if p in W else -1
    nodes = []
    for b in bones:
        par = _par(b)
        local = W[b] if par == -1 else np.linalg.inv(W[par]) @ W[b]
        node = {'name': f'bone_{b}',
                'matrix': [float(x) for x in local.T.ravel()]}
        nodes.append(node)
    for i, b in enumerate(bones):
        par = _par(b)
        if par != -1:
            nodes[bidx[par]].setdefault('children', []).append(i)
    mesh_node = {'name': char_name, 'mesh': 0, 'skin': 0}
    nodes.append(mesh_node)
    roots = [i for i, b in enumerate(bones) if _par(b) == -1]
    roots.append(len(nodes)-1)
    gltf = {
        'asset': {'version': '2.0', 'generator': 'ur_decode.py (western-heart)'},
        'scene': 0,
        'scenes': [{'nodes': roots}],
        'nodes': nodes,
        'meshes': [{'name': char_name, 'primitives': [{
            'attributes': {'POSITION': a_pos, 'NORMAL': a_nrm,
                           'TEXCOORD_0': a_uv, 'JOINTS_0': a_j,
                           'WEIGHTS_0': a_w},
            'indices': a_idx, 'mode': 4}]}],
        'skins': [{'inverseBindMatrices': a_ibm,
                   'joints': list(range(len(bones)))}],
        'accessors': accessors,
        'bufferViews': views,
        'buffers': [{'byteLength': sum(len(b) for b in blobs)}],
    }
    js = json.dumps(gltf).encode()
    js += b' ' * ((4 - len(js) % 4) % 4)
    binblob = b''.join(blobs)
    binblob += b'\0' * ((4 - len(binblob) % 4) % 4)
    with open(path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2,
                            12 + 8 + len(js) + 8 + len(binblob)))
        f.write(struct.pack('<II', len(js), 0x4E4F534A))
        f.write(js)
        f.write(struct.pack('<II', len(binblob), 0x004E4942))
        f.write(binblob)
    return {'verts': n, 'faces': len(faces), 'bones': len(bones)}

# ------------------------------------------------------------------ main --

def decode(ppk_path, glb_path, char_name):
    """Decode ONE character. All state is local to this call (the
    batch runs one process per character, so the module-level
    active palette set is per-character by construction)."""
    global _ACTIVE_PALETTES
    data = open(ppk_path, 'rb').read()
    vmd = read_vmd(data)
    pal = dict(PALETTES)
    # The character's own header records join the candidate families,
    # minus exact duplicates of the base tables (chr01's own records
    # ARE the base tables -- sweeping both copies would double the
    # seed search for zero new mappings).
    base = {tuple(v) for v in PALETTES.values()}
    base |= {tuple(v[::-1]) for v in PALETTES.values()}
    for name, vals in parse_header_palettes(vmd).items():
        if tuple(vals) not in base:
            pal[name] = vals
    _ACTIVE_PALETTES = pal
    groups, runs = parse_groups(vmd)
    # The identity (node-order) family is a last resort for pieces
    # whose slots exceed every real palette (e.g. char015 grp11,
    # maxslot 30 vs an 18-entry header record). Include it only
    # when some piece actually needs the reach.
    maxslot = -1
    for g in groups:
        for v in g:
            for inf in v['infs']:
                s = slot_of(inf)
                if s > maxslot: maxslot = s
    if maxslot >= max(len(P) for P in pal.values()):
        node_max = parse_node_max(vmd)
        pal['ID'] = list(range(node_max + 1))
        _ACTIVE_PALETTES = pal
    pieces, assign, fit_resid, W, parent, sct = \
        assign_by_trusted_fit(groups, runs)
    assign, W, parent = polish_by_faces(pieces, assign, W, parent)
    W, parent, verts, faces, frame_resid = assemble(pieces, assign,
                                                    W, parent)
    stats = write_glb(glb_path, W, parent, verts, faces, char_name)
    def pid_name(pid):
        gi, lo, hi = pid
        return f"g{gi}:{lo}-{hi}"
    stats['palette_families'] = sorted(pal.keys())
    stats['node_max'] = parse_node_max(vmd)
    stats['palette_provenance'] = {
        pid_name(pid): ('identity-window' if cand[0] == 'ID'
                        else 'record')
        for pid, cand in assign.items()}
    stats['groups'] = len([g for g in groups if g])
    stats['total_verts_parsed'] = sum(len(g) for g in groups)
    stats['placed_verts'] = stats['verts']
    stats['assignment'] = {pid_name(pid): list(c) for pid, c in assign.items()}
    stats['frame_residuals'] = {pid_name(k): round(float(v), 5)
                                for k, v in frame_resid.items()}
    stats['trusted_fit_residuals'] = {pid_name(k): round(float(v), 5)
                                      for k, v in fit_resid.items()}
    stats['trusted_fit_shared_bones'] = {pid_name(k): v
                                          for k, v in sct.items()}
    return stats

if __name__ == '__main__':
    ppk, glb = sys.argv[1], sys.argv[2]
    name = ppk.replace('\\', '/').split('/')[-1].replace('.ppk', '')
    st = decode(ppk, glb, name)
    print(json.dumps(st, indent=1))
