#!/usr/bin/env python3
"""Proof-harness fight run (Python Playwright port of tools/proof-harness/fight.mjs).
Usage: proof.py OUTDIR P1 P2 [shots] [interval_ms]
Serves nothing itself — expects the repo root served on :8893.
Logs each fighter's state, attack, and CURRENT T3 CLIP NAME per sample; the
clip names carry the bank's provenance (row clips are named row:<t3_row>,
action clips t3_*), and the console log captures the game's own
"[WH] Fighter <id>: N real T3 actions from bank '<bank>'" binding lines."""
import sys, time, json
from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path(sys.argv[1]); p1, p2 = sys.argv[2], sys.argv[3]
n_shots = int(sys.argv[4]) if len(sys.argv) > 4 else 6
every = (int(sys.argv[5]) if len(sys.argv) > 5 else 700) / 1000.0
out.mkdir(parents=True, exist_ok=True)
logs = []

JS_STATE = """() => { const g = window.__game; if (!g || !g.p1) return null;
  const f = (x) => { const h = x.bones && x.bones.Hips, hd = x.bones && x.bones.Head;
    if (!h || !hd) return { id: x.char.id, model: x.char.model, bones: x.bones ? Object.keys(x.bones).slice(0,8) : [] };
    const a = new (h.position.constructor)(), b = new (h.position.constructor)();
    h.getWorldPosition(a); hd.getWorldPosition(b);
    return { id: x.char.id, model: x.char.model, st: x.state, atk: x.attackName,
             hipsY: +a.y.toFixed(2), headY: +b.y.toFixed(2),
             t3: x.t3actions ? Object.keys(x.t3actions).length : 0,
             cur: x._t3current && x._t3current._clip ? x._t3current._clip.name : null }; };
  return { p1: f(g.p1), p2: f(g.p2), round: g.roundState }; }"""

with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader',
                                  '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox', '--disable-dev-shm-usage', '--single-process'])
    pg = br.new_page(viewport={'width': 960, 'height': 540})
    pg.set_default_timeout(120000)
    pg.on('console', lambda m: logs.append(f'[{m.type}] {m.text}'))
    pg.on('pageerror', lambda e: logs.append(f'[pageerror] {e}'))
    pg.goto('http://127.0.0.1:8893/game/index.html?demo=1', wait_until='load')
    pg.wait_for_timeout(1500)
    try:
        pg.evaluate("() => window.__modes.startMode('arcade')")
    except Exception as e:
        logs.append('startMode err ' + str(e))
    pg.wait_for_timeout(1000)
    try:
        pg.evaluate("([a, b]) => window.__modes.startFight(a, b, { mode: 'arcade' })", [p1, p2])
    except Exception as e:
        logs.append('startFight err ' + str(e))
    # poll until the fight actually exists (slow under SwiftShader contention)
    for _ in range(60):
        try:
            ready = pg.evaluate("() => !!(window.__game && window.__game.p1 && window.__game.p2)")
        except Exception:
            ready = False
        if ready:
            break
        pg.wait_for_timeout(2000)
    logs.append('fight-ready poll done')
    cdp = br.contexts[0].new_cdp_session(pg) if br.contexts else None
    import base64
    pg.wait_for_timeout(4000)
    for i in range(n_shots):
        if i < n_shots - 1:
            try:
                st = pg.evaluate(JS_STATE)
            except Exception as e:
                st = {'error': str(e)[:120]}
            logs.append(f'STATE {i} ' + json.dumps(st))
            (out / 'console.log').write_text('\n'.join(logs))
            pg.wait_for_timeout(int(every * 1000))
            continue
        try:
            if cdp:
                r = cdp.send('Page.captureScreenshot', {'format': 'png'})
                (out / f'f{i:02d}.png').write_bytes(base64.b64decode(r['data']))
            else:
                pg.screenshot(path=str(out / f'f{i:02d}.png'), timeout=120000)
        except Exception as e:
            logs.append(f'shot {i} err ' + str(e)[:120])
        try:
            st = pg.evaluate(JS_STATE)
        except Exception as e:
            st = {'error': str(e)}
        logs.append(f'STATE {i} ' + json.dumps(st))
        (out / 'console.log').write_text('\n'.join(logs))  # incremental: survive timeouts
        pg.wait_for_timeout(int(every * 1000))
    br.close()
(out / 'console.log').write_text('\n'.join(logs))
print(f'{p1} vs {p2}: {n_shots} shots -> {out}')
