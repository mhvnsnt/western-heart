"""Paint T13 ('XIV' serif numerals, her LEFT upper chest) and T14 (small
ankh/anchor-like symbol, centre sternum) into Parvati_Torso.png.
Geometry comes from work/tattoo_uv.json (Blender raycast surface + UV affine).
Ink: near-black warm grey, alpha ~0.85, mask-limited to nearby torso faces.
"""
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = '/home/hatch/workspace/_pilot2-v2-20261108'
INK = (22, 17, 13)
tex = Image.open(f'{BASE}/tex/Parvati_Torso.png').convert('RGB')
W = tex.size[0]
uvj = json.load(open(f'{BASE}/work/tattoo_uv.json'))

def uv_to_px(u, v):
    return np.array([u * W, (1 - v) * W])

def affine_for(name):
    d = uvj[name]
    P0 = uv_to_px(d['uv'][0] % 1.0 if d['uv'][0] > 1 else d['uv'][0], d['uv'][1])
    # handle wrapped U: use raw u for gradient math, then mod the origin into [0,1)
    du_dx = np.array([d['duv_dx'][0] * W, -d['duv_dx'][1] * W])   # px per metre along +x
    du_dz = np.array([d['duv_dz'][0] * W, -d['duv_dz'][1] * W])   # px per metre along +z
    return P0, du_dx, du_dz

def mask_image(name):
    d = uvj[name]
    m = Image.new('L', (W, W), 0)
    dr = ImageDraw.Draw(m)
    for poly in d['mask_polys']:
        pts = []
        for (u, v) in poly:
            uu = u - 1.0 if u > 1.0 else u
            p = uv_to_px(uu, v)
            pts.append((float(p[0]), float(p[1])))
        dr.polygon(pts, fill=255)
    return m

def warp_glyph(glyph_rgba, P0, ax, az):
    """glyph_rgba drawn in tangent space: x right (metres via glyph_w_m),
    y DOWN in glyph = -z (up on body = +z => glyph top toward +z).
    Returns full-size RGBA layer."""
    gw, gh = glyph_rgba.size
    # glyph pixel -> local metres: lx = (gx - gw/2)/ppm, lz = (gh/2 - gy)/ppm
    ppm = glyph_rgba.info['ppm']
    A = np.stack([ax, az], axis=1)  # 2x2: local (lx,lz) -> px offset
    Ainv = np.linalg.inv(A)
    layer = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    # PIL AFFINE: input = M @ output + b ; we need glyph coords from texture px
    # local = Ainv @ (px - P0); glyph_px = (lx*ppm + gw/2, gh/2 - lz*ppm)
    M = np.array([[1, 0], [0, -1]]) @ (Ainv * ppm)
    b = np.array([gw / 2, gh / 2]) - M @ P0
    data = (M[0, 0], M[0, 1], b[0], M[1, 0], M[1, 1], b[1])
    warped = glyph_rgba.transform((W, W), Image.AFFINE, data, Image.BICUBIC)
    layer.alpha_composite(warped)
    return layer

# ---------------- T13: "XIV" serif ----------------
ppm = 30000  # px per metre in glyph space (30 px/mm)
gw, gh = int(0.036 * ppm), int(0.016 * ppm)
g = Image.new('RGBA', (gw, gh), (0, 0, 0, 0))
dr = ImageDraw.Draw(g)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', int(0.0105 * ppm))
dr.text((gw / 2, gh / 2), 'XIV', font=font, fill=INK + (218,), anchor='mm')
g = g.filter(ImageFilter.GaussianBlur(1.2))
g.info['ppm'] = ppm
P0, ax, az = affine_for('T13')
layer = warp_glyph(g, P0, ax, az)
m = mask_image('T13')
layer.putalpha(Image.composite(layer.split()[3], Image.new('L', (W, W), 0), m))
tex = Image.alpha_composite(tex.convert('RGBA'), layer).convert('RGB')
print('T13 painted at px', P0)

# ---------------- T14: ankh/anchor symbol ----------------
gw2, gh2 = int(0.013 * ppm), int(0.021 * ppm)
g2 = Image.new('RGBA', (gw2, gh2), (0, 0, 0, 0))
d2 = ImageDraw.Draw(g2)
cx = gw2 / 2
sw = int(0.0016 * ppm)  # stroke ~1.6mm
# loop (ring) at top
r = int(0.0032 * ppm)
top = int(0.0012 * ppm)
d2.ellipse([cx - r, top, cx + r, top + 2 * r], outline=INK + (225,), width=sw)
# crossbar
bar_y = top + 2 * r + int(0.0012 * ppm)
bar_hw = int(0.0042 * ppm)
d2.line([cx - bar_hw, bar_y, cx + bar_hw, bar_y], fill=INK + (225,), width=sw)
# stem down with flared base (anchor flukes hint)
bot = gh2 - int(0.0008 * ppm)
d2.line([cx, bar_y, cx, bot], fill=INK + (225,), width=sw)
fl = int(0.0034 * ppm)
d2.line([cx - fl, bot, cx, bot - int(0.0028 * ppm)], fill=INK + (225,), width=sw)
d2.line([cx + fl, bot, cx, bot - int(0.0028 * ppm)], fill=INK + (225,), width=sw)
g2 = g2.filter(ImageFilter.GaussianBlur(1.0))
g2.info['ppm'] = ppm
P0b, axb, azb = affine_for('T14')
layer2 = warp_glyph(g2, P0b, axb, azb)
mb = mask_image('T14')
layer2.putalpha(Image.composite(layer2.split()[3], Image.new('L', (W, W), 0), mb))
tex = Image.alpha_composite(tex.convert('RGBA'), layer2).convert('RGB')
print('T14 painted at px', P0b)

tex.save(f'{BASE}/tex/Parvati_Torso_v2.png')
# verification crops
for nm, P in [('T13', P0), ('T14', P0b)]:
    x, y = int(P[0]), int(P[1])
    tex.crop((x - 70, y - 70, x + 70, y + 70)).resize((420, 420), Image.NEAREST).save(f'{BASE}/crops/check_{nm}.png')
print('saved tex/Parvati_Torso_v2.png + check crops')
