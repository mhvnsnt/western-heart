/* layering.js — WWE 2K CAW layering rules for the Creation Suite.
   Source: customization/wwe2k-caw/CAW-SUITE-BREAKDOWN.md (WWE 2K19, most
   recent fully documented). WWE 2K19/2K18 GAME FILES ARE NOT ON DISK, so
   this module wires the LAYERING LOGIC as pipeline rules — not extracted
   assets. Merged with Tekken slot-conflict rules from
   customization/create-fighter/js/catalog.js. */

/* 2K19 attire layer order: bottom (skin) -> top (outerwear). */
export const LAYER_ORDER = [
  'body',        // base body / skin
  'tattoo',      // tattoo canvas (under attire)
  'underwear',   // trunks / base layer
  'lower_body',  // pants, tights, shorts, trunks
  'socks',       // part of feet region
  'shoes',       // boots, shoes (separate slot)
  'upper_body',  // shirts, jackets, vests, singlets, bare
  'gloves',      // hands (separate slot)
  'arm_bands',   // elbow pads, wrist tape, arm bands
  'head_base',   // face / makeup / face paint / masks
  'hair',        // 100+ styles, layered on head
  'head_gear',   // hats, helmets, headbands
  'glasses',     // eyewear
  'facial_hair', // beards, goatees, stubble — layered
  'accessories', // belts, chains, jewelry
  'aura',        // auras, visual effects
];

/* Regions that accept MULTIPLE stacked items (2K19 layered attire). */
export const MULTI_STACK_REGIONS = {
  head:        ['head_base', 'hair', 'head_gear', 'glasses', 'facial_hair'],
  upper_body:  ['tattoo', 'underwear', 'upper_body'],
  arms:        ['gloves', 'arm_bands'],
  lower_body:  ['underwear', 'lower_body'],
  feet:        ['socks', 'shoes'],
  accessories: ['accessories'],
};

/* Left/right independent slots (2K19: gloves, wrist tape, elbow pads,
   arm bands, knee pads, shin guards are L/R independent). */
export const LR_INDEPENDENT = ['gloves', 'arm_bands', 'knee_pads', 'shin_guards'];

/* Tekken slot conflicts (from catalog.js CONFLICTS), merged into the
   layering resolver: equipping one of these UNEQUIPS the other. */
export const SLOT_CONFLICTS = {
  full_body: ['upper_body', 'lower_body'],
  upper_body: ['full_body'],
  lower_body: ['full_body'],
  head_gear: ['hat_alt'],   // one head-gear at a time
};

/* Per-item color channels (2K19: every attire piece has independent
   color channels) + material finishes (fabric, leather, metal, matte). */
export const COLOR_CHANNELS = ['primary', 'secondary', 'accent'];
export const MATERIALS = ['fabric', 'leather', 'metal', 'matte', 'gloss'];

/* Resolve an equip request against current loadout.
   Returns { loadout, removed[] } — removed items are the conflict victims. */
export function resolveEquip(loadout, item){
  const removed = [];
  const conflicts = SLOT_CONFLICTS[item.suite_slot] || [];
  for(const slot of conflicts){
    if(loadout[slot] && loadout[slot] !== item.id){
      removed.push(loadout[slot]);
      delete loadout[slot];
    }
  }
  // multi-stack regions: stack, don't replace (except single-slot items)
  if(!MULTI_STACK_REGIONS[item.region]){
    loadout[item.suite_slot] = item.id;
  } else {
    loadout[item.suite_slot] = item.id;
  }
  return { loadout, removed };
}

/* Mirror attire (2K19): copy left-side items to right, retaining
   colors/materials. */
export function mirrorAttire(loadout){
  const out = { ...loadout };
  for(const slot of LR_INDEPENDENT){
    if(out[slot + '_L']) out[slot + '_R'] = out[slot + '_L'];
  }
  return out;
}

/* Randomizer (2K19 Attire Randomizer): build a complete matching outfit
   from the registry — one deterministic pick per region. */
export function randomizeAttire(registryParts, seed = 1){
  let h = seed >>> 0;
  const pick = arr => arr[(h = (Math.imul(h, 1664525) + 1013904223) >>> 0) % arr.length];
  const bySlot = {};
  for(const p of registryParts){
    (bySlot[p.suite_slot] = bySlot[p.suite_slot] || []).push(p);
  }
  const loadout = {};
  for(const region of ['upper_body', 'lower_body', 'shoes', 'gloves', 'hair', 'head_gear', 'accessories']){
    const pool = bySlot[region];
    if(pool && pool.length) loadout[region] = pick(pool).id;
  }
  return loadout;
}
