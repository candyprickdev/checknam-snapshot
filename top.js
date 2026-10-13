const p=require('puppeteer-core');const fs=require('fs');const W=ms=>new Promise(r=>setTimeout(r,ms));
const URL=process.env.URL||'https://stage.checknam.pages.dev/';
(async()=>{const b=await p.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
for(const [z,th,vw,vh,pin] of [['__pin__','dark',390,844,{la:13.875,lo:100.36}],['__pin__','light',390,844,{la:13.856,lo:100.398}],['__pin__','light',390,844,{la:13.80,lo:100.52}]]){try{
const pg=await b.newPage();await pg.setViewport({width:vw,height:vh,deviceScaleFactor:2});
await pg.evaluateOnNewDocument((z,th,pin)=>{localStorage.setItem('nbi_mode','easy');localStorage.setItem('nbi_th',th);localStorage.setItem('nbi_zone',z);localStorage.setItem('nbi_pin',JSON.stringify(pin));},z,th,pin);
pg.on('pageerror',e=>fs.appendFileSync('err.txt',z+' '+e+'\n'));
await pg.goto(URL,{waitUntil:'domcontentloaded'});await W(35000);
await pg.screenshot({path:`top-${pin.la}-${pin.lo}.png`});
fs.appendFileSync('dom.txt',vw+th+'\n'+await pg.evaluate(()=>{const e=document.querySelector('#zH1');const h=document.querySelector('header,.top,#hdr');return (h?h.outerHTML.slice(0,1500):'nohdr')+'\n---\n'+(e?e.outerHTML.slice(0,2500):'')})+'\n\n');
await pg.close();}catch(e){fs.appendFileSync('err.txt',e+'\n');}}
await b.close();})();
