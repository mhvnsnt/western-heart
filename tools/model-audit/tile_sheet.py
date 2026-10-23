#!/usr/bin/env python3
"""tools/model-audit/tile_sheet.py — tile rig_sheet.mjs renders into labelled contact sheets.

    python3 tools/model-audit/tile_sheet.py SWEEP_DIR OUT_PREFIX [--kind rest|stance] [--per 12] [--cols 6]

Reads SWEEP_DIR/results.json (written by tools/proof-harness/rig_sheet.mjs) and SWEEP_DIR/<kind>_<key>.png,
writes OUT_PREFIX_<n>.png. Each tile is labelled with the model key and the facing the game applied
(+Z / -Z TURNED) so a back-facing rest render can be traced to its facing decision.
"""
import json
import os
import sys

from PIL import Image, ImageDraw


def main():
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    opt = lambda k, d: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    sweep, prefix = a[0], a[1]
    kind, per, cols = opt("--kind", "rest"), int(opt("--per", "12")), int(opt("--cols", "6"))
    res = json.load(open(os.path.join(sweep, "results.json")))
    tiles = [r for r in res if os.path.exists(os.path.join(sweep, f"{kind}_{r['key']}.png"))]
    tw, th = (200, 320) if kind == "rest" else (200, 300)
    for n in range(0, len(tiles), per):
        chunk = tiles[n:n + per]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw, rows * (th + 30)), (20, 20, 28))
        d = ImageDraw.Draw(sheet)
        for i, r in enumerate(chunk):
            im = Image.open(os.path.join(sweep, f"{kind}_{r['key']}.png")).convert("RGB")
            im.thumbnail((tw, th))
            x, y = (i % cols) * tw, (i // cols) * (th + 30)
            sheet.paste(im, (x + (tw - im.width) // 2, y + 30))
            fac = {1: "+Z", -1: "-Z TURNED"}.get(r.get("facing"), "?")
            d.text((x + 4, y + 2), r["key"][:30], fill=(255, 255, 255))
            d.text((x + 4, y + 15), f"{fac} swapLR={r.get('swapLR')}", fill=(255, 200, 120))
        out = f"{prefix}_{n // per}.png"
        sheet.save(out)
        print(out, [r["key"] for r in chunk])


if __name__ == "__main__":
    main()
