// ตรวจตัวหนังสือบนภาพลำน้ำ: ขนาด น้ำหนัก ระยะ และความต่างสี (WCAG) เทียบกับพื้นที่อยู่ข้างหลังจริง
const p=require('puppeteer-core');const fs=require('fs');const W=ms=>new Promise(r=>setTimeout(r,ms));
const URL=process.env.URL||'https://checknam.com/';
const Z=[['นนทบุรี/บางใหญ่','light',390],['นนทบุรี/บางใหญ่','light',1280],['ปราจีนบุรี/บ้านสร้าง','dark',390],['กรุงเทพมหานคร/พระนคร','light',390],['แม่ฮ่องสอน/ปาย','light',390]];
(async()=>{const b=await p.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
let i=0;for(const [z,th,vw] of Z){i++;try{const pg=await b.newPage();await pg.setViewport({width:vw,height:1000,deviceScaleFactor:2});
await pg.evaluateOnNewDocument((z,th)=>{localStorage.setItem('nbi_mode','easy');localStorage.setItem('nbi_th',th);localStorage.setItem('nbi_zone',z);},z,th);
pg.on('pageerror',e=>fs.appendFileSync('err.txt',z+' '+e+'\n'));
await pg.goto(URL,{waitUntil:'domcontentloaded'});await W(40000);
const tag=i+'-'+z.split('/')[1]+'-'+vw+'-'+th;
const hx=await pg.$('#easy .ez-x');if(!hx){fs.appendFileSync('err.txt',tag+' no hero\n');continue;}
await pg.evaluate(()=>{const e=document.querySelector('#easy .ez-x');window.scrollTo(0,e.getBoundingClientRect().top+scrollY-170);});await W(1200);
const bb={};
const bb1=await (await pg.$('#easy .ez-x')).boundingBox();const sy=await pg.evaluate(()=>scrollY);const clip={x:0,y:Math.max(0,bb1.y+sy-8),width:vw,height:Math.min(820,1000-bb1.y)};
await pg.screenshot({path:tag+'.png',clip});
// พื้นหลังจริงใต้ตัวหนังสือ: ซ่อนตัวหนังสือบนภาพแล้วถ่ายอีกรูป
const SEL=['.rd b','.rd span','.ez-chip','.xs-g'];const bb2=await (await pg.$('#easy .ez-x')).boundingBox();Object.assign(bb,bb2);
const rects=await pg.evaluate(S=>{const h=document.querySelector('#easy .ez-x');return S.map(s=>{const e=h.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect(),c=getComputedStyle(e);return {s,x:r.x,y:r.y,w:r.width,h:r.height,fs:c.fontSize,fw:c.fontWeight,lh:c.lineHeight,col:c.color,bg:c.backgroundColor,txt:e.textContent.trim().slice(0,40)}})},SEL);
await pg.addStyleTag({content:'#easy .ez-x .rd *,#easy .ez-x .xs-g{color:transparent!important;text-shadow:none!important}#easy .ez-x .ez-chip *{visibility:hidden!important}'});await W(300);
const bgshot=await pg.screenshot({encoding:'base64',clip:{x:bb.x,y:bb.y+sy,width:bb.width,height:bb.height}});
const res=await pg.evaluate(async(b64,rects,bb)=>{const im=new Image();im.src='data:image/png;base64,'+b64;await im.decode();const c=document.createElement('canvas');c.width=im.width;c.height=im.height;const x=c.getContext('2d');x.drawImage(im,0,0);const k=im.width/bb.width;
const lin=v=>{v/=255;return v<=.03928?v/12.92:((v+.055)/1.055)**2.4},L=(r,g,b)=>.2126*lin(r)+.7152*lin(g)+.0722*lin(b);
const parse=s=>s.match(/[\d.]+/g).map(Number);
return rects.map(r=>{if(!r)return null;const [tr,tg,tb]=parse(r.col);const Lt=L(tr,tg,tb);const x0=Math.max(0,Math.round((r.x-bb.x)*k)),y0=Math.max(0,Math.round((r.y-bb.y)*k)),w=Math.round(r.w*k),h=Math.round(r.h*k);if(w<1||h<1)return {...r,cr:null};const d=x.getImageData(x0,y0,Math.min(w,c.width-x0),Math.min(h,c.height-y0)).data;const v=[];for(let i=0;i<d.length;i+=16){const Lb=L(d[i],d[i+1],d[i+2]);const a=Math.max(Lt,Lb),b=Math.min(Lt,Lb);v.push((a+.05)/(b+.05));}v.sort((a,b)=>a-b);return {...r,crMin:+v[0].toFixed(2),crP10:+v[Math.floor(v.length*.1)].toFixed(2),crMed:+v[Math.floor(v.length/2)].toFixed(2)};});},bgshot,rects,bb);
// ตัวหนังสือใต้ภาพ
const below=await pg.evaluate(()=>{const lin=v=>{v/=255;return v<=.03928?v/12.92:((v+.055)/1.055)**2.4},L=a=>.2126*lin(a[0])+.7152*lin(a[1])+.0722*lin(a[2]);const P=s=>{const a=s.match(/[\d.]+/g).map(Number);return s.startsWith('color(')?[a[0]*255,a[1]*255,a[2]*255,a.length>3?a[3]:1]:a};
const bgOf=e=>{while(e){const c=getComputedStyle(e).backgroundColor;const a=P(c);if(a.length<4||a[3]>.9)return c;e=e.parentElement;}return getComputedStyle(document.body).backgroundColor;};
return ['.ez-rkh span','.ez-rkh b','.ez-stn','.ez-stn b','.ez-wxn','.ez-say2','.ez-sc .l span','.ez-sc .l .on','.ez-fh2','.ez-fgt'].map(s=>{const e=document.querySelector('#easy '+s);if(!e)return {s,none:1};const c=getComputedStyle(e),bg=bgOf(e),a=L(P(c.color)),b=L(P(bg));const r=e.getBoundingClientRect();return {s,fs:c.fontSize,fw:c.fontWeight,lh:c.lineHeight,mt:c.marginTop,col:c.color,bg,cr:+((Math.max(a,b)+.05)/(Math.min(a,b)+.05)).toFixed(2),top:Math.round(r.top),h:Math.round(r.height),ov:e.scrollWidth>e.clientWidth+1?[e.scrollWidth,e.clientWidth]:0,w:Math.round(r.width)}});});
fs.appendFileSync('audit.txt',tag+'\nON '+JSON.stringify(res)+'\nBELOW '+JSON.stringify(below)+'\n\n');
await pg.close();}catch(e){fs.appendFileSync('err.txt',z+' '+e+'\n');}}
await b.close();})();
