// Pantera clip provenance (2026-11-10, t386u): for EVERY moveset row, the clip the game would actually play
// (Fighter._attackClipPlan with the T7 move pack loaded, as at boot). kind: t7 = real King T7 clip; t3row = a
// Tekken 3 King bank row (NOT King T7); generic:* = a bank generic action. Run: node tools/anim/pantera_clip_provenance.mjs [out.tsv]
import { dirname, join } from 'node:path'; import { fileURLToPath } from 'node:url';
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
await import(ROOT+'/tools/anim/node_game_env.mjs');
const THREE=await import('three'); const M=await import(ROOT+'/game/js/movesets.js'); const T=await import(ROOT+'/game/js/t3anims.js'); const F=await import(ROOT+'/game/js/fighter.js');
const FT=await import(ROOT+'/game/js/frame-tables.js'); await FT.frameTablesReady;
const q=console.log; console.log=()=>{}; console.warn=()=>{};
await M.loadFighterMovesets(); await M.ensureMovesets(['pantera']);
const bank=F.bankIdFor('pantera','pantera'); const clips=await T.loadT3Clips(THREE,bank); await T.loadT3Clips(THREE,'t7_king'); await T.ensureT7Moves('pantera',THREE);
console.log=q;
const f=Object.create(F.Fighter.prototype);
Object.assign(f,{char:{id:'pantera'},_movesetId:'pantera',t3actions:{},_t3:{bank,clips},root:{position:{x:0,y:0,z:0}},facing:1,dead:false,stun:0});
const ms=M.getFighterMoveset('pantera'); const rows=[]; const kinds={};
for (const [k,mv] of Object.entries(ms.moves)) {

  let p=null; try { const rm=F.getRealMove('pantera',k)||mv; p=f._attackClipPlan(rm,k);} catch(e){ p={name:'ERR '+e.message.slice(0,40)}; }
  const nm=p&&p.name?String(p.name):'NONE'; const kind=nm.startsWith('t7:')?'t7':nm.startsWith('row:')?'t3row':nm==='NONE'?'none':'generic:'+nm.split(':')[0];
  kinds[kind]=(kinds[kind]||0)+1; rows.push([k,mv.name||'',mv.anim_ref||'',nm,kind]);
}
console.log('bound bank',bank,'rows',rows.length, JSON.stringify(kinds));
const fs=await import('node:fs'); fs.writeFileSync(process.argv[2] || join(ROOT, 'docs/proof/2026-11-10/pantera-tekken-dash/clip-provenance.tsv'), 'key\tname\tanim_ref\tplanned_clip\tkind\n' + rows.map(r=>r.join('\t')).join('\n') + '\n');
for (const r of rows.filter(r=>['f,F+1','f,F+2','1','2','1,2','f,f,F+3','f+1+2','d/f+1','u/f+4','1+3','2+4'].includes(r[0]))) console.log(r.join(' | '));
