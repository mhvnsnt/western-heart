#!/usr/bin/env python3
"""Shoot remaining T3 stages with the minimal viewer (no bloom -> no crash)."""
import sys, base64
from playwright.sync_api import sync_playwright

STAGES = sys.argv[1].split(",")
OUT = sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 640, "height": 360})
    msgs = []
    pg.on("console", lambda m: msgs.append(f"{m.type}: {m.text[:200]}"))
    pg.on("pageerror", lambda e: msgs.append(f"PAGEERROR: {str(e)[:250]}"))
    pg.goto("http://127.0.0.1:8932/t3-view.html", wait_until="domcontentloaded")
    pg.wait_for_function("window.__t3", timeout=60000)
    for sid in STAGES:
        r = pg.evaluate(f"""(async () => {{
            const t = await Promise.race([
                window.__t3.show('{sid}'),
                new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), 120000))
            ]);
            return t;
        }})()""")
        data = pg.evaluate("window.__t3.snap()")
        open(f"{OUT}/{sid}.png", "wb").write(base64.b64decode(data.split(",", 1)[1]))
        print(f"SHOT {sid} {r['name']}", flush=True)
    print("errors:", pg.evaluate("window.__t3.errors"), flush=True)
    for m in msgs:
        if "error" in m.lower():
            print(" ", m, flush=True)
    b.close()
print("DONE", flush=True)
