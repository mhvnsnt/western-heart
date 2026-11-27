import sys
from PIL import Image, ImageDraw, ImageFont
d=sys.argv[1]; yaw=sys.argv[2]; out=sys.argv[3]; poses=sys.argv[4].split(',') if len(sys.argv)>4 else ['idle','walk','punch','kick','hit']
M=[('pantera-leoman','A1 LEO MAN'),('pantera-leopard-king','A2 LEOPARD KING'),('pantera','A3 CLASSIC rew.'),('pantera-snow-leopard','A4 SNOW LEOPARD (reweighted)'),('pantera-crimson-rage','A5 CRIMSON RAGE new rig'),('pantera-p2','A6 CLASSIC ALT (new rig)')]
T=300; H=18
try: f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',13)
except Exception: f=ImageFont.load_default()
S=Image.new('RGB',(T*len(poses),(T+H)*len(M)),(20,20,28)); dr=ImageDraw.Draw(S)
for r,(k,lab) in enumerate(M):
    for c,p in enumerate(poses):
        im=Image.open(f'{d}/{k}_{p}_y{yaw}.png').crop((100,120,800,820)).resize((T,T))
        S.paste(im,(c*T,r*(T+H)+H)); dr.text((c*T+4,r*(T+H)+2),f'{lab} · {p}',fill=(255,230,120),font=f)
S.save(out); print(out,S.size)
