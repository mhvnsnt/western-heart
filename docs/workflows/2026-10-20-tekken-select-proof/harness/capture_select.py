#!/usr/bin/env python3
"""Tekken-select verification captures — staged, fresh browser per
stage (SwiftShader GPU targets die under cumulative load in this
VM; staging keeps each stage's evidence independent).
Stages:
  B phone : versus -> DEMONIO (bank stance A/B) -> K attire switch
            -> CONFIRM (P1 lock) -> RIN on P2 -> CONFIRM -> stage
  C phone : versus -> PANTERA vs RIN -> stage -> FIGHT (HUD canvas)
  D desk  : versus -> PANTERA pick (wide framing)
In-process static server rooted at the worktree.
"""
import sys, base64, json, threading, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

ROOT = "/home/hatch/workspace/_wh-work/select-screen"
OUT = "/home/hatch/workspace/your_files"
PREFIX = sys.argv[1] if len(sys.argv) > 1 else "select-new"

handler = functools.partial(SimpleHTTPRequestHandler, directory=ROOT)
httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
PORT = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{PORT}/game/"
print("SERVER", BASE, flush=True)


def open_page(p, viewport):
    b = p.chromium.launch(headless=True, args=[
        "--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader",
        "--no-sandbox", "--disable-dev-shm-usage", "--mute-audio"])
    ctx = b.new_context(viewport=viewport)
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)[:250]))
    pg.on("console", lambda m: errs.append("console.error: " + m.text[:200]) if m.type == "error" else None)
    cdp = pg.context.new_cdp_session(pg)
    return b, pg, cdp, errs


def shot(cdp, name):
    r = cdp.send("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
    path = f"{OUT}/{PREFIX}-{name}.png"
    open(path, "wb").write(base64.b64decode(r["data"]))
    print("SHOT", path, flush=True)
    return path


def tap(pg, selector):
    r = pg.evaluate("""(sel) => { const el = document.querySelector(sel);
        if (!el) return 'missing';
        el.scrollIntoView({block:'nearest', inline:'nearest'}); el.click(); return 'clicked'; }""", selector)
    print("TAP", selector, "->", r, flush=True)
    return r == 'clicked'


def pane_state(pg, side):
    return pg.evaluate(f"""() => {{
        const root = document.querySelector('#pane-{side}');
        const note = root.querySelector('.pane-note');
        return {{ name: root.querySelector('.pane-name').textContent,
                  style: root.querySelector('.pane-style').textContent,
                  noteHidden: note.hidden, note: note.textContent,
                  locked: !root.querySelector('.lock-badge').hidden,
                  active: root.classList.contains('is-active'),
                  chips: [...root.querySelectorAll('.attire-chip')].map(c => c.textContent + (c.classList.contains('on') ? '*' : '')) }}; }}""")


def wait_pane(pg, side, want_name, timeout_s=60):
    for _ in range(timeout_s):
        st = pane_state(pg, side)
        if st["name"] == want_name and st["noteHidden"]:
            print(f"pane {side} ready:", json.dumps(st), flush=True)
            return st
        pg.wait_for_timeout(1000)
    print(f"pane {side} TIMEOUT wanting {want_name}:", json.dumps(pane_state(pg, side)), flush=True)
    return None


def to_select(pg):
    pg.goto(BASE, wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_function("() => !!window.__modes", timeout=120000)
    tap(pg, '[data-action="mode-versus"]')
    pg.wait_for_selector('#screen-select.active', timeout=30000)
    pg.wait_for_timeout(1000)


def stage_b(p):
    print("=== STAGE B (phone, demonio stance + attire + versus) ===", flush=True)
    b, pg, cdp, errs = open_page(p, {"width": 390, "height": 844})
    try:
        to_select(pg)
        tap(pg, '.char-card[data-id="demonio"]')
        wait_pane(pg, "p1", "DEMONIO")
        pg.wait_for_timeout(600)
        shot(cdp, "phone-demonio-stance-a")
        pg.wait_for_timeout(2600)
        shot(cdp, "phone-demonio-stance-b")
        # attire switch: K = attire 2 slot -> chip 'ATTIRE 1' model
        tap(pg, '#attire-kick')
        ok = False
        for _ in range(60):
            st = pane_state(pg, "p1")
            if st["noteHidden"] and any(c.endswith('*') and 'ATTIRE 1' in c for c in st["chips"]):
                ok = True
                break
            pg.wait_for_timeout(1000)
        print("attire switch to ATTIRE 1:", ok, json.dumps(pane_state(pg, "p1")), flush=True)
        pg.wait_for_timeout(600)
        shot(cdp, "phone-demonio-attire1")
        tap(pg, '#confirm-fighter')
        pg.wait_for_timeout(800)
        print("AFTER P1 CONFIRM:", json.dumps({
            "p1": pane_state(pg, "p1"), "p2": pane_state(pg, "p2")}), flush=True)
        tap(pg, '.char-card[data-id="rin"]')
        wait_pane(pg, "p2", "RIN")
        pg.wait_for_timeout(600)
        shot(cdp, "phone-versus-p2-rin")
        tap(pg, '#confirm-fighter')
        pg.wait_for_selector('#screen-stage.active', timeout=20000)
        pg.wait_for_timeout(800)
        shot(cdp, "phone-stage-select")
    finally:
        print("STAGE B ERRORS:", json.dumps(errs[:8]), flush=True)
        b.close()


def stage_c(p):
    print("=== STAGE C (phone, pantera vs rin -> fight) ===", flush=True)
    b, pg, cdp, errs = open_page(p, {"width": 390, "height": 844})
    try:
        to_select(pg)
        tap(pg, '.char-card[data-id="pantera"]')
        wait_pane(pg, "p1", "PANTERA")
        pg.wait_for_timeout(600)
        shot(cdp, "phone-pantera-stance")
        tap(pg, '#confirm-fighter')
        tap(pg, '.char-card[data-id="rin"]')
        wait_pane(pg, "p2", "RIN")
        tap(pg, '#confirm-fighter')
        pg.wait_for_selector('#screen-stage.active', timeout=20000)
        tap(pg, '#confirm-stage')
        hud = False
        for _ in range(25):
            pg.wait_for_timeout(4000)
            hud = pg.evaluate("() => document.getElementById('hud').classList.contains('active')")
            if hud:
                break
        print("HUD REACHED:", hud, flush=True)
        if hud:
            pg.wait_for_timeout(6000)
            data = pg.evaluate("() => document.getElementById('game-canvas').toDataURL('image/png')")
            path = f"{OUT}/{PREFIX}-phone-fight-canvas.png"
            open(path, "wb").write(base64.b64decode(data.split(",", 1)[1]))
            print("SHOT", path, flush=True)
            shot(cdp, "phone-fight-dom")
    finally:
        print("STAGE C ERRORS:", json.dumps(errs[:8]), flush=True)
        b.close()


def stage_d(p):
    print("=== STAGE D (desktop, pantera framing) ===", flush=True)
    b, pg, cdp, errs = open_page(p, {"width": 1280, "height": 800})
    try:
        to_select(pg)
        shot(cdp, "desktop-initial")
        tap(pg, '.char-card[data-id="pantera"]')
        wait_pane(pg, "p1", "PANTERA")
        pg.wait_for_timeout(600)
        shot(cdp, "desktop-pantera-stance-a")
        pg.wait_for_timeout(2600)
        shot(cdp, "desktop-pantera-stance-b")
    finally:
        print("STAGE D ERRORS:", json.dumps(errs[:8]), flush=True)
        b.close()


with sync_playwright() as p:
    stage_b(p)
    stage_c(p)
    stage_d(p)
print("ALL STAGES DONE", flush=True)
