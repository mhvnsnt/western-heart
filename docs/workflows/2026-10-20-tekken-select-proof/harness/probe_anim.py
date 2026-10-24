#!/usr/bin/env python3
"""Probe: is the select preview actually animating? Samples the pane
internals (model rotation, mixer time, action states) twice, 3s apart."""
import json, threading, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

ROOT = "/home/hatch/workspace/_wh-work/select-screen"
handler = functools.partial(SimpleHTTPRequestHandler, directory=ROOT)
httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
PORT = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{PORT}/game/"
print("SERVER", BASE, flush=True)

SAMPLE = """() => {
  const ss = window.__selectScreen;
  if (!ss) return { err: 'no hook' };
  const pane = ss._panes.p1;
  const out = { hasStance: pane.hasStance, loading: pane._loading,
    failed: pane.failed, hasModel: !!pane.model,
    rotY: pane.model ? pane.model.rotation.y : null,
    mixerTime: null, actions: null };
  if (pane.mixer) {
    out.mixerTime = pane.mixer.time;
    out.actions = {};
    // walk the mixer's actions via its stats? use _actions internal
    const acts = pane.mixer._actions || [];
    for (const a of acts) {
      const clip = a.getClip();
      out.actions[clip.name] = { t: +a.time.toFixed(2), w: a.getEffectiveWeight(), running: a.isRunning() };
    }
  }
  return out; }"""

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=[
        "--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader",
        "--no-sandbox", "--disable-dev-shm-usage", "--mute-audio",
        "--single-process", "--no-zygote", "--js-flags=--max-old-space-size=1536"])
    pg = b.new_page(viewport={"width": 390, "height": 844})
    msgs = []
    pg.on("console", lambda m: msgs.append(m.text[:160]) if "WH" in m.text else None)
    pg.goto(BASE, wait_until="domcontentloaded", timeout=90000)
    pg.wait_for_function("() => !!window.__modes", timeout=120000)
    pg.evaluate("() => document.querySelector('[data-action=\"mode-versus\"]').click()")
    pg.wait_for_selector('#screen-select.active', timeout=30000)
    pg.evaluate("() => document.querySelector('.char-card[data-id=\"demonio\"]').click()")
    for _ in range(60):
        st = pg.evaluate("() => { const n = document.querySelector('#pane-p1 .pane-note'); return n.hidden; }")
        if st:
            break
        pg.wait_for_timeout(1000)
    print("SAMPLE 1:", json.dumps(pg.evaluate(SAMPLE), indent=1), flush=True)
    pg.wait_for_timeout(3000)
    print("SAMPLE 2:", json.dumps(pg.evaluate(SAMPLE), indent=1), flush=True)
    print("WH LOGS:", json.dumps(msgs[:10], indent=1), flush=True)
    b.close()
