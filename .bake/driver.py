import os, sys, subprocess, time
os.environ.setdefault('T3REMAKE_RESEARCH', '/home/hatch/workspace/tools/tekken3remake/tools/research')
sys.path.insert(0, 'lab/tools')
import t3_motion_bake as TB

banks = sys.argv[1:]
for bank in banks:
    kmd, divmot, stance = TB.BANKS[bank]
    mbank = TB.motion.parse_bank((TB.T3 / divmot).read_bytes())
    rows = sorted({r for r in mbank.move_index if r < TB.motion.COMMON_FLAG})
    print(f"{bank}: {len(rows)} rows in move index", flush=True)
    t0 = time.time()
    env = dict(os.environ, TMPDIR=os.path.abspath('.tmp'))
    r = subprocess.run([sys.executable, 'tools/anim/t3_row_bake.py', '--bank', bank,
                        '--rows', ','.join(map(str, rows))],
                       env=env, capture_output=True, text=True)
    print(r.stdout.strip()[-400:])
    if r.returncode != 0:
        print("STDERR:", r.stderr[-1500:])
    print(f"{bank} wall: {time.time()-t0:.0f}s rc={r.returncode}", flush=True)
