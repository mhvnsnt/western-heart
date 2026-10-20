#!/usr/bin/env python3
"""Own-eyes stage verification: screenshot every registered stage via the
stage-test harness, saving gallery shots + select-screen thumbnails.

Gallery: ~/workspace/your_files/stage-refs/<id>.png   (owner deliverable)
Thumbs:  game/assets/stages/thumbs/<id>.png            (wired into select UI)

Usage: python3 render_gallery.py [--only id1,id2] [--serve-port 8901]
"""
import argparse
import http.server
import io
import json
import os
import socketserver
import threading
import time

from playwright.sync_api import sync_playwright

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GAME_DIR = os.path.join(REPO, "game")
GALLERY_DIR = os.path.expanduser("~/workspace/your_files/stage-refs")
THUMB_DIR = os.path.join(GAME_DIR, "assets", "stages", "thumbs")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve(port):
    os.chdir(GAME_DIR)
    with socketserver.TCPServer(("127.0.0.1", port), QuietHandler) as httpd:
        httpd.serve_forever()


import os
BATCH = int(os.environ.get("GALLERY_BATCH", "6"))  # restart browser every N stages (SwiftShader OOM guard)


def render_batch(p, port, stages, results, msgs):
    b = p.chromium.launch(headless=True, args=["--use-gl=swiftshader", "--enable-webgl"])
    try:
        pg = b.new_page(viewport={"width": 960, "height": 540})
        pg.on("console", lambda m: msgs.append(f"{m.type}: {m.text[:160]}"))
        pg.on("pageerror", lambda e: msgs.append(f"pageerror: {str(e)[:160]}"))
        pg.goto(f"http://127.0.0.1:{port}/stage-test.html")
        pg.wait_for_function("window.__test && window.__test.stages.length > 0", timeout=30000)
        for s in stages:
            sid = s["id"]
            try:
                r = pg.evaluate(f"window.__test.jump('{sid}')")
            except Exception as e:
                print(f"{sid}: BROWSER CRASH ({e}), will retry in next batch")
                return False
            # let GLBs/textures stream in, then settle
            pg.wait_for_timeout(2500)
            try:
                # pose the camera per-stage (the harness only runs one
                # update(), so the fighting-camera lerp never settles)
                cam = pg.evaluate(
                    f"window.__test.stages.find(s=>s.id==='{sid}')")
                camd = cam.get("camDist") or 7
                ang = (cam.get("camAngle") or 0) * 3.14159265 / 180
                import math as _m
                if cam.get("camPos"):
                    p, t = cam["camPos"], cam["camTgt"] or [0, 1, 0]
                    pg.evaluate(f"__arena.camera.position.set({p[0]},{p[1]},{p[2]});"
                                f"__arena.camera.lookAt({t[0]},{t[1]},{t[2]}); __arena.render();")
                else:
                    pg.evaluate(f"__arena.camera.position.set("
                                f"{_m.sin(ang)*camd:.3f},1.8,"
                                f"{_m.cos(ang)*camd:.3f});"
                                "__arena.camera.lookAt(0,1,0); __arena.render();")
                pg.wait_for_timeout(400)
                shot = pg.screenshot()
            except Exception as e:
                print(f"{sid}: shot failed ({e}), will retry in next batch")
                return False
            gpath = os.path.join(GALLERY_DIR, f"{sid}.png")
            with open(gpath, "wb") as f:
                f.write(shot)
            # thumbnail: downscale to 480x270
            try:
                from PIL import Image
                im = Image.open(io.BytesIO(shot)).resize((480, 270), Image.LANCZOS)
                im.save(os.path.join(THUMB_DIR, f"{sid}.png"))
            except ImportError:
                with open(os.path.join(THUMB_DIR, f"{sid}.png"), "wb") as f:
                    f.write(shot)
            err = r.get("newErrors") or []
            results.append({"id": sid, "name": s["name"], "errors": err})
            flag = "ERRORS: " + " | ".join(err) if err else "OK"
            print(f"{sid}: {flag} -> {gpath}", flush=True)
    finally:
        b.close()
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--skip-done", action="store_true",
                    help="skip stages that already have a gallery png")
    ap.add_argument("--serve-port", type=int, default=8901)
    args = ap.parse_args()

    os.makedirs(GALLERY_DIR, exist_ok=True)
    os.makedirs(THUMB_DIR, exist_ok=True)

    t = threading.Thread(target=serve, args=(args.serve_port,), daemon=True)
    t.start()
    time.sleep(1)

    with sync_playwright() as p:
        # probe stage list once
        b = p.chromium.launch(headless=True, args=["--use-gl=swiftshader"])
        pg = b.new_page()
        pg.goto(f"http://127.0.0.1:{args.serve_port}/stage-test.html")
        pg.wait_for_function("window.__test && window.__test.stages.length > 0", timeout=30000)
        stages = pg.evaluate("window.__test.stages")
        b.close()
        print(f"{len(stages)} stages registered")
        if args.only:
            want = set(args.only.split(","))
            stages = [s for s in stages if s["id"] in want]
        if args.skip_done:
            stages = [s for s in stages
                      if not os.path.exists(os.path.join(GALLERY_DIR, s["id"] + ".png"))]
            print(f"{len(stages)} remaining after --skip-done")

        results, msgs = [], []
        i = 0
        while i < len(stages):
            ok = render_batch(p, args.serve_port, stages[i:i + BATCH], results, msgs)
            if ok:
                i += BATCH
            else:
                print("batch failed, retrying same batch with fresh browser...")
                time.sleep(2)

    with open(os.path.join(GALLERY_DIR, "_render-report.json"), "w") as f:
        json.dump(results, f, indent=2)
    n_err = sum(1 for r in results if r["errors"])
    print(f"done: {len(results)} stages, {n_err} with errors")
    for m in msgs[:20]:
        print("LOG:", m)


if __name__ == "__main__":
    main()
