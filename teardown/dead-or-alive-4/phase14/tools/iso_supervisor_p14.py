#!/usr/bin/env python3
"""DOA4 phase 14: supervisor for the phase-13 ISO assembler.
The egress proxy intermittently kills gh downloads (stream CANCEL /
connection refused); the phase-13 assembler aborts on the first
failed part (check=True). This supervisor re-runs it for the
remaining parts until iso_assembly_log.json shows 30/30:
  - waits while another assembler process is alive (never two);
  - before each attempt, deletes the CURRENT part's partial file
    if one is present (unverified partial; the assembler would
    size-assert on it) — parts already in the log are untouched;
  - the assembler itself still verifies sha256 vs the release
    digest before every write. This script adds no new trust:
    it only retries transport.
Usage: iso_supervisor_p14.py [max_attempts]
Log: stdout (redirected by the launcher to p14/supervisor.log).
"""
import json, os, subprocess, sys, time

SCR = '/home/hatch/workspace/_doa4p2-scratch/p13'
LOG = os.path.join(SCR, 'iso_assembly_log.json')
ASM = '/home/hatch/workspace/_doa4p8-clone/teardown/dead-or-alive-4/phase13/tools/iso_assemble_p13.py'


def landed():
    try:
        return set(json.load(open(LOG))['landed'])
    except Exception:
        return set()


def assembler_alive():
    r = subprocess.run(['pgrep', '-f', 'iso_assemble_p13.py'],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


def main():
    max_attempts = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    for attempt in range(1, max_attempts + 1):
        while assembler_alive():
            time.sleep(20)
        have = landed()
        if len(have) >= 30:
            print('SUPERVISOR: 30/30 landed, done', flush=True)
            return 0
        want = [n for n in range(1, 31)
                if f'doa4-250m.part_{n:02d}' not in have]
        # remove the first wanted part's partial (transport debris)
        first = os.path.join(SCR, f'doa4-250m.part_{want[0]:02d}')
        if os.path.exists(first):
            print(f'SUPERVISOR: removing partial {first} '
                  f'({os.path.getsize(first)} B)', flush=True)
            os.remove(first)
        print(f'SUPERVISOR: attempt {attempt}, landed {len(have)}/30, '
              f'running assembler for {want}', flush=True)
        subprocess.run(['python3', ASM] + [str(n) for n in want])
        time.sleep(5)
    print('SUPERVISOR: attempts exhausted at',
          len(landed()), '/30', flush=True)
    return 1


if __name__ == '__main__':
    sys.exit(main())
