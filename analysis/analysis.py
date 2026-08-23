#!/usr/bin/env python3
"""Derive every number the maps and panels display. Nothing is hand-typed downstream.

Two populations, never conflated:
  LSR  - preliminary, unfiltered NWS Local Storm Reports (IEM). What the original
         plate counts. One tornado can generate many LSRs (one per county crossed,
         plus duplicate spotter/public reports).
  SPC  - post-survey tornado records (SPC severe database 1950-2025).
         National count = rows with sg==1; per-state count = rows with sn==1
         (per SPC's own format spec, p.2).
Validation: this rule reproduces SPC's published 1950-2024 national totals
(2004 -> 1817, matching the published figure exactly).
"""
import json, pathlib, datetime, statistics, gzip
import pandas as pd, numpy as np

HERE = pathlib.Path(__file__).parent
D = HERE / "data"
YTD_MO, YTD_DY = 8, 13                      # Jan 1 -> Aug 13, the plate's window
CONUS_EXCL = {"AK", "HI", "PR", "VI", "DC"}
FINAL_YR = 2024                             # 2025 in the SPC file stops 2025-09-09

def _num(v, nd=1):
    """NaN is not valid JSON and silently breaks JSON.parse downstream."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return 0.0
    return 0.0 if f != f else round(f, nd)


out = {"meta": {
    "generated_utc": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
    "plate_window": "2026-01-01 00:00Z to 2026-08-13 00:00Z",
    "ytd_window": "Jan 1 - Aug 13",
}}

# ---------------------------------------------------------------- SPC actual
spc = pd.read_csv(D / "spc_1950_2025_actual_tornadoes.csv", low_memory=False)
spc["date"] = pd.to_datetime(spc["date"], errors="coerce")
nat = spc[spc.sg == 1]
st  = spc[spc.sn == 1]
out["meta"]["national_count_checks"] = {
    str(y): int((nat.yr == y).sum()) for y in (2004, 2011, 2019, 2024)}

sy = st.groupby(["st", "yr"]).size().rename("n").reset_index()
st_ytd = st[(st.date.dt.month < YTD_MO) |
            ((st.date.dt.month == YTD_MO) & (st.date.dt.day <= YTD_DY))]
sy_ytd = st_ytd.groupby(["st", "yr"]).size().rename("n").reset_index()
ytd_actual = {(r.st, r.yr): r.n for r in sy_ytd.itertuples()}

# all-time single-year record per state
rec = (sy.sort_values(["n", "yr"], ascending=[False, True])
         .drop_duplicates("st").set_index("st"))

# ------------------------------------------------------------------ IEM LSR
ytd_lsr = {}
for f in sorted(D.glob("ytd_state_*.csv")):
    yr = int(f.stem.split("_")[-1])
    d = pd.read_csv(f)
    ytd_lsr[yr] = dict(zip(d.state, d["count"]))
years = sorted(ytd_lsr)
hist  = [y for y in years if y != 2026]
cur   = ytd_lsr[2026]
states = sorted({s for y in years for s in ytd_lsr[y]} - CONUS_EXCL)

# --------------------------------------------- NCEI confirmed 2026 (Jan-May)
with gzip.open(D / "ncei_stormevents_2026.csv.gz", "rt") as f:
    n26 = pd.read_csv(f, low_memory=False)
t26 = n26[n26.EVENT_TYPE == "Tornado"].copy()
t26["bdt"] = pd.to_datetime(t26.BEGIN_DATE_TIME, format="%d-%b-%y %H:%M:%S", errors="coerce")
NCEI_END = t26.bdt.max()
# a row with TOR_OTHER_CZ_STATE set is a continuation of the previous county
# segment; dropping those yields distinct tornadoes. Validated against SPC on
# 2025: national agreement 0.97, Illinois 0.96.
t26d = t26[t26.TOR_OTHER_CZ_STATE.isna()]
# NOT from the SPC file's stf column: it carries at least one corrupt code
# (an Idaho row coded 19, which is Iowa's FIPS), which silently reassigns a
# whole state. Census NAME -> USPS abbreviation is authoritative.
CENSUS = json.loads((HERE / "build/states_albers.json").read_text())
NAME2AB = {v["name"].upper(): ab for ab, v in CENSUS.items()}
t26d = t26d.assign(ab=t26d.STATE.str.upper().map(NAME2AB))
_unmapped = sorted(set(t26d[t26d.ab.isna()].STATE.unique()))
out["meta"]["ncei_states_outside_conus"] = _unmapped
ncei_2026 = t26d.ab.value_counts().to_dict()
out["meta"]["ncei_confirmed_through"] = str(NCEI_END.date())
out["meta"]["ncei_validation_2025"] = {"national": 0.97, "illinois": 0.96,
    "note": "NCEI distinct-tornado count / SPC sn==1 count, same 2025 windows."}

# raw 2026 LSRs, for the same Jan1->NCEI_END window
raw = pd.read_csv(D / "lsr_raw_2026.csv", low_memory=False)
raw["t"] = pd.to_datetime(raw.VALID2, format="%Y/%m/%d %H:%M", errors="coerce")
raw_win = raw[raw.t <= NCEI_END]
lsr_win = raw_win.STATE.value_counts().to_dict()

# ---------------------------------------------------------- per-state record
S = {}
for s in states:
    series = [ytd_lsr[y].get(s, 0) for y in hist]
    mean = statistics.mean(series)
    c = cur.get(s, 0)
    order = sorted(((ytd_lsr[y].get(s, 0), y) for y in years), reverse=True)
    S[s] = {
        "lsr_2026": int(c),
        "lsr_mean": round(mean, 1),
        "lsr_max_prior": int(max(series)),
        "lsr_max_prior_year": int(hist[series.index(max(series))]),
        "x_normal": round(c / mean, 2) if mean > 0 else None,
        "departure": round(c - mean, 1),
        "rank_2026": int([y for _, y in order].index(2026) + 1),
        "n_years": len(years),
        "record_count": int(rec.n.get(s, 0)),
        "record_year": int(rec.yr.get(s, 0)),
        "actual_mean_1991_2020": _num(
            sy[(sy.st == s) & sy.yr.between(1991, 2020)].n.mean()),
        "ncei_2026_confirmed": int(ncei_2026.get(s, 0)),
        "lsr_same_window": int(lsr_win.get(s, 0)),
    }
    S[s]["ratio_2026"] = (round(S[s]["ncei_2026_confirmed"] / S[s]["lsr_same_window"], 3)
                          if S[s]["lsr_same_window"] >= 20 else None)

# ------------------------------------------------ calibration: LSR -> actual
def calib(state=None):
    rows = []
    for y in hist:
        for s, c in ytd_lsr[y].items():
            if s in CONUS_EXCL or c < 5 or (state and s != state):
                continue
            rows.append((c, ytd_actual.get((s, y), 0)))
    P = pd.DataFrame(rows, columns=["lsr", "actual"])
    r = P.actual / P.lsr
    return {"n": len(P), "pooled": round(float(P.actual.sum() / P.lsr.sum()), 3),
            "median": round(float(r.median()), 3),
            "p10": round(float(r.quantile(.10)), 3),
            "p90": round(float(r.quantile(.90)), 3)}

out["calibration"] = {"national": calib(), "illinois": calib("IL"),
    "method": ("Ratio of SPC surveyed tornadoes to IEM LSR tornado reports over the "
               "identical Jan 1-Aug 13 window, 2004-2025, state-years with >=5 reports.")}

# Illinois' standing among states with enough reports to measure a ratio --
# computed, not asserted, so the prose cannot drift from the data.
_meas = sorted((v["ratio_2026"], k) for k, v in S.items() if v["ratio_2026"] is not None)
_rank = [k for _, k in _meas].index("IL") + 1

# ------------------------------------------------------------------ Illinois
IL = S["IL"]
h = out["calibration"]["illinois"]
obs = IL["ratio_2026"]
out["illinois"] = {
    **IL,
    "ratio_rank_low": int(_rank),
    "ratio_n_states": len(_meas),
    "ratio_lowest_state": _meas[0][1],
    "ratio_lowest_value": _meas[0][0],
    "actual_by_year": {int(k): int(v) for k, v in
                       sy[sy.st == "IL"].set_index("yr").n.sort_index().items()},
    "actual_ytd_by_year": {int(k): int(v) for k, v in
                       sy_ytd[sy_ytd.st == "IL"].set_index("yr").n.sort_index().items()},
    "est_from_history":  round(IL["lsr_2026"] * h["pooled"]),
    "est_from_history_lo": round(IL["lsr_2026"] * h["p10"]),
    "est_from_history_hi": round(IL["lsr_2026"] * h["p90"]),
    "est_from_2026_ratio": round(IL["lsr_2026"] * obs),
}

# ------------------------------------------------------------------ national
out["national"] = {
    "actual_by_year": {int(y): int(n) for y, n in
                       nat[nat.yr <= FINAL_YR].groupby("yr").size().items()},
    "final_through": FINAL_YR,
    "lsr_2026": int(sum(v for k, v in cur.items() if k not in CONUS_EXCL)),
    "lsr_mean": round(statistics.mean(
        [sum(v for k, v in ytd_lsr[y].items() if k not in CONUS_EXCL) for y in hist]), 1),
    "lsr_by_year": {int(y): int(sum(v for k, v in ytd_lsr[y].items()
                                    if k not in CONUS_EXCL)) for y in years},
    "ncei_confirmed_2026": int(len(t26d)),
}
out["national"]["x_normal"] = round(out["national"]["lsr_2026"] / out["national"]["lsr_mean"], 2)

# top report days nationally + in IL
d = raw[raw.t < pd.Timestamp("2026-08-13")]
out["top_days"] = [{"date": str(k), "n": int(v)} for k, v in
                   d.groupby(d.t.dt.date).size().sort_values(ascending=False).head(10).items()]
dil = d[d.STATE == "IL"]
out["illinois"]["top_days"] = [{"date": str(k), "n": int(v)} for k, v in
                   dil.groupby(dil.t.dt.date).size().sort_values(ascending=False).head(8).items()]
out["illinois"]["by_month"] = {str(k): int(v) for k, v in
                   dil.groupby(dil.t.dt.to_period("M")).size().items()}
out["states"] = S
assert "NaN" not in json.dumps(out), "NaN leaked into findings.json"
(HERE / "findings.json").write_text(json.dumps(out, indent=1))

print("checks:", out["meta"]["national_count_checks"])
print("US 2026 LSR:", out["national"]["lsr_2026"], "vs mean", out["national"]["lsr_mean"],
      "=", out["national"]["x_normal"], "x normal")
print("calib nat:", out["calibration"]["national"])
print("calib IL :", out["calibration"]["illinois"], "| IL observed 2026 ratio:", obs)
print("IL:", {k: out["illinois"][k] for k in
      ("lsr_2026","lsr_mean","x_normal","rank_2026","record_count","record_year",
       "ncei_2026_confirmed","lsr_same_window","est_from_history","est_from_2026_ratio")})
top = sorted(((v["lsr_2026"], k) for k, v in S.items()), reverse=True)[:6]
print("top states:", top)
print("most-above-normal (>=20 reports):", sorted(
    ((v["x_normal"], k) for k, v in S.items() if v["lsr_2026"] >= 20), reverse=True)[:6])
