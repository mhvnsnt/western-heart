#!/usr/bin/env python3
"""kc2_rebuild.py — rebuild Spike's KC2 container archives (KoC2).

Companion to kc2_extract.py: takes an original archive and a set of
replacement files (by numeric id) and writes a new archive with fresh
offsets. Unchanged files are copied byte-for-byte from the original
archive (stored blob verbatim, flags verbatim) — only replaced files
are re-encoded.

Replacement format: a JSON manifest mapping file id (as a string) to
an object:
  {"path": "<new decompressed bytes file>", "compress": false}
For a file that was stored RAW (flags bit 16 clear), the new data is
stored raw, zero-padded to a 2048-byte boundary (matching the original
text files' padding style; the loader reads stored_size bytes and the
game only uses decomp_size of them).
For a file that was LZSS-compressed, the new data is compressed with
koc2_lzss_enc.py and the stored blob is zero-padded to a 32-byte
boundary (all stored_sizes in the original archives are multiples
of 32). Set "compress": false on a compressed file to store it raw
instead (flags bit 16 cleared) — the loader handles either mode, but
keeping the original mode is the safe default.

Set "pad_to_original": true on a replacement to zero-pad its stored
blob up to the ORIGINAL stored_size, so the file keeps its original
offset and no later file shifts. The game (or its loader) appears to
address some files by absolute position rather than through the entry
table: a rebuilt archive with shifted offsets hangs on the Appearance
screen even though the entry table is internally perfect (verified
2026-11-20). Fails loudly if the new blob is larger than the original
stored_size. With every replacement padded, the rebuilt archive is
exactly the original size.
Set "pad_to": <bytes> to zero-pad the stored blob to an exact size
instead (e.g. to absorb slack so the total archive size stays
unchanged when another file grows). Fails loudly if the blob is
larger than the requested size.

Container layout (from kc2_extract.py, validated 2026-11-19):
  Header (8 bytes): u32 0x800, u32 file_count
  Entry table: count x 16 bytes (offset rel. to data start,
      stored_size, decomp_size, flags)
  Zero padding to the next 2048-byte boundary; data region starts
  there; files packed contiguously.

Usage:
  kc2_rebuild.py <original-archive> <manifest.json> <output-archive>
  With an empty manifest ({}), the rebuild must be byte-identical to
  the original — that is the format proof.

KoC2 English lane, 2026-11-19.
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from koc2_lzss_enc import compress  # noqa: E402


def pad_to(data: bytes, align: int) -> bytes:
    rem = len(data) % align
    if rem:
        data = data + b"\x00" * (align - rem)
    return data


def rebuild(archive: Path, manifest: dict, output: Path):
    data = archive.read_bytes()
    block, count = struct.unpack_from("<II", data, 0)
    assert block == 0x800, f"unexpected block size 0x{block:x}"
    table_end = 8 + count * 16
    base = (table_end + 2047) & ~2047
    entries = []
    for i in range(count):
        off, size, decomp, flags = struct.unpack_from("<IIII", data, 8 + i * 16)
        entries.append({"id": i, "offset": off, "stored_size": size,
                        "decomp_size": decomp, "flags": flags,
                        "abs_offset": base + off})
    # Build the new stored blob for every file.
    new_blobs = []
    new_meta = []
    for e in entries:
        repl = manifest.get(str(e["id"])) or manifest.get(e["id"])
        if repl is None:
            blob = data[e["abs_offset"]: e["abs_offset"] + e["stored_size"]]
            new_blobs.append(blob)
            new_meta.append((e["stored_size"], e["decomp_size"], e["flags"]))
            continue
        new_data = Path(repl["path"]).read_bytes()
        want_compress = repl.get("compress", bool(e["flags"] & 0x10000))
        if want_compress:
            blob = pad_to(compress(new_data), 32)
            flags = e["flags"] | 0x10000
        else:
            blob = pad_to(new_data, 2048)
            flags = e["flags"] & ~0x10000
        if repl.get("pad_to_original"):
            if len(blob) > e["stored_size"]:
                raise ValueError(
                    f"file{e['id']:05d}: new blob {len(blob)} > original "
                    f"stored {e['stored_size']}, cannot pad_to_original")
            blob = blob + b"\x00" * (e["stored_size"] - len(blob))
        elif repl.get("pad_to") is not None:
            target = int(repl["pad_to"])
            if len(blob) > target:
                raise ValueError(
                    f"file{e['id']:05d}: new blob {len(blob)} > pad_to "
                    f"{target}")
            blob = blob + b"\x00" * (target - len(blob))
        new_blobs.append(blob)
        new_meta.append((len(blob), len(new_data), flags))
        print(f"  file{e['id']:05d}: {e['decomp_size']} -> {len(new_data)} "
              f"decomp bytes, stored {e['stored_size']} -> {len(blob)}, "
              f"flags 0x{e['flags']:08x} -> 0x{flags:08x}")
    # Recompute offsets, pack contiguously.
    out = bytearray()
    out += struct.pack("<II", 0x800, count)
    off = 0
    for (stored, decomp, flags) in new_meta:
        out += struct.pack("<IIII", off, stored, decomp, flags)
        off += stored
    # Pad table to the 2048 boundary.
    out += b"\x00" * (base - len(out))
    assert len(out) == base
    for blob in new_blobs:
        out += blob
    output.write_bytes(bytes(out))
    print(f"wrote {output}: {len(out)} bytes "
          f"(original {len(data)}, delta {len(out) - len(data):+d})")
    return len(out)


def main(argv):
    if len(argv) < 4:
        print(__doc__.split("Usage:")[1].strip(), file=sys.stderr)
        return 2
    manifest = json.loads(Path(argv[2]).read_text())
    rebuild(Path(argv[1]), manifest, Path(argv[3]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
