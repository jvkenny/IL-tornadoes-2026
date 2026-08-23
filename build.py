#!/usr/bin/env python3
"""Inject the data bundle into template.html.
  index.html      - links the plate PNGs (local preview / GitHub Pages)
  published.html  - plates inlined as data URIs (Artifact CSP blocks all external hosts)
"""
import pathlib, base64
d = pathlib.Path(__file__).parent
DATA = d / "analysis/build/storymap_data.json"
PLATES = ("plate_II_reports_2026", "plate_III_vs_normal_2026")

t = (d / "template.html").read_text()
page = t.replace("__DATA__", DATA.read_text())
(d / "index.html").write_text(page)

pub = page
for n in PLATES:
    pub = pub.replace(f'src="{n}.png"',
        'src="data:image/png;base64,' + base64.b64encode((d/f"{n}.png").read_bytes()).decode() + '"')
(d / "published.html").write_text(pub)
for f in ("index.html", "published.html"):
    print(f"{f:16s} {(d/f).stat().st_size/1024:8.0f} KB")
