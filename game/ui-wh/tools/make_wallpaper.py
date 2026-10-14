"""Derive the Western Heart menu wallpaper from the owner's existing menu art.
Original game/assets/ui/title-bg.png is read-only input and is never modified.
Transform: upscale + heavy blur (source characters become abstract light),
indigo/crimson/gold duotone, the original logo band painted over, Pantera (rendered
from his own GLB) composited as the hero, and Western Heart universe text in
Japanese styling.  Output: game/ui-wh/art/wallpaper_wh.png
Run: python3 game/ui-wh/tools/make_wallpaper.py
"""
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps, ImageDraw, ImageFont, ImageChops
G = Path(__file__).resolve().parents[2]
SRC = G / "assets/ui/title-bg.png"
OUT = G / "ui-wh/art/wallpaper_wh.png"
HERO = G / "ui-wh/portraits/pantera_full.png"
JP = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
W, H = 1920, 1080

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
hero = hero.resize((int(hero.width * 1.05), int(hero.height * 1.05)), Image.LANCZOS)
shadow = Image.new("RGBA", hero.size, (0, 0, 0, 0)); shadow.putalpha(hero.getchannel("A").filter(ImageFilter.GaussianBlur(18)))
x, y = int(W*0.60), H - hero.height + 40
bg.paste(shadow, (x + 18, y + 10), shadow); bg.paste(hero, (x, y), hero)
# universe text, Japanese styling (vertical kanji)
d = ImageDraw.Draw(bg)
f = ImageFont.truetype(JP, 150)
for i, ch in enumerate("西部の心"):
    d.text((W - 190, 60 + i*165), ch, font=f, fill="#f4e6c8", stroke_width=4, stroke_fill="#2a0612")
f2 = ImageFont.truetype(JP, 34)
d.text((W*0.33, H - 70), "九つの魂 ・ 東の心 ・ 西の心", font=f2, fill="#f2b24a")
OUT.parent.mkdir(parents=True, exist_ok=True)
bg.save(OUT, optimize=True)
print("wrote", OUT, bg.size)
