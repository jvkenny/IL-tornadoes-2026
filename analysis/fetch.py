#!/usr/bin/env python3
"""Re-runnable acquisition of IEM Local Storm Report tornado data.

Source of truth for the recreated map is IEM Autoplot #163 (the same app that
produced the image John shared).  We pull BOTH:
  1. the autoplot's own CSV (state counts) -- guarantees we match the plate
  2. the raw LSR product rows (lat/lon/time/remark) -- powers the story map
"""
import urllib.request, urllib.parse, pathlib, datetime, sys

OUT = pathlib.Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)
UA = {"User-Agent": "IL-tornadoes-2026 (github.com/jvkenny/IL-tornadoes-2026)"}

# The window printed on the plate John shared.
PLATE_START = "2026-01-01 0000"
PLATE_END   = "2026-08-13 0000"
# Extended through the current session date, for the "since the plate" view.
LIVE_END    = "2026-08-22 0000"

def get(url, dest, binary=False):
    dest = OUT / dest
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r:
        body = r.read()
    dest.write_bytes(body)
    print(f"  {dest.name:38s} {len(body):>10,} bytes")
    return body

def autoplot(sdate, edate, by, filt, tag):
    """IEM Autoplot 163 data CSV. Colon-delimited param syntax, :: between pairs."""
    parts = [
        "csector:conus", "var:count",
        f"sdate:{sdate}", f"edate:{edate}",
        f"filter:{filt}", f"by:{by}",
        "cmap:plasma", "lbl:yes",
    ]
    q = "::".join(parts).replace(" ", "%20")
    url = f"https://mesonet.agron.iastate.edu/plotting/auto/plot/163/{q}.csv"
    print(f"autoplot163 by={by} {sdate}->{edate} {filt}")
    get(url, f"autoplot163_{tag}.csv")
    return url

def raw_lsr(sts, ets, tag):
    """Raw LSR rows (one per NWS report) as CSV, all WFOs, tornado only."""
    p = {
        "sts": sts, "ets": ets, "wfo": "ALL",
        "fmt": "csv", "type": "TORNADO",
    }
    url = "https://mesonet.agron.iastate.edu/cgi-bin/request/gis/lsr.py?" + urllib.parse.urlencode(p)
    print(f"raw LSR {sts}->{ets}")
    get(url, f"lsr_raw_{tag}.csv")
    return url

if __name__ == "__main__":
    urls = []
    urls.append(autoplot(PLATE_START, PLATE_END, "state", "TORNADO", "state_plate"))
    urls.append(autoplot(PLATE_START, LIVE_END,  "state", "TORNADO", "state_live"))
    urls.append(autoplot(PLATE_START, PLATE_END, "wfo",   "TORNADO", "wfo_plate"))
    urls.append(raw_lsr("2026-01-01T00:00Z", "2026-08-22T00:00Z", "2026"))
    # Prior full years for the climatological context panel.
    for yr in range(2003, 2026):
        autoplot(f"{yr}-01-01 0000", f"{yr}-08-13 0000", "state", "TORNADO", f"state_ytd_{yr}")
    print("\nretrieved", datetime.datetime.utcnow().isoformat(timespec="seconds"), "UTC")
