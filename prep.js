// เตรียมสำเนาก่อนส่งให้เว็บ: ตรวจรูปแบบ บีบอัด gzip และแยกค่ารายชั่วโมงแบบย่อ
// ทำงานหนักที่นี่แทนฝั่งเว็บ ให้เว็บแค่เก็บไฟล์ ไม่ต้องอ่านข้อมูลทั้งก้อนทุก 5 นาที
// ใช้: node prep.js <k> <in.json>  -> สร้าง <in>.gz และ <in>.h.json (ถ้ามีค่ารายชั่วโมง)
const fs = require('fs'), zlib = require('zlib'); const [,, K, IN] = process.argv;
const txt = fs.readFileSync(IN, 'utf8'); const j = JSON.parse(txt);
const n = x => (x === null || x === undefined || x === '' || isNaN(+x)) ? null : +x;
const tOf = s => Date.parse(String(s || '').replace(' ', 'T').slice(0, 16) + ':00+07:00');
let h = null;
if (K === 'waterlevel_load') {
  const d = j.waterlevel_data?.data; if (!Array.isArray(d) || d.length <= 100) { console.error('bad shape'); process.exit(1); }
  h = []; for (const x of d) { const id = +x?.station?.id, t = tOf(x?.waterlevel_datetime), v = n(x?.waterlevel_msl), q = n(x?.discharge);
    if (id > 0 && t > 0 && (v !== null || q !== null)) h.push([id, t, v, q]); }
} else if (K === 'rain_24h') {
  const d = j.data; if (!Array.isArray(d) || d.length <= 100) { console.error('bad shape'); process.exit(1); }
  h = []; for (const x of d) { const id = +x?.station?.id, t = tOf(x?.rainfall_datetime), v = n(x?.rain_1h);
    if (id > 0 && t > 0 && v !== null && v >= 0 && v <= 300) h.push([id, t, Math.round(v * 10) / 10]); }
}
fs.writeFileSync(IN + '.gz', zlib.gzipSync(txt, { level: 6 }));
if (h) fs.writeFileSync(IN + '.h.json', JSON.stringify(h));
console.log(K, 'gz', fs.statSync(IN + '.gz').size, 'h', h ? h.length : 0);
