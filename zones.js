// สถานะรายเขตสำหรับหัวข้อลิงก์ตอนแชร์ของ checknam.com
// เปิดหน้าเว็บจริงด้วย Chrome แล้วอ่านผลจากฟังก์ชันเดียวกับข้อมูลสรุป (zoneLevels) ไม่คำนวณสูตรซ้ำที่นี่ ตัวเลขจึงตรงกับในเว็บ
const p = require("puppeteer-core");
(async () => {
  const KEY = process.env.KEY; if (!KEY) { console.log("ยังไม่ได้ตั้ง SNAP_KEY ข้าม"); return; }
  const b = await p.launch({ executablePath: "/usr/bin/google-chrome", args: ["--no-sandbox"] });
  try {
    const pg = await b.newPage();
    await pg.setUserAgent((await b.userAgent()) + " checknam-zones/1.0 (+https://checknam.com)");
    await pg.goto("https://checknam.com/z/1", { waitUntil: "domcontentloaded", timeout: 60000 });
    // รอข้อมูลครบทุกแหล่ง (คลังข้อมูลน้ำฯ + กรมทรัพยากรน้ำ + คลอง กทม.) สูงสุด 90 วินาที
    await pg.waitForFunction(() => typeof zoneLevels === "function" && DATA.length > 800 && DWR_N > 0 && BMA_N > 0, { timeout: 90000, polling: 1000 }).catch(() => {});
    await new Promise(r => setTimeout(r, 3000));
    const j = await pg.evaluate(() => { const zl = zoneLevels(); const rc = riskCore(), here = zoneLevelAt(PLACES[place][1], PLACES[place][2]);
      return { zl, check: [rc.f && rc.f[0] && rc.f[0].v, here && here.p + "%"], src: [DATA.length, DWR_N, BMA_N] }; });
    const n = j.zl.z.filter(x => x).length;
    console.log(`::notice::เขตที่มีข้อมูล ${n}/${j.zl.z.length} · สถานี ${j.src.join("/")} · ตรวจตรงกับข้อมูลสรุป ${j.check.join(" = ")}`);
    if (j.check[0] !== j.check[1]) { console.log("::warning::ค่าไม่ตรงกับข้อมูลสรุป ไม่ส่ง"); process.exitCode = 1; return; }
    if (n < 300) { console.log("::warning::เขตที่มีข้อมูลน้อยผิดปกติ ไม่ส่ง"); process.exitCode = 1; return; }
    const r = await fetch("https://checknam.com/api/snap?k=zones", { method: "POST", headers: { "x-key": KEY, "Content-Type": "application/json" }, body: JSON.stringify(j.zl) });
    console.log("::notice::ส่ง " + r.status + " " + (await r.text()).slice(0, 200)); if (!r.ok) process.exitCode = 1;
  } catch (e) { console.log("::error::" + String(e && e.message || e).slice(0, 300)); process.exitCode = 1; } finally { await b.close(); }
})();
