# เติมแนวลำน้ำให้สถานีวัดน้ำที่ยังไม่มีเส้นบนแผนที่ (ห่างเส้นเดิมเกิน 1 กม.) จาก OpenStreetMap
# เข้า: ww.geojsonseq (osmium export waterway=river,stream,canal), ST.json (สถานีจากหน้าเว็บ), OLD.js (rivers-*.js ปัจจุบัน)
import json, sys, math
ww_path, st_path, old_path, out_path = sys.argv[1:5]
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
def nearest(grid, lines, p, maxd):
    best, bi = 1e9, None
    for i in grid.get((int(math.floor(p[0]/C)), int(math.floor(p[1]/C))), []):
        l = lines[i]
        for k in range(1, len(l)):
            d = seg_d(p, l[k-1], l[k])
            if d < best: best, bi = d, i
    return (best, bi) if best <= maxd else (best, None)
def simplify(l, tol=.15):
    out = [l[0]]
    for p in l[1:-1]:
        if km(out[-1], p) >= tol: out.append(p)
    out.append(l[-1]); return [[round(p[0],4), round(p[1],4)] for p in out]
# เส้นเดิม
t = open(old_path, encoding="utf-8").read(); geo = json.loads(t[t.index("["):t.rindex("]")+1])
oldl = [l for g in geo if not g.get("h") for l in g["l"]]
og = {}
for i, l in enumerate(oldl):
    for c in cells(l): og.setdefault(c, []).append(i)
# OSM
W = []
for line in open(ww_path, encoding="utf-8"):
    line = line.strip().lstrip("\x1e")
    if not line: continue
    f = json.loads(line); g = f["geometry"]; pr = f.get("properties", {})
    parts = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"] if g["type"] == "MultiLineString" else []
    nm = (pr.get("name:th") or pr.get("name") or "").strip()
    for c in parts:
        if len(c) < 2: continue
        W.append({"n": nm, "w": pr.get("waterway"), "l": [[p[1], p[0]] for p in c]})
wg = {}
for i, w in enumerate(W):
    for c in cells(w["l"]): wg.setdefault(c, []).append(i)
ends = {}
for i, w in enumerate(W):
    for q in (w["l"][0], w["l"][-1]): ends.setdefault((round(q[0],6), round(q[1],6)), []).append(i)
def chain(i0, maxkm=20):  # ต่อเส้นลำน้ำไม่มีชื่อที่ปลายชนกัน ให้ได้แนวลำน้ำต่อเนื่อง (ไม่เกิน 20 กม.)
    seen, todo, tot = {i0}, [i0], 0
    while todo and tot < maxkm:
        i = todo.pop(0); l = W[i]["l"]; tot += sum(km(l[k-1], l[k]) for k in range(1, len(l)))
        for q in (l[0], l[-1]):
            for j in ends.get((round(q[0],6), round(q[1],6)), []):
                if j not in seen: seen.add(j); todo.append(j)
    return [W[i]["l"] for i in seen]
byname = {}
for i, w in enumerate(W):
    if w["n"]: byname.setdefault(w["n"], []).append(i)
st = json.load(open(st_path, encoding="utf-8"))
add = {}  # key -> entry
stats = {"far": 0, "named": 0, "unnamed": 0, "none": 0}
for s in st:
    p = (s["la"], s["lo"])
    d, _ = nearest(og, oldl, p, 1.0)
    if d <= 1.0: continue
    stats["far"] += 1
    d2, wi = nearest(wg, [w["l"] for w in W], p, 1.5)
    if wi is None: stats["none"] += 1; continue
    w = W[wi]
    if w["n"]:
        stats["named"] += 1
        key = "n:" + w["n"] + ":" + str(round(p[0], 0)) + ":" + str(round(p[1], 0))
        e = next((e for k, e in add.items() if k.startswith("n:" + w["n"] + ":") and min(km(p, q) for q in e["_pts"]) < 60), None)
        if not e:
            ls = [W[i]["l"] for i in byname[w["n"]] if any(km(q, p) <= 50 for q in W[i]["l"][::3] + [W[i]["l"][-1]])]
            e = add.setdefault(key, {"n": s["rn"] or w["n"], "o": w["n"], "l": [simplify(l) for l in ls], "s": [], "_pts": [], "w": w["w"]})
        e["s"].append(s["id"]); e["_pts"].append(p)
    else:
        stats["unnamed"] += 1
        key = "u:%d" % wi
        e = add.setdefault(key, {"n": s["rn"] or "", "o": "", "l": [simplify(l) for l in chain(wi)], "s": [], "_pts": [], "w": w["w"]})
        e["s"].append(s["id"]); e["_pts"].append(p)
def cut_old(l):  # ตัดช่วงที่ทับเส้นเดิม (ห่างเส้นเดิมไม่ถึง 0.6 กม.) ไม่วาดซ้ำ
    out, cur = [], []
    for q in l:
        if nearest(og, oldl, q, .6)[1] is not None:
            if len(cur) >= 2: out.append(cur)
            cur = []
        else: cur.append(q)
    if len(cur) >= 2: out.append(cur)
    return out
new = []
for e in add.values():
    o = {"n": e["n"] or e["o"] or "ลำน้ำ", "s": e["s"], "l": [x for l in e["l"] for x in cut_old(l)]}
    if e["w"] != "river": o["m"] = 1
    if o["l"]: new.append(o)
pts = sum(len(l) for e in new for l in e["l"])
print(json.dumps(stats, ensure_ascii=False), "entries", len(new), "points", pts)
json.dump(new, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
