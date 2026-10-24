# Deep Body Morphing Research — Per-Part Granularity
**Date:** 2026-10-23  
**Owner directive (verbatim):** "what games had like deepest real specific morphing like glute and um breast and like type morphing and like where you can do them individually or like um per body part and area where like you can get really specific really real specific shapes and like sizes of different body parts... any open source or like higher level industry standard things that are free that we can wire up that may even be outside of video games if they're better and deeper"

**Owner addendum:** "for like stomach and different face parts and really specific body parts... customization and morphing."

## TL;DR — The Winner Is Daz Studio (free) + Its Morph Dial System

Nothing in video games touches **Daz Studio's Genesis morph dial system** for per-body-part specificity. Thousands of dials, anatomically named, individually controllable per side (L/R). Daz Studio itself is **free**. The technique (blendshape morph targets + controller dials) is directly portable to our creation suite.

**Combined with:** MetaHuman (Epic, free — 700+ head bones, 600+ face morphs), MB-Lab (open source, hundreds of params), and Blender shape keys (the underlying tech).

---

## 1. Daz Studio — Deepest Per-Part Morphing in Existence

### How it works
- Genesis figures ship with **thousands of morph dials** — each dial is a blendshape target on the mesh
- Dials are organized by body region → anatomical structure → side (L/R)
- **ERC Freeze**: combine any set of dialed morphs into a single controller dial (e.g. "Figure Height" drives all *length morphs at once)
- Daz Studio is **free**; base Genesis figures are free

### Breast morphs (documented examples)
| Dial | Control |
|------|---------|
| Breasts Size | Overall volume |
| Breasts Up-Down / Left / Right | Vertical position, per side |
| Breasts Side-Side / Left / Right | Horizontal position, per side |
| Breasts Hang Forward / Left / Right | Projection angle, per side |
| Breasts Flatten / Left / Right | Compression, per side |
| Breasts In-Out | Toward/away from center |
| Breasts Cleavage | Cleavage depth |
| Breasts Implants / Natural / Heavy / Small | Shape archetypes |
| Areolae Depth / Diameter / Perk | Areola detail |
| Nipples / Depth / Diameter / Volume | Nipple detail |
| Pectorals Developed / Volume | Underlying muscle |

### Glute morphs (documented examples)
| Dial | Control |
|------|---------|
| Gluteus Maximus L/R | Main glute muscle, per side |
| Gluteus Medius L/R | Upper glute, per side |
| Glutes Width | Overall width |
| Glutes Upper Depth / Lower Depth | Projection zones |
| Glute Crease L/R | Under-crease definition |
| Glute swing L/R, flatten, expand | Pose-corrective shapes |
| Greater Trochanter L/R | Hip bone structure |
| Tensor Fascia Lata L/R | Outer thigh |

### Stomach / torso morphs (documented examples)
| Dial | Control |
|------|---------|
| Stomach Depth / Lower Depth | Belly projection zones |
| Rectus Abdominus / Height L/R | Ab muscle definition |
| External Oblique L/R | Side definition |
| Linea Alba Depth | Center line |
| Love Handles | Flank volume |
| Navel Depth / Hollow / Horizontal / Out / Size / Vertical | Belly button detail |
| Sternum Depth / Height | Chest bone |
| Costal Angle Arched / Pointed | Rib flare |

### Muscle-level morphs (documented examples)
Individual dials for: Levator Scapulae, Omohyoid, Sterno Mastoid, Trapezius, Pectoralis Clavicular/Major/Minor, Latissimus, Serratus Anterior, Teres Major/Minor, Biceps, Brachialis, Triceps (3 heads), Deltoid (3 heads), all forearm extensors/flexors — **per side, per muscle head**.

### Face morphs
Genesis face morphs go down to individual facial action units. Combined with MetaHuman's 600+ face morphs / 700+ head bones.

## 2. MetaHuman (Epic — Free)

- **600+ facial morphs**, 700+ head bones driving facial animation
- Body: preset blending (drag features from other presets) + per-part sliders
- Skin regions: redness/saturation/lightness per region, freckles, makeup
- Teeth, eyelashes, eyebrows, facial hair as separate systems
- **MetaMorph** (free Blender addon): edit MetaHuman DNA directly — author blendshapes in Blender, write back to DNA, FaceBoard control rig works in Blender
- Export path: MetaHuman → Blender → our pipeline

## 3. Open Source Morphing (recap + additions)

| System | License | Granularity |
|--------|---------|-------------|
| **MB-Lab** | Open source | Hundreds of params, measures editor, fuzzy-logic coherence |
| **MakeHuman** | Open source | Parametric sliders, areas-of-influence morphing |
| **Blender Shape Keys** | GPL (built-in) | **The underlying tech** — every morph dial in Daz is a shape key. Unlimited custom targets. |
| **MetaMorph** (MetaHuman→Blender) | Free | Blendshape authoring with standardized naming |

## 4. What We Build — The WH Morph Target Library

### Architecture: Daz dials → Blender shape keys → our UI

```
DAZ-STYLE MORPH DIAL          BLENDER SHAPE KEY           OUR UI
─────────────────────         ─────────────────           ──────
Breasts Size (0-100)     →    shape key target      →    slider
Breasts Up-Down L        →    shape key target      →    slider
Gluteus Maximus L        →    shape key target      →    slider
Stomach Depth            →    shape key target      →    slider
...thousands more        →    ...                   →    ...
                                                          ↓
CONTROLLER DIALS (ERC Freeze concept)
  "Bust Size" → drives Breasts Size + Up-Down L/R + Cleavage...
  "Glute Shape" → drives Gluteus Maximus L/R + Width + Depth...
  "Abs" → drives Rectus Abdominus + Obliques + Linea Alba...
  "Face: Smile" → drives 12 individual face morphs...
```

### Granularity tiers
1. **Quick sliders** (controller dials): Bust, Glutes, Stomach, Muscle, Face — one dial each, drives many targets
2. **Per-part sliders** (SvR-style): Breast Size L/R, Glute Width, Stomach Depth... — individual dials
3. **Anatomical sliders** (Daz-level): Gluteus Maximus L, Rectus Abdominus Height R, Areolae Perk... — per-muscle/per-detail
4. **Direct manipulation** (BDO-style): grab the mesh point and drag

### Per-side (L/R) independence
Every bilateral dial gets L/R split — asymmetry is a feature (real bodies aren't symmetric).

### Face part morphing (individual)
Eyes (position/length/height/depth, per eye), eyebrows (depth/angle × 2, per brow), nose (width/height/length/angle/bridge/tip/nostrils), cheeks (length/height/width/thickness), mouth (length/height/depth/thickness/lip fullness upper/lower), jaw (length/height/thickness/outline), ears (length/height/angle × 2), chin, forehead — each independently morphable, then combined via controller dials (Smile, Frown, Surprised...).

## 5. Pull Plan

### From Daz Studio (free)
- [ ] Document the Genesis morph dial taxonomy (region → structure → side)
- [ ] Study ERC Freeze controller-dial technique → replicate as our controller system
- [ ] Study morph organization in the Shaping tab → our menu structure
- [ ] Base Genesis figures (free) as morph-target reference meshes

### From MetaHuman (free)
- [ ] 600+ face morph set as reference for our face target library
- [ ] MetaMorph Blender addon for blendshape authoring workflow
- [ ] Skin region system (redness/saturation/lightness per region)

### Build ourselves (Blender shape keys)
- [ ] WH morph target library: author shape keys on our base bodies at Daz-level granularity
- [ ] Controller dial system (ERC Freeze equivalent)
- [ ] Per-side L/R split for all bilateral dials
- [ ] 4-tier UI (quick → per-part → anatomical → direct manipulation)

## 6. Why This Beats Every Game

No shipped game offers per-muscle-head morphing with L/R independence. Daz does — and it's free. By porting the **dial architecture** (not the assets) onto our fighters via Blender shape keys, our creation suite gets deeper body morphing than Black Desert, Saints Row, or any WWE game ever shipped.

## Sources
- Daz3d.com: Muscularity Morphs for Genesis 9 (full dial list), Genesis Evolution Shapes Bundle (86 partial body morphs documented), Shape Shift for Genesis 3 forum (breast/glute morph wishlist), Breast & Glute movement control thread
- Unreal Engine forums: MetaMorph (customize MetaHumans entirely in Blender)
- Reallusion forums: CC-to-MetaHuman morph mapping (700+ head bones, 600+ morphs)
- Unreal University / lilys.ai / irendering.net: MetaHuman Creator tutorials
