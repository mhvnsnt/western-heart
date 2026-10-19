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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--serve-port", type=int, default=8901)
    args = ap.parse_args()

    os.makedirs(GALLERY_DIR, exist_ok=True)
    os.makedirs(THUMB_DIR, exist_ok=True)

    t = threading.Thread(target=serve, args=(args.serve_port,), daemon=True)
    t.start()
    time.sleep(1)

    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--use-gl=swiftshader", "--enable-webgl"])
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        msgs = []
        pg.on("console", lambda m: msgs.append(f"{m.type}: {m.text[:160]}"))
        pg.on("pageerror", lambda e: msgs.append(f"pageerror: {str(e)[:160]}"))
        pg.goto(f"http://127.0.0.1:{args.serve_port}/stage-test.html")
        pg.wait_for_function("window.__test && window.__test.stages.length > 0", timeout=30000)
        stages = pg.evaluate("window.__test.stages")
        print(f"{len(stages)} stages registered")
        if args.only:
            want = set(args.only.split(","))
            stages = [s for s in stages if s["id"] in want]

        results = []
        for s in stages:
            sid = s["id"]
            r = pg.evaluate(f"window.__test.jump('{sid}')")
            # let GLBs/textures stream in, then settle
            pg.wait_for_timeout(2500)
            pg.evaluate("window.__test.snap()")
            pg.wait_for_timeout(400)
            shot = pg.screenshot()
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
            print(f"{sid}: {flag} -> {gpath}")
        b.close()

    with open(os.path.join(GALLERY_DIR, "_render-report.json"), "w") as f:
        json.dump(results, f, indent=2)
    n_err = sum(1 for r in results if r["errors"])
    print(f"done: {len(results)} stages, {n_err} with errors")
    for m in msgs[:20]:
        print("LOG:", m)


if __name__ == "__main__":
    main()
