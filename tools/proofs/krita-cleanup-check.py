#!/usr/bin/env python3
"""Check a Krita-cleaned proof image. WH PROOFS ONLY.

Verifies the exported cleaned PNG against its source render and records the
operator's attestation that the Krita GUI steps in krita-cleanup.md were done.
This script cannot verify GUI work itself -- that is exactly why --operator
is required and why the JSON record says "operator-attested".

No third-party deps (Pillow used only if present, for mode reporting).
Usage:
  python3 tools/proofs/krita-cleanup-check.py --source SRC.png \
      --cleaned CLEAN.png --operator NAME [--out OUT.json]
Exit: 0 record written, 1 check failed, 2 usage error.
"""
import argparse, hashlib, json, struct, sys
from pathlib import Path

def png_info(path):
    """Return (width, height) for a PNG, or raise ValueError."""
    data = path.read_bytes()
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    w, h = struct.unpack(">II", data[16:24])
    return w, h, len(data)

def main():
    ap = argparse.ArgumentParser(description="Check a Krita-cleaned proof image.")
    ap.add_argument("--source", required=True)
    ap.add_argument("--cleaned", required=True)
    ap.add_argument("--operator", required=True,
                    help="Name of the operator who did the Krita GUI steps.")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    src, clean = Path(a.source), Path(a.cleaned)
    failures, notes = [], []
    record = {"scope": "western-heart PROOF ONLY (not fight code, not a game asset)",
              "tool": "krita (GUI, operator-attested) + krita-cleanup-check.py",
              "source": str(src), "cleaned": str(clean),
              "operator": a.operator, "failures": failures, "notes": notes}
    for label, p in (("source", src), ("cleaned", clean)):
        if not p.exists():
            failures.append(f"{label} not found: {p}")
    dims = {}
    if not failures:
        try:
            dims["source"] = png_info(src)
            dims["cleaned"] = png_info(clean)
        except ValueError as e:
            failures.append(str(e))
        except OSError as e:
            failures.append(str(e))
    if dims.get("source") and dims.get("cleaned"):
        record["source_px"] = dims["source"][:2]
        record["cleaned_px"] = dims["cleaned"][:2]
        record["cleaned_bytes"] = dims["cleaned"][2]
        if dims["source"][:2] != dims["cleaned"][:2]:
            failures.append(
                f"dimension mismatch: source {dims['source'][:2]} != "
                f"cleaned {dims['cleaned'][:2]} (no silent rescale allowed)")
        if dims["cleaned"][2] == 0:
            failures.append("cleaned file is empty")
        record["cleaned_sha256"] = hashlib.sha256(clean.read_bytes()).hexdigest()
        try:
            from PIL import Image
            with Image.open(clean) as im:
                record["cleaned_mode"] = im.mode
                notes.append(f"Pillow opened cleaned image, mode={im.mode}")
        except ImportError:
            notes.append("Pillow not available; mode check skipped (PNG header check still ran)")
    record["krita_gui_step"] = ("operator-attested by " + a.operator +
                                " (Krita GUI work cannot be machine-verified here)")
    record["failures"] = failures
    record["notes"] = notes
    text = json.dumps(record, indent=2) + "\n"
    if a.out:
        Path(a.out).write_text(text)
        print(f"check record -> {a.out}")
    else:
        print(text, end="")
    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1
    print("krita clean-up check: ok (GUI step operator-attested, file checks passed)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
