# Create New Fighter — flow map (WWE rhythm, our freedom)

**Source sequence: WWF No Mercy "Edit / Create a Superstar"** — the most
completely documented creation flow in the teardowns
(`teardown/wwf-no-mercy/re-docs/docs/ui/menus/edit-a-superstar.md`: six
pages — Profile/Music, Appearance, Moves, Fighting Style, Parameter,
Ally/Enemy — with the full Appearance sub-order: Body → Head → Face →
Hair → Front Hair → Facial Hair → Masks/Etc → Hats/Caps → Ring Attire →
Upper Body → Tattoo → Gloves → Wrist Band → Elbow/Knee Pads → Feet →
Entrance Attire → Weapons/Props).

We follow that order **exactly**, with one addition at the front: No Mercy
makes you pick a save slot; WWE 2K makes you pick a base template. Our
front door is the **template select screen** — the WWE 2K starting
experience the owner asked for.

## The journey

```
0. TEMPLATE SELECT  (our front door — WWE 2K style)
   Division tabs: Heavyweight | Cruiserweight | Women's
   -> 9 template cards (visually presented, 3D preview each)
   -> pick one -> its body_type/proportions/skin/head/base_mesh load
   Source: customization/templates/body-templates.json (data-driven)

1. BODY  (No Mercy Appearance > Body)
   WWE: 14M+9F body types + 8 skin tones + height/weight sliders
   OURS: same lists (extracted verbatim) PLUS unified parametric sliders:
         MB-Lab morphs + MPFB2 targets + Build-A-Bod scaling, one panel
   Menu: BODY tab

2. HEAD / FACE  (No Mercy Appearance > Head, Face)
   WWE: 7M+3F head shapes, 98M+20F face textures
   OURS: same pools PLUS unified FACE system — GNM identity/expression
         presets + MB-Lab face morphs + 20 semantic params, tap-to-assign
   Menu: FACE tab

3. SKIN  (extension of Body — WWE folds this into Body)
   WWE: skin tone only
   OURS: tone + MB-Lab skin engine (age/mass/tone-driven displacement),
         Fluid Painter texture-paint jobs for custom skin detail
   Menu: BODY tab > SKIN section (job queue for paint jobs)

4. HAIR  (No Mercy Appearance > Hair + Front Hair)
   WWE: 22 base styles x front-hair combos
   OURS: No Mercy hair list + WMXIX 165-style library + CC0 universal
         hair (real meshes) + MB-Lab hair engine jobs
   Menu: ATTIRE tab > Hairstyle category

5. FACIAL HAIR  (No Mercy Appearance > Facial Hair)
   WWE: 31 numbered styles
   OURS: the 31 styles mapped to extracted meshes where decoded,
         procedural paint fallback otherwise (honestly labeled)
   Menu: ATTIRE tab > Facial Hair category

6. MASKS / HATS  (No Mercy Appearance > Masks/Etc, Hats/Caps)
   WWE: named mask/accessory/hat tables
   OURS: same tables (extracted) + suite mask library, socket-mounted
   Menu: ATTIRE tab > Masks / Headwear categories

7. ATTIRE  (No Mercy Appearance > Ring Attire ... Entrance Attire)
   WWE: ring attire, upper body, tattoo, gloves, wrist/elbow/knee, feet,
        entrance attire, weapons/props
   OURS: same slot order + Tekken 4-slot overlay (head/upper/lower/other)
         attaching via the unified socket system; 3,398 extracted parts
   Menu: ATTIRE tab (categories in WWE order)

8. PROFILE / MUSIC  (No Mercy page 1 — we put it after the look is done)
   WWE: name, short name, alias, picture, height, weight, music, titantron
   OURS: + soul assignment, element, land of origin (Western Heart canon)
   Menu: PROFILE tab

9. MOVES  (No Mercy page 3)
   176-slot unified moveset assignment. (Input mapping itself is
   deferred per owner directive — the slots/assignment UI is here.)
   Menu: MOVESET tab

10. FIGHTING STYLE + PARAMETER  (No Mercy pages 4-5)
    Archetype, aggression, zone offense/defense.
    Menu: PROFILE tab > style section (existing)

11. DONE -> fighter JSON saved (CHARACTER-CREATION.md §6 format),
    exportable to the game via the customization consumer.
```

## WWE vs ours, per step

| Step | WWE gives | We add |
|---|---|---|
| 0 Template | fixed base models | 9 data-driven templates, parametric base_mesh bakes |
| 1 Body | type list + H/W sliders | MB-Lab + MPFB2 + Build-A-Bod parametric sliders |
| 2 Face | texture list | GNM live identity/expression + MB-Lab morphs |
| 3 Skin | tone swatch | skin engine + Fluid Painter jobs |
| 4 Hair | style list | 165 WMXIX styles + CC0 real meshes + hair engine |
| 5 Facial hair | 31 styles | same 31, mesh-mapped where decoded |
| 6 Masks/hats | tables | same tables + socket system |
| 7 Attire | slot tables | 3,398 extracted parts + Tekken overlay slots |
| 8 Profile | name/music/etc | + soul/element/land |
| 9-10 Moves/style/params | slot assignment | same, 176-slot unified |

## Implementation

The wizard is a step bar over the existing tab panels
(`customization/create-fighter/`): each step deep-links to its tab (and
category where relevant) with Next/Back. No duplicated panels — the WWE
rhythm is a *sequence* over the real panels, not a second UI. Template
select is a full-screen overlay shown when starting NEW FIGHTER.
