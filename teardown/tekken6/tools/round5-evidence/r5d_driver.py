#!/usr/bin/env python3
"""Round 5 attempt-3 driver (fixes attempt-2 r5_driver defects).

Defects fixed vs r5_driver.py:
 1. Hit PC detection: r5_driver parsed pc from cpu.getAllRegs categories
    (index 32) — that parse returned None in every round-4 trace (see
    round4-evidence/trace_r5.jsonl: all hits pc=null), so control_hits
    stayed 0 and no loader hit could ever be classified. This driver
    takes the PC from the stepping event itself (ev['pc'], proven in
    ws_control.py) and falls back to cpu.status.
 2. RAM dump pause: r5_driver waited for a control-BP pause that (per
    defect 1) could never be recognised. This driver uses game.pause /
    game.resume (present in the PPSSPP v1.20.4 debugger API) and reads
    memory while paused.
 3. Register capture on loader/wrapper hits: raw getAllRegs reply is
    logged verbatim on the first hits so the format is evidence, and
    a0-a3/v0 are also probed via cpu.getReg variants.

Commands (append one per line to r5d_cmd.txt):
  press <button> <dur_frames>
  wait <seconds>
  shot <name>
  dump <tag>          game.pause -> 32MB RAM dump to dumps_r5/ram_<tag>.bin -> resume
  status
  regsprobe           log raw getAllRegs + cpu.status (format evidence)
  quit
Trace: trace_r5d.jsonl (flushed per record). Breakpoints: loader
0x89d27a0 / wrapper 0x8b559c8 / inflate 0x8b55bf0 / ret 0x89d27ec +
in-session hot-PC control (F7 discipline).
"""
import base64, hashlib, json, os, struct, subprocess, sys, time
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from ws_trace import WS, Debugger

DISP = ':82'
LOGF = open(os.path.join(ROOT, 'trace_r5d.jsonl'), 'a')
DUMPS = os.path.join(ROOT, 'dumps_r5'); os.makedirs(DUMPS, exist_ok=True)
SHOTS = os.path.join(ROOT, 'r5_shots'); os.makedirs(SHOTS, exist_ok=True)
CMD = os.path.join(ROOT, 'r5d_cmd.txt')
RAM_BASE, RAM_SIZE = 0x8800000, 0x2000000
BP = {0x89D27A0: 'loader', 0x8B559C8: 'wrapper', 0x8B55BF0: 'inflate', 0x89D27EC: 'ret'}

def emit(o):
    o['wall'] = round(time.time(), 1)
    LOGF.write(json.dumps(o) + '\n'); LOGF.flush()
    print(json.dumps(o)[:400], flush=True)

def mem_read(dbg, addr, size):
    out = bytearray()
    while size > 0:
        n = min(size, 49152)
        r = dbg.request({'event': 'memory.read', 'address': addr + len(out), 'size': n}, wait=15)
        if not r or 'base64' not in r:
            return None
        chunk = base64.b64decode(r['base64'])
        if not chunk:
            return None
        out += chunk; size -= len(chunk)
    return bytes(out)

def regs_probe(dbg):
    """Return (gprs_dict, raw_reply). Tries getAllRegs category parse in
    several shapes; logs raw once via caller."""
    r = dbg.request({'event': 'cpu.getAllRegs'})
    g = {}
    if r:
        for c in r.get('categories', []) or []:
            vals = c.get('uintValues') or c.get('values') or c.get('registers') or []
            names = c.get('registerNames') or c.get('names') or []
            for i, v in enumerate(vals):
                if isinstance(v, int):
                    g[i] = v
            for i, nm in enumerate(names):
                if i < len(vals) and isinstance(vals[i], int):
                    g[str(nm)] = vals[i]
    return g, r

class Session:
    def __init__(self, dbg):
        self.dbg = dbg
        self.control_pc = None
        self.control_hits = 0
        self.hits = {'loader': 0, 'wrapper': 0, 'inflate': 0, 'ret': 0}
        self.state = {}
        self.seq = 0
        self.raw_regs_logged = 0

    def event_pc(self, ev):
        if isinstance(ev.get('pc'), int):
            return ev['pc']
        r = self.dbg.request({'event': 'cpu.status'})
        return r.get('pc') if r else None

    def service_events(self, timeout=0.4):
        for ev in self.dbg.poll_events(timeout):
            en = ev.get('event', '')
            if en not in ('cpu.breakpoint.hit', 'cpu.stepping'):
                continue
            pc = self.event_pc(ev)
            name = BP.get(pc)
            if pc == self.control_pc:
                self.control_hits += 1
                if self.control_hits % 100 == 1:
                    emit({'t': 'control_hit', 'n': self.control_hits, 'pc': hex(pc)})
            elif name == 'loader':
                self.hits['loader'] += 1
                g, raw = regs_probe(self.dbg)
                if self.raw_regs_logged < 2:
                    emit({'t': 'regs_raw', 'raw': str(raw)[:1500]}); self.raw_regs_logged += 1
                a0 = g.get('a0', g.get(4)); a1 = g.get('a1', g.get(5))
                a2 = g.get('a2', g.get(6)); a3 = g.get('a3', g.get(7))
                cont = mem_read(self.dbg, a0, 4) if a0 else None
                ca = struct.unpack('<I', cont)[0] if cont and len(cont) == 4 else None
                hdr = mem_read(self.dbg, ca, 20) if ca else None
                w = struct.unpack('<5I', hdr) if hdr and len(hdr) == 20 else None
                self.state = {'seq': self.seq, 'dest': a1, 'cap': a2, 'adlerp': a3, 'container': ca, 'w': w}
                emit({'t': 'loader_hit', 'seq': self.seq, 'gpr': {str(k): v for k, v in list(g.items())[:40]},
                      'dest': a1, 'cap': a2, 'container': ca, 'w': w})
            elif name == 'wrapper':
                self.hits['wrapper'] += 1
                g, raw = regs_probe(self.dbg)
                if self.raw_regs_logged < 2:
                    emit({'t': 'regs_raw', 'raw': str(raw)[:1500]}); self.raw_regs_logged += 1
                dest = g.get('a0', g.get(4)); cap = g.get('a1', g.get(5))
                src = g.get('a2', g.get(6)); ad = g.get('a3', g.get(7))
                self.state.update({'wdest': dest, 'wcap': cap, 'src': src, 'wadlerp': ad})
                srcdump = mem_read(self.dbg, src, 512) if src else None
                emit({'t': 'wrapper_hit', 'seq': self.seq, 'dest': dest, 'cap': cap, 'src': src,
                      'src_head': srcdump[:48].hex() if srcdump else None,
                      'src_sha': hashlib.sha256(srcdump).hexdigest() if srcdump else None})
                if srcdump:
                    open(os.path.join(DUMPS, f"load{self.seq}_src512.bin"), 'wb').write(srcdump)
            elif name == 'inflate':
                self.hits['inflate'] += 1
                emit({'t': 'inflate_hit', 'seq': self.seq})
            elif name == 'ret':
                self.hits['ret'] += 1
                g, _ = regs_probe(self.dbg)
                v0 = g.get('v0', g.get(2))
                emit({'t': 'load_done', 'seq': self.seq, 'v0': v0, 'state': self.state})
                try:
                    ca, w = self.state.get('container'), self.state.get('w')
                    if ca and w:
                        dn = min(max(w[4] + 64, 4096), 1_500_000)
                        cd = mem_read(self.dbg, ca, dn)
                        if cd:
                            p = os.path.join(DUMPS, f'load{self.seq}_container.bin'); open(p, 'wb').write(cd)
                            emit({'t': 'container_dump', 'seq': self.seq, 'n': len(cd),
                                  'sha256': hashlib.sha256(cd).hexdigest()})
                        if v0 and isinstance(v0, int) and v0 > 0 and self.state.get('wdest'):
                            dd = mem_read(self.dbg, self.state['wdest'], min(v0, 900_000))
                            if dd:
                                p = os.path.join(DUMPS, f'load{self.seq}_dest.bin'); open(p, 'wb').write(dd)
                                emit({'t': 'dest_dump', 'seq': self.seq, 'n': len(dd),
                                      'sha256': hashlib.sha256(dd).hexdigest()})
                except Exception as e:
                    emit({'t': 'dump_err', 'seq': self.seq, 'err': str(e)})
                self.seq += 1
            else:
                emit({'t': 'stepping_other', 'pc': hex(pc) if pc else None, 'ev': str(ev)[:200]})
            self.dbg.request({'event': 'cpu.resume'})

    def full_ram_dump(self, tag):
        emit({'t': 'dump_start', 'tag': tag, 'control_hits': self.control_hits, 'hits': self.hits})
        r = self.dbg.request({'event': 'game.pause'})
        emit({'t': 'game_pause', 'tag': tag, 'r': str(r)[:200]})
        time.sleep(1.0)
        # drain any stepping events caused by the pause without resuming yet
        path = os.path.join(DUMPS, f'ram_{tag}.bin')
        ok_chunks, total = 0, RAM_SIZE // 49152 + 1
        with open(path, 'wb') as fh:
            for i in range(total):
                n = min(49152, RAM_SIZE - i * 49152)
                if n <= 0:
                    break
                rr = self.dbg.request({'event': 'memory.read', 'address': RAM_BASE + i * 49152, 'size': n}, wait=15)
                if not rr or 'base64' not in rr:
                    fh.write(b'\x00' * n)
                    if i % 50 == 0:
                        emit({'t': 'dump_chunk_fail', 'tag': tag, 'chunk': i, 'r': str(rr)[:150]})
                else:
                    fh.write(base64.b64decode(rr['base64'])); ok_chunks += 1
        sha = hashlib.sha256(open(path, 'rb').read()).hexdigest()
        emit({'t': 'dump_done', 'tag': tag, 'path': path, 'ok_chunks': ok_chunks,
              'total_chunks': total, 'sha256': sha})
        r = self.dbg.request({'event': 'game.resume'})
        emit({'t': 'game_resume', 'tag': tag, 'r': str(r)[:200]})
        self.dbg.request({'event': 'cpu.resume'})

def shot(dbg, name):
    out = os.path.join(SHOTS, name + '.png')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'x11grab', '-video_size', '800x600',
                    '-i', DISP, '-frames:v', '1', out], env={**os.environ, 'DISPLAY': DISP}, timeout=60)
    emit({'t': 'shot', 'name': name})

def main():
    xvfb = subprocess.Popen(['Xvfb', DISP, '-ac', '-screen', '0', '800x600x24'],
                            stdout=open(os.path.join(ROOT, 'xvfb_r5d.log'), 'w'), stderr=subprocess.STDOUT)
    time.sleep(3)
    emu = subprocess.Popen([os.path.join(ROOT, 'run_emu_r5c.sh')],
                           stdout=open(os.path.join(ROOT, 'ppsspp_r5d.log'), 'w'), stderr=subprocess.STDOUT)
    emit({'t': 'launched', 'xvfb_pid': xvfb.pid, 'emu_pid': emu.pid})
    ws = None
    for _ in range(90):
        try:
            ws = WS('127.0.0.1', 54809); break
        except Exception:
            time.sleep(2)
    if ws is None:
        emit({'t': 'FATAL', 'why': 'no ws connect'}); return 1
    dbg = Debugger(ws)
    S = Session(dbg)
    emit({'t': 'version', 'r': dbg.request({'event': 'version', 'name': 'r5d', 'version': '1'})})
    # Boot-wait (attempt-3 launch 1 raced this: under host load PPSSPP took
    # >25s to start the CPU, pc sampled 0x0 and every bp.add returned
    # 'CPU not started'). Poll until the game is running with a non-zero PC.
    t_boot = time.time()
    booted = False
    while time.time() - t_boot < 300:
        gs = dbg.request({'event': 'game.status'})
        cs = dbg.request({'event': 'cpu.status'})
        if gs and gs.get('game') and cs and cs.get('pc'):
            booted = True
            emit({'t': 'booted', 'game': gs.get('game'), 'pc': hex(cs['pc']),
                  'wait_s': round(time.time() - t_boot, 1)})
            break
        time.sleep(2)
    if not booted:
        emit({'t': 'FATAL', 'why': 'game not running after 300s'}); return 1
    pcs = {}
    for _ in range(40):
        r = dbg.request({'event': 'cpu.status'})
        if r and 'pc' in r:
            pcs[r['pc']] = pcs.get(r['pc'], 0) + 1
        time.sleep(0.5)
    emit({'t': 'pc_samples', 'top': {hex(k): v for k, v in sorted(pcs.items(), key=lambda x: -x[1])[:6]}})
    pcs.pop(0, None)
    if not pcs:
        emit({'t': 'FATAL', 'why': 'no nonzero pc samples'}); return 1
    S.control_pc = max(pcs, key=pcs.get)

    def arm():
        ok = {}
        for nm, addr in [('loader', 0x89D27A0), ('wrapper', 0x8B559C8), ('ret', 0x89D27EC),
                         ('inflate', 0x8B55BF0), ('control', S.control_pc)]:
            r = None
            for _try in range(10):
                r = dbg.request({'event': 'cpu.breakpoint.add', 'address': addr, 'enabled': True})
                if r and r.get('event') != 'error':
                    break
                time.sleep(2)
            ok[nm] = bool(r and r.get('event') != 'error')
            emit({'t': 'bp.add', 'name': nm, 'addr': hex(addr), 'r': r})
        emit({'t': 'bp.list', 'r': str(dbg.request({'event': 'cpu.breakpoint.list'}))[:600]})
        return ok
    S.arm = arm
    arm()
    # wait up to 60s for first control hit as the in-session validity proof
    t0 = time.time()
    while time.time() - t0 < 60 and S.control_hits == 0:
        S.service_events(0.4)
    emit({'t': 'READY', 'control_pc': hex(S.control_pc), 'control_hits_after_wait': S.control_hits})
    # F11: control validated -> drop the hot bp so emulation runs full speed.
    r = dbg.request({'event': 'cpu.breakpoint.remove', 'address': S.control_pc})
    emit({'t': 'control_dropped', 'control_hits_final': S.control_hits, 'r': str(r)[:120]})
    open(CMD, 'a').close()
    cmd_off = os.path.getsize(CMD)
    while True:
        S.service_events(0.3)
        if emu.poll() is not None:
            emit({'t': 'FATAL', 'why': f'emu exited rc={emu.returncode}'}); return 2
        try:
            sz = os.path.getsize(CMD)
        except OSError:
            sz = cmd_off
        if sz > cmd_off:
            with open(CMD) as fh:
                fh.seek(cmd_off); lines = fh.read().splitlines(); cmd_off = fh.tell()
            for line in lines:
                parts = line.split()
                if not parts:
                    continue
                emit({'t': 'cmd', 'line': line})
                try:
                    if parts[0] == 'press':
                        r = dbg.request({'event': 'input.buttons.press', 'button': parts[1],
                                         'duration': int(parts[2]) if len(parts) > 2 else 4})
                        emit({'t': 'input', 'button': parts[1], 'r': str(r)[:100]})
                    elif parts[0] == 'wait':
                        t_end = time.time() + float(parts[1])
                        while time.time() < t_end:
                            S.service_events(0.3)
                    elif parts[0] == 'shot':
                        shot(dbg, parts[1])
                    elif parts[0] == 'dump':
                        S.full_ram_dump(parts[1])
                    elif parts[0] == 'regsprobe':
                        g, raw = regs_probe(dbg)
                        emit({'t': 'regsprobe', 'gpr': {str(k): v for k, v in list(g.items())[:40]},
                              'raw': str(raw)[:1500],
                              'cpu_status': dbg.request({'event': 'cpu.status'})})
                    elif parts[0] == 'ctrl':
                        before = S.control_hits
                        dbg.request({'event': 'cpu.breakpoint.add', 'address': S.control_pc, 'enabled': True})
                        t_end = time.time() + 8
                        while time.time() < t_end:
                            S.service_events(0.3)
                        dbg.request({'event': 'cpu.breakpoint.remove', 'address': S.control_pc})
                        emit({'t': 'ctrl_check', 'control_hits_delta': S.control_hits - before,
                              'control_hits': S.control_hits, 'hits': S.hits})
                    elif parts[0] == 'rearm':
                        emit({'t': 'rearm', 'ok': S.arm()})
                    elif parts[0] == 'status':
                        emit({'t': 'status', 'game': dbg.request({'event': 'game.status'}),
                              'cpu': dbg.request({'event': 'cpu.status'}),
                              'hits': S.hits, 'control_hits': S.control_hits})
                    elif parts[0] == 'quit':
                        emit({'t': 'done', 'hits': S.hits, 'control_hits': S.control_hits, 'loads': S.seq})
                        return 0
                except Exception as e:
                    emit({'t': 'cmd_err', 'line': line, 'err': str(e)})

if __name__ == '__main__':
    sys.exit(main())
