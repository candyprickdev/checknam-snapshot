#!/usr/bin/env python3
"""รายชื่อสถานีวัดระดับน้ำของกรมทรัพยากรน้ำ (telemetry.dwr.go.th) -> site/dwrst.json
เก็บเฉพาะข้อมูลที่ใช้: รหัส ชื่อ ลำน้ำ พิกัด ระดับตลิ่งซ้าย/ขวา ท้องน้ำ และเกณฑ์เฝ้าระวัง/วิกฤตของกรมฯ
ไม่เก็บลิงก์กล้องหรือข้อมูลอื่นของระบบกรมฯ  ค่าระดับน้ำปัจจุบันดึงสดผ่าน /api/dwr
ใช้: python3 tools/gen-dwr.py site/dwrst.json   (ต้องต่อเน็ตถึง telemetry.dwr.go.th)"""
import json, sys, time, urllib.request
UA = {"User-Agent": "checknam.com (+https://checknam.com)", "content-type": "application/json"}
B = "https://telemetry.dwr.go.th/api/public/"
def req(path, body=None):
    r = urllib.request.Request(B + path, data=(json.dumps(body).encode() if body is not None else None), headers=UA)
    return json.loads(urllib.request.urlopen(r, timeout=60).read())
cur = req("reportCurrentStatus/getCurrentStatus", {})["value"]
f = lambda v: None if v is None else round(float(v), 3)
out = []
for s in cur:
    if not s.get("wlEnabled"): continue
    try: e = req("station/" + s["id"])["value"]["fullCon"]["entity"]
    except Exception as ex: print("skip", s.get("code"), ex); continue
    p = e.get("point") or {}
    if not p.get("lat"): continue
    ai = s.get("addressInfo") or {}
    out.append({"id": s["id"], "c": e.get("stationCode"), "n": e.get("stnNameTh"), "s": e.get("stream"), "la": round(p["lat"], 5), "lo": round(p["lon"], 5),
                "lb": f(e.get("lbMsl")), "rb": f(e.get("rbMsl")), "bb": f(e.get("bbMsl")), "fw": f(e.get("wlFw")), "fc": f(e.get("wlFc")),
                "p": (ai.get("provinceInfo") or {}).get("nameTh"), "pc": (ai.get("provinceInfo") or {}).get("code"), "a": (ai.get("districtInfo") or {}).get("nameTh")})
    time.sleep(0.6)
json.dump({"at": int(time.time() * 1000), "src": "telemetry.dwr.go.th", "st": out}, open(sys.argv[1], "w"), ensure_ascii=False, separators=(",", ":"))
print("stations", len(out))
