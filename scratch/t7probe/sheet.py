import sys, itertools
sys.path.insert(0, '.')
from render import fk, frame_of, draw
from PIL import Image, ImageDraw
spec = sys.argv[2]; mode = sys.argv[3]; out = sys.argv[1]
fr = frame_of(spec)
hyps = []
for perm in itertools.permutations(range(3)):
    for signs in itertools.product((1, -1), repeat=3):
        hyps.append((perm, signs))
order = tuple(int(c) for c in sys.argv[4]) if len(sys.argv) > 4 else (0, 1, 2)
cols = 8; W, H = 170, 230
img = Image.new('RGB', (cols*W, ((len(hyps)+cols-1)//cols)*H), 'white'); d = ImageDraw.Draw(img)
for k, (perm, signs) in enumerate(hyps):
    pos = fk(fr, perm, signs, order, mode)
    ox, oy = (k % cols)*W + W//2, (k//cols)*H + H - 20
    draw(pos, img, ox, oy, 'side', scale=90)
    d.text(((k % cols)*W + 4, (k//cols)*H + 4), '%s %s' % (''.join(map(str, perm)), ''.join('+' if s > 0 else '-' for s in signs)), fill=(0, 0, 0))
img.save(out)
print(out, len(hyps))
