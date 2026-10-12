const p=require('puppeteer-core');const fs=require('fs');const W=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{const b=await p.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const pg=await b.newPage();await pg.setViewport({width:430,height:900});
await pg.evaluateOnNewDocument(()=>{localStorage.setItem('nbi_mode','easy');localStorage.setItem('nbi_zone','กรุงเทพมหานคร/พระนคร');});
await pg.goto('https://checknam.com/',{waitUntil:'domcontentloaded'});await W(50000);
const r=await pg.evaluate(()=>{const out=[];const sv=place;let n=0;
 for(const k of Object.keys(PLACES)){ if(k===PIN_KEY) continue; n++; place=k; let rc=null; try{rc=riskCore();}catch(e){}
   const mx=rc&&rc.mx; let w=0; try{w=mx?ezWall(mx):0;}catch(e){}
   if(PLACES[k][3]==="กรุงเทพมหานคร"||w) out.push([k,w,mx?String(nm(mx)).trim():"-",mx?mx.river_name:"-",mx?+mx.station.min_bank:null,mx?+mx.storage_percent:null]); }
 place=sv; return {n,out};});
fs.writeFileSync('wall.json',JSON.stringify(r,null,0));
await b.close();})();
