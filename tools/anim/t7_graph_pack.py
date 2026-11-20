#!/usr/bin/env python3
"""t7_graph_pack.py: ship EVERY clip a fighter's imported T7 graph reaches as deterministic shards the game loads
(game/js/t3anims.js loadT7GraphClips). Reuses the resumable bake cache of tools/anim/t7_graph_bake.py as is (rotations
and root_t are copied byte-for-value, never re-baked) and adds one channel per clip: root_motion_fwd_m, the forward
travel from the RAW T7 root channel (slot 0 z, mm -> m), exactly as tools/anim/t7_move_bake.py derives it for the
shipped moves pack (0x64 clips through the game's own sampler, T7_EXE). That channel is cached per clip in
<cache>/root/ (resumable). Lateral travel stays 0 (its sign is not proven), the same as every shipped T7 clip.
Shards: clips in graph breadth-first order from the stance (cancel-table order, then the move's transition), packed
greedily into files of at most --shard-bytes (well under Cloudflare Pages' 25 MiB per-file limit and jsDelivr's 20 MB
per-file limit). Same inputs -> byte-identical shards + index (sha256 per shard recorded).
usage: T7_EXE=<exe> python3 tools/anim/t7_graph_pack.py --graph game/assets/anim/t7/king/graph.json \
         --coverage game/assets/anim/t7/king/graph.coverage.json --cache <bake cache> --mothead <mothead> --code kin \
         --out-dir game/assets/anim/t7/king/graph-clips [--shard-bytes 6000000] [--jobs 6]"""
import argparse, hashlib, json, os, sys
from concurrent.futures import ProcessPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ARC = {'rotsm': 'mask/{code}rotsm.arc', 'motbin': 'bin/{code}mot.bin', 'common': 'mask/common.arc'}
FORMAT = 'wh-t7-graph-clips/1'


def resolve(g, mid):
    return g['aliases'][mid - 0x8000] if mid >= 0x8000 and mid - 0x8000 < len(g['aliases']) else mid


def bfs_clip_order(g, reachable):
    """Clip keys in breadth-first order from the stance (every edge, any requirement), then any reachable rest."""
    order, seen_c, seen_m = [], set(), set()
    q = [g['stance']] + [resolve(g, 0x8000 + i) for i in range(len(g['aliases']))]
    h = 0
    while h < len(q):
        m = q[h]; h += 1
        if m in seen_m or m >= len(g['moves']): continue
        seen_m.add(m); mv = g['moves'][m]
        k = '%s_%s' % (mv['bank'], mv['clip'])
        if mv['clip'] is not None and k not in seen_c: seen_c.add(k); order.append(k)
        for r in mv['cancels']: q.append(resolve(g, r[9]))
        q.append(resolve(g, mv['transition']))
    for b, c, _f in reachable:
        k = '%s_%s' % (b, c)
        if k not in seen_c: seen_c.add(k); order.append(k)
    return order


def root_channel(job):
    key, arc, clip, cache = job
    out = os.path.join(cache, 'root', key + '.json')
    if os.path.exists(out): return key, json.load(open(out))
    import t7_c8_stance_bake as B
    raw = B.decode_c8(arc, clip)
    z0 = raw[0][2]
    fwd = [round((f[2] - z0) / 1000.0, 5) for f in raw]
    tmp = out + '.tmp'; json.dump(fwd, open(tmp, 'w')); os.replace(tmp, out)
    return key, fwd


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ('--graph', '--coverage', '--cache', '--mothead', '--code', '--out-dir'): ap.add_argument(k, required=True)
    ap.add_argument('--shard-bytes', type=int, default=6000000); ap.add_argument('--jobs', type=int, default=6)
    ap.add_argument('--fighter', default='pantera')
    a = ap.parse_args()
    g = json.load(open(a.graph)); cov = json.load(open(a.coverage))
    order = bfs_clip_order(g, cov['reachable_clips'])
    os.makedirs(os.path.join(a.cache, 'root'), exist_ok=True)
    missing = [k for k in order if not os.path.exists(os.path.join(a.cache, k + '.json'))]
    if missing: sys.exit('bake cache is missing %d reachable clips (run t7_graph_bake.py first): %s' % (len(missing), missing[:10]))
    if not os.environ.get('T7_EXE'): sys.exit('T7_EXE=<TekkenGame-Win64-Shipping.exe> is required (0x64 root channels)')
    jobs = []
    for k in order:
        bank, clip = k.rsplit('_', 1)
        jobs.append((k, os.path.join(a.mothead, ARC[bank].format(code=a.code)), int(clip), a.cache))
    roots = {}
    with ProcessPoolExecutor(a.jobs) as ex:
        for i, (k, fwd) in enumerate(ex.map(root_channel, jobs, chunksize=4)):
            roots[k] = fwd
            if i % 100 == 0: print('root channel', i, '/', len(jobs), flush=True)
    os.makedirs(a.out_dir, exist_ok=True)
    gsha = hashlib.sha256(open(a.graph, 'rb').read()).hexdigest()
    shards, cur, cur_bytes, clips_ix = [], {}, 0, {}
    def flush():
        nonlocal cur, cur_bytes
        if not cur: return
        n = len(shards)
        name = 'clips.%02d.json' % n
        body = json.dumps({'format': FORMAT, 'shard': n, 'graph_sha256': gsha, 'clips': cur},
                          separators=(',', ':'), sort_keys=True).encode()
        open(os.path.join(a.out_dir, name), 'wb').write(body)
        shards.append({'file': name, 'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest(), 'clips': list(cur)})
        cur, cur_bytes = {}, 0
    for k in order:
        d = json.load(open(os.path.join(a.cache, k + '.json')))
        if not (d.get('fk_selfcheck_max_m', 1) <= 1e-5): sys.exit('%s: FK self-check %r' % (k, d.get('fk_selfcheck_max_m')))
        if d.get('format') != 'wh-anim/1': sys.exit('%s: format %r' % (k, d.get('format')))
        n = len(d['root_t'])
        if len(roots[k]) != n: sys.exit('%s: root channel %d frames, clip %d' % (k, len(roots[k]), n))
        d['loop'] = False; d['anim_set'] = 'FIGHT'; d['root_motion_fwd_m'] = roots[k]
        sz = len(json.dumps(d, separators=(',', ':'), sort_keys=True))
        if cur and cur_bytes + sz > a.shard_bytes: flush()
        cur[k] = d; cur_bytes += sz + len(k) + 4
        clips_ix[k] = {'frames': n, 'shard': len(shards)}
    flush()
    index = {'format': FORMAT, 'fighter': a.fighter, 'skeleton': '../skeleton.json', 'graph': '../graph.json',
             'graph_sha256': gsha, 'fps': 60, 'clip_count': len(order), 'total_bytes': sum(s['bytes'] for s in shards),
             'max_shard_bytes': max(s['bytes'] for s in shards), 'shard_limit_bytes': a.shard_bytes,
             'root_motion': 'root_motion_fwd_m = raw T7 root channel z (mm/1000) per frame, as tools/anim/t7_move_bake.py; lateral 0 (sign unproven)',
             'source_cache': 'tools/anim/t7_graph_bake.py cache (rotations/root_t copied, not re-baked)',
             'shards': shards, 'clips': clips_ix}
    json.dump(index, open(os.path.join(a.out_dir, 'index.json'), 'w'), separators=(',', ':'), sort_keys=True)
    print('GRAPH_PACK clips', len(order), 'shards', len(shards), 'total', index['total_bytes'], 'max shard', index['max_shard_bytes'])


if __name__ == '__main__':
    main()
