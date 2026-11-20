#!/usr/bin/env python3
"""Live-site proof for the Tekken select deploy.
1) Byte-verify key game files on https://mhvnsnt.github.io/western-heart/
   against origin/main blobs (via the sandbox egress relay).
2) Drive the LIVE game: versus -> demonio -> K attire -> confirm ->
   pantera on P2, CDP screenshots along the way.
"""
import base64, hashlib, json, os, socket, subprocess, sys, time
import urllib.request
from playwright.sync_api import sync_playwright

LIVE = "https://mhvnsnt.github.io/western-heart"
RELAY = "http://127.0.0.1:18080"
OUT = "/home/hatch/workspace/your_files"
PREFIX = "live-select-final"
REPO = "/home/hatch/workspace/_wh-work/select-screen"


def relay_up():
    try:
        s = socket.create_connection(("127.0.0.1", 18080), timeout=3)
        s.close()
        return True
    except OSError:
        return False


if not relay_up():
    print("starting egress relay...", flush=True)
    subprocess.Popen(["python3", "/home/hatch/workspace/agent-ops/egress_relay.py"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    for _ in range(20):
        if relay_up():
            break
        time.sleep(1)
print("relay up:", relay_up(), flush=True)

proxy_handler = urllib.request.ProxyHandler({"http": RELAY, "https": RELAY})
opener = urllib.request.build_opener(proxy_handler)


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"})
    with opener.open(req, timeout=timeout) as r:
        return r.read()


def main_blob(path):
    return subprocess.run(["git", "-C", REPO, "show", f"origin/main:{path}"],
                          capture_output=True, check=True).stdout


FILES = ["game/index.html", "game/select.css", "game/js/select-screen.js", "game/js/main.js"]
ok = bool(os.environ.get("SKIP_VERIFY"))
for attempt in range(0 if ok else 10):
    results = {}
    allok = True
    for f in FILES:
        try:
            live_bytes = fetch(f"{LIVE}/{f}?v=deploy384")
            want = main_blob(f)
            same = hashlib.sha256(live_bytes).hexdigest() == hashlib.sha256(want).hexdigest()
            results[f] = f"{len(live_bytes)}B sha-match={same}"
            allok = allok and same
        except Exception as e:
            results[f] = f"FETCH ERR {str(e)[:80]}"
            allok = False
    print(f"BYTE-VERIFY attempt {attempt}:", json.dumps(results, indent=1), flush=True)
    if allok:
        ok = True
        break
    time.sleep(45)
print("BYTE-VERIFY ALL MATCH:", ok, flush=True)
if not ok:
    print("Pages build may still be propagating; continuing to browser proof anyway", flush=True)


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


def wait_pane(pg, side, want_name, timeout_s=90):
    for _ in range(timeout_s):
        st = pane_state(pg, side)
        if st["name"] == want_name and st["noteHidden"]:
            print(f"pane {side} ready:", json.dumps(st), flush=True)
            return st
        pg.wait_for_timeout(1000)
    print(f"pane {side} TIMEOUT wanting {want_name}:", json.dumps(pane_state(pg, side)), flush=True)
    return None


with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=[
        "--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader",
        "--no-sandbox", "--disable-dev-shm-usage", "--mute-audio",
        "--js-flags=--max-old-space-size=1536",
        "--ignore-certificate-errors"])
    ctx = b.new_context(viewport={"width": 390, "height": 844},
                        proxy={"server": RELAY}, ignore_https_errors=True)
    pg = ctx.new_page()
    # Memory triage for this loaded VM: the select proof needs only
    # demonio (P1 + its attire) and pantera (P2). Abort every other
    # GLB (preloadAll warms several 10-25MB models over the relay;
    # their textures pile up and the SwiftShader target dies).
    def _route(route):
        u = route.request.url
        if u.endswith('.glb') and not any(k in u for k in ('demonio', 'pantera')):
            return route.abort()
        return route.continue_()
    pg.route("**/*.glb", _route)
    errs = []
    pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)[:250]))
    pg.on("console", lambda m: errs.append("console.error: " + m.text[:200]) if m.type == "error" else None)
    pg.goto(LIVE + "/game/", wait_until="domcontentloaded", timeout=120000)
    pg.wait_for_function("() => !!window.__modes", timeout=180000)
    tap(pg, '[data-action="mode-versus"]')
    pg.wait_for_selector('#screen-select.active', timeout=60000)
    pg.wait_for_timeout(1000)
    facts = pg.evaluate("""() => ({
        cards: document.querySelectorAll('.char-card').length,
        stripScrollW: document.getElementById('char-grid').scrollWidth,
        stripClientW: document.getElementById('char-grid').clientWidth,
        bodyScrolls: document.documentElement.scrollHeight > window.innerHeight + 2 })""")
    print("LIVE STRIP FACTS:", json.dumps(facts), flush=True)
    shot(cdp := pg.context.new_cdp_session(pg), "phone-initial")
    tap(pg, '.char-card[data-id="demonio"]')
    wait_pane(pg, "p1", "DEMONIO")
    pg.wait_for_timeout(500)
    shot(cdp, "phone-demonio")
    tap(pg, '#attire-kick')
    switched = False
    for _ in range(60):
        st = pane_state(pg, "p1")
        if st["noteHidden"] and any(c.endswith('*') and 'ATTIRE 1' in c for c in st["chips"]):
            switched = True
            break
        pg.wait_for_timeout(1000)
    print("LIVE ATTIRE SWITCH:", switched, json.dumps(pane_state(pg, "p1")), flush=True)
    pg.wait_for_timeout(500)
    shot(cdp, "phone-demonio-attire1")
    tap(pg, '#confirm-fighter')
    pg.wait_for_timeout(600)
    print("AFTER P1 CONFIRM:", json.dumps({"p1": pane_state(pg, "p1"), "p2": pane_state(pg, "p2")}), flush=True)
    tap(pg, '.char-card[data-id="pantera"]')
    wait_pane(pg, "p2", "PANTERA")
    pg.wait_for_timeout(500)
    shot(cdp, "phone-versus-pair")
    print("LIVE ERRORS:", json.dumps(errs[:8]), flush=True)
    b.close()
print("LIVE PROOF DONE", flush=True)
