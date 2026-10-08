# รอบสอง: เติมเส้นลำน้ำให้สถานีที่ยังไม่มีเส้น (ห่างเส้นเดิมเกิน 1 กม.)
# 1) OpenStreetMap: ชื่อตรง (รวมรูปแบบชื่อที่ต่างกัน) ไม่เกิน 5 กม. -> ลำน้ำ/คลอง/คูระบายน้ำใกล้สุดไม่เกิน 1.5 กม.
# 2) HydroRIVERS (WWF, คำนวณจากแผนที่ความสูง): ลำน้ำใกล้สุดไม่เกิน 2 กม. ต่อตามทิศน้ำไหลขึ้น-ลงรวมราว 30 กม.
# 3) ที่เหลือ: บันทึกรายการสถานีที่ไม่มีเส้นลำน้ำในทั้งสองแหล่ง
import json, sys, math
ww_path, hr_path, st_path, old_path, out_path = sys.argv[1:6]
km = lambda a, b: math.hypot((a[1]-b[1])*108, (a[0]-b[0])*111)
def seg_d(p, a, b):
    ax, ay = (a[1]-p[1])*108, (a[0]-p[0])*111; bx, by = (b[1]-p[1])*108, (b[0]-p[0])*111
    vx, vy = bx-ax, by-ay; L = vx*vx+vy*vy; t = 0 if not L else max(0, min(1, -(ax*vx+ay*vy)/L))
    return math.hypot(ax+vx*t, ay+vy*t)
C = .05
def cells(l):
    s = set()
    for i in range(1, len(l)):
        a, b = l[i-1], l[i]
        for x in range(int(math.floor(min(a[0],b[0])/C))-1, int(math.floor(max(a[0],b[0])/C))+2):
            for y in range(int(math.floor(min(a[1],b[1])/C))-1, int(math.floor(max(a[1],b[1])/C))+2): s.add((x,y))
    return s
def index(lines):
    g = {}
    for i, l in enumerate(lines):
        for c in cells(l): g.setdefault(c, []).append(i)
    return g
def near_all(grid, lines, p, maxd):
    r = int(math.ceil(maxd/5.5)); out = {}
    cx, cy = int(math.floor(p[0]/C)), int(math.floor(p[1]/C))
    for x in range(cx-r, cx+r+1):
        for y in range(cy-r, cy+r+1):
            for i in grid.get((x,y), []):
                if i in out: continue
                l = lines[i]; out[i] = min(seg_d(p, l[k-1], l[k]) for k in range(1, len(l)))
    return sorted([(d, i) for i, d in out.items() if d <= maxd])
def simplify(l, tol=.15):
    out = [l[0]]
    for q in l[1:-1]:
        if km(out[-1], q) >= tol: out.append(q)
    out.append(l[-1]); return [[round(q[0],4), round(q[1],4)] for q in out]
def norm(n): return n.replace(" ", "").replace("-", "")
def variants(n):
    v = {n}
    for a, b in [("น้ำแม่","แม่น้ำ"),("แม่น้ำ","น้ำ"),("แม่น้ำ","แม่"),("ลำน้ำ","ลำ"),("ลำ","ลำน้ำ"),("คลอง","แม่น้ำ"),("แม่น้ำ","คลอง"),("ห้วย","ลำห้วย"),("ลำห้วย","ห้วย"),("คลอง","คลองชลประทาน"),("น้ำ","แม่น้ำ")]:
        if n.startswith(a): v.add(b + n[len(a):])
    return {norm(x) for x in v}
t = open(old_path, encoding="utf-8").read(); geo = json.loads(t[t.index("["):t.rindex("]")+1])
oldl = [l for g in geo if not g.get("h") for l in g["l"]]; og = index(oldl)
W = []
for line in open(ww_path, encoding="utf-8"):
    line = line.strip().lstrip("\x1e")
    if not line: continue
    f = json.loads(line); g = f["geometry"]; pr = f.get("properties", {})
    parts = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"] if g["type"] == "MultiLineString" else []
    nm = (pr.get("name:th") or pr.get("name") or "").strip()
    for c in parts:
        if len(c) >= 2: W.append({"n": nm, "w": pr.get("waterway"), "l": [[q[1], q[0]] for q in c]})
WL = [w["l"] for w in W]; wg = index(WL)
byname = {}
for i, w in enumerate(W):
    if w["n"]: byname.setdefault(norm(w["n"]), []).append(i)
ends = {}
for i, w in enumerate(W):
    for q in (w["l"][0], w["l"][-1]): ends.setdefault((round(q[0],6), round(q[1],6)), []).append(i)
def chain(i0, maxkm=20):
    seen, todo, tot = {i0}, [i0], 0
    while todo and tot < maxkm:
        i = todo.pop(0); l = W[i]["l"]; tot += sum(km(l[k-1], l[k]) for k in range(1, len(l)))
        for q in (l[0], l[-1]):
            for j in ends.get((round(q[0],6), round(q[1],6)), []):
                if j not in seen: seen.add(j); todo.append(j)
    return [W[i]["l"] for i in seen]
# HydroRIVERS
H = {}
for line in open(hr_path, encoding="utf-8"):
    line = line.strip().lstrip("\x1e")
    if not line: continue
    f = json.loads(line); g = f["geometry"]; pr = f["properties"]
    cs = g["coordinates"] if g["type"] == "LineString" else [q for part in g["coordinates"] for q in part]
    H[pr["HYRIV_ID"]] = {"d": pr.get("NEXT_DOWN", 0), "o": pr.get("ORD_STRA", 1), "l": [[q[1], q[0]] for q in cs]}
HID = list(H.keys()); HL = [H[i]["l"] for i in HID]; hg = index(HL)
up = {}
for i, h in H.items():
    if h["d"]: up.setdefault(h["d"], []).append(i)
def hchain(i0, maxkm=15):
    out, tot = [i0], 0; i = i0
    while H.get(i) and H[i]["d"] in H and tot < maxkm:   # ปลายน้ำ
        i = H[i]["d"]; out.append(i); tot += sum(km(H[i]["l"][k-1], H[i]["l"][k]) for k in range(1, len(H[i]["l"])))
    todo, tot = [i0], 0                                   # ต้นน้ำ (ตามสายหลัก ลำดับลำน้ำสูงสุด)
    while todo and tot < maxkm:
        i = todo.pop(0); ups = sorted(up.get(i, []), key=lambda j: -H[j]["o"])[:1]
        for j in ups: out.append(j); todo.append(j); tot += sum(km(H[j]["l"][k-1], H[j]["l"][k]) for k in range(1, len(H[j]["l"])))
    return [H[i]["l"] for i in out]
def cut_old(l, extra=None):
    out, cur = [], []
    for q in l:
        hit = near_all(og, oldl, q, .6) or (extra and near_all(extra[0], extra[1], q, .6))
        if hit:
            if len(cur) >= 2: out.append(cur)
            cur = []
        else: cur.append(q)
    if len(cur) >= 2: out.append(cur)
    return out
st = json.load(open(st_path, encoding="utf-8"))
new, miss, stats = [], [], {"far": 0, "osm_name": 0, "osm_near": 0, "hydro": 0, "none": 0}
addL = []
for s in st:
    p = (s["la"], s["lo"])
    if near_all(og, oldl, p, 1.0): continue
    if addL and near_all(index(addL), addL, p, 1.0): continue
    stats["far"] += 1
    e = None
    if s["rn"]:  # ชื่อตรงกันไม่เกิน 5 กม.
        for v in variants(s["rn"]):
            ids = byname.get(v, [])
            if ids and any(d <= 5 for d, i in near_all(wg, WL, p, 5) if i in set(ids)):
                ls = [W[i]["l"] for i in ids if any(km(q, p) <= 40 for q in W[i]["l"][::3] + [W[i]["l"][-1]])]
                e = {"n": s["rn"], "src": "osm", "l": ls}; stats["osm_name"] += 1; break
    if not e:
        nn = near_all(wg, WL, p, 1.5)
        if nn:
            i = nn[0][1]; w = W[i]
            ls = [W[j]["l"] for j in byname.get(norm(w["n"]), []) if any(km(q, p) <= 40 for q in W[j]["l"][::3])] if w["n"] else chain(i)
            e = {"n": s["rn"] or w["n"], "src": "osm", "l": ls or [w["l"]], "m": 1 if w["w"] in ("drain", "ditch", "stream") else 0}; stats["osm_near"] += 1
    if not e:
        nh = near_all(hg, HL, p, 2.0)
        if nh:
            e = {"n": s["rn"], "src": "hydro", "l": hchain(HID[nh[0][1]]), "m": 1}; stats["hydro"] += 1
    if not e:
        stats["none"] += 1; miss.append(s["id"]); continue
    ls = [x for l in e["l"] for x in cut_old(simplify(l))]
    if not ls: continue
    o = {"n": e["n"] or ("ลำน้ำ (ไม่มีชื่อ) #" + str(s["id"])), "s": [s["id"]], "a": 1, "l": ls}
    if not e["n"]: o["u"] = 1
    if e.get("m"): o["m"] = 1
    if e["src"] == "hydro": o["hy"] = 1
    new.append(o); addL += ls
print(json.dumps(stats, ensure_ascii=False), "entries", len(new), "points", sum(len(l) for e in new for l in e["l"]))
json.dump({"add": new, "miss": miss}, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
