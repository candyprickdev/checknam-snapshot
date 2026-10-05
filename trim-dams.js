// ตัด thailand_main (~10MB) เหลือเฉพาะข้อมูลเขื่อนที่หน้าเว็บใช้ -> ส่งเป็นสำเนา "dams"
const fs = require('fs'); const [,, IN, OUT] = process.argv;
const j = JSON.parse(fs.readFileSync(IN, 'utf8'));
const data = (j.dam?.data?.data || []).map(x => ({
  dam: { dam_name: { th: x.dam?.dam_name?.th }, normal_storage: x.dam?.normal_storage, dam_lat: x.dam?.dam_lat, dam_long: x.dam?.dam_long },
  dam_storage_percent: x.dam_storage_percent, dam_inflow: x.dam_inflow, dam_released: x.dam_released, dam_storage: x.dam_storage,
  dam_date: x.dam_date, geocode: { province_name: { th: x.geocode?.province_name?.th } }
}));
if (data.length < 10) { console.error('too few dams', data.length); process.exit(1); }
fs.writeFileSync(OUT, JSON.stringify({ dam: { data: { data } } }));
console.log(data.length);
