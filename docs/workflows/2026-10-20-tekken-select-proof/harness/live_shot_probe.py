#!/usr/bin/env python3
"""Minimal live capture probe: menu shot, then select element shot."""
import base64, json, os, socket, subprocess, time
from playwright.sync_api import sync_playwright

LIVE = "https://mhvnsnt.github.io/western-heart"
RELAY = "http://127.0.0.1:18080"
OUT = "/home/hatch/workspace/your_files"


def relay_up():
    try:
        s = socket.create_connection(("127.0.0.1", 18080), timeout=3)
        s.close()
        return True
    except OSError:
        return False


if not relay_up():
    subprocess.Popen(["python3", "/home/hatch/workspace/agent-ops/egress_relay.py"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    for _ in range(20):
        if relay_up():
            break
        time.sleep(1)
print("relay:", relay_up(), flush=True)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=[
        "--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader",
        "--no-sandbox", "--disable-dev-shm-usage", "--mute-audio",
        "--ignore-certificate-errors"])
    ctx = b.new_context(viewport={"width": 390, "height": 844},
                        proxy={"server": RELAY}, ignore_https_errors=True)
    pg = ctx.new_page()

    def _route(route):
        u = route.request.url
        if u.endswith('.glb') and not any(k in u for k in ('demonio', 'pantera')):
            return route.abort()
        return route.continue_()
    pg.route("**/*.glb", _route)
    cdp = pg.context.new_cdp_session(pg)

    def shot(name):
        r = cdp.send("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
        path = f"{OUT}/live-select-probe-{name}.png"
        open(path, "wb").write(base64.b64decode(r["data"]))
        print("SHOT", path, flush=True)

    pg.goto(LIVE + "/game/", wait_until="domcontentloaded", timeout=120000)
    pg.wait_for_function("() => !!window.__modes", timeout=180000)
    print("menu ready", flush=True)
    shot("menu")
    pg.evaluate("() => document.querySelector('[data-action=\"mode-versus\"]').click()")
    pg.wait_for_selector('#screen-select.active', timeout=60000)
    pg.wait_for_timeout(20000)
    shot("select-initial")
    pg.evaluate("() => document.querySelector('.char-card[data-id=\"demonio\"]').click()")
    ready = False
    for _ in range(90):
        st = pg.evaluate("() => { const n = document.querySelector('#pane-p1 .pane-note'); const nm = document.querySelector('#pane-p1 .pane-name'); return { hidden: n.hidden, name: nm.textContent }; }")
        if st["hidden"] and st["name"] == "DEMONIO":
            ready = True
            break
        pg.wait_for_timeout(1000)
    print("demonio ready:", ready, flush=True)
    pg.wait_for_timeout(1500)
    shot("select-demonio")
    print("PROBE DONE", flush=True)
    b.close()
