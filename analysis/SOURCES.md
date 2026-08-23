# Sources — Illinois tornado year, 2026

All retrieved **22 August 2026**. Raw snapshots in `data/`, never edited.
Re-acquire with `fetch.py` + `fetch_hist.py`.

| # | Source | What it is | What it was used for |
|---|---|---|---|
| 1 | [IEM Autoplot #163](https://mesonet.agron.iastate.edu/plotting/auto/meta/163.json) — `plot/163/…by:state…filter:TORNADO.csv` | Preliminary/unfiltered NWS **Local Storm Reports**, counted by state. The exact application that produced the map John shared. | Every report count and every ×-normal figure. Pulled for 1 Jan – 13 Aug of each year **2004–2026** (`data/ytd_state_*.csv`). |
| 2 | [IEM LSR archive](https://mesonet.agron.iastate.edu/cgi-bin/request/gis/lsr.py) — `type=TORNADO`, all WFOs, 1 Jan – 22 Aug 2026 | 1,545 individual reports with timestamp, lat/lon, county, source, remark. | The Illinois season replay, the daily histogram, biggest-day and monthly breakdowns. `data/lsr_raw_2026.csv` |
| 3 | [NOAA SPC severe weather database](https://www.spc.noaa.gov/wcm/data/1950-2025_actual_tornadoes.csv) | 73,458 **surveyed tornado** records, 1950–2025. | All confirmed tornado counts, all-time single-year state records, the report→tornado calibration. |
| 4 | [NOAA NCEI Storm Events](https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/) — `d2026_c20260819`, `d2025_c20260819` | NWS-confirmed events with county segmentation and EF rating. 2026 coverage ends **31 May 2026**. | 2026's observed report→tornado ratio; validation of the counting method against SPC. |
| 5 | [US Census cartographic boundary file](https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_state_20m.zip) — states, 2023, 1:20,000,000 | Generalised state polygons. | All map geometry, reprojected to NAD83 / Conus Albers (EPSG:5070). |
| 6 | [SPC database format specification](https://www.spc.noaa.gov/wcm/data/SPC_severe_database_description.pdf) | Field definitions, incl. the `ns`/`sn`/`sg` counting rules. | Establishing the correct counting rule (below). `data/spc_format.pdf` |

## Counting rules, and why

**Tornado counts (SPC).** Per source 6, p.2: national totals use `sg == 1` (one row per
distinct tornado); per-state totals use `sn == 1` ("entire track info in this state"), so a
tornado crossing a state line is credited to both states. *Validation:* this rule returns
**1,817** national tornadoes for 2004, matching SPC's published figure exactly.

**Tornado counts (NCEI).** NCEI segments tornadoes by county. Rows carrying
`TOR_OTHER_CZ_STATE` are continuations of a previous segment; dropping them yields distinct
tornadoes. *Validation:* against SPC over identical 2025 windows this agrees to **0.97**
nationally and **0.96** for Illinois.

**Reports ≠ tornadoes.** LSR counts and surveyed tornado counts are never mixed in one series.

## Known data defects encountered

- **Corrupt state FIPS in the SPC file.** At least one Idaho record carries `stf = 19`, which is
  Iowa's FIPS. Deriving a FIPS→abbreviation map from that column silently reassigned all 39 of
  Iowa's 2026 confirmed tornadoes to Idaho. Fixed by mapping NCEI's state *name* against the
  Census boundary file instead. (SPC's own documentation warns that some FIPS codes are wrong.)
- **2003 unavailable** from Autoplot #163 (HTTP 400); the LSR comparison baseline is 2004–2025.
- **Duplicate LSR rows.** The raw archive returns 289 Illinois rows for the window, five of
  which are byte-identical duplicate filings. The IEM's own state aggregation removes them and
  reports 283; the replay plots the 284 distinct rows. The residual of one is inside the IEM's
  county-association heuristics, which its documentation puts at roughly 1%.
- **2025 is not final** in the SPC file (last record 2025-09-09), so full-year series are drawn
  through 2024. The Jan–Aug 13 window is complete for 2025 and is used.
- **NaN → invalid JSON.** States with no tornadoes in 1991–2020 produced `NaN` means, which
  `json.dumps` writes bare and `JSON.parse` rejects. `analysis.py` now coerces and asserts.
