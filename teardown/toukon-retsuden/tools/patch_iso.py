#!/usr/bin/env python3
"""Patch the TR1 disc image in place (EXE + DTPAC.PAC).

Writes the patched files into their existing ISO9660 extents in the
Track 1 BIN (raw 2352-byte Mode 2 sectors, 2048-byte payload at offset
24). The ISO layout, LBAs, directory records, .cue, and audio tracks
are all untouched:
  - SLPS_000.84: patched EXE, same size (417,792 B) -- direct overwrite
  - TOK/DTPAC.PAC: rebuilt DPAC, SMALLER (2,945,024 vs 2,955,264 B) --
    written into the same extent, tail zero-filled; the DPAC's own
    header/table define its extent, so the dead tail is never read

Caveat: EDC/ECC checksums in the patched sectors are NOT recomputed.
Mednafen and PCSX ReARMed do not verify them on data reads, so this
is safe for the emulator targets. (Real hardware would flag the ECC
mismatch; recomputing Reed-Solomon P/Q parity is out of scope.)

Usage:
  python3 patch_iso.py [--bin <track1.bin>] [--out <patched.bin>]
"""
import sys
from pathlib import Path

HERE = Path(__file__).parent
WORK = HERE.parent / "work"
sys.path.insert(0, str(HERE))
from psx_iso import PsxDisc, RAW_SECTOR, COOKED

PATCHES = [
    ("SLPS_000.84", WORK / "SLPS_000.84.en"),
    ("TOK/DTPAC.PAC", WORK / "DTPAC.en.PAC"),
]


def patch(bin_path, out_path):
    disc = PsxDisc(str(bin_path))
    files = {p.upper(): (lba, size) for p, lba, size in disc.list_files()}
    data = bytearray(Path(bin_path).read_bytes())
    for iso_path, new_file in PATCHES:
        lba, size = files[iso_path.upper()]
        new = new_file.read_bytes()
        assert len(new) <= size, \
            f"{iso_path}: new file {len(new)}B > extent {size}B"
        # write sector by sector into the 2048-byte payloads
        nsec = (size + COOKED - 1) // COOKED
        padded = new + b"\x00" * (size - len(new))
        for i in range(nsec):
            sec_off = (lba + i) * RAW_SECTOR
            raw = data[sec_off:sec_off + RAW_SECTOR]
            assert len(raw) == RAW_SECTOR, f"short sector at LBA {lba + i}"
            assert raw[15] == 2 and not (raw[18] & 0x20), \
                (f"LBA {lba + i} is not Mode 2 Form 1 "
                 f"(mode={raw[15]}, submode={raw[18]:#x})")
            chunk = padded[i * COOKED:(i + 1) * COOKED]
            data[sec_off + 24:sec_off + 24 + len(chunk)] = chunk
        print(f"{iso_path}: LBA {lba}, {len(new)} bytes written "
              f"({size - len(new)} zero-filled tail bytes)")
    disc.close()
    Path(out_path).write_bytes(bytes(data))
    print(f"wrote {out_path} ({len(data)} bytes)")
    return out_path


def verify(orig_bin, patched_bin):
    """Patched image must differ from the original ONLY in the two
    patched extents, and the patched files must read back correctly."""
    d0 = PsxDisc(str(orig_bin))
    d1 = PsxDisc(str(patched_bin))
    files0 = {p.upper(): (lba, size) for p, lba, size in d0.list_files()}
    files1 = {p.upper(): (lba, size) for p, lba, size in d1.list_files()}
    assert files0 == files1, "ISO directory changed!"
    changed = set()
    for path, (lba, size) in files0.items():
        a = d0.read_extent(lba, size)
        b = d1.read_extent(lba, size)
        if a != b:
            changed.add(path)
    d0.close()
    d1.close()
    expect = {p.upper() for p, _ in PATCHES}
    assert changed == expect, \
        f"changed files {changed} != expected {expect}"
    print(f"verify: only {sorted(changed)} differ -- OK")
    # patched files read back byte-exact
    d1 = PsxDisc(str(patched_bin))
    for iso_path, new_file in PATCHES:
        lba, size = files1[iso_path.upper()]
        got = d1.read_extent(lba, len(new_file.read_bytes()))
        assert got == new_file.read_bytes(), f"{iso_path} readback mismatch"
    d1.close()
    print("verify: patched files read back byte-exact -- OK")


def main():
    src = Path(sys.argv[sys.argv.index("--bin") + 1]) \
        if "--bin" in sys.argv else WORK / "tr1-jp" / \
        "Shin Nihon Pro Wrestling - Toukon Retsuden (Japan) (Track 1).bin"
    dst = Path(sys.argv[sys.argv.index("--out") + 1]) \
        if "--out" in sys.argv else WORK / "tr1-en-track1.bin"
    patch(src, dst)
    verify(src, dst)


if __name__ == "__main__":
    main()
