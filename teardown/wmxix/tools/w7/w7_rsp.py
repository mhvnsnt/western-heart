#!/usr/bin/env python3
"""W7 raw RSP client for Dolphin's GDB stub (WrestleMania XIX observation).

Why raw RSP instead of gdb: gdb's `g` handling, command-file aborts on
memory errors, and the "target is running" quirks cost runs; the raw client
is deterministic and logs every breakpoint hit to JSONL.

Protocol notes (from Dolphin master Source/Core/Core/GDBStub.cpp):
- One TCP client per Dolphin run; the listen socket closes after accept.
  Boot blocks in accept() until we connect; game starts PAUSED until `c`.
- `g` returns only 32 GPRs (256 hex chars, big-endian per reg).
- `p N` reads one register (64=pc, 65=msr, 66=cr, 67=lr, 68=ctr, 69=xer).
- `Z0,addr,4` sets a software breakpoint (Dolphin internal, JIT-aware).
- `Z2/Z3/Z4,addr,len` = write/read/access watchpoints (memchecks).
- `m addr,len` reads memory; max ~4,998 bytes per request (GDB_BFR_MAX).
- Stop reply `T` packet carries pc (reg 64) + sp (reg 1).
- Registers/memory values are big-endian hex (PowerPC).

Breakpoints (Ghidra doc WMXIX-GHIDRA-MOVESET-XREF-2026-10-21):
- 0x800364F0 FUN_800364F0: move execution, arg = 12-byte descriptor
  {key, type, variant} (r3 = descriptor pointer per PPC ABI).
- 0x8007609C FUN_8007609C: Table A packed-key lookup.
- 0x80075FB8 FUN_80075FB8: Table B name lookup.

At each 0x800364F0 hit we log the descriptor + all GPRs + a scan of GPRs
for pointers into MEM1 whose +0x514 holds 4 ASCII Defwres codes (the
wrestler identity, copied by FUN_801CD9B8 into the live wrestler object).

Usage:
  python3 w7_rsp.py --host 127.0.0.1 --port 9090 --hits 200 --out hits.jsonl
    (run ON the VM; Dolphin must already be listening on the GDB port)
"""
import argparse
import json
import socket
import sys
import time


def hexsum(data: bytes) -> int:
    return sum(data) & 0xFF


class RSP:
    def __init__(self, host, port, timeout=10.0):
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        self.buf = b""

    def _read(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError("stub closed the connection")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def _read_packet(self):
        """Read one $...#cc packet (or a 1-char response like + / - / 0x03)."""
        while True:
            c = self._read(1)
            if c == b"$":
                break
            if c in (b"+", b"-"):
                continue
            if c == b"\x03":
                continue
        data = bytearray()
        while True:
            c = self._read(1)
            if c == b"#":
                break
            if c == b"}":  # RSP escape: next byte XOR 0x20
                data.append(self._read(1)[0] ^ 0x20)
            else:
                data.append(c[0])
        csum = self._read(2)
        # ack
        try:
            self.sock.sendall(b"+")
        except OSError:
            pass
        return bytes(data)

    def cmd(self, payload: bytes, expect_ack=True):
        pkt = b"$" + payload + b"#" + ("%02x" % hexsum(payload)).encode()
        self.sock.sendall(pkt)
        # read ack
        if expect_ack:
            c = self._read(1)
            if c == b"-":
                # resend once
                self.sock.sendall(pkt)
                c = self._read(1)
        # The stub may (re)send a stop notification (T...) before the reply
        # to a query (observed after an interrupt: the T packet arrives
        # twice). Skip stray stop packets and return the real reply.
        while True:
            data = self._read_packet()
            if data.startswith(b"T"):
                continue
            return data

    def cmd_noreply(self, payload: bytes):
        """Send a command whose reply comes later (e.g. `c`)."""
        pkt = b"$" + payload + b"#" + ("%02x" % hexsum(payload)).encode()
        self.sock.sendall(pkt)
        c = self._read(1)  # ack
        if c == b"-":
            self.sock.sendall(pkt)
            self._read(1)

    def wait_stop(self, timeout=None):
        if timeout is not None:
            self.sock.settimeout(timeout)
        try:
            return self._read_packet()
        finally:
            self.sock.settimeout(10.0)

    # --- typed helpers -------------------------------------------------
    def read_regs(self):
        data = self.cmd(b"g")
        hexs = data.decode()
        regs = []
        for i in range(32):
            regs.append(int(hexs[i * 8:(i + 1) * 8], 16))
        return regs

    def read_reg(self, n):
        data = self.cmd(("p%x" % n).encode())
        return int(data.decode(), 16)

    def read_mem(self, addr, length):
        out = bytearray()
        while length > 0:
            chunk = min(length, 4000)
            data = self.cmd(("m%x,%x" % (addr, chunk)).encode())
            # Real RSP errors are exactly 3 bytes (EXX). A memory reply is
            # long hex; it may legitimately START with hex digit E (first
            # byte 0xE0-0xEF). Only treat 3-byte E.. replies as errors.
            if data.startswith(b"E") and len(data) == 3:
                raise IOError("memory read error at 0x%x: %s" % (addr, data))
            out += bytes.fromhex(data.decode())
            addr += chunk
            length -= chunk
        return bytes(out)

    def set_bp(self, addr):
        data = self.cmd(("Z0,%x,4" % addr).encode())
        return data == b"OK"

    def clear_bp(self, addr):
        data = self.cmd(("z0,%x,4" % addr).encode())
        return data == b"OK"


def is_defwres_code(b4: bytes) -> bool:
    """4 ASCII chars that look like a Defwres code (e.g. A002, B015)."""
    if len(b4) != 4:
        return False
    return (65 <= b4[0] <= 90 and all(48 <= c <= 57 for c in b4[1:4]))


def scan_wrestler(rsp, regs):
    """Find GPRs pointing into MEM1 whose +0x514 holds Defwres codes."""
    found = []
    for i, v in enumerate(regs):
        if 0x80000000 <= v < 0x81800000 and v % 4 == 0:
            try:
                blk = rsp.read_mem(v + 0x514, 16)
            except Exception:
                continue
            codes = [blk[j:j + 4] for j in range(0, 16, 4)]
            if sum(1 for c in codes if is_defwres_code(c)) >= 2:
                found.append({"reg": "r%d" % i, "obj": "0x%x" % v,
                              "codes": [c.decode("ascii", "replace") for c in codes]})
    return found


def parse_stop(pkt: bytes):
    """Parse a T stop packet; return dict with pc/sp if present."""
    if not pkt.startswith(b"T"):
        return {"raw": pkt.decode("latin1")}
    s = pkt[1:].decode()
    sig = s[:2]
    rest = s[2:]
    regs = {}
    for part in rest.split(";"):
        if ":" in part:
            num, val = part.split(":", 1)
            try:
                # values are target-byte-order hex; PPC is big-endian
                regs[int(num, 16)] = int(val, 16)
            except ValueError:
                pass
    return {"signal": sig, "regs": regs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=9090)
    ap.add_argument("--hits", type=int, default=200, help="max breakpoint hits to log")
    ap.add_argument("--bps", default="800364F0,8007609C,80075FB8",
                    help="comma-separated breakpoint addresses (hex, no 0x)")
    ap.add_argument("--out", default="hits.jsonl")
    ap.add_argument("--dump-around", type=int, default=0,
                    help="on first 0x800364F0 hit, dump this many bytes around the descriptor ptr")
    ap.add_argument("--timeout", type=float, default=900, help="overall seconds")
    args = ap.parse_args()

    names = {0x800364F0: "move_exec", 0x8007609C: "tableA_lookup", 0x80075FB8: "tableB_lookup"}
    bps = {}
    for h in args.bps.split(","):
        a = int(h.strip(), 16)
        bps[a] = names.get(a, "bp@0x%x" % a)
    rsp = RSP(args.host, args.port)
    print("connected to stub", flush=True)
    # handshake
    print("qSupported:", rsp.cmd(b"qSupported:multiprocess+;qRelocInsn+"), flush=True)
    rsp.cmd(b"Hc-1")
    rsp.cmd(b"Hh-1")
    for addr, name in bps.items():
        ok = rsp.set_bp(addr)
        print("breakpoint 0x%x (%s): %s" % (addr, name, "OK" if ok else "FAILED"), flush=True)
        if not ok:
            print("FATAL: could not set breakpoint", flush=True)
            sys.exit(1)

    out = open(args.out, "w")
    t0 = time.time()
    nhits = 0
    dumped = False
    rsp.cmd_noreply(b"c")
    print("continued; waiting for stops...", flush=True)
    try:
        while nhits < args.hits and time.time() - t0 < args.timeout:
            pkt = rsp.wait_stop(timeout=max(1.0, args.timeout - (time.time() - t0)))
            if pkt == b"W00" or pkt.startswith(b"W"):
                print("target exited:", pkt, flush=True)
                break
            stop = parse_stop(pkt)
            regs = stop.get("regs", {})
            pc = regs.get(64)
            if pc is None:
                try:
                    pc = rsp.read_reg(64)
                except Exception as e:
                    print("could not read pc:", e, flush=True)
                    pc = 0
            # The stop PC is the breakpoint address (Dolphin stops AT the bp).
            name = bps.get(pc, "unknown@0x%x" % pc if pc else "unknown")
            rec = {"t": round(time.time() - t0, 3), "pc": "0x%x" % pc, "bp": name,
                   "signal": stop.get("signal")}
            try:
                gprs = rsp.read_regs()
                rec["gprs"] = ["0x%x" % r for r in gprs]
            except Exception as e:
                rec["regs_error"] = str(e)
                gprs = []
            if pc == 0x800364F0 and gprs:
                desc_ptr = gprs[3]
                rec["desc_ptr"] = "0x%x" % desc_ptr
                try:
                    desc = rsp.read_mem(desc_ptr, 12)
                    import struct as _s
                    key, typ, variant = _s.unpack(">III", desc)
                    rec["descriptor"] = {"key": key, "key_hex": "0x%x" % key,
                                         "type": typ, "variant": variant}
                except Exception as e:
                    rec["desc_error"] = str(e)
                try:
                    rec["wrestler"] = scan_wrestler(rsp, gprs)
                except Exception as e:
                    rec["wrestler_error"] = str(e)
                if args.dump_around and not dumped:
                    dumped = True
                    try:
                        lo = desc_ptr - args.dump_around // 2
                        blob = rsp.read_mem(lo, args.dump_around)
                        fn = args.out + ".dump"
                        open(fn, "wb").write(blob)
                        rec["dump"] = {"file": fn, "base": "0x%x" % lo, "len": len(blob)}
                    except Exception as e:
                        rec["dump_error"] = str(e)
            out.write(json.dumps(rec) + "\n")
            out.flush()
            nhits += 1
            print("hit %d: %s pc=0x%x %s" % (nhits, name, pc,
                  rec.get("descriptor", "")), flush=True)
            rsp.cmd_noreply(b"c")
    except (ConnectionError, socket.timeout) as e:
        print("stop waiting:", e, flush=True)
    finally:
        out.close()
    print("done: %d hits logged to %s" % (nhits, args.out), flush=True)


if __name__ == "__main__":
    main()
