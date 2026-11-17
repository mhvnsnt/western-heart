"""items.py — the CLOTHING + ACCESSORIES phase item list (creation suite, 2026-11-02).

Two families:
  * kind 'shell'  — original CC0 garments GENERATED on each template body in Blender (shell_fit.py): the garment is the
    template's own skin surface over a region (picked by the body's bone weights + bone-axis cut lines), pushed out
    along the surface normal by a per-item offset, so it fits every template exactly, carries the body's own skin
    weights, and every body slider's shape key is rebuilt for it (offset re-applied along that key's normals).
  * kind 'mh'     — MakeHuman system assets (makehuman_system_assets_cc0.zip, license CC0 per asset in
    packs/makehuman_system_assets.json + the .mhclo header): fitted on the MakeHuman base mesh with the .mhclo
    formula, transferred onto the template (region affine ICP + surface-relative correction, mh_fit.py), then in
    Blender: Shrinkwrap OUTSIDE, Data Transfer skin weights, Surface Deform shape keys (mh_blender.py).

Player-facing names are generic (names law). Slots: t7_slot = Tekken 7 slot spine (menu-data.js ATTIRE_TREE),
equip_slot = the per-attire equip key (one item per key), wwe = WWE 2K CAW Attire > Clothing region / type
(menu-data.js WWE_ATTIRE_TREE).
"""

TEMPLATES = ['super-heavyweight', 'powerhouse', 'showman', 'technician', 'highflyer', 'luchador',
             'powerhouse-w', 'athletic-w', 'striker-w']

# offsets are metres along the skin normal. Layer order: base 2.5 mm < mid 4-7 mm < outer >= 9 mm.
ITEMS = [
    # ---------------- Upper Body ----------------
    dict(id='wh-top-compression', name='Compression Shirt', kind='shell', region='compression', offset=0.0035,
         t7='9', equip='9', wwe=('Upper Body', 'Shirts'), color=[0.06, 0.06, 0.07], rough=0.45),
    dict(id='wh-top-tee', name='Fitted Tee', kind='shell', region='tee', offset=0.008,
         t7='9', equip='9', wwe=('Upper Body', 'Shirts'), color=[0.85, 0.85, 0.85], rough=0.8),
    dict(id='wh-top-tank', name='Tank Top', kind='shell', region='tank', offset=0.0065,
         t7='9', equip='9', wwe=('Upper Body', 'Vests'), color=[0.75, 0.1, 0.1], rough=0.75),
    dict(id='wh-top-crop', name='Sports Top', kind='shell', region='crop', offset=0.0065,
         t7='9', equip='9', wwe=('Upper Body', 'Shirts'), color=[0.1, 0.2, 0.55], rough=0.5),
    dict(id='wh-singlet', name='Singlet', kind='shell', region='singlet', offset=0.005,
         t7='10', equip='10', wwe=('Upper Body', 'Singlets'), color=[0.1, 0.12, 0.45], rough=0.4),
    # ---------------- Lower Body ----------------
    dict(id='wh-trunks', name='Wrestling Trunks', kind='shell', region='trunks', offset=0.005,
         t7='11', equip='11', wwe=('Lower Body', 'Trunks'), color=[0.08, 0.08, 0.08], rough=0.35),
    dict(id='wh-tights-long', name='Long Tights', kind='shell', region='tights', offset=0.002,
         t7='11', equip='11', wwe=('Lower Body', 'Tights'), color=[0.55, 0.08, 0.08], rough=0.35),
    dict(id='wh-shorts-fight', name='Fight Shorts', kind='shell', region='shorts', offset=0.011,
         t7='11', equip='11', wwe=('Lower Body', 'Bottoms'), color=[0.12, 0.12, 0.14], rough=0.8),
    # ---------------- Hands ----------------
    dict(id='wh-gloves-mma', name='Open-Finger Gloves', kind='shell', region='gloves_open', offset=0.0045,
         t7='H', equip='H', wwe=('Arms & Hands', 'Gloves'), color=[0.08, 0.08, 0.08], rough=0.35),
    dict(id='wh-gloves-full', name='Full Gloves', kind='shell', region='gloves_full', offset=0.0035,
         t7='H', equip='H', wwe=('Arms & Hands', 'Gloves'), color=[0.12, 0.08, 0.06], rough=0.45),
    # ---------------- Feet ----------------
    dict(id='wh-boots-knee', name='Knee-High Boots', kind='shell', region='boots_knee', offset=0.009,
         t7='F', equip='F', wwe=('Legs & Feet', 'Boots'), color=[0.06, 0.06, 0.06], rough=0.3),
    dict(id='wh-boots-ankle', name='Ankle Boots', kind='shell', region='boots_ankle', offset=0.008,
         t7='F', equip='F', wwe=('Legs & Feet', 'Boots'), color=[0.22, 0.13, 0.07], rough=0.4),
    dict(id='mh-shoes-sneaker', name='Running Sneakers', kind='mh', src='clothes/shoes05', region='feet',
         t7='F', equip='F', wwe=('Legs & Feet', 'Shoes'), color=[0.85, 0.85, 0.85], rough=0.6),
    dict(id='mh-shoes-boot', name='Work Boots', kind='mh', src='clothes/shoes03', region='feet',
         t7='F', equip='F', wwe=('Legs & Feet', 'Boots'), color=[0.2, 0.2, 0.2], rough=0.5),
    dict(id='mh-shoes-dress', name='Dress Shoes', kind='mh', src='clothes/shoes01', region='feet',
         t7='F', equip='F', wwe=('Legs & Feet', 'Shoes'), color=[0.45, 0.25, 0.12], rough=0.35),
    dict(id='mh-shoes-trainer', name='Street Trainers', kind='mh', src='clothes/shoes06', region='feet',
         t7='F', equip='F', wwe=('Legs & Feet', 'Shoes'), color=[0.25, 0.3, 0.6], rough=0.6),
    # ---------------- Accessories ----------------
    dict(id='wh-kneepads', name='Knee Pads', kind='shell', region='kneepads', offset=0.0115, puff=0.014,
         t7='13', equip='13K', wwe=('Legs & Feet', 'Knee Pads'), color=[0.08, 0.08, 0.08], rough=0.4, acc=True),
    dict(id='wh-elbowpads', name='Elbow Pads', kind='shell', region='elbowpads', offset=0.008, puff=0.01,
         t7='12', equip='12E', wwe=('Arms & Hands', 'Elbow Pads'), color=[0.08, 0.08, 0.08], rough=0.4, acc=True),
    dict(id='wh-wrist-tape', name='Wrist Tape', kind='shell', region='wrist', offset=0.007,
         t7='12', equip='12W', wwe=('Arms & Hands', 'Wrist Tape'), color=[0.92, 0.92, 0.9], rough=0.85, acc=True),
    dict(id='wh-armbands', name='Arm Bands', kind='shell', region='armbands', offset=0.006,
         t7='12', equip='12A', wwe=('Arms & Hands', 'Arm Bands'), color=[0.75, 0.6, 0.1], rough=0.4, acc=True),
    dict(id='wh-headband', name='Headband', kind='shell', region='headband', offset=0.004,
         t7='4', equip='4', wwe=('Headgear', 'Head Accessories'), color=[0.75, 0.1, 0.1], rough=0.8, acc=True),
    dict(id='wh-belt', name='Waist Belt', kind='shell', region='belt', offset=0.013,
         t7='13', equip='13B', wwe=('Lower Body', 'Belts'), color=[0.12, 0.08, 0.05], rough=0.35, acc=True),
    dict(id='mh-hat-fedora', name='Fedora', kind='mh', src='clothes/fedora01', region='head',
         t7='1', equip='1', wwe=('Headgear', 'Headwear'), color=[0.3, 0.3, 0.32], rough=0.7, acc=True),
    dict(id='mh-hat-fedora-tilt', name='Tilted Fedora', kind='mh', src='clothes/fedora_cocked', region='head',
         t7='1', equip='1', wwe=('Headgear', 'Headwear'), color=[0.15, 0.12, 0.1], rough=0.7, acc=True),
]

BY_ID = {i['id']: i for i in ITEMS}
