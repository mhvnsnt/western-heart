#!/usr/bin/env python3
"""Create the Fill 3 PR #1 branch via the Git Data API (no local clone)."""
import subprocess, json, base64, os, sys

REPO = 'mhvnsnt/western-heart'
W = os.path.expanduser('~/workspace/_fill3-ttt2-20261106/work')
MAIN = '0eb3c193a91699b9fcb207ae51207e82a4ea6b11'
BRANCH = 'fill3-ttt2-joins-v2'

def gh_api(path, payload=None, method=None):
    cmd = ['gh', 'api', f'repos/{REPO}/{path}']
    if payload is not None:
        cmd += ['--input', '-']
        data = json.dumps(payload).encode()
    else:
        data = None
    if method: cmd += ['--method', method]
    import time
    for attempt in range(5):
        r = subprocess.run(cmd, input=data, capture_output=True)
        if r.returncode == 0:
            return json.loads(r.stdout) if r.stdout.strip() else {}
        err = r.stderr.decode()[:300]
        if any(k in err for k in ('502', 'TLS', 'timeout', 'EOF', 'connection')) and attempt < 4:
            print('retry', attempt + 1, path, err[:80]); time.sleep(3 * (attempt + 1)); continue
        print('FAILED', path, err); sys.exit(1)

commit = gh_api(f'git/commits/{MAIN}')
base_tree = commit['tree']['sha']
print('base tree', base_tree)

try:
    gh_api('git/refs', {'ref': f'refs/heads/{BRANCH}', 'sha': MAIN})
    print('branch created')
except SystemExit:
    print('branch may exist; continuing')

files = []
for f in sorted(os.listdir(os.path.join(W, 'joins-final'))):
    files.append((os.path.join(W, 'joins-final', f), f'docs/tech/ttt2-mota/join/{f}'))
files.append((os.path.join(W, 'bank-tables-updated.json'), 'docs/tech/ttt2-mota/join/bank-tables.json'))
files.append((os.path.join(W, 'FILL3-JOINS-AND-TABLES.md'), 'docs/tech/ttt2-mota/join/FILL3-JOINS-AND-TABLES.md'))

tree_items = []
for local, remote in files:
    raw = open(local, 'rb').read()
    blob = gh_api('git/blobs', {'content': base64.b64encode(raw).decode(), 'encoding': 'base64'})
    tree_items.append({'path': remote, 'mode': '100644', 'type': 'blob', 'sha': blob['sha']})
    print('blob', remote, len(raw), blob['sha'][:10])

tree = gh_api('git/trees', {'base_tree': base_tree, 'tree': tree_items})
new_commit = gh_api('git/commits', {
    'message': 'Fill 3 (TTT2): joins for the remaining 63 motbin blocks + bank-1 tables for 65/66 characters\n\n'
               '63 new ttt2-join/1 files (125,784 records) built from held data006 via pair-12 parses '
               'cross-validated against +0x10 self-index extent chains (Roger gate: 2160/2160 agreement '
               'with the shipped join). bank-tables.json gains fill3_bank1_tables: data005 bank-1 MOTA '
               'table offsets/counts located by clip-fingerprint matching (Jun gate 35/41 exact). '
               'ANNA bank-1 table is a named gap (not in held data005; PS3 copy is the fallback). '
               'No deletions; shipped roger/jun/unknown joins untouched.',
    'tree': tree['sha'], 'parents': [MAIN]})
gh_api(f'git/refs/heads/{BRANCH}', {'sha': new_commit['sha'], 'force': False}, method='PATCH')
print('commit', new_commit['sha'])
json.dump({'branch': BRANCH, 'commit': new_commit['sha'], 'files': len(files)},
          open(os.path.join(W, 'pr1.json'), 'w'))
