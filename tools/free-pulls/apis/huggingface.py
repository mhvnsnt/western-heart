#!/usr/bin/env python3
"""Hugging Face public read API client for WH -- no auth, no downloads.

VERIFIED 2026-10-24 (live calls, no token):
  - GET https://huggingface.co/api/models?limit=2 -> 200 JSON list.
  - GET https://huggingface.co/api/models?search=image-to-3d&limit=3 -> 200,
    e.g. AIExxplorer/AIEXX_GENAI_IMAGE_TO_3D (text-to-3d/image-to-3d,
    Apache-2.0), kushbhargav/image_to_3d, cebas/oneClick_Windows_ImageTo3D_install.
  - GET https://huggingface.co/api/datasets?search=motion%20capture&limit=3
    -> 200, e.g. OpenLoong-Official/Motion-Capture (CC-BY-2.0),
    nekomata-project/motion-capture-data.
  - Unauthenticated reads work; rate limits are generous for reads but
    not published as a fixed number -- keep limits small. Gated/private
    models/datasets return 401 and are skipped, never worked around.
  - THIS SCRIPT NEVER DOWNLOADS MODEL WEIGHTS. It lists metadata only.
    Any weight download is a separate, explicit, large step that needs
    its own approval and disk budget (WH lane budget here is <50 MB).

Usage:
  python3 huggingface.py --models "image-to-3d" --limit 5
  python3 huggingface.py --datasets "motion capture" --limit 5
  python3 huggingface.py --models "text-to-image" --datasets "pose estimation" --limit 3
Only the Python standard library is used. A HF_TOKEN env var is NOT
read or needed; if one exists in the environment it is ignored.
"""
import argparse, json, urllib.parse, urllib.request

BASE = "https://huggingface.co/api"
UA = {"User-Agent": "WH-free-pulls/1.0"}


def fetch(kind, query, limit):
    url = f"{BASE}/{kind}?search={urllib.parse.quote(query)}&limit={limit}"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def show_models(query, limit):
    for m in fetch("models", query, limit):
        tags = ",".join(t for t in m.get("tags", []) if t.startswith("license:"))
        print(f"{m['id']}\tpipeline={m.get('pipeline_tag')}\t"
              f"likes={m.get('likes')}\tdownloads={m.get('downloads')}\t{tags}")
    print(f"# models matching {query!r} (metadata only -- no weights downloaded)")


def show_datasets(query, limit):
    for d in fetch("datasets", query, limit):
        tags = ",".join(t for t in d.get("tags", []) if t.startswith("license:"))
        print(f"{d['id']}\tdownloads={d.get('downloads')}\tlikes={d.get('likes')}"
              f"\tgated={d.get('gated')}\t{tags}")
    print(f"# datasets matching {query!r} (metadata only)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models")
    ap.add_argument("--datasets")
    ap.add_argument("--limit", type=int, default=5)
    a = ap.parse_args()
    if a.models:
        show_models(a.models, a.limit)
    if a.datasets:
        show_datasets(a.datasets, a.limit)
    if not (a.models or a.datasets):
        # Default WH-relevant sweep (metadata only).
        for q in ["image-to-3d", "text-to-3d"]:
            show_models(q, 3)
        for q in ["motion capture", "human pose"]:
            show_datasets(q, 3)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
