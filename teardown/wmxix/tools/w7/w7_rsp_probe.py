#!/usr/bin/env python3
"""W7 probe: does Dolphin's GDB stub actually trap on breakpoints?

The obs1 run logged 0 hits at 0x800364F0 during ~10 min of live match play.
This probe distinguishes:
  (A) the breakpoint mechanism is broken (JIT never traps), from
  (B) the mechanism works but FUN_800364F0 is never called for these moves.

Method: boot the game (no movie), continue 45 s, interrupt (0x03), read PC,
set a breakpoint AT the interrupted PC (title loop re-executes it 60x/s),
re-arm 0x800364F0, continue, wait 30 s for stops.
  - PC bp fires  => mechanism works (case B).
  - PC bp silent => mechanism broken (case A).

Usage: run on the VM while Dolphin (GDBPort=9090) is waiting at boot.
  python3 w7_rsp_probe.py --host 127.0.0.1 --port 9090
"""
import argparse
import socket
import sys
import time

sys.path.insert(0, "/data/wmxix")
sys.path.insert(0, ".")
from w7_rsp import RSP, parse_stop  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=9090)
    ap.add_argument("--boot-wait", type=float, default=45)
    ap.add_argument("--stop-wait", type=float, default=30)
    ap.add_argument("--dump-mem1", default="",
                    help="if set, interrupt again after the wait and dump MEM1 (0x80000000, 24MB) to this file")
    args = ap.parse_args()

    rsp = RSP(args.host, args.port)
    print("connected", flush=True)
    print("qSupported:", rsp.cmd(b"qSupported:multiprocess+;qRelocInsn+"), flush=True)
    rsp.cmd(b"Hc-1")
    rsp.cmd(b"Hh-1")
    ok = rsp.set_bp(0x800364F0)
    print("bp 0x800364F0 set:", ok, flush=True)
    rsp.cmd_noreply(b"c")
    print("continued; waiting %.0fs for boot..." % args.boot_wait, flush=True)
    time.sleep(args.boot_wait)
    # interrupt: bare 0x03 byte, outside any packet
    rsp.sock.sendall(b"\x03")
    print("sent interrupt, waiting for stop...", flush=True)
    try:
        pkt = rsp.wait_stop(timeout=15)
    except (socket.timeout, ConnectionError) as e:
        print("NO STOP AFTER INTERRUPT:", e, flush=True)
        print("RESULT: stub does not respond to interrupt; mechanism suspect", flush=True)
        return
    stop = parse_stop(pkt)
    print("stop packet:", stop, flush=True)
    # The stop packet itself carries the PC (reg 64) -- use it directly.
    pc = stop.get("regs", {}).get(64)
    if pc is None:
        try:
            pc = rsp.read_reg(64)
        except Exception as e:
            print("could not read pc:", e, flush=True)
            return
    print("interrupted PC = 0x%x" % pc, flush=True)
    # single-step twice to confirm execution control
    for i in range(2):
        rsp.cmd_noreply(b"s")
        try:
            pkt = rsp.wait_stop(timeout=10)
            st = parse_stop(pkt)
            pc2 = st.get("regs", {}).get(64, 0)
            print("step %d: pc=0x%x stop=%s" % (i, pc2, st), flush=True)
            pc = pc2
        except Exception as e:
            print("step %d failed: %s" % (i, e), flush=True)
            break
    # breakpoint at the (stepped) PC + re-arm 0x800364F0
    print("setting bp at current PC 0x%x" % pc, flush=True)
    ok_pc = rsp.set_bp(pc)
    print("bp at PC set:", ok_pc, flush=True)
    ok2 = rsp.set_bp(0x800364F0)
    print("bp 0x800364F0 re-armed:", ok2, flush=True)
    rsp.cmd_noreply(b"c")
    print("continued; waiting %.0fs for stops..." % args.stop_wait, flush=True)
    t0 = time.time()
    fired = []
    try:
        while time.time() - t0 < args.stop_wait:
            pkt = rsp.wait_stop(timeout=args.stop_wait - (time.time() - t0))
            stop = parse_stop(pkt)
            hit_pc = stop.get("regs", {}).get(64, 0)
            print("STOP: pc=0x%x %s" % (hit_pc, stop), flush=True)
            fired.append(hit_pc)
            if len(fired) >= 5:
                break
            rsp.cmd_noreply(b"c")
    except (socket.timeout, ConnectionError) as e:
        print("wait ended:", e, flush=True)
    print("RESULT: %d stops in %.0fs: %s" % (len(fired), args.stop_wait,
          ["0x%x" % p for p in fired]), flush=True)
    if pc in fired:
        print("CONCLUSION: mechanism WORKS (PC bp fired). 0x800364F0 is not called (case B).", flush=True)
    elif fired:
        print("CONCLUSION: mechanism works (some bp fired) but PC bp did not; odd.", flush=True)
    else:
        print("CONCLUSION: mechanism BROKEN (no bp fired at all, case A).", flush=True)
    if args.dump_mem1:
        # interrupt again and dump MEM1 for the polling-path address hunt
        print("interrupting for MEM1 dump...", flush=True)
        rsp.sock.sendall(b"\x03")
        try:
            pkt = rsp.wait_stop(timeout=15)
            st = parse_stop(pkt)
            print("stopped at pc=0x%x" % st.get("regs", {}).get(64, 0), flush=True)
        except Exception as e:
            print("interrupt for dump failed:", e, flush=True)
            return
        print("dumping MEM1 (24MB) to %s ..." % args.dump_mem1, flush=True)
        with open(args.dump_mem1, "wb") as f:
            base, total = 0x80000000, 24 * 1024 * 1024
            done = 0
            while done < total:
                chunk = min(4000, total - done)
                try:
                    f.write(rsp.read_mem(base + done, chunk))
                except Exception as e:
                    print("read error at 0x%x: %s (filling zeros)" % (base + done, e), flush=True)
                    f.write(b"\x00" * chunk)
                done += chunk
                if done % (4 * 1024 * 1024) == 0:
                    print("  %dMB..." % (done // (1024 * 1024)), flush=True)
        print("MEM1 dump done", flush=True)


if __name__ == "__main__":
    main()
