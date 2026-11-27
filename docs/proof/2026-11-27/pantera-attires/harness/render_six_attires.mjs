const { chromium } = await import('/home/box/dpipe/pw/node_modules/playwright-core/index.mjs');
import fs from 'fs';
const out=process.argv[2]; fs.mkdirSync(out,{recursive:true});
const MODELS=['pantera-leoman','pantera-leopard-king','pantera','pantera-snow-leopard','pantera-crimson-rage','pantera-p2'];
const POSES=[['idle','stance',0.5],['walk','walkFwd',0.4],['punch','light',0.45],['kick','medium',0.45],['hit','hit',0.35]];
const browser = await chromium.launch({ executablePath: '/opt/google/chrome/chrome', args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 1200, height: 960 } });
const errs=[]; page.on('pageerror',e=>errs.push(e.message)); page.on('response', r => { if (r.status()>=400) errs.push(r.status()+' '+r.url()); });
await page.goto('http://127.0.0.1:8799/game/poselab.html', { waitUntil: 'load' });
await page.waitForFunction(() => window.__poselab, null, { timeout: 60000 });
// attire resolution exactly as the select screen would (attires.js), per slot
const ladder = await page.evaluate(async()=>{ const m=await import('./js/attires.js'); const r=await import('./js/roster-full.js'); const b=r.FULL_ROSTER.find(x=>x.id==='pantera'); const out={}; for (const k of Object.keys(m)) out[k]=typeof m[k]; let l=null; try { l=(m.attiresFor||m.attireLadderFor)(b).map(a=>a.model||a); } catch(e){ l='ERR '+e.message; } return {exports:out, ladder:l}; });
const res={ladder, rows:[]};
for (const model of MODELS) for (const [name,clip,t] of POSES) {
  try {
    const r=await page.evaluate((a)=>window.__poselab.showFighter(a), {id:'pantera',clip,t,model});
    const k=await page.evaluate(()=>{ const c=window.__poselab.cur(); const b={}; c.tgt.traverse(o=>{ if(o.isBone){ const n=o.name.replace(/^mixamorig[:_]?/,''); if(!b[n]) b[n]=o; } });
      const V=b.Hips.position.constructor; const P=n=>b[n].getWorldPosition(new V()); const q=b.Hips.getWorldQuaternion(new b.Hips.quaternion.constructor());
      let minY=1e9; c.tgt.traverse(o=>{ if(o.isSkinnedMesh){ const v=new V(); const pos=o.geometry.attributes.position; for(let i=0;i<pos.count;i+=7){ o.getVertexPosition(i,v); o.localToWorld(v); if(v.y<minY) minY=v.y; } } });
      const o={minY:+minY.toFixed(3)}; for (const s of ['Left','Right']) { const h=P(s+'UpLeg'),kk=P(s+'Leg'),a=P(s+'Foot'); const u=h.clone().sub(kk).normalize(), d=a.clone().sub(kk).normalize(); o[s+'KneeDeg']=+(Math.acos(Math.max(-1,Math.min(1,u.dot(d))))*180/Math.PI).toFixed(1); }
      return o; });
    const st=await page.evaluate(()=>window.__poselab.stretchMap({minAbs:0.01}).map(s=>s.p999));
    for (const yaw of [0,90]) { await page.evaluate((y)=>window.__poselab.closeup({yaw:y,part:'full'}), yaw); fs.writeFileSync(`${out}/${model}_${name}_y${yaw}.png`, await page.screenshot({clip:{x:150,y:0,width:900,height:900}})); }
    res.rows.push({model,name,clip,bank:r.bank,resolvedModel:r.model,...k,stretchP999max:Math.max(...st.filter(x=>x!=null))});
  } catch(e){ res.rows.push({model,name,error:e.message.slice(0,200)}); }
}
res.errors=[...new Set(errs)];
fs.writeFileSync(`${out}/results.json`, JSON.stringify(res,null,1)); console.log(JSON.stringify(res.ladder)); for (const r of res.rows) console.log(JSON.stringify(r)); console.log(res.errors.join('\n')); await browser.close();
