import sys, itertools
sys.path.insert(0, '.')
from native import fk, draw
from render import frame_of
from PIL import Image, ImageDraw
out, spec, view = sys.argv[1], sys.argv[2], sys.argv[3]
side = 1
fr = frame_of(spec)
hyps = [(o, s) for o in itertools.permutations(range(3)) for s in itertools.product((1, -1), repeat=3)]
cols = 8; W, H = 170, 250
img = Image.new('RGB', (cols * W, ((len(hyps) + cols - 1) // cols) * H), 'white'); d = ImageDraw.Draw(img)
for k, (o, s) in enumerate(hyps):
    pos = fk(fr, o, s, side)
    draw(pos, img, (k % cols) * W + W // 2, (k // cols) * H + H - 15, view, scale=95)
    d.text(((k % cols) * W + 4, (k // cols) * H + 4), 'ord%s %s' % (''.join(map(str, o)), ''.join('+' if v > 0 else '-' for v in s)), fill=(0, 0, 0))
img.save(out); print(out)
