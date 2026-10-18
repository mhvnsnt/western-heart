#!/usr/bin/env python3
"""Interactive harness debug: step next() with per-stage timeout, print everything."""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    msgs = []
    pg.on("console", lambda m: msgs.append(f"{m.type}: {m.text[:200]}"))
    pg.on("pageerror", lambda e: msgs.append(f"PAGEERROR: {str(e)[:300]}"))
    pg.goto("http://127.0.0.1:8932/stage-test.html", wait_until="domcontentloaded")
    pg.wait_for_timeout(6000)
    print("test obj:", pg.evaluate("typeof window.__test"), flush=True)
    for i in range(10):
        try:
            r = pg.evaluate("""(async () => {
                const t = await Promise.race([
                    window.__test.next(),
                    new Promise((_, rej) => setTimeout(() => rej(new Error('next-timeout')), 25000))
                ]);
                return t;
            })()""")
            print(i, r.get("id"), "errors=", r.get("errorCount"), r.get("newErrors"), flush=True)
            if r.get("done"):
                break
        except Exception as e:
            print(i, "EXC", str(e)[:200], flush=True)
            break
    print("--- msgs ---", flush=True)
    for m in msgs[-15:]:
        print(m, flush=True)
    b.close()
print("DBG DONE", flush=True)
