import json, time, urllib.request, urllib.parse, sys
L = json.load(open("miss29.json", encoding="utf-8"))
UA = "checknam-diag/1.0 (+https://checknam.com)"
EP = ["https://overpass.kumi.systems/api/interpreter", "https://overpass.private.coffee/api/interpreter", "https://overpass-api.de/api/interpreter"]
def q(data):
    for u in EP:
        for k in range(2):
            try:
                r = urllib.request.urlopen(urllib.request.Request(u, data=urllib.parse.urlencode({"data": data}).encode(), headers={"User-Agent": UA}), timeout=120).read()
                if r[:1] == b"{": return json.loads(r)
            except Exception as e: print("err", u, e, file=sys.stderr)
            time.sleep(5)
    return None
out = {}
for s in L:
    la, lo = s["la"], s["lo"]; nm = s["rv"]
    nameq = ""
    if nm:
        core = nm.replace("คลอง","").replace("ลำน้ำ","").replace("ลำ","").replace("ห้วย","").replace("แม่น้ำ","").replace("น้ำ","").strip()
        if len(core) >= 2: nameq = f'way(around:8000,{la},{lo})[waterway][name~"{core}"];way(around:8000,{la},{lo})[natural=water][name~"{core}"];'
    data = f'[out:json][timeout:90];(way(around:1500,{la},{lo})[waterway];way(around:1200,{la},{lo})[natural=water];way(around:1200,{la},{lo})[waterway=riverbank];relation(around:1200,{la},{lo})[natural=water];{nameq});out tags geom;'
    out[s["id"]] = q(data); print(s["id"], s["n"], len((out[s["id"]] or {}).get("elements", [])), flush=True); time.sleep(3)
json.dump(out, open("osm29.json", "w"), ensure_ascii=False)
