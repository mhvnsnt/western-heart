import { chromium } from 'playwright';
const [id,opp='awapop']=process.argv.slice(2); const BASE='http://127.0.0.1:8831', OUT='/workspace/rma/shots/rig';
const b=await chromium.launch({channel:'chrome',args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
for (const [w,h] of (process.env.VP?[process.env.VP.split('x').map(Number)]:[[390,844],[844,390]])) {
  const ctx=await b.newContext({viewport:{width:w,height:h},hasTouch:true,isMobile:true});
  await ctx.addInitScript(()=>{globalThis.__WH_PRIVATE_ASSETS=true});
  const p=await ctx.newPage(); const logs=[]; p.on('response',r=>{if(r.status()>=400)logs.push('HTTP'+r.status()+' '+r.url())});p.on('pageerror',e=>logs.push('ERR '+e.message)); p.on('console',m=>{const t=m.text(); if(m.type()==='error'||/\[WH\]/.test(t))logs.push(t)});
  await p.goto(BASE+'/game/index.html'); await p.waitForSelector('#screen-menu [data-mm]',{state:'visible',timeout:30000}); await p.waitForTimeout(4000);
  const tap=async s=>{try{await p.tap(s,{timeout:40000})}catch(e){await p.screenshot({path:`${OUT}/fail-${w}.png`});console.log('FAILTAP',s,JSON.stringify(logs.slice(0,6)));throw e}await p.waitForTimeout(1500)};
  await tap('[data-mm="versus"]'); await p.waitForTimeout(3000);
  await tap(`.char-card[data-id="${id}"]`); await tap('#confirm-fighter'); await tap(`.char-card[data-id="${opp}"]`); await tap('#confirm-fighter');
  await tap('#confirm-stage');
  await p.waitForFunction(()=>{const e=document.getElementById('hud');return e&&getComputedStyle(e).display!=='none'&&!e.classList.contains('hidden')},null,{timeout:240000}).catch(async e=>{await p.screenshot({path:`${OUT}/fail-hud-${w}.png`});console.log('HUDFAIL',JSON.stringify(logs.filter(l=>!/suite slot/.test(l)).slice(-25)));throw e});
  await p.waitForTimeout(2500); await p.screenshot({path:`${OUT}/${id}-fight-${w}x${h}.png`});
  await p.waitForTimeout(2500); await p.screenshot({path:`${OUT}/${id}-fight2-${w}x${h}.png`});
  console.log(w,h,JSON.stringify(logs.filter(l=>/remap|ERR|load failed/i.test(l)).slice(0,8)));
  await ctx.close();
}
await b.close();
