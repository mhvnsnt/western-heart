from PIL import Image
import colorsys, os

SRC = os.path.expanduser("~/workspace/game-reverse-engineering/tekken7/king")
DST = os.path.expanduser("~/workspace/game-reverse-engineering/tekken7/king/p2")

def load(n): return Image.open(f"{SRC}/{n}").convert("RGB")
def save(img, n): img.save(f"{DST}/{n}")

def px_recolor(img, fn):
    w, h = img.size
    src = img.load()
    out = Image.new("RGB", (w, h))
    dst = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = src[x, y]
            hh, ss, vv = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            h2, s2, v2 = fn(hh, ss, vv)
            r2, g2, b2 = colorsys.hsv_to_rgb(h2, s2, v2)
            dst[x, y] = (int(r2*255), int(g2*255), int(b2*255))
    return out

def to_black(ss, vv, vscale=0.16):
    return (0.0, ss*0.12, vv*vscale)
def to_bronze(ss, vv, vbase=0.30, vscale=1.0):
    return (0.075, 0.68, min(1.0, vbase + vv*vscale))
def to_red(ss, vv):
    return (0.0, 0.85, min(1.0, 0.25 + vv*0.6))

def is_blue(h, s): return 0.50 <= h <= 0.75 and s > 0.22
def is_gold(h, s): return 0.07 <= h <= 0.17 and s > 0.30
def is_cyan(h, s): return 0.44 <= h <= 0.56 and s > 0.35
def is_dark(v): return v < 0.28

# 1. PantsLower: blue tights -> black, navy designs -> bronze
img = load("King_PantsLower_D.png")
def f1(h, s, v):
    if s < 0.20 and v > 0.45: return to_bronze(s, v, 0.45, 1.2)   # white highlights -> bronze
    if is_blue(h, s) and is_dark(v): return to_bronze(s, v, 0.42, 1.5)
    if is_blue(h, s): return to_black(s, v)
    return (h, s, v)
save(px_recolor(img, f1), "King_PantsLower_P2_D.png")

# 2. PantsUpper: gold trunks -> black, black designs -> bronze
img = load("King_PantsUpper_D.png")
def f2(h, s, v):
    if is_dark(v): return to_bronze(s, v, 0.30, 1.0)
    if is_gold(h, s): return to_black(s, v)
    return (h, s, v)
save(px_recolor(img, f2), "King_PantsUpper_P2_D.png")

# 3. BootProtector1: gold -> black, dark borders -> dark red
img = load("King_BootProtector1_D.png")
def f3(h, s, v):
    if is_dark(v) and 0.0 <= h <= 0.15: return to_red(s, v)
    if is_dark(v): return to_black(s, v)
    if is_gold(h, s): return to_black(s, v)
    return (h, s, v)
save(px_recolor(img, f3), "King_BootProtector1_P2_D.png")

# 4. BootProtector2: gold/brown -> black, cyan MEXICO -> red, studs -> bronze
img = load("King_BootProtector2_D.png")
def f4(h, s, v):
    if is_cyan(h, s): return to_red(s, v)
    if is_dark(v): return to_black(s, v)
    if is_gold(h, s) or (0.04 <= h <= 0.12 and s > 0.25):
        # bright small studs -> bronze, else black
        if v > 0.55: return to_bronze(s, v, 0.35, 0.8)
        return to_black(s, v)
    return (h, s, v)
save(px_recolor(img, f4), "King_BootProtector2_P2_D.png")

# 5. FootAcc: navy -> black, keep white
img = load("King_FootAcc_D.png")
def f5(h, s, v):
    if is_blue(h, s): return to_black(s, v)
    return (h, s, v)
save(px_recolor(img, f5), "King_FootAcc_P2_D.png")

# 6. PantsLogo: cyan KING text -> bronze, black stays
img = load("King_PantsLogo_D.png")
def f6(h, s, v):
    if is_cyan(h, s): return to_bronze(s, v, 0.35, 0.9)
    return (h, s, v)
save(px_recolor(img, f6), "King_PantsLogo_P2_D.png")

# 7. Buckles: gold -> bronze
img = load("King_Buckles_D.png")
def f7(h, s, v):
    if is_gold(h, s): return to_bronze(s, v, 0.32, 0.9)
    return (h, s, v)
save(px_recolor(img, f7), "King_Buckles_P2_D.png")

print("recolored:", sorted(os.listdir(DST)))
