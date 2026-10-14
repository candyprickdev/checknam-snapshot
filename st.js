const p=require('puppeteer-core');const fs=require('fs');const W=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{const b=await p.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});const pg=await b.newPage();
await pg.evaluateOnNewDocument(()=>{localStorage.setItem('nbi_mode','easy');localStorage.setItem('nbi_zone','นนทบุรี/บางใหญ่');});
await pg.goto('https://stage.checknam.pages.dev/',{waitUntil:'domcontentloaded'});await W(15000);
const r=await pg.evaluate(async()=>{const out={};for(const u of ['/api/status','/api/news?prov='+encodeURIComponent('นนทบุรี')+'&am='+encodeURIComponent('บางใหญ่'),'/api/tmdwarn']){try{const x=await fetch(u);out[u]=await x.text();}catch(e){out[u]=String(e)}}return out;});
fs.writeFileSync('st.json',JSON.stringify(r));await b.close();})();
