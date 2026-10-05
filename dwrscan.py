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
res = {}
for p, body in []:
    try:
        st, b = get(B + "/api/" + p, data=json.dumps(body).encode(), ct="application/json")
        res[p + " " + json.dumps(body)] = [st, len(b), b[:1500]]
    except Exception as e:
        try: res[p + " " + json.dumps(body)] = [str(e)[:100], e.read().decode()[:600]]
        except Exception: res[p + " " + json.dumps(body)] = [str(e)[:200]]
st, b = get(B + "/api/public/reportCurrentStatus/getCurrentStatus", data=b"{}", ct="application/json")
open("d/dwr.json", "w").write(b)

d = {}
sid = "98e9fef4-8968-485a-ad69-b7e02fb349b1"
for path in [f"public/station/{sid}", f"public/station/{sid}?infoType=WL", f"public/station/{sid}?infoType=STATION", f"public/station/{sid}/WL", f"public/station/graph/{sid}?infoType=WL"]:
    try:
        st, b = get(B + "/api/" + path); d[path] = [st, b[:4000]]
    except Exception as e:
        try: d[path] = [str(e)[:80], e.read().decode()[:400]]
        except Exception: d[path] = [str(e)[:200]]
json.dump(d, open("d/detail.json", "w"), ensure_ascii=False, indent=1)
