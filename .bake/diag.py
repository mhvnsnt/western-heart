import json
from playwright.sync_api import sync_playwright
logs = []
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'])
    pg = br.new_page(viewport={'width': 800, 'height': 450})
    pg.set_default_timeout(60000)
    pg.on('console', lambda m: logs.append(f'[{m.type}] {m.text[:200]}'))
    pg.on('pageerror', lambda e: logs.append(f'[pageerror] {str(e)[:200]}'))
    pg.goto('http://127.0.0.1:8893/game/index.html?demo=1', wait_until='load')
    pg.wait_for_timeout(3000)
    print('__modes:', pg.evaluate("() => window.__modes ? Object.keys(window.__modes) : null"))
    print('__game:', pg.evaluate("() => window.__game ? Object.keys(window.__game).slice(0,10) : null"))
    r = pg.evaluate("() => { try { window.__modes.startMode('arcade'); return 'startMode ok'; } catch(e) { return 'ERR ' + e.message; } }")
    print(r)
    pg.wait_for_timeout(2000)
    r = pg.evaluate("() => { try { const p = window.__modes.startFight('docfrank', 'pantera', { mode: 'arcade' }); return 'startFight called: ' + (p && p.constructor ? p.constructor.name : typeof p); } catch(e) { return 'ERR ' + e.message; } }")
    print(r)
    for i in range(10):
        pg.wait_for_timeout(2000)
        g = pg.evaluate("() => window.__game ? { p1: !!window.__game.p1, round: window.__game.roundState } : null")
        print('poll', i, g)
        if g and g.get('p1'):
            break
    br.close()
print('\n'.join(logs[-25:]))
