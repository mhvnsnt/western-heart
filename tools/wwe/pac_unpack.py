#!/usr/bin/env python3
"""WWE 2K .pac unpacker (Yukes HSPC/SHDC/EPK8/EPAC/PACH containers).

Re-port of the container formats as publicly documented by the
WrestleMINUS project (MIT, github.com/pozzum/WrestleMINUS). The format
knowledge (header layouts, table offsets, compression wrappers) was
studied from that project's documentation and re-implemented here in
original Python code; no WrestleMINUS code was copied.

Supported containers (detected by 4-byte magic):
  HSPC  primary container, 2K17+ (hash-named entries)
  EPK8  primary container, 2K15/2K16 (directory tree)
  EPAC  primary container, older games (directory tree)
  SHDC  secondary container, 2K17+ (numbered parts)
  PACH  secondary container, 2K15/2K16 (numbered parts)
  DUMY  single-part wrapper
  TextureLibrary  named texture list (DDS etc.)
  YANMPack  animation pack (big-endian part table)

Supported compression (detected by magic, decompressed, then re-examined):
  ZLIB  "ZLIB" wrapper (stdlib zlib)
  BPE   "BPE " wrapper (yuke_bpe.py, pure Python)
  OODL  "OODL" wrapper, Oodle Kraken (libooz via oodle_krk.py;
        falls back to the `ooz` command-line tool if the library
        is not built)

Leaf files are written with an extension from their detected type:
  YOBJ (.yobj), DDS (.dds), OneT (.onet), YANM (.yanm), else .bin.

Output layout mirrors the original batch-1 extraction:
  <out>/<pac-relative-path>/<hspc-entry-hash>/<part-id>.<ext>

Usage:
  pac_unpack.py <pac-file-or-dir>... --out <dir> [--list] [--manifest FILE]
  --list      only print the container tree, do not write files
  --manifest  write a sha256 manifest of everything written (default:
              <out>/FILES-SHA256.txt)
"""

import argparse
import ctypes
import hashlib
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yuke_bpe  # noqa: E402

try:
    import oodle_krk  # noqa: E402
except Exception:  # library/CLI missing: OODL chunks will be skipped
    oodle_krk = None


# ---------------------------------------------------------------- types

def detect(data, off=0):
    """Detect the type of the blob starting at off (magic-based)."""
    if len(data) - off < 4:
        return "bin"
    magic = data[off:off + 4]
    if magic == b"HSPC":
        return "hspc"
    if magic == b"SHDC":
        return "shdc"
    if magic == b"EPK8":
        return "epk8"
    if magic == b"PACH":
        return "pach"
    if magic == b"EPAC":
        return "epac"
    if magic == b"ZLIB":
        return "zlib"
    if magic == b"OODL":
        return "oodl"
    if magic == b"YOBJ" or magic == b"JBOY":
        return "yobj"
    if magic == b"YANM":
        return "yanm"
    if magic == b"OneT":
        return "onet"
    if magic == b"DUMY":
        return "dumy"
    if magic == b"ARCH":
        return "arc"
    if b"BPE" in magic:
        return "bpe"
    if magic[:3] == b"DDS":
        return "dds"
    if len(data) - off >= 0x98:
        # Heuristic containers need full validation: raw motion data
        # also contains bone names like "root" at 0x24, so a magic
        # sniff alone misfires. Only claim the type when the whole
        # table parses and the entries point at real content.
        if _looks_like_yanmpack(data[off:]):
            return "yanmpack"
        if _looks_like_texlib(data[off:]):
            return "texlib"
    return "bin"


def _looks_like_yanmpack(data):
    """A real YANMPack has "root" at 0x24, a sane big-endian header
    length at 0xC, and entries (from 0x70, 0x28 stride) that point at
    YANM-magic clips."""
    if data[0x24:0x28] != b"root":
        return False
    (header_len,) = struct.unpack_from(">I", data, 0xC)
    (yanm_len,) = struct.unpack_from(">I", data, 4)
    if yanm_len == 0 or header_len < 0x98 or header_len > len(data):
        return False
    idx = 0x70
    found = 0
    while idx < header_len - 0x20:
        (eoff,) = struct.unpack_from(">I", data, idx + 0x24)
        (eln,) = struct.unpack_from(">H", data, idx + 2)
        eoff += header_len
        eln *= 0x20
        if eoff + eln > len(data):
            return False
        if data[eoff:eoff + 4] != b"YANM":
            return False
        found += 1
        idx += 0x28
    return found > 0


def _looks_like_texlib(data):
    """A real TextureLibrary has a sane count in byte 0 (or byte 3
    if byte-swapped) and entries whose offset/length stay in range
    with a known 3-letter type code."""
    count = data[0]
    swapped = False
    if count == 0:
        count = data[3]
        swapped = True
    if count == 0 or count > 64:
        return False
    if data[0x20:0x23] not in (b"dds", b"tex", b"ymx", b"map", b"hkx",
                               b"pac", b"txt", b"cvx", b"bin", b"tpl"):
        return False
    base = 0x10
    if swapped:
        (ln,) = struct.unpack_from(">I", data, base + 0x14)
        (off,) = struct.unpack_from(">I", data, base + 0x18)
    else:
        ln = struct.unpack_from("<I", data, base + 0x14)[0]
        off = struct.unpack_from("<Q", data, base + 0x18)[0]
    return 0 < ln and off + ln <= len(data)


EXT_BY_TYPE = {
    "yobj": "yobj",
    "dds": "dds",
    "onet": "onet",
    "yanm": "yanm",
    "arc": "arc",
    "bin": "bin",
}


# ------------------------------------------------------------ containers
# Each parser returns a list of (name, offset, length) relative to the
# start of the container blob. Offsets are absolute inside the blob.

def _u32(data, off):
    return struct.unpack_from("<I", data, off)[0]


def _u64(data, off):
    return struct.unpack_from("<Q", data, off)[0]


def parse_hspc(data):
    """HSPC: file count at 0x38; name table at 0x800 (8-byte names,
    0x14 stride); info table at the 0x800-aligned filename length +
    0x1000 (offset*0x800, length*0x100, 0xC stride)."""
    count = _u32(data, 0x38)
    fnl = _u32(data, 0x18)
    table = fnl - (fnl % 0x800) + 0x1000
    out = []
    for i in range(count):
        name = data[0x800 + i * 0x14:0x800 + i * 0x14 + 8].hex().upper()
        off = _u32(data, table + i * 0xC) * 0x800
        ln = _u32(data, table + i * 0xC + 4) * 0x100
        if off == 0 and ln == 0:
            continue
        out.append((name, off, ln))
    return out


def parse_shdc(data):
    """SHDC: header flavour at 0xC (1 = plain, 0x10 = 0x10 spacer,
    0x800 = 0x800-scaled); info table at 0x1C (flavour 1); entries
    are 0x10 bytes (name u32, offset u32, length u64). The part count
    lives at 0x38; the byte length at 0x20 is the table's allocated
    size and can be larger than count*0x10 (nested SHDCs in _param
    files), so the count field wins when sane."""
    flavour = _u32(data, 0x0C)
    info_len = _u32(data, 0x20)
    if flavour == 1:
        info_off = _u32(data, 0x1C)
    elif flavour == 0x10:
        tmp = _u32(data, 0x18)
        if tmp % 0x10:
            tmp += 0x10 - (tmp % 0x10)
        info_off = tmp + 0x40 + 0x10
    elif flavour == 0x800:
        info_off = _u32(data, 0x1C) * 0x800
    else:
        raise ValueError(f"unknown SHDC flavour 0x{flavour:X}")
    count = _u32(data, 0x38)
    by_len = info_len // 0x10
    by_room = (len(data) - info_off) // 0x10 if info_off < len(data) else 0
    if count == 0:
        count = by_len
    else:
        count = min(count, by_len, by_room)
    out = []
    for i in range(count):
        name = _u32(data, info_off + i * 0x10)
        if name == 0xFFFFFFFF:
            continue
        if name == 0x42494C5A:
            # "ZLIB" footer/index record, not a data part: its
            # "length" u64 packs (stream_len, uncompressed_len) of
            # the first ZLIB part, and its "offset" points inside
            # that part's stream. Skipping loses nothing.
            continue
        off = _u32(data, info_off + i * 0x10 + 4)
        ln = _u64(data, info_off + i * 0x10 + 8)
        out.append((f"{name:04X}", off, ln))
    return out


def parse_pach(data):
    """PACH: part count at 4; 0xC entries at 0x8 (name u32, offset u32,
    length u32); data starts after the table."""
    count = _u32(data, 4)
    base = 0x8 + count * 0xC
    out = []
    for i in range(count):
        name = _u32(data, 0x8 + i * 0xC)
        off = _u32(data, 0xC + i * 0xC) + base
        ln = _u32(data, 0x10 + i * 0xC)
        out.append((f"{name:04X}", off, ln))
    return out


def parse_epk8(data):
    """EPK8: directory tree at 0x800. Each directory: 4-char name,
    u16 count/4 at +4; entries at +0xC, 0x10 stride (8-char name,
    offset*0x800 + 0x4000, length*0x100)."""
    header_len = _u32(data, 4)
    out = []
    idx = 0
    while idx < header_len - 1:
        dirname = data[0x800 + idx:0x800 + idx + 4].decode("latin1")
        count = struct.unpack_from("<H", data, 0x800 + idx + 4)[0] // 4
        idx += 0xC
        for _ in range(count):
            name = data[0x800 + idx:0x800 + idx + 8].decode("latin1").strip("\x00 ")
            off = _u32(data, 0x800 + idx + 8) * 0x800 + 0x4000
            ln = _u32(data, 0x800 + idx + 12) * 0x100
            out.append((f"{dirname}/{name}", off, ln))
            idx += 0x10
    return out


def parse_epac(data):
    """EPAC: like EPK8 but count/3, 4-char entry names, 0xC stride."""
    header_len = _u32(data, 4)
    out = []
    idx = 0
    while idx < header_len - 1:
        dirname = data[0x800 + idx:0x800 + idx + 4].decode("latin1")
        count = struct.unpack_from("<H", data, 0x800 + idx + 4)[0] // 3
        idx += 0xC
        for _ in range(count):
            name = data[0x800 + idx:0x800 + idx + 4].decode("latin1").strip("\x00 ")
            off = _u32(data, 0x800 + idx + 4) * 0x800 + 0x4000
            ln = _u32(data, 0x800 + idx + 8) * 0x100
            out.append((f"{dirname}/{name}", off, ln))
            idx += 0xC
    return out


def parse_dumy(data):
    """DUMY: big-endian header length at 4; one part after it."""
    (header_len,) = struct.unpack_from(">I", data, 4)
    off = 0x8 + header_len
    return [("0000", off, len(data) - off)]


def parse_texlib(data):
    """TextureLibrary: count in byte 0 (or byte 3 if byte-swapped);
    0x20 entries at 0x10 (name 16 chars, type 3 chars at +0x10,
    length u32 at +0x14, offset u64 at +0x18)."""
    count = data[0]
    swapped = False
    if count == 0:
        count = data[3]
        swapped = True
    out = []
    for i in range(count):
        base = i * 0x20 + 0x10
        name = data[base:base + 0x10].split(b"\x00")[0].decode("latin1")
        ftype = data[base + 0x10:base + 0x13].decode("latin1").lower()
        if swapped:
            ln = struct.unpack_from(">I", data, base + 0x14)[0]
            off = struct.unpack_from(">I", data, base + 0x18)[0]
        else:
            ln = _u32(data, base + 0x14)
            off = _u64(data, base + 0x18)
        out.append((f"{name}.{ftype}", off, ln))
    return out


def parse_yanmpack(data):
    """YANMPack: big-endian header length at 0xC, YANM length at 4;
    entries start at 0x70, 0x28 stride (name 8 chars at +4,
    offset BE u32 at +0x24 + header length, length BE u16 at +2 * 0x20)."""
    (header_len,) = struct.unpack_from(">I", data, 0xC)
    (yanm_len,) = struct.unpack_from(">I", data, 4)
    out = []
    if yanm_len == 0:
        return out
    idx = 0x70
    while idx < header_len - 0x20:
        name = data[idx + 4:idx + 12].decode("latin1").strip("\x00 ")
        (off,) = struct.unpack_from(">I", data, idx + 0x24)
        (ln,) = struct.unpack_from(">H", data, idx + 2)
        out.append((name, off + header_len, ln * 0x20))
        idx += 0x28
    return out


PARSERS = {
    "hspc": parse_hspc,
    "shdc": parse_shdc,
    "pach": parse_pach,
    "epk8": parse_epk8,
    "epac": parse_epac,
    "dumy": parse_dumy,
    "texlib": parse_texlib,
    "yanmpack": parse_yanmpack,
}


# ---------------------------------------------------------- decompression

def decompress_zlib(blob):
    """ZLIB wrapper: u32@8 compressed length, u32@12 uncompressed
    length, zlib stream at 0x10."""
    comp_len = _u32(blob, 8)
    return zlib.decompress(blob[0x10:0x10 + comp_len])


def decompress_bpe(blob):
    return yuke_bpe.decompress(blob)


def decompress_oodle(blob):
    """OODL wrapper (v6): u32@0x10 uncompressed length, u32@0x14
    compressed length, Kraken stream at 0x18. v7 swaps the two
    length fields (compressed at 0xC, uncompressed at 0x14)."""
    if oodle_krk is None:
        raise RuntimeError("oodle_krk unavailable (libooz not built)")
    uncomp_len = _u32(blob, 0x10)
    comp_len = _u32(blob, 0x14)
    # v7 detection: v6 header has "KRKN" at 0xC; v7 has the length there
    if blob[0xC:0x10] != b"KRKN":
        comp_len = _u32(blob, 0x0C)
        uncomp_len = _u32(blob, 0x14)
    stream = blob[0x18:0x18 + comp_len]
    return oodle_krk.decompress(stream, uncomp_len)


DECOMPRESSORS = {
    "zlib": decompress_zlib,
    "bpe": decompress_bpe,
    "oodl": decompress_oodle,
}


# ---------------------------------------------------------------- unpack

class Stats:
    def __init__(self):
        self.files = 0
        self.bytes = 0
        self.containers = 0
        self.decompressed = {}
        self.skipped = []
        self.errors = []

    def note_decomp(self, kind):
        self.decompressed[kind] = self.decompressed.get(kind, 0) + 1


def unpack_blob(blob, outdir, fname, stats, manifest, list_only=False,
                depth=0, disp=None, flat=False):
    """Recursively unpack one blob (a whole file or a container part).

    Containers become directories named after the entry; compressed
    blobs are decompressed in place and re-examined under the same
    name; leaves are written as <fname>.<ext> (or <fname> if it
    already carries an extension). `disp` is the display path used
    only for logging/errors. With flat=True, heuristic containers
    (YANMPack, TextureLibrary) are kept as single .bin leaves,
    matching the original batch-1 extraction layout.
    """
    if disp is None:
        disp = fname
    if depth > 12:
        stats.errors.append(f"{disp}: recursion too deep")
        return
    kind = detect(blob)
    if flat and kind in ("yanmpack", "texlib"):
        kind = "bin"
    if kind in PARSERS:
        stats.containers += 1
        try:
            parts = PARSERS[kind](blob)
        except Exception as exc:
            stats.errors.append(f"{disp}: {kind} parse failed: {exc}")
            return
        for pname, off, ln in parts:
            if off + ln > len(blob):
                stats.skipped.append(
                    f"{disp}/{pname}: part out of range "
                    f"(off 0x{off:X} len 0x{ln:X} in 0x{len(blob):X})")
                continue
            part = blob[off:off + ln]
            # Quirk: in some EVZ2 SHDCs the part length counts the
            # ZLIB stream only, not the 16-byte wrapper header, so
            # the slice is 16 bytes short of the full stream (the
            # stream's tail sits in the gap before the next part).
            # Extend the slice from the parent buffer using the
            # wrapper's declared compressed length.
            if part[:4] == b"ZLIB" and len(part) >= 16:
                need = off + 0x10 + _u32(part, 8)
                if need > off + ln and need <= len(blob):
                    part = blob[off:need]
            sub_kind = detect(part)
            if flat and sub_kind in ("yanmpack", "texlib"):
                sub_kind = "bin"
            if sub_kind in PARSERS:
                subdir = os.path.join(outdir, pname)
                unpack_blob(part, subdir, pname, stats, manifest,
                            list_only, depth + 1, f"{disp}/{pname}", flat)
            elif sub_kind in DECOMPRESSORS:
                # Decompress here (looping for nested compression) and
                # then decide: a container gets its own directory, a
                # leaf is written directly under outdir. Giving every
                # compressed part a subdirectory first would double
                # the leaf path (pname/pname.ext).
                plain = part
                ok = True
                while detect(plain) in DECOMPRESSORS:
                    dk = detect(plain)
                    try:
                        plain = DECOMPRESSORS[dk](plain)
                    except Exception as exc:
                        stats.errors.append(
                            f"{disp}/{pname}: {dk} decompress failed: "
                            f"{exc}")
                        ok = False
                        break
                    stats.note_decomp(dk)
                if not ok:
                    continue
                plain_kind = detect(plain)
                if flat and plain_kind in ("yanmpack", "texlib"):
                    plain_kind = "bin"
                if plain_kind in PARSERS:
                    subdir = os.path.join(outdir, pname)
                    unpack_blob(plain, subdir, pname, stats, manifest,
                                list_only, depth + 1, f"{disp}/{pname}",
                                flat)
                else:
                    write_leaf(plain, outdir, pname, stats, manifest,
                               list_only)
            else:
                write_leaf(part, outdir, pname, stats, manifest, list_only)
        return
    if kind in DECOMPRESSORS:
        try:
            plain = DECOMPRESSORS[kind](blob)
        except Exception as exc:
            stats.errors.append(f"{disp}: {kind} decompress failed: {exc}")
            return
        stats.note_decomp(kind)
        unpack_blob(plain, outdir, fname, stats, manifest, list_only,
                    depth + 1, disp, flat)
        return
    write_leaf(blob, outdir, fname, stats, manifest, list_only)


def write_leaf(blob, outdir, name, stats, manifest, list_only=False):
    kind = detect(blob)
    ext = EXT_BY_TYPE.get(kind, "bin")
    if "." in os.path.basename(name):
        fname = name
    else:
        fname = f"{name}.{ext}"
    rel = os.path.join(outdir, fname)
    if list_only:
        print(f"  {rel} ({len(blob)} bytes, {kind})")
        return
    # makedirs the file's own parent: EPK8 tree names can contain
    # slashes (e.g. EVP3/109), so outdir alone is not enough.
    os.makedirs(os.path.dirname(rel), exist_ok=True)
    with open(rel, "wb") as f:
        f.write(blob)
    stats.files += 1
    stats.bytes += len(blob)
    manifest.append((rel, hashlib.sha256(blob).hexdigest()))


def unpack_file(pac_path, out_root, stats, manifest, list_only=False,
                root=None, flat=False):
    with open(pac_path, "rb") as f:
        blob = f.read()
    kind = detect(blob)
    if kind not in PARSERS and kind not in DECOMPRESSORS:
        stats.skipped.append(f"{pac_path}: not a PAC ({kind})")
        return
    # Mirror the PAC's path relative to --root (minus .pac) under out_root,
    # so pac/ingame/motion/body/50_mpc.pac lands in out/ingame/motion/body/50_mpc/.
    if root:
        rel = os.path.relpath(pac_path, root)
    else:
        rel = os.path.basename(pac_path)
    rel = os.path.splitext(rel)[0]
    outdir = os.path.join(out_root, rel)
    print(f"{pac_path} ({len(blob)} bytes, {kind}) -> {outdir}")
    unpack_blob(blob, outdir, os.path.basename(rel), stats, manifest,
                list_only, disp=rel, flat=flat)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Unpack WWE 2K .pac files.")
    ap.add_argument("inputs", nargs="+",
                    help=".pac files or directories to scan for .pac files")
    ap.add_argument("--out", required=True, help="output root directory")
    ap.add_argument("--root", default=None,
                    help="depot root: PAC paths are mirrored relative to it")
    ap.add_argument("--list", action="store_true",
                    help="list the container tree, write nothing")
    ap.add_argument("--flat", action="store_true",
                    help="keep YANMPack/TextureLibrary parts as single .bin "
                    "leaves (batch-1 layout) instead of recursing into them")
    ap.add_argument("--manifest", default=None,
                    help="sha256 manifest path (default: <out>/FILES-SHA256.txt)")
    args = ap.parse_args(argv)

    pacs = []
    for inp in args.inputs:
        if os.path.isdir(inp):
            for root, _dirs, files in os.walk(inp):
                for fn in sorted(files):
                    if fn.lower().endswith(".pac"):
                        pacs.append(os.path.join(root, fn))
        else:
            pacs.append(inp)
    pacs.sort()
    print(f"{len(pacs)} PAC file(s)")

    stats = Stats()
    manifest = []
    for pac in pacs:
        try:
            unpack_file(pac, args.out, stats, manifest, args.list,
                        root=args.root, flat=args.flat)
        except Exception as exc:
            stats.errors.append(f"{pac}: {exc}")

    print(f"\nfiles written: {stats.files} ({stats.bytes} bytes)")
    print(f"containers parsed: {stats.containers}")
    print(f"decompressed: {stats.decompressed}")
    if stats.skipped:
        print(f"skipped ({len(stats.skipped)}):")
        for s in stats.skipped:
            print(f"  {s}")
    if stats.errors:
        print(f"errors ({len(stats.errors)}):")
        for s in stats.errors:
            print(f"  {s}")
    if manifest and not args.list:
        mpath = args.manifest or os.path.join(args.out, "FILES-SHA256.txt")
        with open(mpath, "w") as f:
            for rel, sha in sorted(manifest):
                f.write(f"{sha}  {rel}\n")
        print(f"manifest: {mpath} ({len(manifest)} entries)")
    return 0 if not stats.errors else 1


if __name__ == "__main__":
    sys.exit(main())
