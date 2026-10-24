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
  WH_JIGGLE: "Western Heart jiggle system — per-area amplitude/frequency/damping, fat-mass scaling, female + male-fat roster families (jiggle lane, owner 2026-10-18)"
};

/* ---- ATTIRE category tree: T7 slots as the spine, T6 subdivisions nested ---- */
export const ATTIRE_TREE = [
  { slot:"1",  label:"Head",           icon:"🪖", src:"T7_SLOTS" },
  { slot:"2",  label:"Hairstyle",      icon:"💇", src:"T7_SLOTS", note:"mirrors BODY > Hair" },
  { slot:"3",  label:"Full Head",      icon:"🎭", src:"T7_SLOTS", note:"masks/helmets — CONFLICTS with Face Paint" },
  { slot:"4",  label:"Hair Accessory", icon:"🎀", src:"T7_SLOTS" },
  { slot:"5",  label:"Glasses",        icon:"👓", src:"T7_SLOTS", note:"DOA glasses live here too" },
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

/* ---- entry flow (verbatim) ---- */
export const ENTRY_FLOW = [
  { menu:"CREATE FIGHTER", src:"T7_LOOP" },
  { menu:"NEW FIGHTER → BODY tab (WMXIX CAW base)", src:"NM_BODY" },
  { menu:"EDIT FIGHTER → roster grid → pick fighter", src:"T7_LOOP" },
  { menu:"ATTIRE 1/2/3/4 (No Mercy 4-slot)", src:"NM_PROFILE" },
  { menu:"CUSTOMIZATION HUB — BODY / ATTIRE / PARTS / JIGGLE / WARDROBE / PROFILE", src:"T7_LOOP" },
];
