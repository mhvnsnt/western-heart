# DEEP MORPHING DIALS V2 — Daz Architecture, MetaHuman DNA, Face-Part Depth, Game Layer Systems, 2026 Tool Watch

Date: 2026-10-23 | Researcher: DoggByte (research subagent)
Companion docs: `docs/research/DEEP-BODY-MORPHING-RESEARCH.md` (#777 — Daz per-muscle L/R dials, MetaHuman basics), `docs/research/MORPHING-FREEDOM-RESEARCH.md` (#775 — SvR 2007 wins WWE slider race).
This doc goes DEEPER and WIDER. No rehash: every section below is new material.

---

## 1. Daz dial architecture — how dials actually compose

### 1.1 Morphs are vertex deltas; dials are additive linear controllers
In Daz Studio every morph asset is a per-vertex position delta stored in a **DSF** (Daz Scene Format, JSON) file. A dial (morph *property*) applies its delta scaled by the dial value, and dials **compose by addition** in the order they're evaluated: `final_pos = base + Σ(dial_value_i × delta_i)`. Dial values are typically 0–100% but can go negative and over-range; negative values invert the delta. That is the primitive our suite should copy: **shape-key-like additive blend of per-vertex deltas, driven by named float dials**.

### 1.2 ERC — Extended Remote Control (the composition layer #777 didn't cover)
ERC is Daz's graph that turns dials into a **dial → dial dependency network**:
- **Add / Multiply / Keyed ERC types.** Any property can be registered as a *controller* of any other. A Multiply controller scales its targets — the documented canonical example: the muscle-flexion set has a master **Flexion** dial, and every per-muscle flex morph is ERC-linked to it with Multiply, so setting Flexion to 0 zeroes the whole set regardless of the other controllers (the actual bend values).
- **ERC Freeze** bakes a set of current dial values into a NEW dial: set dials the way you want them at maximum, ERC-Freeze creates a new property, and at 0 all linked dials return to default while 50% gives the mid-ground ("dial spinning" — interpolation between frozen states is handled by Daz, including the 'tween' values). The Genesis "Basic Child" morph is built this way: it scales the figure down AND reworks bone structure dynamically.
- **Keyed ERC** drives morphs off animation timelines: animate N morphs across a timeline (each at 100% on its own frame range), then ERC-Freeze with "Keyed (Extract from Play Range)" to collapse the whole sequence into one dial. This is the Daz-native pattern for **dial sequencing**.

**Suite mapping:** ERC = a dependency graph between sliders. Two primitives we need in the creation suite:
1. `multiply-link(slave_dials[], master_dial)` — master at 0 forces slaves to 0 (the Flexion pattern).
2. `freeze-to-dial(dial_settings[])` — snapshot a full-body pose/dial state into one new slider (the "create character preset as dial" pattern).
Both are implementable in Blender as drivers between shape keys / custom properties, or baked at export as glTF extras.

Sources: [daz3d.com ERC Freeze](https://www.daz3d.com/forums/discussion/comment/6733501/), [controller morph dials](https://www.daz3d.com/forums/discussion/25846/how-do-i-make-a-controller-morph-dial-to-combine-genesis-morphs-in-daz-studio?srsltid=AfmBOopbXt7Z-oc5dD8aOU6xcl7H5mnNQCNwsopX5RJUC1Yf7BZAtswA), [Animating controller dials](https://www.daz3d.com/forums/discussion/307006/animating-controller-dials), [Content Creation Mastery modules 4–5](https://www.daz3d.com/daz-studio-content-creation-mastery-parts-4-and-5-rigging-morphing-props)

### 1.3 Joint Corrective Morphs (JCMs) — dials driven by pose, not sliders
#777 noted per-muscle dials; the deeper layer is **JCMs**: morphs that auto-fire as a function of bone *rotation*, not user sliders (e.g. bicep bulge as the elbow bends). Daz evaluates them from joint angles, which is exactly the mechanism behind "muscles flex when you pose". The open Diffeomorphic importer converts these for Blender; DS-side they are plain DSF morphs with angle-based activation channels.

**Suite mapping:** export-time JCMs become **bone-rotation drivers** on shape keys in Blender (standard `rotation_euler` driver variables), zero runtime cost in-engine once baked to pose-space deformation or driver curves.

### 1.4 Regional body dials — the existing dial library (beyond per-muscle L/R)
Genesis figures ship with regional dials that stack on top of per-muscle L/R dials. The Genesis Evolution Shapes bundle (123 head morphs, same architecture for body) shows the granularity pattern the suite should mirror:
- **Per-side asymmetry is real**: `Cheeks Dimple Crease L / R`, `Forehead Wrinkle L / R`, `Eyelids Bottom In Height / Out Height`, `Lip Lower ...`, all separate L/R dials. Any dial can be driven asymmetrically.
- **HD morphs**: high-density dials (e.g. `Cheekbones Arch Size HD`) that only affect subdivided geometry — i.e. LOD-aware dials. Relevant for our LOD chain.

Source: [Genesis Evolution: Shapes Bundle dial list](https://www.daz3d.com/genesis-evolution-shapes-bundle)

### 1.5 Which open formats carry Daz dials
- **DSF** (JSON): carries morph delta arrays + the property/ERC graph + JCM activation channels. Open by inspection; Daz's own EULA governs the *assets*, not the format.
- **Blender side**: **Diffeomorphic** (free, open-source, [diffeomorphic.blogspot.com](https://diffeomorphic.blogspot.com/)) imports G1–G8 fully rigged characters **including standard morphs (face/body/JCMs) as Blender shape keys**, converts iray materials to Cycles, and has "Easy Import DAZ" for one-click human import. Its workflow notes: import with morphs as *custom morphs* (shape keys) rather than baked into the DBZ if you want to re-fit outfits later; "Transfer Other Morphs" propagates body shape keys to clothes/hair. It does NOT import HD morphs or custom (vendor) morphs without extra steps ("Load Missing Morphs"). This is the proven open bridge for Daz dial → Blender shape-key work.
- **Licensing flags**: Daz *software/format knowledge* is free to use. Genesis base morphs ship with Daz Studio (free) but the **base figure geometry is NOT freely redistributable** — do not ship Genesis meshes. Vendor morph packs (e.g. the G9 Visage pack, Head Morph Resource Kits) are **paid, single-user licenses — never redistribute**. **Freebie dials** (e.g. Morphalynn's 127 head/face morphs for G3F, released "use for whatever purposes, commercial or non-commercial, don't repackage and call your own") are usable as reference/derivation sources with attribution, but still don't ship their vertex data in our repo — re-derive equivalent dials on our own base meshes. Rule of thumb for the suite: **learn the dial TAXONOMY from Daz, build the DELTAS ourselves** on our own topology.

Sources: [Diffeomorphic easy import](https://diffeomorphic.blogspot.com/2021/03/easy-import.html), [morphed character import](https://diffeomorphic.blogspot.com/2021/03/importing-morphed-character-without-dbz.html), [Morphalynn freebie terms](https://www.daz3d.com/forums/discussion/69268/morphalynn-127-head-and-face-morphs-for-g3f), [G3F freebie morph index](https://poserdazfreebies.miraheze.org/wiki/Genesis_3_Female/Faces_and_Morphs)

---

## 2. MetaHuman DNA pipeline — what transfers outside Unreal

### 2.1 The DNA file: a real, documented, open-readable format
Epic's **MetaHuman DNA Calibration** library (free, from Epic) exposes `.dna` files with:
- **DNACalib** (C++ with Python bindings): read/modify DNA — rename meshes, remove joints/blendshapes/LODs, edit blendshape delta values.
- **DNAViewer**: loads DNA into Maya as a functional facial rig, exportable to FBX.
- Data is organized in **layers**: Descriptor (~3 KB) → Definition (~131 KB) → Behavior (~10 MB) → Geometry (~191 MB; ~22 MB without blendshapes) — read only the layers you need.
- A DNA→JSON round-trip demo ships in the repo, so the format is fully inspectable without Unreal.

**Verdict: DNA is usable outside Unreal TODAY.** The pipeline value for us is not running MetaHumans in our engine — it's that DNA is a *complete, versioned, open-reader character-rig container*: mesh LODs + joint rig + FACS-grade blendshape set + RBF correctives, all addressable by name.

Sources: [cgchannel](https://www.cgchannel.com/2022/11/epic-games-releases-metahuman-dna-calibration-library/), [DNA Calibration docs](https://epicgames.github.io/MetaHuman-DNA-Calibration/index_.html), [dna_binary_to_json_demo.py](https://raw.githubusercontent.com/EpicGames/MetaHuman-DNA-Calibration/main//examples/dna_binary_to_json_demo.py)

### 2.2 The 2026 unlock: Blender-native DNA round-trip (MetaMorph)
As of Sept 2026, **REVO DNA** (Blender addon) and **MetaMorph / SkalinMetaMorph** (free tier + pro beta, Blender 5.2+, UE 5.7-verified) do the full loop **inside Blender**:
- Import any `.dna`, build the character in Blender; export back to a *valid* `.dna`.
- FaceBoard control rig works in Blender (same controls as Unreal); author blendshapes in Blender written straight into DNA with standardized naming (`jaw_open` → `head_lod0_mesh__jaw_open`).
- RBF corrective pose editor (shapes driven by joint rotation = the DNA equivalent of Daz JCMs).
- Per-joint-basis mirroring (naive X-flip gives wrong deformation; MetaMorph mirrors through each joint's real orientation basis), LOD-aware handling, custom-normals writeback.

**This beats the #777 finding.** The #777-era path was "DNA is Unreal/Maya-locked." As of 2026 the path is: **DNA → Blender (free, bidirectional) → FBX/glTF → our pipeline**, with the facial rig and all blendshapes surviving. Licensing: the DNACalib library is free from Epic; the *MetaHuman character assets themselves* are under Epic's MetaHuman license (usable in Unreal-engine projects; check current terms before shipping their mesh data — again, take the *system*, build our own deltas).

Sources: [REVO DNA release](https://blenderartists.org/t/released-revo-dna-metahuman-dna-editing-tools-for-blender/1653438), [MetaMorph thread (free version)](https://forums.unrealengine.com/t/customize-metahumans-entirely-in-blender/2740080), [PolyHammer Character DNA addon](https://www.polyhammer.com/meta-human-dna-addon)

### 2.3 What does NOT transfer
- The **RigLogic** real-time solver (the RBF/ML joint+blendshape evaluator) is Unreal-side; Blender tools reimplement enough to author, not to run in-game. Our engine would need its own RBF/blendshape evaluator (standard tech, not exotic).
- **Body DNA is the weak leg.** MetaHuman body morphing is far less tooled than the head: community tooling (Mesh Morpher, 2026) morphs full bodies via **Bonesnapshots + morph targets driven through animation post-process blueprints** — i.e. one float driving paired morph+bone snapshots, blended at runtime — rather than through DNA body dials. Head DNA is mature; body is "morph-target + snapshot" craft. For our suite this means: **adopt DNA-style architecture for the FACE, keep the BODY on the Daz/Blender shape-key + JCM-driver pattern** (Section 1), where the tooling is deepest.
- DNA geometry layer is ~191 MB per character with blendshapes — fine for authoring, strip aggressively for shipping.

Sources: [Mesh Morpher full-body MetaHuman morphing (2026)](https://meshmorpher.com/blog/morph-full-body-meta-humans-and-skeletons), [UE forums: body DNA export status](https://forums.unrealengine.com/t/ue-5-8-3-macos-arm64-metahuman-body-dna-export-crashes-pair-nullptr-assertion-in-map-h-inl-638-head-dna-succeeds/2834296)

### 2.4 glTF/Blender transfer assessment
| DNA concept | glTF/Blender equivalent | Transferable? |
|---|---|---|
| Blendshape deltas | `KHR` morph targets / Blender shape keys | **Yes — 1:1** |
| Joint rig | glTF skins / Blender armatures | **Yes** |
| RBF correctives (pose-driven shapes) | Blender drivers on shape keys | **Yes, re-author as drivers** |
| DNA layer stack | glTF extras + naming convention | Partial — convention, not format |
| FaceBoard controls | Blender custom rig UI / shape-key panel | Rebuild UI, keep naming |
| RigLogic solver | Engine-side blendshape evaluator | Reimplement (standard) |

---

## 3. Per-face-part dial depth — who goes deepest per part

### 3.1 Daz: the deepest *static* per-part library
Daz's morph catalog is the deepest per-part static dial set found:
- **Nose**: bridge depth/height/slope/width, bump, ridge, ridge width, septum depth/height/width, side-side, tip depth/height, tip up/down/wide (A/B/C variants), nostril flare/shape/tall, wings fleshy/twist/up — ~26+ dials on the nose alone (Genesis 3 Male Head Morph Resource Kit). G9 Visage pack adds nostril width, philtrum defined/narrow, septum down.
- **Lips**: upper/lower independently — size, depth, width, fuller, curve, centre up/down, points defined/width, corners pinch, lower centrepoint down; `Lips Thin`, `Lips Heart`, `Lips Square` as style dials. ~27 lip/mouth dials in the G3M kit.
- **Eyes**: upper/lower lid height + inner/outer height separately, fold down, heavy lids, smooth, puffy upper/lower, almond inner/outer, socket raise, underbrow pinch, lacrimals pinch/size, iris/cornea size — ~15+ dials.
- **Brow**: brow define/depth/width, brow bone large/wide, brow ridge full, brow centre/outer up — but these are mostly **symmetric**; per-side brow dials are thinner (the Evolution bundle gives L/R only for forehead *wrinkles*).
- **Ears**: size, depth, lobes attached/length/size, pinned, elf variants — modest depth (~8).
- **Jaw/chin**: jaw angle/corner width/curve/define/height/size, chin cleft/crease/depth/width/forward/pinch — good depth, but **per-side jaw/chin dials are rare**; asymmetry is usually achieved by posing, not dialing.

**Weakness: per-side (L/R) coverage is asymmetric in itself** — cheeks/lips/eyes have some L/R dials, nose/jaw/brow largely don't. For true per-side control Daz relies on the artist sculpting custom morphs.

Sources: [Genesis Evolution Shapes Bundle (123 dials)](https://www.daz3d.com/genesis-evolution-shapes-bundle), [MR G9 Visage (95 face morphs)](https://www.daz3d.com/mr-g9-visage-face-morphs), [G8M Head Morph Resource Kit 1](https://www.daz3d.com/genesis-8-male-head-morph-resource-kit-1), [G3M Head Morph Resource Kit (zonegfx mirror of dial list)](http://zonegfx.com/genesis-3-male-head-morph-resource-kit/)

### 3.2 FaceGen: deepest *parametric* face system (procedural, not dial-library)
FaceGen (Singular Inversions) is the reference for **parametric** faces rather than stacked dials:
- Ships **FACS-grade blendshape sets** (Animate model set = full FACS + extras), with a documented **ARKit→FaceGen→FACS mapping table** (52 ARKit shapes ↔ AU codes, incl. per-side variants: `eyeBlinkLeft/Right`, `mouthSmileLeft/Right`, `browDownLeft/Right`, `noseSneerLeft/Right`…).
- FaceGen Modeller exposes demographics (age/ethnicity/gender/caricature/asymmetry sliders) + per-feature Shape tab in the Bethesda-Oblivion/Skyrim/Fallout lineage — per-side control comes from the **asymmetry slider** (global) plus FACS blendshapes (local), not from per-part L/R dials.
- Verdict: **FaceGen wins on animation-grade per-side control (FACS blendshapes), Daz wins on static per-part sculpt dials.** The suite wants both: Daz-taxonomy static dials for the *creation* UI, FACS/ARKit-52 blendshape set for *expression/animation*.

Sources: [FaceGen Modeller manual (ARKit→FACS table)](http://facegen.com/modeller_manual.htm), [daz3d forum: FaceGen→Daz dial workflow](https://www.daz3d.com/forums/discussion/comment/3228891/)

### 3.3 MetaHuman: deepest *rig-driven* face (not dial-driven)
MetaHuman's face is driven by **~800 face joints + blendshapes through RigLogic**, authored via Move/Sculpt tools over a PCA face space — not by named per-part dials. Per-side control is native (joint-level), but there is no "nose tip up 0–100" dial to copy; the dial-equivalent is the **blendshape list** (standardized names like `jaw_open`). For the suite, MetaHuman contributes the **expression rig architecture**, not the creation-slider taxonomy.

### 3.4 Per-part depth ranking (creation dials)

| Face part | Deepest system | Notes |
|---|---|---|
| Nose (bridge/tip/nostrils) | **Daz** (~26 dials) | Bridge/tip/nostril/septum/wings all separate |
| Lips upper/lower | **Daz** (~27 dials) | Upper vs lower fully independent |
| Eyes (lids/sockets) | **Daz** (~15 dials) | Inner/outer lid heights separate |
| Brow ridge | Daz (moderate) | Mostly symmetric; FaceGen asymmetry slider covers skew |
| Ears | Daz (modest, ~8) | All systems thin here |
| Jaw/chin per-side | **None off-the-shelf** | Gap: custom L/R jaw+chin dials needed; MetaHuman joint rig does it at runtime, no creation dials |
| Expression per-side | **FaceGen/MetaHuman (FACS)** | ARKit-52 set is the standard to adopt |

**Recommendation:** adopt the Daz per-part dial *taxonomy* (names + groupings) as our slider spec, implement FACS/ARKit-52 as the *expression* layer, and author custom L/R jaw+chin dials to close the one gap none of them cover.

---

## 4. Clothing layer systems across games — toward a unified layer model

### 4.1 Tekken 7 — flat slot list with conflict rules
Slots: Head, Hair, Full-Face, Hair Accessory, Glasses, Make-up, **Upper Body, Lower Body, Entire Body**, Upper Accessory, Lower Accessory, Effects, Aura, Skin Tone, Mirroring. Conflict resolution is **exclusion-based**: conflicting pieces can't combine (full-face mask × make-up), and two accessory slots can't occupy the same body area. "Entire Body" overrides upper+lower. **No inner/outer stacking** — one item per slot, period. (T8 keeps the same philosophy: Full Body presets vs per-Part picks — Head, Glasses, Face Accessories, Upper Body, Lower Body, Shoes, 2 accessory slots; outfits trend toward locked full-body sets.)
Takeaway: simplest model; conflict = hard exclusion. Good for fighting-game readability, weak for fashion layering.

Sources: [Twinfinite T7 customization guide](https://twinfinite.net/guides/tekken-7-customize-character-how/), [Tekken Wiki: Customize](https://tekken.fandom.com/wiki/Customize), [diffsense: T8 editor breakdown](https://diffsense.com/finding-the-character-customization-tekken-8-main-menu-and-making-it-work-p5p)

### 4.2 Soulcalibur VI — region × layer matrix (the one to study hardest)
SC's Create-a-Soul is the deepest *fighting-game* layering system:
- **Per-region equipment with stackable layers**: torso historically splits into **Lower Torso / Mid Torso / Upper Torso** (SC3-era taxonomy surviving into later games: "Lower Torso: Bronze Brassiere / Mid Torso: Fighter's Robe / Upper Torso: Goddess Armor"), plus Head, Hair, Mask/Chin, Neck, Arms, Waist, Upper Legs, Lower Legs, Shins, Feet, Underwear.
- **Undergarments layer** (inner clothing + tattoos) sits under everything.
- **Special 1/2** slots (necklace, capes, tails, horns / faulds, belts) + **3 free-place accessories** (size/rotate/position anywhere, SC6).
- Clipping prevention is **artist-side**: items are authored to the layer matrix; the game does NOT auto-resolve — community notes lizardman/monster templates as the failure case where pieces clip because they were never authored for that body.
- Pattern/sticker layers on top of items for extra depth.

Takeaway: **region × layer (under/mid/upper) matrix + free-place accessories** is the proven fighting-game layering model. Its weakness (no runtime clipping solver) is exactly what our suite should fix with a hide/reveal + shrink-wrap pass at export.

Sources: [SC:BROKEN DESTINY equipment taxonomy (GameFAQs)](https://Gamefaqs.gamespot.com/psp/959863-soulcalibur-broken-destiny/faqs/59614), [SC3 creation guide w/ Lower/Mid/Upper torso](https://gamefaqs.gamespot.com/boards/927089-soulcalibur-iii/54236965), [SCV equipment categories](https://soulcalibur.fandom.com/wiki/Character_Creation/Soulcalibur_V), [Siliconera: SC6 creation suite](https://www.siliconera.com/soulcalibur-vi-creation-suite-works-best-when-you-try-to-stick-to-the-spirit-of-a-character/)

### 4.3 Cyberpunk 2077 — the cleanest inner/outer taxonomy
Slots as of 1.6+: **Head / Face / Outer Torso / Inner Torso / Legs / Feet / Outfit(Special)**. Inner Torso (t-shirts, bras, undershirts) and Outer Torso (jackets, vests, dresses) are **simultaneously worn** — true 2-deep torso layering, with clipping handled by authoring inner items to sit under outer silhouettes. Post-2.0 the **Wardrobe** (6 saved outfits, cosmetic-only, stats from cyberware) separates *appearance* from *stats* — the exact separation our suite needs between "look" and "fight data". Special Outfits lock all other slots (the Entire-Body override pattern, same as Tekken).
Takeaway: copy the **Inner/Outer Torso split** verbatim and the **wardrobe = appearance preset** concept.

Sources: [Cyberpunk Wiki: Clothing](https://cyberpunk.fandom.com/wiki/Cyberpunk_2077_Clothing), [Game8 slot table](https://game8.co/games/Cyberpunk-2077/archives/316176), [Wardrobe guide](https://holdtoreset.com/how-to-access-the-wardrobe-in-cyberpunk-2077/)

### 4.4 Final Fantasy XIV — slot-exclusion + base-slot locking (anti-pattern + one good idea)
5 slots: Head, Body, Hands, Legs, Feet. **No stacking** — instead, *multi-slot gear* (e.g. robes) **locks out** the slots it covers: a body piece can hide head/hands/legs/feet, and glamour projections onto multi-slot gear are restricted to the **base slot** only. Patch 7.1 added **Outfit Glamours** (condense a full set into one slot).
Takeaway: mostly an anti-pattern for us (locking reduces freedom), but the **base-slot rule** is worth stealing: any multi-region item declares a base slot; projections/overrides apply at the base slot; covered slots show empty unless explicitly layered.

Sources: [FFXIV Wiki: Armor](https://ffxiv.consolegameswiki.com/mediawiki/index.php?title=Armor&oldid=624566), [FFXIV Wiki: Glamours (multi-slot rules)](https://ffxiv.consolegameswiki.com/mediawiki/index.php?title=Glamours&oldid=1172533&mobileaction=toggle_view_mobile), [Outfit Glamours (7.1)](https://consolegameswiki.com/mediawiki/index.php?title=Outfit_Glamours&oldid=933339)

### 4.5 Baldur's Gate 3 — armor vs camp-clothes visibility toggle
Slots: Head, Body (armor), Hands, Feet, plus **Camp Clothes** (Clothes/Shoes/Underwear) with a **visibility toggle**: show camp clothes over armor while keeping armor stats. Helmet has show/hide/hide-in-dialogue states. Dye applies per-item via combine.
Takeaway: the **appearance-vs-stats visibility toggle** is the second vote (with Cyberpunk's Wardrobe) for separating look from data. Helmet visibility states are a clean pattern for any head-slot item.

Sources: [BG3 camp clothes guide](https://playerassist.com/where-to-find-the-best-camp-clothes-in-baldurs-gate-3/), [BG3 helmet visibility](https://scalacube.com/blog/baldurs-gate-3/how-to-change-clothes-in-baldurs-gate)

### 4.6 Code Vein 1/2 — deep face, shallow clothing
Code Vein's creation is face-first (asymmetric eyes, scars, face paint layers) with **template-based clothing**: pick a preset outfit, recolor per-part (collar/sleeves/chest separately), add gloves/boots/mask/cloaks, and stack **8 accessory slots** (CV1; CV2 expands to a 50-slot cost system). You **cannot** mix trousers/tops/shoes across templates.
Takeaway: per-part **recolor zones** on clothing items (collar/sleeve/chest as separate color regions) — adopt as our material-zone standard. The template lock-in is an anti-pattern for us.

Sources: [CV1 character creation (Fextralife)](https://codevein.wiki.fextralife.com/Character+Creation), [CV2 character creation (Fextralife)](https://codevein2.wiki.fextralife.com/Character+Creation), [PS Lifestyle: inner clothing colors](https://www.playstationlifestyle.net/2017/09/13/new-code-vein-character-customization-information-released/244)

### 4.7 UNIFIED LAYER MODEL — recommendation for the suite

```
Layer 0 — BODY (the morphed base mesh; dials from §1–3)
Layer 1 — UNDER (underwear/inner clothing/tattoos; SC undergarments)
Layer 2 — INNER (Cyberpunk Inner Torso generalized: shirts, bras, base layers)
Layer 3 — MID   (SC Mid Torso: main garments, pants, skirts)
Layer 4 — OUTER (Cyberpunk Outer Torso generalized: jackets, coats, armor, dresses)
Layer 5 — GEAR  (Tekken accessories / SC Special slots / CV accessories: belts, capes,
                 pauldrons, holsters — free-place, size/rotate/position)
Layer 6 — FX    (Tekken Effects/Aura; face paint/decals as overlay)
```

Rules (synthesized from all six games):
1. **Region × layer addressing**: every item declares `(region, layer)`; regions = Head, Face, Hair, Neck, Torso, Pelvis, UpperLeg, LowerLeg, Foot, Arm, Hand. Two items may share a region only if on different layers (CP2077 rule).
2. **Base-slot override** (FFXIV rule): an item covering multiple regions declares one base slot; it hides lower-layer items in covered regions unless they opt into `show_through`.
3. **Entire-body shortcut** (Tekken rule): Layer 3–4 "entire body" items are just items with region=FullBody; equipping one unequips conflicting region items.
4. **Appearance vs data split** (CP2077 Wardrobe + BG3 toggle): clothing items carry only look; stats/moveset live elsewhere. Saved looks = named presets ("wardrobe slots"), switchable without touching fight data.
5. **Free-place accessories** (SC6/Tekken rule): Layer 5 items get position/rotation/scale gizmos; max N per character (budget like CV2's cost system).
6. **Clipping contract** (fixes SC's weakness): at export, higher-layer cloth gets an automatic **shrink-wrap/offset pass** against lower layers + a per-item `clip_priority`; unresolved intersections are flagged in the suite UI, not silently shipped. Daz's "Transfer Other Morphs" (body shape keys → clothing) is the authoring-side complement: clothing inherits the body's dial deltas.
7. **Material zones** (Code Vein rule): every clothing item exposes named color zones (collar/sleeve/chest/trim) with HSV control (T8's full-HSV color tool is the bar).

---

## 5. Daz-style dial → creation-suite slider: concrete mapping proposal

### 5.1 The dial record (one per slider in the suite)
```json
{
  "id": "nose_tip_up",
  "label": "Nose Tip Up",
  "group": "Head / Nose",
  "source_taxonomy": "daz",
  "side": "center",
  "range": [-100, 100],
  "default": 0,
  "deltas": "<per-vertex delta array, authored on OUR topology>",
  "erc": {
    "multiply_masters": ["face_all"],
    "freeze_group": "nose_cluster"
  },
  "lod": "all"
}
```

### 5.2 Mapping rules
1. **One Daz dial → one suite slider**, same name normalized (`Nose Tip Up` → `nose_tip_up`), grouped under the Daz parameter path (`Actor/Head/Face/Nose/...`). Start from the Genesis Evolution + Resource Kit dial lists (§3.1) as the spec — ~120 head + ~80 body dials.
2. **L/R dials → side-aware sliders**: Daz `Cheeks Dimple Crease L/R` become one UI row with L/R sub-sliders (linked by default, unlinkable) — matches FaceGen's asymmetry workflow.
3. **ERC Multiply → slider link**: the Flexion pattern becomes `master_dial` links in the suite; zeroing the master zeroes the group. Expose in UI as "link" toggles.
4. **ERC Freeze → preset-to-dial**: "Save current dial state as new slider" — snapshots all non-default dial values into one named slider (interpolated). This is how character presets become reusable dials (the Basic Child pattern).
5. **JCMs → pose drivers**: not sliders at all; authored as bone-rotation → shape-key drivers in Blender, exported as driver curves or baked pose-space deformation.
6. **FACS/ARKit-52 → expression tab**: separate from creation dials; same underlying shape-key machinery, different UI (face board).
7. **Deltas are re-authored, never imported**: Daz vertex data stays in Daz. We copy the *taxonomy + composition semantics*, and sculpt deltas on our own base meshes (or derive from freebie-licensed sources with attribution, per §1.5).
8. **Export**: sliders bake to glTF morph targets (`extras.dial_id`, `extras.side`, `extras.erc_master`) + a sidecar JSON of the ERC graph so the engine can rebuild master/slave behavior without Daz.

### 5.3 Priority order for implementation
1. Body regional dials (the #777 per-muscle L/R set) + ERC multiply-link. 
2. Head per-part dials (§3.1 taxonomy, Daz order: nose → lips → eyes → brow → ears → jaw/chin).
3. Custom L/R jaw+chin dials (the gap).
4. ERC Freeze preset-to-dial.
5. JCM pose drivers.
6. FACS/ARKit-52 expression layer (can ride the MetaMorph/DNA tooling in Blender).

---

## 6. 2026 open-source tool watch — what beats #775/#777

| Tool | What it is | Why it matters vs #775/#777 | License / cost |
|---|---|---|---|
| **MetaMorph (SkalinMetaMorph)** | Blender-native MetaHuman DNA import/edit/export, free tier | **Beats #777**: DNA is no longer Unreal/Maya-locked; full round-trip in Blender, free | Free version + pro beta |
| **REVO DNA** | Blender addon: import/conform/sculpt/export MetaHuman DNA, LOD sync | Same as above, released Sept 2026 | Paid addon (Blender Market-style) |
| **Diffeomorphic** | Daz G1–G9 → Blender, morphs as shape keys, JCM conversion | Still the best open Daz bridge; #777 under-covered its morph-import depth | Free, open-source |
| **Mesh Morpher (Graph, 2026)** | UE/Blender mesh sync, DNA topology edit, full-body MetaHuman morphs via Bonesnapshots | New: live Blender↔UE mesh stream; body-morph pattern we can copy | Paid (UE marketplace) |
| **PolyHammer Character DNA** | Blender DNA import with 1:1 RigLogic face-board | Alternative to MetaMorph for DNA→Blender | Paid |
| **Faceit** | Blender facial rig → 52 ARKit shape keys + iPhone mocap | Cheapest path to our FACS expression layer on any topology | Paid (Superhive) |
| **BlenRig 6** | Free advanced Blender body rig | Free alternative to Auto-Rig Pro for the body rig under our dials | Free |
| **X-Muscle System** | Anatomical muscle/tissue sim under skin | Corrective layer *above* dials: jiggle/flex sim the dials can't do statically | Paid (Superhive) |

Net: **no 2026 open-source tool beats SvR 2007's slider UX** (that was a UI finding, still stands), but the *pipeline* picture changed completely — Blender is now a first-class citizen for both Daz-dial and MetaHuman-DNA authoring, free. The suite's authoring home should be Blender with these bridges, not Daz Studio or Unreal.

Sources: [MetaMorph](https://forums.unrealengine.com/t/customize-metahumans-entirely-in-blender/2740080), [REVO DNA](https://blenderartists.org/t/released-revo-dna-metahuman-dna-editing-tools-for-blender/1653438), [Mesh Morpher blog](https://meshmorpher.com/blog), [2026 Blender rigging addons roundup](https://www.strayspark.studio/blog/best-blender-rigging-addons-2026), [Tripo 2026 shape-key tools roundup](https://www.tripo3d.ai/content/en/guide/the-best-blender-shape-keys-for-facial-rig-tools)

---

## 7. Licensing summary (per asset class)

- **Daz format knowledge / dial taxonomy / ERC semantics**: free to reimplement. No license encumbers *ideas about sliders*.
- **Genesis base meshes**: NOT redistributable. Never ship.
- **Daz vendor morph packs** (paid): single-user; never redistribute deltas; OK to use their *dial lists* as a spec.
- **Daz freebie morphs** (e.g. Morphalynn): check each item's terms; typically "use commercially, don't repackage as your own" — usable as derivation reference with attribution; don't commit their vertex data.
- **MetaHuman DNA tools** (DNACalib, MetaMorph free, REVO DNA): tools are free/paid-per-tool; **MetaHuman character content** is under Epic's license — usable in Unreal projects; verify before shipping any Epic-derived mesh/delta data in our engine. Take the architecture, author our own deltas.
- **FaceGen**: commercial SDK; the FACS/AU taxonomy and ARKit-52 naming are open standards — adopt names, not their data.
- **Game layer taxonomies** (Tekken/SC/CP2077/FFXIV/BG3/CV): game *design* patterns aren't copyrightable as functional systems; document and reimplement freely. Don't copy item names/art.

## 8. Open questions for the build lane
1. L/R jaw+chin dial authoring: sculpt on our base head, or derive from Daz freebie dials? (Needs owner's call on reference material.)
2. RBF solver in-engine: reimplement RigLogic-lite, or bake correctives to driver curves at export? (Perf vs flexibility tradeoff.)
3. Clothing auto-fit: Diffeomorphic's "Transfer Other Morphs" (shape-key propagation to clothes) as the suite's auto-fit — prototype on one outfit first.
4. glTF morph-target budget: ~200 dials × per-vertex deltas — measure payload; consider quantized/delta-compressed sidecar.

---
*End of DEEP-MORPHING-DIALS-V2-2026-10-23. Filed per standing directive: everything goes in the repo.*
