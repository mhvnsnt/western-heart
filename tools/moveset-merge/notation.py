#!/usr/bin/env python3
"""One Tekken notation for every move source in Western Heart.

The sources write the same input four different ways:
  T8 wavu.wiki (id path) : 'Eddy-df+1,3', 'ws1', 'FC.df+4', 'H.2+3', 'R.df+1+2', 'f,F+2', 'b+1+2*'
  T7 t7chicken           : '(d/f+1), 3', 'WS 1', 'FC d/f+4', 'BT 1 (or 2)', '(During Rage) d/f+1+2',
                           'Approach enemy... 1+3', 'f, F+2'
  T3 decoded banks       : 'd/f+1,3', 'f,F+2', 'd,d/f,f+1' (tools/gen-movesets-t3.py)
  WH files               : 'd/f+1', '1,2', 'qcf+2', 'S', 'P+K' (legacy WH buttons)
`canon()` maps all of them to the WH notation game/js/movesets.js resolves:
  tokens joined by ',' (no spaces); a token is [STANCE.]*[dir][+buttons][suffix]
  dirs f b u d d/f d/b u/f u/b (tap) and F B U D D/F D/B U/F U/B (hold)
  buttons 1-4 sorted inside a chord; '*' hold, '~' immediate, ':' just-frame kept
  universal states WS. FC. SS. BT. WR. H. (heat) R. (rage) + character stance codes (SNK. DRG. ...)
It returns (notation, note): notation None when the row is a description the engine cannot
key (e.g. 'Face Up, Feet Towards+3'); the row is still imported, just not auto-slotted.

game/js/movesets.js canonNotation() is the JavaScript twin; tests/notation_cases.json holds the
shared cases both must agree on.
"""
import html
import re

DIR_WAVU = {"df": "d/f", "db": "d/b", "uf": "u/f", "ub": "u/b", "DF": "D/F", "DB": "D/B", "UF": "U/F", "UB": "U/B"}
DIRS = {"f", "b", "u", "d", "d/f", "d/b", "u/f", "u/b", "n", "F", "B", "U", "D", "D/F", "D/B", "U/F", "U/B", "N",
        "qcf", "qcb", "hcf", "hcb", "f,F"}
STATE_ALIASES = {"ws": "WS", "fc": "FC", "ss": "SS", "bt": "BT", "wr": "WR", "fcd/f": "FC"}
# t7chicken descriptive prefixes -> state prefix ('' = plain input, None = not keyable)
DESCR = [
    (r"^\(during rage\)\s*", "R."),
    (r"^during rage\s*", "R."),
    (r"^approach enemy\.\.\.\s*", ""),
    (r"^while enemy is down\.\.\.\s*", "OTG."),
    (r"^while opponent is down\.\.\.\s*", "OTG."),
    (r"^back towards wall\.\.\.\s*", "WALL."),
    (r"^\(back to wall\)\.?\s*", "WALL."),
    (r"^back to wall\.\.\.\s*", "WALL."),
    (r"^time with high enemy attack\.\.\.\s*", "REV."),
    (r"^time with mid enemy attack\.\.\.\s*", "REV."),
    (r"^time with low enemy attack\.\.\.\s*", "REV."),
    (r"^time with enemy attack\.\.\.\s*", "REV."),
    (r"^\(during heat\)\s*", "H."),
    (r"^approach from behind\.\.\.\s*", "BACK."),
    (r"^approach from (?:the )?left(?: side)?\.\.\.\s*", "SIDE_L."),
    (r"^approach from (?:the )?right(?: side)?\.\.\.\s*", "SIDE_R."),
    (r"^approach \(crouching enemy\)\s*", "CROUCHING."),
    (r"^approach mid-air enemy\.\.\.\s*", "AIR."),
    (r"^face up, feet towards,?\s*\+?", "FUFT."),
    (r"^face up, feet away,?\s*\+?", "FUFA."),
    (r"^face down, feet towards,?\s*\+?", "FDFT."),
    (r"^face down, feet away,?\s*\+?", "FDFA."),
    (r"^held jump\s*\+?", "JUMP."),
    (r"^jump,\s*", "JUMP."),
    (r"^wr\s*\+", "WR."),
    (r"^wr\s+", "WR."),  # 'WR 4' is while-running 4, never plain 4 (game canonNotation: 'WR.4'; 2026-11-01)
]
# wavu ids that name a throw by side instead of an input
NAMED = {"left throw": "SIDE_L.1+3", "right throw": "SIDE_R.2+4", "back throw": "BACK.1+3"}
QUALIFIER = re.compile(r"\((?:or [^)]*|while [^)]*|full screen|hold|when [^)]*|close range|on hit|on block|during [^)]*|can be [^)]*|cancel[^)]*|\d+ ?hits?|input [^)]*|tap|mash[^)]*|[^)]*enemy[^)]*|[^)]*opponent[^)]*|[^)]*guard[^)]*|[^)]*wall[^)]*|[^)]*hits? only[^)]*|close|far|\d+f|second [^)]*|first [^)]*)\)", re.I)
BTN_TOKEN = re.compile(r"^(?:(?P<pre>(?:[A-Za-z][A-Za-z0-9]*\.)*))(?P<dir>[fbudnFBUDN](?:/[fbFB])?|qcf|qcb|hcf|hcb)?(?:\+?(?P<btn>[1-4](?:\+[1-4])*))?(?P<suf>[*~:]*)$")


def _dir(d):
    return DIR_WAVU.get(d, d)


def _token(t):
    """Canonicalize one comma-separated token. Returns None if it is not notation."""
    t = t.strip()
    if not t:
        return None
    t = t.replace(" ", "")
    # wavu compact state forms: ws1 ss2 wr3 -> WS.1 / FC.df+1 keeps its dot
    m = re.match(r"^(ws|ss|wr|fc|bt)\+?(?=[1-4udfb])", t, re.I)
    if m and not t[len(m.group(0)):].startswith("."):
        t = STATE_ALIASES[m.group(1).lower()] + "." + t[len(m.group(0)):]
    # state prefixes like 'WS.' 'FC.' 'SNK.' 'H.' 'R.' ; normalise known aliases' case
    parts = t.split(".")
    pre, body = parts[:-1], parts[-1]
    pre = [STATE_ALIASES.get(p.lower(), p) if p.lower() in STATE_ALIASES else p for p in pre]
    # direction spelled wavu-style (df+1, DF+1, uf, ub)
    body = re.sub(r"^(df|db|uf|ub|DF|DB|UF|UB)(?=$|\+|\*)", lambda x: _dir(x.group(1)), body)
    # buttons sorted inside a chord, direction first
    m = re.match(r"^(?P<dir>(?:[fbudnFBUDN](?:/[fbFB])?)|qcf|qcb|hcf|hcb)?(?P<rest>.*)$", body)
    d, rest = m.group("dir") or "", m.group("rest")
    suf = ""
    while rest and rest[-1] in "*~":
        suf = rest[-1] + suf
        rest = rest[:-1]
    if rest.startswith("+"):
        rest = rest[1:]
    if rest and not re.fullmatch(r"[1-4](\+[1-4])*", rest):
        return None
    btn = "+".join(sorted(rest.split("+"))) if rest else ""
    if not d and not btn:
        return None
    tok = d + ("+" if d and btn else "") + btn + suf
    return ".".join(pre + [tok]) if pre else tok


def canon(raw):
    """-> (notation | None, note). See module docstring."""
    if raw is None:
        return None, "empty"
    # scraped rows can be escaped twice ('1,2,&amp;#58;4' is '1,2,:4'): unescape until stable
    s = str(raw)
    for _ in range(3):
        u = html.unescape(s)
        if u == s:
            break
        s = u
    s = s.strip()
    note = ""
    prefix = ""
    low = s.lower()
    for pat, pre in DESCR:
        m = re.match(pat, low)
        if m:
            prefix = pre
            note = s[:m.end()].strip()
            s = s[m.end():]
            low = s.lower()
            break
    # alternatives: 'AIR.1+3 / AIR.f+1+3', 'RAS1.1_2', '1+3 (or 2+4)' -> first
    s = s.split(" / ")[0]
    if s.lower() in NAMED:
        return NAMED[s.lower()], note
    m = re.match(r"^\(during ([^)]+)\)\s*", s, re.I)
    if m and not prefix:
        prefix = re.sub(r"[^A-Za-z0-9]+", "_", m.group(1)).strip("_").upper() + "."
        note = (note + " " + m.group(0)).strip()
        s = s[m.end():]
    s = re.sub(r"\s+or\s+\S+(?:\s+or\s+\S+)*\s*$", "", s)      # '1 or 2' -> '1'
    s = re.sub(r"(?<=[1-4])/[1-4]", "", s)                            # '1/2' -> '1'
    s = re.sub(r"\[([^\]]*)\]", r"\1", s)                         # 'TGR [3], f+1' optional hit
    q = QUALIFIER.findall(s)
    if q:
        note = (note + " " + " ".join(q)).strip()
        s = QUALIFIER.sub("", s)
    s = re.sub(r"(?<=[1-4])_[1-4]", "", s)
    # t7chicken string rows mark the hits already thrown with parentheses: '(1), (2), 1' -> '1,2,1'
    s = re.sub(r"\(([^()]*)\)", r"\1", s)
    # t7chicken 'WS 1' / 'SNK 1' / 'FC d/f+1': a leading stance word separated by a space
    m = re.match(r"^\s*([A-Za-z][A-Za-z0-9]{1,6})\s+(?=[1-4udfbnUDFBN(])", s)
    if m and m.group(1).lower() not in ("qcf", "qcb", "hcf", "hcb"):
        w = m.group(1)
        s = STATE_ALIASES.get(w.lower(), w.upper()) + "." + s[m.end():]
    if re.search(r"[a-z]{3,}", s.replace("qcf", "").replace("qcb", "").replace("hcf", "").replace("hcb", "")):
        return None, (note + " descriptive: " + s).strip()
    s = s.replace(", ", ",").replace(" ,", ",")
    # a just-frame / immediate link written after the comma ('1,2,:4', '3,~4') belongs to the hit before it
    s = re.sub(r",([:~])", r"\1", s)
    # 'f, F+2' dash / 'f,f,F+3' run stay as motion tokens
    toks = [x for x in s.split(",")]
    out = []
    for t in toks:
        # a ':' just-frame link inside a token becomes its own segment marker
        for sub in re.split(r"(?<=.)([:~])", t):
            if sub in (":", "~"):
                out.append(sub)
                continue
            c = _token(sub)
            if c is None:
                return None, (note + " unparsed: " + t).strip()
            out.append(c)
    n = ",".join(out).replace(",:,", ":").replace(",~,", "~")
    return (prefix + n) if n else None, note


def limb(notation):
    """WH limb of the LAST hit (armL armR legL legR both)."""
    if not notation:
        return "armR"
    last = re.split(r"[,:~]", notation)[-1].split(".")[-1]
    btns = re.findall(r"[1-4]", last)
    if len(set(btns)) > 1:
        return "both"
    return {"1": "armL", "2": "armR", "3": "legL", "4": "legR"}.get(btns[0] if btns else "", "armR")


def is_motion(notation):
    if not notation:
        return False
    body = notation.split(".")[-1]
    return bool(re.match(r"^(qcf|qcb|hcf|hcb)", body)) or bool(re.match(r"^[fbudnFBUDN](/[fbFB])?,", body))


if __name__ == "__main__":
    import sys
    for a in sys.argv[1:]:
        print(repr(a), "->", canon(a))
