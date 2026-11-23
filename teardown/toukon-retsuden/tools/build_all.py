#!/usr/bin/env python3
"""End-to-end build for the Toukon Retsuden English patch.

Input: the original JP TR1 disc (Track 1 BIN + CUE, multi-track set)
       and the US Power Move Pro Wrestling disc (single BIN + CUE,
       used only as the translation reference for banners/names).
Output: a patched English TR1 disc set (BIN/CUE) + CHD if chdman
        is available.

Pipeline:
  1. extract JP disc files (EXE, DTPAC.PAC) + US disc files
  2. extract DPAC entries (JP PAC_GAME_MES + TIM_END, US BIG_MES TIMs,
     US GAME_MES sections) and decompress the BPE sections
  3. build the English name sheet + "Ring Out!" banner
  4. patch the EXE names, rebuild PAC_GAME_MES, rebuild DTPAC.PAC
  5. patch the ISO in place, assemble the disc set, convert to CHD

Nothing here contains game data: the script reads the user's own
disc images and writes the patched output. Run from the
teardown/toukon-retsuden directory (tools/ + work/ siblings).

Usage:
  python3 build_all.py --jp-dir <dir with TR1 Track 1 .bin/.cue>
                       --us-bin <pmpw-usa.bin> --us-cue <pmpw-usa.cue>
                       [--workdir <dir>] [--skip-chd]
"""
import argparse
import shutil
import struct
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from psx_iso import PsxDisc  # noqa: E402
from dpac import parse_table  # noqa: E402
from bpe import decompress_section  # noqa: E402


def extract_disc(bin_path, cue_path, outdir):
    bin_path = Path(bin_path)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    disc = PsxDisc(str(bin_path), str(cue_path) if cue_path else None)
    n = disc.extract_all(str(outdir))
    disc.close()
    print(f"extracted {n} files from {bin_path.name} -> {outdir}")
    return outdir


def extract_dpac_entries(pac_path, outdir, names=None):
    """Extract named DPAC entries (or all) into outdir."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    info = parse_table(str(pac_path))
    data = Path(pac_path).read_bytes()
    got = []
    for e in info["entries"]:
        if names and e["name"] not in names:
            continue
        blob = data[e["b"] * 0x800:e["b"] * 0x800 + e["a"]]
        dest = outdir / (e["name"] + ".bin")
        dest.write_bytes(blob)
        got.append(e["name"])
    print(f"extracted {len(got)} DPAC entries -> {outdir}")
    return got


def decompress_bpe_sections(pac_entry_path, outdir):
    """Decompress every BPE section in a WRES entry file."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    data = Path(pac_entry_path).read_bytes()
    off = 0
    n = 0
    while True:
        off = data.find(b"BPE ", off)
        if off < 0:
            break
        _ver, comp_size, _ds = struct.unpack_from("<III", data, off + 4)
        section = data[off:off + 16 + comp_size]
        dec = decompress_section(section)
        (outdir / f"bpe{n:02d}_{off:#x}.bin").write_bytes(dec)
        off += 16 + comp_size
        n += 1
    print(f"decompressed {n} BPE sections from {pac_entry_path.name}")
    return n


def extract_bigmes_tims(pac_entry_path, outdir):
    """BIG_MES holds RAW (uncompressed) TIMs after the 0xC80 header:
    split them by scanning for TIM magic (0x10) at 4-byte alignment."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    data = Path(pac_entry_path).read_bytes()
    # table at 0x888 gives (offset/4, size/4) per slot
    n = 0
    for slot in range(32):
        off4, size4 = struct.unpack_from("<HH", data, 0x888 + slot * 4)
        if not size4:
            continue
        off, size = 0xC80 + off4 * 4, size4 * 4
        blob = data[off:off + size]
        assert blob[:4] == b"\x10\x00\x00\x00", f"slot {slot} not a TIM"
        (outdir / f"big{n:02d}_{off:#x}.bin").write_bytes(blob)
        n += 1
    print(f"extracted {n} raw TIMs from {pac_entry_path.name}")
    return n


def run_tool(name, *args):
    cmd = [sys.executable, str(HERE / name), *[str(a) for a in args]]
    print(f"+ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jp-dir", required=True,
                    help="dir with the TR1 Track 1 .bin + .cue (and 2-7)")
    ap.add_argument("--us-bin", required=True)
    ap.add_argument("--us-cue", required=True)
    ap.add_argument("--workdir", default=str(HERE.parent / "work"))
    ap.add_argument("--skip-chd", action="store_true")
    args = ap.parse_args()
    work = Path(args.workdir)
    # The sub-tools resolve work/ relative to tools/ (HERE.parent),
    # so a custom workdir must equal that location.
    assert work.resolve() == (HERE.parent / "work").resolve(), \
        "workdir must be <repo>/work (sub-tools resolve it relatively)"
    work.mkdir(parents=True, exist_ok=True)
    jp_dir = Path(args.jp_dir)

    jp_bin = next(jp_dir.glob("*(Track 1).bin"))
    jp_cue = next(jp_dir.glob("*.cue"))

    # 1. extract both discs
    jp_files = extract_disc(jp_bin, jp_cue, work / "tr1-files")
    us_files = extract_disc(args.us_bin, args.us_cue, work / "us-files")

    # 2. DPAC entries + BPE decompression
    extract_dpac_entries(jp_files / "DTPAC.PAC", work / "pac-entries",
                         {"PAC_GAME_MES", "PAC_COMMON"})
    extract_dpac_entries(jp_files / "DTPAC.PAC", work / "pac-tim",
                         {"TIM_END"})
    extract_dpac_entries(us_files / "DTPAC.PAC", work / "us-pac",
                         {"PAC_GAME_MES", "PAC_BIG_MES", "PAC_COMMON"})
    extract_dpac_entries(us_files / "DTPAC.PAC", work / "us-pac-tim",
                         {"TIM_END"})
    decompress_bpe_sections(work / "pac-entries" / "PAC_GAME_MES.bin",
                            work / "gamemes-dec")
    decompress_bpe_sections(work / "us-pac" / "PAC_GAME_MES.bin",
                            work / "us-gamemes-dec")
    extract_bigmes_tims(work / "us-pac" / "PAC_BIG_MES.bin",
                        work / "us-bigmes-tim")

    # 3. build the new graphics
    run_tool("name_sheet.py")
    run_tool("ringout_banner.py")

    # 4. patch EXE, rebuild PAC_GAME_MES + DTPAC.PAC
    run_tool("exe_names.py")
    run_tool("rebuild_gamemes.py")
    run_tool("rebuild_dpac.py")

    # 5. patch the ISO + assemble the disc set
    patched_bin = work / "tr1-en-track1.bin"
    run_tool("patch_iso.py", "--bin", jp_bin, "--out", patched_bin)
    en_dir = work / "tr1-en"
    en_dir.mkdir(exist_ok=True)
    shutil.copy(patched_bin, en_dir / "Toukon Retsuden EN (Track 1).bin")
    for n in range(2, 8):
        src = next(jp_dir.glob(f"*(Track {n}).bin"))
        shutil.copy(src, en_dir / f"Toukon Retsuden EN (Track {n}).bin")
    cue = jp_cue.read_text()
    cue = cue.replace(jp_bin.stem.replace(" (Track 1)", ""),
                      "Toukon Retsuden EN")
    (en_dir / "Toukon Retsuden EN.cue").write_text(cue)
    print(f"disc set assembled in {en_dir}")

    # 6. CHD
    if not args.skip_chd:
        chdman = shutil.which("chdman")
        if chdman:
            chd = work / "toukon-retsuden-en.chd"
            subprocess.run([chdman, "createcd", "-i",
                            str(en_dir / "Toukon Retsuden EN.cue"),
                            "-o", str(chd)], check=True)
            print(f"wrote {chd}")
        else:
            print("chdman not found -- skipping CHD (run on the Oracle VM)")
    print("BUILD COMPLETE")


if __name__ == "__main__":
    main()
