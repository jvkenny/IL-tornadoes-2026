#!/usr/bin/env python3
"""Census 20m generalised state boundaries -> two artifacts:
   build/states_wgs84.json  (lon/lat, for the web map)
   build/states_albers.json (EPSG:5070 metres, for the print plates)
20m generalisation is the right resolution for a national thematic map --
full-resolution coastlines at this scale are noise (gis-cartography step 2).
"""
import json, pathlib, shapefile
from pyproj import Transformer

HERE = pathlib.Path(__file__).parent
SHP = HERE / "data/states_shp/cb_2023_us_state_20m"
OUT = HERE / "build"; OUT.mkdir(exist_ok=True)
DROP = {"AK", "HI", "PR", "VI", "GU", "MP", "AS", "DC"}   # CONUS thematic frame

# EPSG:5070 NAD83 / Conus Albers -- equal area, the correct choice for
# comparing a quantity across states (gis-cartography step 3).
tx = Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True)

r = shapefile.Reader(str(SHP))
flds = [f[0] for f in r.fields[1:]]
i_ab, i_nm = flds.index("STUSPS"), flds.index("NAME")

wgs, alb = {}, {}
for sr in r.iterShapeRecords():
    ab = sr.record[i_ab]
    if ab in DROP:
        continue
    pts, parts = sr.shape.points, list(sr.shape.parts) + [len(sr.shape.points)]
    rings_w, rings_a = [], []
    for a, b in zip(parts, parts[1:]):
        ring = pts[a:b]
        if len(ring) < 4:
            continue
        rings_w.append([[round(x, 4), round(y, 4)] for x, y in ring])
        xs, ys = tx.transform(*zip(*ring))
        rings_a.append([[round(x, 1), round(y, 1)] for x, y in zip(xs, ys)])
    wgs[ab] = {"name": sr.record[i_nm], "rings": rings_w}
    alb[ab] = {"name": sr.record[i_nm], "rings": rings_a}

(OUT / "states_wgs84.json").write_text(json.dumps(wgs, separators=(",", ":")))
(OUT / "states_albers.json").write_text(json.dumps(alb, separators=(",", ":")))
print(f"{len(wgs)} states")
for f in ("states_wgs84.json", "states_albers.json"):
    print(f"  {f}  {(OUT/f).stat().st_size/1024:.0f} KB")
xs = [p[0] for s in alb.values() for r_ in s["rings"] for p in r_]
ys = [p[1] for s in alb.values() for r_ in s["rings"] for p in r_]
print(f"  albers extent x {min(xs):.0f}..{max(xs):.0f}  y {min(ys):.0f}..{max(ys):.0f}")
