const {chromium}=require('/workspace/cs-proof/node_modules/playwright-core');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--use-gl=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage({viewport:{width:2000,height:760}});
p.on('console',m=>console.log('C',m.text()));p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('http://127.0.0.1:59653/index.html');await p.waitForFunction(()=>document.title==='DONE',null,{timeout:60000});
console.log(JSON.stringify(await p.evaluate(()=>window.REPORT),null,0));await p.screenshot({path:'/workspace/cs-proof/proof.png'});await b.close();})();
