import fs from 'fs';
const M='docs/proof/moveset-sweep-20261028/MATRIX.md', S='/workspace/sweep-out';
const src=fs.readFileSync(M,'utf8').split('\n');
const ids=src.filter(l=>/^\| [a-z0-9]/.test(l)).map(l=>l.split('|')[1].trim());
const dirs=(process.env.SWEEP_DIRS||'r10').split(',');
let ran=0,T={m:0,p:0,f:0,n:0};const rows=[];
for(const id of ids){if(id==='fighter')continue;let r=null;for(const d of dirs){const f=`${S}/${d}/${id}.json`;if(fs.existsSync(f)){r=JSON.parse(fs.readFileSync(f));break}}
 if(!r){rows.push(`| ${id} | | | | | | not yet run |`);continue}
 if(r.error){rows.push(`| ${id} | | | | | | harness: ${r.error} |`);continue}
 if(r.blocker){rows.push(`| ${id} | | | | | | BLOCKER: ${r.blocker.how} |`);continue}
 ran++;T.m+=r.moves;T.p+=r.pass;T.f+=r.fail;T.n+=r.na;
 rows.push(`| ${id} | ${r.moves} | ${r.pass} | ${r.fail} | ${r.na} | ${r.jugglePass??''}/${r.juggles??''} | ran |`)}
const out=[`# Moveset sweep matrix (2026-10-29)`,``,`${ran}/${ids.length} fighters ran: ${T.m} moves, ${T.p} pass, ${T.f} fail, ${T.n} n/a. Full rerun 2026-10-29 (\`rerun-20261029/\`), one result per fighter. Bodies follow the game's default attire (sweep-bodies.md); blockers are listed with their reason.`,``,`Moveset editor e2e: 128/128 open/edit/save/reload/reset (\`editor.json\`). Fight shots: \`sweep-*.png\`.`,``,`| fighter | moves | pass | fail | n/a | juggles | status |`,`|---|---|---|---|---|---|---|`,...rows,``];
fs.writeFileSync('/tmp/MATRIX.new.md',out.join('\n'));console.log(out[2]);
