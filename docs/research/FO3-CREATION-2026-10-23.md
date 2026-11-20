# Fallout 3: Game of the Year Edition — Character Creation & Customization Depth/Parts Research

- **Date:** 2026-10-23
- **Status:** RESEARCH ONLY — no Steam file pull was performed and no game files were accessed. No claims are faked; every substantive claim below cites a public source. Findings are marked [RESEARCHED]; anything requiring the actual game files is marked [AWAITS FILE PULL].
- **Steam app ID:** 22370

## Owner instruction (verbatim)

> *"Fallout 3 - Game of the Year Edition : character creation and customization depth and parts"*

---

## Section 0: What the game is

Fallout 3 (Bethesda Game Studios, 2008; Game of the Year Edition bundles the base game with all five DLCs) is an open-world first/third-person action RPG set in a post-nuclear Washington D.C. wasteland, built on the Gamebryo engine with Havok physics. Its character system splits into two halves the owner asked about: (1) a **stat/skill/perk system** (the classic S.P.E.C.I.A.L. RPG layer) and (2) a **face/hair customization system** (the "Gene Projector," built on licensed FaceGen morph technology). Notably, the game is famous for *diegetic* character creation — every creation step is presented as a life event (birth, a children's book, a school exam) rather than a menu screen.

---

## 1. Character creation system — full taxonomy

### 1a. The diegetic creation sequence [RESEARCHED]

Fallout 3 deliberately hides its character creator inside the tutorial questline:

1. **Birth** — the player picks **sex** (male/female) and types their **name** while talking to their father (James). Then the "Gene Projection" machine shows what the baby will look like "when you're all grown up" — this is the full appearance editor. [Source: https://fallouthub.blog/2014/05/fallout-3-walkthrough.html; https://www.gamebanshee.com/fallout3/walkthrough/growingup.php]
2. **Age 1 ("Baby Steps")** — the player reads a children's book titled *"You're S.P.E.C.I.A.L.!"* and allocates their **seven primary statistics**. [Source: https://www.gamebanshee.com/fallout3/walkthrough/growingup.php]
3. **Age 10 ("Growing Up Fast")** — the player receives the **Pip-Boy 3000** (birthday party). [Source: https://www.gamebanshee.com/fallout3/walkthrough/growingup.php]
4. **Age 16 ("Future Imperfect")** — the **G.O.A.T. (Generalized Occupational Aptitude Test)** exam: a personality quiz in the style of Ultima IV that recommends **3 "tag" skills**; the player may override the quiz result and pick tags manually through dialogue with Mr. Brotch. [Source: http://www.vrbones.com/2008/10/falloutlog-01.html; http://www.fallout.gamepedia.com/wiki/Fallout_3_SPECIAL]
5. **Leaving Vault 101** — before exiting, the player is offered a **complete re-spec of everything** chosen in steps 1–4 (appearance, SPECIAL, tags). Every early-life choice is changeable at this exit point. [Source: http://www.fallout.gamepedia.com/wiki/Fallout_3_SPECIAL]

Post-tutorial: face can only be re-done via **Pinkerton's Lasergrafter** (Rivet City bow) — a one-time cosmetic-surgery NPC; hair/beard can be changed any number of times by barber NPCs (Wadsworth at the Megaton house, Godfrey at Tenpenny Tower, Butch, Snowflake in Underworld, Joseph in Little Lamplight). [Source: https://fallout.wiki/wiki/Gene_Projector_(Fallout_3); https://fallout-archive.fandom.com/wiki/Gene_projector]

### 1b. S.P.E.C.I.A.L. primary statistics [RESEARCHED]

Seven attributes, each defaulting to **5** with **5 additional points to distribute** (range 1–10; nothing can push an attribute below 1 or above 10 at creation). [Source: http://www.fallout.gamepedia.com/wiki/Fallout_3_SPECIAL]

| Stat | Governs |
|---|---|
| **Strength** | Melee damage, carry weight |
| **Perception** | Ranged accuracy, threat detection on compass |
| **Endurance** | Hit points, poison/radiation resistance, healing rate |
| **Charisma** | NPC disposition, Barter and Speech skill bonuses |
| **Intelligence** | Skill points per level |
| **Agility** | V.A.T.S. action points, stealth |
| **Luck** | Critical hit chance, all skill values slightly |

Key derived statistics (formulas are public data, useful as structural reference): Action Points = 65 + 2×AGI; Carry Weight = 150 + 10×STR; Critical Chance = Luck%; Hit Points = 90 + 20×EN + 10×level; Melee Damage bonus = STR/2; Skill points per level = **10 + INT** (so INT 10 yields 23/level). [Source: http://www.fallout.gamepedia.com/wiki/Fallout_3_SPECIAL]

### 1c. Skills — 13 total [RESEARCHED]

Weapon skills (6): **Big Guns, Energy Weapons, Explosives, Melee Weapons, Small Guns, Unarmed.** Non-weapon skills (7): **Barter, Lockpick, Medicine, Repair, Science, Speech, Sneak.** Each skill is tied to one SPECIAL stat and starts at **(stat × 2) + 2 + (Luck ÷ 2)**. **Tagging** a skill grants an immediate **+15 point bonus**; the player tags 3 skills at the G.O.A.T. Skills cap at 100. [Source: https://fallout.fandom.com/wiki/Fallout_3_skills; http://www.fallout.gamepedia.com/wiki/Fallout_3_SPECIAL]

### 1d. Perks — and the notable ABSENCE of traits [RESEARCHED]

- **Perks are granted every character level** (not every 3–4 levels as in Fallout 1/2). Many perks have SPECIAL and/or skill prerequisites — e.g. Mysterious Stranger requires Luck 6. [Source: http://www.fallout.gamepedia.com/wiki/Fallout_3_SPECIAL]
- **Traits were REMOVED in Fallout 3.** In Fallout 1/2, traits were picked at character creation as advantage+disadvantage pairs; in FO3 the designers "merged" the two systems, folding old traits into perks with their downsides stripped out. [Source: http://fallout.wiki/wiki/Fallout_3]
- [AWAITS FILE PULL]: the exact perk count (~59 in the base game) and each perk's data fields can only be verified from Fallout3.esm via the GECK.

---

## 2. The Gene Projector — appearance creation options (full slider taxonomy)

The Gene Projector is the in-game appearance UI. Its complete option tree is documented on the Fallout wiki: [Source: https://fallout.wiki/wiki/Gene_Projector_(Fallout_3)]

**Top-level options:** Sex (male/female) · character name · **4 race presets** (Caucasian, African-American, Hispanic, Asian — functionally just starting offsets, see §3) · **Age 18–60** · **Eye color** (4: Green, Blue, Hazel, Dark Brown) · **face presets** (reported as 8 per sex in a contemporary press write-up, and as ~10 per sex by modders; each preset is a full slider snapshot used as a starting point — cite both: https://www.dailygame.net/fallout-3-character-creation-the-details/ and https://forums.nexusmods.com/topic/385758-porting-request/page/3/).

**Face-shape sliders (~35), grouped by region:**

| Region | Sliders |
|---|---|
| Shape | Heavy/Light (face fullness), Thin/Wide (face width) |
| Forehead | Small/Large, Tall/Short, Tilt Forward/Back |
| Brow | High/Low, Up/Down (Inner), Up/Down (Outer) |
| Eyes | Up/Down (height), Small/Large, Together/Apart |
| Nose | Bridge Depth, Up/Down (length), Flat/Pointed, Nostril Tilt, Nostrils Wide/Thin, Sellion Height, Short/Long |
| Mouth | Large/Small (lip depth), Overbite/Underbite |
| Cheeks | Low/High, Shallow/Pronounced, Concave/Convex |
| Jaw | Retracted/Jutting, Wide/Thin, Slope High/Low, Concave/Convex |
| Chin | Forward/Backward, Broad/Recessed, Shallow/Deep, Tall/Short |

Deliberately **not** customizable: the ears. Every feature can also be **randomized**. [Source: https://www.dailygame.net/fallout-3-character-creation-the-details/]

**Tone sliders (12 facial tint layers):** Shade (overall skin), Flushed, Blue Tint, Yellow Tint, Eye Sockets, Eyebrows, Eyeliner, Nose, Lips, Moustache, Cheeks, Beard. [Source: https://fallout.wiki/wiki/Gene_Projector_(Fallout_3)]

**Hair system [RESEARCHED]:** 13 named hair colors **plus a free RGB color picker** (Bleached, Brown, Chocolate, Platinum, Cornsilk, Suede, Pecan, Auburn, Ginger, Honey, Gold, Rosewood, Black, Chestnut, Steel, Champagne, + RGB). Hairstyles: **6 unisex** (Sarge, Clean Cut, Buzz Cut, Bedraggled, Blast Back, The Unsettler), **13 male** (Tunnel Snake, Pompadour, Waster, Balding, Buzz Saw, Combover, Smooth Wave, Shaggy Suave, Terrorsaur, Punked, Warhawk, High Riser), **17 female** (Domestic Goddess, No Nonsense, Prim 'N Proper, Rough Nite, Wendy the Welder, The Sophisticate, Frazzled, Iron Maiden, Unladylike, Rude Ridge, Mangy, Fallen Angel, FairyTails, Shaved, L'il Devil, Seductress, Pretty Puff). **Facial hair: 18 styles** (Survivalist, Rough Beard, Goatee, Beatnick, Gunslinger, The Gentleman, Muttonstache, Shaggy Sideburns, Soul Patch, Old Coot, The Gettysburg, Chopper, Chin Strip, Honest Abe, Man's Man, Swashbuckler, Lady's Man, Tough Guy). [Source: https://fallout-archive.fandom.com/wiki/Gene_projector]

**Body:** Fallout 3 has **no body-shape/size sliders at creation** — the body comes from the race record's fixed body mesh (see §4). This is a researched limitation, not a gap: the Gene Projector covers face/hair only.

---

## 3. FaceGen morph technology — how sliders map to meshes

### [RESEARCHED]

Fallout 3's faces are built on **licensed FaceGen technology** (Singular Inversions). The public FaceGen documentation describes the underlying model:

- Each head is a base mesh with **morph targets** (blendshapes). FaceGen divides them into **Expressions, Phonemes, Modifiers, and Morphs**, scaled 0–1, where 1 = the full morph target. Shape statistics are computed with a closed mouth; UVs must be non-overlapping across the face. [Source: https://facegen.com/modeller35_help.htm]
- In FO3's file layout, each head NIF is paired with three sidecar files — **.egm** (geometry morph data), **.egt** (texture morph data), and **.tri** (morph-target index): modders describe these as "data files to achieve specific, unique facial geometries for any character or NPC, that are already fully rigged & capable of performing animations." [Source: https://forums.nexusmods.com/topic/155387-fallout-body-editing-engine/?do=findComment&comment=1331876]
- A fully working custom head needs **~80 morphs** covering not just the head mesh but the **inner mouth, upper teeth, lower teeth, tongue, both eyes (and ears where present)** — and every one of these must morph **in unison** or parts clip horribly (e.g. teeth dropping through the chin during speech). [Source: https://forums.nexusmods.com/topic/706231-how-to-add-phoneme-mapping-to-a-custom-mesh-actor/?do=findComment&comment=5625170]
- Slider values are stored per-NPC as long hex strings: **FGGS** (FaceGen Geometry Symmetric), **FGGA** (asymmetric), **FGTS** (texture symmetric) — extractable from save games with FaceGen ripper tools and copy-pasteable between NPCs. [Source: https://forums.nexusmods.com/topic/218126-custom-face-texture/]
- **Race modifiers are applied on top of slider values:** a neutral (all sliders centered) face is NOT ethnically neutral — the game applies per-race offsets, plus an extra offset for female characters, so the "race preset" is effectively a hidden morph offset layered over the user's slider vector. Modders who import photo-fit faces from the commercial FaceGen Modeler must build modifier-free races to cancel this out. [Source: https://www.nexusmods.com/fallout3/mods/16154]
- The community's standard pipeline for custom heads: build morphs in FaceGen Modeler → export → Blender → NIF with correct shader flags (**SHADER_SKIN** + `SF_ShadowMap` + `SF_FaceGen` for skin; `SHADER_DEFAULT` + `SF_Remappable_Textures` for clothing) → register in GECK with matching .egm filename. [Source: https://forums.nexusmods.com/topic/11181013-new-modder-need-help-trying-to-make-custom-race/; https://forums.nexusmods.com/topic/6368216-converting-meshs-from-other-games-help/page/3/]

### [AWAITS FILE PULL]

- Exact morph count per vanilla head and the EGM/EGT/TRI binary formats (reverse-engineered by modders but best verified against the shipped files).
- The per-race modifier vectors (the actual numeric offsets for the 4 human races + female modifier).
- The slider→morph mapping table (which morph indices each of the ~35 UI sliders drives, and their weight curves).

---

## 4. GECK exposure — how character parts are organized for modders

### [RESEARCHED]

The GECK (Garden of Eden Creation Kit — Bethesda's free official editor) exposes characters through **Race records** and **HeadPart records**, as documented by modders working in the tool:

- **Race record** contains a **Body Data tab**: an **Upper Body model** NIF plus **Left and Right Hand** NIFs per race, and texture fields where the game — not the NIF — defines the textures. Naming convention: if the head texture is `headhuman.dds`, the game auto-expects `headhuman_n.dds` (normal map) and `headhuman_sk.dds` (skin map) in the same folder; playable races additionally need `*_1st.dds` first-person hand textures. [Source: https://forums.nexusmods.com/topic/6972806-issues-with-npc-face-textures/?do=findComment&comment=63413181; https://forums.nexusmods.com/topic/6245401-nifskope-body-texture-changes-not-showing-in-geck-or-in-game/]
- **HeadParts** are individual plug-in records (their own form type): **head, hair, eyes, eyebrows, eyelashes, facial hair** each get a HeadPart record pointing at a mesh, with flags for which races/sexes may use it and whether it's playable (shows in the creator). Modders add new hairstyles/eyes/brows by creating HeadPart records — e.g. eyelashes can be authored as a "female facial hair" HeadPart. [Source: https://forums.nexusmods.com/topic/348043-facegenracenpcgeck/?do=findComment&comment=2991844; https://forums.nexusmods.com/topic/385758-porting-request/page/3/]
- A custom-race folder layout used by the community shows the parts inventory: `Head` (headfemale.nif + .egm/.egt/.tri), `Hair`, `Eyelash`, upper body + hands. [Source: https://forums.nexusmods.com/topic/348043-facegenracenpcgeck/?do=findComment&comment=2991844]
- NPC face data lives in the **NPC record's FaceGen section** (the FGGS/FGGA/FGTS hex blobs) plus a **PNAM Head Parts** list selecting which HeadParts that NPC uses. [Source: https://forums.nexusmods.com/topic/385758-porting-request/page/3/]
- Texture layering trick: modders zero out the symmetric texture FaceGen data so the hand-authored diffuse texture shows through untouched — giving the texture artist full control. [Source: https://forums.nexusmods.com/topic/348043-facegenracenpcgeck/?do=findComment&comment=2991844]

### [AWAITS FILE PULL]

- The actual Race record field list and HeadPart flag enums from the GECK on real data (Fallout3.esm).
- The vanilla HeadPart inventory counts (exact number of shipped hair/eye/brow/beard records).

---

## 5. What the modding community does with character customization

### [RESEARCHED]

- **Body replacers** (the biggest category): Type 3 / Babe / Exnem-style body mods swap the race record's body NIFs. One long-running proposal ("Fallout 3 Omni-Bod Engine") explicitly wanted to port the **EGM/EGT/TRI morph technique from faces to bodies** — base body mesh + deformation sliders scripted into the race menu with body-type presets. [Source: https://forums.nexusmods.com/topic/155387-fallout-body-editing-engine/?do=findComment&comment=1331876]
- **Photo-fit faces:** mods like "Facegen Race" (Nexus Mods #16154) let players generate a head from real photos in the commercial FaceGen Modeler (~$300) and import it, working around FO3's race/female modifier offsets with a custom modifier-free race. [Source: https://www.nexusmods.com/fallout3/mods/16154]
- **Preset packs and face stealing:** the standard workflow is stealing an NPC's FGGS/FGGA/FGTS hex from a save with a FaceGen ripper and pasting it onto a new character — i.e. faces are treated as **portable parameter vectors**, exactly the "preset" concept. [Source: https://forums.nexusmods.com/topic/218126-custom-face-texture/]
- **Head resources:** only one fully from-scratch community head is widely cited (ThrottleKitty's Head06), because authoring ~80 synchronized morphs is "tedious"; most heads are reshapes of vanilla meshes that **reuse the existing EGM/TRI files** — a key lesson: morph libraries are the expensive asset, meshes are cheap. [Source: https://forums.nexusmods.com/topic/706231-how-to-add-phoneme-mapping-to-a-custom-mesh-actor/?do=findComment&comment=5625170]

---

## 6. Structural techniques WH can pull (techniques, not assets)

1. **Region-grouped slider taxonomy with semantic endpoints.** FO3's ~35 sliders are grouped Face → Forehead → Brow → Eyes → Nose → Mouth → Cheeks → Jaw → Chin, each slider labeled with what it does ("Heavy/Light = face fullness"). This is directly reusable as WH's face-sculpt UI layout — a proven, player-legible taxonomy.
2. **Presets as full parameter vectors + race presets as hidden offset layers.** FO3 ships ~8–10 face presets per sex (each a complete slider snapshot) and 4 race presets that are really just morph offsets applied over the slider vector. WH can do the same: user-facing "ethnicity/archetype" presets implemented as offset vectors on top of the slider state.
3. **EGM/EGT/TRI split architecture.** Separate the base mesh (NIF) from the deformation data (morph deltas) from the skin-tone data (texture maps). WH's morph-target pipeline should mirror this: base mesh + morph library + tint layers as independent, swappable files.
4. **"Morph in unison" rule.** Any slider that moves the jaw must move teeth, tongue, and inner mouth by the same delta — FO3's modders learned this the hard way. WH's face rig should bind sub-meshes (teeth, eyes, brows) to the same morph channels as the head, not as separate controls.
5. **HeadParts as a plug-in parts library.** Hair, eyes, brows, lashes, beards are independent records flagged by race/sex/playable — this is the exact data model WH wants for its swappable parts library (each part = mesh + metadata + compatibility flags).
6. **12 facial tint layers.** FO3's Tone tab (shade, flushed, blue/yellow tint, sockets, liner, lips, beard/moustache tint…) is a ready-made spec for WH's makeup/skin-tint layering.
7. **Zero-out for artist control.** The community practice of zeroing procedural texture morphs to let hand-authored textures show through is a good default for WH: procedural systems should always have a "bypass" so artists' textures win.
8. **Diegetic creation flow.** FO3 teaches its whole character system inside the tutorial (birth → book → exam → re-spec). WH's creation suite could similarly be staged as an in-fiction sequence (e.g. the Trial intake) rather than a flat menu — the owner's "feel like Tekken studio" ethos applies to UX too.
9. **Tag-skill concept → fighter style tags.** FO3's 3 tag skills (+15) are a clean model for WH fighter "style tags" (e.g. tag 3 archetype traits that boost related move families).
10. **No body sliders = a cautionary tale.** FO3 shipped face-only customization with fixed race bodies, and the modding community spent 15 years building body replacers to fix it. WH should ship body morphs (height/build/muscle) in the suite from day one — don't repeat the gap.

---

## 7. Extraction plan for the credentialed machine

When the user's Steam-credentialed machine is available (app 22370 — Fallout 3: Game of the Year Edition):

1. **Install via Steam**, then locate `Data\Fallout3.esm` (+ the 5 DLC ESMs).
2. **Download the GECK** (free from Bethesda's site) — load Fallout3.esm and export: all **Race** records (Body Data tab fields, texture paths, playable flags), all **HeadPart** records (type, mesh path, race/sex validity), and one NPC record's **FaceGen FGGS/FGGA/FGTS** hex as reference slider vectors.
3. **Extract meshes:** `Data\Meshes\Characters\` — head/body/hand/hair NIFs **with their .egm/.egt/.tri sidecars** (keep filename pairs intact; the game matches them by name).
4. **Extract textures:** `Data\Textures\Characters\` — diffuse/`_n`/`_sk` triples.
5. **Tools:** **NifSkope** (inspect NIF shader flags — verify SHADER_SKIN + SF_FaceGen on skin parts), **FO3Edit** (dump Race/NPC/HeadPart records including the FaceGen hex), FaceGen SDK docs for EGM/EGT/TRI format notes.
6. **Deliverables for WH:** (a) the full slider→morph index table, (b) per-race modifier offset vectors, (c) the vanilla HeadPart inventory with counts, (d) the base head mesh + morph set as a **structural reference only** — no Bethesda assets ship in WH; everything gets re-authored.

---

## Vision mapping — how each FO3 system maps to WH's creation suite

| FO3 system | WH creation-suite mapping |
|---|---|
| Gene Projector slider taxonomy (§2) | Direct template for WH face-sculpt UI: same region groups, same semantic endpoint labels, same ~35-slider depth |
| Face presets (8–10/sex) + race presets as offset vectors | WH "template select" screen: presets = full parameter snapshots; lineage/archetype = offset layers over sliders |
| EGM/EGT/TRI split | WH face pipeline architecture: base mesh ‖ morph-delta library ‖ tint-layer maps, independently swappable |
| ~80 synchronized morphs incl. teeth/tongue/eyes | WH face rig rule: sub-meshes share morph channels with the head; no independent jaw/teeth controls |
| HeadPart plug-in records (hair/eyes/brows/lashes/beard) | WH parts library data model: part = mesh + metadata + compatibility flags, swappable per fighter |
| 12 facial tint layers | WH makeup/skin-tint layering spec |
| SPECIAL + 13 skills + tags + perks | WH fighter "style tags" (tag 3, +bonus) and unlockable perk-like traits for custom movesets |
| Diegetic creation (birth → book → G.O.A.T. → re-spec) | WH creation staged as in-fiction Trial intake sequence, not a flat menu |
| Missing body sliders (community filled the gap) | WH ships body morphs (height/build/muscle) at launch — lesson learned |
| Perk prerequisites (stat + skill gates) | WH creation gates: advanced parts/moves unlock behind style-tag prerequisites |

*End of report. All findings from public sources cited inline; no game files were accessed.*
