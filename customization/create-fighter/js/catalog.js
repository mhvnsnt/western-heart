/* catalog.js — processes PARTS-INDEX.json into UI-ready categories.
   Real part ids/names from the 3,372-part teardown index. Geometry status is
   honest: no .obj/.glb mesh is wired yet, so every part carries geometryPending:true
   and the preview shows a labeled socket-proxy marker, never a fake mesh. */

export const CATEGORIES = [
  { key:'upper_body',  icon:'🥋', label:'Upper Body',  slotId:'9',  anchor:'Spine2'   },
  { key:'lower_body',  icon:'👖', label:'Lower Body',  slotId:'11', anchor:'Hips'     },
  { key:'attire',      icon:'👘', label:'Full Body',   slotId:'10', anchor:'Hips'     },
  { key:'hair',        icon:'💇', label:'Hair',        slotId:'2',  anchor:'Head'     },
  { key:'faces',       icon:'😐', label:'Face',        slotId:'6',  anchor:'Head'     },
  { key:'gloves',      icon:'🥊', label:'Gloves',      slotId:'H',  anchor:'RightHand'},
  { key:'shoes',       icon:'🥾', label:'Shoes',       slotId:'F',  anchor:'RightFoot'},
  { key:'accessories', icon:'⌚', label:'Accessories', slotId:'12', anchor:'LeftForeArm'},
  { key:'gears',       icon:'⛓️', label:'Gears',       slotId:'14', anchor:'Spine1'   },
  { key:'bodies',      icon:'🦾', label:'Body Parts',  slotId:'B1', anchor:'Hips'     },
  { key:'skins',       icon:'🎨', label:'Skins',       slotId:'B2', anchor:'Hips'     },
];

/* T7-style conflict zones: equipping one of these unequips (after confirm) the other. */
export const CONFLICTS = {
  '10': ['9','11'],   // Full Body vs Upper/Lower Body
  '9':  ['10'],
  '11': ['10'],
};

function hashStr(s){ let h=2166136261; for(let i=0;i<s.length;i++){ h^=s.charCodeAt(i); h=Math.imul(h,16777619);} return h>>>0; }

export function friendlyName(part){
  const id = part.part_id;
  // wmxix: edit_data/MODEL/Man/Upper_Body/mp0_000/c5.ymg
  let m = id.match(/MODEL\/(?:Man|Woman)\/([^/]+)\/([a-z0-9]+)_(\d+)/i);
  if(m) return `${titleCase(m[1].replace(/_/g,' '))} · Set ${m[3]}`;
  // no-mercy: no-mercy:0x10f6:body_parts/model_10F6.obj
  m = id.match(/^no-mercy:0x([0-9a-f]+):([^:]+)\//i);
  if(m) return `${titleCase(m[2].replace(/_/g,' '))} · 0x${m[1].toUpperCase()}`;
  m = id.match(/^no-mercy:skin-tex:(.+)\.png/i);
  if(m) return `Skin Texture · ${m[1]}`;
  return id.split('/').pop();
}
function titleCase(s){ return s.replace(/\b\w/g,c=>c.toUpperCase()); }

export function priceFor(part){
  const h = hashStr(part.part_id);
  return 100 + (h % 14) * 100;             // 100–1500 Fight Money, deterministic
}
export function rarityFor(part){
  const h = hashStr(part.part_id);
  return 1 + (h % 5);                       // 1–5 stars, deterministic
}

export class Catalog {
  constructor(indexJson){
    this.byCategory = {};
    for(const c of [...CATEGORIES, ...UNIVERSAL_CATEGORIES]) this.byCategory[c.key] = [];
    for(const p of indexJson.parts){
      if(this.byCategory[p.slot]){
        this.byCategory[p.slot].push({
          ...p,
          displayName: friendlyName(p),
          price: priceFor(p),
          rarity: rarityFor(p),
          geometryPending: true,   // no .obj/.glb wired to the preview yet — honest badge
        });
      }
    }
    this.total = indexJson.total_parts;
  }
  items(catKey){ return this.byCategory[catKey] || []; }
  count(catKey){ return this.items(catKey).length; }
  get(partId){
    for(const k of Object.keys(this.byCategory)){
      const f = this.byCategory[k].find(p=>p.part_id===partId);
      if(f) return f;
    }
    return null;
  }
  catForPart(partId){
    for(const c of CATEGORIES){
      if(this.byCategory[c.key].some(p=>p.part_id===partId)) return c;
    }
    return null;
  }
  catBySlotId(slotId){ return CATEGORIES.find(c=>c.slotId===slotId); }
}

/* ---- Universal parts registry wiring (2026-10-18) ----
   The new universal libraries (eye-library, decal-library/pantera,
   parts/pantera-eyes, parts/superhero) are wired into the suite via
   customization/PARTS-REGISTRY.json (see packages/creation-suite/src/parts.js).
   Their entries land in the parts index under the slots below, so the
   existing Catalog picks them up untouched — this only ADDS categories.
   Eye/decal texture swaps are universal (character_mappings); superhero mesh
   pieces attach at bone sockets on any character. */
export const UNIVERSAL_CATEGORIES = [
  { key:'eyes',   icon:'👁️', label:'Eyes',           slotId:'eyes',   anchor:'Head' },
  { key:'decals', icon:'🏷️', label:'Decals & Logos', slotId:'decals', anchor:'Hips' },
  { key:'masks',  icon:'🎭', label:'Masks & Pieces', slotId:'masks',  anchor:'Head' },
];
// Merged view: teardown-index categories + universal-library categories.
export const ALL_CATEGORIES = [...CATEGORIES, ...UNIVERSAL_CATEGORIES];
