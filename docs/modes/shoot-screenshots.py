"""Stream 4 visual proof rig: screenshots of menus, overlays, VS, story cards.
Usage: serve game/ on PORT (default 8902), then: python3 docs/modes/shoot-screenshots.py
Output: docs/modes/shots/*.png
"""
import os, sys
from playwright.sync_api import sync_playwright

PORT = int(os.environ.get("PORT", "8902"))
BASE = f"http://127.0.0.1:{PORT}/index.html"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")
os.makedirs(OUT, exist_ok=True)

def shot(page, name):
    import base64
    p = os.path.join(OUT, name + ".png")
    session = page.context.new_cdp_session(page)
    data = session.send("Page.captureScreenshot", {"format": "png"})["data"]
    with open(p, "wb") as f:
        f.write(base64.b64decode(data))
    print("shot:", p, flush=True)

def click_action(page, action):
    page.evaluate(f"""() => {{
      document.querySelector('[data-action="{action}"]').click();
    }}""")

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    pg.goto(BASE, wait_until="networkidle")
    pg.wait_for_timeout(2500)
    # dismiss tap-to-start so it never intercepts
    pg.evaluate("() => document.getElementById('tap-to-start').classList.remove('show')")

    shot(pg, "01-menu")

    click_action(pg, "mode-options")
    pg.wait_for_timeout(600)
    shot(pg, "02-options")

    pg.evaluate("""() => document.querySelector('#wh-options [data-wh="back"]').click()""")
    pg.wait_for_timeout(300)
    click_action(pg, "mode-records")
    pg.wait_for_timeout(600)
    shot(pg, "03-records")
    pg.evaluate("""() => document.querySelector('#wh-records [data-wh="back"]').click()""")
    pg.wait_for_timeout(300)

    # VS screen (same DOM the startMatch hook fills)
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

    # story dialogue card
    pg.evaluate("""() => {
      const o = document.getElementById('wh-story');
      o.querySelector('.wh-story-kicker').textContent = 'DEMONIO — DESCENT OF THE APOLOGY';
      o.querySelector('.wh-story-name').textContent = 'DEMONIO';
      o.querySelector('.wh-story-text').textContent = 'Then I will descend as I fight: precisely. If there is a sin I am atoning for, I will find it, name it, and put it down.';
      const img = o.querySelector('.sportrait img');
      img.src = 'assets/portraits/demonio.png';
      img.onerror = () => img.style.display = 'none';
      o.querySelector('.wh-story-hint').textContent = 'TAP TO CONTINUE · 2/3';
      o.classList.add('show');
    }""")
    pg.wait_for_timeout(500)
    shot(pg, "05-story")
    pg.evaluate("""() => document.getElementById('wh-story').classList.remove('show')""")

    # loading overlay
    pg.evaluate("""() => {
      const o = document.getElementById('wh-loading');
      o.querySelector('.wh-load-status').textContent = 'DESCENDING…';
      o.querySelector('.wh-load-fill').style.width = '42%';
      o.classList.add('show');
    }""")
    pg.wait_for_timeout(500)
    shot(pg, "06-loading")
    pg.evaluate("""() => document.getElementById('wh-loading').classList.remove('show')""")

    # pause overlay
    pg.evaluate("""() => document.getElementById('wh-pause').classList.add('show')""")
    pg.wait_for_timeout(400)
    shot(pg, "07-pause")
    pg.evaluate("""() => document.getElementById('wh-pause').classList.remove('show')""")

    # heartmind select flow
    click_action(pg, "mode-heartmind")
    pg.wait_for_timeout(800)
    shot(pg, "08-heartmind-select")

    # episodes select flow
    click_action(pg, "back-menu")
    pg.wait_for_timeout(400)
    click_action(pg, "mode-episodes")
    pg.wait_for_timeout(800)
    shot(pg, "09-episodes-select")

    print("PAGE ERRORS:", errs[:5] if errs else "none")
    b.close()
print("DONE")
