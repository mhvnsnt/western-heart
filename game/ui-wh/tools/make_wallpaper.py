"""Derive the Western Heart menu wallpaper from the owner's existing menu art.
Original game/assets/ui/title-bg.png is read-only input and is never modified.
Transform: upscale + heavy blur (source characters become abstract light),
indigo/crimson/gold duotone, the original logo band painted over, Pantera (rendered
from his own GLB) composited as the hero, and Western Heart universe text in
Japanese styling (purple パンテーラ / 黒豹, owner 2026-10-14).  Output: game/ui-wh/art/wallpaper_wh.png
Run: python3 game/ui-wh/tools/make_wallpaper.py            (v2 lunge -> art/wallpaper_wh.png, unchanged default)
     python3 game/ui-wh/tools/make_wallpaper.py v3         (v3 folded -> art/wallpaper_wh_v3.png)
v3 hero is cropped with a frame box offset from v2's, so the same scale factor and
the same camera-space anchor are used; only the arms differ (see TITLE_VARIANTS.md).
"""
import sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps, ImageDraw, ImageFont, ImageChops
G = Path(__file__).resolve().parents[2]
SRC = G / "assets/ui/title-bg.png"
OUT = G / "ui-wh/art/wallpaper_wh.png"
HERO = G / "ui-wh/portraits/pantera_hero.png"   # P1 attire, grab pose (lab/game/tools/render_title_hero.gd)
JP = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
W, H = 1920, 1080
VARIANT = sys.argv[1] if len(sys.argv) > 1 else "v2"
# hero crop boxes inside the 900x1200 render of render_title_hero.gd (same camera for both)
V2_BOX = (235, 144, 844, 1144)          # pantera_hero.png = grab@0.35 cropped to this box
HERO_BOX = V2_BOX
if VARIANT == "v3":
    HERO = G / "ui-wh/portraits/pantera_hero_folded.png"   # idle@0.0 (the v1 arms-folded pose), title camera
    OUT = G / "ui-wh/art/wallpaper_wh_v3.png"
    HERO_BOX = (213, 131, 844, 1144)

src = Image.open(SRC).convert("RGB")
# fill a 16:9 frame: scale to width, crop the middle (drops the source logo band at the top)
s = src.resize((W, int(src.height * W / src.width)), Image.LANCZOS)
top = int(s.height * 0.30)
bg = s.crop((0, top, W, top + H)).filter(ImageFilter.GaussianBlur(28))
gray = ImageOps.autocontrast(ImageOps.grayscale(bg))
bg = ImageOps.colorize(gray, black="#0b0518", mid="#5a1030", white="#f2b24a")
# vignette
v = Image.new("L", (W, H), 0); d = ImageDraw.Draw(v)
for i in range(60):
    d.ellipse((-W*0.2 + i*12, -H*0.3 + i*8, W*1.2 - i*12, H*1.3 - i*8), fill=int(i*255/60))
bg = Image.composite(bg, Image.new("RGB", (W, H), "#05020c"), v.filter(ImageFilter.GaussianBlur(60)))
# sun disc behind hero (Eastern-Mind / hinomaru nod, in crimson)
d = ImageDraw.Draw(bg)
d.ellipse((W*0.56, H*0.10, W*0.56 + 620, H*0.10 + 620), fill="#9e1b2c")
bg = bg.filter(ImageFilter.GaussianBlur(1))
# hero from the owner's GLB
hero = Image.open(HERO).convert("RGBA")
k = (H * 0.98) / (V2_BOX[3] - V2_BOX[1])   # v2 scale for every variant
hero = hero.resize((int(hero.width * k), int(hero.height * k)), Image.LANCZOS)
shadow = Image.new("RGBA", hero.size, (0, 0, 0, 0)); shadow.putalpha(hero.getchannel("A").filter(ImageFilter.GaussianBlur(18)))
x0, y0 = int(W*0.50), H - int((V2_BOX[3] - V2_BOX[1]) * k)
x, y = x0 + int((HERO_BOX[0] - V2_BOX[0]) * k), y0 + int((HERO_BOX[1] - V2_BOX[1]) * k)
bg.paste(shadow, (x + 18, y + 10), shadow); bg.paste(hero, (x, y), hero)
# universe text, Japanese styling (vertical kanji)
d = ImageDraw.Draw(bg)
PURPLE = "#b469ff"   # owner: Japanese lettering in purple, reading Pantera
f = ImageFont.truetype(JP, 140)
for i, ch in enumerate("パンテーラ"):
    if ch == "ー":   # long-vowel mark turns vertical in tategaki
        d.rectangle((W - 130, 70 + i*160 + 10, W - 118, 70 + i*160 + 130), fill=PURPLE, outline="#14041f", width=3); continue
    d.text((W - 190, 70 + i*160), ch, font=f, fill=PURPLE, stroke_width=5, stroke_fill="#14041f")
f2 = ImageFont.truetype(JP, 34)
d.text((W*0.33, H - 70), "黒豹 ・ 豹の魂", font=f2, fill=PURPLE, stroke_width=2, stroke_fill="#14041f")
OUT.parent.mkdir(parents=True, exist_ok=True)
bg.save(OUT, optimize=True)
print("wrote", OUT, bg.size)
