#!/usr/bin/env python3
"""W7: in-match MEM1 dump. Connects to the GDB stub, continues the game
(which is playing a DTM), waits until the match is in progress, interrupts,
and dumps MEM1 (24MB) to a file. Used to capture wrestler objects +
descriptor arrays + current-motion state (breakpoints don't trap in this
Dolphin build, so memory snapshots are the observation path).

Usage (on the VM, Dolphin already waiting at the stub):
  python3 w7_dump_match.py --wait 300 --out /data/wmxix/w7/mem1_match.bin
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
    ap.add_argument("--wait", type=float, default=300,
                    help="seconds of gameplay before interrupting")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rsp = RSP(args.host, args.port)
    print("connected", flush=True)
    rsp.cmd(b"qSupported:multiprocess+;qRelocInsn+")
    rsp.cmd(b"Hc-1")
    rsp.cmd(b"Hh-1")
    rsp.cmd_noreply(b"c")
    print("continued; waiting %.0fs for the match..." % args.wait, flush=True)
    time.sleep(args.wait)
    rsp.sock.sendall(b"\x03")
    print("sent interrupt, waiting for stop...", flush=True)
    pkt = rsp.wait_stop(timeout=20)
    st = parse_stop(pkt)
    print("stopped at pc=0x%x sp=0x%x" % (st.get("regs", {}).get(64, 0),
          st.get("regs", {}).get(1, 0)), flush=True)
    print("dumping MEM1 (24MB) to %s ..." % args.out, flush=True)
    t0 = time.time()
    with open(args.out, "wb") as f:
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
                print("  %dMB (%.0fs elapsed)" % (done // (1024 * 1024), time.time() - t0), flush=True)
    print("MEM1 dump done in %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
