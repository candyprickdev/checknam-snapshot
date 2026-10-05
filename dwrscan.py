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
    for key in ["public/teleMap", "public/reportCurrentStatus", "public/station", "public/report/hour"]:
        for m in re.finditer(re.escape(key), t):
            ctx.setdefault(key, []).append(c.split("/")[-1] + " :: " + t[max(0, m.start() - 300):m.end() + 300])
json.dump(ctx, open("d/ctx.json", "w"), ensure_ascii=False, indent=1)
res = {}
for p in ["public/teleMap", "public/reportCurrentStatus", "public/station", "public/dropdown"]:
    for meth in ["GET", "POST"]:
        try:
            st, body = get(B + "/api/" + p, data=(b"{}" if meth == "POST" else None), ct=("application/json" if meth == "POST" else None))
            res[p + " " + meth] = [st, len(body), body[:800]]
        except Exception as e: res[p + " " + meth] = [str(e)[:200]]
json.dump(res, open("d/try.json", "w"), ensure_ascii=False, indent=1)
