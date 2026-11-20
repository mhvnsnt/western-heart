#!/usr/bin/env python3
"""Generate the Western Heart moveset-library index from the current moveset files.

Regenerates three outputs (never hand-edited):
  1. game/data/moveset-library/index.json       (the editor library index, schema v1)
  2. game/data/moveset-library/deletion-report.json
  3. game/data/moveset-library/quarantine.json

Inputs (read live at generation time; nothing is cached or guessed):
  - The 128 moveset JSONs in game/assets/movesets/*.json whose ids are in
    game/assets/movesets/index.json -> fighters (the loader-accepted set).
    Anything not in fighters (bf-* stubs, t7-* kits, ur-char* banks, the t7/
    overlay dir) is NOT an input and is logged as skipped.
  - game/data/moveset-library/schema.json (v1) + axes.json (properties vocabulary).
  - The 16 audit wronglists (--wronglists DIR): <fighter>.txt, one
    "key | name | src=<bank> row=<N> | <anim_ref> | <class>" line per wrong move.
    mariposa-monarch has no wronglist file; its wrong set is derived from the
    file itself (moves with t3_source == "xiaoyu", verified by the P1B lane).
  - The resolver prefix list + per-fighter stance vocabularies
    (EDITOR-SPEC section 4c / PLAN section 6.1). Stance codes are discovered
    from each file's keys, never from a hardcoded global list.

Usage:
  python3 tools/moveset-library/generate_library_index.py \
      --repo-root /path/to/western-heart \
      --wronglists /path/to/wronglists \
      --source-commit <40-hex main HEAD the files were read from> \
      [--out-dir game/data/moveset-library] [--built 2026-11-20]
  --fetch-ref <sha> downloads the inputs from raw.githubusercontent.com into a
  temporary directory first (for runs without a local clone; git clone is
  blocked on the build box by the EPERM write flicker).

Determinism: same inputs + same --source-commit => byte-identical output.
moves is sorted by fighter::key; per_* maps are sorted; quarantine is sorted
by id. Only `built` in the header/top level changes between runs.

Rules implemented (EDITOR-SPEC section 4 + Lane-1 PLAN):
  - Detector contract (moveset-editor-ui.js fetchLibraryIndex): the index has
    header.counts + moves as an object; NO banks key.
  - source is a label ARRAY (EDITOR-SPEC section 4d: a move may carry several
    layers). This is the ONE deviation from schema.json v1, which declares
    source as a string; it is recorded in header.notes.schema_deviation.
  - Demonio canon: the 80 Devil Jin moves in demonio.json are indexed ONLY
    under demonio-winged:: (matched by source id); they are recorded in the
    deletion report's re_attributed section, never as demonio:: entries.
  - Quarantine (visible, never silently dropped; one reason per entry, first
    match wins in this precedence order):
      Q2 corrupt-key           key contains an HTML-escaped colon (#58;)
      Q3 audit-wrong-still-present
                               wronglist key still in the file AND its content
                               still matches the wrong bank (t3_source or
                               anim_ref). A key whose content was fixed
                               (e.g. tou 1+3/2+4 re-keyed to Paul) is NOT Q3.
      Q4 no-anim-no-source     baek-master-white moves with no anim_ref and
                               no t3_source.
      Q1 no-resolver-prefix    first dot-prefix in GROUNDED/FUFT/FDFA/FDFL/
                               FDFR/FDFT/FUFA/FUFL/CH/TACKLE/REV.
      Q5 validation-failed     missing name/input, wrong JSON type for a
                               numeric field, bad input_slots, duplicate key.
      Q6 unmapped-anim         anim_ref UNMAPPED:* or null/absent. Flagged
                               with anim_status + assignable: null (UNDECIDED
                               -- owner call owed, EDITOR-SPEC section 6d.1).
                               Q6 entries are NOT in the quarantine array;
                               they are flagged in `moves` only.
  - UNMAPPED assignability is NEVER decided by this script.
  - First generation: the previous index was the banks shape (no per-move
    entries), so the deletion report's index-diff `deleted` is {} and the
    P1A deletions (already landed, PR #1790) are recorded separately under
    deleted_by_prior_fix, verified by absence against the current files.
  - Judgement calls recorded in header.notes (PLAN-faithful, data-driven):
    hit_level keeps the first NON-EMPTY hit's level (multi-hit strings
    often lead with a blank, e.g. ',m'); _r<N> row-disambiguation suffixes
    are not layers; UR covers anim_ref "urban-reign:" as well as "ur:";
    moves whose anim_ref game has no PLAN label (KOF XV, Samurai Shodown,
    TTT2, Mortal Kombat) keep source ["WH"] (the msSrc fallback) with the
    true game in source_game_label -- adding those labels is a follow-up.
  - The script reads movesets and writes ONLY the three library outputs. It
    never touches fighter.js, t3-throw.js, t7-throw-clips.js, any moveset
    JSON, claimed-map.json, or the roster.

Exit codes: 0 ok; 2 on a hard error (unreadable input, unparseable JSON, a
fighter id in `fighters` with no file on disk).
"""

import argparse
import collections
import json
import math
import os
import re
import shutil
import sys
import tempfile
import urllib.request

# ---------------------------------------------------------------- constants

SCHEMA = "moveset-library/v1"
HONESTY = ("estimated fields are flagged per-entry in provenance.estimated; "
           "nothing is invented as canon.")

# Resolver prefixes (movesets.js resolver order). BT is handled separately
# because it dominates stance prefixes (BT_<stance>. / <stance>.BT. / BT.).
RESOLVER_PREFIXES = {"WR", "CD", "R", "H", "RD", "SSL", "SSR", "SS",
                     "FC", "hFC", "OTG", "WALL", "WS", "AIR"}
# First dot-prefixes with data but NO resolver path (EDITOR-SPEC 4c / 6a).
NO_RESOLVER_PREFIXES = {"GROUNDED", "FUFT", "FDFA", "FDFL", "FDFR", "FDFT",
                        "FUFA", "FUFL", "CH", "TACKLE", "REV"}
# Schema-enum position for a resolver position (EDITOR-SPEC 4b mapping).
# Anything unlisted (stances, soul states, CD/R/H/RD/SS) maps to standing
# with the exact prefix kept in resolver_position.
POSITION_ENUM = {
    "standing": "standing", "FC.": "crouching", "hFC.": "crouching",
    "BT.": "back-turned", "SSL.": "sidestep-left", "SSR.": "sidestep-right",
    "WR.": "running", "AIR.": "airborne",
    "GROUNDED.": "grounded", "FUFT.": "grounded", "FDFA.": "grounded",
    "FDFL.": "grounded", "FDFR.": "grounded", "FDFT.": "grounded",
    "FUFA.": "grounded", "FUFL.": "grounded", "OTG.": "grounded",
    "WALL.": "corner", "TACKLE.": "mounted", "WS.": "crouching",
    "(back to wall)": "corner", "(backtowall)": "corner",
}
# Throw-chain stage tags (PLAN 6.1). A key whose first dot-prefix is one of
# these AND whose move is a throw carries it as chain_tag.
CHAIN_TAGS = {
    "AB1", "AB2b", "AB2c", "ARM_BREAKER", "CHICKEN_WING_FACE_LOCK",
    "COBRA_CLUTCH", "BURNING_HAMMER", "DHH", "GERMAN_SUPLEX", "PILE_DRIVER",
    "POWER_BOMB", "SLEEPER", "REVERSE_DDT", "CROSS_ARM_LOCK",
    "LEG_CROSS_HOLD", "DOUBLE_HEEL_HOLD", "INDIAN_DEATH_LOCK",
    "HEAD_JAMMER", "REVERSE_ARM_SLAM", "REVERSE_SPECIAL_STRETCH_BOMB",
    "VICTORY_BOMB", "MANHATTAN_DROP", "CANNONBALL_BUSTER", "COBRA_TWIST",
    "STANDING_HEEL_HOLD", "BACKDROP", "BLIND_KICK_HIT",
}
CHAIN_TAG_RE = re.compile(r"^(MMD\d+|RAS\d+|RSSB\d+|SHH\d+c?)$")
# schema.json type enum (v1).
TYPE_ENUM = {"strike", "grapple", "throw", "hold", "aerial", "counter",
             "transition", "stance", "taunt", "special"}
# t3_source values that are Street Fighter banks, not Tekken 3 banks.
SF_BANKS = {"sf6", "sfv", "sf4", "sf", "sfex"}
# Move boolean fields -> axes.json properties terms (only emitted when the
# axes vocabulary contains the term; rageArt/rageDrive are NOT in axes.json).
PROP_MAP = [
    ("launch", "launch"), ("unblockable", "unblockable"),
    ("knockdown", "knockdown"), ("powerCrush", "power-crush"),
    ("screw", "screw"), ("homing", "homing"), ("heavy", "heavy-hit"),
    ("wall_splat", "wall-splat"), ("bound", "bound"), ("taunt", "taunt"),
    ("ko", "ko"), ("armor", "armor"), ("crumple", "crumple"),
    ("aerial", "aerial"), ("counter_hit", "counter-hit"),
    ("finisher", "finisher"),
]
# msSrc priority order for the source label array (moveset-editor-ui.js).
SOURCE_ORDER = ["WH", "T8", "T7", "DONOR", "T3", "VF", "DOA", "SF", "UR"]
GAME_LABEL = {"T3": "Tekken 3", "T7": "Tekken 7", "T8": "Tekken 8",
              "VF": "Virtua Fighter 5", "DOA": "Dead or Alive",
              "SF": "Street Fighter", "UR": "Urban Reign",
              "WH": "Western Heart"}
# Game names for anim_ref prefixes that have NO source label in the PLAN
# table (KOF XV, Samurai Shodown, TTT2, Mortal Kombat). Those moves keep
# source ["WH"] (the msSrc fallback) but carry the true game here, so the
# gap is visible instead of silent. Adding KOF/SAMSHO/TTT2/MK labels is a
# follow-up decision, not a generator one.
ANIM_GAME = {"kofxv": "KOF XV", "samsho": "Samurai Shodown",
             "ttt2": "Tekken Tag Tournament 2", "mk": "Mortal Kombat",
             "urban-reign": "Urban Reign", "t3": "Tekken 3",
             "t7": "Tekken 7", "t8": "Tekken 8",
             "vf": "Virtua Fighter 5", "doa": "Dead or Alive",
             "wh": "Western Heart", "ur": "Urban Reign",
             "sf6": "Street Fighter 6", "sfv": "Street Fighter V",
             "sf4": "Street Fighter IV", "sf": "Street Fighter"}
LAYER_RE = re.compile(r"~(t8|t7|t3|donor)(?:\.|$)")
TRAILING_SUFFIX_RE = re.compile(r"(__main|_c36|_r\d+|_t8)$")


def f2f(seconds):
    """JS Math.round(seconds * 60); None stays None."""
    if seconds is None:
        return None
    return int(math.floor(seconds * 60 + 0.5))


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def norm_hit_level(v):
    """Normalize a stored hit_level to the schema enum (or None).

    Stored values are wild: 'h', 'm', 'M,M', 'high, mid', 's. mid',
    'th(h)', 'high throw', '', '-', 'sl', ... The first NON-EMPTY hit's
    level is kept (multi-hit strings often lead with a blank, e.g. ',m');
    anything unmappable returns None (counted in the run log).
    """
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in ("", "-", "air", "s", "m?", "!", "imd"):
        return None
    toks = [t.strip() for t in s.split(",")]
    toks = [t for t in toks if t]
    if not toks:
        return None
    first = re.sub(r"\(.*?\)", "", toks[0]).strip().rstrip("!")
    if "throw" in s or first in ("t", "th"):
        return "throw"
    if first.startswith("ub"):
        return "unblockable"
    if first in ("high", "h"):
        return "high"
    if first in ("mid", "m", "mmid"):
        return "mid"
    if first in ("low", "l"):
        return "low"
    if first in ("special mid", "special-mid", "s. mid", "s.mid", "sm", "s mid"):
        return "special-mid"
    return None


def parse_key(key):
    """Split a moveset dict key into (base_key, layer, layer_leading).

    Layer suffixes (PLAN 6.1): ~t8.<char> / ~t7.<char> / ~t3.<char> /
    ~donor.<fighter> after the base input; leading t7./t8./donor. markers;
    trailing __main / _c36 / _r<N> / _t8. The base key is what position and
    chain-tag analysis run on.
    """
    m = LAYER_RE.search(key)
    if m:
        return key[:m.start()], m.group(1), False
    if key.startswith("t7.") or key.startswith("t8."):
        return key, key[:2], True
    if key.startswith("donor."):
        return key, "donor", True
    m = TRAILING_SUFFIX_RE.search(key)
    if m:
        tok = m.group(1)
        # __main / _c36 / _t8 are layer-ish suffixes. _r<N> is a row
        # disambiguator, not a layer (PLAN 1.3: layer is the ~t8/~t7/~t3/
        # ~donor suffix the key carries; the _r<N> stays in the key itself).
        if tok == "_t8":
            return key[:m.start()], "t8", False
        if tok == "__main":
            return key[:m.start()], "main", False
        if tok == "_c36":
            return key[:m.start()], "c36", False
        return key, None, False
    return key, None, False


def resolver_position(key):
    """First dot-prefix of the base key, or 'standing'.

    Returns (resolver_position, first_segment). BT dominates stance
    (BT. / BT_<stance>. / <stance>.BT.). Unknown prefixes are per-fighter
    stance/soul-state codes (discovered, never hardcoded) -- except the
    closed NO_RESOLVER_PREFIXES list, which is quarantine Q1. Leading
    layer markers (donor.<fighter>. / t7. / t8.) are stripped first: the
    remainder is what carries the position (e.g. donor.kronos.None~donor.
    sf-zangief.10 has no position prefix once both markers are stripped).
    """
    k = key
    # Strip leading layer markers repeatedly: some keys carry them twice
    # (donor.kronos.donor.sf-zangief.360+2).
    while True:
        if k.startswith("donor."):
            parts = k.split(".", 2)
            k = parts[2] if len(parts) == 3 else ""
            if not k:
                return "standing", None
            continue
        if k.startswith("t7.") or k.startswith("t8."):
            return "standing", None
        break
    base, _layer, _ll = parse_key(k)
    if "." not in base:
        return "standing", None
    segs = base.split(".")
    if "BT" in segs or segs[0].startswith("BT_"):
        return "BT.", "BT"
    seg = segs[0]
    if seg == "None":
        return "standing", None
    return seg + ".", seg


def chain_tag_for(key, is_throw):
    """Throw-chain stage tag, or None (PLAN 6.1)."""
    if not is_throw:
        return None
    _pos, seg = resolver_position(key)
    if seg is None:
        return None
    if seg in CHAIN_TAGS or CHAIN_TAG_RE.match(seg):
        return seg
    return None


def devil_markers(m):
    """True if a demonio.json move is a Devil Jin move (owner canon)."""
    if m.get("t3_source") == "deviljin":
        return True
    ar = m.get("anim_ref") or ""
    if isinstance(ar, str) and (ar.startswith("t7:devil_jin") or
                                ar.startswith("t8:devil_jin")):
        return True
    for f in ("t7_source", "t8_source"):
        if "devil" in str(m.get(f, "")).lower():
            return True
    t7 = m.get("t7") or {}
    if isinstance(t7, dict) and "devil" in str(t7.get("id", "")).lower():
        return True
    if "devil" in str(m.get("t7_move_id", "")).lower():
        return True
    if "devil" in str(m.get("t8_id", "")).lower():
        return True
    return False


def source_ids(m):
    """Source ids used to match a demonio.json Devil move to its winged copy."""
    ids = set()
    if m.get("t7_move_id"):
        ids.add(("t7", str(m["t7_move_id"])))
    t7 = m.get("t7") or {}
    if isinstance(t7, dict) and t7.get("id"):
        ids.add(("t7", str(t7["id"])))
    if m.get("t8_id"):
        ids.add(("t8", str(m["t8_id"])))
    if m.get("t3_source") == "deviljin" and m.get("t3_row") is not None:
        ids.add(("t3", str(m["t3_row"])))
    return ids


def source_labels(m, file_markers):
    """Label array for one move, ordered by msSrc priority (EDITOR-SPEC 4d).

    T3 requires a Tekken 3 bank in t3_source; SF bank values (sfv/sf6/...)
    in that slot label SF instead. A move with no discriminator at all falls
    back to WH, matching msSrc's final else (its quarantine reason, where
    applicable, carries the no-source truth).
    """
    labels = set()
    ar = m.get("anim_ref") or ""
    ar = ar if isinstance(ar, str) else ""
    t7 = m.get("t7") or {}
    t7_id = m.get("t7_move_id") or (t7.get("id") if isinstance(t7, dict) else None)
    wh_sig = bool(m.get("wh_original")) or (
        m.get("move_class") == "signature" and ar.startswith("wh:"))
    if wh_sig:
        labels.add("WH")
    if m.get("t8_source") or m.get("t8_id") or ar.startswith("t8:"):
        labels.add("T8")
    if (m.get("t7_source") or t7_id or ar.startswith("t7:") or
            (isinstance(t7, dict) and t7.get("wired"))):
        labels.add("T7")
    ms = m.get("merge_source") or ""
    if isinstance(ms, str) and ms.startswith("donor"):
        labels.add("DONOR")
    t3s = m.get("t3_source")
    if t3s and t3s not in SF_BANKS:
        labels.add("T3")
    if m.get("vf_move") or m.get("vf_input") or ar.startswith("vf:"):
        labels.add("VF")
    if m.get("doa_move") or m.get("doa_input") or ar.startswith("doa:"):
        labels.add("DOA")
    if (m.get("sf_move") or m.get("sf_input") or m.get("sf_source") or
            m.get("sf_game") or m.get("sf_motion") or
            ar.startswith(("sf6:", "sfv:", "sf4:", "sf:")) or
            (t3s in SF_BANKS if t3s else False)):
        labels.add("SF")
    if ar.startswith("ur:") or ar.startswith("urban-reign:"):
        labels.add("UR")
    if not labels:
        labels.add("WH")
    return [lab for lab in SOURCE_ORDER if lab in labels]


def load_json_with_dup_check(path, dup_log):
    """json.load that records duplicate keys (same key twice in one object)."""
    def hook(pairs):
        keys = [k for k, _v in pairs]
        dups = [k for k, c in collections.Counter(keys).items() if c > 1]
        for k in dups:
            dup_log.append((path, k))
        return dict(pairs)
    with open(path, encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=hook)


def parse_wronglist(path):
    """wronglist txt -> {key: (bank, anim_ref)}."""
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            key = parts[0]
            bank = None
            if len(parts) > 2:
                m = re.search(r"src=(\S+)", parts[2])
                bank = m.group(1) if m else None
            anim = parts[3] if len(parts) > 3 else ""
            out[key] = (bank, anim)
    return out


def fetch_inputs(ref, dest):
    """Download the repo inputs for --fetch-ref via raw.githubusercontent.com."""
    import concurrent.futures
    base = f"https://raw.githubusercontent.com/mhvnsnt/western-heart/{ref}"
    paths = ["game/assets/movesets/index.json",
             "game/data/moveset-library/schema.json",
             "game/data/moveset-library/axes.json"]
    # fighters list first, then the 128 files (parallel; the proxy is slow).
    def fetch(path, tries=4):
        import time as _t
        url = f"{base}/{path}"
        req = urllib.request.Request(url, headers={"User-Agent": "lane2-generate"})
        last = None
        for i in range(tries):
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    return path, r.read(), None
            except Exception as e:  # noqa: BLE001
                last = f"{type(e).__name__}: {e}"
                _t.sleep(5 * (i + 1))
        return path, None, last
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        first = list(ex.map(fetch, paths))
    for path, data, err in first:
        if err:
            raise RuntimeError(f"fetch failed for {path}: {err}")
        fp = os.path.join(dest, path)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, "wb") as f:
            f.write(data)
    with open(os.path.join(dest, paths[0]), encoding="utf-8") as f:
        fighters = sorted(json.load(f)["fighters"].keys())
    mpaths = [f"game/assets/movesets/{fid}.json" for fid in fighters]
    fails = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
        for path, data, err in ex.map(fetch, mpaths):
            if err:
                fails.append((path, err))
                continue
            fp = os.path.join(dest, path)
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            with open(fp, "wb") as f:
                f.write(data)
    if fails:
        raise RuntimeError(f"fetch failed for {len(fails)} files: {fails[:5]}")
    return dest


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", default=None,
                    help="repo checkout root (default: derived from this script)")
    ap.add_argument("--wronglists", required=True,
                    help="dir with the 16 audit wronglist *.txt files")
    ap.add_argument("--source-commit", default=None,
                    help="40-hex main HEAD the files were read from")
    ap.add_argument("--out-dir", default=None,
                    help="output dir (default: <repo-root>/game/data/moveset-library)")
    ap.add_argument("--built", default=None, help="build date YYYY-MM-DD")
    ap.add_argument("--fetch-ref", default=None,
                    help="download inputs from this ref instead of a local root")
    args = ap.parse_args()

    import datetime
    built = args.built or datetime.date.today().isoformat()
    tmpdir = None
    if args.fetch_ref:
        tmpdir = tempfile.mkdtemp(prefix="wh-library-fetch-")
        root = fetch_inputs(args.fetch_ref, tmpdir)
        source_commit = args.fetch_ref
    else:
        root = args.repo_root
        if root is None:
            # tools/moveset-library/generate_library_index.py -> repo root
            root = os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))))
        source_commit = args.source_commit or "unknown"
    out_dir = args.out_dir or os.path.join(root, "game/data/moveset-library")
    movesets_dir = os.path.join(root, "game/assets/movesets")
    lib_dir = os.path.join(root, "game/data/moveset-library")
    log = []

    def note(msg):
        log.append(msg)
        print(msg)

    # ---- inputs ------------------------------------------------------
    loader_path = os.path.join(movesets_dir, "index.json")
    try:
        with open(loader_path, encoding="utf-8") as f:
            loader = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"HARD ERROR: cannot read loader index {loader_path}: {e}",
              file=sys.stderr)
        return 2
    fighters = sorted(loader.get("fighters", {}).keys())
    if not fighters:
        print("HARD ERROR: no fighters in loader index", file=sys.stderr)
        return 2
    note(f"fighters in loader index: {len(fighters)}")

    axes = {}
    axes_path = os.path.join(lib_dir, "axes.json")
    if os.path.exists(axes_path):
        with open(axes_path, encoding="utf-8") as f:
            axes = json.load(f)
    else:
        note("GAP: axes.json unreadable -- properties emitted as []")
    axes_props = set((axes.get("properties") or {}).keys())

    # Wronglists: content-verified Q3 sets.
    wrong = {}   # fighter -> {key: (bank, anim_ref)}
    wl_files = sorted(fn for fn in os.listdir(args.wronglists)
                      if fn.endswith(".txt"))
    for fn in wl_files:
        wrong[fn[:-4]] = parse_wronglist(os.path.join(args.wronglists, fn))
    note(f"wronglist files: {len(wl_files)} "
         f"({sum(len(v) for v in wrong.values())} wrong moves listed)")

    # ---- per-fighter generation --------------------------------------
    moves = {}
    quarantine = []
    re_attributed = collections.defaultdict(list)
    deleted_prior = collections.defaultdict(list)
    rekeyed_prior = collections.defaultdict(list)
    stats = collections.Counter()
    stance_vocab = collections.defaultdict(set)
    unmapped_hit_level = collections.Counter()
    dup_log = []
    q3_by_source = collections.Counter()
    t3_source_values = collections.Counter()
    layer_counts = collections.Counter()

    # Winged index for the Demonio re-attribution (source-id match).
    wing_path = os.path.join(movesets_dir, "demonio-winged.json")
    wing_by_id = {}
    if os.path.exists(wing_path):
        with open(wing_path, encoding="utf-8") as f:
            wing_moves = json.load(f).get("moves", {})
        for wk, wm in wing_moves.items():
            for sid in source_ids(wm):
                wing_by_id.setdefault(sid, []).append(wk)

    for fid in fighters:
        fpath = os.path.join(movesets_dir, f"{fid}.json")
        if not os.path.exists(fpath):
            print(f"HARD ERROR: fighter {fid} in loader index but no file "
                  f"on disk: {fpath}", file=sys.stderr)
            return 2
        try:
            data = load_json_with_dup_check(fpath, dup_log)
        except (OSError, json.JSONDecodeError) as e:
            print(f"HARD ERROR: cannot parse {fpath}: {e}", file=sys.stderr)
            return 2
        file_moves = data.get("moves") or {}
        file_markers = data
        wl = wrong.get(fid, {})
        # mariposa-monarch derived wrong set (no wronglist file exists).
        if fid == "mariposa-monarch":
            wl = {k: ("xiaoyu", "") for k, m in file_moves.items()
                  if isinstance(m, dict) and m.get("t3_source") == "xiaoyu"}
        # Q4 set for baek-master-white.
        q4 = set()
        if fid == "baek-master-white":
            q4 = {k for k, m in file_moves.items()
                  if isinstance(m, dict) and not m.get("anim_ref")
                  and not m.get("t3_source")}

        for key in sorted(file_moves.keys()):
            m = file_moves[key]
            eid = f"{fid}::{key}"
            if not isinstance(m, dict):
                stats["q5_non_dict"] += 1
                quarantine.append({"id": eid, "reason": "validation-failed",
                                   "detail": "move entry is not a JSON object"})
                moves[eid] = {"id": eid, "key": key, "fighter": fid,
                              "name": None, "input": None,
                              "position": "standing",
                              "resolver_position": "standing",
                              "orientation": "forward",
                              "move_class": None, "type": "special",
                              "subtype": None, "damage": None,
                              "startup": None, "active": None, "recovery": None,
                              "frames": {"startup": None, "active": None,
                                         "recovery": None, "total": None},
                              "anim_ref": None, "anim_status": "null",
                              "source": ["WH"], "isGrab": False,
                              "throw_break": None, "input_slots": [],
                              "layer": None, "chain_tag": None,
                              "wh_original": False, "name_status":
                              f"auto-label — as stored in {fid}.json",
                              "hit_level": None, "limb": None,
                              "properties": [], "wh": {},
                              "provenance": {"note": f"{fid}.json key {key}",
                                             "estimated": []},
                              "quarantined": True, "assignable": False,
                              "quarantine_reason": "validation-failed"}
                continue

            # Demonio canon: Devil Jin moves live ONLY under demonio-winged::.
            if fid == "demonio" and devil_markers(m):
                ids = source_ids(m)
                targets = sorted({wk for sid in ids
                                  for wk in wing_by_id.get(sid, [])})
                if not targets:
                    note(f"WARNING: demonio devil move {key} has no winged "
                         f"match by source id {sorted(ids)}")
                    targets = []
                re_attributed[fid].append(
                    {"key": key,
                     "to": f"demonio-winged::{targets[0]}" if targets else None,
                     "reason": "demonio-devil-form-canon"})
                stats["demonio_re_attributed"] += 1
                continue

            # ---- validation (Q5) ----
            vfail = []
            name = m.get("name")
            if name is None or not isinstance(name, str):
                vfail.append("name")
            inp = m.get("input")
            if inp is None or not isinstance(inp, str):
                vfail.append("input")
            nums = {}
            for fld in ("damage", "startup", "active", "recovery"):
                v = m.get(fld)
                if v is None:
                    nums[fld] = None
                elif is_number(v):
                    nums[fld] = v
                else:
                    vfail.append(fld)
                    nums[fld] = None
            slots = m.get("input_slots")
            if slots is None:
                slots = []
            elif (not isinstance(slots, list) or
                    not all(isinstance(s, str) for s in slots)):
                vfail.append("input_slots")
                slots = []
            if eid in [f"{fid}::{k}" for (_p, k) in dup_log
                       if _p == fpath]:
                vfail.append("duplicate-key")

            # ---- position / layer / chain ----
            res_pos, seg = resolver_position(key)
            _base, layer, _ll = parse_key(key)
            layer_counts[layer] += 1
            if seg is not None:
                stance_vocab[fid].add(seg)
            schema_pos = POSITION_ENUM.get(res_pos, "standing")
            is_grab = bool(m.get("isGrab")) or m.get("move_class") == "throw"
            chain = chain_tag_for(key, is_grab)

            # ---- source labels ----
            labels = source_labels(m, file_markers)
            for lab in labels:
                stats[f"src_{lab}"] += 1
            if len(labels) > 1:
                stats["multi_layer"] += 1
            if m.get("t3_source"):
                t3_source_values[m["t3_source"]] += 1

            # ---- anim status ----
            ar = m.get("anim_ref")
            if ar is None:
                anim_status = "null"
            elif isinstance(ar, str) and ar.startswith("UNMAPPED"):
                anim_status = "UNMAPPED"
            else:
                anim_status = "mapped"
            stats[f"anim_{anim_status}"] += 1
            if isinstance(ar, str) and ":" in ar:
                apref = ar.split(":")[0]
                if apref in ("kofxv", "samsho", "ttt2", "mk"):
                    stats[f"anim_game_{apref}"] += 1

            # ---- quarantine reason (precedence Q2 > Q3 > Q4 > Q1 > Q5) ----
            reason = None
            detail = ""
            if "#58;" in key:
                reason = "corrupt-key"
                detail = "key contains an HTML-escaped colon (#58;)"
            elif key in wl:
                bank, wanim = wl[key]
                if m.get("t3_source") == bank or m.get("anim_ref") == wanim:
                    reason = "audit-wrong-still-present"
                    detail = (f"audit wronglist {fid}: T3 {bank} still "
                              f"present in current file")
                    q3_by_source[fid] += 1
            if reason is None and key in q4:
                reason = "no-anim-no-source"
                detail = ("no anim_ref and no t3_source; provenance "
                          "undocumented")
            if reason is None and seg in NO_RESOLVER_PREFIXES:
                reason = "no-resolver-prefix"
                detail = (f"first dot-prefix {seg}. has no resolver path")
            if reason is None and vfail:
                reason = "validation-failed"
                detail = "validation failed: " + ", ".join(sorted(set(vfail)))
            if reason is not None:
                stats[f"q_{reason}"] += 1

            # ---- type / subtype ----
            mc = m.get("move_class")
            if isinstance(mc, str) and mc in TYPE_ENUM:
                typ, subtype = mc, None
            else:
                typ, subtype = "special", mc if isinstance(mc, str) else None

            # ---- hit level ----
            hl_raw = m.get("hit_level")
            if hl_raw is None or (isinstance(hl_raw, str) and not hl_raw.strip()):
                t7d = m.get("t7") or {}
                hl_raw = t7d.get("hit_level") if isinstance(t7d, dict) else None
            hit_level = norm_hit_level(hl_raw)
            if hl_raw not in (None, "") and hit_level is None:
                unmapped_hit_level[str(hl_raw)[:40]] += 1

            # ---- properties (axes vocabulary only) ----
            props = set()
            for field, term in PROP_MAP:
                if m.get(field) is True and term in axes_props:
                    props.add(term)
            if is_grab and "throw" in axes_props:
                props.add("throw")
            if (mc == "string" or "multi_hit" in m) and "string" in axes_props:
                props.add("string")

            # ---- frames ----
            fr = {fld: f2f(nums[fld]) for fld in ("startup", "active", "recovery")}
            fr["total"] = (fr["startup"] + fr["active"] + fr["recovery"]
                           if all(v is not None for v in fr.values()) else None)

            # ---- wh tuning ----
            wh = {k: m[k] for k in ("heavy", "knock", "soulGain") if k in m}

            # ---- provenance ----
            t7d = m.get("t7") or {}
            t7_id = m.get("t7_move_id") or (t7d.get("id")
                                            if isinstance(t7d, dict) else None)
            if m.get("t3_source"):
                row = m.get("t3_row")
                row_s = ",".join(str(r) for r in row) if isinstance(row, list) else row
                pnote = (f"Tekken 3 {m['t3_source']} row {row_s} "
                         f"via {fid}.json")
            elif m.get("t8_id") or m.get("t8_source"):
                pnote = (f"Tekken 8 {m.get('t8_source') or m.get('t8_id')} "
                         f"via {fid}.json")
            elif t7_id or m.get("t7_source"):
                pnote = (f"Tekken 7 {m.get('t7_source') or t7_id} "
                         f"via {fid}.json")
            elif m.get("vf_move") or (isinstance(ar, str) and ar.startswith("vf:")):
                pnote = (f"Virtua Fighter {file_markers.get('vf_source') or 'VF5'} "
                         f"{m.get('vf_move') or key} via {fid}.json")
            elif m.get("doa_move") or (isinstance(ar, str) and ar.startswith("doa:")):
                pnote = (f"Dead or Alive {file_markers.get('doa_source') or ''} "
                         f"{m.get('doa_move') or key} via {fid}.json")
            elif (m.get("sf_move") or m.get("sf_game") or m.get("sf_source")):
                pnote = (f"Street Fighter {m.get('sf_game') or ''} "
                         f"{m.get('sf_move') or key} via {fid}.json")
            elif isinstance(ar, str) and ar.startswith("ur:"):
                pnote = f"Urban Reign {ar} via {fid}.json"
            elif mc == "signature":
                pnote = f"Western Heart signature {name} via {fid}.json"
            else:
                pnote = f"{fid}.json key {key}"
            estimated = []
            if "estimated" in str(m.get("note", "")).lower():
                estimated = ["startup", "active", "recovery", "damage"]

            # ---- damage_raw ----
            draw = m.get("damage_raw")
            if not is_number(draw):
                draw = m.get("t3_damage") if is_number(m.get("t3_damage")) else None
            if draw is None:
                draw = m.get("t8_damage") if is_number(m.get("t8_damage")) else None

            entry = {
                "id": eid, "key": key, "fighter": fid, "name": name,
                "input": inp if isinstance(inp, str) else None,
                "position": schema_pos, "resolver_position": res_pos,
                "orientation": ("backward" if res_pos == "BT."
                                else "forward"),
                "move_class": mc, "type": typ, "subtype": subtype,
                "damage": nums["damage"], "startup": nums["startup"],
                "active": nums["active"], "recovery": nums["recovery"],
                "frames": fr, "anim_ref": ar if isinstance(ar, str) else None,
                "anim_status": anim_status, "source": labels,
                "isGrab": is_grab,
                "throw_break": m.get("throw_break"),
                "input_slots": slots, "layer": layer, "chain_tag": chain,
                "wh_original": bool(m.get("wh_original")),
                "name_status": f"auto-label — as stored in {fid}.json",
                "hit_level": hit_level, "limb": m.get("limb"),
                "properties": sorted(props), "wh": wh,
                "provenance": {"note": pnote, "estimated": estimated},
                "quarantined": reason is not None,
                "assignable": False if reason is not None else (
                    None if anim_status in ("UNMAPPED", "null") else True),
                "quarantine_reason": reason,
            }
            # Raw discriminator fields (msSrc/msCat fallbacks, EDITOR-SPEC 4b).
            for f in ("merge_source", "t8_id", "t7_move_id", "t3_source",
                      "t3_row", "t3_command", "t7_source", "t8_source",
                      "vf_move", "vf_input", "doa_move", "doa_input",
                      "sf_move", "sf_input", "sf_game", "sf_source",
                      "donor_fighter"):
                if f in m:
                    entry[f] = m[f]
            if t7_id is not None and "t7_move_id" not in entry:
                entry["t7_move_id"] = t7_id
            if draw is not None:
                entry["damage_raw"] = draw
            sc = (m.get("t3_source") or m.get("t8_source") or
                  m.get("t7_source"))
            if sc:
                entry["source_character"] = sc
            elif isinstance(ar, str) and ar.count(":") >= 1:
                entry["source_character"] = ar.split(":")[1]
            first_lab = labels[0]
            if first_lab in GAME_LABEL:
                entry["source_game_label"] = (
                    m.get("sf_game") if first_lab == "SF" and m.get("sf_game")
                    else GAME_LABEL[first_lab])
            # True game for moves whose anim_ref game has no source label
            # (KOF XV / Samurai Shodown / TTT2 / Mortal Kombat): the source
            # array stays ["WH"] (msSrc fallback) but the game is not hidden.
            if labels == ["WH"] and isinstance(ar, str) and ":" in ar:
                agame = ANIM_GAME.get(ar.split(":")[0])
                if agame:
                    entry["source_game_label"] = agame
            elif first_lab == "DONOR" and isinstance(m.get("merge_source"), str):
                entry["source_character"] = m["merge_source"].split(":")[1] \
                    if ":" in m["merge_source"] else m["merge_source"]

            moves[eid] = entry
            if reason is not None:
                quarantine.append({"id": eid, "reason": reason,
                                   "detail": detail})
            elif anim_status in ("UNMAPPED", "null"):
                stats["q6_unmapped_anim_flagged"] += 1

        # P1A prior-fix accounting (verified by absence against current files).
        if fid in wrong:
            for k, (bank, wanim) in wrong[fid].items():
                if k not in file_moves:
                    deleted_prior[fid].append(k)
                elif (file_moves[k].get("t3_source") != bank and
                        file_moves[k].get("anim_ref") != wanim):
                    rekeyed_prior[fid].append(
                        {"key": k,
                         "from": f"T3 {bank}",
                         "to": (f"T3 {file_moves[k].get('t3_source')} row "
                                f"{file_moves[k].get('t3_row')}")})

    # ---- counts -------------------------------------------------------
    per_fighter = collections.Counter()
    per_position = collections.Counter()
    per_input = collections.Counter()
    per_source = collections.Counter()
    per_class = collections.Counter()
    per_qreason = collections.Counter()
    n_multi = 0
    n_unmapped = 0
    n_assignable = 0
    n_unassignable = 0
    n_undecided = 0
    null_inputs = 0
    for eid, e in moves.items():
        per_fighter[e["fighter"]] += 1
        per_position[e["resolver_position"]] += 1
        if e["input"] is None:
            null_inputs += 1
        else:
            per_input[e["input"]] += 1
        for lab in e["source"]:
            per_source[lab] += 1
        if len(e["source"]) > 1:
            n_multi += 1
        # per_move_class.throw uses the runtime grab test (fighter.js:449-453).
        if e["isGrab"]:
            per_class["throw"] += 1
        elif e["move_class"] is not None:
            per_class[str(e["move_class"])] += 1
        else:
            per_class["null"] += 1
        if e["anim_status"] in ("UNMAPPED", "null"):
            n_unmapped += 1
        if e["assignable"] is True:
            n_assignable += 1
        elif e["assignable"] is False:
            n_unassignable += 1
        else:
            n_undecided += 1
        if e["quarantine_reason"]:
            per_qreason[e["quarantine_reason"]] += 1
    quarantine.sort(key=lambda q: q["id"])

    counts = {
        "total_moves": len(moves),
        "total_fighters": len(per_fighter),
        "per_fighter": dict(sorted(per_fighter.items())),
        "per_position": dict(sorted(per_position.items())),
        "per_input": dict(sorted(per_input.items())),
        "unique_inputs": len(per_input),
        "per_source": dict(sorted(per_source.items())),
        "multi_layer": n_multi,
        "per_move_class": dict(sorted(per_class.items())),
        "quarantined": len(quarantine),
        "per_quarantine_reason": dict(sorted(per_qreason.items())),
        "unmapped_anim": n_unmapped,
        "assignable": n_assignable,
        "unassignable": n_unassignable,
        "assignability_undecided": n_undecided,
        "null_input": null_inputs,
    }
    notes = {
        "per_source_note": ("a move counts under each layer label it "
                            "carries; per_source values do not sum to "
                            "total_moves"),
        "schema_deviation": ("source is an array of labels per EDITOR-SPEC "
                             "section 4d (a move may carry several layers); "
                             "schema.json v1 declares string"),
        "type_mapping": ("type = move_class when it is in the schema enum "
                         "(strike, throw, special, stance, transition, "
                         "grapple, hold, aerial, counter, taunt); otherwise "
                         "type = special with the real move_class preserved "
                         "in move_class + subtype (string/signature/parry/"
                         "launcher/reversal/movement/super/unblockable/"
                         "projectile/null)"),
        "throw_definition": ("per_move_class.throw counts the runtime grab "
                             "set (isGrab true OR move_class throw, "
                             "fighter.js:449-453); other classes count by "
                             "move_class value"),
        "position_mapping": ("position is the schema enum; WS. maps to "
                             "crouching (rising, approximation); stance and "
                             "soul-state prefixes map to standing with the "
                             "exact prefix kept in resolver_position; "
                             "(back to wall)/(backtowall) map to corner"),
        "quarantine_note": ("quarantined counts the quarantine array (Q1-"
                            "Q5). Q6 unmapped-anim moves are flagged in "
                            "moves with anim_status + assignable null and "
                            "are NOT in the quarantine array (owner call "
                            "owed, EDITOR-SPEC section 6d.1)"),
        "demonio_note": ("the 80 Devil Jin moves in demonio.json are "
                         "indexed ONLY under demonio-winged:: (matched by "
                         "source id); see deletion-report re_attributed"),
        "exclusions_note": ("inputs are the 128 fighters in the loader "
                            "index only; excluded: 26 bf-* stubs, 11 t7-* "
                            "kits, 31 ur-char* banks, 4 non-moveset files, "
                            "and the t7/ overlay dir"),
        "source_fallback_note": ("a move with no discriminator at all "
                                 "carries source [WH], matching msSrc's "
                                 "final else in moveset-editor-ui.js"),
        "frames_note": ("frames are Math.round(seconds * 60) per component; "
                        "total is the sum of the rounded components, null "
                        "when any component is null"),
        "t3_source_note": ("T3 requires a Tekken 3 bank in t3_source; "
                           "sfv/sf6/sf4 values in that slot label SF, not "
                           "T3"),
        "loader_stale_note": ("counts are computed from the moveset files, "
                              "never from game/assets/movesets/index.json, "
                              "whose counts are stale for 7 fighters "
                              "(cainelias, charger, megami, ryuji, "
                              "ryuji-rock, thor, vainabel)"),
        "other_games_note": ("moves whose anim_ref game has no source label "
                             "in the PLAN table carry source [WH] (the msSrc "
                             "fallback) with the true game in "
                             "source_game_label: "
                             + ", ".join(
                                 f"{g} {stats.get('anim_game_' + g, 0)}"
                                 for g in ("kofxv", "samsho", "ttt2", "mk"))
                             + "; adding KOF/SAMSHO/TTT2/MK labels is a "
                               "follow-up decision"),
        "layer_note": ("layer is the ~t8/~t7/~t3/~donor suffix (or leading "
                       "t7./t8./donor. marker, or __main/_c36/_t8); _r<N> "
                       "row-disambiguation suffixes are NOT layers"),
    }
    index = {
        "schema": SCHEMA, "built": built,
        "builder": "tools/moveset-library/generate_library_index.py",
        "source_commit": source_commit, "honesty": HONESTY,
        "header": {"counts": counts, "notes": notes},
        "moves": dict(sorted(moves.items())),
        "quarantine": quarantine,
    }

    deleted = {fid: sorted(keys) for fid, keys in
               sorted(deleted_prior.items()) if keys}
    rekeyed = {fid: sorted(v, key=lambda r: r["key"]) for fid, v in
               sorted(rekeyed_prior.items()) if v}
    reattr = {fid: sorted(v, key=lambda r: r["key"]) for fid, v in
              sorted(re_attributed.items()) if v}
    deletion_report = {
        "schema": "moveset-library/deletion-report/v1",
        "built": built,
        "builder": "tools/moveset-library/generate_library_index.py",
        "source_commit": source_commit,
        "generated_from": ("baseline-first-generation (previous index was "
                           "banks shape, no per-move entries to diff)"),
        "deleted": {},
        "total_deleted": 0,
        "deleted_by_prior_fix": deleted,
        "deleted_by_prior_fix_total": sum(len(v) for v in deleted.values()),
        "deleted_by_prior_fix_source": ("P1A fix, PR #1790, merge 3484f9dd; "
                                        "keys verified absent from the "
                                        "current files at generation time"),
        "re_keyed_by_prior_fix": rekeyed,
        "re_keyed_by_prior_fix_total": sum(len(v) for v in rekeyed.values()),
        "re_attributed": reattr,
        "re_attributed_total": sum(len(v) for v in reattr.values()),
    }
    quarantine_doc = {
        "schema": "moveset-library/quarantine/v1",
        "built": built,
        "builder": "tools/moveset-library/generate_library_index.py",
        "source_commit": source_commit,
        "total": len(quarantine),
        "quarantine": quarantine,
    }

    # ---- write --------------------------------------------------------
    os.makedirs(out_dir, exist_ok=True)
    for name, doc in (("index.json", index),
                      ("deletion-report.json", deletion_report),
                      ("quarantine.json", quarantine_doc)):
        fp = os.path.join(out_dir, name)
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, separators=(",", ":"),
                      sort_keys=True)
            f.write("\n")
        note(f"wrote {fp} ({os.path.getsize(fp)} bytes)")

    # ---- run summary --------------------------------------------------
    note(f"TOTAL indexed moves: {len(moves)} across {len(per_fighter)} fighters")
    note(f"quarantined: {len(quarantine)} {dict(sorted(per_qreason.items()))}")
    note(f"unmapped_anim: {n_unmapped} "
         f"(assignability_undecided: {n_undecided})")
    note(f"assignable: {n_assignable}  unassignable: {n_unassignable}")
    note(f"per_source: {dict(sorted(per_source.items()))} "
         f"multi_layer: {n_multi}")
    note(f"per_move_class: {dict(sorted(per_class.items()))}")
    note(f"demonio re-attributed: {sum(len(v) for v in reattr.values())}")
    note(f"deleted_by_prior_fix: "
         f"{sum(len(v) for v in deleted.values())} "
         f"re_keyed_by_prior_fix: {sum(len(v) for v in rekeyed.values())}")
    note(f"Q3 by fighter: {dict(sorted(q3_by_source.items()))}")
    note(f"duplicate keys found while parsing: {len(dup_log)} {dup_log[:10]}")
    note(f"unmapped hit_level values (top 20): "
         f"{dict(unmapped_hit_level.most_common(20))}")
    note(f"t3_source values: {dict(t3_source_values)}")
    note(f"layer counts: {dict(layer_counts)}")
    note(f"stance vocab sizes: "
         f"{sum(len(v) for v in stance_vocab.values())} distinct "
         f"fighter/prefix pairs")
    if tmpdir:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
