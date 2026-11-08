#!/usr/bin/env python3
"""romD archive reader / extractor for Tekken 5 (PS2) TK5DATA2.BIN.

STATUS: UNVALIDATED AGAINST REAL BYTES (2026-11-08). No TK5DATA2.BIN
exists in the repo or on disk anywhere found -- the Tekken 5 ISO was
deleted after the 2026-10-23 survey and only the 498-name manifest
survives (teardown/tekken5/t5_motion_manifest.txt). Everything in this
file is built from:
  - the repo's own survey (t5_survey.py, INVENTORY.md, TEARDOWN.md):
    romD magic at offset 0, CRLF filename manifest, 21 BDPK markers,
    file-table -> data-offset mapping NOT yet reversed;
  - the community toolset smb123w64gb/Tekken5_Tools (public, main,
    commit a1df701812e6b263a773f23e725a2a03d7cc27f5), read as text
    (FileTableGet.py re-read 2026-11-08 to verify the entry layout):
    FileTableGetPS2.py, FileTableGet.py, TK5AssetRipPS2.py,
    tk5psp_crypt.py (sector cipher, read in full), FileTableGet2x6.py.
    Those tools document the LUT tables for TK5DATA1/TK5DATA3 and the
    retail/beta tables -- NOT the romD table itself. This tool reuses
    their documented layouts as CANDIDATE table formats for romD and
    reports candidates; it never silently extracts on a guess.

What the tool does, in order:
  scan    verify romD magic, locate the CRLF manifest region and the
          BDPK markers, and hunt for candidate LUT tables (runs of
          plausible (sector, size) entries). Prints candidates scored
          by structural checks; extraction needs an explicit table.
  extract extract by manifest name order using a confirmed LUT
          (generic 40-byte entries or PS2 8-byte entries), decrypting
          each entry with the sector cipher (seed = entry id).
  selftest build a synthetic romD in memory and verify round-trip
          parse -> decrypt -> extract. Proves the code works
          mechanically; it does NOT prove the real romD layout.

Stdlib only. Usage:
  python3 romd_extract.py TK5DATA2.BIN --manifest t5_motion_manifest.txt --scan
  python3 romd_extract.py TK5DATA2.BIN --manifest t5_motion_manifest.txt \\
      --extract --lut generic --table-offset 0x2F82B4 --table-count 498 --out out/
  python3 romd_extract.py --selftest
"""
import argparse
import hashlib
import struct
import sys
from pathlib import Path

SECTOR = 0x800
MAGIC = b"romD"
BDPK = b"BDPK"

# Documented LUT layouts (Tekken5_Tools). Offsets below are where the
# tools look for tables in THEIR target files -- not romD.
LUT_GENERIC_ENTRY = 40   # 10 x u32: offset x0x800, size, crc[5], unk0, id, unk1 (FileTableGet.py LUT.read)
LUT_PS2_ENTRY = 8        # offset u32 x0x800, size u32 (checksums in a separate u32 array)
PS2_TABLESTART = 0x0027B5B0
PS2_CHECKSTART = 0x0027E838
PS2_TABLECOUNT = 1571
RETAIL_TABLESTART = 0x002F82B4
RETAIL_TABLECOUNT = 5004
BETA_TABLESTART = 0x26F63C
BETA_TABLECOUNT = 3030


# ---------------------------------------------------------------- cipher
def decrypt_sector_data_fast(data: bytearray, seed: int, size: int) -> None:
    """Port of tk5psp_crypt.decrypt_sector_data_fast (Tekken5_Tools).

    Keystream: 512 u32 words from an LCG, key = key*5+3 (mod 2**32),
    starting from seed. Data is XORed in 2048-byte blocks with the
    2048-byte keystream; the tail uses the first rem_len keystream bytes.
    In-place, exactly as the original.
    """
    if size <= 0:
        return
    seed &= 0xFFFFFFFF
    keystream = [0] * 512
    key = seed
    for i in range(512):
        keystream[i] = key
        key = (key * 5 + 3) & 0xFFFFFFFF
    keystream_bytes = struct.pack("<512I", *keystream)
    num_blocks = size >> 11
    rem_words = ((size & 0x7FF) + 3) >> 2
    ks_int_2048 = int.from_bytes(keystream_bytes, "little")
    offset = 0
    for _ in range(num_blocks):
        chunk = data[offset:offset + 2048]
        data[offset:offset + 2048] = (
            int.from_bytes(chunk, "little") ^ ks_int_2048
        ).to_bytes(2048, "little")
        offset += 2048
    if rem_words != 0:
        rem_len = rem_words * 4
        chunk = data[offset:offset + rem_len]
        rem_ks_int = int.from_bytes(keystream_bytes[:rem_len], "little")
        data[offset:offset + rem_len] = (
            int.from_bytes(chunk, "little") ^ rem_ks_int
        ).to_bytes(rem_len, "little")


def word_sum(data: bytes) -> int:
    """u32 little-endian word sum (FileTableGetPS2.py references a
    compute_word_sum_fast checksum; exact endianness/padding is
    UNCONFIRMED -- verify against real bytes before trusting it)."""
    n = len(data) // 4
    total = 0
    for (w,) in struct.iter_unpack("<I", data[:n * 4]):
        total = (total + w) & 0xFFFFFFFF
    return total


# ---------------------------------------------------------------- manifest
def parse_manifest(path: Path) -> list:
    names = [l.strip() for l in path.read_text().splitlines() if l.strip()]
    return names


# ---------------------------------------------------------------- LUT parsing
def parse_lut_generic(buf: bytes, start: int, count: int) -> list:
    """40-byte entries (10 x u32): offset(u32)x0x800, size(u32),
    crc[5](u32), unk0(u32), id(u32), unk1(u32). Verified against
    FileTableGet.py LUT.read (reads 1+1+5+1+1+1 u32 = 40 bytes).
    Entries with size == 0xFFFFFFFF are empty slots (skipped)."""
    entries = []
    for i in range(count):
        off = start + i * LUT_GENERIC_ENTRY
        if off + LUT_GENERIC_ENTRY > len(buf):
            break
        sector, size = struct.unpack_from("<II", buf, off)
        crc = struct.unpack_from("<5I", buf, off + 8)
        unk0, eid, unk1 = struct.unpack_from("<III", buf, off + 28)
        entries.append({"index": i, "sector": sector, "offset": sector * SECTOR,
                        "size": size, "crc": crc, "unk0": unk0, "id": eid,
                        "unk1": unk1})
    return entries


def parse_lut_ps2(buf: bytes, start: int, count: int) -> list:
    """8-byte entries: offset(u32)x0x800, size(u32). Checksums live in a
    separate u32 array (CHECKSTART in FileTableGetPS2.py)."""
    entries = []
    for i in range(count):
        off = start + i * LUT_PS2_ENTRY
        if off + LUT_PS2_ENTRY > len(buf):
            break
        sector, size = struct.unpack_from("<II", buf, off)
        entries.append({"index": i, "sector": sector, "offset": sector * SECTOR,
                        "size": size, "id": i})
    return entries


def entries_plausible(entries: list, filesize: int, min_run: int = 8) -> bool:
    """Structural checks only: offsets in-bounds and ascending, sizes
    sane. A passing run is a CANDIDATE, not a proven table."""
    if len(entries) < min_run:
        return False
    prev = -1
    for e in entries:
        if e["size"] == 0xFFFFFFFF:
            continue  # empty slot (FileTableGet.py skips these)
        if e["size"] <= 0 or e["size"] > filesize:
            return False
        if e["offset"] < 0 or e["offset"] + e["size"] > filesize:
            return False
        if e["offset"] <= prev:
            return False
        prev = e["offset"]
    return True


# ---------------------------------------------------------------- scanning
def find_manifest_region(buf: bytes) -> tuple:
    """Locate the CRLF filename manifest: the longest run of lines
    ending in .dat followed by CRLF."""
    idx = buf.find(b".dat\r\n")
    if idx == -1:
        return (-1, -1)
    # walk back to the start of the first filename line
    start = buf.rfind(b"\r\n", 0, idx - 4)
    start = 0 if start == -1 else start + 2
    end = buf.find(b"\r\n", idx)
    # count consecutive .dat lines from start
    pos = start
    count = 0
    while True:
        nl = buf.find(b"\r\n", pos)
        if nl == -1:
            break
        line = buf[pos:nl]
        if not line.endswith(b".dat"):
            break
        count += 1
        pos = nl + 2
    return (start, count)


def find_bdpk(buf: bytes) -> list:
    out = []
    pos = 0
    while True:
        i = buf.find(BDPK, pos)
        if i == -1:
            break
        out.append(i)
        pos = i + 1
    return out


def scan_for_lut(buf: bytes, count: int, fmt: str = "generic") -> list:
    """Hunt for candidate LUT tables: scan 4-byte-aligned positions for
    a run of >=8 consecutive plausible entries. Returns a list of
    (offset, score) candidates, best first. SLOW on a 244 MB file --
    it steps 4 bytes at a time; use --scan-step to widen the stride.
    A candidate is NOT a proven table: confirm by extracting a known
    file (e.g. a .dat whose header is recognisable) before trusting it."""
    entry_size = LUT_GENERIC_ENTRY if fmt == "generic" else LUT_PS2_ENTRY
    parse = parse_lut_generic if fmt == "generic" else parse_lut_ps2
    filesize = len(buf)
    candidates = []
    # Only positions where a full run of 8 entries fits.
    limit = filesize - 8 * entry_size
    for off in range(0, limit, 4):
        run = parse(buf, off, 8)
        if entries_plausible(run, filesize):
            # extend the run as far as it stays plausible
            full = parse(buf, off, count)
            good = 0
            prev = -1
            for e in full:
                if e["size"] == 0xFFFFFFFF:
                    good += 1
                    continue
                if e["size"] <= 0 or e["size"] > filesize:
                    break
                if e["offset"] < 0 or e["offset"] + e["size"] > filesize:
                    break
                if e["offset"] <= prev:
                    break
                prev = e["offset"]
                good += 1
            candidates.append((off, good))
    candidates.sort(key=lambda c: -c[1])
    return candidates


def scan(archive: Path, manifest: list) -> int:
    buf = archive.read_bytes()
    print(f"archive: {archive} ({len(buf)} bytes, sha256 {hashlib.sha256(buf).hexdigest()[:16]}...)")
    if buf[:4] != MAGIC:
        print(f"FAIL: magic at 0 is {buf[:4]!r}, expected {MAGIC!r} -- not a romD archive")
        return 1
    print("magic: romD OK at offset 0")
    mstart, mcount = find_manifest_region(buf)
    print(f"manifest region: offset {mstart}, {mcount} .dat lines found "
          f"(manifest file lists {len(manifest)})")
    bdpk = find_bdpk(buf)
    print(f"BDPK markers: {len(bdpk)} at offsets {[hex(o) for o in bdpk]}")
    for fmt in ("generic", "ps2"):
        print(f"hunting {fmt} LUT candidates (count={len(manifest)}) ...")
        cands = scan_for_lut(buf, len(manifest), fmt)
        if not cands:
            print(f"  none found for {fmt}")
        for off, good in cands[:5]:
            print(f"  candidate table at {hex(off)}: {good}/{len(manifest)} plausible entries")
    print("NOTE: candidates are structural only. Confirm by extracting a "
          "known file before trusting any table.")
    return 0


# ---------------------------------------------------------------- extraction
def extract(archive: Path, manifest: list, lut_fmt: str, table_offset: int,
            table_count: int, outdir: Path, decrypt: bool = True) -> int:
    buf = archive.read_bytes()
    parse = parse_lut_generic if lut_fmt == "generic" else parse_lut_ps2
    entries = parse(buf, table_offset, table_count)
    if len(entries) < len(manifest):
        print(f"FAIL: table at {hex(table_offset)} yields {len(entries)} entries, "
              f"manifest lists {len(manifest)}")
        return 1
    outdir.mkdir(parents=True, exist_ok=True)
    ok = 0
    for name, e in zip(manifest, entries):
        if e["size"] == 0xFFFFFFFF:
            print(f"  SKIP {name}: empty slot (size 0xFFFFFFFF)")
            continue
        raw = bytearray(buf[e["offset"]:e["offset"] + e["size"]])
        if len(raw) != e["size"]:
            print(f"  SKIP {name}: entry runs past end of file")
            continue
        if decrypt:
            decrypt_sector_data_fast(raw, e["id"], e["size"])
        (outdir / name).write_bytes(bytes(raw))
        ok += 1
    print(f"extracted {ok}/{len(manifest)} files to {outdir}")
    return 0 if ok == len(manifest) else 1


# ---------------------------------------------------------------- self-test
def selftest() -> int:
    """Synthetic round-trip: build a tiny fake romD (magic + manifest +
    a generic-format LUT + two encrypted files), then scan/parse/extract
    it and check the bytes come back identical."""
    import io
    names = ["gym_ikdv_beam.dat", "gym_kmb1_machinegun.dat"]
    payloads = [b"BEAMDATA" * 100, b"GUNJACK!" * 64]
    # layout: header(0x1000) | lut | data sectors
    lut_off = 0x1000
    data_base = 0x2000
    buf = bytearray(b"\x00" * 0x4000)
    buf[0:4] = MAGIC
    man = ("\r\n".join(names) + "\r\n").encode()
    buf[0x100:0x100 + len(man)] = man
    buf[0x800:0x804] = BDPK
    entries = []
    off = data_base
    for i, p in enumerate(payloads):
        sector = off // SECTOR
        entries.append((sector, len(p), i))
        enc = bytearray(p)
        decrypt_sector_data_fast(enc, i, len(p))  # cipher is its own inverse
        buf[off:off + len(p)] = enc
        off += ((len(p) + SECTOR - 1) // SECTOR) * SECTOR
    for i, (sector, size, eid) in enumerate(entries):
        struct.pack_into("<II5I III", buf, lut_off + i * LUT_GENERIC_ENTRY,
                         sector, size, 0, 0, 0, 0, 0, 0, eid, 0)
    # scan checks
    assert bytes(buf[:4]) == MAGIC
    mstart, mcount = find_manifest_region(bytes(buf))
    assert mcount == 2, mcount
    assert find_bdpk(bytes(buf)) == [0x800]
    parsed = parse_lut_generic(bytes(buf), lut_off, 2)
    assert entries_plausible(parsed, len(buf), min_run=2)  # only 2 synthetic entries
    assert [e["id"] for e in parsed] == [0, 1]
    # extract round-trip
    out = Path("/tmp/romd_selftest")
    import shutil
    shutil.rmtree(out, ignore_errors=True)
    tmp = Path("/tmp/romd_selftest.bin")
    tmp.write_bytes(bytes(buf))
    rc = extract(tmp, names, "generic", lut_off, 2, out)
    assert rc == 0
    assert (out / names[0]).read_bytes() == payloads[0]
    assert (out / names[1]).read_bytes() == payloads[1]
    print("selftest PASS: synthetic romD scan/parse/decrypt/extract round-trips")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("archive", nargs="?", help="TK5DATA2.BIN path")
    ap.add_argument("--manifest", default="t5_motion_manifest.txt")
    ap.add_argument("--scan", action="store_true", help="scan magic/manifest/BDPK/LUT candidates")
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--lut", choices=["generic", "ps2"], default="generic")
    ap.add_argument("--table-offset", type=lambda s: int(s, 0), default=None)
    ap.add_argument("--table-count", type=int, default=None)
    ap.add_argument("--out", default="romd_out")
    ap.add_argument("--no-decrypt", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.archive:
        ap.error("archive path required (or --selftest)")
    manifest = parse_manifest(Path(args.manifest))
    print(f"manifest: {len(manifest)} names from {args.manifest}")
    if args.scan:
        return scan(Path(args.archive), manifest)
    if args.extract:
        if args.table_offset is None or args.table_count is None:
            ap.error("--extract needs --table-offset and --table-count (from --scan candidates)")
        return extract(Path(args.archive), manifest, args.lut,
                       args.table_offset, args.table_count,
                       Path(args.out), decrypt=not args.no_decrypt)
    ap.error("choose --scan, --extract, or --selftest")


if __name__ == "__main__":
    sys.exit(main())
