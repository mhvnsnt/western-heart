"""Collider banks land at game/assets/anim/t3/<stem>_ttt2/ (never overwrite
the live Tekken-3 bank at <stem>/). The only place the rows bank label is
functional is rows.pack.json's target_rig skeleton path; swap exactly that
one string (must occur exactly once)."""
import sys
for stem in sys.argv[1:]:
    p = f'out/{stem}/rows.pack.json'
    s = open(p, encoding='utf8').read()
    old = f'game/assets/anim/t3/{stem}/skeleton.json'
    assert s.count(old) == 1, (stem, s.count(old))
    open(p, 'w', encoding='utf8').write(s.replace(old, f'game/assets/anim/t3/{stem}_ttt2/skeleton.json'))
    print(stem, '-> target_rig now t3/%s_ttt2/skeleton.json' % stem)
