"""Parity smoke test: select screen preview pane + attire strip."""
import sys
from playwright.sync_api import sync_playwright

PORT = sys.argv[1] if len(sys.argv) > 1 else "8910"
OUT = "/home/hatch/workspace/wt-stream4-parity/docs/modes/shots-parity"
import os
os.makedirs(OUT, exist_ok=True)

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 390, "height": 844})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    pg.goto(f"http://127.0.0.1:{PORT}/index.html", wait_until="domcontentloaded", timeout=60000)
    # Wait until the roster cards are built and the menu is live.
    try:
        pg.wait_for_function(
            "() => document.querySelectorAll('.char-card').length > 0",
            timeout=60000)
    except Exception as e:
        print("WAIT WARN:", str(e)[:120], flush=True)
    pg.wait_for_timeout(800)
    pg.evaluate("() => document.getElementById('tap-to-start').classList.remove('show')")
    # Go to arcade -> select
    pg.evaluate('() => document.querySelector("[data-action=mode-arcade]").click()')
    pg.wait_for_timeout(600)
    print("preview pane exists:", pg.evaluate("() => !!document.getElementById('select-preview')"), flush=True)
    pg.screenshot(path=f"{OUT}/11-select-default.png")
    # Pick thor (has 2 attires)
    pg.evaluate('() => document.querySelector(".char-card[data-id=thor]")?.click()')
    pg.wait_for_timeout(1200)
    print("preview name:", pg.evaluate("() => document.getElementById('preview-name').textContent"), flush=True)
    print("attire chips:", pg.evaluate("() => document.querySelectorAll('.attire-chip').length"), flush=True)
    print("chip labels:", pg.evaluate("() => [...document.querySelectorAll('.attire-chip')].map(c => c.textContent).join(' | ')"), flush=True)
    pg.screenshot(path=f"{OUT}/12-select-thor.png")
    # Pick attire 2
    pg.evaluate('() => document.querySelectorAll(".attire-chip")[1]?.click()')
    pg.wait_for_timeout(800)
    print("saved attire:", pg.evaluate("() => JSON.parse(localStorage.getItem('wh_attires_v1') || '{}').thor"), flush=True)
    print("hint:", pg.evaluate("() => document.getElementById('select-hint').textContent"), flush=True)
    pg.screenshot(path=f"{OUT}/13-select-thor-attire2.png")
    # Pick demonio (5 attires)
    pg.evaluate('() => document.querySelector(".char-card[data-id=demonio]")?.click()')
    pg.wait_for_timeout(800)
    print("demonio chips:", pg.evaluate("() => document.querySelectorAll('.attire-chip').length"), flush=True)
    pg.screenshot(path=f"{OUT}/14-select-demonio.png")
    print("PAGE ERRORS:", errs[:5] if errs else "none", flush=True)
    b.close()
print("DONE", flush=True)
