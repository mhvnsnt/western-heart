"""Capture remaining shots: fixed VS, episodes select, scrolled menu."""
import os, base64
from playwright.sync_api import sync_playwright

PORT = int(os.environ.get("PORT", "8904"))
BASE = f"http://127.0.0.1:{PORT}/index.html"
OUT = "/home/hatch/workspace/wt-stream4/docs/modes/shots"

def shot(page, name):
    p = os.path.join(OUT, name + ".png")
    session = page.context.new_cdp_session(page)
    data = session.send("Page.captureScreenshot", {"format": "png"})["data"]
    with open(p, "wb") as f:
        f.write(base64.b64decode(data))
    print("shot:", p, flush=True)

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    pg.goto(BASE, wait_until="networkidle")
    pg.wait_for_timeout(2500)
    pg.evaluate("() => document.getElementById('tap-to-start').classList.remove('show')")

    # scrolled menu showing new buttons
    pg.evaluate("""() => {
      const mc = document.querySelector('#screen-menu .menu-content');
      mc.scrollTop = mc.scrollHeight;
    }""")
    pg.wait_for_timeout(500)
    shot(pg, "10-menu-scrolled")

    # fixed VS layout
    pg.evaluate("""() => {
      const o = document.getElementById('wh-vs');
      o.querySelector('.wh-vs-inner').innerHTML = `
        <div class="wh-vs-card left">
          <div class="portrait"><img src="assets/portraits/demonio.png" onerror="this.style.display='none'"></div>
          <div class="vname">DEMONIO</div><div class="vtitle">The Demon Soul</div>
        </div>
        <div class="wh-vs-mid"><div class="vsburst">VS</div><div class="vsstage">SHRINE OF THE BLADE</div></div>
        <div class="wh-vs-card right">
          <div class="portrait"><img src="assets/portraits/diablo.png" onerror="this.style.display='none'"></div>
          <div class="vname">DIABLO</div><div class="vtitle">The Devil Soul</div>
        </div>`;
      o.querySelector('.wh-vs-mode').textContent = 'THE HEART AND MIND INSIDE';
      o.classList.add('show');
    }""")
    pg.wait_for_timeout(700)
    shot(pg, "04-vs")
    pg.evaluate("""() => document.getElementById('wh-vs').classList.remove('show')""")

    # episodes select
    pg.evaluate("""() => document.querySelector('[data-action="mode-episodes"]').click()""")
    pg.wait_for_timeout(800)
    shot(pg, "09-episodes-select")

    print("PAGE ERRORS:", errs[:5] if errs else "none")
    b.close()
print("DONE")
