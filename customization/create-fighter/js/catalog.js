/* catalog.js — processes PARTS-INDEX.json into UI-ready categories.
   Real part ids/names from the 3,372-part teardown index. Geometry status is
   honest: no .obj/.glb mesh is wired yet, so every part carries geometryPending:true
   and the preview shows a labeled socket-proxy marker, never a fake mesh. */

export const CATEGORIES = [
  { key:'upper_body',  icon:'🥋', label:'Upper Body',  slotId:'9',  anchor:'Spine2'   },
  { key:'lower_body',  icon:'👖', label:'Lower Body',  slotId:'11', anchor:'Hips'     },
  { key:'attire',      icon:'👘', label:'Full Body',   slotId:'10', anchor:'Hips'     },
  { key:'head',        icon:'🎩', label:'Head',        slotId:'1',  anchor:'Head'     },
  { key:'hair',        icon:'💇', label:'Hair',        slotId:'2',  anchor:'Head'     },
  { key:'facialhair',  icon:'🧔', label:'Facial Hair', slotId:'7',  anchor:'Head'     },
  { key:'faces',       icon:'😐', label:'Face',        slotId:'6',  anchor:'Head'     },
  { key:'gloves',      icon:'🥊', label:'Gloves',      slotId:'H',  anchor:'RightHand'},
  { key:'shoes',       icon:'🥾', label:'Shoes',       slotId:'F',  anchor:'RightFoot'},
  { key:'accessories', icon:'⌚', label:'Accessories', slotId:'12', anchor:'LeftForeArm'},
  { key:'gears',       icon:'⛓️', label:'Gears',       slotId:'14', anchor:'Spine1'   },
  { key:'bodies',      icon:'🦾', label:'Body Parts',  slotId:'B1', anchor:'Hips'     },
  { key:'skins',       icon:'🎨', label:'Skins',       slotId:'B2', anchor:'Hips'     },
  { key:'textures',    icon:'🖌️', label:'Textures',    slotId:'TX', anchor:'Hips'     },
  { key:'defjam_unsorted', icon:'🎮', label:'Def Jam — Unsorted', slotId:'14', anchor:'Spine1' },
];

/* T7-style conflict zones: equipping one of these unequips (after confirm) the other.
   §7 spine: Full Body(10) vs Upper(9)/Lower(11); Full Head(3) vs Face Paint(8)/Facial Hair(7). */
export const CONFLICTS = {
  '10': ['9','11'],   // Full Body vs Upper/Lower Body
  '9':  ['10'],
  '11': ['10'],
  '3':  ['8','7'],    // Full Head vs Face Paint / Facial Hair
  '8':  ['3'],
  '7':  ['3'],
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
  // cc0-hair: cc0-hair:quaternius-buns:Hair_Buns.gltf
  m = id.match(/^cc0-hair:([^:]+):(.+?)\.(gltf|glb)$/i);
  if(m) return `${titleCase(m[1].replace(/-/g,' '))} (CC0)`;
  // defjam: defjam:defjam:V2CP_110_0001_A.o
  m = id.match(/^defjam:defjam:V2CP_(\d+)_(\d+)_?([A-Z])?\.?o?$/i);
  if(m) return `Def Jam · ${m[1]}-${m[2]}${m[3]||''} (CAW part)`;
  // defjam-v2ip: defjam-v2ip:V2IP_001A.o / V2IP_501A_F.o
  m = id.match(/^defjam-v2ip:V2IP_(\d+)([A-Z])(?:_([A-Z]))?\.o$/i);
  if(m) return `Def Jam · V2IP ${m[1]}${m[2]}${m[3]?'_'+m[3]:''} (base model)`;
  // doa4: doa4:chrone_00_7861v_14370t.glb
  m = id.match(/^doa4:([a-z]+)_(\d+)_/i);
  if(m) return `DOA4 · ${m[1]} costume ${m[2]}`;
  m = id.match(/^doa4:(bass_cos\d+_.*)\.glb$/i);
  if(m) return `DOA4 · ${m[1].replace(/_/g,' ')}`;
  // wmxix-tex: wmxix-tex:face_0123.png
  m = id.match(/^wmxix-tex:(.+)$/i);
  if(m) return `WMXIX texture · ${m[1]}`;
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
          // CC0 universal parts ship real geometry (GLB/glTF in-repo); teardown
          // ymg/obj parts are honest about it: geometryPending until decoded.
          geometryPending: !(p.geometryReady || p.source_game==='cc0-hair'),
        });
      }
    }
    this.total = indexJson.total_parts;
    /* FACIAL HAIR is a virtual category (worker 38): in the AKI engine beards
       live in the face TEXTURE parts, so the WWE flow's FACIAL HAIR step
       merges face textures + head parts. Equips into T7 slot 7. */
    this.byCategory['facialhair'] = [
      ...(this.byCategory['faces']||[]).filter(p=>p.kind==='texture'),
      ...(this.byCategory['head']||[]),
    ];
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
