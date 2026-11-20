import json, sys
from playwright.sync_api import sync_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8931/game/"
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=[
        "--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader",
        "--no-sandbox", "--disable-dev-shm-usage", "--mute-audio"])
    pg = b.new_page(viewport={"width": 390, "height": 844})
    msgs = []
    pg.on("pageerror", lambda e: msgs.append("PAGEERROR: " + str(e)[:300]))
    pg.on("console", lambda m: msgs.append("console." + m.type + ": " + m.text[:200]) if m.type == "error" else None)
    pg.on("requestfailed", lambda r: msgs.append("REQFAIL: " + r.url.split('/')[-1]))
    pg.on("response", lambda r: msgs.append(f"HTTP {r.status}: " + r.url.split('/')[-1]) if r.status >= 400 else None)
    pg.goto(URL, wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_timeout(25000)
    st = pg.evaluate("""() => ({ modes: typeof window.__modes, game: typeof window.__game,
        cards: document.querySelectorAll('.char-card').length })""")
    print("STATE:", json.dumps(st), flush=True)
    for m in msgs[:15]:
        print(m, flush=True)
    b.close()
