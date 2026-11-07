#!/usr/bin/env python3
"""Fetch + parse a wavu.wiki movelist page (CC0-1.0) into move rows.

wavu.wiki's Cargo table only covers Tekken 8, so older-game movelists (Tag 2, Tekken 5/DR,
Tekken 6) are read from the page wikitext: every {{Move2|...}} / {{Move5|...}} / {{Move6|...}}
template becomes one row with its fields verbatim (id, parent, input, name, alt, target,
damage, startup, block, hit, ch, crush, recv, notes). Inline icon templates are expanded to
their words ({{BB}} -> Balcony Break, {{Plainlist|* a * b}} -> "a; b"); nothing else is changed.
`input_full` / `damage_full` / `target_full` join a string's parent chain (wavu stores each
string hop as ",3" under its parent).

The page API is reachable with a plain HTTP client; the /t/ HTML pages sit behind a bot wall.

Usage:
  python3 tools/frame-data/wavu_movelist_wikitext.py "Roger Jr. movelist (Tag 2)" OUT.json
"""
import json, sys, urllib.parse, urllib.request
import re
ICON = {'BB': 'Balcony Break', 'TB': 'Tag Buffer', 'Spike': 'Spike', 'Homing': 'Homing', 'Bound': 'Bound',
        'FB': 'Floor Break', 'Elbow': 'Elbow', 'Head': 'Head', 'Shoulder': 'Shoulder', 'Knee': 'Knee',
        'WB': 'Wall Break', 'WS': 'Wall Splat', 'Tornado': 'Tornado', 'Heat': 'Heat', 'PC': 'Power Crush'}

def _templates(text, prefix):
    i = 0
    while True:
        j = text.find('{{' + prefix, i)
        if j < 0: return
        depth, k = 0, j
        while k < len(text):
            if text.startswith('{{', k): depth += 1; k += 2; continue
            if text.startswith('}}', k):
                depth -= 1; k += 2
                if depth == 0: break
                continue
            k += 1
        yield text[j + 2:k - 2]
        i = k

def _split_top(body):
    parts, depth, cur, k = [], 0, [], 0
    while k < len(body):
        if body.startswith('{{', k): depth += 1; cur.append('{{'); k += 2; continue
        if body.startswith('}}', k): depth -= 1; cur.append('}}'); k += 2; continue
        c = body[k]
        if c == '|' and depth == 0: parts.append(''.join(cur)); cur = []
        else: cur.append(c)
        k += 1
    parts.append(''.join(cur))
    return parts

def clean(v):
    v = v.replace('&ZeroWidthSpace;', '').replace('\u200b', '')
    def rep(m):
        inner = m.group(1)
        name, _, rest = inner.partition('|')
        name = name.strip()
        if name in ('Plainlist', 'Dotlist'):
            items = [re.sub(r'^\s*\*\s*', '', l).strip() for l in rest.splitlines() if l.strip().startswith('*')]
            return '; '.join(i for i in items if i)
        if name == 'MoveDataIcon':
            segs = [s for s in rest.split('|') if '=' not in s]
            return segs[-1].strip() if segs else ''
        return ICON.get(name, name)
    for _ in range(4):
        nv = re.sub(r'\{\{([^{}]*)\}\}', rep, v)
        if nv == v: break
        v = nv
    v = re.sub(r"'''?|\[\[|\]\]", '', v)
    return re.sub(r'\s+', ' ', v).strip()

def parse(text, prefix='Move'):
    rows = []
    for body in _templates(text, prefix):
        parts = _split_top(body)
        tname = parts[0].strip()
        if not re.match(r'^Move\d*$', tname): continue
        row = {}
        for p in parts[1:]:
            if '=' not in p: continue
            k, _, v = p.partition('=')
            row[k.strip()] = clean(v)
        if row.get('id'): rows.append(row)
    return rows

def full_inputs(rows):
    byid = {r['id']: r for r in rows}
    for r in rows:
        chain, p, g = [r.get('input', '')], r.get('parent'), 0
        while p and p in byid and g < 15:
            chain.insert(0, byid[p].get('input', '')); p = byid[p].get('parent'); g += 1
        r['input_full'] = ''.join(chain).strip().lstrip(',')
        # damage/target of strings carry a leading comma for the new hit; full chain too
        dmg, tgt, p, g = [r.get('damage', '')], [r.get('target', '')], r.get('parent'), 0
        while p and p in byid and g < 15:
            dmg.insert(0, byid[p].get('damage', '')); tgt.insert(0, byid[p].get('target', '')); p = byid[p].get('parent'); g += 1
        r['damage_full'] = ''.join(dmg).strip(',')
        r['target_full'] = ''.join(tgt).strip(',')
    return rows


API = "https://wavu.wiki/w/api.php"


def fetch(title):
    q = {"action": "query", "prop": "revisions", "rvprop": "content|ids|timestamp", "rvslots": "main",
         "format": "json", "redirects": "1", "titles": title}
    r = urllib.request.Request(API + "?" + urllib.parse.urlencode(q), headers={"User-Agent": "WH-reference/1.0"})
    d = json.load(urllib.request.urlopen(r, timeout=60))
    page = next(iter(d["query"]["pages"].values()))
    rev = page["revisions"][0]
    return page["title"], rev["revid"], rev["timestamp"], rev["slots"]["main"]["*"]


def build(title):
    real, revid, ts, text = fetch(title)
    rows = full_inputs(parse(text))
    url = "https://wavu.wiki/t/" + real.replace(" ", "_")
    return {"source": url, "permalink": f"https://wavu.wiki/w/index.php?title={urllib.parse.quote(real.replace(' ', '_'))}&oldid={revid}",
            "page_title": real, "revid": revid, "revision_timestamp": ts, "license": "CC0-1.0 (wavu.wiki)",
            "parser": "tools/frame-data/wavu_movelist_wikitext.py", "moves": rows}


if __name__ == "__main__":
    doc = build(sys.argv[1])
    open(sys.argv[2], "w").write(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    print(sys.argv[2], len(doc["moves"]), "moves, revid", doc["revid"])
