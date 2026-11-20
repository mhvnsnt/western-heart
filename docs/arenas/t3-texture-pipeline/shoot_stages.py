#!/usr/bin/env python3
"""Screenshot every stage in stages.js via game/stage-test.html. Own-eyes verification.
Captures via the harness's canvas.toDataURL snap() (pg.screenshot hangs on fonts
under SwiftShader). Usage: shoot_stages.py [outdir] [id1,id2,...]
"""
import os, sys, base64
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8932/stage-test.html"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/arena-shots"
ONLY = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None
os.makedirs(OUT, exist_ok=True)

def snap(pg, path):
    data = pg.evaluate("window.__test.snap()")
    assert data.startswith("data:image/png;base64,"), data[:60]
    with open(path, "wb") as f:
        f.write(base64.b64decode(data.split(",", 1)[1]))

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=[
        "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 640, "height": 360})
    msgs = []
    pg.on("console", lambda m: msgs.append(f"{m.type}: {m.text[:220]}"))
    pg.on("pageerror", lambda e: msgs.append(f"pageerror: {str(e)[:220]}"))
    pg.goto(URL, wait_until="domcontentloaded")
    pg.wait_for_function("window.__test && window.__test.stages.length > 0", timeout=60000)
    n = pg.evaluate("window.__test.stages.length")
    print("stage count:", n, flush=True)
    done = 0
    for _ in range(n):
        try:
            r = pg.evaluate("""(async () => {
                const t = await Promise.race([
                    window.__test.next(),
                    new Promise((_, rej) => setTimeout(() => rej(new Error('next-timeout')), 180000))
                ]);
                return t;
            })()""")
        except Exception as e:
            print(f"STAGE-ERROR: {str(e)[:160]}", flush=True)
            continue
        if r.get("done"):
            break
        sid = r["id"]
        if ONLY and sid not in ONLY:
            continue
        pg.wait_for_timeout(600)
        snap(pg, f"{OUT}/{sid}.png")
        print(f"SHOT {sid}: errors={r['errorCount']} {r.get('newErrors', [])}", flush=True)
        done += 1
    b.close()

print("--- console warnings/errors of interest ---", flush=True)
seen = set()
for m in msgs:
    if ("error" in m.lower() or "warn" in m.lower()) and m not in seen:
        seen.add(m)
        print(" ", m, flush=True)
print("DONE", done, flush=True)
