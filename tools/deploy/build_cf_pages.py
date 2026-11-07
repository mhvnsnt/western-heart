#!/usr/bin/env python3
"""tools/deploy/build_cf_pages.py — build the Cloudflare Pages site (no 1 GB cap) from a committed ref.

Why (owner 2026-11-06: "a free fix for my cap on my storage for game assets to the deployable build the top industry
standard way"): GitHub Pages caps a published site at 1 GB and the live tree reached it exactly (1,000.0 MB on
2026-11-06), so main could no longer deploy at all (tools/deploy/deploy_delta.py: "refusing: 1003796545 bytes is over the
Pages cap"). Cloudflare Pages (free plan) has no total-size cap and unlimited bandwidth on Cloudflare's CDN; its limits
are 20,000 files per deployment and 25 MiB per file. The game's full reference closure (the same one build_pages.py
computes for GitHub Pages) is ~8,000 files / ~6.2 GB, of which ~7,930 files / ~3.1 GB are <= 25 MiB. Those all ship here;
the larger ones keep loading through game/js/asset-config.js's remote base / jsDelivr candidates and are listed in
OUT/cf-oversize.json (each is a compression job: meshopt + texture resize brings a model under 25 MiB).

Works in a blob:none partial clone (CI: actions/checkout with filter: blob:none): only the blobs the site needs are
fetched, in batches, then streamed out with `git cat-file --batch` — never the whole 14 GB tree.

    python3 tools/deploy/build_cf_pages.py --ref HEAD --out cf-site
    npx wrangler@4.150.0 pages deploy cf-site --project-name western-heart --branch main
(.github/workflows/deploy-cloudflare-pages.yml runs both on every push to main.)
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_pages as B  # noqa: E402  (the same closure the GitHub Pages deploy uses)

CF_FILE_MAX = 25 * 1024 * 1024
CF_FILE_COUNT_MAX = 20000

ROOT_INDEX = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Western Heart</title>
<meta http-equiv="refresh" content="0; url=game/index.html">
<style>html,body{margin:0;background:#05070c;color:#f2f4f8;font-family:system-ui,sans-serif}
a{color:#f2c14e}main{padding:24px}</style></head>
<body><main><a href="game/index.html">Play Western Heart</a></main>
<script>location.replace('game/index.html' + location.search + location.hash);</script>
</body></html>
"""

# A top-level 404.html switches Cloudflare Pages OFF its single-page-app fallback (2026-11-07). Without it, Pages answers
# every missing path with index.html + HTTP 200, so the game's "page copy first, then remote / jsDelivr" loaders read
# HTML as JSON / GLB and fail ("Unexpected token '<', \"<!doctype \"... is not valid JSON" on the first live fight: the
# 74 files over 25 MiB are never on this site and must 404 to fall through). With it, missing paths return a real 404.
NOT_FOUND = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Not found</title></head>
<body style="background:#05070c;color:#f2f4f8;font-family:system-ui,sans-serif">
<p>Not found. <a href="/game/" style="color:#f2c14e">Play Western Heart</a></p></body></html>
"""

# Cache rules (Cloudflare Pages _headers): code and data revalidate so a deploy is seen at once; heavy binary assets
# are cached a day at the edge and in the browser (they change by path when a model is re-rigged, e.g. -refit.glb).
HEADERS = """/game/js/*
  Cache-Control: public, max-age=0, must-revalidate
/game/data/*
  Cache-Control: public, max-age=0, must-revalidate
/*.html
  Cache-Control: public, max-age=0, must-revalidate
/*.glb
  Cache-Control: public, max-age=86400
  Access-Control-Allow-Origin: *
/*.mp3
  Cache-Control: public, max-age=86400
  Access-Control-Allow-Origin: *
/*.ogg
  Cache-Control: public, max-age=86400
  Access-Control-Allow-Origin: *
"""


def git(*args, inp=None, binary=False, env=None):
    r = subprocess.run(['git', *args], input=inp, capture_output=True, env=env, text=not binary)
    if r.returncode:
        raise SystemExit('git %s failed: %s' % (' '.join(args[:3]), (r.stderr if not binary else r.stderr.decode())[:400]))
    return r.stdout


def fetch_missing(oids):
    """Batch-fetch blobs a blob:none clone does not have yet (2,000 per fetch, like build_pages.prefetch_text)."""
    env = dict(os.environ, GIT_NO_LAZY_FETCH='1')
    out = subprocess.run(['git', 'cat-file', '--batch-check=%(objectname) %(objecttype)'],
                         input='\n'.join(oids) + '\n', capture_output=True, text=True, env=env).stdout
    miss = [line.split()[0] for line in out.splitlines() if line.endswith(' missing')]
    for i in range(0, len(miss), 2000):
        subprocess.run(['git', '-c', 'fetch.negotiationAlgorithm=noop', 'fetch', '-q', '--no-tags',
                        '--no-write-fetch-head', '--filter=blob:none', 'origin', *miss[i:i + 2000]], check=True)
    return len(miss)


def write_blobs(pairs, out):
    """Stream every (path, oid) out of the object store with one `git cat-file --batch`. A blob whose real size is over
    the Cloudflare per-file limit (its size was unknown when planned) is skipped and returned, never uploaded."""
    skipped = []
    p = subprocess.Popen(['git', 'cat-file', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for path, oid in pairs:
        p.stdin.write((oid + '\n').encode())
        p.stdin.flush()
        header = p.stdout.readline().decode().split()
        if len(header) < 3 or header[1] != 'blob':
            raise SystemExit('cannot read %s (%s)' % (path, ' '.join(header)))
        size = int(header[2])
        data = p.stdout.read(size)
        p.stdout.read(1)  # trailing LF
        if size > CF_FILE_MAX:
            skipped.append([path, size])
            continue
        dst = os.path.join(out, path)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'wb') as f:
            f.write(data)
    p.stdin.close()
    p.wait()
    return skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', default='HEAD')
    ap.add_argument('--out', required=True)
    ap.add_argument('--list-only', action='store_true', help='print the plan, fetch and write nothing')
    a = ap.parse_args()
    t0 = time.time()
    sha = git('rev-parse', a.ref).strip()
    sizes, oids = B.blob_sizes(sha)
    B.prefetch_text(oids)
    r = B.compute_deploy_files(sha, sizes, oids)
    files = r[0] if isinstance(r, tuple) else r
    ship = [f for f in files if sizes[f] <= CF_FILE_MAX]
    over = sorted(([f, sizes[f]] for f in files if sizes[f] > CF_FILE_MAX), key=lambda x: -x[1])
    total = sum(sizes[f] for f in ship)
    print('ref %s: closure %d files; Cloudflare site %d files %.1f MB; %d over 25 MiB (%.1f MB) stay on the remote '
          'candidates' % (sha[:10], len(files), len(ship), total / 1e6, len(over), sum(s for _, s in over) / 1e6))
    if len(ship) + 3 > CF_FILE_COUNT_MAX:
        raise SystemExit('refusing: %d files is over the Cloudflare Pages per-deployment limit' % len(ship))
    if a.list_only:
        return
    os.makedirs(a.out, exist_ok=True)
    n = fetch_missing(sorted({oids[f] for f in ship}))
    print('fetched %d blobs' % n)
    late = write_blobs([(f, oids[f]) for f in ship], a.out)
    if late:
        print('skipped %d files over 25 MiB whose size was unknown at planning time' % len(late))
        over = sorted(over + late, key=lambda x: -x[1])
    with open(os.path.join(a.out, 'index.html'), 'w') as f:
        f.write(ROOT_INDEX)
    with open(os.path.join(a.out, '404.html'), 'w') as f:
        f.write(NOT_FOUND)
    with open(os.path.join(a.out, '_headers'), 'w') as f:
        f.write(HEADERS)
    with open(os.path.join(a.out, 'cf-oversize.json'), 'w') as f:
        json.dump({'_doc': 'Closure files over Cloudflare Pages 25 MiB per-file limit: not on this site; the game '
                   'loads them through game/js/asset-config.js remote / jsDelivr candidates.', 'ref': sha,
                   'files': over}, f, indent=1)
    with open(os.path.join(a.out, 'deploy-manifest.json'), 'w') as f:
        json.dump({'ref': sha, 'host': 'cloudflare-pages', 'files': len(ship), 'bytes': total,
                   'built': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}, f, indent=1)
    print('wrote %s in %.0f s' % (a.out, time.time() - t0))


if __name__ == '__main__':
    main()
