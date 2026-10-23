#!/usr/bin/env python3
"""DOA4 phase 15: keep the phase-13 assembler (p15 paths) alive until
30/30 parts are landed in the assembly log. The assembler itself
sha256-verifies every part against the release digest before writing;
this supervisor only removes the CURRENT part's unverified partial
after a confirmed assembler death (proxy kill) and relaunches.
Never touches a live download."""
import json, os, subprocess, sys, time

SCR = '/home/hatch/workspace/_doa4p2-scratch/p15'
LOG = os.path.join(SCR, 'iso_assembly_log.json')
ASM = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iso_assemble_p15.py')

def landed():
    if os.path.exists(LOG):
        return len(json.load(open(LOG)).get('landed', {}))
    return 0

def assembler_alive():
    r = subprocess.run(['pgrep', '-f', 'iso_assemble_p15.py'], capture_output=True, text=True)
    return bool(r.stdout.strip())

def main():
    while landed() < 30:
        if assembler_alive():
            time.sleep(20); continue
        # assembler dead: drop only unverified partial part files
        for f in os.listdir(SCR):
            if f.startswith('doa4-250m.part_'):
                p = os.path.join(SCR, f)
                print('removing unverified partial', f, os.path.getsize(p), flush=True)
                os.remove(p)
        todo = [n for n in range(1, 31)
                if f'doa4-250m.part_{n:02d}' not in
                (json.load(open(LOG)).get('landed', {}) if os.path.exists(LOG) else {})]
        print('launching assembler for parts', todo, flush=True)
        subprocess.run([sys.executable, ASM] + [str(n) for n in todo])
        time.sleep(5)
    print('SUPERVISOR DONE: 30/30 landed', flush=True)

if __name__ == '__main__':
    main()
