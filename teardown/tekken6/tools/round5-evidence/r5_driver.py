#!/usr/bin/env python3
"""Round 5 driver: PPSSPP session with control-validated breakpoints on
loader/wrapper/inflate, an interactive command queue (r5_cmd.txt), and
full-RAM dumps on demand.

Commands (one per line appended to r5_cmd.txt):
  press <button> <dur_frames>     e.g. press cross 4
  wait <seconds>
  shot <name>                     screenshot to r5_shots/<name>.png
  dump <tag>                      pause via control BP, dump 32MB RAM to dumps_r5/ram_<tag>.bin
  status                          log cpu/game status
  quit                            end session
Every breakpoint hit is logged to trace_r5.jsonl (flushed). The control
BP is a hot PC sampled IN THIS SESSION (F7 discipline); its hit count is
the validity control for every zero-hit claim."""
import base64, hashlib, json, os, struct, subprocess, sys, time
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from ws_trace import WS, Debugger

DISP = ':81'
LOGF = open(os.path.join(ROOT, 'trace_r5.jsonl'), 'a')
DUMPS = os.path.join(ROOT, 'dumps_r5'); os.makedirs(DUMPS, exist_ok=True)
SHOTS = os.path.join(ROOT, 'r5_shots'); os.makedirs(SHOTS, exist_ok=True)
CMD = os.path.join(ROOT, 'r5_cmd.txt')
RAM_BASE, RAM_SIZE = 0x8800000, 0x2000000

def emit(o):
    o['wall'] = round(time.time(), 1)
    LOGF.write(json.dumps(o) + '\n'); LOGF.flush()
    print(json.dumps(o)[:300], flush=True)

def mem_read(dbg, addr, size):
    out = bytearray()
    while size > 0:
        n = min(size, 49152)
        r = dbg.request({'event': 'memory.read', 'address': addr + len(out), 'size': n}, wait=15)
        if not r or 'base64' not in r: return None
        chunk = base64.b64decode(r['base64'])
        if not chunk: return None
        out += chunk; size -= len(chunk)
    return bytes(out)

def get_gprs(dbg):
    r = dbg.request({'event': 'cpu.getAllRegs'})
    g = {}
    if r:
        for c in r.get('categories', []):
            if c.get('name') in ('GPR', 'gpr', 'General', 'MIPS'):
                for i, v in enumerate(c.get('values', [])): g[i] = v
    return g

class Session:
    def __init__(self, dbg):
        self.dbg = dbg
        self.control_pc = None
        self.control_hits = 0
        self.hits = {'loader': 0, 'wrapper': 0, 'inflate': 0, 'ret': 0}
        self.state = {}
        self.seq = 0
        self.paused_for_dump = False

    def service_events(self, timeout=0.4):
        for ev in self.dbg.poll_events(timeout):
            en = ev.get('event', '')
            if en in ('cpu.breakpoint.hit', 'cpu.stepping'):
                g = get_gprs(self.dbg)
                pc = g.get(32)
                if pc == self.control_pc:
                    self.control_hits += 1
                    if self.control_hits % 200 == 1:
                        emit({'t': 'control_hit', 'n': self.control_hits, 'pc': hex(pc)})
                elif pc == 0x89D27A0:
                    self.hits['loader'] += 1
                    a0, a1, a2, a3 = g.get(4), g.get(5), g.get(6), g.get(7)
                    cont = mem_read(self.dbg, a0, 4) if a0 else None
                    ca = struct.unpack('<I', cont)[0] if cont and len(cont) == 4 else None
                    hdr = mem_read(self.dbg, ca, 20) if ca else None
                    w = struct.unpack('<5I', hdr) if hdr and len(hdr) == 20 else None
                    self.state = {'seq': self.seq, 'dest': a1, 'cap': a2, 'adlerp': a3, 'container': ca, 'w': w}
                    emit({'t': 'loader_hit', 'seq': self.seq, 'dest': a1, 'cap': a2, 'container': ca, 'w': w})
                elif pc == 0x8B559C8:
                    self.hits['wrapper'] += 1
                    self.state.update({'wdest': g.get(4), 'wcap': g.get(5), 'src': g.get(6), 'wadlerp': g.get(7)})
                    srcdump = mem_read(self.dbg, g.get(6), 512) if g.get(6) else None
                    emit({'t': 'wrapper_hit', 'seq': self.seq, 'dest': g.get(4), 'cap': g.get(5), 'src': g.get(6),
                          'src_head': srcdump[:48].hex() if srcdump else None,
                          'src_sha': hashlib.sha256(srcdump).hexdigest() if srcdump else None})
                    if srcdump and self.state.get('container'):
                        open(os.path.join(DUMPS, f"load{self.seq}_src512.bin"), 'wb').write(srcdump)
                elif pc == 0x8B55BF0:
                    self.hits['inflate'] += 1
                    emit({'t': 'inflate_hit', 'seq': self.seq})
                elif pc == 0x89D27EC:
                    self.hits['ret'] += 1
                    v0 = g.get(2)
                    emit({'t': 'load_done', 'seq': self.seq, 'v0': v0, 'state': self.state})
                    try:
                        ca, w = self.state.get('container'), self.state.get('w')
                        if ca and w:
                            dn = min(max(w[4] + 64, 4096), 1_500_000)
                            cd = mem_read(self.dbg, ca, dn)
                            if cd:
                                p = os.path.join(DUMPS, f'load{self.seq}_container.bin'); open(p, 'wb').write(cd)
                                emit({'t': 'container_dump', 'seq': self.seq, 'n': len(cd), 'sha256': hashlib.sha256(cd).hexdigest()})
                            if v0 and v0 > 0 and self.state.get('wdest'):
                                dd = mem_read(self.dbg, self.state['wdest'], min(v0, 900_000))
                                if dd:
                                    p = os.path.join(DUMPS, f'load{self.seq}_dest.bin'); open(p, 'wb').write(dd)
                                    emit({'t': 'dest_dump', 'seq': self.seq, 'n': len(dd), 'sha256': hashlib.sha256(dd).hexdigest()})
                    except Exception as e:
                        emit({'t': 'dump_err', 'seq': self.seq, 'err': str(e)})
                    self.seq += 1
                if not self.paused_for_dump:
                    self.dbg.request({'event': 'cpu.resume'})

    def full_ram_dump(self, tag):
        """Pause via a one-shot BP on the control PC, dump RAM, resume."""
        emit({'t': 'dump_start', 'tag': tag, 'control_hits': self.control_hits, 'hits': self.hits})
        # poll until a control hit leaves us paused: set flag first
        self.paused_for_dump = True
        t0 = time.time()
        paused = False
        while time.time() - t0 < 30:
            for ev in self.dbg.poll_events(0.4):
                if ev.get('event') in ('cpu.breakpoint.hit', 'cpu.stepping'):
                    g = get_gprs(self.dbg)
                    if g.get(32) == self.control_pc:
                        paused = True; break
                    self.dbg.request({'event': 'cpu.resume'})
            if paused: break
        if not paused:
            emit({'t': 'dump_FAIL', 'tag': tag, 'why': 'no control pause in 30s'})
            self.paused_for_dump = False
            return
        path = os.path.join(DUMPS, f'ram_{tag}.bin')
        ok_chunks, total = 0, RAM_SIZE // 49152 + 1
        with open(path, 'wb') as fh:
            for i in range(total):
                n = min(49152, RAM_SIZE - i * 49152)
                if n <= 0: break
                r = self.dbg.request({'event': 'memory.read', 'address': RAM_BASE + i * 49152, 'size': n}, wait=15)
                if not r or 'base64' not in r:
                    fh.write(b'\x00' * n); emit({'t': 'dump_chunk_fail', 'tag': tag, 'chunk': i})
                else:
                    fh.write(base64.b64decode(r['base64'])); ok_chunks += 1
        emit({'t': 'dump_done', 'tag': tag, 'path': path, 'ok_chunks': ok_chunks, 'total_chunks': total,
              'sha256': hashlib.sha256(open(path, 'rb').read()).hexdigest()})
        self.paused_for_dump = False
        self.dbg.request({'event': 'cpu.resume'})

def shot(name):
    out = os.path.join(SHOTS, name + '.png')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'x11grab', '-video_size', '800x600',
                    '-i', DISP, '-frames:v', '1', out], env={**os.environ, 'DISPLAY': DISP}, timeout=60)
    emit({'t': 'shot', 'name': name})

def main():
    xvfb = subprocess.Popen(['Xvfb', DISP, '-ac', '-screen', '0', '800x600x24'],
                            stdout=open(os.path.join(ROOT, 'xvfb_r5.log'), 'w'), stderr=subprocess.STDOUT)
    time.sleep(3)
    emu = subprocess.Popen([os.path.join(ROOT, 'run_emu_r5.sh')],
                           stdout=open(os.path.join(ROOT, 'ppsspp_r5.log'), 'w'), stderr=subprocess.STDOUT)
    emit({'t': 'launched', 'xvfb_pid': xvfb.pid, 'emu_pid': emu.pid})
    ws = None
    for _ in range(90):
        try: ws = WS('127.0.0.1', 54809); break
        except Exception: time.sleep(2)
    if ws is None:
        emit({'t': 'FATAL', 'why': 'no ws connect'}); return 1
    dbg = Debugger(ws)
    S = Session(dbg)
    emit({'t': 'version', 'r': dbg.request({'event': 'version', 'name': 'r5', 'version': '1'})})
    # wait for game to be running, sample hot PC (in-session control, F7 method)
    pcs = {}
    for _ in range(40):
        r = dbg.request({'event': 'cpu.status'})
        if r and 'pc' in r: pcs[r['pc']] = pcs.get(r['pc'], 0) + 1
        time.sleep(0.5)
    emit({'t': 'pc_samples', 'top': {hex(k): v for k, v in sorted(pcs.items(), key=lambda x: -x[1])[:6]}})
    if not pcs:
        emit({'t': 'FATAL', 'why': 'no pc samples'}); return 1
    S.control_pc = max(pcs, key=pcs.get)
    for name, addr in [('loader', 0x89D27A0), ('wrapper', 0x8B559C8), ('ret', 0x89D27EC), ('inflate', 0x8B55BF0), ('control', S.control_pc)]:
        emit({'t': 'bp.add', 'name': name, 'addr': hex(addr), 'r': dbg.request({'event': 'cpu.breakpoint.add', 'address': addr, 'enabled': True})})
    emit({'t': 'READY', 'control_pc': hex(S.control_pc)})
    open(CMD, 'a').close()
    cmd_off = os.path.getsize(CMD)
    while True:
        S.service_events(0.3)
        if emu.poll() is not None:
            emit({'t': 'FATAL', 'why': f'emu exited rc={emu.returncode}'}); return 2
        try: sz = os.path.getsize(CMD)
        except OSError: sz = cmd_off
        if sz > cmd_off:
            with open(CMD) as fh:
                fh.seek(cmd_off); lines = fh.read().splitlines(); cmd_off = fh.tell()
            for line in lines:
                parts = line.split()
                if not parts: continue
                emit({'t': 'cmd', 'line': line})
                try:
                    if parts[0] == 'press':
                        r = dbg.request({'event': 'input.buttons.press', 'button': parts[1], 'duration': int(parts[2]) if len(parts) > 2 else 4})
                        emit({'t': 'input', 'button': parts[1], 'r': str(r)[:100]})
                    elif parts[0] == 'wait':
                        t_end = time.time() + float(parts[1])
                        while time.time() < t_end: S.service_events(0.3)
                    elif parts[0] == 'shot': shot(parts[1])
                    elif parts[0] == 'dump': S.full_ram_dump(parts[1])
                    elif parts[0] == 'status':
                        emit({'t': 'status', 'game': dbg.request({'event': 'game.status'}), 'cpu': dbg.request({'event': 'cpu.status'}), 'hits': S.hits, 'control_hits': S.control_hits})
                    elif parts[0] == 'quit':
                        emit({'t': 'done', 'hits': S.hits, 'control_hits': S.control_hits, 'loads': S.seq}); return 0
                except Exception as e:
                    emit({'t': 'cmd_err', 'line': line, 'err': str(e)})

if __name__ == '__main__':
    sys.exit(main())
