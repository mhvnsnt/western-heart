/* menu-data.js — VERBATIM menu trees extracted from the teardown games.
   Every node carries its source. No invented menus.
   See UI-EXTRACTION-LOG.md for the full extraction record. */

export const MENU_SRC = {
  T7_SLOTS: "Tekken 7 TKDataPatcher item schema — customization/parts/tekken/tekken7-slot-catalog.json (slots 1-15,17; UI titles HEAD/HAIR/FULL_HEAD/HAIR_ACC/GLA/FACE/FACE_HAIR/MAKE_UP/UPPER/FULL_BODY/LOWER/UPPER_ACC/LOWER_ACC/EXTRA/EFFECT/AURA)",
  T7_GROUPS: "Tekken 7 slot-group IDs (-236..-254) — same catalog; these ARE the in-game UI group ordering",
  T7_CONFLICTS: "Tekken 7 zone-conflict rules — same catalog (FULL_HEAD vs FACE/HAIR/GLA/..., FULL_BODY vs UPPER/LOWER)",
  T7_COLORS: "Tekken 7 color system — 0-5 color slots per item (max 5), hex per channel",
  T7_LOOP: "Tekken 7 verified game flow — pick fighter → pick 1 of 10 slots → category list; buy/equip two-step; hover try-on; exit → photo mode (UNIFIED-UI-SPEC.md §2, verified from guides + TKDataPatcher)",
  T6_SUB: "Tekken 6 subdivisions restored — Upper Inner/Outer, Hands (separate), Feet (separate), Waist L/R (UNIFIED-UI-SPEC.md §5.2, Tekken 6 PSP teardown)",
  T8_SLOTS: "Tekken 8 additions — Footwear slot, 30 shared slots, 2 accessory slots (tekken7-slot-catalog.json tekken8_additions)",
  WWE_FLOW: "WWE 2K Create-A-Moveset research — moveset-library/MOVESET-EDITOR-RESEARCH.md: Creations tab → Move-Set → pick superstar → Moves → category → position → select empty slot → select move from list → assigned; slot-first, no drag-and-drop",
  WWE_STYLE: "WWE 2K16 Creation Suite — fighting style inside the editor (Aerialist/Brawler/Giant/Powerhouse/Showboat/Striker/Technician) + personality sliders (same research doc)",
  WWE_CAW: "WWE 2K CAW structure — pac/edit targets (bbtemplate/default/edit/sample.pac, slots 256/257 base bodies), customization/wwe2k-caw/PULL-PLAN.md. Game files NOT on disk — editor screen flows come from research, NOT from extracted binaries",
  NM_PROFILE: "WWF No Mercy Edit-A-Superstar — profile page 1, 4 attire slots, moveset/AI shared across attires (teardown/wwf-no-mercy/re-docs/docs/ui/menus/edit-a-superstar.md via UNIFIED-UI-SPEC.md §2/§4)",
  NM_BODY: "No Mercy body system — 14M+9F body types, 8 skin tones, 7M+3F head shapes, 28M+20F faces (UNIFIED-UI-SPEC.md §5.1)",
  WMXIX_PROP: "WrestleMania XIX parametric proportions — Height, Weight, Muscle, Shoulder, Chest, Waist, Hips, Arms, Legs (UNIFIED-UI-SPEC.md §5.1)",
  DOA_WARD: "DOA6 wardrobe — 10 slots per fighter, Costume+Hairstyle+Glasses+Title, two-phrase titles (UNIFIED-UI-SPEC.md §5.3)",
  MDICKIE_TAP: "MDickie tap grammar — tap slot → browse by tapping → tap to assign; tap-once-inspect/tap-again-enter (MOVESET-EDITOR-RESEARCH.md §2)",
  WH_PLACE: "Western Heart placement paradigm — position X/Y/Z + rotation pitch/yaw/roll + scale per attached part, mirrors Tekken's accessory adjustment (~/workspace/tekken-customization-extraction/REPORT.md §6; PartPoser 10-slider mapping)",
  WH_JIGGLE: "Western Heart jiggle system — per-area amplitude/frequency/damping, fat-mass scaling, female + male-fat roster families (jiggle lane, owner 2026-10-18)",
  WWE_ENTRY: "WWE 2K22 Create-A-Superstar entry — Creations → Superstar → New Custom Superstar / WWE Superstar / Edit Custom Superstar; weight class (Cruiserweight/Light Heavyweight/Heavyweight/Super Heavyweight) + archetype (Striker/Technician/Powerhouse/High Flyer) → Persona outfit template (skippable) (fpsindex 2K22 CAW guide, primagames CAW guide)",
  WWE_ATTIRE: "WWE 2K22 Attire submenu — per attire slot (Ring 1/2, Entrance 1/2): Attire Type, Appearance (per-attire hairstyle/eyes/facial hair), Clothing (Headgear: headwear/masks/glasses/face covers/piercings/head accessories/hooded/high-collar; Upper Body jackets; Lower Body: trunks/tights/bottoms/belts/knee pads/socks; Boots/Shoes), Parts Color, Import Parts, Select Persona; 60 attire layers + 40 body/head layers, body morphing, 40+ body templates (2K26 ringside report; fpsindex/revelleution guides)",
  WWE_FACEBODY: "WWE 2K22 Face/Body — 16 face presets, Face Photo, 261 hairstyles, individual eye customization, 31 eyebrows, eyelashes/makeup/scars/facepaint, 165 facial-hair options, 31 preset tattoos + unlimited CC placement, 34M/36F body types, any-color skin tone, 64 body-hair options, movable + immovable scars, custom logos (smackdownhotel 2K22-vs-2K20 comparison)",
  WWE_PROFILE: "WWE 2K22 Personal Information — name information, custom render (select-screen image), crowd reaction (boo/cheer), crowd signs, hometown, menu screen pose (face/hands/body settable), personality traits, custom side plates (fpsindex + revelleution 2K22 guides)",
  WWE_PERF: "WWE 2K22 Performance tab — quick-apply entrance + victory scenes, taunts, signatures, finishers (revelleution 2K22 guide)",
  WWE_STATS: "WWE 2K22 Statistics — 24 customizable attributes, paybacks (Resiliency/Low Blow/Poison Mist/Brass Knuckles/Run-In/Move Thief/Blackout/Comeback), superstar classes (revelleution 2K22 guide)",
  SC_CAS: "Soulcalibur VI Create-a-Soul — 16 races → weapon/style pick → body → equipment (Undergarments, Head, Upper Body, Shoulder, Arm, Lower Body, Leg, Special1, Special2) → Adjust Equipment (scale W/H/D, move, rotate) → color schemes/patterns → sticker & pattern editor → voice pitch → battle comments → photo (select image) → name; layered Undergarments/Mid-layer/Outerwear; 1,586 creation parts (siliconera, soulcalibur fandom, shapes.inc; SCIV equipment destruction)",
  DEFJAM_SHOP: "Def Jam: Fight for NY create-a-fighter shops — SUS Urban Streetwear (Tops/Jackets|Jerseys|Shirts|Sweaters|T-Shirts; Bottoms/Jeans|Pants; Shorts; Shoes/Athletic|Casual; Acc/Headwear|Armband|Eyewear), Manny's Tats (tattoos), Stingray's Barber Shop (hair/facial hair/hair color), Jacob & Co. (necklaces/earrings/rings/bracelets/watches), Stapleton Athletics gym (Train Skills: Upper/Lower Power, Speed, Toughness, Health; Learn Styles; Learn Moves; Assign Moves); gear → Charisma → momentum fill (supercheats FFNY FAQ, psxextreme review)",
  NM_CAW: "WWF No Mercy Create-A-Wrestler — Appearance: Body, Head, Face, Hair (+Front Hair), Facial Hair, Masks/Etc, Hats/Caps, Ring Attire (4 independent costumes), Upper Body (per costume), Tattoo, Gloves, Wrist Band, Elbow Pad L/R, Knee Pad L/R, Feet, Entrance Attire, Weapons/Props; Moves: position trees (grappling/striking/running/ground/turnbuckle/ringside/apron/irish whip) with LIVE move preview on highlight; 4 attires share one moveset; Smackdown Mall unlocks (gamefaqs SBurk CAW guide, honestgamers review)",
  WMXIX_CAW: "WWE WrestleMania XIX CAW — HEAD (hair type+color, eyebrow, nose, mouth, mustache, outline, wrinkles), BODY (type, lowerbody base, 3 color channels, 2 logo/pattern slots), ETC (tattoo, wrist, shoes), GEAR (attachable items with per-item translate/rotate/scale), FIGURE (12 region width/length/depth sliders: crown/head/neck/shoulder/upperarm/forearm/hand/chest/waist/abdomen/thigh/calf/foot), MOVES (fighting pose, rising, striking, front/rear grapple, specials), ENTRANCE (template/music/titantron/stage+ramp+ring+general animation/fireworks/cameras/start position+wait/appeal+telop points), Shopzone unlocks (gamefaqs Mega_Waihnt CAW FAQ)",
  TOUCH: "Western Heart touch conversion — tap grammar (MDickie: tap slot → scroll → tap assign; tap-once-inspect/tap-again-enter), bottom-sheet panels, swipe paging, pinch-zoom preview, 48px targets, portrait-first (verify-by-playing law: phone portrait, owner 2026-10-22)"
};

/* ---- ATTIRE category tree: T7 slots as the spine, T6 subdivisions nested ---- */
export const ATTIRE_TREE = [
  { slot:"1",  label:"Head",           icon:"🪖", src:"T7_SLOTS" },
  { slot:"2",  label:"Hairstyle",      icon:"💇", src:"T7_SLOTS", note:"mirrors BODY > Hair" },
  { slot:"3",  label:"Full Head",      icon:"🎭", src:"T7_SLOTS", note:"masks/helmets — CONFLICTS with Face Paint" },
  { slot:"4",  label:"Hair Accessory", icon:"🎀", src:"T7_SLOTS" },
  { slot:"5",  label:"Glasses",        icon:"👓", src:"T7_SLOTS", note:"glasses and eyewear" },
  { slot:"6",  label:"Face",           icon:"😐", src:"T7_SLOTS" },
  { slot:"7",  label:"Facial Hair",    icon:"🧔", src:"T7_SLOTS" },
  { slot:"8",  label:"Face Paint",     icon:"🎨", src:"T7_SLOTS", note:"texture class, not mesh" },
  { slot:"9",  label:"Upper Body",     icon:"👕", src:"T7_SLOTS", children:[
      { slot:"9a", label:"Upper — Inner", icon:"🎽", src:"T6_SUB", note:"undershirt/base layer" },
      { slot:"9b", label:"Upper — Outer", icon:"🧥", src:"T6_SUB", note:"jacket/armor over it" } ] },
  { slot:"10", label:"Full Body",      icon:"🥻", src:"T7_SLOTS", note:"CONFLICTS with Upper+Lower" },
  { slot:"11", label:"Lower Body",     icon:"👖", src:"T7_SLOTS" },
  { slot:"H",  label:"Hands",          icon:"🧤", src:"T6_SUB", note:"separate slot, restored — T7 merged it away" },
  { slot:"F",  label:"Feet",           icon:"🥾", src:"T8_SLOTS", note:"T8 footwear slot; T6 had it separate too" },
  { slot:"12", label:"Upper Accessory",icon:"📿", src:"T7_SLOTS" },
  { slot:"13", label:"Lower Accessory",icon:"🦵", src:"T7_SLOTS" },
  { slot:"WL", label:"Waist L",        icon:"⛓️", src:"T6_SUB" },
  { slot:"WR", label:"Waist R",        icon:"⛓️", src:"T6_SUB" },
  { slot:"14", label:"Extra",          icon:"✨", src:"T7_SLOTS", note:"Item Moves live here (T6)" },
  { slot:"15", label:"Effects",        icon:"💫", src:"T7_SLOTS", note:"effect class" },
  { slot:"17", label:"Aura",           icon:"🔥", src:"T7_SLOTS", note:"aura class" },
];

/* ---- BODY tab: wrestling CAW ---- */
export const BODY_TREE = [
  { key:"bodytype",   label:"Body Type",   icon:"🧍", src:"NM_BODY", note:"14M + 9F types — full-body morphs" },
  { key:"skintone",   label:"Skin Tone",   icon:"🎨", src:"NM_BODY", note:"8 tones, single tap" },
  { key:"proportions",label:"Proportions", icon:"📐", src:"WMXIX_PROP", note:"Height, Weight, Muscle, Shoulder, Chest, Waist, Hips, Arms, Legs — live sliders" },
  { key:"headshape",  label:"Head Shape",  icon:"🗿", src:"NM_BODY", note:"7M + 3F shapes" },
  { key:"jiggle",     label:"Jiggle",      icon:"〰️", src:"WH_JIGGLE", note:"per-area jiggle scales — see JIGGLE tab" },
];

/* ---- PARTS tab: the wired libraries ---- */
export const PARTS_TREE = [
  { key:"eyes",   label:"Eyes",   icon:"👁️", src:"WH_PARTS", note:"PLACEABLE mesh eye parts first (Spider-Girl lenses, CC0 eyebrows — owner verdict 2026-10-20: eyes are parts, not decals); eye-library textures are legacy variants, listed separately" },
  { key:"decals", label:"Decals", icon:"🏷️", src:"WH_PARTS", note:"customization/decal-library/pantera/ — logo/tights/pants texture swaps at parameterized placements" },
  { key:"masks",  label:"Masks",  icon:"🦸", src:"WH_PARTS", note:"customization/parts/superhero/ — spidergirl eyes, batgirl mask+gauntlets, spaceghost cowl; mesh parts on head/hand sockets" },
  { key:"hair",   label:"Hair",   icon:"💇‍♀️", src:"WH_PARTS", note:"mesh + texture hair parts (silvertongue drills, mariposa ponytail restore)" },
];
MENU_SRC.WH_PARTS = "Western Heart PARTS-REGISTRY.json — 34 parts, suite_slot + placement socket schema (customization/PARTS-REGISTRY.json)";

/* ---- JIGGLE tab: per-area scales (schema from jiggle lane) ---- */
export const JIGGLE_AREAS = [
  { key:"hips",     label:"Hips" },
  { key:"glutes",   label:"Glutes" },
  { key:"thighs",   label:"Thighs" },
  { key:"pecs",     label:"Pectorals" },
  { key:"mammary",  label:"Mammary" },
  { key:"belly",    label:"Belly" },
  { key:"arms",     label:"Upper Arms" },
  { key:"calves",   label:"Calves" },
];
export const JIGGLE_PARAMS = [
  { key:"amplitude", label:"Amplitude", min:0, max:1, step:0.01, def:0.5, note:"travel distance of the jiggle" },
  { key:"frequency", label:"Frequency", min:0.1, max:3, step:0.05, def:1.0, note:"oscillations per second — fat mass lowers it" },
  { key:"damping",   label:"Damping",   min:0, max:1, step:0.01, def:0.5, note:"how fast it settles — fat mass lowers it" },
  { key:"stiffness", label:"Stiffness", min:0, max:1, step:0.01, def:0.5, note:"spring tightness — muscle raises it" },
];
export const JIGGLE_FAMILIES = [
  { key:"female",   label:"Female roster",   note:"hips/glutes/thighs/mammary primary" },
  { key:"male_fat", label:"Male fat roster", note:"belly/pecs/arms primary — even muscular masses jiggle" },
];

/* ---- placement axes: Tekken accessory-adjustment paradigm ---- */
export const PLACE_AXES = [
  { key:"px", label:"Position X", min:-0.5, max:0.5, step:0.001, def:0, unit:"m", src:"WH_PLACE" },
  { key:"py", label:"Position Y", min:-0.5, max:0.5, step:0.001, def:0, unit:"m", src:"WH_PLACE" },
  { key:"pz", label:"Position Z", min:-0.5, max:0.5, step:0.001, def:0, unit:"m", src:"WH_PLACE" },
  { key:"rx", label:"Pitch",      min:-180, max:180, step:0.1, def:0, unit:"°", src:"WH_PLACE" },
  { key:"ry", label:"Yaw",        min:-180, max:180, step:0.1, def:0, unit:"°", src:"WH_PLACE" },
  { key:"rz", label:"Roll",       min:-180, max:180, step:0.1, def:0, unit:"°", src:"WH_PLACE" },
  { key:"s",  label:"Scale",      min:0.1, max:3, step:0.01, def:1, unit:"×", src:"WH_PLACE" },
];

/* ---- WWE CAW internal hierarchy: region → garment type (WWE runs the creator).
   Each region maps onto our T7 spine slots via `slots` so the same part catalog
   serves both browse modes. Per the owner division: Tekken runs the game's menus,
   WWE runs the creation flow's internal hierarchy. ---- */
export const WWE_ATTIRE_TREE = [
  { key:"wwe-head",  label:"Headgear",      sub:"Headwear · Masks · Glasses · Face Covers · Piercings · Head Accessories · Hooded / High-Collar", icon:"🎩", slots:["1","3","4","5"], src:"WWE_ATTIRE" },
  { key:"wwe-face",  label:"Face & Hair",   sub:"Hairstyle · Eyes · Facial Hair · Face Paint — per-attire Appearance", icon:"💇", slots:["2","6","7","8"], src:"WWE_ATTIRE" },
  { key:"wwe-upper", label:"Upper Body",    sub:"Jackets · Shirts · Vests · Singlets — Inner / Outer layers", icon:"👕", slots:["9","9a","9b","10"], src:"WWE_ATTIRE" },
  { key:"wwe-arms",  label:"Arms & Hands",  sub:"Gloves · Wrist Tape · Elbow Pads · Arm Bands (L/R independent)", icon:"🧤", slots:["H","12"], src:"WWE_ATTIRE" },
  { key:"wwe-lower", label:"Lower Body",    sub:"Trunks · Tights · Bottoms · Belts · Waist L/R", icon:"👖", slots:["11","WL","WR"], src:"WWE_ATTIRE" },
  { key:"wwe-legs",  label:"Legs & Feet",   sub:"Knee Pads · Socks · Boots · Shoes", icon:"🥾", slots:["13","F"], src:"WWE_ATTIRE" },
  { key:"wwe-acc",   label:"Accessories",   sub:"Chains · Jewelry · Props — freely placed, per-attire", icon:"📿", slots:["14"], src:"WWE_ATTIRE" },
  { key:"wwe-fx",    label:"Effects & Aura",sub:"Hit FX · Auras — per-attire", icon:"✨", slots:["15","17"], src:"WWE_ATTIRE" },
];

/* ---- WWE CAW entry flow (2K22): the three doors into the creator ---- */
export const WWE_ENTRY_FLOW = [
  { menu:"CREATIONS → SUPERSTAR", src:"WWE_ENTRY" },
  { menu:"NEW CUSTOM SUPERSTAR → weight class + archetype → Persona outfit template (skippable) → editor", src:"WWE_ENTRY" },
  { menu:"WWE SUPERSTAR → edit a roster wrestler's attire + menu pose (moveset/personal info locked)", src:"WWE_ENTRY" },
  { menu:"EDIT CUSTOM SUPERSTAR → pick your CAW → full editor", src:"WWE_ENTRY" },
  { menu:"Editor: APPEARANCE (Face/Body) → ATTIRE (per slot: Type / Appearance / Clothing / Parts Color) → PERSONAL INFO → PERFORMANCE → STATISTICS", src:"WWE_ATTIRE" },
];

/* ---- WWE Appearance: Face tab ---- */
export const WWE_FACE_TREE = [
  { key:"face-preset", label:"Face Preset",  sub:"16 presets (M/F)", icon:"😐", src:"WWE_FACEBODY" },
  { key:"face-photo",  label:"Face Photo",   sub:"photo-to-face alignment (mouth/lips first)", icon:"📸", src:"WWE_FACEBODY" },
  { key:"face-morph",  label:"Face Morphs",  sub:"jaw · cheek · brow · nose · eyes · mouth · chin · ears", icon:"📐", src:"WWE_FACEBODY" },
  { key:"eyes",        label:"Eyes",          sub:"individual L/R eye color + shape", icon:"👁️", src:"WWE_FACEBODY" },
  { key:"brows",       label:"Eyebrows",      sub:"31 options", icon:"🤨", src:"WWE_FACEBODY" },
  { key:"hair",        label:"Hairstyle",    sub:"261 options — also settable per-attire (Attire → Appearance)", icon:"💇", src:"WWE_FACEBODY" },
  { key:"facial-hair", label:"Facial Hair",  sub:"165 options — also settable per-attire", icon:"🧔", src:"WWE_FACEBODY" },
  { key:"makeup",      label:"Makeup / Face Paint / Tattoos", sub:"layers + movable scar/oval blending", icon:"🎨", src:"WWE_FACEBODY" },
];

/* ---- WWE Appearance: Body tab ---- */
export const WWE_BODY_TREE = [
  { key:"body-type",   label:"Body Type",   sub:"34M / 36F types", icon:"🧍", src:"WWE_FACEBODY" },
  { key:"body-morph",  label:"Body Morphing", sub:"mix-and-match body parts + 40+ templates (2K26)", icon:"🫀", src:"WWE_FACEBODY" },
  { key:"skin",        label:"Skin Tone",   sub:"any color", icon:"🎨", src:"WWE_FACEBODY" },
  { key:"body-hair",   label:"Body Hair",   sub:"64 options", icon:"🦍", src:"WWE_FACEBODY" },
  { key:"tattoos",     label:"Tattoos",      sub:"31 presets + unlimited CC placement (scale/rotate anywhere)", icon:"🐉", src:"WWE_FACEBODY" },
  { key:"logos",       label:"Custom Logos",sub:"placeable decals", icon:"🏷️", src:"WWE_FACEBODY" },
];

/* ---- WWE Personal Information tab ---- */
export const WWE_PROFILE_TREE = [
  { key:"name",      label:"Name Information", sub:"name · nickname · hometown", icon:"📝", src:"WWE_PROFILE" },
  { key:"render",    label:"Custom Render",    sub:"select-screen image (photo mode)", icon:"🖼️", src:"WWE_PROFILE" },
  { key:"reaction",  label:"Crowd Reaction",  sub:"Face / Heel / Tweener — drives victory scenes + crowd audio", icon:"📣", src:"WWE_PROFILE" },
  { key:"signs",     label:"Crowd Signs",     sub:"billboards the crowd holds", icon:"🪧", src:"WWE_PROFILE" },
  { key:"pose",      label:"Menu Screen Pose",sub:"facial anim + hand signs + body pose (templates or individual)", icon:"🧍", src:"WWE_PROFILE" },
  { key:"traits",    label:"Personality Traits", sub:"egotistical/prideful/disrespectful/respectful/desperate/perseverant/treacherous/loyal/cowardly/bold/aggressive/disciplined", icon:"🎭", src:"WWE_PROFILE" },
];

/* ---- WWE Performance tab (entrance/victory/taunts — repurposed per owner: cutscene + taunt creation) ---- */
export const WWE_PERFORMANCE_TREE = [
  { key:"entrance",  label:"Entrance",  sub:"motion + lighting + pyro + titantron (→ cutscene creator)", icon:"🎆", src:"WWE_PERF" },
  { key:"victory",   label:"Victory",   sub:"Face AND Heel scenes (separate)", icon:"🏆", src:"WWE_PERF" },
  { key:"taunts",    label:"Taunts",    sub:"in-ring taunts (→ taunt creator)", icon:"🕺", src:"WWE_PERF" },
  { key:"sigs",      label:"Signatures & Finishers", sub:"per-fighter special moves", icon:"💥", src:"WWE_PERF" },
];

/* ---- WWE Statistics tab ---- */
export const WWE_STATS_TREE = [
  { key:"attributes", label:"Attributes", sub:"24 customizable attributes → overall rating", icon:"📊", src:"WWE_STATS" },
  { key:"paybacks",   label:"Paybacks",   sub:"Resiliency · Low Blow · Poison Mist · Brass Knuckles · Run-In · Move Thief · Blackout · Comeback", icon:"🃏", src:"WWE_STATS" },
  { key:"class",      label:"Superstar Class", sub:"Striker / Technician / Powerhouse / High Flyer (+ weight class)", icon:"⚖️", src:"WWE_STATS" },
];

/* ---- Soulcalibur VI Create-a-Soul equipment tree.
   `wh` maps each SC equipment slot onto our T7-spine slot keys. ---- */
export const SC_CAS_TREE = [
  { key:"sc-under",   label:"Undergarments", sub:"inner clothing + tattoos — base layer", icon:"🩲", wh:["10","11"], src:"SC_CAS" },
  { key:"sc-head",    label:"Head",          sub:"hats · hoods · hairbands · masks · helms", icon:"🪖", wh:["1","3","4"], src:"SC_CAS" },
  { key:"sc-upper",   label:"Upper Body",    sub:"breastplates · cuirass · shirts · vests · suits — mid/outer layers", icon:"🛡️", wh:["9","9a","9b"], src:"SC_CAS" },
  { key:"sc-shoulder",label:"Shoulder",      sub:"spaulders · pauldrons", icon:"🎖️", wh:["12"], src:"SC_CAS" },
  { key:"sc-arm",     label:"Arm",           sub:"gauntlets · armlets · gloves · braces", icon:"🧤", wh:["H","12"], src:"SC_CAS" },
  { key:"sc-lower",   label:"Lower Body",    sub:"pants · hakamas · slacks · breeches", icon:"👖", wh:["11"], src:"SC_CAS" },
  { key:"sc-leg",     label:"Leg",           sub:"greaves · boots · shoes", icon:"🥾", wh:["F","13"], src:"SC_CAS" },
  { key:"sc-sp1",     label:"Special 1",     sub:"necklaces · capes · tails · horns · wings", icon:"🧛", wh:["12","14"], src:"SC_CAS" },
  { key:"sc-sp2",     label:"Special 2",     sub:"faulds · belts · tassets", icon:"⛓️", wh:["13","WL","WR"], src:"SC_CAS" },
];
export const SC_CAS_FLOW = [
  { menu:"Pick 1 of 16 RACES (human · outcast · lizardman · automaton · …)", src:"SC_CAS" },
  { menu:"Pick WEAPON + FIGHTING STYLE (any roster style usable)", src:"SC_CAS" },
  { menu:"EQUIP — layered Under / Mid / Outer (no-clip layering rules)", src:"SC_CAS" },
  { menu:"ADJUST EQUIPMENT — scale W/H/D + move + rotate per piece", src:"SC_CAS" },
  { menu:"COLORS + PATTERNS → sticker/pattern editor → voice pitch → battle comments", src:"SC_CAS" },
  { menu:"PHOTO (select-screen image) → NAME → done", src:"SC_CAS" },
];

/* ---- Def Jam FFNY shop organization — the streetwear-boutique model.
   `wh` maps each shop category onto our T7-spine slot keys. ---- */
export const DEFJAM_SHOP_TREE = [
  { key:"dj-tops",   label:"Tops",        sub:"Jackets · Jerseys · Shirts · Sweaters · T-Shirts", icon:"🧥", wh:["9","9a","9b"], src:"DEFJAM_SHOP" },
  { key:"dj-bottoms",label:"Bottoms",     sub:"Jeans · Pants · Shorts", icon:"👖", wh:["11"], src:"DEFJAM_SHOP" },
  { key:"dj-shoes",  label:"Shoes",       sub:"Athletic · Casual", icon:"👟", wh:["F"], src:"DEFJAM_SHOP" },
  { key:"dj-head",   label:"Headwear",    sub:"caps · bandanas · hats · sweatbands · durags", icon:"🧢", wh:["1","4"], src:"DEFJAM_SHOP" },
  { key:"dj-acc",    label:"Accessories", sub:"Armbands · Eyewear (shades)", icon:"🕶️", wh:["5","12"], src:"DEFJAM_SHOP" },
  { key:"dj-bling",  label:"Jacob & Co. Bling", sub:"necklaces · earrings · rings · bracelets · watches — raises Charisma", icon:"💎", wh:["12","14"], src:"DEFJAM_SHOP" },
  { key:"dj-tats",   label:"Manny's Tats",sub:"tattoos — raises Charisma", icon:"🐉", wh:["8"], src:"DEFJAM_SHOP" },
  { key:"dj-hair",   label:"Stingray's Barbershop", sub:"haircuts · facial hair · hair color", icon:"💈", wh:["2","7"], src:"DEFJAM_SHOP" },
];
export const DEFJAM_GYM_TREE = [
  { key:"train",  label:"Train Skills", sub:"Upper Power · Lower Power · Speed · Toughness · Health (Dev Points)", icon:"🏋️", src:"DEFJAM_SHOP" },
  { key:"styles", label:"Learn Styles", sub:"up to 3 fighting styles: Streetfighting · Kickboxing · Martial Arts · Wrestling · Submissions", icon:"🥋", src:"DEFJAM_SHOP" },
  { key:"moves",  label:"Learn Moves",  sub:"buy Blazin' Moves (unlock by beating fighters)", icon:"🔥", src:"DEFJAM_SHOP" },
  { key:"assign", label:"Assign Moves", sub:"map Blazin' Moves to stick directions (4 at once)", icon:"🎮", src:"DEFJAM_SHOP" },
];

/* ---- WWF No Mercy CAW tree (AKI classic — the 4-attire model we follow) ---- */
export const NM_CAW_TREE = [
  { key:"nm-body",   label:"Body",        sub:"body type · skin tone", icon:"🧍", src:"NM_CAW" },
  { key:"nm-head",   label:"Head / Face", sub:"head shape · face texture · hair (+front hair) · facial hair · masks/etc · hats/caps", icon:"🗿", src:"NM_CAW" },
  { key:"nm-attire", label:"Ring Attire", sub:"4 independent costumes — each with own Upper Body, colors, name, music", icon:"🥋", src:"NM_CAW" },
  { key:"nm-gear",   label:"Gear",        sub:"tattoo · gloves · wrist band · elbow pads L/R · knee pads L/R · boots · entrance attire · weapons/props", icon:"🥊", src:"NM_CAW" },
  { key:"nm-moves",  label:"Moves",       sub:"position trees — LIVE move preview on highlight (steal this)", icon:"🎬", src:"NM_CAW" },
];

/* ---- WrestleMania XIX CAW tree (Yuke's parametric model) ---- */
export const WMXIX_CAW_TREE = [
  { key:"xix-head",   label:"Head",    sub:"hair · eyebrow · nose · mouth · mustache · outline · wrinkles", icon:"🗿", src:"WMXIX_CAW" },
  { key:"xix-body",   label:"Body",    sub:"type · lowerbody base · 3 color channels · 2 logo/pattern slots", icon:"🧍", src:"WMXIX_CAW" },
  { key:"xix-etc",    label:"Etc",     sub:"tattoo · wrist · shoes", icon:"🐉", src:"WMXIX_CAW" },
  { key:"xix-gear",   label:"Gear",    sub:"attachables (wings · swords …) — per-item translate/rotate/scale", icon:"🗡️", src:"WMXIX_CAW" },
  { key:"xix-figure", label:"Figure",  sub:"12 region W/L/D sliders: head→foot proportions", icon:"📐", src:"WMXIX_CAW" },
  { key:"xix-moves",  label:"Moves",   sub:"fighting pose · rising · striking · front/rear grapple · specials (8+ finishers)", icon:"🥋", src:"WMXIX_CAW" },
  { key:"xix-entr",   label:"Entrance",sub:"template · music · titantron · stage/ramp/ring animation · fireworks · cameras", icon:"🎆", src:"WMXIX_CAW" },
];

/* ---- Touch / mobile conversion map (phone-first per verify-by-playing law) ---- */
export const TOUCH_MAP = [
  { gesture:"Tap",        use:"Select slot / category / part — tap-to-assign, NEVER drag-and-drop", src:"TOUCH" },
  { gesture:"Tap ×2",      use:"Tap once = inspect + live preview · tap again = enter / equip (MDickie grammar)", src:"TOUCH" },
  { gesture:"Swipe ←/→",   use:"Page item grids · swipe fighter sideways to rotate preview", src:"TOUCH" },
  { gesture:"Pinch",       use:"Zoom preview — auto-frames the picked slot's body region, pulls back on exit", src:"TOUCH" },
  { gesture:"Long-press",  use:"Part options sheet: color channels · placement · conflict info", src:"TOUCH" },
  { gesture:"Bottom sheet",use:"Item grid + part detail slide up from bottom — fighter stays visible above, never covered", src:"TOUCH" },
  { rule:"48px minimum touch targets; left-rail tabs become a bottom tab bar in portrait", src:"TOUCH" },
  { rule:"Breadcrumb bar always visible: Fighter › Attire N › Tab › Category", src:"TOUCH" },
  { rule:"Buy → Equip stays a two-step; owned items equip in one tap (T7 loop, touch-sized)", src:"TOUCH" },
];

/* ---- entry flow (verbatim) ---- */
export const ENTRY_FLOW = [
  { menu:"CREATE FIGHTER", src:"T7_LOOP" },
  { menu:"NEW FIGHTER → BODY tab (WMXIX CAW base)", src:"NM_BODY" },
  { menu:"EDIT FIGHTER → roster grid → pick fighter", src:"T7_LOOP" },
  { menu:"ATTIRE 1/2/3/4 (No Mercy 4-slot)", src:"NM_PROFILE" },
  { menu:"CUSTOMIZATION HUB — BODY / ATTIRE / PARTS / JIGGLE / WARDROBE / PROFILE", src:"T7_LOOP" },
  { menu:"WWE three doors: NEW CUSTOM SUPERSTAR (weight class + archetype → Persona) / WWE SUPERSTAR (edit roster attire+pose) / EDIT CUSTOM SUPERSTAR", src:"WWE_ENTRY" },
  { menu:"ATTIRE tab browse modes: TEKKEN SLOTS (T7 spine) ⇄ WWE REGIONS (region → garment type)", src:"WWE_ATTIRE" },
];

