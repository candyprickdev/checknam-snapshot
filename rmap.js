const p=require('puppeteer-core');const fs=require('fs');const W=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{const b=await p.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
for(const [z,th,vw] of [['นนทบุรี/บางใหญ่','dark',430],['กรุงเทพมหานคร/พระนคร','light',390],['เชียงใหม่/เมืองเชียงใหม่','light',1280],['นครราชสีมา/เมืองนครราชสีมา','dark',390]]){try{
const pg=await b.newPage();await pg.setViewport({width:vw,height:900,deviceScaleFactor:2});
await pg.evaluateOnNewDocument((z,th)=>{localStorage.setItem('nbi_mode','easy');localStorage.setItem('nbi_th',th);localStorage.setItem('nbi_zone',z);},z,th);
pg.on('pageerror',e=>fs.appendFileSync('err.txt',z+' '+e+'\n'));
await pg.goto('https://checknam.com/',{waitUntil:'domcontentloaded'});await W(30000);
await pg.evaluate(()=>document.getElementById('rmap').scrollIntoView({block:'center'}));await W(12000);
const el=await pg.$('#rmap');await el.screenshot({path:z.split('/')[1]+'-'+vw+'.png'});await pg.close();}catch(e){fs.appendFileSync('err.txt',z+' '+e+'\n');}}
await b.close();})();
