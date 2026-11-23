#!/usr/bin/env python3
"""Emulate the game's MIPS BPE decoder (0x80048a20) with Unicorn.

Compares the game's ACTUAL decoder execution against the Python decoder
(bpe.py) for a given section. Reports output match/mismatch, instruction
count, and (with --trace) a step-by-step divergence log.

Usage:
  emu_bpe.py <section.bin> [--trace] [--max-ins 2000000]
"""
import struct
import sys

from unicorn import Uc, UC_ARCH_MIPS, UC_MODE_32, UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import (
    UC_MIPS_REG_PC, UC_MIPS_REG_SP, UC_MIPS_REG_RA,
    UC_MIPS_REG_A0, UC_MIPS_REG_A1, UC_MIPS_REG_T0, UC_MIPS_REG_T1,
    UC_MIPS_REG_T2, UC_MIPS_REG_T3, UC_MIPS_REG_T4, UC_MIPS_REG_T5,
    UC_MIPS_REG_T7,
)

EXE_PATH = "work/tr1-files/SLPS_000.84"
DECODER_ADDR = 0x80048A20
STOP_ADDR = 0x80000000  # sentinel $ra
TEXT_BASE = 0x80010000
SCRATCH_BASE = 0x1F800000
SEC_ADDR = 0x80100000
OUT_ADDR = 0x80110000


def run_decoder(section, trace=False, max_ins=5000000):
    """Run the MIPS decoder on `section` bytes. Returns (output_bytes, info)."""
    exe = open(EXE_PATH, "rb").read()
    text = exe[0x800:0x800 + 0x65800]

    uc = Uc(UC_ARCH_MIPS, UC_MODE_32 | UC_MODE_LITTLE_ENDIAN)
    # Unicorn translates KSEG0 (0x80000000+) to physical (addr & 0x1FFFFFFF).
    # Map code/data at PHYSICAL addresses; the CPU uses virtual addresses.
    uc.mem_map(0x0, 0x200000)          # physical RAM: text @ 0x10000, bufs @ 0x100000
    uc.mem_map(SCRATCH_BASE, 0x1000)   # KSEG1 scratchpad (direct-mapped)
    uc.mem_write(TEXT_BASE & 0x1FFFFFFF, text)
    # Zero scratchpad (fresh boot state)
    uc.mem_write(SCRATCH_BASE, b"\x00" * 0x400)
    # Write section + zero output buffer (at physical addresses)
    uc.mem_write(SEC_ADDR & 0x1FFFFFFF, section)
    dsize = struct.unpack_from("<I", section, 12)[0]
    uc.mem_write(OUT_ADDR & 0x1FFFFFFF, b"\x00" * (dsize + 0x100))

    uc.reg_write(UC_MIPS_REG_A0, SEC_ADDR)
    uc.reg_write(UC_MIPS_REG_A1, OUT_ADDR)
    uc.reg_write(UC_MIPS_REG_RA, STOP_ADDR)
    uc.reg_write(UC_MIPS_REG_SP, 0x801FF000)

    info = {"ins_count": 0, "trace": []}

    def hook_code(uc, address, size, user_data):
        info["ins_count"] += 1
        if trace and info["ins_count"] % 1000 == 0:
            info["trace"].append((address, uc.reg_read(UC_MIPS_REG_T0),
                                  uc.reg_read(UC_MIPS_REG_T1)))
        if info["ins_count"] > max_ins:
            uc.emu_stop()
            info["timeout"] = True

    from unicorn import UC_HOOK_CODE
    uc.hook_add(UC_HOOK_CODE, hook_code)

    try:
        uc.emu_start(DECODER_ADDR, STOP_ADDR, count=max_ins)
    except Exception as e:
        info["error"] = str(e)

    out = bytes(uc.mem_read(OUT_ADDR & 0x1FFFFFFF, dsize))
    info["t0"] = uc.reg_read(UC_MIPS_REG_T0)
    info["t1"] = uc.reg_read(UC_MIPS_REG_T1)
    # Scratchpad heap contents (for inspection)
    info["heap"] = bytes(uc.mem_read(SCRATCH_BASE + 0x300, 64))
    return out, info


if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from bpe import decompress_section

    path = sys.argv[1]
    trace = "--trace" in sys.argv
    section = open(path, "rb").read()
    expected = decompress_section(section)
    out, info = run_decoder(section, trace=trace)
    print(f"section: {path} ({len(section)}B)")
    print(f"MIPS decoder output: {len(out)}B, Python expected: {len(expected)}B")
    print(f"match: {out == expected}")
    print(f"instructions: {info['ins_count']}")
    if info.get("error"):
        print(f"ERROR: {info['error']}")
    if info.get("timeout"):
        print("TIMEOUT (infinite loop?)")
    if out != expected:
        for i in range(min(len(out), len(expected))):
            if out[i] != expected[i]:
                print(f"first output diff at {i} (0x{i:x}): MIPS={out[i]:02x} Python={expected[i]:02x}")
                break
        else:
            print(f"length differs but prefix matches ({min(len(out), len(expected))}B)")
