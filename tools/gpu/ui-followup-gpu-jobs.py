#!/usr/bin/env python3
"""UI-followup GPU jobs (Western Heart, UI lane 2026-10-24).

Two modes, one report contract. Every run records: GPU proof (nvidia-smi +
torch.cuda, verbatim, or their honest absence), input sizes, outputs, and
wall time per step. NOTHING here claims a speedup: the report records the
run's own wall time, and speedup is computed by comparing this report's
wall time against a CPU-baseline report's wall time. A run on a host with
no GPU is a valid CPU-baseline run, not a failure.

Modes:
  regression  -- Playwright screenshots of every screen this lane touched
                 (fight UI incl. the 18-banner removal, the 7 legacy
                 screens, select) at phone portrait 390x844 and landscape
                 844x390. Sections are activated by class (markup + CSS
                 render check), NOT a full playthrough -- live phone
                 playtesting stays with the coordinator's browser lane.
                 If a baseline dir is given, pixelmatch is attempted via
                 npx and its result recorded; if pixelmatch is absent,
                 captures are recorded as the baseline (no fake diff).
  t3-assets   -- Reads game/data/t3-ui-art.json, builds a labeled contact
                 sheet + phone-width crops of all 11 T3 UI previews.
                 img2img generation runs ONLY with --img2img on a host
                 with torch + diffusers; otherwise it is recorded as
                 skipped (model absent) and the sheet + crops are the
                 deliverable. Raw T3 pixels never ship; generated art
                 ships only after an owner eye-check of the sheet.

Select-render gate (Lane H spec, PR #1070): T8-select-framed renders are
DIAGNOSTIC ONLY until the model's texture gate passes + owner eye-check.
This script never emits select card art for shipping; both select slots
stay on the existing "model coming" placeholder until that gate passes.

Usage (from a full repo checkout):
  python3 tools/gpu/ui-followup-gpu-jobs.py regression --repo . --out out/ui-reg
  python3 tools/gpu/ui-followup-gpu-jobs.py t3-assets --repo . --out out/t3-ui
  python3 tools/gpu/ui-followup-gpu-jobs.py t3-assets --repo . --out out/t3-ui --img2img
Kaggle (coordinator browser lane): clone the repo in the notebook, run the
same commands, and paste the printed JSON report into the run log.
Colab is the backup/overflow host (switch, never stop).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

SCREENS = [
    "screen-online", "screen-collection", "screen-daily", "screen-howto",
    "screen-movelist", "screen-modewin", "screen-reincarnate",
    "screen-menu", "screen-select", "screen-result", "screen-stage",
    "screen-vssetup",
]
VIEWPORTS = {"portrait": (390, 844), "landscape": (844, 390)}


def gpu_proof():
    """Verbatim GPU evidence, or its honest absence. Never inferred."""
    proof = {}
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total",
                            "--format=csv,noheader"], capture_output=True,
                           text=True, timeout=30)
        proof["nvidia_smi"] = (r.stdout.strip() if r.returncode == 0
                               else f"nvidia-smi exit {r.returncode}: "
                                    f"{r.stderr.strip()[:200]}")
    except FileNotFoundError:
        proof["nvidia_smi"] = "absent: no nvidia-smi on this host"
    except Exception as e:  # noqa: BLE001 - report, don't crash
        proof["nvidia_smi"] = f"error: {e}"
    try:
        import torch  # noqa: PLC0415
        proof["torch"] = torch.__version__
        proof["torch_cuda_available"] = bool(torch.cuda.is_available())
        proof["torch_cuda_devices"] = (
            torch.cuda.device_count() if torch.cuda.is_available() else 0)
    except ImportError:
        proof["torch"] = "absent: no torch on this host"
        proof["torch_cuda_available"] = False
    except Exception as e:  # noqa: BLE001
        proof["torch"] = f"error: {e}"
        proof["torch_cuda_available"] = False
    return proof


def timed(fn):
    t0 = time.perf_counter()
    out = fn()
    return out, round(time.perf_counter() - t0, 3)


def run_regression(repo, out, baseline):
    from playwright.sync_api import sync_playwright
    import http.server
    import functools
    import threading

    os.makedirs(out, exist_ok=True)
    game_dir = os.path.join(repo, "game")
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=game_dir)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    shots, errors = [], []
    try:
        return _regression_with_browser(port, out, shots, errors, httpd,
                                        baseline)
    except Exception as e:  # noqa: BLE001 - a failed launch still yields a report
        try:
            httpd.shutdown()
        except Exception:  # noqa: BLE001
            pass
        return {"shots": shots, "console_errors": errors[:20],
                "launch_error": str(e)[:500],
                "pixelmatch": "not run: browser launch failed",
                "note": "Browser launch failed on this host (both Playwright "
                "Chromium builds crash on launch in this VM). This report "
                "is the environment record, not a screenshot baseline; "
                "run the same command on Kaggle/Colab where Chromium "
                "launches."}


def _regression_with_browser(port, out, shots, errors, httpd, baseline):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = None
        last_err = None
        for kwargs in ({}, {"channel": "chromium",
                            "args": ["--no-sandbox", "--disable-gpu"]}):
            try:
                browser = p.chromium.launch(**kwargs)
                break
            except Exception as e:  # noqa: BLE001
                last_err = e
        if browser is None:
            raise RuntimeError(f"Chromium launch failed (both channels): "
                               f"{last_err}")
        for name, (w, h) in VIEWPORTS.items():
            page = browser.new_page(viewport={"width": w, "height": h})
            page.on("console", lambda m: errors.append(m.text)
                    if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(f"http://127.0.0.1:{port}/index.html",
                      wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
            for sid in SCREENS:
                ok = page.evaluate(
                    """(sid) => {
                        const el = document.getElementById(sid);
                        if (!el) return false;
                        document.querySelectorAll('.screen').forEach(
                            s => s.classList.remove('active'));
                        el.classList.add('active');
                        window.scrollTo(0, 0);
                        return true; }""", sid)
                path = os.path.join(out, f"{sid}-{name}.png")
                try:
                    data = page.screenshot(full_page=False)
                    with open(path, "wb") as f:
                        f.write(data)
                    shots.append({"screen": sid, "viewport": name,
                                  "file": os.path.basename(path),
                                  "bytes": len(data), "found": bool(ok)})
                except Exception as e:  # noqa: BLE001
                    shots.append({"screen": sid, "viewport": name,
                                  "file": os.path.basename(path),
                                  "bytes": 0, "found": bool(ok),
                                  "save_error": str(e)[:200]})
            page.close()
        browser.close()
    httpd.shutdown()
    diffs = None
    if baseline and os.path.isdir(baseline):
        diffs = []
        for s in shots:
            base = os.path.join(baseline, s["file"])
            cur = os.path.join(out, s["file"])
            if not (os.path.exists(base) and os.path.exists(cur)):
                diffs.append({"file": s["file"], "status": "no-baseline"})
                continue
            diff_path = os.path.join(out, "diff-" + s["file"])
            try:
                r = subprocess.run(["npx", "-y", "pixelmatch", base, cur,
                                    diff_path], capture_output=True,
                                   text=True, timeout=120)
                diffs.append({"file": s["file"],
                              "status": "compared" if r.returncode == 0
                              else f"pixelmatch-exit-{r.returncode}",
                              "output": (r.stdout + r.stderr).strip()[:300]})
            except Exception as e:  # noqa: BLE001
                diffs.append({"file": s["file"],
                              "status": f"pixelmatch-unavailable: {e}"[:200]})
    return {"shots": shots, "console_errors": errors[:20],
            "pixelmatch": diffs or "no baseline dir given: captures are "
            "the baseline (no fake diff)"}


def run_t3_assets(repo, out, img2img):
    from PIL import Image, ImageDraw
    os.makedirs(out, exist_ok=True)
    manifest_path = os.path.join(repo, "game", "data", "t3-ui-art.json")
    with open(manifest_path) as f:
        manifest = json.load(f)
    items, total_in = [], 0
    for a in manifest["assets"]:
        src = os.path.join(repo, a["png"])
        im = Image.open(src).convert("RGBA")
        total_in += os.path.getsize(src)
        crop_w = 390
        scale = crop_w / im.width if im.width else 1
        crop = im.resize((crop_w, max(1, round(im.height * scale))),
                         Image.LANCZOS)
        crop_path = os.path.join(out, a["id"] + "-phone390.png")
        try:
            crop.save(crop_path)
            crop_bytes = os.path.getsize(crop_path)
        except Exception as e:  # noqa: BLE001
            crop_bytes, crop_path = 0, f"save-error: {e}"[:200]
        items.append({"id": a["id"], "category": a["category"],
                      "input": a["png"], "input_bytes": os.path.getsize(src),
                      "input_dims": f"{im.width}x{im.height}",
                      "crop": os.path.basename(crop_path)
                      if crop_bytes else crop_path,
                      "crop_bytes": crop_bytes})
    # Contact sheet: 3 columns, labeled cells, 390px-wide thumbs.
    thumbs = []
    for a, it in zip(manifest["assets"], items):
        im = Image.open(os.path.join(repo, a["png"])).convert("RGBA")
        im.thumbnail((390, 390), Image.LANCZOS)
        thumbs.append((a["id"], im))
    cols = 3
    cell_w = 410
    rows = []
    y = 0
    sheet_h = 0
    for i in range(0, len(thumbs), cols):
        row = thumbs[i:i + cols]
        rh = max(im.height for _, im in row) + 30
        rows.append((y, rh, row))
        y += rh
        sheet_h = y
    sheet = Image.new("RGBA", (cols * cell_w, sheet_h), (16, 16, 24, 255))
    d = ImageDraw.Draw(sheet)
    for y0, rh, row in rows:
        for j, (aid, im) in enumerate(row):
            x = j * cell_w + 10
            d.text((x, y0 + 4), aid, fill=(255, 255, 255, 255))
            sheet.alpha_composite(im, (x, y0 + 28))
    sheet_path = os.path.join(out, "t3-ui-contact-sheet.png")
    try:
        sheet.save(sheet_path)
        sheet_bytes = os.path.getsize(sheet_path)
    except Exception as e:  # noqa: BLE001
        sheet_bytes, sheet_path = 0, f"save-error: {e}"[:200]
    gen = "skipped: --img2img not passed (contact sheet + crops only)"
    if img2img:
        try:
            import torch  # noqa: PLC0415
            gen = ("img2img requested but no supported pipeline is wired "
                   "in this script; torch present: "
                   f"{torch.cuda.is_available()}. Generation runs in the "
                   "coordinator notebook with a model the coordinator "
                   "selects; this script never invents model output.")
        except ImportError:
            gen = ("img2img requested but torch is absent on this host; "
                   "no generation performed, no output faked.")
    return {"assets": items, "total_input_bytes": total_in,
            "contact_sheet": os.path.basename(sheet_path)
            if sheet_bytes else sheet_path,
            "contact_sheet_bytes": sheet_bytes, "img2img": gen}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["regression", "t3-assets"])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--baseline", default="")
    ap.add_argument("--img2img", action="store_true")
    args = ap.parse_args()
    t_start = time.perf_counter()
    report = {"mode": args.mode, "repo": args.repo, "out": args.out,
              "gpu_proof": gpu_proof(), "steps": {}}
    if args.mode == "regression":
        res, dt = timed(lambda: run_regression(
            args.repo, args.out, args.baseline or None))
        report["steps"]["regression"] = {"wall_s": dt, **res}
    else:
        res, dt = timed(lambda: run_t3_assets(
            args.repo, args.out, args.img2img))
        report["steps"]["t3_assets"] = {"wall_s": dt, **res}
    report["total_wall_s"] = round(time.perf_counter() - t_start, 3)
    report["speedup"] = ("not computed here: compare this report's "
                         "total_wall_s against a CPU-baseline report's "
                         "total_wall_s for the same inputs")
    # Print FIRST: the report must survive even where the sandbox blocks
    # Python file writes (observed in this VM: open(..., "w") raises
    # PermissionError while shell redirects still work). The file write
    # below is best-effort; stdout is the authoritative record.
    print(json.dumps(report, indent=2))
    out_json = os.path.join(args.out, "report.json")
    try:
        with open(out_json, "w") as f:
            json.dump(report, f, indent=2)
        print(f"REPORT: {out_json}")
    except Exception as e:  # noqa: BLE001
        print(f"REPORT NOT SAVED to {out_json} ({e}); "
              "stdout above is the record", file=sys.stderr)


if __name__ == "__main__":
    main()
