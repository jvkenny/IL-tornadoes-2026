# AGENTS.md — Illinois' tornado year, 2026

Guide for AI coding agents. Read `README.md` (findings, reproduction) and `analysis/NOTES.md`
(verdict and caveats) before changing anything.

## Identity

- **What:** a data story and two print plates on Illinois' record 2026 preliminary tornado
  report count, compared with each state's own 2004–2025 history.
- **Repository:** `github.com/jvkenny/IL-tornadoes-2026` (public, MIT for code and prose).
  Default branch `main`.
- **Site:** https://jvkenny.github.io/IL-tornadoes-2026/ — GitHub Pages from `main`, repo root.
- **Status:** finished, static snapshot (data window 1 Jan – 13 Aug 2026). Updating it means
  re-fetching and re-running the whole pipeline, then revising prose that quotes numbers.

## Architecture

```
analysis/fetch.py, fetch_hist.py  -> analysis/data/        raw source snapshots (committed, never hand-edited)
analysis/geometry.py              -> analysis/build/states_*.json   state boundaries (Census 20m, EPSG:5070 + WGS84)
analysis/analysis.py              -> analysis/findings.json         single source of truth for every number
analysis/plates.py                -> plate_II_*, plate_III_* (.png 300 dpi + .pdf)
analysis/build_web.py             -> analysis/build/storymap_data.json
build.py   template.html + storymap_data.json -> index.html (and published.html, plates inlined; gitignored)
```

`index.html` is self-contained (no external requests) apart from linking the plate PNGs.

## Boundaries

- Raw files in `analysis/data/` are dated snapshots of continuously revised preliminary data.
  Never edit them; re-fetch instead and note the retrieval date in `analysis/SOURCES.md`.
- No derived number is typed by hand into the plates or the site; it must come from
  `findings.json` via the pipeline. Prose in README/NOTES/template quoting numbers must be
  updated to match after a re-run.
- Keep the core caveat: reports are not tornadoes. Show both report-to-tornado calibrations
  rather than averaging them.
- Map states by Census state name, not the SPC file's state FIPS column (it has a corrupt code).
- Cartography: equal-area EPSG:5070; Plate III diverges about 1.0x; states averaging under five
  reports a year are masked; label/fill pairs must clear WCAG 4.5:1.

## Development

```bash
cd analysis
uv run --with pandas --with numpy   python3 fetch.py && python3 fetch_hist.py   # optional re-acquire
uv run --with pyshp --with pyproj   python3 geometry.py
uv run --with pandas --with numpy   python3 analysis.py
uv run --with matplotlib            python3 plates.py
uv run --with pandas --with pyproj --with matplotlib python3 build_web.py
cd .. && python3 build.py
python3 -m http.server 8000         # then open http://localhost:8000/
```

No test suite. Verify that `analysis.py` reproduces `findings.json` (without a re-fetch the
only diff is `meta.generated_utc`; verified 2026-10-12) and the page renders.

## Deployment

Pushing to `main` publishes via GitHub Pages; no build runs on GitHub, so commit the regenerated
`index.html`, plates, and `analysis/build/*.json`. Agents open a PR; the maintainer merges.

## Handoff

- Complete and live. Ideas for follow-up data are in `analysis/NOTES.md`.
