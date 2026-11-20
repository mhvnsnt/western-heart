#!/usr/bin/env python3
"""
psp_elf_xref.py — PSP ELF static-analysis helper for the Western Heart RE bench.

Promotes the ad-hoc helpers from the Tekken 6 DATA401 watchdog runs
(teardown/tekken6/DATA401-RE-NOTES.md, 2026-10-14) into a permanent,
tested pipeline stage. Stdlib only, except capstone (optional) for the
disassembly pass.

What it does (no Ghidra needed — runs on any Linux VM):
  1. Parses ELF32-LE program headers -> vaddr<->file-offset map.
  2. Scans code for `lui`+`addiu`/`ori` pairs -> absolute-address xrefs
     (code vaddr -> data vaddr). PSP binaries have no section headers, so
     this replaces symbol-based xrefs.
  3. Finds NUL-terminated ASCII strings and reports xrefs to a watchlist
     (DATA401, DINF, openPac, ktRead, packdatas_t, disc0:/sce_lbn, ...).
  4. Hunts crypto constants: AES S-box head, TEA/XTEA delta 0x9E3779B9,
     CRC32 table, XOR-0xA5 string-decrypt idiom (addiu $x,$zero,-91),
     plus Tekken 6 session constants when --t6 is given.
  5. Lists `jr $ra; nop` import-stub pairs (PSP loader patches these at
     runtime, so static call targets behind them are unresolvable — the
     report says so explicitly instead of guessing).
  6. Optionally disassembles an address range with capstone (MIPS32-LE).

Usage:
  python3 psp_elf_xref.py EBOOT.DECRYPTED.ELF --out report.json
  python3 psp_elf_xref.py EBOOT.DECRYPTED.ELF --t6 --disasm 0x8AA1000:0x400 --out report.json
  python3 psp_elf_xref.py EBOOT.DECRYPTED.ELF --strings-only

Exit 0 + JSON report on stdout (or --out). All addresses are vaddrs.
"""

import argparse
import json
import struct
import sys

try:
    from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN
    HAVE_CAPSTONE = True
except ImportError:
    HAVE_CAPSTONE = False

# ---------------------------------------------------------------- ELF parse

def parse_elf(path):
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] != b"\x7fELF" or data[4] != 1 or data[5] != 1:
        raise SystemExit("not an ELF32-LE file")
    e_phoff, = struct.unpack_from("<I", data, 0x1C)
    e_phentsize, e_phnum = struct.unpack_from("<HH", data, 0x2A)
    entry, = struct.unpack_from("<I", data, 0x18)
    segs = []
    for i in range(e_phnum):
        o = e_phoff + i * e_phentsize
        p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = \
            struct.unpack_from("<IIIIIIII", data, o)
        if p_type == 1:  # PT_LOAD
            segs.append({"offset": p_offset, "vaddr": p_vaddr,
                         "filesz": p_filesz, "memsz": p_memsz})
    if not segs:
        raise SystemExit("no PT_LOAD segments")
    return data, segs, entry


def make_xlat(data, segs):
    def v2f(vaddr):
        for s in segs:
            if s["vaddr"] <= vaddr < s["vaddr"] + s["filesz"]:
                return vaddr - s["vaddr"] + s["offset"]
        return None

    def f2v(off):
        for s in segs:
            if s["offset"] <= off < s["offset"] + s["filesz"]:
                return off - s["offset"] + s["vaddr"]
        return None

    def read_word(vaddr):
        fo = v2f(vaddr)
        if fo is None or fo + 4 > len(data):
            return None
        return struct.unpack_from("<I", data, fo)[0]

    return v2f, f2v, read_word


# ------------------------------------------------------- lui/addiu xref scan

def sign16(x):
    return x - 0x10000 if x & 0x8000 else x


def scan_lui_pairs(data, segs, v2f, f2v):
    """Find lui rt,hi / addiu|ori rt,rt,lo pairs -> {code_vaddr: data_vaddr}."""
    xrefs = {}
    for s in segs:
        start, end = s["offset"], s["offset"] + s["filesz"]
        # Only scan plausible code: keep it simple, scan everything; pairs are
        # distinctive enough (lui followed within 4 insns by addiu/ori on same rt).
        words = struct.unpack("<%dI" % ((end - start) // 4), data[start:end])
        n = len(words)
        for i, w in enumerate(words):
            if (w >> 26) != 0x0F:  # lui
                continue
            rt = (w >> 16) & 0x1F
            hi = w & 0xFFFF
            for j in range(i + 1, min(i + 5, n)):
                w2 = words[j]
                op = w2 >> 26
                rs, rt2 = (w2 >> 21) & 0x1F, (w2 >> 16) & 0x1F
                if op in (0x09, 0x0D) and rs == rt and rt2 == rt:
                    lo = w2 & 0xFFFF
                    addr = ((hi << 16) + (sign16(lo) if op == 0x09 else lo)) & 0xFFFFFFFF
                    code_v = f2v(start + i * 4)
                    if code_v is not None and 0x8800000 <= addr < 0xC000000:
                        xrefs.setdefault(addr, []).append(code_v)
                    break
    return xrefs


# ------------------------------------------------------------------ strings

def scan_strings(data, segs, f2v, minlen=4):
    out = []
    for s in segs:
        start, end = s["offset"], s["offset"] + s["filesz"]
        i = start
        while i < end:
            if 32 <= data[i] < 127:
                j = i
                while j < end and 32 <= data[j] < 127:
                    j += 1
                if j < end and data[j] == 0 and j - i >= minlen:
                    out.append({"vaddr": f2v(i), "text": data[i:j].decode()})
                    i = j
            i += 1
    return out


WATCHLIST_DEFAULT = ["DATA401", "DINF", "openPac", "ktRead", "packdatas_t",
                     "disc0:/sce_lbn", "ReadInfo", ".pac", ".PAC", "sceIo",
                     "KIRK", "kirk", "crypt", "decrypt", "key"]

# ---------------------------------------------------------- crypto constant
# hunts

AES_SBOX_HEAD = bytes([0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5])
TEA_DELTA = 0x9E3779B9
CRC32_POLY_WORDS = None  # built lazily: standard CRC32 table first row


def build_crc32_table():
    t = []
    for i in range(256):
        c = i
        for _ in range(8):
            c = 0xEDB88320 ^ (c >> 1) if c & 1 else c >> 1
        t.append(c & 0xFFFFFFFF)
    return t


def hunt_crypto(data, segs, t6=False):
    hits = []
    blobs = [(s["offset"], s["offset"] + s["filesz"]) for s in segs]

    def add(kind, fo, detail):
        hits.append({"kind": kind, "file_offset": fo, "detail": detail})

    # AES S-box head
    pos = data.find(AES_SBOX_HEAD)
    while pos != -1:
        add("aes_sbox", pos, "AES S-box head bytes found")
        pos = data.find(AES_SBOX_HEAD, pos + 1)
    # TEA/XTEA delta as lui/ori material or raw word
    for pat in (struct.pack("<I", TEA_DELTA), struct.pack(">I", TEA_DELTA)):
        pos = data.find(pat)
        while pos != -1:
            add("tea_delta", pos, "0x9E3779B9 (TEA/XTEA delta)")
            pos = data.find(pat, pos + 1)
    # CRC32 table (256 LE words)
    table = struct.pack("<256I", *build_crc32_table())
    pos = data.find(table)
    while pos != -1:
        add("crc32_table", pos, "standard CRC32 (poly 0xEDB88320) table")
        pos = data.find(table, pos + 1)
    # XOR-0xA5 idiom: addiu $rt,$zero,-91 -> LE bytes A5 FF rt 24, rs==0.
    # memmem for the 2-byte head, then verify the remaining bytes.
    pos = 0
    while True:
        pos = data.find(b"\xa5\xff", pos)
        if pos == -1 or pos + 4 > len(data):
            break
        b2, b3 = data[pos + 2], data[pos + 3]
        if b3 == 0x24 and (b2 & 0xE0) == 0:
            add("xor_a5_idiom", pos,
                "addiu $%d,$zero,-91 (XOR 0xA5 string-decrypt idiom)" % (b2 & 0x1F))
        pos += 2
    if t6:
        for const, name in [(0xBCBD1C51, "t6 crypto header C1"),
                            (0xE8BDE039, "t6 crypto header C2"),
                            (0x38BFE591, "t6 key-extract mask 1"),
                            (0xD3610818, "t6 key-extract mask 2")]:
            pat = struct.pack("<I", const)
            pos = data.find(pat)
            while pos != -1:
                add("t6_const", pos, "%s = 0x%08X" % (name, const))
                pos = data.find(pat, pos + 1)
    # dedupe + sort
    seen = set()
    uniq = []
    for h in sorted(hits, key=lambda h: h["file_offset"]):
        k = (h["kind"], h["file_offset"])
        if k not in seen:
            seen.add(k)
            uniq.append(h)
    return uniq


# ------------------------------------------------------------- import stubs

def scan_import_stubs(data, segs, v2f, f2v):
    """`jr $ra; nop` pairs = PSP import stubs (patched by the loader)."""
    stubs = []
    for s in segs:
        start, end = s["offset"], s["offset"] + s["filesz"]
        words = struct.unpack("<%dI" % ((end - start) // 4), data[start:end])
        for i in range(len(words) - 1):
            if words[i] == 0x03E00008 and words[i + 1] == 0x00000000:
                v = f2v(start + i * 4)
                if v is not None:
                    stubs.append(v)
    # group contiguous pairs
    ranges = []
    for v in stubs:
        if ranges and v == ranges[-1][1] + 8:
            ranges[-1][1] = v
            ranges[-1][2] += 1
        else:
            ranges.append([v, v, 1])
    return {"count": len(stubs),
            "ranges": [{"start": hex(a), "end": hex(b), "stubs": c}
                       for a, b, c in ranges]}


# ------------------------------------------------------------------ disasm

def disasm_range(data, v2f, read_word, vaddr, size):
    if not HAVE_CAPSTONE:
        return {"error": "capstone not installed (pip install capstone)"}
    fo = v2f(vaddr)
    if fo is None:
        return {"error": "vaddr 0x%X not mapped" % vaddr}
    code = data[fo:fo + size]
    md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_LITTLE_ENDIAN)
    md.detail = False
    return [{"addr": hex(i.address), "mnemonic": i.mnemonic,
             "op_str": i.op_str} for i in md.disasm(code, vaddr)]


# -------------------------------------------------------------------- main

def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("elf", help="PSP decrypted ELF (ELF32-LE MIPS)")
    ap.add_argument("--out", help="write JSON report here (default: stdout)")
    ap.add_argument("--t6", action="store_true",
                    help="also hunt Tekken 6 session constants")
    ap.add_argument("--watch", nargs="*", default=WATCHLIST_DEFAULT,
                    help="string watchlist (default: built-in)")
    ap.add_argument("--strings-only", action="store_true")
    ap.add_argument("--disasm", metavar="VADDR:SIZE",
                    help="capstone-disassemble hex range, e.g. 0x8AA1000:0x400")
    ap.add_argument("--minlen", type=int, default=4)
    a = ap.parse_args(argv)

    data, segs, entry = parse_elf(a.elf)
    v2f, f2v, read_word = make_xlat(data, segs)

    report = {
        "tool": "psp_elf_xref.py",
        "file": a.elf,
        "file_size": len(data),
        "entry": hex(entry),
        "segments": [{"vaddr": hex(s["vaddr"]), "file_offset": hex(s["offset"]),
                      "filesz": hex(s["filesz"])} for s in segs],
    }

    strings = scan_strings(data, segs, f2v, a.minlen)
    report["string_count"] = len(strings)

    if a.strings_only:
        report["strings"] = strings
    else:
        xrefs = scan_lui_pairs(data, segs, v2f, f2v)
        report["lui_xref_targets"] = len(xrefs)
        watched = []
        for st in strings:
            for w in a.watch:
                if w in st["text"]:
                    watched.append({"text": st["text"], "vaddr": hex(st["vaddr"]),
                                    "xrefs": [hex(c) for c in
                                              xrefs.get(st["vaddr"], [])],
                                    "watch": w})
                    break
        report["watched_strings"] = watched
        crypto = []
        for h in hunt_crypto(data, segs, t6=a.t6):
            v = f2v(h["file_offset"])
            h = dict(h)
            h["vaddr"] = hex(v) if v is not None else None
            crypto.append(h)
        report["crypto_hits"] = crypto
        report["import_stubs"] = scan_import_stubs(data, segs, v2f, f2v)
        if a.disasm:
            v, sz = a.disasm.split(":")
            report["disasm"] = disasm_range(data, v2f, read_word, int(v, 16), int(sz, 16))

    out = json.dumps(report, indent=1)
    if a.out:
        with open(a.out, "w") as f:
            f.write(out)
        print("wrote %s (%d bytes)" % (a.out, len(out)))
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
