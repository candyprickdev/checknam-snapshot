# ตรวจทุกสถานีทั่วประเทศ: เทียบเส้นลำน้ำบนเว็บ (RIVER_GEO) กับลำน้ำใน OpenStreetMap
# สถานีที่ OSM มีลำน้ำใกล้จุดกว่าเส้นบนเว็บชัดเจน (หรือชื่อตรงกัน) -> เสนอเส้นใหม่จาก OSM ต่อตามแนวน้ำ
import json, math, sys
st_path, rv_path, ww_path, out_path = sys.argv[1:5]
km = lambda a, b: math.hypot((a[1]-b[1])*108, (a[0]-b[0])*111)
def sd(p, a, b):
    ax, ay = (a[1]-p[1])*108, (a[0]-p[0])*111; bx, by = (b[1]-p[1])*108, (b[0]-p[0])*111
    vx, vy = bx-ax, by-ay; L = vx*vx+vy*vy; t = 0 if not L else max(0, min(1, -(ax*vx+ay*vy)/L)); return math.hypot(ax+vx*t, ay+vy*t)
C = .02
def build(lines):
    g = {}
    for i, l in enumerate(lines):
        for k in range(1, len(l)):
            a, b = l[k-1], l[k]
            for x in range(int(math.floor(min(a[0],b[0])/C)), int(math.floor(max(a[0],b[0])/C))+1):
                for y in range(int(math.floor(min(a[1],b[1])/C)), int(math.floor(max(a[1],b[1])/C))+1): g.setdefault((x,y), set()).add(i)
    return g
def near(g, lines, p, r):
    n = int(math.ceil(r/2.2)); cx, cy = int(math.floor(p[0]/C)), int(math.floor(p[1]/C)); res = {}
    for x in range(cx-n, cx+n+1):
        for y in range(cy-n, cy+n+1):
            for i in g.get((x,y), ()):
                if i not in res:
                    l = lines[i]; res[i] = min(sd(p, l[k-1], l[k]) for k in range(1, len(l)))
    return {i: d for i, d in res.items() if d <= r}
def core(n):
    n = n.replace(" ", "").replace("-", "")
    for p in ["แม่น้ำ","ลำน้ำ","ลำห้วย","คลอง","ห้วย","ลำ","น้ำ","แม่"]:
        if n.startswith(p): n = n[len(p):]
    return n
ST = json.load(open(st_path, encoding="utf-8"))
SKIP = {'1106454', '1091551'}
ST = [s for s in ST if s['id'] not in SKIP]
t = open(rv_path, encoding="utf-8").read(); GEO = json.loads(t[t.index("["):t.rindex("]")+1])
RL, RN = [], []
for g in GEO:
    if g.get("h"): continue
    for l in g["l"]: RL.append(l); RN.append(g["n"])
rg = build(RL)
W = []
for line in open(ww_path, encoding="utf-8"):
    line = line.strip().lstrip("\x1e")
    if not line: continue
    f = json.loads(line); pr = f.get("properties", {}); g = f["geometry"]
    if g["type"] != "LineString": continue
    c = g["coordinates"]
    if len(c) < 2: continue
    W.append({"id": pr.get("@id"), "n": (pr.get("name:th") or pr.get("name") or "").strip(), "w": pr.get("waterway"), "l": [[q[1], q[0]] for q in c]})
WL = [w["l"] for w in W]; wg = build(WL)
ends = {}
for i, w in enumerate(W):
    for q in (w["l"][0], w["l"][-1]): ends.setdefault((round(q[0],7), round(q[1],7)), []).append(i)
out, rep = [], []
for s in ST:
    p = [s["la"], s["lo"]]; rv = s.get("rv") or ""; c = core(rv) if rv else ""
    rn = near(rg, RL, p, 3); d0 = min(rn.values()) if rn else 99; n0 = RN[min(rn, key=rn.get)] if rn else ""
    same0 = bool(rv) and any(RN[i] == rv and d <= 1.6 for i, d in rn.items())
    on = near(wg, WL, p, 1.6)
    nm = {i: d for i, d in on.items() if c and len(c) >= 2 and W[i]["n"] and (c in core(W[i]["n"]) or core(W[i]["n"]) in c)}
    seed = None
    if nm: seed = min(nm, key=nm.get)
    elif on:
        i = min(on, key=on.get)
        if on[i] <= .3: seed = i
    if seed is None:
        rep.append({**s, "d0": round(d0,2), "n0": n0, "act": "none" if d0 > .7 else "ok"}); continue
    d1 = on[seed]
    # ต้องดีกว่าเส้นเดิมชัดเจน: เส้นเดิมไกลกว่า 0.7 กม. หรือเส้นใหม่ใกล้กว่าอย่างน้อย 0.25 กม. และเส้นเดิมไม่ใช่ลำน้ำชื่อเดียวกันที่อยู่ใกล้อยู่แล้ว
    better = (d0 > .7 and not (same0 and d0 <= 1.2)) or (d1 + .25 < d0 and d0 > .35 and not (same0 and d0 <= .5)) or (d1 <= .1 and d0 > .25 and not (same0 and d0 <= .3))
    if not better:
        rep.append({**s, "d0": round(d0,2), "n0": n0, "act": "ok", "d1": round(d1,2)}); continue
    sw = W[seed]; same = (lambda w: w["n"] == sw["n"]) if sw["n"] else (lambda w: not w["n"] and w["w"] == sw["w"])
    seen = {seed}; todo = [seed]; tot = 0
    while todo and tot < 14:
        i = todo.pop(0); l = W[i]["l"]; tot += sum(km(l[k-1], l[k]) for k in range(1, len(l)))
        for q in (l[0], l[-1]):
            for j in ends.get((round(q[0],7), round(q[1],7)), []):
                if j not in seen and same(W[j]): seen.add(j); todo.append(j)
    lines = []
    for i in seen:
        l = W[i]["l"]; o = [l[0]]
        for x in l[1:-1]:
            if km(o[-1], x) >= .05: o.append(x)
        o.append(l[-1]); lines.append([[round(x[0],4), round(x[1],4)] for x in o])
    name = sw["n"] or (rv if nm else "")
    out.append({"n": name or f"ลำน้ำ (ไม่มีชื่อ) #{s['id']}", "a": 1, "s": [s["id"]], "l": lines, **({} if name else {"u": 1})})
    rep.append({**s, "d0": round(d0,2), "n0": n0, "act": "add", "d1": round(d1,2), "osm": sw["n"], "w": sw["w"], "km": round(tot,1), "byname": bool(nm)})
json.dump({"add": out, "rep": rep}, open(out_path, "w"), ensure_ascii=False)
print(len(ST), "stations;", sum(r["act"]=="add" for r in rep), "add;", sum(r["act"]=="none" for r in rep), "none")
