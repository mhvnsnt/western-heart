"""File-based parity verification (survives exec aborts)."""
import os
from playwright.sync_api import sync_playwright

OUT = "/home/hatch/workspace/wt-stream4-parity/docs/modes/shots-parity"
LOG = "/home/hatch/workspace/tmp-chromium/verify.log"
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def log(*a):
    line = " ".join(str(x) for x in a)
    with open(LOG, "a") as f:
        f.write(line + "\n")
    print(line, flush=True)

open(LOG, "w").close()
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-dev-shm-usage", "--no-sandbox"], timeout=120000)
    pg = b.new_page(viewport={"width": 390, "height": 844})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    pg.goto("http://127.0.0.1:8910/index.html", wait_until="domcontentloaded", timeout=60000)
    try:
        pg.wait_for_function("() => document.querySelectorAll('.char-card').length > 0", timeout=90000)
        log("cards built: yes")
    except Exception as e:
        log("cards built: TIMEOUT")
    log("cards:", pg.evaluate("() => document.querySelectorAll('.char-card').length"))
    log("preview pane:", pg.evaluate("() => !!document.getElementById('select-preview')"))
    pg.evaluate("() => document.getElementById('tap-to-start').classList.remove('show')")
    pg.evaluate('() => document.querySelector("[data-action=mode-arcade]").click()')
    pg.wait_for_timeout(800)
    pg.evaluate('() => document.querySelector(".char-card[data-id=thor]")?.click()')
    pg.wait_for_timeout(2500)
    log("preview name:", pg.evaluate("() => document.getElementById('preview-name').textContent"))
    log("attire chips:", pg.evaluate("() => document.querySelectorAll('.attire-chip').length"))
    log("chip labels:", pg.evaluate("() => [...document.querySelectorAll('.attire-chip')].map(c => c.textContent).join(' | ')"))
    pg.screenshot(path=f"{OUT}/12-select-thor.png")
    pg.evaluate('() => document.querySelectorAll(".attire-chip")[1]?.click()')
    pg.wait_for_timeout(800)
    log("saved attire:", pg.evaluate("() => JSON.parse(localStorage.getItem('wh_attires_v1') || '{}').thor"))
    pg.screenshot(path=f"{OUT}/13-select-thor-attire2.png")
    pg.evaluate('() => document.querySelector(".char-card[data-id=demonio]")?.click()')
    pg.wait_for_timeout(1500)
    log("demonio chips:", pg.evaluate("() => document.querySelectorAll('.attire-chip').length"))
    log("demonio preview:", pg.evaluate("() => document.getElementById('preview-name').textContent"))
    pg.screenshot(path=f"{OUT}/14-select-demonio.png")
    log("PAGE ERRORS:", errs[:5] if errs else "none")
    b.close()
log("VERIFY DONE")
