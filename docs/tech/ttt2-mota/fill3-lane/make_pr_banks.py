"""Upload one batch of completed Fill-3 banks (bake clips + skeleton +
rows.pack.json + hit_frames.json) plus per-bank proof reports to
mhvnsnt/western-heart via the Git Data API and open the PR.
Usage: python3 make_pr_banks.py <batch_no> <bank> [<bank> ...]
Reads work/bake-summary data from work/out/<bank>/bake-report.json and
work/rows-reports/<bank>.json (both must exist), and the generalized
rows tool + slot mapper on batch 1 only (later batches: data only).
"""
import base64, json, os, subprocess, sys, time

W = os.path.expanduser('~/workspace/_fill3-ttt2-20261106/work')
REPO = 'mhvnsnt/western-heart'
# Existing Tekken-3/T7 bank dirs on main that must never be overwritten:
# colliding TTT2 banks land inert at <stem>_ttt2 (FILL3-BANKS.md rule).
COLLIDERS = {'anna', 'bosconovitch', 'bryan', 'eddy', 'heihachi', 'hwoarang',
             'jin', 'julia', 'kuma', 'law', 'nina', 'ogre', 'paul', 'raven', 'yoshimitsu'}


def repo_dir(stem):
    return stem + '_ttt2' if stem in COLLIDERS else stem


def gh_api(path, method='GET', payload=None, tries=5):
    for t in range(tries):
        cmd = ['gh', 'api', f'repos/{REPO}/{path}']
        if method != 'GET':
            cmd += ['-X', method, '--input', '-']
        r = subprocess.run(cmd, input=json.dumps(payload) if payload else None,
                           capture_output=True, text=True)
        if r.returncode == 0:
            return json.loads(r.stdout) if r.stdout.strip() else {}
        print('gh api retry', t, path, r.stderr.strip()[:160], flush=True)
        time.sleep(4 * (t + 1))
    raise SystemExit('gh api failed: ' + path)


def blob(content_bytes):
    return gh_api('git/blobs', 'POST', {
        'content': base64.b64encode(content_bytes).decode(), 'encoding': 'base64'})['sha']


def main():
    batch = sys.argv[1]
    banks = sys.argv[2:]
    assert banks, 'no banks'
    files = []          # (repo_path, local_path)
    stats = {}
    for b in banks:
        out = os.path.join(W, 'out', b)
        rep = json.load(open(os.path.join(out, 'bake-report.json')))
        rows = json.load(open(os.path.join(W, 'rows-reports', b + '.json')))
        stats[b] = {'clips_baked': len(rep['baked']), 'clips_skipped': len(rep['skipped']),
                    'slot_gaps': len(rep['gaps']), 'pack_rows': rows['pack_rows'],
                    'hit_rows': rows['hit_rows'], 'rows_missing': len(rows['missing'])}
        for f in sorted(os.listdir(out)):
            if f.endswith('.json') and f != 'bake-report.json':
                files.append((f'game/assets/anim/t3/{repo_dir(b)}/{f}', os.path.join(out, f)))
        files.append((f'docs/proof/2026-11-07/fill3-ttt2/{b}-bake-report.json',
                      os.path.join(out, 'bake-report.json')))
        files.append((f'docs/proof/2026-11-07/fill3-ttt2/{b}-rows-report.json',
                      os.path.join(W, 'rows-reports', b + '.json')))
    if batch == '1':
        files.append(('tools/anim/ttt2_bank_rows.py',
                      os.path.expanduser('~/workspace/_fill3-ttt2-20261106/tools/ttt2_bank_rows_gen.py')))
        files.append(('tools/anim/ttt2_slot_mapper.py',
                      os.path.join(W, 'slot_mapper.py')))
        files.append(('docs/tech/ttt2-mota/join/FILL3-BANKS.md',
                      os.path.join(W, 'FILL3-BANKS.md')))
        files.append(('tools/anim/ttt2_bank_bake.py',
                      os.path.expanduser('~/workspace/_fill3-ttt2-20261106/tools/ttt2_bank_bake.py')))
    else:
        # keep the shipped rows tool in sync with production (join-label fix)
        files.append(('tools/anim/ttt2_bank_rows.py',
                      os.path.expanduser('~/workspace/_fill3-ttt2-20261106/tools/ttt2_bank_rows_gen.py')))
        files.append(('docs/tech/ttt2-mota/join/FILL3-BANKS.md',
                      os.path.join(W, 'FILL3-BANKS.md')))
    if batch == '2':
        # remove batch 1's stray bake-report.json files from bank dirs
        # (they belong under docs/proof/, where they also landed)
        for b in ('alex', 'alisa', 'angel', 'armor_king', 'asuka', 'bob_satsuma', 'anna'):
            files.append((f'game/assets/anim/t3/{b}/bake-report.json', None))
    print('files:', len(files), 'total MB: %.1f' % (sum(os.path.getsize(p) for _, p in files if p) / 1e6), flush=True)

    main_sha = gh_api('git/ref/heads/main')['object']['sha']
    base_tree = gh_api(f'git/commits/{main_sha}')['tree']['sha']
    tree_items = []
    for repo_path, local in files:
        if local is None:
            tree_items.append({'path': repo_path, 'mode': '100644', 'type': 'blob', 'sha': None})
            continue
        tree_items.append({'path': repo_path, 'mode': '100644', 'type': 'blob',
                           'sha': blob(open(local, 'rb').read())})
        if len(tree_items) % 20 == 0:
            print('blobs', len(tree_items), '/', len(files), flush=True)
    tree = gh_api('git/trees', 'POST', {'base_tree': base_tree, 'tree': tree_items})
    lines = '\n'.join('- %s: %d clips baked, %d skipped, %d slot gaps; %d pack rows, %d hit rows, %d rows missing'
                      % (b, s['clips_baked'], s['clips_skipped'], s['slot_gaps'],
                         s['pack_rows'], s['hit_rows'], s['rows_missing'])
                      for b, s in stats.items())
    commit = gh_api('git/commits', 'POST', {
        'message': 'Fill 3 (TTT2) banks batch %s: %s\n\n%s' % (batch, ', '.join(banks), lines),
        'tree': tree['sha'], 'parents': [main_sha]})
    branch = f'fill3-ttt2-banks-{batch}'
    gh_api('git/refs', 'POST', {'ref': f'refs/heads/{branch}', 'sha': commit['sha']})
    json.dump({'branch': branch, 'commit': commit['sha'], 'stats': stats,
               'files': [p for p, _ in files]},
              open(os.path.join(W, f'pr-banks-{batch}.json'), 'w'), indent=1)
    print('BRANCH_READY', branch, commit['sha'], flush=True)


if __name__ == '__main__':
    main()
