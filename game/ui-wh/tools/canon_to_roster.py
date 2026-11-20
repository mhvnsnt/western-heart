"""Extract real canon text per fighter from CANON.md -> game/ui-wh/roster_canon.json.
Run: python3 game/ui-wh/tools/canon_to_roster.py   (re-run whenever CANON.md changes; never hand-edit the json)."""
import json, re, pathlib
root = pathlib.Path(__file__).resolve().parents[3]
txt = (root / "CANON.md").read_text()
out, tier = {}, None
for blk in re.split(r"\n(?=## |### )", txt):
    h = blk.splitlines()[0]
    if h.startswith("## "):
        tier = {"2": "THE SEVEN", "3": "THE FOUR", "6": "THE TWELVE"}.get(h[3:4], tier); continue
    m = re.match(r"### (.+?) — (.+)", h)
    if not m: continue
    name, soul = m.group(1).strip(), m.group(2).strip()
    def field(label):
        f = re.search(r"\*\*" + label + r"[.:]?\*\*[.:]?\s*(.+)", blk)
        return f.group(1).strip() if f else ""
    phil = field("Fighting philosophy"); q = re.search(r"[\"“](.+?)[\"”]", phil)
    body = re.search(r"BODY:\s*(.+?)\.", blk)
    sub = blk.splitlines()[1].strip().strip("*") if len(blk.splitlines()) > 1 else ""
    t = "BOSS" if "Boss" in soul else ("THE HUNTER" if "Hunter" in soul else tier)
    out[name] = {"name": name, "soul": soul, "tier": t, "subtitle": sub,
                 "quote": q.group(1) if q else phil[:140], "element": field("Element").split(".")[0],
                 "body": body.group(1) if body else "", "signature": field("Signature detail"),
                 "owner_locked": field("Owner-locked"), "origin": "parts unknown"}
(root / "game/ui-wh/roster_canon.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(len(out), "fighters:", ", ".join(out))
