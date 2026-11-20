#!/usr/bin/env python3
"""Probe: does the king-bank stance pass the fit gate on pantera now?
Captures the pane + the [WH] gate log lines."""
import base64, json, threading, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

ROOT = "/home/hatch/workspace/_wh-work/select-screen"
handler = functools.partial(SimpleHTTPRequestHandler, directory=ROOT)
httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
PORT = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{PORT}/game/"
print("SERVER", BASE, flush=True)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=[
        "--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader",
        "--no-sandbox", "--disable-dev-shm-usage", "--mute-audio",
        "--single-process", "--no-zygote", "--js-flags=--max-old-space-size=1536"])
    pg = b.new_page(viewport={"width": 390, "height": 844})
    msgs = []
    pg.on("console", lambda m: msgs.append(m.text[:200]) if ("WH" in m.text and ("stance" in m.text or "preview" in m.text)) else None)
    cdp = pg.context.new_cdp_session(pg)
    pg.goto(BASE, wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_function("() => !!window.__modes", timeout=120000)
    pg.evaluate("() => document.querySelector('[data-action=\"mode-versus\"]').click()")
    pg.wait_for_selector('#screen-select.active', timeout=30000)
    pg.evaluate("() => document.querySelector('.char-card[data-id=\"pantera\"]').click()")
    for _ in range(75):
        st = pg.evaluate("() => { const n = document.querySelector('#pane-p1 .pane-note'); return n.hidden; }")
        if st:
            break
        pg.wait_for_timeout(1000)
    pg.wait_for_timeout(1500)
    st = pg.evaluate("() => { const q = window.__selectScreen._panes.p1; return { hasStance: q.hasStance }; }")
    print("PANTERA PANE:", json.dumps(st), flush=True)
    print("GATE LOGS:", json.dumps(msgs, indent=1), flush=True)
    r = cdp.send("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
    open("/home/hatch/workspace/your_files/select-v3-phone-pantera-gate.png", "wb").write(base64.b64decode(r["data"]))
    print("SHOT saved", flush=True)
    b.close()
