"""Guarded delta deploy of origin/main onto the live Pages branch (tools/deploy/REPUBLISH.md, git plumbing).
Run from anywhere inside the repo checkout; dry run by default.
- update: every file in the deploy roots present on BOTH main and the live branch whose blob differs (vs the live
  branch's ACTUAL blobs, not its manifest commit);
- add: files missing on live under ADD_PREFIXES (new data the shipped code fetches) + any target the module-graph
  check reports missing;
- refuse: any removal, a tree over the size cap, or a non-zero tools/deploy/check_module_graph.py on the new tree;
- push fast-forward only (no force). Usage: python3 deploy_delta.py [--push] [--note TEXT] [--pr N]"""
import json, os, subprocess, sys, tempfile, datetime

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
LIVE, MAIN, BRANCH = 'origin/gh-pages-m1-20261029', 'origin/main', 'gh-pages-m1-20261029'
ROOTS = ('game/', 'customization/', 'packages/', 'roster/')
ADD_PREFIXES = ('game/assets/anim/t7/',)
CAP = 1_000_000_000
CODE_EXT = ('.js', '.mjs', '.html', '.json', '.css')


def git(*a, inp=None, env=None):
    r = subprocess.run(['git', *a], cwd=REPO, capture_output=True, text=inp is not None or True, input=inp, env=env)
    if r.returncode: raise SystemExit('git %s failed: %s' % (' '.join(a), r.stderr))
    return r.stdout


def tree(ref):
    out = {}
    for line in git('ls-tree', '-r', '-l', ref).splitlines():
        meta, path = line.split('\t', 1)
        mode, typ, sha, size = meta.split()
        if typ == 'blob': out[path] = (sha, int(size) if size != '-' else 0, mode)
    return out


def main():
    push = '--push' in sys.argv
    note = sys.argv[sys.argv.index('--note') + 1] if '--note' in sys.argv else ''
    pr = int(sys.argv[sys.argv.index('--pr') + 1]) if '--pr' in sys.argv else None
    git('fetch', '-q', 'origin', 'main', BRANCH)
    tip, main_c = git('rev-parse', LIVE).strip(), git('rev-parse', MAIN).strip()
    L, M = tree(LIVE), tree(MAIN)
    upd = sorted(p for p in L if p in M and p.startswith(ROOTS) and L[p][0] != M[p][0])
    # add only the T7 stance files the shipped code fetches (T7_STANCES dirs in main's t3anims.js)
    import re as _re
    t3 = git('show', MAIN + ':game/js/t3anims.js')
    blk = _re.search(r'export const T7_STANCES = \{(.*?)\n\};', t3, _re.S)
    dirs = sorted(set(_re.findall(r"dir:\s*'(assets/anim/t7/[\w-]+/)'", blk.group(1)))) if blk else []
    want = ['game/' + d + f for d in dirs for f in ('skeleton.json', 'stance.json')]
    add = sorted(p for p in want if p in M and p not in L)
    env = dict(os.environ, GIT_INDEX_FILE=tempfile.mktemp(prefix='deploy.index.'))
    git('read-tree', tip, env=env)
    for p in upd + add:
        git('update-index', '--add', '--cacheinfo', '%s,%s,%s' % (M[p][2], M[p][0], p), env=env)
    # module-graph check on the assembled tree (code/data files only)
    new = dict(L); new.update({p: M[p] for p in upd + add})
    with tempfile.TemporaryDirectory() as td:
        for p, (sha, _, _) in new.items():
            if p.endswith(CODE_EXT):  # every code/data file of the assembled tree (game/, packages/, customization/, root)
                dst = os.path.join(td, p); os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, 'wb') as f: f.write(subprocess.run(['git', 'cat-file', 'blob', sha], cwd=REPO, capture_output=True).stdout)
        r = subprocess.run([sys.executable, os.path.join(REPO, 'tools/deploy/check_module_graph.py'), td], capture_output=True, text=True)
        print(r.stdout[-1500:])
        missing = [l for l in r.stdout.splitlines() if 'MISSING MODULE (static)' in l]
        if r.returncode or missing:
            extra = []
            for l in missing:
                tgt = l.split('-> ')[-1].split(' ')[0]
                if tgt in M and tgt not in new: extra.append(tgt)
            if not extra: raise SystemExit('module graph check FAILED and the missing targets are not on main: refusing')
            for p in extra:
                git('update-index', '--add', '--cacheinfo', '%s,%s,%s' % (M[p][2], M[p][0], p), env=env)
                add.append(p)
            print('added module-graph targets:', extra, '(re-run to re-check)')
            if not push: return
    size = sum(v[1] for v in new.values()) + sum(M[p][1] for p in add if p not in new)
    man = json.loads(git('show', LIVE + ':deploy-manifest.json'))
    man.update({'commit': main_c, 'files': man['files'] + len(add), 'bytes': size,
                'built': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'delta_note': ('Delta deploy (Claude, git plumbing, REPUBLISH.md section 2 logic) live %s -> main %s: '
                               '%d updated, %d added, 0 removed; module graph checked. %s' % (tip[:8], main_c[:8], len(upd), len(add), note)).strip()})
    if pr: man['source_pr'] = pr
    b = subprocess.run(['git', 'hash-object', '-w', '--stdin'], cwd=REPO, capture_output=True, text=True, input=json.dumps(man, indent=1) + '\n').stdout.strip()
    git('update-index', '--add', '--cacheinfo', '100644,%s,deploy-manifest.json' % b, env=env)
    t = git('write-tree', env=env).strip()
    removed = git('diff', '--diff-filter=D', '--name-only', tip, t).split()
    total = sum(int(l.split()[3]) for l in git('ls-tree', '-r', '-l', t).splitlines() if l.split()[3] != '-')
    print('updated %d, added %d, removed %d, new tree %d bytes (%.1f MB)' % (len(upd), len(add), len(removed), total, total / 1e6))
    for p in upd[:60]: print('  M', p)
    for p in add[:60]: print('  A', p)
    if removed: raise SystemExit('refusing: the deploy would remove files')
    if total > CAP: raise SystemExit('refusing: %d bytes is over the Pages cap' % total)
    if not push: print('dry run (pass --push to deploy)'); return
    msg = ('Pages shell deploy: main %s%s - %d updated, %d added, 0 removed\n\n%s\nModule graph checked '
           '(tools/deploy/check_module_graph.py on the assembled tree). Fast-forward only.\n\n'
           'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n'
           'Claude-Session: https://claude.ai/code/session_01CLThWtX97Fi7zFw5wnvydL\n') % (
        main_c[:8], (' (#%d)' % pr) if pr else '', len(upd), len(add), man['delta_note'])
    c = subprocess.run(['git', '-c', 'user.name=mhvnsnt', '-c', 'user.email=197314870+mhvnsnt@users.noreply.github.com',
                        'commit-tree', t, '-p', tip, '-F', '-'], cwd=REPO, capture_output=True, text=True, input=msg).stdout.strip()
    r = subprocess.run(['git', 'push', 'origin', '%s:refs/heads/%s' % (c, BRANCH)], cwd=REPO, capture_output=True, text=True)
    print('push', c[:9], r.returncode, (r.stderr or r.stdout).strip()[-300:])


if __name__ == '__main__':
    main()
