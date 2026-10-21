import sys, base64
from pathlib import Path
from playwright.sync_api import sync_playwright
out = Path(sys.argv[1]); p1, p2 = sys.argv[2], sys.argv[3]
out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox', '--disable-dev-shm-usage', '--single-process'])
    pg = br.new_page(viewport={'width': 960, 'height': 540})
    pg.set_default_timeout(120000)
    pg.goto('http://127.0.0.1:8893/game/index.html?demo=1', wait_until='load')
    pg.wait_for_timeout(1500)
    pg.evaluate("() => window.__modes.startMode('arcade')")
    pg.wait_for_timeout(800)
    pg.evaluate("([a, b]) => window.__modes.startFight(a, b, { mode: 'arcade' })", [p1, p2])
    for _ in range(45):
        try:
            ready = pg.evaluate("() => !!(window.__game && window.__game.p1 && window.__game.roundState === 'fight')")
        except Exception:
            ready = False
        if ready: break
        pg.wait_for_timeout(2000)
    pg.wait_for_timeout(2500)
    cdp = br.contexts[0].new_cdp_session(pg)
    r = cdp.send('Page.captureScreenshot', {'format': 'png'})
    (out / 'fight-front.png').write_bytes(base64.b64decode(r['data']))
    print('shot saved', out)
    br.close()
