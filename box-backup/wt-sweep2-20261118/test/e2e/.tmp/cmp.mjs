import fs from 'node:fs';
const idx=JSON.parse(fs.readFileSync(new URL('../../../game/assets/movesets/index.json',import.meta.url),'utf8')).fighters;
const A=(await import('./bodies-old.mjs')).bodyFor, B=(await import('../moveset-sweep.bodies.mjs')).bodyFor;
let n=0;for(const id of Object.keys(idx)){const a=A(id,idx[id]),b=B(id,idx[id]);if(a.model!==b.model||a.how!==b.how&&a.ok!==b.ok){n++;console.log(id,':',a.model,a.ok,'->',b.model,b.ok,b.how)}}console.log('changed',n,'of',Object.keys(idx).length)
