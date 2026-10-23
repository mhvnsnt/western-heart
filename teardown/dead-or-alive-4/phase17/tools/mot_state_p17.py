#!/usr/bin/env python3
"""DOA4 phase 17 Job 3 (DATA route): stateful per-item length-rule tests.

Baseline framing (phase 16, PROVEN): a .mot sub-block is a stream of
items; item = u16 BE tag + k data u16s (item spans 1+k u16s). Phase 16
FALSIFIED k as a pure function of the tag. This tool runs generalized
constraint propagation for STATEFUL rule classes:

  class 0   k = f(tag)                        (phase-16 control)
  class i   k = f(tag, previous item's tag)   (start state = None)
  class ii  k = f(tag, item index mod K)      for K in 2..6
  class iv  k = f(tag, block's first u16)     (per-sub-block header state)
  class v   k = f(tag, channel index)         (bonus: channel state)

Method per class: iterate to a fixpoint — for every block, a
forward/backward DP over (position, state) finds every
(state, tag, k) transition used by SOME exact tiling consistent
with the current allowed-transition set; the corpus-wide
intersection of used transitions shrinks the allowed set. A class
is FALSIFIED when blocks stop tiling (dead > 0) while the allowed
set is still non-deterministic, or when the intersection empties a
needed transition. A class is a CANDIDATE only if the fixpoint is
deterministic (one k per (state, tag)) with zero dead blocks; the
candidate is then scored by exact-tile rate under the frozen
deterministic table.

Usage: mot_state_p17.py <mot_dir> <class> [K] [scope]
  scope: triple (zack/m_zack/c_zack only) | full (+ all t_* files)
Output: JSON report to stdout.
"""
import json, os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mot_parse_p17 import parse_fighter, parse_t

def corpus(mot_dir, scope):
    for name in ('zack.mot', 'm_zack.mot', 'c_zack.mot'):
        b, tab, ds, recs = parse_fighter(os.path.join(mot_dir, name))
        for r in recs:
            for ch, (off, sz) in enumerate(r['subs']):
                if sz >= 4:
                    yield name, ch, b[off:off + sz]
    if scope == 'full':
        for name in sorted(os.listdir(mot_dir)):
            if name.startswith('t_'):
                b, pairs, recs = parse_t(os.path.join(mot_dir, name))
                for r in recs:
                    for ch, (off, sz) in enumerate(r['subs']):
                        if sz >= 4:
                            yield name, ch, b[off:off + sz]

def make_statefns(cls, K=None):
    """Return (init_state(block, ch), step(state, tag, item_index))."""
    if cls == '0':
        return (lambda blk, ch: 0), (lambda st, tag, i: 0)
    if cls == 'i':
        return (lambda blk, ch: -1), (lambda st, tag, i: tag)
    if cls == 'ii':
        return (lambda blk, ch: 0), (lambda st, tag, i: (i + 1) % K)
    if cls == 'iv':
        return (lambda blk, ch: struct.unpack_from('>H', blk, 0)[0]), (lambda st, tag, i: st)
    if cls == 'v':
        return (lambda blk, ch: ch), (lambda st, tag, i: st)
    raise ValueError(cls)

def used_transitions(words, init_state, step, allowed, kset=(1, 2)):
    """Set of (state, tag, k) used by some exact tiling of words
    under the allowed set (None = all allowed), or None if the
    block cannot tile."""
    m = len(words)
    # forward reachable states per position: list of dict state->item_index
    fwd = [dict() for _ in range(m + 1)]
    fwd[0][init_state] = 0
    for i in range(m):
        if not fwd[i]:
            continue
        tag = words[i]
        for st, cnt in fwd[i].items():
            for k in kset:
                j = i + 1 + k
                if j <= m and (allowed is None or (st, tag, k) in allowed):
                    ns = step(st, tag, cnt)
                    if ns not in fwd[j]:
                        fwd[j][ns] = cnt + 1
    if not fwd[m]:
        return None
    # backward completable (position, state)
    bwd = [set() for _ in range(m + 1)]
    bwd[m] = set(fwd[m].keys())
    for i in range(m - 1, -1, -1):
        if not fwd[i]:
            continue
        tag = words[i]
        for st, cnt in fwd[i].items():
            for k in kset:
                j = i + 1 + k
                if j <= m and (allowed is None or (st, tag, k) in allowed):
                    ns = step(st, tag, cnt)
                    if ns in bwd[j]:
                        bwd[i].add(st)
    used = set()
    for i in range(m):
        tag = words[i]
        for st, cnt in fwd[i].items():
            if st not in bwd[i]:
                continue
            for k in kset:
                j = i + 1 + k
                if j <= m and (allowed is None or (st, tag, k) in allowed):
                    if step(st, tag, cnt) in bwd[j]:
                        used.add((st, tag, k))
    return used

def run(mot_dir, cls, K, scope, kset=(1, 2)):
    init_fn, step = make_statefns(cls, K)
    blocks = []
    for name, ch, blk in corpus(mot_dir, scope):
        words = struct.unpack(f'>{len(blk) // 2}H', blk)
        blocks.append((init_fn(blk, ch), words))
    print(f'corpus blocks: {len(blocks)}', file=sys.stderr)
    allowed = None
    for it in range(16):
        inter = None
        dead = 0
        for init_state, words in blocks:
            u = used_transitions(words, init_state, step, allowed, kset)
            if u is None:
                dead += 1
                continue
            inter = u if inter is None else (inter & u)
        if inter is None:
            inter = set()
        # determinism: (state, tag) -> set of k in the intersection
        bykey = {}
        if allowed is not None:
            # only transitions still allowed can be 'used'; the effective
            # table is allowed restricted to keys seen in inter
            keys = {(s, t) for (s, t, k) in inter}
            for (s, t, k) in allowed:
                if (s, t) in keys:
                    bykey.setdefault((s, t), set()).add(k)
        else:
            for (s, t, k) in inter:
                bykey.setdefault((s, t), set()).add(k)
        amb = {kk: sorted(v) for kk, v in bykey.items() if len(v) > 1}
        new_allowed = inter if allowed is None else (allowed & inter) | {
            (s, t, k) for (s, t, k) in allowed if (s, t) not in {(a, b) for (a, b, _) in inter}}
        # simpler + sound: allowed becomes exactly the transitions that
        # survive in some tiling of every block = inter when inter covers
        # all keys; blocks that never use a transition do not falsify it,
        # so the correct shrink is: allowed_{n+1} = allowed_n minus
        # transitions whose (state,tag) key was exercised in some block
        # but never with that k in ANY tiling of that block. The
        # per-block used sets already encode that; the global object to
        # intersect is per-key k-sets:
        ksets = {}
        for init_state, words in blocks:
            u = used_transitions(words, init_state, step, allowed, kset)
            if u is None:
                continue
            local = {}
            for (s, t, k) in u:
                local.setdefault((s, t), set()).add(k)
            for kk, vv in local.items():
                ksets[kk] = vv if kk not in ksets else (ksets[kk] & vv)
        new_allowed = {(s, t, k) for (s, t), vv in ksets.items() for k in vv}
        changed = (new_allowed != allowed)
        amb2 = {kk: sorted(v) for kk, v in ksets.items() if len(v) > 1}
        print(f'iter {it}: keys {len(ksets)}, ambiguous keys {len(amb2)}, dead blocks {dead}', file=sys.stderr)
        allowed = new_allowed
        if not changed:
            break
    # final scoring: tile every block deterministically if table is a function
    ksets = {}
    for (s, t, k) in allowed:
        ksets.setdefault((s, t), set()).add(k)
    deterministic = all(len(v) == 1 for v in ksets.values())
    report = {'class': cls, 'K': K, 'scope': scope, 'blocks': len(blocks),
              'keys': len(ksets), 'deterministic': deterministic,
              'ambiguous_keys': sum(1 for v in ksets.values() if len(v) > 1),
              'dead_blocks_final': dead, 'kset': list(kset)}
    if deterministic:
        table = {kk: next(iter(v)) for kk, v in ksets.items()}
        ok = 0
        for init_state, words in blocks:
            st = init_state; i = 0; cnt = 0; good = True
            while i < len(words):
                k = table.get((st, words[i]))
                if k is None or i + 1 + k > len(words):
                    good = False; break
                st = step(st, words[i], cnt); cnt += 1; i += 1 + k
            if good and i == len(words):
                ok += 1
        report['exact_tile_rate'] = ok / len(blocks)
        report['exact_tile'] = ok
    json.dump(report, sys.stdout, indent=1)
    print()

if __name__ == '__main__':
    mot_dir, cls = sys.argv[1], sys.argv[2]
    K = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] != '-' else None
    scope = sys.argv[4] if len(sys.argv) > 4 else 'triple'
    kset = tuple(int(c) for c in sys.argv[5]) if len(sys.argv) > 5 else (1, 2)
    run(mot_dir, cls, K, scope, kset)
