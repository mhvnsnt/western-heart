#!/usr/bin/env python3
"""
server.py — HTTP API backend for the creation suite's AI Edit panel.

Endpoints:
    GET  /api/health              -> {"ok": true, "backends": [...]}
    GET  /api/backends            -> available generative backends
    POST /api/ai-edit             multipart: image=<file>, instruction=<str>,
                                  backend=<name>, size=<int>, seed=<int>
                                  -> edited PNG image bytes
    POST /api/basic-edit          multipart: image=<file>, ops=<json>
                                  -> edited PNG image bytes
                                  ops example: {"resize": "800x600", "saturation": 1.4}

Run:
    python server.py [--port 8791] [--host 127.0.0.1]

The creation suite's ART > AI EDIT panel talks to this server. Serve it
alongside the suite, or point the panel at wherever it runs.
"""
import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image

try:
    from flask import Flask, request, jsonify, send_file
except ImportError:
    print("server.py needs flask: pip install flask", file=sys.stderr)
    sys.exit(2)

import backends
import edit as edit_cli

app = Flask(__name__)
MAX_BYTES = 25 * 1024 * 1024


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "backends": [
        {"name": n, "available": a, "description": d}
        for n, a, d in backends.list_backends()
    ]})


@app.get("/api/backends")
def get_backends():
    return jsonify([
        {"name": n, "available": a, "description": d}
        for n, a, d in backends.list_backends()
    ])


def _load_upload(field="image"):
    f = request.files.get(field)
    if not f:
        return None, jsonify({"error": f"missing '{field}' file"}), 400
    data = f.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        return None, jsonify({"error": "image too large (max 25MB)"}), 400
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as e:
        return None, jsonify({"error": f"cannot decode image: {e}"}), 400
    return img, None, None


def _png_response(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


@app.post("/api/ai-edit")
def ai_edit():
    img, err_resp, code = _load_upload()
    if err_resp:
        return err_resp, code
    instruction = (request.form.get("instruction") or "").strip()
    if not instruction:
        return jsonify({"error": "missing 'instruction'"}), 400
    backend = request.form.get("backend", "auto")
    try:
        size = int(request.form.get("size", 512))
    except ValueError:
        size = 512
    seed_raw = request.form.get("seed")
    seed = int(seed_raw) if seed_raw and seed_raw.strip() else None
    try:
        out = backends.run_instruction(img, instruction, backend=backend, size=size, seed=seed)
    except Exception as e:
        return jsonify({"error": str(e)[:500]}), 502
    return _png_response(out)


@app.post("/api/basic-edit")
def basic_edit():
    """Apply PIL ops from a JSON ops dict. See edit.py --help for op names."""
    img, err_resp, code = _load_upload()
    if err_resp:
        return err_resp, code
    try:
        ops = json.loads(request.form.get("ops", "{}"))
    except json.JSONDecodeError as e:
        return jsonify({"error": f"bad ops JSON: {e}"}), 400

    # Map JSON ops onto argparse-style namespace consumed by apply_basic_ops
    parser = edit_cli.build_parser()
    ns = parser.parse_args(["x.png", "-o", "y.png"])  # defaults
    allowed = {
        "resize", "crop", "rotate", "flip", "brightness", "contrast",
        "saturation", "sharpness", "hue", "tint", "tint_strength",
        "grayscale", "blur", "text", "text_pos", "text_size",
        "text_color", "text_stroke", "text_stroke_color",
    }
    for key, val in ops.items():
        if key in allowed:
            setattr(ns, key, val)
    ns.no_expand = False
    ns.overlay = None
    ns.font = None
    try:
        out = edit_cli.apply_basic_ops(img, ns)
    except Exception as e:
        return jsonify({"error": f"op failed: {e}"}), 400
    return _png_response(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8791)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    print(f"image-edit server on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
