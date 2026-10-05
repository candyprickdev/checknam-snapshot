import re, urllib.request, json
UA = {"User-Agent": "checknam.com (+https://checknam.com)"}
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read().decode("utf-8", "ignore")
B = "https://telemetry.dwr.go.th"
root = get(B + "/")
js = sorted(set(re.findall(r'/_next/static/[^"\' >]+\.js', root)))
bm = [j for j in js if "_buildManifest" in j]
chunks = set(js)
if bm:
    t = get(B + bm[0]); chunks |= {"/_next/" + c for c in re.findall(r'static/chunks/[^"\', \]]+?\.js', t)}
out = {}
for c in sorted(chunks):
    try: t = get(B + c)
    except Exception as e: continue
    for m in set(re.findall(r'public/[A-Za-z0-9/_]+', t)): out.setdefault(m, []).append(c.split("/")[-1])
    for m in set(re.findall(r'["`](/[a-zA-Z]+/[A-Za-z0-9/_]{3,})["`]', t)):
        if "api" in m or "report" in m.lower(): out.setdefault(m, []).append(c.split("/")[-1])
json.dump({"chunks": len(chunks), "apis": out}, open("d/apis.json", "w"), ensure_ascii=False, indent=1)
print(len(chunks), len(out))
