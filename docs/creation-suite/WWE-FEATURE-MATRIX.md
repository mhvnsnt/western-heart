# Creation Suite — Competitor Research: WWE 2K × Tekken 8 × MDickie

**Lane H · 2026-10-18 · branch `r2/creation-suite`**
Sources: `customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md` (WWE 2K19, 2026-10-13),
`~/workspace/menu-research/wwe2k_menus.md` (WWE 2K24/2K25), WWE 2K19 official
online manual (2K Games), WWE 2K22 Create-a-Superstar guide (FPS Index),
MDickie Wrestling Empire official instruction manual (mdickie.com),
esports.gg + Bandai Namco official Tekken 8 customization docs.

Owner directive: **WWE 2K = depth** (layering, parts, morphs, decals, freedom),
**Tekken = front-end** (setup, flow, look, feel, built from our real Tekken files).

## 1. WWE 2K creation suite — full feature set

**8 creation editors** (2K19; 2K24/25 add Custom Referee, Custom Signs, Custom Matches):

| Editor | What it does |
|---|---|
| Custom Superstar | body, face, attire, attributes, entrance, victory, AI — the CAW itself |
| Custom Entrance | motion, Titantron video, lighting, pyro, music, camera, movies |
| Custom Victory | Face AND Heel victory scenes (separate); individuals, tag, trios; crowd reaction celebrate/jeer |
| Custom Moveset | hundreds of moves across positions; signatures, finishers, super finishers, taunts, paybacks |
| Custom Championship / Arena / Show / Video / MITB | belt, arena, brand, Titantron video, briefcase designers |

**Custom Superstar menu structure** (2K24/25, SmackTalks CAS preview + manual):
Preset Templates → Appearance: Face (morph sliders: jaw, cheek, brow, nose, eyes,
mouth, chin, ears) → Appearance: Body (morphs: height, weight, muscle, shoulders,
chest, waist, arms, legs) → Appearance: Hair & Facial (100+ styles, layered) →
Clothing: Head / Upper / Lower (shoes separate) → Superstar Information (name,
nickname, hometown, gender, crowd reaction face/heel/tweener, weight class,
commentary name, announcer call name, alternate attire, referee attire) →
**Performance section: Entrance, Victory, Taunt, Signature, Finisher quick-picks**
(full editing via the separate Creation entries).

**Attire layering:** every body region stacks multiple items; left/right independent
(gloves, pads); per-item color channels; material editor (fabric/leather/metal/matte);
logo placement (scalable/rotatable, any piece); Attire Randomizer; Mirror Attire.

**Body morph system:** parametric morph targets on base templates (male slot 256 /
female 257); muscle definition is a texture overlay; height/weight scale the skeleton.

**Moveset editor categories** (positions, from 2K19 manual + community move lists):
Standing (Attack / Grapple Attack / Submission / Signature / Power / Quick),
Back Attack, Ground Attack (upper/lower), Turnbuckle, Rope/Rebound, Aerial/Diving,
Running, Double Team, Special (Finishers, Signatures), Taunts (4 slots), Paybacks
(Blackout, Comeback, Low Blow, Move Thief). Grapple placement convention:
Grapple+Up = suplexes/lifts, Grapple+Down = piledrivers/powerbombs/slams,
Grapple+Left/Right = DDTs/lariats.

**Moveset editor interaction (the tap flow):** select a move slot from the
position/category tree → scroll the move list for that category → tap the move to
assign (confirm inline). No drag-and-drop anywhere in WWE 2K's editor.

## 2. MDickie (Wrestling Empire / Wrestling Revolution) — the phone interaction model

From the official MDickie instruction manual (mdickie.com) — the closest reference
for a phone-first game doing deep customization:

- **"Touch either side of a value or box to browse its contents left or right."**
  Every option is a tap-browse stepper — no sliders, no drag.
- **"When selecting characters, touching their slot once will display their
  stats and touching again will proceed to access them."** — tap-once = preview,
  tap-twice = commit. This is the exact pattern for our move library:
  tap move once → live animation preview on the model; tap ASSIGN (or the move
  again) → assigned to the slot.
- Menus are instantly reachable by touch; back arrow / ESC exits any screen.
- Match-setup "Cast" screen: tap a character to replace them, +/- to add/remove —
  tap-to-swap, never drag.

## 3. Tekken 8 customization — the front-end reference

Main menu → **Customization** tab → Character Customization → pick a character →
10 outfit slots → dressing room with **full-screen real-time 3D rendering**
("what you see is exactly what you get"). Categories: head, entire face, glasses,
entire body, shoes; per-part color; accessory size/position adjustable.
**Conflict rule:** "Entire Body outfits take up all item slots apart from Accessory
slots." Customized content saves to multiple slots per character; pick the slot on
the character select screen. **Intros/victories are NOT selectable** — fixed per
character; Tekken puts no intro/victory picker inside (or outside) customization.

## 4. Gap table

| WWE 2K feature | Tekken 8 feature | WH status (v0.2) | Plan (this branch) |
|---|---|---|---|
| Face morph sliders (dozens) | Face parts (eyes, brows) | 10 head shapes, no morph sliders | v0.3: proportion sliders exist (height/weight/muscle); face morphs = gap, needs morph-target pipeline |
| Body morph sliders (height/weight/muscle/shoulders/…) | — | Height/weight/muscle sliders ✓; 16 No Mercy body-type presets ✓ | extend presets; shoulder/chest/waist sliders = later |
| Attire layers per region, L/R independent | 4-slot item system (Head/Upper/Lower/Other) | 11 WWE categories + Tekken 4-slot overlay spec'd; buy/equip loop ✓ | wire real part geometry (ymg/obj parser — biggest gap) |
| Per-item color channels + material editor | Per-part color, accessory size/position | 3 color channels + metalness/roughness ✓ | keep; add per-part position/scale (Tekken 8) |
| Logo/decal placement (any piece, scale/rotate) | — | Pantera decal library (6 entries + MANIFEST) ✓ data; no UI | v0.3: DECALS section in ATTIRE driven by MANIFESTs |
| Moveset editor: categories → slot → tap move | — (fixed movelists) | 176-slot WWE-layout browser, tap-to-assign ✓; sample DB only (5 moves) | v0.3: seed library from 45 real Tekken movelists (539 moves); live preview on tap-select |
| Signatures / Finishers / Super Finishers | Rage Arts (fixed) | not present | v0.3: finisher/signature slots in PERFORMANCE tab (Tekken: rage-art-equivalent flag on moves) |
| Taunts (4 slots) | — | not present | v0.3: TAUNT picker (T3 stance clips) in PERFORMANCE tab |
| Entrance / Victory editors | fixed per character (not selectable) | not present | v0.3: INTRO/VICTORY quick-pick in PERFORMANCE tab (T3 clips); full editor later. Placement: INSIDE the Create flow per WWE 2K22's Performance section (see §5) |
| Fighting styles (5 + sub-styles) + attributes | — | archetype + aggression sliders ✓ | keep; map WWE styles → WH archetypes (doc'd in DESIGN.md) |
| Weight classes + lift rules | — | height/weight params ✓ | gameplay effect = Lane F/gameplay; suite records the class |
| AI tendencies | — | aggression/high-flyer/technical ✓ | keep |
| Crowd reaction (Face/Heel/Tweener) | — | not present | v0.3: alignment field in PROFILE (Face/Heel/Tweener) — drives victory scene choice |
| Alternate attires (4) | 10 outfit slots per character | 4 attire slots ✓ + 10 wardrobe quick-slots ✓ | keep |
| Preset templates | — | NEW FIGHTER base + 36 roster bases ✓ | keep |

## 5. Intro/victory placement — verified answer

Owner's brief: "the picker lives INSIDE character customization Tekken-style —
unless research shows Tekken puts it outside, then it goes outside."

Research verdict:
- **Tekken 8:** no picker at all — intros/outros fixed per character, not
  selectable in (or out of) customization.
- **WWE 2K (2K22, verified):** the Create-a-Superstar flow contains a
  **Performance section with Entrance, Victory, Taunt, Signature, Finisher
  quick-pick slots** (FPS Index guide); the DEEP editors (Custom Entrance,
  Custom Victory, Custom Move-Set) live outside as separate Creations entries.

**Decision (honest):** the INTRO / VICTORY / TAUNT quick-pickers live INSIDE the
Create Fighter flow as a PERFORMANCE tab — this matches WWE 2K's actual pattern
(quick-picks inside, deep editors outside) and the owner's "inside" requirement.
Cited per-screen in DESIGN.md.
