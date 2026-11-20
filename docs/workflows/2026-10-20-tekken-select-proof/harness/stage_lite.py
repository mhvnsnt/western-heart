#!/usr/bin/env python3
"""Lite select-proof stages — one short flow per fresh browser,
memory-lean flags for this loaded VM. Usage: stage_lite.py <stage>
Stages: attire | versus | fight | desktop"""
import sys, base64, json, threading, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

ROOT = "/home/hatch/workspace/_wh-work/select-screen"
OUT = "/home/hatch/workspace/your_files"
PREFIX = sys.argv[2] if len(sys.argv) > 2 else "select-v2"

handler = functools.partial(SimpleHTTPRequestHandler, directory=ROOT)
httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
PORT = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{PORT}/game/"
print("SERVER", BASE, flush=True)

ARGS = ["--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader",
        "--no-sandbox", "--disable-dev-shm-usage", "--mute-audio",
        "--single-process", "--no-zygote", "--js-flags=--max-old-space-size=1536"]


def open_page(p, viewport):
    b = p.chromium.launch(headless=True, args=ARGS)
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


def wait_pane(pg, side, want_name, timeout_s=75):
    for _ in range(timeout_s):
        st = pane_state(pg, side)
        if st["name"] == want_name and st["noteHidden"]:
            print(f"pane {side} ready:", json.dumps(st), flush=True)
            return st
        pg.wait_for_timeout(1000)
    print(f"pane {side} TIMEOUT wanting {want_name}:", json.dumps(pane_state(pg, side)), flush=True)
    return None



def ensure_highlight(pg, side, card_id, want_name, tries=4):
    """The game's real 99s select timer can TIME UP during slow test
    loads and jump the cursor to a random fighter; re-tap the wanted
    card until the pane shows the wanted fighter."""
    for _ in range(tries):
        st = pane_state(pg, side)
        if st["name"] == want_name and st["noteHidden"]:
            return st
        tap(pg, f'.char-card[data-id="{card_id}"]')
        st = wait_pane(pg, side, want_name, timeout_s=30)
        if st:
            return st
    return pane_state(pg, side)

def to_select(pg):
    pg.goto(BASE, wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_function("() => !!window.__modes", timeout=120000)
    tap(pg, '[data-action="mode-versus"]')
    pg.wait_for_selector('#screen-select.active', timeout=30000)
    pg.wait_for_timeout(1000)


def st_attire(p):
    b, pg, cdp, errs = open_page(p, {"width": 390, "height": 844})
    try:
        to_select(pg)
        tap(pg, '.char-card[data-id="demonio"]')
        wait_pane(pg, "p1", "DEMONIO")
        pg.wait_for_timeout(500)
        shot(cdp, "phone-demonio-stance-a")
        ensure_highlight(pg, "p1", "demonio", "DEMONIO")
        pg.wait_for_timeout(2600)
        shot(cdp, "phone-demonio-stance-b")
        ensure_highlight(pg, "p1", "demonio", "DEMONIO")
        tap(pg, '#attire-kick')
        ok = False
        for _ in range(60):
            st = pane_state(pg, "p1")
            if st["noteHidden"] and any(c.endswith('*') and 'ATTIRE 1' in c for c in st["chips"]):
                ok = True
                break
            pg.wait_for_timeout(1000)
        print("attire switch to ATTIRE 1:", ok, json.dumps(pane_state(pg, "p1")), flush=True)
        pg.wait_for_timeout(500)
        shot(cdp, "phone-demonio-attire1")
    finally:
        print("ATTIRE ERRORS:", json.dumps(errs[:6]), flush=True)
        b.close()


def st_versus(p):
    b, pg, cdp, errs = open_page(p, {"width": 390, "height": 844})
    try:
        to_select(pg)
        tap(pg, '.char-card[data-id="pantera"]')
        wait_pane(pg, "p1", "PANTERA")
        ensure_highlight(pg, "p1", "pantera", "PANTERA")
        tap(pg, '#confirm-fighter')
        pg.wait_for_timeout(600)
        print("AFTER P1 CONFIRM:", json.dumps({"p1": pane_state(pg, "p1"), "p2": pane_state(pg, "p2")}), flush=True)
        tap(pg, '.char-card[data-id="rin"]')
        wait_pane(pg, "p2", "RIN")
        pg.wait_for_timeout(500)
        shot(cdp, "phone-versus-p2-rin")
        ensure_highlight(pg, "p2", "rin", "RIN")
        tap(pg, '#confirm-fighter')
        pg.wait_for_selector('#screen-stage.active', timeout=20000)
        pg.wait_for_timeout(700)
        shot(cdp, "phone-stage-select")
    finally:
        print("VERSUS ERRORS:", json.dumps(errs[:6]), flush=True)
        b.close()


def st_fight(p):
    b, pg, cdp, errs = open_page(p, {"width": 390, "height": 844})
    try:
        to_select(pg)
        tap(pg, '.char-card[data-id="pantera"]')
        wait_pane(pg, "p1", "PANTERA")
        ensure_highlight(pg, "p1", "pantera", "PANTERA")
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
            shot(cdp, "phone-fight-dom-a")
            pg.wait_for_timeout(3000)
            shot(cdp, "phone-fight-dom-b")
    finally:
        print("FIGHT ERRORS:", json.dumps(errs[:6]), flush=True)
        b.close()


def st_desktop(p):
    b, pg, cdp, errs = open_page(p, {"width": 1280, "height": 800})
    try:
        to_select(pg)
        shot(cdp, "desktop-initial")
        tap(pg, '.char-card[data-id="pantera"]')
        wait_pane(pg, "p1", "PANTERA")
        pg.wait_for_timeout(500)
        shot(cdp, "desktop-pantera-stance-a")
        pg.wait_for_timeout(2600)
        shot(cdp, "desktop-pantera-stance-b")
    finally:
        print("DESKTOP ERRORS:", json.dumps(errs[:6]), flush=True)
        b.close()



def st_motion(p):
    b, pg, cdp, errs = open_page(p, {"width": 390, "height": 844})
    try:
        to_select(pg)
        tap(pg, '.char-card[data-id="demonio"]')
        wait_pane(pg, "p1", "DEMONIO")
        s1 = pg.evaluate("() => { const q = window.__selectScreen._panes.p1; return { rotY: q.model.rotation.y, mt: q.mixer.time }; }")
        print("MOTION SAMPLE 1:", json.dumps(s1), flush=True)
        shot(cdp, "phone-demonio-motion-a")
        pg.wait_for_timeout(75000)
        s2 = pg.evaluate("() => { const q = window.__selectScreen._panes.p1; return { rotY: q.model.rotation.y, mt: q.mixer.time }; }")
        print("MOTION SAMPLE 2:", json.dumps(s2), flush=True)
        shot(cdp, "phone-demonio-motion-b")
    finally:
        print("MOTION ERRORS:", json.dumps(errs[:6]), flush=True)
        b.close()

STAGES = {"motion": st_motion, "attire": st_attire, "versus": st_versus, "fight": st_fight, "desktop": st_desktop}
with sync_playwright() as p:
    STAGES[sys.argv[1]](p)
print("STAGE DONE", sys.argv[1], flush=True)
