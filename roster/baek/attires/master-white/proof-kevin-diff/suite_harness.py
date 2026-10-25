"""Suite harness (rebuild): drives the REAL Creation Suite UI for Baek ->
Master White. The attire now has a committed customization.json, so the
suite's own per-attire restore fetches and applies it (morphs, parts,
colors). The harness then ALSO drives controls through the UI (slider input
events on face_oval/jaw_width, PARTS tab brow detail) to evidence the UI
path, captures the re-emitted customizationRecord(), and screenshots:
suite-full.png (BODY tab), suite-controls.png (slider close-up),
suite-brow.png (brow detail + placement dock).
Writes suite-report.json + suite-record.json next to this script.
"""
import json, threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[5]
OUT = ROOT / 'roster/baek/attires/master-white/proof-kevin-diff'
PORT = 8798
report = {"steps": [], "ok": False}
def step(name, ok, extra=None):
    report["steps"].append({"step": name, "ok": bool(ok), **(extra or {})})
    print(("PASS " if ok else "FAIL ") + name, extra or "")

httpd = ThreadingHTTPServer(("127.0.0.1", PORT), partial(SimpleHTTPRequestHandler, directory=str(ROOT)))
threading.Thread(target=httpd.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader",
                                 "--disable-dev-shm-usage", "--no-sandbox"])
    page = b.new_page(viewport={"width": 1280, "height": 800})
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto(f"http://127.0.0.1:{PORT}/customization/creation-suite-ui/index.html")
    page.wait_for_function("() => window.__suite && window.__suite.viewer && window.__suite.viewer.ready", timeout=90000)
    step("boot", True)

    page.evaluate("() => window.__suite.selectRosterAttire('baek','master-white')")
    page.wait_for_function(
        "() => window.__suite.viewer.currentUrl && window.__suite.viewer.currentUrl.includes('baek-master-white-rigged')",
        timeout=90000)
    step("roster-load", True, {"url": page.evaluate("() => window.__suite.viewer.currentUrl")})
    # per-attire restore of the committed customization.json
    try:
        page.wait_for_function("() => Math.abs((window.__suite.F.morphs||{}).jaw_width - (-0.5)) < 0.001", timeout=30000)
        step("restore-morphs", True, {"morphs": page.evaluate("() => window.__suite.F.morphs")})
    except Exception as e:
        step("restore-morphs", False, {"error": str(e)[:200],
               "morphs": page.evaluate("() => window.__suite.F.morphs")})
    equipped = page.evaluate("() => window.__suite.F.attires[window.__suite.F.attireIndex].equipped")
    step("restore-equipped", equipped, {"equipped": equipped})
    skin = page.evaluate("() => window.__suite.F.body.skin_tone")
    step("restore-skin", skin == "#dba06e", {"skin_tone": skin})

    # BODY tab screenshots (restored values visible)
    page.evaluate("() => window.__suite.setTab('body')")
    page.wait_for_timeout(600)
    page.screenshot(path=str(OUT / 'suite-full.png'))
    page.evaluate("() => { const e = document.querySelector('#morph-jaw_width'); if (e) e.scrollIntoView({block: 'center'}); }")
    page.wait_for_timeout(400)
    box = page.locator('#morph-jaw_width').bounding_box()
    page.screenshot(path=str(OUT / 'suite-controls.png'),
                    clip={"x": max(0, box["x"] - 20), "y": max(0, box["y"] - 260),
                          "width": 420, "height": 560} if box else None)
    step("screenshots-body", True)

    # Drive two sliders through real DOM input events (attempt-1 values and back)
    def set_slider(mid, val):
        page.evaluate("""([mid, val]) => {
          const inp = document.querySelector('#morph-' + mid + ' input[data-morph="' + mid + '"]');
          inp.focus(); inp.value = val;
          inp.dispatchEvent(new Event('input', {bubbles: true}));
          inp.dispatchEvent(new Event('change', {bubbles: true}));
        }""", [mid, val])
        page.wait_for_timeout(250)
        return page.evaluate(f"() => window.__suite.F.morphs['{mid}']")
    v1 = set_slider('face_oval', 0.45)
    v2 = set_slider('face_oval', 0.35)
    step("ui-slider-drive", abs(v1 - 0.45) < 0.011 and abs(v2 - 0.35) < 0.011,
         {"face_oval_set": v1, "face_oval_restored": v2})

    # PARTS tab: brow detail + placement dock (as in the original authoring run)
    page.evaluate("() => window.__suite.setTab('parts')")
    page.wait_for_function("() => !!document.querySelector('#pslot-6')", timeout=30000)
    page.evaluate("() => document.querySelector('#pslot-6').click()")
    page.wait_for_function("() => !!document.querySelector('#part-search')", timeout=30000)
    page.evaluate("""() => { const s = document.querySelector('#part-search');
        s.focus(); s.value = 'brow'; s.dispatchEvent(new Event('input', {bubbles: true})); }""")
    page.wait_for_function("() => !!document.querySelector('#part-brow-cc0-regular')", timeout=30000)
    page.evaluate("() => document.querySelector('#part-brow-cc0-regular').click()")
    page.wait_for_function("() => !!document.querySelector('#btn-equip-part') || !!document.querySelector('#place-dock')", timeout=30000)
    page.wait_for_timeout(600)
    page.screenshot(path=str(OUT / 'suite-brow.png'))
    step("parts-brow-panel", True)

    rec = page.evaluate("() => window.__suite.customizationRecord()")
    (OUT / 'suite-record.json').write_text(json.dumps(rec, indent=1))
    step("record-emit", bool(rec and rec.get('app') == 'wh-creation-suite'),
         {"morph_count": len(rec.get('morphs') or {}), "parts": list((rec.get('parts') or {}).keys()),
          "textures": len(rec.get('textures') or [])})
    report["page_errors"] = errs
    report["ok"] = all(s["ok"] for s in report["steps"])
    b.close()
httpd.shutdown()
(OUT / 'suite-report.json').write_text(json.dumps(report, indent=1))
print("REPORT ok:", report["ok"])
