import os, sys, subprocess
os.environ.setdefault('T3REMAKE_RESEARCH', '/home/hatch/workspace/tools/tekken3remake/tools/research')
sys.path.insert(0, 'tools/anim')
import t3_row_bake as RB
rows = sorted(RB.referenced_rows('king'))
print('king-referenced rows:', len(rows), flush=True)
env = dict(os.environ, TMPDIR=os.path.abspath('.tmp'))
r = subprocess.run([sys.executable, 'tools/anim/t3_row_bake.py', '--bank', 'armorking',
                    '--rows', ','.join(map(str, rows))], env=env, capture_output=True, text=True)
print(r.stdout[-300:]); print(r.stderr[-800:] if r.returncode else '')
