#!/usr/bin/env python3
"""CI: fail if lines a PR adds to player-facing UI files (game/**.html|js|css|json) contain a source-game name.
Diff-based, so existing content isn't flagged. Usage: check.py BASE HEAD.
Binary-derived *.pack.json animation packs are skipped: their base64 payload is opaque
motion data, not UI text (false positive: "wwe" inside base64, PR #1149, 2026-10-26)."""
import json, re, subprocess, sys, pathlib
base, head = sys.argv[1], sys.argv[2]
terms = json.load(open(pathlib.Path(__file__).with_name('denylist.json')))['terms']
pats = [(t, re.compile(r'\b' + re.escape(t) + r'\b', re.I)) for t in terms]
# Owner-ruled exemptions: (file, term) pairs where a denylisted string is faithful
# source data, not a UI name leak. "Nioh" in Geese's file is the Japanese word for
# the Buddhist guardian kings in his own Tekken 7 movelist name "Nioh Kuzushi"
# (GRE teardown/tekken7-steam/tkdata/mothead/movelist/mry.mvl); the denylist entry
# targets the Koei Tecmo game title. The name was withheld in PR #1618 as a false
# positive and restored by owner ruling 2026-11-06.
EXEMPTIONS = {('game/assets/movesets/t7-geese.json', 'nioh')}
diff = subprocess.run(['git', 'diff', '-U0', f'{base}...{head}', '--', 'game/'], capture_output=True, text=True, check=True).stdout
bad, f = [], None
for ln in diff.splitlines():
    if ln.startswith('+++ '): f = ln[6:]; continue
    if not f or f.endswith('.pack.json') or not re.search(r'\.(html|js|mjs|css|json)$', f) or not ln.startswith('+'): continue
    for t, p in pats:
        if (f, t) in EXEMPTIONS: continue
        if p.search(ln): bad.append(f'{f}: "{t}" in: {ln[1:].strip()[:120]}')
if bad:
    print('CANON NAME GATE FAILED (owner rule: imported names need EMWH canon names)'); print('\n'.join(bad)); sys.exit(1)
print('canon-names: ok')
