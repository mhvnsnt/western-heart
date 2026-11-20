#!/usr/bin/env python3
"""Google Fonts (CSS2, no key) downloader for Western Heart (WH).

VERIFIED 2026-10-24 (live calls, no key, no account):
  - GET https://fonts.googleapis.com/css2?family=Bebas+Neue
        &family=Inter:wght@400;700&family=Oswald:wght@600;700&display=swap
    -> 200 CSS with @font-face blocks. With a plain (non-browser) UA the
    server returns TTF URLs; with a browser UA it returns WOFF2 URLs.
    This script therefore sends a browser UA and keeps only the LATIN
    unicode-range block per family/weight (css2 returns one block per
    script subset; keeping all of them would overwrite the same filename).
  - Fonts are OFL-licensed (check each family's OFL.txt on
    https://fonts.google.com). No API key exists for the css2 endpoint;
    the separate Google Fonts *Developer* API (metadata JSON) does need
    a key, but WH does not need it -- css2 + the google/fonts GitHub
    repo are enough.
  - WH picks (verified present in css2 on 2026-10-24):
      Bebas Neue 400  -- bold condensed display (fight UI, VS banners)
      Oswald 600,700  -- alternate bold display
      Inter 400,700   -- clean body / menus / movelist text

Usage:
  python3 google_fonts.py --out samples/fonts
  python3 google_fonts.py --families "Bebas Neue" "Inter:400;700" --out samples/fonts
Writes <Family>-<weight>.woff2 files + fonts.css with @font-face rules
and a <link> snippet. No credentials are read or sent.
"""
import argparse, os, re, urllib.request

CSS2 = "https://fonts.googleapis.com/css2"
BROWSER_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "Chrome/120 Safari/537.36")
DEFAULT = ["Bebas Neue", "Inter:400;700", "Oswald:600;700"]


def fetch_css(families):
    # Specs look like "Bebas Neue" or "Inter:400;700" (weights after ':').
    # css2 syntax needs family=Inter:wght@400;700 -- the ':wght@' part
    # was missing in v1 of this script and Google answered HTTP 400.
    parts = []
    for spec in families:
        if ":" in spec:
            name, weights = spec.split(":", 1)
            parts.append("family=" + name.replace(" ", "+") + ":wght@" + weights)
        else:
            parts.append("family=" + spec.replace(" ", "+"))
    qs = "&".join(parts)
    url = f"{CSS2}?{qs}&display=swap"
    req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode()


def latin_blocks(css):
    """Yield (family, weight, url) for latin-subset blocks only."""
    for block in re.findall(r"@font-face \{[^}]+\}", css):
        fam = re.search(r"font-family: '([^']+)'", block).group(1)
        weight = re.search(r"font-weight: (\d+)", block).group(1)
        url = re.search(r"url\((https://[^)]+)\)", block).group(1)
        urange = re.search(r"unicode-range: ([^;]+);", block)
        # Latin block is the one whose range starts at U+0000.
        if urange and "U+0000-00FF" not in urange.group(1):
            continue
        yield fam, weight, url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", nargs="*", default=DEFAULT)
    ap.add_argument("--out", default="samples/fonts")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    css = fetch_css(a.families)
    # Inter and Oswald are VARIABLE fonts: css2 returns the SAME woff2 URL
    # for weight 400 and 700 (verified 2026-10-24: identical latin URLs,
    # identical bytes). That is correct -- the browser interpolates the
    # weight from one variable file -- not a download bug. Group by URL
    # per family so we write one file per variable font, with a weight
    # range in the @font-face rule, instead of two identical files.
    grouped = {}
    for fam, weight, url in latin_blocks(css):
        grouped.setdefault((fam, url), []).append(int(weight))
    css_rules = []
    for (fam, url), weights in sorted(grouped.items()):
        weights = sorted(set(weights))
        if len(weights) > 1:
            fname = f"{fam.replace(' ', '')}-variable.woff2"
            weight_decl = f"{weights[0]} {weights[-1]}"
        else:
            fname = f"{fam.replace(' ', '')}-{weights[0]}.woff2"
            weight_decl = str(weights[0])
        req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            blob = r.read()
        with open(os.path.join(a.out, fname), "wb") as f:
            f.write(blob)
        print(f"{fname}\t{len(blob)} bytes\t{fam} weights={weights}"
              + (" (variable font: one file serves all listed weights)" if len(weights) > 1 else ""))
        css_rules.append(
            f"@font-face {{\n  font-family: '{fam}';\n  font-style: normal;\n"
            f"  font-weight: {weight_decl};\n  font-display: swap;\n"
            f"  src: url('./{fname}') format('woff2');\n}}")
    snippet = "\n\n".join(css_rules) + """

/* WH wiring (drop into the game's CSS, or use the hosted <link> instead):
   <link rel="preconnect" href="https://fonts.googleapis.com">
   <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
   <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;700&family=Oswald:wght@600;700&display=swap" rel="stylesheet">
   .wh-display { font-family: 'Bebas Neue', 'Oswald', sans-serif; }
   .wh-body    { font-family: 'Inter', system-ui, sans-serif; }
*/
"""
    with open(os.path.join(a.out, "fonts.css"), "w") as f:
        f.write(snippet)
    print(f"OK wrote {os.path.join(a.out, 'fonts.css')} "
          f"({len(grouped)} latin woff2 files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
