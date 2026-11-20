"""Functional test: heartmind select -> story -> fight dispatch (stubbed)."""
import sys
from playwright.sync_api import sync_playwright

PORT = sys.argv[1] if len(sys.argv) > 1 else "8907"
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
    pg = b.new_page(viewport={"width": 390, "height": 844})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    pg.goto(f"http://127.0.0.1:{PORT}/index.html", wait_until="networkidle")
    pg.wait_for_timeout(2500)
    pg.evaluate("() => document.getElementById('tap-to-start').classList.remove('show')")
    pg.evaluate("""() => {
      window.__fightCalls = [];
      const hm = window.__heartmind;
      hm.startFight = (p1, p2, opts) => {
        window.__fightCalls.push({p1, mode: opts.mode, stage: opts.stage,
          foe: opts.enemyChar.name, rtw: opts.roundsToWin, hpCarry: opts.hpCarry});
      };
    }""")
    pg.evaluate('() => document.querySelector("[data-action=mode-heartmind]").click()')
    pg.wait_for_timeout(400)
    print("mode:", pg.evaluate("() => window.__modes.mode"), flush=True)
    pg.evaluate('() => document.querySelector(".char-card[data-id=demonio]").click()')
    pg.wait_for_timeout(300)
    pg.evaluate('() => document.getElementById("confirm-fighter").click()')
    pg.wait_for_timeout(600)
    print("story shown:", pg.evaluate("() => document.getElementById('wh-story').classList.contains('show')"), flush=True)
    print("kicker:", pg.evaluate("() => document.querySelector('.wh-story-kicker').textContent"), flush=True)
    for _ in range(3):
        pg.evaluate("() => document.getElementById('wh-story').click()"); pg.wait_for_timeout(250)
    pg.wait_for_timeout(400)
    print("stage kicker:", pg.evaluate("() => document.querySelector('.wh-story-kicker').textContent"), flush=True)
    for _ in range(3):
        pg.evaluate("() => document.getElementById('wh-story').click()"); pg.wait_for_timeout(250)
    pg.wait_for_timeout(600)
    print("fight calls:", pg.evaluate("() => JSON.stringify(window.__fightCalls)"), flush=True)
    print("ERRORS:", errs[:5] if errs else "none", flush=True)
    b.close()
print("TEST DONE", flush=True)
