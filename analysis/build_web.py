#!/usr/bin/env python3
"""Assemble one self-contained data bundle for the story map.

Everything the page draws comes from here; no number is typed into the HTML.
Geometry is pre-projected to EPSG:5070 Albers so the browser draws an
equal-area map without carrying a projection library.
"""
import json, pathlib, pandas as pd
from pyproj import Transformer

HERE = pathlib.Path(__file__).parent
B = HERE / "build"
F = json.loads((HERE / "findings.json").read_text())
G = json.loads((B / "states_albers.json").read_text())

# 1 km coordinate precision: sub-pixel at national scale, and a third the bytes
geo = {ab: {"n": s["name"],
            "r": [[[round(x/1000), round(y/1000)] for x, y in ring] for ring in s["rings"]]}
       for ab, s in G.items()}

# Illinois tornado reports, projected, with time -- the season replay
tx = Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True)
raw = pd.read_csv(HERE / "data/lsr_raw_2026.csv", low_memory=False)
raw["t"] = pd.to_datetime(raw.VALID2, format="%Y/%m/%d %H:%M", errors="coerce")
il = raw[(raw.STATE == "IL") & (raw.t < pd.Timestamp("2026-08-13"))]
# the archive carries a handful of byte-identical rows (same time, place and
# type, filed twice); the IEM's own state aggregation removes them, so the
# replay does too, and the residual against 283 is reported rather than hidden
_n_raw = len(il)
il = il.drop_duplicates(["VALID", "LAT", "LON", "CITY", "COUNTY", "TYPECODE"]).sort_values("t")
xs, ys = tx.transform(il.LON.values, il.LAT.values)
doy = il.t.dt.dayofyear.values
pts = [[round(x/1000), round(y/1000), int(d)] for x, y, d in zip(xs, ys, doy)]

# distinct report days, for the replay's day ticks
days = (il.groupby(il.t.dt.dayofyear).size()
          .reindex(range(1, 226), fill_value=0).tolist())

# the plates' own centroid + nudge table, so the web map places its labels
# in exactly the same spots as the printed sheets
import importlib.util as _iu
_sp = _iu.spec_from_file_location("plates", HERE / "plates.py")
_pl = _iu.module_from_spec(_sp)
import matplotlib; matplotlib.use("Agg")
_sp.loader.exec_module(_pl)
centroids = {ab: [round(x/1000), round(y/1000)] for ab, (x, y) in _pl.CEN.items()}

bundle = {
    "centroids": centroids,
    "callout_states": _pl.CALLOUT,
    "findings": F,
    "geo": geo,
    "il_points": pts,
    "il_daily": days,
    "il_points_plotted": int(len(il)),
    "il_rows_raw": int(_n_raw),
}
(B / "storymap_data.json").write_text(json.dumps(bundle, separators=(",", ":")))
kb = (B / "storymap_data.json").stat().st_size / 1024
print(f"bundle {kb:.0f} KB · {len(pts)} Illinois report points · {len(geo)} states")
print("IL peak day index:", max(range(len(days)), key=lambda i: days[i]) + 1,
      "with", max(days), "reports")
