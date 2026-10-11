// ข่าวน้ำท่วมจาก RSS ของสำนักข่าว: เก็บเฉพาะหัวข่าว ลิงก์ เวลา ชื่อสำนักข่าว และข้อความต้นข่าวสั้นๆ ไว้จับคู่กับชื่ออำเภอ/จังหวัด
// รวมกับรอบก่อน (news-state.json) เก็บย้อนหลัง 3 วัน แล้วเขียน news-out.json ให้ส่งไปเก็บที่เว็บ
// ใช้: node news.js
const fs = require("fs");
const FEEDS = [
  ["มติชน", "https://www.matichon.co.th/feed"], ["มติชน", "https://www.matichon.co.th/region/feed"], ["มติชน", "https://www.matichon.co.th/local/feed"],
  ["ข่าวสด", "https://www.khaosod.co.th/feed"], ["ข่าวสด", "https://www.khaosod.co.th/around-thailand/feed"], ["ข่าวสด", "https://www.khaosod.co.th/breaking-news/feed"],
  ["ประชาชาติธุรกิจ", "https://www.prachachat.net/feed"], ["ไทยโพสต์", "https://www.thaipost.net/feed/"], ["เดลินิวส์", "https://www.dailynews.co.th/news/feed/"],
  ["ผู้จัดการออนไลน์", "https://mgronline.com/store/rss/index.xml"], ["ผู้จัดการออนไลน์", "https://mgronline.com/store/rss/local.xml"], ["ผู้จัดการออนไลน์", "https://mgronline.com/store/rss/around.xml"],
  ["ผู้จัดการออนไลน์", "https://mgronline.com/store/rss/south.xml"], ["ผู้จัดการออนไลน์", "https://mgronline.com/store/rss/qol.xml"],
  ["INN", "https://www.innnews.co.th/feed/"], ["The Reporters", "https://www.thereporters.co/feed/"], ["เชียงใหม่นิวส์", "https://www.chiangmainews.co.th/feed/"],
];
// หัวข่าวที่มีคำเหล่านี้ถือเป็นข่าวน้ำ/ฝน · ถ้าหัวข่าวไม่มี แต่ต้นข่าวมีคำหลักชัดเจน ก็นับด้วย
const KW_T = /น้ำท่วม|ท่วมขัง|ท่วมหนัก|ท่วมสูง|ท่วมบ้าน|น้ำป่า|น้ำหลาก|อุทกภัย|ล้นตลิ่ง|ระดับน้ำ|น้ำเอ่อ|น้ำทะเลหนุน|ระบายน้ำ|ดินถล่ม|ดินสไลด์|ฝนตกหนัก|ฝนถล่ม|พายุ|มวลน้ำ|เขื่อน|ประตูระบายน้ำ|ภัยพิบัติ/;
const KW_X = /น้ำท่วม|อุทกภัย|น้ำป่า|ล้นตลิ่ง|น้ำหลาก|มวลน้ำ/;
const KEEP = 3 * 864e5, MAXN = 500;
const UA = "Mozilla/5.0 (compatible; checknam.com news reader; +https://checknam.com)";
const dec = s => String(s || "").replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1").replace(/<[^>]+>/g, " ").replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#0?39;|&#8217;|&#8216;/g, "'").replace(/&#8220;|&#8221;/g, '"').replace(/&#8211;|&#8212;/g, "–").replace(/&#8230;|&hellip;/g, "…").replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(+n)).replace(/\s+/g, " ").trim();
const tag = (x, t) => { const m = new RegExp("<" + t + "(?:\\s[^>]*)?>([\\s\\S]*?)</" + t + ">").exec(x); return m ? m[1] : ""; };
async function one([src, url]) {
  try {
    const r = await fetch(url, { headers: { "User-Agent": UA, Accept: "application/rss+xml, application/xml, text/xml" }, signal: AbortSignal.timeout(25000) });
    if (!r.ok) return { src, url, err: r.status, items: [] };
    const xml = await r.text(), items = [];
    for (const it of xml.split(/<item[\s>]/).slice(1)) {
      const t = dec(tag(it, "title")), u = dec(tag(it, "link")) || dec(tag(it, "guid")), d = Date.parse(dec(tag(it, "pubDate")));
      if (!t || !/^https:\/\//.test(u) || !d) continue;
      const x = (dec(tag(it, "description")) + " " + dec(tag(it, "content:encoded"))).slice(0, 1500);
      if (!(KW_T.test(t) || KW_X.test(x.slice(0, 600)))) continue;
      items.push({ s: src, t: t.slice(0, 220), u, d, x });
    }
    return { src, url, items };
  } catch (e) { return { src, url, err: String(e.name || e), items: [] }; }
}
(async () => {
  let old = [];
  try { old = JSON.parse(fs.readFileSync("news-state.json", "utf8")).items || []; } catch (e) { old = []; }
  const res = await Promise.all(FEEDS.map(one));
  for (const r of res) console.log(`${r.src} ${r.url} ${r.err ? "ERR " + r.err : r.items.length + " ข่าว"}`);
  const now = Date.now(), by = new Map();
  for (const it of [...old, ...res.flatMap(r => r.items)]) {
    if (!(it.d > now - KEEP && it.d < now + 36e5)) continue;
    const k = it.u.replace(/[?#].*$/, "").replace(/\/$/, "");
    if (!by.has(k)) by.set(k, it);
  }
  // หัวข่าวเดียวกันจากหลายหน้า (เช่น หน้าหลักกับหมวดภูมิภาค) เก็บอันเดียว
  const seen = new Set(), items = [...by.values()].sort((a, b) => b.d - a.d).filter(it => { const k = it.t.replace(/\s/g, ""); if (seen.has(k)) return false; seen.add(k); return true; }).slice(0, MAXN);
  const ok = res.filter(r => !r.err).length;
  const out = { t: now, feeds: ok, items };
  fs.writeFileSync("news-state.json", JSON.stringify(out));
  fs.writeFileSync("news-out.json", JSON.stringify(out));
  console.log(`รวม ${items.length} ข่าว จาก ${ok}/${FEEDS.length} ฟีด`);
  if (!ok) process.exit(1);
})();
