#!/usr/bin/env python3
"""koc2_file01999_build.py — rebuild KoC2's WrestlerData file (01999)
with translated names, in place.

File 01999 (1,252,521 bytes): header (16 B) + 255 x 64 B move-group
table + 441 x 2285 B wrestler records at 0x3FD0 + sparse tail.
Each record carries four fixed-width Shift-JIS name fields:
  family   +0x04, 12 bytes
  given    +0x13, 12 bytes
  nickname +0x28, 32 bytes
  finisher +0x49, 32 bytes
The bytes BETWEEN fields are non-zero data (verified 2026-11-19),
so fields are strictly fixed-width — this builder writes ONLY the
field bytes, never the gaps. English text is written as ASCII +
NUL padding to the field width. A value exactly as wide as the
field is written with no NUL terminator, matching the original
file's behavior (11 records use the full 12 bytes of family/given
with no NUL — the game reads these fields fixed-width).

Translation input: work/translations-01999.json —
{"0": {"ja": {...}, "en": {"family": ..., ...}}, ...}.
Before writing, the builder checks each field's current Japanese
text matches the recorded "ja" value (guards against stale input).
After writing, it re-parses the output with koc2_file01999.parse()
and verifies every field equals the expected English text.

Usage:
  koc2_file01999_build.py <file01999.bin> <translations.json> <output.bin>

KoC2 English lane, 2026-11-19.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import koc2_file01999 as F99  # noqa: E402

FIELDS = {
    "family": (0x04, 12),
    "given": (0x13, 12),
    "nickname": (0x28, 32),
    "finisher": (0x49, 32),
}


def build(data: bytes, translations: dict) -> bytes:
    assert len(data) == 1252521, f"unexpected size {len(data)}"
    out = bytearray(data)
    n_changed = 0
    for key, entry in translations.items():
        idx = int(key)
        base = F99.WRESTLER_BASE + idx * F99.WRESTLER_STRIDE
        for field, (off, width) in FIELDS.items():
            ja = entry["ja"][field]
            en = entry["en"][field]
            cur = F99.sjis(bytes(data[base + off: base + off + width]))
            assert cur == ja, \
                f"record {idx} {field}: file has {cur!r}, expected ja {ja!r}"
            if en is None:
                continue
            raw = en.encode("ascii")
            assert len(raw) <= width, \
                f"record {idx} {field}: {en!r} ({len(raw)}B) exceeds {width}B"
            if raw == bytes(data[base + off: base + off + len(raw)]) and \
                    all(b == 0 for b in data[base + off + len(raw):
                                             base + off + width]):
                continue  # already identical (no-op path)
            out[base + off: base + off + width] = raw + b"\x00" * (width - len(raw))
            n_changed += 1
    print(f"fields written: {n_changed} (of {len(translations) * 4} max)")
    # Verify by re-parsing the output.
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
        f.write(bytes(out))
        tmp = f.name
    try:
        parsed = F99.parse(tmp)
    finally:
        os.unlink(tmp)
    for key, entry in translations.items():
        idx = int(key)
        rec = parsed["wrestler_records"][idx]
        for field in FIELDS:
            en = entry["en"][field]
            if en is None:
                continue
            assert rec[field] == en, \
                f"record {idx} {field}: re-parse got {rec[field]!r}, want {en!r}"
    print(f"self-check OK: all {len(translations)} records re-parsed, "
          f"English verified")
    return bytes(out)


def main(argv):
    if len(argv) < 4:
        print(__doc__.split("Usage:")[1].strip(), file=sys.stderr)
        return 2
    data = Path(argv[1]).read_bytes()
    translations = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
    out = build(data, translations)
    Path(argv[3]).write_bytes(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
