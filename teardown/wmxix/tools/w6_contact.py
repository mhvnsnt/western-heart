#!/usr/bin/env python3
"""W6: wrestler face contact sheets for Mars (slot identification).

Picks each slot's face texture from the wrestler-tex output (prefer a
non-m_ *face* entry, fall back to *head*, *_me*, *_all*, *body*) and
lays them out in labeled grids. Also harvests name-leak evidence from
texture entry names (e.g. slot 001 has rock_me / rock__grow; slot 000
has hhh_* — the same kind of evidence that confirmed Triple H).

Writes /data/wmxix/out/contact/face-contact-N.png + slot-index.json.
"""
import json, os, re
from PIL import Image, ImageDraw, ImageFont

MAN = '/data/wmxix/out/wrestler-tex-manifest.json'
TEXDIR = '/data/wmxix/out/wrestler-tex'
OUT = '/data/wmxix/out/contact'
GENERIC = {'face', 'head', 'body', 'arm', 'leg', 'foot', 'hand', 'mouth',
           'tooth', 'blood', 'cloth', 'leather', 'kami', 'me', 'usi',
           'waists', 'pants', 'pad', 'all', 'tatto', 'grow', 'dummy',
           'skin', 'g', 'c', 'm', 'gr', '1p', '2p', 'b', 'e', 'f'}


def slot_of(path):
    m = re.search(r'/(\d{3})_(\d)\.tex$', path)
    return (m.group(1), int(m.group(2))) if m else (None, None)


def is_blank(path):
    """True if the PNG is nearly uniform (a placeholder, not a face)."""
    try:
        im = Image.open(path).convert('L')
        px = list(im.getdata())
        mean = sum(px) / len(px)
        var = sum((v - mean) ** 2 for v in px) / len(px)
        return var ** 0.5 < 5.0
    except OSError:
        return True


def pick_face(entries, base):
    """Best face-like entry for one .tex file. Patterns in order:
    face, kao (JP face), mae (JP front), head, _all, body. The m_
    variants are tried too (slot 000's real face is m_face; plain
    face is a blank placeholder). Blank images are skipped."""
    names = [r['entry'] for r in entries if 'w' in r]

    def cands(pat):
        out = [n for n in names if pat in n.lower()]
        # prefer non-m_ first, then m_; largest first within each group
        def key(n):
            size = next((r['w'] * r['h'] for r in entries
                         if r['entry'] == n), 0)
            m = 1 if n.lower().startswith('m_') or '_m0' in n.lower() \
                or n.lower().startswith('m0') else 0
            return (m, -size)
        return sorted(out, key=key)

    for pat in ('face', 'kao', 'mae', 'head', '_all', 'body'):
        for n in cands(pat):
            p = os.path.join(TEXDIR, base, n + '.png')
            if os.path.exists(p) and not is_blank(p):
                return n
    return None


def name_evidence(entries):
    """Person-name signal: the prefix before a body-part suffix
    (_kao/_mae/_me/_KE*/__grow/_body/_arm...), excluding slot codes
    (c001, m030...) and generic prefixes. E.g. booker_kao -> booker,
    big_me -> big, rock__grow -> rock, hhh_body -> hhh."""
    names = set()
    for r in entries:
        e = r.get('entry', '')
        m = re.match(r'^([A-Za-z]+)_(kao|mae|me|KE\d+|grow|body|arm|leg|'
                     r'foot|hand|head|top|usi|back|waists)',
                     e)
        if m:
            pre = m.group(1).lower()
            if not re.match(r'^[cm]\d+$', pre) and pre not in ('g', 'c', 'm'):
                names.add(pre)
        m2 = re.match(r'^([A-Za-z]+)__grow$', e)
        if m2:
            names.add(m2.group(1).lower())
        if 'nwo' in e.lower():
            names.add('nwo')
    return sorted(names)


def main():
    os.makedirs(OUT, exist_ok=True)
    man = json.load(open(MAN))
    slots = {}
    for path, entries in man['files'].items():
        slot, var = slot_of(path)
        if slot is None:
            continue
        if slot not in slots or var < slots[slot][0]:
            slots[slot] = (var, path, entries)
    print(f'{len(slots)} slots')
    index = {}
    cells = []
    for slot in sorted(slots):
        var, path, entries = slots[slot]
        base = os.path.basename(path)[:-4]
        face = pick_face(entries, base)
        ev = name_evidence(entries)
        fpath = os.path.join(TEXDIR, base, face + '.png') if face else None
        if fpath and not os.path.exists(fpath):
            fpath = None
        index[slot] = {'variant': var, 'face_entry': face,
                       'face_file': fpath, 'name_evidence': ev}
        cells.append((slot, fpath, ev))
    with open(os.path.join(OUT, 'slot-index.json'), 'w') as f:
        json.dump(index, f, indent=1, sort_keys=True)
    # name-leak summary
    print('slots with name-like evidence:')
    for slot, fpath, ev in cells:
        if ev:
            print(f'  {slot}: {", ".join(ev)}')
    print('slots with NO face image:',
          [s for s, p, e in cells if p is None])
    # contact sheets: 4 cols, 7 rows per sheet
    try:
        font = ImageFont.truetype(
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
        small = ImageFont.truetype(
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    except OSError:
        font = ImageFont.load_default()
        small = font
    CW, CH, PAD = 270, 200, 10
    COLS, ROWS = 4, 7
    per_sheet = COLS * ROWS
    for si in range(0, len(cells), per_sheet):
        chunk = cells[si:si + per_sheet]
        W = COLS * (CW + PAD) + PAD
        H = ROWS * (CH + PAD) + PAD + 40
        sheet = Image.new('RGB', (W, H), 'white')
        d = ImageDraw.Draw(sheet)
        d.text((PAD, 8), f'WMXIX wrestler faces — slots '
               f'{chunk[0][0]}..{chunk[-1][0]} (sheet {si // per_sheet + 1})',
               fill='black', font=font)
        for k, (slot, fpath, ev) in enumerate(chunk):
            r, c = divmod(k, COLS)
            x = PAD + c * (CW + PAD)
            y = 40 + PAD + r * (CH + PAD)
            d.rectangle([x, y, x + CW, y + CH], outline='#888888')
            if fpath:
                im = Image.open(fpath).convert('RGB')
                im.thumbnail((CW - 8, 128))
                sheet.paste(im, (x + 4, y + 4))
            label = f'slot {slot}'
            if slot == '000':
                label += ' = Triple H'
            while d.textlength(label, font=font) > CW - 8 and len(label) > 8:
                label = label[:-1]
            d.text((x + 4, y + 138), label, fill='black', font=font)
            if ev:
                evline = 'tex: ' + ', '.join(ev)
                while d.textlength(evline, font=small) > CW - 8 \
                        and len(evline) > 8:
                    evline = evline[:-1]
                d.text((x + 4, y + 164), evline, fill='#555555', font=small)
        out = os.path.join(OUT, f'face-contact-{si // per_sheet + 1}.png')
        sheet.save(out)
        print(f'wrote {out} ({len(chunk)} slots)')


if __name__ == '__main__':
    main()
