#!/usr/bin/env python3
"""proof.py — Creation Suite proof harness (pattern: packages/creation-suite/proof/shot.cjs).
Serves the repo root, drives the real suite UI with Playwright:
  Baek -> Master White loaded (real GLB) -> two morph sliders set (bulk,
  shoulders) -> a hair part equipped (mariposa ponytail GLB) -> screenshots.
Outputs in this folder: shot-full.png, shot-controls.png, report.json.
Run:  python3 customization/creation-suite-ui/proof-pass/proof.py
"""
import json
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PORT = 8791
URL = f"http://127.0.0.1:{PORT}/customization/creation-suite-ui/index.html"
HAIR_ID = "mariposa-hair-original-ponytail-roses"


def main() -> int:
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    report = {"url": URL, "steps": [], "errors": []}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.on("pageerror", lambda e: report["errors"].append(f"pageerror: {e}"))
            page.on("console", lambda m: report["errors"].append(f"console.error: {m.text}") if m.type == "error" else None)
            page.goto(URL)
            page.wait_for_function("() => window.__suite && window.__suite.viewer && window.__suite.viewer.ready", timeout=60000)
            report["steps"].append("boot: blank fighter loaded")

            # 1) Roster mode: Baek -> Master White (real GLB)
            page.evaluate("() => window.__suite.selectRosterAttire('baek', 'master-white')")
            page.wait_for_function(
                "() => window.__suite.viewer.currentUrl && window.__suite.viewer.currentUrl.includes('baek-master-white-rigged') && window.__suite.viewer.model",
                timeout=60000)
            state = page.evaluate("() => ({ mode: __suite.F.mode, ref: __suite.F.rosterRef, baseGlb: __suite.F.baseGlb, url: __suite.viewer.currentUrl, name: __suite.F.profile.name })")
            report["roster"] = state
            assert state["mode"] == "roster" and state["ref"]["attire"] == "master-white", state
            report["steps"].append(f"roster: Baek -> Master White loaded ({state['url']})")

            # 2) Two morph sliders set on the BODY tab (real UI inputs)
            page.evaluate("() => window.__suite.setTab('body')")
            page.wait_for_function("() => !!document.querySelector('input[data-morph=\"bulk\"]')", timeout=30000)
            for morph, val in [("bulk", "0.6"), ("shoulders", "0.35")]:
                page.evaluate("""([id, v]) => { const el = document.querySelector(`input[data-morph="${id}"]`);
                    el.value = v; el.dispatchEvent(new Event('input', { bubbles: true })); }""", [morph, val])
            morphs = page.evaluate("() => ({ bulk: __suite.F.morphs.bulk, shoulders: __suite.F.morphs.shoulders })")
            report["morphs"] = morphs
            assert morphs["bulk"] == 0.6 and morphs["shoulders"] == 0.35, morphs
            report["steps"].append(f"morphs set: {morphs}")
            page.evaluate("() => document.querySelector('#morph-bulk').scrollIntoView({ block: 'start' })")
            page.wait_for_timeout(300)
            page.screenshot(path=str(OUT / "shot-controls.png"), clip={"x": 908, "y": 0, "width": 372, "height": 800})
            report["steps"].append("shot-controls.png: right-rail BODY morph controls close-up (bulk slider in view)")

            # 3) Hair part equipped via PARTS tab (T7 slot 2 -> search -> tap card -> equip)
            page.evaluate("() => window.__suite.setTab('parts')")
            page.wait_for_function("() => !!document.querySelector('#pslot-2')", timeout=30000)
            page.evaluate("() => document.querySelector('#pslot-2').click()")
            page.wait_for_function("() => !!document.querySelector('#part-search')", timeout=30000)
            page.evaluate("() => { const s = document.querySelector('#part-search'); s.focus(); }")
            page.keyboard.type("ponytail")
            page.wait_for_function(f"() => !!document.querySelector('#part-{HAIR_ID}')", timeout=30000)
            page.evaluate(f"() => document.querySelector('#part-{HAIR_ID}').click()")
            page.wait_for_function("() => !!document.querySelector('#btn-equip-part')", timeout=30000)
            page.evaluate("() => document.querySelector('#btn-equip-part').click()")
            page.wait_for_function(f"() => window.__suite.viewer.parts.has('{HAIR_ID}')", timeout=30000)
            equipped = page.evaluate("() => ({ equipped: __suite.F.attires[__suite.F.attireIndex].equipped, parts: [...__suite.viewer.parts.keys()] })")
            report["equipped"] = equipped
            assert HAIR_ID in equipped["parts"], equipped
            report["steps"].append(f"hair part equipped in viewer: {HAIR_ID}")

            # 4) Full-suite shot: close the placement dock and pull the camera
            # back so the fighter is full-body and no panel covers him.
            page.evaluate("() => document.querySelector('#pd-close').click()")
            page.evaluate("() => { const v = __suite.viewer; v.camDist = (v.headHeight || 1.7) * 3.6; v.theta = 0.35; }")
            page.wait_for_timeout(600)
            page.screenshot(path=str(OUT / "shot-full.png"))
            report["record_key"] = page.evaluate("() => window.__suite.currentKey()")
            report["record"] = page.evaluate("() => window.__suite.customizationRecord()")
            report["parts_total"] = page.evaluate("() => window.__suite.PARTS.length")
            assert report["record"]["fighter"] == "baek" and report["record"]["attire"] == "master-white", report["record"]
            assert report["record"]["morphs"].get("bulk") == 0.6, report["record"]
            assert any(v.get("part_id") == HAIR_ID for v in report["record"]["parts"].values()), report["record"]
            report["steps"].append("shot-full.png: full suite, fighter full-body")
            browser.close()
    finally:
        httpd.shutdown()
    report["ok"] = not report["errors"]
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
