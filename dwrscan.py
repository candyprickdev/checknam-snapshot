import re, urllib.request, json
UA = {"User-Agent": "checknam.com (+https://checknam.com)"}
def get(u, data=None, ct=None):
    h = dict(UA); 
    if ct: h["content-type"] = ct
    r = urllib.request.urlopen(urllib.request.Request(u, data=data, headers=h), timeout=60); return r.status, r.read().decode("utf-8", "ignore")
B = "https://telemetry.dwr.go.th"
_, root = get(B + "/")
js = sorted(set(re.findall(r'/_next/static/[^"\' >]+\.js', root)))
bm = [j for j in js if "_buildManifest" in j]
_, t = get(B + bm[0]); chunks = sorted(set(js) | {"/_next/" + c for c in re.findall(r'static/chunks/[^"\', \]]+?\.js', t)})
ctx = {}
for c in chunks:
    try: _, t = get(B + c)
    except Exception: continue
    for key in ["public/reportCurrentStatus", "public/report/hour", "getCurrentStatus(", "getWL", "getRF("]:
        for m in re.finditer(re.escape(key), t):
            ctx.setdefault(key, []).append(c.split("/")[-1] + " :: " + t[max(0, m.start() - 1500):m.end() + 2500])
json.dump(ctx, open("d/ctx.json", "w"), ensure_ascii=False, indent=1)
res = {}
for p, body in [("public/reportCurrentStatus/getCurrentStatus", {}), ("public/reportCurrentStatus/getCurrentStatus", {"provinceIds": [], "mainBasinIds": [], "subBasinIds": []}), ("public/report/hour/getRF", {}), ("public/report/hour/getWL", {})]:
    try:
        st, b = get(B + "/api/" + p, data=json.dumps(body).encode(), ct="application/json")
        res[p + " " + json.dumps(body)] = [st, len(b), b[:1500]]
    except Exception as e:
        try: res[p + " " + json.dumps(body)] = [str(e)[:100], e.read().decode()[:600]]
        except Exception: res[p + " " + json.dumps(body)] = [str(e)[:200]]
json.dump(res, open("d/try.json", "w"), ensure_ascii=False, indent=1)
