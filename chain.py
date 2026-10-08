import json, time, math, urllib.request, urllib.parse, sys
L = json.load(open("miss29.json", encoding="utf-8"))
UA = "checknam-diag/1.0 (+https://checknam.com)"
EP = ["https://overpass.kumi.systems/api/interpreter", "https://overpass.private.coffee/api/interpreter", "https://overpass-api.de/api/interpreter"]
def q(data):
    for k in range(3):
        for u in EP:
            try:
                r = urllib.request.urlopen(urllib.request.Request(u, data=urllib.parse.urlencode({"data": data}).encode(), headers={"User-Agent": UA}), timeout=150).read()
                if r[:1] == b"{": return json.loads(r)
            except Exception as e: print("err", u, e, file=sys.stderr)
            time.sleep(6)
    return None
km = lambda a, b: math.hypot((a[1]-b[1])*108, (a[0]-b[0])*111)
def segd(p, l):
    best = 1e9
    for i in range(1, len(l)):
        a, b = l[i-1], l[i]; ax, ay = (a[1]-p[1])*108, (a[0]-p[0])*111; bx, by = (b[1]-p[1])*108, (b[0]-p[0])*111
        vx, vy = bx-ax, by-ay; L2 = vx*vx+vy*vy; t = 0 if not L2 else max(0, min(1, -(ax*vx+ay*vy)/L2)); best = min(best, math.hypot(ax+vx*t, ay+vy*t))
    return best
def core(n):
    n = n.replace(" ", "").replace("-", "")
    for p in ["แม่น้ำ","ลำน้ำ","ลำห้วย","คลอง","ห้วย","ลำ","น้ำ","แม่"]:
        if n.startswith(p): n = n[len(p):]
    return n
res = {}
for s in L:
    p = [s["la"], s["lo"]]; rv = s["rv"]
    o = q(f'[out:json][timeout:120];way(around:5000,{p[0]},{p[1]})[waterway~"^(river|canal|stream|ditch|drain)$"];out body geom;')
    if o is None: res[s["id"]] = {"err": 1}; print(s["id"], "ERR", flush=True); continue
    W = []
    for e in o["elements"]:
        g = e.get("geometry") or []
        if len(g) < 2: continue
        t = e.get("tags", {}); W.append({"id": e["id"], "nodes": e["nodes"], "n": (t.get("name:th") or t.get("name") or "").strip(), "w": t.get("waterway"), "l": [[x["lat"], x["lon"]] for x in g]})
    for w in W: w["d"] = segd(p, w["l"])
    c = core(rv) if rv else ""
    nm = [w for w in W if c and len(c) >= 2 and w["n"] and (c in core(w["n"]) or core(w["n"]) in c) and w["d"] <= 1.6]
    near = [w for w in W if w["d"] <= 0.3]
    seed = min(nm, key=lambda w: w["d"]) if nm else (min(near, key=lambda w: w["d"]) if near else None)
    if not seed: res[s["id"]] = {"none": 1, "n": len(W)}; print(s["id"], s["n"], "none", flush=True); time.sleep(3); continue
    ends = {}
    for i, w in enumerate(W):
        for nd in (w["nodes"][0], w["nodes"][-1]): ends.setdefault(nd, []).append(i)
    same = (lambda w: w["n"] == seed["n"]) if seed["n"] else (lambda w: not w["n"] and w["w"] == seed["w"])
    si = W.index(seed); seen = {si}; todo = [si]; tot = 0
    while todo and tot < 14:
        i = todo.pop(0); l = W[i]["l"]; tot += sum(km(l[k-1], l[k]) for k in range(1, len(l)))
        for nd in (W[i]["nodes"][0], W[i]["nodes"][-1]):
            for j in ends.get(nd, []):
                if j not in seen and same(W[j]): seen.add(j); todo.append(j)
    lines = []
    for i in seen:
        l = W[i]["l"]; out = [l[0]]
        for x in l[1:-1]:
            if km(out[-1], x) >= .05: out.append(x)
        out.append(l[-1]); lines.append([[round(x[0], 5), round(x[1], 5)] for x in out])
    res[s["id"]] = {"name": seed["n"], "w": seed["w"], "d": round(seed["d"], 3), "byname": bool(nm), "ways": [W[i]["id"] for i in seen], "km": round(tot, 1), "l": lines}
    print(s["id"], s["n"], "->", seed["n"] or "(ไม่มีชื่อ)", seed["w"], round(seed["d"], 2), "km", round(tot, 1), flush=True); time.sleep(3)
json.dump(res, open("chain29.json", "w"), ensure_ascii=False)
