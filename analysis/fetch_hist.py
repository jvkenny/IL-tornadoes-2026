#!/usr/bin/env python3
"""Year-to-date (Jan 1 -> Aug 13) tornado LSR counts by state, 2003-2026.
Same autoplot, same filter, same calendar window -- so the comparison is
apples-to-apples against the plate John shared."""
import urllib.request, pathlib, time, sys
OUT = pathlib.Path(__file__).parent / "data"
UA = {"User-Agent": "IL-tornadoes-2026 (github.com/jvkenny/IL-tornadoes-2026)"}

def one(yr, tries=4):
    q = ("csector:conus::var:count::"
         f"sdate:{yr}-01-01%200000::edate:{yr}-08-13%200000::"
         "filter:TORNADO::by:state::cmap:plasma::lbl:yes")
    url = f"https://mesonet.agron.iastate.edu/plotting/auto/plot/163/{q}.csv"
    dest = OUT / f"ytd_state_{yr}.csv"
    if dest.exists() and dest.stat().st_size > 40:
        return "cached"
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=180) as r:
                b = r.read()
            if b.startswith(b"state,count") and len(b) > 40:
                dest.write_bytes(b); return f"{len(b)}B"
            last = f"unexpected body {b[:60]!r}"
        except Exception as e:
            last = repr(e)
        time.sleep(4 * (a + 1))
    return f"FAIL {last}"

for yr in range(2003, 2027):
    print(f"{yr}: {one(yr)}", flush=True)
    time.sleep(1.5)
